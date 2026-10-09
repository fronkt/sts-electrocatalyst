"""Offline checks for round 3 of the S8 arm-C extension (the last missing state of one Cu8 and one Fe25 support
site, from round 2's moved densities with gentler density mixing) and for the readout's stacked rounds; never
launch QE/Slurm or open a network connection. The runner check needs round 2's local densities (never in git)
and skips without them."""
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/dft"))
import arm_c_ext_r2_build as r2  # noqa: E402
import arm_c_ext_r3_build as r3  # noqa: E402
import arm_c_readout as readout  # noqa: E402
import hea_panel_readout as hpr  # noqa: E402
import research_batch_seeded as runner  # noqa: E402

PACKAGE = ROOT / r3.PACKAGE
SPEC = json.loads((PACKAGE / "launch_spec.json").read_text(encoding="utf-8"))
PLAN = json.loads((PACKAGE / "ext_plan.json").read_text(encoding="utf-8"))
R2_SPEC = json.loads((ROOT / r3.R2_SPEC).read_text(encoding="utf-8"))
JOBS = SPEC["stages"]["r3_main"]["jobs"]
SLURM = ROOT / "anvil/98_arm_c_ext_r3.slurm"
LOCAL_SEEDS = [ROOT / r2.PACKAGE / "seeds" / site / state / r2.DENSITY for site, state in r3.EXPECTED]
needs_local = pytest.mark.skipif(not all(p.exists() for p in LOCAL_SEEDS) or not (ROOT / r2.INPUTS).is_dir(),
                                 reason="round 2's moved densities and fetched seed XMLs are local only")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(name):
    spec = importlib.util.spec_from_file_location("arm_c_ext_r3_" + Path(name).stem, PACKAGE / name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # the network parts run only under __main__
    return module


# ---------------------------------------------------------------- the round-3 package
def test_build_reproduces_every_committed_file_byte_for_byte():
    built = r3.build()
    assert len(built) == 9  # 2 decks, 4 seed text files, manifest, plan, spec
    for relative, data in built.items():
        assert (ROOT / relative).read_bytes() == data, relative
        assert b"\r" not in data


def test_targets_are_the_support_sites_missing_exactly_one_state_after_round_2():
    source = json.loads((ROOT / r3.R2_READOUT).read_text(encoding="utf-8"))
    assert r3.targets(source) == [("Cu8Cr23Mn35Co34__s16_site2", "slab"), ("Fe25Co25Ni25Cr25__s25_site2", "O")]
    assert {f: v["status"] for f, v in source["alloys"].items() if f in r3.r1.ALLOYS} == {
        "Cu8Cr23Mn35Co34": "NO_VALUE", "Fe25Co25Ni25Cr25": "NO_VALUE"}
    for site in source["sites"]:
        for name, state in r3.EXPECTED:
            if site["dir"].endswith("/" + name):
                assert [s for s, row in site["states"].items() if not row["accepted"]] == [state]
                assert {"support_lo", "support_hi"} & set(site["roles"])


def test_decks_differ_from_round_2_only_in_prefix_mixing_and_max_seconds():
    beta_line = f"  mixing_beta = {r3.MIXING['mixing_beta']}"
    for job in JOBS:
        new = (ROOT / f"runs/{job['dir']}/{job['job']}.in").read_text(encoding="utf-8").split("\n")
        old = (ROOT / job["source_deck"]).read_text(encoding="utf-8").split("\n")
        assert sha(ROOT / job["source_deck"]) == R2_SPEC["files"][job["source_deck"]]
        old_job = job["source_deck"].rsplit("/", 1)[-1][:-len(".in")]
        beta = old.index("  mixing_beta = 0.3")
        assert len(new) == len(old) + 1 and new[beta + 1] == f"  mixing_ndim = {r3.MIXING['mixing_ndim']}"
        rest = new[:beta + 1] + new[beta + 2:]
        expected = [(f"  prefix = '{old_job}'", f"  prefix = '{job['job']}'"),
                    ("  max_seconds = 165000", "  max_seconds = 18400")]
        if beta_line != old[beta]:
            expected.append((old[beta], beta_line))
        assert [(a, b) for a, b in zip(old, rest) if a != b] == expected
        assert "  electron_maxstep = 300" in new and "  startingpot = 'file'" in new and beta_line in new
        assert job["job"] == job["source_deck"].rsplit("/", 1)[-1][:-len("__atomic_moved.in")] + r3.JOB_SUFFIX


def test_the_start_is_round_2_s_byte_for_byte_and_copied_on_anvil():
    r2_jobs = {(j["dir"].rsplit("/", 1)[-1], j["job"]): j for j in R2_SPEC["stages"]["r2_main"]["jobs"]}
    assert len(JOBS) == len(PLAN["selection"]) == 2
    for job, row in zip(JOBS, PLAN["selection"]):
        assert (job["dir"], job["job"]) == (row["dir"], row["job"])
        old = r2_jobs[(job["dir"].rsplit("/", 1)[-1], row["round_2_job"])]
        assert job["scratch_source"]["files"] == old["scratch_source"]["files"]
        assert (job["seed"], job["nk"], job["recipe"]) == (old["seed"], old["nk"], old["recipe"])
        for name in ("occup.txt", "paw.txt"):
            assert (ROOT / job["scratch_source"]["save_dir"] / name).read_bytes() == (
                ROOT / old["scratch_source"]["save_dir"] / name).read_bytes()
        assert row["remote_copy"] == {name: r3.R2_REMOTE + "/" + old["scratch_source"]["save_dir"] + "/" + name
                                      for name in (r2.DENSITY, r2.XML)}
        assert "upload" not in row


def test_limits_let_qe_stop_itself_and_fit_the_runner_and_the_campaign():
    for job in JOBS:
        assert (job["max_iterations"], job["scf_seconds"], job["projection_seconds"]) == (300, 19000, 600)
        assert job["scf_seconds"] <= runner.SCF_SECONDS
        # QE stops itself at 18,400 s and writes its last density, nine round-2 iterations (63 s) before the wall
        assert job["scf_seconds"] - r3.QE_MAX_SECONDS >= 9 * 63
    allocation = SPEC["allocation"]
    assert allocation["stage_ceilings_cpu_su"] == {"r3_main": 1472} == {"r3_main": 2 * 345 * 128 // 60}
    assert allocation["this_launch_ceiling_cpu_su"] == 1472
    assert allocation["spent_before_this_launch_cpu_su"] == 20888.5  # 17,471.8 before round 2 + round 2's 3,416.7
    assert allocation["spent_before_this_launch_cpu_su"] + 1472 <= allocation["approved_campaign_ceiling_cpu_su"] == 23680
    assert SPEC["stages"]["r3_main"]["wall_minutes"] * 60 >= max(j["scf_seconds"] + j["projection_seconds"] for j in JOBS) + 300
    assert SPEC["pseudo_md5"] == R2_SPEC["pseudo_md5"] and SPEC["qe_binaries_sha256"] == R2_SPEC["qe_binaries_sha256"]
    assert SPEC["exclusions"] == R2_SPEC["exclusions"]
    for relative in r3.r1.RUNNER_FILES:
        assert SPEC["files"][relative] == R2_SPEC["files"][relative]
    for relative, pin in SPEC["files"].items():
        assert sha(ROOT / relative) == pin, relative


def test_plan_records_round_mixing_and_round_2_s_failure():
    assert PLAN["round"] == 3 and PLAN["mixing"] == r3.MIXING and PLAN["qe_max_seconds"] == 18400
    assert PLAN["source_readout"] == SPEC["source_readout"]
    assert PLAN["source_readout"]["sha256"] == sha(ROOT / r3.R2_READOUT)
    assert PLAN["round_2"]["spec_sha256"] == sha(ROOT / r3.R2_SPEC)
    for row in PLAN["selection"]:
        assert row["round"] == 3 and row["seed_density"] == "moved" and row["round_2_failure"] == "CEILING"
        assert row["mixing"] == PLAN["mixing"]


@needs_local
def test_the_unchanged_runner_validates_the_stage(tmp_path):
    for relative in SPEC["files"]:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    for job, row in zip(JOBS, PLAN["selection"]):
        bundle = tmp_path / job["scratch_source"]["save_dir"]
        r2_bundle = row["remote_copy"][r2.DENSITY][len(r3.R2_REMOTE) + 1:].rsplit("/", 1)[0]
        shutil.copyfile(ROOT / r2_bundle / r2.DENSITY, bundle / r2.DENSITY)
        shutil.copyfile(ROOT / r2.INPUTS / row["seed"]["id"] / r2.XML, bundle / r2.XML)
    group = runner.validate(SPEC, tmp_path, "r3_main")
    assert [j["job"] for j in group["jobs"]] == ["slab" + r3.JOB_SUFFIX, "O" + r3.JOB_SUFFIX]


def test_slurm_script_pins_the_spec_and_runner_and_keeps_round_2_resources():
    text = SLURM.read_text(encoding="utf-8")
    assert "\r" not in text
    assert f'check_hash "$SPEC" {sha(PACKAGE / "launch_spec.json")}' in text
    assert f'check_hash "$RUNNER" {sha(ROOT / "src/dft/research_batch_seeded.py")}' in text
    assert "r3_main) ;;" in text and 'ROOT="$PROJECT/sts_arm_c_ext_r3_2026-10-09"' in text
    old = (ROOT / "anvil/97_arm_c_ext_r2.slurm").read_text(encoding="utf-8")
    assert [l for l in text.split("\n") if l.startswith("#SBATCH") and "log" not in l] == [
        l for l in old.split("\n") if l.startswith("#SBATCH") and "log" not in l]
    assert text.split("export OMP_NUM_THREADS", 1)[1] == old.split("export OMP_NUM_THREADS", 1)[1]
    bash = shutil.which("bash")
    if bash:
        assert subprocess.run([bash, "-n", str(SLURM)]).returncode == 0


def test_ops_target_the_round_3_root_copy_on_anvil_and_release_after_validation():
    module = load("launch_ops.py")
    assert module.REMOTE == "/anvil/projects/x-che260157/sts_arm_c_ext_r3_2026-10-09"
    assert module.SLURM_REL == "anvil/98_arm_c_ext_r3.slurm"
    assert {k: (v["array"], v["tasks"], v["time"], v["minutes"]) for k, v in module.ARRAYS.items()} == {
        "r3_main": ("1-2%2", 2, "05:45:00", 345)}
    shape = module.ARRAYS["r3_main"]
    assert shape["tasks"] * shape["minutes"] * 128 // 60 == SPEC["allocation"]["stage_ceilings_cpu_su"]["r3_main"]
    assert shape["minutes"] == SPEC["stages"]["r3_main"]["wall_minutes"] and shape["tasks"] == len(JOBS)
    copies = module.seed_copies()
    assert len(copies) == 4 and not hasattr(module, "uploads")
    pins = {j["scratch_source"]["save_dir"]: j["scratch_source"]["files"] for j in JOBS}
    for source, target, pin in copies:
        assert source.startswith(r3.R2_REMOTE + "/" + r2.PACKAGE + "/seeds/")
        bundle, name = target[len(module.REMOTE) + 1:].rsplit("/", 1)
        assert bundle.startswith(r3.PACKAGE + "/seeds/") and pins[bundle][name] == pin and source.endswith("/" + name)
    ops = (PACKAGE / "launch_ops.py").read_text(encoding="utf-8")
    assert "held shape not validated" in ops and "canary" not in ops.split("def release", 1)[1]
    assert '"--exclude=" + SPEC["exclusions"]' in ops and 'bad["ExcNodeList"]' in ops
    for name in ("status_once.py", "collect_terminal.py", "start_check.py"):
        assert "/anvil/projects/x-che260157/sts_arm_c_ext_r3_2026-10-09\"" in (PACKAGE / name).read_text(encoding="utf-8")
    collect = (PACKAGE / "collect_terminal.py").read_text(encoding="utf-8")
    assert "-path '*/tmp_*/*.save/occup.txt'" in collect and '".save/occup.txt"' in collect


def test_the_start_check_expects_round_2_s_first_lines():
    module = load("start_check.py")
    want = {row["job"]: module.expected(row) for row in PLAN["selection"]}
    assert want == {
        "slab" + r3.JOB_SUFFIX: {"negative_rho": "negative rho (up, down): 7.515E-02 3.168E-01",
                                 "accuracy": "estimated scf accuracy < 3.43867242 Ry"},
        "O" + r3.JOB_SUFFIX: {"negative_rho": "negative rho (up, down): 4.686E-03 4.562E-01",
                              "accuracy": "estimated scf accuracy < 38.00323795 Ry"}}
    canary = (ROOT / r2.PACKAGE / "raw_mirror/runs" / r2.RUN_ROOT / "canary/Cu8Cr23Mn35Co34__s16_site2/slab__atomic_moved.out")
    assert module.first_lines(canary.read_text(errors="replace")) == want["slab" + r3.JOB_SUFFIX]  # other node, same digits
    assert module.first_lines("     iteration #  1\n") == {"negative_rho": None, "accuracy": None}


# ---------------------------------------------------------------- the readout's stacked rounds
def write_fake(run_dir, job, energy_Ry=None, ceiling=False, seeded=False, iterations=40, moment=None):
    """The QE output and runner receipt shapes of tests/test_arm_c_ext.py."""
    run_dir.mkdir(parents=True, exist_ok=True)
    lines = ["     running on   128 processor cores"]
    if seeded:
        lines.append("     The initial density is read from file :")
    if moment is not None:
        lines.append(f"     total magnetization       =    {moment:.2f} Bohr mag/cell")
    if energy_Ry is not None:
        lines += [f"     convergence has been achieved in {iterations:3d} iterations",
                  f"!    total energy              =   {energy_Ry:.8f} Ry",
                  f"     Writing all to output data dir /x/{run_dir.name}/tmp_{job}/{job}.save/ :"]
    lines.append("   JOB DONE.")
    (run_dir / (job + ".out")).write_text("\n".join(lines) + "\n", encoding="utf-8")
    receipt = {"status": "REJECTED", "reason": "SCF iteration ceiling"} if ceiling else {
        "status": "COMPLETE", "reason": None, "scf": {"energy_Ry": energy_Ry, "iterations": iterations}}
    (run_dir / (job + ".qc.json")).write_text(json.dumps(receipt), encoding="utf-8")
    if ceiling:
        (run_dir / (job + ".KILLED")).write_text("SCF iteration ceiling\n", encoding="utf-8")


def test_stacked_rounds_complete_a_site_and_record_round_and_mixing(tmp_path):
    name = "Cu8Cr23Mn35Co34__s16_site2"
    site_dir = "hea/arm_c_2026-10-07/" + name
    production, round_2, round_3 = tmp_path / "production", tmp_path / "r2", tmp_path / "r3"
    energies = {"slab": -7872.00022049, "OH": -7914.75368997, "O": -7913.46937673, "OOH": -7956.25801633}
    for state, energy in energies.items():
        failed = state in ("slab", "OH")
        write_fake(production / "runs" / site_dir, state + "__atomic", None if failed else energy, ceiling=failed)
    r2_dir, r3_dir = r2.RUN_ROOT + "/" + name, r3.RUN_ROOT + "/" + name
    write_fake(round_2 / "runs" / r2_dir, "OH__atomic_moved", energies["OH"], seeded=True, iterations=33)
    write_fake(round_2 / "runs" / r2_dir, "slab__atomic_moved", None, ceiling=True, seeded=True)
    write_fake(round_3 / "runs" / r3_dir, "slab__atomic_moved_b010", energies["slab"], seeded=True, iterations=150)
    site = {"formula": "Cu8Cr23Mn35Co34", "seed": 16, "site_index": 2, "site_metal": "Mn",
            "roles": {"support_lo": {"weight": "1/2", "p10_V": 0.38}}, "eta_mlip_V": 0.36,
            "dG_mlip_eV": {"OH": 1.0, "O": 2.0, "OOH": 4.0}, "dir": site_dir,
            "states": {s: {"job": s + "__atomic"} for s in readout.STATES}}
    gas = {g: hpr.gas_references()[g]["E_eV"] for g in ("H2O", "H2")}
    seed = {"state": "O", "job": "O__atomic_ndim16"}
    r2_rows = {state: {"site_dir": site_dir, "state": state, "dir": r2_dir, "job": state + "__atomic_moved",
                       "seed": seed, "seed_density": "moved"} for state in ("OH", "slab")}
    r3_rows = {"slab": {"site_dir": site_dir, "state": "slab", "dir": r3_dir, "job": "slab__atomic_moved_b010",
                        "seed": seed, "seed_density": "moved", "round": 3, "mixing": {"mixing_beta": 0.1, "mixing_ndim": 16}}}
    one = readout.site_result(site, production, gas, {}, None, r2_rows, round_2)
    both = readout.site_result(site, production, gas, {}, None, r2_rows, round_2, [(r3_rows, round_3)])
    assert not one["complete"] and one["failures"] == {"slab": "CEILING"}
    assert both["complete"] and [a["job"] for a in both["extension_attempts"]] == [
        "OH__atomic_moved", "slab__atomic_moved", "slab__atomic_moved_b010"]
    last = both["extension_attempts"][-1]
    assert last["accepted"] and last["round"] == 3 and last["mixing"] == {"mixing_beta": 0.1, "mixing_ndim": 16}
    assert last["beyond_registered_cap"] and "round" not in both["extension_attempts"][0]
    assert both["states"]["slab"]["job"] == "slab__atomic_moved_b010" and both["recipes"] == ["production", "seeded"]
    assert one["extension_attempts"] == both["extension_attempts"][:2]


def test_a_converged_round_3_state_is_set_against_its_site_s_magnetic_state(tmp_path):
    name = "Cu8Cr23Mn35Co34__s16_site2"
    site_dir = "hea/arm_c_2026-10-07/" + name
    production = tmp_path / "production"
    energies = {"slab": -7872.00022049, "OH": -7914.75368997, "O": -7913.46937673, "OOH": -7956.25801633}
    moments = {"O": 49.63, "OH": 50.13, "OOH": 50.00}
    for state, energy in energies.items():
        write_fake(production / "runs" / site_dir, state + "__atomic", None if state == "slab" else energy,
                   ceiling=state == "slab", moment=moments.get(state))
    site = {"formula": "Cu8Cr23Mn35Co34", "seed": 16, "site_index": 2, "site_metal": "Mn",
            "roles": {"support_lo": {"weight": "1/2", "p10_V": 0.38}}, "eta_mlip_V": 0.36,
            "dG_mlip_eV": {"OH": 1.0, "O": 2.0, "OOH": 4.0}, "dir": site_dir,
            "states": {s: {"job": s + "__atomic"} for s in readout.STATES}}
    gas = {g: hpr.gas_references()[g]["E_eV"] for g in ("H2O", "H2")}
    ext_dir = r3.RUN_ROOT + "/" + name
    for label, moment, nearest, flag in (("low", 45.20, "O", True), ("high", 51.25, "OH", False)):
        extension = tmp_path / label
        job = "slab" + r3.JOB_SUFFIX
        write_fake(extension / "runs" / ext_dir, job, energies["slab"], seeded=True, iterations=150, moment=moment)
        row = {"site_dir": site_dir, "state": "slab", "dir": ext_dir, "job": job, "seed": {"state": "O", "job": "O__atomic"},
               "seed_density": "moved", "round": 3, "mixing": dict(r3.MIXING)}
        result = readout.site_result(site, production, gas, {}, None, {"slab": row}, extension)
        check = result["extension_attempts"][0]["magnetization_vs_site"]
        assert result["complete"] and check["nearest_state"] == nearest and check["flag"] is flag
        assert check["difference_uB"] == round(moment - moments[nearest], 2)


def test_qe_s_own_stop_counts_as_a_ceiling_and_records_its_saved_density(tmp_path):
    name = "Fe25Co25Ni25Cr25__s25_site2"
    site_dir = "hea/arm_c_2026-10-07/" + name
    production, extension = tmp_path / "production", tmp_path / "r3"
    for state in readout.STATES:
        write_fake(production / "runs" / site_dir, state + "__atomic", None if state == "O" else -8900.0, ceiling=state == "O")
    ext_dir = r3.RUN_ROOT + "/" + name
    site = {"formula": "Fe25Co25Ni25Cr25", "seed": 25, "site_index": 2, "site_metal": "Fe",
            "roles": {"support_hi": {"weight": "1/2"}}, "eta_mlip_V": 0.45, "dir": site_dir,
            "states": {s: {"job": s + "__atomic"} for s in readout.STATES}}
    gas = {g: hpr.gas_references()[g]["E_eV"] for g in ("H2O", "H2")}
    rows = {}
    for job, stop in (("O_time", "     Maximum CPU time exceeded"),
                      ("O_steps", "     convergence NOT achieved after 300 iterations: stopping")):
        run_dir = extension / "runs" / ext_dir
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / (job + ".out")).write_text("\n".join([
            "     The initial density is read from file :", stop,
            f"     Writing config to output data dir /x/{name}/tmp_{job}/{job}.save/ :", "   JOB DONE.", ""]), encoding="utf-8")
        (run_dir / (job + ".qc.json")).write_text(json.dumps({"status": "REJECTED", "reason": "numerical failure marker"}),
                                                  encoding="utf-8")
        (run_dir / (job + ".REJECTED")).write_text("numerical failure marker\n", encoding="utf-8")
        rows[job] = {"site_dir": site_dir, "state": "O", "dir": ext_dir, "job": job, "seed": {"state": "slab", "job": "slab__atomic"},
                     "seed_density": "moved", "round": 3, "mixing": dict(r3.MIXING)}
    for job, kind in (("O_time", "time"), ("O_steps", "iterations")):
        result = readout.site_result(site, production, gas, {}, None, {"O": rows[job]}, extension)
        attempt = result["extension_attempts"][0]
        assert (attempt["failure"], attempt["qe_stop"], attempt["config_written"], attempt["save_written"]) == (
            "CEILING", kind, True, False)
        assert result["failures"] == {"O": "CEILING"} and not result["complete"]
    old_style = {k: v for k, v in rows["O_time"].items() if k not in ("round", "mixing")}  # a round-2 row
    attempt = readout.site_result(site, production, gas, {}, None, {"O": old_style}, extension)["extension_attempts"][0]
    assert attempt["failure"] == "OTHER" and "qe_stop" not in attempt and "config_written" not in attempt


def test_stacked_plans_need_strictly_increasing_rounds(tmp_path):
    for label, rnd in (("a", 3), ("b", 2)):
        (tmp_path / label / "runs").mkdir(parents=True)
        (tmp_path / (label + ".json")).write_text(json.dumps({"round": rnd, "selection": []}), encoding="utf-8")
    base = ["--plan", str(ROOT / "results/arm_c_2026-10-07/site_plan.json"), "--mirror", str(tmp_path),
            "--rerun-plan", str(ROOT / "results/arm_c_2026-10-07_rerun/rerun_plan.json"),
            "--rerun-mirror", str(ROOT / "results/arm_c_2026-10-07_rerun/raw_mirror"), "--out", str(tmp_path / "out.json")]
    with pytest.raises(SystemExit):
        readout.main(base + ["--ext-plan", str(tmp_path / "a.json"), "--ext-mirror", str(tmp_path / "a"),
                             "--ext-plan", str(tmp_path / "b.json"), "--ext-mirror", str(tmp_path / "b")])
    assert not (tmp_path / "out.json").exists()


def test_the_readout_needs_one_mirror_per_extension_round(tmp_path):
    (tmp_path / "m2" / "runs").mkdir(parents=True)
    base = ["--plan", str(ROOT / "results/arm_c_2026-10-07/site_plan.json"), "--mirror", str(tmp_path),
            "--rerun-plan", str(ROOT / "results/arm_c_2026-10-07_rerun/rerun_plan.json"),
            "--rerun-mirror", str(ROOT / "results/arm_c_2026-10-07_rerun/raw_mirror"), "--out", str(tmp_path / "out.json")]
    with pytest.raises(SystemExit):
        readout.main(base + ["--ext-plan", str(ROOT / r2.PACKAGE / "ext_plan.json"), "--ext-mirror", str(tmp_path / "m2"),
                             "--ext-plan", str(PACKAGE / "ext_plan.json")])
    with pytest.raises(SystemExit):
        readout.main(base + ["--ext-mirror", str(tmp_path / "m2")])
    assert not (tmp_path / "out.json").exists()
