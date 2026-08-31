#!/usr/bin/env python3
"""RU-AFM-PROBE: docs/61 decision item 10's "4 SCFs" -- the U = 9.0 endpoint decks.

NOT LICENSED FOR SUBMISSION -- docs/61 decision item 10 (the entrant) is OPEN.
Recorded either way; does not enter the A7.3 score. Both-U-endpoint AFM/NM probe
on the gate-(h) recipe. This builder writes DECKS and a manifest; it stages and
submits nothing. Electing item 10 is the entrant's, and the manifest carries the
open QUESTION-FOR-THE-ENTRANT.

WHAT THE 4 SCFs ARE (derived, not quoted -- see the manifest's question block)
------------------------------------------------------------------------------
{s0_OH, s0_OOH} x {AFM, NM}, fixed-geometry single points at U = 9.0 eV in the
2x1v cell, on the SAME NM-relaxed OFF-arm final BFGS geometries the banked
gate-(h) family used (runs/s0/h_afm_anchor/README.md; P11 limit (ii)). The U = 0
endpoint of D_M is BANKED and is not re-run:

    AFM  runs/s0/h_afm_anchor/{s0_OH,s0_OOH}__2x1v_off__afm.out
         -3304.20342621 / -3345.68881990 Ry
    NM   runs/probe/Ru_cellsym/{s0_OH,s0_OOH}__2x1v_off.out (final BFGS)
         -3304.19715356 / -3345.68064313 Ry
    dc_M(0) = -25.91 meV (docs/63 section 4; re-derived below from these pins)

c_M cancels the slab and every gas reference exactly (docs/61 A11.1), so only
*OH and *OOH enter D_M = dc_M(9.0) - dc_M(0); s0_O is excluded by design (its
AFM SCF is the measured flat-moment instability, docs/64 section 4, trap 27).
No U-carrying 2x1v Ru deck exists anywhere in runs/, so BOTH pairs at U = 9.0
are new compute: differencing a 2x1v AFM@9 against the 1x1 A0 u900 rows would
cross cell, k-set and symmetry treatment (docs/61 A11.7 guard 1).

PARENTAGE -- each child derives from the committed parent of ITS OWN magnetic class
-----------------------------------------------------------------------------------
AFM children <- runs/s0/h_afm_anchor/<state>__2x1v_off__afm.in
    diff = the prefix line + an appended 3-line HUBBARD card. NOTHING else. The
    parent is already calculation = 'scf', so there is NO calculation change.
NM children  <- runs/probe/Ru_cellsym/<state>__2x1v_off.in
    The NM parent is a RELAX deck: its ATOMIC_POSITIONS hold the PRE-relax
    geometry, while the banked NM U = 0 energy is the relaxation's FINAL BFGS
    energy. A prefix+card-only child would therefore be a single point at the
    WRONG geometry. diff = the prefix line + calculation 'relax' -> 'scf' (the
    parent is a relax deck -- stated here and in the manifest) + the moving-atom
    coordinate fields refreshed to the parent's OWN .out final BFGS values + an
    appended 2-line HUBBARD card. Frozen '0 0 0' rows stay byte-identical; the
    refreshed fields reuse the AFM anchor deck's coordinate STRINGS (which are
    that same final geometry, banked) after asserting them against the .out to
    <= 2e-8 A, so the NM/AFM twins are coordinate-identical by construction.
    The parent's max_seconds is kept verbatim (inert runner machinery for an
    SCF; kept to hold the diff minimal, noted in the manifest).

THE TRAP THIS BUILDER EXISTS TO PREVENT
---------------------------------------
QE's HUBBARD card addresses SPECIES LABELS. The AFM decks split Ru into TWO
labels Ru1/Ru2 (identical pseudo and mass, +0.5/-0.5 seeds), so their card MUST
carry BOTH 'U Ru1-4d 9.0000' AND 'U Ru2-4d 9.0000'. QE raises no error for a
U-less species: a single 'U Ru-4d' line would name no species present, and a
one-label card would silently leave the other sublattice at U = 0 -- a spin-U
cross-contamination no output grep would catch. The card is therefore built
FROM EACH DECK'S OWN ATOMIC_SPECIES (build_a0spin.py's read-it-from-the-deck
rule), never from a constant. Card syntax and placement (last card, after
K_POINTS, unindented) follow the committed precedent runs/a0/main/Ru/
s0_OH__u900.in, whose u000-vs-u900 diff is exactly {prefix, appended card}.

BUILD-TIME ASSERTIONS (all fatal; the builder refuses, never warns)
-------------------------------------------------------------------
P1  parent .in and .out exist
P2  parent .in is byte-identical to its committed blob at HEAD
P3  parent .out is scoreable: AFM -- 'convergence has been achieved' >= 1, zero
    'convergence NOT achieved', a final '^!' line, JOB DONE; NM -- zero
    'convergence NOT achieved', 'End of BFGS Geometry Optimization', JOB DONE,
    exactly one 'Final energy' line (success is NEVER 'JOB DONE' alone)
P4  parent energies equal the BANKED U = 0 endpoint values quoted above, and
    dc_M(0) re-derived from them equals -25.91 meV
A1  AFM parent: nspin = 2, nosym/noinv .true., NO HUBBARD card, calculation 'scf'
A2  AFM sublattice pair FOUND from the deck (two labels, one element), seeds
    equal and antiparallel at their own indices, all other species 0.0
A3  AFM card label set == the deck's own Ru-pseudo label set == {Ru1, Ru2}
A4  AFM diff shape: exactly 1 replaced line (prefix) + exactly 3 appended lines
    (the card) immediately after the K_POINTS card at EOF; 0 deletions;
    ATOMIC_POSITIONS and K_POINTS blocks byte-identical to the parent
N1  NM parent: calculation 'relax', NO nspin key, NO starting_magnetization,
    NO HUBBARD, nosym/noinv .true., max_seconds present
N2  NM card label set == the deck's own Ru-pseudo label set == {Ru}
N3  .out final-coordinates block: row count == nat, label sequence == deck's
N4  frozen rows ('0 0 0'): .out displacement < 1e-5 A, parent coordinate
    strings == anchor coordinate strings, row kept byte-identical
N5  every coordinate: |anchor string - .out float| <= 2e-8 A, anchor base label
    and flags match the NM row's, row formatter reproduces the parent line
    byte-for-byte before any substitution
N6  NM diff shape: replaced lines == {calculation, prefix} + moving-coordinate
    rows where ONLY the three coordinate fields change; + exactly 2 appended
    card lines after K_POINTS at EOF; 0 deletions
X1  the NM child and its AFM twin agree row-by-row: coordinate strings, flags,
    base labels; and their CELL_PARAMETERS blocks are string-identical
Y1  prefix == filename stem for every child (the runner rm -rf's
    dens/${prefix}.save; a colliding prefix wipes a banked density)
Y2  children land only under runs/s0/h_afm_probe/, never in a banked tree
Y3  trailing-newline preserved, zero CR bytes (LF-only, like every parent)

USAGE
-----
    python src/dft/build_ru_afm_probe.py

Deterministic: no timestamps, no environment reads; two runs must produce
byte-identical decks and manifest (verify with md5sum).
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ANCHOR_DIR = os.path.join(REPO, "runs", "s0", "h_afm_anchor")
NM_DIR = os.path.join(REPO, "runs", "probe", "Ru_cellsym")
OUT_DIR = os.path.join(REPO, "runs", "s0", "h_afm_probe")
MANIFEST = os.path.join(REPO, "runs", "s0", "m_h_afm_probe.txt")

RU_PSEUDO = "Ru_ONCV_PBE-1.0.oncvpsp.upf"
MANIFOLD = "4d"          # precedent: runs/a0/main/Ru/s0_OH__u900.in 'U Ru-4d 9.0000'
U_STR = "9.0000"         # A7.3's registered U_max endpoint (a0main_readout.json u_hi)
RY_MEV = 13605.693122994

STATES = ["s0_OH", "s0_OOH"]

# The BANKED U = 0 endpoint (P4). Sources: runs/s0/h_afm_anchor/*.out last '^!'
# lines; runs/probe/Ru_cellsym/*.out 'Final energy' (also tabled to these digits
# in h_afm_anchor/README.md); dc_M(0) = -25.91 meV per docs/63 section 4.
BANKED = {
    "s0_OH": dict(nat=38, afm_ry=-3304.20342621, nm_ry=-3304.19715356),
    "s0_OOH": dict(nat=39, afm_ry=-3345.68881990, nm_ry=-3345.68064313),
}
DC0_MEV = -25.91


class BuildRefused(SystemExit):
    """A fatal build-time assertion. Never downgraded to a warning."""


def fail(assertion: str, msg: str) -> None:
    raise BuildRefused(f"REFUSED [{assertion}] {msg}")


# ----------------------------------------------------------------- helpers ---

def committed_blob(relpath: str) -> bytes | None:
    try:
        return subprocess.check_output(
            ["git", "show", f"HEAD:{relpath}"], cwd=REPO, stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        return None


def md5_bytes(b: bytes) -> str:
    return hashlib.md5(b).hexdigest()


def species_block(txt: str) -> list[tuple[str, str, str]]:
    m = re.search(r"ATOMIC_SPECIES\s*\n((?:[ \t]*\S+[ \t]+[\d.]+[ \t]+\S+[ \t]*\n)+)", txt)
    if not m:
        return []
    return [tuple(line.split()) for line in m.group(1).strip().split("\n")]


def deck_rows(lines: list[str], labels: set[str]) -> list[tuple[int, list[str], str]]:
    """(line_index, split_fields, raw_line) per ATOMIC_POSITIONS row, in order."""
    rows, in_pos = [], False
    for i, ln in enumerate(lines):
        if ln.startswith("ATOMIC_POSITIONS"):
            in_pos = True
            continue
        if in_pos:
            p = ln.split()
            if len(p) >= 4 and p[0] in labels:
                rows.append((i, p, ln))
            else:
                in_pos = False
    return rows


def row_rebuild(indent: str, label: str, x: str, y: str, z: str, flags: list[str]) -> str:
    return f"{indent}{label}  {x}  {y}  {z}  {flags[0]} {flags[1]} {flags[2]}"


def final_coordinates(otxt: str) -> list[tuple[str, tuple[float, float, float], str]]:
    """(label, xyz, flags) from the LAST final-coordinates block of a relax .out."""
    if "Begin final coordinates" not in otxt:
        fail("N3", "no `Begin final coordinates` block in the NM parent .out")
    block = otxt.split("Begin final coordinates")[-1].split("End final coordinates")[0]
    rows = []
    for line in block.split("\n"):
        p = line.split()
        if len(p) >= 4 and re.match(r"^[A-Z][a-z]?[0-9]?$", p[0]):
            xyz = (float(p[1]), float(p[2]), float(p[3]))
            flags = " ".join(p[4:7]) if len(p) >= 7 else "1 1 1"
            rows.append((p[0], xyz, flags))
    if not rows:
        fail("N3", "final-coordinates block parsed to zero atoms")
    return rows


def hubbard_card(species: list[tuple[str, str, str]], where: str) -> list[str]:
    """The U card, read from THIS deck's own ATOMIC_SPECIES -- never a constant."""
    ru = [(label, mass) for (label, mass, pseudo) in species if pseudo == RU_PSEUDO]
    if not ru:
        fail("H1", f"{where}: no species uses the Ru pseudo {RU_PSEUDO}")
    for label, mass in ru:
        if label.rstrip("0123456789") != "Ru":
            fail("H1", f"{where}: Ru-pseudo species has non-Ru label {label!r}")
        if mass != "101.070":
            fail("H1", f"{where}: Ru species {label} mass {mass} != 101.070")
    return ["HUBBARD (atomic)"] + [f"U {label}-{MANIFOLD} {U_STR}" for label, _ in ru]


