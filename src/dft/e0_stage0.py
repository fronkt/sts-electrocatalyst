"""Stage 0 of R3: is the UMA/DFT disagreement a reference-energy (E0) problem?

The R3 plan (docs/28 §7, tasks/todo.md) budgeted a free "Stage 0" control before
paying for a fine-tune: refit only the per-element reference energies E0 on the 785
archived QE frames and see how much of the disagreement that removes. The MACE naive
fine-tune recipe re-initialises E0, so it seemed like the cheapest thing to rule out.

It is a no-op, and provably so.

The CHE reference is stoichiometrically closed by construction
(`hea_oer.referencing._REF_COEFFS`):

    ΔG(*OH)  = [E(*OH)  − E(*)] − (  E_H2O − ½ E_H2) + 0.35
    ΔG(*O)   = [E(*O)   − E(*)] − (  E_H2O −   E_H2) + 0.05
    ΔG(*OOH) = [E(*OOH) − E(*)] − (2 E_H2O − 3/2 E_H2) + 0.40

Add an arbitrary per-element shift Σ_e n_e·a_e to every energy the model predicts.
For *OH the adslab-minus-slab difference carries exactly +1 O +1 H, so it picks up
a_O + a_H, while the reference term picks up (a_O + 2a_H) − a_H = a_O + a_H. They
cancel identically. Same for *O and *OOH:

    δΔG(*OH)  = (a_O + a_H)   − [(a_O + 2a_H) − a_H]        = 0
    δΔG(*O)   = (a_O)         − [(a_O + 2a_H) − 2a_H]       = 0
    δΔG(*OOH) = (2a_O + a_H)  − [2(a_O + 2a_H) − 3a_H]      = 0

The metal coefficient a_M cancels too: adslab and slab hold the same metal count.

Three consequences, and they are the actual Stage 0 deliverable:

  1. **Stage 0 cannot settle anything** — there is no E0 that changes any ΔG, so the
     control experiment has no informative outcome. Do not spend time on it.
  2. **ρ = −1.00 for the oc22 head is not a reference-energy artefact.** The whole
     composition-linear subspace of model error is projected out of the descriptor,
     so the anti-correlation lives in geometry-dependent, local-chemistry error —
     the relative binding of *O vs *OH across metals. Only a real fine-tune touches
     that. A per-element constant also has zero force, so relaxed geometries are
     untouched as well; this is not merely a ranking invariance.
  3. **The R3 acceptance gate must be the CHE observable, not energy MAE.** A
     fine-tune can cut total-energy MAE dramatically by absorbing the
     composition-linear part while leaving every η exactly where it was. Rank
     correlation on η is the only honest gate. (todo.md already specifies
     Spearman ≥ 0.8 — this is why that is the right choice, not energy MAE.)

Run as a script to verify (2) numerically on the stored records rather than trusting
the algebra: it applies a large random per-element shift to every stored energy and
re-derives η through the real `hea_oer.referencing` code path.

    PYTHONPATH=src python src/dft/e0_stage0.py runs
"""
from __future__ import annotations

import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from hea_oer.referencing import delta_G  # noqa: E402
from hea_oer.descriptors import oer_overpotential  # noqa: E402

#: Atom counts per structure for the rutile MO2(110) 18-atom slab used throughout.
#: Confirmed against qe_qc `nat`: slab 18, +O 19, +OH 20, +OOH 21.
COUNTS = {
    "slab": {"M": 6, "O": 12, "H": 0},
    "O":    {"M": 6, "O": 13, "H": 0},
    "OH":   {"M": 6, "O": 13, "H": 1},
    "OOH":  {"M": 6, "O": 14, "H": 1},
    "H2O":  {"M": 0, "O": 1,  "H": 2},
    "H2":   {"M": 0, "O": 0,  "H": 2},
}


def shift(counts: dict, a_M: float, a_O: float, a_H: float) -> float:
    return counts["M"] * a_M + counts["O"] * a_O + counts["H"] * a_H


def eta_from(E_slab, E_O, E_OH, E_OOH, E_H2O, E_H2) -> tuple[float, int, dict]:
    dG = {s: delta_G(E_slab, E, s, E_H2O, E_H2)
          for s, E in (("OH", E_OH), ("O", E_O), ("OOH", E_OOH))}
    res = oer_overpotential(dG["OH"], dG["O"], dG["OOH"])
    return res.overpotential, res.potential_limiting_step, dG


def recalibrated(rec: dict, a_M: float, a_O: float, a_H: float):
    """η after adding a per-element E0 shift to every energy in the record."""
    return eta_from(
        rec["E_slab"] + shift(COUNTS["slab"], a_M, a_O, a_H),
        rec["E_O"]   + shift(COUNTS["O"],    a_M, a_O, a_H),
        rec["E_OH"]  + shift(COUNTS["OH"],   a_M, a_O, a_H),
        rec["E_OOH"] + shift(COUNTS["OOH"],  a_M, a_O, a_H),
        rec["E_H2O"] + shift(COUNTS["H2O"],  a_M, a_O, a_H),
        rec["E_H2"]  + shift(COUNTS["H2"],   a_M, a_O, a_H),
    )


def main(root: str = "runs") -> int:
    # Deliberately large and asymmetric: if any composition-linear term survived,
    # shifts of this size would move η by several volts.
    A_M, A_O, A_H = -3.7591, 2.4113, -1.0827

    files = sorted(glob.glob(os.path.join(root, "*_slab", "uma_eta_1p2_oc22.json")) +
                   glob.glob(os.path.join(root, "*_anchor", "uma_eta_1p2_oc22.json")))
    if not files:
        print(f"no uma_eta_1p2_oc22.json under {root}/")
        return 1

    print(f"per-element E0 shift applied: a_M={A_M}  a_O={A_O}  a_H={A_H} eV/atom")
    print(f"{'system':<10} {'eta_before':>11} {'eta_after':>10} {'|delta|':>10} "
          f"{'pls':>4} {'dG_O-dG_OH before':>19} {'after':>9}")
    worst = 0.0
    for f in files:
        rec = json.load(open(f))
        comp = rec["composition"]
        e0, p0, d0 = eta_from(rec["E_slab"], rec["E_O"], rec["E_OH"], rec["E_OOH"],
                              rec["E_H2O"], rec["E_H2"])
        e1, p1, d1 = recalibrated(rec, A_M, A_O, A_H)
        worst = max(worst, abs(e1 - e0))
        assert p0 == p1, f"{comp}: potential-limiting step moved {p0} -> {p1}"
        print(f"{comp:<10} {e0:>11.6f} {e1:>10.6f} {abs(e1-e0):>10.2e} {p0:>4} "
              f"{d0['O']-d0['OH']:>19.6f} {d1['O']-d1['OH']:>9.6f}")

    print(f"\nlargest |delta eta| across {len(files)} systems: {worst:.3e} eV")
    print("The CHE reference is stoichiometrically closed, so the entire "
          "composition-linear\nsubspace of model error is projected out of every "
          "dG. E0 refitting is a no-op:\nit cannot change eta, the ranking, or "
          "(having zero force) the relaxed geometry.")
    return 0 if worst < 1e-9 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "runs"))
