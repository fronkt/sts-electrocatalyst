"""Strict pw.x input/output readers for the low-tail DFT validation track.

Forces are read ONLY from the rows that immediately follow the header
``Forces acting on atoms (cartesian axes, Ry/au):`` -- the total forces. With high
verbosity pw.x prints further per-term blocks ("The non-local contrib.  to forces",
"The ionic contribution  to forces", ...) whose rows have the same ``atom i type t
force =`` shape; those blocks are counted and never read as forces.

Failure vocabulary for accepted SCF evidence is the set of src/dft/hea_followup_qc.py
(FAILURES, :19-22), re-read from that file at import.
"""
from __future__ import annotations

import math
import re
from pathlib import Path

import numpy as np

from lt_common import ROOT, RY_BOHR_TO_EV_A, RY_TO_EV

NUM = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eEdD][+-]?\d+)?"
FORCE_HEADER = re.compile(r"^\s*Forces acting on atoms \(cartesian axes, Ry/au\):\s*$", re.M)
FORCE_ROW = re.compile(r"^\s*atom\s+(\d+)\s+type\s+(\d+)\s+force\s*=\s*(" + NUM + r")\s+(" + NUM + r")\s+(" + NUM + r")\s*$")
CONTRIB_HEADER = re.compile(r"^\s*The .*(?:contrib|contribution|correction term).*to forces\s*$", re.M | re.I)
ENERGY = re.compile(r"^!\s+total energy\s*=\s*(" + NUM + r")\s+Ry\s*$", re.M)
SCF_OK = re.compile(r"convergence has been achieved in\s+(\d+)\s+iterations")
SCF_BAD = re.compile(r"convergence NOT achieved after\s+(\d+)\s+iterations")
BFGS_OK = re.compile(r"bfgs converged in\s+(\d+)\s+scf cycles and\s+(\d+)\s+bfgs steps")
FINAL_ENERGY = re.compile(r"^\s*Final energy\s*=\s*(" + NUM + r")\s+Ry\s*$", re.M)
TIMER = re.compile(r"^\s*(\w[\w:]*)\s*:\s*(" + NUM + r")s CPU\s+(" + NUM + r")s WALL\s*\(\s*(\d+)\s+calls\)", re.M)
PWSCF_WALL = re.compile(r"^\s*PWSCF\s*:\s*(.+?)\s+CPU\s+(.+?)\s+WALL\s*$", re.M)


def _failure_regex() -> re.Pattern:
    text = (ROOT / "src" / "dft" / "hea_followup_qc.py").read_text(encoding="utf-8")
    match = re.search(r"FAILURES = re\.compile\((.*?), re\.I\)", text, re.S)
    if match is None:
        raise RuntimeError("FAILURES pattern not found in src/dft/hea_followup_qc.py")
    pieces = re.findall(r'r"((?:[^"\\]|\\.)*)"', match.group(1))
    if not pieces:
        raise RuntimeError("FAILURES pattern pieces not parsed")
    return re.compile("".join(pieces), re.I)


FAILURES = _failure_regex()
BENIGN_IEEE_NOTICE = re.compile(
    r"(?m)^Note: The following floating-point exceptions are signalling:"
    r"(?:[ \t]+(?:IEEE_UNDERFLOW_FLAG|IEEE_DENORMAL))+[ \t]*\r?$")
NUMERICAL_FAILURES = re.compile(
    r"IEEE_(?:INVALID|DIVIDE_BY_ZERO|OVERFLOW)(?:_FLAG)?|SIGFPE|floating.point exception"
    r"|Program received signal[^\n]*", re.I)


def number(token: str) -> float:
    value = float(token.replace("D", "e").replace("d", "e"))
    if not math.isfinite(value):
        raise ValueError("nonfinite numeric token")
    return value


# --------------------------------------------------------------------------- input
def _strip_comments(text: str) -> list[str]:
    return [line.split("!", 1)[0].rstrip() for line in text.replace("\r\n", "\n").split("\n")]


