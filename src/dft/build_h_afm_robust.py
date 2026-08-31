#!/usr/bin/env python3
"""RU-AFM-PROBE ROBUSTNESS ARM: the 6 AFM-relaxed-geometry SCFs of docs/43 A11.R3.

LICENSED 2026-08-31 by the robustness sentence of docs/43 A11.R3 [RU AFM PROBE
2026-08-31: RUNS, both U endpoints]: "Robustness arm, its own line: +6 SCFs on
the AFM-relaxed geometries (runs/s0/h_afm_relax finals): NM u000 (2), AFM u900
(2), NM u900 (2); the AFM u000 legs are the banked __g1 fresh-density children"
(elections docs/66 SS2 row 15). The arm inherits item 10's no-A7.3-score limit
verbatim; recorded either way. Submission additionally waits on the A11.R5
deposit (the deposit precedes any deck this amendment licenses).

READ FIRST: src/dft/build_ru_afm_probe.py (the primary arm's builder -- this
builder imports its helpers and inherits its trap analysis: the two-label
HUBBARD card, the read-it-from-the-deck rule, the byte-minimal diff idiom) and
src/dft/build_a0spin_s1.py (the S1-a..S1-g guard style, the --sandbox
determinism rebuild, and the collision/overwrite semantics replicated here).

WHAT THE 6 SCFs ARE (the A11.R3 enumeration, not derived)
---------------------------------------------------------
All six run at the AFM-RELAXED geometries: the final BFGS coordinates of
runs/s0/h_afm_relax/{s0_OH,s0_OOH}__2x1v_off__afm__relax.out, which the banked
__g1 fresh-density children already carry verbatim as fixed-geometry SCF
coordinate strings -- so every child derives from the __g1 .in parents
(byte-minimal), and the strings are asserted against the relax .out finals to
<= 2e-8 A (RG3). Per state {s0_OH, s0_OOH}:

  NM  u000  <state>__2x1v_off__afmgeo__u000       (new compute, 2 decks)
  AFM u900  <state>__2x1v_off__afm__afmgeo__u900  (new compute, 2 decks)
  NM  u900  <state>__2x1v_off__afmgeo__u900       (new compute, 2 decks)

The AFM u000 legs are BANKED, never re-run: the __g1 children (the ELECTED
legs, pre-stated in A11.R3 before any U = 9 result exists):
  runs/s0/h_afm_relax/{s0_OH,s0_OOH}__2x1v_off__afm__relax__g1.out
  -3304.20359479 / -3345.68944522 Ry, totmag/absmag -1.25/3.76 and -0.15/4.97.

Deliverable: D_M|afmgeo = dc_M(9.0)|afmgeo - dc_M(0)|afmgeo with dc_M(U) =
[E_AFM(OOH,U)-E_AFM(OH,U)] - [E_NM(OOH,U)-E_NM(OH,U)], all four legs of each
dc_M at the SAME AFM-relaxed coordinates. Context pins, re-derived at build
time (RP4): relaxed-AFM-vs-NM-relaxed Dc_M(0) = -32.12 meV via the g1
children, -32.51 meV via the relax finals (docs/43 A11.R3); the arm's NM u000
legs complete the fixed-AFM-geometry dc_M(0)|afmgeo no banked pair measures.

PARENTAGE -- each child from the committed parent of its OWN magnetic class
---------------------------------------------------------------------------
AFM u900 <- runs/s0/h_afm_relax/<state>__2x1v_off__afm__relax__g1.in (already
    calculation='scf' at the AFM-relaxed coords). diff = prefix line + an
    appended 3-line HUBBARD card, NOTHING else. The card carries BOTH
    'U Ru1-4d 9.0000' AND 'U Ru2-4d 9.0000', read from THAT deck's own
    ATOMIC_SPECIES (the primary arm's trap: QE raises no error for a U-less
    species, so a one-label card would silently leave the other sublattice at
    U = 0 -- a spin-U cross-contamination no output grep would catch).
NM u000 <- runs/probe/Ru_cellsym/<state>__2x1v_off.in (a RELAX deck; the NM
    namelist shape of record -- single Ru label, nspin unset, i.e. the AFM
    sublattice split stripped back to the NM class). diff = calculation
    'relax'->'scf' + prefix line + moving-atom coordinate fields replaced by
    the __g1 deck's coordinate STRINGS. Frozen '0 0 0' rows are asserted
    string-identical between the two parents and kept byte-identical. NO
    HUBBARD card (this IS the u000 leg). Parent max_seconds kept verbatim
    (inert runner machinery for an SCF; primary-arm precedent).
NM u900 = the NM u000 deck + prefix + an appended 2-line HUBBARD card
    'U Ru-4d 9.0000' (single label, read from the deck; syntax precedent
    runs/a0/main/Ru/s0_OH__u900.in); asserted byte-identical to its u000
    sibling everywhere else (RM5).

Stems carry __afmgeo__ so no stem/prefix collides with the primary arm
(runs/s0/h_afm_probe: {s0_OH,s0_OOH}__2x1v_off{,__afm}__u900) -- the runner
rm -rf's dens/${prefix}.save, so a colliding prefix would wipe a banked
density (RY1/RS1).

BUILD-TIME ASSERTIONS (all fatal; the builder refuses, never warns)
-------------------------------------------------------------------
RL1  docs/43 carries the licence: the [RU AFM PROBE 2026-08-31] line, the
     "+6 SCFs on the AFM-relaxed geometries" robustness sentence, the
     inherits-the-limit sentence, and "nk pre-stated: 4"
RS1  the plan is exactly the registered 6 (2 NM u000 + 2 AFM u900 + 2 NM
     u900); every stem carries __afmgeo__; no planned stem equals a primary-
     arm stem; no <stem>.out exists anywhere under runs/ (banked evidence);
     no <stem>.in exists anywhere under runs/ except, in a --sandbox rebuild,
     this builder's own pass-1 products; nothing at an output path is ever
     overwritten (deck or committed manifest)                     [S1-c idiom]
RP1  parent .in/.out exist        RP2  parent .in byte-identical to its
     committed blob at HEAD (md5 recorded in the manifest)
RP3  parent .out scoreable -- g1: gate-(h) SCF recipe ('convergence has been
     achieved' >= 1, zero 'convergence NOT achieved', final '^!', JOB DONE,
     16 k printed, 'No symmetry found'); relax + NM cellsym: zero
     'convergence NOT achieved', 'End of BFGS Geometry Optimization',
     JOB DONE, exactly one 'Final energy'
RP4  energies equal the BANKED pins (g1, relax finals, NM finals); g1
     totmag/absmag equal the banked reference moments; Dc_M(0) re-derives to
     -32.12 meV (g1) and -32.51 meV (relax finals) within 0.05
RG1  g1 parent treatment: calculation 'scf', nspin 2, nosym/noinv .true.,
     no HUBBARD, ntyp 4, K_POINTS 'automatic / 4 4 1 0 0 0' as final card
RG2  AFM sublattice pair FOUND from the deck (two labels, one element), seeds
     equal and antiparallel at their own indices, all other species 0.0; card
     label set == the deck's own Ru-pseudo label set == {Ru1, Ru2}
RG3  g1 deck coordinates == the relax .out final BFGS coordinates to <= 2e-8 A
     per field, row count == nat, label sequence and flags match (the arm
     runs on the RELAX FINALS; the g1 strings are proven to BE them)
RG4  AFM diff shape: exactly 1 replaced line (prefix) + exactly 3 appended
     card lines after K_POINTS at EOF; 0 deletions; ATOMIC_POSITIONS and
     K_POINTS byte-identical to the parent
RM1  NM parent treatment: calculation 'relax', NO nspin key, NO
     starting_magnetization, NO HUBBARD, nosym/noinv .true., max_seconds
     present, ntyp 3, same K_POINTS card
RM2  NM card (u900 only) label set == the deck's own Ru-pseudo label set ==
     {Ru}; the u000 child carries NO HUBBARD card
RM3  row alignment NM-parent-vs-g1: counts == nat, base-label mapping, flags
     equal; frozen rows string-identical and kept byte-identical; moving-row
     displacement NM-start-vs-AFM-relaxed < 1.5 A; the row formatter
     reproduces every parent line byte-for-byte before substitution
RM4  NM u000 diff shape: replaced == {calculation, prefix} + moving rows
     where ONLY the three coordinate fields change; 0 appended, 0 deleted;
     K_POINTS unchanged and final; max_seconds carried verbatim
RM5  NM u900 vs its u000 sibling: prefix line + 2 appended card lines,
     byte-identical everywhere else
RX1  the three children of each state agree row-by-row: coordinate strings
     equal AND |dx| <= 2e-8 A numeric, flags equal, base labels correspond;
     CELL_PARAMETERS and K_POINTS blocks string-identical across ALL 6 decks
     and both classes (k-set/symmetry match NM-vs-AFM: 4 4 1 + nosym/noinv
     -> 16 k, as the h_afm family); nosym/noinv .true. in every child
RY1  prefix == filename stem for every child
RY2  children land only under runs/s0/h_afm_robust/, never in a banked tree
RY3  trailing newline preserved, zero CR bytes (LF-only, like every parent)
RA1  every file this builder read (parents, outs, primary-arm decks, primary
     manifest) is md5-swept before and after the build: unchanged on disk
RB1  the manifest carries exactly one '# NP=128 NCONC=1' line, the EXCLUDE
     header + the a120/a200 note, the LICENSED header, one '# md5' line per
     deck, and exactly 6 4-field rows

USAGE
-----
    python src/dft/build_h_afm_robust.py                  # build into the repo
    python src/dft/build_h_afm_robust.py --sandbox DIR    # independent rebuild
                                                          # into DIR/runs/...
                                                          # (determinism check)

Deterministic: no timestamps, no environment reads; two builds must produce
byte-identical decks and manifest (S1-g: prove it by md5-comparing a --sandbox
rebuild against the repo build).
"""
from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import build_ru_afm_probe as P  # helpers + trap analysis; imported, not copied

