"""Real raw QC, lineage hashes and paired thermodynamic/state calculations.

Synthetic bundle fixtures isolate readout behavior; the guard has its own
schema/deck/XML tests, and the real frozen-bundle case covers their integration.
"""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/dft"))
import hea_sensitivity_readout as sr
import hea_followup_qc as qc
import test_hea_numerical_readout as fixtures

write, dump, sha = fixtures.write, fixtures.dump, fixtures.sha
DIRECTORY = "hea/sensitivity_2026-09-09"
SOURCE_DIRECTORY = "hea/numerical_2026-09-08"
INVENTORY = "results/hea_sensitivity_2026-09-09/source_checkpoints.json"


def raw_output(energy, minus_ts, changed=False):
    text = fixtures.output(energy, "tight", changed)
    return text.replace("convergence has been achieved", f"smearing contrib. (-TS) = {minus_ts:.8f} Ry\ninternal energy E=F+TS = {energy-minus_ts:.8f} Ry\nconvergence has been achieved")


def complete(folder, job, text, energy, minus_ts, changed=False):
    write(folder / (job + ".run.in"), text)
    write(folder / (job + ".out"), raw_output(energy, minus_ts, changed))
    write(folder / (job + ".projwfc.out"), fixtures.projection(changed))
    refresh_qc(folder, job)


def refresh_qc(folder, job):
    audit = qc.audit_files(*(folder / (job + suffix) for suffix in (".run.in", ".out", ".projwfc.out")))
    dump(folder / (job + ".qc.json"), audit)


@pytest.fixture
def batch(tmp_path, monkeypatch):
    sources, checkpoints, metadata, jobs = {}, {}, {}, []
    old = tmp_path / "runs" / SOURCE_DIRECTORY
    new = tmp_path / "runs" / DIRECTORY
    for endpoint, energy, minus_ts in (("builder", -10, -0.1), ("pull2.10", -12, -0.2)):
        source_job = "hn__leader_" + endpoint + "__ortho__tight"
        prefix = "hc__leader_" + endpoint + "__ortho__fragment"
        text = fixtures.deck(prefix, "ortho", endpoint == "pull2.10")
        text = text.replace(" calculation='scf'", " calculation='scf'\n restart_mode='from_scratch'")
        text = text.replace("&ELECTRONS\n", "&ELECTRONS\n startingpot='file'\n startingwfc='file'\n")
        text = text.replace("conv_thr=1.0d-6", "conv_thr=1.0d-8").replace("./tmp_" + prefix, "./tmp_" + source_job)
        text = text.replace(" nspin=2", " nspin=2\n occupations='smearing'\n smearing='mv'\n degauss=0.01")
        complete(old, source_job, text, energy, minus_ts)
        sources[endpoint] = (source_job, prefix, text)
        checkpoints[source_job] = dict(source_job=source_job, prefix=prefix,
            dir=SOURCE_DIRECTORY+"/tmp_"+source_job+"/"+prefix+".save",
            source_input="runs/"+SOURCE_DIRECTORY+"/"+source_job+".run.in",
            source_input_sha256=sha(old/(source_job+".run.in")),
            source_output_sha256=sha(old/(source_job+".out")),
            source_projection_sha256=sha(old/(source_job+".projwfc.out")),
            source_qc_sha256=sha(old/(source_job+".qc.json")),
            files=[dict(path="data-file-schema.xml", size_bytes=1, sha256="a"*64)])
        metadata[source_job] = dict(converged=True, energy_hartree=energy/2,
            smearing_contribution_hartree=minus_ts/2, total_moment_muB=2.0, absolute_moment_muB=2.0)
    for arm in sr.ARMS:
        for endpoint in sr.ENDPOINTS:
            source_job, prefix, source = sources[endpoint]
            job = "hs__leader_" + endpoint + "__ortho__" + arm
            text = source.replace("./tmp_"+source_job, "./tmp_"+job)
            if arm == "wfc":
                text = text.replace("ecutwfc=80", "ecutwfc=100")
            elif arm == "rho":
                text = text.replace("ecutrho=640", "ecutrho=800")
            else:
                text = text.replace("degauss=0.01", "degauss=0.005")
            path = new / (job + ".in")
            write(path, text)
            jobs.append(dict(job=job, dir=DIRECTORY, suffix=".in", nk=8, sha256=sha(path),
                             prefix=prefix, source_job=source_job, arm=arm))
    inventory = tmp_path / INVENTORY
    dump(inventory, dict(schema="hea_sensitivity_sources_v1", checkpoints=list(checkpoints.values())))
    spec = dict(jobs=jobs, source_checkpoints=INVENTORY, source_checkpoints_sha256=sha(inventory))
    spec_path = tmp_path / "spec.json"
    dump(spec_path, spec)
    bundle = dict(spec=spec, root=tmp_path/"runs", checkpoints=checkpoints, metadata=metadata)
    monkeypatch.setattr(sr.guard, "load_bundle", lambda spec_path, runs: bundle)
    return tmp_path, spec_path, bundle


