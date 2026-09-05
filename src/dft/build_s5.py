#!/usr/bin/env python
"""S5 -- the BEEF-vdW sigma arm: 12 slab single points + 2 gas references.

STATUS: NOT LICENSED. Built ahead of the Amendment 10 deposit so that the
objects can be md5-manifested before the thresholds are authored, on the
ordering build_pproj6.py established (decks first, thresholds second, submit
third). The manifest carries a NOT LICENSED notice; anvil/47_submit_a0.sh and
anvil/43_submit_s3_wave1.sh refuse such a manifest with no override.

WHAT THIS BUILDS

  {Ru, Ir, Ti} x {ref, s0_O, s0_OH, s0_OOH}  = 12 self-consistent BEEF-vdW
  single points at fixed PBE tier_v3 2x1v geometries, plus H2 and H2O in the
  12 A Martyna-Tuckerman box, all under calculation = 'ensemble' so that the
  2000-member BEEF ensemble is emitted after the SCF.

  Stage spec: docs/research/2026-08-15-lit-sweep-round2-synthesis.md:286-291
  ("12 self-consistent BEEF-vdW SCFs at fixed PBE+U tier_v3 geometries ...
  plus 2 gas references"); docs/74-amendment-10-DRAFT.md section A10.4.

SOURCES (every source .out is a converged relax: JOB DONE, bfgs converged,
one `Begin final coordinates` block, zero `convergence NOT achieved`):

  Ru  runs/probe/Ru_cellsym/{ref__2x1v, s0_O__2x1v_mir, s0_OH__2x1v_mir,
                             s0_OOH__2x1v_mir}          (docs/54 section 2.6)
  Ir  runs/probe/Ir_cellsym/ the same four               (docs/54 section 2.7)
  Ti  runs/s3/Ti/            the same four               (docs/54 section 2.8)
  gas runs/Ru_anchor/{H2, H2O}  -- byte-identical decks live in all nine
      runs/*_slab and runs/*_anchor directories (one md5 per species), and
      every banked .out lands on the same final geometry; asserted below.

WHICH SYMMETRY ARM. tier_v3 carries two arms per adsorbate state (mir =
symmetry ON, off = nosym + displacement; docs/54:19-22). docs/74 names the
cell and the tier but not the arm. This build takes the mir arm, on the
precedent of the only other fixed-geometry 2x1v single-point arm in the
campaign, runs/a0/cell/manifest.json ("mir arm = symmetry-ON, the counterpart
of the symmetry-ON 1x1 ladder"), and the bare ref__2x1v deck (nosym + noinv,
the block-1A reference convention, docs/54:130). The arm is a constant below
and is recorded in the manifest as a builder choice, not a registration.

THE TRANSFORMATION, and the guard on it

Each deck differs from its source deck in exactly these lines and no others:

    calculation = 'relax'          ->  calculation = 'ensemble'
    prefix = '<stem>'              ->  prefix = '<stem>__beef'
    (inserted, last line of &SYSTEM)   input_dft = 'BEEF-vdW'
    ATOMIC_POSITIONS coordinates   ->  the source .out's final coordinates,
                                       8 decimals, species and if_pos
                                       flags preserved line by line

Cell, cutoffs, k-mesh, smearing, mixing, conv_thr, electron_maxstep,
max_seconds, pseudopotentials, nosym/noinv and the absence of any HUBBARD
card and of any nspin = 2 line are inherited byte-identically. build_one()
diffs source against product line by line and DIES on any other difference.
No startingpot / startingwfc / restart_mode is ever emitted: fresh density.

WHY calculation = 'ensemble' AND NOT 'scf'. docs/43:1497-1498 (deposited):
"BEEF is reachable only through calculation='ensemble'". The S0(a) control
deck runs/s0/a_beef/slab__beefctl.in (calculation='scf' + input_dft) reached
JOB DONE with zero BEEFens lines; runs/s0/a_beef/slab__beefcalc.in
(calculation='ensemble') emitted `BEEFens 2000 ensemble energies`
(slab__beefcalc.out:1076). In QE 7.5 'ensemble' is an SCF followed by the
non-self-consistent ensemble on the converged BEEF-vdW density, which is the
stage spec's non-negotiable (i).

nk PER ROW is derived from the source .out's printed k-point count exactly as
build_s3_wave2.hess_nk does (16 if >= 16, else 8 if >= 8, else 4, else 1),
which reproduces runs/s3/m_s3_wave1.txt:81-87 for the Ti sources; NP = 128 is
a multiple of every value.

DETERMINISM: no timestamps, no environment-dependent content; two runs are
byte-identical (verified by md5 over the emitted tree).

Usage:
    PYTHONPATH=src python src/dft/build_s5.py            # build + verify
    PYTHONPATH=src python src/dft/build_s5.py --check    # verify only, no write
"""