def pin_parent(src_in: str, src_out: str, kind: str, state: str) -> tuple[bytes, str]:
    """P1/P2/P3/P4 for one parent; returns (raw deck bytes, .out text)."""
    for p in (src_in, src_out):
        if not os.path.exists(p):
            fail("P1", f"parent missing: {p}")
    raw = open(src_in, "rb").read()
    rel = os.path.relpath(src_in, REPO).replace(os.sep, "/")
    blob = committed_blob(rel)
    if blob is None:
        fail("P2", f"{rel}: parent .in is not committed at HEAD")
    if md5_bytes(blob) != md5_bytes(raw):
        fail("P2", f"{rel}: parent .in differs from its committed blob")
    otxt = open(src_out, errors="replace").read()
    if "convergence NOT achieved" in otxt:
        fail("P3", f"{state} {kind}: parent .out reports a convergence failure")
    if "JOB DONE" not in otxt:
        fail("P3", f"{state} {kind}: parent .out has no JOB DONE")
    if kind == "afm":
        if "convergence has been achieved" not in otxt:
            fail("P3", f"{state} afm: parent .out never reports convergence")
        bang = re.findall(r"^!\s*total energy\s*=\s*(-\d+\.\d+)\s*Ry", otxt, re.M)
        if not bang:
            fail("P3", f"{state} afm: no '^!' final energy line")
        e = float(bang[-1])
        pin = BANKED[state]["afm_ry"]
    else:
        if "End of BFGS Geometry Optimization" not in otxt:
            fail("P3", f"{state} nm: BFGS never converged")
        fe = re.findall(r"Final energy\s*=\s*(-\d+\.\d+)\s*Ry", otxt)
        if len(fe) != 1:
            fail("P3", f"{state} nm: {len(fe)} 'Final energy' lines, expected exactly 1")
        e = float(fe[0])
        pin = BANKED[state]["nm_ry"]
    if f"{round(e, 8):.8f}" != f"{pin:.8f}":
        fail("P4", f"{state} {kind}: parent energy {e!r} != banked pin {pin!r}")
    return raw, otxt


