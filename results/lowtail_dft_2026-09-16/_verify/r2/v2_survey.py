"""Independent verifier: relaxation-survey step statistics, cost arithmetic, per-leg kill-ceiling exposure.

Own parser (no track code). Population rule re-implemented from the note text plus the
track's documented filters (calculation relax, nspin 2, outside runs/hea, same-stem .in)."""
import hashlib, json, math, re, statistics, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "src" / "dft"))
RY_EV = 13.605693122994
BOHR = 0.529177210903


def nv(text, key):
    m = re.search(r"^\s*" + re.escape(key) + r"\s*=\s*([^,\n/]+)", text, re.M | re.I)
    if not m:
        return None
    v = m.group(1).strip().strip("'\"")
    try:
        return float(v.replace("d", "e").replace("D", "e"))
    except ValueError:
        return v


def ifpos(text_in, nat):
    lines = text_in.splitlines()
    j = [k for k, l in enumerate(lines) if l.strip().upper().startswith("ATOMIC_POSITIONS")][0]
    out = []
    for l in lines[j + 1:j + 1 + nat]:
        t = l.split()
        out.append([int(x) for x in t[4:7]] if len(t) >= 7 else [1, 1, 1])
    return np.array(out)


def force_blocks(text, nat):
    blocks = []
    lines = text.splitlines()
    for k, l in enumerate(lines):
        if "Forces acting on atoms (cartesian axes, Ry/au)" in l:
            F = []
            q = k + 1
            while len(F) < nat and q < len(lines):
                m = re.match(r"\s*atom\s+\d+\s+type\s+\d+\s+force\s+=\s+(\S+)\s+(\S+)\s+(\S+)", lines[q])
                if m:
                    F.append([float(m.group(i)) for i in (1, 2, 3)])
                q += 1
            blocks.append(np.array(F) * RY_EV / BOHR)
    return blocks


def nearest_rank(vals, q):
    v = sorted(vals)
    return v[max(0, math.ceil(q / 100 * len(v)) - 1)]


import hea_panel_readout as hpr


def corrected_status(path):
    """Scorer with (i) hour-format wall token parsed and (ii) the gfortran note phrase neutralised."""
    blob = Path(path).read_bytes().decode("utf-8", "replace")
    blob2 = re.sub(r"^(Note: The following )floating-point exceptions( are signalling:)", r"\1fpe\2", blob, flags=re.M)
    tmp = Path(__file__).with_name("_tmp_scorer.out")
    tmp.write_text(blob2, encoding="utf-8")
    orig = hpr._wall_seconds

    def wall(s):
        m = re.match(r"\s*(?:(\d+)d)?\s*(?:(\d+)h)?\s*(?:(\d+)m)?\s*(?:([\d.]+)s)?\s*$", s)
        return int(m.group(1) or 0) * 86400 + int(m.group(2) or 0) * 3600 + int(m.group(3) or 0) * 60 + float(m.group(4) or 0)
    hpr._wall_seconds = wall
    try:
        o = hpr.parse_out(tmp, allow_relax=True)
    finally:
        hpr._wall_seconds = orig
        tmp.unlink()
    return o["status"], o.get("severe_failures")


rows, excl = [], []
for out in sorted((ROOT / "runs").rglob("*.out")):
    rel = out.relative_to(ROOT / "runs")
    if rel.parts[0] == "hea" or out.name.endswith(".projwfc.out"):
        continue
    inp = out.with_name(out.name[:-4] + ".in")
    if not inp.exists():
        continue
    tin = inp.read_text(errors="replace")
    if nv(tin, "calculation") != "relax" or nv(tin, "nspin") != 2.0:
        continue
    text = out.read_bytes().decode("utf-8", "replace")
    m = re.search(r"number of atoms/cell\s*=\s*(\d+)", text)
    nat = int(m.group(1)) if m else None
    if nat is None or nat < 18:
        continue
    blocks = force_blocks(text, nat)
    if not blocks:
        excl.append(str(out.relative_to(ROOT)))
        continue
    ip = ifpos(tin, nat)
    f0 = float(np.max(np.linalg.norm(blocks[0] * ip, axis=1)))
    its = [int(x) for x in re.findall(r"convergence has been achieved in\s+(\d+) iterations", text)]
    bad = re.findall(r"convergence NOT achieved after\s+(\d+) iterations", text)
    b = re.search(r"bfgs converged in\s+(\d+) scf cycles and\s+(\d+) bfgs steps", text)
    conv = bool(b) and not bad and text.count("JOB DONE") >= 1
    st, sev = corrected_status(out)
    rows.append(dict(out=str(out.relative_to(ROOT)).replace("\\", "/"), nat=nat, nfree=int((ip.sum(1) > 0).sum()), f0=f0,
                     cycles=int(b.group(1)) if b else None, conv=conv, status=st, sev=sev,
                     sub_med=statistics.median(its[1:]) if len(its) > 1 else None, first=its[0] if its else None))