def finish(batch):
    root, _, bundle = batch
    folder = root / "runs" / DIRECTORY
    for job in bundle["spec"]["jobs"]:
        endpoint = "builder" if "__leader_builder__" in job["job"] else "pull2.10"
        base_energy = -10 if endpoint == "builder" else -12
        shifts = {"wfc": (0.10, 0.14), "rho": (0.20, 0.23), "smearing": (0.04, 0.07)}
        energy = base_energy - shifts[job["arm"]][endpoint == "pull2.10"]
        minus_ts = (-0.03 if endpoint == "builder" else -0.04) if job["arm"] == "smearing" else (-0.1 if endpoint == "builder" else -0.2)
        complete(folder, job["job"], (folder/(job["job"]+".in")).read_text(), energy, minus_ts, True)
        cp = bundle["checkpoints"][job["source_job"]]
        receipt = dict(schema="hea_sensitivity_clone_v1", job=job["job"], prefix=job["prefix"],
                       source_job=job["source_job"], arm=job["arm"], source=cp["dir"],
                       destination=job["dir"]+"/tmp_"+job["job"]+"/"+job["prefix"]+".save",
                       source_checkpoints_sha256=bundle["spec"]["source_checkpoints_sha256"], files=cp["files"])
        dump(folder/(job["job"]+".clone_receipt.json"), receipt)


def test_pending_has_two_verified_sources_six_targets_and_no_new_gaps(batch):
    result = sr.build_readout(*batch[:2])
    assert result["counts"] == dict(accepted=0, pending=6, rejected=0)
    assert result["source_counts"] == dict(accepted=2, pending=0, rejected=0)
    assert result["status"] == "PENDING" and not result["batch_readout_complete"]
    assert all(p["source_gap_eV"] == pytest.approx(-2*sr.RY_TO_EV) for p in result["pairs"])
    assert all(p["target_gap_eV"] is None and p["thermodynamic_gap_terms"] is None for p in result["pairs"])
    assert all(s["source_artifact_hashes_match"] and s["source_checkpoint_metadata_match"] for s in result["sources"])


