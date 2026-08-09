#!/usr/bin/env python3
"""Block 1C — the Hessian pilot. Decide whether the lead contribution has a proof.

Why this exists
---------------
The campaign's lead contribution (tasks/plan-maximal-rigor.md §1) is an audit of three
convergence-invisible error classes. Its load-bearing *novel* object is a Hessian:
Goniakowski & Gillan, Surf. Sci. (1995) — an UNVERIFIED citation that must be read before
it is relied on — reportedly already noted on rutile(110) that symmetric adsorbed
configurations are unstable to symmetry lowering. So "we found the symmetry trap" is dead
as a discovery (novelty ledger, §6). What survives is the quantified audit **plus** a proof
that the constrained geometries the field publishes are literal saddle points rather than
minima. No such proof exists for these states, and if the spectrum comes back all-real the
lead loses its proof and the paper reweights to S1 + S4. That is risk R3, and R3 has to be
known in Week 1, not Week 6 — hence a two-state pilot before the 378-SCF full audit (2B).

The rule this script serves
---------------------------
**docs/43 §3 (P14) and §3-A (amendment 1, 2026-08-09) are the pre-registration, and they
are the only one.** This file does not restate them, quote them, or instruct anybody to
paste anything into them. Earlier revisions of this script and of `hessian_analyze.py`
carried their own `PREREG` block; it contradicted docs/43 in six places and it is deleted.
A rule that exists in two places is a rule that will be read in whichever version suits the
result (docs/43 amendment 1, "A rule this amendment establishes").

    read it:   docs/43-prereg-week1-factorial.md, §3 and §3-A
    print it:  python src/dft/hessian_analyze.py --print-prereg
               (which reads those two sections out of docs/43 — it does not hold a copy)

The two states, and why exactly these
-------------------------------------
    Ir  *OOH   runs/Ir_anchor/s0_OOH.out        eta 0.781 V, on the record since docs/32.
                                                This is the state P10 found a -0.291 eV
                                                escape from at yaw90 — the one place the
                                                campaign already has independent evidence
                                                that the mirror geometry is not the best
                                                basin. nspin = 1, no Hubbard U: nothing
                                                about it can be taken back by a later U or
                                                magnetic decision.  ** RUNS NOW. **
    Cr  *OOH   runs/probe/Cr_basin/s0_OOH.out   The BASIN-CORRECTED geometry, i.e. the one
                                                that is actually in tier_v2 (docs/41 §6f).
                                                *** NOT runs/Cr_slab/s0_OOH.out ***, which
                                                is a known-wrong magnetic solution 178.58
                                                meV high. Cr's corrected eta = 0.330 V sits
                                                9 meV above its own scaling floor, so this
                                                *OOH is the state that sets c_Cr; if it is
                                                a saddle, the floor moves too.
                                                ** HELD — see the scope trap below. **

Both are exactly mirror-symmetric about y = y_cus, verified here rather than assumed: the
guard below refuses to write unless every adsorbate atom shares one y to 1e-6 A and the
source relaxation printed max|F_y| = 0 on every adsorbate atom.

Scope, and why Cr is held (docs/43 §3-A.7)
------------------------------------------
Every verdict this pilot can produce is scoped to **q = 0, in the 1x1 cell, at 1 ML**, and
that scope is stamped into the manifest and printed by the analyser rather than left to the
report to remember. The reason is measured, not stylistic: at 1x1 the adsorbate touches its
own periodic image along the cus row. This script now measures the minimum-image adsorbate
contact from the emitted geometry and refuses to be quiet about it —

    Cr  *OOH   H...O = 1.338 A, O...O = 2.399 A   a low-barrier hydrogen bond
    Ir  *OOH   O...O = 2.516 A                    the same class, milder

The two modes most likely to come back imaginary — the OOH yaw and the H torsion — are on Cr
governed by that image contact rather than by the mirror constraint the paper is about, so a
CONFIRMED on Cr at 1x1 would be attributed to the symmetry trap when its cause is the
coverage. A proton in a 2.40 A O...O bond is also the worst case for a harmonic finite
difference. Block 1A is concurrently deciding whether the 1x1 cell is admissible at all.

So **Cr is held until 1A returns its cell verdict** and is then run in the chosen production
cell; building it requires `--cell-verdict-1a "<the verdict>"`, which is recorded in the
manifest. **Ir runs now**: it is the milder contact and it is the state with the known
-291 meV escape, so it is the one the saddle-point claim most needs.

Which decks decide the verdict (docs/43 §3-A.8, corrected by amendment 3)
-------------------------------------------------------------------------
At an exactly mirror-symmetric reference the y block decouples exactly, so F_y is identically
zero in every +/-x and +/-z deck and all 18 y/xz cross-elements of the Hessian are
structurally zero. **1C's verdict rests on the y block.** The +/-x and +/-z decks are
still emitted, and their stated purpose is now block 2B's in-house ZPE/-TS table, not this
verdict. [U15] The ym decks buy NO sqrt(2) noise gain and NO independent noise realisation:
each ym deck is the EXACT mirror of its yp partner (verified to 8.9e-16 A, slab included),
pw.x is deterministic, so F(ym) is the mirror of F(yp) — SCF convergence error included —
and the central difference reduces algebraically to the one-sided difference (docs/43
amendment 3). docs/43 am.4 §7 items 1-2 resolve what follows: **the y-block of H is built
from the +dy FORWARD difference exclusively, with the reference forces as the base point;
the ym decks are RETAINED and RUN solely as the Q6 mirror-identity control and NEVER enter
H.** The identity F_y(ym) = -F_y(yp), F_x/F_z(ym) = +F_x/F_z(yp) on the raw force blocks
is the ONLY available test of the Hessian DIAGONAL, and hessian_analyze.py enforces it as
gate Q6 (finding N34). `axes_purpose` in the manifest records this so a reader cannot
mistake the 12 in-plane decks for evidence the verdict used.

Method, and the four traps in it
--------------------------------
Partial Hessian, ADSORBATE ATOMS ONLY, finite differences of forces: the x/z rows by
central +/- pairs, the y rows by the +dy FORWARD difference with the reference forces as
the base point (docs/43 am.4 §7 items 1-2 — the ym decks run solely as the Q6 mirror
control and never enter H).

    3 adsorbate atoms x 3 cartesian x 2 signs = 18 displacements
                                              +  1 reference
                                              = 19 SCFs per state, 38 for the pilot.

(The plan's "36 SCFs" omitted the reference. The reference is not optional: it is the
baseline for the magnetisation guard, the base point of every y-row forward difference
(am.4 §7 item 2), and the only place the residual gradient at the on-record geometry gets
measured. This script prints the arithmetic for whatever it actually generates — do not
trust the number in the plan, trust the one it prints.)

**Trap 1 — conv_thr, and it is now MEASURED rather than extrapolated.** QE's default 1e-8 is
not tight enough, and the arithmetic says so. The Hellmann-Feynman force error is *linear* in
the density error while the total-energy error is *quadratic*, so if conv_thr bounds the
energy estimate at eps the force noise goes as sigma_F ~ C*sqrt(eps) with C of order
1 Ry/bohr (ORDER-OF-MAGNITUDE ASSUMPTION — the analysis script measures C for real, from the
Hessian asymmetry, and reports it). A +/- pair of displaced SCFs with INDEPENDENT errors —
the +/-x and +/-z pairs — gives a force-constant noise sigma_k = sqrt(2)*sigma_F/(2*delta).
[U15] The +/-y pair is NOT such a pair: the ym run is the exact mirror of the yp run
(docs/43 amendment 3), its error is the same realisation mirrored, so there is no averaging
on the block the verdict rests on. Per am.4 §7 item 2 the y rows of H are the +dy FORWARD
difference (F(+dy) - F(ref))/delta — two independent SCF evaluations, so the y-row noise
is sqrt(2)*sigma_F/delta, twice the central-pair sigma_F/(sqrt(2)*delta) of the x/z rows.
At delta = 0.01 A, 2*delta = 0.0377946 bohr.
Converting to the frequency of an oxygen atom (kappa_50 = 3.027e-3 Ry/bohr^2 is a 50 cm^-1
oscillator of mass 16 amu):

    conv_thr    sigma_F (Ry/bohr)   sigma_k (Ry/bohr^2)   equivalent nu on O
    1e-6              1e-3               3.7e-2               176 cm^-1
    1e-8  (default)   1e-4               3.7e-3                56 cm^-1     <-- AT threshold
    1e-10 (ours)      1e-5               3.7e-4                18 cm^-1
    1e-12             1e-6               3.7e-5                 6 cm^-1

18 cm^-1 is the ONE-SIGMA figure and it is carried by OXYGEN. The rule scores at 3 sigma and
the out-of-plane modes of *OOH are hydrogen-dominated, so the number that governs is the
3-sigma floor on an H-carried mode, ~= i111 cm^-1 at the design sigma_F (docs/43 §3-A.3).
That is why §3-A adds an UNDERPOWERED verdict at i80 cm^-1: at the design noise this pilot is
close to being unable to see the mode it exists to detect, and blindness is not a null.

**1e-10 is reachable. This was measured, not assumed.** A single registered throwaway
feasibility probe, `runs/probe/Ir_hess/s0_OOH__hess_ref` (docs/43 amendment 1; its energy is
NOT reused as the Hessian reference), was released before the rest of the block and ran to
completion at NP = 20, -nk 4:

    convergence has been achieved in  30 iterations
    !    total energy              =   -1674.09176149 Ry
         estimated scf accuracy    <          6.9E-11 Ry

  * **30 iterations from a fresh atomic-superposition density**, against the 35 this file
    used to project (23 measured to 1e-6 plus 12 extrapolated). The projection was 17% HIGH,
    which is the first time in this project an estimate came in high rather than low.
  * **No plateau.** The tail decays FASTER than the 0.35 decades/iteration measured on
    BFGS-extrapolated cycles: 1.0e-8 -> 3.8e-9 -> 1.0e-9 -> 3.1e-10 -> 6.9e-11 over
    iterations 26-30 is 0.55 decades/iteration.
  * **The Davidson threshold never hit QE's clamp.** ethr = 0.1*dr2/nelec with nelec = 175,
    and the deepest printed value was `ethr = 1.79E-13` on the last iteration — above the
    `MAX(ethr, 1e-13)` clamp. So the last decades ran against a real, still-shrinking
    diagonalisation threshold, not a fixed floor.

**But the registered 1e-12 escalation is NOT demonstrated, and this probe is the reason to
say so out loud.** Converging to 1e-12 needs ethr ~ 0.1*1e-12/175 = 5.7e-16, two and a half
decades below the 1e-13 clamp. The final decades would then run against a FIXED
diagonalisation floor, which is exactly where an `estimated scf accuracy` plateau appears.
1e-12 may still work — the clamp bounds the eigen-residual, not the density — but nothing in
this repository shows that it does. If Q4a fires, the escalation must itself be probed with
one job before 19 are spent on it.

`electron_maxstep = 120` (down from the inherited 200): 30 iterations is the measured cost, so
120 is 4x headroom, and a stall now costs 120 x 21 s = 42 min at NP = 20 instead of 70.

**Trap 2 — nosym AND noinv on EVERY deck, INCLUDING THE REFERENCE.** This is the subtle one
and it is why the reference cannot simply be the existing GATE-1 audit SCF. A +y
displacement destroys the mirror the reference still has. With symmetry on, pw.x would
solve the reference in a 2-operation group at 15 irreducible k-points and the y-displaced
structures in a 1-operation group at 32 — different Brillouin-zone sampling on the two
sides of the same finite difference, and `symvector` would additionally project the
reference forces onto the mirror. The differences would then be inconsistent by an amount
nobody can bound. So every deck here carries nosym/noinv and every deck therefore uses the
full mesh: 8x4x1 -> 32 k-points on Ir, 9x4x1 -> 36 on Cr. hessian_analyze.py refuses to
build a Hessian unless every job reports "No symmetry found" and the identical k count.

**Trap 3 — the magnetic basin.** Each displacement is a separate pw.x invocation from a
fresh atomic-superposition density, which is deliberate: it makes the 19 points independent
so path dependence (the exact defect docs/41 §6d/§6f repaired) cannot propagate down the
list. The price is that a displacement may land in a *different* magnetic solution than the
reference, and its whole force row is then contaminated — the fingerprint is an ASYMMETRIC
Hessian. The manifest records the reference magnetisation and hessian_analyze.py flags any
displacement more than 0.1 mu_B away, reports it, and refuses to average over it. Ir runs
nspin = 1 so the guard is inapplicable there and is reported as such, not as a pass.

**Trap 4 — constrained atoms.** pw.x prints UNCONSTRAINED forces (verified: the frozen
bottom-layer atoms in both source runs carry up to 0.076 Ry/au while the movable fmax is
1.5e-3), so a force row on an if_pos = 0 atom would be meaningless for a Hessian. The guard
refuses to write unless every adsorbate atom carries `1 1 1`. Both states satisfy it.

What this script will NOT do
----------------------------
Every quantity it does not intend to change is compared field by field against the source
deck before a single byte is written — cutoffs, k-mesh, Hubbard U, smearing, occupations,
starting_magnetization, nspin, cell, pseudopotential filenames, species masses, constraint
mask, and the slab coordinates. It raises SystemExit and writes nothing on any mismatch.
The complete list of INTENDED differences from the source deck is exactly seven:

    calculation       'relax' -> 'scf'          (a Hessian is 19 single points)
    prefix            -> per-job                (concurrent jobs must not collide)
    outdir            -> ./tmp                  (queue_r1.sh rewrites this per job anyway)
    conv_thr          1.0d-6 -> 1.0d-10         (Trap 1)
    electron_maxstep  200 -> 120                (Trap 1; 4x the measured 30 iterations)
    nosym/noinv       absent -> .true./.true.   (Trap 2)
    positions         starting -> RELAXED final geometry, one component +/- delta

Cost (one full production-identical SCF, timed today)
-----------------------------------------------------
Everything below is read off `runs/probe/Ir_hess/s0_OOH__hess_ref.out`, which is the real
workload at the real settings — 21 atoms, 32 k-points, nosym+noinv, conv_thr = 1e-10 — not
a cheaper system extrapolated (lessons.md 2026-08-05, three consecutive 2.4-3.5x misses,
every one of them from extrapolating across a system change):

    NP = 20, -nk 4     PWSCF  10m10.73s CPU  10m43.33s WALL
                       electrons 628.54 s WALL / 30 iterations = 20.95 s per iteration
                       init_run 10.07 s, forces 3.80 s

  Ir arm : 19 SCFs x 643 s = **3.4 h wall** at NP = 20, NCONC = 1 (one job at a time on
           20 of the box's 23.04 usable cores). 68 core-hours.

That is the whole Ir arm in an afternoon, and NP = 20 is an exact multiple of -nk 4.

The old NP = 4 / NCONC = 5 plan is NOT recommended and its basis is now known to be shaky.
It rested on 124.5 s/iteration inferred from `probe/Ir_orient/s0_OOH__yaw90.out`, a 654-
iteration BFGS relaxation whose per-iteration figure carries ionic overhead and whatever
else shared that box. Against today's 20.95 s/iteration at 5x the ranks that would be a
5.94x speed-up from a 5x rank increase, i.e. superlinear, i.e. one of the two numbers is
not measuring what it claims. The measured one is today's. If NP = 4 is wanted anyway, time
one job first; do not schedule 19 against an inherited number.

Cr, when 1A releases it, has NOT been timed at these settings. Its per-iteration cost is
nspin = 2 + Hubbard U at 36 k-points and the only honest statement available is that the
`probe/Cr/*__base` runs are ~2.4x Ir per iteration at equal k. Time one Cr SCF before
sizing that arm — that is the same rule this probe was released to obey.

Usage
-----
  PYTHONPATH=src python src/dft/build_hessian_pilot.py --out runs/probe            # Ir only
  PYTHONPATH=src python src/dft/build_hessian_pilot.py --states Cr \
      --cell-label 1x1 \
      --cell-verdict-1a "1x1 ADMISSIBLE; PRODUCTION CELL = 1x1 (block 1A 2026-08-xx)"
      # Cr, held: --cell-label must equal the label DERIVED from CELL_PARAMETERS, and the
      # verdict must ADMIT that label under the documented grammar ('<label> [cell] [is]
      # ADMISSIBLE' or 'PRODUCTION CELL = <label>') — mere mention is not admission
      # (N30, 1C verify round).

then, on the box (NP must be an exact multiple of -nk):

  bash queue_r1.sh /workspace/sts/runs/probe/m_hess.txt 20 1

and afterwards

  PYTHONPATH=src python src/dft/hessian_analyze.py runs/probe/Ir_hess

The interpretation rule is docs/43 §3 + §3-A. It is not in this file and not in
`hessian_analyze.py`; `--print-prereg` reads it out of docs/43.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_decks import (parse_input_deck, parse_final_coordinates,  # noqa: E402
                         relax_final_energy_ev, write_probe, parse_variant)

BOHR_A = 0.529177210903

#: The pilot's two states. `rundir` supplies BOTH the protocol (from <job>.in) and the
#: geometry (from <job>.out final coordinates), so the deck we emit and the state we are
#: making a claim about cannot come apart.
STATES = {
    # N30+N36: cell_1x1_A is the measured in-plane (|a|, |b|) of the production 1x1 cell,
    # read from the named source deck's CELL_PARAMETERS. It is a geometry anchor, not a
    # registered threshold: _derive_cell_label compares the deck actually being emitted
    # against it so cell_label / coverage_ML / verdict_scope are MEASURED, never asserted.
    "Ir": dict(
        rundir="runs/Ir_anchor", job="s0_OOH", n_slab=18, held=False,
        cell_1x1_A=(3.15400000, 6.36113260),   # runs/Ir_anchor/s0_OOH.in CELL_PARAMETERS
        note="on-record mirror-plane *OOH, eta 0.781 V (docs/32); nspin=1, no Hubbard U; "
             "the state P10 found a -0.291 eV yaw90 escape from (docs/41 s6c)",
    ),
    "Cr": dict(
        rundir="runs/probe/Cr_basin", job="s0_OOH", n_slab=18, held=True,
        cell_1x1_A=(2.91600000, 6.25223816),   # runs/probe/Cr_basin/s0_OOH.in CELL_PARAMETERS
        note="the BASIN-CORRECTED *OOH that is in tier_v2 (docs/41 s6f). NOT "
             "runs/Cr_slab/s0_OOH, which is 178.58 meV high in a wrong magnetic solution. "
             "This *OOH sets c_Cr = 3.102 eV and hence Cr's 9 meV scaling excess",
    ),
}

#: docs/43 §3-A.7: Cr is held until block 1A returns its cell verdict, because at 1x1 its
#: *OOH carries a 1.338 A H-bond to its own periodic image and the two modes most likely to
#: come back imaginary are governed by that contact rather than by the mirror.
DEFAULT_STATES = [k for k, v in STATES.items() if not v["held"]]

AXES = ("x", "y", "z")

#: docs/43 §3-A.8 as corrected by amendment 3. Stamped into the manifest so nobody can later
#: read the 12 in-plane decks as evidence the 1C verdict used.
AXES_PURPOSE = {
    # U15: the sqrt(2)-gain / independent-noise claim is DELETED — docs/43 amendment 3
    # measured that each ym deck is the exact mirror of its yp partner, so it carries no
    # independent noise realisation and the central difference reduces algebraically to the
    # one-sided difference. The ym decks' real value is N34's identity gate on the Hessian
    # diagonal (hessian_analyze.py Q6).
    "y": "THE 1C VERDICT. Mirror-normal. The y-block of H is built from the +dy FORWARD "
         "difference exclusively, with the reference forces as the base point (docs/43 "
         "am.4 s7 items 1-2). The ym deck is the exact mirror of the yp deck (docs/43 "
         "amendment 3): no sqrt(2) gain, no independent noise realisation. It NEVER "
         "enters H; it is retained and run solely as the Q6 mirror-identity control — "
         "F_y(ym) = -F_y(yp), F_x/F_z(ym) = +F_x/F_z(yp) on the raw force blocks — the "
         "only available test of the Hessian diagonal (finding N34).",
    "x": "block 2B in-house ZPE/-TS table. NOT diagnostic for 1C: F_y is identically zero "
         "in these decks by mirror symmetry, so they carry no y-block information.",
    "z": "block 2B in-house ZPE/-TS table. NOT diagnostic for 1C: F_y is identically zero "
         "in these decks by mirror symmetry, so they carry no y-block information.",
}

#: N30+N36: the scope is DERIVED per state — cell_label and coverage_ML are measured from
#: the source deck's CELL_PARAMETERS against the recorded 1x1 lattice (_derive_cell_label),
#: never asserted as module constants. This is only the template (docs/43 §3-A.7 scopes
#: every 1C verdict; the cell in the stamp is now a measurement).
VERDICT_SCOPE_TEMPLATE = "q = 0, {cell} cell, {cov} ML"

#: U14+N31: per-SCF wall cost, MEASURED, keyed by state — a state absent from this dict has
#: NOT been timed at these settings and gets no number, because a cost taken from a cheaper
#: system and quoted for a harder one is the exact pattern lessons.md 2026-08-05 documents
#: three times. Ir: 643 s = the 2026-08-09 feasibility probe on the real deck (30 iterations
#: x 20.95 s electrons + init_run/forces overhead) at NP = 20 / -nk 4. Cr is nspin=2 + U at
#: 36 k-points and is NOT in this dict on purpose (docstring: ~2.4x Ir per iteration is an
#: extrapolation, not a measurement).
MEASURED_SEC_PER_SCF = {"Ir": 643.0}


# ------------------------------------------------------------------ helpers ---

def _parse_text(text: str) -> dict:
    """parse_input_deck on an in-memory deck, so the guard reads what will be written."""
    fh = tempfile.NamedTemporaryFile("w", suffix=".in", delete=False, newline="\n",
                                     encoding="utf-8")
    try:
        fh.write(text)
        fh.close()
        return parse_input_deck(fh.name)
    finally:
        os.unlink(fh.name)


def _last_force_block(outfile: str):
    """Last printed force block as a list of [fx, fy, fz] in Ry/bohr, or None.

    pw.x prints UNCONSTRAINED forces (frozen atoms carry real values) with the acoustic
    sum rule already imposed (sum over atoms is 0 to 1e-8) and to 8 decimals in Ry/au.
    All three verified on the two source runs; see Trap 4.

    None of those conventions biases the finite difference. The sum-rule subtraction is a
    rigid per-component shift applied to every atom, and for a periodic system the raw
    total force is zero anyway, so it removes numerical residue rather than signal. The
    1e-8 Ry/au print quantisation contributes sigma ~ 3e-9 Ry/bohr, about 0.4 cm^-1 of
    frequency noise on oxygen -- three orders below the i50 cm^-1 floor, and it lands in
    hessian_analyze.py's measured sigma_F rather than hiding.
    """
    txt = open(outfile, errors="replace").read()
    blocks = re.findall(
        r"Forces acting on atoms.*?\n\n((?:\s*atom\s+\d+ type\s+\d+\s+force =.*\n)+)", txt)
    if not blocks:
        return None
    return [[float(v) for v in line.split("force =")[1].split()]
            for line in blocks[-1].strip().split("\n")]


def _fmt_float(x: float) -> str:
    return f"{x:.8f}"


def _final_magnetisation(outfile: str):
    """(total, absolute) magnetisation in mu_B from the LAST printed pair, or (None, None).

    Q0 (docs/43 §3-A.5) needs the magnetisation of the SOURCE relaxation, not only its
    energy: docs/41 §6f is a case where a fresh SCF at identical coordinates agreed to
    0.02 meV *after* it was pushed into the right basin, and disagreed by 175 meV before.
    Energy alone would have passed the wrong state on a near-degeneracy.
    """
    txt = open(outfile, errors="replace").read()
    tot = re.findall(r"total magnetization\s+=\s+([-\d.]+)\s+Bohr mag/cell", txt)
    ab = re.findall(r"absolute magnetization\s+=\s+([-\d.]+)\s+Bohr mag/cell", txt)
    return (float(tot[-1]) if tot else None, float(ab[-1]) if ab else None)


def _min_image_contacts(positions, ads, cell):
    """Shortest adsorbate-to-periodic-image-of-adsorbate distances, in Angstrom.

    docs/43 §3-A.7 scopes every 1C verdict to "1x1 cell, 1 ML" because at this coverage the
    adsorbate is hydrogen-bonded to its own image along the cus row. That is a measurement,
    so it is measured here from the geometry actually being emitted rather than quoted from
    the review, and it goes into the manifest.

    Returns {'min_any': (d, label), 'min_H': (d, label) or None} where a label looks like
    'H21...O19(+1,0)'. Only in-plane translations are scanned: the c axis is 25 A of vacuum.
    """
    ax = [cell[0][0], cell[0][1], cell[0][2]]
    bx = [cell[1][0], cell[1][1], cell[1][2]]
    best_any, best_H = None, None
    for i in ads:
        si, ri = positions[i][0], positions[i][1:]
        for j in ads:
            sj, rj = positions[j][0], positions[j][1:]
            for n1 in (-1, 0, 1):
                for n2 in (-1, 0, 1):
                    if n1 == 0 and n2 == 0:
                        continue            # same cell is a bond, not an image contact
                    d = math.sqrt(sum(
                        (ri[k] - rj[k] - n1 * ax[k] - n2 * bx[k]) ** 2 for k in range(3)))
                    lab = f"{si}{i+1}...{sj}{j+1}({n1:+d},{n2:+d})"
                    if best_any is None or d < best_any[0]:
                        best_any = (d, lab)
                    if "H" in (si, sj) and (best_H is None or d < best_H[0]):
                        best_H = (d, lab)
    return dict(min_any=best_any, min_H=best_H)


def _verdict_admits_cell(verdict: str, label: str):
    """The N30 admissibility grammar. Returns the matched admission text, or None.

    Defect: 1C verify round on N30 (docs/43 am.4 §7 governs the ym items; this guard is
    the verify round's re-opening of round-2 N30). The previous guard was bare substring
    containment — `cell_label not in args.cell_verdict_1a` — and N30's own acid string,
    "2x1-vacant REQUIRED; the 1x1 cell is INADMISSIBLE", defeated it: a verdict that
    rules the 1x1 OUT necessarily NAMES the 1x1. Mere mention is not admission.

    GRAMMAR (exact, documented here because refusal messages point at it). A verdict
    string ADMITS cell label L if and only if it contains, case-insensitively, one of:

        1.  L [cell] [is] ADMISSIBLE      e.g. "1x1 ADMISSIBLE", "2x1 cell is ADMISSIBLE"
            — the label, optionally the literal words "cell" and/or "is", then the word
            ADMISSIBLE. ADMISSIBLE must follow whitespace and end at a word boundary, so
            "INADMISSIBLE" and "NOT ADMISSIBLE" can never match, and the label is
            bounded so "21x1" can never admit "1x1".
        2.  PRODUCTION CELL = L           e.g. "PRODUCTION CELL = 2x1"

    Anything else — including naming the label while ruling it out — is NOT admission
    and the build refuses.
    """
    lab = re.escape(label)
    for pat in (rf"(?<![0-9A-Za-z]){lab}(?:\s+cell)?(?:\s+is)?\s+ADMISSIBLE(?![A-Za-z])",
                rf"PRODUCTION\s+CELL\s*=\s*{lab}(?![0-9A-Za-z])"):
        m = re.search(pat, verdict, re.I)
        if m:
            return m.group(0)
    return None


def _derive_cell_label(cell, cell_1x1, tag):
    """(cell_label, coverage_ML) MEASURED from the emitted cell — findings N30+N36.

    docs/43 §3-A.7 requires Cr to be run "in the chosen production cell", and the scope
    stamp exists to stop a coverage artifact being read as the symmetry trap. A hardcoded
    cell_label = "1x1" is an assertion, not a measurement: repoint the rundir at a 2x1
    relaxation and every verdict would still be stamped "1x1, 1 ML". So the label is
    derived here from the source deck's CELL_PARAMETERS against the recorded 1x1 lattice,
    and refuses when the cell is not an integer multiple of it.
    """
    a_len = math.sqrt(sum(c * c for c in cell[0]))
    b_len = math.sqrt(sum(c * c for c in cell[1]))
    mult = []
    for length, l1, ax in ((a_len, cell_1x1[0], "a"), (b_len, cell_1x1[1], "b")):
        n = max(1, round(length / l1))
        if abs(length - n * l1) > 0.02 * l1:
            raise Refuse(
                f"{tag}: in-plane lattice |{ax}| = {length:.5f} A is not an integer "
                f"multiple of the recorded 1x1 value {l1:.5f} A (nearest {n}x is off by "
                f"{length - n * l1:+.5f} A) — cannot derive cell_label, and the scope "
                f"stamp may not be asserted without it (N30/N36)")
        mult.append(n)
    n1, n2 = mult
    return f"{n1}x{n2}", 1.0 / (n1 * n2)


# ------------------------------------------------------------------- guards ---

class Refuse(SystemExit):
    def __init__(self, msg: str):
        super().__init__(f"refusing to write: {msg}")


#: Everything parse_input_deck extracts that this script has NO business changing.
#: `nosym` and `positions` are the two deliberate exceptions and are checked separately.
INVARIANT_FIELDS = ("cell", "species", "flags", "kpts", "hubbard", "mags", "ecutwfc",
                    "ecutrho", "degauss", "nspin", "assume_isolated", "ibrav", "celldm1")


def verify_emitted(text: str, src: dict, ref_pos, n_slab: int, disp, conv_thr: str,
                   emaxstep: int, tag: str) -> float:
    """Compare the emitted deck to the source deck field by field. Returns the ACTUAL
    displacement in Angstrom as it will appear in the file (see note below).

    `disp` is None for the reference, else (atom_index0, axis_index, sign).

    The returned displacement is read back out of the emitted text rather than assumed:
    write_probe formats coordinates to 8 decimals while pw.x prints its final geometry to
    10, so the realised +delta/-delta differ from 0.01 A by up to 5e-9 A. That is
    irrelevant physically and fatal to an exact-equality check, so the analysis divides by
    the realised step instead of the nominal one — 2*delta for the central x/z pairs,
    delta for the y-row forward difference (docs/43 am.4 s7 item 2).
    """
    got = _parse_text(text)

    for f in INVARIANT_FIELDS:
        if got[f] != src[f]:
            raise Refuse(f"{tag}: field {f!r} changed\n  source: {src[f]!r}\n  emitted: {got[f]!r}")

    if not got["nosym"]:
        raise Refuse(f"{tag}: nosym not set — pw.x would symmetrise the forces (Trap 2)")
    for key in ("nosym", "noinv"):
        if not re.search(rf"^\s*{key}\s*=\s*\.true\.\s*$", text, re.M | re.I):
            raise Refuse(f"{tag}: {key} = .true. missing (Trap 2)")
    if not re.search(rf"^\s*conv_thr\s*=\s*{re.escape(conv_thr)}\s*$", text, re.M):
        raise Refuse(f"{tag}: conv_thr is not {conv_thr} (Trap 1)")
    if not re.search(rf"^\s*electron_maxstep\s*=\s*{emaxstep}\s*$", text, re.M):
        raise Refuse(f"{tag}: electron_maxstep is not {emaxstep} (Trap 1). The measured "
                     f"cost is 30 iterations; 200 buys nothing and makes a stall cost 70 "
                     f"min instead of 42 at NP = 20.")
    if not re.search(r"^\s*calculation\s*=\s*'scf'\s*$", text, re.M):
        raise Refuse(f"{tag}: calculation is not 'scf'")
    if not re.search(r"^\s*tprnfor\s*=\s*\.true\.\s*$", text, re.M):
        raise Refuse(f"{tag}: tprnfor missing — no forces, no Hessian")
    if not re.search(r"^\s*occupations\s*=\s*'smearing'\s*$", text, re.M) or \
       not re.search(r"^\s*smearing\s*=\s*'mv'\s*$", text, re.M):
        raise Refuse(f"{tag}: smearing scheme changed")
    for forbidden in ("startingpot", "startingwfc", "input_dft", "tefield", "dipfield",
                      "assume_isolated", "nbnd", "tot_magnetization",
                      "constrained_magnetization"):
        if re.search(rf"^\s*{forbidden}\s*=", text, re.M):
            raise Refuse(f"{tag}: deck carries {forbidden}, which the source deck does not")

    # coordinates: slab frozen to the relaxed geometry, exactly one adsorbate component moved
    got_pos = got["positions"]
    if len(got_pos) != len(ref_pos):
        raise Refuse(f"{tag}: {len(got_pos)} atoms emitted vs {len(ref_pos)} relaxed")
    realised = 0.0
    for i, (gp, rp) in enumerate(zip(got_pos, ref_pos)):
        if gp[0] != rp[0]:
            raise Refuse(f"{tag}: atom {i+1} species {gp[0]} != {rp[0]}")
        for j in range(3):
            d = gp[j + 1] - rp[j + 1]
            moved = disp is not None and i == disp[0] and j == disp[1]
            if moved:
                realised = d
                if abs(abs(d) - abs(_DELTA[0])) > 1e-7:
                    raise Refuse(f"{tag}: atom {i+1} {AXES[j]} moved {d:.10f} A, "
                                 f"expected {disp[2] * _DELTA[0]:+.10f}")
                if d * disp[2] <= 0:
                    raise Refuse(f"{tag}: atom {i+1} {AXES[j]} moved the wrong way")
            elif abs(d) > 1e-7:
                raise Refuse(f"{tag}: atom {i+1} {AXES[j]} drifted {d:.3e} A but should "
                             f"be byte-identical to the relaxed geometry")
    if disp is not None and realised == 0.0:
        raise Refuse(f"{tag}: intended displacement did not survive into the deck")
    return realised


#: module-level so verify_emitted can see the delta the caller chose without threading it
#: through every signature; set once in main() and never rebound.
_DELTA = [0.01]


# --------------------------------------------------------------------- build ---

def build_state(name: str, cfg: dict, args) -> dict:
    rundir, job, n_slab = cfg["rundir"], cfg["job"], cfg["n_slab"]
    src_in = os.path.join(rundir, job + ".in")
    src_out = os.path.join(rundir, job + ".out")
    for p in (src_in, src_out):
        if not os.path.exists(p):
            raise Refuse(f"{name}: missing {p}")

    deck = parse_input_deck(src_in)
    pos, prov = parse_final_coordinates(src_out)
    if pos is None:
        raise Refuse(f"{name}: no coordinates in {src_out}")
    if prov != "final":
        raise Refuse(f"{name}: geometry provenance is {prov!r}, not a converged final "
                     f"geometry — a Hessian at a non-stationary nstep-exhausted point is "
                     f"not interpretable")
    if len(pos) != len(deck["positions"]) or len(pos) != len(deck["flags"]):
        raise Refuse(f"{name}: coordinate/flag round trip failed "
                     f"({len(pos)} / {len(deck['positions'])} / {len(deck['flags'])})")

    nat = len(pos)
    ads = list(range(n_slab, nat))
    if len(ads) < 1:
        raise Refuse(f"{name}: n_slab={n_slab} leaves no adsorbate atoms in {nat}")

    # Trap 4 — a force row on a constrained atom is not a Hessian row.
    bad = [i + 1 for i in ads if deck["flags"][i].split() != ["1", "1", "1"]]
    if bad:
        raise Refuse(f"{name}: adsorbate atoms {bad} are constrained ({deck['flags']}); "
                     f"their printed forces cannot be differenced")

    # the mirror-plane premise, verified not assumed
    ys = [pos[i][2] for i in ads]
    y_spread = max(ys) - min(ys)
    forces = _last_force_block(src_out)
    if forces is None or len(forces) != nat:
        raise Refuse(f"{name}: could not read a full force block from {src_out}")
    max_fy = max(abs(forces[i][1]) for i in ads)
    res_max = max(abs(c) for i in ads for c in forces[i])
    mov_max = max(abs(c) for i in range(nat)
                  for c, k in zip(forces[i], deck["flags"][i].split()) if k == "1")

    mirror = y_spread <= 1e-6 and max_fy == 0.0
    if not mirror and not args.off_plane_ok:
        raise Refuse(
            f"{name}: this is not the mirror-symmetric state the pilot is about "
            f"(adsorbate y spread {y_spread:.3e} A, max|F_y| {max_fy:.3e} Ry/au). "
            f"Pass --off-plane-ok ONLY if you mean to Hessian an escaped geometry "
            f"(block 6B); the manifest is then stamped mirror_plane=false and "
            f"hessian_analyze.py will not apply the y-block decoupling check.")

    idx = {s: i for i, (s, _, _) in enumerate(deck["species"])}
    masses = [deck["species"][idx[pos[i][0]]][1] for i in ads]

    nk_mesh = deck["kpts"][1]
    expected_nk = 1
    for v in nk_mesh[:3]:
        expected_nk *= int(v)

    # docs/43 §3-A.7 — the coverage contact, measured from the geometry being emitted.
    contacts = _min_image_contacts(pos, ads, deck["cell"])

    # N30+N36: cell_label / coverage_ML / verdict_scope are DERIVED from the source deck's
    # CELL_PARAMETERS against the recorded 1x1 lattice, not asserted as constants.
    cell_label, coverage_ML = _derive_cell_label(deck["cell"], cfg["cell_1x1_A"], name)
    scope = VERDICT_SCOPE_TEMPLATE.format(cell=cell_label, cov=f"{coverage_ML:g}")

    # N30, re-opened by the 1C verify round: the old check here was bare substring
    # containment, and N30's own acid string ("2x1-vacant REQUIRED; the 1x1 cell is
    # INADMISSIBLE") defeated it — a verdict ruling the 1x1 OUT names the 1x1, so
    # `cell_label in verdict` read a refusal as an authorisation. Replaced by three
    # refuse-by-default checks: (a) --cell-label is REQUIRED alongside the verdict and is
    # an operator assertion, (b) it must EQUAL the label DERIVED from CELL_PARAMETERS,
    # (c) the derived label must appear as an ADMITTED cell in the verdict under the
    # explicit admissibility grammar of _verdict_admits_cell — mere mention is not
    # admission. The manifest records which grammar production matched.
    admission = None
    if args.cell_verdict_1a is not None:
        if args.cell_label is None:
            raise Refuse(
                f"{name}: --cell-verdict-1a was given without --cell-label. The operator "
                f"must assert the cell being built (--cell-label {cell_label!r} to match "
                f"this source deck); the assertion is checked against the label DERIVED "
                f"from CELL_PARAMETERS and against the verdict's admissibility grammar "
                f"(N30, 1C verify round).")
        if args.cell_label != cell_label:
            raise Refuse(
                f"{name}: --cell-label {args.cell_label!r} does not equal the label "
                f"DERIVED from the source deck's CELL_PARAMETERS, {cell_label!r} "
                f"(coverage {coverage_ML:g} ML). Either the assertion or the source "
                f"rundir is wrong — repoint STATES[{name!r}]['rundir'] at the relaxation "
                f"in the cell 1A chose, or fix the flag (N30/N36).")
        admission = _verdict_admits_cell(args.cell_verdict_1a, cell_label)
        if admission is None:
            raise Refuse(
                f"{name}: the recorded block-1A verdict does not ADMIT the cell this "
                f"build is actually using. Derived from CELL_PARAMETERS: {cell_label} "
                f"(coverage {coverage_ML:g} ML); --cell-verdict-1a = "
                f"{args.cell_verdict_1a!r}. Admission requires "
                f"'{cell_label} [cell] [is] ADMISSIBLE' or "
                f"'PRODUCTION CELL = {cell_label}' in the verdict string — mere mention "
                f"is NOT admission; a verdict that rules a cell INADMISSIBLE names it "
                f"too (N30, 1C verify round; grammar documented at "
                f"_verdict_admits_cell). docs/43 §3-A.7 says the held state is run IN "
                f"THE CHOSEN PRODUCTION CELL — repoint STATES[{name!r}]['rundir'] first "
                f"if 1A chose a different cell.")
    elif args.cell_label is not None and args.cell_label != cell_label:
        raise Refuse(
            f"{name}: --cell-label {args.cell_label!r} does not equal the derived label "
            f"{cell_label!r} (N30/N36).")

    outdir = os.path.join(args.out, f"{name}_hess")
    deck = dict(deck)
    deck["nosym"] = True          # Trap 2: write_probe emits nosym AND noinv from this
    e_ref = relax_final_energy_ev(src_out)
    src_mag, src_absmag = _final_magnetisation(src_out)
    if deck["nspin"] == 2 and src_mag is None:
        raise Refuse(f"{name}: nspin = 2 but {src_out} prints no total magnetization — Q0 "
                     f"(docs/43 §3-A.5) cannot be evaluated and the reference could sit in "
                     f"a different magnetic basin undetected (docs/41 §6f)")

    # ---- build every deck in memory and verify all of them BEFORE writing anything ----
    pending = []   # (filename, text, jobrec)

    def emit(prefix, positions, disp):
        text, _meta = write_probe(deck, positions, parse_variant("base"), prefix,
                                  args.pseudo_dir, args.scratch, calculation="scf")
        text, n = re.subn(r"^(\s*)conv_thr\s*=\s*\S+\s*$",
                          rf"\g<1>conv_thr = {args.conv_thr}", text, count=1, flags=re.M)
        if n != 1:
            raise Refuse(f"{prefix}: did not find exactly one conv_thr to tighten")
        text, n = re.subn(r"^(\s*)electron_maxstep\s*=\s*\S+\s*$",
                          rf"\g<1>electron_maxstep = {args.electron_maxstep}",
                          text, count=1, flags=re.M)
        if n != 1:
            raise Refuse(f"{prefix}: did not find exactly one electron_maxstep to set")
        realised = verify_emitted(text, deck, pos, n_slab, disp, args.conv_thr,
                                  args.electron_maxstep, prefix)
        return text, realised

    ref_prefix = f"{job}__hess_ref"
    text, _ = emit(ref_prefix, pos, None)
    pending.append((ref_prefix + ".in", text,
                    dict(job=ref_prefix, file=ref_prefix + ".in", kind="reference",
                         atom_1based=None, atom_index0=None, axis=None, sign=0,
                         displacement_A=0.0)))

    for i in ads:
        for j, ax in enumerate(AXES):
            for sign in (+1, -1):
                newpos = [list(p) for p in pos]
                newpos[i][j + 1] += sign * args.delta
                newpos = [tuple(p) for p in newpos]
                tag = f"{job}__hess_a{i+1}{ax}{'p' if sign > 0 else 'm'}"
                text, realised = emit(tag, newpos, (i, j, sign))
                pending.append((tag + ".in", text,
                                dict(job=tag, file=tag + ".in", kind="displacement",
                                     atom_1based=i + 1, atom_index0=i, axis=ax, sign=sign,
                                     displacement_A=round(realised, 12))))

    n_disp = len(ads) * 3 * 2
    if len(pending) != n_disp + 1:
        raise Refuse(f"{name}: generated {len(pending)} decks, expected {n_disp + 1}")

    os.makedirs(outdir, exist_ok=True)
    for fn, text, _rec in pending:
        # LF only: a CRLF .in dies silently inside the box's tmux (lessons.md)
        with open(os.path.join(outdir, fn), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)

    man = dict(
        state=name, source_run=rundir, source_in=src_in, source_out=src_out, job=job,
        note=cfg["note"],
        # docs/43 am.4 s7 items 1-2: the y-block is NOT a central difference.
        method=("Partial Hessian on the adsorbate atoms only, finite differences of "
                "forces: x/z rows by central +/- pairs; y rows by the +dy FORWARD "
                "difference with the reference forces as the base point (docs/43 am.4 s7 "
                "items 1-2 — the ym decks run solely as the Q6 mirror-identity control "
                "and never enter H). nosym/noinv on every deck INCLUDING the reference; "
                "each SCF starts from a fresh atomic-superposition density so the 19 "
                "points are independent."),
        prereg="docs/43-prereg-week1-factorial.md sec 3 (P14) + sec 3-A (amendment 1). "
               "This manifest holds no copy of the rule; hessian_analyze.py "
               "--print-prereg reads those sections out of docs/43.",
        # N30+N36: verdict_scope / cell_label / coverage_ML are MEASURED from the emitted
        # cell by _derive_cell_label, not module constants.
        verdict_scope=scope,
        cell_label=cell_label, coverage_ML=coverage_ML, wavevector="Gamma (q = 0)",
        cell_1x1_A=list(cfg["cell_1x1_A"]),
        verdict_axis="y",
        axes_purpose=dict(AXES_PURPOSE),
        cr_held_pending_1a=STATES[name].get("held", False),
        cell_verdict_1a=getattr(args, "cell_verdict_1a", None),
        # N30 (1C verify round): the operator's own cell assertion and the exact grammar
        # production that admitted the derived label, for provenance.
        cell_label_operator=getattr(args, "cell_label", None),
        cell_verdict_admission_match=admission,
        min_image_contact_angstrom=(contacts["min_any"][0] if contacts["min_any"] else None),
        min_image_contact_label=(contacts["min_any"][1] if contacts["min_any"] else None),
        min_image_H_contact_angstrom=(contacts["min_H"][0] if contacts["min_H"] else None),
        min_image_H_contact_label=(contacts["min_H"][1] if contacts["min_H"] else None),
        geometry_provenance=prov,
        reference_relax_energy_ev=e_ref,
        # Q0, docs/43 §3-A.5: the reference SCF must be the state it claims to be.
        source_final_energy_ev=e_ref,
        source_final_total_mag=src_mag,
        source_final_abs_mag=src_absmag,
        n_atoms=nat, n_slab=n_slab,
        adsorbate_indices_1based=[i + 1 for i in ads],
        adsorbate_species=[pos[i][0] for i in ads],
        adsorbate_masses_amu=masses,
        mirror_plane=bool(mirror),
        mirror_y_angstrom=(sum(ys) / len(ys)),
        mirror_y_spread_angstrom=y_spread,
        source_relax_adsorbate_max_abs_Fy_ry_bohr=max_fy,
        source_relax_adsorbate_max_abs_F_component_ry_bohr=res_max,
        source_relax_movable_max_abs_F_component_ry_bohr=mov_max,
        delta_nominal_angstrom=args.delta,
        conv_thr=args.conv_thr, electron_maxstep=args.electron_maxstep,
        nosym=True, noinv=True,
        kpoints=deck["kpts"], expected_nk=expected_nk, nk_pools=args.nk,
        nspin=deck["nspin"], starting_magnetization=deck["mags"], hubbard=deck["hubbard"],
        ecutwfc=deck["ecutwfc"], ecutrho=deck["ecutrho"], degauss=deck["degauss"],
        reference_job=ref_prefix,
        n_displacements=n_disp, n_scf_total=n_disp + 1,
        jobs=[rec for _fn, _t, rec in pending],
    )
    with open(os.path.join(outdir, "hess_manifest.json"), "w", encoding="utf-8",
              newline="\n") as fh:
        json.dump(man, fh, indent=2)

    print(f"{name}: {nat} atoms, adsorbate {man['adsorbate_species']} at "
          f"{man['adsorbate_indices_1based']}, geometry {prov}")
    print(f"  relaxed E                     = {e_ref:.4f} eV")
    print(f"  mirror plane y                = {man['mirror_y_angstrom']:.8f} A "
          f"(spread {y_spread:.2e} A), max|F_y| on adsorbate = {max_fy:.10f} Ry/au")
    print(f"  residual |F| component on ads = {res_max:.3e} Ry/au  "
          f"({res_max * 13.605693122 / BOHR_A:.4f} eV/A) -- IN-PLANE ONLY; the y block is "
          f"an exact stationary direction")
    src_nk = re.search(r"number of k points=\s*(\d+)",
                       open(src_out, errors="replace").read())
    print(f"  k-mesh {' '.join(nk_mesh[:3])} with nosym+noinv -> {expected_nk} k-points "
          f"(the source relaxation ran {src_nk.group(1) if src_nk else '?'} irreducible; "
          f"that difference is the whole point of Trap 2)")
    print(f"  source magnetisation          : total {src_mag}, absolute {src_absmag} mu_B "
          f"(Q0 baseline, docs/43 s3-A.5)")
    if contacts["min_any"]:
        d, lab = contacts["min_any"]
        print(f"  min image contact             : {d:.3f} A  {lab}")
    if contacts["min_H"]:
        d, lab = contacts["min_H"]
        print(f"  min image contact involving H : {d:.3f} A  {lab}")
    print(f"  SCOPE                         : every verdict is scoped to '{scope}' "
          f"(cell_label {cell_label} DERIVED from CELL_PARAMETERS vs 1x1 = "
          f"{cfg['cell_1x1_A']}, N30/N36)")
    print(f"  {len(ads)} atoms x 3 cartesian x 2 signs = {n_disp} displacements "
          f"+ 1 reference = {n_disp + 1} SCFs")
    print(f"    of which the 1C VERDICT rests on the y block (docs/43 s3-A.8): the "
          f"{len(ads)} +y decks + the reference carry it as a FORWARD difference with "
          f"the reference as base point (am.4 s7 items 1-2); the {len(ads)} -y decks are "
          f"the exact mirrors of the +y decks (amendment 3 — no sqrt(2) gain, no "
          f"independent noise; U15), NEVER enter H, and run solely as the Q6 "
          f"mirror-identity control on the Hessian diagonal (N34); the {len(ads) * 4} "
          f"+/-x and +/-z decks are bought for block 2B's ZPE/-TS table and carry no "
          f"y-block information")
    print(f"  -> {outdir.replace(os.sep, '/')}")
    return man


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--states", nargs="+", default=list(DEFAULT_STATES),
                    choices=list(STATES),
                    help="which pilot states to build (default: Ir only — docs/43 s3-A.7 "
                         "holds Cr until block 1A returns its cell verdict)")
    ap.add_argument("--cell-verdict-1a", dest="cell_verdict_1a", default=None,
                    help="block 1A's cell verdict, verbatim. REQUIRED to build a held "
                         "state; recorded in the manifest. The label derived from "
                         "CELL_PARAMETERS must appear in it as an ADMITTED cell — "
                         "'<label> [cell] [is] ADMISSIBLE' or 'PRODUCTION CELL = "
                         "<label>'; mere mention is not admission (N30, 1C verify "
                         "round).")
    ap.add_argument("--cell-label", dest="cell_label", default=None,
                    help="the cell label the operator asserts is being built (e.g. 1x1, "
                         "2x1). REQUIRED alongside --cell-verdict-1a; refused unless it "
                         "EQUALS the label derived from the source deck's "
                         "CELL_PARAMETERS (N30, 1C verify round).")
    ap.add_argument("--out", default="runs/probe")
    ap.add_argument("--manifest", default="runs/probe/m_hess.txt")
    ap.add_argument("--delta", type=float, default=0.01,
                    help="finite-difference step in Angstrom (default 0.01)")
    ap.add_argument("--conv-thr", dest="conv_thr", default="1.0d-10",
                    help="SCF threshold; see Trap 1 for why 1.0d-8 is not enough")
    ap.add_argument("--electron-maxstep", dest="electron_maxstep", type=int, default=120,
                    help="measured cost is 30 iterations; 120 is 4x headroom (Trap 1). "
                         "Accepted band 30..150; 151..200 needs "
                         "--allow-electron-maxstep-200 (U13+N29)")
    # U13+N29: 200 was silently reachable through the ordinary flag (the old band was
    # 30..200 inclusive), so "guard fires on 200" was false. The inherited value now
    # requires an explicit escape hatch.
    ap.add_argument("--allow-electron-maxstep-200", dest="allow_emaxstep_200",
                    action="store_true",
                    help="explicit escape hatch: widen the accepted electron_maxstep band "
                         "from 30..150 to 30..200. The inherited 200 is the value Trap 1 "
                         "exists to cut; without this flag it is refused (U13+N29)")
    ap.add_argument("--nk", type=int, default=4,
                    help="pw.x -nk; NP on the queue must be an exact multiple of this")
    ap.add_argument("--np", type=int, default=20,
                    help="MPI ranks the printed queue line will use. Measured: 20.95 s per "
                         "SCF iteration at NP=20/-nk 4 on the real deck.")
    ap.add_argument("--nconc", type=int, default=1,
                    help="concurrent jobs for the printed queue line; NP x NCONC must be "
                         "<= 23 (the box's cgroup gives 23.04 usable cores, not nproc's 48)")
    ap.add_argument("--pseudo-dir", default="/usr/share/espresso/pseudo")
    ap.add_argument("--scratch", default="./tmp")
    ap.add_argument("--off-plane-ok", action="store_true",
                    help="allow a non-mirror-symmetric reference (block 6B re-audits); "
                         "stamps mirror_plane=false in the manifest")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    if not (0.002 <= args.delta <= 0.05):
        raise Refuse(f"delta = {args.delta} A is outside [0.002, 0.05]: below that the "
                     f"force difference drowns in SCF noise, above it the harmonic "
                     f"approximation is the error")
    if not re.fullmatch(r"1\.0d-1[02]", args.conv_thr):
        raise Refuse(f"conv_thr = {args.conv_thr!r}; a force-difference Hessian at "
                     f"delta = {args.delta} A needs 1.0d-10 (or 1.0d-12). See Trap 1.")
    # U13+N29: the accepted band is 30..150. Reaching the inherited 200 requires the
    # explicit --allow-electron-maxstep-200 escape flag; it is never a side effect of the
    # ordinary --electron-maxstep argument.
    emax_cap = 200 if args.allow_emaxstep_200 else 150
    if not (30 <= args.electron_maxstep <= emax_cap):
        raise Refuse(
            f"electron_maxstep = {args.electron_maxstep}: accepted band is 30..{emax_cap}. "
            f"Below 30 is under the measured iteration count (30). "
            + ("Above 200 is never accepted." if args.allow_emaxstep_200 else
               "151..200 is the inherited regime Trap 1 exists to cut and requires the "
               "explicit --allow-electron-maxstep-200 escape flag (U13+N29); above 200 is "
               "never accepted."))
    if args.np % args.nk:
        raise Refuse(f"NP = {args.np} is not an exact multiple of -nk {args.nk}; pw.x "
                     f"aborts. Fix the printed queue line, not the deck.")
    if args.np * args.nconc > 23:
        raise Refuse(f"NP x NCONC = {args.np * args.nconc} > 23 usable cores (the box's "
                     f"cgroup cpu.max is 2304000/100000 = 23.04; nproc says 48 and is wrong)")

    # docs/43 §3-A.7 — Cr does not launch on this script's say-so.
    for name in args.states:
        if STATES[name]["held"] and not (args.cell_verdict_1a and args.cell_label):
            raise Refuse(
                f"{name} is HELD by docs/43 §3-A.7 until block 1A returns its cell verdict. "
                f"At 1x1 this state's *OOH hydrogen-bonds to its own periodic image "
                f"(H...O = 1.338 A, O...O = 2.399 A along the cus row), so the OOH yaw and "
                f"the H torsion — the two modes most likely to come back imaginary — are "
                f"governed by the coverage rather than by the mirror, and a CONFIRMED here "
                f"would be attributed to the symmetry trap on a coverage artifact. If 1A has "
                f"reported, pass BOTH --cell-verdict-1a \"<verdict>\" AND --cell-label "
                f"<label>, and build it in the chosen production cell. The builder DERIVES "
                f"the cell from the source deck's CELL_PARAMETERS, refuses unless "
                f"--cell-label equals that derived label, and refuses unless the verdict "
                f"ADMITS the derived label under the documented grammar — "
                f"'<label> [cell] [is] ADMISSIBLE' or 'PRODUCTION CELL = <label>'; mere "
                f"mention is not admission (N30, 1C verify round) — repoint "
                f"STATES['{name}']['rundir'] first if 1A chose a different cell.")
    _DELTA[0] = args.delta

    built = []
    total = 0
    for name in args.states:
        man = build_state(name, STATES[name], args)
        built.append((name, man))
        total += man["n_scf_total"]

    # N30+N36: the manifest header quotes the DERIVED per-state scopes, not a constant.
    scope_txt = "; ".join(f"{name}: '{man['verdict_scope']}'" for name, man in built)
    lines = [
        "# Block 1C Hessian pilot. Fixed-geometry SCFs, nosym+noinv, conv_thr "
        f"{args.conv_thr}, electron_maxstep {args.electron_maxstep}, delta {args.delta} A. "
        f"x/z rows central differences; the y rows are the +dy FORWARD difference against "
        f"the reference (docs/43 am.4 s7 — the ym decks run solely as the Q6 "
        f"mirror-identity control and never enter H).",
        "# RULE: docs/43 s3 + s3-A. No copy of it lives in the code. Verdict scope is "
        f"DERIVED from each source deck's CELL_PARAMETERS (N30/N36): {scope_txt}.",
        "# NOT a relaxation. 'JOB DONE' is not success: hessian_analyze.py gates on an "
        "energy, 'No symmetry found', the k count, the magnetisation, Q0 and the Q6 "
        "mirror-identity check on the raw forces (N34).",
        f"# NP on queue_r1.sh must be an exact multiple of {args.nk}. NP x NCONC <= 23.",
        "# BEFORE LAUNCHING: delete or rename every stale <job>.out in these directories. "
        "queue_r1.sh:33 SKIPS any job whose .out contains 'JOB DONE', and pw.x prints that "
        "after a failure, after nstep exhaustion and after a user .EXIT. The 2026-08-09 "
        "conv_thr feasibility probe left exactly such an .out at "
        "probe/Ir_hess/s0_OOH__hess_ref.out; it has been renamed to "
        "*.THROWAWAY-convthr-feasibility-probe-2026-08-09.out so the production reference "
        "is not silently replaced by a job docs/43 amendment 1 forbids reusing.",
    ]
    for name, man in built:
        for rec in man["jobs"]:
            lines.append(f"probe/{name}_hess {rec['job']} .in {args.nk}")

    with open(args.manifest, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    rel = os.path.relpath(args.manifest, "runs").replace(os.sep, "/")
    print(f"\nwrote {args.manifest} ({total} jobs across {len(args.states)} states)")
    print(f"  bash queue_r1.sh /workspace/sts/runs/{rel} {args.np} {args.nconc}"
          f"   # NP={args.np} (= {args.np // args.nk} x -nk {args.nk}), NCONC={args.nconc} "
          f"-> {args.np * args.nconc} of the box's 23.04 usable cores")
    # U14+N31: the measured extrapolation is printed ONLY for states measured at these
    # exact settings; every other state prints NOT TIMED instead of a number, because the
    # printout is what gets copied into a plan (hard rule 6; lessons.md 2026-08-05).
    for name, man in built:
        n = man["n_scf_total"]
        sec = MEASURED_SEC_PER_SCF.get(name)
        if sec is not None:
            print(f"  {name}: measured 20.95 s/SCF-iteration x 30 iterations at NP=20/"
                  f"-nk 4 on this exact deck -> {n} SCFs x {sec:.0f} s = "
                  f"{n * sec / 3600:.1f} h wall at NCONC=1.")
        else:
            print(f"  {name}: NOT TIMED at these settings — time one SCF before sizing "
                  f"this arm ({n} SCFs; no wall-hour figure is printed on purpose, "
                  f"U14+N31).")
    print(f"  rule: docs/43 s3 + s3-A.  python src/dft/hessian_analyze.py --print-prereg")
    held = [n for n in STATES if STATES[n]["held"] and n not in args.states]
    if held:
        print(f"  HELD, not built: {', '.join(held)} (docs/43 s3-A.7, pending block 1A's "
              f"cell verdict)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