REPO = P.REPO
G1_DIR = os.path.join(REPO, "runs", "s0", "h_afm_relax")
NM_DIR = os.path.join(REPO, "runs", "probe", "Ru_cellsym")
PROBE_DIR = os.path.join(REPO, "runs", "s0", "h_afm_probe")
RUNS = os.path.join(REPO, "runs")
DOCS43 = os.path.join(REPO, "docs", "43-prereg-week1-factorial.md")
MANIFEST_REL = "runs/s0/m_h_afm_robust.txt"

STATES = ["s0_OH", "s0_OOH"]

#: BANKED pins. Sources: runs/s0/h_afm_relax/*__g1.out last '^!' + last
#: totmag/absmag pair; runs/s0/h_afm_relax/*__relax.out 'Final energy' (also
#: tabled in runs/s0/m_h_afm_g1.txt's comparator block); runs/probe/
#: Ru_cellsym/*.out 'Final energy' (the primary arm's banked NM pins).
BANKED = {
    "s0_OH": dict(nat=38, g1_ry=-3304.20359479, relax_ry=-3304.20358815,
                  nm_ry=-3304.19715356, g1_totmag=-1.25, g1_absmag=3.76),
    "s0_OOH": dict(nat=39, g1_ry=-3345.68944522, relax_ry=-3345.68946738,
                   nm_ry=-3345.68064313, g1_totmag=-0.15, g1_absmag=4.97),
}
DC0_G1_MEV = -32.12     # docs/43 A11.R3: "via the g1 children"
DC0_RELAX_MEV = -32.51  # docs/43 A11.R3: "via the relax finals"

#: The primary arm's four stems (runs/s0/m_h_afm_probe.txt rows) -- no
#: robustness stem may collide with them (RS1).
PRIMARY_STEMS = {
    "s0_OH__2x1v_off__afm__u900", "s0_OOH__2x1v_off__afm__u900",
    "s0_OH__2x1v_off__u900", "s0_OOH__2x1v_off__u900",
}

#: docs/43 A11.R3 licence pins (RL1) -- build refuses on a tree without the
#: adopted amendment text.
LICENCE_PINS = [
    "[RU AFM PROBE 2026-08-31: RUNS, both U endpoints]",
    "+6 SCFs on the AFM-relaxed geometries",
    "The robustness arm inherits item 10's no-A7.3-score limit verbatim.",
    "nk pre-stated: 4",
]

fail = P.fail


def stems_of(state: str) -> dict:
    return {
        "nm_u000": f"{state}__2x1v_off__afmgeo__u000",
        "afm_u900": f"{state}__2x1v_off__afm__afmgeo__u900",
        "nm_u900": f"{state}__2x1v_off__afmgeo__u900",
    }


def read_bytes(path: str) -> bytes:
    with open(path, "rb") as fh:
        return fh.read()


def write_lf(path: str, lines: list[str], tag: str) -> bytes:
    txt = "\n".join(lines)
    raw = txt.encode()
    if not txt.endswith("\n") or "\r" in txt:
        fail("RY3", f"{tag}: newline/CR hygiene violated")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(raw)
    return raw


def last_moments(otxt: str, tag: str) -> tuple[float, float]:
    tm = re.findall(r"total magnetization\s*=\s*(-?\d+\.\d+)", otxt)
    am = re.findall(r"absolute magnetization\s*=\s*(-?\d+\.\d+)", otxt)
    if not tm or not am:
        fail("RP4", f"{tag}: no printed totmag/absmag pair")
    return float(tm[-1]), float(am[-1])


