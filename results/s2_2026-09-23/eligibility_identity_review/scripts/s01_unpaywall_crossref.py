"""Step 1: Unpaywall + exact Crossref /works/{doi} for every unresolved eligibility case DOI.

Legal-access discovery only. No OpenAlex. No search queries.
Writes access_discovery.json summarising OA locations per DOI.
"""
import json
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from httpfetch import get, q, MAILTO, ROOT  # noqa: E402

CASES = json.loads((ROOT / "case_list.json").read_text(encoding="utf-8"))

out = []
dois = []
for c in CASES["cases"]:
    dois.append(c["doi"])
    dois.extend(c.get("linked_version_dois", []))
seen = set()
for doi in dois:
    if doi in seen:
        continue
    seen.add(doi)
    row = {"doi": doi}
    rec, body = get(f"https://api.unpaywall.org/v2/{q(doi)}?email={MAILTO}", f"unpaywall_{doi}", ext=".json")
    row["unpaywall_receipt"] = rec
    if body and rec["status"] == 200:
        j = json.loads(body)
        row["is_oa"] = j.get("is_oa")
        row["oa_locations"] = [
            {k: loc.get(k) for k in ("url", "url_for_pdf", "url_for_landing_page", "host_type", "version", "license", "repository_institution")}
            for loc in (j.get("oa_locations") or [])
        ]
    rec2, body2 = get(f"https://api.crossref.org/works/{q(doi)}?mailto={MAILTO}", f"crossref_{doi}", ext=".json")
    row["crossref_receipt"] = rec2
    if body2 and rec2["status"] == 200:
        m = json.loads(body2)["message"]
        row["crossref"] = {
            "title": m.get("title"),
            "authors": [(a.get("given"), a.get("family")) for a in m.get("author", [])],
            "container": m.get("container-title"),
            "type": m.get("type"),
            "published_online": m.get("published-online"),
            "published_print": m.get("published-print"),
            "posted": m.get("posted"),
            "created": m.get("created", {}).get("date-time"),
            "relation": m.get("relation"),
            "links": [l.get("URL") for l in m.get("link", [])],
        }
    out.append(row)
    print(doi, rec["status"], row.get("is_oa"), len(row.get("oa_locations", [])), rec2["status"])

(ROOT / "access_discovery.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
