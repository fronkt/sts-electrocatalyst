"""Build the P-BUILDER prestate: structures, slabs, enumerated configurations, denominators.

    python -m s2.p_builder.prestate build      [--fetch]   # from repo root, src/ on sys.path
    python -m s2.p_builder.prestate manifest

No symmetry is computed on any adsorbate structure by this module (the census module is
not imported). The clean-slab space group is recorded because the registered enumerator
itself reduces sites by the clean slab's symmetry.
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from pymatgen.io.cif import CifWriter

from . import decision
from .enumeration import (enumerate_configs, enumerator_internal_tolerances, min_image_distance_over_configs,
                          record_to_json, site_type_counts)
from .registered import (ADSORBATE_ORDER, ADSORBATES, BULK_CELL_SETTING, CODE_DIR, DECISION_DOC, DOCS43,
                         ENUM_FIND_ARGS, ENUM_REPEAT, FAMILIES, FAMILY_ORDER, PRESTATE_DIR, REPO, SLABGEN_KWARGS,
                         SYMPREC, T2_PY)
from .slabs import (clean_slab_symmetry, describe_slab, generate_slabs, reduced_in_plane_basis, select_termination,
                    surface_species, top_metal_atoms)
from .structures import (cif_provenance, fetch_cod, load_bulk, rutile_matches_cod, sha256_file,
                         write_rutile_cif)

MAN2011_PDF = REPO / "docs" / "research" / "papers" / "man2011.pdf"


def versions() -> dict:
    import numpy, scipy, spglib, pymatgen.core
    return dict(python=platform.python_version(), pymatgen=pymatgen.core.__version__, numpy=numpy.__version__,
                scipy=scipy.__version__, spglib=spglib.__version__, platform=platform.platform())


def _dump(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, indent=1, sort_keys=True)
        fh.write("\n")


def ensure_structures(out: Path, fetch: bool) -> dict:
    status = {}
    for fam in FAMILY_ORDER:
        spec = FAMILIES[fam]
        cod_file = out / (spec.get("provenance_cif") or spec["structure_file"])
        if not cod_file.exists():
            if not fetch:
                raise FileNotFoundError(f"{cod_file} missing; rerun with --fetch")
            fetch_cod(spec["cod_id"], cod_file)
            status[fam] = "fetched"
        else:
            status[fam] = "present"
    write_rutile_cif(out / FAMILIES["rutile110"]["structure_file"])
    return status


def plane_normal(lattice, miller) -> list[float]:
    """Unit normal of the (hkl) plane of `lattice`, in that lattice's Cartesian frame."""
    g = np.asarray(miller, dtype=float) @ lattice.reciprocal_lattice.matrix
    g = g / np.linalg.norm(g)
    return [round(float(x), 6) + 0.0 for x in g]


def shares_cartesian_frame(bulk, prim, tol: float = 1e-4) -> bool:
    """True when every site of `prim`, taken in Cartesian coordinates, sits on a same-species site of
    `bulk` (mod the bulk lattice): the two cells are then one crystal in one Cartesian frame."""
    for site in prim:
        frac = bulk.lattice.get_fractional_coords(site.coords)
        if not any(o.species_string == site.species_string
                   and bulk.lattice.get_all_distances(frac, o.frac_coords)[0][0] < tol for o in bulk):
            return False
    return True


def primitive_input_alternative(bulk, miller) -> dict:
    """The same registered SlabGenerator call on the primitive reduction of the source cell.

    Recorded to document the bulk-cell setting; the population uses the cell as deposited.
    Enumerator and geometry only (no symmetry on any adsorbate structure).
    """
    prim = bulk.get_primitive_structure()
    cands = []
    for i, s in enumerate(generate_slabs(prim, miller)):
        o = enumerate_configs(s, "O")
        ooh = enumerate_configs(s, "OOH")
        cands.append(dict(slab_index=i, n_atoms=len(s), surface_species=surface_species(s),
                          top_metal_atoms=top_metal_atoms(s), reduced_in_plane_basis=reduced_in_plane_basis(s),
                          n_configurations=len(o), site_types=site_type_counts(o),
                          OOH_min_image_distance=min_image_distance_over_configs(ooh)))
    return dict(primitive_bulk_n_sites=len(prim), primitive_bulk_abc_A=[float(x) for x in prim.lattice.abc],
                primitive_bulk_angles_deg=[float(x) for x in prim.lattice.angles],
                shares_source_cartesian_frame=shares_cartesian_frame(bulk, prim),
                plane_normal_deposited_cell=plane_normal(bulk.lattice, miller),
                plane_normal_primitive_cell=plane_normal(prim.lattice, miller), candidates=cands)


