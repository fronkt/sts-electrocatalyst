"""Byte-safe Quantum ESPRESSO readers; force units are Ry/bohr.

Adsorbates are identified against a bare reference, never from an adsorbate
filename tag. Incomplete evidence remains explicit for the census to report.
"""
from __future__ import annotations

from collections import Counter
from decimal import Decimal
from pathlib import Path
import math
import re

_NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eEdD][+-]?\d+)?"
_FORCE = re.compile(r"^\s*atom\s+(\d+)\s+type\s+\d+\s+force\s*=\s*(" + _NUMBER + r")\s+(" + _NUMBER + r")\s+(" + _NUMBER + r")\s*$", re.I)


def _float(token):
    value = float(token.replace("D", "e").replace("d", "e"))
    if not math.isfinite(value):
        raise ValueError("non-finite printed value")
    if value == 0.0 and Decimal(token.replace("D", "e").replace("d", "e")) != 0:
        raise ValueError("nonzero printed value underflows float")
    return value


def _text(path):
    return Path(path).read_bytes().decode("utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")


def read_energies(path):
    """Return converged SCF total energies, in printed order, in Ry.

    Only QE's exclamation-mark total-energy records count: ordinary SCF
    iteration energies do not constitute additional ionic steps.
    """
    return [_float(m.group(1)) for m in re.finditer(
        r"^\s*!\s+total energy\s*=\s*(" + _NUMBER + r")\s+Ry\b", _text(path), re.M | re.I)]


def read_header(text):
    """Read both registered symmetry header grammars and preserve witnesses."""
    headers = []
    for line in text.splitlines():
        first = re.search(r"\b(\d+)\s+Sym\.\s*Ops\..*?\bfound\b", line, re.I)
        last = re.search(r"\bSym\.\s*Ops\..*?\bfound\s+(\d+)\b", line, re.I)
        if first:
            form = "count-first"
            form += ", no-inversion" if "no inversion" in line else ", with-inversion"
            if "fractional translation" in line:
                form += ", with-fractional-translation"
            headers.append({"n_symops": int(first.group(1)), "header_form": form})
        elif last:
            headers.append({"n_symops": int(last.group(1)), "header_form": "count-last"})
        elif re.search(r"\bNo symmetry found\b", line, re.I):
            headers.append({"n_symops": 1, "header_form": "no-symmetry"})
    counts = {h["n_symops"] for h in headers}
    return {"n_symops": headers[0]["n_symops"] if len(counts) == 1 else None,
            "header_form": headers[0]["header_form"] if headers else "none",
            "symmetry_headers": headers,
            "symmetry_conflict": len(counts) > 1}


