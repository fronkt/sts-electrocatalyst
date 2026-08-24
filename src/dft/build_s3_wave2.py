#!/usr/bin/env python3
"""S3 wave-2 deck builder (37 __g1 children + 19 Cr re-Hessian SCFs), 2026-08-24.

SCOPE IS THE REGISTERED WAVE-2 SPEC, NOT THIS FILE
--------------------------------------------------
Registration of record: deposited A8, DOI 10.5281/zenodo.22072991; dispositions
docs/54-s3-deck-matrix-2026-08-23.md (SS3 SCF families; the re-Hessian row
docs/54:158/:324); the __g1 construction convention is docs/43:1575-1592 (A8.3)
with runs/s3/Cr/s0_OOH__basin_g1.in and the banked runs/probe/Cr_cellsym __g1
decks as the emitted-style exemplars.

WHAT IS BUILT (56 decks + runs/s3/m_s3_wave2.txt)
-------------------------------------------------
A) 37 `__g1` children -- one fresh-density fixed-geometry SCF per CONVERGED
   wave-1 RELAX parent (46 converged = 37 relax + 9 SCF; the 9 SCFs get no
   children; the 9 rung-iii NOT_CONVERGED relaxations get none either).
   Construction: the deck that ACTUALLY CONVERGED the parent (the `.retry_bh.in`
   beta-0.15 deck for Co/s0_O__1x1_off and Ni/s0_O__1x1_off, the plain `.in`
   everywhere else) is cloned VERBATIM -- symmetry flags, &IONS block, CONTROL
   extras, HUBBARD, K_POINTS, cell, if_pos flags -- and differs ONLY in
     {calculation 'relax'->'scf', prefix -> '<job>__g1',
      ATOMIC_POSITIONS coordinates -> the parent's converged FINAL geometry}.
   No startingpot/restart keys are ever emitted: fresh density.
   manifest nk for a child = its parent's row nk in runs/s3/m_s3_wave1.txt.

B) 19 Cr block-1C re-Hessian SCFs at the ESCAPED geometry (docs/54:158 "1C
   escape relax + re-Hessian", conv_thr 1e-10 class): base geometry = final
   coords of runs/s3/Cr/s0_OOH__2x1v_escape.out; everything else mirrors the
   banked runs/probe/Cr_hess decks EXACTLY (conv_thr 1.0d-10, electron_maxstep
   120, nosym+noinv on every deck INCLUDING the reference, K_POINTS 4 4 1 0 0 0,
   same species/pseudos/cell) except base geometry and prefixes. Same displaced
   atoms/axes/signs as runs/probe/Cr_hess/hess_manifest.json (atoms 37/38/39 x
   x/y/z x +/-), delta nominal 0.01 A. Names:
   runs/s3/Cr/s0_OOH__2x1v_esc__hess_<tag>.in, <tag> in {ref, a37xp..a39zm} --
   the SAME tag scheme as probe/Cr_hess so src/dft/hessian_analyze.py stays
   parseable.

hessian_analyze.py COMPATIBILITY (verified 2026-08-24)
------------------------------------------------------
hessian_analyze.py takes DIRECTORIES on argv and discovers every file through
`<dir>/hess_manifest.json`: it reads `man["jobs"][i]["job"] + ".out"` and
`man["reference_job"] + ".in"` inside that directory (hessian_analyze.py:1457,
:1462, :589). There is NO hardcoded glob or job-name pattern, so keeping the
banked tag scheme means ZERO parser changes. What the analysis step will need is
a wave-2 `hess_manifest.json` (jobs renamed s0_OOH__2x1v_esc__hess_*) placed in
the directory holding the .out files. That manifest is deliberately NOT emitted
here: its fields encode analysis-method decisions (mirror_plane drives the
forward-y vs central-y construction of H, reference energies drive the magnetic
guard) that belong to the analysis step at the escaped -- mirror-BROKEN --
geometry, not to a deck builder.

SPEC AMBIGUITIES RESOLVED (recorded per instruction)
----------------------------------------------------
1. DELTA ARITHMETIC: the banked hess_manifest records achieved displacements
   like 0.0099999965 A because the banked builder displaced the UNROUNDED relax
   finals and then rounded to the deck's 8 decimals. This build applies the
   nominal +/-0.01 A to the 8-decimal-ROUNDED reference coordinates (exact in
   decimal), so every emitted displacement is EXACTLY +/-0.01000000 in the
   written text -- which is what the required assert ("exactly +/-delta")
   checks. Physical difference < 5e-9 A.
2. max_seconds: the banked Cr_cellsym __g1 children rewrote max_seconds (a
   Vast-box budget artifact). The wave-2 spec's exclusive-difference list and
   the s0_OOH__basin_g1.in template (max_seconds = 165000 = the parent's value)
   govern: max_seconds is cloned VERBATIM from the parent deck.
3. Cr s0_OOH__2x1v_escape IS a converged wave-1 relax parent, so it gets a
   __g1 child (s0_OOH__2x1v_escape__g1); the 37 count closes only with it.
4. The ym decks (Q6 mirror-identity controls in the banked set) are emitted:
   "mirror runs/probe/Cr_hess EXACTLY" -- all 18 displaced tags, both y signs.
5. The banked hess decks carry no max_seconds line; mirrored as-is (none added).

DETERMINISM: no timestamps, no environment-dependent content; two runs must be
byte-identical (verified by md5 over the emitted tree).

Usage:  python src/dft/build_s3_wave2.py
Emits ONLY: runs/s3/<Metal>/<job>__g1.in (37),
            runs/s3/Cr/s0_OOH__2x1v_esc__hess_<tag>.in (19),
            runs/s3/m_s3_wave2.txt.
"""
from __future__ import annotations