def pin_scf_out(path: str, state: str) -> str:
    """RP3/RP4 for a __g1 fixed-geometry SCF .out (gate-(h) recipe)."""
    otxt = open(path, errors="replace").read()
    if "convergence NOT achieved" in otxt:
        fail("RP3", f"{state} g1: .out reports a convergence failure")
    if "convergence has been achieved" not in otxt:
        fail("RP3", f"{state} g1: .out never reports convergence")
    if "JOB DONE" not in otxt:
        fail("RP3", f"{state} g1: no JOB DONE")
    bang = re.findall(r"^!\s*total energy\s*=\s*(-\d+\.\d+)\s*Ry", otxt, re.M)
    if not bang:
        fail("RP3", f"{state} g1: no '^!' final energy line")
    km = re.findall(r"number of k points\s*=\s*(\d+)", otxt)
    if not km or int(km[-1]) != 16:
        fail("RP3", f"{state} g1: printed k count {km and km[-1]!r} != 16")
    if "No symmetry found" not in otxt:
        fail("RP3", f"{state} g1: 'No symmetry found' absent")
    e = float(bang[-1])
    if f"{round(e, 8):.8f}" != f"{BANKED[state]['g1_ry']:.8f}":
        fail("RP4", f"{state} g1: energy {e!r} != banked {BANKED[state]['g1_ry']!r}")
    tm, am = last_moments(otxt, f"{state} g1")
    if abs(tm - BANKED[state]["g1_totmag"]) > 0.005 or \
       abs(am - BANKED[state]["g1_absmag"]) > 0.005:
        fail("RP4", f"{state} g1: moments {tm}/{am} != banked "
             f"{BANKED[state]['g1_totmag']}/{BANKED[state]['g1_absmag']}")
    return otxt


def pin_relax_out(path: str, state: str, key: str, tag: str) -> str:
    """RP3/RP4 for a BFGS relax .out (relax finals + NM cellsym parents)."""
    otxt = open(path, errors="replace").read()
    if "convergence NOT achieved" in otxt:
        fail("RP3", f"{tag}: .out reports a convergence failure")
    if "End of BFGS Geometry Optimization" not in otxt:
        fail("RP3", f"{tag}: BFGS never converged")
    if "JOB DONE" not in otxt:
        fail("RP3", f"{tag}: no JOB DONE")
    fe = re.findall(r"Final energy\s*=\s*(-\d+\.\d+)\s*Ry", otxt)
    if len(fe) != 1:
        fail("RP3", f"{tag}: {len(fe)} 'Final energy' lines, expected exactly 1")
    e = float(fe[0])
    if f"{round(e, 8):.8f}" != f"{BANKED[state][key]:.8f}":
        fail("RP4", f"{tag}: energy {e!r} != banked {BANKED[state][key]!r}")
    return otxt


def pin_parent_in(path: str) -> bytes:
    """RP1/RP2: parent .in exists and is byte-identical to its HEAD blob."""
    if not os.path.exists(path):
        fail("RP1", f"parent missing: {path}")
    raw = read_bytes(path)
    rel = os.path.relpath(path, REPO).replace(os.sep, "/")
    blob = P.committed_blob(rel)
    if blob is None:
        fail("RP2", f"{rel}: parent .in is not committed at HEAD")
    if P.md5_bytes(blob) != P.md5_bytes(raw):
        fail("RP2", f"{rel}: parent .in differs from its committed blob")
    return raw


def kp_block(lines: list[str], tag: str) -> tuple[int, list[str]]:
    """The K_POINTS card index and its two lines; must be the final card."""
    idx = [i for i, ln in enumerate(lines) if ln.startswith("K_POINTS")]
    if len(idx) != 1:
        fail("RG1", f"{tag}: {len(idx)} K_POINTS cards, expected exactly 1")
    kp = idx[0]
    if kp != len(lines) - 2:
        fail("RG1", f"{tag}: K_POINTS is not the final card")
    if lines[kp] != "K_POINTS automatic" or lines[kp + 1].split() != \
            ["4", "4", "1", "0", "0", "0"]:
        fail("RG1", f"{tag}: K_POINTS block is not 'automatic / 4 4 1 0 0 0'")
    return kp, [lines[kp], lines[kp + 1]]


# ------------------------------------------------------------- AFM children ---

def build_afm(state: str, out_dir: str, g1_lines: list[str], g1_txt: str,
              new_stem: str) -> dict:
    stem = f"{state}__2x1v_off__afm__relax__g1"
    body_lines = g1_lines[:-1]

    # RG1 -- treatment
    if not re.search(r"^\s*calculation\s*=\s*'scf'", g1_txt, re.M):
        fail("RG1", f"{stem}: parent is not calculation='scf'")
    if not re.search(r"^\s*nspin\s*=\s*2", g1_txt, re.M):
        fail("RG1", f"{stem}: nspin is not 2")
    if "HUBBARD" in g1_txt:
        fail("RG1", f"{stem}: parent already carries a HUBBARD card")
    P.check_flags(g1_txt, ["nosym", "noinv"], stem, "RG1")
    ntyp = re.search(r"^\s*ntyp\s*=\s*(\d+)", g1_txt, re.M)
    if not ntyp or int(ntyp.group(1)) != 4:
        fail("RG1", f"{stem}: ntyp != 4")
    kp_block(body_lines, stem)

    # RG2 -- the pair and its seeds, at indices read from THIS deck
    species = P.species_block(g1_txt)
    if not species:
        fail("RG2", f"{stem}: no ATOMIC_SPECIES block")
    ru1, ru2 = P.find_sublattice_pair(species, stem)
    idx = {label: i + 1 for i, (label, _m, _p) in enumerate(species)}
    mags = {int(m.group(1)): float(m.group(2)) for m in re.finditer(
        r"starting_magnetization\((\d+)\)\s*=\s*([-\d.eE+]+)", g1_txt)}
    if sorted(mags) != list(range(1, len(species) + 1)):
        fail("RG2", f"{stem}: starting_magnetization indices {sorted(mags)} "
             f"!= 1..{len(species)}")
    s1, s2 = mags[idx[ru1]], mags[idx[ru2]]
    if s1 <= 0 or s2 >= 0 or abs(abs(s1) - abs(s2)) > 1e-12:
        fail("RG2", f"{stem}: {ru1}/{ru2} seeds {s1}/{s2} not equal+antiparallel")
    for label in {s[0] for s in species} - {ru1, ru2}:
        if mags[idx[label]] != 0.0:
            fail("RG2", f"{stem}: non-metal {label} carries seed {mags[idx[label]]}")
    card = P.hubbard_card(species, stem)
    if set(card[1:]) != {f"U {ru1}-{P.MANIFOLD} {P.U_STR}",
                        f"U {ru2}-{P.MANIFOLD} {P.U_STR}"}:
        fail("RG2", f"{stem}: card {card[1:]} does not cover {ru1}/{ru2}")

    # ---- the transformation: prefix line + appended card, nothing else
    body, prefix_changed = [], 0
    for ln in body_lines:
        if re.match(r"^\s*prefix\s*=", ln):
            nl = ln.replace(f"'{stem}'", f"'{new_stem}'")
            if nl == ln:
                fail("RG4", f"{stem}: prefix replacement failed on {ln!r}")
            body.append(nl)
            prefix_changed += 1
        else:
            body.append(ln)
    child_lines = body + card + [""]

    # RG4 -- diff shape
    if prefix_changed != 1:
        fail("RG4", f"{stem}: {prefix_changed} prefix lines changed, expected 1")
    diffs = [i for i, (a, b) in enumerate(zip(body_lines, body)) if a != b]
    if len(diffs) != 1 or not re.match(r"^\s*prefix\s*=", body_lines[diffs[0]]):
        fail("RG4", f"{stem}: replaced lines {diffs} are not exactly the prefix")
    kp, _kb = kp_block(body_lines, stem)
    if body[kp] != body_lines[kp] or body[kp + 1] != body_lines[kp + 1]:
        fail("RG4", f"{stem}: K_POINTS card changed")
    if child_lines[len(body):len(body) + 3] != card or child_lines[-1] != "":
        fail("RG4", f"{stem}: card placement/shape wrong at EOF")
    labels = {s[0] for s in species}
    if [r[2] for r in P.deck_rows(child_lines, labels)] != \
       [r[2] for r in P.deck_rows(g1_lines, labels)]:
        fail("RG4", f"{stem}: ATOMIC_POSITIONS not byte-identical to the parent")

    raw = finish_child(out_dir, new_stem, child_lines)
    return dict(stem=new_stem, parent=stem, cls="afm", state=state, card=card,
                md5=P.md5_bytes(raw), rows_changed=0,
                note="none (parent already 'scf')")


