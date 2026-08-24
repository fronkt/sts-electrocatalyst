#!/usr/bin/env python3
"""S3 wave-1 deck builder (46 production-seed relaxations + 9 SCFs), 2026-08-23.

SCOPE IS docs/54, NOT THIS FILE
-------------------------------
`docs/54-s3-deck-matrix-2026-08-23.md` SS0-SS1 (recipe base, cells/arms, per-metal
nspin/seed/U/pseudo/k table) is the disposition of record, derived from the deposited
A8 (DOI 10.5281/zenodo.22072991). This builder emits ONLY the wave-1 partition:

  RELAX (46): Mn 10, Fe 10 (ref__2x1v; s0_*__1x1_off x3; s0_*__2x1v_{mir,off} x3+3)
              Co 9, Ni 9 (as above MINUS s0_OOH__1x1_off -- Co 1x1 *OOH mir is a
              registered GAP and the 1x1-off row is OPEN, docs/54 SS6 item 6;
              s0_OOH__2x1v_mir IS the registered Co *OOH re-attempt on the fresh
              standard recipe, never the failed runs/Co_slab/s0_OOH.in recipe
              [docs/51:23]; Ni *OOH expected-fail -> A8.4 ladder is the registered
              outcome)
              Ti 7 (2x1v block only; NO 1x1 -- registered GAP, docs/54 SS2.8)
              Cr 1 (s0_OOH__2x1v_escape: block-1C escape relax along imaginary
              mode #0, i244.7 cm-1)
  SCF (9):    Mn k-bridge x4 ({ref,s0_O,s0_OH,s0_OOH}__1x1_k8, 8 4 1, synthesis:252)
              Co fresh-density audits x2 ({s0_O,s0_OH}__1x1_base, the
              runs/probe/{Mn,Fe,Ni}_audit __base convention)
              basin-row children x3 (<state>__basin_g1 at the final geometries of
              runs/probe/{Cr_basin/s0_OOH, Co_basin/s0_OH, Ni_basin/s0_OH}.out)

  NOT BUILT (parked for the entrant, docs/54 SS6): every __magm / __ns deck, the
  dy-ladder pilot, Co/Ni s0_OOH__1x1_off, all BUILD-T second-seed cells, the HOLD
  (Ru AFM) family, Ru/Ir __g1 top-up, the Mn AFM arm, Ti nspin=2 controls, and the
  __g1 children of wave-1 decks (built only after their parents converge).

REGISTERED PROTOCOL CHANGE CARRIED (S0(b)): `noinv` IS DROPPED from every new
OFF-PLANE deck this builder writes (the 1x1_off / 2x1v_off / escape rows) -- "noinv
is dropped from every subsequent off-plane job in the program -- a registered
protocol change recorded here and cited by S3 deck builders, never a silent edit"
(runs/s0/b_noinv/README.md:107-111; measured |dE| = 3.2e-7 Ry). The stock emitter
(probe_decks.write_probe) cannot express nosym-without-noinv, so the noinv line is
stripped AFTER emission and the guard asserts the result. The five bare ref__2x1v
decks KEEP noinv: docs/54 SS1 fixes the reference convention at "nosym at 16 k,
matching the block-1A reference convention" and every banked ref__2x1v (Cr/Ru/Ir)
ran the full 16-k grid -- S0(b)'s registered scope is off-plane jobs, and dropping
noinv on the refs would leave 10 TR-reduced k-points, breaking k-set comparability
with the banked refs (and, for nspin=1 Ti, aborting at -nk 16 outright: pw.x
refuses more pools than k-points). SCF decks that CLONE a banked parent's namelist
(the Mn k-bridge, the Co __base audits, the Co/Ni __basin_g1 children) keep the
parent's nosym/noinv verbatim, because their whole point is to differ from the
parent in exactly one declared thing (mesh, density, or calculation class).

POOL ARITHMETIC (the fix of record for the wave-1 audit BLOCKER): a noinv-dropped
nosym deck on the Gamma-centred 4x4x1 mesh has 10 irreducible k-points (time
reversal alone; the banked measurement, runs/s0/b_noinv/README.md:29), NOT the
full-grid 16 -- so those rows run -nk 8 (8 <= 10, 128 % 8 == 0, the mirror-row
shape). nkpt_tr() below is the estimator; the guard prices every row against it.
The 1x1_off rows stay -nk 16 legally (TR-reduced 8x4x1 = 18, 9x4x1 = 19 >= 16).

DISPLACEMENT INSTRUMENT (extracted, not invented): the off-arm start is the banked
block-1A/cellsym operation (build_cellsym_pilot.py:158-160, :357-375) -- *O
y-translated by the kick, *OH/*OOH yawed about the vertical axis through the binding
atom. The numeric values are EXTRACTED at build time by diffing the banked
runs/probe/Cr_cellsym off decks against their mir siblings (kick = +0.35 A, yaw =
+90 deg) and the build refuses to proceed if the extraction disagrees with
build_cellsym_pilot.ADSORBATE_KICK_A / YAW_DEG. Deposited criterion: achieved
max|dy| >= 0.30 A (docs/43:145-147, :474-481).

GEOMETRY SOURCES: production FINAL coordinates per state, with the energy-of-record
basin repairs substituted where the production relaxation is in the wrong SCF
solution -- the exact Cr *OOH precedent (build_cellsym_pilot.METALS basin_out;
docs/41 s6f): Co s0_OH -> runs/probe/Co_basin/s0_OH.out (-406.51 meV below
production), Ni s0_OH -> runs/probe/Ni_basin/s0_OH.out (-175.85 meV). Co/Ni *OOH
have NO banked geometry (GAP by record) -> the adsorbate is hand-placed on the
relaxed clean-slab cus by the in-house fragment convention
(hea_oer.surfaces._adsorbate) rigidly pulled to M-O = 1.70 A -- the PULL_TO idiom
the campaign's only fresh *OOH start used (runs/s0/g_tio2_timing/README.md item 4).

MIRROR-SYMMETRIZED MIR BASES (orchestrator ruling 2026-08-23, on the audit finding
"Mn s0_OOH__2x1v_mir binding O sits 0.23 A off the mirror plane"): the registered
mirror arm is "symmetry ON, no nosym/noinv, adsorbate ON the plane" (docs/54 SS1,
citing S0(c) and docs/43:1515), and the banked C corners (Cr/Ru/Ir cellsym) are
LOCKED runs whose mirrors pw.x genuinely enforced -- a mir start inherited
asymmetric from a nosym EXPLORED production final gives pw.x nothing to enforce
and is NOT the registered arm. Every Mn/Fe/Co/Ni 2x1v base (incl. the hand-placed
Co/Ni *OOH, routed through the same path so the assert covers them) is therefore
mirror-symmetrized about the registered plane (the xz plane through the cus row,
y = clean-slab cus y -- the build_cellsym_pilot convention): each atom paired with
its nearest-image reflection (an atom may pair with itself if on-plane) and
averaged, pos_sym = (pos + Reflect(partner))/2, the adsorbate landing exactly ON
the plane per the banked on-plane convention (build_cellsym_pilot.py:755-762).
The mir deck is that symmetrized base verbatim; the off deck is THE SAME base +
the banked kick/yaw -- exactly the banked cellsym pairing (off = mir sibling +
kick). Asserted on the emitted bytes: (a) every mir start reflection-symmetric to
<= 1e-6 A (so pw.x detects the mirror), (b) every 2x1v off deck == its mir
sibling + kick and nothing else, (c) no symmetrization displacement >= 0.30 A
(else REFUSE and report). Ti mir starts are template-derived and verified exactly
mirror-symmetric by the same guard (no rewrite needed); the 1x1_off decks stay
production-final + kick (S corner, pairing with the banked N row as-is -- the
N-corner membership ruling of docs/54 SS6 item 5 remains the entrant's); the
refs, the Cr escape deck and the 9 SCFs are untouched.

Ti: geometry + namelist template = runs/s0/g_tio2_timing/s0_OOH__2x1v_off.in (the
gate-(g) A8.6-timed deck). Its adsorbate is REPRODUCED from the fragment convention
at build time and asserted identical before any Ti state is derived from it.

LAUNCH SHAPE (A8.6): 128 ranks, -N 1, 48 h; -nk per row from the irreducible
k-count: -nk 16 only where >= 16 k-points exist (the noinv-kept refs at the full
16-k grid; the 1x1_off rows at TR-reduced 18/19; the parent-cloning SCFs at 32),
-nk 8 on every 10-k noinv-dropped 4x4x1 row (all 2x1v_off + the escape) and on
the mirror-arm / symmetric-parent rows (~9-15 irreducible); per-deck
max_seconds = 165000 s (~45.8 h, inside the cap). PARITY_PASS gate in force.
Pseudos: exact docs/54 filenames, staged + md5-matched on Anvil
(anvil/pseudo_md5_preflight_2026-08-23.md).

Usage:  python src/dft/build_s3.py [--dry-run]
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(_HERE, "..", ".."))
sys.path.insert(0, _HERE)

from probe_decks import (parse_input_deck, parse_final_coordinates,  # noqa: E402
                         write_probe, parse_variant)
import build_cellsym_pilot as bcp  # noqa: E402  (imports only; its main() is guarded)

S3 = os.path.join(ROOT, "runs", "s3")
DOI = "10.5281/zenodo.22072991"
MAX_SECONDS = 165000          # ~45.8 h < the 48 h Slurm cap
PSEUDO_DIR = "/usr/share/espresso/pseudo"   # rewritten at runtime by the driver
SCRATCH = "./tmp"
MIN_DY = 0.30                 # docs/43:145-147 deposited off-plane criterion
MIN_BOND = 0.85
SYM_TOL_A = 1e-6              # ruling 2026-08-23 assert (a): mir starts exactly
                              # reflection-symmetric so pw.x detects the mirror
MAX_SYM_SHIFT_A = 0.30        # ruling assert (c): symmetrization may not move
                              # any atom this far -- REFUSE rather than emit
NP, NK_WIDE, NK_NARROW = 128, 16, 8

# docs/54:78-91 recipe table (values asserted against every emitted deck)
RECIPE = {
    "Cr": dict(nspin=2, mag=0.6, hub=("Cr-3d", 3.7),  upf="cr_pbe_v1.5.uspp.F.UPF",          k1=("9", "4", "1")),
    "Mn": dict(nspin=2, mag=0.5, hub=("Mn-3d", 3.9),  upf="mn_pbe_v1.5.uspp.F.UPF",          k1=("9", "4", "1")),
    "Fe": dict(nspin=2, mag=0.5, hub=("Fe-3d", 5.3),  upf="Fe.pbe-spn-kjpaw_psl.0.2.1.UPF",  k1=("8", "4", "1")),
    "Co": dict(nspin=2, mag=0.4, hub=("Co-3d", 3.32), upf="Co_pbe_v1.2.uspp.F.UPF",          k1=("8", "4", "1")),
    "Ni": dict(nspin=2, mag=0.3, hub=("Ni-3d", 6.2),  upf="ni_pbe_v1.4.uspp.F.UPF",          k1=("8", "4", "1")),
    "Ti": dict(nspin=1, mag=None, hub=None,           upf="ti_pbe_v1.4.uspp.F.UPF",          k1=None),
}
AUX_UPF = {"H": "H.pbe-rrkjus_psl.1.0.0.UPF", "O": "O.pbe-n-kjpaw_psl.0.1.UPF"}
K2X1 = ("4", "4", "1")
N_SLAB = 18

#: In-house adsorbate fragments (hea_oer.surfaces._adsorbate), binding atom first,
#: offsets in the (x, z) plane == ON the y-mirror. Used only where no banked
#: relaxed geometry exists (Co/Ni *OOH, Ti *O/*OH) with the pull-to-1.70 height.
FRAG = {
    "s0_O":   [("O", 0.0, 0.0, 0.0)],
    "s0_OH":  [("O", 0.0, 0.0, 0.0), ("H", 0.7, 0.0, 0.7)],
    "s0_OOH": [("O", 0.0, 0.0, 0.0), ("O", 1.1, 0.0, 0.9), ("H", 1.4, 0.0, 1.85)],
}
PULL_TO = 1.70   # A; PULL_TO median M-O (surfaces_rutile.PULL_TO; g_tio2 README item 4)
ADS_SPECIES = {"s0_O": ["O"], "s0_OH": ["O", "H"], "s0_OOH": ["O", "O", "H"]}

TI_TEMPLATE = os.path.join(ROOT, "runs", "s0", "g_tio2_timing", "s0_OOH__2x1v_off.in")
CR_HESS_DIR = os.path.join(ROOT, "runs", "probe", "Cr_hess")
CR_ESCAPE_SRC_IN = os.path.join(ROOT, "runs", "probe", "Cr_cellsym", "s0_OOH__2x1v_mir.in")

_FORBIDDEN = bcp._FORBIDDEN


def die(msg):
    raise SystemExit(f"REFUSING TO BUILD: {msg}")


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


# ------------------------------------------------------ displacement extraction ---

def extract_banked_displacements():
    """Kick + yaw pulled out of the banked cellsym decks by diffing off vs mir.

    Rule 3 of the wave-1 spec: reuse the SAME numeric values the banked decks used,
    extracted from the artifacts, never re-invented.
    """
    d = os.path.join(ROOT, "runs", "probe", "Cr_cellsym")
    mir_O = parse_input_deck(os.path.join(d, "s0_O__2x1v_mir.in"))
    off_O = parse_input_deck(os.path.join(d, "s0_O__2x1v_off.in"))
    kick = off_O["positions"][-1][2] - mir_O["positions"][-1][2]
    for (pm, po) in zip(mir_O["positions"][:-1], off_O["positions"][:-1]):
        if any(abs(a - b) > 1e-9 for a, b in zip(pm[1:], po[1:])):
            die("Cr_cellsym s0_O off/mir differ outside the adsorbate; extraction invalid")
    mir_OH = parse_input_deck(os.path.join(d, "s0_OH__2x1v_mir.in"))
    off_OH = parse_input_deck(os.path.join(d, "s0_OH__2x1v_off.in"))
    (_, ox, oy, _), (_, hx, hy, _) = mir_OH["positions"][-2], mir_OH["positions"][-1]
    (_, ox2, oy2, _), (_, hx2, hy2, _) = off_OH["positions"][-2], off_OH["positions"][-1]
    if abs(ox2 - ox) > 1e-9 or abs(oy2 - oy) > 1e-9:
        die("banked *OH off deck moved the binding atom; yaw extraction invalid")
    v1 = (hx - ox, hy - oy)
    v2 = (hx2 - ox2, hy2 - oy2)
    yaw = math.degrees(math.atan2(v1[0] * v2[1] - v1[1] * v2[0],
                                  v1[0] * v2[0] + v1[1] * v2[1]))
    if abs(kick - bcp.ADSORBATE_KICK_A) > 1e-8:
        die(f"extracted kick {kick} != build_cellsym_pilot.ADSORBATE_KICK_A "
            f"{bcp.ADSORBATE_KICK_A}")
    if abs(yaw - bcp.YAW_DEG) > 1e-4:
        die(f"extracted yaw {yaw} deg != build_cellsym_pilot.YAW_DEG {bcp.YAW_DEG}")
    return bcp.ADSORBATE_KICK_A, bcp.YAW_DEG


# ----------------------------------------------------- mirror symmetrization ---
# Orchestrator ruling 2026-08-23 (audit finding: Mn s0_OOH__2x1v_mir binding O
# off the mirror plane). Registered plane: the xz plane through the cus-site
# row, y = clean-slab cus y (build_cellsym_pilot.py:750-752 convention, the
# plane the banked LOCKED Cr/Ru/Ir cellsym mir runs kept).

def reflection_mismatch(positions, y_mirror, cell):
    """Max over atoms of the distance to the best same-species partner image
    under reflection about the xz plane at y = y_mirror (x/y nearest-image).
    0 iff the geometry is exactly mirror-symmetric."""
    a, b = cell[0][0], cell[1][1]
    worst = 0.0
    for (s, x, y, z) in positions:
        rx, ry = x, 2.0 * y_mirror - y
        best = min(
            math.dist((x2 + lx * a, y2 + ly * b, z2), (rx, ry, z))
            for (s2, x2, y2, z2) in positions if s2 == s
            for lx in (-1, 0, 1) for ly in (-1, 0, 1))
        worst = max(worst, best)
    return worst


def mirror_symmetrize(positions, y_mirror, cell, name):
    """Pair each atom with its reflection image about y = y_mirror (nearest-
    image pairing; an atom may pair with itself if on-plane) and average:
    pos_sym = (pos + Reflect(partner))/2. Self-paired atoms -- the adsorbate
    included -- land exactly ON the plane, the banked on-plane convention
    (build_cellsym_pilot.py:755-762). REFUSES on ambiguous pairing (a best
    match that is not an involution) or any per-atom displacement >=
    MAX_SYM_SHIFT_A. Returns (sym_positions, per_atom_shifts)."""
    a, b = cell[0][0], cell[1][1]
    n = len(positions)
    match = []
    for (s, x, y, z) in positions:
        rx, ry = x, 2.0 * y_mirror - y
        best = (1e9, None, None)
        for j, (s2, x2, y2, z2) in enumerate(positions):
            if s2 != s:
                continue
            for lx in (-1, 0, 1):
                for ly in (-1, 0, 1):
                    dd = math.dist((x2 + lx * a, y2 + ly * b, z2), (rx, ry, z))
                    if dd < best[0]:
                        best = (dd, j, (lx, ly))
        match.append(best)
    for i, (dd, j, _L) in enumerate(match):
        if j is None or match[j][1] != i:
            die(f"{name}: mirror pairing ambiguous -- atom {i} pairs to {j} but "
                f"atom {j} pairs to {None if j is None else match[j][1]}; "
                "refusing to symmetrize (ruling assert (c))")
        if dd / 2.0 >= MAX_SYM_SHIFT_A:
            die(f"{name}: symmetrization would displace atom {i} by "
                f"{dd / 2.0:.4f} A >= {MAX_SYM_SHIFT_A} A; refusing "
                "(ruling assert (c) -- pairing or geometry suspect)")
    out = [None] * n
    for i, (dd, j, (lx, ly)) in enumerate(match):
        if out[i] is not None:
            continue
        s, x, y, z = positions[i]
        _s2, x2, y2, z2 = positions[j]
        qx = 0.5 * (x + x2 + lx * a)
        qy = 0.5 * (y + 2.0 * y_mirror - y2 - ly * b)
        qz = 0.5 * (z + z2)
        out[i] = (s, qx, qy, qz)
        if j != i:
            # exact reflection of out[i], shifted back to the partner's image
            out[j] = (s, qx - lx * a, 2.0 * y_mirror - qy - ly * b, qz)
    shifts = [math.dist(p[1:], q[1:]) for p, q in zip(positions, out)]
    if max(shifts) >= MAX_SYM_SHIFT_A:
        k = shifts.index(max(shifts))
        die(f"{name}: symmetrization moved atom {k} by {shifts[k]:.4f} A >= "
            f"{MAX_SYM_SHIFT_A} A; refusing (ruling assert (c))")
    mm = reflection_mismatch(out, y_mirror, cell)
    if mm > 1e-9:
        die(f"{name}: symmetrized geometry still {mm:.2e} A off exact "
            "reflection symmetry; pairing inconsistent")
    return out, shifts


def assert_off_is_mir_plus_kick(mir_text, off_text, n_ads, y_mirror, pair):
    """Ruling assert (b): every 2x1v off deck == its mir sibling + the banked
    kick and NOTHING else. Checked on the emitted bytes: after normalizing the
    prefix and dropping the symmetry-flag lines, the two decks must be line-
    identical everywhere except the n_ads adsorbate position rows, and those
    rows must equal off_plane_start(mir adsorbate) to <= 2e-6 A."""
    def norm(t):
        t = re.sub(r"^\s*nosym\s*=\s*\.true\.\s*\n", "", t, flags=re.M)
        t = re.sub(r"^\s*noinv\s*=\s*\.true\.\s*\n", "", t, flags=re.M)
        return re.sub(r"^(\s*prefix\s*=\s*)'[^']*'", r"\1'X'", t, flags=re.M)
    lm, lo = norm(mir_text).splitlines(), norm(off_text).splitlines()
    if len(lm) != len(lo):
        die(f"{pair}: mir/off decks differ in line count after normalization")
    kidx = next((i for i, ln in enumerate(lm) if ln.startswith("K_POINTS")), None)
    if kidx is None or not lo[kidx].startswith("K_POINTS"):
        die(f"{pair}: K_POINTS rows misaligned between mir and off decks")
    allowed = set(range(kidx - n_ads, kidx))
    bad = [i for i, (u, v) in enumerate(zip(lm, lo)) if u != v and i not in allowed]
    if bad:
        die(f"{pair}: off deck differs from its mir sibling outside the "
            f"adsorbate rows (lines {bad[:5]}) -- ruling requires the same "
            "symmetrized base + kick and nothing else")
    dm = bcp.parse_input_deck_text(mir_text)
    do = bcp.parse_input_deck_text(off_text)
    exp_ads = bcp.off_plane_start(dm["positions"][-n_ads:], y_mirror, pair)
    worst = 0.0
    for (p, q) in zip(exp_ads, do["positions"][-n_ads:]):
        if p[0] != q[0]:
            die(f"{pair}: adsorbate species order changed between mir and off")
        worst = max(worst, max(abs(u - v) for u, v in zip(p[1:], q[1:])))
    if worst > 2e-6:
        die(f"{pair}: off adsorbate differs from kick(mir sibling) by "
            f"{worst:.2e} A -- not the banked cellsym pairing")


# --------------------------------------------------------------------- guard ---

def _scalar(txt, key):
    m = re.search(rf"^\s*{key}\s*=\s*'([^']*)'", txt, re.M | re.I)
    if m:
        return m.group(1)
    m = re.search(rf"^\s*{key}\s*=\s*([^\s,!/]+)", txt, re.M | re.I)
    return m.group(1).strip().strip("'\"") if m else None


def guard(text, name, exp):
    """Assert-everything check on the emitted bytes, re-parsed, never on intent."""
    def g_die(msg):
        die(f"{name}: {msg}")

    for k, want in (("calculation", exp["calculation"]), ("ecutwfc", "80.0"),
                    ("ecutrho", "640.0"), ("degauss", "0.01"),
                    ("conv_thr", "1.0d-6"), ("mixing_mode", "local-TF"),
                    ("mixing_beta", "0.3"), ("electron_maxstep", "200"),
                    ("forc_conv_thr", "2.0d-3"), ("nstep", "200"),
                    ("ion_dynamics", "bfgs"), ("smearing", "mv"),
                    ("occupations", "smearing"), ("prefix", name),
                    ("pseudo_dir", PSEUDO_DIR), ("outdir", SCRATCH),
                    ("nspin", str(exp["nspin"]) if exp["nspin"] == 2 else None)):
        got = _scalar(text, k)
        if want is None:
            if k == "nspin" and got is not None:
                g_die(f"nspin present ({got}) on an nspin=1 metal")
            continue
        if got != want:
            g_die(f"{k} = {got!r}, expected {want!r}")
    for k in _FORBIDDEN:
        if re.search(rf"^\s*{k}\s*=", text, re.M | re.I):
            g_die(f"forbidden key {k!r} present")
    ms = re.findall(r"^\s*max_seconds\s*=\s*(\d+)\s*$", text, re.M)
    if len(ms) != 1 or int(ms[0]) != MAX_SECONDS:
        g_die(f"max_seconds lines {ms}, expected one line = {MAX_SECONDS}")
    if text.index("max_seconds") > text.index("&SYSTEM"):
        g_die("max_seconds sits outside &CONTROL")

    has_nosym = bool(re.search(r"^\s*nosym\s*=\s*\.true\.", text, re.M | re.I))
    has_noinv = bool(re.search(r"^\s*noinv\s*=\s*\.true\.", text, re.M | re.I))
    if (has_nosym, has_noinv) != (exp["nosym"], exp["noinv"]):
        g_die(f"(nosym, noinv) = {(has_nosym, has_noinv)}, expected "
              f"{(exp['nosym'], exp['noinv'])} (S0(b): noinv dropped on "
              "off-plane decks; refs keep it per the docs/54 nosym-at-16-k "
              "ref convention; cloning SCFs keep the parent's flags)")

    d = bcp.parse_input_deck_text(text)
    if len(d["positions"]) != exp["nat"] or int(_scalar(text, "nat")) != exp["nat"]:
        g_die(f"nat {len(d['positions'])} != expected {exp['nat']}")
    if len(d["flags"]) != exp["nat"]:
        g_die(f"{len(d['flags'])} constraint flags for {exp['nat']} atoms")
    if tuple(d["kpts"][1][:3]) != tuple(exp["kmesh"]) or tuple(d["kpts"][1][3:]) != ("0", "0", "0"):
        g_die(f"k-mesh {d['kpts'][1]} != {list(exp['kmesh'])} + 0 0 0")

    # cell: exact expected vectors (doubling exactness asserted upstream too)
    for i in range(3):
        for j in range(3):
            if abs(d["cell"][i][j] - exp["cell"][i][j]) > 1e-9:
                g_die(f"cell[{i}][{j}] = {d['cell'][i][j]} != {exp['cell'][i][j]}")

    # species / pseudos / hubbard / mags against the docs/54 recipe table
    upfs = {s: p for s, _m, p in d["species"]}
    M = exp["metal"]
    for s, p in upfs.items():
        want = RECIPE[M]["upf"] if s == M else AUX_UPF.get(s)
        if p != want:
            g_die(f"pseudo for {s} is {p!r}, docs/54 table says {want!r}")
    if exp["ads_species"] is not None:
        got_ads = [q[0] for q in d["positions"][exp["n_halves"] * N_SLAB:]]
        if got_ads != exp["ads_species"]:
            g_die(f"adsorbate species {got_ads} != {exp['ads_species']}")
    hub = d["hubbard"]
    want_hub = [RECIPE[M]["hub"]] if RECIPE[M]["hub"] else []
    if [(l, u) for l, u in hub] != [(l, u) for l, u in want_hub]:
        g_die(f"HUBBARD {hub} != {want_hub}")
    if RECIPE[M]["nspin"] == 2:
        idx = {s: i + 1 for i, (s, _m, _p) in enumerate(d["species"])}
        for s, i in idx.items():
            want_m = RECIPE[M]["mag"] if s == M else 0.0
            if abs(d["mags"].get(i, 0.0) - want_m) > 1e-9:
                g_die(f"starting_magnetization({i}) [{s}] = "
                      f"{d['mags'].get(i)} != {want_m}")

    # mask: every 18-atom half equals the source mask, adsorbate free
    for h in range(exp["n_halves"]):
        got = d["flags"][N_SLAB * h:N_SLAB * (h + 1)]
        if got != exp["mask"]:
            g_die(f"slab half {h} mask != source mask")
    for f in d["flags"][N_SLAB * exp["n_halves"]:]:
        if f != "1 1 1":
            g_die(f"adsorbate atom constrained ({f!r})")

    # the arm has to be physically performed / not performed
    ads = d["positions"][N_SLAB * exp["n_halves"]:]
    dy = max((abs(q[2] - exp["y_mirror"]) for q in ads), default=0.0)
    if exp["arm_dy"] == "off" and dy < MIN_DY:
        g_die(f"off/escape arm but achieved max|dy| = {dy:.4f} < {MIN_DY} A")
    if exp["arm_dy"] == "mir" and dy >= MIN_DY:
        g_die(f"mirror arm but an adsorbate atom sits {dy:.4f} A off-plane "
              ">= the off-arm criterion -- arms swapped?")
    if exp["arm_dy"] == "mir":
        # ruling 2026-08-23 assert (a): the registered arm is symmetry ON with
        # a mirror pw.x can DETECT -- the emitted start must be exactly
        # reflection-symmetric, adsorbate exactly ON the plane.
        mm = reflection_mismatch(d["positions"], exp["y_mirror"], d["cell"])
        if mm > SYM_TOL_A:
            g_die(f"mir start is reflection-asymmetric by {mm:.2e} A > "
                  f"{SYM_TOL_A} A -- pw.x would find no mirror to enforce "
                  "(orchestrator ruling 2026-08-23; registered arm docs/54 SS1)")
        if dy > SYM_TOL_A:
            g_die(f"mir adsorbate sits {dy:.2e} A off the plane > {SYM_TOL_A} A "
                  "(banked on-plane convention, build_cellsym_pilot.py:755-762)")

    dmin = bcp.min_distance(d["positions"], d["cell"])
    if dmin < MIN_BOND:
        g_die(f"minimum interatomic distance {dmin:.3f} < {MIN_BOND} A")
    if exp["nk"] > exp["nkpt_est"]:
        g_die(f"-nk {exp['nk']} exceeds the estimated {exp['nkpt_est']} k-points")
    if NP % exp["nk"]:
        g_die(f"NP={NP} not an exact multiple of nk={exp['nk']}")
    return dict(nat=exp["nat"], dmin=round(dmin, 4), max_ads_dy=round(dy, 6))


# ------------------------------------------------------------------ emission ---

EMITTED = []   # manifest rows, in build order


def emit(metal, name, deck, positions, flags, kmesh, *, calculation, nosym, noinv,
         cell, n_halves, y_mirror, arm_dy, ads_species, nk, nkpt_est, note,
         geom_src, dry, sym_rec=None):
    d = dict(deck)
    d["flags"] = list(flags)
    d["nosym"] = nosym          # write_probe emits nosym+noinv together...
    d["cell"] = [list(cell[0]), list(cell[1]), list(cell[2])]
    d["kpts"] = ("automatic", list(kmesh) + ["0", "0", "0"])
    if len(positions) != len(flags):
        die(f"{name}: {len(positions)} positions vs {len(flags)} flags")
    text, _ = write_probe(d, positions, parse_variant("base"), name,
                          PSEUDO_DIR, SCRATCH, calculation=calculation)
    if nosym and not noinv:     # ...so S0(b) strips the noinv line, then asserts
        text2 = re.sub(r"^\s*noinv\s*=\s*\.true\.\s*\n", "", text, flags=re.M)
        if text2 == text:
            die(f"{name}: expected to strip a noinv line and found none")
        text = text2
    cut = text.index("\n/\n")
    text = text[:cut] + f"\n  max_seconds = {MAX_SECONDS}" + text[cut:]

    meta = guard(text, name, dict(
        calculation=calculation, nspin=RECIPE[metal]["nspin"], nosym=nosym,
        noinv=noinv, nat=len(positions), kmesh=kmesh, cell=d["cell"],
        metal=metal, n_halves=n_halves, mask=list(deck["flags"])[:N_SLAB]
        if n_halves else [], y_mirror=y_mirror, arm_dy=arm_dy,
        ads_species=ads_species, nk=nk, nkpt_est=nkpt_est))

    outdir = os.path.join(S3, metal)
    path = os.path.join(outdir, name + ".in")
    if not os.path.realpath(path).startswith(os.path.realpath(S3) + os.sep):
        die(f"{name}: write target {path} escapes runs/s3/")
    if os.path.exists(os.path.join(outdir, name + ".out")):
        die(f"{name}: a .out already exists beside the target -- will not shadow "
            "a banked result (A8.8)")
    blob = text.encode("utf-8")
    if not dry:
        os.makedirs(outdir, exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(blob)
    EMITTED.append(dict(metal=metal, job=name, calculation=calculation, nk=nk,
                        kmesh=" ".join(kmesh), nkpt_est=nkpt_est,
                        nosym=nosym, noinv=noinv, geom_src=rel(geom_src),
                        note=note, md5=hashlib.md5(blob).hexdigest(),
                        **({"symmetrization": sym_rec} if sym_rec else {}),
                        **meta))
    return text


# --------------------------------------------------------------- geometry IO ---

def load_state(rundir, job, basin_out=None):
    ip = os.path.join(rundir, job + ".in")
    op = basin_out or os.path.join(rundir, job + ".out")
    for p in (ip, op):
        if not os.path.exists(p):
            die(f"missing {p}")
    txt = open(op, errors="replace").read()
    if "bfgs converged" not in txt:
        die(f"{op}: no `bfgs converged`; an unconverged geometry is not a start")
    pos, prov = parse_final_coordinates(op)
    if pos is None or prov != "final":
        die(f"{op}: geometry provenance {prov!r}")
    deck = parse_input_deck(ip)
    if len(pos) != len(deck["positions"]):
        die(f"{op}: {len(pos)} coords vs deck nat {len(deck['positions'])}")
    return dict(deck=deck, pos=pos, geom_src=op)


def nkpt_full(kmesh):
    """Full-grid product: the k-count ONLY for decks that keep noinv (nosym +
    noinv suppresses every reduction, e.g. the banked 16-k ref__2x1v decks)."""
    return int(kmesh[0]) * int(kmesh[1])


def nkpt_tr(kmesh):
    """Irreducible k-count for nosym decks whose noinv was DROPPED (S0(b)):
    time reversal alone pairs k with -k on the Gamma-centred n1 x n2 x 1 grid,
    leaving (full + self_paired) / 2 points, where a dimension contributes its
    0 and (if even) N/2 planes to the self-paired set. 4x4 -> 10 == the banked
    measurement (runs/s0/b_noinv/README.md:29, 'number of k points= 10');
    8x4 -> 18; 9x4 -> 19. Using nkpt_full() here was the wave-1 audit BLOCKER:
    it priced the 10-k off/escape rows at 16 and let -nk 16 through the guard,
    which pw.x rejects at startup ('some pools have no k-points') on nspin=1."""
    n1, n2 = int(kmesh[0]), int(kmesh[1])
    full = n1 * n2
    self_paired = (2 if n1 % 2 == 0 else 1) * (2 if n2 % 2 == 0 else 1)
    return (full - self_paired) // 2 + self_paired


def nkpt_mir_floor(kmesh):
    """Conservative irreducible-count floor with symmetry on: time reversal alone
    on a Gamma-centred even grid. 4x4 -> 10; the measured Cr mirror value is 9."""
    n1, n2 = int(kmesh[0]), int(kmesh[1])
    full = n1 * n2
    self_paired = (2 if n1 % 2 == 0 else 1) * (2 if n2 % 2 == 0 else 1)
    return min(9 if (n1, n2) == (4, 4) else full, (full - self_paired) // 2 + self_paired)


# ----------------------------------------------------------- per-metal build ---

def build_metal(M, states_1x1_off, oohless, kick, yaw, dry):
    rd = os.path.join(ROOT, "runs", f"{M}_slab")
    basin = {}
    if M in ("Co", "Ni"):
        basin["s0_OH"] = os.path.join(ROOT, "runs", "probe", f"{M}_basin", "s0_OH.out")
    src = {"slab": load_state(rd, "slab")}
    for st in ("s0_O", "s0_OH") + (() if oohless else ("s0_OOH",)):
        src[st] = load_state(rd, st, basin.get(st))

    slab_clean = src["slab"]["pos"]
    mask = src["slab"]["deck"]["flags"][:N_SLAB]
    for st, s in src.items():
        if s["deck"]["flags"][:N_SLAB] != mask:
            die(f"{M} {st}: slab mask differs from slab.in mask")
    a1 = src["slab"]["deck"]["cell"][0][0]
    cell1 = src["slab"]["deck"]["cell"]
    cus = bcp.cus_metal(slab_clean, src["s0_O"]["pos"][N_SLAB:])
    y_mirror = cus[2]
    k1 = RECIPE[M]["k1"]

    def cell2x1(deck):
        c = deck["cell"]
        if any(abs(c[0][j] - cell1[0][j]) > 1e-9 for j in range(3)) or \
           any(abs(c[i][j] - cell1[i][j]) > 1e-9 for i in (1, 2) for j in range(3)):
            die(f"{M}: state deck cell differs from slab.in cell")
        out = [[c[0][0] * 2.0, 0.0, 0.0], list(c[1]), list(c[2])]
        if abs(out[0][0] - 2.0 * a1) > 1e-12 or c[0][1] or c[0][2]:
            die(f"{M}: a1 doubling not exact")
        return out

    # ref__2x1v: clean slab doubled, nosym + noinv KEPT -- docs/54 SS1: "Bare
    # ref__2x1v decks run nosym at 16 k, matching the block-1A reference
    # convention (build_cellsym_pilot.py:874-887)". S0(b)'s registered noinv
    # drop covers off-plane jobs; the refs stay on the banked 16-k grid.
    emit(M, "ref__2x1v", src["slab"]["deck"],
         slab_clean + bcp.shift_x(slab_clean, a1), list(mask) * 2, K2X1,
         calculation="relax", nosym=True, noinv=True,
         cell=cell2x1(src["slab"]["deck"]), n_halves=2, y_mirror=y_mirror,
         arm_dy=None, ads_species=[], nk=NK_WIDE, nkpt_est=nkpt_full(K2X1),
         note="bare 2x1v reference, production seed",
         geom_src=src["slab"]["geom_src"], dry=dry)

    # 1x1 off decks: banked production/basin final + displacement, production mesh
    for st in states_1x1_off:
        pos = src[st]["pos"]
        ads = bcp.off_plane_start(pos[N_SLAB:], y_mirror, f"{M}/{st}__1x1_off")
        emit(M, f"{st}__1x1_off", src[st]["deck"], pos[:N_SLAB] + ads,
             list(mask) + ["1 1 1"] * len(ads), k1,
             calculation="relax", nosym=True, noinv=False,
             cell=src[st]["deck"]["cell"], n_halves=1, y_mirror=y_mirror,
             arm_dy="off", ads_species=ADS_SPECIES[st], nk=NK_WIDE,
             nkpt_est=nkpt_tr(k1),
             note="1x1 coverage-contrast leg, off-plane start (S corner)",
             geom_src=src[st]["geom_src"], dry=dry)

    # 2x1v mir + off, all three states. Orchestrator ruling 2026-08-23: base =
    # doubled production final, MIRROR-SYMMETRIZED about the registered plane;
    # mir = that base verbatim, off = THE SAME base + the banked kick (the
    # banked cellsym pairing), asserted pairwise below.
    for st in ("s0_O", "s0_OH", "s0_OOH"):
        if st in src:
            pos = src[st]["pos"]
            slab_s, ads_raw = pos[:N_SLAB], pos[N_SLAB:]
            deck_src = src[st]["deck"]
            geom_src = src[st]["geom_src"]
            hand_placed = False
        else:
            # Co/Ni *OOH: GAP by record -- fresh standard-recipe attempt, adsorbate
            # hand-placed on the relaxed clean-slab cus (PULL_TO 1.70 idiom).
            slab_s = slab_clean
            zc = cus[3]
            ads_raw = [(s, cus[1] + dx, y_mirror + dyy, zc + PULL_TO + dz)
                       for (s, dx, dyy, dz) in FRAG[st]]
            deck_src = src["s0_OH"]["deck"]   # standard production recipe w/ H species
            geom_src = src["slab"]["geom_src"]
            hand_placed = True
        n_ads = len(ads_raw)
        cell2 = cell2x1(deck_src)
        base = slab_s + bcp.shift_x(slab_clean, a1) + list(ads_raw)
        base_sym, shifts = mirror_symmetrize(base, y_mirror, cell2,
                                             f"{M}/{st}__2x1v")
        sym_rec = dict(plane_y=round(y_mirror, 8),
                       max_shift_A=round(max(shifts), 6),
                       ads_snap_A=round(max(shifts[2 * N_SLAB:]), 6))
        slab_sym, ads_mir = base_sym[:2 * N_SLAB], base_sym[2 * N_SLAB:]
        pair_text = {}
        for sym in ("mir", "off"):
            ads = (list(ads_mir) if sym == "mir"
                   else bcp.off_plane_start(ads_mir, y_mirror, f"{M}/{st}__2x1v_off"))
            pair_text[sym] = emit(
                 M, f"{st}__2x1v_{sym}", deck_src,
                 slab_sym + ads,
                 list(mask) * 2 + ["1 1 1"] * n_ads, K2X1,
                 calculation="relax", nosym=(sym == "off"), noinv=False,
                 cell=cell2, n_halves=2, y_mirror=y_mirror,
                 arm_dy=sym, ads_species=ADS_SPECIES[st],
                 nk=NK_NARROW,      # off: noinv dropped -> 10 TR-reduced k-points
                 nkpt_est=nkpt_tr(K2X1) if sym == "off" else nkpt_mir_floor(K2X1),
                 sym_rec=sym_rec,
                 note=("1/2 ML, neighbouring cus vacant"
                       + ("; base mirror-symmetrized about the cus-row xz plane "
                          "(orchestrator ruling 2026-08-23 on the audit's "
                          "off-plane-mir finding; registered arm docs/54 SS1) "
                          "-- see the symmetrization record"
                          if sym == "mir" else
                          "; off start = the mir sibling's mirror-symmetrized "
                          "base + the banked kick, nothing else (banked cellsym "
                          "pairing; orchestrator ruling 2026-08-23)")
                       + ("; adsorbate HAND-PLACED (no banked geometry -- "
                          "registered fresh re-attempt)" if hand_placed else "")
                       + ("; Co *OOH re-attempt under A8.4's ladder" if hand_placed
                          and M == "Co" and st == "s0_OOH" else "")
                       + ("; Ni *OOH expected-fail -> A8.4 NOT_CONVERGED is the "
                          "registered outcome" if hand_placed and M == "Ni"
                          and st == "s0_OOH" else "")),
                 geom_src=geom_src, dry=dry)
        assert_off_is_mir_plus_kick(pair_text["mir"], pair_text["off"], n_ads,
                                    y_mirror, f"{M}/{st}__2x1v")
    return src, mask, y_mirror


# ------------------------------------------------------------------ Ti build ---

def build_ti(yaw, kick, dry):
    t = parse_input_deck(TI_TEMPLATE)
    if len(t["positions"]) != 2 * N_SLAB + 3:
        die("Ti template nat != 39")
    half1, half2, ads_t = (t["positions"][:N_SLAB], t["positions"][N_SLAB:2 * N_SLAB],
                           t["positions"][2 * N_SLAB:])
    mask = t["flags"][:N_SLAB]
    if t["flags"][N_SLAB:2 * N_SLAB] != mask:
        die("Ti template mask halves differ")
    a1_1x1 = t["cell"][0][0] / 2.0
    for (p1, p2) in zip(half1, half2):
        if p1[0] != p2[0] or abs(p2[1] - p1[1] - a1_1x1) > 1e-6 or \
           abs(p2[2] - p1[2]) > 1e-6 or abs(p2[3] - p1[3]) > 1e-6:
            die("Ti template halves are not an exact a1 translation pair")
    cus = bcp.cus_metal(half1, ads_t)
    y_mirror, zc = cus[2], cus[3]
    if abs(ads_t[0][3] - (zc + PULL_TO)) > 1e-6:
        die(f"Ti template binding O height != z_cus + {PULL_TO}")

    def place_mir(st):
        return [(s, cus[1] + dx, y_mirror + dyy, zc + PULL_TO + dz)
                for (s, dx, dyy, dz) in FRAG[st]]

    # identity assert: template adsorbate == convention fragment yawed +90
    rebuilt = bcp.yaw_fragment(place_mir("s0_OOH"), yaw)
    for (a, b) in zip(rebuilt, ads_t):
        if a[0] != b[0] or any(abs(x - y) > 1e-6 for x, y in zip(a[1:], b[1:])):
            die(f"Ti template *OOH does not reproduce from the fragment "
                f"convention + yaw {yaw}: {a} vs {b}")

    base = dict(t)   # namelist template: nspin=1, no Hubbard (asserted by guard)
    sp3 = t["species"]                                    # H, Ti, O
    sp2 = [s for s in sp3 if s[0] != "H"]                 # Ti, O

    def ti_emit(name, positions, flags, *, nosym, noinv, arm_dy, ads_species,
                species, nk, nkpt_est, note, sym_rec=None):
        d = dict(base)
        d["species"] = species
        return emit("Ti", name, d, positions, flags, K2X1, calculation="relax",
                    nosym=nosym, noinv=noinv, cell=t["cell"], n_halves=2,
                    y_mirror=y_mirror, arm_dy=arm_dy, ads_species=ads_species,
                    nk=nk, nkpt_est=nkpt_est, note=note, geom_src=TI_TEMPLATE,
                    dry=dry, sym_rec=sym_rec)

    slab36 = half1 + half2
    # ref: noinv KEPT (docs/54 nosym-at-16-k ref convention) -- also the only
    # legal -nk 16 shape on nspin=1 Ti (noinv-dropped would leave 10 k-points
    # and pw.x aborts with more pools than k-points).
    ti_emit("ref__2x1v", slab36, list(mask) * 2, nosym=True, noinv=True,
            arm_dy=None, ads_species=[], species=sp2, nk=NK_WIDE,
            nkpt_est=nkpt_full(K2X1),
            note="bare TiO2 2x1v reference (template slab, adsorbate stripped)")
    ti_mm_max = 0.0
    for st in ("s0_O", "s0_OH", "s0_OOH"):
        mir = place_mir(st)
        # ruling 2026-08-23: the Ti mir starts are template-derived -- VERIFY
        # they are exactly mirror-symmetric; if not, the same symmetrize-then-
        # kick treatment as the 3d metals applies.
        slab_use, sym_rec = slab36, None
        mm = reflection_mismatch(slab36 + mir, y_mirror, t["cell"])
        ti_mm_max = max(ti_mm_max, mm)
        if mm > SYM_TOL_A:
            base_sym, shifts = mirror_symmetrize(slab36 + mir, y_mirror,
                                                 t["cell"], f"Ti/{st}__2x1v")
            slab_use, mir = base_sym[:2 * N_SLAB], base_sym[2 * N_SLAB:]
            sym_rec = dict(plane_y=round(y_mirror, 8),
                           max_shift_A=round(max(shifts), 6),
                           ads_snap_A=round(max(shifts[2 * N_SLAB:]), 6))
        off = (bcp.kick_y(mir, kick) if len(mir) == 1 else bcp.yaw_fragment(mir, yaw))
        if st == "s0_OOH" and sym_rec is None:
            off = ads_t   # byte-identical to the gate-(g) timed deck (asserted above)
        dy = max(abs(q[2] - y_mirror) for q in off)
        if dy < MIN_DY:
            die(f"Ti {st} off start reached only |dy| = {dy}")
        sp = sp2 if st == "s0_O" else sp3
        n_ads = len(mir)
        tm = ti_emit(f"{st}__2x1v_mir", slab_use + mir,
                     list(mask) * 2 + ["1 1 1"] * n_ads,
                     nosym=False, noinv=False, arm_dy="mir",
                     ads_species=ADS_SPECIES[st], species=sp,
                     nk=NK_NARROW, nkpt_est=nkpt_mir_floor(K2X1), sym_rec=sym_rec,
                     note="TiO2 2x1v mirror arm, fragment convention @ pull-1.70")
        to = ti_emit(f"{st}__2x1v_off", slab_use + off,
                     list(mask) * 2 + ["1 1 1"] * n_ads,
                     nosym=True, noinv=False, arm_dy="off",
                     ads_species=ADS_SPECIES[st], species=sp,
                     nk=NK_NARROW, nkpt_est=nkpt_tr(K2X1), sym_rec=sym_rec,
                     note="TiO2 2x1v off arm"
                          + (" (geometry = the gate-(g) A8.6-timed deck, fresh "
                             "full relax, no A8.8 conflict)"
                             if st == "s0_OOH" and sym_rec is None else ""))
        assert_off_is_mir_plus_kick(tm, to, n_ads, y_mirror, f"Ti/{st}__2x1v")
    return ti_mm_max


# ------------------------------------------------------------ Cr escape build ---

def build_cr_escape(dry):
    """Escape relax: hess_ref geometry kicked along imaginary mode #0 (i244.7)."""
    import numpy as np
    import hessian_analyze as ha
    man = json.load(open(os.path.join(CR_HESS_DIR, "hess_manifest.json"),
                         encoding="utf-8"))
    outs = {r["job"]: ha.parse_scf_out(os.path.join(CR_HESS_DIR, r["job"] + ".out"))
            for r in man["jobs"]}
    g = ha.run_gates(man, outs)
    hb = ha.build_hessian(man, outs, g["contaminated"])
    if hb["dropped"]:
        die(f"Cr Hessian dropped coordinates {hb['dropped']}; eigenvector basis "
            "incomplete")
    Ds = 0.5 * (hb["D"] + hb["D"].T)
    vals, vecs = np.linalg.eigh(Ds)
    if not vals[0] < 0:
        die("Cr Hessian mode #0 is not imaginary any more")
    nu = ha.CM1_PER_ROOT * math.sqrt(-vals[0])
    if abs(nu - 244.669) > 0.5:
        die(f"mode #0 is i{nu:.3f} cm-1, expected i244.7 (docs/49 verdict)")
    coords = hb["coords"]                       # [(atom0based, axis)] x 9
    masses = hb["masses"]
    u = vecs[:, 0] / np.sqrt(masses)            # Cartesian displacement pattern

    ref = parse_input_deck(os.path.join(CR_HESS_DIR, "s0_OOH__2x1v_mir__hess_ref.in"))
    src = parse_input_deck(CR_ESCAPE_SRC_IN)    # production relax namelist
    pos_ref, _ = parse_final_coordinates(
        os.path.join(ROOT, "runs", "probe", "Cr_cellsym", "s0_OOH__2x1v_mir.out"))
    for (a, b) in zip(ref["positions"], pos_ref):
        if a[0] != b[0] or any(abs(x - y) > 1e-6 for x, y in zip(a[1:], b[1:])):
            die("hess_ref geometry != Cr_cellsym s0_OOH__2x1v_mir final coords")

    ads_idx = [i - 1 for i in man["adsorbate_indices_1based"]]
    h_atom0 = ads_idx[man["adsorbate_species"].index("H")]
    uy_h = sum(abs(u[k]) for k, (a, ax) in enumerate(coords)
               if a == h_atom0 and ax == "y")
    if uy_h < 1e-8:
        die("mode #0 has no H y-component; cannot size the kick from it")
    scale = MIN_DY / uy_h
    disp = {(a, ax): scale * float(u[k]) for k, (a, ax) in enumerate(coords)}
    newpos = []
    for i, (s, x, y, z) in enumerate(ref["positions"]):
        newpos.append((s,
                       x + disp.get((i, "x"), 0.0),
                       y + disp.get((i, "y"), 0.0),
                       z + disp.get((i, "z"), 0.0)))
    seeded_dy_h = abs(newpos[h_atom0][2] - ref["positions"][h_atom0][2])
    if abs(seeded_dy_h - MIN_DY) > 1e-9:
        die(f"seeded H |dy| = {seeded_dy_h} != {MIN_DY}")
    y_mirror = man["mirror_y_angstrom"]
    emit("Cr", "s0_OOH__2x1v_escape", src, newpos, ref["flags"], K2X1,
         calculation="relax", nosym=True, noinv=False, cell=src["cell"],
         n_halves=2, y_mirror=y_mirror, arm_dy="off",
         ads_species=man["adsorbate_species"], nk=NK_NARROW,
         nkpt_est=nkpt_tr(K2X1),
         note=(f"block-1C escape relax: hess_ref geometry displaced along "
               f"imaginary mode #0 (i{nu:.1f} cm-1), kick scaled so seeded "
               f"H |dy| = {MIN_DY} A (docs/43:145-147 scale); production relax "
               "class -- conv_thr 1e-6 per docs/54:76-78 ('S3 production "
               "relaxations stay conv_thr 1e-6'); the docs/54 escape row's "
               "'1e-10 class' binds to the 19 re-Hessian displacement SCFs, "
               "which are parked until this relax converges (they need a fresh "
               "1e-10 hess_ref at the escaped geometry); nosym so the escape "
               "can leave the plane (S0(b): no noinv)"),
         geom_src=os.path.join(CR_HESS_DIR, "s0_OOH__2x1v_mir__hess_ref.in"),
         dry=dry)
    return dict(nu_cm1=round(nu, 3), scale_A=round(scale, 6),
                seeded_dy_H_A=MIN_DY,
                per_atom_disp={f"a{a+1}{ax}": round(v, 6)
                               for (a, ax), v in sorted(disp.items())})


