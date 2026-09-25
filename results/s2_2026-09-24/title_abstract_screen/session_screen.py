"""Two independent title/abstract passes run by in-session screeners, batch by batch.

Same design as the pilot: each screener gets one batch file of 200 records, the shared
instructions, and nothing else; it reads every record itself and writes one label per record.
Pass A and pass B use different seeded groupings (the seeds of batch_screen.py), so no batch of
one pass shares its record set with a batch of the other, and a pass-B screener works through its
batch from the last record backwards.  Nothing is merged here; merge_passes.py does that.

  python session_screen.py prepare --pass A      write passes/session_pass_A/batches/*.in.jsonl + plan.json
  python session_screen.py status  --pass A      list batches without a valid output
  python session_screen.py collect --pass A      validate every batch output, write pass_A.jsonl + collection.json

Inputs: inputs/chunk_*.jsonl (the provider union) and reference_inputs/chunk_ref.jsonl (DOIs added
by the one-generation reference pass).
"""
import argparse
import datetime as dt
import hashlib
import json
import pathlib
import random

HERE = pathlib.Path(__file__).resolve().parent
BATCH = 200
SEEDS = {"A": 20260924, "B": 92406202}
LABELS = {"CLEARLY_IRRELEVANT", "POSSIBLY_RELEVANT", "LIKELY_RELEVANT"}
FIELDS = ("screen_id", "doi", "title", "publication_date", "type", "venue", "language", "abstract")


def input_files():
    return sorted(HERE.glob("inputs/chunk_*.jsonl")) + [HERE / "reference_inputs/chunk_ref.jsonl"]


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def pdir(which):
    return HERE / "passes" / ("session_pass_" + which)


def prepare(which):
    records = [json.loads(line) for f in input_files() for line in open(f, encoding="utf-8")]
    ids = [r["screen_id"] for r in records]
    assert len(ids) == len(set(ids)), "duplicate screen_id"
    order = list(range(len(records)))
    random.Random(SEEDS[which]).shuffle(order)
    d = pdir(which) / "batches"
    d.mkdir(parents=True, exist_ok=True)
    plan = {}
    for b, i in enumerate(range(0, len(order), BATCH), 1):
        name = "%s_%03d" % (which, b)
        batch = [{k: records[j].get(k) for k in FIELDS} for j in order[i:i + BATCH]]
        path = d / (name + ".in.jsonl")
        path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in batch), encoding="utf-8", newline="\n")
        plan[name] = dict(records=len(batch), sha256=sha(path))
    json.dump(dict(recorded_utc=dt.datetime.now(dt.timezone.utc).isoformat(), pass_=which, seed=SEEDS[which],
                   batch_size=BATCH, records=len(records), batches=len(plan),
                   instructions_sha256=sha(HERE / "screening_instructions.md"),
                   inputs={f.relative_to(HERE).as_posix(): sha(f) for f in input_files()}, plan=plan),
              open(pdir(which) / "plan.json", "w", encoding="utf-8"), indent=1)
    print(which, len(records), "records,", len(plan), "batches")


def check(inp, out):
    """Return a list of problems with one batch output (empty = valid)."""
    if not out.exists():
        return ["missing"]
    want = [json.loads(line)["screen_id"] for line in open(inp, encoding="utf-8")]
    problems, got = [], []
    for n, line in enumerate(open(out, encoding="utf-8"), 1):
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except ValueError:
            problems.append("line %d not JSON" % n)
            continue
        got.append(r.get("screen_id"))
        if r.get("label") not in LABELS:
            problems.append("line %d bad label %r" % (n, r.get("label")))
    if got != want:
        problems.append("screen_id order/coverage mismatch (%d of %d)" % (len(set(got) & set(want)), len(want)))
    return problems


def status(which):
    plan = json.load(open(pdir(which) / "plan.json", encoding="utf-8"))["plan"]
    d = pdir(which) / "batches"
    bad = {n: check(d / (n + ".in.jsonl"), d / (n + ".out.jsonl")) for n in plan}
    bad = {n: p for n, p in bad.items() if p}
    print(json.dumps(dict(batches=len(plan), done=len(plan) - len(bad), open=bad), indent=1))
    return bad


def collect(which):
    plan = json.load(open(pdir(which) / "plan.json", encoding="utf-8"))["plan"]
    d = pdir(which) / "batches"
    bad = status(which)
    rows = []
    for n in plan:
        if n not in bad:
            rows += [json.loads(line) for line in open(d / (n + ".out.jsonl"), encoding="utf-8") if line.strip()]
    out = pdir(which) / ("pass_%s.jsonl" % which)
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8", newline="\n")
    json.dump(dict(recorded_utc=dt.datetime.now(dt.timezone.utc).isoformat(), records=len(rows), invalid_batches=bad,
                   outputs={n: sha(d / (n + ".out.jsonl")) for n in plan if n not in bad},
                   labels={l: sum(r["label"] == l for r in rows) for l in sorted(LABELS)},
                   pass_file=dict(path=out.name, sha256=sha(out))),
              open(pdir(which) / "collection.json", "w", encoding="utf-8"), indent=1)
    print(len(rows), "records collected;", len(bad), "invalid batches")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["prepare", "status", "collect"])
    p.add_argument("--pass", dest="which", choices=["A", "B"], required=True)
    a = p.parse_args()
    dict(prepare=prepare, status=status, collect=collect)[a.cmd](a.which)
