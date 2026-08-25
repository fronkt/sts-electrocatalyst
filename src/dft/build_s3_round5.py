#!/usr/bin/env python3
"""S3 round 5 (2026-08-25): the seven remaining S3 failures + the four owed
wave-4 __g1 children.

DELEGATION OF RECORD
--------------------
The entrant's instruction, 2026-08-25: "Continue to make the failures run
correctly, run the wave 4 children." Registered-parameter values below are set
under that delegation and are the entrant's to re-author; every one is recorded
with its reason so a single dated line can change it. This mirrors the
2026-08-24 precedent in docs/55, where four parked calls were delegated by
criterion.

WHAT THIS ROUND CHANGES, AND WHY IT IS ONE THING
------------------------------------------------
`mixing_ndim` is the Broyden mixing history depth. It is **unset in every S3
deck**, so QE's default of 8 has been in force for the whole campaign -- the
same shape of omission as `upscale` (docs/45 CORRECTION). The A8.4 ladder
escalated `mixing_beta` three times (0.3 -> 0.15 -> 0.075) and never once
touched the history depth, which is the parameter the "saturated history"
diagnosis actually names.

This repository's earlier R1 slab campaign did use it, in 26 decks:
  mixing_ndim = 12, beta 0.2, local-TF   -- the standard shape
  mixing_ndim = 16, beta 0.05, local-TF  -- the "attempt4" escalation, which
                                            converged Cr_slab/s0_OH,
                                            Mn_slab/s0_OOH, Co_slab/s0_O
So the value 16 is this project's own proven escalation for this failure mode
on these metals.

`mixing_beta` is deliberately NOT changed. The R1 attempt4 shape pairs ndim=16
with beta=0.05, but beta has already been escalated three times here and is not
the untested axis; changing both would repeat exactly the error round 4 made
(tasks/lessons.md 2026-08-25: a remedy that changes two things at once tests
neither). If ndim=16 alone fails, beta=0.05 is the next rung and we will know
which one mattered.

`upscale` IS DELIBERATELY NOT DECLARED. Its QE default is 100, and that default
is what held the 39 banked converged relaxes to an effective 1e-8. Leaving it
untouched keeps these rows numerically identical in protocol to their banked
siblings -- no goalpost moves, no two-tier threshold enters the ladder, and the
decks stay textually comparable. The value belongs in the methods text, which is
the entrant's to author (docs/45: methods correction owed). Note also that
`upscale` is an &IONS variable and the QE install on Anvil ships only a 57-byte
INPUT_PW.html stub, so there is no local authority to verify placement against;
injecting an unverifiable key for zero numerical gain would risk a parse abort
on all seven decks.

Consequence: what was parked as R1 dissolves. Both UNREG_THR rows
(Ni s0_OOH__2x1v_mir at 3.2e-7, Mn ...__basin at 5.0e-7) are convergence
problems, not threshold problems, and take the same remedy as everyone else.

PER-DECK RIDERS (each one justified, nothing uniform-by-accident)
-----------------------------------------------------------------
`electron_maxstep` is raised ONLY where it is demonstrably binding:
  Co s0_O__2x1v_mir       500 -> 1500. The single SLOW row: its running minimum
                          was still improving >2x per 150 iterations at cutoff
                          (4.29e-5 @ 488 of 500). This is the R2 call.
  Mn s0_OOH__2x1v_off__basin  200 -> 500. It is the only S3 deck still at 200;
                          500 is the campaign standard. Not an escalation, an
                          alignment.
The other five keep 500. Raising it on a limit-cycled deck buys nothing (round
4 established Co s0_OH__2x1v_off oscillates in a 2% band).

GEOMETRY SPLICE: any deck with banked BFGS progress restarts from its last
ATOMIC_POSITIONS rather than from cold, so converged ionic work is not thrown
away (src/dft/build_restarts.py precedent). Measured: Mn basin 19 steps,
Ni s0_OOH__2x1v_mir 3 steps, the other five 0 steps (their first SCF never
converged, so there is no geometry to carry).

A8.8
----
The seven retry jobs already own a `.out` carrying JOB DONE, and
anvil/42_s3_wave1.slurm refuses to overwrite one. Deployment therefore archives
each dead `.out` to `.out.attempt<N+1>` before launch (the documented
build_restarts.py deployment step); this script only PRINTS the archive plan and
never moves a file itself. The four __g1 children have no `.out` and are pure
additions.
"""
import difflib
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import build_s3_wave2 as W  # noqa: E402  (proven geometry/deck primitives)

