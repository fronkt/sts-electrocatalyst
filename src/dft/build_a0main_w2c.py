#!/usr/bin/env python
"""A0-main tranche 2c (2026-08-29): the second escalation round.

Two points did not converge in tranche 2b/3, and they failed for different
reasons. This builder registers the response to each BEFORE it runs, and
re-derives every fact it depends on from the outputs on disk, so the record
cannot drift from the evidence.

===========================================================================
1. Fe s0_O at U = 4.5 -- rung (i) failed, escalate to rung (ii)
===========================================================================

A6.5(2) (docs/43:1267): "(i) restart from the converged neighbouring-U
density as `startingpot`; (ii) halve the mixing beta; (iii) failing both,
the point is recorded NOT_CONVERGED and plotted as a gap".

Rung (i) ran as array 20204306 task 2: seeded from dens/s0_O__u530.save, it
O. Its sibling, u300 seeded from u150, converged in 202 s andscillated between ~1e-4 and ~8e-2 Ry for most of its 200 iterations and only settled to ~1.2-4e-5 Ry over the final ~17, never reaching conv_thr 1e-6, with totmag pinned at 21.98 throughout
landed at totmag 22.90.

WHY u450 IS THE HARD ONE. The measured s0_O moment along the ladder:

    u000 18.91 | u150 21.36 | u300 22.90 | u450 ????
    u530 21.98 | u600 21.99 | u750 22.00 | u900 21.99

u450 sits on the crossing between the 22.90 branch below it and the 21.98
branch above it. That is a near-degeneracy, which is the exact failure mode
A6.5(2) exists for -- not a broken deck.

WHAT IS BUILT. Rung (ii), halve the mixing beta (0.3 -> 0.15), applied
CUMULATIVELY on top of rung (i)'s density seed: the ladder escalates, it
does not reset. Because two converged neighbours now exist -- u530 (21.98)
and the newly repaired u300__r1 (22.90) -- and rung (i) names "the
converged neighbouring-U density" without picking one, BOTH legal parents
are run:

    s0_O__u450__r2   beta 0.15, seeded from dens/s0_O__u530.save
    s0_O__u450__r2b  beta 0.15, seeded from dens/s0_O__u300__r1.save

SELECTION RULE, FIXED HERE BEFORE EITHER RUNS. If both converge, the LOWER
total energy is the banked u450 point -- the campaign's standing rule that
the lower converged state is the state of record (docs/41 s6d, A6.4) -- and
the difference between them is reported as the measured branch splitting at
U = 4.5. If exactly one converges it is the point, labelled with the branch
it landed on. If neither converges, A6.5(2)(iii): NOT_CONVERGED, plotted as
a gap, never interpolated.

DISCLOSED LIMIT: the other seven s0_O rungs were not branch-searched; each
took whatever state it reached from starting_magnetization 0.5. u450 (and
u300 before it) are therefore the only seeded points on the Fe s0_O curve,
and the readout carries each row's totmag so a reader can see which branch
every point is on. Nothing is being tuned toward a target -- the target is
whichever converged state is lower, which is fixed independently of what it
turns out to be.

Note: local-TF mixing is ALREADY on -- qe_slab.py:175 sets it for every
slab deck in the campaign -- so "switch the mixer" is not an available
escalation here or anywhere else in this project.

===========================================================================
2. Ti s0_OOH -- rungs (i) and (ii) exhausted; the failure is GEOMETRIC
===========================================================================

Rung (i) never applied (a relaxation has no neighbouring-U density, and the
failed run retained none). Rung (ii) ran as array 20204308: mixing_beta
0.15 banked TWO ionic steps -- the energy fell 0.023 Ry and the total force
fell 0.173 -> 0.125 Ry/bohr, continuing a walk that began at 0.281 in the
FAILED first run -- and then the third step's SCF limit-cycled,
descending cleanly to ~1.2e-4 Ry by iteration 13 and never improving over
the remaining 187, with periodic spikes to ~5e-3.

DIAGNOSIS. qe_slab.py starts every Ti adsorbate about 3.1-3.2 A from the
nearest Ti -- a deliberately generous non-bonded height. Measured on this
campaign's own Ti runs:

    state   built d(anchor O, nearest Ti)   relaxed        steps
    s0_O            3.117 A                  1.735 A         36
    s0_OH           3.167 A                  1.829 A         56
    s0_OOH          3.167 A                  walking UP:      3 (then failed)
                                             3.167 -> 3.263
                                             -> 3.325 -> 3.414

*O and *OH walked DOWN into a Ti-O bond over dozens of steps. *OOH is
walking the other way. The adsorbate itself is intact and healthy (O-O
1.421 -> 1.36 A, O-H 0.996 -> 0.99 A, both tightening toward gas-phase
values), so this is not a dissociation; the molecule is fixing its internal
geometry while its centre drifts away from the surface. In that desorbed
region *OOH is a radical with an odd electron count, and the Ti chain's
nspin = 1 convention cannot spin-split the resulting half-occupied state --
which is precisely what a plateau-with-spikes limit cycle looks like.

So the SCF failure is a SYMPTOM of a bad starting geometry, not a mixing
problem to be patched. Three ionic steps is also far too short a walk to
conclude that TiO2 does not bind *OOH: *O needed 36 and *OH needed 56.

WHAT IS BUILT -- two relaxations, identical numerics, different starts:

    s0_OOH_r2   THE CONSERVATIVE CONTINUATION. Continues rung (ii)'s walk
                from its own last trajectory geometry (spliced verbatim,
                pw.x's own constraint flags), beta still 0.15. Numerics-only
                additions: mixing_ndim 8 -> 16 (more Broyden history, the
                textbook lever against a limit cycle) and electron_maxstep
                200 -> 400. conv_thr, forc_conv_thr, degauss, smearing,
                nspin, mixing_mode and mixing_beta are UNTOUCHED.

    s0_OOH_r3   THE RE-ANCHORED START. The originally built deck with the
                three adsorbate atoms rigidly translated -- orientation and
                internal geometry preserved exactly -- so that the anchor O
                starts at the MEAN of Ti's own two converged Ti-O bond
                lengths, mean(d(s0_O), d(s0_OH)), both read off the relaxed
                outputs by this script rather than typed in. Same numerics
                as r2. This starts the walk inside the bonded basin instead
                of 1.4 A outside it.

    The start DOES select which local minimum BFGS reaches -- that is the
    point of r3, and it is why the selection rule below has a basin gap to
    report at all. What makes this not outcome-tuning is narrower and
    checkable: the re-anchor distance is computed mechanically from Ti's own
    two converged states, the rule that picks between r2 and r3 was fixed
    before either ran, and neither deck's energy was known when either was
    chosen.

SELECTION RULE, FIXED HERE BEFORE EITHER RUNS. If both converge, the LOWER
total energy is the banked s0_OOH geometry (docs/41 s6d, A6.4) and the
difference is reported as the measured basin gap. If exactly one converges
it is the geometry, labelled with its provenance. If neither converges,
A6.5(2)(iii) stands: Ti s0_OOH is NOT_CONVERGED, and A7.3's own registered
text shrinks the span denominator ("a converged *OOH geometry" conditions
it) rather than blocking the readout.

STATUS OF THE LADDER. mixing_ndim and electron_maxstep are not rungs
A6.5(2) names. They are declared here as a dated extension of the ladder
for RELAXATIONS -- disclosed infrastructure, drafted by the assistant for
the entrant to countersign (docs/59 s5). Its authority is bounded by
construction: the only thing this round can do is FILL a gap that (iii)
would otherwise leave. It cannot move a threshold, cannot change a
convergence criterion, and cannot flip a verdict -- if both decks fail,
the recorded outcome is identical to what (iii) alone would have recorded.

THE OPEN QUESTION THIS DOES NOT SETTLE (for the entrant, not the
assistant): whether the Ti arm should run nspin = 2 throughout. It would be
strictly more general -- a closed-shell system converges to the nspin = 1
answer with totmag -> 0 -- and it would remove the radical-state pathology
at the root. It is not done here because it is a CONVENTION change across
all four Ti states and 24 banked SCFs, and conventions are the entrant's to
set. Recorded in docs/59 s3c.

Usage:  PYTHONPATH=src python src/dft/build_a0main_w2c.py
"""

