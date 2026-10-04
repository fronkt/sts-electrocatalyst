"""Target list of the extension round: the ten non-tier-1 Elsevier checklist records Frank approved on 2026-10-04.
Read-only inputs: si_checklist.csv, reconcile/current_state.csv.  Output: targets.json (this directory)."""
import csv
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import si_recovery_lib as L  # noqa: E402

IDS = ["S22127", "S23544", "S31125", "S00882", "S14386", "S21070", "S30334", "S21253", "S22941", "S29795"]
chk = {r["screen_id"]: r for r in csv.DictReader(open(L.FT / "si_checklist.csv", encoding="utf-8"))}
st = {r["screen_id"]: r for r in csv.DictReader(open(L.FT / "reconcile" / "current_state.csv", encoding="utf-8"))}
targets = []
for sid in IDS:
    c, s = chk[sid], st[sid]
    assert c["publisher"] == "Elsevier", sid
    pii_in_link = re.search(r"/pii/([A-Z0-9]+)", c["si_link"]).group(1)
    targets.append({"screen_id": sid, "doi": c["doi"], "title": c["title"], "publisher": c["publisher"],
                    "checklist_tier": int(c["tier"]), "checklist_si_items": c["si_items"],
                    "checklist_pii_from_si_link": pii_in_link, "current_v5_final": s["v5_final"],
                    "current_lane": s["lane"], "main_text": "text/%s.txt" % sid})
out = {"derived_from": ["si_checklist.csv", "reconcile/current_state.csv"],
       "approval": "Frank, in session, 2026-10-04: extend the Elsevier asset-CDN route to these ten non-tier-1 Elsevier checklist records",
       "targets": targets}
(L.PHASE / "targets.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
print(len(targets), "targets")
for t in targets:
    print(t["screen_id"], t["checklist_tier"], t["current_v5_final"], t["checklist_pii_from_si_link"], t["doi"])