# -------------------------------------------------------------- NM children ---

def nm_transform(state: str, nm_lines: list[str], nm_txt: str,
                 g1_rows: list, new_stem: str, ms_val: str) -> tuple[list[str], int]:
    """The shared NM body: calc 'relax'->'scf' + prefix + g1 coordinates."""
    stem = f"{state}__2x1v_off"
    species = P.species_block(nm_txt)
    labels = {s[0] for s in species}
    nm_rows = P.deck_rows(nm_lines, labels)
    nat = BANKED[state]["nat"]
    if not (len(nm_rows) == len(g1_rows) == nat):
        fail("RM3", f"{stem}: row counts nm={len(nm_rows)} g1={len(g1_rows)} "
             f"nat={nat} disagree")

    new_by_index: dict[int, str] = {}
    for (i, p, ln), (_gi, gp, _gl) in zip(nm_rows, g1_rows):
        if len(p) != 7 or len(gp) != 7:
            fail("RM3", f"{stem}: a position row lacks explicit flags: {ln!r}")
        indent = ln[: len(ln) - len(ln.lstrip())]
        if P.row_rebuild(indent, p[0], p[1], p[2], p[3], p[4:7]) != ln:
            fail("RM3", f"{stem}: row formatter does not reproduce {ln!r}")
        if gp[0].rstrip("0123456789") != p[0]:
            fail("RM3", f"{stem}: g1 label {gp[0]} does not map to NM {p[0]}")
        if gp[4:7] != p[4:7]:
            fail("RM3", f"{stem}: flags differ NM {p[4:7]} vs g1 {gp[4:7]}")
        if p[4:7] == ["0", "0", "0"]:
            if gp[1:4] != p[1:4]:
                fail("RM3", f"{stem}: frozen strings differ NM {p[1:4]} vs g1 "
                     f"{gp[1:4]}")
            # frozen row kept byte-identical: no entry in new_by_index
        else:
            d = max(abs(float(p[1 + k]) - float(gp[1 + k])) for k in range(3))
            if d > 1.5:
                fail("RM3", f"{stem}: implausible NM-start-vs-AFM-relaxed "
                     f"displacement {d:.3f} A (atom line {i + 1})")
            nl = P.row_rebuild(indent, p[0], gp[1], gp[2], gp[3], p[4:7])
            if nl != ln:
                new_by_index[i] = nl

    body, calc_changed, prefix_changed = [], 0, 0
    for i, ln in enumerate(nm_lines[:-1]):
        if re.match(r"^\s*calculation\s*=", ln):
            nl = ln.replace("'relax'", "'scf'")
            if nl == ln:
                fail("RM4", f"{stem}: calculation replacement failed")
            body.append(nl)
            calc_changed += 1
        elif re.match(r"^\s*prefix\s*=", ln):
            nl = ln.replace(f"'{stem}'", f"'{new_stem}'")
            if nl == ln:
                fail("RM4", f"{stem}: prefix replacement failed on {ln!r}")
            body.append(nl)
            prefix_changed += 1
        elif i in new_by_index:
            body.append(new_by_index[i])
        else:
            body.append(ln)

    # RM4 -- diff shape of the shared body
    if calc_changed != 1 or prefix_changed != 1:
        fail("RM4", f"{stem}: calculation/prefix changed {calc_changed}/"
             f"{prefix_changed} times")
    row_set = {i for i, _p, _l in nm_rows}
    for i, (a, b) in enumerate(zip(nm_lines[:-1], body)):
        if a == b:
            continue
        if re.match(r"^\s*(calculation|prefix)\s*=", a):
            continue
        if i not in row_set:
            fail("RM4", f"{stem}: unexpected changed line {a!r}")
        pa, pb = a.split(), b.split()
        if pa[0] != pb[0] or pa[4:] != pb[4:]:
            fail("RM4", f"{stem}: a row changed label or flags: {a!r} -> {b!r}")
    kp, _kb = kp_block(nm_lines[:-1], stem)
    if body[kp] != nm_lines[kp] or body[kp + 1] != nm_lines[kp + 1]:
        fail("RM4", f"{stem}: K_POINTS card moved or changed")
    if not re.search(r"^\s*max_seconds\s*=\s*" + re.escape(ms_val) + r"\b",
                     "\n".join(body), re.M):
        fail("RM4", f"{stem}: parent max_seconds was not carried verbatim")
    return body, len(new_by_index)