import json
import math
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import build_s3_wave2 as W  # noqa: E402
import probe_decks as P  # noqa: E402
from build_a0main import DST_ROOT  # noqa: E402

FE_DST = os.path.join(DST_ROOT, "Fe")
TI_SRC = os.path.join(W.ROOT, "runs", "Ti_slab")
A0_ROOT = os.path.join(W.ROOT, "runs", "a0")
NK_FE = 4
NK_TI = 8
N_ADSORBATE = 3          # *OOH = O, O, H, and they are the last three atoms

TRAJ_BLOCK = re.compile(
    r"ATOMIC_POSITIONS \(angstrom\)\s*\n((?:\s*[A-Z][a-z]?\s+[-\d.eE+]+.*\n)+)")


def dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a[1:4], b[1:4])))


# --------------------------------------------------------- re-derive facts ---

def failed(path):
    txt = W.read(path)
    if "convergence NOT achieved" not in txt:
        W.die("%s does not carry an SCF failure -- refusing to 'repair' a "
              "point that converged (A8.8)" % W.rel(path))
    return txt


def converged_scf(path):
    txt = W.read(path)
    if "convergence NOT achieved" in txt or "JOB DONE" not in txt:
        W.die("%s is not a cleanly converged SCF" % W.rel(path))
    return txt


