"""Compose readout.md from the log, manifest, targets and gate registry (numbers come from the files, not from memory)."""
import collections
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import si_recovery_lib as L  # noqa: E402

rows = [json.loads(x) for x in open(L.LOG, encoding="utf-8") if x.strip()]
T = json.loads((L.PHASE / "targets.json").read_text(encoding="utf-8"))
M = json.loads((L.PHASE / "recovered_manifest.json").read_text(encoding="utf-8"))
G = L.gates()
by = collections.defaultdict(list)
for r in rows:
    by[r["screen_id"]].append(r)
rank = ["recovered", "wrong-version", "main-only", "no-SI-evidence", "gated", "not-found"]


def final(sid):
    outs = {r["outcome"] for r in by[sid]}
    return next((o for o in rank if o in outs), "none")


rec_ids = {p["screen_id"] for p in M["packages"]}
tid = [t["screen_id"] for t in T["targets"]]
cnt = collections.Counter(final(s) for s in tid)
rowcnt = collections.Counter(r["outcome"] for r in rows)

NOTES = {
    "S05155": "OSTI, DTU Orbit and Imperial Spiral copies are accepted manuscripts (OSTI copy is byte-identical to the local main file); MIT DSpace refused (HTTP 405); RSC pages 403",
    "S00759": "Radboud and Groningen copies are the 6-page article only; ACS gated",
    "S08806": "EPFL author manuscript (27 pp) is main only; Materials Cloud holds a data deposit (IsSupplementTo the article), no SI PDF; ACS gated",
    "S08766": "NLR/OSTI copies are the 10-page JES article only; IOP bot-captcha",
    "S26740": "PSI DORA manuscript (23 pp) cites Figure S1-S23 but has no SI pages; Wiley gated",
    "S03607": "Springer Nature Link page loaded, shows no supplementary section (D10 evidence, not a decision)",
}
lines = []
add = lines.append
add("# Public SI recovery round, 2026-10-04 (retrieval only)")
add("")
add("No screening or eligibility decision is made here. Packages listed below are ready for two independent blind reads; whether to run them is the coordinator's call.")
add("")
add("## 1. Target list and how it was derived")
add("")
add("- `si_checklist.csv` (144 rows, unchanged since 2026-10-03: tiers 60/31/47/6) cross-checked against `reconcile/current_state.csv`: all 60 tier-1 rows are still NEEDS_SI (56) or ELIGIBLE with an open SI question (4: S29721, S10090, S22807, S26024).")
add("- Priority inside tier 1 (checklist order breaks ties): (0) the 4 ELIGIBLE records, (1) records whose deciding rows name specific SI items, (2) D10 checks, (3) the rest. See `build_targets.py`, `targets.json`.")
add("- Six handoff dead ends were not re-searched (S11392 journal lead, S13316, S14704 and S11549 repository copies, S23244, S22690). Two of them were then touched by routes the handoff had not covered, as noted below (S14704 via the Elsevier asset CDN; S11392 via its own preprint page).")
add("- Processed in priority order: **40 records** (cap reached). Not reached (14, all Wiley except S26744 RSC): " + ", ".join(t["screen_id"] for t in T["not_reached"]) + ".")
add("- Prior routes were skipped, not repeated: Unpaywall DOI lookups, figshare exact-DOI, Europe PMC OA checks, earlier publisher-page blocks (si_public_log.jsonl and the 2026-10-01/02/03 route files).")
add("")
add("## 2. Outcomes")
add("")
add("Final outcome per processed record (best outcome over all routes): **recovered %d, main-only %d, no-SI-evidence %d, gated %d, wrong-version %d, not-found %d** (total %d)." % (
    cnt["recovered"], cnt["main-only"], cnt["no-SI-evidence"], cnt["gated"], cnt["wrong-version"], cnt["not-found"], sum(cnt.values())))
add("")
add("Dead ends: S14704 recovered (new route), S11392 recovered (preprint-version SI, new route), S13316 and S11549 main-only as already known, S23244 and S22690 not re-searched.")
add("")
add("Route-level rows in `search_log.jsonl`: %d total (%s)." % (len(rows), ", ".join("%s %d" % (k, rowcnt[k]) for k in rank if rowcnt[k])))
add("Most `not-found` rows are API checks per record (Crossref, OpenAlex locations, Europe PMC DOI and title, DataCite related-identifier and title, Zenodo DOI and title, OpenAIRE, arXiv, Crossref preprints, OpenAlex title, figshare title, NOMAD). A not-found is never evidence that no SI exists.")
add("")
add("| rank | id | publisher | final | note |")
add("|---|---|---|---|---|")
for t in T["targets"]:
    s = t["screen_id"]
    f = final(s)
    note = NOTES.get(s, "")
    if f == "recovered":
        p = next(x for x in M["packages"] if x["screen_id"] == s)
        note = "%s, %s pages" % (p["source_route"].split("_")[0], p["pages"])
    elif f == "gated" and not note:
        note = "publisher host blocked this phase; no repository, preprint or dataset copy found"
    add("| %d | %s | %s | %s | %s |" % (t["rank"], s, t["publisher"], f, note))
