"""Current decision per record, under instruction v4 and under v3 (the original-rule sensitivity set).

  python current_state.py

Mechanical join, no judgement:
  v3 decision  AGREED_EXCLUDE / AGREED_ELIGIBLE lane -> the agreed pass disposition;
               THIRD_READ -> the third read; NEEDS_SI -> NEEDS_SI; RERETRIEVE -> none (no readable text).
  v4 decision  the v4 re-read where one exists (v4_read.py); otherwise the v3 decision, which v4 cannot
               change for that record by the v4_read.py selection rule.
Passes run after instruction v4 took effect (2026-09-27 07:50Z) are v4 reads; for those records the v3
decision is left empty ("v3 not read") and needs a v3 read before the sensitivity comparison.

Mechanical steps on the v4 decision (column v4_final), each logged in instruction_changes.md:
  E6_WITHOUT_SI  an EXCLUDE:E6 whose file holds no SI breaks the rule that E6 is never excluded from
                 the main text alone -> NEEDS_SI if E1-E5 are YES, else UNRESOLVED (checked by hand).
  dates          an E2 UNCLEAR row takes E2 from reconcile/date_check.csv (ruling 10); the disposition is
                 re-derived from the six verdicts by the instructions' rule.
  versions       reconcile/version_groups.csv: a linked version is counted through its group's primary
                 ("collapsed"); an unlinked non-article form is EXCLUDE:E1 (D3) unless already excluded.
Writes reconcile/current_state.csv and reconcile/current_state.json.
"""
import csv
import json
import pathlib

from reconcile import rows

HERE = pathlib.Path(__file__).resolve().parent
V4_FROM = "2026-09-27T07:50"
E6_WITHOUT_SI = {"S09618", "S23884", "S29788"}  # v4 EXCLUDE:E6, no SI in the file (checked 2026-09-27)


def derive(r):
    """The instructions' disposition rule applied to six verdicts."""
    v = {c: (r.get(c) or {}).get("v") for c in ("E1", "E2", "E3", "E4", "E5", "E6")}
    for c in ("E1", "E2", "E3", "E4", "E5", "E6"):
        if v[c] == "NO":
            return "EXCLUDE:" + c
    if all(v[c] == "YES" for c in v):
        return "ELIGIBLE"
    if all(v[c] == "YES" for c in ("E1", "E2", "E3", "E4")) and v["E5"] == "UNCLEAR":
        return "NEEDS_SI"
    if all(v[c] == "YES" for c in ("E1", "E2", "E3", "E4", "E5")) and v["E6"] == "UNCLEAR":
        return "NEEDS_SI"
    return "UNRESOLVED"


def final_v4(sid, d4, r4, dates):
    """(decision, step) after the E6 and date steps."""
    if not r4:
        return d4, ""
    if sid in E6_WITHOUT_SI and d4 == "EXCLUDE:E6":
        return derive(dict(r4, E6={"v": "UNCLEAR"})), "E6_WITHOUT_SI"
    if (r4.get("E2") or {}).get("v") == "UNCLEAR" and d4 in ("UNRESOLVED", "NEEDS_SI", "ELIGIBLE"):
        dc = dates.get(sid) or {}
        if dc.get("first_publication") and not dc.get("flag"):
            return derive(dict(r4, E2={"v": "YES"})), "dated"
        if dc.get("flag") == "OUTSIDE_WINDOW":
            return "EXCLUDE:E2", "dated"
    return d4, ""


def label(r):
    return r and r["disposition"] + (":" + r["exclude_criterion"] if r.get("exclude_criterion") else "")


def jsonl(p):
    return {json.loads(l)["screen_id"]: json.loads(l) for l in open(p, encoding="utf-8") if l.strip()} if p.exists() else {}


def main():
    p1, p2 = rows("1"), rows("2")
    t3 = jsonl(HERE / "third_read" / "third_read.jsonl")
    v4 = jsonl(HERE / "v4_read" / "v4_read.jsonl")
    dp = HERE / "reconcile" / "date_check.csv"
    dates = {r["screen_id"]: r for r in csv.DictReader(open(dp, encoding="utf-8"))} if dp.exists() else {}
    vp = HERE / "reconcile" / "version_groups.csv"
    vers = {r["screen_id"]: r for r in csv.DictReader(open(vp, encoding="utf-8"))} if vp.exists() else {}
    out, n3, n4, nf = [], {}, {}, {}
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
        f4, step = final_v4(sid, d4, r4, dates)
        vg = vers.get(sid) or {}
        if vg.get("status") == "collapses into primary":
            member = "collapsed into " + vg["primary"]
        elif vg.get("status") == "unlinked non-article" and f4 and not f4.startswith("EXCLUDE"):
            member, step = "EXCLUDE:E1", (step + ";" if step else "") + "D3"
        else:
            member = f4 or s4
        out.append(dict(screen_id=sid, doi=q["doi"], lane=ln, v3_decision=d3, v3_source=s3, v4_decision=d4, v4_source=s4,
                        v4_final=member, v4_step=step, version_primary=vg.get("primary", ""),
                        eta_form=(r4 or {}).get("eta_form"), secondary=(r4 or {}).get("secondary"),
                        entrant_question=bool((r4 or {}).get("entrant_question"))))
        n3[d3 or s3] = n3.get(d3 or s3, 0) + 1
        n4[d4 or s4] = n4.get(d4 or s4, 0) + 1
        key = "collapsed" if member.startswith("collapsed") else member
        nf[key] = nf.get(key, 0) + 1
    with open(HERE / "reconcile" / "current_state.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    json.dump(dict(records=len(out), v3=n3, v4=n4, v4_final=nf), open(HERE / "reconcile" / "current_state.json", "w"),
              indent=1)
    print(len(out), "records\nv3:", dict(sorted(n3.items())), "\nv4:", dict(sorted(n4.items())),
          "\nv4 final:", dict(sorted(nf.items())))


if __name__ == "__main__":
    main()