def rederive():
    """Every claim the docstring makes about what failed, checked on disk."""
    facts = {}
    r1 = os.path.join(FE_DST, "s0_O__u450__r1.out")
    txt = failed(r1)
    facts["fe_u450_r1_failed"] = True
    mags = re.findall(r"total magnetization\s+=\s+([-\d.]+)", txt)
    if not mags or abs(float(mags[-1]) - 21.98) > 0.02:
        W.die("Fe u450 r1 final moment %r, expected the 21.98 branch"
              % (mags[-1] if mags else None))
    facts["fe_u450_r1_totmag"] = float(mags[-1])

    p300 = os.path.join(FE_DST, "s0_O__u300__r1.out")
    t300 = converged_scf(p300)
    m300 = re.findall(r"total magnetization\s+=\s+([-\d.]+)", t300)
    facts["fe_u300_r1_totmag"] = float(m300[-1])
    if abs(facts["fe_u300_r1_totmag"] - 22.90) > 0.02:
        W.die("Fe u300 r1 moment %r, expected 22.90" % m300[-1])

    ti = os.path.join(TI_SRC, "s0_OOH_r1.out")
    t = failed(ti)
    nsteps = len(TRAJ_BLOCK.findall(t))
    if nsteps != 2:
        W.die("Ti s0_OOH_r1 banked %d ionic steps, the record says 2" % nsteps)
    if "bfgs converged" in t:
        W.die("Ti s0_OOH_r1 converged -- this builder would be a replacement")
    facts["ti_r1_ionic_steps"] = nsteps
    return facts


# ------------------------------------------------------------ Fe rung (ii) ---

def build_fe_rung2():
    src_in = os.path.join(FE_DST, "s0_O__u450__r1.in")
    src = W.read(src_in)
    if "startingpot = 'file'" not in src:
        W.die("%s lost its rung-(i) density seed" % W.rel(src_in))
    if "  mixing_beta = 0.3\n" not in src:
        W.die("%s: expected mixing_beta 0.3 to halve" % W.rel(src_in))
    rows = []
    for stem, parent in (("s0_O__u450__r2", "s0_O__u530"),
                         ("s0_O__u450__r2b", "s0_O__u300__r1")):
        dst = os.path.join(FE_DST, stem + ".in")
        for p in (dst, os.path.join(FE_DST, stem + ".out")):
            if os.path.exists(p):
                W.die("%s already exists (A8.8)" % W.rel(p))
        new = W.swap_scalar_line(src, src_in, "prefix", "s0_O__u450__r1", stem)
        new2 = new.replace("  mixing_beta = 0.3\n", "  mixing_beta = 0.15\n")
        if new2 == new or new2.count("mixing_beta = 0.15") != 1:
            W.die("%s: mixing_beta halving failed" % W.rel(dst))
        new = new2
        diffs = W.diff_lines(src, new, dst)
        if len(diffs) != 2:
            W.die("%s: %d lines differ from the rung-(i) deck, expected exactly "
                  "2 (prefix, mixing_beta): %r" % (W.rel(dst), len(diffs), diffs))
        keys = sorted(d[1].strip().split("=")[0].strip() for d in diffs)
        if keys != ["mixing_beta", "prefix"]:
            W.die("%s: the two changed lines are %r" % (W.rel(dst), keys))
        if src.endswith("\n") and not new.endswith("\n"):
            W.die("%s: trailing newline lost (docs/45 trap 6)" % W.rel(dst))
        W.write(dst, new)
        rows.append((stem, parent))
        print("WROTE %s  (beta 0.15, seed %s)" % (W.rel(dst), parent))
    return rows


