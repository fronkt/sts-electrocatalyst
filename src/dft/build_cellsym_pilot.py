#!/usr/bin/env python3
"""Block 1A: the cell x symmetry crossed factorial (tasks/plan-maximal-rigor.md, W1).

THE PRE-REGISTRATION IS docs/43, NOT THIS FILE
----------------------------------------------
`docs/43-prereg-week1-factorial.md` s2 and s2-A (amendment 1) are the ONLY
pre-registration for this block. This file IMPLEMENTS them and deliberately does
not restate them. An earlier version of this docstring carried its own rules and
two of them contradicted docs/43 -- it excluded `*O` from the factorial, and it
asserted that the 2x1o spectator "leaves the interaction term unaffected either
way". Both were wrong, both were caught in the 2026-08-09 review (findings [1]
and [7]), and both are now settled in docs/43 s2-A.1 and s2-A.2.

    A rule that exists in two places is a rule that will be read in whichever
    version suits the result.  -- docs/43 amendment 1

Every registered NUMBER this code needs is in `PREREG` below, each carrying the
docs/43 clause it comes from and a literal substring that must still be present
in docs/43. `_prereg_check()` runs before anything is built and aborts if an
anchor has moved. Where this file and docs/43 disagree, docs/43 wins and this
file is the thing that changes.

The design, in one line: metals {Cr, Ir, Ru} x cells {1x1, 2x1v, 2x1o} x symmetry
{mir, off} x states {*O, *OH, *OOH}, each arm with its own reference in its own
cell. Why it is crossed rather than staged is docs/43 s2 ("Why it is a factorial
and not a sequence"); the collinearity evidence it rests on is docs/41 s2e.

The engineering decisions this file makes, and the evidence for each
--------------------------------------------------------------------
1. WHICH VECTOR TO DOUBLE -- a1, the x axis. Determined from the production
   CELL_PARAMETERS and the relaxed positions, not from memory:

     M    a1 (x)    a2 (y)    a2/a1    a2/sqrt(2)   literature a_rutile
     Cr   2.9160    6.2522    2.144    4.4210       CrO2  4.42
     Ru   3.1070    6.3527    2.045    4.4920       RuO2  4.49
     Ir   3.1540    6.3611    2.017    4.4980       IrO2  4.50

   a1 IS c_rutile = the [001] axis; a2 is [1-10] = a_rutile*sqrt(2). The cus row
   runs along [001], so the cus metal's nearest like neighbour is its own image
   at x + a1, and the adsorbate-adsorbate nearest-image distance in the 1x1 cell
   is exactly a1. Doubling a1 takes it to Cr 5.832 / Ru 6.214 / Ir 6.308 A.
   Doubling a2 instead would separate BRIDGE rows, leave the cus row at 1 ML,
   and measure nothing about the interaction docs/41 s6a identified.

2. THE K-MESH IN THE DOUBLED CELL -- 4 x 4 x 1, and for Ir and Ru this is EXACT,
   not merely matched: a Gamma-centred 4x4x1 grid in a cell with a1' = 2*a1
   samples k = (i/8)b1 + (j/4)b2, whose union under 2x1 band folding is exactly
   the 1x1 8x4x1 grid.

     M    1x1 mesh   n1*a1     n2*a2    2x1 mesh   4*(2a1)   4*a2   folds?
     Cr   9 4 1      26.24     25.01    4 4 1      23.33     25.01  NO
     Ru   8 4 1      24.86     25.41    4 4 1      24.86     25.41  YES
     Ir   8 4 1      25.23     25.44    4 4 1      25.23     25.44  YES

   Cr's odd n1 does not fold onto any integer 2x1 mesh. docs/43 s2-A.5 registers
   the resolution: Cr runs 4 4 1 like the others and the 9 -> 8 shift is measured
   explicitly by fixed-geometry SCFs of the Cr 1x1 mirror states at 8 4 1. There
   are FOUR of those here, not the three s2-A.5 names, because s2-A.1 adds `*O`
   to the state list and every state whose dG enters eta needs the bridge.

3. THE STARTING GEOMETRY -- production FINAL coordinates via
   parse_final_coordinates, per state, with Cr *OOH redirected to
   runs/probe/Cr_basin/s0_OOH.out (the production one is a metastable magnetic
   solution 178.58 meV high, docs/41 s6f). The 2x1 cells are assembled
   half-and-half: the half carrying the working adsorbate gets THAT state's own
   relaxed substrate, and the neighbouring half gets the substrate of whatever it
   carries (clean slab for 2x1v, the relaxed s0_O substrate plus its *O for
   2x1o).

4. MAGNETIC STARTS -- fresh atomic superposition everywhere. Cr keeps its
   production starting_magnetization (0.6 on Cr) and U = 3.7 eV on Cr-3d; Ru and
   Ir stay nspin = 1, U = 0. No deck may carry startingpot or startingwfc:
   docs/41 s6f showed the Cr/Co/Ni basin failures were path dependence in the
   extrapolated density. `_FORBIDDEN` enforces this on the emitted text.

5. THE CONSTRAINT MASK -- replicated, not re-derived. All three metals run the
   identical production mask (docs/41 s6a found it byte-identical across
   Cr/Ru/Ir); doubling the cell makes the new mask literally `mask + mask`, and
   the guard asserts each 18-atom half equals the source mask element by element.

6. OFF-PLANE MEANS A PHYSICAL DISPLACEMENT, PER STATE. `nosym` on an exactly
   symmetric input does nothing -- F_y stays at ~1e-8 against a 1e-3 threshold
   (lessons.md 2026-08-09). A polyatomic adsorbate is yawed 90 deg about the
   vertical axis through its binding atom (matches P10, so the 1x1 rows are
   comparable). A single `*O` cannot be yawed, so it is TRANSLATED in y by
   `ADSORBATE_KICK_A`; docs/43 s2-A.1 registers exactly this and requires
   >= 0.30 A. The guard checks the achieved displacement, never the flag.

7. THE 2x1o SPECTATOR IS KICKED IN `ref__2x1o` AND NOWHERE ELSE (docs/43
   s2-A.2). Kicking it in the `off` adslab decks but not the `mir` ones put the
   spectator's own off-plane relaxation energy inside S(2x1o) and not inside
   S(2x1v), i.e. straight into the interaction term the whole crossed design
   exists to measure. The contingency docs/43 s2-A.2 registers -- a
   `ref__2x1o_mir` job if the reference's spectator settles at |dy| > 0.02 A --
   is written into cellsym_manifest.json so it is read from the artifact rather
   than remembered.

Reused from disk, declared per row in the manifest: the Ir/Ru production
1x1/mir states, Cr *OOH's basin-restart mirror row, and Ru's P10 off-plane 1x1
*OOH run. NOT reused any more: Ir's P10 off-plane run (it is the docs/43 s2
replication gate and must be reproduced, not re-read -- finding N2) and Cr's
s0_O / s0_OH mirror rows (re-emitted under this emitter's own mixing so each
pair differs in exactly one thing -- amendment 2 / finding N11).

Known, INTENDED deviation from the production decks
---------------------------------------------------
`write_probe` hardcodes `mixing_mode = 'local-TF'`. Cr's production ADSLAB decks
carry no `mixing_mode` at all. So the Cr adslab decks emitted here differ from
their production source in exactly that one field. It is declared, not
accidental: it is the same emitter every probe deck in this campaign was built
with, including runs/probe/Cr_basin, whose step-1 energy reproduced the audit SCF
to 8.7e-4 meV (docs/41 s6f). `_ALLOWED_DIFFS` lists it and the guard refuses to
write if ANY other field moves.

Usage
-----
  PYTHONPATH=src python src/dft/build_cellsym_pilot.py
  PYTHONPATH=src python src/dft/build_cellsym_pilot.py --dry-run
  PYTHONPATH=src python src/dft/build_cellsym_pilot.py --metals Ir
  PYTHONPATH=src python src/dft/build_cellsym_pilot.py --gate1     # wave 2, after 1A returns
  PYTHONPATH=src python src/dft/build_cellsym_pilot.py --score     # wave 3, the readout
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_decks import (parse_input_deck, parse_final_coordinates,  # noqa: E402
                         relax_final_energy_ev, write_probe, parse_variant)

_HERE = os.path.dirname(os.path.abspath(__file__))
DOC43_PATH = os.path.normpath(os.path.join(_HERE, "..", "..", "docs",
                                           "43-prereg-week1-factorial.md"))
DOC43 = "docs/43-prereg-week1-factorial.md"

# --------------------------------------------------------------------------
# PREREG -- pointers, not copies.
#
# Each entry is (value, docs/43 clause, literal substring that must still be
# present in docs/43). The value is here because a machine needs a number; the
# anchor is here so the number cannot silently drift away from the clause it
# claims to implement, WHICH MEANS EVERY ANCHOR MUST RUN THROUGH THE NUMBER IT
# PINS. Round-2 finding N1 demonstrated the failure: six anchors stopped just
# short of their number, five registered thresholds were changed in a scratch
# copy of docs/43, and the builder emitted all 56 decks without a warning.
# _prereg_check() aborts the build if any anchor is gone.
# --------------------------------------------------------------------------
PREREG = {
    "states": (
        ("s0_O", "s0_OH", "s0_OOH"), "s2",
        "States: `*O`, `*OH`, `*OOH`"),
    "monatomic_offplane_min_dy_A": (
        0.30, "s2-A.1",
        "y-translation of ≥ 0.30 Å"),
    "spectator_kick_ref_only": (
        True, "s2-A.2",
        "the kick is applied to `ref__2x1o` only"),
    "spectator_contingency_dy_A": (
        0.02, "s2-A.2",
        "0.02 Å, a `ref__2x1o_mir` job is added"),
    "cr_pair_magnetisation_tol_bohrmag": (
        0.1, "s2-A.3(a)",
        "must agree to within **0.1 μ_B**"),
    "cr_gate1_scf_tol_meV": (
        5.0, "s2-A.3(b)",
        "required to agree to **≤ 5 meV**"),
    "gate_c_energy_tol_meV": (
        5.0, "s2 / s2-A.4",
        "≤ 5 meV can be passed by a different"),
    "gate_c_magnetisation_tol_bohrmag": (
        0.1, "s2-A.4",
        "Magnetisation must match to 0.1 μ_B"),
    "cr_2x1_kmesh": (
        ("4", "4", "1"), "s2-A.5",
        "Cr therefore runs the same 4 4 1 as the others"),
    "production_cell_decision_eV": (
        0.10, "s2",
        "by **≥ 0.10 eV** on any of the three metals"),
    "sign_rule_max_positive_dE_sym_eV": (
        0.02, "s1",
        "ΔE_sym > +0.02 eV is a failure of the search or"),
    # (expected, tolerance) for the replication gate. The anchor spans the
    # line wrap in docs/43 so it pins BOTH numbers.
    "replication_gate_ir_oohx_1x1_eV": (
        (-0.291, 0.05), "s2 (Pre-registered predictions)",
        "must reproduce ΔE_sym = **−0.291 ±\n0.05 eV**"),
}


def _prereg_check():
    """Refuse to build if docs/43 no longer says what PREREG claims it says."""
    if not os.path.exists(DOC43_PATH):
        raise SystemExit(f"refusing to build: {DOC43} not found at {DOC43_PATH}. "
                         "This file implements that pre-registration; it will not "
                         "run without it.")
    txt = open(DOC43_PATH, encoding="utf-8").read()
    missing = [(k, sec, anc) for k, (_, sec, anc) in PREREG.items() if anc not in txt]
    if missing:
        lines = "\n".join(f"    {k}  ({DOC43} {sec})  anchor not found: {anc!r}"
                          for k, sec, anc in missing)
        raise SystemExit("refusing to build: docs/43 anchors moved. This file must "
                         "be re-read against the pre-registration, not patched.\n" + lines)
    # Verify-round finding: the anchors catch a docs/43 edit, but a change to
    # the PREREG VALUE beside an intact anchor built 61 decks silently, and the
    # manifest then recorded value and anchor contradicting each other in
    # adjacent fields. Every anchor now contains its digits, so demand the
    # scalar value literally appear in its own anchor text.
    drift = []
    for k, (v, sec, anc) in PREREG.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            forms = {f"{v}", f"{v:g}", f"{float(v):.2f}".rstrip("0").rstrip(".")}
            if not any(f in anc for f in forms):
                drift.append(f"    {k} = {v} does not appear in its anchor {anc!r}")
        elif isinstance(v, tuple) and v and all(
                isinstance(x, (int, float)) and not isinstance(x, bool) for x in v):
            for x in v:
                forms = {f"{x}", f"{x:g}", f"{abs(x):g}"}
                if not any(f in anc for f in forms):
                    drift.append(f"    {k}: component {x} does not appear in "
                                 f"its anchor {anc!r}")
    if drift:
        raise SystemExit("refusing to build: a PREREG value drifted away from "
                         "the anchor that pins it. Change docs/43 by amendment, "
                         "then the anchor, then the value -- never the value "
                         "alone.\n" + "\n".join(drift))
    return {k: dict(value=v, clause=f"{DOC43} {sec}", anchor=anc)
            for k, (v, sec, anc) in PREREG.items()}


# --------------------------------------------------------------------------
# what is on disk. rundir is the production run; basin_out overrides the
# geometry source for a state whose production relaxation is in the wrong SCF
# solution (docs/41 s6f). Step counts are ALWAYS taken from the production .out
# even when the geometry comes from a basin restart: the restart started from an
# already-relaxed geometry (4 ionic steps) and is not a measure of BFGS effort.
# --------------------------------------------------------------------------
METALS = {
    "Cr": dict(rundir="runs/Cr_slab", n_slab=18,
               basin_out={"s0_OOH": "runs/probe/Cr_basin/s0_OOH.out"},
               kmesh_1x1=("9", "4", "1"), kfolds=False, magnetic=True),
    "Ir": dict(rundir="runs/Ir_anchor", n_slab=18, basin_out={},
               kmesh_1x1=("8", "4", "1"), kfolds=True, magnetic=False),
    "Ru": dict(rundir="runs/Ru_anchor", n_slab=18, basin_out={},
               kmesh_1x1=("8", "4", "1"), kfolds=True, magnetic=False),
}

STATES = PREREG["states"][0]

#: 1x1 off-plane cell already computed under P10 -- not rebuilt (22.6 h at
#: NP=4). It used this same emitter with production cutoffs, k-mesh and mask,
#: plus nosym/noinv and a yaw-90 start. Declared as REUSE in the manifest.
#:
#: Ir s0_OOH 1x1 off is deliberately NOT here any more (round-2 finding N2):
#: docs/43 s2 makes that job the replication gate ("must reproduce DE_sym =
#: -0.291 +/- 0.05 eV ... a pipeline control"), and a control that re-reads the
#: very output it exists to replicate returns -0.291 by construction and cannot
#: fail. The Ir deck is emitted and RUN fresh; the gate scores the fresh run.
ALREADY_ON_DISK = {
    ("Ru", "s0_OOH", "1x1", "off"): "runs/probe/Ru_orient/s0_OOH__yaw90.out",
}

KMESH_2X1 = PREREG["cr_2x1_kmesh"][0]
KMESH_CR_CONTROL = ("8", "4", "1")   # the mesh Cr's 2x1 4 4 1 folds from

#: MEASURED restart class. A relaxation restarted from its own converged
#: geometry: the three docs/41 s6f basin restarts converged in 3, 4 and 5 ionic
#: steps. 6 = that class + 1 step of headroom for the 9 -> 8 mesh nudge. Used
#: ONLY for restart-from-own-minimum jobs, never for the spliced 2x1 cells (U1).
RESTART_STEPS_ALLOWANCE = 6

#: docs/43 AMENDMENT 2 ("the 1x1 mirror arm must be re-emitted, not reused") /
#: round-2 finding N11: Cr's production s0_O and s0_OH decks carry no
#: mixing_mode while every deck this emitter writes carries local-TF, and
#: docs/41 s6f measured a 178.58 meV basin difference on exactly that axis for
#: Cr. These two mirror rows are re-emitted through THIS emitter so each Cr 1x1
#: pair differs in exactly one thing. Cr *OOH is clean already: its mirror row
#: is the basin restart (runs/probe/Cr_basin), which used local-TF, as do all
#: Ir/Ru production rows. The production values remain the tier-of-record.
CR_MIR_REEMIT = ("s0_O", "s0_OH")
YAW_DEG = 90.0                       # matches P10, so the 1x1 rows are comparable
#: y displacement of the 2x1o spectator *O in `ref__2x1o` ONLY (docs/43 s2-A.2).
#: It must clear MIN_OFFPLANE_DY_A below, because in `ref__2x1o` the spectator is
#: the only adsorbate and therefore the only thing that can break the mirror.
SPECTATOR_KICK_A = 0.35
#: y displacement used to take a MONATOMIC adsorbate (*O) off the mirror plane,
#: since it cannot be yawed. docs/43 s2-A.1 requires >= 0.30 A.
ADSORBATE_KICK_A = 0.35
MIN_OFFPLANE_DY_A = PREREG["monatomic_offplane_min_dy_A"][0]
MIN_BOND_A = 0.85                    # O-H is 0.96-1.06 A here; below this is a bug

#: Fields that write_probe is ALLOWED to change relative to the production deck
#: it was parsed from. Anything else moving is a refuse-to-write.
_ALLOWED_DIFFS = {
    "prefix",        # per-job, and the queue rewrites it anyway
    "outdir",        # queue_r1.sh sed-replaces this per job
    "nat",           # the cell arm changes the atom count by construction
    "nosym", "noinv",  # the symmetry arm IS the manipulation
    "calculation",   # 'scf' for the fixed-geometry controls only
    "mixing_mode",   # Cr adslab decks only; see the module docstring
}

#: Keys that must NEVER appear in an emitted deck.
_FORBIDDEN = ("startingpot", "startingwfc", "input_dft", "tefield", "dipfield",
              "assume_isolated", "constrained_magnetization", "tot_magnetization",
              "nbnd", "lda_plus_u", "restart_mode")

#: Scalars compared field by field between the emitted deck and its source.
_CHECK_KEYS = ("calculation", "prefix", "outdir", "pseudo_dir", "tprnfor",
               "forc_conv_thr", "nstep", "ibrav", "nat", "ntyp", "ecutwfc",
               "ecutrho", "occupations", "smearing", "degauss", "conv_thr",
               "mixing_mode", "mixing_beta", "electron_maxstep", "ion_dynamics",
               "nosym", "noinv", "nspin")


# --------------------------------------------------------------- geometry ---

def shift_x(atoms, dx):
    return [(s, x + dx, y, z) for (s, x, y, z) in atoms]


def yaw_fragment(frag, deg):
    """Rotate an adsorbate fragment about the vertical axis through atom 0.

    The binding atom does not move, so the M-O distance -- the only coordinate
    the production multi-start ever explored -- is untouched and only the frozen
    degree of freedom changes.
    """
    ax, ay = frag[0][1], frag[0][2]
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    out = [frag[0]]
    for (sp, x, y, z) in frag[1:]:
        dx, dy = x - ax, y - ay
        out.append((sp, ax + c * dx - s * dy, ay + s * dx + c * dy, z))
    return out


def kick_y(atoms, dy):
    return [(s, x, y + dy, z) for (s, x, y, z) in atoms]


def off_plane_start(frag, y_mirror, job):
    """Take an adsorbate fragment off the mirror plane, per docs/43 s2-A.1.

    Polyatomic -> yaw about the binding atom (P10's operation, so the 1x1 rows
    stay comparable). Monatomic -> y-translation, because a single atom has no
    yaw. Either way the ACHIEVED displacement is checked here and again in the
    guard: `nosym` with nothing to push against is not a search (lessons.md
    2026-08-09).
    """
    out = (yaw_fragment(frag, YAW_DEG) if len(frag) > 1
           else kick_y(frag, ADSORBATE_KICK_A))
    dy = max(abs(q[2] - y_mirror) for q in out)
    if dy < MIN_OFFPLANE_DY_A:
        raise SystemExit(
            f"refusing to build {job}: off-plane start reached only "
            f"|dy| = {dy:.4f} A < {MIN_OFFPLANE_DY_A} A. For a polyatomic "
            "adsorbate that means the yaw axis and the bond are collinear; the "
            "displacement, not the flag, is what breaks the plane.")
    return out


def min_distance(atoms, cell):
    """Smallest interatomic distance including x/y periodic images."""
    a, b = cell[0][0], cell[1][1]
    best = 1e9
    for i in range(len(atoms)):
        for j in range(i + 1, len(atoms)):
            for ix in (-1, 0, 1):
                for iy in (-1, 0, 1):
                    d = math.dist(
                        (atoms[i][1], atoms[i][2], atoms[i][3]),
                        (atoms[j][1] + ix * a, atoms[j][2] + iy * b, atoms[j][3]))
                    best = min(best, d)
    return best


def cus_metal(slab, ads):
    """The top-layer metal directly under the adsorbate's binding atom."""
    metals = [q for q in slab if q[0] not in ("O", "H")]
    zmax = max(q[3] for q in metals)
    top = [q for q in metals if zmax - q[3] < 0.6]
    return min(top, key=lambda q: (q[1] - ads[0][1]) ** 2 + (q[2] - ads[0][2]) ** 2)


