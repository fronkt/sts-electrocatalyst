"""Summarise the metadata sweep: for each target, every non-publisher lead (repository/preprint locations,
Europe PMC records with supplements, DataCite/Zenodo deposits, OpenAIRE instances, arXiv matches)."""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import si_recovery_lib as L  # noqa: E402

T = json.loads((L.PHASE / "targets.json").read_text(encoding="utf-8"))
PUBHOSTS = ("doi.org", "onlinelibrary.wiley.com", "sciencedirect.com", "pubs.acs.org", "pubs.rsc.org", "iopscience.iop.org",
            "link.springer.com", "pubmed.ncbi.nlm.nih.gov")
for rec in T["targets"]:
    sid = rec["screen_id"]
    p = L.META / ("%s_sweep.json" % sid)
    if not p.exists():
        print(sid, "NO SWEEP")
        continue
    m = json.loads(p.read_text(encoding="utf-8"))
    leads = []
    for loc in (m["openalex"].get("locations") or []):
        u = loc.get("pdf") or loc.get("landing") or ""
        if loc.get("stype") in ("repository", "preprint server") or not any(h in u for h in PUBHOSTS):
            leads.append(("oa_loc", loc.get("source"), loc.get("version"), u))
    for h in m.get("epmc_doi", []):
        leads.append(("epmc_doi", h.get("source"), h.get("id"), h.get("pmcid"), "OA=" + str(h.get("isOpenAccess")), "suppl=" + str(h.get("hasSuppl"))))
    for h in m.get("epmc_title", []):
        if h.get("doi") != rec["doi"]:
            leads.append(("epmc_title_other_version", h))
    for d in m.get("datacite_rel", []):
        leads.append(("datacite_rel", d["doi"], d["publisher"], d["title"], [r.get("relationType") for r in (d.get("related") or []) if (r.get("relatedIdentifier") or "").lower() == rec["doi"].lower()]))
    for d in m.get("datacite_title", []):
        leads.append(("datacite_title", d))
    for z in m.get("zenodo", []):
        leads.append(("zenodo", z))
    for u in m.get("openaire_instances", []):
        if not any(h in u for h in PUBHOSTS):
            leads.append(("openaire", u))
    for a in m.get("arxiv", []):
        leads.append(("arxiv", a))
    cr = m["crossref"]
    rel = cr.get("relation") or {}
    print("==", sid, rec["publisher"], rec["doi"], "| crossref relation:", sorted(rel) or "-", "| OA:", (m["openalex"].get("open_access") or {}).get("oa_status"))
    for l in leads:
        print("    ", json.dumps(l, ensure_ascii=False)[:420])