S3 = W.S3
NDIM = "16"

# (metal, job, source_suffix, nk, new_electron_maxstep or None, triage class)
RETRIES = [
    ("Co", "s0_O__2x1v_mir",            ".retry_ms.in", 8, "1500", "SLOW"),
    ("Co", "s0_OH__2x1v_mir",           ".retry_ms.in", 8, None,   "STALLED"),
    ("Co", "s0_OH__2x1v_off",           ".retry_ms.in", 8, None,   "STALLED"),
    ("Co", "s0_OOH__2x1v_off",          ".retry_ms.in", 8, None,   "STALLED"),
    ("Ni", "s0_OOH__2x1v_mir",          ".retry_ms.in", 8, None,   "UNREG_THR"),
    ("Ni", "s0_OOH__2x1v_off",          ".retry_ms.in", 8, None,   "BRANCH"),
    ("Mn", "s0_OOH__2x1v_off__basin",   ".in",          8, "500",  "UNREG_THR"),
]

# (metal, job, source_suffix = the deck that ACTUALLY converged the parent, nk)
G1 = [
    ("Co", "ref__2x1v",              ".retry_ms.in", 16),
    ("Co", "s0_OH__1x1_off",         ".retry_ms.in", 16),
    ("Co", "s0_OOH__2x1v_mir",       ".retry_ms.in", 8),
    ("Fe", "s0_OOH__1x1_off__basin", ".in",          16),
]

RETRY_SUFFIX = ".retry_ndim.in"


def only_diff(a, b, path):
    """(changed_pairs, inserted_lines) between a and b; deletions are fatal."""
    la, lb = a.splitlines(), b.splitlines()
    sm = difflib.SequenceMatcher(None, la, lb, autojunk=False)
    ch, ins = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        if tag == "replace":
            ch += list(zip(la[i1:i2], lb[j1:j2]))
        elif tag == "insert":
            ins += lb[j1:j2]
        else:
            W.die(f"{path}: unexpected deletion {la[i1:i2]}")
    return ch, ins


def last_positions(out_path):
    """Lines of the FINAL ATOMIC_POSITIONS block in a .out (build_restarts.py
    convention). Unlike parse_final_coordinates this does not require the run to
    have converged -- these are dead runs and we want their last geometry."""
    lines = W.read(out_path).splitlines()
    starts = [i for i, l in enumerate(lines) if l.startswith("ATOMIC_POSITIONS")]
    if not starts:
        return None
    out = []
    for l in lines[starts[-1] + 1:]:
        m = re.match(r"^([A-Z][a-z]?)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)", l)
        if not m:
            break
        out.append((m.group(1), float(m.group(2)), float(m.group(3)), float(m.group(4))))
    return out or None


def coord_line(x, y):
    """True if x/y are the same atom's position line differing only in coords."""
    px, py = x.split(), y.split()
    return (len(px) in (4, 7) and len(py) == len(px)
            and px[0] == py[0] and px[4:] == py[4:])


rows, notes, archive_plan = [], [], []

