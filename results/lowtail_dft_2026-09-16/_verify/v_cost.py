"""Independent cost checks: anchors from banked accepted HEA SCFs, relaxation survey, per-deck formula."""
import glob
import json
import math
import os
import re
import statistics

import numpy as np

ROOT = r"C:\Users\frank\sts-electrocatalyst"
os.chdir(ROOT)
RY, BOHR = 13.605693122994, 0.529177210903
FC = RY / BOHR
Z = json.load(open("results/lowtail_dft_2026-09-16/_verify/v_zero.json"))


def nr(xs, q):
    xs = sorted(xs)
    return xs[max(1, math.ceil(q / 100 * len(xs))) - 1] if xs else None


def secs(s):
    # QE wall strings like '31m56.92s', '1h 2m 3.00s', '45.3s'
    tot = 0.0
    for val, unit in re.findall(r"([\d.]+)([hms])", s):
        tot += float(val) * {"h": 3600, "m": 60, "s": 1}[unit]
    return tot


def nml(text, key):
    m = re.search(rf"^\s*{key}\s*=\s*'?([^'\s,]+)'?", text, re.M)
    return m.group(1) if m else None


# ---- anchors
rows = []
for x in Z["rows"]:
    if x["status"] != "ACCEPTED":
        continue
    tin = open(x["in"], encoding="utf-8").read()
    if not (float(nml(tin, "ecutwfc")) == 80.0 and float(nml(tin, "ecutrho")) == 640.0 and float(nml(tin, "degauss")) == 0.01):
        continue
    o = open(x["in"].replace(".run.in", ".out").replace(".in", ".out") if x["in"].endswith(".run.in") else x["in"][:-3] + ".out",
             encoding="utf-8", errors="replace").read()
    it = int(re.search(r"convergence has been achieved in\s+(\d+) iterations", o).group(1))
    ew = float(re.search(r"^\s+electrons\s+:.*?([\d.]+)s WALL", o, re.M).group(1))
    fw = float(re.search(r"^\s+forces\s+:.*?([\d.]+)s WALL", o, re.M).group(1))
    iw = float(re.search(r"^\s+init_run\s+:.*?([\d.]+)s WALL", o, re.M).group(1))
    pw = secs(re.search(r"PWSCF\s+:.*CPU\s+(.*)WALL", o).group(1))
    vol_au = float(re.search(r"unit-cell volume\s+=\s+([\d.]+)", o).group(1))
    nbnd = int(re.search(r"Kohn-Sham states=\s+(\d+)", o).group(1))
    ram = float(re.search(r"Estimated total dynamical RAM >\s+([\d.]+) GB", o).group(1))
    V = vol_au * BOHR ** 3
    card = re.search(r"^HUBBARD \(([\w-]+)\)", tin, re.M).group(1)
    scratch = nml(tin, "startingwfc") is None and nml(tin, "startingpot") is None
    rows.append(dict(job=x["job"], proj="ortho" if "ortho" in card else "atomic", it=it, t_iter_norm=ew / it / (V * nbnd),
                     t_force_norm=fw / (V * nbnd), init=iw, rest=pw - iw - ew - fw, ram_norm=ram / (V * nbnd), scratch=scratch,
                     baseline=x["job"].endswith("__baseline") or x["job"].startswith("g_")))
anch = {}
for pj in ("atomic", "ortho"):
    R = [r for r in rows if r["proj"] == pj]
    anch[pj] = dict(n=len(R), t_iter_norm=statistics.median(r["t_iter_norm"] for r in R), t_force_norm=statistics.median(r["t_force_norm"] for r in R),
                    init=statistics.median(r["init"] for r in R), rest_all_median=statistics.median(r["rest"] for r in R),
                    ram_norm=statistics.median(r["ram_norm"] for r in R),
                    first=sorted(r["it"] for r in R if r["scratch"] and r["baseline"]),
                    jobs=[r["job"] for r in R])
    anch[pj]["first_p50"] = nr(anch[pj]["first"], 50)
    anch[pj]["first_p90"] = nr(anch[pj]["first"], 90)

# ---- relaxation survey (outside runs/hea)
survey, excl = [], []
for out in sorted(glob.glob("runs/**/*.out", recursive=True)):
    o_ = out.replace("\\", "/")
    if o_.startswith("runs/hea/") or o_.endswith(".projwfc.out"):
        continue
    inp = out[:-4] + ".in"
    if not os.path.exists(inp):
        continue
    tin = open(inp, encoding="utf-8", errors="replace").read()
    if nml(tin, "calculation") != "relax":
        continue
    ns = nml(tin, "nspin")
    if ns is None or int(float(ns)) != 2:
        continue
    t = open(out, encoding="utf-8", errors="replace").read()
    m = re.search(r"number of atoms/cell\s+=\s+(\d+)", t)
    if not m:
        continue
    nat = int(m.group(1))
    if nat < 18:
        continue
    L = tin.splitlines()
    ai = [i for i, l in enumerate(L) if l.strip().upper().startswith("ATOMIC_POSITIONS")]
    try:
        ifp = []
        for k in range(nat):
            tok = L[ai[0] + 1 + k].split()
            ifp.append([int(v) for v in tok[4:7]] if len(tok) >= 7 else [1, 1, 1])
    except Exception as e:  # noqa: BLE001
        excl.append((o_, "if_pos parse"))
        continue
    lines = t.splitlines()
    hdrs = [i for i, l in enumerate(lines) if "Forces acting on atoms (cartesian axes, Ry/au)" in l]
    if not hdrs:
        excl.append((o_, "no force block"))
        continue
    F = []
    i = hdrs[0] + 1
    while len(F) < nat and i < len(lines):
        mm = re.match(r"^\s*atom\s+\d+\s+type\s+\d+\s+force\s*=\s*(\S+)\s+(\S+)\s+(\S+)", lines[i])
        if mm:
            F.append([float(mm.group(k)) * FC for k in (1, 2, 3)])
        i += 1
    if len(F) != nat:
        excl.append((o_, "short force block"))
        continue
    f0 = float(np.max(np.linalg.norm(np.array(F) * np.array(ifp), axis=1)))
    bc = re.search(r"bfgs converged in\s+(\d+) scf cycles and\s+(\d+) bfgs steps", t)
    its = [int(v) for v in re.findall(r"convergence has been achieved in\s+(\d+) iterations", t)]
    fails = ("convergence NOT achieved" in t) or ("IEEE_INVALID" in t)
    survey.append(dict(out=o_, nat=nat, nfree=sum(1 for f in ifp if any(f)), f0=f0, conv=bool(bc) and not fails and "JOB DONE" in t,
                       cycles=int(bc.group(1)) if bc else None, its=its))

