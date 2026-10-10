"""Offline checks for round 4 of the S8 arm-C extension (the Fe25 s25/2 O from round 3's stopped density, with
Fe 22's Hubbard occupations and PAW block from the converged OH state, the occupations held for the first 5
iterations) and for the readout's held-occupations rule; never launch QE/Slurm or open a network connection."""
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
import arm_c_ext_build as r1  # noqa: E402
import arm_c_ext_r2_build as r2  # noqa: E402
import arm_c_ext_r3_build as r3  # noqa: E402
import arm_c_ext_r4_build as r4  # noqa: E402
import arm_c_readout as readout  # noqa: E402
import hea_panel_readout as hpr  # noqa: E402
import research_batch_seeded as runner  # noqa: E402

PACKAGE = ROOT / r4.PACKAGE
SPEC = json.loads((PACKAGE / "launch_spec.json").read_text(encoding="utf-8"))
PLAN = json.loads((PACKAGE / "ext_plan.json").read_text(encoding="utf-8"))
R3_SPEC = json.loads((ROOT / r4.R3_SPEC).read_text(encoding="utf-8"))
PINS = json.loads((ROOT / r4.START_SOURCES).read_text(encoding="utf-8"))
JOBS = SPEC["stages"]["r4_main"]["jobs"]
ROW = PLAN["selection"][0]
BUNDLE = PACKAGE / "seeds/Fe25Co25Ni25Cr25__s25_site2/O"
SLURM = ROOT / "anvil/99_arm_c_ext_r4.slurm"
R3_OUT = (ROOT / r3.PACKAGE / "raw_mirror/runs" / r3.RUN_ROOT / "Fe25Co25Ni25Cr25__s25_site2/O__atomic_moved_ndim16.out")
R3_START = ROOT / r3.PACKAGE / "seeds/Fe25Co25Ni25Cr25__s25_site2/O/occup.txt"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(name):
    spec = importlib.util.spec_from_file_location("arm_c_ext_r4_" + Path(name).stem, PACKAGE / name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # the network parts run only under __main__
    return module


def blocks(path, size=r1.NS_BLOCK):
    values = r1.numbers(Path(path).read_text(encoding="ascii"))
    assert len(values) % size == 0
    return [values[k:k + size] for k in range(0, len(values), size)]


# ---------------------------------------------------------------- the round-4 package
def test_build_reproduces_every_committed_file_byte_for_byte():
    built = r4.build()
    assert len(built) == 6  # deck, occup.txt, paw.txt, manifest, plan, spec
    for relative, data in built.items():
        assert (ROOT / relative).read_bytes() == data, relative
        assert b"\r" not in data


def test_the_target_is_the_fe25_o_round_3_stopped_with_its_density_written():
    source = json.loads((ROOT / r4.R3_READOUT).read_text(encoding="utf-8"))
    attempt = r4.target(source)
    assert (attempt["job"], attempt["failure"], attempt["qe_stop"], attempt["config_written"], attempt["iterations"]) == (
        "O" + r3.JOB_SUFFIX, "CEILING", "iterations", True, 300)
    assert source["alloys"]["Fe25Co25Ni25Cr25"]["status"] == "NO_VALUE"
    receipt = json.loads((ROOT / r3.PACKAGE / "raw_mirror/runs" / r3.RUN_ROOT /
                          "Fe25Co25Ni25Cr25__s25_site2/O__atomic_moved_ndim16.qc.json").read_text(encoding="utf-8"))
    assert PINS["save"] == receipt["scratch_retained"] + "/O__atomic_moved_ndim16.save"
    assert PINS["all_match"] and PINS["occup_matches_mirror"]


def test_the_deck_differs_from_round_3_only_in_prefix_and_held_occupations():
    job = JOBS[0]
    new = (ROOT / f"runs/{job['dir']}/{job['job']}.in").read_text(encoding="utf-8").split("\n")
    old = (ROOT / job["source_deck"]).read_text(encoding="utf-8").split("\n")
    assert sha(ROOT / job["source_deck"]) == R3_SPEC["files"][job["source_deck"]]
    ndim = old.index("  mixing_ndim = 16")
    assert len(new) == len(old) + 1 and new[ndim + 1] == "  mixing_fixed_ns = 5"
    rest = new[:ndim + 1] + new[ndim + 2:]
    assert [(a, b) for a, b in zip(old, rest) if a != b] == [
        ("  prefix = 'O__atomic_moved_ndim16'", "  prefix = 'O__atomic_fe22oh_fixns5'")]
    electrons = new[new.index("&ELECTRONS"):new.index("/", new.index("&ELECTRONS"))]
    assert "  mixing_fixed_ns = 5" in electrons and "  startingpot = 'file'" in electrons
    assert job["job"] == "O" + r4.JOB_SUFFIX


def test_the_occupations_are_round_3_s_last_with_fe22_from_the_converged_oh_state():
    built = blocks(BUNDLE / "occup.txt")
    stop = blocks(ROOT / ROW["occupations"]["start"])
    source = blocks(ROOT / ROW["occupations"]["from"]["path"])
    assert len(built) == len(stop) == r1.nat_of("O") == 73 and len(source) == r1.nat_of("OH")
    assert [k + 1 for k in range(73) if built[k] != stop[k]] == [22]
    assert built[21] == source[21] and not any(built[72])  # Fe 22 from OH; O1 carries no occupations
    assert sha(ROOT / ROW["occupations"]["start"]) == PINS["files"]["occup.txt"]["sha256"] == ROW["occupations"]["start_sha256"]
    assert sha(ROOT / ROW["occupations"]["from"]["path"]) == PINS["fetched"]["oh_occup.txt"]["sha256"]
    receipt = json.loads((ROOT / r4.R3_SITE_OCCUPATIONS).read_text(encoding="utf-8"))
    assert [(f["state"], f["job"], f["sha256"]) for f in receipt["files"]
            if f["site"] == "Fe25Co25Ni25Cr25__s25_site2" and f["state"] == "OH"] == [
        ("OH", "OH__atomic_moved", ROW["occupations"]["from"]["sha256"])]
    _, atoms = r1.geometry((ROOT / JOBS[0]["source_deck"]).read_text(encoding="utf-8"))
    assert atoms[21][0] == "Fe" and "kjpaw" in (ROOT / JOBS[0]["source_deck"]).read_text(encoding="utf-8").split(
        "  Fe  55.845  ", 1)[1].split("\n", 1)[0]
    up, down = sum(built[21][k * 6] for k in range(5)), sum(built[21][25 + k * 6] for k in range(5))
    assert (round(up, 5), round(down, 5)) == (4.90774, 1.29229)  # moment 3.62 uB; round 3 stopped at 3.18


def test_the_paw_file_is_round_3_s_last_with_fe22_s_blocks_from_the_oh_state():
    built = r1.numbers((BUNDLE / "paw.txt").read_text(encoding="ascii"))
    stop = r1.numbers((ROOT / ROW["paw"]["start"]).read_text(encoding="ascii"))
    source = r1.numbers((ROOT / ROW["paw"]["from"]["path"]).read_text(encoding="ascii"))
    nat, nat_oh, b = 73, 74, r1.BEC_BLOCK
    assert len(built) == len(stop) == b * nat * 2 and len(source) == b * nat_oh * 2
    changed = sorted({(k // b) % nat + 1 for k in range(len(built)) if built[k] != stop[k]})
    assert changed == [22]
    for spin in range(2):
        lo, src = b * (spin * nat + 21), b * (spin * nat_oh + 21)
        assert built[lo:lo + b] == source[src:src + b] != stop[lo:lo + b]
    assert sha(ROOT / ROW["paw"]["start"]) == PINS["files"]["paw.txt"]["sha256"] == ROW["paw"]["start_sha256"]
    assert ROW["paw"]["from"]["sha256"] == PINS["fetched"]["oh_paw.txt"]["sha256"] == sha(ROOT / ROW["paw"]["from"]["path"])


def test_the_start_is_round_3_s_stopped_save_copied_on_anvil():
    job = JOBS[0]
    files = job["scratch_source"]["files"]
    assert set(files) == {r2.DENSITY, r2.XML, "paw.txt", "occup.txt"}
    for name in (r2.DENSITY, r2.XML):
        assert files[name] == PINS["files"][name]["sha256"]
        assert ROW["remote_copy"][name] == PINS["save"] + "/" + name
    assert set(ROW["remote_copy"]) == {r2.DENSITY, r2.XML} and ROW["seed_density"] == "stopped"
    assert files["occup.txt"] == sha(BUNDLE / "occup.txt") == ROW["occupations"]["sha256"]
    assert files["paw.txt"] == sha(BUNDLE / "paw.txt") == ROW["paw"]["sha256"]
    assert (job["seed"]["state"], job["seed"]["job"]) == ("O", "O" + r3.JOB_SUFFIX) and job["seed"]["save_dir"] == PINS["save"]
    assert job["nk"] == 8 and job["recipe"] == "seeded"


def test_limits_let_qe_stop_itself_and_fit_the_runner_and_the_campaign():
    job = JOBS[0]
    assert (job["max_iterations"], job["scf_seconds"], job["projection_seconds"]) == (300, 19000, 600)
    assert job["scf_seconds"] <= runner.SCF_SECONDS and job["scf_seconds"] - r4.QE_MAX_SECONDS >= 9 * 63
    assert r4.FIXED_NS == 5 < job["max_iterations"]
    allocation = SPEC["allocation"]
    assert allocation["stage_ceilings_cpu_su"] == {"r4_main": 736} == {"r4_main": 345 * 128 // 60}
    # 20,888.5 before round 3 + round 3's sacct CPU time (2,129,664 + 2,338,816 core-seconds = 1,241.2 SU)
    assert allocation["spent_before_this_launch_cpu_su"] == 22129.7 == round(20888.5 + 4468480 / 3600, 1)
    assert allocation["spent_before_this_launch_cpu_su"] + 736 <= allocation["approved_campaign_ceiling_cpu_su"] == 23680
    assert SPEC["stages"]["r4_main"]["wall_minutes"] * 60 >= job["scf_seconds"] + job["projection_seconds"] + 300
    assert SPEC["pseudo_md5"] == R3_SPEC["pseudo_md5"] and SPEC["qe_binaries_sha256"] == R3_SPEC["qe_binaries_sha256"]
    assert SPEC["exclusions"] == R3_SPEC["exclusions"]
    for relative in r1.RUNNER_FILES:
        assert SPEC["files"][relative] == R3_SPEC["files"][relative]
    for relative, pin in SPEC["files"].items():
        assert sha(ROOT / relative) == pin, relative


def test_plan_records_round_4_the_held_occupations_and_round_3_s_failure():
    assert PLAN["round"] == 4 and PLAN["mixing"] == {"mixing_beta": 0.3, "mixing_ndim": 16, "mixing_fixed_ns": 5}
    assert PLAN["source_readout"] == SPEC["source_readout"] and PLAN["source_readout"]["sha256"] == sha(ROOT / r4.R3_READOUT)
    assert PLAN["round_3"]["spec_sha256"] == sha(ROOT / r4.R3_SPEC)
    assert (ROW["round"], ROW["round_3_job"], ROW["round_3_failure"], ROW["mixing"]) == (
        4, "O" + r3.JOB_SUFFIX, "CEILING", PLAN["mixing"])
    assert ROW["occupations"]["atoms_replaced"] == ROW["paw"]["atoms_replaced"] == [22]
    assert ROW["occupations"]["from"]["state"] == ROW["paw"]["from"]["state"] == "OH"


def test_the_unchanged_runner_validates_the_stage(tmp_path):
    """The density and XML live only on Anvil; stand-ins with their own pins exercise everything else."""
    for relative in SPEC["files"]:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    spec = json.loads(json.dumps(SPEC))
    source = spec["stages"]["r4_main"]["jobs"][0]["scratch_source"]
    for name in (r2.DENSITY, r2.XML):
        stand_in = tmp_path / source["save_dir"] / name
        stand_in.write_bytes(b"stand-in for " + name.encode())
        source["files"][name] = sha(stand_in)
    group = runner.validate(spec, tmp_path, "r4_main")
    assert [j["job"] for j in group["jobs"]] == ["O" + r4.JOB_SUFFIX]
    (tmp_path / source["save_dir"] / r2.XML).write_bytes(b"drifted stand-in")
    with pytest.raises(ValueError, match="drifted: " + r2.XML):
        runner.validate(spec, tmp_path, "r4_main")


def test_slurm_script_pins_the_spec_and_runner_and_keeps_round_3_resources():
    text = SLURM.read_text(encoding="utf-8")
    assert "\r" not in text
    assert f'check_hash "$SPEC" {sha(PACKAGE / "launch_spec.json")}' in text
    assert f'check_hash "$RUNNER" {sha(ROOT / "src/dft/research_batch_seeded.py")}' in text
    assert "r4_main) ;;" in text and 'ROOT="$PROJECT/sts_arm_c_ext_r4_2026-10-10"' in text
    old = (ROOT / "anvil/98_arm_c_ext_r3.slurm").read_text(encoding="utf-8")
    assert [l for l in text.split("\n") if l.startswith("#SBATCH") and "log" not in l] == [
        l for l in old.split("\n") if l.startswith("#SBATCH") and "log" not in l]
    assert text.split("export OMP_NUM_THREADS", 1)[1] == old.split("export OMP_NUM_THREADS", 1)[1]
    bash = shutil.which("bash")
    if bash:
        assert subprocess.run([bash, "-n", str(SLURM)]).returncode == 0


def test_ops_target_the_round_4_root_and_copy_round_3_s_save():
    module = load("launch_ops.py")
    assert module.REMOTE == "/anvil/projects/x-che260157/sts_arm_c_ext_r4_2026-10-10"
    assert module.SLURM_REL == "anvil/99_arm_c_ext_r4.slurm"
    assert {k: (v["array"], v["tasks"], v["time"], v["minutes"]) for k, v in module.ARRAYS.items()} == {
        "r4_main": ("1-1%1", 1, "05:45:00", 345)}
    shape = module.ARRAYS["r4_main"]
    assert shape["tasks"] * shape["minutes"] * 128 // 60 == SPEC["allocation"]["stage_ceilings_cpu_su"]["r4_main"]
    assert shape["minutes"] == SPEC["stages"]["r4_main"]["wall_minutes"] and shape["tasks"] == len(JOBS)
    copies = module.seed_copies()
    assert len(copies) == 2
    for source, target, pin in copies:
        name = source.rsplit("/", 1)[1]
        assert source == PINS["save"] + "/" + name and pin == PINS["files"][name]["sha256"]
        assert target == module.REMOTE + "/" + ROW["bundle"] + "/" + name
    for name in ("occup.txt", "paw.txt"):  # the rebuilt files are uploaded, pinned
        assert ROW["bundle"] + "/" + name in module.STAGE
    ops = (PACKAGE / "launch_ops.py").read_text(encoding="utf-8")
    assert "held shape not validated" in ops and '"--exclude=" + SPEC["exclusions"]' in ops
    for name in ("status_once.py", "collect_terminal.py", "start_check.py"):
        assert '/anvil/projects/x-che260157/sts_arm_c_ext_r4_2026-10-10"' in (PACKAGE / name).read_text(encoding="utf-8")


def test_the_start_check_confirms_the_occupations_read_and_the_hold():
    module = load("start_check.py")
    text = R3_OUT.read_text(errors="replace")
    r3_start = R3_START.read_text(encoding="ascii")
    found = module.check(text, r3_start)  # round 3 printed its own start, but held nothing
    assert found["same_atoms"] and not found["over_tolerance"] and found["max_difference"] < 5.1e-6
    assert found["fe22_matrix_max_difference"] <= 5.01e-4
    assert found["density_read"] and not found["held"] and found["match"] is False
    held = text.replace("     iteration #  2", "     " + module.RESET + "\n\n     iteration #  2", 1)
    assert module.check(held, r3_start)["match"] is True
    before = text.split("     iteration #  1", 1)[0]  # the starting block is out, the first iteration is not
    assert module.check(before, r3_start)["match"] is None
    built = (BUNDLE / "occup.txt").read_text(encoding="ascii")
    assert module.check(held, built)["match"] is False and module.check(before, built)["match"] is False
    assert module.check("     iteration #  1\n", built)["match"] is None


# ---------------------------------------------------------------- the readout's held-occupations rule
def write_fake(run_dir, job, energy_Ry=None, iterations=40):
    run_dir.mkdir(parents=True, exist_ok=True)
    lines = ["     running on   128 processor cores", "     The initial density is read from file :"]
    if energy_Ry is not None:
        lines += [f"     convergence has been achieved in {iterations:3d} iterations",
                  f"!    total energy              =   {energy_Ry:.8f} Ry",
                  f"     Writing all to output data dir /x/{run_dir.name}/tmp_{job}/{job}.save/ :"]
    lines.append("   JOB DONE.")
    (run_dir / (job + ".out")).write_text("\n".join(lines) + "\n", encoding="utf-8")
    receipt = {"status": "REJECTED", "reason": "SCF iteration ceiling"} if energy_Ry is None else {
        "status": "COMPLETE", "reason": None, "scf": {"energy_Ry": energy_Ry, "iterations": iterations}}
    (run_dir / (job + ".qc.json")).write_text(json.dumps(receipt), encoding="utf-8")


def test_a_convergence_within_the_held_iterations_is_not_accepted(tmp_path):
    name = "Fe25Co25Ni25Cr25__s25_site2"
    site_dir = "hea/arm_c_2026-10-07/" + name
    production, extension = tmp_path / "production", tmp_path / "r4"
    for state in readout.STATES:
        write_fake(production / "runs" / site_dir, state + "__atomic", None if state == "O" else -8900.0)
    site = {"formula": "Fe25Co25Ni25Cr25", "seed": 25, "site_index": 2, "site_metal": "Cr",
            "roles": {"support_hi": {"weight": "4/5"}}, "eta_mlip_V": 0.45, "dir": site_dir,
            "dG_mlip_eV": {"OH": 1.0, "O": 2.0, "OOH": 4.0},
            "states": {s: {"job": s + "__atomic"} for s in readout.STATES}}
    gas = {g: hpr.gas_references()[g]["E_eV"] for g in ("H2O", "H2")}
    ext_dir = r4.RUN_ROOT + "/" + name
    results = {}
    for job, iterations, mixing in (("O_early", 5, r4.MIXING), ("O_late", 6, r4.MIXING),
                                    ("O_unheld", 4, dict(r3.MIXING))):
        write_fake(extension / "runs" / ext_dir, job, -8913.9, iterations=iterations)
        row = {"site_dir": site_dir, "state": "O", "dir": ext_dir, "job": job, "seed": {"state": "O", "job": "O_r3"},
               "seed_density": "stopped", "round": 4, "mixing": mixing}
        results[job] = readout.site_result(site, production, gas, {}, None, {"O": row}, extension)
    early = results["O_early"]["extension_attempts"][0]
    assert not early["accepted"] and early["held_occupations"] and early["failure"] == "HELD" and early["E_eV"] is None
    assert results["O_early"]["failures"] == {"O": "CEILING"} and not results["O_early"]["complete"]
    assert results["O_late"]["complete"] and "held_occupations" not in results["O_late"]["extension_attempts"][0]
    assert results["O_unheld"]["complete"]  # the rule needs held occupations
    assert readout.failure_class({"accepted": False, "held_occupations": True, "parser_status": "CONVERGED"}) == "HELD"
