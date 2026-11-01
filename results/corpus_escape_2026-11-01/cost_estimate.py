"""Cost and wall-time estimate for the corpus-escape relaxations, from banked pw.x 7.5 runs on Anvil (128 ranks).

Per SCF iteration the time is scaled from five banked outputs (read here, path in CALIBRATION) by
  model A (planning, the program's envelope convention, src/dft/hea_cost_model.py): k_local x nbnd^2 x npw
  model B (floor):                                                                k_local x nbnd   x npw
where k_local = ceil(k-list length / 8 pools) (the k list is doubled for nspin = 2) and npw scales as
V x ecutwfc^1.5 from each calibration's printed plane-wave count. Planning takes the largest model-A
prediction over the calibrations; the floor the smallest model-B one; the ceiling is 3 x planning
(docs/43-prereg-week1-factorial.md:4453-4456, the q333 5.8x miss; same factor as hea_cost_model.py).

SCF iterations per relaxation cycle come from the deposited run of the same case (census scf_iterations, plain
mixing beta 0.3 and conv_thr 1e-6 as kept): first cycle = deposited first + 2, later cycles = deposited median of
later cycles + 2 (pw.x's upscale already lowers conv_thr toward 1e-8 near convergence in both; the +2 prices the
longer time spent near the tighter force threshold). Cycles per run (planning): held 12 from a converged deposit, 30
from one that stopped unconverged; escape 30. Billing: wholenode, 128 SU per node-hour.

Usage: python results/corpus_escape_2026-11-01/cost_estimate.py   (writes cost_estimate.json)
"""
import json
import math
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CASES = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))
SPEC = json.loads((HERE / "launch_spec.json").read_text(encoding="utf-8"))
NP, POOLS, BOHR_A = 128, 8, 0.529177210903
CEILING_FACTOR = 3.0
ITER_PAD = 2
CYCLES = {"held_converged": 12, "held_unconverged": 30, "escape": 30}
BALANCE_SU = 9963.3          # mybalance, 2026-11-01 (read-only probe)
COMMITTED_SU = 300.0         # array 21852915, two wholenode tasks still running
CALIBRATION = [  # banked np = 128 outputs (pw.x 7.5), all nspin = 2
    "runs/a0/cell/s0_OOH__2x1v_escape__u715.out",
    "runs/a0/cell/ref__2x1v__u715.out",
    "runs/s3/Mn/s0_OOH__2x1v_mir.out",
    "runs/hea/winner_2026-09-10/g_bd2523d558a6d76f7856eae53f3de623869b6bd1fb927bed3aaea5a06b693ba1__atomic.out",
    "runs/hea/lowtail_validation_2026-09-16/Cu8Cr23Mn35Co34__s20_site2/O_recon__atomic.out",
]


def wall_seconds(text):
    w = re.search(r"PWSCF\s*:\s*.+?CPU\s+(.+?)\s*WALL", text).group(1).replace(" ", "")
    return sum(float(v) * {"d": 86400, "h": 3600, "m": 60, "s": 1}[u] for v, u in re.findall(r"([\d.]+)([dhms])", w))


def calibration_point(rel):
    text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
    deck = (ROOT / rel).with_suffix(".in").read_text(encoding="utf-8", errors="replace")
    nspin = int(re.search(r"nspin\s*=\s*(\d)", deck).group(1)) if re.search(r"nspin\s*=", deck) else 1
    if "Number of MPI processes:               128" not in text:
        raise SystemExit("calibration not at 128 ranks: " + rel)
    iters = sum(int(v) for v in re.findall(r"convergence has been achieved in\s+(\d+) iterations", text))
    nks = int(re.search(r"number of k points=\s*(\d+)", text).group(1))
    npool = int(re.search(r"npool\s*=\s*(\d+)", text).group(1))
    return {"out": rel, "nbnd": int(re.search(r"number of Kohn-Sham states=\s*(\d+)", text).group(1)),
            "nks": nks, "nspin": nspin, "npool": npool, "k_local": math.ceil(nks * nspin / npool),
            "npw": int(re.search(r"^\s*Sum\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+(\d+)", text, re.M).group(1)),
            "V_bohr3": float(re.search(r"unit-cell volume\s*=\s*([\d.]+)", text).group(1)),
            "ecutwfc": float(re.search(r"kinetic-energy cutoff\s*=\s*([\d.]+)", text).group(1)),
            "wall_s": round(wall_seconds(text), 2), "iterations": iters,
            "s_per_iter": round(wall_seconds(text) / iters, 3)}


def nint(x):
    return int(math.floor(abs(x) + 0.5)) * (1 if x >= 0 else -1)


def default_nbnd(nelec, tot_mag):
    """pw.x setup.f90 default for smearing: max(1.2 nelec/2, 1.2 nelup, 1.2 neldw, max(nelec/2, nelup, neldw) + 4)."""
    up = (nelec + tot_mag) / 2 if tot_mag is not None else nelec / 2
    dw = (nelec - tot_mag) / 2 if tot_mag is not None else nelec / 2
    base = max(nint(nelec / 2), nint(up), nint(dw))
    return max(nint(1.2 * nelec / 2), nint(1.2 * up), nint(1.2 * dw), base + 4)


def per_iter(case, nbnd, k_list, cal):
    V = case["volume_A3"] / BOHR_A ** 3
    k_local = math.ceil(k_list / POOLS)
    rows = []
    for c in cal:
        npw = c["npw"] * (V / c["V_bohr3"]) * (40.0 / c["ecutwfc"]) ** 1.5
        base = c["s_per_iter"] / c["k_local"] * k_local * (npw / c["npw"])
        rows.append({"A": base * (nbnd / c["nbnd"]) ** 2, "B": base * (nbnd / c["nbnd"])})
    return max(r["A"] for r in rows), min(r["B"] for r in rows)


