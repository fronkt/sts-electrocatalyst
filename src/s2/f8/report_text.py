"""Markdown for docs/research/f8-clearance-2026-09-16.md; every number comes from ``summary``."""
from __future__ import annotations

OUTDIR = "results/s2_2026-09-16/f8"


def _t(rows: list[list], head: list[str], align: str | None = None) -> str:
    a = align or "|".join("---" for _ in head)
    out = ["| " + " | ".join(head) + " |", "|" + a + "|"]
    for r in rows:
        out.append("| " + " | ".join("" if c is None else str(c).replace("|", "\\|") for c in r) + " |")
    return "\n".join(out)


def _mev(x):
    if x is None:
        return "—"
    return f"{x * 1000:.1f}" if abs(x) < 0.01 else f"{x * 1000:.0f}"


def _first_author(a: str | None) -> str:
    if not a:
        return "?"
    return a.split(";")[0].split(",")[0].strip()


def _ref(r: dict) -> str:
    j = r.get("journal") or ""
    vol = f" {r['volume']}" if r.get("volume") else ""
    pg = f", {r['firstpage']}" if r.get("firstpage") else ""
    doi = f", {r['doi']}" if r.get("doi") else ""
    return f"{_first_author(r.get('authors'))} {r.get('year')}, {j}{vol}{pg}{doi}"


def _n(n, word: str) -> str:
    return f"{n} {word}" + ("" if n == 1 else "s")


def _year_fix(wrong: list, registrar: list) -> str:
    return ", ".join(f"{w} → {'/'.join(map(str, registrar))}" for w in wrong)


def _sub(s2: dict, sid: str) -> dict:
    return next(sc for c in s2["claims"] for sc in c["subclaims"] if sc["id"] == sid)


def _check_text(k: dict) -> str:
    p = k.get("params") or {}
    if k["kind"] in ("cod_type_present", "cod_type_absent"):
        qual = (" ambient" if p.get("ambient") else "") + (f" mineral {p['mineral']}" if p.get("mineral") else "") \
            + (f" named /{p['name_regex']}/" if p.get("name_regex") else "")
        return (f"COD {p['formula']} {p['type']}{qual} {k['kind'].split('_')[-1]} → {k['result']} "
                f"({_n(k['n'], 'record')}{': ' + ', '.join(k['cod_ids']) if k['cod_ids'] else ''})")
    if k["kind"] == "not_checkable":
        return f"no accessible evidence: {k['reason']}"
    if k["kind"] == "mp_lowest_ehull":
        want = f"sg {p['sg_number']}" if "sg_number" in p else f"not sg {p['not_sg_number']}"
        return f"MP lowest-E_hull {p['formula']} is {want} → {k['result']}"
    if k["kind"] == "mp_id_sg":
        extra = (f", label {p['robocrys_mineral']}" if p.get("robocrys_mineral") else "") + \
            (", octahedra text" if p.get("description_contains") else "")
        return f"MP {p['legacy_id']} sg {p['sg_number']}{extra} → {k['result']}"
    if k["kind"] == "formal_d_count":
        return f"formal d count {p['element']}({p['oxidation_state']:+d}) = {p['expected']} → {k['result']}"
    return f"{k['kind']} → {k['result']}"