# ------------------------------------------------------- Ti numerics bump ----

def bump_numerics(txt, path):
    """mixing_ndim 8 -> 16 (added; QE's default is 8) and maxstep 200 -> 400.

    Nothing else. conv_thr, forc_conv_thr, degauss, smearing, nspin,
    mixing_mode and mixing_beta are left exactly as the source deck has them.
    """
    if "mixing_ndim" in txt:
        W.die("%s already sets mixing_ndim" % W.rel(path))
    m = re.search(r"^(\s*)mixing_beta\s*=.*$", txt, re.M)
    if not m:
        W.die("%s: no mixing_beta line to anchor mixing_ndim to" % W.rel(path))
    txt = txt[:m.end()] + "\n%smixing_ndim = 16" % m.group(1) + txt[m.end():]
    new = txt.replace("  electron_maxstep = 200\n", "  electron_maxstep = 400\n")
    if new == txt or new.count("electron_maxstep = 400") != 1:
        W.die("%s: electron_maxstep bump failed" % W.rel(path))
    for guard in ("conv_thr = 1.0d-6", "forc_conv_thr = 2.0d-3",
                  "degauss = 0.01", "mixing_mode = 'local-TF'"):
        if guard not in new:
            W.die("%s: numerics bump disturbed %r" % (W.rel(path), guard))
    return new


def splice_positions(txt, lines, path):
    block = "ATOMIC_POSITIONS angstrom\n" + "\n".join(lines) + "\n"
    new = re.sub(r"ATOMIC_POSITIONS\s+\S+\s*\n(?:\s*[A-Z][a-z]?\s+[-\d.eE+]+.*\n)+",
                 lambda m: block, txt, count=1)
    if new == txt or block not in new:
        W.die("%s: ATOMIC_POSITIONS splice failed" % W.rel(path))
    if new.count("ATOMIC_POSITIONS") != 1:
        W.die("%s: must carry exactly one ATOMIC_POSITIONS block" % W.rel(path))
    return new


def build_ti_r2():
    """Continue rung (ii)'s own walk from where it stopped."""
    src_in = os.path.join(TI_SRC, "s0_OOH_r1.in")
    src = W.read(src_in)
    dst = os.path.join(TI_SRC, "s0_OOH_r2.in")
    for p in (dst, os.path.join(TI_SRC, "s0_OOH_r2.out")):
        if os.path.exists(p):
            W.die("%s already exists (A8.8)" % W.rel(p))
    blocks = TRAJ_BLOCK.findall(W.read(os.path.join(TI_SRC, "s0_OOH_r1.out")))
    lines = [l.rstrip() for l in blocks[-1].rstrip("\n").split("\n") if l.strip()]
    deck = P.parse_input_deck(src_in)
    if len(lines) != len(deck["positions"]):
        W.die("trajectory block has %d atoms, deck has %d"
              % (len(lines), len(deck["positions"])))
    for line, (s, _, _, _) in zip(lines, deck["positions"]):
        if line.split()[0] != s:
            W.die("species order changed in the trajectory block")
    new = W.swap_scalar_line(src, src_in, "prefix", "s0_OOH_r1", "s0_OOH_r2")
    new = bump_numerics(new, dst)
    new = splice_positions(new, lines, dst)
    if W.FORBIDDEN_RESTART.search(new):
        W.die("%s: restart directive appeared" % W.rel(dst))
    if "  mixing_beta = 0.15\n" not in new:
        W.die("%s: rung (ii) beta must survive the continuation" % W.rel(dst))
    W.write(dst, new)
    print("WROTE %s  (continuation, beta 0.15, ndim 16, maxstep 400)"
          % W.rel(dst))
    return "s0_OOH_r2"


def _fmt_like(sp, x, y, z, flags):
    """Rebuild a position line in the source deck's own formatting."""
    line = "  %s  %.8f  %.8f  %.8f" % (sp, x, y, z)
    if flags:
        line += "  " + flags
    return line


