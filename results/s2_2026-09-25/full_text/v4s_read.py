"""v4 sensitivity read: one independent read under the historical instruction v4 for records that were
only ever screened under v5 (both passes run after V5_FROM), so v4 membership, like v3 membership,
covers every record.  The v3 counterpart is v3_read.py.

  python v4s_read.py prepare     select the records (reconcile/queue.csv; both pass rows from V5_FROM, no v4 read)
  python v4s_read.py status      batches without a valid output
  python v4s_read.py collect     validate -> v4s_read/v4s_read.jsonl + collection.json

The read gets the exact v4 bytes (eligibility_instructions_v4.md without its two-line archive header,
sha256 checked against V4_SHA) and no earlier rows as hints: v5 rows must not steer a v4 read.
Records screened under v3 or v4 already carry a v4 decision (a v4 pass, the v4 re-read, or a v3
decision v4 cannot change) and are not selected.
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import pathlib

from ft_screen import BUDGET, MAX_PER_BATCH, check, sha
from reconcile import rows
from v5_read import V5_FROM

HERE = pathlib.Path(__file__).resolve().parent
D = HERE / "v4s_read"
V4_SHA = "18fe8fd1e09dc504ca121e2eb582abf0d463d6942f27867fc4d335284630b007"


def v4_text():
    raw = (HERE / "eligibility_instructions_v4.md").read_bytes()
    body = raw.split(b"\n", 2)[2]  # drop the archive comment and the blank line after it
    if hashlib.sha256(body).hexdigest() != V4_SHA:
        raise SystemExit("eligibility_instructions_v4.md does not reproduce the v4 bytes")
    return body.decode("utf-8")


def prepare():
    v4_text()
    (D / "batches").mkdir(parents=True, exist_ok=True)
    plan_p = D / "plan.json"
    plan = json.load(open(plan_p)) if plan_p.exists() else {"batches": {}}
    done = {s for b in plan["batches"].values() for s in b["records"]}
    p1, p2 = rows("1"), rows("2")
    v4p = HERE / "v4_read" / "v4_read.jsonl"
    v4 = {json.loads(l)["screen_id"] for l in open(v4p, encoding="utf-8") if l.strip()} if v4p.exists() else set()
    chars = {r["screen_id"]: int(r["chars"]) for r in csv.DictReader(open(HERE / "texts.csv", encoding="utf-8"))
             if r.get("chars")}
    todo = []
    for q in csv.DictReader(open(HERE / "reconcile" / "queue.csv", encoding="utf-8")):
        sid = q["screen_id"]
        if q["lane"] == "RERETRIEVE" or sid in done or sid in v4:
            continue
        if all(x and (x.get("_screener") or {}).get("at", "") >= V5_FROM for x in (p1.get(sid), p2.get(sid))):
            todo.append(dict(screen_id=sid, doi=q["doi"], text="text/%s.txt" % sid, chars=chars.get(sid)))
    batch, size, k = [], 0, len(plan["batches"])

    def flush():
        nonlocal batch, size, k
        if not batch:
            return
        k += 1
        name = "V4S_%04d" % k
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
    plan.update(instructions="v4", instructions_sha256=V4_SHA, updated_utc=dt.datetime.now(dt.timezone.utc).isoformat())
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
    out = D / "v4s_read.jsonl"
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rs), encoding="utf-8", newline="\n")
    disp = {}
    for r in rs:
        key = r["disposition"] + (":" + r["exclude_criterion"] if r["disposition"] == "EXCLUDE" else "")
        disp[key] = disp.get(key, 0) + 1
    json.dump(dict(recorded_utc=dt.datetime.now(dt.timezone.utc).isoformat(), records=len(rs), instructions_sha256=V4_SHA,
                   open_or_invalid=sorted(bad), dispositions=disp, file_sha256=sha(out)),
              open(D / "collection.json", "w"), indent=1)
    print(len(rs), "records;", disp)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["prepare", "status", "collect"])
    dict(prepare=prepare, status=status, collect=collect)[p.parse_args().cmd]()
