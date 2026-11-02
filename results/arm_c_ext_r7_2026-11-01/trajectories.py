"""Round 7 trajectories: QE's "estimated scf accuracy" (Ry), total magnetization and time per iteration for the two
Cu8 s16/2 slab runs, read from the sha256-matched mirror (terminal_collection.json). Writes trajectories.json."""
import json
import re
import statistics as st
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = HERE / "raw_mirror/runs/hea/arm_c_ext_r7_2026-11-01/Cu8Cr23Mn35Co34__s16_site2"
JOBS = ["slab__atomic_moved_cg", "slab__atomic_moved_nbnd470"]
ROUND3 = {"best": 5.3e-6, "best_iteration": 68, "magnetization_from_101": [51.08, 51.25]}   # Round 3 readout table
SITE_CONVERGED_MAGNETIZATION = [49.6, 50.1]   # O, OH, OOH at this site (Round 7 rule)

ITER = re.compile(r"iteration #\s*(\d+).*?\n(.*?)(?=iteration #|\Z)", re.S)
ACC = re.compile(r"estimated scf accuracy\s*<\s*([0-9.Ee+-]+)\s*Ry")
MAG = re.compile(r"total magnetization\s*=\s*([-0-9.]+)\s*Bohr")
CPU = re.compile(r"total cpu time spent up to now is\s*([0-9.]+)\s*secs")


def window(rows, lo, hi):
    vals = [a for i, a, _ in rows if lo <= i <= hi and a is not None]
    return st.median(vals) if vals else None


out = {"round3_slab": ROUND3, "site_converged_magnetization_uB": SITE_CONVERGED_MAGNETIZATION, "runs": {}}
for job in JOBS:
    text = (RUN / f"{job}.out").read_text(encoding="utf-8", errors="replace")
    rows = []
    for m in ITER.finditer(text):
        body = m.group(2)
        a, g = ACC.search(body), MAG.search(body)
        rows.append((int(m.group(1)), float(a.group(1)) if a else None, float(g.group(1)) if g else None))
    acc = [(i, a) for i, a, _ in rows if a is not None]
    best_i, best = min(acc, key=lambda x: x[1])
    mags = [g for _, _, g in rows if g is not None]
    cpu = [float(x) for x in CPU.findall(text)]
    n = len(acc)
    tail = mags[len(mags) // 3:]   # last two thirds of the run, so both lengths compare
    out["runs"][job] = {
        "iterations_with_accuracy": n,
        "best_accuracy_Ry": best, "best_iteration": best_i,
        "last_accuracy_Ry": acc[-1][1],
        "iterations_below_1e-4": sum(a < 1e-4 for _, a in acc),
        "iterations_below_1e-5": sum(a < 1e-5 for _, a in acc),
        "median_by_window": {f"{lo}-{hi}": window(rows, lo, hi) for lo, hi in [(1, 50), (51, 100), (101, 200), (201, 300)]},
        "magnetization_uB_last_two_thirds": [min(tail), max(tail)] if tail else None,
        "magnetization_uB_last": mags[-1] if mags else None,
        "seconds_per_iteration": round((cpu[-1] - cpu[0]) / (len(cpu) - 1), 1) if len(cpu) > 1 else None,
        "qe_stop": "Maximum CPU time exceeded" if "Maximum CPU time exceeded" in text else None,
        "config_written": "Writing config" in text or "Writing all to output data dir" in text,
    }
(HERE / "trajectories.json").write_bytes((json.dumps(out, indent=2) + "\n").encode())
print(json.dumps(out["runs"], indent=1))
