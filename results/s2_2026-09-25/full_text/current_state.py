"""Current decision per record, under instruction v4 and under v3 (the original-rule sensitivity set).

  python current_state.py

Mechanical join, no judgement:
  v3 decision  AGREED_EXCLUDE / AGREED_ELIGIBLE lane -> the agreed pass disposition;
               THIRD_READ -> the third read; NEEDS_SI -> NEEDS_SI; RERETRIEVE -> none (no readable text).
  v4 decision  the v4 re-read where one exists (v4_read.py); otherwise the v3 decision, which v4 cannot
               change for that record by the v4_read.py selection rule.
Passes run after instruction v4 took effect (2026-09-27 07:50Z) are v4 reads; for those records the v3
decision is left empty ("v3 not read") and needs a v3 read before the sensitivity comparison.
Writes reconcile/current_state.csv and reconcile/current_state.json.
"""
import csv
import json
import pathlib

from reconcile import rows

HERE = pathlib.Path(__file__).resolve().parent
V4_FROM = "2026-09-27T07:50"


def label(r):
    return r and r["disposition"] + (":" + r["exclude_criterion"] if r.get("exclude_criterion") else "")


def jsonl(p):
    return {json.loads(l)["screen_id"]: json.loads(l) for l in open(p, encoding="utf-8") if l.strip()} if p.exists() else {}


def main():
    p1, p2 = rows("1"), rows("2")
    t3 = jsonl(HERE / "third_read" / "third_read.jsonl")
    v4 = jsonl(HERE / "v4_read" / "v4_read.jsonl")
    out, n3, n4 = [], {}, {}
    for q in csv.DictReader(open(HERE / "reconcile" / "queue.csv", encoding="utf-8")):
        sid, ln = q["screen_id"], q["lane"]
        a, b = p1.get(sid), p2.get(sid)
        v4_pass = any(x and (x.get("_screener") or {}).get("at", "") >= V4_FROM for x in (a, b))
        if ln == "RERETRIEVE":
            d3, s3 = "", "no readable text"
        elif v4_pass:
            d3, s3 = "", "v3 not read"
        elif ln == "THIRD_READ":
            d3, s3 = label(t3.get(sid)) or "", "third read" if sid in t3 else "third read pending"
        elif ln == "NEEDS_SI":
            d3, s3 = "NEEDS_SI", "passes"
        else:
            d3, s3 = label(a), "passes agree"
        if sid in v4:
            d4, s4, r4 = label(v4[sid]), "v4 read", v4[sid]
        elif v4_pass and ln in ("AGREED_EXCLUDE", "AGREED_ELIGIBLE", "NEEDS_SI"):
            d4, s4, r4 = label(a) if ln != "NEEDS_SI" else "NEEDS_SI", "v4 passes", None
        elif v4_pass and ln == "THIRD_READ":
            d4, s4, r4 = label(t3.get(sid)) or "", "third read (v4)" if sid in t3 else "third read pending", t3.get(sid)
        else:
            d4, s4, r4 = d3, s3, None
        out.append(dict(screen_id=sid, doi=q["doi"], lane=ln, v3_decision=d3, v3_source=s3, v4_decision=d4, v4_source=s4,
                        eta_form=(r4 or {}).get("eta_form"), secondary=(r4 or {}).get("secondary"),
                        entrant_question=bool((r4 or {}).get("entrant_question"))))
        n3[d3 or s3] = n3.get(d3 or s3, 0) + 1
        n4[d4 or s4] = n4.get(d4 or s4, 0) + 1
    with open(HERE / "reconcile" / "current_state.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    json.dump(dict(records=len(out), v3=n3, v4=n4), open(HERE / "reconcile" / "current_state.json", "w"), indent=1)
    print(len(out), "records\nv3:", dict(sorted(n3.items())), "\nv4:", dict(sorted(n4.items())))


if __name__ == "__main__":
    main()