def namelist_value(text: str, key: str):
    """Last literal assignment of ``key`` in the namelists (string/number/logical token)."""
    values = re.findall(rf"^\s*{re.escape(key)}\s*=\s*([^,\n]+?)\s*,?\s*$", "\n".join(_strip_comments(text)), re.M | re.I)
    if not values:
        return None
    raw = values[-1].strip()
    if raw[:1] in "'\"":
        return raw.strip("'\"")
    if raw.lower() in (".true.", ".false."):
        return raw.lower() == ".true."
    try:
        return number(raw)
    except ValueError:
        return raw


def element_of(label: str) -> str:
    """Element symbol of a species label such as Cr, Cr1, O2 or Mn_up."""
    m = re.match(r"([A-Z][a-z]?)(?:[0-9_]\w*)?$", label)
    if m is None:
        raise ValueError(f"cannot read an element from species label {label!r}")
    return m.group(1)


def parse_input(text: str) -> dict:
    lines = _strip_comments(text)
    calc = namelist_value(text, "calculation")
    nat = namelist_value(text, "nat")
    if not isinstance(nat, float) or nat != int(nat) or nat <= 0:
        raise ValueError("one positive integer nat required")
    nat = int(nat)
    stripped = [line.strip() for line in lines]
    starts = [i for i, s in enumerate(stripped) if s.upper().startswith("ATOMIC_POSITIONS")]
    cells = [i for i, s in enumerate(stripped) if s.upper().startswith("CELL_PARAMETERS")]
    species_at = [i for i, s in enumerate(stripped) if s.upper() == "ATOMIC_SPECIES"]
    if len(starts) != 1 or "angstrom" not in stripped[starts[0]].lower():
        raise ValueError("exactly one ATOMIC_POSITIONS angstrom card required")
    if len(cells) != 1 or "angstrom" not in stripped[cells[0]].lower():
        raise ValueError("exactly one CELL_PARAMETERS angstrom card required")
    if len(species_at) != 1:
        raise ValueError("exactly one ATOMIC_SPECIES card required")
    species = []
    for s in stripped[species_at[0] + 1:]:
        parts = s.split()
        if len(parts) != 3:
            break
        try:
            number(parts[1])
        except ValueError:
            break
        species.append(dict(label=parts[0], mass=number(parts[1]), upf=parts[2]))
    labels = [row["label"] for row in species]
    if not species or len(set(labels)) != len(labels):
        raise ValueError("missing or duplicate ATOMIC_SPECIES labels")
    cell = []
    for s in stripped[cells[0] + 1:cells[0] + 4]:
        parts = s.split()
        if len(parts) != 3:
            raise ValueError("incomplete CELL_PARAMETERS")
        cell.append([number(p) for p in parts])
    symbols, positions, if_pos = [], [], []
    rows = [s for s in stripped[starts[0] + 1:] if s][:nat]
    if len(rows) != nat:
        raise ValueError("incomplete ATOMIC_POSITIONS")
    for s in rows:
        parts = s.split()
        if len(parts) not in (4, 7) or parts[0] not in labels:
            raise ValueError(f"invalid atom row {s!r}")
        flags = parts[4:] or ["1", "1", "1"]
        if any(flag not in ("0", "1") for flag in flags):
            raise ValueError("if_pos flags must be 0 or 1")
        symbols.append(parts[0])
        positions.append([number(p) for p in parts[1:4]])
        if_pos.append([int(flag) for flag in flags])
    params = {key: namelist_value(text, key) for key in (
        "prefix", "ecutwfc", "ecutrho", "degauss", "smearing", "conv_thr", "mixing_beta",
        "nspin", "nstep", "forc_conv_thr", "electron_maxstep", "max_seconds", "startingwfc",
        "startingpot", "ion_dynamics", "tprnfor")}
    mags = {int(m.group(1)): number(m.group(2)) for m in re.finditer(
        r"^\s*starting_magnetization\((\d+)\)\s*=\s*(" + NUM + r")", "\n".join(lines), re.M)}
    hubbard = [s for s in stripped if s.upper().startswith("HUBBARD")]
    elements = [element_of(label) for label in symbols]
    return dict(calculation=calc, nat=nat, species=species, symbols=symbols, elements=elements, positions=positions,
                if_pos=if_pos, cell=cell, params=params, starting_magnetization=mags,
                hubbard_card=hubbard[0] if len(hubbard) == 1 else None,
                fixed=[i for i, flags in enumerate(if_pos) if flags == [0, 0, 0]])