def test_three_independent_pairs_keep_force_spin_hubbard_and_smearing_terms(batch):
    finish(batch)
    result = sr.build_readout(*batch[:2])
    assert result["counts"] == dict(accepted=6, pending=0, rejected=0)
    assert result["status"] == "COMPLETE" and result["batch_readout_complete"]
    assert [p["delta_gap_eV"] for p in result["pairs"]] == pytest.approx([-0.04*sr.RY_TO_EV, -0.03*sr.RY_TO_EV, -0.03*sr.RY_TO_EV])
    smear = result["pairs"][2]
    assert smear["thermodynamic_gap_terms"]["minus_ts"]["delta_gap_eV"] == pytest.approx(0.09*sr.RY_TO_EV)
    assert smear["thermodynamic_gap_terms"]["internal_energy"]["delta_gap_eV"] == pytest.approx(-0.12*sr.RY_TO_EV)
    diff = smear["endpoints"][0]
    expected = 0.1*sr.numerical.force.RY_BOHR_TO_EV_A
    assert diff["max_free_vector_difference_ev_A"] == pytest.approx(2**0.5*expected)
    assert diff["rms_free_component_difference_ev_A"] == pytest.approx(expected)
    assert diff["atoms"][0]["delta_free_force_ev_A"] == pytest.approx([expected, 0, expected])
    assert diff["delta_total_moment_muB"] == pytest.approx(0.2)
    assert diff["hubbard_atoms"][0]["delta_trace_up_e"] == pytest.approx(0.1)
    assert result["numerical_accuracy_status"] == result["electronic_basin_status"] == "NOT_INFERRED"
    assert "E0" not in json.dumps(result)


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "nonfinite", "inconsistent"])
def test_malformed_smearing_evidence_excludes_that_pair(batch, mutation):
    finish(batch)
    root, spec_path, bundle = batch
    job = bundle["spec"]["jobs"][4]["job"]
    folder = root / "runs" / DIRECTORY
    path = folder/(job+".out")
    value = path.read_text()
    if mutation == "missing":
        value = value.replace("smearing contrib. (-TS)", "omitted term")
    elif mutation == "duplicate":
        value += "smearing contrib. (-TS) = -0.03000000 Ry\n"
    elif mutation == "nonfinite":
        value = value.replace("smearing contrib. (-TS) = -0.03000000", "smearing contrib. (-TS) = NaN")
    else:
        value = value.replace("internal energy E=F+TS = -10.01000000", "internal energy E=F+TS = -10.50000000")
    write(path, value)
    refresh_qc(folder, job)
    result = sr.build_readout(root, spec_path)
    assert result["counts"]["rejected"] == 1
    assert result["pairs"][2]["status"] == "REJECTED"
    assert result["pairs"][2]["target_gap_eV"] is None
    assert result["pairs"][0]["status"] == result["pairs"][1]["status"] == "COMPLETE"


@pytest.mark.parametrize("mutation", ["receipt", "startup", "projection", "runtime", "invalid_flag", "qc"])
def test_invalid_new_lineage_or_raw_qc_never_enters_pair(batch, mutation):
    finish(batch)
    root, spec_path, bundle = batch
    folder = root / "runs" / DIRECTORY
    job = bundle["spec"]["jobs"][0]["job"]
    if mutation == "receipt":
        path = folder/(job+".clone_receipt.json")
        value = json.loads(path.read_text())
        value["source_job"] = "wrong_source"
        dump(path, value)
    elif mutation == "startup":
        path = folder/(job+".out")
        write(path, path.read_text().replace("Starting wfcs from file", "Starting wfcs are 12 randomized atomic wfcs"))
    elif mutation == "projection":
        path = folder/(job+".projwfc.out")
        write(path, path.read_text().replace("JOB DONE.", ""))
    elif mutation == "runtime":
        path = folder/(job+".run.in")
        write(path, path.read_text().replace("ecutwfc=100", "ecutwfc=120"))
    elif mutation == "invalid_flag":
        path = folder/(job+".out")
        write(path, path.read_text()+"Note: IEEE_INVALID_FLAG\n")
    else:
        path = folder/(job+".qc.json")
        value = json.loads(path.read_text())
        value["scf"]["energy_eV"] += 1
        dump(path, value)
    if mutation != "qc":
        refresh_qc(folder, job)
    result = sr.build_readout(root, spec_path)
    assert result["counts"]["rejected"] == 1
    assert result["pairs"][0]["delta_gap_eV"] is None
    assert result["pairs"][1]["status"] == "COMPLETE"


