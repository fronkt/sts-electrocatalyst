"""Sun, Reuter & Scheffler, Phys. Rev. B 70, 235402 (2004): record and claim check.

The MPG repository supplies an archived copy of the published article. Its
identity and quoted passages are checked directly; aggregate access labels do
not override readable primary evidence. The arXiv preprint is retained as a
separate source, with its own identity checks and page locators.
"""
from __future__ import annotations

import html
import re
import urllib.parse
from datetime import date

from .common import Fetcher, cache_key, pdf_text_pages, read_lines, rel, sha256_file
from .registry import lookup
from .textnorm import fold

DOI = "10.1103/physrevb.70.235402"
ARXIV_ID = "cond-mat/0309714v1"
ARXIV_API = "https://export.arxiv.org/api/query?"
ARXIV_PDF = "https://arxiv.org/pdf/" + ARXIV_ID
APS_ABSTRACT = "https://journals.aps.org/prb/abstract/10.1103/PhysRevB.70.235402"
VOR_PDF = "https://pure.mpg.de/rest/items/item_739138_2/component/file_2052691/content"
OPENALEX = "https://api.openalex.org/works/doi:" + DOI
S2 = ("https://api.semanticscholar.org/graph/v1/paper/DOI:" + DOI +
      "?fields=title,externalIds,publicationDate,openAccessPdf,journal")

QUOTES = {
    "symmetry_breaking_allowed": r"the structural relaxation allowed for any symmetry breaking at the surface\.",
    "crucial": r"This was found to be crucial to obtain the correct energetics and structures",
    "tilt_energy": r"the energy gain by the tilting is 0\.1 eV/H atom compared to the higher-symmetry, up-? ?right configuration",
}

CITE_RE = re.compile(r"Sun[,/ ]+(?:&\s*)?Reuter|235402")

CLEARED, EXCLUDED = "CLEARED", "EXCLUDED"      # docs/43 :1945 "each cleared or excluded"
SUB_STATEMENT = "SUN-crucial-statement-by-these-authors"
SUB_VERSION_OF_RECORD = "SUN-same-wording-in-PRB-70-235402"

MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July",
                                       "August", "September", "October", "November", "December"], 1)}


LIGATURES = {"ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl"}


def normalise_pdf_text(t: str) -> str:
    for k, v in LIGATURES.items():
        t = t.replace(k, v)
    t = re.sub(r"-\n(?=[a-z])", "", t)       # de-hyphenate line breaks
    t = re.sub(r"\s+", " ", t)
    return t


def find_quotes(pages: list[str]) -> dict:
    out = {}
    norm = [normalise_pdf_text(p) for p in pages]
    for key, pat in QUOTES.items():
        rx = re.compile(pat)
        hit = None
        for i, t in enumerate(norm, 1):
            m = rx.search(t)
            if m:
                s = max(0, m.start() - 260)
                hit = {"page": i, "match": m.group(0), "context": t[s:m.end() + 200]}
                break
        out[key] = hit
    return out


def version_of_record_checks(pages: list[str]) -> dict:
    """Require the journal header, DOI and authors on the PDF's first page.

    A matching quotation alone does not identify a manuscript as the published
    version. These independent identity checks fail closed for the preprint.
    """
    first = normalise_pdf_text(pages[0]) if pages else ""
    return {
        "journal_volume_article_year": bool(re.search(
            r"PHYSICAL REVIEW B\s+70,?\s+235402\s*\(?2004\)?", first, re.I)),
        "doi": DOI.lower() in first.lower(),
        "author_names": all(name in first for name in
                            ("Qiang Sun", "Karsten Reuter", "Matthias Scheffler")),
    }


def parse_arxiv_atom(xml: str) -> dict:
    entry = xml.split("<entry>", 1)[1] if "<entry>" in xml else ""

    def tag(name):
        m = re.search(rf"<{name}[^>]*>(.*?)</{name}>", entry, re.S)
        return html.unescape(re.sub(r"\s+", " ", m.group(1)).strip()) if m else ""
    authors = [html.unescape(a.strip()) for a in re.findall(r"<name>(.*?)</name>", entry, re.S)]
    return {"id": tag("id"), "title": tag("title"), "published": tag("published"),
            "summary": tag("summary"), "authors": authors,
            "journal_ref": tag("arxiv:journal_ref"), "doi": tag("arxiv:doi"),
            "comment": tag("arxiv:comment")}


