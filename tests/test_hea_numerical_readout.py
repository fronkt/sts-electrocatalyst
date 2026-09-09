"""Pending outputs, paired vectors/state diagnostics and strict evidence identity."""
import copy
import hashlib
import json
import math
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/dft"))
import hea_numerical_readout as nr
import hea_followup_qc as qc
import hea_numerical_guard as guard


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def dump(path, value):
    write(path, json.dumps(value, indent=2) + "\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def deck(prefix, projector="atomic", pull=False):
    return f"""&CONTROL
 calculation='scf'
 prefix='{prefix}'
 outdir='./tmp_{prefix}'
 pseudo_dir='/anvil/projects/x-che260157/pseudo'
 max_seconds=13200
/
&SYSTEM
 nat=2
 ecutwfc=80
 ecutrho=640
 nspin=2
/
&ELECTRONS
 conv_thr=1.0d-6
 mixing_beta=0.3
 electron_maxstep=300
/
ATOMIC_SPECIES
Cr 51.996 cr.UPF
O 15.999 o.UPF
CELL_PARAMETERS angstrom
5 0 0
0 5 0
0 0 20
ATOMIC_POSITIONS angstrom
Cr 0 0 0 1 0 1
O 0 0 {3 if pull else 2} 0 0 0
K_POINTS automatic
4 2 1 0 0 0
HUBBARD ({'atomic' if projector == 'atomic' else 'ortho-atomic'})
U Cr-3d 3.7000
"""


def hubbard(delta=0.0):
    body = "=================== HUBBARD OCCUPATIONS ===================\n"
    body += "------------------------ ATOM    1 ------------------------\n"
    body += f"Tr[ns(  1)] (up, down, total) = {3+delta:.5f} 1.00000 {4+delta:.5f}\n"
    body += f"Atomic magnetic moment for atom   1 = {2+delta:.5f}\n"
    for spin, value in ((1, 0.6+delta/5), (2, 0.2)):
        body += f"SPIN  {spin}\neigenvalues:\n" + " ".join([f"{value:.3f}"]*5) + "\n"
        body += "eigenvectors (columns):\n"
        body += "\n".join(" ".join("1.000" if i == j else "0.000" for j in range(5)) for i in range(5)) + "\n"
        body += "occupation matrix ns (before diag.):\n"
        body += "\n".join(" ".join(f"{value:.3f}" if i == j else "0.000" for j in range(5)) for i in range(5)) + "\n"
    return body + f"Number of occupied Hubbard levels = {4+delta:.4f}\n"


def output(energy=-10, mode=None, changed=False):
    startup = ""
    if mode:
        startup = "The initial density is read from file\n" + (
            "Starting wfcs from file\n" if mode == "tight" else "Starting wfcs are  12 randomized atomic wfcs\n")
    return startup + "number of atoms/cell = 2\nEnd of self-consistent calculation\n" + hubbard(0.1 if changed else 0) + f"""!    total energy = {energy:.8f} Ry
convergence has been achieved in 3 iterations
total magnetization = {2.2 if changed else 2.0} Bohr mag/cell
absolute magnetization = {2.2 if changed else 2.0} Bohr mag/cell
Forces acting on atoms (cartesian axes, Ry/au):
 atom 1 type 1 force = {'0.20000000 10.00000000 0.40000000' if changed else '0.10000000 0.20000000 0.30000000'}
 atom 2 type 2 force = 2.00000000 0.00000000 0.00000000
 Total force = 2.10000000
 JOB DONE.
"""


def projection(changed=False):
    return f"""Lowdin Charges:
 Atom # 1: total charge = 6.0000, s = 2.0000, d = 4.0000,
 spin up = {4.1 if changed else 4:.4f}, s = 1.0000, d = {3.1 if changed else 3:.4f},
 spin down = {1.9 if changed else 2:.4f}, s = 1.0000, d = {0.9 if changed else 1:.4f},
 polarization = {2.2 if changed else 2:.4f}, s = 0.0000, d = {2.2 if changed else 2:.4f},
 Atom # 2: total charge = 6.0000, s = 2.0000, p = 4.0000,
 spin up = 3.0000, s = 1.0000, p = 2.0000,
 spin down = 3.0000, s = 1.0000, p = 2.0000,
 polarization = 0.0000, s = 0.0000, p = 0.0000,
 Spilling Parameter: 0.0022
 JOB DONE.
"""


def complete(folder, job, text, energy, mode=None, changed=False):
    write(folder / (job + ".run.in"), text)
    write(folder / (job + ".out"), output(energy, mode, changed))
    write(folder / (job + ".projwfc.out"), projection(changed))
    audit = qc.audit_files(*(folder / (job + suffix) for suffix in (".run.in", ".out", ".projwfc.out")))
    assert audit["status"] == "COMPLETE", audit
    dump(folder / (job + ".qc.json"), audit)


@pytest.fixture
def batch(tmp_path):
    old = tmp_path / nr.SOURCE_DIR
    new = tmp_path / "runs" / guard.DIRECTORY
    jobs, checkpoints = [], []
    for job, (endpoint, projector, seed, mode) in nr.EXPECTED.items():
        prefix = f"hc__leader_{endpoint}__{projector}__{seed}"
        source = deck(prefix, projector, endpoint != "builder")
        energy = -10 if endpoint == "builder" else -12
        if mode == "tight":
            complete(old, prefix, source, energy)
        else:
            write(old / (prefix + ".run.in"), source)
            write(old / (prefix + ".out"), "convergence NOT achieved\n! total energy = -99999 Ry\n")
        target = source.replace(" calculation='scf'", " calculation='scf'\n restart_mode='from_scratch'")
        target = target.replace("&ELECTRONS\n", "&ELECTRONS\n startingpot='file'\n startingwfc='" + ("file" if mode == "tight" else "atomic+random") + "'\n")
        target = target.replace("./tmp_"+prefix, "./tmp_"+job)
        target = target.replace("conv_thr=1.0d-6", "conv_thr=1.0d-8") if mode == "tight" else target.replace("mixing_beta=0.3", "mixing_beta=0.1")
        path = new / (job + ".in")
        write(path, target)
        jobs.append(dict(job=job, dir=guard.DIRECTORY, suffix=".in", nk=8, sha256=sha(path), prefix=prefix, mode=mode))
        files = guard.PORTABLE_FILES | (guard.WFC_FILES if mode == "tight" else set())
        checkpoints.append(dict(prefix=prefix, dir=guard.SOURCE_DIRECTORY+"/tmp_"+prefix+"/"+prefix+".save",
                                files=[dict(path=p, size_bytes=1, sha256="0"*64) for p in sorted(files)]))
    for endpoint, seed in (("builder", "baseline"), ("pull2.10", "metal_alternating")):
        prefix = f"hc__leader_{endpoint}__ortho__{seed}"
        complete(old, prefix, deck(prefix, "ortho", endpoint != "builder"), -10 if endpoint == "builder" else -12)
    inventory = tmp_path / guard.INVENTORY
    dump(inventory, dict(schema=guard.SOURCE_SCHEMA, checkpoints=checkpoints))
    manifest = tmp_path / guard.MANIFEST
    write(manifest, "# NP=128 NCONC=1\n" + "\n".join("{dir} {job} {suffix} {nk}".format(**j) for j in jobs) + "\n")
    spec = dict(schema=guard.SCHEMA, manifest=guard.MANIFEST, manifest_sha256=sha(manifest), np=128,
                concurrency=1, wall_hours=4, source_checkpoints=guard.INVENTORY, source_checkpoints_sha256=sha(inventory), jobs=jobs)
    spec_path = tmp_path / "spec.json"
    dump(spec_path, spec)
    return tmp_path, spec_path, spec, checkpoints


def finish(batch):
    root, _, spec, checkpoints = batch
    folder = root / "runs" / guard.DIRECTORY
    for job, checkpoint in zip(spec["jobs"], checkpoints):
        text = (folder / (job["job"] + ".in")).read_text()
        endpoint = nr.EXPECTED[job["job"]][0]
        complete(folder, job["job"], text, -10.01 if endpoint == "builder" else -12.03, job["mode"], True)
        receipt = dict(schema="hea_numerical_clone_v1", job=job["job"], prefix=job["prefix"], mode=job["mode"],
                       source=checkpoint["dir"], destination=job["dir"]+"/tmp_"+job["job"]+"/"+job["prefix"]+".save",
                       source_checkpoints_sha256=spec["source_checkpoints_sha256"], files=checkpoint["files"])
        dump(folder / (job["job"] + ".clone_receipt.json"), receipt)


def test_pending_retains_six_jobs_and_never_uses_failed_energy(batch):
    root, spec_path, _, _ = batch
    result = nr.build_readout(root, spec_path)
    assert result["counts"] == dict(accepted=0, pending=6, rejected=0)
    assert not result["batch_readout_complete"]
    assert result["source_counts"] == dict(accepted=6, pending=0, rejected=0, unresolved_source=2)
    assert result["status"] == "PENDING"
    assert all(p["source_gap_eV"] == pytest.approx(-2*nr.force.RY_TO_EV) for p in result["paired_tight"])
    failed = [x for x in result["sources"] if x["status"] == "UNRESOLVED_SOURCE"]
    assert len(failed) == 2 and all("energy_eV" not in row for row in failed)
    assert all(row["gap_pull_minus_builder_eV"] is None for row in result["recovery_pairs"])
    assert result["numerical_accuracy_status"] == "NOT_INFERRED"


def test_complete_pair_gap_masked_vector_and_separate_state_differences(batch):
    finish(batch)
    result = nr.build_readout(*batch[:2])
    assert result["counts"] == dict(accepted=6, pending=0, rejected=0)
    assert result["batch_readout_complete"]
    pair = result["paired_tight"][0]
    assert pair["delta_gap_eV"] == pytest.approx(-0.02*nr.force.RY_TO_EV)
    diff = pair["endpoints"][0]
    expected = 0.1*nr.force.RY_BOHR_TO_EV_A
    assert diff["n_free_components"] == 2
    assert diff["max_free_vector_difference_ev_A"] == pytest.approx(2**0.5*expected)
    assert diff["rms_free_component_difference_ev_A"] == pytest.approx(expected)
    assert diff["atoms"][0]["delta_free_force_ev_A"] == pytest.approx([expected, 0, expected])
    assert diff["atoms"][1]["delta_free_force_ev_A"] == [0, 0, 0]
    assert diff["atoms"][0]["delta_moment_muB"] == pytest.approx(0.2)
    assert diff["hubbard_atoms"][0]["delta_trace_up_e"] == pytest.approx(0.1)
    assert diff["hubbard_atoms"][0]["spins"][0]["delta_occupation_matrix"][0][0] == pytest.approx(0.02)
    assert result["recovery_pairs"][0]["gap_pull_minus_builder_eV"] == pytest.approx(-2.03*nr.force.RY_TO_EV)
    assert result["recovery_pairs"][1]["gap_pull_minus_builder_eV"] == pytest.approx(-1.99*nr.force.RY_TO_EV)
    assert all(not row["failed_source_energy_used"] for row in result["recovery_pairs"])


def test_qc_tampering_or_raw_edits_are_rejected(batch):
    finish(batch)
    root, spec_path, spec, _ = batch
    path = root / "runs" / guard.DIRECTORY / (spec["jobs"][0]["job"] + ".qc.json")
    record = json.loads(path.read_text())
    record["scf"]["energy_eV"] += 1
    dump(path, record)
    result = nr.build_readout(root, spec_path)
    assert result["counts"]["rejected"] == 1
    assert "stored QC" in result["endpoints"][0]["reasons"][0]
    assert result["paired_tight"][0]["delta_gap_eV"] is None


@pytest.mark.parametrize("mutation", ["missing_density", "wrong_wfc", "fallback", "bad_receipt", "runtime_physics", "bad_projection"])
def test_invalid_new_evidence_never_enters_pairs(batch, mutation):
    finish(batch)
    root, spec_path, spec, _ = batch
    job = spec["jobs"][0]["job"]
    folder = root / "runs" / guard.DIRECTORY
    out = folder / (job + ".out")
    if mutation in ("missing_density", "wrong_wfc", "fallback"):
        value = out.read_text()
        if mutation == "missing_density":
            value = value.replace("The initial density is read from file", "density from atoms")
        elif mutation == "wrong_wfc":
            value = value.replace("Starting wfcs from file", "Starting wfcs are 12 randomized atomic wfcs")
        else:
            value = value.replace("End of self-consistent calculation", "Cannot read wfcs: file not found\nEnd of self-consistent calculation")
        write(out, value)
    elif mutation == "bad_receipt":
        path = folder / (job + ".clone_receipt.json")
        value = json.loads(path.read_text())
        value["files"][0]["sha256"] = "1"*64
        dump(path, value)
    elif mutation == "runtime_physics":
        path = folder / (job + ".run.in")
        write(path, path.read_text().replace("ecutwfc=80", "ecutwfc=40"))
    else:
        path = folder / (job + ".projwfc.out")
        write(path, path.read_text().replace("JOB DONE.", ""))
    # Refresh QC so startup/receipt/runtime validation cannot be replaced by hash checks alone.
    audit = qc.audit_files(*(folder / (job + suffix) for suffix in (".run.in", ".out", ".projwfc.out")))
    dump(folder / (job + ".qc.json"), audit)
    result = nr.build_readout(root, spec_path)
    assert result["counts"]["rejected"] == 1
    assert result["paired_tight"][0]["delta_gap_eV"] is None


def test_declared_target_changes_do_not_allow_physical_or_mask_drift(batch):
    root, spec_path, spec, _ = batch
    job = spec["jobs"][0]
    path = root / "runs" / guard.DIRECTORY / (job["job"]+".in")
    write(path, path.read_text().replace("Cr 0 0 0 1 0 1", "Cr 0 0 0 1 1 1"))
    job["sha256"] = sha(path)
    dump(spec_path, spec)
    with pytest.raises(ValueError, match="undeclared"):
        nr.build_readout(root, spec_path)


@pytest.mark.parametrize("mutation", [
    lambda t: t.replace("End of self-consistent calculation", ""),
    lambda t: t.replace("ATOM    1", "ATOM    2"),
    lambda t: t.replace("Number of occupied Hubbard levels", "bad terminator"),
    lambda t: t.replace("0.600 0.600 0.600 0.600 0.600", "NaN 0.600 0.600 0.600 0.600"),
    lambda t: t.replace("occupation matrix ns (before diag.):", "bad matrix header", 1),
    lambda t: t.replace("SPIN  2", "SPIN  1"),
])
def test_missing_partial_nonfinite_or_reordered_final_hubbard_rejected(mutation):
    with pytest.raises(ValueError):
        nr.hubbard_occupations(deck("test"), mutation(output()))


def test_final_hubbard_excludes_initial_tables_and_no_free_coordinates(batch):
    assert nr.hubbard_occupations(deck("test"), hubbard(99) + output())["atoms"][0]["trace_up_e"] == 3
    finish(batch)
    result = nr.build_readout(*batch[:2])
    source = next(x for x in result["sources"] if x["status"] == "ACCEPTED")
    target = result["endpoints"][0]
    source, target = copy.deepcopy(source), copy.deepcopy(target)
    for record in (source, target):
        for atom in record["audit"]["scf"]["per_atom"]:
            atom["if_pos"] = [0, 0, 0]
    diff = nr.endpoint_difference(source, target)
    assert diff["max_free_vector_difference_ev_A"] is None
    assert diff["rms_free_component_difference_ev_A"] is None


def test_cli_preserves_existing_artifacts_and_all_raw_bytes(batch):
    root, spec_path, _, _ = batch
    before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
    out = root / "pending.json"
    argv = ["--root", str(root), "--spec", str(spec_path), "--out", str(out)]
    assert nr.main(argv) == 0
    first = out.read_bytes()
    assert nr.main(argv) == 2
    assert out.read_bytes() == first
    assert all(path.read_bytes() == raw for path, raw in before.items())


@pytest.mark.parametrize("projector,endpoint", [(p, e) for p in ("atomic", "ortho") for e in ("builder", "pull2.10")])
def test_banked_fragment_sources_have_complete_final_occupations(projector, endpoint):
    folder = ROOT / nr.SOURCE_DIR
    job = f"hc__leader_{endpoint}__{projector}__fragment"
    if not all((folder / (job + suffix)).is_file() for suffix in (".run.in", ".out", ".projwfc.out", ".qc.json")):
        pytest.skip("banked followup files absent in this checkout")
    result = nr.accepted_endpoint(folder, job)
    assert result["status"] == "ACCEPTED", result["reasons"]
    assert len(result["hubbard"]["atoms"]) == 23
    assert len(result["audit"]["projection"]["atoms"]) == 75


def test_only_derived_norms_allow_four_ulp_runtime_rounding():
    exact = dict(scf=dict(per_atom=[dict(norm_all_ev_A=1.0, norm_free_ev_A=1.0, force_ev_A=[1.0, 0.0, 0.0])],
                         fmax_all_ev_A=1.0, fmax_free_ev_A=1.0, energy_eV=-10.0),
                 input=dict(path="old-host-path", sha256_bytes="a"*64))
    changed = copy.deepcopy(exact)
    four = 1.0
    for _ in range(4):
        four = math.nextafter(four, math.inf)
    changed["scf"]["per_atom"][0]["norm_all_ev_A"] = four
    changed["scf"]["fmax_free_ev_A"] = four
    changed["input"]["path"] = "new-host-path"
    assert nr.qc_consistent(changed, exact)
    changed["scf"]["fmax_free_ev_A"] = math.nextafter(four, math.inf)
    assert not nr.qc_consistent(changed, exact)
    changed = copy.deepcopy(exact)
    changed["scf"]["per_atom"][0]["force_ev_A"][0] = math.nextafter(1.0, math.inf)
    assert not nr.qc_consistent(changed, exact)
    changed = copy.deepcopy(exact)
    changed["input"]["sha256_bytes"] = "b"*64
    assert not nr.qc_consistent(changed, exact)
    changed = copy.deepcopy(exact)
    changed["scf"]["energy_eV"] = math.nextafter(-10.0, math.inf)
    assert not nr.qc_consistent(changed, exact)


def test_old_source_rejection_surfaces_despite_all_new_outputs_pending(batch):
    root, spec_path, spec, _ = batch
    path = root / nr.SOURCE_DIR / (spec["jobs"][0]["prefix"] + ".qc.json")
    data = json.loads(path.read_text())
    data["input"]["sha256_bytes"] = "f"*64
    dump(path, data)
    result = nr.build_readout(root, spec_path)
    assert result["counts"] == dict(accepted=0, pending=6, rejected=0)
    assert result["source_counts"]["rejected"] == 1
    assert result["status"] == "REJECTED"
    assert result["paired_tight"][0]["status"] == "REJECTED"
    assert nr.main(["--root", str(root), "--spec", str(spec_path), "--out", str(root / "rejected.json")]) == 2


@pytest.mark.parametrize("edit", [lambda s: s.replace("./tmp_", "/different/tmp_"),
                                 lambda s: s.replace("/anvil/projects/x-che260157/pseudo", "/other/pseudo"),
                                 lambda s: s.replace("\n", "\r\n")])
def test_runtime_requires_exact_prepared_bytes(edit):
    text = deck("a")
    with pytest.raises(ValueError, match="exact frozen"):
        nr.validate_runtime(text, edit(text))
