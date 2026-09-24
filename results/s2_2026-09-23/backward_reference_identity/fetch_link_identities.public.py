"""Link preserved one-generation backward-reference occurrences to DOI/provider evidence.

Scope (hard limits):
- Network: only Crossref /works/{doi} and Crossref /works?query.bibliographic=...
  User-Agent carries mailto; >= MIN_INTERVAL seconds between requests (< 5 req/s);
  retry with backoff on 429/5xx/network errors; every failure body is saved as evidence.
- No OpenAlex request of any kind. The OpenAlex provider union is read from the local
  2026-09-22 identity handoff only.
- Existing cached Crossref /works responses in the repo are reused (bytes copied here,
  source path and original receipt recorded, hashes verified).
- Writes only inside this script's directory. Inputs are read-only.
- Discovery/identity records only: no eligibility decision, no method coding, no P-LIT
  proportion or verdict. A failed or missing DOI record is UNRESOLVED, not an exclusion.
  A conflict is recorded with both sides and never deleted.

Resumable: request receipts are appended to request_receipts.jsonl; a successful earlier
receipt whose saved bytes still hash-match is reused on rerun.
"""
from pathlib import Path
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib, html, json, re, shutil, sys, time, unicodedata
import urllib.error, urllib.parse, urllib.request

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
INPUTS = [
    'results/s2_2026-09-20/backward_reference_discovery/reference_occurrences.json',
    'results/s2_2026-09-21/backward_reference_extension/reference_occurrences.json',
]
UNION = 'results/s2_2026-09-22/identity_handoff/provider_identity_union.jsonl'
WORKS_DIR = BASE / 'crossref_works'
QUERY_DIR = BASE / 'crossref_bibliographic'
FAIL_DIR = BASE / 'crossref_failures'
RECEIPTS = BASE / 'request_receipts.jsonl'
LINKS = BASE / 'reference_identity_links.jsonl'
SUMMARY = BASE / 'summary.json'
HASHES_BEFORE = BASE / 'input_hashes_before.json'
USER_AGENT = 'sts-electrocatalyst-backward-reference-identity/1.0 (mailto:<contact-email-redacted>)'
MIN_INTERVAL = 0.35   # seconds between requests (about 2.9 req/s, below the 5 req/s cap)
MAX_ATTEMPTS = 5
QUERY_ROWS = 5
QUERY_MAX_CHARS = 1000

# Existing Crossref /works caches (receipt files and directories); broad-search pages are not used.
CACHE_RECEIPT_FILES = [
    'results/s2_2026-09-19/primary_identity_review/crossref_receipts.json',
    'results/s2_2026-09-20/complementary_identity_review/crossref_receipts.json',
    'results/s2_2026-09-20/complementary_identity_review/crossref_receipts_supplement.json',
    'results/s2_2026-09-20/priority_source_receipts/priority_doi_receipts.json',
]
CACHE_META_DIRS = ['results/s2_2026-09-16/f8/crossref_cache']

# Printed citation styles, from inspection of the preserved bibliographies. In the
# abbreviated Wiley/ChemPhysChem-type styles the article title is not printed, so title
# agreement cannot be established from the citation.
TITLE_PRINTED_STYLE = {
    'man2011_article': False, 'garciamota2011_article': False, 'lee2022_article': False,
    'feng2025_article': True, 'xu2015_article': True, 'xu2015_si': True,
    'neto2025_article': True, 'neto2025_si': True, 'dickens2017_article': True,
    'dickens2017_si': True, 'lim2021_article': True,
}

NOTICE_RE = re.compile(r'^\s*(correction|erratum|corrigendum|retraction|addendum)\b|\b(erratum|corrigendum)\b')
STOP = {'the', 'of', 'and', 'for', 'in', 'a', 'an', 'on', 'fur', 'de', 'la', 'le', 'des', 'du', 'und', 'et'}
SINGLE_LETTER_OK = {'journal', 'zeitschrift'}
SPECIAL = str.maketrans({'ø': 'o', 'Ø': 'O', 'æ': 'ae', 'Æ': 'AE', 'ß': 'ss', 'ł': 'l', 'Ł': 'L',
                         'đ': 'd', 'Đ': 'D', 'ı': 'i', 'œ': 'oe', 'Œ': 'OE', 'þ': 'th', 'ð': 'd'})


def sha(data):
    return hashlib.sha256(data).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def rel(path):
    return str(Path(path).resolve().relative_to(ROOT)).replace('\\', '/')


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def norm_doi(doi):
    doi = (doi or '').strip()
    doi = re.sub(r'^(https?://(dx\.)?doi\.org/|doi:\s*)', '', doi, flags=re.I)
    return doi.lower()


def safe_name(doi):
    return re.sub(r'[<>:"\\|?*]', '_', doi.replace('/', '__'))


# ---------------------------------------------------------------- text folding

def fold(s):
    s = html.unescape(re.sub(r'<[^>]+>', ' ', s or ''))
    s = s.translate(SPECIAL)
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return s.lower()


def letters(s):
    return re.sub(r'[^a-z0-9]', '', fold(s))


def tokens(s):
    return re.findall(r'[a-z0-9]+', fold(s))


# ---------------------------------------------------------------- HTTP

_last = [0.0]


