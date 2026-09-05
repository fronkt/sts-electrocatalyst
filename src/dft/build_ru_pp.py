#!/usr/bin/env python
"""RU-PP: the Ru second-pseudopotential control -- 12 SCFs. NOT LICENSED.

WHAT THIS IS FOR

Ru is the only norm-conserving metal in the A0 roster (Ru_ONCV_PBE-1.0.oncvpsp.upf
x32 under runs/a0/main/Ru) against GBRV ultrasoft for Cr/Mn/Ti/Ir and PAW for Fe
(docs/45 section B row 10, docs/45:35; docs/70:283-286). Ru is also the one row
A7.3 turns on: as-built span(c_M)/2 = 0.09225 V against the registered 0.100 V
floor (docs/figs/a0main_readout.json, a7_3.per_metal.Ru.span_over_2_V), so Ru
crossing alone would take A7.3 from NOT MET at 3 of 6 to MET at 4 of 6. No
pseudopotential arm exists (docs/45:3173: "No PP arm is registered and none is
proposed here").

This builds the same Ru SCFs under a second pseudopotential FAMILY -- the GBRV
v1.2 ultrasoft potential, the family Cr/Mn/Ti/Ir already run on -- so the Ru
row can be read as an ANCHOR-PAIR COMPARABILITY CONTROL (docs/70:291-292), not
as a new error class and not as a replacement for any banked row.

  {slab, s0_O, s0_OH, s0_OOH} x {U = 0.00, 6.73, 9.00} = 12 SCFs.

THE THREE RUNGS, and why these three

  docs/70:291 and docs/45:3165 say "the three Ru anchors" without listing them.
  The three U values at which the word "anchor" attaches to Ru in the tree are:
    u000  U = 0.00  production U for Ru (a0main_readout.py:95 production_u=0.0;
                    docs/43:1758 "production convention U = 0 on Ru and Ir");
                    A7.3's fixed lower endpoint (docs/43:1368-1369)
    u673  U = 6.73  the Xu 2015 declared anchor point (runs/a0/m_a0main.txt:19,
                    :50; a0main_readout.py:95 anchor=6.73), PROJECTOR-MISMATCHED
    u900  U = 9.00  U_max = A7.3's fixed upper endpoint (docs/43:1368-1369) and
                    the rung that carries A6.3's verdict outright (docs/58:91-99)
  A7.3's Ru quantity is decided by four of the twelve decks (s0_OH and s0_OOH at
  u000 and u900); the other eight give eta(U) at the three rungs for the A6.3
  anchor-pair reading. This is one reading of "three anchors"; docs/89 carries a
  blank entrant slot for it, and changing RUNGS below rebuilds the arm.

THE TRANSFORMATION, and the guard on it

Each control deck differs from runs/a0/main/Ru/<state>__<u>.in in EXACTLY two
lines:

    prefix = '<state>__<u>'                       ->  '<state>__<u>_gbrv'
    Ru  101.070  Ru_ONCV_PBE-1.0.oncvpsp.upf      ->  Ru  101.070  ru_pbe_v1.2.uspp.F.UPF

Cutoffs (ecutwfc 80 / ecutrho 640 Ry -- the frozen protocol every GBRV metal in
the tree already runs at, e.g. runs/a0/main/Ir/s0_OH__u000.in:14-15), k-mesh
(8 4 1 0 0 0), spin convention (no nspin line, i.e. nspin = 1), smearing,
geometry, cell, if_pos flags and the HUBBARD card are inherited byte-identically.
build_one() diffs source against product line by line and DIES if any third
line differs, if either expected change is missing, or if any inherited
invariant it asserts (cutoffs, k-mesh, U line, no nspin) is not what the
docstring says.

Only banked partners are cloned: a source whose .out lacks JOB DONE, or carries
"convergence NOT achieved", or does not print the staged ONCV file's md5
(be037bb81c227cfb9b1461a9f099f4bd, anvil/pseudo_md5_preflight_2026-08-23.md) is
refused, so the pair is provably ONCV-banked vs GBRV-new.

projwfc.in is NOT written here. anvil/46_a0.slurm generates it at runtime from
the deck's own prefix (A6.5(1)).

THE NEW PSEUDOPOTENTIAL

  ru_pbe_v1.2.uspp.F.UPF, GBRV v1.2, PBE, ultrasoft, Z valence 16 (the same 16
  electrons per Ru as the ONCV file: 168 electrons in the slab .out either way),
  with a 4D pseudo-wavefunction so the HUBBARD "U Ru-4d" card resolves. Source,
  md5 and staging record: runs/a0/ru_pp/PSEUDO_PROVENANCE.md. It is NOT in the
  repository (pseudopotentials never are); it is staged at $PROJECT/pseudo on
  Anvil with the md5 verified on both ends.

REGISTRATION -- NOT LICENSED

  There is no dated registration line for this arm. docs/89 is a PROPOSAL with
  blank entrant slots. The manifest carries a NOT LICENSED notice, which
  anvil/47_submit_a0.sh refuses fail-closed (docs/66 section 4). The decks are
  built and md5-manifested BEFORE any threshold is adopted, on the P-PROJ-6
  ordering (c2e9a18 built, 8aba0ae licensed); do not collapse that ordering.

Re-running this script rewrites decks and manifest deterministically (no
timestamps, no environment-dependent content).

Usage:
    PYTHONPATH=src python src/dft/build_ru_pp.py            # build + verify
    PYTHONPATH=src python src/dft/build_ru_pp.py --check    # verify only, no write
"""