def relaxed_bond(state):
    """d(anchor adsorbate O, nearest Ti) in the CONVERGED relax of `state`."""
    out = os.path.join(TI_SRC, state + ".out")
    txt = W.read(out)
    if "bfgs converged" not in txt or "convergence NOT achieved" in txt:
        W.die("%s is not a converged relax; its bond length may not be used "
              "to anchor anything" % W.rel(out))
    pos, prov = P.parse_final_coordinates(out)
    if prov != "final":
        W.die("%s: geometry provenance %r, not the converged final block"
              % (W.rel(out), prov))
    nads = {"s0_O": 1, "s0_OH": 2}[state]
    anchor = pos[-nads]
    if anchor[0] != "O":
        W.die("%s: anchor atom is %r, expected O" % (W.rel(out), anchor[0]))
    tis = [a for a in pos[:-nads] if a[0] == "Ti"]
    return sorted(dist(t, anchor) for t in tis)[0]


def build_ti_r3():
    """Re-anchor the built *OOH into the bonded basin and restart the walk."""
    src_in = os.path.join(TI_SRC, "s0_OOH.in")
    src = W.read(src_in)
    dst = os.path.join(TI_SRC, "s0_OOH_r3.in")
    for p in (dst, os.path.join(TI_SRC, "s0_OOH_r3.out")):
        if os.path.exists(p):
            W.die("%s already exists (A8.8)" % W.rel(p))

    d_O, d_OH = relaxed_bond("s0_O"), relaxed_bond("s0_OH")
    d_target = (d_O + d_OH) / 2.0

    deck = P.parse_input_deck(src_in)
    pos, flags = deck["positions"], deck["flags"]
    if len(pos) != 21:
        W.die("%s: expected nat=21, got %d" % (W.rel(src_in), len(pos)))
    ads, sub = pos[-N_ADSORBATE:], pos[:-N_ADSORBATE]
    if [a[0] for a in ads] != ["O", "O", "H"]:
        W.die("%s: last three atoms are %r, expected the *OOH adsorbate"
              % (W.rel(src_in), [a[0] for a in ads]))
    anchor = ads[0]
    tis = [a for a in sub if a[0] == "Ti"]
    ranked = sorted(tis, key=lambda t: dist(t, anchor))
    d0, d1 = dist(ranked[0], anchor), dist(ranked[1], anchor)
    if d1 - d0 < 0.5:
        W.die("nearest Ti is ambiguous (%.3f vs %.3f A)" % (d0, d1))
    ti = ranked[0]
    if not (2.5 < d0 < 4.0):
        W.die("built anchor distance %.3f A is not the expected non-bonded "
              "start" % d0)
    if not (1.5 < d_target < 2.5):
        W.die("re-anchor target %.3f A is not a plausible Ti-O bond" % d_target)

    u = [(anchor[i + 1] - ti[i + 1]) / d0 for i in range(3)]
    shift = [ti[i + 1] + d_target * u[i] - anchor[i + 1] for i in range(3)]

    # --- self-test: the formatter must reproduce the deck's own lines -------
    body = re.search(
        r"ATOMIC_POSITIONS\s+\S*\s*\n((?:.*\n)+?)"
        r"(?=K_POINTS|CELL_PARAMETERS|HUBBARD|\Z)", src).group(1)
    srclines = [l for l in body.rstrip("\n").split("\n") if l.strip()]
    if len(srclines) != len(pos):
        W.die("position line count mismatch (%d lines, %d atoms)"
              % (len(srclines), len(pos)))
    for i, (line, (sp, x, y, z)) in enumerate(zip(srclines, pos)):
        if _fmt_like(sp, x, y, z, flags[i]) != line.rstrip():
            W.die("the position formatter does not reproduce line %d of %s "
                  "byte-for-byte:\n  deck: %r\n  fmt : %r"
                  % (i, W.rel(src_in), line.rstrip(),
                     _fmt_like(sp, x, y, z, flags[i])))

    newlines = [l.rstrip() for l in srclines]
    for k in range(N_ADSORBATE):
        i = len(pos) - N_ADSORBATE + k
        sp, x, y, z = pos[i]
        newlines[i] = _fmt_like(sp, x + shift[0], y + shift[1], z + shift[2],
                                flags[i])
    changed = [i for i, (a, b) in enumerate(zip(srclines, newlines))
               if a.rstrip() != b]
    if changed != [18, 19, 20]:
        W.die("re-anchor touched rows %r, expected exactly the three "
              "adsorbate rows [18, 19, 20]" % changed)

    new = W.swap_scalar_line(src, src_in, "prefix", "s0_OOH", "s0_OOH_r3")
    new2 = new.replace("  mixing_beta = 0.3\n", "  mixing_beta = 0.15\n")
    if new2 == new or new2.count("mixing_beta = 0.15") != 1:
        W.die("%s: mixing_beta halving failed" % W.rel(dst))
    new = bump_numerics(new2, dst)
    new = splice_positions(new, newlines, dst)
    if W.FORBIDDEN_RESTART.search(new):
        W.die("%s: restart directive appeared" % W.rel(dst))
    W.write(dst, new)

    # --- verify the deck ON DISK actually lands where we said ---------------
    check = P.parse_input_deck(dst)
    cpos = check["positions"]
    canchor = cpos[-N_ADSORBATE]
    cd = min(dist(t, canchor) for t in cpos[:-N_ADSORBATE] if t[0] == "Ti")
    if abs(cd - d_target) > 1e-6:
        W.die("%s: built anchor distance %.6f A, wanted %.6f"
              % (W.rel(dst), cd, d_target))
    for (a, b) in ((0, 1), (1, 2)):
        before = dist(ads[a], ads[b])
        after = dist(cpos[-N_ADSORBATE + a], cpos[-N_ADSORBATE + b])
        if abs(before - after) > 1e-6:
            W.die("%s: internal adsorbate geometry changed (%.6f -> %.6f A)"
                  % (W.rel(dst), before, after))
    for i, (before, after) in enumerate(zip(sub, cpos[:-N_ADSORBATE])):
        if before != after:
            W.die("%s: substrate atom %d moved" % (W.rel(dst), i))
    print("WROTE %s  (re-anchored %.3f -> %.6f A; mean of s0_O %.6f and "
          "s0_OH %.6f)" % (W.rel(dst), d0, d_target, d_O, d_OH))
    return "s0_OOH_r3", dict(built_A=round(d0, 4), target_A=round(d_target, 6),
                             from_s0_O_A=round(d_O, 6),
                             from_s0_OH_A=round(d_OH, 6))


