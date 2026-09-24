"""Step 2: exact-DOI repository lookups (OSTI records API, Europe PMC) for every case DOI.

These are identifier lookups (doi:<x>), not topical searches. No OpenAlex.
"""
import json
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from httpfetch import get, q, ROOT  # noqa: E402

CASES = json.loads((ROOT / "case_list.json").read_text(encoding="utf-8"))
out = []
for c in CASES["cases"]:
    doi = c["doi"]
    row = {"case_id": c["case_id"], "doi": doi}
    rec, body = get(f"https://www.osti.gov/api/v1/records?doi={q(doi)}", f"osti_{doi}", ext=".json", accept="application/json")
    row["osti_receipt"] = rec
    if body and rec["status"] == 200:
        try:
            j = json.loads(body)
            row["osti_hits"] = [
                {"osti_id": h.get("osti_id"), "title": h.get("title"), "doi": h.get("doi"),
                 "links": h.get("links"), "publication_date": h.get("publication_date")}
                for h in j if (h.get("doi") or "").lower() == doi.lower()
            ]
        except Exception as e:
            row["osti_parse_error"] = repr(e)
    rec2, body2 = get(
        f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:%22{q(doi)}%22&format=json&resultType=core",
        f"epmc_{doi}", ext=".json")
    row["epmc_receipt"] = rec2
    if body2 and rec2["status"] == 200:
        j = json.loads(body2)
        row["epmc_hits"] = [
            {"pmcid": h.get("pmcid"), "doi": h.get("doi"), "title": h.get("title"),
             "isOpenAccess": h.get("isOpenAccess"), "hasSuppl": h.get("hasSuppl"),
             "firstPublicationDate": h.get("firstPublicationDate")}
            for h in j.get("resultList", {}).get("result", []) if (h.get("doi") or "").lower() == doi.lower()
        ]
    out.append(row)
    print(c["case_id"], doi, "osti", rec["status"], len(row.get("osti_hits", [])), "epmc", rec2["status"], row.get("epmc_hits"))

(ROOT / "repository_lookup.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