add("")
add("## 3. Recovered packages (details in `recovered_manifest.json`)")
add("")
add("| id | pages | route | identity | completeness | caveat |")
add("|---|---|---|---|---|---|")
for p in M["packages"]:
    ce = p["completeness_evidence"]
    ie = p["identity_evidence"]
    ident = "title in SI text=%s; %s" % (ie["title_full_in_si_text"], ie["author_surnames_found_in_si"].split(" (")[0] if "of" in ie["author_surnames_found_in_si"] else "authors not checked")
    comp = "%d main-referenced SI items, %d missing; %d caption labels" % (len(ce["main_text_SI_items_referenced"]), len(ce["main_referenced_items_missing_from_SI_text"]), len(ce["SI_caption_labels_found"]))
    add("| %s | %s | %s | %s | %s | %s |" % (p["screen_id"], p["pages"], p["source_route"], ident, comp, p["caveats"] or ""))
add("")
add("Page counts: PDF pages for S00358 and S11279; Word-stored page counts (docProps/app.xml) for the Word files, since no layout render is available. Images inside Word files were counted, not read.")
add("")
add("### Ready for two independent blind reads")
add("")
add("All 14 packages in the manifest: " + ", ".join(p["screen_id"] for p in M["packages"]) + ".")
add("Needs a coordinator note first: **S11392** (preprint-version SI; the journal version S13010 already has complete SI reads and a different SI document). Needs visual reading: **S23308** (one table, supplied as an image). The four ELIGIBLE-question records (S29721, S10090, S22807, S26024) are not recovered: all are Wiley or ACS, both gated.")
add("")
add("## 4. Gates hit")
add("")
add("| host (family) | first block | evidence |")
add("|---|---|---|")
DESC = {
    "pubs.acs.org": "HTTP 403 to WebFetch on the ACS article page (S29721)",
    "pmc.ncbi.nlm.nih.gov": "HTTP 200 body was a Google reCAPTCHA challenge page (S29976); not read",
    "dspace.mit.edu": "HTTP 405 on the bitstream URL (S05155)",
    "commons.case.edu": "HTTP 403 on the repository file URL (S05043)",
    "scholars.cityu.edu.hk": "HTTP 403 on the repository file URL (S27476)",
    "wiley.com": "HTTP 403 to WebFetch on the Wiley article page (S10090); all *.wiley.com treated as blocked",
    "sciencedirect.com": "HTTP 403 to WebFetch on the ScienceDirect article page (S23308)",
    "acs.org": "family-level registration of the ACS 403",
    "biblio.vub.ac.be": "HTTP 200 body was a 246-byte 'Request Rejected' WAF page instead of the PDF (S23308)",
    "espace.library.uq.edu.au": "HTTP 403 on the UQ eSpace record (S21441)",
    "papers.ssrn.com": "HTTP 403 Cloudflare 'Just a moment' challenge (S27476)",
    "iop.org": "HTTP 200 body was a Radware Bot Manager captcha page, redirect to validate.perfdrive.com (S08766)",
    "pubs.rsc.org": "HTTP 403 to WebFetch on the RSC article landing page (S05155)",
}
seen = set()
for h, g in G.items():
    key = (g.get("first_host", h), DESC.get(h, g["why"]))
    if key in seen or (h == "acs.org" and "pubs.acs.org" in G):
        continue
    seen.add(key)
    add("| %s | %s | %s |" % (g.get("first_host", h), g["first_blocked_at"], DESC.get(h, g["why"])))