import hashlib
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import build_s3_wave2 as W  # noqa: E402

SRC_ROOT = os.path.join(W.ROOT, "runs", "a0", "main", "Ru")
DST_ROOT = os.path.join(W.ROOT, "runs", "a0", "ru_pp", "Ru")
MANIFEST = os.path.join(W.ROOT, "runs", "a0", "m_ru_pp.txt")
PROVENANCE = os.path.join(W.ROOT, "runs", "a0", "ru_pp", "PSEUDO_PROVENANCE.md")

STATES = ["slab", "s0_O", "s0_OH", "s0_OOH"]
# (token, U in eV); u000 carries no HUBBARD card in the source decks.
RUNGS = [("u000", 0.0), ("u673", 6.73), ("u900", 9.0)]
SUFFIX = "_gbrv"
NK = 4  # the banked source rows' nk (runs/a0/m_a0main.txt:129-160)

PP_OLD = "Ru_ONCV_PBE-1.0.oncvpsp.upf"
PP_NEW = "ru_pbe_v1.2.uspp.F.UPF"
PP_OLD_MD5 = "be037bb81c227cfb9b1461a9f099f4bd"   # pw.x-printed, every source .out
PP_NEW_MD5 = "7158a806dd851261a58e6920c40ebe78"   # PSEUDO_PROVENANCE.md, both ends
SPECIES_OLD = "  Ru  101.070  " + PP_OLD
SPECIES_NEW = "  Ru  101.070  " + PP_NEW

# Inherited invariants, asserted verbatim on every source deck.
CUTOFF_LINES = ("  ecutwfc = 80.0", "  ecutrho = 640.0")
KPOINTS = "  8 4 1 0 0 0"

# Inherited from the most recent a0 manifest (runs/a0/m_eproj_np128.txt).
EXCLUDE = "a024,a049,a050,a088,a196,a220,a223,a171,a120,a200"


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def source_is_banked(stem):
    """JOB DONE, no SCF failure, and pw.x read the staged ONCV file."""
    out = os.path.join(SRC_ROOT, stem + ".out")
    if not os.path.exists(out):
        return False, "no .out"
    with open(out, "rb") as fh:
        txt = fh.read().decode("latin-1")
    if "JOB DONE" not in txt:
        return False, "no JOB DONE"
    if re.search(r"convergence NOT achieved", txt):
        return False, "convergence NOT achieved"
    if ("MD5 check sum: " + PP_OLD_MD5) not in txt:
        return False, "does not print the staged ONCV md5 " + PP_OLD_MD5
    return True, "ok"


def build_one(state, utok, u, write):
    stem = "%s__%s" % (state, utok)
    src_path = os.path.join(SRC_ROOT, stem + ".in")
    if not os.path.exists(src_path):
        W.die("%s: source deck missing" % W.rel(src_path))

    ok, why = source_is_banked(stem)
    if not ok:
        W.die("Ru/%s: source is not banked (%s) -- a pseudopotential control "
              "against an unbanked state is meaningless" % (stem, why))

    src = W.read(src_path)  # dies on CRLF

    if src.count(SPECIES_OLD) != 1:
        W.die("%s: expected exactly one %r line" % (W.rel(src_path), SPECIES_OLD))
    if PP_NEW in src:
        W.die("%s: already names %s" % (W.rel(src_path), PP_NEW))
    want_prefix_old = "prefix = '%s'" % stem
    if src.count(want_prefix_old) != 1:
        W.die("%s: expected exactly one %r" % (W.rel(src_path), want_prefix_old))

    # Inherited invariants -- the docstring's claims, checked rather than assumed.
    lines = src.split("\n")
    for want in CUTOFF_LINES + (KPOINTS,):
        if lines.count(want) != 1:
            W.die("%s: expected exactly one %r line" % (W.rel(src_path), want))
    if re.search(r"^\s*nspin\s*=", src, re.M):
        W.die("%s: carries an nspin line; Ru's convention is nspin = 1 by default"
              % W.rel(src_path))
    ulines = [ln for ln in lines if re.match(r"^U\s+Ru-4d\s+[0-9.]+\s*$", ln)]
    if u == 0.0:
        if ulines or "HUBBARD" in src:
            W.die("%s: u000 source unexpectedly carries a HUBBARD card" % W.rel(src_path))
    else:
        if len(ulines) != 1:
            W.die("%s: expected exactly one 'U Ru-4d' line, got %d"
                  % (W.rel(src_path), len(ulines)))
        if abs(float(ulines[0].split()[2]) - u) > 1e-9:
            W.die("%s: U is %s, expected %.4f -- wrong rung"
                  % (W.rel(src_path), ulines[0].split()[2], u))

    new = src.replace(want_prefix_old, "prefix = '%s%s'" % (stem, SUFFIX), 1)
    new = new.replace(SPECIES_OLD, SPECIES_NEW, 1)

    a = src.split("\n")
    b = new.split("\n")
    if len(a) != len(b):
        W.die("%s: line count changed %d -> %d" % (W.rel(src_path), len(a), len(b)))
    d = [(i, x, y) for i, (x, y) in enumerate(zip(a, b), 1) if x != y]
    if len(d) != 2:
        W.die("Ru/%s: expected exactly 2 differing lines, got %d: %r"
              % (stem, len(d), [x[0] for x in d]))
    for _, before, after in d:
        if before.strip() == want_prefix_old and after.strip() == "prefix = '%s%s'" % (stem, SUFFIX):
            continue
        if before == SPECIES_OLD and after == SPECIES_NEW:
            continue
        W.die("Ru/%s: unexpected differing line %r -> %r" % (stem, before, after))

    dst = os.path.join(DST_ROOT, stem + SUFFIX + ".in")
    if write:
        if not os.path.isdir(DST_ROOT):
            os.makedirs(DST_ROOT)
        W.write(dst, new)
    return dst, src_path, [(i, x, y) for i, x, y in d]


