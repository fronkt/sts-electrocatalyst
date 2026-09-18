"""The +0.40 eV *OOH ZPE - TS constant: where it is, and where it is not.

Reads (i) the Man 2011 PDF text, (ii) Divanis 2020 ESI Table SI-1 (hash-checked
against the committed SHA256SUMS), (iii) the in-repo constant and its stated
attribution, and records the open-access status of every candidate primary
source. The implied adsorbate ZPE - TS for *OOH is derived from the Table SI-1
molecule columns so the convention behind +0.40 is explicit:

    corr_X = [ZPE(X*) - TS(X*)] + sum_j nu_j [ZPE(j) - TS(j)]   (j = H2O, H2)

with the CHE references of ``src/hea_oer/referencing.py``:
*OH vs H2O - 1/2 H2, *O vs H2O - H2, *OOH vs 2 H2O - 3/2 H2.
"""
from __future__ import annotations

import re

from .common import Fetcher, cache_key, pdf_text_pages, read_lines, rel, sha256_file, REPO
from .registry import lookup

MAN2011_PDF = REPO / "docs/research/papers/man2011.pdf"
DIVANIS_TXT = REPO / "docs/research/2026-08-15-sampling/divanis_esi.txt"
DIVANIS_SUMS = REPO / "docs/research/2026-08-15-sampling/SHA256SUMS"
REFERENCING = REPO / "src/hea_oer/referencing.py"

# CHE reference stoichiometry: adsorbate X is formed from nu_H2O H2O with nu_H2 H2 released
REF = {"OH": {"H2O": 1.0, "H2": -0.5}, "O": {"H2O": 1.0, "H2": -1.0}, "OOH": {"H2O": 2.0, "H2": -1.5}}

CANDIDATES = [
    {"label": "Norskov et al. 2004", "doi": "10.1021/jp047349j", "why": "ref [25] of the Divanis ESI; Table SI-1 attributed to it"},
    {"label": "Man et al. 2011", "doi": "10.1002/cctc.201000397", "why": "named in src/hea_oer/referencing.py"},
    {"label": "Valdes et al. 2008", "doi": "10.1021/jp711929d", "why": "named in src/hea_oer/referencing.py"},
    {"label": "Rossmeisl, Logadottir & Norskov 2005", "doi": "10.1016/j.chemphys.2005.05.038", "why": "OER-on-metal-oxide CHE precursor of Man 2011"},
    {"label": "Rossmeisl et al. 2007", "doi": "10.1016/j.jelechem.2006.11.008", "why": "rutile OER CHE study cited in docs/28"},
]
MAN2011_SI_URL = ("https://chemistry-europe.onlinelibrary.wiley.com/action/downloadSupplement?"
                  "doi=10.1002%2Fcctc.201000397&file=cctc_201000397_sm_miscellaneous_information.pdf")


def _num(tok: str) -> float:
    return float(tok.replace(",", "."))


def parse_table_si1(lines: list[str]) -> dict:
    """Rows of Divanis ESI Table SI-1 (comma decimals) keyed by row label."""
    start = next(i for i, t in enumerate(lines) if t.strip().startswith("Table SI-1"))
    header_i = next(i for i in range(start + 1, len(lines)) if "ZPE" in lines[i])
    rows, order = {}, []
    num = re.compile(r"-?\d+,\d+|(?<![\w,])0(?![\w,])")
    for t in lines[header_i + 1:]:
        if not t.strip():
            if rows:
                break
            continue
        m = num.search(t)
        if not m:
            break
        label = t[:m.start()].strip()
        vals = [_num(x) for x in num.findall(t[m.start():])]
        rows[label] = vals
        order.append(label)
    return {"table_line": start + 1, "header": lines[header_i].strip(), "rows": rows, "order": order}


def species_columns(table: dict) -> dict:
    """Per-species TS and ZPE from the single-species rows.

    Two-value rows (H2, 1/2 O2, O*, HO*, H*) are (TS, ZPE); the H2O row is
    (TS, TdS, ZPE, dZPE, dZPE - TdS).
    """
    r = table["rows"]
    out = {"H2O": {"TS": r["H2O"][0], "ZPE": r["H2O"][2]}}
    for lab, key in (("H2", "H2"), ("O*", "O*"), ("HO*", "HO*"), ("H*", "H*"), ("½ O2", "1/2 O2")):
        if lab in r and len(r[lab]) == 2:
            out[key] = {"TS": r[lab][0], "ZPE": r[lab][1]}
    return out


def corr_from_species(ads_zpe_minus_ts: float, species: str, cols: dict) -> float:
    """dZPE - TdS for forming ``species`` from its CHE references."""
    ref = REF[species]
    ref_term = sum(nu * (cols[j]["ZPE"] - cols[j]["TS"]) for j, nu in ref.items())
    return ads_zpe_minus_ts - ref_term


def implied_adsorbate(corr: float, species: str, cols: dict) -> float:
    ref = REF[species]
    return corr + sum(nu * (cols[j]["ZPE"] - cols[j]["TS"]) for j, nu in ref.items())


def pdf_token_census(pages: list[str], tokens: list[str]) -> dict:
    out = {}
    for tok in tokens:
        hits = []
        rx = re.compile(tok, re.I)
        for i, t in enumerate(pages, 1):
            flat = re.sub(r"\s+", " ", t)
            for m in rx.finditer(flat):
                hits.append({"page": i, "context": flat[max(0, m.start() - 90):m.end() + 90]})
        out[tok] = {"n": len(hits), "hits": hits}
    return out