import hashlib
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import build_s3_wave2 as W  # noqa: E402
from probe_decks import parse_final_coordinates, parse_input_deck  # noqa: E402

ROOT = W.ROOT
DST_ROOT = os.path.join(ROOT, "runs", "s5")
MANIFEST = os.path.join(DST_ROOT, "m_s5.txt")

# --- stage constants; each one is read from the tree, and the citation says where
XC = "BEEF-vdW"            # runs/s0/a_beef/README.md; docs/74 section A10.4 item 4
CALC_OLD = "relax"
CALC_NEW = "ensemble"      # docs/43:1497-1498; runs/s0/a_beef/slab__beefcalc.out:1076
SUFFIX = "__beef"
ARM = "mir"                # runs/a0/cell/manifest.json precedent (see docstring)
NP = 128                   # anvil/47_submit_a0.sh NP default; anvil/46_a0.slurm -n 128
# most recent sick-node list carried by a manifest: runs/a0/m_pproj6.txt:15,
# runs/a0/m_pproj_cell.txt:26 (docs/66 section 4 adds a120,a200 at submit time)
EXCLUDE = "a024,a049,a050,a088,a196,a220,a223,a171"

SLAB_SRC = {
    "Ru": os.path.join(ROOT, "runs", "probe", "Ru_cellsym"),
    "Ir": os.path.join(ROOT, "runs", "probe", "Ir_cellsym"),
    "Ti": os.path.join(ROOT, "runs", "s3", "Ti"),
}
METALS = ["Ru", "Ir", "Ti"]
STATES = [("ref", "ref__2x1v"),
          ("s0_O", "s0_O__2x1v_" + ARM),
          ("s0_OH", "s0_OH__2x1v_" + ARM),
          ("s0_OOH", "s0_OOH__2x1v_" + ARM)]

GAS_SRC = os.path.join(ROOT, "runs", "Ru_anchor")
GAS = ["H2", "H2O"]
# every directory that carries a banked copy of the gas decks (md5 asserted equal)
GAS_COPIES = ["Co_slab", "Cr_slab", "Cu_slab", "Fe_slab", "Mn_slab", "Ni_slab",
              "Ti_slab", "Ir_anchor", "Ru_anchor"]

FORBIDDEN_RESTART = re.compile(r"startingpot|startingwfc|restart_mode", re.I)


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def md5_text(txt):
    return hashlib.md5(txt.encode("ascii")).hexdigest()


def read_out(path):
    """A banked pw.x output, read for its markers only. Outputs are not decks:
    runs/*/H2.out and H2O.out are CRLF-mirrored and some outputs carry NUL
    bytes, so the deck reader's LF rule does not apply here. Nothing read
    through this function is ever emitted."""
    with open(path, newline="", errors="replace") as fh:
        return fh.read().replace("\r\n", "\n")


# ------------------------------------------------------------ source checks ---

def source_is_converged(out_path):
    if not os.path.exists(out_path):
        return False, "no .out"
    txt = read_out(out_path)
    if "JOB DONE" not in txt:
        return False, "no JOB DONE"
    if "convergence NOT achieved" in txt:
        return False, "convergence NOT achieved"
    if "bfgs converged" not in txt or "End of BFGS Geometry Optimization" not in txt:
        return False, "relax did not converge (no 'bfgs converged')"
    if txt.count("Begin final coordinates") != 1:
        return False, "expected exactly one 'Begin final coordinates' block"
    return True, "ok"


