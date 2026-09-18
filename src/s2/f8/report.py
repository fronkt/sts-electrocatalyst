"""Summary object and the dated research note, rendered from result JSON only."""
from __future__ import annotations

from collections import Counter

REGISTRATION = "docs/43-prereg-week1-factorial.md"


def _r(x, n=4):
    return None if x is None else round(float(x), n)


def build_summary(sun: dict, st: dict, zp: dict, itf: dict, bb: dict) -> dict:
    # --- 1
    cl = [r for r in sun["citing_lines"] if r["role"] == "CLAIM"]
    s1 = {
        "verdicts": sun["claim_verdicts"],
        "subclaims": sun["subclaims"],
        "crossref": sun["crossref"],
        "record_matches": sun["bibliographic_record_matches_repo_citation"],
        "arxiv_id": sun["arxiv"]["id"], "arxiv_title": sun["arxiv"]["title"],
        "identity": sun["identity_checks"], "access": sun["access"],
        "quotes": {k: (None if v is None else {"page": v["page"], "match": v["match"]})
                   for k, v in sun["quotes"].items()},
        "pdf_pages": sun["pdf_pages"],
        "version_of_record": sun["version_of_record"],
        "claim_lines": [{"file": r["file"], "line": r["line"], "quote": r.get("claim_quote")} for r in cl],
        "other_lines": [{"file": r["file"], "line": r["line"], "role": r["role"]}
                        for r in sun["citing_lines"] if r["role"] != "CLAIM"],
    }
    # --- 2
    cod_tab = {}
    for f, c in st["cod"].items():
        mp = st["mp"][f]["docs"]
        rut = [d for d in mp if d["sg_number"] == 136]
        cod_tab[f] = {"cod_returned": c["n_returned"], "cod_parsed": c["n_parsed"],
                      "cod_unparsed": c["n_unparsed"], "prototypes": c["prototype_counts"],
                      "cod_ambient_prototypes": dict(sorted(Counter(
                          e["prototype"] for e in c["entries"] if e["ambient_pressure"]).items())),
                      "cod_declared_vs_computed_sg_disagreements": sum(
                          1 for e in c["entries"] if e["sg_number_declared"] and
                          int(e["sg_number_declared"]) != e["sg_number_computed"]),
                      "mp_n": st["mp"][f]["n"], "mp_lowest": mp[0] if mp else None,
                      "mp_rutile_e_above_hull": rut[0]["e_above_hull_eV_atom"] if rut else None,
                      "mp_rutile_icsd_ids": rut[0]["icsd_ids"] if rut else [],
                      "mp_next": mp[1:4]}
    def _chk(k):
        return {"kind": k["kind"], "result": k["result"], "n": k.get("n_matching_entries"),
                "params": k.get("params"), "reason": k.get("reason"),
                "cod_ids": [e["cod_id"] for e in k.get("evidence", [])]}
    claims = [{"id": c["id"], "file": c["file"], "line": c["located"]["line"], "found": c["located"]["found"],
               "assertion": c["assertion"],
               "subclaims": [{"id": sc["id"], "text": sc["text"], "verdict": sc["verdict"], "reason": sc["reason"],
                              "checks": [_chk(k) for k in sc["checks"]],
                              "supporting_context": [_chk(k) for k in sc["supporting_context"]],
                              "narrowed": ({"text": sc["narrowed"]["text"], "verdict": sc["narrowed"]["verdict"],
                                            "checks": [_chk(k) for k in sc["narrowed"]["checks"]]}
                                           if "narrowed" in sc else None)}
                             for sc in c["subclaims"]],
               "context": [_chk(k) for k in c["context_checks"]],
               "note": c["polymorphism_note"]} for c in st["claims"]]
    refs = {}
    for f, c in {**st["cod"], **st["cod_reference"]}.items():
        for e in c["entries"]:
            refs[e["cod_id"]] = {"formula": f, "authors": e["authors"], "year": e["year"],
                                 "journal": e["journal"], "volume": e["volume"], "firstpage": e["firstpage"],
                                 "doi": e["doi"], "title": e["title"], "mineral": e["mineral"],
                                 "sg": e["sg_symbol_computed"], "prototype": e["prototype"],
                                 "pressure_kPa": e["pressure_kPa"]}
    used = sorted({i for cl_ in claims for sc in cl_["subclaims"]
                   for k in sc["checks"] + sc["supporting_context"] for i in k["cod_ids"]}, key=int)
    s2 = {"cod_refs": {i: refs[i] for i in used}, "cod_all": refs,
          "symprec_A": st["symprec_A"], "ambient_max_kPa": st["ambient_max_kPa"],
          "cod_mp": cod_tab, "claims": claims, "verdict_rule": st["verdict_rule"],
          "cod_reference_counts": {f: {"returned": c["n_returned"], "parsed": c["n_parsed"],
                                       "prototypes": c["prototype_counts"]}
                                   for f, c in st["cod_reference"].items()},
          "subclaim_verdict_counts": dict(sorted(Counter(sc["verdict"] for cl_ in claims
                                                         for sc in cl_["subclaims"]).items())),
          "mention_counts": st["mention_counts"],
          "n_mentions": len(st["mentions"]), "mp_ids": st["mp_ids"],
          "unmatched_curated": st["curated_mentions_not_matched_by_scan"]}
    # --- 3
    cen = zp["man2011_pdf"]["token_census"]
    s3 = {
        "man2011_sha256": zp["man2011_pdf"]["sha256"], "man2011_pages": zp["man2011_pdf"]["pages"],
        "man2011_token_counts": {k: v["n"] for k, v in cen.items()},
        "man2011_0.05_context": [h["context"] for h in cen[r"0\.05"]["hits"]],
        "man2011_zero_point_context": [h["context"] for h in cen[r"zero[- ]point"]["hits"]],
        "man2011_si": zp["man2011_si_fetch"],
        "table_si1": {k: zp["divanis_table_si1"][k] for k in ("path", "line", "header", "rows", "row_order",
                                                                "has_OOH_row", "sha256_matches_SHA256SUMS")},
        "species": zp["species_columns_from_table"],
        "corr_tabulated": zp["corr_tabulated"],
        "corr_recomputed": {k: _r(v, 3) for k, v in zp["corr_recomputed_from_species_columns"].items()},
        "repo_constant": zp["repo_constant"],
        "implied": {k: _r(v, 3) for k, v in zp["implied"].items()},
        "candidates": zp["candidate_primary_sources"],
    }
    s3["registered_delta"] = zp["registered_delta"]
    s3["attribution_line_numbers"] = [int(a.split(":")[1]) for a in zp["repo_constant"]["attribution_lines"]]
    unread = all(not c["main_text_pdf_on_disk"] and c["openalex_oa_status"] == "closed"
                 for c in zp["candidate_primary_sources"] if c["doi"] != "10.1002/cctc.201000397")
    s3["verdict"] = ("EXCLUDED" if s3["man2011_token_counts"][r"0\.40"] == 0
                     and not s3["table_si1"]["has_OOH_row"] and unread else "REVIEW")
    # --- 4
    s4 = {"summary": itf["summary"], "patterns": itf["patterns"], "n_files_scanned": itf["n_files_scanned"],
          "n_lines_in_src_or_tests": sum(1 for r in itf["rows"] if r["file"].startswith(("src/", "tests/"))),
          "quantitative": [{"file": r["file"], "line": r["line"], "class": r["class"],
                            "fragment": r.get("fragment"), "note": r.get("note")}
                           for r in itf["rows"] if r["quantitative_use"]],
          "unclassified": [{"file": r["file"], "line": r["line"], "excerpt": r["excerpt"]}
                           for r in itf["rows"] if r["class"] in ("UNCLASSIFIED", "FRAGMENT_MISMATCH")],
          "class_definitions": itf["class_definitions"],
          "sweep_pattern": itf["sweep_pattern"], "n_sweep_lines": itf["n_sweep_lines"]}
    # --- 5
    corr = bb["docs28_corrections"]
    lab = [{"line": r["line"], "doi": r["doi"], "label": r["label_segment"][-60:], "flags": r.get("flags", []),
            "title": r.get("title"), "first_author": r.get("first_author"),
            "registrar_years": r.get("registrar_years"), "label_years": r.get("label_years"),
            "wrong_label_years": r.get("wrong_label_years"),
            "slash_names": r.get("slash_names"),
            "journal_and_year_consistent": r.get("label_journal_and_year_consistent")}
           for r in bb["docs28"] if r.get("flags") or r["state"] != "RESOLVED"]
    s5 = {"bib": bb["bib_summary"], "docs28_n_doi_mentions": len(bb["docs28"]),
          "docs28_n_unique_dois": len({r["doi"] for r in bb["docs28"]}),
          "docs28_flagged": lab, "docs28_corrections": corr,
          "docs28_label_echoes": bb["docs28_label_echoes"]}
    verdicts = {
        "sun_reuter_scheffler_2004": s1["verdicts"],
        "structure_subclaims": {sc["id"]: sc["verdict"] for c in claims for sc in c["subclaims"]},
        "structure_narrowed_forms": {sc["id"]: sc["narrowed"]["verdict"] for c in claims
                                     for sc in c["subclaims"] if sc["narrowed"]},
        "ooh_plus_0.40": s3["verdict"],
        "intercept_floor_quantitative_lines": s4["summary"]["n_quantitative_lines"],
        "intercept_floor_unclassified": s4["summary"]["n_unclassified"],
        "bib_non_match_rows": len(s5["bib"]["non_match_rows"]),
        "bib_doi_field_defects": len(s5["bib"]["doi_field_defects"]),
        "docs28_corrected_dois": {k: v["corrected_doi"] for k, v in corr.items()},
    }
    return {"verdicts": verdicts, "sun2004": s1, "structures": s2, "zpe": s3,
            "intercept_floor": s4, "bibliography": s5}


def render(s: dict) -> str:
    from .report_text import render as _render
    return _render(s)
