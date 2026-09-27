"""v3 sensitivity read: one independent read under the historical instruction v3 for records that were
only ever screened under v4 (passes run after 2026-09-27 07:50Z), so the original-rule membership covers
every record.

  python v3_read.py prepare     select the records (reconcile/current_state.csv, v3_source "v3 not read")
  python v3_read.py status      batches without a valid output
  python v3_read.py collect     validate -> v3_read/v3_read.jsonl + collection.json

The read gets the exact v3 bytes (eligibility_instructions_v3.md without its two-line archive header,
sha256 checked against V3_SHA) and no earlier rows as hints: v4 rows must not steer a v3 read.
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import pathlib

from ft_screen import BUDGET, MAX_PER_BATCH, check, sha

HERE = pathlib.Path(__file__).resolve().parent
D = HERE / "v3_read"
V3_SHA = "19895e5757a8b81db09dc102e5b6078e33f9473cbb39318b03bab4f319dbe91c"


def v3_text():
    raw = (HERE / "eligibility_instructions_v3.md").read_bytes()
    body = raw.split(b"\n", 2)[2]  # drop the archive comment and the blank line after it
    if hashlib.sha256(body).hexdigest() != V3_SHA:
        raise SystemExit("eligibility_instructions_v3.md does not reproduce the v3 bytes")
    return body.decode("utf-8")


def prepare():
    v3_text()
    (D / "batches").mkdir(parents=True, exist_ok=True)
    plan_p = D / "plan.json"
    plan = json.load(open(plan_p)) if plan_p.exists() else {"batches": {}}
    done = {s for b in plan["batches"].values() for s in b["records"]}
    chars = {r["screen_id"]: int(r["chars"]) for r in csv.DictReader(open(HERE / "texts.csv", encoding="utf-8"))
             if r.get("chars")}
    todo = [dict(screen_id=r["screen_id"], doi=r["doi"], text="text/%s.txt" % r["screen_id"], chars=chars.get(r["screen_id"]))
            for r in csv.DictReader(open(HERE / "reconcile" / "current_state.csv", encoding="utf-8"))
            if r["v3_source"] == "v3 not read" and r["screen_id"] not in done]
    batch, size, k = [], 0, len(plan["batches"])

    def flush():
        nonlocal batch, size, k
        if not batch:
            return
        k += 1
        name = "V3_%04d" % k
        p = D / "batches" / (name + ".in.jsonl")
        p.write_text("".join(json.dumps(x) + "\n" for x in batch), encoding="utf-8", newline="\n")
        plan["batches"][name] = dict(records=[x["screen_id"] for x in batch], chars=size, sha256=sha(p))
        batch, size = [], 0

    for r in todo:
        c = r["chars"] or 0
        if batch and (size + c > BUDGET or len(batch) >= MAX_PER_BATCH):
            flush()
        batch.append(r)
        size += c
    flush()
    plan.update(instructions="v3", instructions_sha256=V3_SHA, updated_utc=dt.datetime.now(dt.timezone.utc).isoformat())
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
    out = D / "v3_read.jsonl"
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rs), encoding="utf-8", newline="\n")
    disp = {}
    for r in rs:
        key = r["disposition"] + (":" + r["exclude_criterion"] if r["disposition"] == "EXCLUDE" else "")
        disp[key] = disp.get(key, 0) + 1
    json.dump(dict(recorded_utc=dt.datetime.now(dt.timezone.utc).isoformat(), records=len(rs), instructions_sha256=V3_SHA,
                   open_or_invalid=sorted(bad), dispositions=disp, file_sha256=sha(out)),
              open(D / "collection.json", "w"), indent=1)
    print(len(rs), "records;", disp)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["prepare", "status", "collect"])
    dict(prepare=prepare, status=status, collect=collect)[p.parse_args().cmd]()