def read_deck(path):
    """Parse namelist metadata, Cartesian atom positions and if_pos flags.

    Crystal positions are transformed using an explicit CELL_PARAMETERS card.
    Unsupported or incomplete coordinate systems are reported, never guessed.
    """
    path = Path(path)
    text = _text(path)
    # QE comments start at ! outside quoted strings.
    text = re.sub(r"'[^']*'|\"[^\"]*\"|![^\n]*", lambda m: "" if m.group(0).startswith("!") else m.group(0), text)
    issues = []
    def number(name, default=None):
        m = re.search(r"\b" + re.escape(name) + r"\s*=\s*(" + _NUMBER + r")", text, re.I)
        return _float(m.group(1)) if m else default
    def flag(name):
        m = re.search(r"\b" + name + r"\s*=\s*(\.?(?:true|false)\.?|[tf])\b", text, re.I)
        return m.group(1).strip(".").lower() in ("true", "t") if m else False
    nat_value = number("nat")
    nat = int(nat_value) if nat_value is not None else None
    lines = text.splitlines()
    cell, atoms, units = [], [], None
    for i, line in enumerate(lines):
        if re.match(r"\s*CELL_PARAMETERS\b", line, re.I):
            for row in lines[i + 1:i + 4]:
                try:
                    cell.append([_float(x) for x in row.split()[:3]])
                except ValueError:
                    cell = []
                    break
        if re.match(r"\s*ATOMIC_POSITIONS\b", line, re.I):
            units = re.sub(r"[(){}]", "", line).split()[1:]
            units = units[0].lower() if units else "alat"
            for row in lines[i + 1:]:
                fields = row.split()
                if len(fields) < 4 or not re.fullmatch(r"[A-Z][a-z]?\d*", fields[0]):
                    break
                try:
                    xyz = [_float(x) for x in fields[1:4]]
                    if len(fields) not in (4, 7):
                        raise ValueError("incomplete if_pos")
                    flags = [int(x) for x in fields[4:7]] if len(fields) == 7 else [1, 1, 1]
                    if any(x not in (0, 1) for x in flags):
                        raise ValueError("invalid if_pos")
                except ValueError:
                    issues.append("invalid atomic position or if_pos")
                    break
                atoms.append({"index": len(atoms) + 1, "species": re.sub(r"\d+$", "", fields[0]), "position": xyz, "if_pos": flags})
            continue
    if nat is None or len(atoms) != nat:
        issues.append("missing or incomplete ATOMIC_POSITIONS/nat")
    if units == "crystal":
        if len(cell) == 3 and all(len(row) == 3 for row in cell):
            for atom in atoms:
                p = atom["position"]
                atom["position"] = [sum(p[j] * cell[j][k] for j in range(3)) for k in range(3)]
        else:
            issues.append("crystal positions require CELL_PARAMETERS")
    elif units not in ("angstrom", "bohr", "alat", None):
        issues.append("unsupported coordinate units: " + units)
    u = {m.group(1): _float(m.group(2)) for m in re.finditer(r"^\s*U\s+(\S+)\s+(" + _NUMBER + r")", text, re.M)}
    u.update({"Hubbard_U(" + m.group(1) + ")": _float(m.group(2)) for m in re.finditer(r"\bHubbard_U\s*\(\s*(\d+)\s*\)\s*=\s*(" + _NUMBER + r")", text, re.I)})
    return {"path": path.as_posix(), "nat": nat, "atoms": atoms, "position_units": units,
            "nosym": flag("nosym"), "nspin": int(number("nspin", 1)),
            "tot_magnetization": number("tot_magnetization"), "U": u,
            "forc_conv_thr": number("forc_conv_thr", 1e-3), "issues": issues}


def _metals(deck):
    return Counter(a["species"] for a in deck["atoms"] if a["species"] not in {"O", "H"})


def _bare_candidates(path, deck):
    """Observed bare naming: slab/ref cards and Xu bare[-U-*] directories.

    Search locally first. In-house probe directories without a bare reference
    can reuse the same-metal production bare slab after matching atom counts.
    """
    folder = path.parent
    candidates = set()
    for directory in (folder, folder.parent):
        for pattern in ("slab*.in", "ref*.in", "bare*.in", "bare*/*.in"):
            candidates.update(directory.glob(pattern))
    runs = next((p for p in path.parents if p.name == "runs"), None)
    if runs is not None:
        for metal in _metals(deck):
            for suffix in ("_slab", "_anchor"):
                candidates.update((runs / (metal + suffix)).glob("slab*.in"))
    return sorted(candidates)


def _identify(path, deck):
    if deck["issues"]:
        return [], None, [], ["deck geometry incomplete"]
    metals = _metals(deck)
    if not metals:
        return [], None, [], ["no metal slab reference"]
    local = []
    for candidate in _bare_candidates(path, deck):
        try:
            bare = read_deck(candidate)
        except (OSError, ValueError):
            continue
        if bare["issues"] or _metals(bare) != metals:
            continue
        # A matching slab shares the species sequence of its prefix; adsorbate
        # tags and adsorption-state names do not enter this decision.
        local.append((candidate, bare["nat"]))
    counts = {nat for _, nat in local}
    if len(counts) != 1:
        return [], None, [], ["missing or inconsistent same-metal bare nat"]
    bare_nat = counts.pop()
    if bare_nat > deck["nat"]:
        return [], bare_nat, [str(p) for p, _ in local], ["bare nat exceeds adslab nat"]
    for candidate, _ in local:
        bare = read_deck(candidate)
        if [a["species"] for a in bare["atoms"]] != [a["species"] for a in deck["atoms"][:bare_nat]]:
            return [], bare_nat, [str(p) for p, _ in local], ["bare and adslab species prefixes disagree"]
    proposed = deck["atoms"][bare_nat:]
    top = max(a["position"][2] for a in deck["atoms"] if a["species"] not in {"O", "H"})
    if any(a["species"] not in {"O", "H"} or a["position"][2] <= top for a in proposed):
        return [], bare_nat, [str(p) for p, _ in local], ["bare-index and species/height rules disagree"]
    return [a["index"] for a in proposed], bare_nat, [str(p) for p, _ in local], []