import json
import os
import re
import sys
from decimal import Decimal

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(_HERE, "..", ".."))
sys.path.insert(0, _HERE)

from probe_decks import parse_input_deck, parse_final_coordinates  # noqa: E402

S3 = os.path.join(ROOT, "runs", "s3")
CR_HESS = os.path.join(ROOT, "runs", "probe", "Cr_hess")
WAVE1_MANIFEST = os.path.join(S3, "m_s3_wave1.txt")
WAVE2_MANIFEST = os.path.join(S3, "m_s3_wave2.txt")
DOI = "10.5281/zenodo.22072991"
NP = 128
DELTA = Decimal("0.01")           # nominal displacement, A (docs/43 P14)
HESS_BASE_JOB = "s0_OOH__2x1v_escape"
HESS_JOB_STEM = "s0_OOH__2x1v_esc__hess_"
BANKED_HESS_STEM = "s0_OOH__2x1v_mir__hess_"

#: the 9 rung-iii convergence failures of wave 1 (A8.4 ladder; docs/45). The
#: build DERIVES convergence from the .out markers and REFUSES if the derived
#: set differs from this registered record.
EXPECTED_NOT_CONVERGED = {
    ("Co", "ref__2x1v"), ("Co", "s0_OH__1x1_off"),
    ("Co", "s0_O__2x1v_mir"), ("Co", "s0_OH__2x1v_mir"),
    ("Co", "s0_OOH__2x1v_mir"),
    ("Co", "s0_OH__2x1v_off"), ("Co", "s0_OOH__2x1v_off"),
    ("Ni", "s0_OOH__2x1v_mir"), ("Ni", "s0_OOH__2x1v_off"),
}
#: the two decks whose CONVERGED run was the beta-0.15 retry (their .out IS the
#: retry run); the build derives this from the .out's printed mixing beta and
#: REFUSES on any mismatch with this record.
EXPECTED_RETRY_BH = {("Co", "s0_O__1x1_off"), ("Ni", "s0_O__1x1_off")}

FORBIDDEN_RESTART = re.compile(r"startingpot|startingwfc|restart_mode", re.I)

EMITTED = []      # (relpath, class, nk, note)