# ------------------------------------------------------------- A) 7 retries --
for metal, job, suf, nk, maxstep, klass in RETRIES:
    d = os.path.join(S3, metal)
    src = os.path.join(d, job + suf)
    out_p = os.path.join(d, job + ".out")
    if not os.path.exists(src):
        W.die(f"{W.rel(src)}: source deck missing")
    src_txt = W.read(src)
    ref_deck = W.parse_input_deck(src)
    deck_rows = W.selftest_formatter(src_txt, src)

    if re.search(r"^\s*mixing_ndim\s*=", src_txt, re.M):
        W.die(f"{W.rel(src)}: already sets mixing_ndim -- refusing to double-set")
    if re.search(r"^\s*calculation\s*=\s*'relax'", src_txt, re.M) is None:
        W.die(f"{W.rel(src)}: not a relax; the &IONS/maxstep reasoning assumes one")

    txt = src_txt.replace("&ELECTRONS\n", f"&ELECTRONS\n  mixing_ndim = {NDIM}\n")
    if txt.count(f"mixing_ndim = {NDIM}") != 1:
        W.die(f"{W.rel(src)}: mixing_ndim insertion is not unique")

    old_ms = re.search(r"^\s*electron_maxstep\s*=\s*(\d+)\s*$", src_txt, re.M)
    if maxstep is not None:
        if not old_ms:
            W.die(f"{W.rel(src)}: no electron_maxstep to raise")
        txt = re.sub(r"^(\s*electron_maxstep\s*=\s*)\d+\s*$",
                     rf"\g<1>{maxstep}", txt, count=1, flags=re.M)

    pos = last_positions(out_p)
    spliced = 0
    if pos:
        if len(pos) != len(deck_rows):
            W.die(f"{W.rel(out_p)}: {len(pos)} atoms != {len(deck_rows)} in deck")
        if [p[0] for p in pos] != [r[0] for r in deck_rows]:
            W.die(f"{W.rel(out_p)}: species order differs from deck")
        new_rows = [(sp, f"{x:.8f}", f"{y:.8f}", f"{z:.8f}", r[4])
                    for (sp, x, y, z), r in zip(pos, deck_rows)]
        txt = W.swap_positions(txt, src, new_rows)
        spliced = len(pos)

    ch, ins = only_diff(src_txt, txt, W.rel(src))
    if ins != [f"  mixing_ndim = {NDIM}"]:
        W.die(f"{W.rel(src)}: unexpected insertions {ins}")
    for x, y in ch:
        if re.match(r"\s*electron_maxstep\s*=", x) and maxstep is not None:
            continue
        if coord_line(x, y) and spliced:
            continue
        W.die(f"{W.rel(src)}: disallowed change:\n  - {x!r}\n  + {y!r}")

    dst = os.path.join(d, job + RETRY_SUFFIX)
    if os.path.exists(dst):
        W.die(f"A8.8: {W.rel(dst)} already exists")
    W.write(dst, txt)
    W.namelist_sanity_relax = None  # not applicable: this stays a relax
    new_deck = W.parse_input_deck(dst)
    for key in ("cell", "species", "kpts", "hubbard", "mags", "flags"):
        if new_deck[key] != ref_deck[key]:
            W.die(f"{W.rel(dst)}: {key} differs from source deck")
    if new_deck["nosym"] != ref_deck["nosym"]:
        W.die(f"{W.rel(dst)}: nosym differs from source deck")
    if W.FORBIDDEN_RESTART.search(txt):
        W.die(f"{W.rel(dst)}: restart/startingpot key emitted")
    if 128 % nk:
        W.die(f"{W.rel(dst)}: 128 % nk={nk} != 0")

    n_att = len([f for f in os.listdir(d) if f.startswith(job + ".out.attempt")])
    archive_plan.append((f"s3/{metal}", f"{job}.out", f"{job}.out.attempt{n_att + 1}"))
    rows.append(f"s3/{metal} {job} {RETRY_SUFFIX} {nk}")
    ms = maxstep or (old_ms.group(1) if old_ms else "?")
    notes.append(f"retry  s3/{metal}/{job:26s} {klass:10s} ndim={NDIM} "
                 f"maxstep={ms:4s} splice={spliced or '-':>3} nk={nk}")