# ------------------------------------------------------------------ guards ---

def _scalars(txt):
    out = {}
    for k in _CHECK_KEYS:
        m = re.search(rf"^\s*{k}\s*=\s*([^\s,!/]+)", txt, re.M | re.I)
        out[k] = m.group(1).strip().strip("'\"") if m else None
    return out


def guard(text, src_path, job, expect):
    """Refuse to write unless every quantity we did not intend to change is equal.

    Compares the deck we are ABOUT to write, re-parsed, against the production
    deck it was derived from -- not against what the code meant to do. Rule 5 of
    the campaign's hard rules, and the reason build_basin_restarts.py exists in
    the shape it does.
    """
    def die(msg):
        raise SystemExit(f"refusing to write {job}: {msg}")

    src = open(src_path, encoding="utf-8").read()
    a, b = _scalars(src), _scalars(text)
    for k in _CHECK_KEYS:
        if k in _ALLOWED_DIFFS:
            continue
        if a[k] != b[k]:
            die(f"{k} changed {a[k]!r} -> {b[k]!r} vs {src_path}")

    for k in _FORBIDDEN:
        if re.search(rf"^\s*{k}\s*=", text, re.M | re.I):
            die(f"deck carries forbidden key {k!r}")

    # max_seconds: pw.x stops cleanly and restartably instead of walking to
    # nstep = 200 (finding [8]). It must be present exactly once, carry the value
    # this build computed, and sit inside &CONTROL.
    ms_hits = re.findall(r"^\s*max_seconds\s*=\s*(\d+)\s*$", text, re.M)
    if len(ms_hits) != 1:
        die(f"{len(ms_hits)} max_seconds lines, expected exactly 1")
    if int(ms_hits[0]) != int(expect["max_seconds"]):
        die(f"max_seconds {ms_hits[0]} != computed {expect['max_seconds']}")
    if text.index("max_seconds") > text.index("&SYSTEM"):
        die("max_seconds is outside &CONTROL")

    d_src, d_new = parse_input_deck(src_path), parse_input_deck_text(text)

    if d_src["species"] != d_new["species"]:
        die(f"ATOMIC_SPECIES changed {d_src['species']} -> {d_new['species']}")
    if d_src["hubbard"] != d_new["hubbard"]:
        die(f"HUBBARD changed {d_src['hubbard']} -> {d_new['hubbard']}")
    if d_src["mags"] != d_new["mags"]:
        die(f"starting_magnetization changed {d_src['mags']} -> {d_new['mags']}")

    # cell: a2 and a3 must be identical; a1 is 1x or exactly 2x, and nothing else
    for i in (1, 2):
        for j in range(3):
            if abs(d_src["cell"][i][j] - d_new["cell"][i][j]) > 1e-9:
                die(f"cell vector a{i+1} changed -- vacuum/lateral b must not move")
    r = d_new["cell"][0][0] / d_src["cell"][0][0]
    if abs(r - expect["cell_mult"]) > 1e-9:
        die(f"a1 multiplier {r:.6f}, expected {expect['cell_mult']}")
    # cell_mult is the caller's word for how long a1 is; n_halves is the caller's
    # word for how many 18-atom slabs it put in there, and it is the one the mask
    # check below actually verifies against the emitted bytes. They must agree, or
    # the deck is a slab with a hole in it: a mutation test on 2026-08-09 doubled
    # a1 on a 19-atom 1x1 deck and every other check in this function passed it.
    if abs(expect["cell_mult"] - expect["n_halves"]) > 1e-9:
        die(f"a1 multiplier {expect['cell_mult']} but {expect['n_halves']} slab "
            "half/halves of atoms -- one of the two is wrong and the cell would "
            "carry vacuum along x")
    if abs(d_new["cell"][0][1]) + abs(d_new["cell"][0][2]) > 1e-9:
        die("a1 acquired off-diagonal components")

    if tuple(d_new["kpts"][1][:3]) != tuple(expect["kmesh"]):
        die(f"k-mesh {d_new['kpts'][1][:3]} != declared {list(expect['kmesh'])}")
    if tuple(d_new["kpts"][1][3:]) != ("0", "0", "0"):
        die(f"k-mesh acquired an offset {d_new['kpts'][1][3:]}")

    nat = len(d_new["positions"])
    if nat != expect["nat"]:
        die(f"nat {nat} != expected {expect['nat']}")
    if len(d_new["flags"]) != nat:
        die(f"{len(d_new['flags'])} constraint flags for {nat} atoms")

    # mask: each 18-atom slab half must equal the production mask element by element
    src_mask = d_src["flags"][:18] if len(d_src["flags"]) >= 18 else None
    if src_mask is None:
        die("source deck has fewer than 18 atoms; cannot verify the mask")
    for h in range(expect["n_halves"]):
        got = d_new["flags"][18 * h:18 * (h + 1)]
        if got != src_mask:
            die(f"slab half {h} mask {got} != production mask {src_mask}")
    for f in d_new["flags"][18 * expect["n_halves"]:]:
        if f != "1 1 1":
            die(f"adsorbate atom is constrained ({f!r}); production leaves them free")

    # the symmetry arm has to actually be performed, in both halves.
    # `*_fixed` variants are for wave-2 fixed-geometry SCFs at an ALREADY relaxed
    # geometry: the flags must still match the arm, but the displacement is a
    # measurement by then, not an input, so it is not re-thresholded.
    y_mirror = expect["y_mirror"]
    ads = d_new["positions"][18 * expect["n_halves"]:]
    dy = max((abs(q[2] - y_mirror) for q in ads), default=0.0)
    has_nosym = bool(re.search(r"^\s*nosym\s*=\s*\.true\.", text, re.M | re.I))
    has_noinv = bool(re.search(r"^\s*noinv\s*=\s*\.true\.", text, re.M | re.I))
    sym = expect["sym"]
    if sym in ("off", "off_fixed"):
        if not (has_nosym and has_noinv):
            die("off-plane arm without nosym AND noinv")
        if sym == "off" and dy < MIN_OFFPLANE_DY_A:
            die(f"off-plane arm but max|y - y_cus| = {dy:.4f} A < "
                f"{MIN_OFFPLANE_DY_A} -- nosym alone does nothing on an exactly "
                "symmetric input")
    elif sym in ("mir", "mir_fixed"):
        if has_nosym or has_noinv:
            die("mirror arm must not carry nosym/noinv")
        if sym == "mir" and dy > 1e-6:
            die(f"mirror arm but an adsorbate atom is {dy:.2e} A off y_cus")
        if sym == "mir_fixed" and dy > 1e-3:
            die(f"mirror-arm relaxation ended {dy:.2e} A off y_cus -- pw.x cannot "
                "do that with the mirror on; the geometry source is wrong")

    dmin = min_distance(d_new["positions"], d_new["cell"])
    if dmin < MIN_BOND_A:
        die(f"minimum interatomic distance {dmin:.3f} A < {MIN_BOND_A} -- "
            "the assembly overlapped two atoms")

    zext = max(q[3] for q in d_new["positions"]) - min(q[3] for q in d_new["positions"])
    return dict(nat=nat, dmin=round(dmin, 4), z_extent=round(zext, 4),
                vac_gap=round(d_new["cell"][2][2] - zext, 4),
                max_ads_dy=round(dy, 4))


def parse_input_deck_text(text):
    """parse_input_deck operates on a path; give it one without touching the tree."""
    import tempfile
    fd, p = tempfile.mkstemp(suffix=".in", text=True)
    try:
        with os.fdopen(fd, "w", newline="\n") as fh:
            fh.write(text)
        return parse_input_deck(p)
    finally:
        os.unlink(p)


# ------------------------------------------------------------------- cost ---
#
# Hard rule 6: state the measured basis for every number, and prefer measuring to
# extrapolating. Every constant below names the file it was measured from. Two of
# them are still assumptions and say so.

#: MEASURED. Ru s0_OOH__yaw90: 36900 s / (23 ionic steps x 32 kpt) = 50.1 s;
#: Ir s0_OOH__yaw90: 81420 s / (54 x 32) = 47.1 s. Both 18+3-atom nspin=1 rutile
#: adslabs at NP=4 / npool=4 with NCONC=4 on the 23.04-core box, i.e. exactly the
#: configuration manifest A runs in.
SEC_PER_KPT_STEP = 48.6

