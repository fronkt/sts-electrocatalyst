"""Deterministic merge of two independent pre-screen passes.

A record is logged PRESCREEN_EXCLUDED only when BOTH passes labelled it CLEARLY_IRRELEVANT.
Every other record (including any record missing from either pass) goes to FULL_TEXT_REVIEW.
Nothing here is a final eligibility decision; method fields stay NOT_CODED.

  python merge_passes.py --a pilot/pass_A.jsonl --b pilot/pass_B.jsonl --out pilot/merge [--key pilot/pilot_key.json]
"""
import argparse
import collections
import csv
import datetime as dt
import hashlib
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent


def read(path):
    return {r["screen_id"]: r for r in (json.loads(l) for l in open(path, encoding="utf-8") if l.strip())}


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--a", required=True)
    p.add_argument("--b", required=True)
    p.add_argument("--inputs", nargs="*", default=None, help="input JSONL files (default: all chunks)")
    p.add_argument("--out", required=True)
    p.add_argument("--key", default=None, help="pilot sentinel key (known-eligible screen_ids)")
    a = p.parse_args()
    files = a.inputs or sorted(str(f) for f in HERE.glob("inputs/chunk_*.jsonl"))
    records = [json.loads(l) for f in files for l in open(f, encoding="utf-8")]
    A, B = read(a.a), read(a.b)
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows, pair = [], collections.Counter()
    for r in records:
        la = A.get(r["screen_id"], {}).get("label", "MISSING")
        lb = B.get(r["screen_id"], {}).get("label", "MISSING")
        pair[(la, lb)] += 1
        route = "PRESCREEN_EXCLUDED" if la == lb == "CLEARLY_IRRELEVANT" else "FULL_TEXT_REVIEW"
        rows.append(dict(screen_id=r["screen_id"], doi=r.get("doi") or "", title=r.get("title") or "",
                         publication_date=r.get("publication_date") or "", label_a=la, label_b=lb,
                         reason_a=A.get(r["screen_id"], {}).get("reason", ""),
                         reason_b=B.get(r["screen_id"], {}).get("reason", ""), route=route,
                         eligibility_status="NOT_DECIDED", method_status="NOT_CODED"))
    with open(out / "merged_routes.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    ci = lambda x: x == "CLEARLY_IRRELEVANT"
    agree = sum(n for (x, y), n in pair.items() if ci(x) == ci(y))
    summary = dict(
        recorded_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
        inputs={f: sha(f) for f in files}, pass_a=dict(path=a.a, sha256=sha(a.a)), pass_b=dict(path=a.b, sha256=sha(a.b)),
        records=len(rows), routes=collections.Counter(r["route"] for r in rows),
        label_pairs={"%s|%s" % k: v for k, v in sorted(pair.items())},
        exclusion_agreement=dict(agree=agree, disagree=len(rows) - agree, rate=round(agree / len(rows), 4)),
        rule="PRESCREEN_EXCLUDED only when both independent passes label CLEARLY_IRRELEVANT; all else FULL_TEXT_REVIEW")
    if a.key:
        key = json.load(open(a.key))["known_eligible_sentinels"]
        by = {r["screen_id"]: r for r in rows}
        summary["sentinels"] = {s: dict(route=by[s]["route"], a=by[s]["label_a"], b=by[s]["label_b"]) for s in key}
        summary["sentinel_recall"] = sum(by[s]["route"] == "FULL_TEXT_REVIEW" for s in key) / len(key)
    json.dump(summary, open(out / "merge_summary.json", "w", encoding="utf-8"), indent=1)
    print(json.dumps({k: summary[k] for k in summary if k not in ("inputs", "sentinels")}, indent=1))
    if a.key:
        print(json.dumps(summary["sentinels"], indent=1))


if __name__ == "__main__":
    main()
