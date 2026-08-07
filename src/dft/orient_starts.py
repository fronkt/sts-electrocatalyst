#!/usr/bin/env python3
"""Off-mirror-plane *OOH restarts: break the symmetry trap (docs/41 §2e, P10).

The defect
----------
`hea_oer.surfaces._adsorbate` defines every OER adsorbate with **y ≡ 0**::

    OOH -> Atoms("OOH", positions=[[0,0,0], [1.1,0,0.9], [1.4,0,1.85]])

and `surfaces_rutile.add_oer_adsorbate_at` places it at (x_cus, y_cus). So every
adsorbate in the entire campaign starts exactly on the rutile(110) mirror plane
y = y_cus, which is an exact symmetry of the slab. `pw.x` uses that mirror to
reduce 32 k-points to 15 irreducible — and then symmetrises the forces onto it.

Verified directly from the outputs, not inferred: over **all** ionic steps of
`runs/Ru_anchor/s0_OOH.out` (68), `runs/Ir_anchor/s0_OOH.out` (60),
`runs/Ru_anchor/s0_OH.out` (33) and `runs/Cr_slab/s0_OOH.out` (82), the maximum
|F_y| on any adsorbate atom is **exactly 0.0000000000 Ry/au**, while other atoms
in the same runs carry |F_y| up to 0.049 Ry/au.

Every adsorbate relaxation in this campaign was therefore a constrained
optimisation in a 2-D (x, z) subspace. The "textbook" convergence the anchors are
credited with in docs/32 — fmax 0.0014–0.0019 Ry/au — is convergence *inside* that
constraint. The multi-start machinery in `surfaces_rutile.adsorbate_starts` varies
only the radial M–O distance (`PULL_TO`), so it never leaves the plane either,
which is why docs/38 could measure it as worth ≤3 mV.

This is the same failure class the campaign has already been bitten by twice — the
trapped Cr *O (1.396 eV above the true minimum) and the desorbed *OOH on Mn/Fe/Ni —
except that a numerical QC gate cannot see it at all, because the constrained
optimum is a genuine stationary point of the constrained problem.

The fix
-------
Restart *OOH from orientations rotated **off** the mirror plane, with `nosym` and
`noinv` set so `pw.x` cannot symmetrise the forces back onto it. Cost: irreducible
k goes 15 -> 32, so roughly 2x the original job, not 5x.

Usage
-----
  PYTHONPATH=src python src/dft/orient_starts.py runs/Ru_anchor \
      --job s0_OOH --n-slab 18 --yaw 90 270 --outdir runs/probe/Ru_orient
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_decks import (parse_input_deck, parse_final_coordinates,  # noqa: E402
                         relax_final_energy_ev, write_probe, parse_variant)


def yaw_adsorbate(positions, n_slab, deg, flip_h=False):
    """Rotate the adsorbate about the vertical axis through its binding atom.

    The binding atom (first adsorbate atom) is left exactly where the production
    relaxation put it, so the M-O distance -- the one coordinate the existing
    multi-start already explored -- is unchanged. Only the orientation moves, which
    is precisely the degree of freedom the mirror plane froze.
    """
    out = [list(p) for p in positions]
    ax, ay = positions[n_slab][1], positions[n_slab][2]
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    for i in range(n_slab, len(positions)):
        dx, dy = positions[i][1] - ax, positions[i][2] - ay
        out[i][1] = ax + c * dx - s * dy
        out[i][2] = ay + s * dx + c * dy
    if flip_h:  # mirror the terminal H through the O-O axis plane
        out[-1][3] = 2.0 * out[-2][3] - out[-1][3]
    return [tuple(p) for p in out]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rundir")
    ap.add_argument("--job", default="s0_OOH")
    ap.add_argument("--n-slab", type=int, required=True)
    ap.add_argument("--yaw", type=float, nargs="+", default=[90.0, 270.0])
    ap.add_argument("--flip-h", action="store_true")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--pseudo-dir", default="/usr/share/espresso/pseudo")
    ap.add_argument("--scratch", default="./tmp")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    deck = parse_input_deck(os.path.join(a.rundir, a.job + ".in"))
    pos, prov = parse_final_coordinates(os.path.join(a.rundir, a.job + ".out"))
    e_ref = relax_final_energy_ev(os.path.join(a.rundir, a.job + ".out"))
    assert pos and len(pos) == len(deck["positions"]), "coordinate round trip failed"
    n_ads = len(pos) - a.n_slab
    print(f"{a.rundir}/{a.job}: {len(pos)} atoms, {n_ads} adsorbate, geometry {prov}")
    print(f"  on-record relaxed E = {e_ref:.4f} eV")

    os.makedirs(a.outdir, exist_ok=True)
    man = {"source_run": a.rundir, "job": a.job, "n_slab": a.n_slab,
           "note": ("Off-mirror-plane *OOH restarts. The production relaxation had "
                    "max|F_y| = 0 on every adsorbate atom at every ionic step, i.e. it "
                    "was constrained to the y = y_cus mirror plane. These decks set "
                    "nosym/noinv so pw.x cannot symmetrise the forces back onto it."),
           "on_record_energy_ev": e_ref, "jobs": []}

    deck["nosym"] = True  # force nosym/noinv into the emitted deck
    for y in a.yaw:
        tag = f"yaw{int(y)}" + ("_hflip" if a.flip_h else "")
        newpos = yaw_adsorbate(pos, a.n_slab, y, flip_h=a.flip_h)
        moved = max(abs(newpos[i][j] - pos[i][j])
                    for i in range(a.n_slab, len(pos)) for j in (1, 2, 3))
        text, meta = write_probe(deck, newpos, parse_variant("base"),
                                 f"{a.job}__{tag}", a.pseudo_dir, a.scratch,
                                 calculation="relax")
        fn = f"{a.job}__{tag}.in"
        with open(os.path.join(a.outdir, fn), "w", newline="\n") as f:
            f.write(text)
        man["jobs"].append(dict(job=a.job, variant=tag, file=fn,
                                yaw_deg=y, flip_h=a.flip_h,
                                max_adsorbate_displacement_A=round(moved, 4),
                                relax_reference_ev=e_ref))
        print(f"  {fn:28s} yaw {y:5.0f} deg  max adsorbate move {moved:.3f} A")

    with open(os.path.join(a.outdir, "probe_manifest.json"), "w") as f:
        json.dump(man, f, indent=2)
    print(f"-> {a.outdir}  ({len(man['jobs'])} decks)")
    print("\nPRE-REGISTERED READOUT (docs/41 P10): dG_OOH(off-plane) - dG_OOH(on record).")
    print("  drop >= 0.30 eV  -> the on-record *OOH is a symmetry-trapped basin, and the")
    print("                      Ir scaling anomaly is a basin failure, not coverage.")
    print("  drop <  0.10 eV  -> the symmetry trap is exonerated at DFT level.")


if __name__ == "__main__":
    main()
