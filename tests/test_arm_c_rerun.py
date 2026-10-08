"""Offline checks for the S8 arm-C full re-run round; never launch QE/Slurm."""
import difflib
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/dft"))
import arm_c_build as cb  # noqa: E402
import arm_c_readout as readout  # noqa: E402
import arm_c_rerun_build as rerun  # noqa: E402
import hea_panel_readout as hpr  # noqa: E402
import research_batch as rb  # noqa: E402

PACKAGE = ROOT / "results/arm_c_2026-10-07_rerun"
SPEC = json.loads((PACKAGE / "launch_spec.json").read_text(encoding="utf-8"))
PLAN = json.loads((PACKAGE / "rerun_plan.json").read_text(encoding="utf-8"))
SOURCE = json.loads((ROOT / "results/arm_c_2026-10-07/readout.json").read_text(encoding="utf-8"))
SOURCE_SPEC = json.loads((ROOT / "results/arm_c_2026-10-07/launch_spec.json").read_text(encoding="utf-8"))
SLURM = ROOT / "anvil/95_arm_c_rerun.slurm"
JOBS = SPEC["stages"]["arm_c_rerun"]["jobs"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def test_build_reproduces_every_committed_file_byte_for_byte():
    built = rerun.build()
    assert len(built) == 36
    for relative, data in built.items():
        assert (ROOT / relative).read_bytes() == data, relative
        assert b"\r" not in data


def test_round_covers_every_failed_state_once_with_its_registered_recipe():
    failed = {(s["dir"], state): kind for s in SOURCE["sites"] for state, kind in s["original_failures"].items()}
    assert len(failed) == 31 and SOURCE["counts"]["scf_accepted"] == 33
    assert sorted(set(failed.values())) == ["CEILING", "IEEE"]
    chosen = {(r["site_dir"], r["state"]): r for r in PLAN["selection"]}
    assert set(chosen) == set(failed) and len(PLAN["selection"]) == PLAN["slots"] == 31
    for key, row in chosen.items():
        assert row["failure"] == failed[key]
        assert row["recipe"] == ("ndim16" if failed[key] == "CEILING" else "production")
        assert row["dir"] == readout.RERUN_ROOT + "/" + key[0].rsplit("/", 1)[-1]
        assert row["job"] == key[1] + "__atomic" + ("_ndim16" if row["recipe"] == "ndim16" else "")
    # The registered selection with the slot cap lifted, in the registered order.
    assert PLAN["selection"] == readout.rerun_selection(SOURCE["sites"], "ndim16", slots=31)
    assert PLAN["probe_recipe"] == SOURCE["probe"]["rerun_recipe_for_ceiling_stops"] == "ndim16"
    assert PLAN["source_readout"] == SPEC["source_readout"]
    assert PLAN["source_readout"]["sha256"] == sha(ROOT / PLAN["source_readout"]["path"])


def test_controls_are_the_production_slabs_of_sites_with_a_ceiling_stop():
    expected = sorted(s["dir"] for s in SOURCE["sites"]
                      if "slab" not in s["original_failures"] and "CEILING" in s["original_failures"].values())
    assert expected == ["hea/arm_c_2026-10-07/Cu26Ni9Cr31Co33__s1_site0",
                        "hea/arm_c_2026-10-07/Fe25Co25Ni25Cr25__s25_site2"]
    assert sorted(c["site_dir"] for c in PLAN["controls"]) == expected
    for control in PLAN["controls"]:
        assert (control["state"], control["recipe"], control["job"], control["control_of"]) == (
            "slab", "ndim16", "slab__atomic_ndim16", "slab__atomic")
    assert [j["role"] for j in JOBS].count("control") == 2


def test_decks_are_production_bytes_or_the_registered_one_line_variant():
    for job in JOBS:
        source = ROOT / job["source_deck"]
        assert sha(source) == SOURCE_SPEC["files"][job["source_deck"]]
        deck = ROOT / "runs" / job["dir"] / (job["job"] + ".in")
        assert sha(deck) == job["sha256"] == SPEC["files"]["runs/" + job["dir"] + "/" + job["job"] + ".in"]
        if job["recipe"] == "production":
            assert deck.read_bytes() == source.read_bytes()
            continue
        base = source.read_text(encoding="utf-8").split("\n")
        lines = deck.read_text(encoding="utf-8").split("\n")
        changed = sorted(d for d in difflib.ndiff(base, lines) if d[:2] in ("- ", "+ "))
        old = Path(job["source_deck"]).stem
        assert changed == sorted(["-   prefix = '" + old + "'", "+   prefix = '" + job["job"] + "'",
                                  "+   mixing_ndim = 16"])


def test_the_fe25_seed2_slab_rerun_repeats_the_converged_probe_deck_exactly():
    probe = ROOT / "runs/hea/arm_c_2026-10-07/probe__Fe25Co25Ni25Cr25__s2_site0/slab__atomic_ndim16.in"
    repeat = ROOT / "runs/hea/arm_c_2026-10-07_rerun/Fe25Co25Ni25Cr25__s2_site0/slab__atomic_ndim16.in"
    assert probe.read_bytes() == repeat.read_bytes()


def test_spec_shape_ceiling_and_campaign():
    assert SPEC["schema"] == "research-batch-2026-09-16" and SPEC["np"] == 128
    for relative, digest in SPEC["files"].items():
        assert sha(ROOT / relative) == digest, relative
    for relative in cb.RUNNER_FILES:
        assert SPEC["files"][relative] == SOURCE_SPEC["files"][relative]
    assert len(JOBS) == 33
    for job in JOBS:
        assert (job["nk"], job["scf_seconds"], job["projection_seconds"], job["max_iterations"]) == (8, 8100, 600, 126)
    stage = SPEC["stages"]["arm_c_rerun"]
    assert stage["wall_minutes"] == 150 and stage["concurrency"] == 33
    allocation = SPEC["allocation"]
    assert allocation["this_launch_ceiling_cpu_su"] == 33 * 150 * 128 // 60 == 10560
    assert allocation["spent_before_this_launch_cpu_su"] == 10876.7
    assert (allocation["spent_before_this_launch_cpu_su"] + allocation["this_launch_ceiling_cpu_su"]
            <= allocation["approved_campaign_ceiling_cpu_su"] == 23680)
    assert SPEC["qe_binaries_sha256"] == cb.QE_BINARIES and SPEC["pseudo_md5"] == SOURCE_SPEC["pseudo_md5"]
    assert SPEC["decision_ref"] == "Frank, 2026-10-07: \"Go with the full rerun.\""


def test_unchanged_runner_accepts_the_stage():
    group = rb.validate(SPEC, ROOT, "arm_c_rerun")
    assert group["kind"] == "hea"
    text = (ROOT / group["manifest"]).read_text(encoding="utf-8")
    assert text.isascii() and "# NP=128 NCONC=1" in text and "NOT LICENSED" not in text.upper()


def test_slurm_script_pins_the_rerun_spec_and_keeps_production_resources():
    text = SLURM.read_text(encoding="utf-8")
    assert "\r" not in text
    pins = re.findall(r'check_hash "\$(\w+)" ([0-9a-f]{64})', text)
    assert dict(pins) == {"SPEC": sha(PACKAGE / "launch_spec.json"), "RUNNER": sha(ROOT / "src/dft/research_batch.py")}
    assert 'case "${STAGE:-}" in arm_c_rerun)' in text
    assert text.count("/anvil/projects/x-che260157/sts_arm_c_2026-10-07_rerun/logs/arm_c_rerun_%A_%a.log") == 2
    production = (ROOT / "anvil/94_arm_c_batch.slurm").read_text(encoding="utf-8")

    def resources(t):
        return [line for line in t.splitlines() if line.startswith("#SBATCH") and "--output" not in line
                and "--error" not in line]
    assert resources(text) == resources(production)
    tail = production.split("export OMP_NUM_THREADS", 1)[1]
    assert text.split("export OMP_NUM_THREADS", 1)[1] == tail
    bash = shutil.which("bash")
    if bash:
        assert subprocess.run([bash, "-n", str(SLURM)]).returncode == 0


def test_ops_target_the_rerun_root_and_shape():
    spec = importlib.util.spec_from_file_location("arm_c_rerun_launch_ops", PACKAGE / "launch_ops.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.ARRAYS == {"arm_c_rerun": {"array": "1-33%33", "tasks": 33, "throttle": "33", "name": "arm-c-rerun"}}
    assert module.REMOTE == "/anvil/projects/x-che260157/sts_arm_c_2026-10-07_rerun"
    assert module.SLURM_REL == "anvil/95_arm_c_rerun.slurm" and module.TIME_LIMIT == "02:30:00"
    assert 33 * 150 * 128 // 60 == SPEC["allocation"]["this_launch_ceiling_cpu_su"]
    for name in ("status_once.py", "collect_terminal.py"):
        source = (PACKAGE / name).read_text(encoding="utf-8")
        assert "/anvil/projects/x-che260157/sts_arm_c_2026-10-07_rerun\"" in source
        assert "sts_arm_c_2026-10-07\"" not in source


# ---------------------------------------------------------------- substitution and controls
ENERGIES_RY = {"slab": -7872.00022049, "OH": -7914.75368997, "O": -7913.46937673, "OOH": -7956.25801633}


def write_fake(run_dir, job, energy_Ry=None, ceiling=False):
    run_dir.mkdir(parents=True, exist_ok=True)
    lines = ["     running on   128 processor cores"]
    if energy_Ry is not None:
        lines += ["     convergence has been achieved in  40 iterations",
                  f"!    total energy              =   {energy_Ry:.8f} Ry"]
    lines.append("   JOB DONE.")
    (run_dir / (job + ".out")).write_text("\n".join(lines) + "\n", encoding="utf-8")
    receipt = {"status": "REJECTED", "reason": "SCF iteration ceiling"} if ceiling else {
        "status": "COMPLETE", "reason": None, "scf": {"energy_Ry": energy_Ry, "iterations": 40}}
    (run_dir / (job + ".qc.json")).write_text(json.dumps(receipt), encoding="utf-8")
    if ceiling:
        (run_dir / (job + ".KILLED")).write_text("SCF iteration ceiling\n", encoding="utf-8")


def test_a_ceiling_rerun_completes_a_chain_and_a_control_reports_its_offset(tmp_path):
    site_dir = "hea/arm_c_2026-10-07/Ni31Cr29Cu5Mn35__s10_site2"
    rerun_dir = readout.RERUN_ROOT + "/Ni31Cr29Cu5Mn35__s10_site2"
    production, repeat = tmp_path / "production", tmp_path / "rerun"
    for state, energy in ENERGIES_RY.items():
        write_fake(production / "runs" / site_dir, state + "__atomic", None if state == "OH" else energy,
                   ceiling=state == "OH")
    write_fake(repeat / "runs" / rerun_dir, "OH__atomic_ndim16", ENERGIES_RY["OH"])
    write_fake(repeat / "runs" / rerun_dir, "slab__atomic_ndim16", ENERGIES_RY["slab"] + 1e-4)
    site = {"formula": "Ni31Cr29Cu5Mn35", "seed": 10, "site_index": 2, "site_metal": "Ni",
            "roles": {"support_hi": {"weight": "7/10"}}, "eta_mlip_V": 0.487,
            "dG_mlip_eV": {"OH": 1.0, "O": 2.0, "OOH": 4.0}, "dir": site_dir,
            "states": {s: {"job": s + "__atomic"} for s in readout.STATES}}
    gas = {g: hpr.gas_references()[g]["E_eV"] for g in ("H2O", "H2")}
    substitution = {"OH": {"site_dir": site_dir, "state": "OH", "failure": "CEILING", "recipe": "ndim16",
                           "dir": rerun_dir, "job": "OH__atomic_ndim16"}}
    without = readout.site_result(site, production, gas)
    assert without["complete"] is False and without["original_failures"] == {"OH": "CEILING"}
    result = readout.site_result(site, production, gas, substitution, repeat)
    assert result["complete"] and result["mixed_recipe"] and result["recipes"] == ["ndim16", "production"]
    assert result["states"]["OH"]["replaces"] == "OH__atomic"
    control_row = {"site_dir": site_dir, "state": "slab", "recipe": "ndim16", "dir": rerun_dir,
                   "job": "slab__atomic_ndim16", "control_of": "slab__atomic"}
    control = readout.recipe_control(control_row, production, repeat, [result], gas)
    assert abs(control["energy_control_minus_production_meV"] - 1e-4 * 13605.693) < 0.05
    shifted = dict({s: result["states"][s]["E_eV"] for s in readout.STATES},
                   slab=control["control"]["E_eV"])
    assert control["eta_dft_V_with_control"] == hpr.che_from_energies(shifted, gas)["eta"]
    assert abs(control["eta_dft_V_with_control"] - result["eta_dft_V"]) < 0.01
    missing = readout.recipe_control(control_row, production, None, [result], gas)
    assert missing["control"] is None and "energy_control_minus_production_meV" not in missing


def test_a_rerun_that_fails_again_is_recorded_and_leaves_the_state_failed(tmp_path):
    site_dir = "hea/arm_c_2026-10-07/Fe25Co25Ni25Cr25__s2_site0"
    rerun_dir = readout.RERUN_ROOT + "/Fe25Co25Ni25Cr25__s2_site0"
    production, repeat = tmp_path / "production", tmp_path / "rerun"
    for state, energy in ENERGIES_RY.items():
        write_fake(production / "runs" / site_dir, state + "__atomic", None if state == "slab" else energy,
                   ceiling=state == "slab")
    write_fake(repeat / "runs" / rerun_dir, "slab__atomic_ndim16", None, ceiling=True)
    site = {"formula": "Fe25Co25Ni25Cr25", "seed": 2, "site_index": 0, "site_metal": "Cr",
            "roles": {"best": {}}, "eta_mlip_V": 0.453, "dG_mlip_eV": {"OH": 1.0, "O": 2.0, "OOH": 4.0},
            "dir": site_dir, "states": {s: {"job": s + "__atomic"} for s in readout.STATES}}
    gas = {g: hpr.gas_references()[g]["E_eV"] for g in ("H2O", "H2")}
    substitution = {"slab": {"site_dir": site_dir, "state": "slab", "failure": "CEILING", "recipe": "ndim16",
                             "dir": rerun_dir, "job": "slab__atomic_ndim16"}}
    result = readout.site_result(site, production, gas, substitution, repeat)
    assert result["complete"] is False and result["failures"] == {"slab": "CEILING"}
    assert [(a["state"], a["job"], a["accepted"], a["failure"]) for a in result["rerun_attempts"]] == [
        ("slab", "slab__atomic_ndim16", False, "CEILING")]
    assert "rerun_attempts" not in readout.site_result(site, production, gas)


def test_a_rerun_readout_refuses_a_missing_rerun_mirror(tmp_path):
    args = ["--plan", str(ROOT / "results/arm_c_2026-10-07/site_plan.json"),
            "--mirror", str(ROOT / "results/arm_c_2026-10-07/raw_mirror"),
            "--rerun-plan", str(PACKAGE / "rerun_plan.json"), "--out", str(tmp_path / "out.json")]
    with pytest.raises(SystemExit):
        readout.main(args)
    with pytest.raises(SystemExit):
        readout.main(args + ["--rerun-mirror", str(tmp_path / "absent")])
    assert not (tmp_path / "out.json").exists()


def test_the_amended_readout_reproduces_the_committed_terminal_readout(tmp_path):
    mirror = ROOT / "results/arm_c_2026-10-07/raw_mirror"
    if not any(mirror.rglob("*.projwfc.out")):
        pytest.skip("projection outputs are kept local, outside git")
    out = tmp_path / "readout.json"
    readout.main(["--plan", str(ROOT / "results/arm_c_2026-10-07/site_plan.json"), "--mirror", str(mirror),
                  "--out", str(out)])
    assert out.read_bytes() == (ROOT / "results/arm_c_2026-10-07/readout.json").read_bytes()


def test_the_rerun_readout_reproduces_the_committed_rerun_readout(tmp_path):
    mirror, rerun_mirror = ROOT / "results/arm_c_2026-10-07/raw_mirror", PACKAGE / "raw_mirror"
    if not (any(mirror.rglob("*.projwfc.out")) and any(rerun_mirror.rglob("*.projwfc.out"))):
        pytest.skip("projection outputs are kept local, outside git")
    out = tmp_path / "readout.json"
    readout.main(["--plan", str(ROOT / "results/arm_c_2026-10-07/site_plan.json"), "--mirror", str(mirror),
                  "--rerun-plan", str(PACKAGE / "rerun_plan.json"), "--rerun-mirror", str(rerun_mirror),
                  "--out", str(out)])
    assert out.read_bytes() == (PACKAGE / "readout.json").read_bytes()
