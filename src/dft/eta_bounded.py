"""eta for a metal whose `*OOH` never converged, derived as a bound rather than a value.

Why this module exists
----------------------
The 2026-08-03/04 campaign bought five DFT jobs to take the tier from n = 5 to n = 7.
Three converged; both `*OOH` jobs did not (Ni failed SCF three times, Co ran out of
credit at 16 ionic steps). `dft_reference()` therefore excludes Ni and Co, correctly --
neither has a complete, chemically valid CHE chain.

But eta does not always need one. The four CHE steps are

    dG1 = dG_OH
    dG2 = dG_O - dG_OH
    dG3 = dG_OOH - dG_O
    dG4 = G_TOTAL - dG_OOH          (G_TOTAL = 4.92 eV = 4 x 1.23 V)

and eta = max(dG1..dG4) - 1.23. The key identity is that dG3 and dG4 **sum to a quantity
that does not contain dG_OOH at all**:

    dG3 + dG4 = G_TOTAL - dG_O

So once dG_OH and dG_O are measured, the only way for step 3 or 4 to be the maximum is
for one of them to exceed max(dG1, dG2) while the pair sums to G_TOTAL - dG_O -- which
forces the other one deeply negative, i.e. dG_OOH outside an explicitly computable
window. If that window comfortably contains every dG_OOH the campaign has ever measured
(3.65-4.94 eV across six metals), eta is determined without the `*OOH` job.

This is deliberately NOT the universal scaling relation (dG_OOH ~ dG_OH + 3.2 +/- 0.2).
docs/32 s4 measured a **+0.45 eV violation of that relation for IrO2** in this very
pipeline, so leaning on it here would repeat the campaign's characteristic mistake. The
bound below uses only measured quantities plus the observed range of dG_OOH.

Worked outcomes (docs/35):

    Ni   dG_OH 2.314  dG_O 4.556   window [2.61, 6.87]   width 4.26 eV   SAFE
    Co   dG_OH 1.774  dG_O 3.382   window [3.15, 5.16]   width 2.01 eV   TIGHT

Ni's window is wide enough that no plausible dG_OOH threatens it. Co's upper edge (5.16)
sits only 0.22 eV above the largest dG_OOH on record (Mn, 4.94), so Co needed the extra
evidence its partial relaxation supplies: a relaxation stopped early sits ABOVE its own
minimum, so the dG_OOH it implies is an **upper bound** on the converged value. Co's
partial gives 4.571 eV, closing the upper edge rigorously.

    PYTHONPATH=src python src/dft/eta_bounded.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

G_TOTAL = 4.92
U_EQ = 1.23
#: dG_OOH observed across every metal with a converged, chemically valid *OOH.
#: Ir 3.652, Ru 3.709, Cr 4.799, Fe 4.845, Mn 4.942 (docs/32 s3).
OBSERVED_DG_OOH = (3.652, 4.942)


def eta_window(dG_OH: float, dG_O: float) -> dict:
    """eta assuming steps 3/4 are not limiting, plus the dG_OOH window where that holds.

    Returns `lo`/`hi`: dG_OOH strictly inside (lo, hi) => eta = max(dG1, dG2) - 1.23.
    """
    dG1, dG2 = dG_OH, dG_O - dG_OH
    mx = max(dG1, dG2)
    # dG3 > mx  <=>  dG_OOH > dG_O + mx
    hi = dG_O + mx
    # dG4 > mx  <=>  dG_OOH < G_TOTAL - mx
    lo = G_TOTAL - mx
    return dict(dG1=dG1, dG2=dG2, dG3_plus_dG4=G_TOTAL - dG_O, max_12=mx,
                eta=mx - U_EQ, pls=1 if dG1 >= dG2 else 2, lo=lo, hi=hi,
                margin_hi=hi - OBSERVED_DG_OOH[1], margin_lo=OBSERVED_DG_OOH[0] - lo)


#: Metals whose `*OOH` job failed, so eta comes from the bounded identity above rather
#: than a complete CHE chain (docs/35 s3), with the partial-relaxation output that
#: closes the upper edge where one exists.
BOUNDED = (("Ni", "Ni_slab", None),
           ("Co", "Co_slab", "s0_OOH.out.stageB-partial"))


def _partial_dG_OOH(path: str, E: dict) -> float | None:
    """dG_OOH implied by a relaxation that was stopped early — an UPPER bound.

    A run halted above its own minimum can only overestimate the converged energy,
    which is what closes Co's tight high edge (docs/35 s3).
    """
    from hea_oer.referencing import delta_G
    if not os.path.exists(path):
        return None
    Es = [float(l.split("=")[1].split("Ry")[0]) for l in open(path, errors="ignore")
          if l.startswith("!    total energy")]
    if not Es:
        return None
    return delta_G(E["slab"], Es[-1] * 13.605693122, "OOH", E["H2O"], E["H2"])


def bounded_eta(root: str, dirname: str, partial: str | None = None) -> dict | None:
    """eta for a metal with a QC-passing `*OH` and `*O` but no usable `*OOH`.

    Returns None if any required state fails QC — absence, never a guessed number.
    """
    from hea_oer.referencing import delta_G
    from dft.qe_qc import trusted_energy_ev

    E = {s: trusted_energy_ev(os.path.join(root, dirname, s + ".out"),
                              os.path.join(root, dirname, s + ".in"))
         for s in ("slab", "s0_O", "s0_OH", "H2O", "H2")}
    if any(v is None for v in E.values()):
        return None
    dG_OH = delta_G(E["slab"], E["s0_OH"], "OH", E["H2O"], E["H2"])
    dG_O = delta_G(E["slab"], E["s0_O"], "O", E["H2O"], E["H2"])
    w = eta_window(dG_OH, dG_O)
    ub = _partial_dG_OOH(os.path.join(root, dirname, partial), E) if partial else None
    w.update(dG_OH=dG_OH, dG_O=dG_O, dG_OOH=None, source="bounded",
             upper_bound_dG_OOH=ub, hi_closed=bool(ub is not None and ub < w["hi"]))
    return w


def reference_tier(root: str = "runs") -> dict:
    """The **n = 7 tier of record** — eta per metal, however it was established.

    Five metals have a complete, QC-gated CHE chain; Ni and Co do not, because both
    `*OOH` jobs failed (docs/35 s3), and their eta comes from the bounded identity in
    this module. Both routes are QC-gated and both are published numbers, but until
    now they lived in two modules and no single call returned the tier docs/35 quotes
    — `score_n7.py` on its own reports "nothing to score". Anything scoring a model
    against the DFT should call this, so it never has to decide which half to trust.

    Each record carries `source` = "chain" | "bounded".
    """
    from dft.mlip_eval import dft_reference

    tier = {m: dict(v, source="chain") for m, v in dft_reference(root).items()}
    for metal, dirname, partial in BOUNDED:
        if metal in tier:
            continue
        w = bounded_eta(root, dirname, partial)
        if w is not None:
            tier[metal] = w
    return tier


def report(name: str, dG_OH: float, dG_O: float, partial_dG_OOH: float | None = None) -> dict:
    w = eta_window(dG_OH, dG_O)
    print(f"\n{name}:  dG_OH {dG_OH:.3f}   dG_O {dG_O:.3f}")
    print(f"  dG1 {w['dG1']:.3f}   dG2 {w['dG2']:.3f}   dG3+dG4 {w['dG3_plus_dG4']:.3f} (measured)")
    print(f"  eta = {w['eta']:.3f} V  (pls = {w['pls']})  provided dG_OOH in "
          f"({w['lo']:.2f}, {w['hi']:.2f}) eV")
    print(f"  observed dG_OOH across the tier: {OBSERVED_DG_OOH[0]}-{OBSERVED_DG_OOH[1]} eV")
    print(f"  margin: {w['margin_lo']:+.2f} eV at the low edge, {w['margin_hi']:+.2f} eV at the high edge")
    if partial_dG_OOH is not None:
        ok = partial_dG_OOH < w["hi"]
        print(f"  partial relaxation gives dG_OOH <= {partial_dG_OOH:.3f} eV (upper bound, "
              f"the relax stopped above its minimum)")
        print(f"    -> high edge {'CLOSED rigorously' if ok else 'NOT closed'}")
        w["upper_bound_dG_OOH"] = partial_dG_OOH
        w["hi_closed"] = ok
    return w


def main():
    out = {}
    for metal, d, partial in BOUNDED:
        w = bounded_eta("runs", d, partial)
        if w is None:
            print(f"{metal}O2(110): missing a QC-passing state, skipping")
            continue
        out[metal] = report(f"{metal}O2(110)", w["dG_OH"], w["dG_O"],
                            w.get("upper_bound_dG_OOH"))
    tier = reference_tier("runs")
    print(f"\n{'='*60}\nTIER OF RECORD  n = {len(tier)}\n{'='*60}")
    for m, v in sorted(tier.items(), key=lambda kv: kv[1]["eta"]):
        print(f"  {m:<3} eta = {v['eta']:.3f} V   pls = {v['pls']}   ({v['source']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