def check_flags(txt: str, keys_true: list[str], where: str, assertion: str) -> None:
    for key in keys_true:
        if not re.search(rf"^\s*{key}\s*=\s*\.true\.", txt, re.M | re.I):
            fail(assertion, f"{where}: {key} is not .true.")


def find_sublattice_pair(species: list[tuple[str, str, str]], where: str) -> tuple[str, str]:
    cands = []
    for i, (li, mi, pi) in enumerate(species):
        for j in range(i + 1, len(species)):
            lj, mj, pj = species[j]
            if (mi, pi) != (mj, pj):
                continue
            bi, bj = li.rstrip("0123456789"), lj.rstrip("0123456789")
            if bi and bi == bj and li != lj:
                cands.append((li, lj))
    if len(cands) != 1:
        fail("A2", f"{where}: expected exactly one AFM sublattice pair, found {cands}")
    return cands[0]


def split_keep(raw: bytes, where: str) -> list[str]:
    if b"\r" in raw:
        fail("Y3", f"{where}: parent carries CR bytes; the family is LF-only")
    txt = raw.decode()
    if not txt.endswith("\n"):
        fail("Y3", f"{where}: parent does not end with a newline")
    return txt.split("\n")          # last element is ""


def write_child(new_stem: str, child_lines: list[str], where: str) -> tuple[str, bytes]:
    new_txt = "\n".join(child_lines)
    new_raw = new_txt.encode()
    if not new_txt.endswith("\n") or "\r" in new_txt:
        fail("Y3", f"{where}: child newline/CR hygiene violated")
    pm = re.search(r"^\s*prefix\s*=\s*'([^']+)'", new_txt, re.M)
    if not pm or pm.group(1) != new_stem:
        fail("Y1", f"{where}: prefix {pm and pm.group(1)!r} != stem {new_stem!r}")
    dest = os.path.join(OUT_DIR, new_stem + ".in")
    for banked in (ANCHOR_DIR, NM_DIR):
        if os.path.commonpath([os.path.abspath(dest), os.path.abspath(banked)]) == os.path.abspath(banked):
            fail("Y2", f"{where}: child would land inside a banked tree")
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(dest, "wb") as fh:
        fh.write(new_raw)
    return dest, new_raw