def die(msg):
    raise SystemExit(f"REFUSING TO BUILD: {msg}")


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


def read(path):
    with open(path, newline="") as fh:
        txt = fh.read()
    if "\r" in txt:
        die(f"{rel(path)}: CRLF line ending found; the banked tree is LF")
    return txt


def write(path, txt):
    with open(path, "w", newline="\n") as fh:
        fh.write(txt)


# ------------------------------------------------------------ deck surgery ---

def pos_block_span(txt, path):
    """(start, end) character span of the ATOMIC_POSITIONS body (excl. header)."""
    if txt.count("ATOMIC_POSITIONS angstrom") != 1:
        die(f"{rel(path)}: expected exactly one 'ATOMIC_POSITIONS angstrom'")
    m = re.search(r"^ATOMIC_POSITIONS angstrom\n", txt, re.M)
    j = txt.find("K_POINTS", m.end())
    if j < 0:
        die(f"{rel(path)}: no K_POINTS after ATOMIC_POSITIONS")
    return m.end(), j


def parse_pos_lines(body, path):
    """[(species, xs, ys, zs, flags)] with coordinates as the literal strings."""
    out = []
    for line in body.rstrip("\n").split("\n"):
        p = line.split()
        if len(p) != 7:
            die(f"{rel(path)}: position line not 7 fields: {line!r}")
        out.append((p[0], p[1], p[2], p[3], f"{p[4]} {p[5]} {p[6]}"))
    return out


def fmt_line(sp, xs, ys, zs, flags):
    return f"  {sp}  {xs}  {ys}  {zs}  {flags}"


def fmt_block(rows):
    return "".join(fmt_line(*r) + "\n" for r in rows)


def selftest_formatter(txt, path):
    """Rebuilding the deck's own position block from parsed fields must be
    byte-identical -- validates the emitter convention on every source deck."""
    a, b = pos_block_span(txt, path)
    body = txt[a:b]
    rows = parse_pos_lines(body, path)
    if fmt_block(rows) != body:
        die(f"{rel(path)}: formatter self-test failed (layout drift)")
    return rows


def swap_positions(txt, path, new_rows):
    a, b = pos_block_span(txt, path)
    return txt[:a] + fmt_block(new_rows) + txt[b:]


def swap_scalar_line(txt, path, key, old, new):
    pat = re.compile(rf"^(\s*{key}\s*=\s*)'{re.escape(old)}'\s*$", re.M)
    if len(pat.findall(txt)) != 1:
        die(f"{rel(path)}: expected exactly one {key} = '{old}' line")
    return pat.sub(rf"\g<1>'{new}'", txt, count=1)


def diff_lines(src_txt, new_txt, path):
    """Independent verifier: return the list of (i, src_line, new_line) diffs;
    line counts must be equal."""
    a, b = src_txt.split("\n"), new_txt.split("\n")
    if len(a) != len(b):
        die(f"{rel(path)}: line count changed vs source deck")
    return [(i, x, y) for i, (x, y) in enumerate(zip(a, b)) if x != y]


def classify_diff(x, y, path):
    """Allowed diff kinds: 'calculation', 'prefix', 'coords' (species+flags
    preserved, only coordinate fields changed)."""
    if re.match(r"\s*calculation\s*=", x) and re.match(r"\s*calculation\s*=", y):
        return "calculation"
    if re.match(r"\s*prefix\s*=", x) and re.match(r"\s*prefix\s*=", y):
        return "prefix"
    px, py = x.split(), y.split()
    if len(px) == 7 and len(py) == 7 and px[0] == py[0] and px[4:] == py[4:]:
        return "coords"
    die(f"{rel(path)}: disallowed diff vs source deck:\n  - {x!r}\n  + {y!r}")