bands = {}
for key, fref in (("O_atomic", 1.58255978350026), ("O_ortho", 1.518580629163242), ("slab_atomic", 1.5621142603152407), ("slab_ortho", 1.5298026971418026)):
    B = [s for s in survey if fref / 2 <= s["f0"] <= 2 * fref]
    C = [s for s in B if s["conv"] and s["cycles"]]
    sub = [statistics.median(s["its"][1:]) for s in C if len(s["its"]) > 1]
    bands[key] = dict(n_band=len(B), n_conv=len(C), p50=nr([s["cycles"] for s in C], 50), p90=nr([s["cycles"] for s in C], 90),
                      max=max(s["cycles"] for s in C), sub_p50=nr(sub, 50), sub_p90=nr(sub, 90), max_free=max(s["nfree"] for s in C),
                      not_conv=[s["out"] for s in B if s not in C])

# ---- deck formula with my anchors and bands
VAL = {"Cr": 14.0, "Mn": 15.0, "Fe": 16.0, "Co": 17.0, "Ni": 18.0, "Cu": 11.0, "O": 6.0, "H": 1.0}
plan = json.load(open("results/lowtail_dft_2026-09-16/deck_plan.json"))
deck_rows = []
for dk in plan["decks"]:
    t = open(dk["path"], encoding="utf-8").read()
    L = t.splitlines()
    ci = [i for i, l in enumerate(L) if l.startswith("CELL_PARAMETERS")][0]
    ai = [i for i, l in enumerate(L) if l.startswith("ATOMIC_POSITIONS")][0]
    nat = int(re.search(r"nat = (\d+)", t).group(1))
    cell = np.array([[float(v) for v in L[ci + 1 + k].split()] for k in range(3)])
    syms = [L[ai + 1 + k].split()[0] for k in range(nat)]
    nelec = sum(VAL[s] for s in syms)
    nb = int(math.floor(1.2 * int(math.floor(nelec / 2 + 0.5)) + 0.5))
    V = abs(np.linalg.det(cell))
    a = anch[dk["projector"]]
    band = bands[("O" if dk["state"].startswith("O") else "slab") + "_" + dk["projector"]]
    t_it, t_f = a["t_iter_norm"] * V * nb, a["t_force_norm"] * V * nb
    rest = dk["cost"]["wall_forces_s"] * 0 + plan["cost_inputs"]["anchors"][dk["projector"]]["rest_s"]

    def wall(S, I1, Is):
        return a["init"] + (I1 + (S - 1) * Is) * t_it + S * (t_f + rest)
    pl = wall(band["p50"], a["first_p50"], band["sub_p50"])
    p9 = wall(band["p90"], a["first_p90"], band["sub_p90"])
    ce = max(3 * pl, p9)
    deck_rows.append(dict(deck=dk["path"], nelec=nelec, nbnd=nb, plan_core_h=pl * 128 / 3600, ceil_core_h=ce * 128 / 3600,
                          worker_plan=dk["cost"]["planning_core_h"], worker_ceil=dk["cost"]["ceiling_core_h"],
                          t_force=t_f, worker_t_force=dk["cost"]["wall_forces_s"], ram_GB=a["ram_norm"] * V * nb,
                          worker_ram=dk["cost"]["memory_printed_estimate_GB"], ceil_wall_h=ce / 3600))
tot = {}
for pj in ("atomic", "ortho"):
    R = [r for r in deck_rows if r["deck"].endswith(pj + ".in")]
    tot[pj] = dict(plan=sum(r["plan_core_h"] for r in R), ceil=sum(r["ceil_core_h"] for r in R))
out = dict(anchors=anch, survey_n=len(survey), survey_excluded=len(excl), excl=excl, bands=bands, decks=deck_rows, totals=tot)
json.dump(out, open("results/lowtail_dft_2026-09-16/_verify/v_cost.json", "w"), indent=1)
print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "jobs"} for k, v in anch.items()}, indent=1))
print("survey", len(survey), "excluded", len(excl), excl[:12])
print(json.dumps(bands, indent=1))
for r in deck_rows:
    print(r["deck"][40:], r["nelec"], r["nbnd"], round(r["plan_core_h"], 1), round(r["worker_plan"], 1), round(r["ceil_core_h"], 1), round(r["worker_ceil"], 1), round(r["t_force"], 1), round(r["ram_GB"], 1), round(r["ceil_wall_h"], 2))
print(tot)