def kpoints_index(lines: list[str], where: str) -> int:
    idx = [i for i, ln in enumerate(lines) if ln.startswith("K_POINTS")]
    if len(idx) != 1:
        fail("A4", f"{where}: {len(idx)} K_POINTS cards, expected exactly 1")
    return idx[0]


# ------------------------------------------------------------- AFM children ---

def build_afm(state: str) -> dict:
    stem = f"{state}__2x1v_off__afm"
    new_stem = stem + "__u900"
    raw, _ = pin_parent(os.path.join(ANCHOR_DIR, stem + ".in"),
                        os.path.join(ANCHOR_DIR, stem + ".out"), "afm", state)
    lines = split_keep(raw, stem)
    txt = raw.decode()

    # A1 -- treatment
    if not re.search(r"^\s*calculation\s*=\s*'scf'", txt, re.M):
        fail("A1", f"{stem}: parent is not calculation='scf' -- no calculation change is licensed")
    if not re.search(r"^\s*nspin\s*=\s*2", txt, re.M):
        fail("A1", f"{stem}: nspin is not 2")
    if "HUBBARD" in txt:
        fail("A1", f"{stem}: parent already carries a HUBBARD card")
    check_flags(txt, ["nosym", "noinv"], stem, "A1")

    # A2 -- the pair and its seeds, at indices read from THIS deck
    species = species_block(txt)
    if not species:
        fail("A2", f"{stem}: no ATOMIC_SPECIES block")
    ru1, ru2 = find_sublattice_pair(species, stem)
    idx = {label: i + 1 for i, (label, _m, _p) in enumerate(species)}
    mags = {int(m.group(1)): float(m.group(2))
            for m in re.finditer(r"starting_magnetization\((\d+)\)\s*=\s*([-\d.eE+]+)", txt)}
    if sorted(mags) != list(range(1, len(species) + 1)):
        fail("A2", f"{stem}: starting_magnetization indices {sorted(mags)} != 1..{len(species)}")
    s1, s2 = mags[idx[ru1]], mags[idx[ru2]]
    if s1 <= 0 or s2 >= 0 or abs(abs(s1) - abs(s2)) > 1e-12:
        fail("A2", f"{stem}: {ru1}/{ru2} seeds {s1}/{s2} are not equal and antiparallel")
    for label in {s[0] for s in species} - {ru1, ru2}:
        if mags[idx[label]] != 0.0:
            fail("A2", f"{stem}: non-metal species {label} carries seed {mags[idx[label]]}")

    # A3 -- the card, read from the deck
    card = hubbard_card(species, stem)
    if set(card[1:]) != {f"U {ru1}-{MANIFOLD} {U_STR}", f"U {ru2}-{MANIFOLD} {U_STR}"}:
        fail("A3", f"{stem}: card {card[1:]} does not cover the sublattice pair {ru1}/{ru2}")

    # ---- the transformation: prefix line + appended card, nothing else
    body, prefix_changed = [], 0
    for ln in lines[:-1]:
        if re.match(r"^\s*prefix\s*=", ln):
            nl = ln.replace(f"'{stem}'", f"'{new_stem}'")
            if nl == ln:
                fail("A4", f"{stem}: prefix line replacement failed on {ln!r}")
            body.append(nl)
            prefix_changed += 1
        else:
            body.append(ln)
    child_lines = body + card + [""]

    # A4 -- diff shape
    if prefix_changed != 1:
        fail("A4", f"{stem}: {prefix_changed} prefix lines changed, expected 1")
    diffs = [i for i, (a, b) in enumerate(zip(lines[:-1], body)) if a != b]
    if len(diffs) != 1 or not re.match(r"^\s*prefix\s*=", lines[diffs[0]]):
        fail("A4", f"{stem}: replaced lines {diffs} are not exactly the prefix line")
    kp = kpoints_index(lines[:-1], stem)
    if kp != len(lines) - 3:
        fail("A4", f"{stem}: K_POINTS card is not the parent's final card")
    if body[kp] != lines[kp] or body[kp + 1] != lines[kp + 1]:
        fail("A4", f"{stem}: K_POINTS card changed")
    if child_lines[len(body):len(body) + 3] != card or child_lines[-1] != "":
        fail("A4", f"{stem}: card placement/shape wrong at EOF")
    labels = {s[0] for s in species}
    if [r[2] for r in deck_rows(child_lines, labels)] != [r[2] for r in deck_rows(lines, labels)]:
        fail("A4", f"{stem}: ATOMIC_POSITIONS block is not byte-identical to the parent")

    dest, new_raw = write_child(new_stem, child_lines, stem)
    return dict(stem=new_stem, parent=stem, cls="afm", nat=BANKED[state]["nat"],
                card=card, parent_md5=md5_bytes(raw), md5=md5_bytes(new_raw),
                path=os.path.relpath(dest, REPO).replace(os.sep, "/"),
                calc_change="none (parent already 'scf')", rows_changed=0)