# ----------------------------------------------------------------- output ---

HDR_FE = """\
# A0-main A6.5(2)(ii) ESCALATION, Fe s0_O U = 4.5. Rung (i) (density seed
# from u530) oscillated between ~1e-4 and ~8e-2 Ry for most of its 200
# iterations, settling to ~1.2-4e-5 Ry only over the final ~17 and never
# reaching conv_thr 1e-6, with totmag pinned at 21.98; its sibling u300
# (seeded from u150) converged.
# u450 sits on the crossing between the 22.90 branch (u300) and the 21.98
# branch (u530+). Rung (ii) halves the mixing beta, applied CUMULATIVELY on
# top of the seed, from BOTH converged neighbours -- both are legal rung-(i)
# parents and the registration does not pick one.
#
# SELECTION RULE (fixed before launch, build_a0main_w2c.py docstring): if
# both converge the LOWER total energy is the banked point and the gap is
# reported as the branch splitting at U = 4.5; if one converges it is the
# point; if neither, A6.5(2)(iii) NOT_CONVERGED, plotted as a gap.
#
# SUBMIT WITH EXCLUDE=a024,a049,a050,a088,a196,a220,a223  (49_submit_repairs.sh)
#
# row: dir job suffix nk parent_density_prefix
# NP=128 NCONC=2
"""

HDR_TI = """\
# TiO2 s0_OOH, second escalation round. Rung (i) never applied (no
# neighbouring-U density for a relaxation); rung (ii) (beta 0.15) banked two
# ionic steps and then limit-cycled at ~1.3e-4 Ry. The cause is geometric:
# qe_slab.py starts every Ti adsorbate ~3.2 A off the nearest Ti, and where
# *O and *OH walked DOWN to 1.735 A / 1.829 A over 36 / 56 steps, *OOH walked
# UP (3.167 -> 3.414 A) into the desorbed-radical region that nspin=1 cannot
# describe. Three steps is far too short a walk to call it unbound.
#
#   s0_OOH_r2   continue rung (ii)'s walk from its last geometry
#   s0_OOH_r3   restart from a re-anchored geometry: the adsorbate rigidly
#               translated (orientation + internal geometry preserved) so the
#               anchor O starts at the mean of Ti's OWN converged Ti-O bond
#               lengths, read off s0_O.out / s0_OH.out by the builder
#
# Both add mixing_ndim = 16 and electron_maxstep = 400 -- numerics only, a
# dated extension of the ladder for relaxations (docs/59 s3c), bounded so
# that it can only FILL the gap (iii) would otherwise leave.
#
# SELECTION RULE (fixed before launch): lower converged total energy is the
# banked geometry; one converged = that one, labelled; neither = A6.5(2)(iii)
# NOT_CONVERGED and A7.3's own text shrinks the span denominator.
#
# SUBMIT WITH EXCLUDE=a024,a049,a050,a088,a196,a220,a223  (43_submit_s3_wave1.sh)
#
# NCONC below is the token 43's DRY PREFLIGHT checks, not the array cap:
# 43 invokes the driver with concurrency 1 unconditionally, so every
# manifest routed through it declares 1. The array itself is submitted at
# whatever %cap the caller passes (here 2 -- the two decks are independent
# and we want both answers in the same wall-clock window).
#
# row: dir job suffix nk
# NP=128 NCONC=1
"""


