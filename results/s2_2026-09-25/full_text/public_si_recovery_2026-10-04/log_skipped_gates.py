"""One row per still-unrecovered target for its publisher route, which the phase's gate registry stopped after the first
block (so the publisher site was not requested for these records)."""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import si_recovery_lib as L  # noqa: E402

T = json.loads((L.PHASE / "targets.json").read_text(encoding="utf-8"))
G = L.gates()
rows = [json.loads(l) for l in open(L.LOG, encoding="utf-8") if l.strip()]
recovered = {r["screen_id"] for r in rows if r["outcome"] == "recovered"}
have_pub_row = {r["screen_id"] for r in rows if r["route"].startswith(("webfetch_publisher", "iop_publisher", "springer_publisher"))}
FAM = {"10.1002": ("wiley.com", "Wiley"), "10.1021": ("acs.org", "ACS"), "10.1039": ("pubs.rsc.org", "RSC"), "10.1149": ("iop.org", "IOP/ECS")}
n = 0
for t in T["targets"]:
    sid, doi = t["screen_id"], t["doi"]
    if sid in recovered or sid in have_pub_row:
        continue
    fam = FAM.get(doi.split("/")[0])
    if not fam or fam[0] not in G:
        continue
    g = G[fam[0]]
    L.log(sid, doi, "publisher_site_not_requested_host_gated", "https://doi.org/" + doi, None, "gated",
          "%s publisher host(s) were blocked in this phase (%s at %s on %s); the rule is to record the block and move on, so the publisher "
          "article/SI page was not requested for this record. Earlier phases also logged %s publisher blocks (si_public_log.jsonl)." %
          (fam[1], g["why"], g["first_blocked_at"], g.get("first_host", fam[0]), fam[1]))
    n += 1
print("rows added", n)