# -------------------------------------------------------------- NM children ---

def build_nm(state: str, anchor_lines: list[str], anchor_labels: set[str]) -> dict:
    stem = f"{state}__2x1v_off"
    new_stem = stem + "__u900"
    raw, otxt = pin_parent(os.path.join(NM_DIR, stem + ".in"),
                           os.path.join(NM_DIR, stem + ".out"), "nm", state)
    lines = split_keep(raw, stem)
    txt = raw.decode()

    # N1 -- treatment: this parent is a RELAX deck in the NM (nspin unset) class
    if not re.search(r"^\s*calculation\s*=\s*'relax'", txt, re.M):
        fail("N1", f"{stem}: parent is not calculation='relax'")
    if re.search(r"^\s*nspin\s*=", txt, re.M) or "starting_magnetization" in txt:
        fail("N1", f"{stem}: parent carries spin keys; the NM class runs nspin unset")
    if "HUBBARD" in txt:
        fail("N1", f"{stem}: parent already carries a HUBBARD card")
    check_flags(txt, ["nosym", "noinv"], stem, "N1")
    ms = re.search(r"^\s*max_seconds\s*=\s*(\d+)", txt, re.M)
    if not ms:
        fail("N1", f"{stem}: expected the emitter's max_seconds in the relax parent")

    species = species_block(txt)
    card = hubbard_card(species, stem)
    if card[1:] != [f"U Ru-{MANIFOLD} {U_STR}"]:
        fail("N2", f"{stem}: NM card is {card[1:]}, expected the single-label line")
    labels = {s[0] for s in species}

    nat = int(re.search(r"^\s*nat\s*=\s*(\d+)", txt, re.M).group(1))
    if nat != BANKED[state]["nat"]:
        fail("N3", f"{stem}: nat {nat} != banked {BANKED[state]['nat']}")
    rows = deck_rows(lines, labels)
    arows = deck_rows(anchor_lines, anchor_labels)
    fin = final_coordinates(otxt)
    if not (len(rows) == len(arows) == len(fin) == nat):
        fail("N3", f"{stem}: row counts deck={len(rows)} anchor={len(arows)} "
                   f"out={len(fin)} nat={nat} disagree")
    if [p[0] for _i, p, _l in rows] != [lab for lab, _x, _f in fin]:
        fail("N3", f"{stem}: .out final-coordinates label sequence differs from the deck")

    new_by_index: dict[int, str] = {}
    max_disp = 0.0
    for (i, p, ln), (_ai, ap, _al), (olab, xyz, oflags) in zip(rows, arows, fin):
        if len(p) != 7 or len(ap) != 7:
            fail("N5", f"{stem}: a position row lacks explicit flags: {ln!r}")
        indent = ln[: len(ln) - len(ln.lstrip())]
        if row_rebuild(indent, p[0], p[1], p[2], p[3], p[4:7]) != ln:
            fail("N5", f"{stem}: row formatter does not reproduce the parent line {ln!r}")
        if ap[0].rstrip("0123456789") != p[0]:
            fail("N5", f"{stem}: anchor label {ap[0]} does not map to NM label {p[0]}")
        if ap[4:7] != p[4:7]:
            fail("N5", f"{stem}: constraint flags differ NM {p[4:7]} vs anchor {ap[4:7]}")
        for k in range(3):
            if abs(float(ap[1 + k]) - xyz[k]) > 2e-8:
                fail("N5", f"{stem}: anchor coord {ap[1 + k]} vs .out {xyz[k]!r} "
                           f"differ beyond 8-dp rounding (atom line {i + 1})")
        d = max(abs(float(p[1 + k]) - xyz[k]) for k in range(3))
        if p[4:7] == ["0", "0", "0"]:
            if d > 1e-5:
                fail("N4", f"{stem}: frozen atom moved {d:.2e} A in the .out")
            if oflags != "0 0 0":
                fail("N4", f"{stem}: .out flags {oflags!r} on a frozen row")
            if ap[1:4] != p[1:4]:
                fail("N4", f"{stem}: frozen coordinate strings differ NM {p[1:4]} "
                           f"vs anchor {ap[1:4]}")
            # byte-identical: no entry in new_by_index
        else:
            if d > 1.5:
                fail("N5", f"{stem}: implausible relaxation displacement {d:.3f} A")
            max_disp = max(max_disp, d)
            nl = row_rebuild(indent, p[0], ap[1], ap[2], ap[3], p[4:7])
            if nl != ln:
                new_by_index[i] = nl

    # ---- the transformation: calculation + prefix + moving coordinates + card
    body, calc_changed, prefix_changed = [], 0, 0
    for i, ln in enumerate(lines[:-1]):
        if re.match(r"^\s*calculation\s*=", ln):
            nl = ln.replace("'relax'", "'scf'")
            if nl == ln:
                fail("N6", f"{stem}: calculation line replacement failed")
            body.append(nl)
            calc_changed += 1
        elif re.match(r"^\s*prefix\s*=", ln):
            nl = ln.replace(f"'{stem}'", f"'{new_stem}'")
            if nl == ln:
                fail("N6", f"{stem}: prefix line replacement failed on {ln!r}")
            body.append(nl)
            prefix_changed += 1
        elif i in new_by_index:
            body.append(new_by_index[i])
        else:
            body.append(ln)
    child_lines = body + card + [""]

    # N6 -- diff shape
    if calc_changed != 1 or prefix_changed != 1:
        fail("N6", f"{stem}: calculation/prefix changed {calc_changed}/{prefix_changed} times")
    row_set = {i for i, _p, _l in rows}
    for i, (a, b) in enumerate(zip(lines[:-1], body)):
        if a == b:
            continue
        if re.match(r"^\s*(calculation|prefix)\s*=", a):
            continue
        if i not in row_set:
            fail("N6", f"{stem}: unexpected changed line {a!r}")
        pa, pb = a.split(), b.split()
        if pa[0] != pb[0] or pa[4:] != pb[4:]:
            fail("N6", f"{stem}: a position row changed label or flags: {a!r} -> {b!r}")
    changed_rows = sum(1 for i in new_by_index)
    kp = kpoints_index(lines[:-1], stem)
    if kp != len(lines) - 3 or body[kp] != lines[kp] or body[kp + 1] != lines[kp + 1]:
        fail("N6", f"{stem}: K_POINTS card moved or changed")
    if child_lines[len(body):len(body) + 2] != card or child_lines[-1] != "":
        fail("N6", f"{stem}: card placement/shape wrong at EOF")
    if not re.search(r"^\s*max_seconds\s*=\s*" + ms.group(1) + r"\b",
                     "\n".join(child_lines), re.M):
        fail("N6", f"{stem}: parent max_seconds was not carried verbatim")

    dest, new_raw = write_child(new_stem, child_lines, stem)
    return dict(stem=new_stem, parent=stem, cls="nm", nat=nat, card=card,
                parent_md5=md5_bytes(raw), md5=md5_bytes(new_raw),
                path=os.path.relpath(dest, REPO).replace(os.sep, "/"),
                calc_change="'relax' -> 'scf' (parent is a relax deck)",
                rows_changed=changed_rows, max_disp=max_disp,
                max_seconds=ms.group(1))