#: MEASURED 2026-08-09, m_cellmult wave, box 47025043 (the manifest-C analysis,
#: exactly as registered in the manifest header): median `total cpu time spent
#: up to now` increment, first and last dropped, divided by the master pool's
#: k-count ceil(nk/4), identical NP=20/nk=4 on all three legs.
#:
#:   Cr 1x1 s0_OH  15 kpt, 27 iters, median 15.80 s -> 3.95 s/master-k
#:   Ru 1x1 s0_OH  15 kpt, 22 iters, median  9.70 s -> 2.43 s/master-k
#:   Cr 2x1o s0_OH  9 kpt, 29 iters, median 61.55 s -> 20.52 s/master-k
#:
#: Per-iteration magnetic ratio Cr/Ru = 1.63 (estimator spread 1.63-1.67);
#: x the archive's SCF-iterations-per-ionic-step ratio (Cr 26.1-28.8 vs Ir/Ru
#: 11.9-13.9, hardware-free) = 3.06-4.03. The old planning value 3.5 sits
#: mid-band and is RETAINED; the bracket is now the MEASURED band. Note the
#: pre-measurement optimistic end (1.0, from cross-box relaxation timings) is
#: EXCLUDED by this same-box same-workload measurement -- the relaxation
#: numbers were contaminated by box sharing, exactly as their caveat suspected.
MAG_MULT = 3.5
MAG_MULT_BRACKET = (3.06, 4.03)

#: MEASURED 2026-08-09, same wave, same analysis: CELL_MULT = Cr 2x1o / Cr 1x1
#: = 20.52 / 3.95 = 5.19 (estimator spread 5.19-5.21 across median / mean /
#: total-time -- the measurement is tight). The old planning value 5.5 was 6%
#: high; the assumed floor 4.0 / ceiling 8.0 correctly bracketed it.
#: FLOOR/CEILING below are a LABELLED ALLOWANCE for state dependence, not a
#: measured spread: the wave measured s0_OH only, and the other states differ
#: in nat by +/-2 and in adsorbate SCF hardness (s0_OOH is the historically
#: hard one). +/-15% covers the nat range; nothing measured contradicts it.
CELL_MULT_FLOOR = 4.5
CELL_MULT_PLANNING = 5.19
CELL_MULT_CEILING = 6.0

#: ASSUMED, and labelled. A 2x1 cell has 22 free atoms against 11, so BFGS runs
#: in twice the dimension, and its start is spliced from two different
#: relaxations so the interface is not at a stationary point. The measured 1x1
#: counts are the FLOOR (finding [2]: assuming fewer steps in a harder cell is
#: the project's standing costing failure with the sign flipped).
#: The bracket end feeds est_bracket_np4 -- round-2 finding N9: a published
#: bracket that varies MAG_MULT and CELL_MULT but pins the step count at both
#: ends is not a bracket of the quantity finding [2] was about.
STEP_MULT_2X1 = 1.5
STEP_MULT_2X1_BRACKET = (1.5, 2.0)
# Round-2 finding N9: `ceil(n * STEP_MULT_2X1) < n` is false for every n >= 1
# whenever the constant is >= 1.0, so the in-function "guard" could never fire
# in production. The real invariant is on the CONSTANT, so it lives here, at
# import time, where an edit to the constant is the only thing that can trip it.
# Not a bare `assert` -- the verify round demonstrated `python -O` strips those.
if STEP_MULT_2X1 < 1.0:
    raise SystemExit(
        "STEP_MULT_2X1 < 1.0 would cost the 2x1 cells below their measured 1x1 "
        "ionic-step counts (finding [2])")

#: MEASURED. A fresh-density fixed-geometry SCF costs about 1.3-1.6 ionic-step
#: equivalents in this model: probe/Cr/s0_OH__base 258.5 s/kpt / (48.6 x 3.5) =
#: 1.52; probe/Ru/s0_OH__base 63.9 / 48.6 = 1.31. Rounded UP to 2.0.
SCF_STEP_EQUIV = 2.0

#: The wall-clock speedup of ONE job given the whole 20-rank budget (NP=20,
#: NCONC=1, manifest B) against the same job as one of five concurrent NP=4 jobs
#: (manifest A). Two measurements, neither clean:
#:   * Ir *OOH, 21 atoms, identical cell (3444.9838 a.u.^3): probe/Ir/s0_OOH__base
#:     at NP=4/npool=4 = 3.39 s per k-point per SCF iteration; probe/Ir_hess/
#:     s0_OOH__hess_ref at NP=20/npool=4 = 0.669 -> 5.07x. But the NP=4 arm was
#:     sharing the box with 2-4 other jobs and the NP=20 arm had it to itself, so
#:     this is contention plus ranks.
#:   * Ir *OOH relaxations, NP=4 (47.1 s/kpt/step) vs NP=12 (31.5) -> 1.50x for
#:     3x the ranks, i.e. ~50% marginal efficiency, which extrapolates to ~2.5x
#:     at 5x the ranks.
#: 3.0 is the conservative end. Quoted as a bracket everywhere it is used.
RANK_SPEEDUP_NP20 = 3.0
RANK_SPEEDUP_BRACKET = (2.5, 5.1)

#: max_seconds is set to this multiple of the corrected estimate (finding [8]).
MAX_SECONDS_SAFETY = 2.0
MAX_SECONDS_FLOOR = 7200

#: Manifest A: jobs short enough to pack at NP=4 x NCONC=5. Manifest B: every
#: LONG job -- Cr relaxations plus any job whose NP=4 estimate exceeds
#: LONG_JOB_NP4_HOURS -- one at a time at full ranks. Round-2 finding U6:
#: manifest A used to hold Ru s0_OOH 2x1 jobs estimated at 121.2 h at NP=4,
#: a single-job critical path that renting more boxes cannot shorten; only
#: ranks can, so those jobs belong in B. NP x NCONC <= 23 usable cores in
#: both, and NP is an exact multiple of every nk in the file.
LONG_JOB_NP4_HOURS = 30.0
MANIFESTS = {
    "A": dict(file="m_cellsym_a_np4.txt", np=4, nconc=5),
    "B": dict(file="m_cellsym_b_cr_np20.txt", np=20, nconc=1),
    "C": dict(file="m_cellmult.txt", np=20, nconc=1),
}
SUPERSEDED_MANIFEST = "m_cellsym.txt"

#: Wall cap on each leg of the CELL_MULT/MAG_MULT wave. SIZED FROM A MEASUREMENT,
#: not from the "~15 minutes" in finding [5]: the binding leg is Cr 2x1o, and 15
#: or 20 minutes does not buy enough SCF iterations there to take a median of.
#:
#:   probe/Cr/s0_OH__base.out  26 SCF iterations, median 139.5 s/iteration
#:   probe/Ru/s0_OH__base.out  21 SCF iterations, median  43.6 s/iteration
#:   (both NP=4 sharing the box; /RANK_SPEEDUP_NP20 = 3.0 for this wave's NP=20)
#:
#: so Cr 1x1 ~46 s/iteration (whole SCF inside 20 min) and Cr 2x1o
#: ~46 x CELL_MULT = 256 s/iteration at the 5.5 planning value, 372 s at the 8.0
#: ceiling. At 1200 s that is 3-5 iterations, and the analysis drops the first and
#: the last -- so at the pessimistic end the "median" would be a median of one
#: number. 3600 s gives 10-14 iterations, i.e. 8-12 usable increments.
#: An SCF that converges exits early, so the extra cap costs nothing on the two
#: 1x1 legs and is only spent on the leg that actually needs it.
CELLMULT_MAX_SECONDS = 3600


def est_hours_np4(nk, steps, magnetic, big):
    h = nk * steps * SEC_PER_KPT_STEP / 3600.0
    if magnetic:
        h *= MAG_MULT
    if big:
        h *= CELL_MULT_PLANNING
    return h


def est_bracket_np4(nk, steps, magnetic, big):
    """(low, high) hours at NP=4 over the MAG_MULT x CELL_MULT x STEP_MULT bracket.

    `steps` arrives already multiplied by STEP_MULT_2X1 for the 2x1 jobs, so the
    high end rescales it to the bracket ceiling (finding N9: the published
    bracket must bracket the step count too, not just the per-step cost).
    """
    base = nk * steps * SEC_PER_KPT_STEP / 3600.0
    lo = base * (MAG_MULT_BRACKET[0] if magnetic else 1.0) * (CELL_MULT_FLOOR if big else 1.0)
    hi = base * (MAG_MULT_BRACKET[1] if magnetic else 1.0) * (CELL_MULT_CEILING if big else 1.0)
    if big:
        hi *= STEP_MULT_2X1_BRACKET[1] / STEP_MULT_2X1
    return lo, hi


# -------------------------------------------------------------------- build ---

def count_ionic_steps(outfile):
    """Ionic steps actually taken, = the number of printed force blocks."""
    txt = open(outfile, errors="replace").read()
    return len(re.findall(r"Total force", txt))


def final_magnetisation(outfile):
    """(total, absolute) magnetisation from the last SCF printed, or (None, None).

    docs/43 s2-A.3(a): recorded for every Cr job, and the mir/off members of a
    pair must agree to 0.1 mu_B or the pair is CONFOUNDED. pw.x prints it every
    iteration, so this is free.
    """
    txt = open(outfile, errors="replace").read()
    tot = re.findall(r"total magnetization\s*=\s*([-\d.]+)\s*Bohr mag/cell", txt)
    ab = re.findall(r"absolute magnetization\s*=\s*([-\d.]+)\s*Bohr mag/cell", txt)
    return (float(tot[-1]) if tot else None), (float(ab[-1]) if ab else None)


def load(rundir, job, basin_out=None):
    ip = os.path.join(rundir, job + ".in")
    prod_out = os.path.join(rundir, job + ".out")
    op = basin_out or prod_out
    if not os.path.exists(ip):
        raise SystemExit(f"refusing to build: missing {ip}")
    for p in (op, prod_out):
        if not os.path.exists(p):
            raise SystemExit(f"refusing to build: missing {p}")
    txt = open(op, errors="replace").read()
    if "bfgs converged" not in txt:
        raise SystemExit(f"refusing to build from {op}: no `bfgs converged`; "
                         "an unconverged geometry is not a start, it is a guess")
    pos, prov = parse_final_coordinates(op)
    if pos is None or prov != "final":
        raise SystemExit(f"refusing to build from {op}: geometry provenance {prov!r}")
    deck = parse_input_deck(ip)
    if len(pos) != len(deck["positions"]):
        raise SystemExit(f"{op}: {len(pos)} relaxed coords vs {len(deck['positions'])}")
    steps = count_ionic_steps(prod_out)
    if steps < 1:
        raise SystemExit(f"{prod_out}: 0 ionic steps parsed; the step model would "
                         "silently cost this state at zero")
    return dict(deck=deck, pos=pos, energy_ev=relax_final_energy_ev(op),
                geom_src=op, steps_1x1=steps, steps_src=prod_out)


