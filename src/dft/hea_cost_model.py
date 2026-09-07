#!/usr/bin/env python3
"""Cost model for the HEA fixed-geometry SCF arms: an extrapolation from banked pw.x size
descriptors to the nat 72-75 rutile(110) HEA cells, documented input by input.

Every banked number below is copied from a file in this tree (path:line beside it). The
model is calibrated on three banked np = 128 SCFs and printed with its residual on each so
the reader can see how far the extrapolation reaches beyond them. The planning figure is
the ENVELOPE model (model A); the best-fit model (model B) is printed as the floor; the
ceiling is 3x the planning figure, on the precedent of the 5.8x cost miss of the CrO2 q333
pair (docs/43-prereg-week1-factorial.md:4453-4456).

The SCF iteration count is the dominant uncertainty and is taken from a survey of every
banked nspin = 2 slab output in runs/ (first SCF of each file): the planning count is the
90th percentile of the local-TF / beta 0.3 subset, the ceiling is 3x that, and the fraction
of banked SCFs above each count is printed beside them.

Usage:  python src/dft/hea_cost_model.py [--write runs/hea/COST_MODEL.md] [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
COST_MD = REPO / "runs" / "hea" / "COST_MODEL.md"
BANK = REPO / "results" / "cr_site_chains_2026-09-06"

NP = 128                      # anvil/46_a0.slurm:46 (NP default 128)
NODE_GB = 237.0               # anvil/logs/a0_20419733_1.out:17 and a0_20419733_2.out:17 ('Memory Efficiency: 0.00% of 237.00 GB (1.85 GB/core)')
BILL_GB_PER_SU = 2.0          # anvil/README.md:91: `shared` bills max(cores, ceil(mem_GB/2)) SU per hour
CEILING_FACTOR = 3.0          # docs/43:4453-4456 (q333 pair 317.4 core-h vs ~55 planned, 5.8x)
PLANNING_ITERS = 42           # p90 of the banked local-TF / beta 0.3 nspin = 2 slab first-SCF survey (iteration_survey(); n = 564 at build)
ECUTWFC_RY = 80.0             # runs/a0/cell/ref__2x1v__u715.in:15

# UPF valences of record, read from the 'atomic species   valence' tables of banked outputs.
VALENCE = {
    "Cr": (14.0, "runs/a0/cell/ref__2x1v__u715.out:114"),
    "Mn": (15.0, "runs/Mn_slab/s0_OH.out:127"),
    "Fe": (16.0, "runs/Fe_slab/s0_OOH.out:128"),
    "Co": (17.0, "runs/Co_slab/s0_OH.out:126"),
    "Ni": (18.0, "runs/Ni_slab/s0_OH.out:127"),
    "Cu": (11.0, "runs/Cu_slab/s0_OH.out:121"),
    "O":  (6.0,  "runs/a0/cell/ref__2x1v__u715.out:115"),
    "H":  (1.0,  "runs/a0/p_proj/s0_OH__u715_atomic.out:125"),
}

# Banked size descriptors, np = 128, one SCF each.
BANKED = {
    "ref__2x1v__u715 (atomic)": dict(
        out="runs/a0/cell/ref__2x1v__u715.out",
        nat=36, nelec=312.0, nbnd=187, kpts=16, npool=8, V_bohr3=6153.8249, npw=84555,
        ngdense=1682519, ram_proc_MB=303.54, ram_tot_GB=32.33, wall_s=8 * 60 + 42.67, iters=22,
        lines="nat :51, nelec :53, nbnd :54, V :50, kpts :166, PW/G :42, RAM :189/:191, iters :2647, WALL :2747",
    ),
    "s0_OOH__2x1v_escape__u715 (atomic)": dict(
        out="runs/a0/cell/s0_OOH__2x1v_escape__u715.out",
        nat=39, nelec=325.0, nbnd=196, kpts=10, npool=8, V_bohr3=6153.8249, npw=84555,
        ngdense=1682519, ram_proc_MB=299.19, ram_tot_GB=31.78, wall_s=6 * 60 + 29.41, iters=26,
        lines="nelec :51, nbnd :52, V :48, kpts :180, G :193, RAM :197/:199, iters :2412, WALL :2515",
    ),
    "s0_OH__u715_atomic (1x1, atomic)": dict(
        out="runs/a0/p_proj/s0_OH__u715_atomic.out",
        nat=20, nelec=163.0, nbnd=98, kpts=15, npool=4, V_bohr3=3076.9124, npw=None,
        ngdense=841263, ram_proc_MB=79.14, ram_tot_GB=8.69, wall_s=3 * 60 + 5.39, iters=30,
        lines="nelec :52, nbnd :53, V :49, kpts :162, G :180, RAM :184/:186, iters :1762, WALL :1846",
    ),
}
ORTHO_TWIN = dict(out="runs/a0/pproj_cell/s0_OOH__2x1v_escape__u715_ortho.out",
                  wall_s=7 * 60 + 53.78, iters=27, lines="iters :2426, WALL :2530")
REF = "ref__2x1v__u715 (atomic)"

#: ortho/atomic WALL ratio of record for planning: the 2x1v OOH twin pair (the only ortho
#: measurement on the adopted cell class; both legs np = 128).
ORTHO_WALL_RATIO = ORTHO_TWIN["wall_s"] / BANKED["s0_OOH__2x1v_escape__u715 (atomic)"]["wall_s"]

#: Per-state ortho/atomic WALL pairs on the 1x1 cell (the aggregate 1.1834 of
#: src/dft/build_pproj_cell.py:78 is formed from these four); WALL seconds and path:line.
ONE_BY_ONE_PAIRS = {
    "slab": (3 * 60 + 43.05, 4 * 60 + 52.85, "runs/a0/p_proj/slab__u715_atomic.out:2332", "runs/a0/p_proj/slab__u715_ortho.out:2376"),
    "O":    (12 * 60 + 2.24, 13 * 60 + 2.18, "runs/s0/e_proj/s0_O__u715_atomic.out:1758 (np = 20)", "runs/s0/e_proj/s0_O__u715_ortho.out:1788 (np = 20)"),
    "OH":   (3 * 60 + 5.39, 4 * 60 + 58.33, "runs/a0/p_proj/s0_OH__u715_atomic.out:1846", "runs/a0/p_proj/s0_OH__u715_ortho.out:2112"),
    "OOH":  (2 * 60 + 32.86, 2 * 60 + 25.62, "runs/a0/p_proj/s0_OOH__u715_atomic.out:1851", "runs/a0/p_proj/s0_OOH__u715_ortho.out:1880"),
}

BOHR_A = 0.529177210903
RY_EV = 13.605693122


def nint(x: float) -> int:
    """Fortran NINT: round half away from zero."""
    return int(math.floor(abs(x) + 0.5)) * (1 if x >= 0 else -1)


def nbnd_rule(nelec: float) -> int:
    """nbnd = NINT(1.2 * NINT(nelec/2)); reproduces all nine banked (nelec, nbnd) pairs listed
    in COST_MODEL.md (312->187, 325->196, 318->191, 319->192, 163->98, 162->97, 181->109,
    168->101, 348->209)."""
    return nint(1.2 * nint(nelec / 2.0))


def nelec_of(counts: dict) -> float:
    return float(sum(VALENCE[s][0] * n for s, n in counts.items()))


def cell_volume_A3(cell) -> float:
    a, b, c = cell
    cx = (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
    return abs(cx[0] * c[0] + cx[1] * c[1] + cx[2] * c[2])


def kloc(kpts: int, npool: int) -> int:
    """LSDA doubles the k-point list; per-pool load is the ceiling of the share."""
    return math.ceil(2 * kpts / npool)


def descriptors(counts: dict, cell, kpts: int, nk: int) -> dict:
    V_A3 = cell_volume_A3(cell)
    V = V_A3 / BOHR_A ** 3
    nelec = nelec_of(counts)
    ref = BANKED[REF]
    return dict(
        nat=sum(counts.values()), nelec=nelec, nbnd=nbnd_rule(nelec), V_A3=V_A3, V_bohr3=V,
        npw=ref["npw"] * V / ref["V_bohr3"], ngdense=ref["ngdense"] * V / ref["V_bohr3"],
        kpts=kpts, npool=nk, kloc=kloc(kpts, nk), ppp=NP // nk,
    )


def factors(d: dict, ref: dict | None = None) -> dict:
    """Scaling factors of d relative to the reference SCF."""
    ref = ref or BANKED[REF]
    fV = d["V_bohr3"] / ref["V_bohr3"]
    fB = d["nbnd"] / ref["nbnd"]
    fK = kloc(d["kpts"], d["npool"]) / kloc(ref["kpts"], ref["npool"])
    fP = (NP // ref["npool"]) / (NP // d["npool"])      # ideal within-pool scaling
    A = fV * fB ** 2 * fK * fP                          # envelope: V x nbnd^2 x k_local
    B = fV * fB * fK * fP                               # best fit: V x nbnd x k_local
    mem_wfc = fV * fB * fK * fP
    mem_dens = fV * fP
    return dict(fV=fV, fB=fB, fK=fK, fP=fP, A=A, B=B, mem=max(mem_wfc, mem_dens),
                mem_wfc=mem_wfc, mem_dens=mem_dens)


def calibration() -> list:
    """Predict each banked point from the reference and print the residual."""
    ref = BANKED[REF]
    t_ref = ref["wall_s"] / ref["iters"]
    rows = []
    for name, b in BANKED.items():
        f = factors(b, ref)
        t_obs = b["wall_s"] / b["iters"]
        rows.append(dict(name=name, out=b["out"], t_iter_obs=t_obs, t_iter_A=t_ref * f["A"],
                         t_iter_B=t_ref * f["B"], ram_obs=b["ram_proc_MB"],
                         ram_pred=ref["ram_proc_MB"] * f["mem"], nbnd_obs=b["nbnd"],
                         nbnd_rule=nbnd_rule(b["nelec"])))
    return rows


def per_scf(counts: dict, cell, kpts: int, nk: int, planning_iters: int = PLANNING_ITERS) -> dict:
    ref = BANKED[REF]
    d = descriptors(counts, cell, kpts, nk)
    f = factors(d, ref)
    t_ref = ref["wall_s"] / ref["iters"]
    tA = t_ref * f["A"]
    tB = t_ref * f["B"]
    plan_wall_s = tA * planning_iters
    floor_wall_s = tB * planning_iters
    plan_coreh = plan_wall_s * NP / 3600.0
    floor_coreh = floor_wall_s * NP / 3600.0
    ram_proc = ref["ram_proc_MB"] * f["mem"]
    ram_tot_env = ram_proc * NP / 1024.0
    ram_tot_scaled = ref["ram_tot_GB"] * f["mem"]
    out = dict(
        descriptors=d, factors=f, t_iter_A_s=tA, t_iter_B_s=tB, planning_iters=planning_iters,
        ceiling_iters=int(round(CEILING_FACTOR * planning_iters)),
        atomic=dict(plan_wall_s=plan_wall_s, plan_coreh=plan_coreh, floor_coreh=floor_coreh,
                    ceiling_coreh=CEILING_FACTOR * plan_coreh),
        ortho=dict(plan_wall_s=plan_wall_s * ORTHO_WALL_RATIO, plan_coreh=plan_coreh * ORTHO_WALL_RATIO,
                   floor_coreh=floor_coreh * ORTHO_WALL_RATIO,
                   ceiling_coreh=CEILING_FACTOR * plan_coreh * ORTHO_WALL_RATIO),
        ram_proc_MB=ram_proc, ram_total_GB_envelope=ram_tot_env, ram_total_GB_scaled=ram_tot_scaled,
        ram_proc_MB_ceiling=CEILING_FACTOR * ram_proc,
        ram_total_GB_ceiling=CEILING_FACTOR * ram_tot_env,
    )
    out["billing"] = billing(ram_tot_env)
    out["billing_ceiling"] = billing(CEILING_FACTOR * ram_tot_env)
    return out


def billing(total_GB: float) -> dict:
    mem_units = math.ceil(total_GB / BILL_GB_PER_SU)
    return dict(total_GB=total_GB, mem_units=mem_units, su_per_h=max(NP, mem_units),
                core_bound=mem_units <= NP, fits_node=total_GB <= NODE_GB)


# --------------------------------------------------------------------------- iteration survey
_RE_NAT = re.compile(r"number of atoms/cell\s*=\s*(\d+)")
_RE_ACH = re.compile(r"convergence has been achieved in\s+(\d+) iterations")
_RE_BETA = re.compile(r"mixing beta\s*=\s*([\d.]+)")
_RE_MODE = re.compile(r"(local-TF|plain|TF)\s+mixing")


def _percentile(sorted_vals: list, p: float):
    """Nearest-rank percentile."""
    if not sorted_vals:
        return None
    return sorted_vals[min(len(sorted_vals) - 1, max(0, int(math.ceil(p * len(sorted_vals))) - 1))]


def iteration_survey(root: Path = REPO / "runs", exclude_dirs=("hea",), min_nat: int = 18) -> dict:
    """First-SCF iteration counts of every banked nspin = 2 pw.x slab output under root.

    A file counts when it is a pw.x output (`Program PWSCF`), has nat >= min_nat and prints a
    magnetisation (nspin = 2). The first `convergence has been achieved` count is the SCF from
    the starting density; files whose first SCF never converged are counted separately.
    """
    root = Path(root)
    rows = []
    for p in root.rglob("*.out"):
        rel = p.relative_to(root).as_posix()
        if any(rel.split("/")[0] == e for e in exclude_dirs):
            continue
        try:
            b = p.read_bytes().decode("utf-8", "replace")
        except OSError:
            continue
        if "Program PWSCF" not in b:
            continue
        m = _RE_NAT.search(b)
        if not m or int(m.group(1)) < min_nat:
            continue
        if "total magnetization" not in b and "Starting magnetic structure" not in b:
            continue
        ach = _RE_ACH.search(b)
        beta = _RE_BETA.search(b)
        mode = _RE_MODE.search(b)
        rows.append(dict(path=rel, nat=int(m.group(1)), first=int(ach.group(1)) if ach else None,
                         not_achieved="convergence NOT achieved" in b,
                         beta=beta.group(1) if beta else None, mode=mode.group(1) if mode else None))
    conv = sorted(r["first"] for r in rows if r["first"] is not None)
    sub = sorted(r["first"] for r in rows if r["first"] is not None and r["mode"] == "local-TF" and r["beta"] == "0.3000")
    big = sorted((r["first"], r["nat"], r["path"]) for r in rows if r["first"] is not None and r["nat"] >= 36)

    def stats(v):
        return dict(n=len(v), min=v[0] if v else None, median=statistics.median(v) if v else None,
                    p75=_percentile(v, 0.75), p90=_percentile(v, 0.90), max=v[-1] if v else None)
    return dict(
        n_files=len(rows), n_converged_first=len(conv), n_not_achieved=sum(1 for r in rows if r["not_achieved"]),
        all=stats(conv), local_tf_beta03=stats(sub), nat_ge_36=big,
        above_planning=sum(1 for c in conv if c > PLANNING_ITERS),
        above_ceiling=sum(1 for c in conv if c > CEILING_FACTOR * PLANNING_ITERS),
    )


# --------------------------------------------------------------------------- arm geometries
def _panel_decks():
    """The five panel geometries (label, counts, cell, source)."""
    from collections import Counter
    panel_path = BANK / "dft_branch_panel.json"
    if not panel_path.exists():
        return []
    panel = json.load(open(panel_path, encoding="utf-8"))
    entries = []
    for pair in panel["pairs"]:
        for st in pair["states"]:
            entries.append((pair["arm"], st["start"], st["source_json"], st["geometry_pointer"]))
    for opt in panel.get("optional", []):
        entries.append((opt["arm"], opt["start"], opt["source_json"], opt["geometry_pointer"]))
    decks = []
    for arm, start, src, ptr in entries:
        doc = json.load(open(BANK / src, encoding="utf-8"))
        g = doc["attempts"][int(ptr.split("/")[2])]["geometry"]
        decks.append(dict(label=f"{arm}_{start}", counts=dict(Counter(g["symbols"])), cell=g["cell_A"],
                          src=f"results/cr_site_chains_2026-09-06/{src} {ptr}"))
    return decks


#: The two retained chains and the panel deck each chain's OOH state duplicates.
RETAINED_CHAINS = (
    dict(census="equiatomic_result.json", formula="Fe25Co25Ni25Cr25", seed=2, site=0, reuse={"OOH": "equiatomic_pull2.10"}),
    dict(census="leader_result.json", formula="Ni31Cr29Cu5Mn35", seed=0, site=0, reuse={"OOH": "leader_pull2.10"}),
)


def _pilot_decks():
    """slab/OH/O/OOH geometries of the two retained chains (label, state, counts, cell, reuse)."""
    from collections import Counter
    decks = []
    for spec in RETAINED_CHAINS:
        path = BANK / spec["census"]
        if not path.exists():
            continue
        doc = json.load(open(path, encoding="utf-8"))
        row = [r for r in doc["results"] if r["formula"] == spec["formula"]][0]["row"]
        dec = [d for d in row["decoration_records"] if d["seed"] == spec["seed"]][0]
        ps = [p for p in row["per_site_records"] if p["seed"] == spec["seed"] and p["site_index"] == spec["site"]][0]
        geoms = {"slab": dec["relaxed_slab"], **{s: ps["relaxed_states"][s] for s in ("OH", "O", "OOH")}}
        tag = f"{spec['formula']}__s{spec['seed']}_site{spec['site']}"
        for st, g in geoms.items():
            decks.append(dict(label=f"{tag}/{st}", tag=tag, state=st, counts=dict(Counter(g["symbols"])), cell=g["cell_A"],
                              reuse=spec["reuse"].get(st)))
    return decks


def arm_totals() -> dict:
    """Per-deck sums for both arms (the figure the manifests print), with the reused OOH rows
    listed but excluded from the pilot total."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from hea_deck import choose_nk, kgrid_from_cell, kpoint_count  # noqa: E402
    out = {}
    for arm, decks in (("panel", _panel_decks()), ("pilot", _pilot_decks())):
        rows, plan = [], dict(n=0, plan=0.0, floor=0.0, ceiling=0.0, ram_max=0.0)
        for dk in decks:
            mesh = kgrid_from_cell(dk["cell"])
            kpts = kpoint_count(mesh)
            nk = choose_nk(kpts)
            r = per_scf(dk["counts"], dk["cell"], kpts, nk)
            for proj in ("atomic", "ortho"):
                row = dict(label=dk["label"], projector=proj, nat=r["descriptors"]["nat"], nelec=r["descriptors"]["nelec"],
                           nbnd=r["descriptors"]["nbnd"], plan=r[proj]["plan_coreh"], floor=r[proj]["floor_coreh"],
                           ceiling=r[proj]["ceiling_coreh"], ram=r["ram_total_GB_envelope"], reuse=dk.get("reuse"))
                rows.append(row)
                if row["reuse"]:
                    continue
                plan["n"] += 1
                plan["plan"] += row["plan"]
                plan["floor"] += row["floor"]
                plan["ceiling"] += row["ceiling"]
                plan["ram_max"] = max(plan["ram_max"], row["ram"])
        plan["walltime_cap_su"] = plan["n"] * NP * 48
        out[arm] = dict(rows=rows, **plan)
    return out