def read_force_blocks(text):
    """Read delimited total-force blocks, keeping incomplete blocks explicit.

    Contribution rows remain in a separate state until the Total force trailer.
    A surviving orphan block is accepted only when that trailer witnesses it;
    the caller checks that every adsorbate atom survived, per the ruling.
    """
    steps, warnings, issues = [], [], []
    rows, state, orphan = {}, "outside", False
    def finish(terminated=False):
        nonlocal rows, state, orphan
        if state == "total":
            steps.append(rows)
            if orphan:
                warnings.append("recovered headerless force block")
                if not terminated:
                    issues.append("headerless force block lacks Total force delimiter")
        rows, state, orphan = {}, "outside", False
    for line in text.replace("\x00", "\n").splitlines():
        if "Forces acting on atoms" in line:
            finish()
            state = "total"
            continue
        if re.search(r"(?:contrib\.|contribution|SCF correction term).*\bforces\b", line, re.I):
            finish(True)
            state = "contribution"
            continue
        if re.match(r"\s*Total force\s*=", line, re.I):
            finish(True)
            continue
        match = _FORCE.match(line)
        if match:
            if state == "contribution":
                continue
            if state == "outside":
                state, orphan = "total", True
            index = int(match.group(1))
            if index in rows:
                issues.append("duplicate atom in force block")
            try:
                rows[index] = [_float(match.group(j)) for j in (2, 3, 4)]
            except ValueError as exc:
                issues.append("invalid atom force: " + str(exc))
        elif re.match(r"\s*atom\s+\d+\s+type\s+\d+\s+force\s*=", line):
            if state != "contribution":
                issues.append("malformed atom force row")
        elif line.strip() and state == "total" and rows:
            finish()
    finish()
    if not steps:
        issues.append("no total-force blocks")
    return steps, warnings, issues


def read_qe(path, deck_path=None):
    """Return raw QE evidence for census; atom indices are one-based."""
    path = Path(path)
    text = _text(path)
    header = read_header(text)
    steps, warnings, force_issues = read_force_blocks(text)
    companion = Path(deck_path) if deck_path is not None else path.with_suffix(".in")
    try:
        deck = read_deck(companion)
        ads, bare_nat, references, identification_issues = _identify(companion, deck)
    except (OSError, ValueError) as exc:
        deck = {"path": companion.as_posix(), "nat": None, "atoms": [], "nosym": None,
                "nspin": None, "tot_magnetization": None, "U": {}, "forc_conv_thr": 1e-3,
                "issues": [str(exc)]}
        ads, bare_nat, references, identification_issues = [], None, [], ["missing or invalid companion deck"]
    excluded = [a["index"] for a in deck["atoms"] if 0 in a["if_pos"]]
    eligible = [i for i in ads if i not in excluded]
    for i, step in enumerate(steps):
        if any(atom not in step for atom in ads):
            force_issues.append("force step %d missing adsorbate atoms" % (i + 1))
        if deck["nat"] is not None and any(atom < 1 or atom > deck["nat"] for atom in step):
            force_issues.append("force step %d has out-of-range atom index" % (i + 1))
    energies = [_float(m.group(1)) for m in re.finditer(r"^\s*!\s+total energy\s*=\s*(" + _NUMBER + r")\s+Ry\b", text, re.M | re.I)]
    return {"path": path.as_posix(), **header, "force_steps": steps,
            "force_issues": force_issues, "issues": warnings + deck["issues"] + identification_issues + force_issues,
            "deck": deck, "nosym_in_deck": deck["nosym"], "forc_conv_thr": deck["forc_conv_thr"],
            "adsorbate_indices": eligible, "identified_adsorbate_indices": ads,
            "n_adsorbate": len(ads) if not identification_issues else None,
            "excluded_indices": excluded, "n_if_pos_excluded": len(excluded),
            "unidentified": bool(identification_issues), "bare_nat": bare_nat, "bare_references": references,
            "energies_ry": energies, "force_units": "Ry/bohr", "nul_bytes": text.count("\x00"),
            "job_done": "JOB DONE." in text, "mpi_abort": "MPI_ABORT" in text}