def out_facts(out_path):
    """Header facts of the banked run, for the manifest (all read, none computed)."""
    txt = read_out(out_path)
    ver = re.search(r"Program PWSCF (v\.\S+) starts on\s+(\S+)", txt)
    cores = re.search(r"running on\s+(\d+) processor cores", txt)
    nat = re.search(r"number of atoms/cell\s*=\s*(\d+)", txt)
    nk = re.search(r"number of k points=\s*(\d+)", txt)
    energies = re.findall(r"^!\s+total energy\s+=\s+(-?[\d.]+)\s+Ry", txt, re.M)
    if not (ver and cores and nat and energies):
        W.die("%s: could not read the run header" % W.rel(out_path))
    return dict(version=ver.group(1), date=ver.group(2), cores=int(cores.group(1)),
                nat=int(nat.group(1)), nkpt=int(nk.group(1)) if nk else 1,
                energy=energies[-1])


def nk_for(nkpt):
    for cand in (16, 8, 4, 1):
        if nkpt >= cand:
            if NP % cand:
                W.die("NP=%d is not a multiple of nk=%d" % (NP, cand))
            return cand
    W.die("no legal nk for %d k-points" % nkpt)


# ------------------------------------------------------------- deck surgery ---

def parse_rows(body, path):
    """[(species, xs, ys, zs, flags-or-None)] -- 4-field (gas) or 7-field (slab)
    position lines, coordinates kept as the literal strings."""
    rows = []
    for line in body.rstrip("\n").split("\n"):
        p = line.split()
        if len(p) == 7:
            rows.append((p[0], p[1], p[2], p[3], "%s %s %s" % (p[4], p[5], p[6])))
        elif len(p) == 4:
            rows.append((p[0], p[1], p[2], p[3], None))
        else:
            W.die("%s: position line not 4 or 7 fields: %r" % (W.rel(path), line))
    return rows


def fmt_rows(rows):
    out = []
    for sp, xs, ys, zs, flags in rows:
        line = "  %s  %s  %s  %s" % (sp, xs, ys, zs)
        if flags is not None:
            line += "  " + flags
        out.append(line + "\n")
    return "".join(out)


def selftest_formatter(txt, path):
    a, b = W.pos_block_span(txt, path)
    rows = parse_rows(txt[a:b], path)
    if fmt_rows(rows) != txt[a:b]:
        W.die("%s: formatter self-test failed (layout drift)" % W.rel(path))
    return rows


def swap_positions(txt, path, rows):
    a, b = W.pos_block_span(txt, path)
    return txt[:a] + fmt_rows(rows) + txt[b:]


def insert_input_dft(txt, path):
    """Insert `input_dft = 'BEEF-vdW'` as the last line of &SYSTEM. Returns the
    new text and the 0-based index of the inserted line."""
    lines = txt.split("\n")
    heads = [i for i, l in enumerate(lines) if l.strip().upper() == "&SYSTEM"]
    if len(heads) != 1:
        W.die("%s: expected exactly one &SYSTEM namelist" % W.rel(path))
    j = heads[0] + 1
    while j < len(lines) and lines[j].strip() != "/":
        j += 1
    if j >= len(lines):
        W.die("%s: &SYSTEM namelist has no closing '/'" % W.rel(path))
    lines.insert(j, "  input_dft = '%s'" % XC)
    return "\n".join(lines), j


def classify(x, y, path):
    if re.match(r"\s*calculation\s*=", x) and re.match(r"\s*calculation\s*=", y):
        return "calculation"
    if re.match(r"\s*prefix\s*=", x) and re.match(r"\s*prefix\s*=", y):
        return "prefix"
    px, py = x.split(), y.split()
    if len(px) == len(py) and len(px) in (4, 7) and px[0] == py[0] and px[4:] == py[4:]:
        return "coords"
    W.die("%s: disallowed diff vs source deck:\n  - %r\n  + %r" % (W.rel(path), x, y))


def read_deck(path, allow_crlf):
    """A source deck. The banked slab decks are LF and W.read enforces that.
    The nine banked gas decks (June 2026) are CRLF in every copy, so the gas
    sources are read with CRLF normalised; the emitted deck is LF either way
    (the Anvil runner strips CR when it writes the .run.in, anvil/46_a0.slurm,
    and the driver preflight refuses a CR deck). Returns (text, was_crlf)."""
    if not allow_crlf:
        return W.read(path), False
    with open(path, newline="") as fh:
        txt = fh.read()
    if "\r" not in txt:
        return txt, False
    if txt.count("\r\n") != txt.count("\r"):
        W.die("%s: a bare CR (not CRLF) in the source deck" % W.rel(path))
    return txt.replace("\r\n", "\n"), True