def namelist_sanity(path, want_prefix, ref_deck):
    txt = read(path)
    deck = parse_input_deck(path)
    nat = int(re.search(r"^\s*nat\s*=\s*(\d+)", txt, re.M).group(1))
    if len(deck["positions"]) != nat:
        die(f"{rel(path)}: nat={nat} != {len(deck['positions'])} position lines")
    if re.search(r"^\s*calculation\s*=\s*'scf'", txt, re.M) is None:
        die(f"{rel(path)}: calculation is not 'scf'")
    if re.search(rf"^\s*prefix\s*=\s*'{re.escape(want_prefix)}'", txt, re.M) is None:
        die(f"{rel(path)}: prefix is not '{want_prefix}'")
    if FORBIDDEN_RESTART.search(txt):
        die(f"{rel(path)}: restart/startingpot key emitted -- must be fresh density")
    for key in ("cell", "species", "kpts", "hubbard", "mags", "flags"):
        if deck[key] != ref_deck[key]:
            die(f"{rel(path)}: {key} differs from source deck")
    if deck["nosym"] != ref_deck["nosym"]:
        die(f"{rel(path)}: nosym flag differs from source deck")
    return deck


# ------------------------------------------------------- wave-1 census (A) ---

def load_wave1_rows():
    rows = []
    for line in read(WAVE1_MANIFEST).split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        loc, job, suf, nk = line.split()
        if suf != ".in":
            die(f"wave-1 manifest row with suffix {suf!r}")
        rows.append((loc.split("/")[1], job, int(nk)))
    if len(rows) != 55:
        die(f"wave-1 manifest has {len(rows)} rows, expected 55")
    return rows


def census(rows):
    """Split wave-1 rows into converged relax / unconverged relax / scf, from
    the decks and .out markers themselves (then assert vs the record)."""
    relax, scf = [], []
    for metal, job, nk in rows:
        deck = read(os.path.join(S3, metal, job + ".in"))
        m = re.search(r"^\s*calculation\s*=\s*'(\w+)'", deck, re.M)
        {"relax": relax, "scf": scf}[m.group(1)].append((metal, job, nk))
    if (len(relax), len(scf)) != (46, 9):
        die(f"wave-1 partition {len(relax)} relax / {len(scf)} scf != 46/9")
    conv, unconv, retry = [], set(), set()
    for metal, job, nk in relax:
        out_p = os.path.join(S3, metal, job + ".out")
        out = read(out_p)
        ok = ("bfgs converged" in out
              and "End of BFGS Geometry Optimization" in out
              and out.count("Begin final coordinates") == 1)
        if not ok:
            unconv.add((metal, job))
            continue
        beta = float(re.search(r"mixing beta\s*=\s*([\d.]+)", out).group(1))
        if abs(beta - 0.15) < 1e-9:
            retry.add((metal, job))
        elif abs(beta - 0.30) > 1e-9:
            die(f"{rel(out_p)}: unexpected mixing beta {beta}")
        conv.append((metal, job, nk))
    if unconv != EXPECTED_NOT_CONVERGED:
        die(f"derived NOT_CONVERGED set differs from record: {sorted(unconv)}")
    if retry != EXPECTED_RETRY_BH:
        die(f"derived retry-beta set differs from record: {sorted(retry)}")
    if len(conv) != 37:
        die(f"{len(conv)} converged relax parents, expected 37")
    return conv, retry


