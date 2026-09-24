"""Part B: re-attempt the 17 unresolved complementary identity keys.

For each key: Crossref /works/{doi} for any recorded candidate DOI, and one Crossref
query.bibliographic request built only from the text the source occurrence actually gives
(label + disambiguating context words). A canonical identity is accepted only on full agreement
of title + first author + year + venue with what the occurrence states; otherwise the key stays
UNRESOLVED. All raw responses are saved and hashed; nothing is merged or deleted.
"""
import json
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from httpfetch import get, q, MAILTO, ROOT  # noqa: E402

REPO = ROOT.parents[2]
SRC = REPO / "results/s2_2026-09-20/complementary_identity_review/unresolved_identities.jsonl"
QUERIES = {
    "Paz": None,
    "Holm": "Holm sequentially rejective multiple test procedure",
    "Nabat": None,
    "Dickens": "Dickens Norskov theoretical investigation role of surface defects oxygen evolution RuO2",
    "program books": None,
    "Reuter & Scheffler": "Reuter Scheffler ab initio atomistic thermodynamics",
    "Otani": "Otani ESM-RISM tutorial",
    "AFLOW": "AFLOW",
    "Alexandria": "Alexandria materials database",
    "MP Crystalium": "MP Crystalium",
    "MPtrj": "MPtrj",
    "ODAC23": "ODAC23",
    "OMat24": "OMat24",
    "OMC25": "OMC25",
    "OMol25": "OMol25",
    "OQMD": "OQMD",
    "hp.x manual": "hp.x Hubbard parameters Quantum ESPRESSO manual",
}

out = []
for line in SRC.read_text(encoding="utf-8").splitlines():
    u = json.loads(line)
    lab = u["source_labels"][0]
    row = {"source_identity": u["source_identity"], "source_labels": u["source_labels"],
           "source_occurrence_ids": u["source_occurrence_ids"], "prior_status": u["identity_status"],
           "prior_candidates": u["candidate_identities"], "works_lookups": [], "bibliographic_query": None}
    for cand in u["candidate_identities"]:
        if cand.startswith("doi:"):
            doi = cand[4:]
            rec, body = get(f"https://api.crossref.org/works/{q(doi)}?mailto={MAILTO}", f"idB_works_{doi}", ext=".json")
            ent = {"doi": doi, "receipt": rec}
            if body and rec["status"] == 200:
                m = json.loads(body)["message"]
                ent["metadata"] = {"title": m.get("title"), "first_author": (m.get("author") or [{}])[0].get("family"),
                                   "authors": [(a.get("given"), a.get("family")) for a in m.get("author", [])],
                                   "container": m.get("container-title"), "type": m.get("type"),
                                   "published_online": m.get("published-online"), "published_print": m.get("published-print"),
                                   "volume": m.get("volume"), "page": m.get("page")}
            row["works_lookups"].append(ent)
    qs = QUERIES.get(lab)
    if qs:
        rec, body = get(f"https://api.crossref.org/works?query.bibliographic={q(qs)}&rows=5&mailto={MAILTO}",
                        f"idB_query_{lab}", ext=".json")
        ent = {"query": qs, "receipt": rec, "top": []}
        if body and rec["status"] == 200:
            for it in json.loads(body)["message"]["items"]:
                ent["top"].append({"doi": it.get("DOI"), "title": it.get("title"),
                                   "first_author": (it.get("author") or [{}])[0].get("family"),
                                   "year": (it.get("issued", {}).get("date-parts") or [[None]])[0][0],
                                   "container": it.get("container-title"), "score": it.get("score")})
        row["bibliographic_query"] = ent
    else:
        row["bibliographic_query"] = {"query": None, "reason": "occurrence supplies no searchable bibliographic string beyond a bare surname/collective noun"}
    out.append(row)
    print(lab, [w["receipt"]["status"] for w in row["works_lookups"]], (row["bibliographic_query"] or {}).get("receipt", {}).get("status"))

(ROOT / "identity_crossref_attempts.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