# ----------------------------------------------------------------- SCF decks ---

def emit_scf_clone(metal, name, parent_in, geom_out, kmesh_override, note, dry,
                   nkpt_est, nk):
    """g1-class / bridge / audit SCF: clone the parent namelist verbatim (incl. its
    nosym/noinv), swap in the parent's FINAL geometry, calculation='scf', fresh
    density (no restart keys are ever emitted)."""
    deck = parse_input_deck(parent_in)
    txt = open(geom_out, errors="replace").read()
    if "bfgs converged" not in txt:
        die(f"{geom_out}: parent not converged")
    pos, prov = parse_final_coordinates(geom_out)
    if pos is None or prov != "final":
        die(f"{geom_out}: geometry provenance {prov!r}")
    if len(pos) != len(deck["positions"]):
        die(f"{geom_out} vs {parent_in}: atom count mismatch")
    kmesh = kmesh_override or tuple(deck["kpts"][1][:3])
    ads_n = len(pos) - N_SLAB
    st = {1: "s0_O", 2: "s0_OH", 3: "s0_OOH"}.get(ads_n)
    emit(metal, name, deck, pos, deck["flags"], kmesh, calculation="scf",
         nosym=deck["nosym"],
         noinv=bool(re.search(r"^\s*noinv\s*=\s*\.true\.", deck["raw"], re.M | re.I)),
         cell=deck["cell"], n_halves=1,
         y_mirror=bcp.cus_metal([q for q in pos[:N_SLAB]], pos[N_SLAB:])[2]
         if ads_n else 0.0,
         arm_dy=None, ads_species=ADS_SPECIES.get(st, []) if ads_n else [],
         nk=nk, nkpt_est=nkpt_est, note=note, geom_src=geom_out, dry=dry)


