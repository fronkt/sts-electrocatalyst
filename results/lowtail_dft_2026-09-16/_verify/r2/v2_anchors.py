"""Independent verifier: per-iteration / force wall anchors from the accepted HEA single points, and the
winner *O force parse vs the stored force audit."""
import json, re, statistics
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[4]


def clock(tok):
    m = re.fullmatch(r"\s*(?:(\d+)d)?\s*(?:(\d+)h)?\s*(?:(\d+)m)?\s*(?:([\d.]+)s)?\s*", tok)
    return int(m.group(1) or 0) * 86400 + int(m.group(2) or 0) * 3600 + int(m.group(3) or 0) * 60 + float(m.group(4) or 0)


def timer(text, name):
    m = re.search(r"^\s*" + name + r"\s*:\s*(.+?)CPU\s+(.+?)WALL", text, re.M)
    return clock(m.group(2))


accepted = {
    "atomic": ["winner_2026-09-10/g_132934a8907edb7d2ce224ae46c90eab5deb73395993e300b6aa499474f3a2b6__atomic",
               "winner_2026-09-10/g_80ebe76a616d61d6fecca57d1cd6c2ef27990771fbc3db9a8cfea6a4bf228e5c__atomic",
               "winner_2026-09-10/g_9a2ae68020203b9e4530466fdcb9881c5c84ec63fec7351b2f981336d0ef6b84__atomic",
               "winner_2026-09-10/g_bd2523d558a6d76f7856eae53f3de623869b6bd1fb927bed3aaea5a06b693ba1__atomic",
               "controls_2026-09-07/hc__leader_builder__atomic__baseline", "controls_2026-09-07/hc__leader_builder__atomic__fragment",
               "controls_2026-09-07/hc__leader_builder__atomic__metal_alternating", "controls_2026-09-07/hc__leader_builder__atomic__metal_alternating_fragment",
               "controls_2026-09-07/hc__leader_pull2.10__atomic__baseline", "controls_2026-09-07/hc__leader_pull2.10__atomic__fragment",
               "controls_2026-09-07/hc__leader_pull2.10__atomic__metal_alternating", "controls_2026-09-07/hc__leader_pull2.10__atomic__metal_alternating_fragment",
               "ieee_2026-09-09/hd__leader_builder__atomic__ieee_repro", "numerical_2026-09-08/hn__leader_pull2.10__atomic__tight"],
}
res = {}
for proj, jobs in accepted.items():
    it_norm, f_norm, first = [], [], []
    for j in jobs:
        out = (ROOT / "runs/hea" / (j + ".out")).read_text(errors="replace")
        deck = (ROOT / "runs/hea" / (j + ".run.in")).read_text()
        lines = deck.splitlines()
        i = [k for k, l in enumerate(lines) if l.startswith("CELL_PARAMETERS")][0]
        cell = np.array([[float(x) for x in lines[i + k].split()] for k in (1, 2, 3)])
        vol = abs(np.linalg.det(cell))
        nbnd = int(re.search(r"number of Kohn-Sham states=\s*(\d+)", out).group(1))
        nit = int(re.findall(r"convergence has been achieved in\s+(\d+) iterations", out)[-1])
        it_norm.append(timer(out, "electrons") / nit / (vol * nbnd))
        f_norm.append(timer(out, "forces") / (vol * nbnd))
        scratch = "startingwfc" not in deck and "startingpot" not in deck
        baseline = ("__baseline" in j) or j.startswith("winner")
        if scratch and baseline:
            first.append(nit)
    res[proj] = dict(per_iteration_norm=statistics.median(it_norm), forces_norm=statistics.median(f_norm), first=sorted(first))
print(json.dumps(res, indent=1))
plan = json.loads((ROOT / "results/lowtail_dft_2026-09-16/deck_plan.json").read_text())
a = plan["cost_inputs"]["anchors"]["atomic"]
print("track", a["per_iteration_norm"], a["forces_norm"], a["first_iterations"])

# force audit comparison (winner *O atomic)
RY_EV, BOHR = 13.605693122994, 0.529177210903
wr = json.loads((ROOT / "results/hea_continuation_2026-09-11/winner_readout.json").read_text())
ep = [e for e in wr["endpoints"] if e["job"].startswith("g_80ebe") and e["job"].endswith("atomic")][0]
stored = np.array([p["force_ev_A"] for p in ep["audit"]["scf"]["per_atom"]])
v = json.loads((Path(__file__).with_name("v2_forces.json")).read_text())
out = (ROOT / "runs/hea/winner_2026-09-10/g_80ebe76a616d61d6fecca57d1cd6c2ef27990771fbc3db9a8cfea6a4bf228e5c__atomic.out").read_text()
F = np.array([[float(x) for x in m] for m in re.findall(r"atom\s+\d+\s+type\s+\d+\s+force\s+=\s+(\S+)\s+(\S+)\s+(\S+)", out)])
print("n force lines", len(F), "max |mine - stored| (CODATA2018 conv)", float(np.abs(F * RY_EV / BOHR - stored).max()))
