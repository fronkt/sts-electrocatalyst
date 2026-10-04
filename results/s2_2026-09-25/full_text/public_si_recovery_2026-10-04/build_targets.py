"""Derive the 2026-10-04 target list from si_checklist.csv (read-only) and reconcile/current_state.csv.

Tier 1 = the SI decides eligibility (E1-E5 YES and E6 UNCLEAR, or a forced-question ELIGIBLE record).
Priority inside tier 1 (checklist order breaks ties):
  0  ELIGIBLE records on the checklist (forced eligible-question IDs: the SI answers an open question)
  1  records whose deciding rows name specific SI items (Fig. S.., Table S..)
  2  D10 checks (does any SI exist - needs publisher evidence)
  3  remaining tier-1 NEEDS_SI records
Known dead ends from the handoff are not re-searched (logged as skipped, not counted as processed).
Cap: about 40 processed records, then stop.
"""
import csv
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
FT = HERE.parent
DEAD_ENDS = {
    "S11392": "journal lead is existing S13010 (SI reads complete); pairwise version linkage only, no duplicate screening",
    "S13316": "public package is 17 main-figure images, not SI",
    "S14704": "NSF PAR copy is accepted manuscript only (main-only)",
    "S11549": "laboratory repository copy is main article only",
    "S23244": "Bicocca repository item has no files",
    "S22690": "discovery unresolved in prior phases (handoff: do not redo)",
}
CAP = 40

rows = list(csv.DictReader(open(FT / "si_checklist.csv", encoding="utf-8")))
state = {r["screen_id"]: r for r in csv.DictReader(open(FT / "reconcile/current_state.csv", encoding="utf-8"))}
tier1 = [r for r in rows if r["tier"] == "1"]


def group(r):
    if r["v5_final"] == "ELIGIBLE":
        return 0
    if r["si_items"].strip():
        return 1
    if r["d10_check"] == "True":
        return 2
    return 3


order = {r["screen_id"]: i for i, r in enumerate(rows)}
ranked = sorted(tier1, key=lambda r: (group(r), order[r["screen_id"]]))
out = {"derived_from": ["si_checklist.csv", "reconcile/current_state.csv"], "checklist_rows": len(rows),
       "tier1_rows": len(tier1), "dead_ends": DEAD_ENDS, "cap": CAP, "targets": [], "skipped_dead_end": [],
       "not_reached": []}
n = 0
for r in ranked:
    sid = r["screen_id"]
    rec = {"screen_id": sid, "doi": r["doi"], "publisher": r["publisher"], "title": r["title"],
           "v5_final": r["v5_final"], "open_criteria": r["open_criteria"], "si_items": r["si_items"],
           "expected_file": r["file"], "d10_check": r["d10_check"] == "True",
           "checklist_publisher_page_blocked": r["publisher_page_blocked"] == "True",
           "priority_group": group(r), "current_v5_final": state[sid]["v5_final"]}
    if sid in DEAD_ENDS:
        rec["skip_reason"] = DEAD_ENDS[sid]
        out["skipped_dead_end"].append(rec)
    elif n < CAP:
        n += 1
        rec["rank"] = n
        out["targets"].append(rec)
    else:
        out["not_reached"].append(rec)
(HERE / "targets.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
print("tier1", len(tier1), "targets", len(out["targets"]), "dead-end skips", len(out["skipped_dead_end"]),
      "not reached", len(out["not_reached"]))
for t in out["targets"]:
    print(t["rank"], t["screen_id"], t["publisher"], t["priority_group"], t["doi"])
print("NOT REACHED:", [t["screen_id"] for t in out["not_reached"]])