def _pace():
    wait = MIN_INTERVAL - (time.monotonic() - _last[0])
    if wait > 0:
        time.sleep(wait)
    _last[0] = time.monotonic()


def load_receipts():
    out = {}
    if RECEIPTS.exists():
        for line in RECEIPTS.read_text(encoding='utf-8').splitlines():
            if line.strip():
                r = json.loads(line)
                out[r['request_key']] = r  # latest wins; earlier lines stay in the file
    return out


def append_receipt(r):
    with RECEIPTS.open('a', encoding='utf-8') as fh:
        fh.write(json.dumps(r, ensure_ascii=False) + '\n')


def http_get(key, kind, url, target, validate):
    """GET url with pacing and retry; save body to target on 200; save failures as evidence."""
    attempts = []
    receipt = {'request_key': key, 'kind': kind, 'url': url, 'user_agent': USER_AGENT,
               'status': 'REQUEST_FAILED', 'attempts': attempts}
    for attempt in range(1, MAX_ATTEMPTS + 1):
        _pace()
        stamp = now()
        delay = None
        try:
            req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT, 'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read()
                code = resp.status
                hdrs = {k: resp.headers.get(k) for k in ('x-rate-limit-limit', 'x-rate-limit-interval',
                                                          'x-api-pool', 'content-type') if resp.headers.get(k)}
            problem = validate(raw)
            target.write_bytes(raw)
            attempts.append({'requested_utc': stamp, 'http_status': code, 'response_headers': hdrs})
            receipt.update(status='HTTP_200' if not problem else 'HTTP_200_VALIDATION_ISSUE',
                           validation_issue=problem, http_status=code, retrieved_utc=stamp,
                           raw_path=rel(target), sha256=sha(raw), bytes=len(raw))
            return receipt
        except urllib.error.HTTPError as exc:
            body = exc.read() or b''
            fpath = FAIL_DIR / (target.stem + f'.http{exc.code}.attempt{attempt}.' + stamp.replace(':', '-').replace('+', '_') + '.txt')
            fpath.write_bytes(body)
            entry = {'requested_utc': stamp, 'http_status': exc.code, 'error_path': rel(fpath), 'error_sha256': sha(body)}
            attempts.append(entry)
            receipt['http_status'] = exc.code
            if exc.code not in (429, 500, 502, 503, 504):
                receipt['status'] = 'HTTP_404_NOT_FOUND' if exc.code == 404 else f'HTTP_{exc.code}'
                return receipt
            ra = exc.headers.get('Retry-After') if exc.headers else None
            if ra:
                try:
                    delay = float(ra)
                except ValueError:
                    try:
                        delay = (parsedate_to_datetime(ra) - datetime.now(timezone.utc)).total_seconds()
                    except Exception:
                        delay = None
                entry['retry_after'] = ra
        except Exception as exc:  # network / parse
            attempts.append({'requested_utc': stamp, 'error': repr(exc)})
        if attempt < MAX_ATTEMPTS:
            if delay is None:
                delay = 2.0 * (2 ** (attempt - 1))
            delay = min(max(delay, 1.0), 120.0)
            attempts[-1]['backoff_seconds'] = delay
            time.sleep(delay)
    return receipt


# ---------------------------------------------------------------- caches

def build_cache_index():
    """Index existing Crossref /works responses in the repo by lower-case DOI."""
    idx = {}
    notes = []

    def consider(doi, raw_path, receipt_path, retrieved, url, sha_expected, http_status):
        p = ROOT / raw_path
        if not p.exists():
            notes.append({'doi': doi, 'raw_path': raw_path, 'issue': 'CACHE_FILE_MISSING'})
            return
        raw = p.read_bytes()
        if sha_expected and sha(raw) != sha_expected:
            notes.append({'doi': doi, 'raw_path': raw_path, 'issue': 'CACHE_HASH_MISMATCH_NOT_USED'})
            return
        try:
            data = json.loads(raw)
        except Exception:
            notes.append({'doi': doi, 'raw_path': raw_path, 'issue': 'CACHE_NOT_JSON'})
            return
        if data.get('status') != 'ok' or data.get('message-type') != 'work':
            return
        got = norm_doi(data['message'].get('DOI'))
        entry = {'cache_source_path': raw_path, 'cache_receipt_path': receipt_path,
                 'original_retrieved_utc': retrieved, 'original_url': url,
                 'original_http_status': http_status, 'sha256': sha(raw), 'returned_doi': got}
        for key in {got, norm_doi(doi)}:
            if key and (key not in idx or (retrieved or '') > (idx[key]['original_retrieved_utc'] or '')):
                idx[key] = entry

    for rf in CACHE_RECEIPT_FILES:
        path = ROOT / rf
        if not path.exists():
            continue
        for r in json.loads(path.read_text(encoding='utf-8-sig')):
            if not r.get('raw_path'):
                continue
            if r.get('status') not in (None, 'DOI_RESOLVED', 'CACHE_REUSED'):
                continue
            doi = r.get('doi') or r.get('requested_doi') or ''
            consider(doi, r['raw_path'], rf, r.get('retrieved_utc') or r.get('requested_utc'),
                     r.get('url'), r.get('sha256'), r.get('http_status', 200))
    for d in CACHE_META_DIRS:
        for meta in sorted((ROOT / d).glob('*.meta.json')):
            m = json.loads(meta.read_text(encoding='utf-8-sig'))
            if m.get('status') != 200:
                continue
            raw = meta.with_name(meta.name[:-len('.meta.json')] + '.json')
            doi = urllib.parse.unquote(m.get('url', '').split('/works/')[-1])
            consider(doi, rel(raw), rel(meta), m.get('fetched_utc'), m.get('url'), m.get('sha256'), 200)
    return idx, notes