# --------------------------------------------------------------------------- forces
def force_blocks(text: str, nat: int) -> list[np.ndarray]:
    """Every total-force block, in eV/A, each exactly ``nat`` ordered rows."""
    blocks = []
    lines = text.replace("\r\n", "\n").split("\n")
    header_lines = [i for i, line in enumerate(lines) if FORCE_HEADER.match(line)]
    for h in header_lines:
        rows = []
        j = h + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        while j < len(lines):
            match = FORCE_ROW.match(lines[j])
            if not match:
                break
            rows.append(match)
            j += 1
        if len(rows) != nat or [int(m.group(1)) for m in rows] != list(range(1, nat + 1)):
            raise ValueError(f"total-force block after line {h + 1} has {len(rows)} rows, expected {nat} ordered rows")
        blocks.append(np.array([[number(m.group(k)) for k in (3, 4, 5)] for m in rows]) * RY_BOHR_TO_EV_A)
    return blocks


def count_contribution_blocks(text: str) -> int:
    return len(CONTRIB_HEADER.findall(text))


# --------------------------------------------------------------------------- output
def _wall_seconds(token: str) -> tuple[float, float]:
    """Seconds and print resolution of a pw.x clock token such as 31m33.31s, 7h47m or 1d10h27m."""
    match = re.fullmatch(r"\s*(?:(\d+)d)?\s*(?:(\d+)h)?\s*(?:(\d+)m)?\s*(?:(" + NUM + r")s)?\s*", token)
    if match is None or not any(match.groups()):
        raise ValueError(f"cannot parse wall token {token!r}")
    seconds = (int(match.group(1) or 0) * 86400 + int(match.group(2) or 0) * 3600
               + int(match.group(3) or 0) * 60 + float(match.group(4) or 0.0))
    resolution = 0.01 if match.group(4) is not None else 60.0
    return seconds, resolution


def timers(text: str) -> dict:
    """Top-level timers (first occurrence of each name) and the PWSCF wall in seconds."""
    out = {}
    for match in TIMER.finditer(text):
        name = match.group(1)
        if name not in out:
            out[name] = dict(cpu_s=number(match.group(2)), wall_s=number(match.group(3)), calls=int(match.group(4)))
    wall = PWSCF_WALL.findall(text)
    if wall:
        out["PWSCF_wall_s"], out["PWSCF_wall_resolution_s"] = _wall_seconds(wall[-1][1])
    else:
        out["PWSCF_wall_s"] = out["PWSCF_wall_resolution_s"] = None
    return out


def header_numbers(text: str) -> dict:
    def grab(pattern, cast=float):
        match = re.search(pattern, text)
        return cast(match.group(1)) if match else None
    return dict(
        nat=grab(r"number of atoms/cell\s*=\s*(\d+)", int),
        nelec=grab(r"number of electrons\s*=\s*(" + NUM + ")"),
        nbnd=grab(r"number of Kohn-Sham states\s*=\s*(\d+)", int),
        volume_au3=grab(r"unit-cell volume\s*=\s*(" + NUM + r")\s*\(a\.u\.\)\^3"),
        nkpts=grab(r"number of k points\s*=\s*(\d+)", int),
        npool=grab(r"K-points division:\s*npool\s*=\s*(\d+)", int),
        procs=grab(r"running on\s+(\d+)\s+processor cores", int),
        ram_per_process_MB=grab(r"Estimated max dynamical RAM per process >\s*(" + NUM + r")\s*MB"),
        ram_total_GB=grab(r"Estimated total dynamical RAM >\s*(" + NUM + r")\s*GB"),
    )


def magnetizations(text: str) -> dict:
    total = re.findall(r"total magnetization\s*=\s*(" + NUM + ")", text)
    absolute = re.findall(r"absolute magnetization\s*=\s*(" + NUM + ")", text)
    return dict(total_muB=number(total[-1]) if total else None,
                absolute_muB=number(absolute[-1]) if absolute else None)


