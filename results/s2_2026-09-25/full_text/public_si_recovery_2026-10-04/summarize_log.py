"""Count search_log.jsonl rows by outcome and route, and derive each target's final per-record outcome."""
import collections
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import si_recovery_lib as L  # noqa: E402

rows = [json.loads(l) for l in open(L.LOG, encoding="utf-8") if l.strip()]
print("rows", len(rows))
print("by outcome", dict(collections.Counter(r["outcome"] for r in rows)))
print("by route", dict(collections.Counter(r["route"] for r in rows)))
T = json.loads((L.PHASE / "targets.json").read_text(encoding="utf-8"))
tid = [t["screen_id"] for t in T["targets"]]
by = collections.defaultdict(list)
for r in rows:
    by[r["screen_id"]].append(r)
final = {}
rank = ["recovered", "wrong-version", "main-only", "no-SI-evidence", "gated", "not-found"]
for sid in tid + [t["screen_id"] for t in T["skipped_dead_end"]]:
    outs = {r["outcome"] for r in by[sid]}
    final[sid] = next((o for o in rank if o in outs), "none")
print("final per record (40 processed):", dict(collections.Counter(final[s] for s in tid)))
print("final dead ends:", {s: final[s] for s in [t["screen_id"] for t in T["skipped_dead_end"]]})
print("rows per record min/max", min(len(by[s]) for s in tid), max(len(by[s]) for s in tid))
for s in tid:
    print(s, final[s], len(by[s]))
