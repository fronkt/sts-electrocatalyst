#!/usr/bin/env python3
"""Shared deck writer for the HEA fixed-geometry SCF arms (branch panel + fidelity pilot).

Every deck written through this module:

  * clones the &CONTROL / &SYSTEM / &ELECTRONS / &IONS namelists of the banked production
    2x1v deck runs/a0/cell/ref__2x1v__u715.in VERBATIM, and asserts at render time that the
    only lines that differ from that template are the ones this arm must change:
    prefix, nat, ntyp, the per-species starting_magnetization block, electron_maxstep
    (200 -> 300) and max_seconds (226002 -> 165000, the S3 value);
  * writes ibrav = 0 with CELL_PARAMETERS angstrom copied from the retained cell_A;
  * lists ATOMIC_SPECIES as metals alphabetically, then O, then H, with the SSSP file
    names and masses of record (src/dft/qe_slab.py ELEMENTS table);
  * writes ATOMIC_POSITIONS angstrom with if_pos 0 0 0 on the retained fixed_atom_indices
    and 1 1 1 elsewhere, every coordinate in shortest round-trip repr so that re-parsing
    the deck reproduces the source floats EXACTLY (asserted);
  * emits one 'U <M>-3d <U>' line per 3d metal present with U > 0 under the projector card
    requested ('HUBBARD (atomic)' or 'HUBBARD (ortho-atomic)'); Cu has no U line;
  * sets K_POINTS automatic from the k-mesh rule of src/dft/qe_slab.py (kgrid_from_cell:
    n_i = max(1, round(25 / |a_i|)) in-plane, 1 along c), computed on the actual cell;
  * refuses CR bytes, refuses any UPF absent from anvil/pseudo_md5_preflight_2026-08-23.md,
    and refuses to overwrite an existing file whose bytes differ.

Nothing here launches anything.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TEMPLATE = REPO / "runs" / "a0" / "cell" / "ref__2x1v__u715.in"
PREFLIGHT = REPO / "anvil" / "pseudo_md5_preflight_2026-08-23.md"
EXCLUDE = "a024,a049,a050,a088,a196,a220,a223,a171,a120,a200"
NP = 128

# Per-element settings of record, copied from src/dft/qe_slab.py:35-47 (ELEMENTS):
# SSSP file name, mass, MP-calibrated U_eff (eV) on the 3d channel, starting magnetization.
ELEMENTS = {
    "Cr": dict(pseudo="cr_pbe_v1.5.uspp.F.UPF",             mass=51.996,  U=3.7,  mag=0.6),
    "Mn": dict(pseudo="mn_pbe_v1.5.uspp.F.UPF",             mass=54.938,  U=3.9,  mag=0.5),
    "Fe": dict(pseudo="Fe.pbe-spn-kjpaw_psl.0.2.1.UPF",     mass=55.845,  U=5.3,  mag=0.5),
    "Co": dict(pseudo="Co_pbe_v1.2.uspp.F.UPF",             mass=58.933,  U=3.32, mag=0.4),
    "Ni": dict(pseudo="ni_pbe_v1.4.uspp.F.UPF",             mass=58.693,  U=6.2,  mag=0.3),
    "Cu": dict(pseudo="Cu.paw.z_11.ld1.psl.v1.0.0-low.upf", mass=63.546,  U=0.0,  mag=0.2),
    "O":  dict(pseudo="O.pbe-n-kjpaw_psl.0.1.UPF",          mass=15.999,  U=0.0,  mag=0.0),
    "H":  dict(pseudo="H.pbe-rrkjus_psl.1.0.0.UPF",         mass=1.008,   U=0.0,  mag=0.0),
}
METALS = ("Cr", "Mn", "Fe", "Co", "Ni", "Cu")

CARD = {"atomic": "HUBBARD (atomic)", "ortho": "HUBBARD (ortho-atomic)"}
ELECTRON_MAXSTEP = 300
MAX_SECONDS = 165000


class BuildError(SystemExit):
    pass


# --------------------------------------------------------------------------- helpers
def md5_bytes(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def md5_file(path: Path) -> str:
    return md5_bytes(Path(path).read_bytes())


def sha256_lf(path: Path) -> str:
    data = Path(path).read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def json_pointer(doc, pointer: str):
    """Resolve an RFC 6901 pointer such as '/attempts/2/geometry'."""
    node = doc
    for tok in pointer.lstrip("/").split("/"):
        tok = tok.replace("~1", "/").replace("~0", "~")
        node = node[int(tok)] if isinstance(node, list) else node[tok]
    return node


def preflight_upfs(path: Path = PREFLIGHT) -> dict:
    """UPF file name -> Anvil md5, parsed from the preflight table rows."""
    out = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\|\s*([A-Z][a-z]?)\s*\|\s*(\S+\.(?:UPF|upf))\s*\|.*?\|\s*([0-9a-f]{32})\s*\|", line)
        if m:
            out[m.group(2)] = m.group(3)
    if not out:
        raise BuildError(f"{path}: no UPF rows parsed")
    return out


def species_order(symbols) -> list:
    """Metals alphabetically, then O, then H."""
    present = set(symbols)
    unknown = present - set(ELEMENTS)
    if unknown:
        raise BuildError(f"no settings of record for {sorted(unknown)}")
    order = sorted(s for s in present if s in METALS)
    for s in ("O", "H"):
        if s in present:
            order.append(s)
    return order


def kgrid_from_cell(cell, target: float = 25.0):
    """The k-mesh rule of src/dft/qe_slab.py:77-84, re-stated without numpy."""
    lengths = [math.sqrt(sum(c * c for c in row)) for row in cell]
    n = [max(1, int(round(target / L))) for L in lengths]
    n[2] = 1
    return tuple(n)


def kpoint_count(mesh) -> int:
    """nosym + noinv: the full Monkhorst-Pack mesh is used, no reduction."""
    return mesh[0] * mesh[1] * mesh[2]


def choose_nk(nkpts: int, np_: int = NP) -> int:
    """Largest divisor of NP that does not exceed the k-point count."""
    return max(d for d in range(1, np_ + 1) if np_ % d == 0 and d <= nkpts)


# --------------------------------------------------------------------------- template
def load_template(path: Path = TEMPLATE) -> list:
    """The four namelists of the banked 2x1v deck, as lines (up to and excluding ATOMIC_SPECIES)."""
    text = Path(path).read_bytes()
    if b"\r" in text:
        raise BuildError(f"{path}: template carries CR bytes")
    lines = text.decode("utf-8").split("\n")
    try:
        end = lines.index("ATOMIC_SPECIES")
    except ValueError:
        raise BuildError(f"{path}: no ATOMIC_SPECIES card")
    nml = lines[:end]
    for must in ("&CONTROL", "&SYSTEM", "&ELECTRONS", "&IONS", "  calculation = 'scf'",
                 "  nspin = 2", "  nosym = .true.", "  noinv = .true.",
                 "  ecutwfc = 80.0", "  ecutrho = 640.0", "  mixing_mode = 'local-TF'",
                 "  mixing_beta = 0.3", "  conv_thr = 1.0d-6", "  degauss = 0.01",
                 "  smearing = 'mv'", "  occupations = 'smearing'", "  tprnfor = .true.",
                 "  ibrav = 0"):
        if must not in nml:
            raise BuildError(f"{path}: template lacks {must!r}")
    return nml


_ALLOWED = (
    re.compile(r"^  prefix = '.*'$"),
    re.compile(r"^  nat = \d+$"),
    re.compile(r"^  ntyp = \d+$"),
    re.compile(r"^  starting_magnetization\(\d+\) = -?\d+\.\d+$"),
    re.compile(r"^  electron_maxstep = \d+$"),
    re.compile(r"^  max_seconds = \d+$"),
)


def render_namelists(template: list, prefix: str, nat: int, order: list) -> list:
    out = []
    mag_done = False
    for ln in template:
        if ln.startswith("  prefix = "):
            out.append(f"  prefix = '{prefix}'")
        elif ln.startswith("  nat = "):
            out.append(f"  nat = {nat}")
        elif ln.startswith("  ntyp = "):
            out.append(f"  ntyp = {len(order)}")
        elif ln.startswith("  starting_magnetization("):
            if not mag_done:
                for i, sp in enumerate(order, 1):
                    out.append(f"  starting_magnetization({i}) = {ELEMENTS[sp]['mag']}")
                mag_done = True
        elif ln.startswith("  electron_maxstep = "):
            out.append(f"  electron_maxstep = {ELECTRON_MAXSTEP}")
        elif ln.startswith("  max_seconds = "):
            out.append(f"  max_seconds = {MAX_SECONDS}")
        else:
            out.append(ln)
    # every line not in the template must be one of the allowed substitutions
    tset = set(template)
    for ln in out:
        if ln not in tset and not any(p.match(ln) for p in _ALLOWED):
            raise BuildError(f"rendered namelist line not in template and not allowed: {ln!r}")
    for ln in template:
        if ln not in set(out) and not any(p.match(ln) for p in _ALLOWED):
            raise BuildError(f"template namelist line dropped: {ln!r}")
    return out


# --------------------------------------------------------------------------- deck
def render_deck(prefix: str, symbols, positions, cell, fixed, projector: str,
                template: list | None = None) -> str:
    """Return the deck text (LF, trailing newline). Raises BuildError on any inconsistency."""
    if projector not in CARD:
        raise BuildError(f"projector must be one of {sorted(CARD)}, got {projector!r}")
    symbols = list(symbols)
    nat = len(symbols)
    if len(positions) != nat:
        raise BuildError("positions/symbols length mismatch")
    if len(cell) != 3 or any(len(r) != 3 for r in cell):
        raise BuildError("cell must be 3x3")
    fixed = sorted(int(i) for i in fixed)
    if any(i < 0 or i >= nat for i in fixed):
        raise BuildError("fixed index out of range")
    order = species_order(symbols)
    nml = render_namelists(template or load_template(), prefix, nat, order)

    lines = list(nml)
    lines.append("ATOMIC_SPECIES")
    for sp in order:
        lines.append(f"  {sp}  {ELEMENTS[sp]['mass']}  {ELEMENTS[sp]['pseudo']}")
    lines.append("CELL_PARAMETERS angstrom")
    for row in cell:
        lines.append("  " + "  ".join(repr(float(x)) for x in row))
    lines.append("ATOMIC_POSITIONS angstrom")
    fset = set(fixed)
    for i, (sp, pos) in enumerate(zip(symbols, positions)):
        flag = "0 0 0" if i in fset else "1 1 1"
        lines.append(f"  {sp}  " + "  ".join(repr(float(x)) for x in pos) + f"  {flag}")
    mesh = kgrid_from_cell(cell)
    lines.append("K_POINTS automatic")
    lines.append(f"  {mesh[0]} {mesh[1]} {mesh[2]} 0 0 0")
    ulines = [f"U {sp}-3d {ELEMENTS[sp]['U']:.4f}" for sp in order if ELEMENTS[sp]["U"] > 0]
    if ulines:
        lines.append(CARD[projector])
        lines.extend(ulines)
    text = "\n".join(lines) + "\n"
    verify_deck(text, symbols, positions, cell, fixed)
    return text


def parse_deck(text: str) -> dict:
    lines = text.split("\n")
    d = {"symbols": [], "positions": [], "cell": [], "fixed": [], "species": [], "upfs": [],
         "mesh": None, "hubbard_card": None, "U": {}, "nat": None, "ntyp": None, "mag": {}}
    sec = None
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        m = re.match(r"^nat = (\d+)$", s)
        if m:
            d["nat"] = int(m.group(1))
        m = re.match(r"^ntyp = (\d+)$", s)
        if m:
            d["ntyp"] = int(m.group(1))
        m = re.match(r"^starting_magnetization\((\d+)\) = (-?[\d.]+)$", s)
        if m:
            d["mag"][int(m.group(1))] = float(m.group(2))
        if s in ("ATOMIC_SPECIES", "ATOMIC_POSITIONS angstrom", "CELL_PARAMETERS angstrom",
                 "K_POINTS automatic") or s.startswith("HUBBARD"):
            sec = s
            if s.startswith("HUBBARD"):
                d["hubbard_card"] = s
            continue
        if s.startswith("&") or s == "/":
            sec = None
            continue
        if sec == "ATOMIC_SPECIES":
            sp, mass, upf = s.split()
            d["species"].append(sp)
            d["upfs"].append(upf)
        elif sec == "CELL_PARAMETERS angstrom":
            d["cell"].append([float(x) for x in s.split()])
        elif sec == "ATOMIC_POSITIONS angstrom":
            parts = s.split()
            d["symbols"].append(parts[0])
            d["positions"].append([float(x) for x in parts[1:4]])
            if parts[4:7] == ["0", "0", "0"]:
                d["fixed"].append(len(d["symbols"]) - 1)
        elif sec == "K_POINTS automatic":
            d["mesh"] = tuple(int(x) for x in s.split()[:3])
        elif sec and sec.startswith("HUBBARD"):
            m = re.match(r"^U (\w+)-3d ([\d.]+)$", s)
            if not m:
                raise BuildError(f"bad HUBBARD line {s!r}")
            d["U"][m.group(1)] = float(m.group(2))
    return d


def verify_deck(text: str, symbols, positions, cell, fixed) -> dict:
    """Byte-level and value-level checks; returns the parsed deck."""
    if "\r" in text:
        raise BuildError("deck carries CR bytes")
    p = parse_deck(text)
    symbols = list(symbols)
    if p["symbols"] != symbols:
        raise BuildError("deck symbols differ from the source record")
    if p["nat"] != len(symbols):
        raise BuildError("nat differs from the atom count")
    if [[float(x) for x in r] for r in p["positions"]] != [[float(x) for x in r] for r in positions]:
        raise BuildError("deck positions are not byte-for-byte the retained positions")
    if [[float(x) for x in r] for r in p["cell"]] != [[float(x) for x in r] for r in cell]:
        raise BuildError("deck cell is not byte-for-byte the retained cell")
    if p["fixed"] != sorted(int(i) for i in fixed):
        raise BuildError("if_pos flags do not reproduce fixed_atom_indices")
    order = species_order(symbols)
    if p["species"] != order:
        raise BuildError("ATOMIC_SPECIES order is not metals-alphabetical, O, H")
    if p["ntyp"] != len(order):
        raise BuildError("ntyp differs from the species count")
    if Counter(p["symbols"]) != Counter(symbols):
        raise BuildError("species counts differ from the source record")
    for i, sp in enumerate(order, 1):
        if p["mag"].get(i) != ELEMENTS[sp]["mag"]:
            raise BuildError(f"starting_magnetization({i}) for {sp} is not the value of record")
    want_u = {sp: ELEMENTS[sp]["U"] for sp in order if ELEMENTS[sp]["U"] > 0}
    if p["U"] != want_u:
        raise BuildError(f"HUBBARD U lines {p['U']} differ from the set of record {want_u}")
    if p["mesh"] != kgrid_from_cell(cell):
        raise BuildError("K_POINTS mesh differs from the k-mesh rule")
    pre = preflight_upfs()
    for upf in p["upfs"]:
        if upf not in pre:
            raise BuildError(f"UPF {upf} is not in {PREFLIGHT.name}")
    return p


def write_lf(path: Path, text: str) -> str:
    """Write LF bytes; refuse a differing existing file; return md5."""
    if "\r" in text:
        raise BuildError(f"{path}: refusing to write CR bytes")
    data = text.encode("utf-8")
    path = Path(path)
    if path.exists():
        if path.read_bytes() != data:
            raise BuildError(f"{path} exists with different content; refusing to overwrite")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(data)
    if b"\r" in path.read_bytes():
        raise BuildError(f"{path}: CR byte found after write")
    return md5_bytes(data)


def deck_info(text: str) -> dict:
    """Size descriptors a manifest and the cost model need."""
    p = parse_deck(text)
    mesh = p["mesh"]
    nk = choose_nk(kpoint_count(mesh))
    return dict(nat=p["nat"], ntyp=p["ntyp"], mesh=mesh, nkpts=kpoint_count(mesh), nk=nk,
                counts=dict(Counter(p["symbols"])), cell=p["cell"], projector=p["hubbard_card"])


def check_manifest_text(text: str, expect_not_licensed: bool = True) -> dict:
    """The submitter's own greps (anvil/47_submit_a0.sh:57-80; src/dft/queue_r1.sh:87-100)."""
    if "\r" in text:
        raise BuildError("manifest carries CR bytes")
    lines = text.split("\n")
    not_lic = any("not licensed" in ln.lower() for ln in lines)
    if expect_not_licensed and not not_lic:
        raise BuildError("manifest lacks the NOT LICENSED notice the submitter must refuse")
    excl = [ln for ln in lines if ln.startswith("# SUBMIT WITH EXCLUDE=")]
    if len(excl) != 1:
        raise BuildError("manifest must carry exactly one '# SUBMIT WITH EXCLUDE=' header")
    if excl[0].split("=", 1)[1].strip() != EXCLUDE:
        raise BuildError("EXCLUDE header differs from the list of record")
    ndirect = sum(1 for ln in lines if re.match(r"^# *N(P|CONC)=", ln))
    nstrict = sum(1 for ln in lines if re.match(r"^# NP=[0-9]+ NCONC=[0-9]+$", ln))
    if ndirect != nstrict or nstrict > 1:
        raise BuildError(f"NP directive malformed: {ndirect} directive-like lines, {nstrict} strict")
    rows = [ln for ln in lines if ln.strip() and not ln.startswith("#")]
    for r in rows:
        parts = r.split()
        if len(parts) != 4 or not parts[3].isdigit() or NP % int(parts[3]) != 0:
            raise BuildError(f"bad manifest row {r!r}")
    return dict(not_licensed=not_lic, exclude=EXCLUDE, n_rows=len(rows),
                np_directive=nstrict == 1)


def load_json(path: Path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)