# ---------------------------------------------------------------- Crossref metadata

def date_parts(obj):
    if not obj or not obj.get('date-parts') or not obj['date-parts'][0] or obj['date-parts'][0][0] is None:
        return None
    return '-'.join(f'{x:02d}' if i else str(x) for i, x in enumerate(obj['date-parts'][0]))


def extract(msg):
    return {
        'doi': msg.get('DOI'),
        'title': msg.get('title') or [],
        'subtitle': msg.get('subtitle') or [],
        'authors': [{k: a.get(k) for k in ('given', 'family', 'name', 'sequence', 'ORCID') if a.get(k)}
                    for a in msg.get('author') or []],
        'container_title': msg.get('container-title') or [],
        'short_container_title': msg.get('short-container-title') or [],
        'type': msg.get('type'),
        'publisher': msg.get('publisher'),
        'volume': msg.get('volume'), 'issue': msg.get('issue'), 'page': msg.get('page'),
        'article_number': msg.get('article-number'),
        'identifiers': {'DOI': msg.get('DOI'), 'URL': msg.get('URL'), 'ISSN': msg.get('ISSN') or [],
                        'ISBN': msg.get('ISBN') or [], 'alternative_id': msg.get('alternative-id') or []},
        'dates': {'published_online': date_parts(msg.get('published-online')),
                  'published_print': date_parts(msg.get('published-print')),
                  'issued': date_parts(msg.get('issued')),
                  'published': date_parts(msg.get('published')),
                  'created': date_parts(msg.get('created'))},
        'relation': msg.get('relation') or {},
        'update_to': msg.get('update-to') or [],
    }


def years_of(meta):
    out = set()
    for k in ('published_online', 'published_print', 'issued', 'published'):
        v = meta['dates'].get(k)
        if v:
            out.add(int(v[:4]))
    return out


# ---------------------------------------------------------------- agreement tests

def abbrev_ok(c, j):
    """c (printed token) abbreviates j (journal word): same first letter, c a subsequence of j."""
    if not c or not j or c[0] != j[0]:
        return False
    if len(c) == 1 and not (j in SINGLE_LETTER_OK or len(j) == 1):
        return False
    it = iter(j)
    return all(ch in it for ch in c)


def journal_variants(meta):
    out = []
    for label in ('container_title', 'short_container_title'):
        for name in meta[label]:
            out.append((label, name))
            if ':' in name:
                out.append((label + '_before_colon', name.split(':')[0]))
    return out


def journal_agreement(cit, meta):
    variants = journal_variants(meta)
    if not variants:
        return {'status': 'NOT_AVAILABLE_IN_CROSSREF'}
    ct = [t for t in tokens(cit) if t not in STOP]
    cl = letters(cit)
    partial = None
    for label, name in variants:
        jt = [t for t in tokens(name) if t not in STOP]
        if not jt:
            continue
        n = len(jt)
        for i in range(len(ct) - n + 1):
            if all(abbrev_ok(ct[i + k], jt[k]) for k in range(n)):
                return {'status': 'AGREE', 'basis': 'TOKEN_ABBREVIATION', 'crossref_field': label,
                        'crossref_value': name, 'printed_tokens': ct[i:i + n]}
        # letter-spaced / hyphen-broken fallback: concatenated prefixes (>= 2 letters, 1 for 'journal')
        pat = ''.join('(?:' + '|'.join(re.escape(j[:k]) for k in range(len(j), (1 if (j in SINGLE_LETTER_OK or len(j) == 1) else min(2, len(j))) - 1, -1)) + ')' for j in jt)
        m = re.search(pat, cl)
        if m and len(m.group(0)) >= 6:
            return {'status': 'AGREE', 'basis': 'LETTERS_ONLY_PREFIX_ABBREVIATION', 'crossref_field': label,
                    'crossref_value': name, 'printed_letters': m.group(0)}
        if n >= 3 and partial is None:
            for k in range(n - 1, 1, -1):
                hit = next((i for i in range(len(ct) - k + 1) if all(abbrev_ok(ct[i + q], jt[q]) for q in range(k))), None)
                if hit is not None:
                    partial = {'status': 'PARTIAL', 'basis': f'LEADING_{k}_OF_{n}_TOKENS', 'crossref_field': label,
                               'crossref_value': name, 'printed_tokens': ct[hit:hit + k]}
                    break
    if partial:
        return partial
    return {'status': 'NOT_FOUND', 'crossref_values': [v for _, v in variants]}


