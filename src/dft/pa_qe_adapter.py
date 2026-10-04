"""Raw QE 7.5 adapter for the bounded first-boundary catalyst experiment.

This module does not launch a process or submit a job.  A pre-resume decision
selects a branch; acceptance of checkpoint consumption is a separate, post-hoc
audit.  Every result remains a numerical diagnostic, never a production step.
The initial four-file density seed is explicitly not a restart checkpoint.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import stat
import xml.etree.ElementTree as ET

if __package__:
    from . import pa_checked_contract as contract
else:
    import pa_checked_contract as contract


BOHR_ANGSTROM = 0.529177210903
# QE7.5 Modules/constants.f90: Hartree joules / electron-volt joules / e2.
RY_EV = (4.3597447222071e-18 / 1.602176634e-19) / 2
RY_MEV = contract.RY_MEV
TOLERANCES = {"energy_Ry": 1e-6, "position_bohr": 1e-5,
              "force_Ry_bohr": 1e-5}
NUM = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eEdD][+-]?\d+)?"
FAILURE = re.compile(
    r"convergence NOT achieved|Error in routine|MPI_ABORT|SIGTERM|SIGINT|"
    r"SIGSEGV|Segmentation fault|Floating point exception|forrtl:\s*severe|"
    r"IEEE_(?:INVALID|OVERFLOW|DIVIDE_BY_ZERO)_FLAG", re.I)
STOP = "Program stopped by user request"
SEED_FILES = {"charge-density.hdf5", "data-file-schema.xml", "occup.txt", "paw.txt"}
OPERATIONAL = {
    "control": {"calculation", "restart_mode", "prefix", "outdir", "wfcdir",
                "pseudo_dir", "nstep", "max_seconds"},
    "electrons": {"startingpot", "startingwfc"},
}


class AdapterError(ValueError):
    pass


def _hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _json_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode("utf-8")).hexdigest()


def _number(text):
    if isinstance(text, bool):
        raise AdapterError("boolean is not a numerical value")
    try:
        value = float(str(text).replace("D", "e").replace("d", "e"))
    except (TypeError, ValueError, OverflowError) as error:
        raise AdapterError("malformed numerical value") from error
    if not math.isfinite(value):
        raise AdapterError("nonfinite numerical value")
    return value


def _numbers(text, count=None):
    values = [_number(v) for v in (text or "").split()]
    if not values or (count is not None and len(values) != count):
        raise AdapterError("wrong numerical array dimensions")
    return values


def _safe_path(value, *, directory=None, exists=True):
    """Reject symlink ancestors as well as a symlink/special leaf."""
    raw = Path(value).absolute()
    for candidate in [raw] + list(raw.parents):
        try:
            info = candidate.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode):
            raise AdapterError("symlink path or ancestor: " + str(candidate))
        if candidate != raw and not stat.S_ISDIR(info.st_mode):
            raise AdapterError("non-directory path ancestor")
    resolved = raw.resolve(strict=exists)
    if resolved == Path(resolved.anchor):
        raise AdapterError("filesystem root is outside adapter scope")
    if exists:
        info = resolved.lstat()
        wanted = stat.S_ISDIR if directory else stat.S_ISREG
        if directory is not None and not wanted(info.st_mode):
            raise AdapterError("path is not an ordinary " + ("directory" if directory else "file"))
    return resolved


def _source(path, first=1, last=None):
    path = _safe_path(path, directory=False)
    if last is None:
        last = max(1, len(path.read_bytes().splitlines()))
    return {"path": str(path), "sha256": _hash(path),
            "line_start": first, "line_end": last}


def _read(path, expected_sha256=None):
    path = _safe_path(path, directory=False)
    raw = path.read_bytes()
    source = {"path": str(path), "sha256": hashlib.sha256(raw).hexdigest(),
              "line_start": 1, "line_end": max(1, len(raw.splitlines()))}
    if expected_sha256 is not None and source["sha256"] != expected_sha256:
        raise AdapterError("source pin differs: " + source["path"])
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise AdapterError("raw source is not UTF-8") from error
    return text, source


def _uncomment(line):
    quote = None
    for i, character in enumerate(line):
        if character in "'\"":
            if quote is None:
                quote = character
            elif quote == character:
                quote = None
        elif character == "!" and quote is None:
            return line[:i].strip()
    return line.strip()


def _literal(text):
    text = text.strip().rstrip(",").strip()
    if re.fullmatch(NUM, text):
        return _number(text)
    if text.lower() in {".true.", ".false."}:
        return text.lower() == ".true."
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "'\"":
        return text[1:-1]
    raise AdapterError("unsupported or ambiguous input literal: " + text)


def _integer(value, label, minimum=0):
    if isinstance(value, bool) or type(value) not in (int, float) or int(value) != value or value < minimum:
        raise AdapterError("invalid integer " + label)
    return int(value)


def parse_deck(path, expected_sha256=None):
    """Parse the supported explicit fixed-cell QE deck, retaining exact pins.

    The adapter supports bohr/angstrom Cartesian cards, automatic/gamma k-points,
    and the atomic HUBBARD card.  Unknown cards and duplicate assignments fail.
    QE if_pos is retained and inverted coordinate by coordinate for the contract.
    """
    text, source = _read(path, expected_sha256)
    lines = [_uncomment(line) for line in text.splitlines()]
    sections, cards = {}, {}
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line:
            i += 1
            continue
        if line.startswith("&"):
            name = line[1:].lower()
            if name not in {"control", "system", "electrons", "ions"} or name in sections:
                raise AdapterError("unknown or duplicated namelist")
            sections[name] = {}
            i += 1
            while i < len(lines) and lines[i] != "/":
                if lines[i]:
                    match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*(?:\(\d+\))?)\s*=\s*(.+)", lines[i])
                    if not match:
                        raise AdapterError("one explicit assignment per input line required")
                    key = match.group(1).lower()
                    if key in sections[name]:
                        raise AdapterError("duplicate input assignment: " + key)
                    sections[name][key] = _literal(match.group(2))
                i += 1
            if i == len(lines):
                raise AdapterError("unterminated namelist")
            i += 1
            continue
        match = re.fullmatch(r"(ATOMIC_SPECIES|CELL_PARAMETERS|ATOMIC_POSITIONS|K_POINTS|HUBBARD)(?:\s*(?:\(([^)]+)\)|\{([^}]+)\}|([^\s]+)))?", line, re.I)
        if not match:
            raise AdapterError("unknown or malformed input card: " + line)
        name = match.group(1).upper()
        unit = next((v for v in match.groups()[1:] if v is not None), "").lower()
        if name in cards:
            raise AdapterError("duplicate input card")
        system = sections.get("system", {})
        count = {"ATOMIC_SPECIES": system.get("ntyp"), "CELL_PARAMETERS": 3,
                 "ATOMIC_POSITIONS": system.get("nat"),
                 "K_POINTS": 0 if unit == "gamma" else 1}.get(name)
        i += 1
        if name == "HUBBARD":
            if unit != "atomic":
                raise AdapterError("only the pinned atomic HUBBARD projector is supported")
            rows = []
            while i < len(lines):
                if lines[i]:
                    if not re.fullmatch(r"U\s+[A-Za-z][A-Za-z0-9_]*-[0-9]+[spdf]\s+" + NUM, lines[i]):
                        raise AdapterError("unsupported HUBBARD row")
                    rows.append(lines[i].split())
                i += 1
            if not rows:
                raise AdapterError("empty HUBBARD card")
        else:
            count = _integer(count, name + " row count")
            rows = []
            while len(rows) < count and i < len(lines):
                if lines[i]:
                    rows.append(lines[i].split())
                i += 1
            if len(rows) != count:
                raise AdapterError("incomplete input card")
        cards[name] = {"unit": unit, "rows": rows}
    if not {"control", "system", "electrons"} <= set(sections):
        raise AdapterError("required namelists missing")
    if not {"ATOMIC_SPECIES", "CELL_PARAMETERS", "ATOMIC_POSITIONS", "K_POINTS"} <= set(cards):
        raise AdapterError("required explicit input cards missing")
    system = sections["system"]
    if system.get("ibrav") != 0:
        raise AdapterError("explicit fixed cell with ibrav=0 required")
    nat, ntyp = _integer(system.get("nat"), "nat", 1), _integer(system.get("ntyp"), "ntyp", 1)
    upfs = []
    for row in cards["ATOMIC_SPECIES"]["rows"]:
        if len(row) != 3 or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", row[0]):
            raise AdapterError("malformed atomic species")
        if Path(row[2]).name != row[2] or "/" in row[2] or "\\" in row[2] or ":" in row[2]:
            raise AdapterError("UPF filename must be a safe basename")
        mass = _number(row[1])
        if mass <= 0:
            raise AdapterError("positive atomic mass required")
        upfs.append({"species": row[0], "mass": mass, "filename": row[2]})
    if len(set(v["species"] for v in upfs)) != ntyp:
        raise AdapterError("duplicate species identity")
    if cards.get("HUBBARD") is not None:
        hubbard_labels = [row[1] for row in cards["HUBBARD"]["rows"]]
        if len(hubbard_labels) != len(set(hubbard_labels)) or any(
                label.rsplit("-", 1)[0] not in {v["species"] for v in upfs} for label in hubbard_labels):
            raise AdapterError("Hubbard species identity/order is ambiguous")
    species, positions, if_pos = [], [], []
    for row in cards["ATOMIC_POSITIONS"]["rows"]:
        if len(row) not in (4, 7) or row[0] not in {v["species"] for v in upfs}:
            raise AdapterError("malformed atomic position or species")
        species.append(row[0])
        positions.append([_number(v) for v in row[1:4]])
        flags = row[4:] if len(row) == 7 else ["1", "1", "1"]
        if any(v not in {"0", "1"} for v in flags):
            raise AdapterError("QE if_pos must contain three integer binary flags")
        if_pos.append([int(v) for v in flags])
    if len(positions) != nat:
        raise AdapterError("atom count mismatch")
    cell = [[_number(v) for v in row] for row in cards["CELL_PARAMETERS"]["rows"]]
    if any(len(row) != 3 for row in cell):
        raise AdapterError("three explicit cell vectors required")
    for name, matrix in (("ATOMIC_POSITIONS", positions), ("CELL_PARAMETERS", cell)):
        unit = cards[name]["unit"]
        if unit not in {"bohr", "angstrom"}:
            raise AdapterError("explicit bohr or angstrom input units required")
        if unit == "angstrom":
            matrix[:] = [[v / BOHR_ANGSTROM for v in row] for row in matrix]
    if abs(_determinant(cell)) < 1e-10:
        raise AdapterError("singular cell")
    kpoints = cards["K_POINTS"]
    if kpoints["unit"] == "automatic":
        if len(kpoints["rows"][0]) != 6 or any(not re.fullmatch(r"\d+", v) for v in kpoints["rows"][0]):
            raise AdapterError("automatic k-point mesh requires six integers")
        mesh = [int(v) for v in kpoints["rows"][0]]
        if any(v <= 0 for v in mesh[:3]) or any(v not in (0, 1) for v in mesh[3:]):
            raise AdapterError("invalid k-point mesh or shift")
    elif kpoints["unit"] != "gamma":
        raise AdapterError("unsupported k-point card")
    control, electrons = sections["control"], sections["electrons"]
    if "max_xml_steps" in control:
        raise AdapterError("MAX_XML_STEPS is an environment variable, not a QE control keyword")
    calculation = control.get("calculation")
    if calculation not in {"scf", "relax"}:
        raise AdapterError("only the scoped SCF/relax calculation is supported")
    restart = control.get("restart_mode", "from_scratch")
    if restart not in {"from_scratch", "restart"}:
        raise AdapterError("unsupported restart mode")
    threshold = _number(electrons.get("conv_thr"))
    if threshold <= 0:
        raise AdapterError("positive explicit SCF threshold required")
    common = {name: {key: value for key, value in values.items()
                     if key not in OPERATIONAL.get(name, set())}
              for name, values in sections.items()}
    settings = {"namelists": common, "atomic_species": upfs,
                "k_points": kpoints, "hubbard": cards.get("HUBBARD")}
    operations = {key: control.get(key) for key in OPERATIONAL["control"]}
    operations.update({key: electrons.get(key) for key in OPERATIONAL["electrons"]})
    operations["restart_mode"] = restart
    return {"source": source, "nat": nat, "ntyp": ntyp, "upfs": upfs,
            "geometry": {"unit": "bohr", "species": species, "positions": positions,
                         "cell": cell, "fixed_flags": [[1-v for v in row] for row in if_pos]},
            "qe_if_pos": if_pos, "source_position_unit": cards["ATOMIC_POSITIONS"]["unit"],
            "source_cell_unit": cards["CELL_PARAMETERS"]["unit"],
            "operations": operations, "settings": settings,
            "settings_identity": _json_hash(settings), "conv_thr_Ry": threshold}


def _determinant(cell):
    a, b, c = cell
    return (a[0]*(b[1]*c[2]-b[2]*c[1]) - a[1]*(b[0]*c[2]-b[2]*c[0])
            + a[2]*(b[0]*c[1]-b[1]*c[0]))


def validate_upfs(deck, pseudo_dir, expected_pins):
    """Reopen and pin every external UPF before an invocation."""
    root = _safe_path(pseudo_dir, directory=True)
    names = {v["filename"] for v in deck["upfs"]}
    if set(expected_pins) != names:
        raise AdapterError("UPF pins must exactly cover the source species")
    result = {}
    for name in sorted(names):
        source = _source(root / name)
        if not contract.SHA256.fullmatch(str(expected_pins[name])) or source["sha256"] != expected_pins[name]:
            raise AdapterError("external UPF pin differs: " + name)
        result[name] = {**source, "md5": hashlib.md5((root / name).read_bytes()).hexdigest()}
    return result


def render_trial_deck(source_text, *, arm_kind, prefix, outdir, pseudo_dir,
                      wfcdir=None, geometry=None, max_seconds=7080, nstep=30):
    """Render only the explicitly declared trial operational substitutions.

    Reparse the resulting file with parse_deck and compare common settings before
    use.  The source's numerical/physical assignments and input constraint flags
    remain visible.  Fresh SCF starts from atomic potential/wavefunctions; reseed
    and initial controls use the pinned electronic density with fresh WFCs.
    """
    if arm_kind not in {"control", "candidate", "continuous", "candidate-stop",
                        "resumed", "negative", "negative-fresh", "fresh", "reseed"}:
        raise AdapterError("unknown registered trial arm")
    if not re.fullmatch(r"[A-Za-z0-9_]+", prefix):
        raise AdapterError("safe trial prefix required")
    if _integer(max_seconds, "max_seconds", 1) > 7080 or _integer(nstep, "nstep", 30) > 200:
        raise AdapterError("trial stop allowance or spare ionic-loop budget differs")
    text = source_text
    def field(namelist, key, value):
        nonlocal text
        pattern = r"(?mi)^([ \t]*" + re.escape(key) + r"[ \t]*=[ \t]*)[^\r\n]*$"
        text, count = re.subn(pattern, lambda m: m.group(1)+value, text)
        if count > 1:
            raise AdapterError("ambiguous operational substitution")
        if count == 0:
            text, count = re.subn(r"(?mi)^([ \t]*&" + namelist + r"[ \t]*)$",
                                  lambda m: m.group(1)+"\n  "+key+" = "+value, text)
            if count != 1:
                raise AdapterError("missing operational namelist")
    def literal_path(value):
        path = str(Path(value).absolute()).replace("\\", "/")
        if any(character in path for character in "'\"\r\n"):
            raise AdapterError("unsafe runtime path literal")
        return "'"+path+"'"
    field("control", "calculation", "'scf'" if arm_kind == "fresh" else "'relax'")
    field("control", "restart_mode", "'restart'" if arm_kind == "resumed" else "'from_scratch'")
    field("control", "prefix", "'"+prefix+"'")
    field("control", "outdir", literal_path(outdir))
    field("control", "pseudo_dir", literal_path(pseudo_dir))
    if wfcdir is not None:
        field("control", "wfcdir", literal_path(wfcdir))
    elif re.search(r"(?mi)^\s*wfcdir\s*=", source_text):
        raise AdapterError("source has a distinct WFC tree; explicit runtime path required")
    field("control", "max_seconds", str(max_seconds))
    field("control", "nstep", str(nstep))
    field("electrons", "startingwfc", "'file'" if arm_kind == "resumed" else "'atomic+random'")
    field("electrons", "startingpot", "'atomic'" if arm_kind == "fresh" else "'file'")
    if geometry is not None:
        geometry = contract._geometry(geometry, "runtime")
        pattern = r"(?mi)^\s*ATOMIC_POSITIONS[^\r\n]*\r?\n"
        matches = list(re.finditer(pattern, text))
        if len(matches) != 1:
            raise AdapterError("one runtime position card required")
        start = matches[0].start()
        end = matches[0].end()
        rows = text[end:].splitlines(keepends=True)
        if len(rows) < len(geometry["species"]):
            raise AdapterError("incomplete source geometry")
        original = [row.split() for row in rows[:len(geometry["species"])]]
        if [row[0] for row in original] != geometry["species"]:
            raise AdapterError("runtime geometry changes source atom order")
        original_flags = [[int(v) for v in row[4:7]] if len(row) == 7 else [1, 1, 1] for row in original]
        if original_flags != [[1-v for v in flags] for flags in geometry["fixed_flags"]]:
            raise AdapterError("runtime geometry changes source constraints")
        position_text = "ATOMIC_POSITIONS bohr\n" + "\n".join(
            "  "+species+" "+" ".join(format(v, ".17g") for v in position)+" "+
            " ".join(str(1-v) for v in flags)
            for species, position, flags in zip(geometry["species"], geometry["positions"], geometry["fixed_flags"]))+"\n"
        text = text[:start]+position_text+"".join(rows[len(geometry["species"]):])
    return text


def _tag(node):
    return node.tag.rsplit("}", 1)[-1]


def _one(node, name):
    values = [v for v in node if _tag(v) == name]
    if len(values) != 1:
        raise AdapterError("one XML " + name + " required")
    return values[0]


def _xml_bool(node):
    text = (node.text or "").strip()
    if text not in {"true", "false"}:
        raise AdapterError("explicit XML boolean required")
    return text == "true"


def _schema_smearing(value):
    """QE7.5 PW/src/set_occupations.f90 schema_smearing aliases, not labels.

    In particular, cold/Marzari-Vanderbilt input aliases serialize as ``mv``;
    accepting ``cold`` in XML would hide a source-schema mismatch.
    """
    aliases = {
        "gaussian": {"gaussian", "gauss", "Gaussian", "Gauss"},
        "mp": {"methfessel-paxton", "m-p", "mp", "Methfessel-Paxton", "M-P", "MP"},
        "mv": {"marzari-vanderbilt", "cold", "m-v", "mv", "Marzari-Vanderbilt", "M-V", "MV"},
        "fd": {"fermi-dirac", "f-d", "fd", "Fermi-Dirac", "F-D", "FD"},
    }
    for canonical, names in aliases.items():
        if value in names:
            return canonical
    raise AdapterError("unsupported source smearing")


def _xml_geometry(node, deck):
    structure = _one(node, "atomic_structure")
    if structure.attrib.get("nat") != str(deck["nat"]):
        raise AdapterError("XML atom count differs")
    atoms = list(_one(structure, "atomic_positions"))
    expected = list(zip(deck["geometry"]["species"], map(str, range(1, deck["nat"] + 1))))
    if [(_tag(a), a.attrib.get("name"), a.attrib.get("index")) for a in atoms] != [
            ("atom", species, index) for species, index in expected]:
        raise AdapterError("XML atom case/identity/order differs")
    cell_node = _one(structure, "cell")
    if [_tag(v) for v in cell_node] != ["a1", "a2", "a3"]:
        raise AdapterError("XML cell vector order differs")
    cell = [_numbers(v.text, 3) for v in cell_node]
    if _matrix_delta(cell, deck["geometry"]["cell"]) > 1e-7:
        raise AdapterError("XML cell differs from source")
    return {"unit": "bohr", "species": list(deck["geometry"]["species"]),
            "positions": [_numbers(a.text, 3) for a in atoms], "cell": cell,
            "fixed_flags": copy.deepcopy(deck["geometry"]["fixed_flags"])}


def _matrix_delta(left, right):
    if len(left) != len(right) or any(len(a) != len(b) for a, b in zip(left, right)):
        raise AdapterError("matrix dimensions differ")
    return max(abs(_number(a)-_number(b)) for row, other in zip(left, right) for a, b in zip(row, other))


def _geometry_matches(left, right, tolerance=1e-7):
    return (left["species"] == right["species"] and left["fixed_flags"] == right["fixed_flags"]
            and _matrix_delta(left["cell"], right["cell"]) <= tolerance
            and _matrix_delta(left["positions"], right["positions"]) <= tolerance)


def _xml_evaluation(node, deck, source):
    convergence = (_one(node, "scf_conv") if _tag(node) == "step" else
                   _one(_one(node, "convergence_info"), "scf_conv"))
    if not _xml_bool(_one(convergence, "convergence_achieved")):
        raise AdapterError("XML evaluation has no converged SCF")
    energy = _numbers(_one(_one(node, "total_energy"), "etot").text, 1)[0] * 2
    forces = _one(node, "forces")
    if forces.attrib.get("rank") != "2" or _numbers(forces.attrib.get("dims"), 2) != [3, deck["nat"]]:
        raise AdapterError("XML force dimensions differ")
    values = _numbers(forces.text, 3*deck["nat"])
    return {"geometry_role": "evaluated", "status": "CONVERGED", "scf_converged": True,
            "geometry": _xml_geometry(node, deck), "energy_unit": "Ry", "geometry_unit": "bohr",
            "force_unit": "Ry/bohr", "energy_Ry": energy,
            "forces_Ry_bohr": [[2*v for v in values[i:i+3]] for i in range(0, len(values), 3)],
            "settings_identity": deck["settings_identity"], "source": source}


def _xml_common(node, parents=()):
    """Canonical complete XML input, excluding only declared operational fields."""
    name = _tag(node)
    parent = parents[-1] if parents else ""
    if name == "atomic_structure":
        return None
    if parent == "control_variables" and name in {
            "title", "calculation", "restart_mode", "prefix", "pseudo_dir", "outdir",
            "wfcdir", "max_seconds", "nstep", "max_xml_steps", "print_every"}:
        return None
    if parent == "electron_control" and name in {"startingpot", "startingwfc"}:
        return None
    attributes = {key: value for key, value in sorted(node.attrib.items())
                  if not (name == "atomic_species" and key == "pseudo_dir")}
    children = [_xml_common(child, parents + (name,)) for child in node]
    return {"tag": name, "attributes": attributes, "text": " ".join((node.text or "").split()),
            "children": [child for child in children if child is not None]}


def _check_xml_input(root, deck):
    node = _one(root, "input")
    if not _geometry_matches(_xml_geometry(node, deck), deck["geometry"]):
        raise AdapterError("XML input geometry differs from actual input")
    species = _one(node, "atomic_species")
    rows = []
    for child in species:
        rows.append({"species": child.attrib.get("name"),
                     "mass": _number(_one(child, "mass").text),
                     "filename": (_one(child, "pseudo_file").text or "").strip()})
    if rows != deck["upfs"]:
        raise AdapterError("XML species/UPF identities differ from actual input")
    flags = _one(node, "free_positions")
    if _numbers(flags.attrib.get("dims"), 2) != [3, deck["nat"]]:
        raise AdapterError("XML constraint dimensions differ")
    free = _numbers(flags.text, 3*deck["nat"])
    if free != [v for row in deck["qe_if_pos"] for v in row]:
        raise AdapterError("XML QE if_pos differs from actual input")
    electron = _one(node, "electron_control")
    if abs(2*_number(_one(electron, "conv_thr").text)-deck["conv_thr_Ry"]) > 1e-15:
        raise AdapterError("XML input SCF threshold differs")
    basis = _one(node, "basis")
    for key in ("ecutwfc", "ecutrho"):
        if abs(2*_number(_one(basis, key).text)-deck["settings"]["namelists"]["system"][key]) > 1e-10:
            raise AdapterError("XML cutoff differs from source")
    spin = _one(node, "spin")
    if _xml_bool(_one(spin, "lsda")) != (deck["settings"]["namelists"]["system"].get("nspin", 1) == 2):
        raise AdapterError("XML spin setting differs")
    _check_xml_common_source(node, deck)
    return _json_hash(_xml_common(node))


def _check_xml_common_source(node, deck):
    """Check explicit source physical/solver values against official XML fields."""
    sections = deck["settings"]["namelists"]
    system, electrons = sections["system"], sections["electrons"]
    control, ions = sections["control"], sections.get("ions", {})
    def value(parent, tag, expected, factor=1):
        child = _one(parent, tag)
        if type(expected) is bool:
            agrees = _xml_bool(child) == expected
        elif type(expected) in (int, float):
            agrees = abs(_number(child.text)*factor-expected) <= 1e-12*max(1., abs(expected))
        else:
            agrees = (child.text or "").strip() == expected
        if not agrees:
            raise AdapterError("XML source setting differs: " + tag)
    xml_control = _one(node, "control_variables")
    for source_key, xml_key, factor in (("tprnfor", "forces", 1), ("tstress", "stress", 1),
                                       ("forc_conv_thr", "forc_conv_thr", 2),
                                       ("etot_conv_thr", "etot_conv_thr", 2),
                                       ("disk_io", "disk_io", 1)):
        if source_key in control:
            value(xml_control, xml_key, control[source_key], factor)
    electron = _one(node, "electron_control")
    for source_key, xml_key in (("mixing_mode", "mixing_mode"), ("mixing_beta", "mixing_beta"),
                                ("mixing_ndim", "mixing_ndim"), ("electron_maxstep", "max_nstep"),
                                ("diagonalization", "diagonalization"), ("diago_thr_init", "diago_thr_init"),
                                ("diago_full_acc", "diago_full_acc")):
        if source_key in electrons:
            value(electron, xml_key, electrons[source_key])
    xml_ions = _one(node, "ion_control")
    for key in ("ion_dynamics", "upscale", "remove_rigid_rot", "refold_pos"):
        if key in ions:
            value(xml_ions, key, ions[key])
    if "bfgs_ndim" in ions:
        value(_one(xml_ions, "bfgs"), "ndim", ions["bfgs_ndim"])
    for key in ("trust_radius_min", "trust_radius_max", "trust_radius_ini"):
        if key in ions:
            value(_one(xml_ions, "bfgs"), "trust_radius_init" if key == "trust_radius_ini" else key, ions[key])
    spin = _one(node, "spin")
    for key in ("noncolin", "lspinorb"):
        value(spin, "spinorbit" if key == "lspinorb" else key, system.get(key, False))
    species = list(_one(node, "atomic_species"))
    for index, row in enumerate(species, 1):
        key = "starting_magnetization({})".format(index)
        if key in system and any(system.get("starting_magnetization({})".format(i), 0) != 0
                                 for i in range(1, deck["ntyp"]+1)):
            value(row, "starting_magnetization", system[key])
    bands = _one(node, "bands")
    for key in ("occupations", "tot_charge", "nbnd"):
        if key in system:
            value(bands, key, system[key])
    if system.get("occupations") == "smearing":
        smearing = _one(bands, "smearing")
        if (smearing.text or "").strip() != _schema_smearing(system["smearing"]) or abs(
                2*_number(smearing.attrib.get("degauss"))-system["degauss"]) > 1e-12:
            raise AdapterError("XML source smearing or width differs")
    if any(key in system for key in ("nosym", "noinv", "nosym_evc", "no_t_rev")):
        symmetry = _one(node, "symmetry_flags")
        for key in ("nosym", "noinv", "nosym_evc", "no_t_rev"):
            if key in system:
                value(symmetry, key, system[key])
    points = _one(node, "k_points_IBZ")
    if deck["settings"]["k_points"]["unit"] == "automatic":
        mesh = _one(points, "monkhorst_pack")
        expected = [int(v) for v in deck["settings"]["k_points"]["rows"][0]]
        actual = [_integer(_number(mesh.attrib.get(key)), "XML k-point grid")
                  for key in ("nk1", "nk2", "nk3", "k1", "k2", "k3")]
        if actual != expected:
            raise AdapterError("XML source k-point mesh/offset differs")
    else:
        value(_one(node, "basis"), "gamma_only", True)
    functional = (_one(_one(node, "dft"), "functional").text or "").strip()
    if functional != system.get("input_dft", "PBE"):
        raise AdapterError("XML functional differs from pinned PBE source")
    dft = _one(node, "dft")
    dftu_nodes = [child for child in dft if _tag(child) == "dftU"]
    source_hubbard = deck["settings"]["hubbard"]
    if source_hubbard is None:
        if dftu_nodes:
            raise AdapterError("XML Hubbard correction has no source card")
    else:
        if len(dftu_nodes) != 1:
            raise AdapterError("one source-matched XML Hubbard correction required")
        dftu = dftu_nodes[0]
        value(dftu, "lda_plus_u", True)
        value(dftu, "lda_plus_u_kind", 0)
        value(dftu, "U_projection_type", source_hubbard["unit"])
        expected = {(row[1].rsplit("-", 1)[0], row[1].rsplit("-", 1)[1]): _number(row[2])
                    for row in source_hubbard["rows"]}
        actual = {}
        for child in dftu:
            tag = _tag(child)
            if tag == "Hubbard_U":
                key = (child.attrib.get("specie"), child.attrib.get("label"))
                if key in actual:
                    raise AdapterError("duplicate XML Hubbard_U")
                actual[key] = _number(child.text)*2*RY_EV
            elif tag in {"Hubbard_J0", "Hubbard_alpha", "Hubbard_alpha_back", "Hubbard_beta", "Hubbard_J"}:
                if any(v != 0 for v in _numbers(child.text)):
                    raise AdapterError("unregistered nonzero XML Hubbard correction")
        if set(actual) != set(expected) or any(abs(actual[key]-expected[key]) > 1e-10 for key in actual):
            raise AdapterError("XML Hubbard_U species/shell/eV setting differs")


def validate_saved_upfs(outdir, prefix, deck, expected_pins):
    """Validate XML identity and any checkpoint-local UPFs before a copy runs."""
    if not re.fullmatch(r"[A-Za-z0-9_]+", prefix):
        raise AdapterError("safe checkpoint prefix required")
    save = _safe_path(Path(outdir) / (prefix+".save"), directory=True)
    text, source = _read(save / "data-file-schema.xml")
    try:
        root = ET.fromstring(text)
    except ET.ParseError as error:
        raise AdapterError("malformed checkpoint XML") from error
    result = {}
    for section in ("input", "output"):
        names = [(v.attrib.get("name"), (_one(v, "pseudo_file").text or "").strip())
                 for v in _one(_one(root, section), "atomic_species")]
        if names != [(v["species"], v["filename"]) for v in deck["upfs"]]:
            raise AdapterError("checkpoint XML species/UPF identity differs")
    if set(expected_pins) != {v["filename"] for v in deck["upfs"]}:
        raise AdapterError("complete external UPF pin map required")
    for name, digest in expected_pins.items():
        target = save / name
        if target.exists() or target.is_symlink():
            pinned = _source(target)
            if pinned["sha256"] != digest:
                raise AdapterError("checkpoint-local UPF pin differs")
            result[name] = {"present": True, "source": pinned}
        else:
            result[name] = {"present": False, "external_pinned_fallback_required": True}
    return {"xml_source": source, "files": result}


def _xml_source_ranges(text, source, name):
    matches = list(re.finditer(r"<(?:[A-Za-z_][\w.-]*:)?" + name +
                              r"(?:\s[^>]*)?>.*?</(?:[A-Za-z_][\w.-]*:)?" + name + r"\s*>", text, re.S))
    return [{**source, "line_start": text[:m.start()].count("\n") + 1,
             "line_end": text[:m.end()].count("\n") + 1} for m in matches]


def _raw_upf_reads(text, deck, pins, read_path_map=None):
    if set(pins) != {v["filename"] for v in deck["upfs"]}:
        raise AdapterError("exact external UPF SHA256 pins required")
    reads = list(re.finditer(r"PseudoPot\.\s*#\s*(\d+)\s+for\s+(\S+)\s+read from file:[ \t]*\n?[ \t]*([^\r\n]+)", text))
    md5s = re.findall(r"MD5 check sum:\s*([a-f0-9]{32})", text)
    if len(reads) != len(deck["upfs"]) or len(md5s) != len(reads):
        raise AdapterError("one actual UPF read and MD5 per source species required")
    result = []
    for index, (match, pseudo, md5) in enumerate(zip(reads, deck["upfs"], md5s), 1):
        if int(match.group(1)) != index or match.group(2) != pseudo["species"]:
            raise AdapterError("actual UPF species/type order differs")
        recorded_path = match.group(3).strip()
        actual = _safe_path((read_path_map or {}).get(recorded_path, recorded_path), directory=False)
        if actual.name != pseudo["filename"] or _hash(actual) != pins[actual.name]:
            raise AdapterError("actual consumed UPF path/hash differs")
        if hashlib.md5(actual.read_bytes()).hexdigest() != md5:
            raise AdapterError("logged consumed UPF MD5 differs")
        result.append({**_source(actual), "species": pseudo["species"], "md5": md5,
                       "actual_logged_read_path": recorded_path,
                       "retained_mirror_used": str(actual) != recorded_path})
    return result


def _raw_parallel(text, source, expected):
    """Bind runtime layout separately from XML band-group metadata.

    Only the registered catalyst shape and retained one-process tiny shape are
    supported.  XML ndiag does not prove the actual ELPA subgroup: the catalyst
    must print its 4*4 ELPA group independently.
    """
    catalyst = {"nprocs": 128, "nthreads": 1, "ntasks": 1,
                "nbgrp": 1, "npool": 8, "ndiag": 16}
    serial = {key: 1 for key in catalyst}
    if expected not in (catalyst, serial):
        raise AdapterError("unregistered raw runtime parallel shape")
    evidence = {}
    def matched(name, pattern, optional=False):
        # Raw evidence is byte-bound and may retain Windows CRLF fixtures.
        pattern = pattern[:-1] + r"\r?$"
        matches = list(re.finditer(pattern, text, re.M))
        if optional and not matches:
            return None
        if len(matches) != 1:
            raise AdapterError("one raw runtime " + name + " line required")
        match = matches[0]
        span = {**source, "line_start": text[:match.start()].count("\n")+1,
                "line_end": text[:match.end()].count("\n")+1}
        evidence[name] = {"line": match.group(0), "source": span}
        return [_integer(_number(value), "raw runtime " + name, 1) for value in match.groups()]
    processes = matched("mpi_processes", r"^[ \t]*Number of MPI processes:[ \t]*(\d+)[ \t]*$")[0]
    threads = matched("threads_per_mpi", r"^[ \t]*Threads/MPI process:[ \t]*(\d+)[ \t]*$")[0]
    cores = matched("processor_cores", r"^[ \t]*Parallel version \(MPI & OpenMP\), running on[ \t]*(\d+)[ \t]+processor cores[ \t]*$")[0]
    if processes != expected["nprocs"] or threads != expected["nthreads"] or cores != processes*threads:
        raise AdapterError("actual stdout MPI/process/thread shape differs")
    pool = matched("kpoint_pools", r"^[ \t]*K-points division:[ \t]*npool[ \t]*=[ \t]*(\d+)[ \t]*$", optional=expected == serial)
    division = matched("proc_per_band_pool_image", r"^[ \t]*R & G space division:[ \t]*proc/nbgrp/npool/nimage[ \t]*=[ \t]*(\d+)[ \t]*$", optional=expected == serial)
    if expected == serial:
        matched("serial_diagonalization", r"^[ \t]*a serial algorithm will be used[ \t]*$")
        if "ELPA distributed-memory algorithm" in text or (pool is not None and pool != [1]) or (division is not None and division != [1]):
            raise AdapterError("serial tiny runtime layout differs")
        defaults = {"npool": "one MPI process and bound serial algorithm"} if pool is None else {}
        if division is None:
            defaults["proc_per_band_pool_image"] = "one MPI process and bound serial algorithm"
        subgroup = None
        algorithm = "serial"
    else:
        if pool != [8] or division != [16]:
            raise AdapterError("actual stdout pool/band-group decomposition differs")
        subgroup = matched("elpa_subgroup", r"^[ \t]*ELPA distributed-memory algorithm \(size of sub-group:[ \t]*(\d+)[ \t]*\*[ \t]*(\d+)[ \t]+procs\)[ \t]*$")
        if subgroup != [4, 4] or "a serial algorithm will be used" in text:
            raise AdapterError("actual ELPA subgroup differs from registered4*4")
        algorithm, defaults = "ELPA", {}
    return {"nprocs": processes, "nthreads": threads, "processor_cores": cores,
            "npool": expected["npool"], "proc_per_band_pool_image": 1 if expected == serial else 16,
            "diagonalization_algorithm": algorithm, "elpa_subgroup": subgroup,
            "matched_lines": evidence, "inferred_serial_defaults": defaults}


def read_qe_arm(input_path, stdout_path, stderr_path, xml_path, process_receipt, *,
                expected_settings, expected_parallel, expected_exit="clean_stop",
                expected_evaluations=None):
    """Parse actual input/log/XML evidence and fail closed on invalid results.

    A clean stop's XML output is a proposal, never an evaluated energy.  The
    XML Hartree convention is explicit: energy and force are multiplied by two.
    The input's common settings are exact; operational deviations remain visible.
    `expected_settings` is parse_deck output plus an exact `upf_pins` mapping.
    """
    if expected_evaluations is not None:
        _integer(expected_evaluations, "expected evaluated count", 1)
    if set(expected_parallel) != {"nprocs", "nthreads", "ntasks", "nbgrp", "npool", "ndiag"}:
        raise AdapterError("complete registered XML parallel shape required")
    for value in expected_parallel.values():
        _integer(value, "expected parallel shape", 1)
    deck = parse_deck(input_path)
    if deck["settings_identity"] != expected_settings["settings_identity"]:
        raise AdapterError("common physical/solver settings differ")
    text, log_source = _read(stdout_path)
    errors, error_source = _read(stderr_path)
    xml, xml_source = _read(xml_path)
    if type(process_receipt.get("returncode")) is not int or process_receipt["returncode"] not in (0, 255) or process_receipt.get("timed_out") is not False:
        raise AdapterError("process did not complete under its registered allowance")
    if FAILURE.search(text + errors) or "JOB DONE." not in text:
        raise AdapterError("raw failure or missing normal QE shutdown")
    if re.findall(r"Program PWSCF v\.([0-9.]+) starts", text) != ["7.5"]:
        raise AdapterError("exactly one QE7.5 banner required")
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as error:
        raise AdapterError("malformed QE XML") from error
    if root.attrib.get("Units") != "Hartree atomic units":
        raise AdapterError("explicit QE Hartree XML units required")
    creator = _one(_one(root, "general_info"), "creator")
    if creator.attrib.get("NAME") != "PWSCF" or creator.attrib.get("VERSION") != "7.5":
        raise AdapterError("XML creator/version differs")
    parallel = {}
    for node in _one(root, "parallel_info"):
        name = _tag(node)
        if name in parallel:
            raise AdapterError("duplicate XML parallel field")
        parallel[name] = _integer(_number(node.text), "XML " + name, 1)
    if parallel != expected_parallel:
        raise AdapterError("actual processor/pool/thread/diagonalization shape differs")
    runtime_parallel = _raw_parallel(text, log_source, expected_parallel)
    xml_identity = _check_xml_input(root, deck)
    if expected_settings.get("xml_settings_identity") not in (None, xml_identity):
        raise AdapterError("complete common XML settings differ")
    nodes = [node for node in root if _tag(node) == "step"]
    ranges = _xml_source_ranges(xml, xml_source, "step")
    if len(nodes) != len(ranges):
        raise AdapterError("XML step source ranges are ambiguous")
    evaluations = [_xml_evaluation(node, deck, span) for node, span in zip(nodes, ranges)]
    output = _one(root, "output")
    status = _integer(_number(_one(root, "exit_status").text), "XML exit status")
    if expected_exit == "clean_stop":
        if deck["operations"]["calculation"] != "relax" or status != 255 or STOP not in text:
            raise AdapterError("registered clean relaxation stop not evidenced")
        if "bfgs converged in" in text.lower() or "maximum number of steps" in text.lower():
            raise AdapterError("relaxation ended before the registered evaluated boundary")
        if not evaluations:
            raise AdapterError("clean stop has no evaluated trajectory")
        proposal = _xml_geometry(output, deck)
    elif expected_exit == "normal_scf":
        if deck["operations"]["calculation"] != "scf" or status != 0 or STOP in text or process_receipt["returncode"] != 0:
            raise AdapterError("fresh reference did not complete normally")
        if evaluations:
            raise AdapterError("fixed SCF unexpectedly contains ionic step records")
        output_range = _xml_source_ranges(xml, xml_source, "output")
        if len(output_range) != 1:
            raise AdapterError("ambiguous SCF XML output source")
        evaluations = [_xml_evaluation(output, deck, output_range[0])]
        proposal = None
    else:
        raise AdapterError("unsupported expected exit kind")
    if "Maximum CPU time" in text or "Maximum wall time" in text:
        raise AdapterError("time limit shutdown cannot be a reference or registered stop")
    if expected_evaluations is not None and len(evaluations) != expected_evaluations:
        raise AdapterError("missed registered evaluated stop boundary")
    energies = [_number(v) for v in re.findall(r"(?m)^\s*!\s+total energy\s*=\s*(" + NUM + r")\s+Ry\s*$", text)]
    if len(energies) != len(evaluations):
        raise AdapterError("raw log/XML evaluated energy counts differ")
    for energy, evaluated in zip(energies, evaluations):
        if abs(energy-evaluated["energy_Ry"]) > 5.1e-8:
            raise AdapterError("ordered raw log/XML energies disagree")
    force_markers = list(re.finditer(r"Forces acting on atoms \(cartesian axes, Ry/au\):", text))
    if len(force_markers) != len(evaluations):
        raise AdapterError("raw log/XML force evaluation counts differ")
    for index, (marker, evaluated) in enumerate(zip(force_markers, evaluations)):
        end = force_markers[index+1].start() if index+1 < len(force_markers) else len(text)
        block = text[marker.end():end]
        rows = list(re.finditer(r"(?m)^\s*atom\s+(\d+)\s+type\s+(\d+)\s+force\s*=\s*("+NUM+r")\s+("+NUM+r")\s+("+NUM+r")\s*$", block))
        if len(rows) != deck["nat"] or [int(v.group(1)) for v in rows] != list(range(1, deck["nat"]+1)):
            raise AdapterError("ordered complete raw force block required")
        types = {pseudo["species"]: i+1 for i, pseudo in enumerate(deck["upfs"])}
        if [int(v.group(2)) for v in rows] != [types[s] for s in deck["geometry"]["species"]]:
            raise AdapterError("raw force atom/species type order differs")
        # forces.f90 prints unconstrained force, then multiplies by if_pos.
        # qexsd subsequently serializes the masked force used by the optimizer.
        masked = [[_number(v.group(j+3))*flag for j, flag in enumerate(flags)]
                  for v, flags in zip(rows, deck["qe_if_pos"])]
        if _matrix_delta(masked, evaluated["forces_Ry_bohr"]) > 5.1e-8:
            raise AdapterError("masked raw log/XML forces disagree")
    position_matches = list(re.finditer(r"(?mi)^\s*ATOMIC_POSITIONS\s*\((bohr|angstrom)\)\s*\n", text))
    logged_geometries = []
    for match in position_matches:
        rows = [row.split() for row in text[match.end():].splitlines()[:deck["nat"]]]
        if len(rows) != deck["nat"] or any(len(row) not in (4, 7) for row in rows):
            raise AdapterError("incomplete raw logged proposal geometry")
        if [row[0] for row in rows] != deck["geometry"]["species"]:
            raise AdapterError("raw logged geometry atom identity/order differs")
        factor = 1 if match.group(1).lower() == "bohr" else 1/BOHR_ANGSTROM
        logged_geometries.append([[_number(v)*factor for v in row[1:4]] for row in rows])
    if proposal is not None:
        if len(logged_geometries) < len(evaluations):
            raise AdapterError("raw proposals do not cover each evaluated move")
        for index, evaluated in enumerate(evaluations[1:], 1):
            if _matrix_delta(logged_geometries[index-1], evaluated["geometry"]["positions"]) > 1e-7:
                raise AdapterError("raw proposal/evaluated trajectory order differs")
        if _matrix_delta(logged_geometries[-1], proposal["positions"]) > 1e-7:
            raise AdapterError("raw last proposal differs from saved XML proposal")
    if not _geometry_matches(evaluations[0]["geometry"], deck["geometry"]):
        raise AdapterError("first evaluation is not at the actual input geometry")
    initial = expected_settings["geometry"]
    for evaluated in evaluations + ([{"geometry": proposal}] if proposal else []):
        for actual, original, flags in zip(evaluated["geometry"]["positions"], initial["positions"], initial["fixed_flags"]):
            if any(flag and abs(a-b) > 1e-7 for a, b, flag in zip(actual, original, flags)):
                raise AdapterError("coordinate marked fixed moved")
    bfgs_matches = list(re.finditer(r"number of bfgs steps\s*=\s*(\d+)", text))
    counts = [int(v.group(1)) for v in bfgs_matches]
    cycles = [int(v) for v in re.findall(r"number of scf cycles\s*=\s*(\d+)", text)]
    startup = text[:bfgs_matches[0].start()] if bfgs_matches else text
    thresholds = [_number(v) for v in re.findall(r"convergence threshold\s*=\s*(" + NUM + r")", text)]
    if not thresholds:
        raise AdapterError("actual first SCF threshold absent")
    upf_reads = _raw_upf_reads(text, deck, expected_settings.get("upf_pins", {}),
                             expected_settings.get("upf_read_path_map"))
    result = {"schema": "pa-qe-raw-arm-v1", "raw_validated": True,
              "production_accepted": False, "evaluations": evaluations,
              "proposal_geometry": proposal, "xml_exit_status": status,
              "units": {"xml": "Hartree atomic units", "energy": "Ry", "geometry": "bohr", "force": "Ry/bohr"},
              "parallel": parallel, "runtime_parallel": runtime_parallel,
              "settings_identity": deck["settings_identity"],
              "xml_settings_identity": xml_identity, "input": deck,
              "first_conv_thr_Ry": thresholds[0], "optimizer_counts": counts, "scf_counts": cycles,
              "startup_history_deleted": ".bfgs deleted, as requested" in startup,
              "startup_optimizer_initialized": bool(re.search(r"(?m)^\s*BFGS Geometry Optimization\s*$", startup)),
              "startup_history_reset": (".bfgs deleted, as requested" in startup or bool(re.search(r"(?m)^\s*BFGS Geometry Optimization\s*$", startup))),
              "restart_fallback": bool(re.search(r"restart disabled:\s*needed files not found", text, re.I)),
              "sources": {"input": deck["source"], "stdout": log_source, "stderr": error_source, "xml": xml_source},
              "upf_reads": upf_reads, "process": copy.deepcopy(process_receipt)}
    result["evidence_sha256"] = _json_hash(result)
    return result


def require_expected_first_threshold(arm, deck):
    if arm["first_conv_thr_Ry"] != deck["conv_thr_Ry"] or deck["conv_thr_Ry"] != 1e-6:
        raise AdapterError("first-boundary threshold differs from the registered source1e-6 Ry")
    return True


def _validate_arm(arm):
    if arm.get("raw_validated") is not True or arm.get("schema") != "pa-qe-raw-arm-v1":
        raise AdapterError("raw adapter evidence required")
    body = {key: value for key, value in arm.items() if key != "evidence_sha256"}
    if _json_hash(body) != arm.get("evidence_sha256"):
        raise AdapterError("normalized raw evidence was modified")
    for source in list(arm["sources"].values()) + arm["upf_reads"]:
        if _hash(_safe_path(source["path"], directory=False)) != source["sha256"]:
            raise AdapterError("raw source drifted after parsing")


def checkpoint_inventory(outdir, wfcdir=None):
    # A path/hash-only manifest cannot reveal an alias outside either tree.
    # Require exclusive regular-file ownership and unique inode identities
    # before delegating to the unchanged historical inventory contract.
    seen = set()
    def visit(directory):
        for child in sorted(directory.iterdir()):
            info = child.lstat()
            if stat.S_ISDIR(info.st_mode):
                visit(child)
            elif stat.S_ISREG(info.st_mode):
                identity = (info.st_dev, info.st_ino)
                if info.st_nlink != 1 or identity in seen:
                    raise AdapterError("hardlink or inode alias in checkpoint")
                seen.add(identity)
            else:
                raise AdapterError("symlink or special checkpoint entry")
    for root in (outdir, wfcdir):
        if root is not None:
            visit(_safe_path(root, directory=True))
    return contract.checkpoint_inventory(outdir, wfcdir)


def _tree_directories(root):
    root = _safe_path(root, directory=True)
    result = []
    def visit(directory):
        for child in sorted(directory.iterdir()):
            mode = child.lstat().st_mode
            if stat.S_ISLNK(mode) or not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                raise AdapterError("symlink or special checkpoint entry")
            if stat.S_ISDIR(mode):
                result.append(child.relative_to(root).as_posix())
                visit(child)
    visit(root)
    return sorted(result)


def _content_inventory(outdir, wfcdir=None):
    inventory = checkpoint_inventory(outdir, wfcdir)
    body = {}
    for name in ("outdir", "wfcdir"):
        tree = inventory[name]
        body[name] = None if tree is None else {
            "files": tree["files"], "directories": _tree_directories(tree["root"])}
    return inventory, _json_hash(body)


def _no_overlap(paths):
    roots = [_safe_path(p, exists=False) for p in paths if p is not None]
    for i, left in enumerate(roots):
        for right in roots[i+1:]:
            if left == right or left in right.parents or right in left.parents:
                raise AdapterError("checkpoint roots overlap or alias")


def _copy_tree(source, destination):
    """Copy only ordinary files with no-follow opens; leave failed attempts intact."""
    source = _safe_path(source, directory=True)
    destination = _safe_path(destination, exists=False)
    if destination.exists():
        raise AdapterError("refusing checkpoint overwrite")
    _tree_directories(source)
    destination.mkdir()
    for child in sorted(source.iterdir()):
        before = child.lstat()
        if stat.S_ISDIR(before.st_mode):
            _copy_tree(child, destination / child.name)
        elif stat.S_ISREG(before.st_mode):
            if before.st_nlink != 1:
                raise AdapterError("hardlink or inode alias in checkpoint")
            descriptor = os.open(str(child), os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
            with os.fdopen(descriptor, "rb") as inp:
                opened = os.fstat(inp.fileno())
                if not stat.S_ISREG(opened.st_mode) or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
                    raise AdapterError("checkpoint entry changed while copying")
                if opened.st_nlink != 1:
                    raise AdapterError("hardlink or inode alias in opened checkpoint file")
                with (destination / child.name).open("xb") as out:
                    shutil.copyfileobj(inp, out, 1024 * 1024)
        else:
            raise AdapterError("symlink or special checkpoint entry")


def snapshot_checkpoint(outdir, destination, *, wfcdir=None):
    """Recursively freeze full output and optional distinct WFC trees."""
    outdir = _safe_path(outdir, directory=True)
    wave = _safe_path(wfcdir, directory=True) if wfcdir is not None else None
    destination = _safe_path(destination, exists=False)
    _no_overlap([outdir, wave, destination])
    if destination.exists():
        raise AdapterError("snapshot destination already exists")
    source_inventory, identity = _content_inventory(outdir, wave)
    destination.mkdir()
    saved_out, saved_wave = destination / "outdir", destination / "wfcdir" if wave else None
    _copy_tree(outdir, saved_out)
    if wave:
        _copy_tree(wave, saved_wave)
    inventory, copied_identity = _content_inventory(saved_out, saved_wave)
    after, source_identity_after = _content_inventory(outdir, wave)
    if not contract.checkpoint_unchanged(source_inventory, after) or identity != source_identity_after or identity != copied_identity:
        raise AdapterError("full immutable checkpoint copy identity differs")
    return {"schema": "pa-qe-snapshot-v1", "copied": True,
            "snapshot": {"outdir": str(saved_out), "wfcdir": str(saved_wave) if wave else None},
            "source_inventory": source_inventory, "inventory": inventory,
            "content_sha256": identity}


def copy_checkpoint(snapshot, outdir, *, wfcdir=None):
    if snapshot.get("schema") != "pa-qe-snapshot-v1" or snapshot.get("copied") is not True:
        raise AdapterError("complete immutable snapshot required")
    original = snapshot["snapshot"]
    if (original["wfcdir"] is None) != (wfcdir is None):
        raise AdapterError("distinct WFC destination must match the complete snapshot")
    _no_overlap([original["outdir"], original["wfcdir"], outdir, wfcdir])
    before, identity = _content_inventory(original["outdir"], original["wfcdir"])
    if not contract.checkpoint_unchanged(before, snapshot["inventory"]) or identity != snapshot["content_sha256"]:
        raise AdapterError("immutable checkpoint snapshot drifted")
    _copy_tree(original["outdir"], outdir)
    if wfcdir is not None:
        _copy_tree(original["wfcdir"], wfcdir)
    inventory, copied_identity = _content_inventory(outdir, wfcdir)
    after, after_identity = _content_inventory(original["outdir"], original["wfcdir"])
    if not contract.checkpoint_unchanged(before, after) or identity != copied_identity or identity != after_identity:
        raise AdapterError("checkpoint copy differs or immutable source changed")
    return {"outdir": str(_safe_path(outdir, directory=True)),
            "wfcdir": str(_safe_path(wfcdir, directory=True)) if wfcdir is not None else None,
            "inventory": inventory, "content_sha256": copied_identity, "copied": True}


def seed_initialization(seed_dir, target_save_dir, expected_files):
    """Copy the pinned four-file density seed; explicitly not a full restart."""
    if set(expected_files) != SEED_FILES:
        raise AdapterError("initial density seed requires exactly the four registered files")
    seed = _safe_path(seed_dir, directory=True)
    target = _safe_path(target_save_dir, exists=False)
    _no_overlap([seed, target])
    if target.exists():
        raise AdapterError("initialization target already exists")
    sources = {}
    for name in sorted(SEED_FILES):
        sources[name] = _source(seed / name)
        if sources[name]["sha256"] != expected_files[name]:
            raise AdapterError("initial density seed pin differs")
    target.mkdir()
    for name in sorted(SEED_FILES):
        with (seed / name).open("rb") as inp, (target / name).open("xb") as out:
            shutil.copyfileobj(inp, out, 1024 * 1024)
        if _hash(target / name) != expected_files[name] or _hash(seed / name) != expected_files[name]:
            raise AdapterError("initial density seed copy differs")
    return {"kind": "INITIAL_ELECTRONIC_DENSITY_ONLY", "full_restart_checkpoint": False,
            "sources": sources, "target_save_dir": str(target), "files": copy.deepcopy(expected_files)}


def read_bfgs(path, *, nat, cell_bohr, evaluated=None):
    """Read QE7.5's fractional prior state/counters, with reviewed dimensions.

    Fixed-cell QE uses 3*nat+10 optimizer components.  The full history is retained;
    this reader extracts only the leading fractional prior coordinates/gradient
    and counters.  Inactive fixed-cell/non-FCP slots must remain zero, and the
    saved Newton-Raphson step must pass QE's pre-write eps16 positivity check.
    A prior accepted point can differ from the last evaluated
    trial after Wolfe rejection; optional correspondence is deliberately explicit.
    """
    nat = _integer(nat, "optimizer nat", 1)
    if len(cell_bohr) != 3 or any(len(row) != 3 for row in cell_bohr):
        raise AdapterError("full optimizer cell required")
    cell = [[_number(v) for v in row] for row in cell_bohr]
    if abs(_determinant(cell)) < 1e-10:
        raise AdapterError("singular optimizer cell")
    text, source = _read(path)
    values = _numbers(text)
    dimension = 3*nat + 10
    if len(values) != dimension*dimension + 4*dimension + 6:
        raise AdapterError("unexpected QE7.5 complete BFGS dimensions")
    # bfgs_module.f90:312-319 zero the inactive nine cell and one FCP slots.
    # write_bfgs_file:844-854 writes pos/grad, counters+energy, histories,
    # inverse Hessian, tr_min_hit and nr_step_length, in this exact order.
    tail_ranges = ((3*nat, dimension), (dimension+3*nat, 2*dimension),
                   (2*dimension+4+3*nat, 3*dimension+4),
                   (3*dimension+4+3*nat, 4*dimension+4))
    inactive_tail_max = max(abs(v) for first, last in tail_ranges for v in values[first:last])
    inactive_tail_tolerance = 1e-12
    if inactive_tail_max > inactive_tail_tolerance:
        raise AdapterError("saved optimizer inactive cell/FCP slots are nonzero")
    nr_step_length = values[-1]
    # bfgs_module.f90:576-582 rejects <eps16 before writing this checkpoint.
    if nr_step_length < 1e-16:
        raise AdapterError("saved optimizer Newton-Raphson step length is not positive")
    tr_min_hit = _integer(values[-2], "optimizer trust-radius reset count")
    if tr_min_hit > 2:
        raise AdapterError("invalid optimizer trust-radius reset count")
    scf, bfgs, gdiis = [_integer(v, "optimizer counter") for v in values[2*dimension:2*dimension+3]]
    fractional = [values[i:i+3] for i in range(0, 3*nat, 3)]
    prior_positions = [[sum(row[k]*cell[k][j] for k in range(3)) for j in range(3)] for row in fractional]
    fractional_gradient = [values[dimension+i:dimension+i+3] for i in range(0, 3*nat, 3)]
    energy = values[2*dimension+3]
    if evaluated is not None:
        if _matrix_delta(prior_positions, evaluated["geometry"]["positions"]) > 1e-8 or abs(energy-evaluated["energy_Ry"]) > 1e-8:
            raise AdapterError("saved optimizer prior geometry/energy differs from evaluation")
        forces = [[force*(1-fixed) for force, fixed in zip(row, flags)]
                  for row, flags in zip(evaluated["forces_Ry_bohr"], evaluated["geometry"]["fixed_flags"])]
        expected_gradient = [[-sum(cell[k][j]*force[j] for j in range(3)) for k in range(3)] for force in forces]
        if _matrix_delta(fractional_gradient, expected_gradient) > 1e-8:
            raise AdapterError("saved optimizer gradient differs from constrained evaluated force")
    return {"scf_count": scf, "bfgs_count": bfgs, "gdiis_count": gdiis,
            "dimension": dimension, "prior_positions_bohr": prior_positions,
             "prior_fractional_positions": fractional, "prior_fractional_gradient_Ry": fractional_gradient,
             "prior_energy_Ry": energy,
             "nr_step_length_bohr": nr_step_length, "tr_min_hit": tr_min_hit,
             "inactive_tail_max_abs": inactive_tail_max,
             "inactive_tail_zero_tolerance": inactive_tail_tolerance,
             "source": source}


def _checkpoint_binding(before, scratch_paths):
    separation = contract.validate_scratch_separation(**scratch_paths)
    if Path(separation["roots"]["restart.outdir"]) != Path(before["outdir"]["root"]):
        raise AdapterError("immutable checkpoint is not bound to registered scratch")
    wave = before["wfcdir"]
    registered = separation["roots"].get("restart.wfcdir")
    if (wave is None) != (registered is None) or (wave is not None and Path(wave["root"]) != Path(registered)):
        raise AdapterError("immutable WFC checkpoint binding differs")
    return separation


def pre_resume_decision(warm, fresh, checkpoint_before, checkpoint_after, *,
                        scratch_paths, remaining_segments=1, remaining_reseeds=1):
    """Select fresh branch before launching a continuation; never accept a step."""
    for value, label in ((remaining_segments, "remaining segments"), (remaining_reseeds, "remaining reseeds")):
        _integer(value, label)
    stable = contract.checkpoint_unchanged(checkpoint_before, checkpoint_after)
    current = checkpoint_inventory(checkpoint_before["outdir"]["root"],
                                   checkpoint_before["wfcdir"]["root"] if checkpoint_before["wfcdir"] else None)
    stable = stable and contract.checkpoint_unchanged(checkpoint_after, current)
    separation = _checkpoint_binding(checkpoint_before, scratch_paths)
    result = {"decision_timing": "PRE_RESUME_BRANCH_SELECTION", "action": "HOLD",
              "production_accepted": False, "next_geometry": None,
              "checkpoint_unchanged": stable, "scratch_separation": separation,
              "checkpoint_sha256": checkpoint_before["sha256"], "reason": None}
    if not stable:
        result["reason"] = "immutable checkpoint changed during isolated fresh check"
        return result
    if warm is None or fresh is None:
        result["reason"] = "no raw converged warm/fresh reference"
        return result
    _validate_arm(warm)
    _validate_arm(fresh)
    fresh_operations = fresh["input"]["operations"]
    if _safe_path(fresh_operations["outdir"], exists=False) != Path(separation["roots"]["fresh.outdir"]):
        raise AdapterError("actual fresh scratch differs from its registered isolated root")
    wave = fresh_operations.get("wfcdir")
    registered_wave = separation["roots"].get("fresh.wfcdir")
    if (wave is None) != (registered_wave is None) or (wave is not None and _safe_path(wave, exists=False) != Path(registered_wave)):
        raise AdapterError("actual fresh WFC scratch differs from its isolated root")
    if (fresh_operations["calculation"] != "scf" or fresh_operations["restart_mode"] != "from_scratch"
            or fresh_operations.get("startingpot") != "atomic"
            or fresh_operations.get("startingwfc") != "atomic+random"):
        raise AdapterError("fresh reference lacks explicitly fresh electronic initialization")
    require_expected_first_threshold(warm, warm["input"])
    require_expected_first_threshold(fresh, warm["input"])
    if warm["settings_identity"] != fresh["settings_identity"] or warm["xml_settings_identity"] != fresh["xml_settings_identity"]:
        raise AdapterError("fresh/common source/XML settings differ")
    if len(warm["evaluations"]) != 1 or len(fresh["evaluations"]) != 1 or warm["proposal_geometry"] is None:
        raise AdapterError("first evaluated boundary and distinct saved proposal required")
    if warm["optimizer_counts"] != [0] or warm["scf_counts"] != [1]:
        raise AdapterError("candidate did not stop at the first optimizer evaluation")
    if _matrix_delta(warm["proposal_geometry"]["positions"], warm["evaluations"][0]["geometry"]["positions"]) <= 1e-8:
        raise AdapterError("first saved proposal has no nonzero ionic displacement")
    evaluated, reference = warm["evaluations"][0], fresh["evaluations"][0]
    if not _geometry_matches(evaluated["geometry"], reference["geometry"]):
        raise AdapterError("fresh SCF is not at the warm evaluated geometry")
    if not remaining_segments:
        result["reason"] = "segment cap prevents the next evaluation"
        return result
    drop = (evaluated["energy_Ry"]-reference["energy_Ry"]) * RY_MEV
    result.update({"warm_minus_fresh_meV": drop, "warm_source": evaluated["source"],
                   "fresh_source": reference["source"], "warm_evidence_sha256": warm["evidence_sha256"],
                   "fresh_evidence_sha256": fresh["evidence_sha256"]})
    if reference["energy_Ry"] < evaluated["energy_Ry"] - contract.DELTA_MEV / RY_MEV:
        if not remaining_reseeds:
            result["reason"] = "reseed cap prevents intentional electronic reset"
        else:
            result.update(action="RESEED_CANDIDATE", next_geometry=evaluated["geometry"],
                          reason="fresh state lower by strictly more than10meV per cell")
    else:
        result.update(action="RESUME_CANDIDATE", next_geometry=warm["proposal_geometry"],
                      reason="fresh comparison permits observed continuation audit")
    return result


def audit_consumption(warm, fresh, saved_optimizer, resume, checkpoint_before,
                      checkpoint_after, *, scratch_paths):
    """Audit the already-observed resume, then invoke the unchanged offline oracle."""
    decision = pre_resume_decision(warm, fresh, checkpoint_before, checkpoint_after,
                                  scratch_paths=scratch_paths)
    if decision["action"] != "RESUME_CANDIDATE":
        raise AdapterError("a HOLD/RESEED branch cannot audit inherited continuation")
    _validate_arm(resume)
    operations = resume["input"]["operations"]
    if operations.get("startingpot") != "file" or operations.get("startingwfc") != "file":
        raise AdapterError("continuation electronic initialization is not explicit file restart")
    _no_overlap([checkpoint_before["outdir"]["root"],
                 checkpoint_before["wfcdir"]["root"] if checkpoint_before["wfcdir"] else None,
                 scratch_paths["fresh_outdir"], scratch_paths.get("fresh_wfcdir"),
                 operations["outdir"], operations.get("wfcdir")])
    if resume["input"]["operations"]["restart_mode"] != "restart":
        raise AdapterError("continuation input did not request restart")
    if (resume["startup_history_reset"] or resume["restart_fallback"]
            or not resume["optimizer_counts"] or not resume["scf_counts"]
            or resume["optimizer_counts"][0] != saved_optimizer["bfgs_count"]
            or resume["scf_counts"][0] != saved_optimizer["scf_count"]+1):
        raise AdapterError("observed continuation did not consume saved optimizer counters")
    if resume["parallel"] != warm["parallel"] or resume["xml_settings_identity"] != warm["xml_settings_identity"]:
        raise AdapterError("continuation common XML or processor shape differs")
    if not _geometry_matches(resume["evaluations"][0]["geometry"], warm["proposal_geometry"], TOLERANCES["position_bohr"]):
        raise AdapterError("first resumed evaluation differs from saved proposal")
    saved_source = saved_optimizer["source"]
    expected_saved_path = Path(checkpoint_before["outdir"]["root"]) / (warm["input"]["operations"]["prefix"]+".bfgs")
    if Path(saved_source["path"]) != expected_saved_path:
        raise AdapterError("saved optimizer is not bound to the immutable full checkpoint")
    if _hash(_safe_path(saved_source["path"], directory=False)) != saved_source["sha256"]:
        raise AdapterError("saved optimizer source drifted")
    reparsed = read_bfgs(expected_saved_path, nat=warm["input"]["nat"],
                         cell_bohr=warm["evaluations"][0]["geometry"]["cell"],
                         evaluated=warm["evaluations"][0])
    if reparsed != saved_optimizer:
        raise AdapterError("supplied saved optimizer differs from reopened raw history")
    if (reparsed["scf_count"], reparsed["bfgs_count"], reparsed["gdiis_count"]) != (1, 1, 0):
        raise AdapterError("saved first-move optimizer counters are not1/1/0")
    actual = resume["upf_reads"]
    upf_manifest = {v["path"]: v["sha256"] for v in actual}
    # The oracle has one UPF handle.  Retain every actual consumed UPF in the
    # adapter's separate complete manifest rather than hide the remaining types.
    observed = {"first_optimizer_bfgs_count": resume["optimizer_counts"][0],
                "first_scf_count": resume["scf_counts"][0], "startup_history_reset": False,
                "restart_fallback": False, "settings_identity": warm["settings_identity"],
                "checkpoint_source_validated": True, "upf_source_validated": True,
                "settings_source_validated": True, "source": resume["sources"]["stdout"],
                "checkpoint_source": resume["sources"]["xml"],
                "upf_source": actual[0], "settings_source": resume["sources"]["input"],
                "complete_upf_manifest": upf_manifest}
    warm_record = {**warm["evaluations"][0], "proposal_geometry": warm["proposal_geometry"]}
    fresh_record = copy.deepcopy(fresh["evaluations"][0])
    # Unit conversions and QE XML decimal serialization can differ in the last
    # binary place.  Raw coordinates remain in each arm; the oracle's exact
    # normalized equality uses the previously verified same-geometry comparison.
    normalization = {"fresh_position_max_delta_bohr": _matrix_delta(
        warm_record["geometry"]["positions"], fresh_record["geometry"]["positions"]),
        "fresh_cell_max_delta_bohr": _matrix_delta(
            warm_record["geometry"]["cell"], fresh_record["geometry"]["cell"]),
        "normalization_tolerance_bohr": 1e-7}
    fresh_record["geometry"] = copy.deepcopy(warm_record["geometry"])
    proposal = copy.deepcopy(warm_record["proposal_geometry"])
    fixed_deltas = []
    for proposed, evaluated, flags in zip(proposal["positions"], warm_record["geometry"]["positions"], proposal["fixed_flags"]):
        for index, fixed in enumerate(flags):
            if fixed:
                fixed_deltas.append(abs(proposed[index]-evaluated[index]))
                if fixed_deltas[-1] > 1e-7:
                    raise AdapterError("saved proposal moved a fixed coordinate")
                proposed[index] = evaluated[index]
    normalization["proposal_fixed_coordinate_max_delta_bohr"] = max(fixed_deltas or [0.0])
    warm_record["proposal_geometry"] = proposal
    result = contract.decide_segment(
        warm=warm_record, fresh=fresh_record, checkpoint_before=checkpoint_before,
        checkpoint_after=checkpoint_after, scratch_paths=scratch_paths, segment_index=1,
        reseeds_so_far=0, max_segments=2, max_reseeds=1,
        saved_optimizer=saved_optimizer, resume_receipt=observed)
    result["raw_consumption_audit"] = {"passed": True, "resume_evidence_sha256": resume["evidence_sha256"],
                                       "upf_manifest": upf_manifest, "geometry_normalization": normalization}
    return result


def compare_trajectories(continuous, split):
    """Compare all ordered evaluations; no dropping, alignment or remapping."""
    if len(continuous) < 3 or len(continuous) != len(split):
        raise AdapterError("equal complete trajectories of at least three evaluations required")
    maxima = dict.fromkeys(TOLERANCES, 0.0)
    deltas = []
    order = continuous[0]["geometry"]["species"]
    for left, right in zip(continuous, split):
        if (left.get("status") != "CONVERGED" or right.get("status") != "CONVERGED"
                or left["geometry"]["species"] != order or right["geometry"]["species"] != order
                or left["geometry"]["fixed_flags"] != right["geometry"]["fixed_flags"]
                or left["settings_identity"] != right["settings_identity"]
                or _matrix_delta(left["geometry"]["cell"], right["geometry"]["cell"]) > 1e-7):
            raise AdapterError("trajectory atom/cell/constraint/settings identity differs")
        delta = {"energy_Ry": abs(_number(left["energy_Ry"])-_number(right["energy_Ry"])),
                 "position_bohr": _matrix_delta(left["geometry"]["positions"], right["geometry"]["positions"]),
                 "force_Ry_bohr": _matrix_delta(left["forces_Ry_bohr"], right["forces_Ry_bohr"])}
        deltas.append(delta)
        maxima = {key: max(maxima[key], delta[key]) for key in maxima}
    return {"production_accepted": False, "evaluations": len(continuous), "tolerances": TOLERANCES.copy(),
            "ordered_differences": deltas, "max_abs_deltas": maxima,
            "within_tolerances": all(maxima[key] <= TOLERANCES[key] for key in maxima)}