def build_scfs(dry):
    # Mn k-bridge: 4 fresh-density SCFs at the banked production finals, 8 4 1
    # (synthesis:252; docs/54 SS1 -- n1 = 9 odd folds onto no 2x1 mesh).
    rd = os.path.join(ROOT, "runs", "Mn_slab")
    for job, name in (("slab", "ref__1x1_k8"), ("s0_O", "s0_O__1x1_k8"),
                      ("s0_OH", "s0_OH__1x1_k8"), ("s0_OOH", "s0_OOH__1x1_k8")):
        emit_scf_clone("Mn", name, os.path.join(rd, job + ".in"),
                       os.path.join(rd, job + ".out"), ("8", "4", "1"),
                       "Mn k-mesh bridge 9 4 1 -> 8 4 1 at fixed banked geometry, "
                       "fresh density (production namelist cloned verbatim)",
                       dry, nkpt_est=32, nk=NK_WIDE)
    # Co fresh-density audits, __base convention (runs/probe/Mn_audit exemplars)
    rd = os.path.join(ROOT, "runs", "Co_slab")
    for job in ("s0_O", "s0_OH"):
        emit_scf_clone("Co", f"{job}__1x1_base", os.path.join(rd, job + ".in"),
                       os.path.join(rd, job + ".out"), None,
                       "fresh-density audit SCF at the banked production final "
                       "geometry (__base convention, runs/probe/{Mn,Fe,Ni}_audit)",
                       dry, nkpt_est=32, nk=NK_WIDE)
    # basin-row children: g1-class fresh-density SCFs at the basin finals
    for metal, st, nkpt, nk in (("Cr", "s0_OOH", 15, NK_NARROW),
                                ("Co", "s0_OH", 32, NK_WIDE),
                                ("Ni", "s0_OH", 32, NK_WIDE)):
        bd = os.path.join(ROOT, "runs", "probe", f"{metal}_basin")
        emit_scf_clone(metal, f"{st}__basin_g1", os.path.join(bd, st + ".in"),
                       os.path.join(bd, st + ".out"), None,
                       "GATE-1 child of the energy-of-record basin row: fresh-"
                       "density fixed-geometry SCF at the parent's final coords "
                       "(docs/43:311-319)", dry, nkpt_est=nkpt, nk=nk)