# --------------------------------------------------------------------------- report
def build_report() -> tuple[str, dict]:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from hea_deck import choose_nk, kgrid_from_cell, kpoint_count  # noqa: E402

    lines = []
    L = lines.append
    L("# HEA fixed-geometry SCF cost model")
    L("")
    L("Extrapolation from banked np = 128 pw.x size descriptors to the nat 72-75 rutile(110) HEA cells.")
    L("Every input number is copied from the file cited beside it; every output is computed by")
    L("`src/dft/hea_cost_model.py`, which regenerates this file.")
    L("")
    L("## 1. Inputs of record")
    L("")
    L("| quantity | value | source |")
    L("|---|---|---|")
    L(f"| ranks per job | {NP} | anvil/46_a0.slurm:46 |")
    L(f"| node memory | {NODE_GB} GB | anvil/logs/a0_20419733_1.out:17 and a0_20419733_2.out:17 (`Memory Efficiency: 0.00% of 237.00 GB (1.85 GB/core)`) |")
    L(f"| shared-partition billing | max(cores, ceil(mem_GB/{BILL_GB_PER_SU:.0f})) SU/h | anvil/README.md:91 |")
    L(f"| ortho/atomic WALL ratio, planning | {ORTHO_WALL_RATIO:.4f} | the 2x1v OOH twin: {ORTHO_TWIN['out']} WALL {ORTHO_TWIN['wall_s']:.2f} s (:2530) / runs/a0/cell/s0_OOH__2x1v_escape__u715.out WALL {BANKED['s0_OOH__2x1v_escape__u715 (atomic)']['wall_s']:.2f} s (:2515) |")
    L("| ortho/atomic WALL ratio, 1x1 aggregate | 1.1834 | src/dft/build_pproj_cell.py:78 (four states aggregated; per-state table below) |")
    L(f"| ceiling factor | {CEILING_FACTOR:.0f}x planning | docs/43-prereg-week1-factorial.md:4453-4456 (q333 pair 317.4 core-h against ~55 planned, 5.8x) |")
    L(f"| planning SCF iterations | {PLANNING_ITERS} | p90 of the banked local-TF / beta 0.3 nspin = 2 slab first-SCF survey (section 1b) |")
    L(f"| ceiling SCF iterations | {int(CEILING_FACTOR * PLANNING_ITERS)} | {CEILING_FACTOR:.0f}x planning; the kill count of docs/92 section 7 |")
    L(f"| cutoffs | {ECUTWFC_RY:.0f} / 640 Ry | runs/a0/cell/ref__2x1v__u715.in:15-16 |")
    L("| non-convergence precedent | Ru nspin = 2 ladder: 5,216.7 SU for 0 of 16 converged | docs/76-projector-generalization-decision-2026-09-03.md:214 |")
    L("")
    L("Per-state ortho/atomic WALL ratios on the 1x1 cell (the aggregate 1.1834 is formed from these; the OOH state is the LOWEST of the four, the OH state the highest):")
    L("")
    L("| state | atomic WALL (s) | ortho WALL (s) | ratio | sources |")
    L("|---|---|---|---|---|")
    for st, (ta, to, sa, so) in ONE_BY_ONE_PAIRS.items():
        L(f"| {st} | {ta:.2f} | {to:.2f} | {to / ta:.3f} | {sa}; {so} |")
    L("")
    L("UPF valences (electrons per atom), from the `atomic species   valence` table of a banked output:")
    L("")
    L("| species | valence | source |")
    L("|---|---|---|")
    for sp, (z, src) in VALENCE.items():
        L(f"| {sp} | {z:.0f} | {src} |")
    L("")
    L("Banked calibration SCFs (np = 128):")
    L("")
    L("| SCF | nat | electrons | KS states | k-points | npool | V (bohr^3) | RAM/proc (MB) | RAM total (GB) | WALL (s) | iterations | lines |")
    L("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for name, b in BANKED.items():
        L(f"| {name} | {b['nat']} | {b['nelec']:.0f} | {b['nbnd']} | {b['kpts']} | {b['npool']} | {b['V_bohr3']} | {b['ram_proc_MB']} | {b['ram_tot_GB']} | {b['wall_s']:.2f} | {b['iters']} | {b['out']} ({b['lines']}) |")
    L(f"| {ORTHO_TWIN['out']} (ortho twin of the nat 39 row) | 39 | 325 | 196 | 10 | 8 | 6153.8249 | 299.19 | 31.78 | {ORTHO_TWIN['wall_s']:.2f} | {ORTHO_TWIN['iters']} | {ORTHO_TWIN['lines']} |")
    L("")
    L(f"Plane waves per k-point at the reference: {BANKED[REF]['npw']} (runs/a0/cell/ref__2x1v__u715.out:42, third G-vector column); dense G-vectors {BANKED[REF]['ngdense']} (:42 / :185). Both scale with cell volume at fixed cutoff.")
    L("")
    L("## 1b. SCF iteration survey of the banked nspin = 2 slab outputs")
    L("")
    sv = iteration_survey()
    L(f"Every pw.x output under runs/ (runs/hea excluded) with nat >= 18 and a printed magnetisation: {sv['n_files']} files; first SCF converged in {sv['n_converged_first']} of them, and {sv['n_not_achieved']} files carry `convergence NOT achieved`. Nearest-rank percentiles of the first-SCF iteration count:")
    L("")
    L("| subset | n | min | median | p75 | p90 | max |")
    L("|---|---|---|---|---|---|---|")
    for key, name in (("all", "all nspin = 2 slab outputs"), ("local_tf_beta03", "local-TF, mixing_beta 0.3 (the setting of every deck here)")):
        s = sv[key]
        L(f"| {name} | {s['n']} | {s['min']} | {s['median']} | {s['p75']} | {s['p90']} | {s['max']} |")
    L("")
    L(f"Banked first SCFs above the planning count ({PLANNING_ITERS}): {sv['above_planning']} of {sv['n_converged_first']}; above the ceiling count ({int(CEILING_FACTOR * PLANNING_ITERS)}): {sv['above_ceiling']} of {sv['n_converged_first']}; never converged: {sv['n_not_achieved']} of {sv['n_files']}. The three calibration points (22, 26, 30 iterations) sit at or below the median; the largest banked cells (nat >= 36) show:")
    L("")
    L("| first-SCF iterations | nat | output |")
    L("|---|---|---|")
    for it, nat, path in sv["nat_ge_36"][-8:]:
        L(f"| {it} | {nat} | runs/{path} |")
    L("")
    live_p90 = sv["local_tf_beta03"]["p90"]
    L(f"PLANNING_ITERS is fixed at {PLANNING_ITERS} in the source; the survey's live p90 is {live_p90}{' (equal)' if live_p90 == PLANNING_ITERS else ' (DIFFERS: the constant is stale)'}. No banked SCF is a five-3d-species disordered slab; the survey bounds the single-metal precedent, not this arm.")
    L("")
    L("## 2. The model")
    L("")
    L("With the reference SCF `ref__2x1v__u715` as the anchor, for a target cell:")
    L("")
    L("- electrons = sum of UPF valences; KS states by the pw.x rule `nbnd = NINT(1.2 * NINT(nelec/2))`, which reproduces every banked pair checked (312->187, 325->196, 318->191, 319->192, 163->98, 162->97, 181->109, 168->101, 348->209; runs/a0/cell/*.out, runs/a0/p_proj/s0_OH__u715_atomic.out:52-53, runs/a0/main/Mn/slab__u750.out, runs/a0/main/Fe/s0_OOH__u750.out, runs/a0/main/Ru/slab__u000.out, runs/s3/Co/ref__2x1v__g1.out);")
    L("- k-points = full mesh of the k-mesh rule (nosym + noinv); LSDA doubles the list; per-pool load k_local = ceil(2 k / npool);")
    L("- f_V = V / V_ref, f_B = nbnd / nbnd_ref, f_K = k_local / k_local_ref, f_P = (ranks per pool)_ref / (ranks per pool);")
    L("- **model A (envelope, planning):** wall per SCF iteration = t_ref x f_V x f_B^2 x f_K x f_P (subspace/orthogonalisation-dominated);")
    L("- **model B (floor):** wall per SCF iteration = t_ref x f_V x f_B x f_K x f_P (FFT-dominated);")
    L(f"- per-SCF wall = per-iteration wall x {PLANNING_ITERS} iterations; core-h = wall x {NP} / 3600; ortho = atomic x {ORTHO_WALL_RATIO:.4f}; ceiling = {CEILING_FACTOR:.0f} x planning (= {int(CEILING_FACTOR * PLANNING_ITERS)} iterations at the model-A rate);")
    L("- memory per process = m_ref x max(f_V f_B f_K f_P, f_V f_P) (the wavefunction-dominated and density-dominated limits); total = per-process x 128 (envelope) and m_tot_ref x the same factor (scaled).")
    L("")
    L("Calibration of the model on the three banked points (prediction from the reference; residual = predicted / observed):")
    L("")
    L("| SCF | t/iter observed (s) | model A (s) | A/obs | model B (s) | B/obs | RAM/proc observed (MB) | RAM/proc model (MB) | model/obs | nbnd rule |")
    L("|---|---|---|---|---|---|---|---|---|---|")
    for r in calibration():
        L(f"| {r['name']} | {r['t_iter_obs']:.2f} | {r['t_iter_A']:.2f} | {r['t_iter_A'] / r['t_iter_obs']:.2f} | {r['t_iter_B']:.2f} | {r['t_iter_B'] / r['t_iter_obs']:.2f} | {r['ram_obs']:.2f} | {r['ram_pred']:.2f} | {r['ram_pred'] / r['ram_obs']:.2f} | {r['nbnd_rule']} vs {r['nbnd_obs']} |")
    L("")
    L("Model A under-predicts the 1x1 point (0.53, through f_P = 0.5: ideal within-pool scaling to 32 ranks is not realised on a 1x1 cell) and over-predicts the nat 39 point (1.31); model B fits both within 25 %. For the HEA cells f_P = 1 (nk = 8, as the reference), so the two models differ only through the extra factor f_B = 2.2, and model A is kept as the planning envelope on the cost-miss precedent; model B is the floor.")
    L("")
    L("## 3. Extrapolation to the retained 75-atom HEA cells")
    L("")
    results = {}
    reps = [dk for dk in _panel_decks() if dk["label"] in ("equiatomic_pull2.10", "leader_pull2.10")]
    for dk in reps:
        mesh = kgrid_from_cell(dk["cell"])
        kpts = kpoint_count(mesh)
        nk = choose_nk(kpts)
        r = per_scf(dk["counts"], dk["cell"], kpts, nk)
        results[dk["label"]] = dict(src=dk["src"], counts=dk["counts"], mesh=mesh, kpts=kpts, nk=nk, **r)
        d, f = r["descriptors"], r["factors"]
        L(f"### {dk['label']} (75-atom OOH cell)")
        L("")
        L(f"Source geometry: `{dk['src']}`; composition {json.dumps(dk['counts'])}; cell volume {d['V_A3']:.4f} A^3 = {d['V_bohr3']:.2f} bohr^3; k-mesh {mesh[0]} {mesh[1]} {mesh[2]} -> {kpts} k-points (full mesh), nk = {nk}, ranks per pool {d['ppp']}, k_local {d['kloc']} (LSDA).")
        L("")
        L("| descriptor | value |")
        L("|---|---|")
        L(f"| electrons | {d['nelec']:.0f} |")
        L(f"| KS states (rule) | {d['nbnd']} |")
        L(f"| plane waves per k-point (V-scaled) | {d['npw']:.0f} |")
        L(f"| dense G-vectors (V-scaled) | {d['ngdense']:.0f} |")
        L(f"| f_V, f_B, f_K, f_P | {f['fV']:.4f}, {f['fB']:.4f}, {f['fK']:.4f}, {f['fP']:.4f} |")
        L(f"| per-iteration wall, model A / B (s) | {r['t_iter_A_s']:.2f} / {r['t_iter_B_s']:.2f} |")
        L(f"| **atomic, per SCF: planning / floor / ceiling (core-h)** | **{r['atomic']['plan_coreh']:.1f} / {r['atomic']['floor_coreh']:.1f} / {r['atomic']['ceiling_coreh']:.1f}** (planning wall {r['atomic']['plan_wall_s'] / 3600:.2f} h at {PLANNING_ITERS} iterations) |")
        L(f"| **ortho, per SCF: planning / floor / ceiling (core-h)** | **{r['ortho']['plan_coreh']:.1f} / {r['ortho']['floor_coreh']:.1f} / {r['ortho']['ceiling_coreh']:.1f}** (planning wall {r['ortho']['plan_wall_s'] / 3600:.2f} h) |")
        L(f"| memory per process, planning / ceiling (MB) | {r['ram_proc_MB']:.1f} / {r['ram_proc_MB_ceiling']:.1f} |")
        L(f"| memory total at np = 128, envelope / scaled / ceiling (GB) | {r['ram_total_GB_envelope']:.1f} / {r['ram_total_GB_scaled']:.1f} / {r['ram_total_GB_ceiling']:.1f} |")
        b, bc = r["billing"], r["billing_ceiling"]
        L(f"| billing at planning memory | max({NP}, ceil({b['total_GB']:.1f}/2) = {b['mem_units']}) = {b['su_per_h']} SU/h, {'core-bound' if b['core_bound'] else 'MEMORY-bound'}, {'fits' if b['fits_node'] else 'EXCEEDS'} the {NODE_GB:.0f} GB node |")
        L(f"| billing at ceiling memory | max({NP}, ceil({bc['total_GB']:.1f}/2) = {bc['mem_units']}) = {bc['su_per_h']} SU/h, {'core-bound' if bc['core_bound'] else 'MEMORY-bound'}, {'fits' if bc['fits_node'] else 'EXCEEDS'} the {NODE_GB:.0f} GB node |")
        L("")
    L("## 4. Arm totals (per-deck sums; the figure each manifest prints)")
    L("")
    tot = arm_totals()
    results["_totals"] = {k: {kk: vv for kk, vv in v.items() if kk != "rows"} for k, v in tot.items()}
    L("Branch panel (runs/hea/branch_panel): 5 geometries x {atomic, ortho} = 10 SCFs on 75-atom cells. Pilot on the two retained chains (runs/hea/pilot_retained): 2 chains x {slab 72, OH 74, O 73, OOH 75 atoms} x 2 projectors = 16 states, of which the four OOH decks are byte-identical (except prefix) to the panel decks `equiatomic_pull2.10` and `leader_pull2.10` and are NOT built again: the pilot readout reads those four panel outputs, so the pilot runs 12 SCFs. Per-deck figures below come from each state's own geometry.")
    L("")
    L("| deck | projector | nat | electrons | KS states | planning (core-h) | floor | ceiling | RAM envelope (GB) | note |")
    L("|---|---|---|---|---|---|---|---|---|---|")
    for arm in ("panel", "pilot"):
        for row in tot[arm]["rows"]:
            note = f"REUSED: panel deck {row['reuse']}__{row['projector']} (not counted)" if row["reuse"] else ""
            L(f"| {row['label']} | {row['projector']} | {row['nat']} | {row['nelec']:.0f} | {row['nbnd']} | {row['plan']:.1f} | {row['floor']:.1f} | {row['ceiling']:.1f} | {row['ram']:.1f} | {note} |")
    L("")
    L("| arm | SCFs | planning (core-h) | floor (core-h) | ceiling (core-h) | 48 h walltime cap (SU) |")
    L("|---|---|---|---|---|---|")
    p, q = tot["panel"], tot["pilot"]
    L(f"| branch panel (2 equiatomic + 3 leader geometries, both projectors) | {p['n']} | {p['plan']:.1f} | {p['floor']:.1f} | {p['ceiling']:.1f} | {p['walltime_cap_su']} |")
    L(f"| pilot on the two retained chains (slab, OH, O in both projectors; OOH read from the panel) | {q['n']} | {q['plan']:.1f} | {q['floor']:.1f} | {q['ceiling']:.1f} | {q['walltime_cap_su']} |")
    L(f"| both arms | {p['n'] + q['n']} | {p['plan'] + q['plan']:.1f} | {p['floor'] + q['floor']:.1f} | {p['ceiling'] + q['ceiling']:.1f} | {p['walltime_cap_su'] + q['walltime_cap_su']} |")
    L("")
    L("The walltime cap is what anvil/47_submit_a0.sh:108-109 prints (N x 128 x 48 SU); it is a cap, not a forecast. Balance context: 59,473.5 SU on 2026-09-05 (docs/88-a10-signature-sheet-2026-09-05.md:245, `mybalance`) before the 11.41 core-h of the gate-(e) pair (docs/90-small-arms-readout-2026-09-06.md:352-355) and the q333 pair.")
    L("")
    L("## 5. What the model does not cover")
    L("")
    L(f"- The SCF iteration count on a five-3d-species disordered slab with a ferromagnetic start has no precedent in this tree; section 1b bounds it from the single-metal record only. The planning figure assumes {PLANNING_ITERS} iterations, the ceiling {int(CEILING_FACTOR * PLANNING_ITERS)}; `electron_maxstep = 300` in the decks caps a non-convergent SCF at {300 / PLANNING_ITERS:.1f}x the planning wall, which is why a kill rule is proposed as an entrant slot in docs/92.")
    L(f"- The ortho-atomic x nspin = 2 x five-species combination has never run; the {ORTHO_WALL_RATIO:.4f} ratio is one 2x1v OOH pair, and the 1x1 per-state ratios span {min(to / ta for ta, to, _, _ in ONE_BY_ONE_PAIRS.values()):.3f}-{max(to / ta for ta, to, _, _ in ONE_BY_ONE_PAIRS.values()):.3f}.")
    L("- projwfc.x (run inline by anvil/46_a0.slurm on a converged point) is not costed; on the banked Ru u750 row it added 28.45 s to 442.81 s of pw.x for four SCFs (docs/89-ru-pseudopotential-control-DRAFT.md:215).")
    L("- Memory at the ceiling exceeds the 237 GB node for both cells; if the planning memory is exceeded by more than ~2.6x the job cannot run at 128 ranks on one node as designed. nk = 4 halves the density-part share per process and is the fallback, not the plan.")
    return "\n".join(lines) + "\n", results


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", default=None, help="write the report to this path (LF)")
    ap.add_argument("--json", default=None)
    args = ap.parse_args(argv)
    text, results = build_report()
    print(text)
    if args.write:
        from hea_deck import write_lf  # noqa: E402
        out = Path(args.write)
        if out.exists() and out.read_bytes() != text.encode("utf-8"):
            # regenerated report: replace, but only this file and only if it is ours
            head = out.read_text(encoding="utf-8").splitlines()[0]
            if head != "# HEA fixed-geometry SCF cost model":
                raise SystemExit(f"{out} is not a cost-model report; refusing to overwrite")
            out.unlink()
        write_lf(out, text)
        print(f"written {out}")
    if args.json:
        with open(args.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(results, fh, indent=2, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
