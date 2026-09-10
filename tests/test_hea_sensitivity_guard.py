"""Independent source clones, six isolated arms and frozen source/XML identity."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/dft"))
import hea_sensitivity_guard as sg

SPECIES = [("Cr", 51.996, "cr_pbe_v1.5.uspp.F.UPF"), ("Cu", 63.546, "Cu.paw.z_11.ld1.psl.v1.0.0-low.upf"),
           ("Mn", 54.938, "mn_pbe_v1.5.uspp.F.UPF"), ("Ni", 58.693, "ni_pbe_v1.4.uspp.F.UPF"),
           ("O1", 15.999, "O.pbe-n-kjpaw_psl.0.1.UPF"), ("O2", 15.999, "O.pbe-n-kjpaw_psl.0.1.UPF"),
           ("H", 1.008, "H.pbe-rrkjus_psl.1.0.0.UPF")]


def put(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw.encode() if isinstance(raw, str) else raw)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def dump(path, value):
    put(path, json.dumps(value, indent=2)+"\n")


def source_deck(endpoint):
    job = "hn__leader_" + endpoint + "__ortho__tight"
    text = f"""&CONTROL
  calculation = 'scf'
  restart_mode = 'from_scratch'
  prefix = '{sg._prefix(endpoint)}'
  outdir = './tmp_{job}'
  pseudo_dir = '/anvil/projects/x-che260157/pseudo'
  max_seconds = 13200
/
&SYSTEM
  nat = 75
  ntyp = 7
  ecutwfc = 80.0
  ecutrho = 640.0
  degauss = 0.01
  nspin = 2
  occupations = 'smearing'
  smearing = 'mv'
"""
    text += "".join(f"  starting_magnetization({i}) = 0.2\n" for i in range(1, 8))
    text += """/
&ELECTRONS
  startingpot = 'file'
  startingwfc = 'file'
  conv_thr = 1.0d-8
  mixing_beta = 0.3
  mixing_mode = 'local-TF'
  electron_maxstep = 300