def test_source_raw_qc_self_consistency_does_not_override_frozen_artifact_hash(batch):
    root, spec_path, bundle = batch
    source_job = next(iter(bundle["checkpoints"]))
    folder = root/"runs"/SOURCE_DIRECTORY
    path = folder/(source_job+".out")
    write(path, path.read_text()+"additional source text\n")
    refresh_qc(folder, source_job)
    result = sr.build_readout(root, spec_path)
    assert result["source_counts"] == dict(accepted=1, pending=0, rejected=1)
    assert result["status"] == "REJECTED"
    assert all(p["status"] == "REJECTED" and p["source_gap_eV"] is None for p in result["pairs"])


@pytest.mark.parametrize("field,delta", [("energy_hartree", 1e-5), ("smearing_contribution_hartree", 1e-5),
                                        ("total_moment_muB", 0.02), ("absolute_moment_muB", 0.02)])
def test_frozen_checkpoint_must_match_parent_raw_state(batch, field, delta):
    bundle = batch[2]
    key = next(iter(bundle["metadata"]))
    bundle["metadata"][key][field] += delta
    result = sr.build_readout(*batch[:2])
    assert result["source_counts"]["rejected"] == 1
    assert not result["batch_readout_complete"]


def test_one_incomplete_endpoint_does_not_pollute_other_pairs(batch):
    finish(batch)
    root, spec_path, bundle = batch
    path = root/"runs"/DIRECTORY/(bundle["spec"]["jobs"][0]["job"]+".qc.json")
    path.unlink()
    result = sr.build_readout(root, spec_path)
    assert result["counts"] == dict(accepted=5, pending=1, rejected=0)
    assert [p["status"] for p in result["pairs"]] == ["PENDING", "COMPLETE", "COMPLETE"]


def test_cli_preserves_raw_files_and_existing_readout(batch):
    root, spec_path, _ = batch
    before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
    destination = root/"pending.json"
    argv = ["--root", str(root), "--spec", str(spec_path), "--out", str(destination)]
    assert sr.main(argv) == 0
    first = destination.read_bytes()
    assert sr.main(argv) == 2 and destination.read_bytes() == first
    assert all(path.read_bytes() == raw for path, raw in before.items())


@pytest.mark.parametrize("endpoint", sr.ENDPOINTS)
def test_real_accepted_parent_thermodynamic_terms(endpoint):
    job = "hn__leader_"+endpoint+"__ortho__tight"
    path = ROOT/"runs"/SOURCE_DIRECTORY/(job+".out")
    if not path.is_file():
        pytest.skip("banked accepted numerical parent absent")
    terms = sr.thermodynamics(path.read_text())
    assert abs(terms["free_energy_Ry"]-terms["minus_ts_Ry"]-terms["internal_energy_Ry"]) <= 1.500001e-8


def test_real_frozen_bundle_pending_readout(tmp_path):
    spec_path = ROOT/"results/hea_sensitivity_2026-09-09/launch_spec.json"
    if not spec_path.is_file():
        pytest.skip("frozen sensitivity bundle absent")
    spec = json.loads(spec_path.read_text())
    inventory = json.loads((ROOT/spec["source_checkpoints"]).read_text())
    paths = {spec_path.relative_to(ROOT).as_posix(), spec["source_checkpoints"], spec["manifest"], spec["manifest"]+".lines"}
    for cp in inventory["checkpoints"]:
        paths.add(cp["source_input"])
        paths.add(cp["source_xml"])
        source_folder = Path(cp["source_input"]).parent
        for suffix in (".out", ".projwfc.out", ".qc.json"):
            paths.add((source_folder/(cp["source_job"]+suffix)).as_posix())
    for job in spec["jobs"]:
        paths.add("runs/"+job["dir"]+"/"+job["job"]+".in")
    for relative in paths:
        source, target = ROOT/relative, tmp_path/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    result = sr.build_readout(tmp_path, tmp_path/spec_path.relative_to(ROOT))
    assert result["source_counts"] == dict(accepted=2, pending=0, rejected=0), result
    assert result["counts"] == dict(accepted=0, pending=6, rejected=0)
    assert result["pairs"][0]["source_gap_eV"] == pytest.approx(-2.1297815948782954)