# ------------------------------------------------------------------ manifest ---

EXPECTED = sorted(
    [f"Mn/{j}" for j in
     ["ref__2x1v", "s0_O__1x1_off", "s0_OH__1x1_off", "s0_OOH__1x1_off",
      "s0_O__2x1v_mir", "s0_OH__2x1v_mir", "s0_OOH__2x1v_mir",
      "s0_O__2x1v_off", "s0_OH__2x1v_off", "s0_OOH__2x1v_off",
      "ref__1x1_k8", "s0_O__1x1_k8", "s0_OH__1x1_k8", "s0_OOH__1x1_k8"]] +
    [f"Fe/{j}" for j in
     ["ref__2x1v", "s0_O__1x1_off", "s0_OH__1x1_off", "s0_OOH__1x1_off",
      "s0_O__2x1v_mir", "s0_OH__2x1v_mir", "s0_OOH__2x1v_mir",
      "s0_O__2x1v_off", "s0_OH__2x1v_off", "s0_OOH__2x1v_off"]] +
    [f"Co/{j}" for j in
     ["ref__2x1v", "s0_O__1x1_off", "s0_OH__1x1_off",
      "s0_O__2x1v_mir", "s0_OH__2x1v_mir", "s0_OOH__2x1v_mir",
      "s0_O__2x1v_off", "s0_OH__2x1v_off", "s0_OOH__2x1v_off",
      "s0_O__1x1_base", "s0_OH__1x1_base", "s0_OH__basin_g1"]] +
    [f"Ni/{j}" for j in
     ["ref__2x1v", "s0_O__1x1_off", "s0_OH__1x1_off",
      "s0_O__2x1v_mir", "s0_OH__2x1v_mir", "s0_OOH__2x1v_mir",
      "s0_O__2x1v_off", "s0_OH__2x1v_off", "s0_OOH__2x1v_off",
      "s0_OH__basin_g1"]] +
    [f"Ti/{j}" for j in
     ["ref__2x1v", "s0_O__2x1v_mir", "s0_OH__2x1v_mir", "s0_OOH__2x1v_mir",
      "s0_O__2x1v_off", "s0_OH__2x1v_off", "s0_OOH__2x1v_off"]] +
    ["Cr/s0_OOH__2x1v_escape", "Cr/s0_OOH__basin_g1"])