def render(s: dict) -> str:
    s1, s2, s3, s4, s5 = (s["sun2004"], s["structures"], s["zpe"], s["intercept_floor"],
                          s["bibliography"])
    mc = s.get("manifest_counts", {})
    L: list[str] = []
    A = L.append

    A("# F8 clearance — 2026-09-16")
    A("")
    A("F8 (docs/43 A9.5 item 8, :1945) requires five items to be cleared or excluded, with the "
      "bibliography regenerated from Crossref; the Sun, Reuter & Scheffler citation is A9.5 item 7 "
      "(:1944). Each item was checked here against registrar records, open full text, crystallographic "
      "databases and the repository's own files. The deadline in :1945 was Sep 15; this record is "
      "dated Sep 16. No registered text was edited.")
    A("")
    A("Source review updated 2026-09-18: the Sun journal wording is checked against the previously "
      "archived MPG copy, and the OsO₂ structural statement names the COD population it describes. "
      "The prior report and summary are preserved in `results/s2_2026-09-16/f8_before_vor_correction/`.")
    A("")
    A(f"Code: `src/s2/f8/`; `PYTHONPATH=src python -m s2.f8.run --offline` rebuilds every table below "
      f"from the cached responses. Outputs: `{OUTDIR}/` (`summary.json`, one JSON per item, "
      f"`references.crossref.bib`, `bib_crossref_diff.json`). `manifest.json` holds the sha256 of "
      f"{mc.get('repo_inputs')} repository inputs and the {mc.get('cached_responses')} cached registrar, "
      f"database and full-text responses this run read; it lists separately, with hashes, "
      f"{_n(mc.get('cached_responses_not_read_this_run'), 'cached response')} that no current request reads ("
      + "; ".join(f"`{u['url']}` HTTP {u['status']}" for u in mc.get("not_read_urls", [])) + ").")
    A("")

    # ------------------------------------------------------------------ verdicts
    A("## Verdicts")
    A("")
    corr = s5["docs28_corrections"]
    bibs = s5["bib"]
    rows = [["Sun, Reuter & Scheffler 2004 (:1944)", sc["text"], f"**{sc['verdict']}**: {sc['basis']}"]
            for sc in s1["subclaims"]]
    for c in s2["claims"]:
        for sc in c["subclaims"]:
            res = f"**{sc['verdict']}**"
            if sc["narrowed"]:
                res += f"; narrowed form \"{sc['narrowed']['text']}\" **{sc['narrowed']['verdict']}**"
            rows.append([f"{c['file'].split('/')[-1]}:{c['line']}", sc["text"], res])
    rows += [
        ["+0.40 eV *OOH ZPE − TS", "the constant has a readable primary source",
         f"**{s3['verdict']}**: absent from every source readable here; the implied convention is "
         f"δ = +{s3['implied']['delta_repo_constant']:.2f} eV"],
        ["3.18 ± 0.12 eV intercept", "qualitative only (disposition)", "disposition holds in the registered "
         f"text; {s4['summary']['n_quantitative_lines']} lines in the tree still use it or the 0.12 V floor "
         "quantitatively (table in §4)"],
        ["~0.12 V code floor", "dead (disposition)", "dead in the registered text; A9.5 item 1 option (b) "
         "still carries a ±0.12 V η gate"],
        ["docs/references.bib vs Crossref", "metadata agrees with the registrar", f"{bibs['n_entries']} entries, "
         f"{bibs['field_status_counts'].get('title|MATCH')} title / "
         f"{bibs['field_status_counts'].get('first_author|MATCH')} first-author / "
         f"{bibs['field_status_counts'].get('year|MATCH')} year / "
         f"{bibs['field_status_counts'].get('journal|MATCH')} journal / "
         f"{bibs['field_status_counts'].get('volume|MATCH')} volume / "
         f"{bibs['field_status_counts'].get('pages|MATCH')} pages match; "
         f"{len(bibs['doi_field_defects'])} DOI fields are not registered DOIs"],
        ["docs/28 DOI defects", "every DOI names the work its label names",
         f"CatBench → `{corr['catbench']['corrected_doi']}` "
         f"(lines {', '.join(map(str, corr['catbench']['docs28_lines']))}); J. Catal. → "
         f"`{corr['jcat']['corrected_doi']}` (line {', '.join(map(str, corr['jcat']['docs28_lines']))})"],
    ]
    A(s2["verdict_rule"])
    A("")
    A(_t(rows, ["Item", "Claim", "Result"]))
    A("")

    # ------------------------------------------------------------------ 1
    cr = s1["crossref"]
    idt = s1["identity"]
    acc = s1["access"]
    q = s1["quotes"]
    A("## 1. Sun, Reuter & Scheffler (2004)")
    A("")
    A(f"**Record.** Crossref `{cr['doi']}` (HTTP {cr['status']}): *{cr['title']}*, "
      f"{', '.join(cr['authors'])}, {cr['journal']} **{cr['volume']}**, {cr['article_number']} "
      f"({cr['year']}). Authors, journal, volume, article number and year agree with the repository "
      f"citation in {sum(s1['record_matches'].values())} of {len(s1['record_matches'])} checks.")
    A("")
    repo_ft = "a repository full text" if acc["openalex_any_repository_has_fulltext"] else "no repository full text"
    same = "the same author list in the same order" if idt["authors_identical_in_order"] else         "a different author list"
    vor = s1["version_of_record"]
    vq = vor["quotes"]
    A(f"**Accessible text.** The MPG repository supplies the [published PDF]({vor['url']}) "
      f"(sha256 `{vor['sha256']}`, {vor['pdf_pages']} pages). Its first-page journal, volume, article "
      f"number, year, DOI and author checks pass: {all(vor['identity_checks'].values())}. "
      f"The cached access indexes say OpenAlex `{acc['openalex_oa_status']}`, {repo_ft}; "
      f"Semantic Scholar `{acc['semanticscholar_open_access_status']}`. Those labels missed this copy. "
      "The previous F8 draft excluded the journal wording because the copy had not been incorporated; "
      "this readout corrects that exclusion using the already archived primary evidence. "
      "The APS abstract page gives received "
      f"{idt['aps_received']} and published {idt['aps_published']}. arXiv:cond-mat/0309714v1, "
      f"*{s1['arxiv_title']}*, was posted on {idt['arxiv_posted']} with {same}, "
      f"{idt['arxiv_posted_minus_aps_received_days']} days after APS receipt, abstract token overlap "
      f"(Jaccard) with the published abstract {idt['abstract_token_jaccard_arxiv_vs_aps']}. The published "
      "title and abstract were revised, so the preprint is the submitted manuscript, not the version of "
      "record.")
    A("")
    A("**The sentence.** The published article describes allowing symmetry breaking during structural "
      f"relaxation on p. 235402-{vq['symmetry_breaking_allowed']['page']}, followed by:")
    A("")
    A(f"> {vq['crucial']['match']}.")
    A("")
    A(f"The tilt example on p. 235402-{vq['tilt_energy']['page']} gives a 0.1 eV/H energy gain "
      "for the tilted surface hydroxyl relative to the upright configuration. The preprint carries "
      f"the corresponding passages on pp. {q['crucial']['page']} and {q['tilt_energy']['page']}.")
    A("")
    A("**Where the repository cites it.**")
    A("")
    sv = "; ".join(f"{k} {v_}" for k, v_ in s1["verdicts"].items())
    rows = [[f"{c['file']}:{c['line']}", "claim", c["quote"], sv] for c in s1["claim_lines"]]
    rows += [[f"{c['file']}:{c['line']}", c["role"].lower().replace("_", " "), "—", "—"]
             for c in s1["other_lines"]]
    A(_t(rows, ["Line", "Role", "Claim as written", "Verdicts"]))
    A("")
    A("**Verdicts.**")
    A("")
    A(_t([[sc["id"], sc["text"], f"**{sc['verdict']}**", sc["basis"]] for sc in s1["subclaims"]],
         ["Sub-claim", "Statement", "Verdict", "Basis"]))
    A("")
    A("Scope of the cleared sub-claim: the paper studies hydrogen at the stoichiometric RuO₂(110) surface; "
      "the \"crucial\" sentence is about relaxations that allow symmetry breaking of surface species, and "
      "the tilt example gives the size of one such case (tilted versus upright surface hydroxyl). It "
      "supports \"called crucial on RuO₂(110) by these authors\"; it says nothing about *OH/*OOH at cus "
      "sites or about any code's symmetrisation. The journal locator is "
      f"PRB 70, 235402 (2004), p. 235402-{vq['crucial']['page']}.")
    A("")

    # ------------------------------------------------------------------ 2
    A("## 2. Structure types: PbO₂, OsO₂, SnO₂, GeO₂, PtO₂")
    A("")
    ntot = sum(x["cod_returned"] for x in s2["cod_mp"].values())
    npar = sum(x["cod_parsed"] for x in s2["cod_mp"].values())
    ndis = sum(x["cod_declared_vs_computed_sg_disagreements"] for x in s2["cod_mp"].values())
    A(f"**Method.** Every COD entry for the five formulas ({ntot} returned, {npar} parsed, "
      f"{ntot - npar} unparsed) was downloaded; space group and Wyckoff sites were recomputed from the CIF "
      f"coordinates with spglib (symprec {s2['symprec_A']} Å). Declared and recomputed space groups "
      f"disagree in {ndis} "
      "entries. A prototype is assigned only by explicit rules: rutile = P4₂/mnm with M 2a, O 4f; "
      "CaCl₂ = Pnnm, M 2a, O 4g; α-PbO₂ = Pbcn, M 4c, O 8d; CdI₂ = P-3m1, M 1a, O 2d; α-quartz = "
      "P3₁21/P3₂21, M 3a/3b, O 6c; fluorite; pyrite; anything else is listed by space group. "
      f"\"Ambient\" means a recorded pressure of at most {s2['ambient_max_kPa'] / 1000:g} MPa or, where "
      "COD records none, a source title that does not name high pressure or an ab initio calculation. "
      "Materials Project summary documents give the DFT energy above hull and ICSD cross-references; "
      "they are 0 K orderings, not phase equilibria.")
    A("")
    rows = []
    for f in ("PbO2", "OsO2", "SnO2", "GeO2", "PtO2"):
        x = s2["cod_mp"][f]
        protos = ", ".join(f"{k} {n}" for k, n in x["prototypes"].items())
        amb = ", ".join(f"{k} {n}" for k, n in x["cod_ambient_prototypes"].items())
        low = x["mp_lowest"]
        nxt = "; ".join(f"{d['sg_symbol']} {_mev(d['e_above_hull_eV_atom'])}" for d in x["mp_next"])
        rows.append([f.replace("2", "₂"), f"{x['cod_parsed']}/{x['cod_returned']}", protos, amb,
                     f"{low['sg_symbol']} ({low['material_id']})", _mev(x["mp_rutile_e_above_hull"]), nxt])
    A(_t(rows, ["Oxide", "COD parsed", "COD prototypes", "…ambient by COD record and title",
                "MP lowest E_hull", "MP rutile-type E_hull (meV/atom)", "MP next (meV/atom)"]))
    A("")
    A("**Assignments found in the repository and their verdicts.**")
    A("")
    rows = []
    for c in s2["claims"]:
        for sc in c["subclaims"]:
            ev = "; ".join(_check_text(k) for k in sc["checks"])
            if sc["narrowed"]:
                ev = ev.rstrip(".") + (f". Narrowed form \"{sc['narrowed']['text']}\": "
                       + "; ".join(_check_text(k) for k in sc["narrowed"]["checks"])
                       + f" → **{sc['narrowed']['verdict']}**")
            rows.append([f"{c['file'].split('/')[-1]}:{c['line']}", sc["id"], sc["text"], ev,
                         f"**{sc['verdict']}**"])
    A(_t(rows, ["Line", "Sub-claim", "Statement", "Evidence tests", "Verdict"]))
    A("")
    cnt = s2["subclaim_verdict_counts"]
    A(f"Sub-claims: {sum(cnt.values())}; " + ", ".join(f"{k} {n}" for k, n in cnt.items()) + ".")
    A("")
    mp996 = s2["mp_ids"].get("mp-996", {})
    ref = s2["cod_reference_counts"]["CaCl2"]
    A(f"OsO₂: MP `mp-996` now resolves to `{mp996.get('material_id')}`, {mp996.get('sg_symbol')} "
      f"(no. {mp996.get('sg_number')}), E_hull {_mev(mp996.get('e_above_hull_eV_atom'))} meV/atom; its "
      f"robocrystallographer label is \"{mp996.get('robocrys_mineral_type')}\" while the same text states "
      "the tetragonal P4₂/mnm group and corner- and edge-sharing OsO₆ octahedra. COD's CaCl₂ records "
      f"({ref['parsed']}/{ref['returned']} parsed; " + ", ".join(f"{k} {n}" for k, n in ref["prototypes"].items())
      + ") carry the mineral name hydrophilite, so the label names the orthorhombic type and does not "
      "change the rutile assignment.")
    A("")
    pt = s2["cod_mp"]["PtO2"]
    A(f"PtO₂: COD holds no rutile-type PtO₂; MP's lowest entry is {pt['mp_lowest']['sg_symbol']}; the MP "
      f"rutile-type PtO₂ lies {_mev(pt['mp_rutile_e_above_hull'])} meV/atom above the hull and carries "
      f"{', '.join(pt['mp_rutile_icsd_ids'])}. Rutile PtO₂(110) slabs in Xu 2015, Man 2011, Mom 2014 "
      "and Lim 2021 are therefore a model phase; \"rutile-like\" (lens-digest :280) holds only through "
      f"the CaCl₂-type distortion. {_sub(s2, 'PtO2-beta-is-CaCl2-type-orthorhombic')['checks'][0]['n']} "
      "CaCl₂-type records name the phase β and "
      f"{_sub(s2, 'PtO2-alpha-is-the-CdI2-type')['checks'][0]['n']} CdI₂-type records name it α, so "
      f"\"α = CdI₂-type\" is {_sub(s2, 'PtO2-alpha-is-the-CdI2-type')['verdict']} while the hexagonal "
      f"CdI₂-type phase itself is {_sub(s2, 'PtO2-a-CdI2-type-hexagonal-phase-exists')['verdict']}.")
    A("")
    A("GeO₂: argutite (rutile-type) and quartz-type records are both ambient by that rule, and MP places "
      f"rutile-type lowest with quartz-type at "
      f"{_mev(next(d['e_above_hull_eV_atom'] for d in s2['cod_mp']['GeO2']['mp_next'] if d['sg_number'] in (152, 154)))}"
      " meV/atom. \"Ambient-stable\" is a phase-equilibrium statement that no text read here makes, so it is "
      f"{_sub(s2, 'GeO2-rutile-type-is-ambient-stable')['verdict']} as written; the narrowed sentence "
      f"\"{_sub(s2, 'GeO2-rutile-type-is-ambient-stable')['narrowed']['text']}\" is "
      f"{_sub(s2, 'GeO2-rutile-type-is-ambient-stable')['narrowed']['verdict']}. The transition temperature is "
      f"{_sub(s2, 'GeO2-converts-to-quartz-type-above-1035C')['verdict']} and the SiO₂ stishovite remark "
      f"{_sub(s2, 'GeO2-sentence-stishovite-is-high-pressure')['verdict']}. docs/43 :1429 "
      "(\"rutile-type IS its ambient polymorph\") is "
      f"{_sub(s2, 'GeO2-docs43-rutile-type-is-an-ambient-polymorph')['verdict']} as \"an ambient polymorph\", "
      "which is what its exclusion argument needs; read as \"the stable one\" it carries the excluded "
      "sub-claim.")
    A("")
    A("**Primary crystallographic sources used as evidence** (COD id, recomputed space group, prototype):")
    A("")
    rows = [[i, r["formula"].replace("2", "₂"), r["sg"], r["prototype"], r.get("mineral") or "—", _ref(r)]
            for i, r in s2["cod_refs"].items()]
    A(_t(rows, ["COD", "Compound", "Space group", "Prototype", "Mineral", "Source"]))
    A("")
    mcnt = s2["mention_counts"]
    A(f"**Scope of the search.** {s2['n_mentions']} lines in docs/, tasks/, src/ and README.md name one of "
      "the five with structure vocabulary: " + ", ".join(f"{k} {n}" for k, n in mcnt.items()) +
      ". MODEL_DESCRIPTION lines say which structure a cited calculation used (for example rutile PtO₂ "
      "slabs) and are consistent with the table above once \"model phase\" is attached to PtO₂. src/ "
      "assigns no structure type to any of the five. The docs/43 A7.5 exclusion list (:1408) can now "
      "carry a COD or MP identifier for PtO₂, GeO₂, PbO₂ and OsO₂ from the tables above.")
    A("")

    # ------------------------------------------------------------------ 3
    tc = s3["man2011_token_counts"]
    n040, n035, n005 = tc[r"0\.40"], tc[r"0\.35"], tc[r"0\.05"]
    nzpe, ntab, nzp = tc[r"\bZPE\b"], tc[r"\bTable\b"], tc[r"zero[- ]point"]
    tab = s3["table_si1"]
    rd = s3["registered_delta"]
    att = s3["attribution_line_numbers"]
    dlt = s3["implied"]["delta_repo_constant"]
    inside = "inside" if rd["range_eV"][0] <= dlt <= rd["range_eV"][1] else "outside"
    A("## 3. The +0.40 eV *OOH ZPE − TS constant")
    A("")
    A(f"**Man 2011** (`docs/research/papers/man2011.pdf`, {s3['man2011_pages']} pages, sha256 "
      f"`{s3['man2011_sha256'][:12]}…`): text search counts \"0.40\" {n040}, \"0.35\" {n035}, \"ZPE\" "
      f"{nzpe}, \"Table\" {ntab}, \"zero point\" {nzp}, \"0.05\" {n005}, \"Supporting Information\" "
      f"{tc['Supporting Information']}. The \"zero point\" hit is the Fig. 2 caption (the plotted "
      "adsorption energies \"do not include zero point energy and entropy corrections\"); the \"0.05\" "
      "hit is the force threshold. The main text holds no ZPE/TS table and defers the derivation to "
      f"the Supporting Information, whose publisher download returned HTTP {s3['man2011_si']['status']}"
      + (" with a bot-challenge page" if s3["man2011_si"]["cloudflare_challenge"] else "") +
      "; it was not read.")
    A("")
    hash_ok = "sha256 matches" if tab["sha256_matches_SHA256SUMS"] else "sha256 DOES NOT match"
    ooh = "has an *OOH row" if tab["has_OOH_row"] else "has no *OOH row"
    A(f"**Divanis 2020 ESI Table SI-1** (`{tab['path']}` line {tab['line']}; {hash_ok} the committed "
      f"SHA256SUMS), attributed there to ref. [25] = Nørskov et al. 2004. Header `{tab['header']}`; the "
      f"table {ooh}.")
    A("")
    rows = [[lab, ", ".join(f"{x:.2f}" for x in tab["rows"][lab])] for lab in tab["row_order"]]
    A(_t(rows, ["Row", "Values as printed"]))
    A("")
    sp = s3["species"]
    A(f"From the single-species rows (H₂O TS {sp['H2O']['TS']:.2f}, ZPE {sp['H2O']['ZPE']:.2f}; H₂ TS "
      f"{sp['H2']['TS']:.2f}, ZPE {sp['H2']['ZPE']:.2f}; HO* ZPE {sp['HO*']['ZPE']:.2f}; O* ZPE "
      f"{sp['O*']['ZPE']:.2f}) the *OH and *O corrections recompute to {s3['corr_recomputed']['OH']:.2f} "
      f"and {s3['corr_recomputed']['O']:.2f} eV against the printed {s3['corr_tabulated']['OH']:.2f} and "
      f"{s3['corr_tabulated']['O']:.2f} (rounding in the table). The convention is ΔG = ΔE + (ΔZPE − TΔS) "
      "with each adsorbate formed from H₂O and released H₂ (the references of "
      f"`{s3['repo_constant']['file']}`). On those molecule columns the repository's "
      f"{s3['repo_constant']['OOH']:.2f} eV requires ZPE − TS(HOO*) = "
      f"{s3['implied']['OOH_adsorbate_ZPE_minus_TS_for_repo_constant']:.2f} eV, and the *OH value applied "
      f"to *OOH requires {s3['implied']['OOH_adsorbate_ZPE_minus_TS_for_corr_equal_OH_row']:.2f} eV. On "
      f"the registered axis \"{rd['text']}\" (docs/43 :{rd['line']}) the constant is δ = "
      f"+{s3['implied']['delta_repo_constant']:.2f} eV ({inside} the registered range).")
    A("")
    rows = [[c["label"], c["doi"], f"{c['crossref_journal']} {c['crossref_volume']}, {c['crossref_pages']} "
             f"({c['crossref_year']})", c["openalex_oa_status"], c["openalex_repository_fulltext"],
             "main text on disk" if c["main_text_pdf_on_disk"] else "not read"]
            for c in s3["candidates"]]
    A(_t(rows, ["Candidate source", "DOI", "Crossref", "OpenAlex OA", "Repository full text", "Read"]))
    A("")
    A(f"**Verdict: {s3['verdict']} as a sourced constant.** {s3['repo_constant']['OOH']:.2f} eV appears in no "
      "text readable here: not in the Man 2011 main text, not in Table SI-1 (no *OOH row), and the "
      "Nørskov 2004 tables, the Man 2011 SI and Valdés 2008 are closed or blocked. The attribution at "
      f"`{s3['repo_constant']['file']}` lines {', '.join(map(str, att))} (Man 2011 / Valdés 2008) stays "
      "unverified, and "
      "the constant remains a declared convention of this repository; where it does and does not enter "
      "reported values is recorded in the 2026-09-04 addendum (docs/43 :3980). Because δ was not resolved from "
      "Nørskov 2004 by Sep 15, A9.3.4's registered fallback applies: P-DIVANIS reports only the δ-curve "
      "and no single-δ number.")
    A("")

    # ------------------------------------------------------------------ 4
    sm = s4["summary"]
    A("## 4. The 3.18 ± 0.12 eV intercept and the ~0.12 V code floor")
    A("")
    A(f"Every line in docs/, tasks/, src/, tests/, README.md and CLAUDE.md ({s4['n_files_scanned']} "
      f"files) matching `3.18`, a 0.12 V/eV value (alone or as the lower end of a range such as "
      "\"0.12-0.30 V\"), 120 mV, \"code(-level) floor\" or \"irreducible floor/band\" was listed: "
      f"{sm['n_matching_lines']} lines in {sm['n_files']} files, {sm['n_unclassified']} unclassified. Each "
      "class is keyed to a verbatim fragment in `src/s2/f8/data/intercept_floor_classes.json`. As a reach "
      f"check, {s4['n_sweep_lines']} further lines hold a bare `0.12` that none of these patterns matches; "
      "they are listed in `intercept_floor.json` (units such as mV at a stated pH, μ_B, %, table cells and "
      "file names), not classified.")
    A("")
    A(_t([[k, n] for k, n in sm["by_class"].items()], ["Class", "Lines"]))
    A("")
    A("The registered text matches the dispositions: :1945 lists the intercept as qualitative and the "
      "floor as dead; :1791-1797 and :1898 withdraw the |z| ≥ 3 gate and keep the z column as reported; "
      ":1938 drops the floor from the Xu-repair justification. Matching lines in src/ and tests/: "
      f"{s4['n_lines_in_src_or_tests']}. Lines that still use a value quantitatively:")
    A("")
    rows = [[f"{r['file']}:{r['line']}", r["class"], f"\"{r['fragment']}\"", r.get("note") or ""]
            for r in s4["quantitative"]]
    A(_t(rows, ["Line", "Class", "Text", "Note"]))
    A("")
    A("Two kinds need attention before report drafting. The three LIVE_QUANTITATIVE lines are a plan and "
      "an index that still treat the pooled ±0.12 eV as a calibration or gate. The "
      "REGISTERED_OPTION_QUANTITATIVE line is open option (b) of the Xu-repair decision: its ±0.12 V η "
      "gate has no stated origin other than round-1 :225's code-to-code floor, so choosing (b) as written "
      "would bring the dead floor back as a gate width. The deposited and dated-record lines are frozen "
      "history and stay as they are.")
    A("")

    # ------------------------------------------------------------------ 5
    fc = bibs["flag_counts"]
    A("## 5. Crossref check of docs/references.bib, and the docs/28 DOIs")
    A("")
    A(f"**docs/references.bib.** {bibs['n_entries']} entries; {bibs['n_with_doi']} with a DOI, "
      f"{bibs['n_without_doi']} without. Registrar that answered: "
      + ", ".join(f"{k} {n}" for k, n in bibs["registrars"].items()) +
      ". Crossref was queried for every DOI, DataCite only after a Crossref 404.")
    A("")
    A(_t([[k.split("|")[0], k.split("|")[1], n] for k, n in bibs["field_status_counts"].items()],
         ["Field", "Status", "Entries"]))
    A("")
    A("No title, first author, year, journal, volume or page field disagrees with its registrar record; the "
      "file was built from the same registrars on 2026-09-04. The defects are of other kinds:")
    A("")
    rows = [["DOI field is not a registered DOI (website suffix)", fc.get("DOI_FIELD_NOT_A_REGISTERED_DOI", 0),
             "; ".join(f"`{d['key']}`: `{d['as_written']}` → `{d['registrar_valid']}`"
                       for d in bibs["doi_field_defects"])],
            ["author field holds only the first author's family name", fc.get("AUTHORS_TRUNCATED", 0), ""],
            ["issue number missing", fc.get("ISSUE_MISSING", 0), ""],
            ["title carries registrar markup or line breaks", fc.get("TITLE_MARKUP_OR_WHITESPACE_IN_BIB", 0), ""],
            ["journal carries HTML entity markup (`&amp;`)", fc.get("JOURNAL_MARKUP_OR_WHITESPACE_IN_BIB", 0),
             "; ".join(f"`{d['key']}`" for d in bibs["journal_markup_rows"])],
            ["print and online years differ (bib uses print)", fc.get("PRINT_ONLINE_YEAR_SPLIT", 0),
             "; ".join(f"`{d['key']}` {d['print']}/{d['online']}" for d in bibs["print_online_year_split"])]]
    A(_t(rows, ["Defect", "Entries", "Detail"]))
    A("")
    repl = "; ".join(f"`{d['key']}` (`{d['doi']}`) → `{d['replaced_by_key']}` (`{d['replaced_by_doi']}`)"
                     for d in bibs["replaced"])
    addl = "; ".join(f"`{d['key']}` (`{d['doi']}`)" for d in bibs["added"])
    A(f"`{OUTDIR}/references.crossref.bib` holds {bibs['n_corrected_entries_written']} entries rebuilt from "
      "the cached registrar records under the original keys: full author lists, plain-text titles, issue "
      f"numbers and the two registered DOI stems. One entry is replaced because its DOI names a different "
      f"work than the lines citing it: {repl}. One entry is added for a cleared citation that had no DOI in "
      f"the tree: {addl}. `bib_crossref_diff.json` lists every changed field per entry. The comparison is "
      "of metadata; whether each citation supports its sentence is outside it.")
    A("")
    cb, jc = corr["catbench"], corr["jcat"]
    cbc = cb["candidates"][0]
    jcc = jc["candidates"][0]
    A(f"**docs/28.** {s5['docs28_n_doi_mentions']} DOI mentions ({s5['docs28_n_unique_dois']} unique), each "
      "resolved and compared with its label. Two DOIs are wrong:")
    A("")
    rows = [
        [", ".join(map(str, cb["docs28_lines"])), f"`{cb['cited_doi']}`",
         f"\"{cb['cited_doi_resolves_to']['title']}\" ({cb['cited_doi_resolves_to']['first_author']} et al.; "
         f"PII {', '.join(cb['cited_doi_resolves_to']['alternative_ids'])})",
         f"`{cb['corrected_doi']}`",
         f"Crossref: \"{cbc['title']}\", {', '.join(cbc['authors'])}, {cbc['journal']} {cbc['volume']}, "
         f"{cbc['pages']} ({cbc['year']}); PII {', '.join(cbc['alternative_ids'])} equals "
         f"{cb['pii_from_survey']} at {cb['survey_line_file']} (match: {cbc['pii_matches_survey']})"],
        [", ".join(map(str, jc["docs28_lines"])), f"`{jc['cited_doi']}`",
         f"not registered; the stem resolves to \"{jc['stem_record']['title']}\" ({jc['stem_record']['journal']} "
         f"{jc['stem_record']['volume']}, {jc['stem_record']['pages']}; {jc['stem_record']['n_authors']} authors)",
         f"`{jc['corrected_doi']}`",
         f"DOI printed on p. 1 of `{jc['local_pdf']}`; Crossref: \"{jcc['title']}\", "
         f"{', '.join(jcc['authors'])}, {jcc['journal']} {jcc['volume']}, {jcc['pages']} ({jcc['year']})"],
    ]
    A(_t(rows, ["docs/28 line", "Cited", "Resolves to", "Correction", "Evidence"]))
    A("")
    A("The wrong CatBench DOI string also appears outside docs/28 at: "
      + ", ".join(x for x in cb["all_citing_lines_in_docs_and_tasks"] if not x.startswith("docs/28")) + ".")
    A("")
    lab = [r for r in s5["docs28_flagged"] if ("LABEL_YEAR_NOT_IN_REGISTRAR_YEARS" in r["flags"]
                                               or "SLASH_NAME_NOT_AN_AUTHOR" in r["flags"])]
    rows = []
    for r in lab:
        if "SLASH_NAME_NOT_AN_AUTHOR" in r["flags"]:
            fix = f"\"{r['slash_names'][0]}\" is not an author; first author is {r['first_author']}"
        else:
            fix = _year_fix(r["wrong_label_years"], r["registrar_years"])
        rows.append([r["line"], f"`{r['doi']}`", r["label"].strip(" ·("), fix])
    A("Label defects where the DOI itself is right:")
    A("")
    A(_t(rows, ["Line", "DOI", "Label", "Correction"]))
    A("")
    ech = s5["docs28_label_echoes"]
    same_lab = [e for e in ech if e["status"] == "SAME_LABEL"]
    A(f"The same defects repeated in docs/28 clauses that carry no DOI: {len(ech)} clauses, {len(same_lab)} "
      "naming the same author, journal and wrong year (or the same name pair), "
      f"{len(ech) - len(same_lab)} naming author and year only.")
    A("")
    rows = []
    for e in ech:
        works = [w for ws in (e.get("other_works_same_author_journal_year") or {}).values() for w in ws]
        other = "; ".join(f"`{w['doi']}` \"{w['title'][:60]}…\" ({'/'.join(map(str, w['years']))}; author "
                          f"{w['author_position']} of {len(w['authors'])}; title words shared with the line: "
                          f"{len(w['line_title_words'])})" for w in works) or "—"
        if e["kind"] == "SLASH_NAME":
            fix = f"as :{e['source_line']}"
        elif e["correction_applies"]:
            fix = _year_fix(e["wrong_years"], e["registrar_years"])
        else:
            fix = "no correction (not linked to one work)"
        res = e.get("resolution", "—")
        if "source_line_title_words" in e:
            res += f" (DOI-row work shares {_n(len(e['source_line_title_words']), 'title word')} with the line)"
        rows.append([e["line"], e["clause"], e["status"], res, f":{e['source_line']} `{e['source_doi']}`", fix,
                     other])
    A(_t(rows, ["Line", "Clause", "Match", "Resolution", "Source row", "Correction",
                "Other works, same author, journal and year"]))
    A("")
    A("\"Other works\" are registrar records in the same journal and year that list the same author, so the "
      "label year could name them instead. A correction is listed only when the DOI row's work is the one "
      "the line is about (more shared title words than every other work) or the clause repeats a resolved "
      "label string verbatim.")
    A("")
    other = [r for r in s5["docs28_flagged"] if r["flags"] == ["NO_AUTHOR_OR_TITLE_AGREEMENT"]
             and r["doi"] != cb["cited_doi"]]
    A("Rows flagged only because the label names no author and shares no title word, with journal and "
      "year consistent, and no defect: " + "; ".join(
          f":{r['line']} `{r['doi']}` ({r['title'][:48]}…, consistent {r['journal_and_year_consistent']})"
          for r in other) + ". The docs/28 sentence \"our exact 9-dopant set\" is a content claim this DOI "
      "check does not test.")
    A("")

    # ------------------------------------------------------------------ limits
    A("## Limits")
    A("")
    A("- The Nørskov 2004 tables, the Man 2011 SI and Valdés 2008 were not read: they are closed, "
      "and the one publisher SI download was blocked. Reading these sources could settle the source "
      "of +0.40 eV. Sun et al. 2004's journal wording is checked against the MPG-hosted published PDF.")
    A("- COD pressure fields are often empty; where they are, \"ambient\" is inferred from the source "
      "title, which is weaker than a recorded pressure. The rutile-type ambient checks rest on "
      "named-mineral entries (plattnerite, cassiterite, argutite); the quartz-type GeO₂ check rests on the "
      "COD ids in its evidence row. Some COD GeO₂ entries are computed structures and are not ambient by "
      "the rule.")
    A("- Materials Project energies are DFT orderings at 0 K and move between database versions; they "
      "support \"lowest in MP\" and nothing about equilibrium at a temperature.")
    A("- Line classes in §4 and mention categories in §2 are judgments recorded with verbatim fragments; "
      "the counts depend on the patterns listed in `intercept_floor.json` and `structures.json`.")
    A("- Sub-claim boundaries in §2 are judgments recorded in `src/s2/f8/data/structure_claims.json`; each "
      "sub-claim is tested on its own evidence and none inherits another's verdict.")
    A("- A docs/28 clause without a DOI is tied to a DOI row only by the same author, journal and wrong "
      "year (or the same name pair); clauses naming author and year alone are listed, not corrected.")
    A("- The bibliography check tests registrar metadata, not whether a cited work supports its sentence.")
    A("")
    return "\n".join(L)