def author_agreement(cit, meta):
    authors = meta['authors']
    if not authors:
        return {'status': 'NOT_AVAILABLE_IN_CROSSREF'}
    first = next((a for a in authors if a.get('sequence') == 'first'), authors[0])
    fam = first.get('family') or first.get('name') or ''
    fl, cl = letters(fam), letters(cit)
    if not fl:
        return {'status': 'NOT_AVAILABLE_IN_CROSSREF'}
    pos = cl.find(fl)
    if 0 <= pos <= 40:
        return {'status': 'AGREE', 'crossref_first_author_family': fam, 'letters_position': pos}
    for part in re.split(r'[\s\-]+', fold(fam)):
        pl = letters(part)
        if len(pl) >= 3 and 0 <= cl.find(pl) <= 40:
            return {'status': 'AGREE_PARTIAL_NAME', 'crossref_first_author_family': fam, 'matched_part': pl,
                    'letters_position': cl.find(pl)}
    if pos > 40:
        return {'status': 'FOUND_NOT_LEADING', 'crossref_first_author_family': fam, 'letters_position': pos}
    return {'status': 'NOT_FOUND', 'crossref_first_author_family': fam}


def printed_years(cit):
    return sorted({int(y) for y in re.findall(r'(?<!\d)(1[89]\d\d|20[0-2]\d)(?!\d)', fold(cit))})


def year_agreement(cit, meta):
    ys = years_of(meta)
    py = printed_years(cit)
    if not ys:
        return {'status': 'NOT_AVAILABLE_IN_CROSSREF', 'printed_years': py}
    if not py:
        return {'status': 'NOT_PRINTED', 'crossref_years': sorted(ys)}
    hit = sorted(ys & set(py))
    return {'status': 'AGREE' if hit else 'NOT_FOUND', 'printed_years': py, 'crossref_years': sorted(ys),
            'matching_years': hit}


def title_agreement(cit, meta):
    titles = [' '.join([t] + meta['subtitle']) for t in meta['title']] + meta['title']
    if not titles:
        return {'status': 'NOT_AVAILABLE_IN_CROSSREF'}
    cl = letters(cit)
    best = 0.0
    for t in titles:
        tl = letters(t)
        if len(tl) >= 10 and tl in cl:
            return {'status': 'AGREE', 'basis': 'EXACT_LETTERS_SUBSTRING', 'crossref_title': t}
    for t in meta['title']:
        words = [w for w in tokens(t) if len(w) >= 3 and w not in STOP]
        if not words:
            continue
        frac = sum(w in cl for w in words) / len(words)
        if len(words) >= 4 and frac >= 0.9:
            return {'status': 'AGREE', 'basis': 'WORD_COVERAGE', 'coverage': round(frac, 3), 'crossref_title': t}
        best = max(best, frac)
    return {'status': 'PARTIAL' if best >= 0.5 else 'NOT_FOUND', 'best_word_coverage': round(best, 3),
            'crossref_title': meta['title'][0]}


def number_agreement(cit, value):
    if not value:
        return 'NOT_AVAILABLE_IN_CROSSREF'
    v = fold(str(value)).strip()
    first = re.split(r'[\-–,]', v)[0].strip()
    if not first:
        return 'NOT_AVAILABLE_IN_CROSSREF'
    if first in tokens(cit):
        return 'AGREE'
    if letters(first) and letters(first) in letters(cit):
        return 'AGREE_LETTERS_ONLY'
    return 'NOT_FOUND'


def assess(cit, meta):
    return {
        'title': title_agreement(cit, meta),
        'first_author': author_agreement(cit, meta),
        'year': year_agreement(cit, meta),
        'journal': journal_agreement(cit, meta),
        'volume': number_agreement(cit, meta['volume']),
        'first_page_or_article_number': (number_agreement(cit, meta['page']) if meta['page']
                                         else number_agreement(cit, meta['article_number'])),
    }


AUTHOR_OK = ('AGREE', 'AGREE_PARTIAL_NAME')


def four_field_flags(a):
    return {'title': a['title']['status'] == 'AGREE',
            'first_author': a['first_author']['status'] in AUTHOR_OK,
            'year': a['year']['status'] == 'AGREE',
            'journal': a['journal']['status'] == 'AGREE'}


def printed_doi_disagreements(a, title_printed):
    out = []
    if a['first_author']['status'] in ('NOT_FOUND', 'FOUND_NOT_LEADING'):
        out.append('first_author')
    if a['year']['status'] == 'NOT_FOUND':
        out.append('year')
    if a['journal']['status'] == 'NOT_FOUND':
        out.append('journal')
    if title_printed and a['title']['status'] == 'NOT_FOUND':
        out.append('title')
    return out


def review_flags(a, meta):
    """Non-blocking flags on an accepted identity, for later human review."""
    out = [k + '_PARTIAL' for k in ('title', 'journal') if a[k]['status'] == 'PARTIAL']
    if a['title'].get('basis') == 'WORD_COVERAGE':
        out.append('TITLE_AGREEMENT_BY_WORD_COVERAGE_NOT_EXACT')
    if a['journal'].get('basis') == 'LETTERS_ONLY_PREFIX_ABBREVIATION':
        out.append('JOURNAL_AGREEMENT_BY_LETTERS_ONLY_FALLBACK')
    if a['first_author']['status'] == 'AGREE_PARTIAL_NAME':
        out.append('FIRST_AUTHOR_PARTIAL_NAME')
    if not any(a[k] in ('AGREE', 'AGREE_LETTERS_ONLY') for k in ('volume', 'first_page_or_article_number')):
        out.append('NEITHER_VOLUME_NOR_PAGE_AGREES')
    if meta['update_to']:
        out.append('CROSSREF_RECORD_IS_AN_UPDATE_NOTICE')
    if NOTICE_RE.search(fold(' '.join(meta['title']))):
        out.append('CROSSREF_TITLE_READS_AS_CORRECTION_OR_ERRATUM')
    return out