def build_children(conv, retry):
    made = []
    for metal, job, nk in conv:
        plain = os.path.join(S3, metal, job + ".in")
        src = (os.path.join(S3, metal, job + ".retry_bh.in")
               if (metal, job) in retry else plain)
        if not os.path.exists(src):
            die(f"{rel(src)}: converged-deck source missing")
        out_p = os.path.join(S3, metal, job + ".out")
        src_txt = read(src)
        if FORBIDDEN_RESTART.search(src_txt):
            die(f"{rel(src)}: parent deck carries a restart key")
        src_deck = parse_input_deck(src)
        rows = selftest_formatter(src_txt, src)

        pos, prov = parse_final_coordinates(out_p)
        if pos is None or prov != "final":
            die(f"{rel(out_p)}: geometry provenance {prov!r}, need 'final'")
        if len(pos) != len(rows):
            die(f"{rel(out_p)}: {len(pos)} final atoms != {len(rows)} deck atoms")
        if [p[0] for p in pos] != [r[0] for r in rows]:
            die(f"{rel(out_p)}: species order differs from deck")

        child = job + "__g1"
        new_rows = [(sp, f"{x:.8f}", f"{y:.8f}", f"{z:.8f}", r[4])
                    for (sp, x, y, z), r in zip(pos, rows)]
        txt = swap_scalar_line(src_txt, src, "calculation", "relax", "scf")
        txt = swap_scalar_line(txt, src, "prefix", job, child)
        txt = swap_positions(txt, src, new_rows)

        dst = os.path.join(S3, metal, child + ".in")
        write(dst, txt)

        kinds = [classify_diff(x, y, dst) for _, x, y in
                 diff_lines(src_txt, read(dst), dst)]
        if kinds.count("calculation") != 1 or kinds.count("prefix") != 1 \
           or set(kinds) - {"calculation", "prefix", "coords"}:
            die(f"{rel(dst)}: diff vs parent deck is not exactly "
                f"{{calculation, prefix, coordinates}}: {kinds}")
        namelist_sanity(dst, child, src_deck)
        EMITTED.append((rel(dst), "g1_child", nk,
                        f"parent {metal}/{job} ({'retry_bh' if (metal, job) in retry else 'plain'})"))
        made.append((metal, child, nk))
        print(f"EMIT {rel(dst):58s} g1_child   nk={nk:2d}  parent={metal}/{job}")
    return made


# ------------------------------------------------------------ hess SCFs (B) ---

def hess_nk():
    out = read(os.path.join(CR_HESS, BANKED_HESS_STEM + "ref.out"))
    m = re.search(r"number of k points=\s*(\d+)", out)
    nkpt = int(m.group(1))
    nk = 16 if nkpt >= 16 else 8
    if nk > nkpt or NP % nk:
        die(f"hess nk={nk} illegal for {nkpt} k-points at NP={NP}")
    return nk, nkpt