def build(out: Path = PRESTATE_DIR, fetch: bool = False) -> dict:
    fetched = ensure_structures(out, fetch)
    enum_internal = enumerator_internal_tolerances()
    denominators = dict(
        date="2026-09-16",
        registered=dict(docs43_lines="1900-1902", slab_generator_kwargs=SLABGEN_KWARGS,
                        enumerator=dict(call="AdsorbateSiteFinder(slab).generate_adsorption_structures",
                                        repeat=ENUM_REPEAT, find_args=ENUM_FIND_ARGS),
                        adsorbates={k: dict(species=v[0], coords_A=v[1]) for k, v in ADSORBATES.items()},
                        census_symprec=SYMPREC),
        enumerator_internal=enum_internal,
        bulk_cell_setting=BULK_CELL_SETTING,
        structure_fetch_status=fetched,
        families={},
    )
    for fam in FAMILY_ORDER:
        spec = FAMILIES[fam]
        bulk = load_bulk(fam, out)
        slabs = generate_slabs(bulk, spec["miller"])
        candidates = [dict(slab_index=i, shift=float(s.shift), n_atoms=len(s), formula=s.composition.formula,
                           surface_species=surface_species(s)) for i, s in enumerate(slabs)]
        idx, slab = select_termination(slabs, spec["termination"])
        slab_json = out / "slabs" / f"{fam}.json"
        slab_cif = out / "slabs" / f"{fam}.cif"
        _dump(slab_json, slab.as_dict())
        CifWriter(slab).write_file(str(slab_cif))
        n_metal = top_metal_atoms(slab)
        fam_rec = dict(
            label=spec["label"], formula=spec["formula"], miller=list(spec["miller"]), blind=spec["blind"],
            bulk=dict(file=(spec["structure_file"]), n_sites=len(bulk),
                      sha256=sha256_file(out / spec["structure_file"]),
                      cod_url=f"https://www.crystallography.net/cod/{spec['cod_id']}.cif",
                      lattice_abc_A=[float(x) for x in bulk.lattice.abc]),
            termination_rule=spec["termination"], termination_candidates=candidates, selected_slab_index=idx,
            slab=describe_slab(slab),
            clean_slab_symmetry=clean_slab_symmetry(slab, enumerator_symprec=enum_internal["symm_reduce_symprec"]),
            coverage=None,
            slab_files={"json": f"slabs/{fam}.json", "cif": f"slabs/{fam}.cif"},
            adsorbates={},
        )
        if spec["source"] == "cod":
            fam_rec["primitive_input_alternative"] = primitive_input_alternative(bulk, spec["miller"])
        if spec["source"] == "cod":
            fam_rec["bulk"]["provenance"] = cif_provenance(out / spec["structure_file"])
        else:
            fam_rec["bulk"]["provenance"] = cif_provenance(out / spec["provenance_cif"])
            fam_rec["bulk"]["registered_vs_cod"] = rutile_matches_cod(out / spec["provenance_cif"])
            fam_rec["bulk"]["provenance_cif_sha256"] = sha256_file(out / spec["provenance_cif"])
        for ads in ADSORBATE_ORDER:
            recs = enumerate_configs(slab, ads)
            path = out / "configs" / f"{fam}__{ads}.json"
            _dump(path, [record_to_json(r) for r in recs])
            fam_rec["adsorbates"][ads] = dict(n_configurations=len(recs), site_types=site_type_counts(recs),
                                              configs_file=f"configs/{fam}__{ads}.json",
                                              min_adsorbate_image_distance=min_image_distance_over_configs(recs))
            if ads == "O":
                per_cell = sorted({len(r["adsorbate_indices"]) for r in recs})  # one O atom per molecule
                fam_rec["coverage"] = dict(adsorbate_molecules_per_cell=per_cell, top_metal_atoms_per_cell=n_metal,
                                           adsorbates_per_top_metal_atom=f"{per_cell[0]}/{n_metal}"
                                           if len(per_cell) == 1 else None)
        denominators["families"][fam] = fam_rec
    _dump(out / "denominators.json", denominators)
    _dump(out / "decision.json", decision.decision_record(denominators))
    return denominators