def main():
    check_only = "--check" in sys.argv
    print("RU-PP builder -- %s" % ("CHECK ONLY, no files written" if check_only
                                   else "building"))
    if not os.path.exists(PROVENANCE):
        W.die("%s missing -- the pseudopotential's source and md5 record must "
              "exist before decks naming it are built" % W.rel(PROVENANCE))
    prov = W.read(PROVENANCE)
    if PP_NEW_MD5 not in prov or PP_NEW not in prov:
        W.die("%s does not record %s with md5 %s" % (W.rel(PROVENANCE), PP_NEW, PP_NEW_MD5))

    rows = []
    for utok, u in RUNGS:
        for state in STATES:
            dst, src, d = build_one(state, utok, u, write=not check_only)
            rows.append((state, utok, u, dst, src, d))

    print("  %d decks %s" % (len(rows), "verified" if check_only else "written"))
    for state, utok, u, dst, src, d in rows:
        print("  %-7s %s  U=%.4f  2-line diff at %s" % (state, utok, u, [i for i, _, _ in d]))

    if check_only:
        return

    lines = [
        "# RU-PP manifest -- Ru second-pseudopotential control, 12 SCFs,",
        "# U = 0.00 / 6.73 / 9.00 eV x {slab, s0_O, s0_OH, s0_OOH}.",
        "# Built by src/dft/build_ru_pp.py. Each deck differs from its",
        "# runs/a0/main/Ru/<state>__<u>.in source in exactly 2 lines:",
        "#   prefix, and the Ru ATOMIC_SPECIES line",
        "#   %s -> %s" % (PP_OLD, PP_NEW),
        "# (GBRV v1.2, PBE, ultrasoft, Z valence 16). Cutoffs 80/640 Ry, k-mesh",
        "# 8 4 1, nspin = 1, smearing, geometry, cell and the HUBBARD card are",
        "# inherited byte-identically.",
        "#",
        "# NOT LICENSED FOR SUBMISSION. This control has no dated registration",
        "# line. docs/89-ru-pseudopotential-control-DRAFT.md is a PROPOSAL with",
        "# blank entrant slots; anvil/47_submit_a0.sh refuses this manifest while",
        "# this notice stands (docs/66 section 4). Licensing also owes a dated row",
        "# for the new UPF in the pseudo md5 preflight record: it is staged at",
        "# $PROJECT/pseudo/%s, md5 %s" % (PP_NEW, PP_NEW_MD5),
        "# on both ends (runs/a0/ru_pp/PSEUDO_PROVENANCE.md), and has no row in",
        "# anvil/pseudo_md5_preflight_2026-08-23.md.",
        "#",
        "# SUBMIT WITH EXCLUDE=%s" % EXCLUDE,
        "#",
        "# nk = %d matches the banked source rows (runs/a0/m_a0main.txt:129-160)," % NK,
        "# and NP = 128 is a multiple of it. Runnable rows are: dir job suffix nk",
        "#",
        "# md5 of each deck, for the record (control deck, then its source deck):",
    ]
    for state, utok, u, dst, src, d in rows:
        lines.append("#   %-7s %6.4f  %s  <- %s %s"
                     % (state, u, md5(dst), md5(src), W.rel(src)))
    lines.append("#")
    for state, utok, u, dst, src, d in rows:
        lines.append("a0/ru_pp/Ru %s__%s%s .in %d" % (state, utok, SUFFIX, NK))
    W.write(MANIFEST, "\n".join(lines) + "\n")
    print("  manifest -> %s" % W.rel(MANIFEST))
    print()
    print("  NOT LICENSED. No dated registration line exists; docs/89 is a proposal.")
    print("  anvil/47_submit_a0.sh will refuse this manifest until the notice is lifted.")


if __name__ == "__main__":
    main()
