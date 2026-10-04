"""Assemble readout.md of this phase from recovered_manifest.json, search_log.jsonl and the identity files."""
import collections
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import si_recovery_lib as L  # noqa: E402

M = json.loads((L.PHASE / "recovered_manifest.json").read_text(encoding="utf-8"))
rows = [json.loads(l) for l in open(L.LOG, encoding="utf-8")]
T = json.loads((L.PHASE / "targets.json").read_text(encoding="utf-8"))["targets"]
cdn = [r for r in rows if r["route"] == "els_cdn_mmc"]
by_status = collections.Counter(r["http_status"] for r in cdn)
by_outcome = collections.Counter(r["outcome"] for r in rows)
pk = {p["screen_id"]: p for p in M["packages"]}
nr = {n["screen_id"]: n for n in M["not_recovered"]}
gates_here = L._read_gates(L.GATES)
ids = [t["screen_id"] for t in T]

o = []
o.append("# Elsevier asset-CDN extension, 2026-10-04 (retrieval only)\n")
o.append("No screening or eligibility decision is made here. Packages listed below are ready for two independent blind reads; whether to run them is the coordinator's call.\n")
o.append("## 1. Scope\n")
o.append("- Frank, in session, 2026-10-04: keep the 11 Elsevier-CDN packages of `public_si_recovery_2026-10-04/` and extend the same route to the 10 non-tier-1 Elsevier checklist records: %s." % ", ".join(ids))
o.append("- Targets come from `si_checklist.csv` (tiers 2: S22127, S23544, S31125; 3: S00882, S14386, S21070, S30334; 4: S21253, S22941, S29795) and `reconcile/current_state.csv`; see `targets.json`.")
o.append("- Method, unchanged from `els_cdn.py` of the earlier round: identity first (Crossref and OpenAlex by exact DOI; PII from the Crossref `alternative-id`, equal to the PII in the checklist's ScienceDirect link for all 10), then plain HTTP GET of `https://ars.els-cdn.com/content/image/1-s2.0-<PII>-mmc<N>.<ext>` with an honest User-Agent, 5 s spacing, no key, no login, no api.elsevier.com, no proxy, no browser. mmc1 was tried with pdf, docx, zip, xlsx, doc; each mmc<N> that existed was followed by mmc<N+1>. For the one record with no hit, seven more extensions (xls, pptx, txt, csv, mp4, docm, rtf) were tried for the exact mmc1 name.")
o.append("- The OpenAlex key was read from `~/.config/openalex/api_key` at request time; it is in no file of this directory (scanned).\n")
o.append("## 2. Outcomes\n")
o.append("Final outcome per record: **recovered %d, not-found %d** (total %d). Requests to ars.els-cdn.com: %d (HTTP 200: %d, HTTP 404: %d); none was refused or challenged, so no host was gated in this phase (`host_gates.json` was not created; hosts gated in the earlier phase stay gated, read only). Route rows in `search_log.jsonl`: %d (recovered %d, not-found %d; the %d `recovered` rows are the %d CDN files plus %d record-final rows)." % (
    len(pk), len(nr), len(ids), len(cdn), by_status.get(200, 0), by_status.get(404, 0), len(rows), by_outcome.get("recovered", 0),
    by_outcome.get("not-found", 0), by_outcome.get("recovered", 0), by_status.get(200, 0), len(pk)))
o.append("A 404 is logged per exact URL; it is never evidence that no supplement exists.\n")
o.append("| id | tier | journal | final | files | pages | note |")
o.append("|---|---|---|---|---|---|---|")
for t in T:
    sid = t["screen_id"]
    if sid in pk:
        p = pk[sid]
        files = ", ".join(pathlib.Path(f["local_path"]).name for f in p["files"])
        o.append("| %s | %d | %s | recovered | %s | %s | %s |" % (sid, t["checklist_tier"], p["identity_confirmation_crossref_openalex"]["crossref_container"].replace("&amp;", "and"),
                                                        files, p["pages"] if p["pages"] is not None else "not claimed", p["pages_basis"]))
    else:
        n = nr[sid]
        o.append("| %s | %d | %s | %s | none | | mmc1 absent for 12 extensions on the CDN; lead noted in section 5 |" % (
            sid, t["checklist_tier"], json.loads((L.META / ("%s_identity.json" % sid)).read_text(encoding="utf-8"))["identity_checks"]["crossref_container"].replace("&amp;", "and"), n["outcome"]))
o.append("")
o.append("## 3. Recovered packages (details in `recovered_manifest.json`)\n")
o.append("| id | pages | route | identity | completeness | caveat |")
o.append("|---|---|---|---|---|---|")
for sid in ids:
    if sid not in pk:
        continue
    p = pk[sid]
    ie, ce = p["identity_evidence"], p["completeness_evidence"]
    title_ok = ie["title_full_in_si_text"] or ie["title_full_compact_in_si_text"]
    o.append("| %s | %s | %s | title in SI text=%s; %s | %d main-referenced SI items, %d missing; %d caption labels | %s |" % (
        sid, p["pages"] if p["pages"] is not None else "n/a", p["source_route"], title_ok, ie["author_surnames_found_in_si"],
        len(ce["main_text_SI_items_referenced"]), len(ce["main_referenced_items_missing_from_SI_text"]), len(ce["SI_caption_labels_found"]), p["caveats"]))
