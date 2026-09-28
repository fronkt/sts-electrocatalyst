"""E2 date check (ruling 10, 2026-09-27) for every record still in play.

  python date_check.py

Records: any pass, third read, v4 read or v5 read marked ELIGIBLE; every record whose v3, v4 or v5 decision
in reconcile/current_state.csv is ELIGIBLE, NEEDS_SI, UNRESOLVED or EXCLUDE:E2; and the journal-article
primary of each such record's version group (reconcile/version_groups.csv).
First publication date (ruling 10): the publisher's first-online or print date as carried in the
DOI-matched Crossref record (earliest of the two); for a preprint (v5 D7) the posting date the preprint
server deposited with Crossref ("posted"); OpenAlex publication_date only when Crossref has none of these,
and otherwise as corroboration.  Received/accepted dates and DOI years are never used.
Crossref dates can have year or month precision.  A partial date stands for its whole span (2026 = any day
of 2026), so first publication lies between the earliest possible day and the earliest latest-possible day
of the candidates; first_publication shows the candidate with the earliest latest-possible day.
Flags, in this order:
  NO_DATE, NO_DOI
  PREPRINT_NOT_V1            the posting date belongs to a DOI that names a later version (v2, v3 ...); D7 needs
                             the version-1 posting date, so the date is not used
  PARTIAL_DATE_AT_EDGE       the first-publication span crosses a window edge (e.g. year-only 2026): stays UNRESOLVED
  SOURCES_STRADDLE_BOUNDARY  Crossref and OpenAlex fall on different sides of a window edge: stays UNRESOLVED
                             (ruling 10); tested before OUTSIDE_WINDOW, so a Crossref record that carries only a
                             future print-issue date while OpenAlex has the in-window online date is not read as outside
  OUTSIDE_WINDOW             first publication outside 2011-01-01 .. 2026-09-18
The date check settles E2 only where a read left it UNCLEAR (current_state.py); a first-online date printed on
the paper outranks it.  Writes reconcile/date_check.csv; nothing here changes a disposition.
"""
import csv
import glob
import json
import os
import pathlib
import re
import time
import urllib.parse
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
LO, HI = "2011-01-01", "2026-09-18"
VERSION = re.compile(r"[/.-]v(\d+)$", re.I)  # a preprint DOI that names its version: .../v2, ...-v2, ....v2


def span(d):
    """Earliest and latest day a year-, month- or day-precision date can stand for."""
    return {4: (d + "-01-01", d + "-12-31"), 7: (d + "-01", d + "-31")}.get(len(d), (d, d))


def side(lo, hi):
    return "in" if LO <= lo and hi <= HI else "out" if hi < LO or lo > HI else "edge"


def settle(row):
    """first_publication, source and flag from the fetched dates (the flag may already hold an API error)."""
    cr = [d for d in (row["crossref_online"], row["crossref_print"], row["crossref_posted"]) if d]
    ds, src = (cr, "crossref") if cr else ([row["openalex_date"]], "openalex") if row["openalex_date"] else ([], "")
    row["source"] = src
    if not ds:
        row["first_publication"], row["flag"] = "", row["flag"] or "NO_DATE"
        return row
    row["first_publication"] = min(ds, key=lambda d: (span(d)[1], -len(d)))
    lo, hi = min(span(d)[0] for d in ds), min(span(d)[1] for d in ds)
    v = VERSION.search(row["doi"])
    oa = row["openalex_date"]
    if row["crossref_posted"] and v and int(v.group(1)) > 1:
        row["flag"] = "PREPRINT_NOT_V1"
    elif side(lo, hi) == "edge":
        row["flag"] = "PARTIAL_DATE_AT_EDGE"
    elif oa and side(*span(oa)) != side(lo, hi):
        row["flag"] = "SOURCES_STRADDLE_BOUNDARY"
    elif side(lo, hi) == "out":
        row["flag"] = "OUTSIDE_WINDOW"
    return row


def key():
    k = os.environ.get("OPENALEX_API_KEY")
    p = pathlib.Path.home() / ".config" / "openalex" / "api_key"
    return k or (p.read_text().strip() if p.exists() else None)


def eligible():
    out = {}
    live = ("ELIGIBLE", "NEEDS_SI", "UNRESOLVED", "EXCLUDE:E2")
    cs = HERE / "reconcile" / "current_state.csv"
    for r in (csv.DictReader(open(cs, encoding="utf-8")) if cs.exists() else []):
        if any(r.get(k, "").startswith(live) for k in ("v3_decision", "v4_decision", "v5_decision")):
            out.setdefault(r["screen_id"], r["doi"])
    vg = HERE / "reconcile" / "version_groups.csv"
    for r in (csv.DictReader(open(vg, encoding="utf-8")) if vg.exists() else []):
        if r["screen_id"] in out and r["primary"] and r["primary"] != r["screen_id"]:
            out.setdefault(r["primary"], "")
    if vg.exists():  # a version primary outside the full-text set: its DOI from the group file, else the screened identities
        dois = {r["screen_id"]: r["doi"] for r in csv.DictReader(open(vg, encoding="utf-8"))}
        ids = HERE.parents[1] / "s2_2026-09-24" / "title_abstract_screen" / "screened_identities.csv"
        for r in (csv.DictReader(open(ids, encoding="utf-8")) if ids.exists() else []):
            if not dois.get(r["screen_id"]):  # until 2026-09-28 such a primary was flagged NO_DOI (S27700)
                dois[r["screen_id"]] = r["doi"]
        for s in out:
            out[s] = out[s] or dois.get(s, "")
    for f in sorted(glob.glob(str(HERE / "pass_*" / "batches" / "*.out.jsonl")) +
                    glob.glob(str(HERE / "third_read" / "batches" / "*.out.jsonl")) +
                    glob.glob(str(HERE / "v4_read" / "batches" / "*.out.jsonl")) +
                    glob.glob(str(HERE / "v5_read" / "batches" / "*.out.jsonl"))):
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
                   crossref_posted="", first_publication="", source="", flag="")
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
            row["crossref_posted"] = part("posted")
        except Exception:
            pass
        rows.append(settle(row))
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