def write_manifest(escape_meta, kick, yaw, dry):
    got = sorted(f"{r['metal']}/{r['job']}" for r in EMITTED)
    if got != EXPECTED:
        extra = set(got) - set(EXPECTED)
        missing = set(EXPECTED) - set(got)
        die(f"emitted set != wave-1 scope. extra={sorted(extra)} "
            f"missing={sorted(missing)}")
    n_relax = sum(1 for r in EMITTED if r["calculation"] == "relax")
    n_scf = sum(1 for r in EMITTED if r["calculation"] == "scf")
    if (n_relax, n_scf) != (46, 9):
        die(f"count check failed: {n_relax} relax + {n_scf} scf, expected 46 + 9")

    hdr = f"""# S3 wave-1 manifest -- built {__import__('datetime').date.today().isoformat()} by src/dft/build_s3.py
# Registration of record: deposited A8, DOI {DOI}; dispositions docs/54-s3-deck-matrix-2026-08-23.md SS0-SS1.
# PARTITION: wave-1 = production-seed only. 46 relax + 9 SCF. PARKED for the
#   entrant's dated lines (docs/54 SS6): all __magm second-seed cells -- the four
#   *OOH 2x1v off __magm baselines (Mn/Fe/Co/Ni) are FIRM BUILD in docs/54
#   (synthesis:250), parked ONLY because the second-seed numeric recipe needs
#   Frank's sign-off (docs/54 SS6 item 2); the other __magm cells are BUILD-T --
#   all __ns decks, the dy-ladder pilot, Co/Ni s0_OOH__1x1_off (OPEN), the HOLD
#   Ru-AFM family, Ru/Ir __g1 top-up, the Mn AFM arm, Ti nspin=2 controls,
#   __g1 children of wave-1 decks (built after their parents converge), and the
#   19 Cr re-Hessian displacement SCFs at the escaped geometry (1e-10 class,
#   docs/54:159/:324 -- buildable only after s0_OOH__2x1v_escape converges).
# SEQUENCING NOTE (dy ladder): docs/54 SS1 orders the {{0.10,0.25,0.50}} A
#   dy-ladder pilot BEFORE the off-plane fleet (synthesis:258, :253); this wave
#   seeds all off rows with the banked block-1A values instead (below).
#   ORCHESTRATOR RULING 2026-08-23: the off rows LAUNCH in wave 1 with the
#   banked constants kick +{kick} A / yaw +{yaw} deg -- comparability with
#   block 1A is A8.1's own logic, and A8.8 no-replacement means these results
#   stand as the banked-constant arm regardless of any later rung choice. The
#   dy-ladder pilot rungs remain the entrant's (docs/54 SS6); the entrant may
#   override this ruling by dated line (added rungs = new decks, never
#   replacements).
# 2x1v mir starts are mirror-symmetrized doubled production finals and each off sibling = the same base + kick (orchestrator ruling 2026-08-23 on the audit's off-plane-mir finding; registered arm definition docs/54 SS1; the N-corner membership ruling of docs/54 SS6 item 5 remains the entrant's)
# LAUNCH SHAPE: 128 ranks, -N 1, 48 h Slurm cap; -nk per row from the
#   irreducible k-count (never above it -- pw.x refuses pools without
#   k-points): -nk 16 where >= 16 k exist (noinv-kept refs at the full 16-k
#   grid; 1x1_off rows, TR-reduced 18/19 k; parent-cloning SCFs at 32 k);
#   -nk 8 on the 10-k noinv-dropped 4x4x1 rows (all 2x1v_off + the escape,
#   runs/s0/b_noinv/README.md:29) and on mirror-arm/symmetric-parent rows
#   (~9-15 k). Per-deck max_seconds = {MAX_SECONDS}. PARITY_PASS REQUIRED:
#   43_submit_s3_wave1.sh refuses unless $PROJECT/parity/PARITY_PASS exists.
# PSEUDOS: docs/54 table filenames, staged + md5-matched on Anvil --
#   anvil/pseudo_md5_preflight_2026-08-23.md (A8.5 discharged).
# PROTOCOL: S0(b) noinv-drop carried on every new OFF-PLANE deck
#   (runs/s0/b_noinv/README.md:107-111); bare ref__2x1v decks KEEP noinv --
#   docs/54 SS1 ref convention "nosym at 16 k", matching the banked Cr/Ru/Ir
#   refs; parent-cloning SCFs keep the parent's symmetry flags verbatim.
#   Off-arm displacement values extracted from the banked cellsym decks:
#   *O y-kick +{kick} A, *OH/*OOH yaw +{yaw} deg;
#   Cr escape kick along mode #0 (i{escape_meta['nu_cm1']} cm-1), seeded H
#   |dy| = {escape_meta['seeded_dy_H_A']} A.
# NP=128 NCONC=1
"""
    rows = "".join(f"s3/{r['metal']} {r['job']} .in {r['nk']}\n" for r in EMITTED)
    if not dry:
        os.makedirs(S3, exist_ok=True)
        with open(os.path.join(S3, "m_s3_wave1.txt"), "w", newline="\n") as fh:
            fh.write(hdr + rows)
        side = dict(date=str(__import__('datetime').date.today()), doi=DOI,
                    displacement=dict(kick_A=kick, yaw_deg=yaw,
                                      criterion_min_dy_A=MIN_DY),
                    escape=escape_meta, np=NP, decks=EMITTED)
        with open(os.path.join(S3, "m_s3_wave1_build.json"), "w",
                  newline="\n") as fh:
            json.dump(side, fh, indent=2)
    return n_relax, n_scf