# ---------------------------------------------------------------- main

def main():
    for d in (WORKS_DIR, QUERY_DIR, FAIL_DIR):
        d.mkdir(exist_ok=True)
    input_hashes = {p: sha((ROOT / p).read_bytes()) for p in INPUTS + [UNION]}
    if not HASHES_BEFORE.exists():
        dump(HASHES_BEFORE, {'recorded_utc': now(), 'sha256': input_hashes,
                             'note': 'Recorded by fetch_link_identities.py before any request; the self-check compares against these.'})
    before = json.loads(HASHES_BEFORE.read_text(encoding='utf-8'))['sha256']
    for p, h in input_hashes.items():
        if before[p] != h:
            raise SystemExit('Input changed since first run: ' + p)

    # OpenAlex provider union (local file only)
    union = {}
    union_lines = 0
    with (ROOT / UNION).open(encoding='utf-8') as fh:
        for line in fh:
            if not line.strip():
                continue
            union_lines += 1
            r = json.loads(line)
            for v in r.get('metadata_variants') or []:
                d = norm_doi((v.get('metadata') or {}).get('doi'))
                if d:
                    union.setdefault(d, set()).add(r['provider_id'])
    print('union identities', union_lines, 'union DOIs', len(union), flush=True)

    cache, cache_notes = build_cache_index()
    print('cache DOIs', len(cache), flush=True)
    prior = load_receipts()
    counters = {'network_requests_issued': 0, 'receipts_reused_from_this_directory': 0, 'cache_reused': 0}

    def reuse_ok(r):
        if not r or r['status'] not in ('HTTP_200', 'HTTP_200_VALIDATION_ISSUE', 'CACHE_REUSED'):
            return False
        p = ROOT / r['raw_path']
        return p.exists() and sha(p.read_bytes()) == r['sha256']

    works_memo = {}

    def fetch_works(doi):
        doi = norm_doi(doi)
        if doi in works_memo:
            return works_memo[doi]
        key = 'works:' + doi
        target = WORKS_DIR / (safe_name(doi) + '.json')
        r = prior.get(key)
        if reuse_ok(r):
            counters['receipts_reused_from_this_directory'] += 1
        elif doi in cache:
            c = cache[doi]
            raw = (ROOT / c['cache_source_path']).read_bytes()
            if target.exists() and target.read_bytes() != raw:
                raise SystemExit('Existing destination differs from cache: ' + doi)
            if not target.exists():
                target.write_bytes(raw)
            r = {'request_key': key, 'kind': 'crossref_works', 'status': 'CACHE_REUSED',
                 'url': c['original_url'], 'http_status': c['original_http_status'],
                 'retrieved_utc': c['original_retrieved_utc'], 'reused_utc': now(),
                 'cache_source_path': c['cache_source_path'], 'cache_receipt_path': c['cache_receipt_path'],
                 'raw_path': rel(target), 'sha256': sha(raw), 'bytes': len(raw)}
            append_receipt(r)
            counters['cache_reused'] += 1
        else:
            url = 'https://api.crossref.org/works/' + urllib.parse.quote(doi, safe='')

            def validate(raw):
                data = json.loads(raw)
                got = norm_doi(data.get('message', {}).get('DOI'))
                return None if got == doi else 'RETURNED_DOI_DIFFERS:' + got
            if r:
                print('retrying earlier failed request', key, flush=True)
            r = http_get(key, 'crossref_works', url, target, validate)
            if prior.get(key):
                r['earlier_receipt_status'] = prior[key]['status']
            counters['network_requests_issued'] += len(r['attempts'])
            append_receipt(r)
            print(key, r['status'], flush=True)
        meta = None
        if r['status'] in ('HTTP_200', 'HTTP_200_VALIDATION_ISSUE', 'CACHE_REUSED'):
            meta = extract(json.loads((ROOT / r['raw_path']).read_bytes())['message'])
        works_memo[doi] = (r, meta)
        return r, meta

    query_memo = {}

    def bibliographic(query):
        qh = sha(query.encode('utf-8'))[:20]
        key = 'bibliographic:' + qh
        if key in query_memo:
            return query_memo[key]
        target = QUERY_DIR / ('q_' + qh + '.json')
        r = prior.get(key)
        if reuse_ok(r):
            counters['receipts_reused_from_this_directory'] += 1
        else:
            url = ('https://api.crossref.org/works?rows=' + str(QUERY_ROWS) + '&query.bibliographic=' +
                   urllib.parse.quote(query, safe=''))

            def validate(raw):
                data = json.loads(raw)
                return None if data.get('message-type') == 'work-list' else 'UNEXPECTED_MESSAGE_TYPE'
            r = http_get(key, 'crossref_query_bibliographic', url, target, validate)
            r['query'] = query
            if prior.get(key):
                r['earlier_receipt_status'] = prior[key]['status']
            counters['network_requests_issued'] += len(r['attempts'])
            append_receipt(r)
            print(key, r['status'], flush=True)
        items = None
        if r['status'] in ('HTTP_200', 'HTTP_200_VALIDATION_ISSUE'):
            items = json.loads((ROOT / r['raw_path']).read_bytes())['message'].get('items', [])
        query_memo[key] = (r, items)
        return r, items

    def receipt_view(r):
        keep = ('request_key', 'kind', 'status', 'url', 'http_status', 'retrieved_utc', 'reused_utc',
                'raw_path', 'sha256', 'cache_source_path', 'cache_receipt_path', 'validation_issue')
        out = {k: r[k] for k in keep if k in r}
        out['attempt_count'] = len(r.get('attempts', []))
        out['failure_evidence'] = [a.get('error_path') for a in r.get('attempts', []) if a.get('error_path')]
        return out

    def union_view(doi):
        doi = norm_doi(doi)
        ids = sorted(union.get(doi, []))
        return {'doi_checked': doi, 'matched': bool(ids), 'openalex_ids': ids,
                'match_basis': 'EXACT_DOI_CASE_INSENSITIVE_AGAINST_ALL_METADATA_VARIANTS', 'union_file': UNION}

    def run_bibliographic(cit, title_printed):
        query = re.sub(r'^\s*[a-z]\)\s*', '', cit)[:QUERY_MAX_CHARS]
        r, items = bibliographic(query)
        out = {'query': query, 'receipt': receipt_view(r)}
        if items is None:
            out['outcome'] = 'REQUEST_FAILED'
            return out
        evaluated = []
        for rank, it in enumerate(items, 1):
            meta = extract(it)
            a = assess(cit, meta)
            f = four_field_flags(a)
            evaluated.append({'rank': rank, 'crossref_score': it.get('score'), 'doi': norm_doi(meta['doi']),
                              'title': meta['title'][:1], 'container_title': meta['container_title'][:1],
                              'first_author_family': (meta['authors'][0].get('family') or meta['authors'][0].get('name')) if meta['authors'] else None,
                              'issued': meta['dates']['issued'], 'type': meta['type'],
                              'agreement': a, 'four_field_agreement': f, 'four_field_agree_count': sum(f.values())})
        out['items_evaluated'] = evaluated
        if not evaluated:
            out['outcome'] = 'NO_ITEMS_RETURNED'
            return out
        cit_names_notice = bool(NOTICE_RE.search(fold(cit)))
        for e in evaluated:
            e['is_correction_or_erratum_notice'] = bool(NOTICE_RE.search(fold(' '.join(e['title']))))
        confirmed = next((e for e in evaluated if e['four_field_agree_count'] == 4
                          and (cit_names_notice or not e['is_correction_or_erratum_notice'])), None)
        notice_only = next((e for e in evaluated if e['four_field_agree_count'] == 4), None)
        if confirmed is None and notice_only is not None:
            out['outcome'] = 'CANDIDATE_MATCHED_CORRECTION_OR_ERRATUM_NOTICE'
            out['chosen_rank'] = notice_only['rank']
            out['note'] = ('All four fields agree, but the matching Crossref record is a correction/erratum notice '
                           'while the printed citation does not name one; not accepted as confirmation.')
            return out
        if confirmed:
            out['outcome'] = 'CONFIRMED_ALL_FOUR_FIELDS'
            out['chosen_rank'] = confirmed['rank']
            return out

        def vp(e):
            return sum(e['agreement'][k] in ('AGREE', 'AGREE_LETTERS_ONLY') for k in ('volume', 'first_page_or_article_number'))
        best = max(evaluated, key=lambda e: (e['four_field_agree_count'], vp(e), e['crossref_score'] or 0))
        out['chosen_rank'] = best['rank']
        f = best['four_field_agreement']
        if best['four_field_agree_count'] >= 2:
            if (not title_printed and f['first_author'] and f['year'] and f['journal'] and vp(best) >= 1):
                out['outcome'] = 'CANDIDATE_TITLE_NOT_PRINTED_OTHER_FIELDS_AGREE'
            else:
                out['outcome'] = 'CANDIDATE_PARTIAL_AGREEMENT'
        else:
            out['outcome'] = 'NO_QUALIFYING_CANDIDATE'
        return out

    links = []
    for inp in INPUTS:
        data = json.loads((ROOT / inp).read_text(encoding='utf-8-sig'))
        for o in data['reference_occurrences']:
            cit = o['display_whitespace_normalized']
            title_printed = TITLE_PRINTED_STYLE[o['document_id']]
            printed = o.get('explicit_dois_as_transcribed') or []
            link = {
                'link_id': o['occurrence_id'],
                'source_input': inp, 'source_input_sha256': input_hashes[inp],
                'occurrence_id': o['occurrence_id'], 'parent_doi': o['parent_doi'],
                'document_id': o['document_id'], 'document_role': o['document_role'],
                'reference_number': o.get('reference_number'), 'subreference_letter': o.get('subreference_letter'),
                'reference_ordinal': o.get('reference_ordinal'), 'label_kind': o.get('label_kind'),
                'parent_reference_group': o.get('parent_reference_group'),
                'locators': {k: o.get(k) for k in ('source_pdf_pages', 'source_text_line_start', 'source_text_line_end',
                                                   'source_web_line_start', 'source_web_line_end',
                                                   'reference_block_line_start', 'reference_block_line_end') if k in o},
                'discovery_generation': o['discovery_generation'],
                'seeds_further_expansion': False,
                'expansion_note': 'One-generation backward reference; it does not seed further reference expansion.',
                'printed_citation_verbatim': o['bibliography_verbatim'],
                'printed_citation_normalized': cit,
                'printed_dois_as_transcribed': printed,
                'doi_basis': o.get('doi_basis'),
                'title_printed_in_citation_style': title_printed,
            }
            res = {}
            if printed:
                if len(printed) != 1:
                    raise SystemExit('Multiple printed DOIs not handled: ' + o['occurrence_id'])
                doi = norm_doi(printed[0])
                r, meta = fetch_works(doi)
                res.update(route='PRINTED_DOI', doi=doi, crossref_works_receipt=receipt_view(r))
                if meta is None:
                    res.update(status='UNRESOLVED', unresolved_reason='PRINTED_DOI_CROSSREF_' + r['status'],
                               note='A failed or missing Crossref DOI record is unresolved, not an exclusion.')
                else:
                    a = assess(cit, meta)
                    dis = printed_doi_disagreements(a, title_printed)
                    res.update(crossref_metadata=meta, agreement=a, disagreeing_fields=dis,
                               openalex_union=union_view(meta['doi'] or doi))
                    if r.get('validation_issue'):
                        dis.append('returned_doi')
                    if dis:
                        res.update(status='CONFLICT', conflict={
                            'printed_citation': cit, 'printed_doi': printed[0],
                            'crossref_record': {'doi': meta['doi'], 'title': meta['title'], 'authors': meta['authors'][:3],
                                                'container_title': meta['container_title'], 'dates': meta['dates'],
                                                'volume': meta['volume'], 'page': meta['page']},
                            'disagreeing_fields': dis,
                            'note': 'Both sides retained; not repaired, not deleted.'})
                    else:
                        res['status'] = 'RESOLVED_PRINTED_DOI'
                        res['review_flags'] = review_flags(a, meta)
                if res['status'] != 'RESOLVED_PRINTED_DOI':
                    res['supplementary_bibliographic_evidence'] = run_bibliographic(cit, title_printed)
                    ch = res['supplementary_bibliographic_evidence'].get('chosen_rank')
                    if ch:
                        cd = res['supplementary_bibliographic_evidence']['items_evaluated'][ch - 1]['doi']
                        res['supplementary_bibliographic_evidence']['chosen_openalex_union'] = union_view(cd)
            else:
                b = run_bibliographic(cit, title_printed)
                res.update(route='BIBLIOGRAPHIC_QUERY', bibliographic_query=b)
                if b['outcome'] == 'CONFIRMED_ALL_FOUR_FIELDS':
                    cdoi = b['items_evaluated'][b['chosen_rank'] - 1]['doi']
                    r, meta = fetch_works(cdoi)
                    res.update(doi=cdoi, crossref_works_receipt=receipt_view(r))
                    if meta is None:
                        res.update(status='UNRESOLVED', unresolved_reason='WORKS_RECORD_FAILED_AFTER_BIBLIOGRAPHIC_MATCH_' + r['status'])
                    else:
                        a = assess(cit, meta)
                        f = four_field_flags(a)
                        res.update(crossref_metadata=meta, agreement=a, openalex_union=union_view(meta['doi'] or cdoi))
                        if all(f.values()):
                            res['status'] = 'RESOLVED_BIBLIOGRAPHIC'
                            res['review_flags'] = review_flags(a, meta)
                        else:
                            res.update(status='CANDIDATE', candidate_class='WORKS_RECORD_DID_NOT_REPEAT_FOUR_FIELD_AGREEMENT')
                elif b['outcome'].startswith('CANDIDATE'):
                    best = b['items_evaluated'][b['chosen_rank'] - 1]
                    res.update(status='CANDIDATE', candidate_class=b['outcome'], candidate_doi=best['doi'],
                               candidate_crossref_score=best['crossref_score'],
                               candidate_openalex_union=union_view(best['doi']),
                               note='Candidate only: title, first author, year and journal do not all agree.')
                else:
                    res.update(status='UNRESOLVED', unresolved_reason='BIBLIOGRAPHIC_' + b['outcome'])
            link['resolution'] = res
            link['identity_validation_status'] = res['status']
            link['eligibility_status'] = 'NOT_SCREENED'
            link['method_coding_status'] = 'NOT_CODED'
            links.append(link)

    with LINKS.open('w', encoding='utf-8') as fh:
        for l in links:
            fh.write(json.dumps(l, ensure_ascii=False) + '\n')
    summary = summarize(links, counters, cache_notes, input_hashes, union_lines, len(union))
    dump(SUMMARY, summary)
    print(json.dumps(summary['counts'], indent=1), flush=True)