/
ATOMIC_SPECIES
"""
    text += "".join(f"  {label} {mass} {pseudo}\n" for label, mass, pseudo in SPECIES)
    text += "CELL_PARAMETERS angstrom\n  6 0 0\n  0 12 0\n  0 0 24\nATOMIC_POSITIONS angstrom\n"
    for i in range(75):
        text += f"  {SPECIES[i%7][0]} {i%5} {(i//5)%10} {4+(i//50)+(0.1 if endpoint == 'pull2.10' and i>71 else 0)} " + ("0 0 0" if i < 8 else "1 1 1") + "\n"
    text += "K_POINTS automatic\n  4 2 1 0 0 0\nHUBBARD (ortho-atomic)\nU Cr-3d 3.7000\nU Mn-3d 3.9000\nU Ni-3d 6.2000\n"
    return text.encode()


def source_xml(raw, endpoint):
    source = sg.validate_source_deck(raw, dict(source_job="hn__leader_"+endpoint+"__ortho__tight", prefix=sg._prefix(endpoint)))
    tree = ET.Element("espresso", Units="Hartree atomic units")
    def add(parent, tag, text=None, **attrs):
        node = ET.SubElement(parent, tag, {k:str(v) for k,v in attrs.items()})
        node.text = None if text is None else str(text)
        return node
    general = add(tree, "general_info")
    add(general, "creator", "QE", NAME="PWSCF", VERSION="7.5")
    parallel = add(tree, "parallel_info")
    for key, val in (("nprocs", 128), ("npool", 8), ("nthreads", 1), ("nbgrp", 1)):
        add(parallel, key, val)
    inp, out = add(tree, "input"), add(tree, "output")
    control = add(inp, "control_variables")
    for key, val in (("calculation", "scf"), ("prefix", sg._prefix(endpoint)), ("outdir", "./tmp_hn__leader_"+endpoint+"__ortho__tight"), ("restart_mode", "from_scratch")):
        add(control, key, val)
    for parent in (inp, out):
        species = add(parent, "atomic_species", ntyp=7)
        for label, mass, pseudo in SPECIES:
            atom = add(species, "species", name=label)
            add(atom, "mass", mass)
            add(atom, "pseudo_file", pseudo)
            add(atom, "starting_magnetization", 0.2)
        structure = add(parent, "atomic_structure", nat=75, alat=6/sg.BOHR_ANGSTROM)
        positions = add(structure, "atomic_positions")
        for i, (label, coords) in enumerate(zip(source["labels"], source["positions"])):
            add(positions, "atom", " ".join(str(x/sg.BOHR_ANGSTROM) for x in coords), name=label, index=i+1)
        cell = add(structure, "cell")
        for i, coords in enumerate(source["cell"]):
            add(cell, "a"+str(i+1), " ".join(str(x/sg.BOHR_ANGSTROM) for x in coords))
        basis = add(parent, "basis" if parent is inp else "basis_set")
        add(basis, "ecutwfc", 40)
        add(basis, "ecutrho", 320)
        if parent is out:
            reciprocal = add(basis, "reciprocal_lattice")
            for key, vals in (("b1", "1 0 0"), ("b2", "0 0.5 0"), ("b3", "0 0 0.25")):
                add(reciprocal, key, vals)
    add(inp, "free_positions", " ".join(str(v) for row in source["masks"] for v in row))
    mesh = dict(nk1=4, nk2=2, nk3=1, k1=0, k2=0, k3=0)
    add(add(inp, "k_points_IBZ"), "monkhorst_pack", **mesh)
    bands = add(out, "band_structure")
    for parent in (add(inp, "spin"), bands):
        for key, val in (("lsda", "true"), ("noncolin", "false"), ("spinorbit", "false")):
            add(parent, key, val)
    add(add(inp, "bands"), "smearing", "mv", degauss=0.005)
    add(bands, "smearing", "mv", degauss=0.005)
    add(add(bands, "starting_k_points"), "monkhorst_pack", **mesh)
    for key, val in (("nbnd_up", 404), ("nbnd_dw", 404), ("nks", 8)):
        add(bands, key, val)
    for x in (0, 0.25, -0.5, -0.25):
        for y in (0, -0.25):
            state = add(bands, "ks_energies")
            add(state, "k_point", f"{x} {y} 0", weight=0.125)
            for name in ("eigenvalues", "occupations"):
                add(state, name, " ".join(["0"]*808), size=808)
    electrons = add(inp, "electron_control")
    for key, val in (("conv_thr", 5e-9), ("mixing_beta", 0.3), ("max_nstep", 300)):
        add(electrons, key, val)
    dft = add(inp, "dft")
    add(dft, "functional", "PBE")
    dftu = add(dft, "dftU")
    add(dftu, "U_projection_type", "ortho-atomic")
    for label, amount in (("Cr", 3.7), ("Mn", 3.9), ("Ni", 6.2)):
        add(dftu, "Hubbard_U", amount/sg.HARTREE_EV, specie=label, label="3d")
    conv_info = add(out, "convergence_info")
    add(conv_info, "wf_collected", "true")
    conv = add(conv_info, "scf_conv")
    add(conv, "convergence_achieved", "true")
    add(conv, "scf_error", 4e-9)
    energy = add(out, "total_energy")
    add(energy, "etot", -4000)
    add(energy, "demet", 0.001)
    magnet = add(out, "magnetization")
    add(magnet, "total", 40)
    add(magnet, "absolute", 65)
    add(tree, "exit_status", 0)
    return ET.tostring(tree)


@pytest.fixture
def sensitivity(tmp_path):
    runs = tmp_path / "runs"
    runs.mkdir()
    checkpoints = []
    for endpoint, name in zip(sg.ENDPOINTS, sg.SOURCE_JOBS):
        prefix = sg._prefix(endpoint)
        item = dict(source_job=name, prefix=prefix, dir=sg.SOURCE_DIRECTORY+"/tmp_"+name+"/"+prefix+".save",
                    source_input="runs/"+sg.SOURCE_DIRECTORY+"/"+name+".run.in",
                    source_xml=sg.XML_DIRECTORY+"/"+name+".xml")
        raw = source_deck(endpoint)
        xml = source_xml(raw, endpoint)
        put(tmp_path / item["source_input"], raw)
        put(tmp_path / item["source_xml"], xml)
        item.update(source_input_sha256=sha(raw), source_xml_sha256=sha(xml))
        for suffix, key in ((".out", "source_output_sha256"), (".projwfc.out", "source_projection_sha256"), (".qc.json", "source_qc_sha256")):
            data = (name+suffix).encode()
            put(runs / sg.SOURCE_DIRECTORY / (name+suffix), data)
            item[key] = sha(data)
        files = []
        for path in sorted(sg.CHECKPOINT_FILES):
            data = xml if path == "data-file-schema.xml" else (name+"/"+path).encode()
            put(runs / item["dir"] / path, data)
            files.append(dict(path=path, size_bytes=len(data), sha256=sha(data)))
        item["files"] = files
        checkpoints.append(item)
    inventory = dict(schema=sg.SOURCE_SCHEMA, checkpoints=checkpoints)
    dump(tmp_path / sg.INVENTORY, inventory)
    jobs = []
    for name, (endpoint, arm) in sg.EXPECTED.items():
        source_job = "hn__leader_"+endpoint+"__ortho__tight"
        raw = source_deck(endpoint)
        raw = raw.replace(("./tmp_"+source_job).encode(), ("./tmp_"+name).encode())
        old, new = {"wfc": (b"ecutwfc = 80.0", b"ecutwfc = 100.0"), "rho": (b"ecutrho = 640.0", b"ecutrho = 800.0"), "smearing": (b"degauss = 0.01", b"degauss = 0.005")}[arm]
        raw = raw.replace(old, new)
        put(runs / sg.DIRECTORY / (name+".in"), raw)
        jobs.append(dict(job=name, dir=sg.DIRECTORY, suffix=".in", nk=8, sha256=sha(raw), prefix=sg._prefix(endpoint), source_job=source_job, arm=arm))
    rows = ["{dir} {job} {suffix} {nk}".format(**job) for job in jobs]
    manifest = ("# NP=128 NCONC=1\n# SUBMIT WITH EXCLUDE=a024\n"+"\n".join(rows)+"\n").encode()
    put(tmp_path / sg.MANIFEST, manifest)
    put(tmp_path / (sg.MANIFEST+".lines"), "\n".join(rows)+"\n")
    spec = dict(schema=sg.SCHEMA, manifest=sg.MANIFEST, manifest_sha256=sha(manifest), np=128, concurrency=1,
                wall_hours=4, source_checkpoints=sg.INVENTORY, source_checkpoints_sha256=sha((tmp_path / sg.INVENTORY).read_bytes()), jobs=jobs)
    path = tmp_path / "spec.json"
    dump(path, spec)
    return tmp_path, path, spec, inventory


def repin_inventory(fixture):
    root, spec_path, spec, inventory = fixture
    dump(root / sg.INVENTORY, inventory)
    spec["source_checkpoints_sha256"] = sha((root / sg.INVENTORY).read_bytes())
    dump(spec_path, spec)


def test_two_accepted_sources_seed_six_exact_arms_without_shared_scratch(sensitivity, capsys):
    root, path, spec, _ = sensitivity
    checked = sg.load_bundle(path, root / "runs")
    assert list(checked["checkpoints"]) == sg.SOURCE_JOBS
    assert len(checked["spec"]["jobs"]) == 6
    assert all(m["nbnd_up"] == 404 and m["converged"] for m in checked["metadata"].values())
    assert sg.main(["--spec", str(path), "--runs", str(root / "runs"), "--row", "3"]) == 0
    assert capsys.readouterr().out.strip().split() == [spec["jobs"][2][k] if k != "nk" else "8" for k in ("dir", "job", "suffix", "nk", "prefix", "source_job", "arm")]
    snapshots = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
    for row in (1, 3, 5):
        result = sg.prepare_row(path, root / "runs", row)
        job = result["selected"]
        folder = root / "runs" / job["dir"]
        assert (folder / (job["job"]+".run.in")).read_bytes() == (folder / (job["job"]+".in")).read_bytes()
        receipt = json.loads((folder / (job["job"]+".clone_receipt.json")).read_text())
        assert receipt["source_job"] == sg.SOURCE_JOBS[0]
        assert receipt["arm"] == job["arm"] and len(receipt["files"]) == 27
        for entry in receipt["files"]:
            source = root / "runs" / receipt["source"] / entry["path"]
            dest = root / "runs" / receipt["destination"] / entry["path"]
            assert source.read_bytes() == dest.read_bytes()
            assert not source.samefile(dest)
    assert all(p.read_bytes() == value for p, value in snapshots.items())
    # Completed siblings do not block another selected row or a post-launch readout.
    sg.validate_batch(path, root / "runs", 2)
    sg.load_bundle(path, root / "runs")
    with pytest.raises(ValueError, match="preexisting"):
        sg.validate_batch(path, root / "runs")


@pytest.mark.parametrize("key,value", [("np", 64), ("np", True), ("concurrency", 2), ("wall_hours", 8)])
def test_resource_expansion_refused(sensitivity, key, value):
    root, path, spec, _ = sensitivity
    spec[key] = value
    dump(path, spec)
    with pytest.raises(ValueError):
        sg.load_bundle(path, root / "runs")


@pytest.mark.parametrize("mutation", ["order", "source", "arm", "prefix", "directory", "nk", "extra_job"])
def test_fixed_six_job_lineage_refuses_expansion_even_after_repin(sensitivity, mutation):
    root, path, spec, _ = sensitivity
    if mutation == "order":
        spec["jobs"].reverse()
    elif mutation == "extra_job":
        spec["jobs"].append(copy.deepcopy(spec["jobs"][0]))
    else:
        key, value = {"source": ("source_job", sg.SOURCE_JOBS[1]), "arm": ("arm", "cutoff"), "prefix": ("prefix", "hc__different"), "directory": ("dir", "hea/elsewhere"), "nk": ("nk", 4)}[mutation]
        spec["jobs"][0][key] = value
    dump(path, spec)
    with pytest.raises(ValueError):
        sg.load_bundle(path, root / "runs")


@pytest.mark.parametrize("old,new", [(b"mixing_beta = 0.3", b"mixing_beta = 0.1"), (b"ecutrho = 640.0", b"ecutrho = 800.0"),
                                    (b"0 0 0\n", b"1 0 0\n"), (b"startingwfc = 'file'", b"startingwfc = 'atomic+random'"),
                                    (b"U Cr-3d 3.7000", b"U Cr-3d 3.8000"), (b"\n", b"\r\n")])
def test_only_one_declared_arm_scalar_may_change(sensitivity, old, new):
    root, path, spec, _ = sensitivity
    job = spec["jobs"][0]
    target = root / "runs" / sg.DIRECTORY / (job["job"]+".in")
    raw = target.read_bytes().replace(old, new)
    target.write_bytes(raw)
    job["sha256"] = sha(raw)
    dump(path, spec)
    with pytest.raises(ValueError):
        sg.load_bundle(path, root / "runs")


@pytest.mark.parametrize("key", ["source_input_sha256", "source_xml_sha256", "source_output_sha256", "source_projection_sha256", "source_qc_sha256"])
def test_all_source_artifact_hashes_are_binding(sensitivity, key):
    root, path, _, inventory = sensitivity
    inventory["checkpoints"][0][key] = "0"*64
    repin_inventory(sensitivity)
    with pytest.raises(ValueError):
        sg.load_bundle(path, root / "runs")


@pytest.mark.parametrize("mutation", ["position", "species", "cell", "mask", "ecut", "band_count", "band_partial", "korder", "spin", "degauss", "convergence", "wf_collected", "hubbard", "nonfinite"])
def test_source_xml_physical_identity_not_only_hash(sensitivity, mutation):
    root, path, _, inventory = sensitivity
    item = inventory["checkpoints"][0]
    tree = ET.fromstring((root / item["source_xml"]).read_bytes())
    if mutation == "position":
        tree.find("output/atomic_structure/atomic_positions/atom").text = "1 2 3"
    elif mutation == "species":
        tree.find("output/atomic_species/species/pseudo_file").text = "wrong.upf"
    elif mutation == "cell":
        tree.find("output/atomic_structure/cell/a1").text = "1 0 0"
    elif mutation == "mask":
        tree.find("input/free_positions").text = "1 "*225
    elif mutation == "ecut":
        tree.find("output/basis_set/ecutwfc").text = "50"
    elif mutation == "band_count":
        tree.find("output/band_structure/nbnd_up").text = "405"
    elif mutation == "band_partial":
        tree.find("output/band_structure/ks_energies/eigenvalues").text = "0 "*807
    elif mutation == "korder":
        tree.find("output/band_structure/ks_energies/k_point").text = "0.25 0 0"
    elif mutation == "spin":
        tree.find("input/spin/noncolin").text = "true"
    elif mutation == "degauss":
        tree.find("input/bands/smearing").set("degauss", "0.01")
    elif mutation == "convergence":
        tree.find("output/convergence_info/scf_conv/scf_error").text = "1e-5"
    elif mutation == "wf_collected":
        tree.find("output/convergence_info/wf_collected").text = "false"
    elif mutation == "hubbard":
        tree.find("input/dft/dftU/Hubbard_U").text = "1.0"
    else:
        tree.find("output/total_energy/etot").text = "NaN"
    raw = ET.tostring(tree)
    put(root / item["source_xml"], raw)
    item["source_xml_sha256"] = sha(raw)
    next(entry for entry in item["files"] if entry["path"] == "data-file-schema.xml").update(sha256=sha(raw), size_bytes=len(raw))
    repin_inventory(sensitivity)
    with pytest.raises(ValueError):
        sg.load_bundle(path, root / "runs")


@pytest.mark.parametrize("change", ["corrupt", "missing", "extra"])
def test_checkpoint_change_refused_before_destination_claim(sensitivity, change):
    root, path, spec, inventory = sensitivity
    source = root / "runs" / inventory["checkpoints"][0]["dir"]
    target = source / "wfcup1.hdf5"
    if change == "corrupt":
        target.write_bytes(b"tampered")
    elif change == "missing":
        target.unlink()
    else:
        (source / "extra").write_bytes(b"new")
    with pytest.raises(ValueError):
        sg.prepare_row(path, root / "runs", 1)
    assert not (root / "runs" / sg.DIRECTORY / ("tmp_"+spec["jobs"][0]["job"])).exists()


def test_mutation_during_copy_retains_partial_clone_and_no_runtime(sensitivity, monkeypatch):
    root, path, spec, inventory = sensitivity
    original = sg.validate_batch
    def checked_then_changed(*args, **kwargs):
        result = original(*args, **kwargs)
        (root / "runs" / inventory["checkpoints"][0]["dir"] / "wfcup1.hdf5").write_bytes(b"changed after preflight")
        return result
    monkeypatch.setattr(sg, "validate_batch", checked_then_changed)
    with pytest.raises(ValueError, match="clone hash"):
        sg.prepare_row(path, root / "runs", 1)
    folder = root / "runs" / sg.DIRECTORY
    assert (folder / ("tmp_"+spec["jobs"][0]["job"])).is_dir()
    assert not (folder / (spec["jobs"][0]["job"]+".run.in")).exists()


@pytest.mark.parametrize("suffix", [".out", ".run.in", ".qc.json", ".clone_receipt.json", ".projwfc.out"])
def test_prior_output_never_overwritten(sensitivity, suffix):
    root, path, spec, _ = sensitivity
    prior = root / "runs" / sg.DIRECTORY / (spec["jobs"][0]["job"]+suffix)
    put(prior, "preserve")
    with pytest.raises(ValueError, match="preexisting"):
        sg.prepare_row(path, root / "runs", 1)
    assert prior.read_text() == "preserve"


def test_real_source_xml_and_fixed_six_decks_if_banked():
    path = ROOT / "results/hea_sensitivity_2026-09-09/launch_spec.json"
    if not path.is_file():
        pytest.skip("banked sensitivity bundle absent")
    checked = sg.load_bundle(path, ROOT / "runs")
    assert len(checked["spec"]["jobs"]) == 6
    assert len(checked["metadata"]) == 2
    assert all(row["nbnd_up"] == 404 and row["nbnd_down"] == 404 for row in checked["metadata"].values())
