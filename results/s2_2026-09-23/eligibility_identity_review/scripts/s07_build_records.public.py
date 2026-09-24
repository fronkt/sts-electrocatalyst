"""Assemble eligibility_records.json, identity_records.json and summary.json.

Assessments are data transcribed from the primary-source inspection in this review (locators
refer to PDF page numbers of the named evidence item, or to section/figure labels of HTML
full text). Local files are re-hashed here; browser-session evidence carries the SHA-256 computed
in the browser at read time (bytes not retained locally). Method-reporting outcome fields are
NOT recorded. No P-LIT proportion or verdict is computed.
"""
import hashlib
import json
import pathlib
import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()


def h(rel):
    p = REPO / rel
    return {"path": rel, "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size}


def local_glob(pattern):
    ps = sorted((ROOT / "files").glob(pattern))
    return [h(str(p.relative_to(REPO)).replace("\\", "/")) for p in ps]


PAPERS = "docs/research/papers"
ACC20 = "docs/research/papers/2026-09-20-access"

BROWSER = "BROWSER_SESSION_READ (ordinary Chrome session; sha256 computed in-browser at read time; bytes not retained locally)"
INST = "INSTITUTIONAL_SUBSCRIPTION_SESSION (institutional library subscription; publisher page labels access 'Purdue'; read-only, no file saved)"


def crit(pr, date, oer, rut, f110, che):
    return {"primary_research": pr, "first_publication_in_window": date, "oer_calculated": oer,
            "rutile_oxide": rut, "surface_110": f110, "che_overpotential_reported_article_or_si": che}


CASES = [
 {
  "case_id": "T01", "label": "Inico 2024", "doi": "10.1002/cctc.202400813",
  "prior": {"source": "results/s2_2026-09-20/reviewed_eligibility_subset.json", "disposition": "UNRESOLVED", "gap": "reported CHE eta; SI missing"},
  "evidence": {"local": [h(f"{PAPERS}/Inico-2024_ChemCatChem_stability-solvation-TiO2-RuO2-IrO2-110.pdf")],
               "remote": [{"item": "official SI cctc202400813-sup-0001-misc_information.pdf (Wiley, CC-BY article)", "route": BROWSER,
                           "sha256": "eb918e40cee22bfc45e67fa143deac7e586ffe2830cb36bb52008f3429e7125d", "bytes": 753762, "pages": 6,
                           "read_utc": "2026-09-24 browser session (approx. 01:45-02:00 UTC)","note": "Scripted GETs to Wiley returned HTTP 403 (receipts.jsonl); SI read via browser session."}]},
  "pass1": {"criteria": crit(
      "YES - original DFT/AIMD comparison, article p2 methods",
      "YES - publisher first published 2024-07-19; Crossref online 2024-09-12 (both retained)",
      "PARTIAL - stability/solvation of OER intermediates (-OH/-O-H, -OOH/-OO-H) only; no full OER free-energy pathway (article Table 1 p5, Fig 4 p6)",
      "YES - article p2 'three oxides display a rutile crystal structure'",
      "YES - title; article Figs 1-3 (110) surfaces",
      "NO - full-text search of all 11 article pages and all 6 SI pages: no overpotential, eta, limiting potential or 1.23 V construction; Fig 4 p6 plots relative free energies of intermediate couples (visually checked), not an overpotential"),
      "disposition": "EXCLUDE", "failed_criterion": "che_overpotential_reported_article_or_si"},
  "pass2": {"criteria": crit("YES", "YES (2024-07-19 / 2024-09-12)",
      "PARTIAL - CHE used for relative stability of intermediates (article p3 'Computational Hydrogen Electrode'); SI Tables S1-S7 geometries, SI Figs S1-S4 pair distribution functions",
      "YES (article p2, p3 'rutile-like')", "YES",
      "NO - SI pp1-6 contain lattice/cell tables, bond-length tables and PDFs; no eta anywhere in article or SI"),
      "disposition": "EXCLUDE", "failed_criterion": "che_overpotential_reported_article_or_si"},
 },
 {
  "case_id": "T02", "label": "Gauthier 2017", "doi": "10.1021/acs.jpcc.7b02383",
  "prior": {"source": "results/s2_2026-09-20/reviewed_eligibility_subset.json", "disposition": "UNRESOLVED", "gap": "separately reported eta; final version/SI inventory"},
  "evidence": {"local": [h(f"{PAPERS}/Gauthier-2017_JPCC_solvation-IrO2-110.pdf")],
               "remote": [{"item": "final published HTML full text, pubs.acs.org (J. Phys. Chem. C 121(21) 11455)", "route": INST,
                           "innertext_sha256": "9590fe4543b7aa972422a51cf3aea633550d6bf0fa36ba26337e1bb3c3455167", "chars": 49172,
                           "note": "Article page has no Supporting Information section (checked page text); OSTI record 1369414 has no full-text link."}]},
  "pass1": {"criteria": crit("YES", "YES - OSTI 2017-05-11, Crossref online 2017-05-17",
      "YES - OER intermediates and free-energy diagram, section 3.2-3.3",
      "YES - 'rutile IrO2(110)' abstract, Computational Details, Fig 4/5/7 captions", "YES",
      "NO - final text: Fig 7 free-energy diagram at 0 V vs RHE (visually checked, no eta annotation); text states only that a potential above 1.23 V is required and that concerted *OOH removal costs 1.8 eV; no reported overpotential/limiting potential; no SI"),
      "disposition": "EXCLUDE", "failed_criterion": "che_overpotential_reported_article_or_si"},
  "pass2": {"criteria": crit("YES", "YES", "YES",
      "YES", "YES",
      "NO - 'overpotential' occurs only in the introduction and reference titles; Fig 5 plots descriptors (dG_O-dG_OH, dG_OOH-dG_OH), not eta; deriving 1.8-1.23 would be a reviewer calculation, not a reported value"),
      "disposition": "EXCLUDE", "failed_criterion": "che_overpotential_reported_article_or_si"},
  "access_caveat": "Final-version evidence came through an institutional subscription session. If the batch rule is read as open-access only, this case reverts to UNRESOLVED (proof copy only)."
 },
 {
  "case_id": "T03", "label": "Exner 2020", "doi": "10.1021/acscatal.0c03865",
  "prior": {"source": "results/s2_2026-09-20/reviewed_eligibility_subset.json", "disposition": "UNRESOLVED", "gap": "primary-research rule application"},
  "evidence": {"local": [h(f"{PAPERS}/Exner-2020_ACSCatal_universal-descriptor-beyond-eta.pdf"), h(f"{ACC20}/exner_si_13100308_1.pdf")], "remote": []},
  "pass1": {"criteria": crit(
      "NO (as a calculating study) - Viewpoint introducing descriptor Gmax(eta); article p6 'the same data set is used to validate Gmax'",
      "YES - Crossref online 2020-10-15",
      "NO own calculation - SI S1 p2 'The data is taken from the work of Viswanathan and co-workers' for RuO2(110) free energies; Gmax values are arithmetic on published dG",
      "YES (RuO2/IrO2 (110) data sets)", "YES",
      "REPRODUCED ONLY - thermodynamic overpotentials come from the reused literature data"),
      "disposition": "EXCLUDE", "failed_criterion": "oer_calculated (no own OER electronic-structure calculation; CHE eta values are reused literature values)"},
  "pass2": {"criteria": crit(
      "UNCLEAR by label; decisive point is below", "YES",
      "NO - SI Section 1 pp2-6 derives Gmax for RuO2(110) from dG1-dG4 attributed to ref 6; SI Table p8 G#rds values attributed to refs 7 and 10; no computational-details section or DFT setup of its own",
      "YES", "YES", "REPRODUCED ONLY"),
      "disposition": "EXCLUDE", "failed_criterion": "oer_calculated"},
  "rule_note": "Rule-application decision: 'calculating OER on a rutile-oxide (110) surface' read as requiring the study's own OER energetics calculation (consistent with the Tripkovic and Cao reasons in prior records). A human adjudicator who reads 'calculating' to include descriptor arithmetic on published energies would reverse this. Flagged for adjudication."
 },
 {
  "case_id": "T04", "label": "Divanis 2020", "doi": "10.1039/c9sc05897d",
  "prior": {"source": "results/s2_2026-09-20/reviewed_eligibility_subset.json", "disposition": "UNRESOLVED", "gap": "rutile polymorph locator for new TiO2(110) arm"},
  "evidence": {"local": local_glob("divanis2020_curis_pdf__*") + local_glob("divanis2020_epmc_xml__*") + local_glob("divanis2020_epmc_suppl__*") +
               local_glob("divanis2020_katladb_page__*") + local_glob("divanis2020_erda_data__*") +
               [h(str(p.relative_to(REPO)).replace("\\", "/")) for p in sorted((ROOT / "files/divanis2020_erda_members").glob("*"))] +
               [h("results/s2_2026-09-23/eligibility_identity_review/divanis2020_erda_traj_listing.json")],
               "remote": [], "notes": [
                 "Europe PMC supplementary zip member SC-011-C9SC05897D-s001.pdf is byte-identical to the local ESI (sha256 348462f7...).",
                 "The KU CURIS PDF labelled submittedVersion by Unpaywall carries the published RSC header ('Published on 11 February 2020').",
                 "katlaDB trajectories archive (3,502,414,611 bytes) was NOT downloaded; only its zip central directory and two small members were fetched by HTTP Range (receipts.jsonl)."]},
  "pass1": {"criteria": crit(
      "YES - new one/two-dopant TiO2 calculations, article section 2.1 (EPMC XML / CURIS p9)",
      "YES - published 2020-02-11",
      "YES - OH*/O*/OOH* on doped TiO2; ESI Fig SI-18 free-energy diagram and volcano",
      "YES - author-deposited host slab TiO2_double_dopants/2Pt/clean/TiO2-fd.traj (linked from the article Conclusions katlaDB URL): Ti24O48 slab, in-plane cell 6.557 x 8.947 A = sqrt2*a x 3c of rutile (a~4.64, c~2.98 A); anatase (110)/(101) cells are incompatible; GPAW log TiO2-2Pt-3-fd.txt shows the identical cell for the doped slab",
      "YES - article section 3 'TiO2(110) structure'",
      "YES_GRAPHICAL - ESI p27 Fig SI-18 eta_OER arrow (prior visual check; not re-derived numerically)"),
      "disposition": "ELIGIBLE_PENDING_DISCOVERY_FREEZE"},
  "pass2": {"criteria": crit("YES", "YES", "YES",
      "YES - same deposited host slab: 6 five-fold and 18 six-fold Ti (the 5c-Ti/cus motif of rutile (110)), shortest Ti-Ti 2.982 A (edge-sharing chains along rutile c); katlaDB data CSV row label 'Nb-Ti15O32 5c-M (cus(M))' uses the rutile-(110) cus nomenclature",
      "YES", "YES_GRAPHICAL (ESI p27)"),
      "disposition": "ELIGIBLE_PENDING_DISCOVERY_FREEZE"},
  "rule_note": "No literal word 'rutile' appears in article or ESI; polymorph established from the authors' own deposited structure files (ERDA share, Last-Modified 2021-04-27, after publication). Accepting deposited primary structure data as the polymorph locator is a reviewer judgment recorded here for adjudication."
 },
 {
  "case_id": "T05", "label": "Mom 2014", "doi": "10.1021/jp409373c",
  "prior": {"source": "results/s2_2026-09-20/reviewed_eligibility_subset.json", "disposition": "UNRESOLVED", "gap": "primary article missing"},
  "evidence": {"local": [h(f"{PAPERS}/Mom-2014_JPCC_unrestricted-DFT-OER-oxides_SI.pdf")],
               "remote": [{"item": "final published HTML full text, pubs.acs.org (J. Phys. Chem. C 118(8) 4095)", "route": INST,
                           "innertext_sha256": "1e5249d6869442ef5f61faf5a248b4bfdc4ae03c938d361802082dff3ea52727", "chars": 45498}]},
  "pass1": {"criteria": crit("YES - own restricted/unrestricted DFT on oxide surfaces (Methods)",
      "YES - article header 2014-02-03 ASAP; Crossref online 2014-02-11",
      "YES - OH/O/OOH reaction energies, eq 6 thermodynamic overpotential",
      "YES - Methods: 'rutile structures of the SnO2, reduced SnO2, TiO2, PbO2, and PtO2'", "YES - Methods: 4x2 unit cell of the (110) surface; Table 1 orientation (110)",
      "YES_GRAPHICAL - reaction energies referenced to SHE with released protons 'taken into account as hydrogen' (Methods); eq 6 eta = max(dG_O-dG_OH, dG_OOH-dG_O) - 1.23; Fig 6b volcano y-axis -eta (restricted/unrestricted), Fig 6c eta differences (visually checked); SI Tables S1-S3 list the per-oxide reaction energies"),
      "disposition": "ELIGIBLE_PENDING_DISCOVERY_FREEZE"},
  "pass2": {"criteria": crit("YES", "YES", "YES", "YES (Methods)", "YES (Table 1)",
      "YES_GRAPHICAL - Fig 6b/6c report eta for the full calculated set, which includes the rutile (110) oxides; individual points are not labelled by material, and the SI (p2) gives energies plus instructions to compute eta rather than a tabulated eta"),
      "disposition": "ELIGIBLE_PENDING_DISCOVERY_FREEZE"},
  "rule_note": "Graphical eta covers the whole calculated set (rutile (110) plus rock-salt and perovskite surfaces) without per-point labels. Treated as a study-level reported CHE overpotential; flagged because the Xu inclusion cited named points.",
  "access_caveat": "Article text came through an institutional subscription session; under an open-access-only reading this case stays UNRESOLVED."
 },
 {
  "case_id": "P01", "label": "Zheng 2025 Sn-RuO2", "doi": "10.3390/catal15080770",
  "prior": {"source": "results/s2_2026-09-20/priority_primary_triage/reconciled_subset.json", "disposition": "UNRESOLVED", "gap": "CHE reference formalism (eqs 5-7)"},
  "evidence": {"local": local_glob("zheng2025_mdpi_*"),
               "remote": [{"item": "MDPI open-access HTML full text (CC BY)", "route": BROWSER,
                           "body_innertext_sha256": "cb0948bb4e2fad5f950a57a1173295c398722d7b3648a58370373f8edc592ab7", "chars": 44535,
                           "read_utc": "2026-09-24T01:38:29Z", "note": "Scripted GETs returned HTTP 403 bot pages (saved)."}]},
  "pass1": {"criteria": crit("YES - DFT+U study (section 3)", "YES - published 2025-08-13",
      "YES - eqs 1-4, Fig 4 free-energy diagrams",
      "YES - section 3 'p(2x2x2) rutile Ru16O32'; introduction 'Rutile-phase RuO2'",
      "YES - Sn/RuO2(110) and (1-10) slabs; undoped RuO2(110) control",
      "YES - eqs 5-7 reference each adsorbate to 1/2, 1 and 3/2 G_H2 (proton-electron pair as 1/2 H2); Fig 4 diagrams at U = 1.23 V; eq 8 eta_OER = max dG/e - 1.23 V; section 2.3 reports 46-Ru_cus 0.51 V and RuO2(110) 0.87 V (0.14 lower with U)"),
      "disposition": "ELIGIBLE_PENDING_DISCOVERY_FREEZE"},
  "pass2": {"criteria": crit("YES", "YES", "YES", "YES", "YES",
      "YES - hydrogen reference explicit in eqs 5-7; eq 4 uses 4.92 eV total; Fig 5b volcano of eta vs dG_O-dG_OH; SI Fig S3 RuO2(110) free-energy diagram listed"),
      "disposition": "ELIGIBLE_PENDING_DISCOVERY_FREEZE"},
 },
 {
  "case_id": "P02", "label": "IrO2 nanostructures 2021 (Appl. Surf. Sci.)", "doi": "10.1016/j.apsusc.2021.149591",
  "prior": {"source": "results/s2_2026-09-20/priority_primary_triage/reconciled_subset.json", "disposition": "UNRESOLVED", "gap": "full article/SI"},
  "evidence": {"local": local_glob("iro2nano_*"), "remote": [
      {"item": "ScienceDirect article page", "route": "BLOCKED - Cloudflare CAPTCHA challenge; not attempted (bot-check completion is prohibited)"},
      {"item": "Elsevier TDM API text/plain", "route": "HTTP 400 without API key"},
      {"item": "ars.els-cdn.com mmc1 pdf/docx", "route": "HTTP 404"}]},
  "pass1": {"criteria": crit("LIKELY_YES (DFT study per registry metadata)", "YES - Crossref print 2021-07", "UNKNOWN", "UNKNOWN", "UNKNOWN", "UNKNOWN"),
            "disposition": "UNRESOLVED", "missing": "article full text and SI"},
  "pass2": {"criteria": crit("UNKNOWN", "YES", "UNKNOWN", "UNKNOWN", "UNKNOWN", "UNKNOWN"),
            "disposition": "UNRESOLVED", "missing": "article full text and SI; a search-engine abstract summary mentions an overpotential for a 'rutile IrO2 bulk' comparison, which is not primary evidence and does not give the facet"},
 },
 {
  "case_id": "P03", "label": "Kuo 2017 JACS", "doi": "10.1021/jacs.6b11932",
  "prior": {"source": "results/s2_2026-09-20/priority_primary_triage/reconciled_subset.json", "disposition": "UNRESOLVED", "gap": "calculated surface, reported CHE eta, date conflict"},
  "evidence": {"local": [], "remote": [
      {"item": "final published HTML full text (JACS 139(9) 3473)", "route": INST, "innertext_sha256": "58f0ea4d6d363a504bdf9c9214b5f9c45554965af964f8e6ee777d37e6b8102c", "chars": 43992},
      {"item": "official SI ja6b11932_si_001.pdf", "route": INST, "sha256": "1d94ba1cb0741947790e85a5e395c2167bcf91fae3c09c5b432011899ac0ace7", "bytes": 1232183, "pages": 13}]},
  "pass1": {"criteria": crit("YES - experimental thin films plus DFT (FHI-aims) adsorption energies",
      "YES - ASAP 2017-02-09 / Crossref online 2017-02-21 (both retained)",
      "PARTIAL - DFT only for OH_ad and O_ad electroadsorption on Ir_cus; article: 'peak energies of OHad and Oad on Ircus are 0.92 and 1.31 V vs computational hydrogen electrode'",
      "YES - 'rutile IrO2(110) films'", "YES",
      "NO - all reported OER overpotentials are experimental (Fig 3c at 5 uA/cm2; SI Fig S4 p11); no computed OOH energetics or theoretical eta in article or SI (SI p2 CHE used for OH/O transition energies only)"),
      "disposition": "EXCLUDE", "failed_criterion": "che_overpotential_reported_article_or_si"},
  "pass2": {"criteria": crit("YES", "YES", "PARTIAL (OH/O only; OOH formation discussed via the dG_O-dG_OH approximation applied to experimental peaks, Fig 4c)", "YES", "YES",
      "NO - SI p6 kinetic rate-law analysis and p11 experimental eta only"),
      "disposition": "EXCLUDE", "failed_criterion": "che_overpotential_reported_article_or_si"},
  "access_caveat": "Institutional subscription session; under an open-access-only reading this case stays UNRESOLVED."
 },
 {
  "case_id": "P04", "label": "Spotti 2026 SSRN (GC-DFT RuO2)", "doi": "10.2139/ssrn.7293461",
  "prior": {"source": "results/s2_2026-09-20/priority_primary_triage/reconciled_subset.json", "disposition": "UNRESOLVED", "gap": "version status, facet, CHE eta"},
  "evidence": {"local": local_glob("ssrn7293461_*"), "remote": [
      {"item": "SSRN preprint PDF (19 pp, posted 2026-08-16)", "route": BROWSER, "sha256": "6c28e85db970070b97894d17096cea2f9da96ce6bd7f606d4dd465011bbaeb24", "bytes": 1169051}]},
  "pass1": {"criteria": crit("YES - GCP-K DFT study (preprint, not peer reviewed; no journal relation found)", "YES - posted 2026-08-16",
      "PARTIAL - potential-dependent stability of -OOH vs -OO-H intermediates",
      "YES - p7 'rutile-like structure'", "YES - RuO2(110) throughout (pp7-11)",
      "NOT_FOUND_IN_MAIN_TEXT - 'overpotential' only p3/p7 experimental context; p12 CHE mentioned only as a previous analysis; SI (cited p5 'Section S1/S3 of the Supporting Information') is not posted on SSRN"),
      "disposition": "UNRESOLVED", "missing": "Supporting Information (not on SSRN) and any journal version"},
  "pass2": {"criteria": crit("YES", "YES", "PARTIAL", "YES", "YES", "NOT_FOUND_IN_MAIN_TEXT; SI unavailable"),
            "disposition": "UNRESOLVED", "missing": "SI"},
 },
 {
  "case_id": "P05", "label": "Ricci 2026 SnSe2/TiO2 (npj 2D Mater. Appl.)", "doi": "10.1038/s41699-026-00721-1",
  "prior": {"source": "results/s2_2026-09-20/priority_primary_triage/reconciled_subset.json", "disposition": "UNRESOLVED", "gap": "TiO2 polymorph, CHE, eta"},
  "evidence": {"local": local_glob("snse2tio2_*"), "remote": []},
  "pass1": {"criteria": crit("YES - experiments plus DFT", "YES - received 2026-02-18, published 2026-07-15 (accelerated article preview)",
      "YES - article pp23-24 OER free energies on defective (100)/(110) TiO2",
      "NO - SI p7 S5.1 'Relaxed TiO2 (anatase) structure' a=3.825, c=9.686 A; article p7 GI-XRD anatase; SI p7: rutile evaluated only as a (100) surface-energy check and discarded",
      "YES (anatase (110))",
      "YES_OTHER_POLYMORPH - article p23 CHE (Norskov) with eta = 1.17 V (100) and p24 eta = 0.67 V (110), both anatase"),
      "disposition": "EXCLUDE", "failed_criterion": "rutile_oxide"},
  "pass2": {"criteria": crit("YES", "YES", "YES", "NO - SI S5.1-S5.2 p7 anatase bulk and anatase (100)/(110) terminations; Methods p30 CHE on the same models", "YES (anatase)", "YES (anatase only)"),
            "disposition": "EXCLUDE", "failed_criterion": "rutile_oxide"},
  "version_note": "Evidence file is the unedited accelerated article preview (nature.com _reference.pdf); final typeset version not inspected, polymorph statement is in the official SI."
 },
 {
  "case_id": "P06", "label": "Camacho-Forero 2022 Co/Ni-IrO2 (J. Catal.)", "doi": "10.1016/j.jcat.2022.02.016",
  "prior": {"source": "results/s2_2026-09-20/priority_primary_triage/reconciled_subset.json", "disposition": "UNRESOLVED", "gap": "facet model and CHE eta"},
  "evidence": {"local": local_glob("conirO2_*"), "remote": [{"item": "ScienceDirect article", "route": "BLOCKED - CAPTCHA; not attempted"}]},
  "pass1": {"criteria": crit("YES (SI p1 computational details; experimental + theoretical)", "YES - Crossref print 2022-04", "YES (SI Tables S1-S4 reaction/activation energies)",
      "UNKNOWN (SI does not name the polymorph; article not inspected)", "UNKNOWN (SI refers to 5-fold Ir sites only)",
      "NOT_FOUND_IN_SI - SI tables give activation barriers and reaction energies of recombination/associative steps and Tafel-slope analysis; no CHE eta; article not accessible"),
      "disposition": "UNRESOLVED", "missing": "article full text"},
  "pass2": {"criteria": crit("YES", "YES", "YES", "UNKNOWN", "UNKNOWN", "NOT_FOUND_IN_SI"),
            "disposition": "UNRESOLVED", "missing": "article full text"},
  "note": "Godinez-Salomon 2022 (P07) cites this work as its ref 114 (same groups)."
 },
 {
  "case_id": "P07", "label": "Godinez-Salomon 2022 (ACS Appl. Nano Mater.)", "doi": "10.1021/acsanm.2c02760",
  "prior": {"source": "results/s2_2026-09-20/priority_primary_triage/reconciled_subset.json", "disposition": "UNRESOLVED", "gap": "CHE reference convention (first pass SUPPORTED vs independent UNRESOLVED)"},
  "evidence": {"local": [h(f"{ACC20}/godinez2022_article.pdf"), h(f"{ACC20}/godinez2022_si_36462591.pdf")], "remote": []},
  "pass1": {"criteria": crit("YES", "YES - Crossref online 2022-07-28",
      "YES - article p15 energy profiles of OER steps; SI Fig S17",
      "YES - SI p8 RuO2 cell a=4.483, c=3.108 A (rutile); article p16 'rutile phases'", "YES - (110)-Ru1-xTixO2 slabs",
      "YES - article p15 potential effect added 'using Norskov's approach' (ref 115, Valdes et al. 2008); article p16 descriptor dE_O - dE_OH = E_O* + 1/2 E_H2(g) - E_OH* (proton-electron pair referenced to 1/2 H2) and eta_OER = {max[(dG_O*-dG_OH*), 3.2 eV-(dG_O*-dG_OH*)]/e} - 1.23 V; theoretical eta plotted Fig 8b,c, values in ESI Table S14"),
      "disposition": "ELIGIBLE_PENDING_DISCOVERY_FREEZE"},
  "pass2": {"criteria": crit("YES", "YES", "YES", "YES", "YES",
      "YES - page image of article p16 checked: the 1/2 E_H2(g) term is explicit; SI p8 gas-phase adsorption-energy definition applies to Eads tables, not to the eta descriptor"),
      "disposition": "ELIGIBLE_PENDING_DISCOVERY_FREEZE"},
  "rule_note": "Resolves the prior reviewer disagreement toward eligibility using the p16 equation that neither prior record quoted; the eta uses Man et al.'s 3.2 eV OOH-OH scaling rather than a computed OOH energy."
 },
 {
  "case_id": "P08", "label": "Divanis 2021 PCCP", "doi": "10.1039/d1cp02999a",
  "linked_version_candidate_ids": ["120cfbcb077ef9080bd24a8b", "1e3ea86259784c51b6c43de2", "52ae5796ed909e2c483243c6", "ae3d7c592d886d696d6496c0"],
  "prior": {"source": "results/s2_2026-09-20/priority_primary_triage/reconciled_subset.json", "disposition": "UNRESOLVED (+4 VERSION rows)", "gap": "rutile polymorph and CHE reference"},
  "evidence": {"local": [], "remote": [
      {"item": "RSC published HTML full text (CC BY 4.0)", "route": BROWSER, "innertext_sha256": "2a523ff17983b88c2e2e3fff8f1595f2cda85f087bd6955dd8d710f9f568710f", "chars": 25357},
      {"item": "ChemRxiv v2 PDF 10.26434/chemrxiv-2021-pfdcx-v2 (10 pp)", "route": BROWSER, "sha256": "5aec7f02bb28e5b16b577177515c1573572088fb3a117543dc78fea051835252", "bytes": 6004454}]},
  "pass1": {"criteria": crit("YES - own GPAW/BEEF-vdW calculations (Computational methods)",
      "YES - 2021 (preprint v1 posted 2021-06-29; Crossref journal year only; EPMC first publication 2021-09-15)",
      "YES - new RuO2 pathway (Fig 1b), Fig 2 volcano",
      "SUPPORTED_BY_MATERIAL_IDENTITY_ONLY - RuO2(110)/IrO2(110) cus and bridge sites (Fig 1c); the word 'rutile' appears only in cited titles",
      "YES",
      "UNRESOLVED_REFERENCE - Fig 2 left axis 'theoretical overpotential' with own blue-pentagon point; 'each step accompanied with the exchange of a proton-electron pair'; conventional pathway cited to Norskov 2004 (ref 21); no explicit hydrogen-electrode / 1/2 H2 reference statement in journal text, and no ESI declared; preprint v2 adds none"),
      "disposition": "UNRESOLVED", "missing": "explicit CHE reference statement (or a ruling that a PCET-volcano theoretical overpotential citing Norskov 2004 suffices)"},
  "pass2": {"criteria": crit("YES", "YES", "YES", "SUPPORTED_BY_MATERIAL_IDENTITY_ONLY", "YES",
      "UNRESOLVED_REFERENCE - Computational methods give functional/slab/k-points only; no free-energy reference, ZPE/TS or potential-shift statement"),
      "disposition": "UNRESOLVED", "missing": "CHE reference evidence"},
  "note": "Same criterion standard as applied to P07 (explicit 1/2 H2 or named CHE). The four ChemRxiv alias/preprint rows collapse to this case and are not additional studies."
 },
 {
  "case_id": "P09", "label": "Creazzo & Luber 2021 (Chem. Eur. J.)", "doi": "10.1002/chem.202102356",
  "prior": {"source": "results/s2_2026-09-20/priority_primary_triage/reconciled_subset.json", "disposition": "UNRESOLVED", "gap": "own CHE eta in article/SI"},
  "evidence": {"local": local_glob("chem2021_*"), "remote": []},
  "pass1": {"criteria": crit("YES - DFT-MD/metadynamics (Computational methods)", "YES - Crossref online 2021-10-15",
      "YES - OER free-energy barriers via metadynamics",
      "YES - 'the rutile RuO2 bulk' (section on the (110) model)", "YES - hydrated (110)-RuO2",
      "NO - explicitly 'free energy activation barriers ... in contrast to traditional thermodynamic free energy differences'; eq 6 defines G_OER only generically; the 0.5-0.7 eV overpotential quoted is Norskov et al.'s literature value; no hydrogen-electrode reference; PMC XML declares no supplementary material and the text cites no Supporting Information"),
      "disposition": "EXCLUDE", "failed_criterion": "che_overpotential_reported_article_or_si"},
  "pass2": {"criteria": crit("YES", "YES", "YES (kinetic)", "YES", "YES",
      "NO - 0 occurrences of 'hydrogen electrode'/'CHE'; reported quantities are activation barriers (e.g. 1.64 eV, 0.46 eV); Europe PMC supplementary bundle contains only figure images"),
      "disposition": "EXCLUDE", "failed_criterion": "che_overpotential_reported_article_or_si"},
  "residual": "Wiley landing/SI listing returned HTTP 403; SI absence rests on the PMC XML and the article text."
 },
 {
  "case_id": "P10", "label": "Zagalskaya & Alexandrov ACS Fall 2020 poster", "doi": "10.1021/scimeetings.0c06708",
  "prior": {"source": "results/s2_2026-09-20/priority_primary_triage/reconciled_subset.json", "disposition": "UNRESOLVED", "gap": "resource type/content"},
  "evidence": {"local": local_glob("scimeetings_exhibit__*"), "remote": [
      {"item": "SciMeetings exhibit page (rendered)", "route": BROWSER, "observed": "labelled 'POSTER', ACS Fall 2020; abstract only; poster download requires sign-in (not attempted)"}]},
  "pass1": {"criteria": crit("NO_AS_RECORD_TYPE - conference poster exhibit", "YES - Crossref posted 2020-10-05",
      "YES per abstract (CHE calculations on RuO2/IrO2)", "UNKNOWN", "UNKNOWN", "abstract mentions a theoretical overpotential; poster content not accessible"),
      "disposition": "EXCLUDE", "failed_criterion": "primary_research (resource type: meeting poster, consistent with the prior ECS meeting-abstract exclusions)"},
  "pass2": {"criteria": crit("NO_AS_RECORD_TYPE", "YES", "YES (abstract)", "UNKNOWN", "UNKNOWN", "UNKNOWN"),
            "disposition": "EXCLUDE", "failed_criterion": "primary_research (record type)"},
  "note": "Any corresponding journal article is a separate candidate and is not asserted here."
 },
 {
  "case_id": "P11", "label": "Adiga 2022 strain RuO2(101) (Mater. Today Energy)", "doi": "10.1016/j.mtener.2022.101087",
  "prior": {"source": "results/s2_2026-09-20/priority_primary_triage/reconciled_subset.json", "disposition": "UNRESOLVED", "gap": "SI (first pass EXCLUDE vs independent UNRESOLVED)"},
  "evidence": {"local": [h(f"{ACC20}/strain2022_article.pdf")] + local_glob("strain2022_si_mmc1_pdf__*"), "remote": []},
  "pass1": {"criteria": crit("NO_CALCULATION - experimental thin-film study", "YES - OSTI 2022-07-02; Crossref print 2022-08",
      "NO - article pp1-8: all calculations cited to literature (refs 17-20, 25, 26, Zagalskaya)", "n/a", "n/a (own work is (101) and (110) films experimentally)",
      "NO - SI pp1-8 (official Elsevier mmc1): film growth, electrochemistry, CV; no DFT"),
      "disposition": "EXCLUDE", "failed_criterion": "oer_calculated (purely experimental)"},
  "pass2": {"criteria": crit("NO_CALCULATION", "YES", "NO", "n/a", "n/a", "NO"),
            "disposition": "EXCLUDE", "failed_criterion": "oer_calculated"},
  "version_note": "Article evidence is the OSTI accepted manuscript; final typeset version not inspected."
 },
 {
  "case_id": "P12", "label": "Gonzalez-Huerta 2014 Co-doped RuO2/IrO2 (J. Power Sources)", "doi": "10.1016/j.jpowsour.2014.06.029",
  "prior": {"source": "results/s2_2026-09-20/priority_primary_triage/reconciled_subset.json", "disposition": "UNRESOLVED", "gap": "surface models, reference, CHE eta"},
  "evidence": {"local": local_glob("copo2014_*"), "remote": [{"item": "ScienceDirect article", "route": "BLOCKED - CAPTCHA; not attempted"}]},
  "pass1": {"criteria": crit("YES (experimental + DFT per title/SI)", "YES - Crossref print 2014-12", "UNKNOWN", "UNKNOWN", "UNKNOWN",
      "NOT_FOUND_IN_SI - SI (official mmc1) contains only experimental LSV (Fig S1) and SEM (Fig S2)"),
      "disposition": "UNRESOLVED", "missing": "article full text"},
  "pass2": {"criteria": crit("YES", "YES", "UNKNOWN", "UNKNOWN", "UNKNOWN", "NOT_FOUND_IN_SI"),
            "disposition": "UNRESOLVED", "missing": "article full text"},
 },
 {
  "case_id": "V01", "label": "Navodye & Gunasooriya 2024 (J. Phys. Chem. C) + ChemRxiv preprint", "doi": "10.1021/acs.jpcc.3c08103",
  "linked_version_candidate_ids": ["1183b3c2cfd620788e81af05"],
  "prior": {"source": "results/s2_2026-09-20/priority_primary_triage/reconciled_subset.json", "disposition": "VERSION_RELATION_SUPPORTED_JOURNAL_ELIGIBILITY_UNRESOLVED (preprint row)", "gap": "journal rutile model and CHE eta"},
  "evidence": {"local": [], "remote": [
      {"item": "ChemRxiv preprint PDF (32 pp)", "route": BROWSER, "sha256": "6a7bf33fea4371e9ba0e48595cbf189afae364b2bd4cc5e80d9b9212160a51cc", "bytes": 12593363},
      {"item": "ChemRxiv preprint SI (30 pp)", "route": BROWSER, "sha256": "21912707da0e61529e350765bc359d15e031622448a714641828c80ff398a009", "bytes": 19376364},
      {"item": "journal HTML full text (JPCC 128(14) 6041)", "route": INST, "innertext_sha256": "6b2244825f7420a6a06111d3f35fa44ed00aaafd1d20a83fcb5a54f837807d52", "chars": 77067},
      {"item": "journal SI jp3c08103_si_001.pdf (32 pp; watermark shows Purdue download)", "route": INST, "sha256": "2934e057df98994e0ed95dfcef234e9972cfe522a1a37ded4f20e5ebfdb99964", "bytes": 21313728},
      {"item": "journal SI jp3c08103_si_002.xlsx", "route": INST, "sha256": "fcbfe1392ddf0b919d7cdfe4d5a214645ac901d5bf74b5493164ed6250d3103f", "bytes": 18530}]},
  "pass1": {"criteria": crit("YES - DFT study", "YES - preprint 2023-12-12; journal online 2024-03-29",
      "PARTIAL - OH*, O*, OOH* adsorption free energies with/without anions (journal Table 4; SI Figs S9-S11)",
      "YES - 'rutile IrO2(110) surface' (preprint p8)", "YES",
      "NO_OWN - the only limiting potential ('OER thermodynamic limiting potential at 1.6 V vs RHE') is cited to ref 45 = Man et al. 2011; no own eta in preprint, journal text, journal SI PDF or SI spreadsheet (string scan of all sheets)"),
      "disposition": "EXCLUDE", "failed_criterion": "che_overpotential_reported_article_or_si"},
  "pass2": {"criteria": crit("YES", "YES", "PARTIAL", "YES", "YES",
      "NO_OWN - preprint pp6-7 overpotentials are experimental literature; p17 1.6 V cited (45); journal identical wording; SI p19 lists adsorption energies on Cl*/Br* only"),
      "disposition": "EXCLUDE", "failed_criterion": "che_overpotential_reported_article_or_si"},
  "access_caveat": "Journal-version evidence via institutional subscription session. Under an open-access-only reading the preprint and preprint SI alone give the same negative finding but the journal representative stays UNRESOLVED."
 },
]

PASS_NOTE = ("Both passes were performed by the same reviewer in one session; the second pass re-read the primary "
             "sources and wrote its criterion evidence before comparing, per the task instruction, but it is not an "
             "independent second reviewer in the registered sense. Treat these as a within-reviewer double pass.")

recs = []
for c in CASES:
    d1, d2 = c["pass1"]["disposition"], c["pass2"]["disposition"]
    agree = d1 == d2
    final = d1 if agree else "UNRESOLVED"
    prior_disp = c["prior"]["disposition"].split(" ")[0]
    rec = dict(c)
    rec.update({
        "agreement": agree,
        "final_disposition": final,
        "proposed_change": None if final.startswith("UNRESOLVED") and prior_disp.startswith("UNRESOLVED")
        else {"status": "PROPOSED_CHANGE", "from": c["prior"]["disposition"], "to": final,
              "prior_record_left_untouched": c["prior"]["source"]},
        "method_reporting_fields": "NOT_CODED",
        "pass_independence_note": PASS_NOTE,
    })
    recs.append(rec)

(ROOT / "eligibility_records.json").write_text(json.dumps({
    "schema": "sts.p_lit.eligibility_identity_review.eligibility.v1", "built_utc": NOW,
    "population_rule": "primary research first published 2011-01-01..2026-09-18, calculating OER on a rutile-oxide (110) surface and reporting a CHE overpotential in article or SI",
    "global_freeze": False, "p_lit_verdict": None, "records": recs}, indent=1, ensure_ascii=False), encoding="utf-8")

# ---------------- identity records ----------------
att = {r["source_identity"]: r for r in json.loads((ROOT / "identity_crossref_attempts.json").read_text(encoding="utf-8"))}
ids = []
for line in (REPO / "results/s2_2026-09-20/complementary_identity_review/unresolved_identities.jsonl").read_text(encoding="utf-8").splitlines():
    u = json.loads(line)
    a = att[u["source_identity"]]
    lab = u["source_labels"][0]
    rec = {"source_identity": u["source_identity"], "source_labels": u["source_labels"],
           "source_occurrence_ids": u["source_occurrence_ids"], "occurrence_count": u["source_occurrence_count"],
           "prior_status": u["identity_status"], "prior_candidates": u["candidate_identities"],
           "crossref_works": [{k: w.get(k) for k in ("doi", "metadata")} | {"raw_sha256": w["receipt"].get("sha256"), "raw_path": w["receipt"].get("local_path")} for w in a["works_lookups"]],
           "crossref_bibliographic_query": ({"query": a["bibliographic_query"].get("query"),
                                              "raw_sha256": a["bibliographic_query"].get("receipt", {}).get("sha256"),
                                              "raw_path": a["bibliographic_query"].get("receipt", {}).get("local_path"),
                                              "top_candidates": a["bibliographic_query"].get("top", [])[:5]}
                                             if a["bibliographic_query"].get("query") else a["bibliographic_query"]),
           "status": "UNRESOLVED", "canonical_identity": None,
           "reason": "Source occurrences give no title, year or venue, so the required title + first-author + year + venue agreement cannot be established; candidates are recorded, none selected."}
    if lab == "Dickens":
        rec.update({
            "status": "RESOLVED_ALL_OCCURRENCES",
            "canonical_identity": "doi:10.1021/acs.jpcc.7b03481",
            "reason": ("Crossref /works: 'A Theoretical Investigation into the Role of Surface Defects for Oxygen Evolution on RuO2', "
                       "first author Dickens, J. Phys. Chem. C, online 2017-08-17. Primary full text (OSTI manuscript "
                       "docs/research/papers/2026-09-20-access/dickens2017_article.pdf) contains both cited contents: the "
                       "~0.7 eV defect-site descriptor range (PDF p2 abstract) cited at round1 L213 and round2 L522, and the "
                       "Briquet critique (PDF pp8-9: Briquet et al. suggested >1 eV chemisorption and >0.6 eV descriptor "
                       "spread; Dickens disputes it) cited at round2 L519. The occurrences state neither year nor venue, so "
                       "this rests on content match plus exact-DOI metadata, not on query.bibliographic agreement."),
            "content_evidence": h(f"{ACC20}/dickens2017_article.pdf"),
            "proposed_change": {"status": "PROPOSED_CHANGE", "from": "PARTIALLY_RESOLVED", "to": "RESOLVED_ALL_OCCURRENCES",
                                "prior_record_left_untouched": "results/s2_2026-09-20/complementary_identity_review/unresolved_identities.jsonl"}})
    if lab == "Nabat":
        rec["reason"] += (" Crossref confirms the candidate DOI is 'Learning broken symmetries with approximate invariance' "
                          "(Nabat, Phys. Rev. D, 2025); the occurrence ('Nabat and Paz both carried publications') names no work.")
    ids.append(rec)

(ROOT / "identity_records.json").write_text(json.dumps({
    "schema": "sts.p_lit.eligibility_identity_review.identity.v1", "built_utc": NOW, "records": ids}, indent=1, ensure_ascii=False), encoding="utf-8")

from collections import Counter
summ = {
    "built_utc": NOW,
    "eligibility_cases": len(recs),
    "final_disposition_counts": dict(Counter(r["final_disposition"] for r in recs)),
    "pass_agreement": sum(r["agreement"] for r in recs),
    "proposed_changes": [{"case_id": r["case_id"], "doi": r["doi"], "from": r["proposed_change"]["from"], "to": r["proposed_change"]["to"]}
                         for r in recs if r["proposed_change"]],
    "cases_relying_on_institutional_session": [r["case_id"] for r in recs if "access_caveat" in r],
    "identity_keys": len(ids),
    "identity_occurrences": sum(r["occurrence_count"] for r in ids),
    "identity_status_counts": dict(Counter(r["status"] for r in ids)),
    "identity_occurrences_resolved": sum(r["occurrence_count"] for r in ids if r["status"].startswith("RESOLVED")),
    "method_reporting_fields": "NOT_CODED", "p_lit_verdict": None, "global_freeze": False,
}
(ROOT / "summary.json").write_text(json.dumps(summ, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(summ, indent=1))
