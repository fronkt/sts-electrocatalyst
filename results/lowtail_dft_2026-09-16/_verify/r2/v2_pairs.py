"""Independent verifier: seed-0 OOH builder/pull2.10 pair energies (DFT vs MACE)."""
import json, re, hashlib
from pathlib import Path
import numpy as np
from ase import Atoms

ROOT = Path(__file__).resolve().parents[4]
RY = 13.605693122


def E(path):
    t = Path(path).read_text(errors="replace")
    return float(re.findall(r"^!\s+total energy\s+=\s+(\S+)\s+Ry", t, re.M)[-1]) * RY


def deck_pos(path):
    lines = Path(path).read_text().splitlines()
    j = [k for k, l in enumerate(lines) if l.strip().startswith("ATOMIC_POSITIONS")][0]
    nat = int(re.search(r"nat\s*=\s*(\d+)", "\n".join(lines)).group(1))
    return [l.split()[0] for l in lines[j + 1:j + 1 + nat]], np.array([[float(x) for x in l.split()[1:4]] for l in lines[j + 1:j + 1 + nat]])


H = ROOT / "runs/hea"
jobs = {
    "hc_atomic_baseline": ("controls_2026-09-07/hc__leader_builder__atomic__baseline", "controls_2026-09-07/hc__leader_pull2.10__atomic__baseline"),
    "hc_atomic_metal_alternating": ("controls_2026-09-07/hc__leader_builder__atomic__metal_alternating", "controls_2026-09-07/hc__leader_pull2.10__atomic__metal_alternating"),
    "hc_atomic_fragment": ("controls_2026-09-07/hc__leader_builder__atomic__fragment", "controls_2026-09-07/hc__leader_pull2.10__atomic__fragment"),
    "hc_atomic_metal_alternating_fragment": ("controls_2026-09-07/hc__leader_builder__atomic__metal_alternating_fragment", "controls_2026-09-07/hc__leader_pull2.10__atomic__metal_alternating_fragment"),
    "hc_ortho_fragment": ("controls_2026-09-07/hc__leader_builder__ortho__fragment", "controls_2026-09-07/hc__leader_pull2.10__ortho__fragment"),
    "hc_ortho_metal_alternating_fragment": ("controls_2026-09-07/hc__leader_builder__ortho__metal_alternating_fragment", "controls_2026-09-07/hc__leader_pull2.10__ortho__metal_alternating_fragment"),
    "hn_ortho_tight": ("numerical_2026-09-08/hn__leader_builder__ortho__tight", "numerical_2026-09-08/hn__leader_pull2.10__ortho__tight"),
    "hs_ortho_wfc": ("sensitivity_2026-09-09/hs__leader_builder__ortho__wfc", "sensitivity_2026-09-09/hs__leader_pull2.10__ortho__wfc"),
    "hs_ortho_rho": ("sensitivity_2026-09-09/hs__leader_builder__ortho__rho", "sensitivity_2026-09-09/hs__leader_pull2.10__ortho__rho"),
    "hd_hn_atomic_replacement": ("ieee_2026-09-09/hd__leader_builder__atomic__ieee_repro", "numerical_2026-09-08/hn__leader_pull2.10__atomic__tight"),
}
replay = json.loads((ROOT / "results/cr_site_chains_2026-09-06/leader_ooh_replay.json").read_text())
geo = {a["start"]: a["geometry"] for a in replay["attempts"]}

gaps = {}
coord_ok = {}
for k, (b, p) in jobs.items():
    for tag, stem in (("builder", b), ("pull2.10", p)):
        deck = H / (stem + ".run.in")
        if not deck.exists():
            deck = H / (stem + ".in")
        s, pos = deck_pos(deck)
        g = geo[tag]
        coord_ok[stem] = bool(s == g["symbols"] and np.array_equal(pos, np.array(g["positions_A"])))
    gaps[k] = E(H / (p + ".out")) - E(H / (b + ".out"))

from mace.calculators import mace_mp
import torch
torch.set_num_threads(2)
calc = mace_mp(model=str(Path.home() / ".cache/mace/macempa0mediummodel"), device="cpu", default_dtype="float64")
mE = {}
for tag in ("builder", "pull2.10"):
    g = geo[tag]
    a = Atoms(g["symbols"], positions=g["positions_A"], cell=g["cell_A"], pbc=True)
    a.calc = calc
    mE[tag] = float(a.get_potential_energy())
mgap = mE["pull2.10"] - mE["builder"]
vals = list(gaps.values())
spin = {k: v for k, v in gaps.items() if k.startswith("hc_atomic") or k.startswith("hc_ortho")}
res = dict(gaps=gaps, coord_ok=coord_ok, mace=mE, mace_stored=dict(builder=geo["builder"]["energy_eV"], pull=geo["pull2.10"]["energy_eV"]),
           mace_gap=mgap, dft_min=min(vals), dft_max=max(vals), diff_min=min(vals) - mgap, diff_max=max(vals) - mgap,
           sign_agree=sum(np.sign(v) == np.sign(mgap) for v in vals), n=len(vals),
           spin_spread_all=max(vals) - min(vals),
           spin_spread_hc=max(spin.values()) - min(spin.values()),
           tight_minus_frag=gaps["hn_ortho_tight"] - gaps["hc_ortho_fragment"],
           wfc_minus_tight=gaps["hs_ortho_wfc"] - gaps["hn_ortho_tight"],
           rho_minus_tight=gaps["hs_ortho_rho"] - gaps["hn_ortho_tight"])
res["sign_agree"] = int(res["sign_agree"])
Path(__file__).with_name("v2_pairs.json").write_text(json.dumps(res, indent=1))
print(json.dumps(res, indent=1))
