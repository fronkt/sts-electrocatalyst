"""Independent self-check of the backward-reference identity links (no network).

1. Recount every number in summary.json['counts'] from the raw link records and receipts.
2. Verify every saved response/failure body hash named in receipts and link records.
3. Verify cache-reused bytes are identical to their cache source.
4. Verify occurrence coverage (every input occurrence linked exactly once) and that the
   link records copy the printed citation, printed DOIs and locators unchanged.
5. Confirm input and union sha256 are unchanged from input_hashes_before.json and from the
   values measured in the shell before the run started.
Writes self_check.json in this directory only.
"""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib, json

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
SHELL_MEASURED_BEFORE = {  # sha256sum run before the directory was created (2026-09-24T01:25:46Z)
    'results/s2_2026-09-20/backward_reference_discovery/reference_occurrences.json':
        'be7fde04d03eb59fd617ba02401caeecfac8240479ee34f59d9694d0ac993867',
    'results/s2_2026-09-21/backward_reference_extension/reference_occurrences.json':
        '8a16a6216c0a1ad49e199fac93a37709c0e1e7569ea0115e6837412fea8388e5',
}
OK = ('HTTP_200', 'HTTP_200_VALIDATION_ISSUE', 'CACHE_REUSED')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    checks = []

    def check(name, ok, detail=None):
        checks.append({'check': name, 'pass': bool(ok), 'detail': detail})

    links = [json.loads(l) for l in (BASE / 'reference_identity_links.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
    summary = json.loads((BASE / 'summary.json').read_text(encoding='utf-8'))
    before = json.loads((BASE / 'input_hashes_before.json').read_text(encoding='utf-8'))['sha256']
    receipts = [json.loads(l) for l in (BASE / 'request_receipts.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]

    # 5. input hashes
    after = {p: sha((ROOT / p).read_bytes()) for p in before}
    for p in before:
        check('input_unchanged_vs_script_record:' + p, before[p] == after[p], {'before': before[p], 'after': after[p]})
    for p, h in SHELL_MEASURED_BEFORE.items():
        check('input_unchanged_vs_shell_measurement:' + p, after[p] == h, {'shell_before': h, 'after': after[p]})

    # 4. coverage and verbatim copy
    inputs = {}
    for p in SHELL_MEASURED_BEFORE:
        for o in json.loads((ROOT / p).read_text(encoding='utf-8-sig'))['reference_occurrences']:
            inputs[o['occurrence_id']] = o
    ids = [l['occurrence_id'] for l in links]
    check('every_input_occurrence_linked_once', sorted(ids) == sorted(inputs) and len(ids) == len(set(ids)),
          {'links': len(ids), 'inputs': len(inputs)})
    mism = [l['occurrence_id'] for l in links
            if l['printed_citation_verbatim'] != inputs[l['occurrence_id']]['bibliography_verbatim']
            or l['printed_citation_normalized'] != inputs[l['occurrence_id']]['display_whitespace_normalized']
            or l['printed_dois_as_transcribed'] != inputs[l['occurrence_id']]['explicit_dois_as_transcribed']
            or l['reference_number'] != inputs[l['occurrence_id']].get('reference_number')
            or l['parent_doi'] != inputs[l['occurrence_id']]['parent_doi']
            or l['discovery_generation'] != inputs[l['occurrence_id']]['discovery_generation']
            or any(l['locators'][k] != inputs[l['occurrence_id']].get(k) for k in l['locators'])]
    check('link_records_copy_input_fields_unchanged', not mism, mism[:20])
    check('no_expansion_seeds_no_eligibility_no_coding',
          all(not l['seeds_further_expansion'] and l['eligibility_status'] == 'NOT_SCREENED'
              and l['method_coding_status'] == 'NOT_CODED' for l in links))

    # 2/3. hashes
    bad = []
    n_files = 0
    for r in receipts:
        if r.get('raw_path'):
            n_files += 1
            b = (ROOT / r['raw_path']).read_bytes()
            if sha(b) != r['sha256']:
                bad.append(r['raw_path'])
            if r['status'] == 'CACHE_REUSED' and (ROOT / r['cache_source_path']).read_bytes() != b:
                bad.append('cache-differs:' + r['cache_source_path'])
        for a in r.get('attempts', []):
            if a.get('error_path'):
                n_files += 1
                if sha((ROOT / a['error_path']).read_bytes()) != a['error_sha256']:
                    bad.append(a['error_path'])
    for l in links:
        res = l['resolution']
        for rv in [res.get('crossref_works_receipt'), (res.get('bibliographic_query') or {}).get('receipt'),
                   (res.get('supplementary_bibliographic_evidence') or {}).get('receipt')]:
            if rv and rv.get('raw_path'):
                n_files += 1
                if sha((ROOT / rv['raw_path']).read_bytes()) != rv['sha256']:
                    bad.append(l['occurrence_id'] + ':' + rv['raw_path'])
    saved = sorted(str(p.relative_to(ROOT)).replace('\\', '/') for d in ('crossref_works', 'crossref_bibliographic', 'crossref_failures')
                   for p in (BASE / d).glob('*') if p.is_file())
    named = {r['raw_path'] for r in receipts if r.get('raw_path')} | {a['error_path'] for r in receipts for a in r.get('attempts', []) if a.get('error_path')}
    check('all_saved_hashes_verify', not bad, {'hash_checks': n_files, 'failures': bad})
    check('every_saved_file_has_a_receipt', set(saved) <= named, sorted(set(saved) - named))

    # 1. recount
    st = Counter(l['resolution']['status'] for l in links)
    resolved = [l for l in links if st and l['resolution']['status'] in ('RESOLVED_PRINTED_DOI', 'RESOLVED_BIBLIOGRAPHIC')]
    rdois = {l['resolution']['crossref_metadata']['doi'].lower() for l in resolved}
    m_occ = [l for l in resolved if l['resolution']['openalex_union']['matched']]
    m_dois = {l['resolution']['crossref_metadata']['doi'].lower() for l in m_occ}
    final = {}
    for r in receipts:
        final[r['request_key']] = r
    attempts = [a for r in receipts for a in r.get('attempts', [])]
    recount = {
        'occurrences': len(links),
        'occurrences_by_input': dict(Counter(l['source_input'] for l in links)),
        'occurrences_by_document': dict(Counter(l['document_id'] for l in links)),
        'occurrences_with_printed_doi': sum(bool(l['printed_dois_as_transcribed']) for l in links),
        'status': dict(st),
        'resolved_doi_occurrences': len(resolved),
        'resolved_doi_occurrences_by_route': dict(Counter(l['resolution']['status'] for l in resolved)),
        'resolved_distinct_dois': len(rdois),
        'matched_to_openalex_union_occurrences': len(m_occ),
        'matched_to_openalex_union_distinct_dois': len(m_dois),
        'new_to_union_distinct_dois': len(rdois - m_dois),
        'new_to_union_occurrences': len(resolved) - len(m_occ),
        'conflicts': st.get('CONFLICT', 0),
        'candidates': st.get('CANDIDATE', 0),
        'candidates_by_class': dict(Counter(l['resolution'].get('candidate_class') for l in links if l['resolution']['status'] == 'CANDIDATE')),
        'unresolved': st.get('UNRESOLVED', 0),
        'resolved_with_review_flags': sum(bool(l['resolution'].get('review_flags')) for l in links if l['resolution']['status'] in ('RESOLVED_PRINTED_DOI', 'RESOLVED_BIBLIOGRAPHIC')),
        'unresolved_by_reason': dict(Counter(l['resolution'].get('unresolved_reason') for l in links if l['resolution']['status'] == 'UNRESOLVED')),
        'identity_not_established_total_candidate_plus_unresolved': st.get('CANDIDATE', 0) + st.get('UNRESOLVED', 0),
        'request_keys': len(final),
        'request_keys_by_final_status': dict(Counter(r['status'] for r in final.values())),
        'failed_requests_final': sum(r['status'] not in OK for r in final.values()),
        'http_attempts_total': len(attempts),
        'http_attempt_status_counts': dict(Counter(str(a.get('http_status', 'NETWORK_ERROR')) for a in attempts)),
        'discovery_generation_values': sorted({l['discovery_generation'] for l in links}),
        'seeds_further_expansion_true': sum(l['seeds_further_expansion'] for l in links),
        'eligibility_decisions': sum(l['eligibility_status'] != 'NOT_SCREENED' for l in links),
        'method_coded_records': sum(l['method_coding_status'] != 'NOT_CODED' for l in links),
    }
    for k, v in recount.items():
        check('summary_count:' + k, summary['counts'].get(k) == v, None if summary['counts'].get(k) == v else {'summary': summary['counts'].get(k), 'recount': v})
    check('summary_has_no_uncounted_keys', set(summary['counts']) == set(recount), sorted(set(summary['counts']) ^ set(recount)))
    check('status_partition_sums_to_occurrences', sum(st.values()) == len(links))
    check('conflict_list_matches', sorted(summary['conflict_occurrences']) == sorted(l['occurrence_id'] for l in links if l['resolution']['status'] == 'CONFLICT'))
    check('new_to_union_list_matches', summary['new_to_union_dois'] == sorted(rdois - m_dois))
    # union membership re-derived for resolved DOIs from the local union file
    union = {}
    with (ROOT / summary['openalex_union']['path']).open(encoding='utf-8') as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                for v in r.get('metadata_variants') or []:
                    d = ((v.get('metadata') or {}).get('doi') or '').lower().replace('https://doi.org/', '')
                    if d:
                        union.setdefault(d, set()).add(r['provider_id'])
    wrong = [l['occurrence_id'] for l in links if l['resolution'].get('openalex_union')
             and sorted(union.get(l['resolution']['openalex_union']['doi_checked'], [])) != l['resolution']['openalex_union']['openalex_ids']]
    check('openalex_union_matches_rederived', not wrong, wrong[:20])
    # resolved records must carry the registered /works fields
    need = ('title', 'authors', 'container_title', 'type', 'identifiers', 'dates')
    missing = [l['occurrence_id'] for l in resolved + [x for x in links if x['resolution']['status'] == 'CONFLICT']
               if not all(k in l['resolution']['crossref_metadata'] for k in need)
               or not l['resolution']['crossref_works_receipt'].get('sha256')]
    check('resolved_and_conflict_records_carry_works_fields_and_receipt', not missing, missing)
    out = {'checked_utc': datetime.now(timezone.utc).isoformat(), 'all_pass': all(c['pass'] for c in checks),
           'check_count': len(checks), 'failed': [c for c in checks if not c['pass']],
           'input_sha256_before': before, 'input_sha256_after': after,
           'shell_measured_before': SHELL_MEASURED_BEFORE, 'recount': recount, 'checks': checks}
    (BASE / 'self_check.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('all_pass', out['all_pass'], 'checks', len(checks), 'failed', [c['check'] for c in out['failed']])


if __name__ == '__main__':
    main()