def repo_constant() -> dict:
    lines = read_lines(REFERENCING)
    i = next(k for k, t in enumerate(lines, 1) if t.startswith("ZPE_TS_CORRECTION"))
    m = re.search(r'"OH":\s*([\d.]+),\s*"O":\s*([\d.]+),\s*"OOH":\s*([\d.]+)', lines[i - 1])
    attrib = [f"{rel(REFERENCING)}:{k}: {t.strip()}" for k, t in enumerate(lines, 1)
              if re.search(r"Man et al|Vald", t)]
    return {"file": rel(REFERENCING), "line": i, "text": lines[i - 1].strip(),
            "OH": float(m.group(1)), "O": float(m.group(2)), "OOH": float(m.group(3)),
            "attribution_lines": attrib}


DOCS43 = REPO / "docs/43-prereg-week1-factorial.md"


def registered_delta() -> dict:
    """The registered delta axis, read from docs/43 A9.3.4."""
    for i, t in enumerate(read_lines(DOCS43), 1):
        m = re.search(r"δ = corr_OOH − (\d+\.\d+) eV, δ ∈ \[(\d+\.\d+), (\d+\.\d+)\] eV", t)
        if m:
            return {"file": rel(DOCS43), "line": i, "text": m.group(0),
                    "reference_eV": float(m.group(1)), "range_eV": [float(m.group(2)), float(m.group(3))]}
    raise ValueError("registered delta definition not found in docs/43")


def run(fetch_crossref: Fetcher, fetch_src: Fetcher) -> dict:
    pages = pdf_text_pages(MAN2011_PDF)
    man = pdf_token_census(pages, [r"0\.40", r"0\.35", r"0\.05", r"zero[- ]point", r"\bZPE\b",
                                   r"entrop", r"\bTable\b", r"Supporting Information"])
    sums = {ln.split()[1].lstrip("*"): ln.split()[0] for ln in read_lines(DIVANIS_SUMS) if ln.strip()}
    div_sha = sha256_file(DIVANIS_TXT)
    table = parse_table_si1(read_lines(DIVANIS_TXT))
    cols = species_columns(table)
    rows = table["rows"]
    has_ooh_row = any("OOH" in lab for lab in rows)
    tab_corr = {"OH": rows["*OH + ½ H2"][4], "O": rows["*O + H2"][4]}
    recomputed = {
        "OH": corr_from_species(cols["HO*"]["ZPE"] - cols["HO*"]["TS"], "OH", cols),
        "O": corr_from_species(cols["O*"]["ZPE"] - cols["O*"]["TS"], "O", cols)}
    const = repo_constant()
    reg = registered_delta()
    implied = {
        "OOH_adsorbate_ZPE_minus_TS_for_repo_constant": implied_adsorbate(const["OOH"], "OOH", cols),
        "OOH_adsorbate_ZPE_minus_TS_for_corr_equal_OH_row": implied_adsorbate(tab_corr["OH"], "OOH", cols),
        "delta_repo_constant": const["OOH"] - reg["reference_eV"],
    }
    access = []
    for c in CANDIDATES:
        rec = lookup(fetch_crossref, c["doi"])
        oa = fetch_src.get("https://api.openalex.org/works/doi:" + c["doi"],
                           cache_key(c["doi"], "openalex_"), "json")
        oaj = oa.json() if oa.status == 200 else {}
        access.append({**c, "crossref_title": rec.title, "crossref_journal": rec.journal,
                       "crossref_volume": rec.volume, "crossref_pages": rec.pages,
                       "crossref_year": rec.year,
                       "openalex_oa_status": (oaj.get("open_access") or {}).get("oa_status"),
                       "openalex_repository_fulltext": (oaj.get("open_access") or {}).get(
                           "any_repository_has_fulltext"),
                       "main_text_pdf_on_disk": c["doi"] == "10.1002/cctc.201000397"})
    si = fetch_src.get(MAN2011_SI_URL, "wiley_man2011_si_attempt", "html",
                       headers={"User-Agent": "Mozilla/5.0"})
    return {
        "man2011_pdf": {"path": rel(MAN2011_PDF), "sha256": sha256_file(MAN2011_PDF),
                        "pages": len(pages), "token_census": man},
        "man2011_si_fetch": {"url": MAN2011_SI_URL, "status": si.status,
                             "content_type": si.content_type,
                             "cloudflare_challenge": b"Just a moment" in si.body},
        "divanis_table_si1": {"path": rel(DIVANIS_TXT), "sha256": div_sha,
                              "sha256_matches_SHA256SUMS": sums.get("divanis_esi.txt") == div_sha,
                              "line": table["table_line"], "header": table["header"],
                              "rows": rows, "row_order": table["order"],
                              "has_OOH_row": has_ooh_row, "attributed_to": "ref [25] = Norskov et al., "
                              "J. Phys. Chem. B 2004, 108, 17886-17892 (divanis_esi.txt)"},
        "species_columns_from_table": cols,
        "corr_tabulated": tab_corr,
        "corr_recomputed_from_species_columns": recomputed,
        "repo_constant": const,
        "registered_delta": reg,
        "implied": implied,
        "candidate_primary_sources": access,
    }
