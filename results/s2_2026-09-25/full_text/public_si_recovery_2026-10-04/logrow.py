"""Append manual route attempts (e.g. WebFetch page reads) to search_log.jsonl.

  python logrow.py rows.json      rows.json = list of {screen_id, doi, route, url, status, outcome, note[, gate_host]}
A row with "gate_host" also records that host as gated for the rest of the phase.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import si_recovery_lib as L  # noqa: E402

rows = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
for r in rows:
    extra = {k: v for k, v in r.items() if k not in ("screen_id", "doi", "route", "url", "status", "outcome", "note", "gate_host")}
    L.log(r["screen_id"], r["doi"], r["route"], r["url"], r.get("status"), r["outcome"], r["note"], **extra)
    if r.get("gate_host"):
        L.gate_host(r["gate_host"], "%s (%s)" % (r.get("status"), r["route"]))
print("logged", len(rows))
