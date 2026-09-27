"""Third read (FT4): batches the THIRD_READ lane of reconcile/queue.csv for adjudicating screeners.

  python third_read.py prepare     add every THIRD_READ record not yet batched
  python third_read.py status      batches without a valid output
  python third_read.py collect     validate -> third_read/third_read.jsonl + collection.json

Each input line carries both earlier rows and the reason the record is in the lane.
The adjudicator sees them (a conflict-resolution read, not an independent pass).
"""
import argparse
import csv
import datetime as dt
import json
import pathlib

from ft_screen import BUDGET, MAX_PER_BATCH, check, sha
from reconcile import INTERPRETIVE, rows

HERE = pathlib.Path(__file__).resolve().parent
D = HERE / "third_read"


def why(r, a, b):
    out = []
    if a and b and a["disposition"] != b["disposition"]:
        out.append("passes disagree (%s vs %s)" % (r["p1"], r["p2"]))
    if r["p1_verified"] == "False" or r["p2_verified"] == "False":
        out.append("an excerpt was not found verbatim in the text")
    if any(x and x["disposition"] == "ELIGIBLE" and not x["_v3"] for x in (a, b)):
        out.append("ELIGIBLE under a pre-v3 instruction: re-read E5")
    if any(x and x["disposition"] == "UNRESOLVED" for x in (a, b)):
        out.append("a pass left it UNRESOLVED")
    if any(x and x.get("exclude_criterion") == "E1" for x in (a, b)):
        out.append("E1 form question (D3 version linking)")
    if r["screen_id"] in INTERPRETIVE:
        out.append("listed as interpretive in instruction_changes.md")
    return "; ".join(out) or "lane rule"


def slim(x):
    if not x:
        return None
    return {k: v for k, v in x.items() if not k.startswith("_")}


def prepare():
    (D / "batches").mkdir(parents=True, exist_ok=True)
    plan_p = D / "plan.json"
    plan = json.load(open(plan_p)) if plan_p.exists() else {"batches": {}}
    done = {s for b in plan["batches"].values() for s in b["records"]}
    p1, p2 = rows("1"), rows("2")
    chars = {r["screen_id"]: int(r["chars"]) for r in csv.DictReader(open(HERE / "texts.csv", encoding="utf-8"))
             if r.get("chars")}
    todo = [r for r in csv.DictReader(open(HERE / "reconcile" / "queue.csv", encoding="utf-8"))
            if r["lane"] == "THIRD_READ" and r["screen_id"] not in done]
    batch, size, k = [], 0, len(plan["batches"])

    def flush():
        nonlocal batch, size, k
        if not batch:
            return
        k += 1
        name = "T_%04d" % k
        lines = []
        for r in batch:
            a, b = p1.get(r["screen_id"]), p2.get(r["screen_id"])
            lines.append(dict(screen_id=r["screen_id"], doi=r["doi"], text="text/%s.txt" % r["screen_id"],
                              chars=chars.get(r["screen_id"]), why=why(r, a, b), pass1=slim(a), pass2=slim(b)))
        p = D / "batches" / (name + ".in.jsonl")
        p.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in lines), encoding="utf-8", newline="\n")
        plan["batches"][name] = dict(records=[x["screen_id"] for x in lines], chars=size, sha256=sha(p))
        batch, size = [], 0

    for r in todo:
        c = chars.get(r["screen_id"], 0)
        if batch and (size + c > BUDGET or len(batch) >= MAX_PER_BATCH):
            flush()
        batch.append(r)
        size += c
    flush()
    plan.update(instructions_sha256=sha(HERE / "eligibility_instructions.md"),
                brief_sha256=sha(HERE / "THIRD_READ_BRIEF.md"), updated_utc=dt.datetime.now(dt.timezone.utc).isoformat())
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
    out = D / "third_read.jsonl"
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