# ------------------------------------------------------------- twin checks ---

def block_of(lines: list[str], start_key: str, end_key: str) -> list[str]:
    out, on = [], False
    for ln in lines:
        if ln.startswith(start_key):
            on = True
        elif ln.startswith(end_key):
            on = False
        elif on:
            out.append(ln)
    return out


def x_check(state: str, afm: dict, nm: dict) -> None:
    a_lines = open(os.path.join(OUT_DIR, afm["stem"] + ".in")).read().split("\n")
    n_lines = open(os.path.join(OUT_DIR, nm["stem"] + ".in")).read().split("\n")
    a_species = {s[0] for s in species_block("\n".join(a_lines))}
    n_species = {s[0] for s in species_block("\n".join(n_lines))}
    ar = deck_rows(a_lines, a_species)
    nr = deck_rows(n_lines, n_species)
    if len(ar) != len(nr):
        fail("X1", f"{state}: twin row counts differ {len(ar)} vs {len(nr)}")
    for (_ai, ap, _al), (_ni, np_, _nl) in zip(ar, nr):
        if ap[0].rstrip("0123456789") != np_[0]:
            fail("X1", f"{state}: twin labels {ap[0]} vs {np_[0]} do not correspond")
        if ap[1:4] != np_[1:4]:
            fail("X1", f"{state}: twin coordinates differ {ap[1:4]} vs {np_[1:4]}")
        if ap[4:7] != np_[4:7]:
            fail("X1", f"{state}: twin flags differ {ap[4:7]} vs {np_[4:7]}")
    if block_of(a_lines, "CELL_PARAMETERS", "ATOMIC_POSITIONS") != \
       block_of(n_lines, "CELL_PARAMETERS", "ATOMIC_POSITIONS"):
        fail("X1", f"{state}: twin CELL_PARAMETERS blocks differ")


