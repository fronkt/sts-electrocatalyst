"""Frozen six-job wfc, density-cutoff and smearing sensitivity stage.

Two accepted ortho tight sources may each seed three independent clones. The
previous numerical stage remains unchanged. No failure removes source or target
scratch. File-start evidence denotes warm initialization, not proof of a basin.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

try:
    from . import hea_numerical_guard as base
    from . import hea_force_audit as force
except ImportError:
    import hea_numerical_guard as base
    import hea_force_audit as force

SCHEMA = "hea_sensitivity_v1"
SOURCE_SCHEMA = "hea_sensitivity_sources_v1"
MANIFEST = "runs/hea/m_sensitivity_2026-09-09.txt"
INVENTORY = "results/hea_sensitivity_2026-09-09/source_checkpoints.json"
DIRECTORY = "hea/sensitivity_2026-09-09"
SOURCE_DIRECTORY = "hea/numerical_2026-09-08"
XML_DIRECTORY = "results/hea_sensitivity_2026-09-09/source_xml"
ARMS = {"wfc": {"ecutwfc": 100.0}, "rho": {"ecutrho": 800.0}, "smearing": {"degauss": 0.005}}
ENDPOINTS = ("builder", "pull2.10")
EXPECTED = {"hs__leader_" + endpoint + "__ortho__" + arm: (endpoint, arm)
            for arm in ARMS for endpoint in ENDPOINTS}
SOURCE_JOBS = ["hn__leader_" + endpoint + "__ortho__tight" for endpoint in ENDPOINTS]
JOB_KEYS = {"job", "dir", "suffix", "nk", "sha256", "prefix", "source_job", "arm"}
SOURCE_KEYS = {"source_job", "prefix", "dir", "source_input", "source_input_sha256", "source_xml",
               "source_xml_sha256", "source_output_sha256", "source_projection_sha256", "source_qc_sha256", "files"}
UPFS = {"cr_pbe_v1.5.uspp.F.UPF", "Cu.paw.z_11.ld1.psl.v1.0.0-low.upf", "mn_pbe_v1.5.uspp.F.UPF",
        "ni_pbe_v1.4.uspp.F.UPF", "O.pbe-n-kjpaw_psl.0.1.UPF", "H.pbe-rrkjus_psl.1.0.0.UPF"}
CHECKPOINT_FILES = base.PORTABLE_FILES | base.WFC_FILES | UPFS | {"atomic_proj.xml"}
BOHR_ANGSTROM = 0.529177210903
HARTREE_EV = 27.211386245988
_path, _json, _read, _digest = base._path, base._json, base._read, base._digest


def _prefix(endpoint):
    return "hc__leader_" + endpoint + "__ortho__fragment"


def validate_spec(spec):
    base._keys(spec, base.SPEC_KEYS, "sensitivity spec")
    if spec["schema"] != SCHEMA or spec["manifest"] != MANIFEST or spec["source_checkpoints"] != INVENTORY:
        raise ValueError("unexpected frozen sensitivity identity")
    for key, expected in (("np", 128), ("concurrency", 1), ("wall_hours", 4)):
        if type(spec[key]) is not int or spec[key] != expected:
            raise ValueError("unexpected sensitivity resources: " + key)
    for key in ("manifest_sha256", "source_checkpoints_sha256"):
        base._sha(spec[key])
    if not isinstance(spec["jobs"], list) or len(spec["jobs"]) != 6:
        raise ValueError("exactly six ordered sensitivity jobs required")
    for job, (name, (endpoint, arm)) in zip(spec["jobs"], EXPECTED.items()):
        base._keys(job, JOB_KEYS, "sensitivity job")
        if (job["job"] != name or job["arm"] != arm or job["dir"] != DIRECTORY or job["suffix"] != ".in"
                or type(job["nk"]) is not int or job["nk"] != 8
                or job["source_job"] != "hn__leader_" + endpoint + "__ortho__tight"
                or job["prefix"] != _prefix(endpoint)):
            raise ValueError("job differs from exact ordered sensitivity design")
        base._sha(job["sha256"])
    return spec


def validate_inventory(inventory):
    base._keys(inventory, {"schema", "checkpoints"}, "sensitivity inventory")
    if inventory["schema"] != SOURCE_SCHEMA or not isinstance(inventory["checkpoints"], list) or len(inventory["checkpoints"]) != 2:
        raise ValueError("exactly two accepted sensitivity sources required")
    found = {}
    for item, endpoint, name in zip(inventory["checkpoints"], ENDPOINTS, SOURCE_JOBS):
        base._keys(item, SOURCE_KEYS, "sensitivity checkpoint")
        prefix = _prefix(endpoint)
        if (item["source_job"] != name or item["prefix"] != prefix
                or item["dir"] != SOURCE_DIRECTORY + "/tmp_" + name + "/" + prefix + ".save"
                or item["source_input"] != "runs/" + SOURCE_DIRECTORY + "/" + name + ".run.in"
                or item["source_xml"] != XML_DIRECTORY + "/" + name + ".xml"):
            raise ValueError("unexpected source input/XML/checkpoint identity")
        for key in SOURCE_KEYS:
            if key.endswith("sha256"):
                base._sha(item[key])
        files = item["files"]
        if not isinstance(files, list) or len(files) != 27:
            raise ValueError("full 27-file source checkpoint required")
        for entry in files:
            base._keys(entry, {"path", "size_bytes", "sha256"}, "checkpoint file")
            if entry["path"] not in CHECKPOINT_FILES or type(entry["size_bytes"]) is not int or entry["size_bytes"] <= 0:
                raise ValueError("unexpected or empty checkpoint file")
            base._sha(entry["sha256"])
        if [entry["path"] for entry in files] != sorted(CHECKPOINT_FILES):
            raise ValueError("checkpoint file set must be exact, sorted and unique")
        xml = next(entry for entry in files if entry["path"] == "data-file-schema.xml")
        if xml["sha256"] != item["source_xml_sha256"]:
            raise ValueError("source XML evidence differs from checkpoint XML")
        found[name] = item
    return found


def _scalar(text, key):
    return force.number(base._assignment(text, key))


def _card(text, name, rows):
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines) if line.strip() == name]
    if len(starts) != 1 or len(lines) < starts[0]+1+rows:
        raise ValueError("missing or duplicated card: " + name)
    return [line.split() for line in lines[starts[0]+1:starts[0]+1+rows]]


def validate_source_deck(raw, item):
    text = raw.decode("utf-8")
    base.validate_deck(raw, dict(job=item["source_job"], prefix=item["prefix"], mode="tight"))
    for key, expected in (("ecutwfc", 80), ("ecutrho", 640), ("degauss", 0.01), ("nspin", 2),
                          ("nat", 75), ("ntyp", 7), ("electron_maxstep", 300)):
        if _scalar(text, key) != expected:
            raise ValueError("unexpected source physical setting: " + key)
    for key, expected in (("occupations", "'smearing'"), ("smearing", "'mv'"), ("mixing_mode", "'local-TF'")):
        if base._assignment(text, key) != expected:
            raise ValueError("unexpected source setting: " + key)
    if _card(text, "K_POINTS automatic", 1) != [["4", "2", "1", "0", "0", "0"]]:
        raise ValueError("unexpected source k-point mesh")
    if re.findall(r"(?m)^HUBBARD\s*\(([^)]+)\)\s*$", text) != ["ortho-atomic"]:
        raise ValueError("source must use ortho-atomic projectors")
    species = _card(text, "ATOMIC_SPECIES", 7)
    if any(len(row) != 3 for row in species) or {row[2] for row in species} != UPFS:
        raise ValueError("unexpected source pseudopotential files")
    labels, masks, _ = force.input_atoms(text)
    positions = _card(text, "ATOMIC_POSITIONS angstrom", 75)
    cell = _card(text, "CELL_PARAMETERS angstrom", 3)
    if any(len(row) != 7 for row in positions) or any(len(row) != 3 for row in cell):
        raise ValueError("explicit Cartesian masks and angstrom geometry required")
    if re.search(r"(?im)^\s*nbnd\s*=", text) and _scalar(text, "nbnd") != 404:
        raise ValueError("source band count differs from 404")
    return dict(text=text, labels=labels, masks=masks, species=species,
                positions=[[force.number(value) for value in row[1:4]] for row in positions],
                cell=[[force.number(value) for value in row] for row in cell])


def validate_deck(raw, source_raw, job):
    """Exact source bytes except private outdir and one declared numerical scalar."""
    source = source_raw.decode("utf-8")
    expected = source
    replacements = {"outdir": "'./tmp_" + job["job"] + "'", **ARMS[job["arm"]]}
    for key, value in replacements.items():
        old = base._assignment(source, key)  # Exactly one source assignment.
        new = base._assignment(raw.decode("utf-8"), key)
        if key == "outdir":
            if new != value:
                raise ValueError("unexpected target outdir")
        elif force.number(new) != value:
            raise ValueError("unexpected target arm value")
        pattern = re.compile(r"(?m)^(\s*" + re.escape(key) + r"\s*=\s*)" + re.escape(old) + r"(?=\s*$)")
        expected, count = pattern.subn(lambda match: match[1] + new, expected)
        if count != 1:
            raise ValueError("source scalar format unsupported: " + key)
    if raw != expected.encode("utf-8"):
        raise ValueError("undeclared source-to-target input byte change")
    # This enforces file/file, from_scratch, 1e-8, beta0.3, exact pseudo/outdir.
    base.validate_deck(raw, dict(job=job["job"], prefix=job["prefix"], mode="tight"))


def validate_source_xml(raw, source, item):
    """Source identity and recorded basis; no assertion of conserved magnetic basin."""
    if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise ValueError("unsupported XML declarations")
    tree = ET.fromstring(raw)
    for element in tree.iter():
        element.tag = element.tag.rsplit("}", 1)[-1]
    if tree.attrib.get("Units") != "Hartree atomic units":
        raise ValueError("unsupported source XML units")
    def one(path):
        nodes = tree.findall(path)
        if len(nodes) != 1:
            raise ValueError("one source XML node required: " + path)
        return nodes[0]
    def value(path):
        return (one(path).text or "").strip()
    def number(path):
        return force.number(value(path))
    def same(actual, expected, label):
        # Text serialization and Bohr->angstrom conversion only, not an accuracy threshold.
        if not math.isclose(actual, expected, rel_tol=1e-13, abs_tol=1e-12):
            raise ValueError("source XML identity mismatch: " + label)
    def vector(node):
        vals = [force.number(token) for token in (node.text or "").split()]
        if len(vals) != 3:
            raise ValueError("source XML vector must have three finite components")
        return vals
    if value("exit_status") != "0" or value("output/convergence_info/scf_conv/convergence_achieved") != "true":
        raise ValueError("source XML is not a successful converged SCF")
    if value("output/convergence_info/wf_collected") != "true":
        raise ValueError("source XML does not establish collected wavefunctions")
    if one("general_info/creator").attrib != {"NAME": "PWSCF", "VERSION": "7.5"}:
        raise ValueError("expected QE 7.5 source XML")
    for key, expected in (("nprocs", 128), ("npool", 8), ("nthreads", 1), ("nbgrp", 1)):
        if number("parallel_info/" + key) != expected:
            raise ValueError("source decomposition mismatch: " + key)
    for key, expected in (("calculation", "scf"), ("prefix", item["prefix"]),
                          ("outdir", "./tmp_" + item["source_job"]), ("restart_mode", "from_scratch")):
        if value("input/control_variables/" + key) != expected:
            raise ValueError("source XML control mismatch: " + key)
    for section in ("input", "output"):
        atomic = one(section + "/atomic_structure")
        if atomic.attrib.get("nat") != "75":
            raise ValueError("source XML atom count mismatch")
        atoms = atomic.findall("atomic_positions/atom")
        if len(atoms) != 75:
            raise ValueError("source XML atom rows incomplete")
        for i, (atom, label, coords) in enumerate(zip(atoms, source["labels"], source["positions"])):
            if atom.attrib.get("index") != str(i+1) or atom.attrib.get("name") != label:
                raise ValueError("source XML atom order/species mismatch")
            for a, b in zip(vector(atom), coords):
                same(a*BOHR_ANGSTROM, b, "atomic position")
        for i, coords in enumerate(source["cell"]):
            for a, b in zip(vector(one(section + "/atomic_structure/cell/a" + str(i+1))), coords):
                same(a*BOHR_ANGSTROM, b, "cell")
        species = one(section + "/atomic_species")
        if species.attrib.get("ntyp") != "7" or len(species.findall("species")) != 7:
            raise ValueError("source XML species count mismatch")
        for i, (node, row) in enumerate(zip(species.findall("species"), source["species"])):
            if node.attrib.get("name") != row[0] or node.findtext("pseudo_file") != row[2]:
                raise ValueError("source XML pseudopotential/species mismatch")
            same(force.number(node.findtext("mass", "")), force.number(row[1]), "species mass")
            same(force.number(node.findtext("starting_magnetization", "")),
                 _scalar(source["text"], "starting_magnetization(" + str(i+1) + ")"), "initial spin")
        basis = section + ("/basis" if section == "input" else "/basis_set")
        for key in ("ecutwfc", "ecutrho"):
            same(2*number(basis + "/" + key), _scalar(source["text"], key), key)
    flags = [int(token) for token in value("input/free_positions").split()]
    if flags != [flag for atom in source["masks"] for flag in atom]:
        raise ValueError("source XML Cartesian constraint mask mismatch")
    mesh = {key: str(val) for key, val in zip(("nk1", "nk2", "nk3", "k1", "k2", "k3"), (4, 2, 1, 0, 0, 0))}
    for path in ("input/k_points_IBZ/monkhorst_pack", "output/band_structure/starting_k_points/monkhorst_pack"):
        if one(path).attrib != mesh:
            raise ValueError("source XML k-point mesh mismatch")
    for path in ("input/spin", "output/band_structure"):
        for key, expected in (("lsda", "true"), ("noncolin", "false"), ("spinorbit", "false")):
            if value(path + "/" + key) != expected:
                raise ValueError("source XML spin representation mismatch")
    for path in ("input/bands/smearing", "output/band_structure/smearing"):
        if value(path) != "mv":
            raise ValueError("source XML smearing kind mismatch")
        same(2*force.number(one(path).attrib.get("degauss", "")), 0.01, "smearing width")
    same(2*number("input/electron_control/conv_thr"), 1e-8, "SCF threshold")
    same(number("input/electron_control/mixing_beta"), 0.3, "mixing beta")
    if number("input/electron_control/max_nstep") != 300:
        raise ValueError("source XML electron iteration limit mismatch")
    if value("input/dft/functional") != "PBE" or value("input/dft/dftU/U_projection_type") != "ortho-atomic":
        raise ValueError("source XML functional/projector mismatch")
    u_rows = re.findall(r"(?m)^U\s+(\S+)-3d\s+(\S+)\s*$", source["text"])
    u_nodes = one("input/dft/dftU").findall("Hubbard_U")
    if len(u_nodes) != len(u_rows):
        raise ValueError("source XML Hubbard entries mismatch")
    for node, (label, amount) in zip(u_nodes, u_rows):
        if node.attrib != {"specie": label, "label": "3d"}:
            raise ValueError("source XML Hubbard species/manifold mismatch")
        same(force.number(node.text or "")*HARTREE_EV, force.number(amount), "Hubbard U")
    for key, expected in (("nbnd_up", 404), ("nbnd_dw", 404), ("nks", 8)):
        if number("output/band_structure/" + key) != expected:
            raise ValueError("source XML band/k-point count mismatch")
    kstates = one("output/band_structure").findall("ks_energies")
    if len(kstates) != 8:
        raise ValueError("source XML k-state rows incomplete")
    def cross(a, b):
        return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
    cell = source["cell"]
    volume = sum(a*b for a, b in zip(cell[0], cross(cell[1], cell[2])))
    if volume <= 0:
        raise ValueError("source cell must have positive volume")
    alat = force.number(one("output/atomic_structure").attrib.get("alat", ""))*BOHR_ANGSTROM
    reciprocal = [[value*alat/volume for value in cross(cell[(i+1)%3], cell[(i+2)%3])] for i in range(3)]
    for i, basis in enumerate(reciprocal):
        for a, b in zip(vector(one("output/basis_set/reciprocal_lattice/b" + str(i+1))), basis):
            same(a, b, "reciprocal cell")
    fractional = [(a, b, 0.0) for a in (0.0, 0.25, -0.5, -0.25) for b in (0.0, -0.5)]
    for state, frac in zip(kstates, fractional):
        for tag in ("eigenvalues", "occupations"):
            nodes = state.findall(tag)
            if len(nodes) != 1 or nodes[0].attrib.get("size") != "808":
                raise ValueError("source XML band array size mismatch")
            values = [force.number(token) for token in (nodes[0].text or "").split()]
            if len(values) != 808:
                raise ValueError("source XML band array incomplete")
        points = state.findall("k_point")
        if len(points) != 1:
            raise ValueError("source XML k-point record missing")
        point = vector(points[0])
        expected_point = [sum(frac[i]*reciprocal[i][j] for i in range(3)) for j in range(3)]
        for a, b in zip(point, expected_point):
            same(a, b, "ordered reciprocal k point")
        same(force.number(points[0].attrib.get("weight", "")), 0.125, "k-point weight")
    error = number("output/convergence_info/scf_conv/scf_error")
    if error < 0 or error > number("input/electron_control/conv_thr"):
        raise ValueError("source XML SCF error exceeds its accepted threshold")
    return dict(converged=True, nbnd_up=404, nbnd_down=404, nks=8,
                scf_error_hartree=error,
                energy_hartree=number("output/total_energy/etot"),
                smearing_contribution_hartree=number("output/total_energy/demet"),
                total_moment_muB=number("output/magnetization/total"),
                absolute_moment_muB=number("output/magnetization/absolute"),
                geometry_identity_tolerance_angstrom=1e-12,
                checkpoint_interpretation="Accepted source metadata and byte identity; cutoff file-start is warm initialization, not exact basis/basin preservation")


def load_bundle(spec_path, runs):
    supplied = Path(runs).absolute()
    if base._link(supplied) or not supplied.is_dir():
        raise ValueError("runs must be an existing real directory")
    root = supplied.resolve(strict=True)
    spec = validate_spec(_json(_read(Path(spec_path))))
    inventory_raw = _read(_path(root.parent, spec["source_checkpoints"]))
    if _digest(inventory_raw) != spec["source_checkpoints_sha256"]:
        raise ValueError("source inventory SHA256 mismatch")
    checkpoints = validate_inventory(_json(inventory_raw))
    raw = _read(_path(root.parent, spec["manifest"]))
    if _digest(raw) != spec["manifest_sha256"] or b"\r" in raw or b"\x00" in raw or not raw.endswith(b"\n"):
        raise ValueError("manifest bytes/hash invalid")
    text = raw.decode("utf-8")
    headers = [line for line in text.splitlines() if line.lstrip().startswith("#") and re.search(r"\b(?:NP|NCONC)\s*=", line, re.I)]
    if headers != ["# NP=128 NCONC=1"]:
        raise ValueError("exactly one sensitivity resource header required")
    rows = ["{dir} {job} {suffix} {nk}".format(**job) for job in spec["jobs"]]
    if [line for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")] != rows:
        raise ValueError("manifest rows differ from ordered spec")
    lines = _path(root.parent, spec["manifest"] + ".lines")
    if _read(lines) != ("\n".join(rows) + "\n").encode():
        raise ValueError("manifest .lines differs from ordered spec")
    sources, metadata = {}, {}
    for name, item in checkpoints.items():
        source_raw = _read(_path(root.parent, item["source_input"]))
        xml_raw = _read(_path(root.parent, item["source_xml"]))
        if _digest(source_raw) != item["source_input_sha256"] or _digest(xml_raw) != item["source_xml_sha256"]:
            raise ValueError("source input/XML hash mismatch")
        for suffix, key in ((".out", "source_output_sha256"), (".projwfc.out", "source_projection_sha256"), (".qc.json", "source_qc_sha256")):
            if _digest(_read(_path(root, SOURCE_DIRECTORY + "/" + name + suffix))) != item[key]:
                raise ValueError("source raw/QC hash mismatch: " + key)
        sources[name] = source_raw
        metadata[name] = validate_source_xml(xml_raw, validate_source_deck(source_raw, item), item)
    for job in spec["jobs"]:
        raw = _read(_path(root, job["dir"] + "/" + job["job"] + ".in"))
        if _digest(raw) != job["sha256"]:
            raise ValueError("sensitivity input SHA256 mismatch")
        validate_deck(raw, sources[job["source_job"]], job)
    return dict(spec=spec, root=root, checkpoints=checkpoints, metadata=metadata)


def validate_batch(spec_path, runs, row=None):
    checked = load_bundle(spec_path, runs)
    spec, root = checked["spec"], checked["root"]
    if row is not None and (type(row) is not int or not 1 <= row <= 6):
        raise ValueError("row must be one-based index 1..6")
    if "NOT LICENSED" in _read(_path(root.parent, spec["manifest"])).decode().upper():
        raise ValueError("manifest is NOT LICENSED")
    selected = spec["jobs"] if row is None else [spec["jobs"][row-1]]
    for job in selected:
        base._fresh(root, job)
    for name in dict.fromkeys(job["source_job"] for job in selected):
        base.verify_source(root, checked["checkpoints"][name])
    checked["selected"] = None if row is None else selected[0]
    return checked


def prepare_row(spec_path, runs, row):
    checked = validate_batch(spec_path, runs, row)
    root, job = checked["root"], checked["selected"]
    checkpoint = checked["checkpoints"][job["source_job"]]
    source = _path(root, checkpoint["dir"])
    scratch = _path(root, job["dir"] + "/tmp_" + job["job"])
    scratch.mkdir()
    destination = scratch / (job["prefix"] + ".save")
    destination.mkdir()
    for entry in checkpoint["files"]:
        src, dst = _path(source, entry["path"]), _path(destination, entry["path"])
        digest, size = hashlib.sha256(), 0
        with src.open("rb") as reader, dst.open("xb") as writer:
            for chunk in iter(lambda: reader.read(base.CHUNK), b""):
                writer.write(chunk)
                digest.update(chunk)
                size += len(chunk)
        if (size, digest.hexdigest()) != (entry["size_bytes"], entry["sha256"]) or base._stream_hash(dst) != (entry["size_bytes"], entry["sha256"]):
            raise ValueError("clone hash/size mismatch; partial clone retained")
    if base._source_files(source) != [entry["path"] for entry in checkpoint["files"]]:
        raise ValueError("source members changed during clone; partial clone retained")
    raw = _read(_path(root, job["dir"] + "/" + job["job"] + ".in"))
    if _digest(raw) != job["sha256"]:
        raise ValueError("input changed during clone; partial clone retained")
    with _path(root, job["dir"] + "/" + job["job"] + ".run.in").open("xb") as handle:
        handle.write(raw)
    receipt = dict(schema="hea_sensitivity_clone_v1", job=job["job"], prefix=job["prefix"], source_job=job["source_job"],
                   arm=job["arm"], source=checkpoint["dir"], destination=destination.relative_to(root).as_posix(),
                   source_checkpoints_sha256=checked["spec"]["source_checkpoints_sha256"], files=checkpoint["files"])
    with _path(root, job["dir"] + "/" + job["job"] + ".clone_receipt.json").open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(receipt, handle, indent=2)
        handle.write("\n")
    return checked


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path)
    parser.add_argument("--runs", type=Path)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--row", type=int)
    selection.add_argument("--prepare-row", type=int)
    parser.add_argument("--startup-output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.startup_output is not None:
            if any(value is not None for value in (args.spec, args.runs, args.row, args.prepare_row)):
                raise ValueError("startup check is standalone")
            print(json.dumps(base.validate_startup(_read(args.startup_output).decode("utf-8"), "tight"), sort_keys=True))
            return 0
        if args.spec is None or args.runs is None:
            raise ValueError("--spec and --runs required")
        checked = (prepare_row(args.spec, args.runs, args.prepare_row) if args.prepare_row is not None else validate_batch(args.spec, args.runs, args.row))
    except (OSError, ValueError, ET.ParseError) as exc:
        print("REFUSE: " + str(exc), file=sys.stderr)
        return 2
    job = checked["selected"]
    print("VALID" if job is None else "{dir} {job} {suffix} {nk} {prefix} {source_job} {arm}".format(**job))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