def build_nm_pair(state: str, out_dir: str, nm_raw: bytes,
                  g1_rows: list, stems: dict) -> tuple[dict, dict]:
    stem = f"{state}__2x1v_off"
    nm_lines = P.split_keep(nm_raw, stem)
    nm_txt = nm_raw.decode()

    # RM1 -- treatment
    if not re.search(r"^\s*calculation\s*=\s*'relax'", nm_txt, re.M):
        fail("RM1", f"{stem}: parent is not calculation='relax'")
    if re.search(r"^\s*nspin\s*=", nm_txt, re.M) or \
            "starting_magnetization" in nm_txt:
        fail("RM1", f"{stem}: parent carries spin keys; the NM class runs "
             "nspin unset")
    if "HUBBARD" in nm_txt:
        fail("RM1", f"{stem}: parent already carries a HUBBARD card")
    P.check_flags(nm_txt, ["nosym", "noinv"], stem, "RM1")
    ms = re.search(r"^\s*max_seconds\s*=\s*(\d+)", nm_txt, re.M)
    if not ms:
        fail("RM1", f"{stem}: expected the emitter's max_seconds")
    ntyp = re.search(r"^\s*ntyp\s*=\s*(\d+)", nm_txt, re.M)
    if not ntyp or int(ntyp.group(1)) != 3:
        fail("RM1", f"{stem}: ntyp != 3")
    nat_m = re.search(r"^\s*nat\s*=\s*(\d+)", nm_txt, re.M)
    if not nat_m or int(nat_m.group(1)) != BANKED[state]["nat"]:
        fail("RM1", f"{stem}: nat {nat_m and nat_m.group(1)!r} != banked "
             f"{BANKED[state]['nat']}")

    # RM2 -- the u900 card, read from the deck
    species = P.species_block(nm_txt)
    card = P.hubbard_card(species, stem)
    if card[1:] != [f"U Ru-{P.MANIFOLD} {P.U_STR}"]:
        fail("RM2", f"{stem}: NM card is {card[1:]}, expected the single-label "
             "line")

    body000, rows_changed = nm_transform(state, nm_lines, nm_txt, g1_rows,
                                         stems["nm_u000"], ms.group(1))
    body900, rows_changed_900 = nm_transform(state, nm_lines, nm_txt, g1_rows,
                                             stems["nm_u900"], ms.group(1))
    if rows_changed_900 != rows_changed:
        fail("RM5", f"{stem}: sibling bodies moved different row counts")

    child000 = body000 + [""]
    if "HUBBARD" in "\n".join(child000):
        fail("RM2", f"{stem}: the u000 child must carry NO HUBBARD card")
    child900 = body900 + card + [""]

    # RM5 -- the u900 sibling differs from u000 by prefix + card only
    if len(body000) != len(body900):
        fail("RM5", f"{stem}: sibling body lengths differ")
    sib = [i for i, (a, b) in enumerate(zip(body000, body900)) if a != b]
    if len(sib) != 1 or not re.match(r"^\s*prefix\s*=", body000[sib[0]]):
        fail("RM5", f"{stem}: sibling diff {sib} is not exactly the prefix line")
    if child900[len(body900):len(body900) + 2] != card or child900[-1] != "":
        fail("RM5", f"{stem}: u900 card placement/shape wrong at EOF")

    raw000 = finish_child(out_dir, stems["nm_u000"], child000)
    raw900 = finish_child(out_dir, stems["nm_u900"], child900)
    d000 = dict(stem=stems["nm_u000"], parent=stem, cls="nm", state=state,
                card=None, md5=P.md5_bytes(raw000), rows_changed=rows_changed,
                note="'relax' -> 'scf'", max_seconds=ms.group(1))
    d900 = dict(stem=stems["nm_u900"], parent=stem, cls="nm", state=state,
                card=card, md5=P.md5_bytes(raw900), rows_changed=rows_changed,
                note="'relax' -> 'scf'", max_seconds=ms.group(1))
    return d000, d900


def finish_child(out_dir: str, new_stem: str, child_lines: list[str]) -> bytes:
    txt = "\n".join(child_lines)
    pm = re.search(r"^\s*prefix\s*=\s*'([^']+)'", txt, re.M)
    if not pm or pm.group(1) != new_stem:
        fail("RY1", f"{new_stem}: prefix {pm and pm.group(1)!r} != stem")
    dest = os.path.join(out_dir, new_stem + ".in")
    norm = dest.replace("\\", "/")
    if not norm.endswith(f"runs/s0/h_afm_robust/{new_stem}.in"):
        fail("RY2", f"child outside runs/s0/h_afm_robust: {dest}")
    for banked in (G1_DIR, NM_DIR, PROBE_DIR):
        if os.path.commonpath([os.path.abspath(dest),
                               os.path.abspath(banked)]) == os.path.abspath(banked):
            fail("RY2", f"{new_stem}: child would land inside a banked tree")
    if os.path.exists(dest):
        fail("RS1", f"refusing to overwrite existing child {dest}")
    return write_lf(dest, child_lines, new_stem)


# ------------------------------------------------------------- twin checks ---

def x_check(state: str, out_dir: str, stems: dict) -> tuple[list[str], list[str]]:
    """RX1 for one state; returns (CELL block, K_POINTS block) for the
    cross-state identity check in main."""
    decks = {}
    for key, stem in stems.items():
        raw = read_bytes(os.path.join(out_dir, stem + ".in"))
        lines = raw.decode().split("\n")
        labels = {s[0] for s in P.species_block(raw.decode())}
        decks[key] = (lines, P.deck_rows(lines, labels), raw.decode())
    ref_key = "afm_u900"
    ref_rows = decks[ref_key][1]
    for key in ("nm_u000", "nm_u900"):
        rows = decks[key][1]
        if len(rows) != len(ref_rows):
            fail("RX1", f"{state}: {key} row count differs from the AFM twin")
        for (_ai, ap, _al), (_ni, np_, _nl) in zip(ref_rows, rows):
            if ap[0].rstrip("0123456789") != np_[0]:
                fail("RX1", f"{state} {key}: labels {ap[0]} vs {np_[0]} do not "
                     "correspond")
            if ap[1:4] != np_[1:4]:
                fail("RX1", f"{state} {key}: coordinate strings differ "
                     f"{ap[1:4]} vs {np_[1:4]}")
            for k in range(3):
                if abs(float(ap[1 + k]) - float(np_[1 + k])) > 2e-8:
                    fail("RX1", f"{state} {key}: twin coordinates differ "
                         "beyond 2e-8 A")
            if ap[4:7] != np_[4:7]:
                fail("RX1", f"{state} {key}: flags differ {ap[4:7]} vs {np_[4:7]}")
    cells, kps = [], []
    for key in ("afm_u900", "nm_u000", "nm_u900"):
        lines, _rows, txt = decks[key]
        cells.append(P.block_of(lines, "CELL_PARAMETERS", "ATOMIC_POSITIONS"))
        _kp, kb = kp_block(_final_card_lines(lines), stems[key])
        kps.append(kb)
        P.check_flags(txt, ["nosym", "noinv"], stems[key], "RX1")
    if any(c != cells[0] for c in cells):
        fail("RX1", f"{state}: CELL_PARAMETERS blocks differ across twins")
    if any(k != kps[0] for k in kps):
        fail("RX1", f"{state}: K_POINTS blocks differ across twins")
    return cells[0], kps[0]


def _final_card_lines(lines: list[str]) -> list[str]:
    """Deck lines up to and including the K_POINTS mesh line, HUBBARD stripped
    (kp_block wants K_POINTS as the final card of the pre-card body)."""
    out = list(lines)
    while out and (out[-1] == "" or out[-1].startswith("HUBBARD") or
                   out[-1].startswith("U ")):
        out.pop()
    return out


# ---------------------------------------------------------------- manifest ---

