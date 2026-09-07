#!/usr/bin/env python3
"""Build fidelity-pilot decks from a screen-diagnostic-v1 census result: for one
(formula, seed, site) chain, fixed-geometry SCFs on the relaxed clean slab (from
decoration_records) and the three winning adsorbate states (relaxed_states OH, O, OOH), each
in HUBBARD (atomic) and HUBBARD (ortho-atomic), into
<out-root>/<formula>__s<seed>_site<site>/<state>__{atomic,ortho}.in, plus one manifest per
out-root in the A0 format (NOT LICENSED). <out-root> must lie under <repo>/runs (manifest
rows are relative to $RUNS, anvil/46_a0.slurm:57); anything else is refused before a byte
is written.

    python src/dft/build_hea_pilot.py --census <result.json> --formula <label> --seed <s> --site <i>
                                      [--states slab,OH,O,OOH] [--out-root runs/hea/pilot]
                                      [--manifest runs/hea/m_pilot.txt] [--verify-sha <verification.json>]
                                      [--reuse STATE=branch_panel/<label>]...

A state whose retained geometry is byte-identical (except the prefix line) to an already
built panel deck is not built twice: `--reuse OOH=branch_panel/<label>` names the panel deck,
the render is asserted identical to it at build, the manifest lists the reuse in its header
with the panel deck's md5, and no runnable row is emitted for it (the readout reads the
panel output). The two retained chains are exercised by --retained (equiatomic seed 2 site 0;
leader seed 0 site 0), whose OOH states are the panel decks equiatomic_pull2.10 and
leader_pull2.10, into runs/hea/pilot_retained/ with manifest runs/hea/m_pilot_retained.txt.

Deck settings and guards are those of src/dft/hea_deck.py (banked 2x1v namelists, MP U set
of record, FM starts of record, k-mesh rule on the actual cell, exact coordinate round-trip,
UPF preflight, CR refusal, overwrite refusal).
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from hea_deck import (BuildError, EXCLUDE, NP, REPO, check_manifest_text, deck_info,  # noqa: E402
                      load_json, load_template, render_deck, sha256_lf, write_lf)
import hea_cost_model as cm  # noqa: E402
import hea_geometry as hg  # noqa: E402

BANK = REPO / "results" / "cr_site_chains_2026-09-06"
RUNS = REPO / "runs"
STATES = ("slab", "OH", "O", "OOH")
PROJECTORS = ("atomic", "ortho")
RETAINED = tuple(dict(census=BANK / c["census"], formula=c["formula"], seed=c["seed"], site=c["site"],
                      reuse={st: f"branch_panel/{lab}" for st, lab in c["reuse"].items()})
                 for c in cm.RETAINED_CHAINS)
RETAINED_OUT = RUNS / "hea" / "pilot_retained"
RETAINED_MANIFEST = RUNS / "hea" / "m_pilot_retained.txt"


def find_chain(census: Path, formula: str, seed: int, site: int) -> dict:
    doc = load_json(census)
    if doc.get("schema") != "screen-diagnostic-v1":
        raise BuildError(f"{census}: schema is {doc.get('schema')!r}, expected screen-diagnostic-v1")
    hits = [r for r in doc["results"] if r["formula"] == formula]
    if len(hits) != 1:
        raise BuildError(f"{census}: {len(hits)} results for formula {formula!r}")
    res = hits[0]
    if res["status"] != "evaluated":
        raise BuildError(f"{census}: {formula} status {res['status']!r}")
    row = res["row"]
    decs = [d for d in row["decoration_records"] if d["seed"] == seed]
    if len(decs) != 1:
        raise BuildError(f"{formula}: {len(decs)} decoration records for seed {seed}")
    sites = [p for p in row["per_site_records"] if p["seed"] == seed and p["site_index"] == site]
    if len(sites) != 1:
        raise BuildError(f"{formula}: {len(sites)} per-site records for seed {seed} site {site}")
    ps = sites[0]
    slab = decs[0]["relaxed_slab"]
    geoms = {"slab": slab}
    for sp in ("OH", "O", "OOH"):
        geoms[sp] = ps["relaxed_states"][sp]
    for name, g in geoms.items():
        if not g.get("converged_by_force", False):
            raise BuildError(f"{formula} s{seed} site{site} {name}: not force-converged in the record")
        if g["pbc"] != [True, True, True] or g.get("other_constraint_types"):
            raise BuildError(f"{formula} {name}: unexpected pbc/constraints")
        if g["cell_A"] != slab["cell_A"] or sorted(g["fixed_atom_indices"]) != sorted(slab["fixed_atom_indices"]):
            raise BuildError(f"{formula} {name}: cell/constraints differ from the clean slab")
        if g["symbols"][:len(slab["symbols"])] != slab["symbols"]:
            raise BuildError(f"{formula} {name}: slab atom order differs from the clean slab")
    se_sites = [s for s in res.get("site_evidence", {}).get("sites", [])
                if s.get("seed") == seed and s.get("site_index") == site]
    se_status = se_sites[0].get("status") if len(se_sites) == 1 else None
    integrity = {st: hg.analyse(g["symbols"], g["positions_A"], g["cell_A"], n_slab=len(slab["symbols"]))
                 for st, g in geoms.items()}
    return dict(census=census, formula=formula, candidate_id=res["candidate_id"], seed=seed, site=site,
                geoms=geoms, energies=ps["energies_eV"], dG=dict(OH=ps["dG_OH"], O=ps["dG_O"], OOH=ps["dG_OOH"]),
                eta=ps["eta"], pls=ps["pls"], desorbed=ps["desorbed"], gas=row["gas_reference_records"],
                initial_metal=ps["initial_binding_metal"], initial_index=ps["initial_binding_metal_index"],
                final_metals={sp: ps["relaxed_states"][sp].get("final_binding_metal") for sp in ("OH", "O", "OOH")},
                model=doc["manifest"]["model"], site_evidence=se_status, integrity=integrity,
                composition_stats={k: row.get(k) for k in ("n_sites", "n_decorations", "eta_min", "eta_mean", "eta_std", "eta_max")},
                reuse={})


def _same_except_prefix(a: str, b: str) -> bool:
    la, lb = a.split("\n"), b.split("\n")
    if len(la) != len(lb):
        return False
    diff = [(x, y) for x, y in zip(la, lb) if x != y]
    return len(diff) == 1 and diff[0][0].startswith("  prefix = ") and diff[0][1].startswith("  prefix = ")


def build_chain(chain: dict, out_root: Path, states, check_only: bool, template) -> list:
    tag = f"{chain['formula']}__s{chain['seed']}_site{chain['site']}"
    rows = []
    for st in states:
        g = chain["geoms"][st]
        for proj in PROJECTORS:
            job = f"{st}__{proj}"
            text = render_deck(job, g["symbols"], g["positions_A"], g["cell_A"], g["fixed_atom_indices"], proj, template)
            info = deck_info(text)
            if info["counts"] != dict(Counter(g["symbols"])):
                raise BuildError(f"{tag}/{job}: species counts differ from the record")
            cost = cm.per_scf(info["counts"], info["cell"], info["nkpts"], info["nk"])
            row = dict(tag=tag, state=st, job=job, projector=proj, info=info, chain=chain, reuse=None,
                       plan_coreh=cost[proj]["plan_coreh"], floor_coreh=cost[proj]["floor_coreh"],
                       ceiling_coreh=cost[proj]["ceiling_coreh"], ram_total_GB=cost["ram_total_GB_envelope"])
            reuse = chain["reuse"].get(st)
            if reuse:
                panel_deck = RUNS / "hea" / f"{reuse}__{proj}.in"
                if not panel_deck.exists():
                    raise BuildError(f"{tag}/{job}: reuse target {panel_deck} does not exist")
                ptext = panel_deck.read_bytes().decode("utf-8")
                if not _same_except_prefix(text, ptext):
                    raise BuildError(f"{tag}/{job}: render is NOT identical (except prefix) to {panel_deck}; refusing the reuse")
                dst = out_root / tag / f"{job}.in"
                if dst.exists():
                    raise BuildError(f"{dst} exists although the state is reused from {panel_deck}; remove it")
                row.update(reuse=f"hea/{reuse}__{proj}", md5=hashlib.md5(panel_deck.read_bytes()).hexdigest())
                rows.append(row)
                continue
            dst = out_root / tag / f"{job}.in"
            if check_only:
                if dst.exists() and dst.read_bytes() != text.encode("utf-8"):
                    raise BuildError(f"{dst} differs from a fresh render")
                h = hashlib.md5(text.encode("utf-8")).hexdigest()
            else:
                h = write_lf(dst, text)
            row.update(md5=h)
            rows.append(row)
    return rows


def manifest_text(rows: list, out_root: Path, chains: list) -> str:
    rel = out_root.relative_to(RUNS).as_posix()   # rows are relative to $RUNS (anvil/46_a0.slurm:57)
    run = [r for r in rows if not r["reuse"]]
    reused = [r for r in rows if r["reuse"]]
    plan = sum(r["plan_coreh"] for r in run)
    floor = sum(r["floor_coreh"] for r in run)
    ceil = sum(r["ceiling_coreh"] for r in run)
    ram = max(r["ram_total_GB"] for r in run)
    meshes = {r["info"]["mesh"] for r in rows}
    nks = {r["info"]["nk"] for r in rows}
    L = [
        f"# HEA fidelity-pilot manifest -- fixed-geometry SCFs on retained MACE chains ({rel}),",
        "# clean slab + winning OH/O/OOH per chain, each in HUBBARD (atomic) and (ortho-atomic).",
        "# Built by src/dft/build_hea_pilot.py; every deck's coordinates re-parse to the retained",
        "# positions_A exactly (asserted at build).",
        "#",
        "# WHY. Zero held-out DFT points exist for the HEA screen (docs/40:34); the SQS tier of",
        "# docs/22 never ran. A fixed-geometry DFT eta on the model's own relaxed chain, read beside",
        "# the model's eta at the same coordinates, is the first surrogate-fidelity number on an",
        "# HEA slab in this tree. Fixed geometry: no DFT minimum, no relaxation correction is claimed.",
        "#",
        "# READOUT (pre-stated, src/dft/hea_panel_readout.py, inherited bands only): per chain,",
        "# dG_OH/dG_O/dG_OOH and eta from the DFT energies with the banked gas references",
        "# runs/Cr_slab/H2O.out and runs/Cr_slab/H2.out (same O/H UPF, 80/640 Ry, Martyna-Tuckerman",
        "# 12 A box) and the referencing of src/hea_oer/referencing.py; primary = |eta_DFT - eta_MACE|",
        "# <= the MACE-MPA-0 single-point eta MAE of docs/33-r3-mlip-evaluation.md:65 (0.164 V, the",
        "# like-for-like single-point row), with the relaxed-pipeline validation MAE of",
        "# results/r4_validate.json (mae_eta, docs/36:16) printed beside it as the second column;",
        "# reported WITHIN/OUTSIDE per chain and per projector; per-step |dG_DFT - dG_MACE| against",
        "# 0.250 eV (docs/33:65); rank order of eta_DFT vs eta_MACE across the chains present.",
        "# A chain whose OOH record is DESORBED (census `desorbed` carries 'OOH'; INTEGRITY below) has",
        "# no *OOH state: its third-state energy is printed as dE(O2(g)-in-cell + H_slab) with NO",
        "# 0.40 eV *OOH correction, its AEM eta is UNDEFINED and is not scored against the band, and",
        "# only the bridge-pathway lower bound max(dG1, dG2, dE3) - 1.23 V is printed with the fourth",
        "# step (OH_b -> O_b + H+ + e-, O2 release) marked UNMEASURED (Svane & Rossmeisl 2022;",
        "# src/hea_oer/site_integrity.py:15,404-409). The census eta of such a chain is kept visible",
        "# and labelled as AEM bookkeeping on a non-*OOH state. A leg is terminal as CONVERGED, NOT",
        "# CONVERGED or KILLED (<job>.KILLED sidecar), PENDING otherwise.",
        "# Nothing elective. No banked value moves in any branch.",
        "#",
        "# MACE reference energies (eV) per chain, copied from the census record (energies_eV):",
    ]
    for c in chains:
        e = c["energies"]
        cs = c["composition_stats"]
        L.append(f"#   {c['formula']} seed {c['seed']} site {c['site']} (candidate {c['candidate_id'][:12]}..., {c['census'].relative_to(REPO).as_posix()})")
        L.append(f"#     slab {e['slab']!r}  OH {e['OH']!r}  O {e['O']!r}  OOH {e['OOH']!r}")
        L.append(f"#     H2O {e['H2O']!r}  H2 {e['H2']!r}  (12 A box, model gas references)")
        L.append(f"#     dG_OH {c['dG']['OH']!r}  dG_O {c['dG']['O']!r}  dG_OOH {c['dG']['OOH']!r}  eta {c['eta']!r} V  pls {c['pls']}  desorbed {c['desorbed']}")
        L.append(f"#     initial binding metal {c['initial_metal']} (index {c['initial_index']}); final binding metal OH/O/OOH {c['final_metals']['OH']}/{c['final_metals']['O']}/{c['final_metals']['OOH']}; site-evidence status {c['site_evidence']}")
        L.append(f"#     census statistic: n_sites {cs['n_sites']}, n_decorations {cs['n_decorations']}, eta_min {cs['eta_min']!r} (the chain IS the census's single site)")
        for st in STATES:
            L.append(f"#     INTEGRITY {st:4s} {hg.summary(c['integrity'][st])}")
    L += [
        "#",
        f"# k-mesh {' / '.join(f'{m[0]} {m[1]} {m[2]} 0 0 0' for m in sorted(meshes))} from the k-mesh rule on the actual cell (nosym+noinv);",
        f"# nk = {' / '.join(str(n) for n in sorted(nks))}, the largest divisor of {NP} not above the k-point count.",
        "#",
    ]
    if reused:
        L.append("# REUSED (no row here; the readout reads the panel output): chain  job  ->  panel deck  md5")
        for r in reused:
            L.append(f"#   {r['tag']:32s} {r['job']:14s} -> {r['reuse']}.in  {r['md5']}  (render identical except prefix, asserted at build)")
        L.append("#")
    L += [
        f"# PLANNING COST (src/dft/hea_cost_model.py, runs/hea/COST_MODEL.md): {plan:.1f} core-h for the",
        f"# {len(run)} SCFs at the model-A envelope ({cm.PLANNING_ITERS} iterations, ortho x {cm.ORTHO_WALL_RATIO:.4f}), floor {floor:.1f},",
        f"# ceiling {ceil:.1f} core-h ({cm.CEILING_FACTOR:.0f}x, {int(cm.CEILING_FACTOR * cm.PLANNING_ITERS)} iterations); memory envelope {ram:.0f} GB total at",
        f"# 128 ranks (core-bound billing). The 48 h walltime cap the submitter prints is",
        f"# {len(run) * NP * 48} SU and is a cap, not a forecast. Realised cost is reported.",
        "#",
        f"# SUBMIT WITH EXCLUDE={EXCLUDE}",
        f"# NP={NP} NCONC=1",
        "#",
        "# NOT LICENSED FOR SUBMISSION. This arm has no dated registration line.",
        "# docs/92-hea-dft-panel-DRAFT.md is a PROPOSAL with blank entrant slots HEA-1 .. HEA-9",
        "# (U set, projectors, spin start, kill rule, pairs, acceptor control, cost, pilot scope,",
        "# eta bar); anvil/47_submit_a0.sh refuses this manifest while this notice stands",
        "# (docs/66 section 4). When licensed, replace this paragraph with the dated adoption line,",
        "# and leave every deck md5 below unchanged.",
        "#",
        "# md5 of each deck, for the record (chain  job  nat  md5):",
    ]
    for r in run:
        L.append(f"#   {r['tag']:32s} {r['job']:14s} {r['info']['nat']:3d}  {r['md5']}")
    L += ["#", "# Runnable rows are: dir job suffix nk"]
    for r in run:
        L.append(f"{rel}/{r['tag']} {r['job']} .in {r['info']['nk']}")
    text = "\n".join(L) + "\n"
    check_manifest_text(text, expect_not_licensed=True)
    return text


def _under_runs(path: Path) -> Path:
    path = Path(path).resolve()
    try:
        path.relative_to(RUNS.resolve())
    except ValueError:
        raise BuildError(f"--out-root {path} is not under {RUNS} (manifest rows are relative to $RUNS); nothing written")
    return path


def run(specs: list, out_root: Path, manifest: Path, states, check_only: bool, verify: Path | None) -> list:
    out_root = _under_runs(out_root)
    template = load_template()
    chains, rows = [], []
    for sp in specs:
        census = Path(sp["census"])
        if verify:
            ver = load_json(verify)["artifact_sha256_lf"]
            key = census.name
            if key not in ver or sha256_lf(census) != ver[key]:
                raise BuildError(f"{census}: sha256 does not match {verify}")
        chain = find_chain(census, sp["formula"], int(sp["seed"]), int(sp["site"]))
        chain["reuse"] = dict(sp.get("reuse") or {})
        for st in chain["reuse"]:
            if st not in STATES:
                raise BuildError(f"--reuse names unknown state {st!r}")
        chains.append(chain)
        rows += build_chain(chain, out_root, states, check_only, template)
    text = manifest_text(rows, out_root, chains)
    if check_only:
        if manifest.exists() and manifest.read_bytes() != text.encode("utf-8"):
            raise BuildError(f"{manifest} differs from a fresh render")
        print(f"CHECK ONLY: {sum(1 for r in rows if not r['reuse'])} decks and the manifest verified, nothing written")
    else:
        write_lf(manifest, text)
    for r in rows:
        note = f"REUSED {r['reuse']}" if r["reuse"] else f"plan {r['plan_coreh']:.1f} core-h"
        print(f"{r['tag']:32s} {r['job']:14s} nat {r['info']['nat']:3d} mesh {r['info']['mesh']} kpts {r['info']['nkpts']} nk {r['info']['nk']} md5 {r['md5']} {note}")
    print(f"manifest -> {manifest.relative_to(REPO).as_posix()}  (NOT LICENSED; nothing submitted)")
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--census")
    ap.add_argument("--formula")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--site", type=int)
    ap.add_argument("--states", default="slab,OH,O,OOH")
    ap.add_argument("--out-root", default=str(RUNS / "hea" / "pilot"))
    ap.add_argument("--manifest", default=str(RUNS / "hea" / "m_pilot.txt"))
    ap.add_argument("--verify-sha", default=None, help="verification.json carrying artifact_sha256_lf for the census")
    ap.add_argument("--reuse", action="append", default=[], help="STATE=branch_panel/<label>: read that panel deck instead of building the state")
    ap.add_argument("--retained", action="store_true", help="the two retained chains into runs/hea/pilot_retained/")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    states = tuple(s for s in args.states.split(",") if s)
    if any(s not in STATES for s in states):
        raise BuildError(f"--states must be among {STATES}")
    if args.retained:
        run(list(RETAINED), RETAINED_OUT, RETAINED_MANIFEST, states, args.check, BANK / "verification.json")
        return 0
    if not (args.census and args.formula and args.seed is not None and args.site is not None):
        ap.error("--census, --formula, --seed and --site are required (or --retained)")
    reuse = {}
    for item in args.reuse:
        if "=" not in item:
            raise BuildError(f"--reuse expects STATE=branch_panel/<label>, got {item!r}")
        st, target = item.split("=", 1)
        reuse[st] = target
    spec = dict(census=args.census, formula=args.formula, seed=args.seed, site=args.site, reuse=reuse)
    run([spec], Path(args.out_root), Path(args.manifest), states, args.check,
        Path(args.verify_sha) if args.verify_sha else None)
    return 0


if __name__ == "__main__":
    sys.exit(main())