# ------------------------------------------------- B) 4 wave-4 __g1 children --
for metal, job, suf, nk in G1:
    d = os.path.join(S3, metal)
    src = os.path.join(d, job + suf)
    out_p = os.path.join(d, job + ".out")
    if not os.path.exists(src):
        W.die(f"{W.rel(src)}: converged-deck source missing")
    pot = W.read(out_p)
    if "JOB DONE" not in pot or "convergence NOT achieved" in pot:
        W.die(f"{W.rel(out_p)}: parent is not a clean converged run")
    if "End of BFGS Geometry Optimization" not in pot and "bfgs converged" not in pot:
        W.die(f"{W.rel(out_p)}: parent did not finish its relax")

    src_txt = W.read(src)
    if W.FORBIDDEN_RESTART.search(src_txt):
        W.die(f"{W.rel(src)}: parent deck carries a restart key")
    ref_deck = W.parse_input_deck(src)
    deck_rows = W.selftest_formatter(src_txt, src)

    pos, prov = W.parse_final_coordinates(out_p)
    if pos is None or prov != "final":
        W.die(f"{W.rel(out_p)}: geometry provenance {prov!r}, need 'final'")
    if len(pos) != len(deck_rows) or [p[0] for p in pos] != [r[0] for r in deck_rows]:
        W.die(f"{W.rel(out_p)}: final geometry does not match the deck's atoms")

    child = job + "__g1"
    new_rows = [(sp, f"{x:.8f}", f"{y:.8f}", f"{z:.8f}", r[4])
                for (sp, x, y, z), r in zip(pos, deck_rows)]
    txt = W.swap_scalar_line(src_txt, src, "calculation", "relax", "scf")
    txt = W.swap_scalar_line(txt, src, "prefix", job, child)
    txt = W.swap_positions(txt, src, new_rows)

    dst = os.path.join(d, child + ".in")
    if os.path.exists(dst):
        W.die(f"A8.8: {W.rel(dst)} already exists")
    W.write(dst, txt)

    kinds = [W.classify_diff(x, y, dst)
             for _, x, y in W.diff_lines(src_txt, W.read(dst), dst)]
    if kinds.count("calculation") != 1 or kinds.count("prefix") != 1 \
       or set(kinds) - {"calculation", "prefix", "coords"}:
        W.die(f"{W.rel(dst)}: diff is not exactly {{calculation, prefix, coords}}: {kinds}")
    W.namelist_sanity(dst, child, ref_deck)
    if 128 % nk:
        W.die(f"{W.rel(dst)}: 128 % nk={nk} != 0")

    rows.append(f"s3/{metal} {child} .in {nk}")
    notes.append(f"g1     s3/{metal}/{child:26s} {'child':10s} "
                 f"parent deck {suf:14s} nk={nk}")

for n in notes:
    print(n)
print("\nA8.8 archive plan (deployment does these BEFORE launch; this script does not):")
for d, a, b in archive_plan:
    print(f"   {d}: {a}  ->  {b}")

hdr = f"""# S3 round 5 -- 2026-08-25. Seven remaining S3 failures + the four owed
# wave-4 __g1 children. Built by src/dft/build_s3_round5.py; run by
# anvil/42_s3_wave1.slurm via 43_submit_s3_wave1.sh.
#
# ONE escalation, applied uniformly: mixing_ndim = {NDIM} (unset in every S3 deck
# so far -> QE default 8). It is the Broyden history DEPTH, which is the
# parameter the "saturated history" diagnosis names and the one axis the A8.4
# ladder never touched -- beta was escalated three times instead. This repo's own
# R1 slab campaign used ndim=12 as standard and ndim=16 + beta=0.05 as its
# "attempt4" rung, which converged Cr_slab/s0_OH, Mn_slab/s0_OOH, Co_slab/s0_O.
# mixing_beta is deliberately left alone so this tests ONE thing.
#
# upscale is deliberately NOT declared: its default 100 is what held the 39
# banked relaxes to an effective 1e-8, so leaving it keeps these rows uniform
# with their siblings and moves no goalpost. The declaration belongs in the
# methods text (entrant's).
#
# Per-deck riders, each demonstrably binding:
#   Co s0_O__2x1v_mir           electron_maxstep 500 -> 1500 (the one SLOW row)
#   Mn s0_OOH__2x1v_off__basin  electron_maxstep 200 ->  500 (the only deck
#                               below the campaign standard; alignment)
#   Mn basin / Ni s0_OOH__2x1v_mir  restart from the last banked BFGS geometry
#                               (19 and 3 ionic steps preserved)
#
# A8.8: the seven retry jobs own a .out with JOB DONE and 42_s3_wave1.slurm
# refuses to overwrite one, so deployment archives each to .out.attempt<N+1>
# first. The four __g1 children are pure additions.
#
# row: d job suffix nk
# NP=128 NCONC=1
#
# The directive line above must read EXACTLY that, and no other comment line may
# mention those two tokens. anvil/43_submit_s3_wave1.sh invokes the driver
# preflight as `bash $DRIVER $MANIFEST $NP 1`, passing a concurrency of 1
# unconditionally; queue_r1.sh refuses a manifest whose directive disagrees, and
# also refuses one where any comment mentions the tokens outside the exact form
# -- a typo there would silently disarm the wrong-rank refusal (finding N6).
# That is why every manifest in this repo declares 1. Slurm concurrency is a
# separate knob: the array throttle in `--array=1-N%C`, under which each task
# still gets its own full 128 cores.
"""
man = os.path.join(S3, "m_s3_round5.txt")
W.write(man, hdr + "\n".join(rows) + "\n")
print(f"\nwrote runs/s3/m_s3_round5.txt: {len(rows)} rows")