def build_metal(M, cfg, outroot, pseudo_dir, scratch, dry):
    rd, n_slab = cfg["rundir"], cfg["n_slab"]
    magnetic = cfg["magnetic"]
    outdir = os.path.join(outroot, f"{M}_cellsym")
    if not dry:
        os.makedirs(outdir, exist_ok=True)

    src = {job: load(rd, job, cfg["basin_out"].get(job))
           for job in ("slab",) + tuple(STATES)}

    slab_clean = src["slab"]["pos"]
    ads_ref = src["s0_OOH"]["pos"][n_slab:]
    cus = cus_metal(slab_clean, ads_ref)
    y_mirror = cus[2]
    a1 = src["slab"]["deck"]["cell"][0][0]
    mask = src["slab"]["deck"]["flags"][:n_slab]

    # every adsorbate in every source state must sit on the mirror plane, or the
    # premise of docs/41 s2e does not hold for this metal and the "mir" arm is
    # not the production condition.
    for job in STATES:
        for q in src[job]["pos"][n_slab:]:
            if abs(q[2] - y_mirror) > 1e-6:
                raise SystemExit(f"refusing to build {M}: {job} adsorbate atom is "
                                 f"{abs(q[2]-y_mirror):.2e} A off the mirror plane")

    jobs = []

    def emit(name, deck_src_job, positions, flags, kmesh, cell_mult, sym,
             n_halves, calculation="relax", note="", steps=0, nkp=0,
             steps_basis=None, manifest=None, max_seconds=None, arm="", state="",
             force_nk=None):
        d = dict(parse_input_deck(os.path.join(rd, deck_src_job + ".in")))
        d["flags"] = flags
        d["nosym"] = sym in ("off", "off_fixed", "none")
        d["cell"] = [[d["cell"][0][0] * cell_mult, 0.0, 0.0],
                     list(d["cell"][1]), list(d["cell"][2])]
        d["kpts"] = ("automatic", list(kmesh) + ["0", "0", "0"])
        text, _ = write_probe(d, positions, parse_variant("base"), name,
                              pseudo_dir, scratch, calculation=calculation)

        big = len(positions) > 24
        eff_steps = steps
        h4 = est_hours_np4(nkp, eff_steps, magnetic, big)
        lo4, hi4 = est_bracket_np4(nkp, eff_steps, magnetic, big)
        if manifest is None:
            # U6: a single long job's wall clock is bounded only by its rank
            # count, so anything over LONG_JOB_NP4_HOURS at NP=4 runs serially
            # at NP=20 regardless of metal. Cr relaxations go to B always
            # (finding [6]): even the short ones are magnetic and their caps
            # were sized at NP=20.
            long_job = h4 > LONG_JOB_NP4_HOURS
            manifest = "B" if (long_job or (M == "Cr" and calculation == "relax")) else "A"
        np_run = MANIFESTS[manifest]["np"]
        speed = RANK_SPEEDUP_NP20 if np_run == 20 else 1.0
        h_run = h4 / speed
        if max_seconds is None:
            max_seconds = max(MAX_SECONDS_FLOOR,
                              int(round(MAX_SECONDS_SAFETY * h_run * 3600)))

        # finding [8](iii): pw.x stops cleanly and restartably instead of walking
        # to nstep = 200. Inserted at the end of &CONTROL; the guard re-reads it
        # out of the emitted bytes rather than trusting this line.
        cut = text.index("\n/\n")
        text = text[:cut] + f"\n  max_seconds = {max_seconds}" + text[cut:]

        meta = guard(text, os.path.join(rd, deck_src_job + ".in"), name,
                     dict(cell_mult=cell_mult, kmesh=kmesh, nat=len(positions),
                          n_halves=n_halves, y_mirror=y_mirror, sym=sym,
                          max_seconds=max_seconds))
        blob = text.encode("utf-8")
        if not dry:
            with open(os.path.join(outdir, name + ".in"), "wb") as fh:
                fh.write(blob)
        nk = force_nk if force_nk else (2 if nkp < 12 else 4)
        if nk > nkp:
            raise SystemExit(f"refusing to write {name}: -nk {nk} exceeds the "
                             f"{nkp} k-points pw.x will have; it aborts on that")
        if np_run % nk:
            raise SystemExit(f"refusing to write {name}: NP={np_run} is not an "
                             f"exact multiple of nk={nk} (hard rule 4)")
        jobs.append(dict(metal=M, job=name, deck_source=deck_src_job, arm=arm,
                         state=state, calculation=calculation, sym=sym, note=note,
                         kmesh=" ".join(kmesh), n_kpt_est=nkp, nk=nk,
                         manifest=manifest, np_run=np_run,
                         steps_est=eff_steps, steps_basis=steps_basis,
                         est_hours_np4=round(h4, 1), est_hours_at_np=round(h_run, 1),
                         est_hours_bracket_np4=[round(lo4, 1), round(hi4, 1)],
                         max_seconds=max_seconds, nspin=d["nspin"],
                         spectator_y=(round(positions[-1][2], 8)
                                      if arm == "2x1o" else None),
                         md5=hashlib.md5(blob).hexdigest(), **meta))
        return h_run

    def steps_2x1(state):
        # s >= n is guaranteed by the import-time assertion on STEP_MULT_2X1;
        # the in-function check that used to sit here could never fire (N9).
        n = src[state]["steps_1x1"]
        s = int(math.ceil(n * STEP_MULT_2X1))
        return s, dict(
            measured_1x1_steps=n, source=src[state]["steps_src"],
            multiplier=STEP_MULT_2X1,
            basis="measured 1x1 ionic steps x STEP_MULT_2X1 (assumed, see module)")

    def steps_1x1(state):
        n = src[state]["steps_1x1"]
        return n, dict(measured_1x1_steps=n, source=src[state]["steps_src"],
                       multiplier=1.0,
                       basis="measured 1x1 ionic steps; the off-plane 1x1 rows on "
                             "record came in at 0.34-0.90x of their mirror row "
                             "(Ru 23/68, Ir 54/60), so 1.0x is already the "
                             "conservative side")

    # ---- arm 1x1, off-plane. mirror rows are production and are not rebuilt.
    for state in STATES:
        if (M, state, "1x1", "off") in ALREADY_ON_DISK:
            continue
        pos = src[state]["pos"]
        newpos = pos[:n_slab] + off_plane_start(pos[n_slab:], y_mirror,
                                                f"{state}__1x1_off")
        nkp = int(cfg["kmesh_1x1"][0]) * int(cfg["kmesh_1x1"][1])   # nosym: full grid
        st, basis = steps_1x1(state)
        emit(f"{state}__1x1_off", state, newpos,
             list(mask) + ["1 1 1"] * (len(pos) - n_slab),
             cfg["kmesh_1x1"], 1.0, "off", 1, steps=st, nkp=nkp, steps_basis=basis,
             arm="1x1", state=state,
             note=("production geometry, off-plane start + nosym/noinv; the 1x1 "
                   "mirror row is the production run and is not rebuilt"))

    # ---- arm 2x1v: clean neighbouring cus site.
    # Round-2 finding U1: costing this at a 5-step allowance put the block's
    # own GATE C job 3.2-4.8x below the block's own rule and gave Cr a
    # max_seconds cap the STEP_MULT model says is 5x short. A replicated
    # relaxed slab probably IS near-stationary and will exit early -- but
    # max_seconds must be sized from the same rule as every other 2x1 job,
    # because a cap that fires converts GATE C into a stale-.out intervention.
    st_ref, basis_ref = steps_2x1("slab")
    emit("ref__2x1v", "slab", slab_clean + shift_x(slab_clean, a1),
         list(mask) * 2, KMESH_2X1, 2.0, "none", 2, steps=st_ref, nkp=16,
         arm="2x1v", state="ref",
         steps_basis=dict(basis_ref, note=(
             "a replicated relaxed clean slab is close to a stationary point "
             "of the 2x1 problem and should exit early; the est/cap use the "
             "measured slab count x STEP_MULT anyway (U1). For Cr the mesh "
             "also changes (9 4 1 does not fold), so it is not exactly "
             "stationary.")),
         note=(f"GATE C: |E(2x1 clean) - 2 E(1x1 clean at the folded mesh)| <= "
               f"{PREREG['gate_c_energy_tol_meV'][0]} meV AND magnetisation to "
               f"{PREREG['gate_c_magnetisation_tol_bohrmag'][0]} mu_B "
               f"({DOC43} s2 / s2-A.4)"))

    # ---- arm 2x1o: spectator *O on the neighbouring cus site
    slab_O, ads_O = src["s0_O"]["pos"][:n_slab], src["s0_O"]["pos"][n_slab:]
    spec_mir = shift_x(ads_O, a1)
    spec_off = kick_y(spec_mir, SPECTATOR_KICK_A)
    st_o, basis_o = steps_2x1("s0_O")
    emit("ref__2x1o", "s0_O", slab_clean + shift_x(slab_O, a1) + spec_off,
         list(mask) * 2 + ["1 1 1"], KMESH_2X1, 2.0, "off", 2,
         steps=st_o, nkp=16, steps_basis=basis_o, arm="2x1o", state="ref",
         note=(f"working cus BARE, spectator *O kicked {SPECTATOR_KICK_A} A off "
               f"y_cus. This is the ONLY deck in the block whose spectator is "
               f"kicked ({DOC43} s2-A.2). Contingency, registered before the "
               f"fact: if the spectator relaxes to |dy| > "
               f"{PREREG['spectator_contingency_dy_A'][0]} A, a ref__2x1o_mir job "
               f"is required BEFORE the interaction term is scored."))

    for state in STATES:
        pos = src[state]["pos"]
        slab_s, ads_s = pos[:n_slab], pos[n_slab:]
        n_ads = len(ads_s)
        st, basis = steps_2x1(state)
        for sym in ("mir", "off"):
            a = (ads_s if sym == "mir"
                 else off_plane_start(ads_s, y_mirror, f"{state}__2x1_{sym}"))
            # MEASURED on the box 2026-08-09 by running Ir s0_OOH__2x1v_mir with
            # max_seconds=25: "2 Sym. Ops. (no inversion) found" and "number of
            # k points= 9". So the mirror survives the cell doubling (the arm's
            # positive control) and reduces the 4x4 grid 16 -> 9. The off-plane
            # arm keeps all 16, confirmed on Ir ref__2x1v and Cr s0_OOH__2x1o_off.
            nkp = 16 if sym == "off" else 9
            emit(f"{state}__2x1v_{sym}", state,
                 slab_s + shift_x(slab_clean, a1) + a,
                 list(mask) * 2 + ["1 1 1"] * n_ads,
                 KMESH_2X1, 2.0, sym, 2, steps=st, nkp=nkp, steps_basis=basis,
                 arm="2x1v", state=state,
                 note="1/2 ML, neighbouring cus vacant")
            # docs/43 s2-A.2: the spectator is NOT kicked here, in either arm.
            gate_note = ""
            if state == "s0_O" and sym == "mir":
                gate_note = (" GATE C-2: with the working state also *O this cell "
                             "is the exact replication of the relaxed 1x1 *O cell, "
                             "so it must return 2 x E(1x1 *O at the folded mesh) "
                             "to the same tolerance as GATE C, and it should "
                             "converge in ~1 ionic step.")
            emit(f"{state}__2x1o_{sym}", state,
                 slab_s + shift_x(slab_O, a1) + a + spec_mir,
                 list(mask) * 2 + ["1 1 1"] * (n_ads + 1),
                 KMESH_2X1, 2.0, sym, 2, steps=st, nkp=nkp, steps_basis=basis,
                 arm="2x1o", state=state,
                 note=("1/2 ML working adsorbate, spectator *O on the "
                       "neighbouring cus, spectator UNKICKED in both arms." +
                       gate_note))

    # ---- Cr only: the k-mesh bridge (docs/43 s2-A.5). 9 4 1 is odd and folds
    # onto no 2x1 mesh, so the 1x1 baseline is recomputed at 8 4 1 -- which folds
    # onto 4 4 1 exactly -- as fixed-geometry single points at the production
    # minima. FOUR states, not the three s2-A.5 names, because s2-A.1 adds *O and
    # every state whose dG enters eta needs a folded-mesh baseline.
    if not cfg["kfolds"]:
        for job, nkp in (("slab", 32), ("s0_O", 15), ("s0_OH", 15), ("s0_OOH", 15)):
            pos = src[job]["pos"]
            flags = list(mask) + ["1 1 1"] * (len(pos) - n_slab)
            emit(f"{job}__1x1_k8", job, pos, flags, KMESH_CR_CONTROL, 1.0,
                 "none" if job == "slab" else "mir", 1, calculation="scf",
                 steps=SCF_STEP_EQUIV, nkp=nkp, arm="1x1", state=job,
                 steps_basis=dict(measured_1x1_steps=None,
                                  multiplier=SCF_STEP_EQUIV,
                                  basis="fixed-geometry SCF; SCF_STEP_EQUIV "
                                        "measured at 1.3-1.6 ionic-step "
                                        "equivalents, rounded up to 2.0"),
                 note=f"k-mesh bridge 9 4 1 -> 8 4 1 at fixed geometry from "
                      f"{src[job]['geom_src']}")

        # Round-2 finding N10 / docs/43 AMENDMENT 4: GATE C and C-2 compared a
        # RELAXED 2x1 energy against a FIXED-GEOMETRY 1x1 baseline evaluated at
        # a geometry relaxed at 9 4 1 -- so any relaxation energy released by
        # the 9 -> 8 mesh change reads as a gate failure with nothing to
        # distinguish "the cell construction is wrong" from "the 1x1 geometry
        # was not stationary at the folded mesh". The two gate baselines are
        # therefore RELAXED at the folded mesh; the fixed-geometry SCFs above
        # stay as the registered k-mesh bridge (s2-A.5), and the difference
        # E(relax@841) - E(scf@841) is reported as mesh_relaxation_meV.
        for job, nkp, sym in (("slab", 32, "none"), ("s0_O", 15, "mir")):
            pos = src[job]["pos"]
            flags = list(mask) + ["1 1 1"] * (len(pos) - n_slab)
            emit(f"{job}__1x1_k8_relax", job, pos, flags, KMESH_CR_CONTROL, 1.0,
                 sym, 1, calculation="relax",
                 steps=RESTART_STEPS_ALLOWANCE, nkp=nkp, arm="1x1", state=job,
                 steps_basis=dict(
                     measured_1x1_steps=None,
                     multiplier=None,
                     basis="restart-from-own-minimum class, MEASURED: the three "
                           "docs/41 s6f basin restarts took 3/4/5 ionic steps "
                           "from converged geometries; 6 = that + 1 for the "
                           "9 -> 8 mesh nudge"),
                 note=(f"GATE {'C' if job == 'slab' else 'C-2'} baseline for Cr, "
                       f"RELAXED at the folded mesh (N10 / amendment 4) so both "
                       f"sides of the gate are the same protocol. Starts from "
                       f"{src[job]['geom_src']}."))

    # ---- docs/43 AMENDMENT 2: the Cr 1x1 s0_O / s0_OH mirror rows are
    # re-emitted through this emitter (local-TF, fresh atomic density) so the
    # 1x1 pair differs from its off-plane partner in exactly one thing. The
    # production 9 4 1 mesh is kept -- the pair partner runs 9 4 1 too.
    if M == "Cr":
        for state in CR_MIR_REEMIT:
            pos = src[state]["pos"]
            emit(f"{state}__1x1_mir", state, pos,
                 list(mask) + ["1 1 1"] * (len(pos) - n_slab),
                 cfg["kmesh_1x1"], 1.0, "mir", 1, calculation="relax",
                 steps=RESTART_STEPS_ALLOWANCE, nkp=15, arm="1x1", state=state,
                 steps_basis=dict(
                     measured_1x1_steps=None,
                     multiplier=None,
                     basis="restart-from-own-minimum class, MEASURED: docs/41 "
                           "s6f basin restarts took 3/4/5 ionic steps"),
                 note=("amendment 2 / N11: mirror row re-emitted under the "
                       "emitter's own settings (local-TF) so DE_sym is a "
                       "difference between two decks that differ only in the "
                       "symmetry arm. The production value remains the "
                       "tier-of-record."))

    # ---- the CELL_MULT / MAG_MULT measurement wave (finding [5]). Three
    # fixed-geometry SCFs at identical NP/nk, capped at 20 minutes each. The
    # ratio of the "total cpu time spent up to now" increments per SCF iteration
    # per k-point gives CELL_MULT from (2)/(1) and MAG_MULT from (1)/(3).
    if M == "Cr":
        pos = src["s0_OH"]["pos"]
        emit("s0_OH__1x1_k8__cellmult", "s0_OH", pos,
             list(mask) + ["1 1 1"] * (len(pos) - n_slab),
             KMESH_CR_CONTROL, 1.0, "mir", 1, calculation="scf",
             steps=SCF_STEP_EQUIV, nkp=15, manifest="C", force_nk=4,
             max_seconds=CELLMULT_MAX_SECONDS, arm="1x1", state="s0_OH",
             note="CELL_MULT/MAG_MULT timing probe, leg 1 of 3 (Cr, 1x1)")
        slab_s, ads_s = pos[:n_slab], pos[n_slab:]
        emit("s0_OH__2x1o_mir__cellmult", "s0_OH",
             slab_s + shift_x(slab_O, a1) + ads_s + spec_mir,
             list(mask) * 2 + ["1 1 1"] * (len(ads_s) + 1),
             KMESH_2X1, 2.0, "mir", 2, calculation="scf",
             steps=SCF_STEP_EQUIV, nkp=9, manifest="C", force_nk=4,
             max_seconds=CELLMULT_MAX_SECONDS, arm="2x1o", state="s0_OH",
             note="CELL_MULT/MAG_MULT timing probe, leg 2 of 3 (Cr, 2x1o) -- "
                  "same geometry the s0_OH__2x1o_mir relaxation starts from")
    if M == "Ru":
        pos = src["s0_OH"]["pos"]
        emit("s0_OH__1x1_k8__cellmult", "s0_OH", pos,
             list(mask) + ["1 1 1"] * (len(pos) - n_slab),
             KMESH_CR_CONTROL, 1.0, "mir", 1, calculation="scf",
             steps=SCF_STEP_EQUIV, nkp=15, manifest="C", force_nk=4,
             max_seconds=CELLMULT_MAX_SECONDS, arm="1x1", state="s0_OH",
             note="CELL_MULT/MAG_MULT timing probe, leg 3 of 3 (Ru, 1x1, "
                  "8 4 1 = Ru's production mesh). Without this leg the pair "
                  "measures CELL_MULT only and MAG_MULT stays cross-wave.")

    # ---- finding [7] as an enforced invariant, not a comment. The spectator *O
    # must sit at exactly the same y in the 2x1o `mir` and `off` adslab decks --
    # otherwise S(2x1o) carries the spectator's own off-plane relaxation energy
    # and S(2x1v) does not, and the interaction term inherits the difference.
    # `ref__2x1o` is the one deck that is allowed to differ, by exactly the kick.
    y_unkicked = round(spec_mir[0][2], 8)
    for j in jobs:
        if j["arm"] != "2x1o" or j["spectator_y"] is None:
            continue
        want = y_unkicked + (SPECTATOR_KICK_A if j["job"] == "ref__2x1o" else 0.0)
        if abs(j["spectator_y"] - want) > 1e-6:
            raise SystemExit(
                f"refusing to build {M}: spectator *O in {j['job']} sits at "
                f"y = {j['spectator_y']:.6f}, expected {want:.6f}. "
                f"{DOC43} s2-A.2 allows the kick in ref__2x1o and nowhere else; "
                "a spectator that differs between the symmetry arms puts its own "
                "relaxation energy inside the interaction term.")

    return jobs, dict(metal=M, a1=a1, a2=src["slab"]["deck"]["cell"][1][1],
                      cus_metal=[cus[0], round(cus[1], 4), round(cus[2], 4),
                                 round(cus[3], 4)],
                      y_mirror=round(y_mirror, 6),
                      nn_image_1x1=round(a1, 4), nn_image_2x1=round(2 * a1, 4),
                      kmesh_1x1=" ".join(cfg["kmesh_1x1"]),
                      kmesh_2x1=" ".join(KMESH_2X1), k_folds_exactly=cfg["kfolds"],
                      measured_1x1_ionic_steps={s: src[s]["steps_1x1"] for s in STATES},
                      geometry_sources={s: src[s]["geom_src"] for s in STATES},
                      mask_fixed=[i for i, f in enumerate(mask) if f == "0 0 0"])