o.append("")
o.append("Identity confirmation by Crossref and OpenAlex (exact DOI): the Crossref title equals the checklist title for 9 records; for S22941 the Crossref title carries MathML markup and the OpenAlex title ('Lattice oxygen evolution in rutile Ru 1-x Ni x O 2 electrocatalysts') equals the checklist title. The Crossref PII equals the checklist PII for all 10; the first Crossref author's surname is in the head of the corpus main text for all 10 (`metadata/<SID>_identity.json`).")
o.append("Page counts: PDF pages for S14386 and S30334; Word-stored page counts (docProps/app.xml) for the Word files, since no layout render is available; S00882 is a binary Word 97-2003 file whose text and tables were read with antiword, so no page count is claimed. Images inside Word files were counted, not read.\n")
o.append("### Ready for two independent blind reads\n")
o.append("All %d recovered packages: %s." % (len(pk), ", ".join(pk)))
o.append("Needs visual reading: S00882 (one embedded image, the Pourbaix diagram 'Fig. SI', outside the text). Figure-heavy Word and PDF files (most of them) have figures as images whose plotted values are not in the text. S22941 is not recovered.\n")
o.append("## 4. Gates hit\n")
o.append("None in this phase. All %d CDN requests were answered 200 or 404 with no challenge page. Hosts gated earlier (www.sciencedirect.com, onlinelibrary.wiley.com and the others in `public_si_recovery_2026-10-04/host_gates.json`) were not requested.\n" % len(cdn))
o.append("## 5. Findings reported, not decided\n")
o.append("- **S22941, not recovered.** The main text states: 'Structures and scripts are available in the electronic supplementary material at link: https://nano.ku.dk/english/research/theoretical-electrocatalysis/katladb/loer-runio2/'. That is a public University of Copenhagen page outside the approved Elsevier-CDN route; it was not requested. Whether the article also has an Elsevier-hosted mmc file under another name is not known.")
o.append("- **S31125.** The SI's title differs from the published title (SI: 'Molybdenum-mediated electronic modulation of RuO2 for balancing oxygen intermediate adsorption and lattice oxygen participation in acidic oxygen evolution reaction'; article: 'Mo-mediated electronic modulation of RuO2 for improved acidic oxygen evolution activity and Ru retention'). Same four authors (the SI prints the last as 'Yang Ji', Crossref has 'Ji Yang'), same sample names, and the main text's Fig. S1 and Tables S3-S4 match the SI's own captions. Identity rests on the exact PII file plus those matches.")
o.append("- **S22127.** mmc1.docx and mmc2.docx are two different files (different sha256) with identical paragraph text (640 of 640) and byte-identical media members; they differ in Word markup only. One SI, text read once.")
o.append("- **S00882.** 2013 article; the SI is a binary .doc (sections a-f, with tables of free enthalpies and one figure). Main text names no numbered SI item.")
o.append("- **S30334.** The completeness script reported 'Section S6' as missing; that is a false hit on 'Sections 6.6.1 and 6.6.2' of the main text. Nothing the main text names is missing.")
o.append("- **Dates (facts only).** Crossref issue date versus OpenAlex publication date: " + "; ".join(
    "%s %s vs %s" % (sid, "-".join("%02d" % x if i else str(x) for i, x in enumerate((pk[sid]["identity_confirmation_crossref_openalex"]["crossref_issued"] or [[0]])[0])),
                     pk[sid]["identity_confirmation_crossref_openalex"]["openalex_publication_date"]) for sid in ids if sid in pk) + ". Existing date reconciliation (`reconcile/date_check.csv`) is not touched here.\n")
o.append("## 6. Files\n")
o.append("In `results/s2_2026-09-25/full_text/public_si_recovery_2026-10-04_ext/`: `search_log.jsonl`, `recovered_manifest.json`, `readout.md`, `targets.json`, `downloads.jsonl`, `outcomes_logged.json`, `els_run.out`, `metadata/` (Crossref/OpenAlex identity files, verify evidence and extracted SI text; local only), `files/` (downloaded binaries; local only, ignored by git through the `results/` rule), and the scripts used (`si_recovery_lib.py`, `build_targets.py`, `meta_check.py`, `els_cdn.py`, `verify_si.py`, `build_manifest.py`, `relog_final_rows.py`, `write_readout.py`). No existing file was changed.")
(L.PHASE / "readout.md").write_text("\n".join(o) + "\n", encoding="utf-8")
print("readout.md", sum(len(x) for x in o))
