"""v5 re-read: one adjudicating read under instruction v5 for every record the 2026-09-27 v5 rulings
(answers to the v4-triage questions D1-D14) can change.

  python v5_read.py prepare     select the affected records and batch them (records already batched are kept)
  python v5_read.py status      batches without a valid output
  python v5_read.py collect     validate -> v5_read/v5_read.jsonl + collection.json

Selection (routing only; nothing here decides eligibility).  A record is re-read when any of its rows
(pass 1, pass 2, third read, v4 read, v3 sensitivity read) is:
  - ELIGIBLE, NEEDS_SI or UNRESOLVED (D1, D4-D6, D8-D10, D12-D14 change E4/E5/E6 and the output fields);
  - EXCLUDE on E4, E5 or E6 (D1, D2, D6, D8, D9, D4, D12, D13);
  - EXCLUDE on E3 where at least one E3 row does not say the paper has no calculation at all
    (D2 Pourbaix/spectra, D3 single intermediates and other reactions, D11 re-analysis);
  - EXCLUDE on E1 where the record is a preprint or report, or a row's note mentions one (D7).
EXCLUDE on E2 alone, and E3 exclusions whose every row says there is no calculation, are unchanged by v5.
RERETRIEVE records wait for a readable text.  v3 and v4 decisions stay on record for the sensitivity comparison.
Records whose two passes both ran under v5 (_screener.at from V5_FROM, e.g. the manual downloads screened
2026-09-27) are not re-read: their passes and third read already apply v5.
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
D = HERE / "v5_read"
V5_FROM = "2026-09-27T10:34:50"  # eligibility_instructions.md became v5; the last pre-v5 pass row is from 09:08Z
NOCALC = re.compile(r"no (dft|density functional|calculation|computation|electronic[- ]structure|theoretical|first[- ]principles|"
                    r"simulation)|purely experimental|entirely experimental|experimental (study|work|paper) only|without any "
                    r"(dft|calculation)|does not (perform|report|include) (any )?(dft|calculation)|no computational", re.I)
K1 = re.compile(r"preprint|research square|arxiv|chemrxiv|report|repository|osti|technical", re.I)


def third_rows():
    p = HERE / "third_read" / "third_read.jsonl"
    return {json.loads(l)["screen_id"]: json.loads(l) for l in open(p, encoding="utf-8") if l.strip()}


def jl(p):
    return {json.loads(l)["screen_id"]: json.loads(l) for l in open(p, encoding="utf-8") if l.strip()} if p.exists() else {}


def reasons(x, rtype, e3_calc):
    d, c = x["disposition"], x.get("exclude_criterion")
    blob = json.dumps({k: x.get(k) for k in ("E1", "E3", "note")}, ensure_ascii=False)
    if d in ("ELIGIBLE", "NEEDS_SI", "UNRESOLVED"):
        return d
    if c in ("E4", "E5", "E6"):
        return "EXCLUDE:" + c
    if c == "E3" and e3_calc:
        return "EXCLUDE:E3 (calculation present)"
    if c == "E1" and (rtype in ("preprint", "report") or K1.search(blob)):
        return "EXCLUDE:E1 (preprint/report form)"
    return None


def prepare():
    (D / "batches").mkdir(parents=True, exist_ok=True)
    plan_p = D / "plan.json"
    plan = json.load(open(plan_p)) if plan_p.exists() else {"batches": {}}
    done = {s for b in plan["batches"].values() for s in b["records"]}
    p1, p2, t3 = rows("1"), rows("2"), third_rows()
    v4, v3s = jl(HERE / "v4_read" / "v4_read.jsonl"), jl(HERE / "v3_read" / "v3_read.jsonl")
    vtype = {r["screen_id"]: r["type"] for r in csv.DictReader(open(HERE / "reconcile" / "version_groups.csv", encoding="utf-8"))}
    chars = {r["screen_id"]: int(r["chars"]) for r in csv.DictReader(open(HERE / "texts.csv", encoding="utf-8"))
             if r.get("chars")}
    todo = []
    for q in csv.DictReader(open(HERE / "reconcile" / "queue.csv", encoding="utf-8")):
        sid = q["screen_id"]
        if q["lane"] == "RERETRIEVE" or sid in done:
            continue
        if all(x and (x.get("_screener") or {}).get("at", "") >= V5_FROM for x in (p1.get(sid), p2.get(sid))):
            continue
        rs = [(k, x) for k, x in (("pass1", p1.get(sid)), ("pass2", p2.get(sid)), ("third", t3.get(sid)),
                                  ("v4", v4.get(sid)), ("v3 sensitivity", v3s.get(sid))) if x]
        e3 = [x for _, x in rs if x.get("exclude_criterion") == "E3"]
        e3_calc = any(not NOCALC.search(json.dumps({kk: x.get(kk) for kk in ("E3", "note")}, ensure_ascii=False)) for x in e3)
        why = sorted({"%s %s" % (k, w) for k, x in rs for w in [reasons(x, vtype.get(sid), e3_calc)] if w})
        if why:
            todo.append(dict(screen_id=sid, doi=q["doi"], text="text/%s.txt" % sid, chars=chars.get(sid),
                             why="v5 re-read; rows: " + "; ".join(why), pass1=slim(p1.get(sid)), pass2=slim(p2.get(sid)),
                             third=slim(t3.get(sid)), v4=slim(v4.get(sid))))
    batch, size, k = [], 0, len(plan["batches"])

    def flush():
        nonlocal batch, size, k
        if not batch:
            return
        k += 1
        name = "V5_%04d" % k
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
    plan.update(instructions_sha256=sha(HERE / "eligibility_instructions.md"), instructions_version="v5",
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
    out = D / "v5_read.jsonl"
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