def build_one(src_in, src_out, dst_dir, stem, write, allow_crlf=False):
    """Clone src_in -> dst_dir/<stem>__beef.in at src_out's final geometry."""
    job = stem + SUFFIX
    dst = os.path.join(dst_dir, job + ".in")
    for p in (src_in, src_out):
        if not os.path.exists(p):
            W.die("%s: missing" % W.rel(p))
    ok, why = source_is_converged(src_out)
    if not ok:
        W.die("%s: not a banked converged relax (%s) -- a BEEF single point on "
              "an unconverged geometry is not the registered object" % (W.rel(src_out), why))

    src, src_crlf = read_deck(src_in, allow_crlf)
    if FORBIDDEN_RESTART.search(src):
        W.die("%s: source deck carries a restart key" % W.rel(src_in))
    if "HUBBARD" in src:
        W.die("%s: source deck carries a HUBBARD card; S5 base set is U = 0" % W.rel(src_in))
    if "input_dft" in src:
        W.die("%s: source deck already sets input_dft" % W.rel(src_in))
    if re.search(r"^\s*nspin\s*=\s*2", src, re.M):
        W.die("%s: source deck is nspin = 2; S5 base set is nspin = 1" % W.rel(src_in))
    if re.search(r"^\s*calculation\s*=\s*'%s'" % CALC_OLD, src, re.M) is None:
        W.die("%s: source calculation is not '%s'" % (W.rel(src_in), CALC_OLD))
    if re.search(r"^\s*prefix\s*=\s*'%s'\s*$" % re.escape(stem), src, re.M) is None:
        W.die("%s: prefix is not '%s'" % (W.rel(src_in), stem))

    src_deck = parse_input_deck(src_in)
    rows = selftest_formatter(src, src_in)
    facts = out_facts(src_out)
    nat = int(re.search(r"^\s*nat\s*=\s*(\d+)", src, re.M).group(1))
    if len(rows) != nat or facts["nat"] != nat:
        W.die("%s: nat=%d, deck rows=%d, .out nat=%d" % (W.rel(src_in), nat, len(rows), facts["nat"]))

    pos, prov = parse_final_coordinates(src_out)
    if pos is None or prov != "final":
        W.die("%s: geometry provenance %r, need 'final'" % (W.rel(src_out), prov))
    if len(pos) != len(rows):
        W.die("%s: %d final atoms != %d deck atoms" % (W.rel(src_out), len(pos), len(rows)))
    if [p[0] for p in pos] != [r[0] for r in rows]:
        W.die("%s: species order differs from deck" % W.rel(src_out))

    new_rows = [(sp, "%.8f" % x, "%.8f" % y, "%.8f" % z, r[4])
                for (sp, x, y, z), r in zip(pos, rows)]
    txt = W.swap_scalar_line(src, src_in, "calculation", CALC_OLD, CALC_NEW)
    txt = W.swap_scalar_line(txt, src_in, "prefix", stem, job)
    txt = swap_positions(txt, src_in, new_rows)
    txt, ins = insert_input_dft(txt, src_in)

    # --- independent verifier: exactly {calculation, prefix, +input_dft, coords}
    a = src.split("\n")
    b = txt.split("\n")
    if len(b) != len(a) + 1:
        W.die("%s: line count %d -> %d, expected +1" % (W.rel(src_in), len(a), len(b)))
    if b[ins].strip() != "input_dft = '%s'" % XC:
        W.die("%s: inserted line is not the input_dft line" % job)
    b_wo = b[:ins] + b[ins + 1:]
    diffs = [(i, x, y) for i, (x, y) in enumerate(zip(a, b_wo), 1) if x != y]
    kinds = [classify(x, y, dst) for _, x, y in diffs]
    if kinds.count("calculation") != 1 or kinds.count("prefix") != 1 \
            or set(kinds) - {"calculation", "prefix", "coords"}:
        W.die("%s: diff vs source is not {calculation, prefix, coords}: %r" % (job, kinds))
    for k in ("startingpot", "startingwfc", "restart_mode", "HUBBARD", "nspin = 2"):
        if k in txt:
            W.die("%s: emitted deck contains %r" % (job, k))

    if write:
        if not os.path.isdir(dst_dir):
            os.makedirs(dst_dir)
        W.write(dst, txt)
        emitted = W.read(dst)
        if emitted != txt:
            W.die("%s: read-back differs from what was written" % W.rel(dst))
        deck = parse_input_deck(dst)
        for key in ("cell", "species", "kpts", "hubbard", "mags", "flags"):
            if deck[key] != src_deck[key]:
                W.die("%s: %s differs from source deck" % (W.rel(dst), key))
        if deck["nosym"] != src_deck["nosym"]:
            W.die("%s: nosym differs from source deck" % W.rel(dst))
        if len(deck["positions"]) != nat:
            W.die("%s: emitted position count != nat" % W.rel(dst))

    # the diff record: every differing line, plus the insertion, numbered in the
    # EMITTED deck (source line numbers are the same up to the insertion point)
    record = []
    for i, x, y in diffs:
        n = i if (i - 1) < ins else i + 1
        record.append((n, x, y))
    record.append((ins + 1, None, b[ins]))
    record.sort(key=lambda t: t[0])
    return dict(job=job, dst=dst, src_in=src_in, src_out=src_out, txt=txt,
                nk=nk_for(facts["nkpt"]), facts=facts, diffs=record,
                ncoord=kinds.count("coords"), src_crlf=src_crlf)