def build_hess():
    man = json.load(open(os.path.join(CR_HESS, "hess_manifest.json")))
    jobs = man["jobs"]
    if len(jobs) != 19 or jobs[0]["kind"] != "reference":
        die("banked hess_manifest.json: expected reference + 18 displacements")
    if abs(man["delta_nominal_angstrom"] - float(DELTA)) > 1e-12:
        die("banked delta_nominal differs from 0.01 A")

    esc_in = os.path.join(S3, "Cr", HESS_BASE_JOB + ".in")
    esc_out = os.path.join(S3, "Cr", HESS_BASE_JOB + ".out")
    esc_txt = read(esc_in)
    esc_rows = selftest_formatter(esc_txt, esc_in)
    out = read(esc_out)
    if "bfgs converged" not in out or "End of BFGS Geometry Optimization" not in out \
       or out.count("Begin final coordinates") != 1:
        die(f"{rel(esc_out)}: escape relax not converged")
    pos, prov = parse_final_coordinates(esc_out)
    if pos is None or prov != "final":
        die(f"{rel(esc_out)}: geometry provenance {prov!r}")
    if len(pos) != len(esc_rows) or [p[0] for p in pos] != [r[0] for r in esc_rows]:
        die(f"{rel(esc_out)}: species/count mismatch vs escape deck")

    ref_src = os.path.join(CR_HESS, BANKED_HESS_STEM + "ref.in")
    ref_txt = read(ref_src)
    banked_rows = selftest_formatter(ref_txt, ref_src)
    # the banked instrument, asserted (guards against a wrong clone source)
    for pat, what in ((r"^\s*conv_thr\s*=\s*1\.0d-10\s*$", "conv_thr 1.0d-10"),
                      (r"^\s*electron_maxstep\s*=\s*120\s*$", "electron_maxstep 120"),
                      (r"^\s*nosym\s*=\s*\.true\.\s*$", "nosym"),
                      (r"^\s*noinv\s*=\s*\.true\.\s*$", "noinv"),
                      (r"^K_POINTS automatic\n\s*4 4 1 0 0 0$", "K_POINTS 4 4 1")):
        if not re.search(pat, ref_txt, re.M):
            die(f"{rel(ref_src)}: banked hess instrument missing {what}")
    if len(banked_rows) != len(esc_rows):
        die("banked hess ref vs escape deck: atom count mismatch")
    for br, er in zip(banked_rows, esc_rows):
        if br[0] != er[0] or br[4] != er[4]:
            die("banked hess ref vs escape deck: species/if_pos order differs")
    esc_cell = re.search(r"CELL_PARAMETERS angstrom\n(?:.+\n){3}", esc_txt).group(0)
    ref_cell = re.search(r"CELL_PARAMETERS angstrom\n(?:.+\n){3}", ref_txt).group(0)
    if esc_cell != ref_cell:
        die("banked hess cell != escape cell (geometry not transplantable)")

    nk, nkpt = hess_nk()
    ref_strs = [(sp, f"{x:.8f}", f"{y:.8f}", f"{z:.8f}", r[4])
                for (sp, x, y, z), r in zip(pos, esc_rows)]
    ax_i = {"x": 1, "y": 2, "z": 3}
    made, esc_ref_txt = [], None
    for rec in jobs:
        tag = rec["job"].split("__hess_")[1]
        new_job = HESS_JOB_STEM + tag
        src = os.path.join(CR_HESS, BANKED_HESS_STEM + tag + ".in")
        src_txt = read(src)
        selftest_formatter(src_txt, src)
        if rec["kind"] == "reference":
            rows = list(ref_strs)
        else:
            i, ax, sg = rec["atom_index0"], ax_i[rec["axis"]], rec["sign"]
            r = list(ref_strs[i])
            r[ax] = f"{Decimal(r[ax]) + sg * DELTA:.8f}"
            rows = list(ref_strs)
            rows[i] = tuple(r)
        txt = swap_scalar_line(src_txt, src, "prefix",
                               BANKED_HESS_STEM + tag, new_job)
        txt = swap_positions(txt, src, rows)
        dst = os.path.join(S3, "Cr", new_job + ".in")
        write(dst, txt)
        emitted = read(dst)

        # (i) vs the banked sibling: only prefix + coordinates may differ
        kinds = [classify_diff(x, y, dst) for _, x, y in
                 diff_lines(src_txt, emitted, dst)]
        if kinds.count("prefix") != 1 or set(kinds) - {"prefix", "coords"}:
            die(f"{rel(dst)}: diff vs banked hess sibling is not exactly "
                f"{{prefix, positions}}: {kinds}")
        # (ii) vs the emitted esc ref deck: exactly one atom, one axis, +/-delta
        if rec["kind"] == "reference":
            esc_ref_txt = emitted
        else:
            diffs = [d for d in diff_lines(esc_ref_txt, emitted, dst)]
            coord = [d for d in diffs if classify_diff(d[1], d[2], dst) == "coords"]
            if len(coord) != 1 or len(diffs) != 2:   # prefix line + 1 atom line
                die(f"{rel(dst)}: expected exactly one displaced atom vs esc ref")
            px, py = coord[0][1].split(), coord[0][2].split()
            moved = [k for k in (1, 2, 3) if px[k] != py[k]]
            if moved != [ax_i[rec["axis"]]]:
                die(f"{rel(dst)}: displaced axis mismatch")
            got = Decimal(py[moved[0]]) - Decimal(px[moved[0]])
            if got != rec["sign"] * DELTA:
                die(f"{rel(dst)}: displacement {got} != {rec['sign'] * DELTA}")
            body_start, _ = pos_block_span(emitted, dst)
            atom_line0 = coord[0][0] - emitted[:body_start].count("\n")
            if atom_line0 != rec["atom_index0"]:
                die(f"{rel(dst)}: displaced atom line {atom_line0} != "
                    f"manifest atom_index0 {rec['atom_index0']}")
        namelist_sanity(dst, new_job, parse_input_deck(src))
        EMITTED.append((rel(dst), "hess", nk,
                        f"esc geometry; banked sibling {rec['job']}"))
        made.append(("Cr", new_job, nk))
        print(f"EMIT {rel(dst):58s} hess       nk={nk:2d}  ({nkpt} k banked)")
    return made, nk, nkpt


