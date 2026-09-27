"""FT4 reconciliation queue: joins the two full-text passes and sorts every record into a lane.

  python reconcile.py

Mechanical steps only; nothing here decides an interpretive case.
  1. Re-application of instruction v2 (instruction_changes.md): EXCLUDE:E6 with E1-E5 all YES
     -> NEEDS_SI.
  2. Excerpt check: each deciding excerpt must contain a fragment of 20+ characters found verbatim
     in the record's text (case, spacing and punctuation normalised; screener comments in
     parentheses or after semicolons are ignored).  An E1/E3 exclusion that rests on absence
     ("no DFT anywhere") is corroborated instead when the text names no electronic-structure
     method at all.  Anything else unverified goes to a third read.
  3. Lanes:
       AGREED_EXCLUDE    both passes EXCLUDE, both excerpts verified
       AGREED_ELIGIBLE   both ELIGIBLE, both deciding excerpts verified, screened under v3
       THIRD_READ        disagreement, unverified excerpt, pre-v3 ELIGIBLE (E5 re-read),
                         E1 non-article forms (D3 version linking), an ELIGIBLE row the
                         entrant has flagged as interpretive
       NEEDS_SI          either pass NEEDS_SI and neither pass a verified EXCLUDE
       RERETRIEVE        text_short, or a pass reports the file unreadable (text_ok false);
                         an UNRESOLVED on a readable text goes to THIRD_READ
       ONE_PASS          only one pass has read the record so far
Writes reconcile/queue.csv and reconcile/summary.json.
"""
import csv
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
CRIT = ["E1", "E2", "E3", "E4", "E5", "E6"]
V3_FROM = {"1": 22, "2": 21}  # first batch number screened under instruction v3
INTERPRETIVE = {"R0003", "S26608", "S30910", "S25109", "S08932"}  # listed in instruction_changes.md / design doc
NON_ARTICLE = re.compile(r"thesis|dissertation|conference|abstract|report|presentation|preprint|poster", re.I)


def norm(s):
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def rows(n):
    out = {}
    for p in sorted((HERE / ("pass_%s" % n) / "batches").glob("*.out.jsonl")):
        b = int(p.name.split("_")[1].split(".")[0])
        try:  # a batch still being written (or invalid) is skipped until it parses
            batch = [json.loads(line) for line in open(p, encoding="utf-8") if line.strip()]
        except ValueError:
            continue
        for r in batch:
            r["_batch"], r["_v3"] = p.name.split(".")[0], b >= V3_FROM[n]
            out[r["screen_id"]] = r
    return out


def apply_v2(r):
    if r["disposition"] == "EXCLUDE" and r.get("exclude_criterion") == "E6" and \
            all((r.get(c) or {}).get("v") == "YES" for c in CRIT[:5]):
        r["disposition"], r["exclude_criterion"], r["_v2_applied"] = "NEEDS_SI", None, True
    return r


COMP = re.compile(r"density[- ]functional|\bDFT\b|first[- ]principles|ab[- ]initio|\bVASP\b|quantum espresso|\bGPAW\b|\bCASTEP\b|free[- ]energy diagram", re.I)


def pieces(excerpt):
    """Quoted fragments of an excerpt: split on ellipses, semicolons and parentheses (screener comments)."""
    return [norm(x) for x in re.split(r"\.\.\.|…|;|\(|\)", excerpt or "") if len(norm(x)) >= 20]


def verified(r, text):
    """Each deciding excerpt has at least one fragment of 20+ characters found verbatim in the text
    (the exclude criterion; all six criteria for ELIGIBLE)."""
    if text is None:
        return False
    t = norm(text)
    crits = [r["exclude_criterion"]] if r["disposition"] == "EXCLUDE" else CRIT if r["disposition"] == "ELIGIBLE" else []
    return all(any(p in t for p in pieces((r.get(c) or {}).get("excerpt"))) for c in crits)


def no_computation(text):
    """Absence corroboration for an E1/E3 exclusion: the text names no electronic-structure method."""
    return text is not None and not COMP.search(text)


def lane(sid, a, b, text, tstat):
    rs = [x for x in (a, b) if x]
    if tstat != "ok" or any(x.get("text_ok") is False for x in rs):
        return "RERETRIEVE"  # unreadable, truncated or wrong-paper file
    if len(rs) == 1:
        return "ONE_PASS"
    da, db = a["disposition"], b["disposition"]
    va, vb = verified(a, text), verified(b, text)
    if da == db == "EXCLUDE":
        nonart = any(x["exclude_criterion"] == "E1" and NON_ARTICLE.search(x.get("note", "")) for x in rs)
        if nonart and not no_computation(text):
            return "THIRD_READ"  # D3: a non-article form with computation needs version linking
        ok = all(v or (x["exclude_criterion"] in ("E1", "E3") and no_computation(text)) for x, v in ((a, va), (b, vb)))
        return "AGREED_EXCLUDE" if ok else "THIRD_READ"
    if da == db == "ELIGIBLE":
        ok = va and vb and a["_v3"] and b["_v3"] and sid not in INTERPRETIVE
        return "AGREED_ELIGIBLE" if ok else "THIRD_READ"
    if "NEEDS_SI" in (da, db) and not any(x["disposition"] == "EXCLUDE" and verified(x, text) for x in rs):
        return "NEEDS_SI"
    return "THIRD_READ"


def main():
    p1, p2 = rows("1"), rows("2")
    tstat = {r["screen_id"]: r["status"] for r in csv.DictReader(open(HERE / "texts.csv", encoding="utf-8"))}
    (HERE / "reconcile").mkdir(exist_ok=True)
    out, counts = [], {}
    for sid in sorted(set(p1) | set(p2)):
        a, b = p1.get(sid), p2.get(sid)
        for x in (a, b):
            if x:
                apply_v2(x)
        tp = HERE / "text" / (sid + ".txt")
        text = tp.read_text(encoding="utf-8") if tp.exists() else None
        ln = lane(sid, a, b, text, tstat.get(sid, "missing"))
        counts[ln] = counts.get(ln, 0) + 1
        out.append(dict(screen_id=sid, doi=(a or b).get("doi", ""), lane=ln,
                        p1=a and (a["disposition"] + (":" + a["exclude_criterion"] if a.get("exclude_criterion") else "")),
                        p2=b and (b["disposition"] + (":" + b["exclude_criterion"] if b.get("exclude_criterion") else "")),
                        p1_verified=a and verified(a, text), p2_verified=b and verified(b, text),
                        p1_batch=a and a["_batch"], p2_batch=b and b["_batch"],
                        v2_applied=any(x and x.get("_v2_applied") for x in (a, b)),
                        text_status=tstat.get(sid, "missing")))
    with open(HERE / "reconcile" / "queue.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    json.dump(dict(records=len(out), lanes=counts), open(HERE / "reconcile" / "summary.json", "w"), indent=1)
    print(len(out), "records;", counts)


if __name__ == "__main__":
    main()