# ---------------------------------------------------------------- manifest ---

HEADER = ("# NOT LICENSED FOR SUBMISSION — docs/61 decision item 10 (the entrant) "
          "is OPEN. Recorded either way; does not enter the A7.3 score. "
          "Both-U-endpoint AFM/NM probe on the gate-(h) recipe.")


def write_manifest(results: list[dict]) -> None:
    by = {(r["cls"], r["parent"].split("__")[0]): r for r in results}
    nm_oh, nm_ooh = by[("nm", "s0_OH")], by[("nm", "s0_OOH")]
    ordered = ([r for r in results if r["cls"] == "afm"]
               + [r for r in results if r["cls"] == "nm"])
    L = []
    L.append(HEADER)
    L.append("# Ru AFM probe, U = 9.0 endpoint -- 4 decks built by src/dft/build_ru_afm_probe.py")
    L.append("# (deterministic; parent and deck md5s below). Do NOT stage or submit while item 10 is open.")
    L.append("#")
    L.append("# The 4 SCFs = {s0_OH, s0_OOH} x {AFM, NM} at U = 9.0 eV, fixed geometry, 2x1v cell, on the")
    L.append("# NM-relaxed OFF-arm final BFGS geometries the banked gate-(h) family used (h_afm_anchor")
    L.append("# README; P11 limit (ii)). DERIVED enumeration -- item 10 gives only '4 SCFs, gate-(h)")
    L.append("# recipe'; see QUESTION-FOR-THE-ENTRANT below. The U = 0 endpoint is BANKED, not re-run:")
    L.append("#   AFM  runs/s0/h_afm_anchor/{s0_OH,s0_OOH}__2x1v_off__afm.out   -3304.20342621 / -3345.68881990 Ry")
    L.append("#   NM   runs/probe/Ru_cellsym/{s0_OH,s0_OOH}__2x1v_off.out final BFGS  -3304.19715356 / -3345.68064313 Ry")
    L.append("#   dc_M(0) = -25.91 meV (docs/63 section 4; re-derived from these pins at build time).")
    L.append("# Deliverable: D_M = dc_M(9.0) - dc_M(0), dc_M(U) = [E_AFM(OOH,U)-E_AFM(OH,U)] -")
    L.append("# [E_NM(OOH,U)-E_NM(OH,U)]; slab and gas references cancel in c_M (docs/61 A11.1), so only")
    L.append("# *OH/*OOH run; s0_O is excluded by design (measured flat-moment instability, docs/64 s4).")
    L.append("#")
    L.append("# Parentage (each child from the committed parent of its OWN magnetic class):")
    L.append("#   AFM children <- runs/s0/h_afm_anchor/<state>__2x1v_off__afm.in; diff = prefix line +")
    L.append("#     appended 3-line HUBBARD card ONLY (parent already calculation='scf' -- no calc change).")
    L.append("#   NM children  <- runs/probe/Ru_cellsym/<state>__2x1v_off.in (a RELAX deck); diff = prefix")
    L.append("#     line + calculation 'relax'->'scf' + moving-atom coordinates refreshed to that parent's")
    L.append("#     OWN .out final BFGS values (frozen '0 0 0' rows byte-identical; coordinate strings")
    L.append("#     asserted equal to the AFM twin's to <= 2e-8 A, so the pair is coordinate-identical) +")
    L.append(f"#     appended 2-line HUBBARD card. Parent max_seconds kept verbatim ({nm_oh['max_seconds']} /")
    L.append(f"#     {nm_ooh['max_seconds']} s -- inert runner machinery for an SCF).")
    L.append("# HUBBARD card read from EACH DECK'S OWN ATOMIC_SPECIES (build_a0spin read-it-from-the-deck")
    L.append("#   rule): the AFM decks split Ru into TWO labels, so their card carries BOTH")
    L.append("#   'U Ru1-4d 9.0000' AND 'U Ru2-4d 9.0000' -- QE raises no error for a U-less species; a")
    L.append("#   one-label card would silently leave the other sublattice at U = 0. NM decks carry the")
    L.append("#   single 'U Ru-4d 9.0000' (syntax precedent runs/a0/main/Ru/s0_OH__u900.in).")
    L.append("#")
    L.append("# Scoring at landing: gate-(h) recipe exactly (h_afm_anchor README) -- converged iff")
    L.append("#   'convergence has been achieved' >= 1 AND 'convergence NOT achieved' == 0 AND a final '^!'")
    L.append("#   line exists (success is NEVER 'JOB DONE' alone); E = last '^!'; totmag/absmag = last")
    L.append("#   printed pair; meV = dRy * 13605.693122994. Guards (adapted docs/61 A11.7): (1) k-count/")
    L.append("#   symmetry match NM-vs-AFM at U=9 (expect 16/16, 'No symmetry found' both); (2) E_AFM vs its")
    L.append("#   NM twin recorded either way (no adoption rule exists for this probe); (3) branch")
    L.append("#   continuity vs the banked U=0 moments (OH totmag/absmag -1.21/3.85, OOH -0.24/4.79) --")
    L.append("#   collapse or sign flip marks D_M branch-conditional. Context, NEVER a score: Ru sits")
    L.append("#   15.5 meV from the A7.3 floor; crossing would need dc_M(9.0) <= -41.4 meV")
    L.append("#   (docs/figs/a0main_readout.json) -- item 10 says the probe does not re-score A7.3 either way.")
    L.append("#")
    L.append("# QUESTION-FOR-THE-ENTRANT (genuine reading ambiguity -- decide when electing item 10):")
    L.append("#   docs/61 item 10 names only '4 SCFs, gate-(h) recipe'; the enumeration above is DERIVED")
    L.append("#   (any other assignment duplicates banked rows, cannot form D_M, or crosses cell/k/symmetry")
    L.append("#   treatments), and 'both U endpoints' is docs/63 s4.3 / docs/64 s3 wording, not item 10's.")
    L.append("#   ALTERNATIVE READING: since docs/64 the AFM-RELAXED OH/OOH geometries exist")
    L.append("#   (runs/s0/h_afm_relax), and the probe could run on those instead -- that reading pairs with")
    L.append("#   dc_M(0) = -32.5 meV (docs/64 s2), re-opens which NM comparator is like-for-like, and needs")
    L.append("#   BOTH endpoints rebuilt consistently on the new geometry. These decks implement the")
    L.append("#   NM-relaxed reading (the recipe as banked). Electing item 10 should countersign the")
    L.append("#   enumeration and the geometry choice (or direct a rebuild), and settle the docs/61 A11.11")
    L.append("#   deposit question for this probe (own dated docs/43 line vs inside the A11 deposit).")
    L.append("#")
    L.append("# Parent md5s (each byte-identical to its committed blob at HEAD, asserted):")
    for r in ordered:
        pdir = "runs/s0/h_afm_anchor" if r["cls"] == "afm" else "runs/probe/Ru_cellsym"
        L.append(f"#   {r['parent_md5']}  {pdir}/{r['parent']}.in")
    L.append("# Deck md5s (build is deterministic; double-build verified):")
    for r in ordered:
        L.append(f"#   {r['md5']}  {r['stem']}.in")
    L.append("# 4-field rows for queue_r1.sh (dir job suffix nk); nk = 4 per the h_afm_anchor README runner")
    L.append("# note (4 4 1 + nosym/noinv -> 16 k >= 12; NP an exact multiple of 4). If routed through the")
    L.append("# Anvil m_h_afm_relax.txt consumer instead, that file's 2x1v adsorbate convention is nk = 8.")
    for r in ordered:
        L.append(f"s0/h_afm_probe {r['stem']} .in 4")
    with open(MANIFEST, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L) + "\n")