# --------------------------------------------------------------- manifest ---

HEADER = """\
# S3 wave-2 manifest -- built 2026-08-24 by src/dft/build_s3_wave2.py
# Registration of record: deposited A8, DOI {doi};
#   dispositions docs/54-s3-deck-matrix-2026-08-23.md (SS3 SCF families; the
#   re-Hessian row docs/54:158/:324); __g1 convention docs/43:1575-1592 (A8.3).
# PARENT WAVE (banked): wave-1 Slurm arrays 20097663 / 20097688 / 20101963 /
#   20107835; 46/55 decks converged (37 relax + 9 SCF); 9 rung-iii NOT_CONVERGED
#   gaps stand (A8.4 ladder): Co ref__2x1v, Co s0_OH__1x1_off,
#   Co s0_O/s0_OH/s0_OOH__2x1v_mir, Co s0_OH/s0_OOH__2x1v_off,
#   Ni s0_OOH__2x1v_mir, Ni s0_OOH__2x1v_off.
# WAVE-2 = 37 __g1 children (fresh-density fixed-geometry SCF at each converged
#   wave-1 relax parent's final coords; converged parent deck cloned verbatim
#   incl. symmetry flags -- the .retry_bh.in beta-0.15 deck for Co/Ni
#   s0_O__1x1_off, the plain .in otherwise) + 19 Cr 1C re-Hessian SCFs at the
#   escaped geometry (1e-10 class, nosym+noinv, docs/54:158).
# A8.3 THRESHOLD: a __g1 child that lands > 1 meV ABOVE its parent is REFUSED
#   and re-run from the parent's converged density; a second failure ->
#   MULTISTABLE, and neither number is banked (docs/43:1589-1592).
# DEFERRED: the 2 Cr_lit3 A8.3 refused-child re-runs (docs/54:324 row --
#   oosh__1x1_off_magp, s0_OOH__1x1_yaw90_magm) are NOT in this wave: they
#   restart from the PARENT'S RETAINED DENSITY and wait on the
#   density-retention runner (separate piece).
# EXCLUDE=a024 -- node a024 OOM-killed 11/12 of its wave-1 tasks (docs/45:91);
#   submit with ExcNodeList=a024.
# nk per row: children INHERIT the parent's wave-1 row nk; hess rows nk {hnk}
#   (banked hess ref prints {hkpt} k; {np} % {hnk} == 0).
# NP=128 NCONC=1
"""


def write_manifest(children, hess, hnk, hkpt):
    rows = [f"s3/{m} {j} .in {nk}" for m, j, nk in children + hess]
    if len(rows) != 56 or len(rows) != len(EMITTED):
        die(f"{len(rows)} manifest rows vs {len(EMITTED)} emitted decks; need 56")
    write(WAVE2_MANIFEST,
          HEADER.format(doi=DOI, hnk=hnk, hkpt=hkpt, np=NP)
          + "\n".join(rows) + "\n")
    print(f"WROTE {rel(WAVE2_MANIFEST)}: {len(rows)} rows")


def main():
    conv, retry = census(load_wave1_rows())
    children = build_children(conv, retry)
    hess, hnk, hkpt = build_hess()
    write_manifest(children, hess, hnk, hkpt)
    n16 = sum(1 for _, _, nk in children if nk == 16)
    print(f"DONE: {len(children)} __g1 children (nk16 x {n16}, nk8 x "
          f"{len(children) - n16}) + {len(hess)} hess SCFs (nk{hnk}) = "
          f"{len(EMITTED)} decks")


if __name__ == "__main__":
    main()
