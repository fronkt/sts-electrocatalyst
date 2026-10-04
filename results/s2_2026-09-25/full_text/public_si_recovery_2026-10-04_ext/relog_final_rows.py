"""Housekeeping inside this phase directory only: drop the record_final_outcome rows of search_log.jsonl and the
outcomes_logged.json marker so that build_manifest.py can append them again with corrected wording.  Touches no other file."""
import json
import pathlib

here = pathlib.Path(__file__).resolve().parent
log = here / "search_log.jsonl"
rows = [json.loads(l) for l in open(log, encoding="utf-8") if l.strip()]
keep = [r for r in rows if r["route"] != "record_final_outcome"]
log.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in keep), encoding="utf-8")
marker = here / "outcomes_logged.json"
if marker.exists():
    marker.unlink()
print("rows kept", len(keep), "dropped", len(rows) - len(keep))