# ------------------------------------------------------- wave 2: GATE-1 SCFs ---

def cmd_gate1(a):
    """Emit the fresh-density GATE-1 SCF for every Cr relaxation in the block.

    docs/43 s2-A.3(b) registers the 2x1 relaxations; amendment 4 extends the
    same control to the 1x1 rows. One fixed-geometry SCF per Cr relaxation,
    at that relaxation's own final
    coordinates, from a fresh atomic superposition, required to agree to <= 5 meV.
    It also captures s2-A.3(a): the total and absolute magnetisation of the
    parent relaxation are recorded here, so the mir/off pair comparison has an
    artifact to read.

    This is wave 2 by construction -- it cannot run until the relaxations have
    converged, and it refuses rather than guessing.
    """
    man_path = os.path.join(a.out, "cellsym_manifest.json")
    if not os.path.exists(man_path):
        raise SystemExit(f"refusing: {man_path} not found; build the block first")
    man = json.load(open(man_path, encoding="utf-8"))
    # s2-A.3(b) registers the 2x1 relaxations; amendment 4 extends GATE-1 to
    # EVERY Cr relaxation this block emits -- the failure it catches was first
    # measured on a 1x1 (Cr *OOH, -178.58 meV, docs/41 s6f), so the 1x1 rows
    # are just as exposed and the marginal cost is five cheap SCFs.
    targets = [j for j in man["jobs"]
               if j["metal"] == "Cr" and j["calculation"] == "relax"]
    # amendment 4 s2: EVERY Cr relaxation gets a GATE-1 child -- including the
    # s2-A.2 contingency relaxation, whose row lives in the refmir manifest.
    rm_path = os.path.join(a.out, "cellsym_refmir_manifest.json")
    if os.path.exists(rm_path):
        rman = json.load(open(rm_path, encoding="utf-8"))
        targets += [j for j in rman["jobs"]
                    if j["metal"] == "Cr" and j["calculation"] == "relax"]
    if not targets:
        raise SystemExit("refusing: no Cr relaxations in the manifest")

    cfg = METALS["Cr"]
    rd, n_slab = cfg["rundir"], cfg["n_slab"]
    outdir = os.path.join(a.out, "Cr_cellsym")
    mask = parse_input_deck(os.path.join(rd, "slab.in"))["flags"][:n_slab]
    y_mirror = [g for g in man["geometry"] if g["metal"] == "Cr"][0]["y_mirror"]

    not_ready, emitted = [], []
    for j in targets:
        op = os.path.join(outdir, j["job"] + ".out")
        if not os.path.exists(op):
            not_ready.append(f"{j['job']}: no .out")
            continue
        txt = open(op, errors="replace").read()
        if "bfgs converged" not in txt:
            # hard rule 3: JOB DONE is not success. A max_seconds or nstep stop
            # writes `Begin final coordinates` too, so provenance is not enough.
            not_ready.append(f"{j['job']}: no `bfgs converged` "
                             f"(JOB DONE present: {'JOB DONE' in txt})")
            continue
        pos, prov = parse_final_coordinates(op)
        if pos is None or prov != "final" or len(pos) != j["nat"]:
            not_ready.append(f"{j['job']}: geometry provenance {prov!r}")
            continue
        emitted.append((j, op, pos))

    if not_ready:
        raise SystemExit("refusing to emit any GATE-1 deck; "
                         f"{len(not_ready)} of {len(targets)} Cr relaxations "
                         "are not scoreable yet:\n  " + "\n  ".join(not_ready))

    rows = []
    for j, op, pos in emitted:
        name = j["job"] + "__g1"
        d = dict(parse_input_deck(os.path.join(rd, j["deck_source"] + ".in")))
        # 1x1 parents keep their own cell and mesh; 2x1 parents doubled a1.
        n_halves = 2 if j["arm"] in ("2x1v", "2x1o") else 1
        n_ads = j["nat"] - n_halves * n_slab
        d["flags"] = list(mask) * n_halves + ["1 1 1"] * n_ads
        # Round-2 finding N3: the build path sets nosym for sym in
        # ("off", "off_fixed", "none") -- ref__2x1v is emitted with sym="none"
        # and runs nosym/noinv at 16 k-points. A GATE-1 child that turns
        # symmetry back on moves the k-set and the symmetry treatment at the
        # same time, so a >5 meV disagreement cannot be attributed and a <5 meV
        # agreement certifies nothing. Mirror the build path exactly -- and
        # then check against the PARENT'S EMITTED BYTES, not this derivation
        # (verify-round residual: the two call-site derivations used to
        # cross-check only each other, so a coordinated revert slipped both).
        d["nosym"] = j["sym"] in ("off", "none")
        parent_deck = os.path.join(outdir, j["job"] + ".in")
        ptxt = open(parent_deck, encoding="utf-8", errors="replace").read()
        parent_nosym = bool(re.search(r"^\s*nosym\s*=\s*\.true\.", ptxt,
                                      re.M | re.I))
        if parent_nosym != d["nosym"]:
            raise SystemExit(
                f"refusing to emit {name}: parent deck {parent_deck} carries "
                f"nosym={parent_nosym} but the child would carry {d['nosym']} "
                "-- a GATE-1 child must run at the parent's own symmetry "
                "treatment (N3)")
        d["cell"] = [[d["cell"][0][0] * float(n_halves), 0.0, 0.0],
                     list(d["cell"][1]), list(d["cell"][2])]
        kmesh = tuple(j["kmesh"].split())
        d["kpts"] = ("automatic", list(kmesh) + ["0", "0", "0"])
        text, _ = write_probe(d, pos, parse_variant("base"), name, a.pseudo_dir,
                              a.scratch, calculation="scf")
        h4 = est_hours_np4(j["n_kpt_est"], SCF_STEP_EQUIV, True, n_halves == 2)
        h_run = h4 / RANK_SPEEDUP_NP20
        ms = max(MAX_SECONDS_FLOOR, int(round(MAX_SECONDS_SAFETY * h_run * 3600)))
        cut = text.index("\n/\n")
        text = text[:cut] + f"\n  max_seconds = {ms}" + text[cut:]
        guard(text, os.path.join(rd, j["deck_source"] + ".in"), name,
              dict(cell_mult=float(n_halves), kmesh=kmesh, nat=j["nat"],
                   n_halves=n_halves, y_mirror=y_mirror,
                   # "none" parents pass off_fixed so the guard re-checks
                   # nosym AND noinv on the emitted bytes (N3).
                   sym=("off_fixed" if j["sym"] in ("off", "none")
                        else "mir_fixed"),
                   max_seconds=ms))
        blob = text.encode("utf-8")
        if not a.dry_run:
            with open(os.path.join(outdir, name + ".in"), "wb") as fh:
                fh.write(blob)
        tot, ab = final_magnetisation(op)
        rows.append(dict(job=name, parent=j["job"], sym=j["sym"], arm=j["arm"],
                         state=j["state"], nk=j["nk"], max_seconds=ms,
                         est_hours_at_np20=round(h_run, 1),
                         parent_final_energy_ev=relax_final_energy_ev(op),
                         parent_total_magnetization=tot,
                         parent_absolute_magnetization=ab,
                         md5=hashlib.md5(blob).hexdigest()))

    lines = ["# docs/43 s2-A.3(b) + amendment 4: one fresh-density",
             f"# fixed-geometry SCF per Cr relaxation, tolerance "
             f"{PREREG['cr_gate1_scf_tol_meV'][0]} meV.",
             "# NP=20 NCONC=1",
             "# bash queue_r1.sh m_cellsym_gate1.txt 20 1",
             # NOT "# NP=20 is an exact multiple ..." -- a comment that BEGINS
             # like a directive trips queue_r1's malformed-np-directive refusal.
             "# 20 is an exact multiple of every nk below; NP x NCONC <= 23."]
    lines += [f"probe/Cr_cellsym {r['job']} .in {r['nk']}" for r in rows]
    if not a.dry_run:
        with open(os.path.join(a.out, "m_cellsym_gate1.txt"), "w",
                  encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(lines) + "\n")
        with open(os.path.join(a.out, "cellsym_gate1_manifest.json"), "w",
                  encoding="utf-8", newline="\n") as fh:
            json.dump(dict(prereg=f"{DOC43} s2-A.3", jobs=rows), fh, indent=2)
    print(f"{len(rows)} GATE-1 SCFs -> {outdir}")
    return 0


# ------------------- s2-A.2 registered contingency: ref__2x1o_mir (--refmir) ---

def cmd_refmir(a):
    """Emit the registered spectator-contingency deck `ref__2x1o_mir` per metal.

    docs/43 s2 (amendment 4) registered, before the fact: if `ref__2x1o`'s
    spectator relaxes to |dy| > 0.02 A, a `ref__2x1o_mir` job is added BEFORE
    the interaction term S(2x1o) - S(2x1v) is scored. This emitter measures the
    trigger from `ref__2x1o.out` itself and REFUSES to emit for a metal whose
    contingency has not fired -- an untriggered mir ref would be a new arm, not
    the registered contingency. The deck is `ref__2x1o` with the spectator
    pinned on the mirror plane (spec_mir, no kick) and the mirror arm's
    symmetry treatment (no nosym/noinv, mirror-folded k-set): exactly the
    construction every 2x1o mir deck in the block uses.
    """
    man_path = os.path.join(a.out, "cellsym_manifest.json")
    if not os.path.exists(man_path):
        raise SystemExit(f"refusing: {man_path} not found; build the block first")
    man = json.load(open(man_path, encoding="utf-8"))
    dy_tol = PREREG["spectator_contingency_dy_A"][0]

    rows = []
    for M in a.metals:
        cfg = METALS[M]
        rd, n_slab = cfg["rundir"], cfg["n_slab"]
        outdir = os.path.join(a.out, f"{M}_cellsym")
        name = "ref__2x1o_mir"

        # ---- the trigger, measured from ref__2x1o.out itself (never from a
        # readout file: the builder re-derives what it acts on)
        op = os.path.join(outdir, "ref__2x1o.out")
        rec = read_out(op)
        if not _scoreable(rec, "relax"):
            raise SystemExit(f"refusing {M}: ref__2x1o is not a converged relax "
                             f"({op}); the contingency cannot be evaluated")
        pos_ref, prov = parse_final_coordinates(op)
        man_geom = [g for g in man["geometry"] if g["metal"] == M][0]
        y_mirror_man = man_geom["y_mirror"]
        if pos_ref is None or prov != "final":
            raise SystemExit(f"refusing {M}: ref__2x1o geometry provenance {prov!r}")
        dy = abs(pos_ref[-1][2] - y_mirror_man)
        if dy <= dy_tol:
            raise SystemExit(
                f"refusing {M}: measured spectator |dy| = {dy:.4f} A <= {dy_tol} "
                "-- the s2-A.2 contingency has NOT fired for this metal and a "
                "mir ref would be a new arm, not the registered contingency")

        # ---- rebuild the wave-1 geometry from the same sources build_metal
        # used, and refuse if they have moved since wave 1
        src = {job: load(rd, job, cfg["basin_out"].get(job))
               for job in ("slab", "s0_O", "s0_OOH")}
        slab_clean = src["slab"]["pos"]
        cus = cus_metal(slab_clean, src["s0_OOH"]["pos"][n_slab:])
        y_mirror = cus[2]
        # the manifest records y_mirror rounded (5 decimals); a real source move
        # is >= 1e-4, so 1e-5 separates rounding from drift
        if abs(y_mirror - y_mirror_man) > 1e-5:
            raise SystemExit(f"refusing {M}: re-derived y_mirror {y_mirror!r} != "
                             f"manifest {y_mirror_man!r}; sources moved since wave 1")
        a1 = src["slab"]["deck"]["cell"][0][0]
        mask = src["slab"]["deck"]["flags"][:n_slab]
        slab_O = src["s0_O"]["pos"][:n_slab]
        spec_mir = shift_x(src["s0_O"]["pos"][n_slab:], a1)
        positions = slab_clean + shift_x(slab_O, a1) + spec_mir

        d = dict(parse_input_deck(os.path.join(rd, "s0_O.in")))
        d["flags"] = list(mask) * 2 + ["1 1 1"]
        d["nosym"] = False                       # mir arm: the mirror stays on
        d["cell"] = [[d["cell"][0][0] * 2.0, 0.0, 0.0],
                     list(d["cell"][1]), list(d["cell"][2])]
        d["kpts"] = ("automatic", list(KMESH_2X1) + ["0", "0", "0"])
        text, _ = write_probe(d, positions, parse_variant("base"), name,
                              a.pseudo_dir, a.scratch, calculation="relax")

        # the mirror folds the 4x4 grid 16 -> 9, measured on this cell in the
        # build path (Ir s0_OOH__2x1v_mir probe, 2026-08-09). More symmetry than
        # the mirror would only lower nkp further; nk=2 still divides.
        nkp = 9
        steps = int(math.ceil(src["s0_O"]["steps_1x1"] * STEP_MULT_2X1))
        h4 = est_hours_np4(nkp, steps, cfg["magnetic"], True)
        h_run = h4 / RANK_SPEEDUP_NP20
        ms = max(MAX_SECONDS_FLOOR, int(round(MAX_SECONDS_SAFETY * h_run * 3600)))
        cut = text.index("\n/\n")
        text = text[:cut] + f"\n  max_seconds = {ms}" + text[cut:]
        meta = guard(text, os.path.join(rd, "s0_O.in"), name,
                     dict(cell_mult=2.0, kmesh=KMESH_2X1, nat=len(positions),
                          n_halves=2, y_mirror=y_mirror, sym="mir",
                          max_seconds=ms))
        blob = text.encode("utf-8")
        nk = 2                                   # nkp 9 < 12; 20 % 2 == 0
        if not a.dry_run:
            with open(os.path.join(outdir, name + ".in"), "wb") as fh:
                fh.write(blob)
        rows.append(dict(metal=M, job=name, deck_source="s0_O", arm="2x1o",
                         state="ref", calculation="relax", sym="mir",
                         kmesh=" ".join(KMESH_2X1), n_kpt_est=nkp, nk=nk,
                         np_run=20, steps_est=steps, max_seconds=ms,
                         est_hours_at_np20=round(h_run, 1),
                         trigger_measured_dy_A=round(dy, 4),
                         trigger_threshold_A=dy_tol,
                         spectator_y=round(positions[-1][2], 8),
                         md5=hashlib.md5(blob).hexdigest(), **meta))

    lines = ["# docs/43 s2 amendment-4 registered contingency (s2-A.2): the",
             "# ref__2x1o spectator settled off-plane, so the mirror reference",
             "# runs BEFORE the interaction S(2x1o) - S(2x1v) is scored.",
             "# NP=20 NCONC=1",
             "# bash queue_r1.sh m_cellsym_refmir.txt 20 1",
             "# 20 is an exact multiple of every nk below; NP x NCONC <= 23."]
    lines += [f"probe/{r['metal']}_cellsym {r['job']} .in {r['nk']}" for r in rows]
    if not a.dry_run:
        with open(os.path.join(a.out, "m_cellsym_refmir.txt"), "w",
                  encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(lines) + "\n")
        with open(os.path.join(a.out, "cellsym_refmir_manifest.json"), "w",
                  encoding="utf-8", newline="\n") as fh:
            json.dump(dict(prereg=f"{DOC43} s2-A.2 registered contingency",
                           note=("Cr's ref__2x1o_mir, once converged, needs its "
                                 "__g1 fresh-density child before its energy "
                                 "enters any gate or pair (amendment 4 s2)."),
                           jobs=rows), fh, indent=2)
    for r in rows:
        print(f"{r['metal']}: {r['job']} dy={r['trigger_measured_dy_A']} A "
              f"steps_est={r['steps_est']} max_seconds={r['max_seconds']} "
              f"md5={r['md5'][:8]}")
    print(f"{len(rows)} contingency decks -> {a.out}")
    return 0


