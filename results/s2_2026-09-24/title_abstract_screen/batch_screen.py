"""Two independent title/abstract pre-screen passes over the screening inputs via the Message Batches API.

Each pass groups the records 20 per request; pass A and pass B use different groupings and orders
(seeded), so no request in one pass shares its context with a request in the other.  Every raw
result is saved.  No decision is merged here; merge_passes.py does that deterministically.

  python batch_screen.py submit --pass A [--model claude-opus-5] [--pilot]
  python batch_screen.py collect --pass A [--pilot]

Requires Anthropic credentials in the environment (ANTHROPIC_API_KEY or an `ant auth login` profile).
"""
import argparse
import datetime as dt
import glob
import hashlib
import json
import pathlib
import random

import anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

HERE = pathlib.Path(__file__).resolve().parent
INSTRUCTIONS = (HERE / "screening_instructions.md").read_text(encoding="utf-8")
GROUP = 20
SEEDS = {"A": 20260924, "B": 92406202}
LABELS = ["CLEARLY_IRRELEVANT", "POSSIBLY_RELEVANT", "LIKELY_RELEVANT"]
SCHEMA = {
    "type": "object",
    "properties": {"results": {"type": "array", "items": {
        "type": "object",
        "properties": {"screen_id": {"type": "string"}, "doi": {"type": ["string", "null"]},
                       "label": {"type": "string", "enum": LABELS}, "reason": {"type": "string"}},
        "required": ["screen_id", "doi", "label", "reason"], "additionalProperties": False}}},
    "required": ["results"], "additionalProperties": False}
FIELDS = ("screen_id", "doi", "title", "publication_date", "type", "venue", "language", "abstract")


def load(pilot):
    files = [HERE / "pilot/pilot_input.jsonl"] if pilot else sorted(HERE.glob("inputs/chunk_*.jsonl"))
    return [json.loads(line) for f in files for line in open(f, encoding="utf-8")]


def outdir(which, pilot):
    d = HERE / ("pilot" if pilot else "passes") / ("api_pass_" + which)
    d.mkdir(parents=True, exist_ok=True)
    return d


def submit(which, model, pilot):
    records = load(pilot)
    order = list(range(len(records)))
    random.Random(SEEDS[which]).shuffle(order)
    groups = [order[i:i + GROUP] for i in range(0, len(order), GROUP)]
    requests, plan = [], {}
    for g, idx in enumerate(groups):
        cid = "%s-%05d" % (which, g)
        batch = [{k: records[i].get(k) for k in FIELDS} for i in idx]
        plan[cid] = [records[i]["screen_id"] for i in idx]
        requests.append(Request(custom_id=cid, params=MessageCreateParamsNonStreaming(
            model=model, max_tokens=4000, system=INSTRUCTIONS,
            output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
            messages=[{"role": "user", "content": "Screen each of these %d records. Return one result per record, "
                       "using its screen_id and doi exactly as given.\n\n%s"
                       % (len(batch), "\n".join(json.dumps(r, ensure_ascii=False) for r in batch))}])))
    client = anthropic.Anthropic()
    made = client.messages.batches.create(requests=requests)
    d = outdir(which, pilot)
    json.dump(dict(recorded_utc=dt.datetime.now(dt.timezone.utc).isoformat(), batch_id=made.id, model=model,
                   pass_=which, seed=SEEDS[which], group_size=GROUP, requests=len(requests), records=len(records),
                   instructions_sha256=hashlib.sha256(INSTRUCTIONS.encode()).hexdigest(), plan=plan),
              open(d / "submission.json", "w", encoding="utf-8"), indent=1)
    print(made.id, made.processing_status, len(requests), "requests")


def collect(which, pilot):
    d = outdir(which, pilot)
    sub = json.load(open(d / "submission.json", encoding="utf-8"))
    client = anthropic.Anthropic()
    batch = client.messages.batches.retrieve(sub["batch_id"])
    if batch.processing_status != "ended":
        print(batch.processing_status, batch.request_counts)
        return
    labels, problems = {}, []
    with open(d / "raw_results.jsonl", "w", encoding="utf-8", newline="\n") as raw:
        for res in client.messages.batches.results(sub["batch_id"]):
            raw.write(res.to_json(indent=None) + "\n")
            expected = sub["plan"][res.custom_id]
            if res.result.type != "succeeded":
                problems.append(dict(custom_id=res.custom_id, type=res.result.type))
                continue
            msg = res.result.message
            text = next((b.text for b in msg.content if b.type == "text"), "")
            try:
                got = {r["screen_id"]: r for r in json.loads(text)["results"]}
            except (ValueError, KeyError):
                problems.append(dict(custom_id=res.custom_id, type="unparseable", stop_reason=msg.stop_reason))
                continue
            for sid in expected:
                if sid in got:
                    labels[sid] = got[sid]
                else:
                    problems.append(dict(custom_id=res.custom_id, type="missing_record", screen_id=sid))
            extra = set(got) - set(expected)
            if extra:
                problems.append(dict(custom_id=res.custom_id, type="unexpected_ids", ids=sorted(extra)))
    records = load(pilot)
    with open(d / ("pass_%s.jsonl" % which), "w", encoding="utf-8", newline="\n") as f:
        for r in records:
            if r["screen_id"] in labels:
                f.write(json.dumps(labels[r["screen_id"]], ensure_ascii=False) + "\n")
    json.dump(dict(recorded_utc=dt.datetime.now(dt.timezone.utc).isoformat(), labelled=len(labels),
                   records=len(records), problems=problems), open(d / "collection.json", "w"), indent=1)
    print(len(labels), "of", len(records), "labelled;", len(problems), "problems (resubmit those records)")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=("submit", "collect"))
    p.add_argument("--pass", dest="which", choices=("A", "B"), required=True)
    p.add_argument("--model", default="claude-opus-5")
    p.add_argument("--pilot", action="store_true")
    a = p.parse_args()
    submit(a.which, a.model, a.pilot) if a.action == "submit" else collect(a.which, a.pilot)