# -------------------------------------------------------------------- main ---

def main() -> int:
    # P4 (family-level): the banked U = 0 endpoint reproduces docs/63's dc_M(0)
    dc0 = ((BANKED["s0_OOH"]["afm_ry"] - BANKED["s0_OH"]["afm_ry"])
           - (BANKED["s0_OOH"]["nm_ry"] - BANKED["s0_OH"]["nm_ry"])) * RY_MEV
    if abs(dc0 - DC0_MEV) > 0.05:
        fail("P4", f"banked pins give dc_M(0) = {dc0:.2f} meV, not {DC0_MEV} meV")

    results = []
    for state in STATES:
        anchor_raw = open(os.path.join(ANCHOR_DIR, f"{state}__2x1v_off__afm.in"), "rb").read()
        anchor_lines = split_keep(anchor_raw, f"{state} anchor")
        anchor_labels = {s[0] for s in species_block(anchor_raw.decode())}
        afm = build_afm(state)
        nm = build_nm(state, anchor_lines, anchor_labels)
        x_check(state, afm, nm)
        results.extend([afm, nm])

    write_manifest(results)

    print(f"Built {len(results)} decks under runs/s0/h_afm_probe/ "
          f"(dc_M(0) re-derived = {dc0:.2f} meV; banked, not re-run)\n")
    print(f"{'stem':<34}{'class':>6}{'nat':>5}{'rows moved':>12}  calc change / card")
    for r in results:
        print(f"{r['stem']:<34}{r['cls']:>6}{r['nat']:>5}{r['rows_changed']:>12}  "
              f"{r['calc_change']}; {' | '.join(r['card'][1:])}")
    print(f"\n{'md5':<34}{'file'}")
    for r in results:
        print(f"{r['md5']:<34}{r['stem']}.in")
    print(f"\nMANIFEST WRITTEN: runs/s0/m_h_afm_probe.txt (NOT licensed for submission; "
          f"item 10 is the entrant's)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
