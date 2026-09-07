#!/usr/bin/env python3
"""Build the HEA branch-panel decks: fixed-geometry SCFs on the retained rutile(110) HEA OOH
geometries of results/cr_site_chains_2026-09-06/dft_branch_panel.json, each in two projector
variants, into runs/hea/branch_panel/<label>__{atomic,ortho}.in, plus the manifest
runs/hea/m_branch_panel.txt in the A0 format for anvil/47_submit_a0.sh.

Geometries (the four panel states plus the optional proton-acceptor control):

    equiatomic_pull2.10   pair 1 state A  (selected *OOH on Cr16, intact, Cr-O 1.975 A)
    equiatomic_builder    pair 1 state B  (HO2 radical in the cell, nearest metal 3.676 A: desorbed)
    leader_builder        pair 2 state A  (HO2 radical in the cell, nearest metal 4.557 A: desorbed)
    leader_pull2.10       pair 2 state B  (O2 in the cell, O-O 1.230 A, nearest metal 3.400 A, + H on slab O56)
    leader_pull1.70       optional        (O2 in the cell, O-O 1.238 A, nearest metal 3.931 A, + H on slab O68)

Every distance is re-derived at build by src/dft/hea_geometry.py and printed in the manifest
with the anomaly class of each state.

Coordinates are taken from the JSON pointer the panel names (positions_A at full precision),
cross-checked against the sha256-banked extxyz export, and written so that re-parsing the
deck reproduces the source floats exactly (src/dft/hea_deck.py). Settings: the banked 2x1v
namelists (runs/a0/cell/ref__2x1v__u715.in) cloned verbatim except prefix/nat/ntyp/
starting_magnetization/electron_maxstep = 300/max_seconds = 165000; MP U set of record on
the 3d metals, no U on Cu; ferromagnetic starts per species; k-mesh by the k-mesh rule on
the actual cell; nk = the largest divisor of 128 not above the k-point count.

The manifest carries a NOT LICENSED notice: nothing here is submitted.

Usage:  python src/dft/build_hea_panel.py [--check]
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from hea_deck import (BuildError, EXCLUDE, NP, REPO, check_manifest_text, deck_info,  # noqa: E402
                      json_pointer, load_json, load_template, render_deck, sha256_lf, write_lf)
import hea_cost_model as cm  # noqa: E402
import hea_geometry as hg  # noqa: E402

BANK = REPO / "results" / "cr_site_chains_2026-09-06"
PANEL = BANK / "dft_branch_panel.json"
VERIF = BANK / "verification.json"
OUT = REPO / "runs" / "hea" / "branch_panel"
MANIFEST = REPO / "runs" / "hea" / "m_branch_panel.txt"
PROJECTORS = ("atomic", "ortho")


def parse_extxyz(path: Path):
    lines = path.read_text(encoding="utf-8").splitlines()
    n = int(lines[0])
    head = lines[1]
    lat = head.split('Lattice="', 1)[1].split('"', 1)[0].split()
    cell = [[float(x) for x in lat[0:3]], [float(x) for x in lat[3:6]], [float(x) for x in lat[6:9]]]
    syms, pos, fixed = [], [], []
    for i, ln in enumerate(lines[2:2 + n]):
        p = ln.split()
        syms.append(p[0])
        pos.append([float(x) for x in p[1:4]])
        if p[4] == "F":
            fixed.append(i)
    return syms, pos, cell, fixed


def collect_states() -> list:
    """The five geometries, each verified against verification.json."""
    panel = load_json(PANEL)
    ver = load_json(VERIF)["artifact_sha256_lf"]
    if sha256_lf(PANEL) != ver["dft_branch_panel.json"]:
        raise BuildError("dft_branch_panel.json does not match its banked sha256")
    states = []
    for pair in panel["pairs"]:
        for role, st in zip(("A", "B"), pair["states"]):
            states.append(dict(arm=pair["arm"], start=st["start"], source_json=st["source_json"],
                               pointer=st["geometry_pointer"], extxyz=st["extxyz"],
                               sha=st["sha256_lf"], role=f"pair {pair['arm']} state {role}",
                               mace_pair_dE=pair["MACE_E_B_minus_E_A_eV"]))
    for opt in panel.get("optional", []):
        ext = f"ooh_readout/{opt['arm']}_{opt['start']}.extxyz"
        states.append(dict(arm=opt["arm"], start=opt["start"], source_json=opt["source_json"],
                           pointer=opt["geometry_pointer"], extxyz=ext, sha=ver[ext],
                           role="optional proton-acceptor control", mace_pair_dE=opt["MACE_E_O68_minus_E_O56_eV"]))
    for s in states:
        src = BANK / s["source_json"]
        if sha256_lf(src) != ver[s["source_json"]]:
            raise BuildError(f"{src} does not match its banked sha256")
        if sha256_lf(BANK / s["extxyz"]) != s["sha"] or ver[s["extxyz"]] != s["sha"]:
            raise BuildError(f"{s['extxyz']}: sha256 mismatch against the panel/verification record")
        doc = load_json(src)
        g = json_pointer(doc, s["pointer"])
        att = json_pointer(doc, s["pointer"].rsplit("/", 1)[0])
        s["geometry"] = g
        s["mace_E"] = att["energy_eV"]
        s["label"] = f"{s['arm']}_{s['start']}"
        s["integrity"] = hg.analyse(g["symbols"], g["positions_A"], g["cell_A"])
        # cross-check the JSON geometry against the sha-banked extxyz (8-decimal export)
        syms, pos, cell, fixed = parse_extxyz(BANK / s["extxyz"])
        if syms != g["symbols"] or fixed != sorted(g["fixed_atom_indices"]):
            raise BuildError(f"{s['label']}: extxyz symbols/constraints differ from the JSON geometry")
        if any(abs(a - b) > 5e-9 for pa, pb in zip(pos, g["positions_A"]) for a, b in zip(pa, pb)):
            raise BuildError(f"{s['label']}: extxyz positions differ from the JSON geometry beyond 8 decimals")
        if any(float(a) != float(b) for ra, rb in zip(cell, g["cell_A"]) for a, b in zip(ra, rb)):
            raise BuildError(f"{s['label']}: extxyz lattice differs from the JSON cell")
        if g["pbc"] != [True, True, True] or g.get("other_constraint_types"):
            raise BuildError(f"{s['label']}: unexpected pbc/constraints")
    return states


def build(check_only: bool = False) -> list:
    template = load_template()
    states = collect_states()
    rows = []
    for s in states:
        g = s["geometry"]
        for proj in PROJECTORS:
            job = f"{s['label']}__{proj}"
            text = render_deck(job, g["symbols"], g["positions_A"], g["cell_A"], g["fixed_atom_indices"], proj, template)
            info = deck_info(text)
            if info["nat"] != len(g["symbols"]) or info["counts"] != dict(Counter(g["symbols"])):
                raise BuildError(f"{job}: atom or species count mismatch")
            dst = OUT / f"{job}.in"
            if check_only:
                if dst.exists() and dst.read_bytes() != text.encode("utf-8"):
                    raise BuildError(f"{dst} differs from a fresh render")
                h = __import__("hashlib").md5(text.encode("utf-8")).hexdigest()
            else:
                h = write_lf(dst, text)
            cost = cm.per_scf(info["counts"], info["cell"], info["nkpts"], info["nk"])
            rows.append(dict(state=s, job=job, projector=proj, md5=h, info=info,
                             plan_coreh=cost[proj]["plan_coreh"], floor_coreh=cost[proj]["floor_coreh"],
                             ceiling_coreh=cost[proj]["ceiling_coreh"], ram_total_GB=cost["ram_total_GB_envelope"]))
    return rows


def manifest_text(rows: list) -> str:
    panel = load_json(PANEL)
    p1, p2 = panel["pairs"]
    opt = panel["optional"][0]
    nk = {r["info"]["nk"] for r in rows}
    mesh = {r["info"]["mesh"] for r in rows}
    if len(nk) != 1 or len(mesh) != 1:
        raise BuildError("panel decks do not share one k-mesh/nk")
    nk = nk.pop()
    mesh = mesh.pop()
    plan = sum(r["plan_coreh"] for r in rows)
    floor = sum(r["floor_coreh"] for r in rows)
    ceil = sum(r["ceiling_coreh"] for r in rows)
    ram = max(r["ram_total_GB"] for r in rows)
    L = [
        "# HEA branch-panel manifest -- fixed-geometry SCFs on the five retained rutile(110) HEA",
        "# OOH geometries of results/cr_site_chains_2026-09-06/dft_branch_panel.json, each in",
        "# HUBBARD (atomic) and HUBBARD (ortho-atomic). Built by src/dft/build_hea_panel.py; every",
        "# deck's coordinates re-parse to the retained positions_A exactly (asserted at build).",
        "#",
        "# WHY. The retained MACE chains place a detached OOH within 31 meV of the metal-contacted",
        "# OOH on the equiatomic Cr site, and 2.28 eV BELOW the detached OOH an OO fragment with H",
        "# transferred to slab O56 on the leader Cr site. No DFT number exists on any HEA slab in",
        "# this tree (every QE run is a single-metal endmember). These ten SCFs put a DFT electronic",
        "# energy on each retained geometry so the branch gaps can be read beside the model's.",
        "#",
        "# READOUT (pre-stated, src/dft/hea_panel_readout.py, inherited bands only): per pair,",
        "# dE_DFT = E(state B) - E(state A) beside dE_MACE; band = |dE_DFT - dE_MACE| <= 0.250 eV,",
        "# the MACE-MPA-0 single-point 15-point dG MAE of docs/33-r3-mlip-evaluation.md:65, reported",
        "# WITHIN/OUTSIDE; the sign of dE_DFT is SCORED against the sign of dE_MACE only when",
        "# |dE_MACE| > 0.250 eV (pair 2, optional control) and printed UNSCORED otherwise (pair 1:",
        "# |dE_MACE| = 0.031 eV lies inside the band, so a sign test there is degenerate); projector",
        "# agreement per pair. A leg is terminal as CONVERGED (energy + JOB DONE), NOT CONVERGED",
        "# (`convergence NOT achieved`, no number) or KILLED (a <job>.KILLED sidecar written by the",
        "# kill rule, no number); PENDING otherwise. The total magnetisation is printed per leg and,",
        "# for the desorbed states listed under INTEGRITY, the Loewdin moment on the adsorbate atoms",
        "# is read from <job>.lowdin.txt beside the free-species moment; a mismatch of 0.5 Bohr mag or",
        "# more, or a missing Loewdin table, prints SPIN-STATE UNRESOLVED on that leg.",
        "# Nothing elective. No banked value moves in any branch.",
        "#",
        "# INTEGRITY (minimum-image distances in A on the retained cell, src/dft/hea_geometry.py;",
        "# thresholds of results/cr_site_chains_2026-09-06/paired_readout/readout.json:269-277;",
        "# h = height above the topmost slab metal):",
    ]
    seen_int = set()
    for r in rows:
        s = r["state"]
        if s["label"] in seen_int:
            continue
        seen_int.add(s["label"])
        L.append(f"#   {s['label']:22s} {hg.summary(s['integrity'])}")
    L += [
        "#",
        "# MACE reference energies (eV), copied from the replay records the panel points to:",
    ]
    seen = set()
    for r in rows:
        s = r["state"]
        if s["label"] in seen:
            continue
        seen.add(s["label"])
        L.append(f"#   {s['label']:22s} {s['mace_E']!r:22s} results/cr_site_chains_2026-09-06/{s['source_json']} {s['pointer'].rsplit('/', 1)[0]}/energy_eV  ({s['role']})")
    L += [
        f"#   pair equiatomic  MACE_E_B_minus_E_A_eV = {p1['MACE_E_B_minus_E_A_eV']!r}  (states [{p1['states'][0]['start']}, {p1['states'][1]['start']}])",
        f"#   pair leader      MACE_E_B_minus_E_A_eV = {p2['MACE_E_B_minus_E_A_eV']!r}  (states [{p2['states'][0]['start']}, {p2['states'][1]['start']}])",
        f"#   optional         MACE_E_O68_minus_E_O56_eV = {opt['MACE_E_O68_minus_E_O56_eV']!r}  (leader pull1.70 - leader pull2.10)",
        "#   (dft_branch_panel.json:8-63; sha256_lf of the panel and every source verified at build)",
        "#",
        f"# k-mesh {mesh[0]} {mesh[1]} {mesh[2]} 0 0 0 from the k-mesh rule on the actual cell (nosym+noinv -> {mesh[0] * mesh[1] * mesh[2]} k-points);",
        f"# nk = {nk} is the largest divisor of {NP} not above that count.",
        "#",
        f"# PLANNING COST (src/dft/hea_cost_model.py, runs/hea/COST_MODEL.md): {plan:.1f} core-h for the",
        f"# ten SCFs at the model-A envelope ({cm.PLANNING_ITERS} iterations, ortho x {cm.ORTHO_WALL_RATIO:.4f}), floor {floor:.1f},",
        f"# ceiling {ceil:.1f} core-h ({cm.CEILING_FACTOR:.0f}x, {int(cm.CEILING_FACTOR * cm.PLANNING_ITERS)} iterations); memory envelope {ram:.0f} GB total at",
        f"# 128 ranks (core-bound billing). The 48 h walltime cap the submitter prints is",
        f"# {len(rows) * NP * 48} SU and is a cap, not a forecast. Realised cost is reported.",
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
        "# md5 of each deck, for the record (job  projector  nat  md5):",
    ]
    for r in rows:
        L.append(f"#   {r['job']:34s} {r['projector']:7s} {r['info']['nat']:3d}  {r['md5']}")
    L += ["#", "# Runnable rows are: dir job suffix nk"]
    for r in rows:
        L.append(f"hea/branch_panel {r['job']} .in {r['info']['nk']}")
    text = "\n".join(L) + "\n"
    check_manifest_text(text, expect_not_licensed=True)
    return text


def main(argv=None) -> int:
    check_only = "--check" in (argv or sys.argv[1:])
    rows = build(check_only)
    text = manifest_text(rows)
    if check_only:
        if MANIFEST.exists() and MANIFEST.read_bytes() != text.encode("utf-8"):
            raise BuildError(f"{MANIFEST} differs from a fresh render")
        print(f"CHECK ONLY: {len(rows)} decks and the manifest verified, nothing written")
    else:
        write_lf(MANIFEST, text)
    for r in rows:
        print(f"{r['job']:34s} nat {r['info']['nat']:3d} mesh {r['info']['mesh']} kpts {r['info']['nkpts']} nk {r['info']['nk']} md5 {r['md5']} plan {r['plan_coreh']:.1f} core-h")
    print(f"manifest -> {MANIFEST.relative_to(REPO).as_posix()}  (NOT LICENSED; nothing submitted)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