def write_manifest(path: str, results: list[dict], parent_md5s: list[tuple[str, str]],
                   moments: dict, ms_vals: dict) -> None:
    order = ["nm_u000", "afm_u900", "nm_u900"]
    by = {(r["cls"], r["stem"].endswith("u900"), r["state"]): r for r in results}
    ordered = []
    for key in order:
        for state in STATES:
            ordered.append(by[("afm" if key == "afm_u900" else "nm",
                              key.endswith("u900"), state)])
    L = []
    L.append("# LICENSED 2026-08-31 -- the robustness sentence of [RU AFM PROBE 2026-08-31: RUNS,")
    L.append("# both U endpoints] (docs/43 A11.R3): \"Robustness arm, its own line: +6 SCFs on the")
    L.append("# AFM-relaxed geometries (runs/s0/h_afm_relax finals): NM u000 (2), AFM u900 (2),")
    L.append("# NM u900 (2); the AFM u000 legs are the banked __g1 fresh-density children\"")
    L.append("# (elections docs/66 §2 row 15; deposit per A11.R5 precedes submission). The arm")
    L.append("# inherits the no-A7.3-score limit: \"The robustness arm inherits item 10's")
    L.append("# no-A7.3-score limit verbatim.\" (A11.R3) -- recorded either way; NEVER enters the")
    L.append("# A7.3 score.")
    L.append("# SUBMIT WITH EXCLUDE=a024,a049,a050,a088,a196,a220,a223")
    L.append("# (submit-time list additionally + a120,a200 per [EXCLUDE EXTENDED 2026-08-31], docs/66 §4)")
    L.append("# NP=128 NCONC=1")
    L.append("#")
    L.append("# Ru AFM probe ROBUSTNESS ARM -- 6 decks built by src/dft/build_h_afm_robust.py")
    L.append("# (deterministic; parent and deck md5s below). All six run at the AFM-RELAXED")
    L.append("# geometries: the runs/s0/h_afm_relax/{s0_OH,s0_OOH}__2x1v_off__afm__relax.out final")
    L.append("# BFGS coordinates, carried verbatim as the banked __g1 children's fixed-geometry")
    L.append("# coordinate strings (asserted equal to the relax finals to <= 2e-8 A at build time).")
    L.append("# Stems carry __afmgeo__ so no stem/prefix collides with the primary arm")
    L.append("# (runs/s0/h_afm_probe, m_h_afm_probe.txt; the runner rm -rf's dens/${prefix}.save).")
    L.append("#")
    L.append("# The 6 SCFs (A11.R3 enumeration order = row order below):")
    L.append("#   NM  u000  {s0_OH,s0_OOH}__2x1v_off__afmgeo__u000       completes dc_M(0)|afmgeo")
    L.append("#   AFM u900  {s0_OH,s0_OOH}__2x1v_off__afm__afmgeo__u900")
    L.append("#   NM  u900  {s0_OH,s0_OOH}__2x1v_off__afmgeo__u900")
    L.append("# The AFM u000 legs are BANKED, not re-run -- the __g1 fresh-density children (the")
    L.append("# ELECTED legs, pre-stated in A11.R3 before any U = 9 result exists):")
    L.append("#   runs/s0/h_afm_relax/{s0_OH,s0_OOH}__2x1v_off__afm__relax__g1.out")
    L.append("#   -3304.20359479 / -3345.68944522 Ry")
    L.append("# Deliverable: D_M|afmgeo = dc_M(9.0)|afmgeo - dc_M(0)|afmgeo, dc_M(U) =")
    L.append("#   [E_AFM(OOH,U)-E_AFM(OH,U)] - [E_NM(OOH,U)-E_NM(OH,U)], all four legs of each")
    L.append("#   dc_M at the SAME AFM-relaxed coordinates; slab and gas references cancel in c_M")
    L.append("#   (docs/61 A11.1), so only *OH/*OOH run; s0_O stays excluded by design (measured")
    L.append("#   flat-moment instability, docs/64 s4).")
    L.append("# Context, NEVER a score: relaxed-AFM-vs-NM-relaxed Dc_M(0) = -32.12 meV via the g1")
    L.append("#   children, -32.51 meV via the relax finals (docs/43 A11.R3; both re-derived from")
    L.append("#   the banked pins at build time); the NM u000 legs complete the fixed-AFM-geometry")
    L.append("#   dc_M(0)|afmgeo, which no banked pair yet measures. The arm never enters the")
    L.append("#   A7.3 score on any outcome.")
    L.append("#")
    L.append("# Parentage (each child from the committed parent of its OWN magnetic class):")
    L.append("#   AFM u900 <- runs/s0/h_afm_relax/<state>__2x1v_off__afm__relax__g1.in (already")
    L.append("#     calculation='scf' at the AFM-relaxed coords); diff = prefix line + appended")
    L.append("#     3-line HUBBARD card ONLY: 'U Ru1-4d 9.0000' + 'U Ru2-4d 9.0000', BOTH sublattice")
    L.append("#     labels, read from THAT deck's own ATOMIC_SPECIES (QE raises no error for a")
    L.append("#     U-less species; a one-label card would silently leave the other sublattice at")
    L.append("#     U = 0).")
    L.append("#   NM u000 <- runs/probe/Ru_cellsym/<state>__2x1v_off.in (a RELAX deck; the NM")
    L.append("#     namelist shape of record -- single Ru label, nspin unset: the AFM sublattice")
    L.append("#     split stripped back to the NM class); diff = calculation 'relax'->'scf' +")
    L.append("#     prefix line + moving-atom coordinate fields replaced by the __g1 deck's")
    L.append("#     coordinate STRINGS (frozen '0 0 0' rows asserted string-identical between the")
    L.append("#     two parents and kept byte-identical). NO HUBBARD card -- this IS the u000 leg.")
    L.append(f"#     Parent max_seconds kept verbatim ({ms_vals['s0_OH']} / {ms_vals['s0_OOH']} s --")
    L.append("#     inert runner machinery for an SCF; primary-arm precedent).")
    L.append("#   NM u900 = the NM u000 deck + prefix + appended 2-line HUBBARD card")
    L.append("#     'U Ru-4d 9.0000' (single label, read from the deck; syntax precedent")
    L.append("#     runs/a0/main/Ru/s0_OH__u900.in); asserted byte-identical to its u000 sibling")
    L.append("#     everywhere else.")
    L.append("#   Twin coordinate identity asserted <= 2e-8 A (in fact string-identical) across")
    L.append("#   all three children of each state; CELL_PARAMETERS and K_POINTS string-identical")
    L.append("#   across all 6 decks; k-set/symmetry match NM-vs-AFM: 4 4 1 + nosym/noinv -> 16 k,")
    L.append("#   as the h_afm family (the g1 outs print 16 k / 'No symmetry found').")
    L.append("#")
    L.append("# Scoring at landing: gate-(h) recipe exactly (h_afm_anchor README) -- converged iff")
    L.append("#   'convergence has been achieved' >= 1 AND 'convergence NOT achieved' == 0 AND a")
    L.append("#   final '^!' line exists (success is NEVER 'JOB DONE' alone); E = last '^!';")
    L.append("#   totmag/absmag = last printed pair; meV = dRy * 13605.693122994. Guards (the")
    L.append("#   m_h_afm_probe.txt set, adapted): (1) k-count/symmetry match NM-vs-AFM at each U")
    L.append("#   (expect 16/16, 'No symmetry found' both); (2) E_AFM vs its NM twin recorded")
    L.append("#   either way (no adoption rule exists for this arm); (3) BRANCH CONTINUITY vs the")
    L.append("#   g1 reference moments -- the AFM u900 legs read against the banked __g1 (U = 0)")
    L.append(f"#   totmag/absmag pairs: OH {moments['s0_OH'][0]:.2f}/{moments['s0_OH'][1]:.2f}, "
             f"OOH {moments['s0_OOH'][0]:.2f}/{moments['s0_OOH'][1]:.2f} (extracted from the")
    L.append("#   g1 .outs at build time) -- collapse or sign flip marks D_M|afmgeo")
    L.append("#   branch-conditional.")
    L.append("#")
    L.append("# Parent md5s (each byte-identical to its committed blob at HEAD, asserted):")
    for h, rel in parent_md5s:
        L.append(f"#   {h}  {rel}")
    L.append("# Deck md5s (build is deterministic; double-build verified byte-identical):")
    for r in ordered:
        L.append(f"# md5 {r['md5']} s0/h_afm_robust/{r['stem']}.in")
    L.append("# 4-field rows (dir job suffix nk; trailing fields are fatal in")
    L.append("# anvil/47_submit_a0.sh); nk = 4 pre-stated by A11.R3 for both arms (the")
    L.append("# h_afm_anchor README runner note: 4 4 1 + nosym/noinv -> 16 k >= 12; NP an exact")
    L.append("# multiple of 4).")
    for r in ordered:
        L.append(f"s0/h_afm_robust {r['stem']} .in 4")

    # RB1 -- manifest self-checks before writing
    if sum(1 for ln in L if ln == "# NP=128 NCONC=1") != 1:
        fail("RB1", "manifest must carry exactly one '# NP=128 NCONC=1' line")
    if sum(1 for ln in L if ln.startswith("# SUBMIT WITH EXCLUDE=")) != 1:
        fail("RB1", "manifest must carry the EXCLUDE header exactly once")
    if "a120,a200" not in "\n".join(L):
        fail("RB1", "manifest must carry the a120/a200 submit-time note")
    if sum(1 for ln in L if ln.startswith("# md5 ")) != 6:
        fail("RB1", "manifest must carry exactly 6 '# md5' deck lines")
    rows = [ln for ln in L if not ln.startswith("#") and ln.strip()]
    if len(rows) != 6 or any(len(ln.split()) != 4 for ln in rows):
        fail("RB1", "manifest must carry exactly 6 4-field rows")
    write_lf(path, L + [""], "manifest")