def main():
    dry = "--dry-run" in sys.argv
    kick, yaw = extract_banked_displacements()
    build_metal("Mn", ("s0_O", "s0_OH", "s0_OOH"), False, kick, yaw, dry)
    build_metal("Fe", ("s0_O", "s0_OH", "s0_OOH"), False, kick, yaw, dry)
    build_metal("Co", ("s0_O", "s0_OH"), True, kick, yaw, dry)
    build_metal("Ni", ("s0_O", "s0_OH"), True, kick, yaw, dry)
    ti_mm = build_ti(yaw, kick, dry)
    escape_meta = build_cr_escape(dry)
    build_scfs(dry)
    n_relax, n_scf = write_manifest(escape_meta, kick, yaw, dry)
    print(f"OK: {n_relax} relax + {n_scf} scf decks "
          f"{'(dry run, nothing written)' if dry else 'written to runs/s3/'}")
    print(f"displacements: kick={kick} A, yaw={yaw} deg; "
          f"escape mode i{escape_meta['nu_cm1']} cm-1 scale={escape_meta['scale_A']} A")
    print(f"Ti template mirror mismatch: {ti_mm:.2e} A "
          f"({'exact, no rewrite' if ti_mm <= SYM_TOL_A else 'SYMMETRIZED'})")
    for r in EMITTED:
        if "symmetrization" in r:
            s = r["symmetrization"]
            print(f"  sym {r['metal']}/{r['job']}: plane_y={s['plane_y']} "
                  f"max_shift={s['max_shift_A']} ads_snap={s['ads_snap_A']}")
    for r in EMITTED:
        print(f"  s3/{r['metal']}/{r['job']}.in  {r['calculation']:5s} "
              f"k={r['kmesh']} nk={r['nk']} nat={r['nat']} "
              f"dy={r['max_ads_dy']} dmin={r['dmin']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