def summarize(links, counters, cache_notes, input_hashes, union_lines, union_dois):
    from collections import Counter
    st = Counter(l['resolution']['status'] for l in links)
    resolved = [l for l in links if l['resolution']['status'] in ('RESOLVED_PRINTED_DOI', 'RESOLVED_BIBLIOGRAPHIC')]
    res_dois = {l['resolution']['crossref_metadata']['doi'].lower() for l in resolved}
    matched_occ = [l for l in resolved if l['resolution']['openalex_union']['matched']]
    matched_dois = {l['resolution']['crossref_metadata']['doi'].lower() for l in matched_occ}
    receipts = {}
    for line in RECEIPTS.read_text(encoding='utf-8').splitlines():
        if line.strip():
            r = json.loads(line)
            receipts.setdefault(r['request_key'], []).append(r)
    final = {k: v[-1] for k, v in receipts.items()}
    ok = ('HTTP_200', 'HTTP_200_VALIDATION_ISSUE', 'CACHE_REUSED')
    failed_final = sorted(k for k, r in final.items() if r['status'] not in ok)
    attempts = [a for v in receipts.values() for r in v for a in r.get('attempts', [])]
    return {
        'schema': 'backward_reference_identity_links/v1',
        'recorded_utc': now(),
        'script': 'results/s2_2026-09-23/backward_reference_identity/fetch_link_identities.py',
        'script_sha256': sha(Path(__file__).read_bytes()),
        'inputs_sha256': input_hashes,
        'openalex_union': {'path': UNION, 'provider_identities': union_lines, 'distinct_dois': union_dois},
        'status_definitions': {
            'RESOLVED_PRINTED_DOI': 'Printed DOI resolved by Crossref /works/{doi}; no disagreement in first author, year, journal (and title where the style prints titles).',
            'RESOLVED_BIBLIOGRAPHIC': 'No printed DOI; Crossref query.bibliographic item agrees on title, first author, year and journal, then confirmed by /works/{doi}.',
            'CONFLICT': 'Printed DOI resolved, but its Crossref record disagrees with the printed citation on at least one field. Both sides retained.',
            'CANDIDATE': 'Bibliographic candidate with at least two of the four fields agreeing but not all four; identity NOT established.',
            'UNRESOLVED': 'No usable record (Crossref 404/failure, or no qualifying bibliographic candidate). Not an exclusion.',
        },
        'counts': {
            'occurrences': len(links),
            'occurrences_by_input': dict(Counter(l['source_input'] for l in links)),
            'occurrences_by_document': dict(Counter(l['document_id'] for l in links)),
            'occurrences_with_printed_doi': sum(bool(l['printed_dois_as_transcribed']) for l in links),
            'status': dict(st),
            'resolved_doi_occurrences': len(resolved),
            'resolved_doi_occurrences_by_route': dict(Counter(l['resolution']['status'] for l in resolved)),
            'resolved_distinct_dois': len(res_dois),
            'matched_to_openalex_union_occurrences': len(matched_occ),
            'matched_to_openalex_union_distinct_dois': len(matched_dois),
            'new_to_union_distinct_dois': len(res_dois - matched_dois),
            'new_to_union_occurrences': len(resolved) - len(matched_occ),
            'conflicts': st.get('CONFLICT', 0),
            'candidates': st.get('CANDIDATE', 0),
            'candidates_by_class': dict(Counter(l['resolution'].get('candidate_class') for l in links if l['resolution']['status'] == 'CANDIDATE')),
            'unresolved': st.get('UNRESOLVED', 0),
        'resolved_with_review_flags': sum(bool(l['resolution'].get('review_flags')) for l in links if l['resolution']['status'] in ('RESOLVED_PRINTED_DOI', 'RESOLVED_BIBLIOGRAPHIC')),
            'unresolved_by_reason': dict(Counter(l['resolution'].get('unresolved_reason') for l in links if l['resolution']['status'] == 'UNRESOLVED')),
            'identity_not_established_total_candidate_plus_unresolved': st.get('CANDIDATE', 0) + st.get('UNRESOLVED', 0),
            'request_keys': len(final),
            'request_keys_by_final_status': dict(Counter(r['status'] for r in final.values())),
            'failed_requests_final': len(failed_final),
            'http_attempts_total': len(attempts),
            'http_attempt_status_counts': dict(Counter(str(a.get('http_status', 'NETWORK_ERROR')) for a in attempts)),
            'discovery_generation_values': sorted({l['discovery_generation'] for l in links}),
            'seeds_further_expansion_true': sum(l['seeds_further_expansion'] for l in links),
            'eligibility_decisions': 0,
            'method_coded_records': sum(l['method_coding_status'] != 'NOT_CODED' for l in links),
        },
        'this_run_counters': counters,
        'failed_request_keys_final': failed_final,
        'conflict_occurrences': [l['occurrence_id'] for l in links if l['resolution']['status'] == 'CONFLICT'],
        'new_to_union_dois': sorted(res_dois - matched_dois),
        'cache_index_notes': cache_notes,
        'limits': [
            'Discovery/identity evidence only: eligibility NOT_SCREENED, method reporting NOT_CODED, no P-LIT proportion or verdict.',
            'One generation only; no linked identity seeds further expansion.',
            'Field agreement is an automated text comparison against the printed citation; CONFLICT means a recorded disagreement for review, not a verdict that the DOI is wrong.',
            'Titles are not printed in the Man, Garcia-Mota and Lee bibliographies, so those references can reach at most CANDIDATE by bibliographic lookup.',
            'Only Crossref was consulted. DataCite-registered DOIs (e.g. Zenodo) return 404 from Crossref and remain UNRESOLVED.',
            'OpenAlex matching is by exact DOI against the local 2026-09-22 provider union; no OpenAlex request was made.',
        ],
    }


if __name__ == '__main__':
    main()