def manifest(out: Path = PRESTATE_DIR) -> dict:
    inputs = {}
    for p in [DOCS43, T2_PY, MAN2011_PDF, DECISION_DOC]:
        if p.exists():
            inputs[p.relative_to(REPO).as_posix()] = sha256_file(p)
        else:
            inputs[p.relative_to(REPO).as_posix()] = None
    code = {p.relative_to(REPO).as_posix(): sha256_file(p) for p in sorted(CODE_DIR.glob("*.py"))}
    outputs = {p.relative_to(out).as_posix(): sha256_file(p)
               for p in sorted(out.rglob("*")) if p.is_file() and p.name != "manifest.json"}
    rec = dict(generated_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               versions=versions(), inputs_sha256=inputs, code_sha256=code, prestate_sha256=outputs,
               note=("man2011.pdf is not tracked in git (docs/research/papers/*.pdf is ignored); "
                     "its sha256 identifies the copy cited. p-builder.md hash is null if the doc did not "
                     "exist when the manifest was written."))
    _dump(out / "manifest.json", rec)
    return rec


def _short(h: str) -> str:
    return f"`{h[:12]}`"


def _frac_str(normal: list[float]) -> str:
    return "(" + ", ".join(f"{x:.4f}" for x in normal) + ")"


def file_hash_rows(out: Path) -> list[tuple[str, str]]:
    """(published path, full sha256) for every structure, slab and configuration file."""
    rows = []
    for d in ("structures", "slabs", "configs"):
        for p in sorted((out / d).glob("*")):
            if p.is_file():
                rows.append((p.relative_to(REPO).as_posix(), sha256_file(p)))
    return rows


