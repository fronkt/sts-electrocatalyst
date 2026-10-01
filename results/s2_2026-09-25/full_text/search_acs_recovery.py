"""Focused public Figshare indexed-DOI search, not repeated resource_doi filtering.

Never assigns eligibility or downloads a file; all hits require identity review.
"""
import csv
import json
import pathlib
import time

import requests

HERE = pathlib.Path(__file__).resolve().parent
IDS = {"S00759", "S01354", "S04318", "S08806", "S29447", "S29721"}


def main():
    out = HERE / "evidence_recovery_2026-10-01" / "acs_routes.json"
    if out.exists():
        print("Existing dated search retained; do not repeat")
        return
    rows = []
    for r in csv.DictReader((HERE / "si_checklist.csv").open(encoding="utf-8")):
        if r["screen_id"] not in IDS:
            continue
        time.sleep(1)
        query = {"search_for": '"' + r["doi"] + '"', "page_size": 20}
        resp = requests.post("https://api.figshare.com/v2/articles/search", json=query, timeout=30)
        resp.raise_for_status()
        hits = resp.json()
        matching = [h for h in hits if (h.get("resource_doi") or "").lower() == r["doi"].lower()
                    or (h.get("doi") or "").lower().startswith(r["doi"].lower() + ".s")]
        rows.append({"screen_id": r["screen_id"], "doi": r["doi"], "title": r["title"],
                     "prior_attempt": "2026-09-28 Figshare resource_doi lookup NO_ITEM; si_public_log.jsonl",
                     "route": "public Figshare indexed exact-DOI search", "api_url": "https://api.figshare.com/v2/articles/search",
                     "query": query, "http": resp.status_code, "hits_returned": len(hits),
                     "status": "MATCH_REQUIRES_REVIEW" if matching else "NO_MATCH_IN_RETURNED_RESULTS",
                     "matching_items": matching,
                     "note": "No absence-of-SI inference. ACS publisher requests returned 403 in this continuation; no alternate publisher bypass."})
        print(r["screen_id"], len(hits), len(matching), flush=True)
    out.write_text(json.dumps(rows, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