def check_gas_identity():
    """The nine banked gas decks are one deck (docs/74 A10.4 item 5 relies on it),
    and every banked .out lands on the same final geometry."""
    for g in GAS:
        ref_in = os.path.join(ROOT, "runs", GAS_COPIES[-1], g + ".in")
        ref_md5 = md5(ref_in)
        ref_pos, prov = parse_final_coordinates(os.path.join(GAS_SRC, g + ".out"))
        if ref_pos is None or prov != "final":
            W.die("%s.out: no final geometry" % g)
        n_out = 0
        for d in GAS_COPIES:
            p = os.path.join(ROOT, "runs", d, g + ".in")
            if not os.path.exists(p):
                W.die("%s: banked gas deck missing" % W.rel(p))
            if md5(p) != ref_md5:
                W.die("%s: gas deck md5 differs across banked copies" % W.rel(p))
            o = os.path.join(ROOT, "runs", d, g + ".out")
            if not os.path.exists(o):
                continue
            pos, prov = parse_final_coordinates(o)
            if pos is None or prov != "final":
                continue
            n_out += 1
            for (s1, x1, y1, z1), (s2, x2, y2, z2) in zip(ref_pos, pos):
                if s1 != s2 or max(abs(x1 - x2), abs(y1 - y2), abs(z1 - z2)) > 1e-8:
                    W.die("%s: final geometry differs from %s" % (W.rel(o), W.rel(GAS_SRC)))
        print("  gas %-3s one deck (md5 %s) in %d dirs; %d banked finals agree"
              % (g, ref_md5, len(GAS_COPIES), n_out))


# --------------------------------------------------------------------- main ---