# ------------------------------------------------ the readout: --score (wave 3) ---
#
# docs/43 s2-A.3(a) and s2-A.4 are RULES, and until this existed they were rules
# with nothing behind them: `cellsym_manifest.json` declared "record total and
# absolute magnetisation for every Cr job" and "GATE C is an energy AND
# magnetisation test", and no code read either. A declared threshold that no code
# evaluates is the failure this whole fix round is about, so the readout is here,
# written BEFORE the numbers exist. It computes and it refuses to guess: a pair
# whose two halves are not both scoreable comes back PENDING, never OK.

def read_out(path):
    """Everything s2-A.3/s2-A.4/s1 need from one pw.x output, or None if absent."""
    if not path or not os.path.exists(path):
        return None
    txt = open(path, errors="replace").read()
    tot, ab = final_magnetisation(path)
    return dict(path=path.replace("\\", "/"),
                energy_ev=relax_final_energy_ev(path),
                total_magnetization=tot, absolute_magnetization=ab,
                bfgs_converged="bfgs converged" in txt,
                scf_fail="convergence NOT achieved" in txt,
                max_seconds_stop="Maximum CPU time exceeded" in txt,
                job_done="JOB DONE" in txt,
                ionic_steps=len(re.findall(r"Total force", txt)))


def _scoreable(rec, calculation):
    """Hard rule 3: never `JOB DONE`. A relax must have converged; an SCF must
    have produced an energy without an SCF failure."""
    if rec is None or rec["energy_ev"] is None or rec["scf_fail"]:
        return False
    return rec["bfgs_converged"] if calculation == "relax" else True


def _mag_complete(rec):
    """Verify-round finding: every magnetisation threshold in the scorer was
    guarded by `is not None`, so an .out with the lines MISSING sailed through
    the registered magnetic tests -- a demonstrated CONFOUNDED pair flipped to
    OK when the lines were stripped. For a magnetic metal, absence of the
    record is NOT_SCOREABLE, never a pass (same shape as ledger N38)."""
    return (rec.get("total_magnetization") is not None
            and rec.get("absolute_magnetization") is not None)