plan = json.loads((ROOT / "results/lowtail_dft_2026-09-16/deck_plan.json").read_text())
fref = plan["cost_inputs"]["force_reference"]["values"]
res = dict(n_rows=len(rows), n_excluded=len(excl), status_counts={}, bands={})
from collections import Counter
res["status_counts"] = dict(Counter(r["status"] for r in rows))
res["n_ieee_invalid"] = sum(1 for r in rows if r["sev"] and any("INVALID" in s for s in r["sev"]))
for key, f in fref.items():
    lo, hi = f / 2, f * 2
    band = [r for r in rows if lo <= r["f0"] <= hi]
    bfgs = [r for r in band if r["conv"] and r["cycles"]]
    basis = [r for r in bfgs if r["status"] == "CONVERGED"]
    cyc = [r["cycles"] for r in basis]
    sub = [r["sub_med"] for r in basis if r["sub_med"] is not None]
    res["bands"][key] = dict(n_band=len(band), n_bfgs=len(bfgs), n_basis=len(basis),
                             p50=nearest_rank(cyc, 50), p90=nearest_rank(cyc, 90), max=max(cyc),
                             sub_p50=nearest_rank(sub, 50), sub_p90=nearest_rank(sub, 90), max_free=max(r["nfree"] for r in basis),
                             cycles=sorted(cyc), rejected=[r["out"] for r in bfgs if r["status"] != "CONVERGED"])

# cost arithmetic and kill-ceiling exposure per deck, using the plan's per-iteration/force costs
exposure = []
for d in plan["decks"]:
    c = d["cost"]
    proj = d["projector"]
    anch = plan["cost_inputs"]["anchors"][proj]
    band = res["bands"]["winner_O|" + proj] if d["state"] != "slab" else res["bands"]["winner_slab|" + proj]
    t_it, t_f = c["wall_per_iteration_s"], c["wall_forces_s"]
    init, rest = anch["init_s"], anch["rest_s"]

    def wall(S, I1, Is):
        return init + (I1 + (S - 1) * Is) * t_it + S * (t_f + rest)
    plan_s = wall(band["p50"], anch["first_iterations_p50"], band["sub_p50"])
    p90_s = wall(band["p90"], anch["first_iterations_p90"], band["sub_p90"])
    ceil_s = max(3 * plan_s, p90_s)
    # exposure: each basis relaxation's own cycles and later-iteration median, first SCF at p50
    basis = [r for r in rows if r["conv"] and r["cycles"] and r["status"] == "CONVERGED"
             and (fref[("winner_O|" if d["state"] != "slab" else "winner_slab|") + proj] / 2) <= r["f0"] <= 2 * fref[("winner_O|" if d["state"] != "slab" else "winner_slab|") + proj]]
    over = [r["out"] for r in basis if wall(r["cycles"], anch["first_iterations_p50"], r["sub_med"] or 0) > math.ceil(ceil_s)]
    exposure.append(dict(deck=d["path"], plan_core_h=plan_s * 128 / 3600, ceil_core_h=ceil_s * 128 / 3600,
                         plan_match=abs(plan_s - c["planning_wall_s"]) < 1e-6, ceil_match=abs(ceil_s - c["ceiling_wall_s"]) < 1e-6,
                         n_basis=len(basis), n_over_ceiling=len(over), over=over,
                         max_cycles_within_ceiling_at_p50_iters=max(S for S in range(1, 300) if wall(S, anch["first_iterations_p50"], band["sub_p50"]) <= math.ceil(ceil_s))))
tot = {}
for d, e in zip(plan["decks"], exposure):
    tot.setdefault(d["projector"], [0, 0])
    tot[d["projector"]][0] += e["plan_core_h"]; tot[d["projector"]][1] += e["ceil_core_h"]
res["exposure"] = exposure
res["totals"] = tot
Path(__file__).with_name("v2_survey.json").write_text(json.dumps(dict(res=res, rows=rows, excluded=excl), indent=1))
print(json.dumps({k: v for k, v in res.items() if k != "exposure"}, indent=1))
for e in exposure:
    print(e["deck"].split("2026-09-16/")[1], "%.1f %.1f" % (e["plan_core_h"], e["ceil_core_h"]), e["plan_match"], e["ceil_match"], e["n_basis"], e["n_over_ceiling"], e["max_cycles_within_ceiling_at_p50_iters"], e["over"])