def main():
    check_only = "--check" in sys.argv
    print("S5 builder -- %s" % ("CHECK ONLY, no files written" if check_only else "building"))
    print("  NOT LICENSED: Amendment 10 is a draft (docs/74); nothing here may be submitted.")
    check_gas_identity()

    recs = []
    for metal in METALS:
        for state, stem in STATES:
            r = build_one(os.path.join(SLAB_SRC[metal], stem + ".in"),
                          os.path.join(SLAB_SRC[metal], stem + ".out"),
                          os.path.join(DST_ROOT, metal), stem, write=not check_only)
            r["group"], r["state"] = metal, state
            recs.append(r)
            print("  %-3s %-7s %-28s nat=%2d nk=%2d coords-changed=%2d  src E=%s Ry"
                  % (metal, state, r["job"], r["facts"]["nat"], r["nk"], r["ncoord"],
                     r["facts"]["energy"]))
    for g in GAS:
        r = build_one(os.path.join(GAS_SRC, g + ".in"), os.path.join(GAS_SRC, g + ".out"),
                      os.path.join(DST_ROOT, "gas"), g, write=not check_only,
                      allow_crlf=True)
        r["group"], r["state"] = "gas", g
        recs.append(r)
        print("  %-3s %-7s %-28s nat=%2d nk=%2d coords-changed=%2d  src E=%s Ry"
              % ("gas", g, r["job"], r["facts"]["nat"], r["nk"], r["ncoord"],
                 r["facts"]["energy"]))
    if len(recs) != 14:
        W.die("built %d decks, expected 14" % len(recs))
    print("  %d decks %s" % (len(recs), "verified" if check_only else "written"))
    if check_only:
        return

    L = [
        "# S5 manifest -- BEEF-vdW sigma arm, {Ru, Ir, Ti} x {ref, s0_O, s0_OH, s0_OOH}",
        "# at fixed PBE tier_v3 2x1v geometries (%s arm), plus H2 and H2O in the" % ARM,
        "# 12 A Martyna-Tuckerman box. Built by src/dft/build_s5.py.",
        "#",
        "# NOT LICENSED. Amendment 10 is DRAFT v2 (docs/74-amendment-10-DRAFT.md) and",
        "# is not adopted, not appended to docs/43 and not deposited. Every threshold",
        "# it governs is the entrant's to author (docs/88-a10-signature-sheet-",
        "# 2026-09-05.md). The submitters refuse this notice with no override",
        "# (anvil/47_submit_a0.sh; anvil/43_submit_s3_wave1.sh; docs/66 section 4).",
        "# When licensed, replace this paragraph with the dated adoption line and",
        "# the deposit DOI, and leave every deck md5 below unchanged.",
        "#",
        "# SUBMIT WITH EXCLUDE=%s" % EXCLUDE,
        "#",
        "# Stage spec: docs/research/2026-08-15-lit-sweep-round2-synthesis.md:286-291.",
        "# calculation = 'ensemble' because docs/43:1497-1498 records that BEEF is",
        "# reachable only through it; the S0(a) control deck (calculation='scf' +",
        "# input_dft, runs/s0/a_beef/slab__beefctl.out) emitted no BEEFens block.",
        "# The symmetry arm (%s) is a builder choice on the runs/a0/cell/manifest.json" % ARM,
        "# precedent; docs/74 names the cell and tier but not the arm.",
        "#",
        "# Each deck differs from its source deck in exactly: calculation",
        "# 'relax' -> 'ensemble', prefix -> '<stem>__beef', one inserted line",
        "# input_dft = 'BEEF-vdW' (last line of &SYSTEM), and the ATOMIC_POSITIONS",
        "# coordinates -> the source .out's final geometry. No HUBBARD card, no",
        "# nspin = 2, no startingpot/startingwfc/restart_mode anywhere. nk per row",
        "# is from the source .out's k-point count; %d ranks is a multiple of each." % NP,
        "#",
        "# md5 of each deck, and of its source deck and source .out, for the record:",
    ]
    for r in recs:
        f = r["facts"]
        L.append("#   %-4s %-7s %-28s %s" % (r["group"], r["state"], r["job"], md5_text(r["txt"])))
        L.append("#        source deck %-45s %s" % (W.rel(r["src_in"]), md5(r["src_in"])))
        L.append("#        source .out %-45s %s" % (W.rel(r["src_out"]), md5(r["src_out"])))
        L.append("#        source run: PWSCF %s, %s, %d cores, nat %d, %d k-points, E %s Ry"
                 % (f["version"], f["date"], f["cores"], f["nat"], f["nkpt"], f["energy"]))
        if r["src_crlf"]:
            L.append("#        source deck is CRLF in every banked copy; emitted deck is LF")
    L.append("#")
    L.append("# Every line that differs from the source deck (line numbers are the")
    L.append("# emitted deck's; '+' marks the inserted line):")
    for r in recs:
        L.append("#   %s  (%d lines differ, %d of them coordinates)"
                 % (r["job"], len(r["diffs"]), r["ncoord"]))
        for n, x, y in r["diffs"]:
            if x is None:
                L.append("#     L%-3d +%s" % (n, y))
            else:
                L.append("#     L%-3d %s  ->  %s" % (n, x.strip(), y.strip()))
    L.append("#")
    L.append("# Runnable rows: dir job suffix nk")
    for r in recs:
        L.append("s5/%s %s .in %d" % (r["group"], r["job"], r["nk"]))
    W.write(MANIFEST, "\n".join(L) + "\n")
    print("  manifest -> %s" % W.rel(MANIFEST))
    print()
    print("  NOT LICENSED. Do not submit. See docs/88-a10-signature-sheet-2026-09-05.md.")


if __name__ == "__main__":
    main()