def cmd_score(a):
    """Read block 1A: GATE-1, the Cr pair test, GATE C/C-2/R, the sign rule,
    and the s2-A.2 spectator contingency."""
    man_path = os.path.join(a.out, "cellsym_manifest.json")
    if not os.path.exists(man_path):
        raise SystemExit(f"refusing: {man_path} not found; build the block first")
    man = json.load(open(man_path, encoding="utf-8"))
    by_job = {(j["metal"], j["job"]): j for j in man["jobs"]}
    mag_tol = PREREG["cr_pair_magnetisation_tol_bohrmag"][0]
    e_tol = PREREG["gate_c_energy_tol_meV"][0]
    gc_mag_tol = PREREG["gate_c_magnetisation_tol_bohrmag"][0]
    sign_tol = PREREG["sign_rule_max_positive_dE_sym_eV"][0]
    g1_tol = PREREG["cr_gate1_scf_tol_meV"][0]

    def deck_out(M, job):
        return os.path.join(a.out, f"{M}_cellsym", job + ".out")

    def prod_out(M, state):
        cfg = METALS[M]
        return cfg["basin_out"].get(state) or os.path.join(cfg["rundir"],
                                                           state + ".out")

    # ---- s2-A.3(a): the record itself, one row per job of a magnetic metal.
    records = []
    for (M, job), j in sorted(by_job.items()):
        if not METALS[M]["magnetic"]:
            continue
        rec = read_out(deck_out(M, job))
        records.append(dict(metal=M, job=job, arm=j["arm"], state=j["state"],
                            sym=j["sym"], calculation=j["calculation"],
                            status=("PENDING" if rec is None else
                                    "SCOREABLE" if _scoreable(rec, j["calculation"])
                                    else "NOT_SCOREABLE"),
                            **(rec or {})))

    # ---- s2-A.3(b): GATE-1, EVALUATED (finding U5: this threshold used to
    # have an emitter and a recorder and no evaluator). One row per __g1 SCF:
    # AGREE within 5 meV, else BASIN_DRIFT -- in which case the fresh-density
    # SCF energy is the corrected value (docs/41 s6f measured the GATE-1 SCF
    # reproducing the true basin to 2-3.5 meV on all three restarts).
    gate1_rows = []
    g1_child = {}       # parent job name -> the child's read_out record
    g1man_path = os.path.join(a.out, "cellsym_gate1_manifest.json")
    if os.path.exists(g1man_path):
        g1man = json.load(open(g1man_path, encoding="utf-8"))
        for r in g1man["jobs"]:
            child = read_out(deck_out("Cr", r["job"]))
            row = dict(job=r["job"], parent=r["parent"], tol_meV=g1_tol,
                       parent_final_energy_ev=r["parent_final_energy_ev"])
            if not _scoreable(child, "scf"):
                row.update(verdict="PENDING",
                           reason="GATE-1 SCF not scoreable yet")
            else:
                dE_meV = (child["energy_ev"]
                          - r["parent_final_energy_ev"]) * 1000.0
                row["dE_meV"] = round(dE_meV, 3)
                if r.get("parent_total_magnetization") is not None and \
                        child["total_magnetization"] is not None:
                    row["d_total_magnetization"] = round(
                        child["total_magnetization"]
                        - r["parent_total_magnetization"], 4)
                if r.get("parent_absolute_magnetization") is not None and \
                        child["absolute_magnetization"] is not None:
                    row["d_absolute_magnetization"] = round(
                        child["absolute_magnetization"]
                        - r["parent_absolute_magnetization"], 4)
                if abs(dE_meV) <= g1_tol:
                    row.update(verdict="AGREE", reason="")
                else:
                    row.update(verdict="BASIN_DRIFT", reason=(
                        f"|dE| {abs(dE_meV):.2f} meV > {g1_tol}: the parent "
                        "relaxation ended in a different SCF solution than a "
                        "fresh density finds. The GATE-1 SCF energy is the "
                        "corrected value (docs/41 s6f); the pair below is "
                        "scored from it."))
                g1_child[r["parent"]] = child
            gate1_rows.append(row)

    def gate1_passed(job_name, rec):
        """docs/43 s1: Cr pair members enter DE_sym as GATE-1-PASSED energies.

        Returns (record-to-score, provenance) or (None, why-not). A manifest Cr
        relaxation needs its __g1 child; the Cr *OOH basin restart is
        prevalidated (its step-1 energy reproduced the audit SCF to 8.7e-4 meV,
        docs/41 s6f) and enters as-is.
        """
        if job_name is None:
            return rec, "prevalidated (docs/41 s6f basin restart / production)"
        child = g1_child.get(job_name)
        if child is None:
            return None, (f"{job_name}: no scoreable GATE-1 SCF -- s2-A.3(b) "
                          "is a precondition of the readout")
        r2 = dict(rec)
        r2["energy_ev"] = child["energy_ev"]
        r2["total_magnetization"] = child["total_magnetization"]
        r2["absolute_magnetization"] = child["absolute_magnetization"]
        return r2, "gate1 SCF"

    # ---- s2-A.3(a) + s1: the mir/off pairs. Ir/Ru 1x1 mirror rows are the
    # production runs; Cr's s0_O/s0_OH mirror rows are the amendment-2
    # re-emissions and Cr *OOH's is the basin restart (all local-TF, so each
    # pair differs from its partner in exactly one thing -- finding N11).
    pairs = []
    for M in METALS:
        for state in STATES:
            for arm in ("1x1", "2x1v", "2x1o"):
                if arm == "1x1":
                    if M == "Cr" and state in CR_MIR_REEMIT:
                        mir_j = f"{state}__1x1_mir"
                        mir_p, mir_calc = deck_out(M, mir_j), "relax"
                        mir_name = mir_j
                    else:
                        mir_p, mir_calc = prod_out(M, state), "relax"
                        mir_name = None
                    off_j = f"{state}__1x1_off"
                    reused = (M, state, "1x1", "off") in ALREADY_ON_DISK
                    off_p = (ALREADY_ON_DISK.get((M, state, "1x1", "off"))
                             or deck_out(M, off_j))
                    off_name = None if reused else off_j
                else:
                    mir_j, off_j = f"{state}__{arm}_mir", f"{state}__{arm}_off"
                    if (M, mir_j) not in by_job:
                        continue
                    mir_p, mir_calc = deck_out(M, mir_j), "relax"
                    off_p = deck_out(M, off_j)
                    mir_name, off_name = mir_j, off_j
                mir, off = read_out(mir_p), read_out(off_p)
                ok = _scoreable(mir, mir_calc) and _scoreable(off, "relax")
                row = dict(metal=M, state=state, arm=arm,
                           mir=mir_p.replace("\\", "/"),
                           off=off_p.replace("\\", "/"))
                if not ok:
                    row.update(verdict="PENDING", reason=(
                        "mirror arm not scoreable" if not _scoreable(mir, mir_calc)
                        else "off-plane arm not scoreable"))
                    pairs.append(row)
                    continue
                if METALS[M]["magnetic"]:
                    mir, mir_prov = gate1_passed(mir_name, mir)
                    off, off_prov = gate1_passed(off_name, off)
                    if mir is None or off is None:
                        row.update(verdict="PENDING_GATE1",
                                   reason=mir_prov if mir is None else off_prov)
                        pairs.append(row)
                        continue
                    row["energy_provenance"] = dict(mir=mir_prov, off=off_prov)
                    if not (_mag_complete(mir) and _mag_complete(off)):
                        side = "mir" if not _mag_complete(mir) else "off"
                        row.update(verdict="NOT_SCOREABLE", reason=(
                            f"the {side} member's output carries no "
                            "magnetisation record -- s2-A.3(a) requires it for "
                            "every Cr job, and a missing record must not score "
                            "as agreement"))
                        pairs.append(row)
                        continue
                dE = off["energy_ev"] - mir["energy_ev"]
                row["dE_sym_eV"] = round(dE, 6)
                # finding U4: threshold BOTH magnetisations. An antiferromagnetic
                # rearrangement -- the exact failure s2-A.3 names for the 2x1 --
                # has dM_total = 0 and a large dM_absolute.
                confound = []
                if mir["total_magnetization"] is not None and \
                        off["total_magnetization"] is not None:
                    dMt = off["total_magnetization"] - mir["total_magnetization"]
                    row["d_total_magnetization"] = round(dMt, 4)
                    if abs(dMt) > mag_tol:
                        confound.append(f"total {abs(dMt):.3f}")
                if mir["absolute_magnetization"] is not None and \
                        off["absolute_magnetization"] is not None:
                    dMa = (off["absolute_magnetization"]
                           - mir["absolute_magnetization"])
                    row["d_absolute_magnetization"] = round(dMa, 4)
                    if abs(dMa) > mag_tol:
                        confound.append(f"absolute {abs(dMa):.3f}")
                if confound:
                    row.update(verdict="CONFOUNDED", reason=(
                        f"|d magnetisation| ({', '.join(confound)}) > {mag_tol} "
                        f"mu_B ({DOC43} s2-A.3(a) / s5): the pair mixes a "
                        "geometry effect with a magnetic basin change. Excluded "
                        "from every symmetry statistic and reported separately."))
                elif dE > sign_tol:
                    row.update(verdict="SIGN_VIOLATION", reason=(
                        f"dE_sym = +{dE:.4f} eV > +{sign_tol} ({DOC43} s1): an "
                        "additional search direction cannot raise the minimum, so "
                        "this is a failure of the search or of the comparison. "
                        "The arm is voided, not reported as 'symmetry does not "
                        "matter here'."))
                else:
                    row.update(verdict="OK", reason="")
                pairs.append(row)

    # ---- s2-A.4: GATE C / C-2, energy AND magnetisation (both kinds, U4).
    # For Ir/Ru the 1x1 baseline is the production relaxation (mesh folds
    # exactly). For Cr it is the __1x1_k8_relax job -- RELAXED at the folded
    # mesh (finding N10 / amendment 4) so both sides are the same protocol; the
    # k8 SCF is kept as the k-mesh bridge and the difference between the two is
    # reported as mesh_relaxation_meV, which separates "the 1x1 geometry was
    # not stationary at the folded mesh" from "the cell construction is wrong".
    gates = []
    for M in METALS:
        folds = METALS[M]["kfolds"]
        for name, big_job, small, small_name, bridge in (
                ("GATE C", "ref__2x1v",
                 prod_out(M, "slab") if folds else deck_out(M, "slab__1x1_k8_relax"),
                 None if folds else "slab__1x1_k8_relax",
                 None if folds else deck_out(M, "slab__1x1_k8")),
                ("GATE C-2", "s0_O__2x1o_mir",
                 prod_out(M, "s0_O") if folds else deck_out(M, "s0_O__1x1_k8_relax"),
                 None if folds else "s0_O__1x1_k8_relax",
                 None if folds else deck_out(M, "s0_O__1x1_k8"))):
            if (M, big_job) not in by_job:
                continue
            big = read_out(deck_out(M, big_job))
            ref = read_out(small)
            g = dict(metal=M, gate=name, big=big_job,
                     baseline=small.replace("\\", "/"),
                     tol_meV=e_tol, tol_bohrmag=gc_mag_tol)
            if bridge is not None:
                br = read_out(bridge)
                if _scoreable(br, "scf") and _scoreable(ref, "relax"):
                    g["mesh_relaxation_meV"] = round(
                        (ref["energy_ev"] - br["energy_ev"]) * 1000.0, 3)
            if not (_scoreable(big, by_job[(M, big_job)]["calculation"])
                    and _scoreable(ref, "relax")):
                g.update(verdict="PENDING")
                gates.append(g)
                continue
            if METALS[M]["magnetic"]:
                # Verify-round finding: gates were scored from RAW parent
                # energies even when that parent's own GATE-1 verdict was
                # BASIN_DRIFT -- an evaluated-then-ignored control. Gate sides
                # go through the same GATE-1 gate as pair members.
                big, big_prov = gate1_passed(big_job, big)
                ref, ref_prov = gate1_passed(small_name, ref)
                if big is None or ref is None:
                    g.update(verdict="PENDING_GATE1",
                             reason=big_prov if big is None else ref_prov)
                    gates.append(g)
                    continue
                g["energy_provenance"] = dict(big=big_prov, baseline=ref_prov)
                if not (_mag_complete(big) and _mag_complete(ref)):
                    side = "big" if not _mag_complete(big) else "baseline"
                    g.update(verdict="NOT_SCOREABLE", reason=(
                        f"the {side} output carries no magnetisation record -- "
                        "s2-A.4 tests magnetisation, and a missing record must "
                        "not score as a match"))
                    gates.append(g)
                    continue
            dE_meV = (big["energy_ev"] - 2.0 * ref["energy_ev"]) * 1000.0
            g["dE_meV"] = round(dE_meV, 3)
            fails = [f"|dE| {abs(dE_meV):.2f} meV > {e_tol}"] if abs(dE_meV) > e_tol else []
            if big["total_magnetization"] is not None and \
                    ref["total_magnetization"] is not None:
                dM = big["total_magnetization"] - 2.0 * ref["total_magnetization"]
                g["d_total_magnetization"] = round(dM, 4)
                if abs(dM) > gc_mag_tol:
                    fails.append(f"|dM total| {abs(dM):.3f} > {gc_mag_tol} mu_B")
            if big["absolute_magnetization"] is not None and \
                    ref["absolute_magnetization"] is not None:
                dMa = (big["absolute_magnetization"]
                       - 2.0 * ref["absolute_magnetization"])
                g["d_absolute_magnetization"] = round(dMa, 4)
                if abs(dMa) > gc_mag_tol:
                    fails.append(f"|dM absolute| {abs(dMa):.3f} > {gc_mag_tol} mu_B")
            if fails:
                # amendment 4 correction note: "comparable" is made numeric --
                # |dE| <= 2x|mesh_relaxation_meV| reads as MESH_RELAXATION,
                # and the readout says which (the verify round found the
                # registered reading left to a human).
                mr = g.get("mesh_relaxation_meV")
                if mr is not None:
                    g["fail_reading"] = ("MESH_RELAXATION"
                                         if abs(dE_meV) <= 2.0 * abs(mr)
                                         else "CELL_MISMATCH_OR_UNATTRIBUTED")
                    fails.append(f"read as {g['fail_reading']} "
                                 f"(mesh_relaxation_meV = {mr})")
            g.update(verdict="FAIL" if fails else "PASS", reason="; ".join(fails))
            gates.append(g)

    # ---- docs/43 s2 "Replication (gating)": GATE R (finding N2). Scores the
    # FRESH Ir s0_OOH 1x1 off-plane run -- the reused P10 output would return
    # the registered number by construction and cannot fail.
    rep_e, rep_tol = PREREG["replication_gate_ir_oohx_1x1_eV"][0]
    prow = next((p for p in pairs if p["metal"] == "Ir"
                 and p["state"] == "s0_OOH" and p["arm"] == "1x1"), None)
    g = dict(metal="Ir", gate="GATE R (replication)", expected_eV=rep_e,
             tol_eV=rep_tol,
             fresh_run="runs/probe/Ir_cellsym/s0_OOH__1x1_off.out")
    if prow is None or "dE_sym_eV" not in prow:
        g.update(verdict="PENDING",
                 reason="fresh Ir s0_OOH__1x1_off not scoreable yet")
    else:
        g["dE_sym_eV"] = prow["dE_sym_eV"]
        miss = abs(prow["dE_sym_eV"] - rep_e)
        if miss <= rep_tol:
            g.update(verdict="PASS", reason="")
        else:
            g.update(verdict="FAIL", reason=(
                f"|dE_sym - ({rep_e})| = {miss:.4f} eV > {rep_tol} ({DOC43} "
                "s2): a miss voids the block and the pipeline is debugged "
                "before anything else is read."))
    gates.append(g)

    # ---- s2-A.2 registered contingency, MEASURED (finding U2: it used to be
    # stored as OPEN with no code evaluating it). The spectator is the last
    # atom of ref__2x1o by construction.
    spectator = []
    dy_tol = PREREG["spectator_contingency_dy_A"][0]
    for M in METALS:
        if (M, "ref__2x1o") not in by_job:
            continue
        p = deck_out(M, "ref__2x1o")
        rec = read_out(p)
        y_mirror = [gm for gm in man["geometry"] if gm["metal"] == M][0]["y_mirror"]
        row = dict(metal=M, deck="ref__2x1o", threshold_A=dy_tol,
                   clause=f"{DOC43} s2-A.2")
        if not _scoreable(rec, "relax"):
            row.update(status="OPEN", reason="ref__2x1o not converged yet")
        else:
            # Verify-round finding: a converged .out with no coordinate block
            # crashed here with a TypeError, and a truncated relax's
            # 'last-step' fallback block would have been silently measured.
            pos, prov = parse_final_coordinates(p)
            nat = by_job[(M, "ref__2x1o")]["nat"]
            if pos is None or prov != "final" or len(pos) != nat:
                row.update(status="NOT_SCOREABLE", reason=(
                    f"geometry provenance {prov!r} with "
                    f"{0 if pos is None else len(pos)}/{nat} atoms -- the "
                    "spectator position cannot be trusted from this output"))
                spectator.append(row)
                continue
            dy = abs(pos[-1][2] - y_mirror)
            row["measured_dy_A"] = round(dy, 4)
            if dy > dy_tol:
                mir_rec = read_out(deck_out(M, "ref__2x1o_mir"))
                row.update(status="TRIGGERED", action=(
                    "ref__2x1o_mir exists and is converged; interaction may be "
                    "scored" if _scoreable(mir_rec, "relax") else
                    "a ref__2x1o_mir job is REQUIRED before the interaction "
                    "term S(2x1o) - S(2x1v) is scored. Adding it after reading "
                    "the interaction is post-hoc."))
            else:
                row.update(status="CLEAR")
        spectator.append(row)

    out = dict(prereg=dict(document=DOC43,
                           sections=["1", "2", "2-A.2", "2-A.3", "2-A.4"],
                           pair_magnetisation_tol_bohrmag=mag_tol,
                           gate1_scf_tol_meV=g1_tol,
                           gate_c_energy_tol_meV=e_tol,
                           gate_c_magnetisation_tol_bohrmag=gc_mag_tol,
                           sign_rule_max_positive_dE_sym_eV=sign_tol,
                           replication_gate_eV=[rep_e, rep_tol],
                           spectator_contingency_dy_A=dy_tol),
               note="PENDING means the job has not produced a defensible result "
                    "yet. Hard rule 3: a relax must carry `bfgs converged` and an "
                    "SCF a final total energy; `JOB DONE` is never the test.",
               magnetic_records=records, gate1=gate1_rows, pairs=pairs,
               gates=gates, spectator_contingency=spectator)
    if not a.dry_run:
        with open(os.path.join(a.out, "cellsym_readout.json"), "w",
                  encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, indent=2)

    def tally(rows, key="verdict"):
        c = {}
        for r in rows:
            c[r.get(key, "?")] = c.get(r.get(key, "?"), 0) + 1
        return ", ".join(f"{k} {v}" for k, v in sorted(c.items()))

    print(f"magnetic records ({len(records)} Cr jobs): {tally(records, 'status')}")
    print(f"GATE-1 SCFs ({len(gate1_rows)}): "
          f"{tally(gate1_rows) if gate1_rows else 'not emitted yet (--gate1)'}")
    print(f"mir/off pairs ({len(pairs)}): {tally(pairs)}")
    print(f"GATE C / C-2 / R ({len(gates)}): {tally(gates)}")
    print(f"spectator contingency ({len(spectator)}): {tally(spectator, 'status')}")
    for r in gate1_rows + pairs + gates:
        if r.get("verdict") not in ("OK", "PASS", "PENDING", "AGREE"):
            print(f"  {r.get('verdict')}  {r.get('metal', 'Cr')} "
                  f"{r.get('state', r.get('gate', r.get('job', '')))} "
                  f"{r.get('arm', '')}: {r.get('reason')}")
    for r in spectator:
        if r.get("status") == "TRIGGERED":
            print(f"  TRIGGERED  {r['metal']} ref__2x1o dy = "
                  f"{r.get('measured_dy_A')} A: {r.get('action')}")
    return 0