def parse_aps_page(page: str) -> dict:
    text = html.unescape(re.sub(r"<[^>]+>", " ", page))
    text = re.sub(r"\s+", " ", text)
    rec = re.search(r"Received (\d{1,2}) (\w+) (\d{4})", text)
    pub = re.search(r"Published (\d{1,2}) (\w+),? (\d{4})", text)
    desc = re.search(r'<meta content="([^"]*)" property="og:description"', page) or \
        re.search(r'<meta property="og:description" content="([^"]*)"', page)

    def d(m):
        return date(int(m.group(3)), MONTHS[m.group(2)], int(m.group(1))).isoformat() if m else None
    abstract = html.unescape(desc.group(1)) if desc else ""
    return {"received": d(rec), "published": d(pub), "abstract": abstract}


def _tokens(s: str) -> set:
    s = re.sub(r"\$[^$]*\$", " ", s)            # drop inline TeX
    s = re.sub(r"\\mathrm\{[^}]*\}", " ", s)
    return {w for w in re.findall(r"[a-z]+", s.lower()) if len(w) > 3}


def jaccard(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    return round(len(ta & tb) / max(1, len(ta | tb)), 3)


def citing_lines(paths) -> list[dict]:
    rows = []
    for p in paths:
        for i, t in enumerate(read_lines(p), 1):
            for m in CITE_RE.finditer(t):
                s = max(0, m.start() - 220)
                rows.append({"file": rel(p), "line": i, "match": m.group(0),
                             "excerpt": t[s:m.end() + 220]})
                break
    return rows


def run(fetch_crossref: Fetcher, fetch_src: Fetcher, fetch_arxiv: Fetcher, cite_paths) -> dict:
    rec = lookup(fetch_crossref, DOI)
    q = urllib.parse.urlencode({"id_list": re.sub(r"v\d+$", "", ARXIV_ID)})
    arx = fetch_arxiv.get(ARXIV_API + q, cache_key(q, "arxiv_api_"), "xml",
                          accept="application/atom+xml")
    # arXiv answers 406 when the colons are percent-encoded; keep them literal
    disc_q = "search_query=ti:RuO2+AND+au:Reuter&max_results=20"
    disc = fetch_arxiv.get(ARXIV_API + disc_q, cache_key(disc_q, "arxiv_api_"), "xml",
                           accept="application/atom+xml")
    pdf = fetch_arxiv.get(ARXIV_PDF, "arxiv_cond-mat_0309714v1", "pdf")
    vor_pdf = fetch_src.get(VOR_PDF, "mpg_prb_70_235402", "pdf")
    aps = fetch_src.get(APS_ABSTRACT, "aps_prb_70_235402_abstract", "html",
                        headers={"User-Agent": "Mozilla/5.0"})
    oa = fetch_src.get(OPENALEX, cache_key(DOI, "openalex_"), "json")
    s2 = fetch_src.get(S2, cache_key(DOI, "semanticscholar_"), "json")

    arxiv = parse_arxiv_atom(arx.text())
    disc_titles = re.findall(r"<title>(.*?)</title>", disc.text(), re.S)[1:]
    aps_meta = parse_aps_page(aps.text()) if aps.status == 200 else {}
    pages = pdf_text_pages(pdf.body_path)
    quotes = find_quotes(pages)
    vor_pages = pdf_text_pages(vor_pdf.body_path) if vor_pdf.status == 200 else []
    vor_identity = version_of_record_checks(vor_pages)
    vor_quotes = find_quotes(vor_pages)
    vor_tied = vor_pdf.status == 200 and all(vor_identity.values())
    vor_found = all(vor_quotes[k] for k in ("symmetry_breaking_allowed", "crucial"))
    vor_ok = vor_tied and vor_found
    vor = {
        "url": VOR_PDF, "status": vor_pdf.status,
        "pdf_cache_file": vor_pdf.body_path.name,
        "sha256": sha256_file(vor_pdf.body_path), "pdf_pages": len(vor_pages),
        "identity_checks": vor_identity, "identified_as_version_of_record": vor_tied,
        "quotes": vor_quotes,
    }
    oa_j = oa.json() if oa.status == 200 else {}
    s2_j = s2.json() if s2.status == 200 else {}

    cr_fams = [fold(a.get("family")) for a in rec.authors]
    ax_fams = [fold(n.split()[-1]) for n in arxiv["authors"]]
    received = aps_meta.get("received")
    posted = arxiv["published"][:10] if arxiv["published"] else None
    lag = (date.fromisoformat(posted) - date.fromisoformat(received)).days if received and posted else None
    identity = {
        "author_families_crossref": cr_fams, "author_families_arxiv": ax_fams,
        "authors_identical_in_order": cr_fams == ax_fams,
        "aps_received": received, "aps_published": aps_meta.get("published"),
        "arxiv_posted": posted, "arxiv_posted_minus_aps_received_days": lag,
        "abstract_token_jaccard_arxiv_vs_aps": jaccard(arxiv["summary"], aps_meta.get("abstract", "")),
        "arxiv_journal_ref": arxiv["journal_ref"], "arxiv_doi": arxiv["doi"],
    }
    tied = identity["authors_identical_in_order"] and lag is not None and 0 <= lag <= 60 and \
        identity["abstract_token_jaccard_arxiv_vs_aps"] >= 0.5
    access = {
        "openalex_is_oa": (oa_j.get("open_access") or {}).get("is_oa"),
        "openalex_oa_status": (oa_j.get("open_access") or {}).get("oa_status"),
        "openalex_any_repository_has_fulltext": (oa_j.get("open_access") or {}).get(
            "any_repository_has_fulltext"),
        "semanticscholar_open_access_status": (s2_j.get("openAccessPdf") or {}).get("status"),
        "aps_abstract_page_status": aps.status,
    }
    all_found = all(quotes[k] for k in ("symmetry_breaking_allowed", "crucial"))
    subclaims = [
        {"id": SUB_STATEMENT,
         "text": "Sun, Reuter & Scheffler state that a structural relaxation allowing any symmetry breaking at "
                 "the RuO2(110) surface was crucial to obtain the correct energetics and structures.",
         "verdict": CLEARED if (vor_ok or (all_found and tied)) else EXCLUDED,
         "basis": (f"PRB 70, 235402 (2004), p. 235402-{vor_quotes['crucial']['page']}: "
                   "published article archived by the MPG repository; PDF identity and wording checked") if vor_ok else
                  (f"arXiv:{ARXIV_ID}, p. {quotes['crucial']['page']}: the authors' submitted manuscript of "
                   "PRB 70, 235402, tied to the record by identity_checks") if (all_found and tied) else
                  ("quote not found in the preprint" if not all_found else
                   "preprint not tied to the record by identity_checks")},
        {"id": SUB_VERSION_OF_RECORD,
         "text": "The same sentence appears in the version of record, Phys. Rev. B 70, 235402 (2004).",
         "verdict": CLEARED if vor_ok else EXCLUDED,
         "basis": (f"PRB 70, 235402 (2004), p. 235402-{vor_quotes['crucial']['page']}: "
                   "the same wording is present in the MPG-hosted published PDF") if vor_ok else
                  ("published PDF identity checks failed" if not vor_tied else
                   "the required wording was not found in the published PDF")},
    ]
    return {
        "crossref": {"doi": rec.doi, "status": rec.status, "title": rec.title,
                     "authors": [a.get("given", "") + " " + a.get("family", "") for a in rec.authors],
                     "journal": rec.journal, "volume": rec.volume, "article_number": rec.pages,
                     "year": rec.year, "published_online": rec.year_online, "type": rec.type,
                     "cache_file": rec.cache_file},
        "bibliographic_record_matches_repo_citation": {
            "authors": [f.title() for f in cr_fams] == ["Sun", "Reuter", "Scheffler"],
            "journal_is_phys_rev_b": rec.journal == "Physical Review B",
            "volume_70": rec.volume == "70", "article_235402": rec.pages == "235402",
            "year_2004": rec.year == 2004},
        "arxiv": {k: arxiv[k] for k in ("id", "title", "published", "authors", "journal_ref", "doi",
                                        "comment")},
        "arxiv_discovery_query": {"query": "ti:RuO2 AND au:Reuter", "titles": [
            re.sub(r"\s+", " ", t).strip() for t in disc_titles]},
        "aps_abstract_page": aps_meta | {"cache_file": aps.body_path.name},
        "identity_checks": identity, "preprint_tied_to_record": tied,
        "access": access, "quotes": quotes, "pdf_pages": len(pages),
        "version_of_record": vor,
        "pdf_cache_file": pdf.body_path.name,
        "subclaims": subclaims,
        "claim_verdicts": {s["id"]: s["verdict"] for s in subclaims},
        "citing_lines": citing_lines(cite_paths),
    }