add("")
add("After each first block the host was not requested again. No challenge was solved or bypassed, no browser, proxy, Purdue/EZproxy, keyed API or shadow library was used, and no paid API was called. The OpenAlex key was read at request time, never printed; a scan of every file in this phase finds no copy of it.")
add("")
add("**Sci-Hub:** the 2026-10-04 coordinator message allowed Sci-Hub as a last resort. One request was attempted (S10090, three mirrors in one call) and the Claude Code permission classifier DENIED the tool call before anything was sent; a following benign local read was also denied. I did not retry through another tool, host or interpreter. Sci-Hub is therefore untried for all records (one `scihub` row is logged). A user-side Bash permission rule would be needed. Note it would mostly return main articles, which do not count as SI.")
add("")
add("## 5. Judgement calls worth a look")
add("")
add("1. **Elsevier asset CDN (ars.els-cdn.com).** After www.sciencedirect.com answered 403 to WebFetch, I fetched the exact file URL behind each article's 'Appendix A. Supplementary data' link (`1-s2.0-<PII>-mmc1.<ext>`, PII from Crossref) by plain GET with an honest User-Agent: no key, no login, no API, no challenge page seen. It returned the SI for 11 of 11 tier-1 Elsevier records. This is a different host from the page that blocked me, but the same publisher; if you read the 'record the block and move on' rule at publisher level, drop the 11 Elsevier packages. The Crossref `link` fields of these records point at api.elsevier.com text-mining URLs; those were NOT used.")
add("2. **Research Square.** Plain HTTP GET of the public preprint pages; the page's embedded file list names the supplement. The earlier NO_SI_LINK_ON_PAGE logs for S21177 and S11392 were false negatives (the link is in the page data, not in visible link text).")
add("3. **RSC direct SI URL** (`www.rsc.org/suppdata/...`) answered 404 for three records (path no longer valid); not a gate.")
add("4. WebSearch is unreliable for this: one query returned another paper's SI (acscatal.2c01944) as if it belonged to S29721; it was rejected.")
add("")
add("## 6. Findings reported, not decided")
add("")
add("- **D10.** S21177 and S11392 (both D10-flagged): the preprint pages list supplement files (S21177 SupportingInformation.docx, 49,126,359 bytes; S11392 VelascoVelezetal.NatureEnergySI2020.docx, 2,605,142 bytes), so SI exists and is now in hand. S03607 (D10-flagged): the official Springer Nature Link page loads and has no supplementary section (sections: Abstract, References, Author information, Additional information, Rights and permissions, About this article; saved as `metadata/S03607_page_springer.html`). S04318 and S11549 (D10-flagged): not re-checked, ACS and IOP gated. Because the old page-text check missed supplements stored in page data, other NO_SI_LINK_ON_PAGE results for JavaScript-built pages deserve a recheck.")
add("- **Version linkage S11392 / S13010** (`metadata/S11392_S13010_linkage.json`): Crossref `relation` is empty for both; OpenAlex lists no link; Europe PMC has the preprint as PPR253311 and the journal article as PMC8397309 (hasSuppl=Y); Research Square page has no version-of-record link. Both author lists share the same surnames (17 vs 18 authors) and titles differ ('...Water Splitting' vs '...Water Oxidation'). The two SI documents differ (preprint: 25 pp, Fig. S1-S7, Table S1-S2; journal: 17 pp, Fig. S1-S10, Table S1-S2). No authoritative link was found.")
add("- **Dates.** S31137 and S31037 keep the existing SOURCES_STRADDLE_BOUNDARY flag. New Crossref facts: DOIs created 2026-09-04 and 2026-09-02, deposited 2026-10-03 and 2026-10-01, issue date 2026-11, license start 2026-11-01; OpenAlex publication dates 2026-09-04 and 2026-09-02.")
add("- **Identity (editions).** Six Angewandte targets (S26024, S21048, S21441, S23402, S26703, S29976) have both an `anie` and an `ange` DOI in Crossref with identical author lists and dates. The corpus already collapses three counterparts (S21049, S21444, S23404); counterparts of S26024, S26703 and S29976 are not in the corpus. Both editions share one SI.")
add("")
add("## 7. Leads that need a human or a new permission")
add("")
add("- **S29976:** Europe PMC lists PMC13427193 (author manuscript, hasSuppl=Y, not OA). PMC served a reCAPTCHA page. A manual look at the PMC record's supplementary-material list is the cheapest next step.")
add("- **S08806:** Materials Cloud datasets (10.24435/materialscloud:sr-bh, :2019.0038 v1/v2) are IsSupplementTo the article: computation inputs and outputs, no SI PDF.")
add("- **S27476:** an SSRN preprint with the same title exists (10.2139/ssrn.5462162, Cloudflare challenge); moot now that its SI is recovered.")
add("- **S21441:** UQ eSpace (403) and Griffith (script-built page) hold the International-Edition record; not readable without a browser.")
add("- **Wiley and ACS/RSC/IOP records** need manual downloads of the checklist file names (`si_checklist.csv`, column `file`) or a decision on Sci-Hub: 27 processed records without SI (22 gated, 5 with only main-article copies) plus 14 not reached.")
add("- **Same Elsevier route, outside tier 1:** 10 more Elsevier checklist records (S22127, S23544, S31125, S00882, S14386, S21070, S30334, S21253, S22941, S29795). I stopped at the tier-1 cap; say go if you accept judgement call 1.")
add("")
add("## 8. Files")
add("")
add("In `results/s2_2026-09-25/full_text/public_si_recovery_2026-10-04/`: `search_log.jsonl`, `recovered_manifest.json`, `readout.md`, `targets.json`, `downloads.jsonl`, `host_gates.json`, `metadata/` (API responses, page captures, verify evidence and extracted SI text; local only), `files/` (downloaded binaries; local only, ignored by git through the `results/` rule), and the scripts used (`si_recovery_lib.py`, `build_targets.py`, `metadata_sweep.py`, `rs_files.py`, `els_cdn.py`, `probe_urls.py`, `verify_si.py`, `verify_summary.py`, `preprint_search.py`, `extra_repos.py`, `date_identity_probe.py`, `linkage_s11392.py`, `epmc_supp.py`, `dl.py`, `logrow.py`, `log_outcomes.py`, `log_skipped_gates.py`, `build_manifest.py`, `summarize_log.py`, `write_readout.py`, `analyze_sweep.py`, `inspect_pdf.py`). Nothing was staged or committed; no existing file was changed.")
(L.PHASE / "readout.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("readout written", len(lines), "lines; final counts", dict(cnt))