# --------------------------------------------------------------------- main ---

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="runs/probe")
    ap.add_argument("--metals", nargs="+", default=list(METALS))
    ap.add_argument("--pseudo-dir", default="/usr/share/espresso/pseudo")
    ap.add_argument("--scratch", default="./tmp")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--gate1", action="store_true",
                    help="wave 2: emit the Cr GATE-1 SCFs from converged 1A outputs")
    ap.add_argument("--refmir", action="store_true",
                    help="s2-A.2 registered contingency: emit ref__2x1o_mir for "
                         "every metal whose ref__2x1o spectator settled at "
                         "|dy| > the registered threshold")
    ap.add_argument("--score", action="store_true",
                    help="wave 3: read the block -- Cr mir/off magnetisation pairs "
                         "(docs/43 s2-A.3(a)), GATE C and C-2 (s2-A.4) and the "
                         "sign rule (s1) -> cellsym_readout.json")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    prereg = _prereg_check()
    if a.gate1:
        return cmd_gate1(a)
    if a.refmir:
        return cmd_refmir(a)
    if a.score:
        return cmd_score(a)

    all_jobs, geom = [], []
    for M in a.metals:
        jobs, g = build_metal(M, METALS[M], a.out, a.pseudo_dir, a.scratch, a.dry_run)
        all_jobs += jobs
        geom.append(g)
        print(f"{M}: {len(jobs)} decks -> {a.out}/{M}_cellsym")

    # ---- manifests, split per findings [6] and U6
    hdr = {
        "A": ["# block 1A, manifest A: the SHORT jobs (every job under "
              f"{LONG_JOB_NP4_HOURS:.0f} h",
              "# at NP=4 that is not a Cr relaxation). Throughput arm.",
              "#   bash queue_r1.sh m_cellsym_a_np4.txt 4 5",
              "# 4 ranks x 5 concurrent = 20 <= 23.04 usable cores; NP is an exact",
              "# multiple of every nk below (hard rule 4). Longest first.",
              "# The manifest's own longest job is stated in",
              "# cellsym_manifest.json manifests.A.longest_job_hours -- the wall",
              "# clock of a full-width launch is THAT number, not sum/slots",
              "# (finding U6)."],
        "B": ["# block 1A, manifest B: the LONG jobs -- every Cr relaxation plus",
              f"# any job over {LONG_JOB_NP4_HOURS:.0f} h at NP=4 -- ONE AT A "
              "TIME at full ranks.",
              "#   bash queue_r1.sh m_cellsym_b_cr_np20.txt 20 1",
              "# Renting more boxes cannot shorten a single job; only ranks can",
              "# (finding [6]). To parallelise, SPLIT THIS FILE across boxes;",
              "# never raise NCONC. NP=20 x NCONC=1 = 20 ranks <= 23.04 usable",
              "# cores, and 20 is an exact multiple of nk in {2,4}. Off-plane",
              "# jobs are ordered FIRST.",
              "# Every line here carries max_seconds. A job that stops on",
              "# max_seconds still prints JOB DONE and queue_r1.sh SKIPs on that",
              "# string, so a capped job must be REBUILT from its own",
              "# `Begin final coordinates` and its .out DELETED before requeue.",
              "# Gate on `bfgs converged`, never on JOB DONE (hard rule 3)."],
        "C": ["# block 1A, manifest C: the CELL_MULT / MAG_MULT measurement.",
              "# STATUS: RAN AND CONVERGED 2026-08-09 on box 47025043 -- all",
              "# three legs exited inside the cap (434 / 212 / 1818 s, 27/22/29",
              "# SCF iterations). CELL_MULT = 5.19, MAG per-iteration = 1.63.",
              "# Kept for provenance and for re-measurement on a new box class.",
              "#   bash queue_r1.sh m_cellmult.txt 20 1",
              f"# Three fixed-geometry SCFs, max_seconds = {CELLMULT_MAX_SECONDS}",
              "# each, identical NP=20 and nk=4 on all three legs (that is why nk",
              "# is forced here rather than derived from the k-count).",
              "# Analysis:",
              "#   for each .out take the `total cpu time spent up to now`",
              "#   increments, drop the first and last, take the MEDIAN, and",
              "#   divide by ceil(`number of k points` / 4) -- the k-points the",
              "#   MASTER POOL carried, not the total. The 2x1 leg has 9 k-points",
              "#   over 4 pools (3,2,2,2) and normalising by 9/4 would overstate",
              "#   its per-k cost by 33%:",
              "#     CELL_MULT = Cr 2x1o / Cr 1x1",
              "#     MAG_MULT  = (Cr 1x1 / Ru 1x1) x (SCF iterations per ionic",
              "#                 step, Cr 26.1-28.8 vs Ir/Ru 11.9-13.9 measured)",
              "# Until this returns, CELL_MULT = 5.5 planning / 8.0 ceiling /",
              "# 4.0 floor and MAG_MULT = 3.5 are ESTIMATES, and every hour",
              "# quoted from them is an estimate too."],
    }
    order = {"A": lambda j: -j["est_hours_at_np"],
             "B": lambda j: (0 if j["sym"] == "off" else 1, -j["est_hours_at_np"]),
             "C": lambda j: j["job"]}
    written = {}
    for key, cfgm in MANIFESTS.items():
        sel = sorted([j for j in all_jobs if j["manifest"] == key], key=order[key])
        # Machine directives, parsed by queue_r1.sh's pre-flight:
        #   NP/NCONC (finding N6) -- every max_seconds below was computed at
        #   THIS NP; running the manifest at a lower NP silently truncates jobs
        #   at ~NP_run/NP of the work, so the pre-flight refuses a mismatch.
        #   EXPECT_CAP (finding N7, manifest C only) -- these legs are DESIGNED
        #   to stop on max_seconds; a capped .out here is the deliverable, not
        #   a stale file, and must never be deleted.
        lines = [f"# NP={cfgm['np']} NCONC={cfgm['nconc']}"]
        if key == "C":
            lines.append("# EXPECT_CAP")
        lines += list(hdr[key])
        for j in sel:
            lines.append(f"probe/{j['metal']}_cellsym {j['job']} .in {j['nk']}")
        written[key] = dict(file=cfgm["file"], np=cfgm["np"], nconc=cfgm["nconc"],
                            n_jobs=len(sel),
                            command=f"bash queue_r1.sh {cfgm['file']} "
                                    f"{cfgm['np']} {cfgm['nconc']}",
                            sum_hours=round(sum(j["est_hours_at_np"] for j in sel), 1),
                            longest_job_hours=max([j["est_hours_at_np"] for j in sel],
                                                  default=0.0))
        if not a.dry_run:
            with open(os.path.join(a.out, cfgm["file"]), "w",
                      encoding="utf-8", newline="\n") as fh:
                fh.write("\n".join(lines) + "\n")

    # the single-NP manifest this replaces is a trap: launching it would run the
    # Cr tail at NP=4 and reproduce finding [6] exactly.
    old = os.path.join(a.out, SUPERSEDED_MANIFEST)
    if os.path.exists(old) and not a.dry_run:
        os.remove(old)
        print(f"removed superseded {old} (split into "
              f"{', '.join(c['file'] for c in MANIFESTS.values())})")

    # every Cr relaxation gets a GATE-1 child (s2-A.3(b) + amendment 4)
    cr_relax = [j for j in all_jobs
                if j["metal"] == "Cr" and j["calculation"] == "relax"]
    manifest = dict(
        block="1A -- cell x symmetry crossed factorial",
        prereg=dict(
            document=DOC43,
            sections=["2", "2-A"],
            rule="docs/43 is the only pre-registration for this block. This "
                 "manifest and its builder are implementations of it. Where they "
                 "disagree, docs/43 wins.",
            anchors_verified=prereg),
        design="3 metals x 3 cells {1x1,2x1v,2x1o} x 2 symmetry {mir,off} x 3 "
               "states {*O,*OH,*OOH}, each arm with its own reference",
        reused_from_disk={f"{k[0]}/{k[1]}/{k[2]}/{k[3]}": v
                          for k, v in ALREADY_ON_DISK.items()},
        cost_model=dict(
            sec_per_kpt_step=SEC_PER_KPT_STEP,
            sec_per_kpt_step_basis="MEASURED: Ru/Ir s0_OOH__yaw90 at NP=4, "
                                   "npool=4, NCONC=4 (50.1 and 47.1 s)",
            mag_mult=MAG_MULT,
            mag_mult_basis="MEASURED 2026-08-09 (m_cellmult wave, box 47025043): "
                           "per-iteration-per-master-k Cr/Ru = 1.63 at identical "
                           "NP=20/nk=4/state, x the archive iters-per-step ratio "
                           "26.1-28.8 vs 11.9-13.9 = band [3.06, 4.03]; 3.5 "
                           "retained mid-band",
            mag_mult_bracket=list(MAG_MULT_BRACKET),
            mag_mult_caveat="the pre-measurement optimistic end (1.0, from "
                            "cross-box relaxation timings) is EXCLUDED by the "
                            "same-box measurement; those timings were "
                            "contaminated by box sharing.",
            cell_mult_floor=CELL_MULT_FLOOR,
            cell_mult_planning=CELL_MULT_PLANNING,
            cell_mult_ceiling=CELL_MULT_CEILING,
            cell_mult_status="MEASURED 2026-08-09 (m_cellmult wave): 20.52/3.95 "
                             "= 5.19 s/master-k, estimator spread 5.19-5.21. "
                             "Floor/ceiling are a labelled +/-15% allowance for "
                             "state dependence (only s0_OH was measured).",
            step_mult_2x1=STEP_MULT_2X1,
            step_mult_status="ASSUMED. 22 free atoms against 11 and a spliced "
                             "half-and-half start. The measured 1x1 counts are "
                             "the floor.",
            scf_step_equiv=SCF_STEP_EQUIV,
            rank_speedup_np20=RANK_SPEEDUP_NP20,
            rank_speedup_bracket=list(RANK_SPEEDUP_BRACKET),
            rank_speedup_basis="Ir *OOH, identical cell: NP=4/npool=4 3.39 "
                               "s/kpt/SCF-iteration (probe/Ir/s0_OOH__base) vs "
                               "NP=20/npool=4 0.669 (probe/Ir_hess/"
                               "s0_OOH__hess_ref) = 5.07x, but the NP=4 arm was "
                               "sharing the box. Relaxations NP=4 -> NP=12 give "
                               "1.50x for 3x ranks. 3.0 is the conservative end.",
            max_seconds_rule=f"{MAX_SECONDS_SAFETY}x the estimate at the NP the "
                             f"job will run at, floor {MAX_SECONDS_FLOOR} s "
                             f"(finding [8](iii))"),
        manifests=written,
        superseded_manifests=[SUPERSEDED_MANIFEST],
        pending_measurements=[
            dict(name="CELL_MULT and MAG_MULT",
                 status="MEASURED 2026-08-09 -- wave ran on box 47025043, all "
                        "three legs converged inside the cap (434/212/1818 s). "
                        "CELL_MULT 5.19 (spread 5.19-5.21), MAG per-iteration "
                        "1.63 -> MAG_MULT band [3.06, 4.03], 3.5 retained. "
                        "Outputs: runs/probe/{Cr,Ru}_cellsym/*__cellmult.out.",
                 manifest=MANIFESTS["C"]["file"],
                 command=f"bash queue_r1.sh {MANIFESTS['C']['file']} 20 1",
                 cost=(f"actual: 2464 s box time against the budgeted "
                       f"{3 * CELLMULT_MAX_SECONDS} s cap"),
                 blocks="nothing -- every hour in this manifest is now quoted "
                        "from the measurement"),
        ],
        gates=dict(
            gate_c=dict(
                clause=f"{DOC43} s2 / s2-A.4",
                energy_tol_meV=PREREG["gate_c_energy_tol_meV"][0],
                magnetisation_tol_bohrmag=PREREG["gate_c_magnetisation_tol_bohrmag"][0],
                test="|E(2x1 clean) - 2 E(1x1 clean at the folded mesh)| within "
                     "tolerance AND total magnetisation within tolerance. Energy "
                     "alone can be passed by a different magnetic state at "
                     "near-degeneracy.",
                second_control="s0_O__2x1o_mir is the exact replication of the "
                               "relaxed 1x1 *O cell and must return 2 x E(1x1 *O "
                               "at the folded mesh) to the same tolerance"),
            spectator_contingency=dict(
                clause=f"{DOC43} s2-A.2",
                registered_before_the_fact=True,
                kicked_deck="ref__2x1o",
                kick_A=SPECTATOR_KICK_A,
                test="after ref__2x1o converges, measure the spectator O's "
                     "|y - y_cus|",
                threshold_A=PREREG["spectator_contingency_dy_A"][0],
                action="if |dy| exceeds the threshold, a ref__2x1o_mir job is "
                       "REQUIRED before the interaction term S(2x1o) - S(2x1v) "
                       "is scored. Adding it after reading the interaction is "
                       "post-hoc.",
                status="OPEN -- ref__2x1o has not run"),
            cr_magnetic=dict(
                clause=f"{DOC43} s2-A.3",
                record=["total magnetization", "absolute magnetization"],
                per="every Cr job, every SCF iteration (pw.x prints it free)",
                pair_tol_bohrmag=PREREG["cr_pair_magnetisation_tol_bohrmag"][0],
                pair_action="a mir/off pair that disagrees by more than the "
                            "tolerance is CONFOUNDED under docs/43 s5: excluded "
                            "from every symmetry statistic and reported "
                            "separately",
                gate1_scf_tol_meV=PREREG["cr_gate1_scf_tol_meV"][0],
                gate1_jobs_required=len(cr_relax),
                gate1_emitter="build_cellsym_pilot.py --gate1 (wave 2; refuses "
                              "until every Cr relaxation has `bfgs "
                              "converged`)",
                gate1_est_hours_at_np20=round(
                    sum(est_hours_np4(j["n_kpt_est"], SCF_STEP_EQUIV, True,
                                      j["arm"] in ("2x1v", "2x1o"))
                        / RANK_SPEEDUP_NP20 for j in cr_relax), 1)),
            readout=dict(
                emitter="build_cellsym_pilot.py --score",
                artifact="cellsym_readout.json",
                evaluates=[f"{DOC43} s1 -- the sign rule on every mir/off pair",
                           f"{DOC43} s2-A.3(a) -- Cr mir/off total and absolute "
                           "magnetisation, CONFOUNDED above tolerance",
                           f"{DOC43} s2-A.4 -- GATE C and GATE C-2 on energy AND "
                           "magnetisation"],
                verdicts=["OK", "CONFOUNDED", "SIGN_VIOLATION", "PENDING",
                          "PENDING_GATE1", "NOT_SCOREABLE", "PASS", "FAIL",
                          "AGREE", "BASIN_DRIFT", "TRIGGERED", "CLEAR", "OPEN"],
                scoreability="hard rule 3: a relax must carry `bfgs converged`, "
                             "an SCF a final total energy and no `convergence NOT "
                             "achieved`. `JOB DONE` is never the test. A pair "
                             "whose halves are not both scoreable is PENDING, "
                             "never OK.",
                scorer_selftest="2026-08-09: the scorer's arithmetic reproduced "
                                "the two P10 rows then on disk (Ir -0.291323, "
                                "Ru -0.081714 eV). That is a CODE test, not the "
                                "replication gate: a gate that re-reads the run "
                                "it exists to replicate cannot fail (N2). The "
                                "replication gate (GATE R) scores the FRESH Ir "
                                "s0_OOH__1x1_off run and is PENDING until that "
                                "run converges."),
            sign_rule=dict(clause=f"{DOC43} s1",
                           max_positive_dE_sym_eV=PREREG["sign_rule_max_positive_dE_sym_eV"][0],
                           action="voids that arm; it is not reported as "
                                  "'symmetry does not matter here'"),
        ),
        scoring_rules=[
            "Gate on `bfgs converged`, never on `JOB DONE` (hard rule 3). pw.x "
            "prints JOB DONE after convergence NOT achieved, after nstep "
            "exhaustion, after a max_seconds stop and after a user .EXIT.",
            "A job that stopped on max_seconds must be REBUILT from its own "
            "`Begin final coordinates` and its .out DELETED before requeue: "
            "queue_r1.sh SKIPs any job whose .out contains JOB DONE, and a bare "
            "requeue would restart from the input geometry and throw the work "
            "away.",
            "Cite the measured max|F_y| or the measured |dy|, never the presence "
            "of nosym (lessons.md 2026-08-09).",
        ],
        geometry=geom,
        jobs=all_jobs)

    if not a.dry_run:
        with open(os.path.join(a.out, "cellsym_manifest.json"), "w",
                  encoding="utf-8", newline="\n") as fh:
            json.dump(manifest, fh, indent=2)

    n_relax = sum(1 for j in all_jobs if j["calculation"] == "relax")
    n_scf = len(all_jobs) - n_relax
    print(f"\n{len(all_jobs)} jobs ({n_relax} relax, {n_scf} scf)")
    for key in ("A", "B", "C"):
        w = written[key]
        print(f"  manifest {key}  {w['file']:26s} {w['n_jobs']:2d} jobs  "
              f"NP={w['np']:2d} NCONC={w['nconc']}  sum {w['sum_hours']:7.1f} h  "
              f"longest {w['longest_job_hours']:6.1f} h")
    tot_lo = sum(j["est_hours_bracket_np4"][0] for j in all_jobs)
    tot_hi = sum(j["est_hours_bracket_np4"][1] for j in all_jobs)
    print(f"  bracket over MAG_MULT {MAG_MULT_BRACKET} x CELL_MULT "
          f"[{CELL_MULT_FLOOR}, {CELL_MULT_CEILING}]: "
          f"{tot_lo:.0f}-{tot_hi:.0f} single-job hours at NP=4")
    print(f"  CELL_MULT {CELL_MULT_PLANNING} MEASURED 2026-08-09 "
          f"({MANIFESTS['C']['file']} wave; floor/ceiling "
          f"[{CELL_MULT_FLOOR}, {CELL_MULT_CEILING}] = labelled state-dependence "
          f"allowance); MAG_MULT {MAG_MULT} inside measured {MAG_MULT_BRACKET}")
    if a.dry_run:
        print("  [DRY RUN, nothing written]")

    print("\n| arm | metal | state | sym | nat | kmesh | nk | manifest | NP | "
          "steps | est h @NP | max_s |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for j in all_jobs:
        st = ("ref" if j["job"].startswith("ref__") else
              "slab" if j["state"] == "slab" else
              "*OOH" if "OOH" in j["state"] else
              "*OH" if "OH" in j["state"] else "*O")
        print(f"| {j['arm']} | {j['metal']} | {st} | {j['sym']} | {j['nat']} | "
              f"{j['kmesh']} | {j['nk']} | {j['manifest']} | {j['np_run']} | "
              f"{j['steps_est']} | {j['est_hours_at_np']:.1f} | "
              f"{j['max_seconds']} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