# -------------------------------------------------------------------- main ---

def main(argv: list[str]) -> int:
    out_root = REPO
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--sandbox":
            if i + 1 >= len(argv):
                fail("RS1", "--sandbox needs a directory")
            out_root = os.path.abspath(argv[i + 1])
            i += 2
            continue
        fail("RS1", f"unsupported argument {a!r} -- this builder builds exactly "
             "the registered 6-deck robustness arm; only --sandbox <dir> is "
             "accepted")
    sandbox = os.path.normcase(out_root) != os.path.normcase(REPO)
    out_dir = os.path.join(out_root, "runs", "s0", "h_afm_robust")
    manifest_path = os.path.join(out_root, *MANIFEST_REL.split("/"))

    print("RU-AFM-PROBE ROBUSTNESS ARM -- 6 decks (docs/43 A11.R3; docs/66 "
          "SS2 row 15). Inherits the no-A7.3-score limit.")
    if sandbox:
        print(f"SANDBOX rebuild into {out_root} (parents/evidence still read "
              "from the repo)")

    # RL1 -- the licence text must exist on this tree (docs/43 hard-wraps its
    # prose, so pins are matched against whitespace-normalized text)
    d43 = re.sub(r"\s+", " ",
                 open(DOCS43, encoding="utf-8", errors="replace").read())
    for pin in LICENCE_PINS:
        if pin not in d43:
            fail("RL1", f"docs/43 does not carry the licence pin {pin!r} -- "
                 "refusing to build on a tree without the adopted A11 text")
    print("  RL1 docs/43 carries the A11.R3 robustness licence (4 pins)")

    # RS1 -- the registered plan, stem hygiene, repo-wide collision sweep
    plan = {state: stems_of(state) for state in STATES}
    all_stems = [s for st in STATES for s in plan[st].values()]
    if len(all_stems) != 6 or len(set(all_stems)) != 6:
        fail("RS1", f"plan drift: {len(all_stems)} stems, registered count is 6")
    repo_files: dict[str, list[str]] = {}
    for root, _dirs, files in os.walk(RUNS):
        for f in files:
            repo_files.setdefault(f, []).append(
                os.path.relpath(os.path.join(root, f), REPO).replace(os.sep, "/"))
    for stem in all_stems:
        if "__afmgeo__" not in stem:
            fail("RS1", f"stem {stem} does not carry __afmgeo__")
        if stem in PRIMARY_STEMS:
            fail("RS1", f"stem {stem} collides with the primary arm")
        if stem + ".out" in repo_files:
            fail("RS1", f"stem {stem} collides with banked evidence "
                 f"{repo_files[stem + '.out']}")
        if stem + ".in" in repo_files:
            hits = repo_files[stem + ".in"]
            own = [h for h in hits if h != f"runs/s0/h_afm_robust/{stem}.in"]
            if own or not sandbox:
                fail("RS1", f"stem {stem} collides with existing deck(s) {hits}"
                     + ("" if sandbox else " (a repo .in is tolerated only in "
                        "a --sandbox rebuild)"))
    if P.committed_blob(MANIFEST_REL) is not None and not sandbox:
        fail("RS1", f"{MANIFEST_REL} is committed at HEAD -- banked manifests "
             "are never overwritten")
    for stem in all_stems:
        for ext in (".in", ".out"):
            c = os.path.join(out_dir, stem + ext)
            if os.path.exists(c):
                fail("RS1", f"refusing to overwrite existing child {c}")
    print("  RS1 plan is the registered 6; no collision anywhere under runs/")

    # RA1 snapshot -- every file this build reads
    read_set = []
    for state in STATES:
        read_set += [
            os.path.join(G1_DIR, f"{state}__2x1v_off__afm__relax__g1.in"),
            os.path.join(G1_DIR, f"{state}__2x1v_off__afm__relax__g1.out"),
            os.path.join(G1_DIR, f"{state}__2x1v_off__afm__relax.out"),
            os.path.join(NM_DIR, f"{state}__2x1v_off.in"),
            os.path.join(NM_DIR, f"{state}__2x1v_off.out"),
        ]
    read_set.append(os.path.join(REPO, "runs", "s0", "m_h_afm_probe.txt"))
    for stem in sorted(PRIMARY_STEMS):
        read_set.append(os.path.join(PROBE_DIR, stem + ".in"))
    snapshot = {p: P.md5_bytes(read_bytes(p)) for p in read_set}

    # ---- parents, pins, and the family-level dc_M(0) re-derivations
    results, parent_md5s, moments, ms_vals = [], [], {}, {}
    g1_e, relax_e, cell_kp = {}, {}, {}
    for state in STATES:
        g1_in = os.path.join(G1_DIR, f"{state}__2x1v_off__afm__relax__g1.in")
        g1_out = os.path.join(G1_DIR, f"{state}__2x1v_off__afm__relax__g1.out")
        relax_out = os.path.join(G1_DIR, f"{state}__2x1v_off__afm__relax.out")
        nm_in = os.path.join(NM_DIR, f"{state}__2x1v_off.in")
        nm_out = os.path.join(NM_DIR, f"{state}__2x1v_off.out")

        g1_raw = pin_parent_in(g1_in)
        nm_raw = pin_parent_in(nm_in)
        if not os.path.exists(g1_out) or not os.path.exists(relax_out) or \
                not os.path.exists(nm_out):
            fail("RP1", f"{state}: a parent .out is missing")
        g1_otxt = pin_scf_out(g1_out, state)
        relax_otxt = pin_relax_out(relax_out, state, "relax_ry",
                                   f"{state} afm-relax")
        pin_relax_out(nm_out, state, "nm_ry", f"{state} nm-cellsym")
        g1_e[state] = BANKED[state]["g1_ry"]
        relax_e[state] = BANKED[state]["relax_ry"]
        moments[state] = last_moments(g1_otxt, f"{state} g1")

        g1_lines = P.split_keep(g1_raw, f"{state} g1")
        g1_txt = g1_raw.decode()
        g1_labels = {s[0] for s in P.species_block(g1_txt)}
        g1_rows = P.deck_rows(g1_lines, g1_labels)

        # RG3 -- the g1 strings ARE the relax finals
        fin = P.final_coordinates(relax_otxt)
        nat = BANKED[state]["nat"]
        if not (len(g1_rows) == len(fin) == nat):
            fail("RG3", f"{state}: row counts g1={len(g1_rows)} out={len(fin)} "
                 f"nat={nat} disagree")
        for (_i, gp, gl), (olab, xyz, oflags) in zip(g1_rows, fin):
            if gp[0] != olab:
                fail("RG3", f"{state}: g1 label {gp[0]} != .out label {olab}")
            if " ".join(gp[4:7]) != oflags:
                fail("RG3", f"{state}: g1 flags {gp[4:7]} != .out flags "
                     f"{oflags!r}")
            for k in range(3):
                if abs(float(gp[1 + k]) - xyz[k]) > 2e-8:
                    fail("RG3", f"{state}: g1 coord {gp[1 + k]} vs relax final "
                         f"{xyz[k]!r} differ beyond 2e-8 A ({gl!r})")
        print(f"  RG3 {state}: g1 coordinates == relax .out final BFGS "
              f"coordinates ({nat} atoms, <= 2e-8 A)")

        stems = plan[state]
        afm = build_afm(state, out_dir, g1_lines, g1_txt, stems["afm_u900"])
        d000, d900 = build_nm_pair(state, out_dir, nm_raw, g1_rows, stems)
        results += [afm, d000, d900]
        ms_vals[state] = d000["max_seconds"]
        cell_kp[state] = x_check(state, out_dir, stems)
        print(f"  RX1 {state}: 3 children coordinate-identical; CELL/K_POINTS "
              "identical; nosym+noinv everywhere")

        parent_md5s.append((P.md5_bytes(g1_raw),
                            f"runs/s0/h_afm_relax/{state}__2x1v_off__afm__relax__g1.in"))
        parent_md5s.append((P.md5_bytes(nm_raw),
                            f"runs/probe/Ru_cellsym/{state}__2x1v_off.in"))

    # RP4 (family level) -- the two A11.R3 Dc_M(0) numbers re-derive
    dc0_g1 = ((g1_e["s0_OOH"] - g1_e["s0_OH"])
              - (BANKED["s0_OOH"]["nm_ry"] - BANKED["s0_OH"]["nm_ry"])) * P.RY_MEV
    dc0_rel = ((relax_e["s0_OOH"] - relax_e["s0_OH"])
               - (BANKED["s0_OOH"]["nm_ry"] - BANKED["s0_OH"]["nm_ry"])) * P.RY_MEV
    if abs(dc0_g1 - DC0_G1_MEV) > 0.05:
        fail("RP4", f"g1 pins give Dc_M(0) = {dc0_g1:.2f} meV, not {DC0_G1_MEV}")
    if abs(dc0_rel - DC0_RELAX_MEV) > 0.05:
        fail("RP4", f"relax finals give Dc_M(0) = {dc0_rel:.2f} meV, not "
             f"{DC0_RELAX_MEV}")
    print(f"  RP4 Dc_M(0) re-derived: {dc0_g1:.2f} meV (g1) / {dc0_rel:.2f} "
          "meV (relax finals) -- match A11.R3")

    # RX1 (cross-state): one cell, one k-set across all 6 decks
    if cell_kp["s0_OH"] != cell_kp["s0_OOH"]:
        fail("RX1", "CELL_PARAMETERS/K_POINTS differ between the two states")
    print("  RX1 cross-state: one CELL_PARAMETERS block, one K_POINTS block "
          "across all 6 decks")

    write_manifest(manifest_path, results, parent_md5s, moments, ms_vals)

    # RA1 -- nothing this build read moved on disk
    for p, h in snapshot.items():
        if P.md5_bytes(read_bytes(p)) != h:
            fail("RA1", f"READ FILE ALTERED DURING BUILD: {p}")
    print(f"  RA1 all {len(snapshot)} read files (parents, outs, primary arm) "
          "unchanged on disk")

    print(f"\nBuilt 6 decks under {os.path.relpath(out_dir, out_root)} "
          f"(AFM u000 legs stay BANKED as the __g1 children)\n")
    print(f"{'stem':<42}{'class':>6}{'rows moved':>12}  calc change / card")
    for r in results:
        card = " | ".join(r["card"][1:]) if r["card"] else "NO card (u000)"
        print(f"{r['stem']:<42}{r['cls']:>6}{r['rows_changed']:>12}  "
              f"{r['note']}; {card}")
    print(f"\n{'md5':<34}{'file'}")
    for r in results:
        print(f"{r['md5']:<34}{r['stem']}.in")
    print(f"\nMANIFEST WRITTEN: {MANIFEST_REL} (submission waits on the A11.R5 "
          "deposit; EXCLUDE list + a120,a200 at submit time)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