def main():
    facts = rederive()
    fe = build_fe_rung2()
    ti2 = build_ti_r2()
    ti3, anchor = build_ti_r3()

    fe_man = os.path.join(A0_ROOT, "m_a0_repairs2.txt")
    W.write(fe_man, HDR_FE + "".join(
        "a0/main/Fe %s .in %d %s\n" % (s, NK_FE, p) for s, p in fe))
    print("WROTE %s: %d rows" % (W.rel(fe_man), len(fe)))

    ti_man = os.path.join(TI_SRC, "m_ti_relax_r2.txt")
    W.write(ti_man, HDR_TI + "".join(
        "Ti_slab %s .in %d\n" % (s, NK_TI) for s in (ti2, ti3)))
    print("WROTE %s: 2 rows" % W.rel(ti_man))

    mpath = os.path.join(DST_ROOT, "manifest.json")
    man = json.load(open(mpath))
    man["tranche_2c"] = {
        "built": "2026-08-29",
        "builder": "src/dft/build_a0main_w2c.py",
        "rederived_facts": facts,
        "fe_s0_O_u450": {
            "rung": "A6.5(2)(ii), cumulative on rung (i)'s density seed",
            "mixing_beta": [0.3, 0.15],
            "decks": [{"stem": s, "parent_density": p} for s, p in fe],
            "branch_context": {"u300__r1": 22.90, "u450__r1_failed_at": 21.98,
                               "u530": 21.98},
            "selection_rule": ("both converge -> lower total energy is the "
                               "banked point, difference reported as the "
                               "branch splitting at U=4.5; one converges -> "
                               "that one, labelled with its branch; neither "
                               "-> A6.5(2)(iii) NOT_CONVERGED gap"),
            "disclosed_limit": ("the other seven s0_O rungs were not "
                                "branch-searched; every row's totmag travels "
                                "into the readout"),
        },
        "ti_s0_OOH": {
            "rungs_exhausted": ["(i) inapplicable to a relaxation",
                                "(ii) beta 0.15 limit-cycled at ~1.3e-4 Ry"],
            "diagnosis": ("geometric: built 3.167 A off the nearest Ti and "
                          "walking UP (3.167 -> 3.414 A over 3 steps) into "
                          "the desorbed-radical region; *O and *OH walked "
                          "DOWN to 1.735 / 1.829 A over 36 / 56 steps"),
            "ladder_extension": {
                "class": "numerics only, dated, disclosed (docs/59 s3c)",
                "mixing_ndim": [8, 16], "electron_maxstep": [200, 400],
                "untouched": ["conv_thr", "forc_conv_thr", "degauss",
                              "smearing", "nspin", "mixing_mode",
                              "mixing_beta"],
                "bounded_by": ("can only FILL the gap (iii) would leave; "
                               "cannot move a threshold or flip a verdict"),
            },
            "decks": {"s0_OOH_r2": "continuation of rung (ii)'s own walk",
                      "s0_OOH_r3": "re-anchored start", "anchor": anchor},
            "selection_rule": ("lower converged total energy is the banked "
                               "geometry; one converges -> that one, "
                               "labelled; neither -> A6.5(2)(iii)"),
            "entrant_decision_open": ("whether the Ti arm should run nspin=2 "
                                      "throughout -- a convention change "
                                      "across 4 states and 24 banked SCFs"),
        },
    }
    with open(mpath, "w", newline="\n") as fh:
        json.dump(man, fh, indent=2)
        fh.write("\n")
    print("UPDATED %s: tranche_2c" % W.rel(mpath))


if __name__ == "__main__":
    main()
