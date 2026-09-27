"""v4 re-read: one adjudicating read under instruction v4 for every record the 2026-09-27 rulings can change.

  python v4_read.py prepare     select the affected records and batch them (records already batched are kept)
  python v4_read.py status      batches without a valid output
  python v4_read.py collect     validate -> v4_read/v4_read.jsonl + collection.json

Selection (routing only; nothing here decides eligibility).  A record is re-read when any of its
rows (pass 1, pass 2, third read) is:
  - ELIGIBLE, NEEDS_SI or UNRESOLVED (rulings 1-7 change E4/E5/E6);
  - EXCLUDE on E5 or E6 (rulings 1, 3, 4, 6, 7);
  - EXCLUDE on E4 with a note/excerpt about an unnamed polymorph (ruling 5);
  - EXCLUDE on E3 with a note/excerpt about scaling, Pourbaix, a single step or earlier work (rulings 2, 8, 9).
EXCLUDE on E1 or E2 alone is unchanged by v4 (ruling 10 keeps reviews and perspectives out; dates are
settled by date_check.py).  RERETRIEVE records wait for a readable text.  The v3 decisions stay on
record for the original-rule sensitivity comparison.
"""
import argparse
import csv
import datetime as dt
import json
import pathlib
import re

from ft_screen import BUDGET, MAX_PER_BATCH, check, sha
from reconcile import rows
from third_read import slim

HERE = pathlib.Path(__file__).resolve().parent
D = HERE / "v4_read"
K3 = re.compile(r"scaling|pourbaix|pcet|single (proton|step)|one step|previous(ly)?|earlier (work|study|paper|report)|"
                r"our (previous|prior|earlier)|reanaly|re-analy|from (ref|reference|the literature)|literature value", re.I)
K4 = re.compile(r"not (stated|specified|named|identified)|never (stated|named)|unspecified|tetragonal|jcpds|pdf ?#|card|"
                r"polymorph (is )?(not|un)|established", re.I)


def third_rows():
    p = HERE / "third_read" / "third_read.jsonl"
    return {json.loads(l)["screen_id"]: json.loads(l) for l in open(p, encoding="utf-8") if l.strip()}


def reasons(x):
    d, c = x["disposition"], x.get("exclude_criterion")
    blob = lambda k: json.dumps({kk: x.get(kk) for kk in (k, "note")}, ensure_ascii=False)
    if d in ("ELIGIBLE", "NEEDS_SI", "UNRESOLVED"):
        return d
    if c in ("E5", "E6"):
        return "EXCLUDE:" + c
    if c == "E4" and K4.search(blob("E4")):
        return "EXCLUDE:E4 (polymorph wording)"
    if c == "E3" and K3.search(blob("E3")):
        return "EXCLUDE:E3 (scaling/partial/earlier-work wording)"
    return None


def prepare():
    (D / "batches").mkdir(parents=True, exist_ok=True)
    plan_p = D / "plan.json"
    plan = json.load(open(plan_p)) if plan_p.exists() else {"batches": {}}
    done = {s for b in plan["batches"].values() for s in b["records"]}
    p1, p2, t3 = rows("1"), rows("2"), third_rows()
    chars = {r["screen_id"]: int(r["chars"]) for r in csv.DictReader(open(HERE / "texts.csv", encoding="utf-8"))
             if r.get("chars")}
    todo = []
    for q in csv.DictReader(open(HERE / "reconcile" / "queue.csv", encoding="utf-8")):
        sid = q["screen_id"]
        if q["lane"] == "RERETRIEVE" or sid in done:
            continue
        rs = [(k, x) for k, x in (("pass1", p1.get(sid)), ("pass2", p2.get(sid)), ("third", t3.get(sid))) if x]
        why = sorted({"%s %s" % (k, w) for k, x in rs for w in [reasons(x)] if w})
        if why:
            todo.append(dict(screen_id=sid, doi=q["doi"], text="text/%s.txt" % sid, chars=chars.get(sid),
                             why="v4 re-read; rows: " + "; ".join(why), pass1=slim(p1.get(sid)),
                             pass2=slim(p2.get(sid)), third=slim(t3.get(sid))))
    batch, size, k = [], 0, len(plan["batches"])

    def flush():
        nonlocal batch, size, k
        if not batch:
            return
        k += 1
        name = "V4_%04d" % k
        p = D / "batches" / (name + ".in.jsonl")
        p.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in batch), encoding="utf-8", newline="\n")
        plan["batches"][name] = dict(records=[x["screen_id"] for x in batch], chars=size, sha256=sha(p))
        batch, size = [], 0

    for r in todo:
        c = r["chars"] or 0
        if batch and (size + c > BUDGET or len(batch) >= MAX_PER_BATCH):
            flush()
        batch.append(r)
        size += c
    flush()
    plan.update(instructions_sha256=sha(HERE / "eligibility_instructions.md"), instructions_version="v4",
                updated_utc=dt.datetime.now(dt.timezone.utc).isoformat())
    json.dump(plan, open(plan_p, "w"), indent=1)
    print(len(plan["batches"]), "batches;", len(todo), "records added")


def status(quiet=False):
    plan = json.load(open(D / "plan.json"))["batches"]
    bad = {b: check(D / "batches" / (b + ".in.jsonl"), D / "batches" / (b + ".out.jsonl")) for b in plan}
    bad = {b: p for b, p in bad.items() if p}
    if not quiet:
        print(json.dumps(dict(batches=len(plan), done=len(plan) - len(bad),
                              open=sorted(b for b, p in bad.items() if p == ["missing"]),
                              invalid={b: p for b, p in bad.items() if p != ["missing"]}), indent=1))
    return bad


def collect():
    plan = json.load(open(D / "plan.json"))["batches"]
    bad = status(quiet=True)
    rs = [json.loads(l) for b in plan if b not in bad
          for l in open(D / "batches" / (b + ".out.jsonl"), encoding="utf-8") if l.strip()]
    out = D / "v4_read.jsonl"
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rs), encoding="utf-8", newline="\n")
    disp = {}
    for r in rs:
        key = r["disposition"] + (":" + r["exclude_criterion"] if r["disposition"] == "EXCLUDE" else "")
        disp[key] = disp.get(key, 0) + 1
    json.dump(dict(recorded_utc=dt.datetime.now(dt.timezone.utc).isoformat(), records=len(rs),
                   entrant_questions=sum(bool(r.get("entrant_question")) for r in rs),
                   open_or_invalid=sorted(bad), dispositions=disp, file_sha256=sha(out)),
              open(D / "collection.json", "w"), indent=1)
    print(len(rs), "records;", disp)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["prepare", "status", "collect"])
    dict(prepare=prepare, status=status, collect=collect)[p.parse_args().cmd]()