def tables(out: Path = PRESTATE_DIR) -> str:
    """Markdown tables for the decision doc, read from the prestate JSON records."""
    den = json.loads((out / "denominators.json").read_text(encoding="utf-8"))
    dec = json.loads((out / "decision.json").read_text(encoding="utf-8"))
    gate_path = out / "atomate_gate.json"
    rerun_path = out / "rutile_nonblind_rerun.json"
    L = ["### Structures", "",
         "| family | source | space group | cell (Å) | literature | file |", "|---|---|---|---|---|---|"]
    for fam in FAMILY_ORDER:
        r = den["families"][fam]
        p = r["bulk"]["provenance"]
        src = "hand-built (t2.py), = COD " + str(p["cod_id"]) if r["bulk"].get("registered_vs_cod", {}).get(
            "sites_equal") else f"COD {p['cod_id']}"
        cell = f"a = {p['a_A']}" + (f", c = {p['c_A']}" if p["c_A"] != p["a_A"] else "")
        if fam == "rutile110":
            cell += f", u = {r['bulk']['registered_vs_cod']['u_cod']}"
        if fam == "spinel001":
            cell += f", O x = {[s['x'] for s in p['atom_sites'] if s['label'] == 'O'][0]} (origin 2)"
        lit = f"{'; '.join(p['authors'])}, *{p['journal']}* {p['volume']}, {p['pages']} ({p['year']})"
        if p.get("doi"):
            lit += f", {p['doi']}"
        if p.get("temperature_K"):
            lit += f"; {p['temperature_K']:g} K"
        L.append(f"| {r['label']} | {src} | {p['space_group_HM']} | {cell} | {lit} | `{r['bulk']['file']}` |")
    L += ["", f"Bulk-cell setting: {den['bulk_cell_setting']}.", "",
          "### Slabs (registered SlabGenerator arguments)", "",
          "| family | candidates (top-surface species) | selected | top layer: species depth Å (neighbours ≤ 2.3 Å) | atoms | "
          "surface cell (Å, °) | reduced in-plane basis (Å, °) | atom span / vacuum along normal (Å) | "
          "adsorbates per top-layer metal atom | clean-slab group (symprec 1e-3) |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for fam in FAMILY_ORDER:
        r = den["families"][fam]
        s = r["slab"]
        cands = "; ".join(f"[{c['slab_index']}] " + " ".join(f"{k}{v}" for k, v in c["surface_species"].items())
                          for c in r["termination_candidates"])
        top = ", ".join(f"{t['species']} {t['depth_A']:.3f} ({t['n_neighbours_2p3A']})" for t in s["top_sites_within_0p9A"])
        cs = r["clean_slab_symmetry"]
        cov = r["coverage"]
        L.append(f"| {r['label']} | {cands} | [{r['selected_slab_index']}] | {top} | {s['n_atoms']} ({s['formula']}) | "
                 f"{s['lattice_abc_A'][0]:.4f} × {s['lattice_abc_A'][1]:.4f}, γ = {s['lattice_angles_deg'][2]:.0f} | "
                 f"{s['reduced_in_plane_basis']['lengths_A'][0]:.4f} × {s['reduced_in_plane_basis']['lengths_A'][1]:.4f}, "
                 f"{s['reduced_in_plane_basis']['angle_deg']:.0f} | "
                 f"{s['atom_span_along_normal_A']:.3f} / {s['vacuum_gap_along_normal_A']:.3f} | "
                 f"{cov['adsorbates_per_top_metal_atom']} ({cov['top_metal_atoms_per_cell']} top-layer metal) | "
                 f"{cs['space_group_symbol']}, {cs['n_operations']} ops ({cs['n_operations_preserving_normal']} keep the normal) |")
    ei = den["enumerator_internal"]
    L += ["", "### Enumerator reduction group (clean slabs only)", "",
          f"Read from the installed pymatgen (`analysis/adsorption.py` sha256 {_short(ei['pymatgen_adsorption_py_sha256'])}): "
          f"`find_adsorption_sites` defaults symm_reduce = {ei['symm_reduce_default']}, near_reduce = "
          f"{ei['near_reduce_default']}, no_obtuse_hollow = {ei['no_obtuse_hollow_default']}; `symm_reduce` takes its "
          f"operations from `SpacegroupAnalyzer(self.slab, {ei['symm_reduce_symprec']})` and matches positions in fractional "
          f"coordinates at atol = threshold: {ei['symm_reduce_matches_fractional_coords_at_threshold']}.", "",
          f"| family | census group (symprec {den['registered']['census_symprec']}) | enumerator group (symprec "
          f"{ei['symm_reduce_symprec']}) | operation sets identical | max translation difference (fractional) | "
          "symm_reduce match tolerance along a, b, c (Å) |", "|---|---|---|---|---|---|"]
    for fam in FAMILY_ORDER:
        r = den["families"][fam]
        cs = r["clean_slab_symmetry"]
        e = cs["at_enumerator_symprec"]
        abc = r["slab"]["lattice_abc_A"]
        tol = " / ".join(f"{ei['symm_reduce_default'] * x:.3f}" for x in abc)
        L.append(f"| {r['label']} | {cs['space_group_symbol']}, {cs['n_operations']} ops | {e['space_group_symbol']}, "
                 f"{e['n_operations']} ops | {e['operation_set_identical_to_census_symprec']} | "
                 f"{e['max_translation_diff_frac']} | {tol} |")
    L += ["", "### Bulk-cell setting: the primitive-input alternative (enumerator only, not in the population)", "",
          "| family | primitive bulk sites | (hkl) normal, deposited cell | (hkl) normal, primitive cell | same frame | "
          "candidates: atoms, top species, reduced basis (Å, °), N (ontop/bridge/hollow), *OOH image contact (Å) |",
          "|---|---|---|---|---|---|"]
    for fam in FAMILY_ORDER:
        r = den["families"][fam]
        pa = r.get("primitive_input_alternative")
        if not pa:
            continue
        cands = "; ".join(
            f"[{c['slab_index']}] {c['n_atoms']}, " + " ".join(f"{k}{v}" for k, v in c["surface_species"].items())
            + f", {c['reduced_in_plane_basis']['lengths_A'][0]:.4f} × {c['reduced_in_plane_basis']['lengths_A'][1]:.4f} "
              f"{c['reduced_in_plane_basis']['angle_deg']:.0f}, N = {c['n_configurations']} "
              f"({c['site_types']['ontop']}/{c['site_types']['bridge']}/{c['site_types']['hollow']}), "
              f"{c['OOH_min_image_distance']['min_distance_A']:.3f}"
            for c in pa["candidates"])
        L.append(f"| {r['label']} | {pa['primitive_bulk_n_sites']} (deposited {r['bulk']['n_sites']}) | "
                 f"{_frac_str(pa['plane_normal_deposited_cell'])} | {_frac_str(pa['plane_normal_primitive_cell'])} | "
                 f"{pa['shares_source_cartesian_frame']} | {cands} |")
    ooh_o1o2 = float(np.linalg.norm(np.array(ADSORBATES["OOH"][1][1]) - np.array(ADSORBATES["OOH"][1][0])))
    L += ["", "### Adsorbate–image contacts (geometry only)", "",
          f"Shortest distance from an adsorbate atom to an adsorbate atom of an in-plane periodic image, minimum over the "
          f"configurations; for reference the O₁–O₂ distance inside the registered OOH is {ooh_o1o2:.3f} Å.", "",
          "| family | *O (Å) | *OH (Å) | *OOH (Å, pair) |", "|---|---|---|---|"]
    for fam in FAMILY_ORDER:
        r = den["families"][fam]
        a = r["adsorbates"]
        L.append(f"| {r['label']} | {a['O']['min_adsorbate_image_distance']['min_distance_A']:.3f} | "
                 f"{a['OH']['min_adsorbate_image_distance']['min_distance_A']:.3f} | "
                 f"{a['OOH']['min_adsorbate_image_distance']['min_distance_A']:.3f} "
                 f"({'–'.join(a['OOH']['min_adsorbate_image_distance']['pair'])}) |")
    L += ["", "### Files named by path and sha256", "", "| file | sha256 |", "|---|---|"]
    for rel, h in file_hash_rows(out):
        L.append(f"| `{rel}` | `{h}` |")
    L += ["", "### Denominators and X", "",
          "| family | N per adsorbate (O = OH = OOH) | ontop/bridge/hollow | X for *O, *OH | HELD if retained ≥ | "
          "FALSIFIED if retained ≤ | gap | *OOH | pooled reading at the predicted minimum (not used) |",
          "|---|---|---|---|---|---|---|---|---|"]
    for fam in FAMILY_ORDER:
        r = den["families"][fam]
        d = dec["families"][fam]
        st = r["adsorbates"]["O"]["site_types"]
        gap = ", ".join(str(g) for g in d["gap"]) or "none"
        pc = d["pooled_reading_not_used"]
        pooled = (f"{pc['fraction']} = {pc['value']:.3f}" + ("; at or below 1/2" if pc["at_or_below_half_line"] else "")
                  + f"; above 1/2 needs ≥ {pc['min_upright_retained_above_half_line_if_pooled']} upright")
        L.append(f"| {r['label']} | {r['adsorbates']['O']['n_configurations']} | {st['ontop']}/{st['bridge']}/{st['hollow']} | "
                 f"{d['X']['fraction']} = {d['X']['value']:.3f} | {d['X']['HELD_if_retained_at_least']} | "
                 f"{d['FALSIFIED_if_retained_at_most']} | {gap} | {d['OOH']['expected_retained']} (construction) | {pooled} |")
    ob = dec["OOH_bound"]
    fam_min = min(ob["shortest_in_plane_vector_A"], key=ob["shortest_in_plane_vector_A"].get)
    L += ["", f"*OOH bound: 2|d_lat(O₂)| = {ob['O2_max_shift_A']:.2f} Å; mirror shift of H = {ob['H_mirror_shift_A']:.2f} Å; "
              f"shortest in-plane lattice vector = {ob['shortest_in_plane_vector_A'][fam_min]:.4f} Å "
              f"({den['families'][fam_min]['label']}); holds for all families: {all(ob['holds'].values())}."]
    if rerun_path.exists():
        rr = json.loads(rerun_path.read_text(encoding="utf-8"))["families"]["rutile110"]
        c = rr["census"]
        L += ["", "### rutile(110) in-repo re-run (non-blind)", "",
              "| adsorbate | retained / N | space group P1 | ontop | bridge | hollow | verdict |", "|---|---|---|---|---|---|---|"]
        for a in ADSORBATE_ORDER:
            bt = c[a]["by_site_type"]
            v = rr["verdicts"].get(a, "construction check: " + ("pass" if rr["construction_checks"]["OOH_zero"] else "fail"))
            L.append(f"| *{a} | {c[a]['retained']}/{c[a]['n_configurations']} | {c[a]['n_space_group_P1']} | "
                     f"{bt['ontop']['retained']}/{bt['ontop']['n']} | {bt['bridge']['retained']}/{bt['bridge']['n']} | "
                     f"{bt['hollow']['retained']}/{bt['hollow']['n']} | {v} |")
        pr = rr["pooled_all_adsorbates"]
        L.append(f"| pooled *O, *OH, *OOH | {pr['fraction']} | – | – | – | – | no verdict (reading) |")
        L.append("")
        L.append(f"Reproduces docs/43 :{rr['disclosure_2026_08_15']['docs43_line']} disclosure: "
                 f"{rr['reproduces_disclosure']}; slab rebuild max |Δ| = {rr['reproduction']['slab_rebuild_max_abs_diff_A']} Å; "
                 f"enumerator re-run max |Δ| = {max(rr['reproduction']['enumerator_rerun_max_abs_diff_A'].values())} Å.")
    if gate_path.exists():
        gate = json.loads(gate_path.read_text(encoding="utf-8"))
        ch, src = gate["checks"], gate["sources"]
        L += ["", "### Atomate gate", "", "| check | result | evidence |", "|---|---|---|"]
        d1 = ch["1_isym0_in_MPSurfaceSet_under_comment_at_a7d5f316"]["detail"]
        L.append(f"| MPSurfaceSet sets ISYM 0 under the comment at a7d5f316 | {ch['1_isym0_in_MPSurfaceSet_under_comment_at_a7d5f316']['ok']} | "
                 f"`{ADS}` class l.{d1['class_span'][0]} (base {d1['base_class']}), comment l.{d1['comment_line']['line']}, "
                 f"`\"ISYM\": 0` l.{d1['isym_line']['line']}, `incar.update(self.user_incar_settings)` "
                 f"l.{d1['user_incar_settings_updates'][0]['line']}; blob {src['adsorption_py_at_isym_commit']['api_blob_sha'][:12]} |")
        d2 = ch["2_introduced_2018_05_25_by_a7d5f316"]["detail"]
        L.append(f"| introduced by a7d5f316 on 2018-05-25 | {ch['2_introduced_2018_05_25_by_a7d5f316']['ok']} | "
                 f"{src['commit_isym']['sha'][:12]}, {d2['committer_date']}, "
                 f"message \"{d2['message']}\"; parent {d2['parent'][:12]} has {d2['parent_isym_count']} ISYM lines |")
        o = ch["2q_comment_predates_isym"]["detail"]
        L.append(f"| comment origin (qualifier) | earlier commit | {o['sha'][:12]}, {o['committer_date']}, \"{o['message']}\" "
                 f"({', '.join(x.lstrip('+') for x in o['added_class_lines'])}) |")
        d3 = ch["3_d2742a3b_uses_MVLSlabSet_no_ISYM"]["detail"]
        L.append(f"| d2742a3b workflow uses MVLSlabSet, no ISYM | {ch['3_d2742a3b_uses_MVLSlabSet_no_ISYM']['ok']} | "
                 f"{src['commit_2017']['sha'][:12]}, {d3['committer_date']}; "
                 f"l.{d3['default_lines'][0]['line']} `{d3['default_lines'][0]['text'].strip()}`; ISYM lines {d3['isym_count']} |")
        d4 = ch["4_MVLSlabSet_at_pinned_pymatgen_sets_no_ISYM"]["detail"]
        L.append(f"| MVLSlabSet at the pinned pymatgen sets no ISYM | {ch['4_MVLSlabSet_at_pinned_pymatgen_sets_no_ISYM']['ok']} | "
                 f"requirements.txt l.{d4['pin'][0]['line']} `{d4['pin'][0]['text']}`; {d4['tag']} sets.py "
                 f"l.{d4['class_line'][0]['line']} `{d4['class_line'][0]['text']}`; ISYM in class {d4['isym_in_class']}, "
                 f"in MPRelaxSet.yaml {d4['isym_in_yaml']}, LHFCALC in yaml {d4['lhfcalc_in_yaml']} |")
        k4b = "4b_MVLSlabSet_chain_no_ISYM_every_admitted_release_before_a7d5f316"
        d4b = ch[k4b]["detail"]
        L.append(f"| scope: every pymatgen release setup.py admits, before a7d5f316 | {ch[k4b]['ok']} | "
                 f"setup.py l.{d4b['setup_py_line'][0]['line']} `pymatgen{d4b['specifier']}`; {d4b['n_releases']} PyPI releases "
                 f"first uploaded before {d4b['uploaded_before_utc']} ({d4b['first']} to {d4b['last']}); sdist sha256 = PyPI "
                 f"{d4b['n_sdist_sha256_match']}/{d4b['n_releases']}; no ISYM in {'; '.join(d4b['chains'])} or in "
                 f"{', '.join(y + '.yaml' for y in d4b['yaml_configs'])}: {d4b['n_no_isym']}/{d4b['n_releases']} |")
        d5 = ch["5_vasp_default_isym_2"]["detail"]
        L.append(f"| VASP default ISYM = 2 | {ch['5_vasp_default_isym_2']['ok']} (qualified) | VASP wiki ISYM rev. "
                 f"{d5['revision_id']}: \"{d5['default_text']}\" |")
        d6 = ch["6_default_branch_still_isym0"]["detail"]
        L.append(f"| default branch today | {ch['6_default_branch_still_isym0']['ok']} | "
                 f"{d6['commit'][:12]} ({src['adsorption_py_at_default_branch']['committer_date']}), "
                 f"`\"ISYM\": 0` l.{d6['isym_line']['line']} |")
        k7 = "7_isym0_every_default_branch_version_since_a7d5f316"
        d7 = ch[k7]["detail"]
        vers = ", ".join(f"{v['sha'][:8]} l.{v['isym_line']}" for v in reversed(d7["versions"]))
        L.append(f"| scope: every default-branch version since a7d5f316 | {ch[k7]['ok']} | {d7['n_versions']} versions "
                 f"({vers}); each has ISYM 0 under the comment and MPSurfaceSet as workflow default: "
                 f"{sum(1 for v in d7['versions'] if v['ok'])}/{d7['n_versions']}; a7d5f316 → head {d7['compare_status']} "
                 f"by {d7['compare_ahead_by']} commits; head blob = newest version: {d7['head_blob_equals_newest_listed']} |")
        L.append("")
        L.append(f"GATE passed: {ch['GATE']['passed']} (checked {gate['checked_utc']}).")
        L.append("")
        L.append("Dated statement, as worded by the checks:")
        L.append("")
        for t in ch["DATED_STATEMENT"]["text"]:
            L.append(f"> {t}")
            L.append(">")
        L.pop()
    text = "\n".join(L) + "\n"
    with open(out / "tables.md", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return text


ADS = "atomate/vasp/workflows/base/adsorption.py"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command", choices=["build", "manifest", "tables"])
    ap.add_argument("--out", type=Path, default=PRESTATE_DIR)
    ap.add_argument("--fetch", action="store_true", help="download missing COD CIFs")
    args = ap.parse_args(argv)
    if args.command == "build":
        d = build(args.out, args.fetch)
        for fam, r in d["families"].items():
            print(fam, {a: v["n_configurations"] for a, v in r["adsorbates"].items()},
                  r["adsorbates"]["O"]["site_types"], r["slab"]["surface_species"])
    elif args.command == "tables":
        sys.stdout.reconfigure(encoding="utf-8")
        print(tables(args.out))
    else:
        m = manifest(args.out)
        print(f"{len(m['prestate_sha256'])} prestate files hashed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
