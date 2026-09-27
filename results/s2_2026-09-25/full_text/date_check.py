"""E2 date check (ruling 10, 2026-09-27) for every record still in play.

  python date_check.py

Records: any pass, third read or v4 read marked ELIGIBLE; every record whose v3 or v4 decision in
reconcile/current_state.csv is ELIGIBLE, NEEDS_SI, UNRESOLVED or EXCLUDE:E2; and the journal-article
primary of each such record's version group (reconcile/version_groups.csv).
First publication date (ruling 10): the publisher's first-online or print date as carried in the
DOI-matched Crossref record (earliest of the two); OpenAlex publication_date only when Crossref has
neither, and otherwise as corroboration.  Received/accepted dates and DOI years are never used.
Flags: OUTSIDE_WINDOW (first publication outside 2011-01-01 .. 2026-09-18),
SOURCES_STRADDLE_BOUNDARY (Crossref and OpenAlex fall on different sides of a window edge: stays
UNRESOLVED), NO_DATE, NO_DOI.  Writes reconcile/date_check.csv; nothing here changes a disposition.
"""
import csv
import glob
import json
import os
import pathlib
import time
import urllib.parse
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
LO, HI = "2011-01-01", "2026-09-18"


def key():
    k = os.environ.get("OPENALEX_API_KEY")
    p = pathlib.Path.home() / ".config" / "openalex" / "api_key"
    return k or (p.read_text().strip() if p.exists() else None)


def eligible():
    out = {}
    live = ("ELIGIBLE", "NEEDS_SI", "UNRESOLVED", "EXCLUDE:E2")
    cs = HERE / "reconcile" / "current_state.csv"
    for r in (csv.DictReader(open(cs, encoding="utf-8")) if cs.exists() else []):
        if r["v3_decision"].startswith(live) or r["v4_decision"].startswith(live):
            out.setdefault(r["screen_id"], r["doi"])
    vg = HERE / "reconcile" / "version_groups.csv"
    for r in (csv.DictReader(open(vg, encoding="utf-8")) if vg.exists() else []):
        if r["screen_id"] in out and r["primary"] and r["primary"] != r["screen_id"]:
            out.setdefault(r["primary"], "")
    if vg.exists():  # a version primary outside the full-text set: take its DOI from the group file or leave for lookup
        dois = {r["screen_id"]: r["doi"] for r in csv.DictReader(open(vg, encoding="utf-8"))}
        for s in out:
            out[s] = out[s] or dois.get(s, "")
    for f in sorted(glob.glob(str(HERE / "pass_*" / "batches" / "*.out.jsonl")) +
                    glob.glob(str(HERE / "third_read" / "batches" / "*.out.jsonl")) +
                    glob.glob(str(HERE / "v4_read" / "batches" / "*.out.jsonl"))):
        try:
            rs = [json.loads(line) for line in open(f, encoding="utf-8") if line.strip()]
        except ValueError:
            continue
        for r in rs:
            if r.get("disposition") == "ELIGIBLE":
                out.setdefault(r["screen_id"], r.get("doi") or "")
    return out


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "p-lit-date-check"}), timeout=30) as r:
        return json.load(r)


def main():
    k = key()
    rows = []
    for sid, doi in sorted(eligible().items()):
        row = dict(screen_id=sid, doi=doi, openalex_date="", crossref_online="", crossref_print="",
                   first_publication="", source="", flag="")
        if not doi:
            row["flag"] = "NO_DOI"
            rows.append(row)
            continue
        try:
            w = get("https://api.openalex.org/works/doi:%s%s" % (urllib.parse.quote(doi),
                                                                 ("?api_key=" + k) if k else ""))
            row["openalex_date"] = w.get("publication_date") or ""
        except Exception as e:
            row["flag"] = "OPENALEX_ERROR:" + type(e).__name__
        try:
            m = get("https://api.crossref.org/works/" + urllib.parse.quote(doi))["message"]
            part = lambda f: "-".join("%02d" % x for x in (m.get(f) or {}).get("date-parts", [[]])[0])
            row["crossref_online"], row["crossref_print"] = part("published-online"), part("published-print")
        except Exception:
            pass
        cr = [d for d in (row["crossref_online"], row["crossref_print"]) if d]
        row["first_publication"], row["source"] = (min(cr), "crossref") if cr else (row["openalex_date"], "openalex")             if row["openalex_date"] else ("", "")
        side = lambda d: "in" if LO <= d <= HI or (len(d) < 10 and LO[:len(d)] <= d <= HI[:len(d)]) else "out"
        fp = row["first_publication"]
        if not fp:
            row["flag"] = row["flag"] or "NO_DATE"
        elif side(fp) == "out":
            row["flag"] = "OUTSIDE_WINDOW"
        elif row["openalex_date"] and side(row["openalex_date"]) != side(fp):
            row["flag"] = "SOURCES_STRADDLE_BOUNDARY"
        rows.append(row)
        time.sleep(0.15)
    with open(HERE / "reconcile" / "date_check.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    flagged = [r for r in rows if r["flag"]]
    print(len(rows), "records checked;", len(flagged), "flagged")
    for r in flagged:
        print(r["screen_id"], r["doi"], r["first_publication"], r["source"], r["openalex_date"], r["flag"])


if __name__ == "__main__":
    main()