def run_cost(case, arm, nbnd, cal):
    nspin = case["nspin"]
    irreducible = case["deposited_nks_printed"] // nspin if nspin == 2 else case["deposited_nks_printed"]
    k_list = (irreducible if arm == "held" else 10) * nspin
    tA, tB = per_iter(case, nbnd, k_list, cal)
    it = case["deposited_scf_iterations"]
    first, later = it[0] + ITER_PAD, statistics.median(it[1:]) + ITER_PAD
    cycles = CYCLES["escape"] if arm == "escape" else (
        CYCLES["held_converged"] if case["deposited_converged"] else CYCLES["held_unconverged"])
    iters = first + later * (cycles - 1)
    plan_s, floor_s = iters * tA, iters * tB
    return {"k_list": k_list, "k_local": math.ceil(k_list / POOLS), "nbnd": nbnd, "cycles": cycles,
            "iterations": round(iters, 1), "s_per_iter_planning": round(tA, 2), "s_per_iter_floor": round(tB, 2),
            "wall_h_planning": round(plan_s / 3600, 3), "wall_h_floor": round(floor_s / 3600, 3),
            "wall_h_ceiling": round(CEILING_FACTOR * plan_s / 3600, 3),
            "su_planning": round(plan_s / 3600 * NP, 1), "su_floor": round(floor_s / 3600 * NP, 1),
            "su_ceiling": round(CEILING_FACTOR * plan_s / 3600 * NP, 1)}


def main():
    cal = [calibration_point(rel) for rel in CALIBRATION]
    rows = []
    for case in CASES["cases"]:
        tot = float(case["tot_magnetization"]) if case["tot_magnetization"] is not None else None
        nb = default_nbnd(case["deposited_nelec"], tot)
        row = {"tier": case["tier"], "metal": case["metal"], "job": case["job"], "nspin": case["nspin"],
               "nat": case["nat"], "nelec": case["deposited_nelec"], "nbnd_default": nb,
               "nbnd_deposited": case["deposited_nbnd"], "deposited_converged": case["deposited_converged"]}
        for arm in ("held", "escape"):
            row[arm] = run_cost(case, arm, nb, cal)
            row[arm + "_deposited_nbnd"] = run_cost(case, arm, case["deposited_nbnd"], cal)
        rows.append(row)
    stage_wall = SPEC["stages"]
    totals = {}
    group_of = {(c["metal"], c["job"]): c["launch_group"] for c in CASES["cases"]}
    for r in rows:
        r["launch_group"] = group_of[(r["metal"], r["job"])]
    for tier in SPEC["launch_groups"]:
        sel = [r for r in rows if r["launch_group"] == tier]
        t = {}
        for key in ("su_planning", "su_floor", "su_ceiling"):
            t[key] = round(sum(r[a][key] for r in sel for a in ("held", "escape")), 0)
            t[key + "_deposited_nbnd"] = round(sum(r[a + "_deposited_nbnd"][key] for r in sel for a in ("held", "escape")), 0)
        for arm in ("held", "escape"):
            stage = tier + "_" + arm
            t[stage] = {"slowest_wall_h_planning": max(r[arm]["wall_h_planning"] for r in sel),
                        "slowest_wall_h_ceiling": max(r[arm]["wall_h_ceiling"] for r in sel),
                        "slurm_wall_h": stage_wall[stage]["wall_minutes"] / 60,
                        "rows_over_slurm_wall_at_ceiling": [r["metal"] + " " + r["job"] for r in sel
                                                            if r[arm]["wall_h_ceiling"] > stage_wall[stage]["wall_minutes"] / 60],
                        "slurm_reservation_su": SPEC["allocation"]["stage_ceilings_cpu_su"][stage]}
        totals[tier] = t
    tier1 = {k: totals["tier1a"][k] + totals["tier1b"][k] for k in totals["tier1a"] if k.startswith("su_")}
    both = {k: tier1[k] + totals["tier2"][k] for k in tier1}
    report = {"schema": "corpus-escape-cost-v1", "calibration": cal, "model": __doc__.split("Usage")[0].strip(),
              "cycles": CYCLES, "iteration_pad": ITER_PAD, "ceiling_factor": CEILING_FACTOR,
              "balance_su": BALANCE_SU, "committed_su": COMMITTED_SU, "available_su": BALANCE_SU - COMMITTED_SU,
              "totals_by_launch_group": totals, "tier1": tier1, "tier1_plus_tier2": both, "rows": rows}
    (HERE / "cost_estimate.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("calibration (s/iter at 128 ranks):")
    for c in cal:
        print("  %-60s nbnd %4d k_local %d npw %6d -> %.2f s/iter" % (c["out"][-60:], c["nbnd"], c["k_local"], c["npw"], c["s_per_iter"]))
    print("%-5s %-5s %-10s nb  arm    k_loc s/it(A)  h_plan h_ceil SU_plan" % ("tier", "metal", "job"))
    for r in rows:
        for arm in ("held", "escape"):
            a = r[arm]
            print("%-5s %-5s %-10s %3d %-6s %d    %6.2f  %6.2f %6.2f %7.1f" % (
                r["tier"], r["metal"], r["job"], a["nbnd"], arm, a["k_local"], a["s_per_iter_planning"],
                a["wall_h_planning"], a["wall_h_ceiling"], a["su_planning"]))
    for tier, t in totals.items():
        print(tier, {k: v for k, v in t.items() if k.startswith("su_")})
        for stage in (tier + "_held", tier + "_escape"):
            print("  ", stage, t[stage])
    print("tier1", tier1)
    print("tier1+2", both, "available", BALANCE_SU - COMMITTED_SU)
    return 0


if __name__ == "__main__":
    sys.exit(main())