def parse_scf(text: str, nat: int) -> dict:
    """One completed fixed-geometry SCF: exactly one energy, convergence, total-force block, JOB DONE."""
    diagnostic_text = BENIGN_IEEE_NOTICE.sub("", text)
    failures = sorted({m.group(0) for regex in (FAILURES, NUMERICAL_FAILURES)
                       for m in regex.finditer(diagnostic_text)})
    energies = [number(m.group(1)) for m in ENERGY.finditer(text)]
    iterations = [int(m.group(1)) for m in SCF_OK.finditer(text)]
    reasons = []
    if failures:
        reasons.append("failure markers: " + ", ".join(failures))
    if text.count("JOB DONE") != 1:
        reasons.append("expected exactly one JOB DONE")
    if len(energies) != 1 or len(iterations) != 1:
        reasons.append("expected exactly one converged SCF energy")
    try:
        blocks = force_blocks(text, nat)
    except ValueError as error:
        blocks = []
        reasons.append(str(error))
    if len(blocks) != 1:
        reasons.append(f"expected one total-force block, found {len(blocks)}")
    head = header_numbers(text)
    if head["nat"] != nat:
        reasons.append("printed nat differs from the input")
    record = dict(status="REJECTED" if reasons else "VALID_SCF", reasons=reasons,
                  energy_Ry=energies[0] if len(energies) == 1 else None,
                  energy_eV=energies[0] * RY_TO_EV if len(energies) == 1 else None,
                  iterations=iterations[0] if len(iterations) == 1 else None,
                  n_contribution_blocks=count_contribution_blocks(text),
                  header=head, timers=timers(text), **magnetizations(text))
    record["forces_eV_A"] = blocks[0] if len(blocks) == 1 and not reasons else None
    return record


def final_coordinates(text: str, nat: int):
    """Symbols/positions (A) of the ``Begin final coordinates`` block, or None."""
    begin = text.rfind("Begin final coordinates")
    end = text.rfind("End final coordinates")
    if begin < 0 or end < begin:
        return None
    block = text[begin:end].replace("\r\n", "\n").split("\n")
    heads = [i for i, line in enumerate(block) if line.strip().upper().startswith("ATOMIC_POSITIONS")]
    if len(heads) != 1 or "angstrom" not in block[heads[0]].lower():
        return None
    rows = [line.split() for line in block[heads[0] + 1:] if line.strip()]
    if len(rows) != nat or any(len(r) not in (4, 7) for r in rows):
        return None
    try:
        return dict(symbols=[r[0] for r in rows], positions=[[number(x) for x in r[1:4]] for r in rows])
    except ValueError:
        return None


def parse_relax(text: str, nat: int) -> dict:
    """Relaxation descriptors used by the cost survey and the basin readout (no acceptance)."""
    energies = [number(m.group(1)) for m in ENERGY.finditer(text)]
    ok = [int(m.group(1)) for m in SCF_OK.finditer(text)]
    bad = [int(m.group(1)) for m in SCF_BAD.finditer(text)]
    bfgs = BFGS_OK.search(text)
    final = FINAL_ENERGY.findall(text)
    try:
        blocks = force_blocks(text, nat)
        force_error = None
    except ValueError as error:
        blocks, force_error = [], str(error)
    return dict(
        n_energies=len(energies), energies_Ry=energies, scf_iterations=ok, scf_failures=bad,
        bfgs_converged=bfgs is not None,
        bfgs_scf_cycles=int(bfgs.group(1)) if bfgs else None,
        bfgs_steps=int(bfgs.group(2)) if bfgs else None,
        max_steps_reached="The maximum number of steps has been reached" in text,
        final_energy_Ry=number(final[-1]) if final else None,
        force_blocks=blocks, force_error=force_error,
        final_coordinates=final_coordinates(text, nat),
        job_done=text.count("JOB DONE"),
        header=header_numbers(text), timers=timers(text), **magnetizations(text))


def free_fmax(forces: np.ndarray, if_pos) -> float | None:
    mask = np.array(if_pos, dtype=float)
    if mask.shape != forces.shape:
        raise ValueError("if_pos mask shape differs from the force array")
    if not mask.any():
        return None
    return float(np.max(np.linalg.norm(forces * mask, axis=1)))


def read_text(path) -> str:
    return Path(path).read_bytes().decode("utf-8", "replace")
