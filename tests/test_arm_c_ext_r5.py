"""Offline checks for round 5 of the S8 arm-C extension (a second start of the Fe25 s25/2 slab from its own converged
density, with Fe 22's Hubbard occupations and PAW block from the converged OH state, the occupations held for the
first 5 iterations), for the readout's second-start rule and for round 5's readout and checks; never launch
QE/Slurm or open a network connection. The readout reproduction needs the local projection outputs and skips
without them."""
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
import arm_c_ext_r5_build as r5  # noqa: E402
import arm_c_readout as readout  # noqa: E402
import hea_panel_readout as hpr  # noqa: E402
import research_batch_seeded as runner  # noqa: E402

PACKAGE = ROOT / r5.PACKAGE
SPEC = json.loads((PACKAGE / "launch_spec.json").read_text(encoding="utf-8"))
PLAN = json.loads((PACKAGE / "ext_plan.json").read_text(encoding="utf-8"))
R4_SPEC = json.loads((ROOT / r5.R4_SPEC).read_text(encoding="utf-8"))
PINS = json.loads((ROOT / r5.START_SOURCES).read_text(encoding="utf-8"))
JOBS = SPEC["stages"]["r5_main"]["jobs"]
ROW = PLAN["selection"][0]
SITE = "Fe25Co25Ni25Cr25__s25_site2"
BUNDLE = PACKAGE / "seeds" / SITE / "slab"
SLURM = ROOT / "anvil/100_arm_c_ext_r5.slurm"
PRODUCTION_DECK = ROOT / "runs/hea/arm_c_2026-10-07" / SITE / "slab__atomic.in"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(name):
    spec = importlib.util.spec_from_file_location("arm_c_ext_r5_" + Path(name).stem, PACKAGE / name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # the network parts run only under __main__
    return module


def blocks(path, size=r1.NS_BLOCK):
    values = r1.numbers(Path(path).read_text(encoding="ascii"))
    assert len(values) % size == 0
    return [values[k:k + size] for k in range(0, len(values), size)]


# ---------------------------------------------------------------- the round-5 package
def test_build_reproduces_every_committed_file_byte_for_byte():
    built = r5.build()
    assert len(built) == 6  # deck, occup.txt, paw.txt, manifest, plan, spec
    for relative, data in built.items():
        assert (ROOT / relative).read_bytes() == data, relative
        assert b"\r" not in data


def test_the_target_is_the_production_slab_of_the_completed_site():
    source = json.loads((ROOT / r5.R4_READOUT).read_text(encoding="utf-8"))
    slab = r5.target(source)
    assert (slab["job"], slab["recipe"], slab["accepted"], slab["iterations"]) == ("slab__atomic", "production", True, 69)
    assert source["alloys"]["Fe25Co25Ni25Cr25"]["status"] == "SINGLE_SITE"
    assert ROW["first"] == {"job": "slab__atomic", "recipe": "production", "E_eV": slab["E_eV"],
                            "total_magnetization": slab["total_magnetization"]}
    receipt = json.loads((ROOT / "results/arm_c_2026-10-07/raw_mirror/runs/hea/arm_c_2026-10-07" / SITE /
                          "slab__atomic.qc.json").read_text(encoding="utf-8"))
    assert PINS["save"] == receipt["scratch_retained"] + "/slab__atomic.save"
    round_1 = json.loads((ROOT / "results/arm_c_ext_2026-10-08/seed_fetch.json").read_text(encoding="utf-8"))
    pinned = round_1["seeds"][SITE + "__slab__atomic"]
    assert pinned["save_dir"] == PINS["save"] and PINS["all_match"] and PINS["matches_round_1"]
    assert {name: f["sha256"] for name, f in PINS["files"].items()} == pinned["sha256"]


def test_the_deck_is_the_production_slab_s_with_round_4_s_changes():
    job = JOBS[0]
    new = (ROOT / f"runs/{job['dir']}/{job['job']}.in").read_text(encoding="utf-8").split("\n")
    old = PRODUCTION_DECK.read_text(encoding="utf-8").split("\n")
    assert job["source_deck"] == PRODUCTION_DECK.relative_to(ROOT).as_posix()
    assert sha(PRODUCTION_DECK) == "200f913e8a129cffd54dfdad8ff0b2e838e62905dcb7dbc2ca067e430c6f2406"
    added = ["  mixing_ndim = 16", "  mixing_fixed_ns = 5", "  startingpot = 'file'"]
    assert len(new) == len(old) + 3 and all(new.count(line) == 1 for line in added)
    rest = [line for line in new if line not in added]
    assert [(a, b) for a, b in zip(old, rest) if a != b] == [
        ("  prefix = 'slab__atomic'", "  prefix = 'slab__atomic_fe22oh_fixns5'"),
        ("  max_seconds = 165000", "  max_seconds = 18400")]
    # the same edits turn the production O deck into round 4's
    o_deck = (ROOT / "runs/hea/arm_c_2026-10-07" / SITE / "O__atomic.in").read_text(encoding="utf-8")
    r4_deck = (ROOT / "runs" / r4.RUN_ROOT / SITE / ("O" + r4.JOB_SUFFIX + ".in")).read_text(encoding="utf-8")
    assert r5.r5_deck(o_deck, "O" + r4.JOB_SUFFIX) == r4_deck
    assert job["job"] == "slab" + r5.JOB_SUFFIX


def test_the_occupations_are_the_slab_s_with_fe22_from_the_converged_oh_state():
    built = blocks(BUNDLE / "occup.txt")
    start = blocks(ROOT / ROW["occupations"]["start"])
    source = blocks(ROOT / ROW["occupations"]["from"]["path"])
    assert len(built) == len(start) == r1.nat_of("slab") == 72 and len(source) == r1.nat_of("OH")
    assert [k + 1 for k in range(72) if built[k] != start[k]] == [22]
    assert built[21] == source[21]
    assert sha(ROOT / ROW["occupations"]["start"]) == PINS["files"]["occup.txt"]["sha256"] == ROW["occupations"]["start_sha256"]
    assert ROW["occupations"]["from"]["job"] == "OH__atomic_moved"
    _, atoms = r1.geometry(PRODUCTION_DECK.read_text(encoding="utf-8"))
    assert atoms[21][0] == "Fe"
    up, down = sum(built[21][k * 6] for k in range(5)), sum(built[21][25 + k * 6] for k in range(5))
    assert (round(up, 5), round(down, 5)) == (4.90774, 1.29229)  # round 4's start for Fe 22


def test_the_paw_file_is_the_slab_s_with_fe22_s_blocks_from_the_oh_state():
    built = r1.numbers((BUNDLE / "paw.txt").read_text(encoding="ascii"))
    start = r1.numbers((ROOT / ROW["paw"]["start"]).read_text(encoding="ascii"))
    source = r1.numbers((ROOT / ROW["paw"]["from"]["path"]).read_text(encoding="ascii"))
    nat, nat_oh, b = 72, 74, r1.BEC_BLOCK
    assert len(built) == len(start) == b * nat * 2 and len(source) == b * nat_oh * 2
    assert sorted({(k // b) % nat + 1 for k in range(len(built)) if built[k] != start[k]}) == [22]
    for spin in range(2):
        lo, src = b * (spin * nat + 21), b * (spin * nat_oh + 21)
        assert built[lo:lo + b] == source[src:src + b] != start[lo:lo + b]
    assert sha(ROOT / ROW["paw"]["start"]) == PINS["files"]["paw.txt"]["sha256"] == ROW["paw"]["start_sha256"]
    assert ROW["paw"]["from"]["path"] == "results/arm_c_ext_r4_2026-10-10/sources/oh_paw.txt"
    assert ROW["paw"]["from"]["sha256"] == sha(ROOT / ROW["paw"]["from"]["path"])


def test_the_start_is_the_production_slab_s_own_save_copied_on_anvil():
    job = JOBS[0]
    files = job["scratch_source"]["files"]
    assert set(files) == {r2.DENSITY, r2.XML, "paw.txt", "occup.txt"}
    for name in (r2.DENSITY, r2.XML):
        assert files[name] == PINS["files"][name]["sha256"]
        assert ROW["remote_copy"][name] == PINS["save"] + "/" + name
    assert set(ROW["remote_copy"]) == {r2.DENSITY, r2.XML} and ROW["seed_density"] == "own_converged"
    assert files["occup.txt"] == sha(BUNDLE / "occup.txt") == ROW["occupations"]["sha256"]
    assert files["paw.txt"] == sha(BUNDLE / "paw.txt") == ROW["paw"]["sha256"]
    assert (job["seed"]["state"], job["seed"]["job"], job["seed"]["recipe"]) == ("slab", "slab__atomic", "production")
    assert job["seed"]["save_dir"] == PINS["save"] and job["nk"] == 8 and job["recipe"] == "seeded"


def test_limits_are_round_4_s_and_fit_the_campaign():
    job = JOBS[0]
    assert (job["max_iterations"], job["scf_seconds"], job["projection_seconds"]) == (300, 19000, 600)
    assert job["scf_seconds"] <= runner.SCF_SECONDS and r5.QE_MAX_SECONDS == 18400
    allocation = SPEC["allocation"]
    assert allocation["stage_ceilings_cpu_su"] == {"r5_main": 736} == {"r5_main": 345 * 128 // 60}
    # 22,129.7 before round 4 + round 4's sacct CPU time (179,840 core-seconds = 49.96 SU)
    assert allocation["spent_before_this_launch_cpu_su"] == 22179.7 == round(22129.7 + 179840 / 3600, 1)
    assert allocation["spent_before_this_launch_cpu_su"] + 736 <= allocation["approved_campaign_ceiling_cpu_su"] == 23680
    assert SPEC["stages"]["r5_main"]["wall_minutes"] * 60 >= job["scf_seconds"] + job["projection_seconds"] + 300
    for key in ("pseudo_md5", "qe_binaries_sha256", "exclusions"):
        assert SPEC[key] == R4_SPEC[key]
    for relative in r1.RUNNER_FILES:
        assert SPEC["files"][relative] == R4_SPEC["files"][relative]
    for relative, pin in SPEC["files"].items():
        assert sha(ROOT / relative) == pin, relative


def test_plan_marks_a_second_start_of_the_accepted_slab():
    assert PLAN["round"] == 5 and PLAN["mixing"] == {"mixing_beta": 0.3, "mixing_ndim": 16, "mixing_fixed_ns": 5}
    assert PLAN["source_readout"] == SPEC["source_readout"] and PLAN["source_readout"]["sha256"] == sha(ROOT / r5.R4_READOUT)
    assert PLAN["round_4"]["spec_sha256"] == sha(ROOT / r5.R4_SPEC)
    assert (ROW["site_dir"], ROW["state"], ROW["second_start"], ROW["round"]) == (
        "hea/arm_c_2026-10-07/" + SITE, "slab", True, 5)
    assert ROW["occupations"]["atoms_replaced"] == ROW["paw"]["atoms_replaced"] == [22]
    assert ROW["occupations"]["from"]["state"] == ROW["paw"]["from"]["state"] == "OH"


def test_the_unchanged_runner_validates_the_stage(tmp_path):
    """The density and XML live only on Anvil; stand-ins with their own pins exercise everything else."""
    for relative in SPEC["files"]:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    spec = json.loads(json.dumps(SPEC))
    source = spec["stages"]["r5_main"]["jobs"][0]["scratch_source"]
    for name in (r2.DENSITY, r2.XML):
        stand_in = tmp_path / source["save_dir"] / name
        stand_in.write_bytes(b"stand-in for " + name.encode())
        source["files"][name] = sha(stand_in)
    group = runner.validate(spec, tmp_path, "r5_main")
    assert [j["job"] for j in group["jobs"]] == ["slab" + r5.JOB_SUFFIX]
    (tmp_path / source["save_dir"] / r2.XML).write_bytes(b"drifted stand-in")
    with pytest.raises(ValueError, match="drifted: " + r2.XML):
        runner.validate(spec, tmp_path, "r5_main")


def test_slurm_script_pins_the_spec_and_runner_and_keeps_round_4_resources():
    text = SLURM.read_text(encoding="utf-8")
    assert "\r" not in text
    assert f'check_hash "$SPEC" {sha(PACKAGE / "launch_spec.json")}' in text
    assert f'check_hash "$RUNNER" {sha(ROOT / "src/dft/research_batch_seeded.py")}' in text
    assert "r5_main) ;;" in text and 'ROOT="$PROJECT/sts_arm_c_ext_r5_2026-10-10"' in text
    old = (ROOT / "anvil/99_arm_c_ext_r4.slurm").read_text(encoding="utf-8")
    assert [l for l in text.split("\n") if l.startswith("#SBATCH") and "log" not in l] == [
        l for l in old.split("\n") if l.startswith("#SBATCH") and "log" not in l]
    assert text.split("export OMP_NUM_THREADS", 1)[1] == old.split("export OMP_NUM_THREADS", 1)[1]
    bash = shutil.which("bash")
    if bash:
        assert subprocess.run([bash, "-n", str(SLURM)]).returncode == 0


def test_ops_target_the_round_5_root_and_copy_the_production_slab_s_save():
    module = load("launch_ops.py")
    assert module.REMOTE == "/anvil/projects/x-che260157/sts_arm_c_ext_r5_2026-10-10"
    assert module.SLURM_REL == "anvil/100_arm_c_ext_r5.slurm"
    assert {k: (v["array"], v["tasks"], v["time"], v["minutes"]) for k, v in module.ARRAYS.items()} == {
        "r5_main": ("1-1%1", 1, "05:45:00", 345)}
    shape = module.ARRAYS["r5_main"]
    assert shape["tasks"] * shape["minutes"] * 128 // 60 == SPEC["allocation"]["stage_ceilings_cpu_su"]["r5_main"]
    copies = module.seed_copies()
    assert len(copies) == 2
    for source, target, pin in copies:
        name = source.rsplit("/", 1)[1]
        assert source == PINS["save"] + "/" + name and pin == PINS["files"][name]["sha256"]
        assert target == module.REMOTE + "/" + ROW["bundle"] + "/" + name
    for name in ("occup.txt", "paw.txt"):
        assert ROW["bundle"] + "/" + name in module.STAGE
    old = (ROOT / r4.PACKAGE / "launch_ops.py").read_text(encoding="utf-8")
    new = (PACKAGE / "launch_ops.py").read_text(encoding="utf-8")
    assert old.split("def stage():", 1)[1].replace("round-3 save file", "source save file") == new.split("def stage():", 1)[1]
    for name in ("status_once.py", "collect_terminal.py", "start_check.py"):
        text = (PACKAGE / name).read_text(encoding="utf-8")
        assert '/anvil/projects/x-che260157/sts_arm_c_ext_r5_2026-10-10"' in text and "sts_arm_c_ext_r4" not in text


def test_the_start_check_is_round_4_s_against_this_bundle():
    module, old = load("start_check.py"), (ROOT / r4.PACKAGE / "start_check.py").read_text(encoding="utf-8")
    new = (PACKAGE / "start_check.py").read_text(encoding="utf-8")
    assert old.split("\ndef ", 1)[1].replace("r4_2026", "r5_2026") == new.split("\ndef ", 1)[1]
    built = (BUNDLE / "occup.txt").read_text(encoding="ascii")
    assert module.traces(built)[22] == pytest.approx((4.90774, 1.29229, 6.20003), abs=5e-6)
    assert len(module.traces(built)) == 24  # the slab's Hubbard atoms


# ---------------------------------------------------------------- the readout's second-start rule
RY = hpr.RY_EV
ENERGIES_EV = {"slab": -120716.3259394683, "OH": -121297.89113096446, "O": -121280.69157822353, "OOH": -121862.60691740233}
MOMENTS = {"slab": 41.98, "OH": 44.44, "O": 44.6, "OOH": 43.4}


def write_fake(run_dir, job, energy_Ry=None, iterations=40, moment=None):
    run_dir.mkdir(parents=True, exist_ok=True)
    lines = ["     running on   128 processor cores", "     The initial density is read from file :"]
    if moment is not None:
        lines.append(f"     total magnetization       =    {moment:.2f} Bohr mag/cell")
    if energy_Ry is not None:
        lines += [f"     convergence has been achieved in {iterations:3d} iterations",
                  f"!    total energy              =   {energy_Ry:.8f} Ry",
                  f"     Writing all to output data dir /x/{run_dir.name}/tmp_{job}/{job}.save/ :"]
    lines.append("   JOB DONE.")
    (run_dir / (job + ".out")).write_text("\n".join(lines) + "\n", encoding="utf-8")
    receipt = {"status": "REJECTED", "reason": "SCF iteration ceiling"} if energy_Ry is None else {
        "status": "COMPLETE", "reason": None, "scf": {"energy_Ry": energy_Ry, "iterations": iterations}}
    (run_dir / (job + ".qc.json")).write_text(json.dumps(receipt), encoding="utf-8")


def second_start(tmp_path, shift_meV, iterations=20, failed=(), second=True, converged=True, moment=None,
                 first_job="slab__atomic"):
    """The Fe25 s25/2 site with production runs at round 4's energies and one second start of its slab."""
    site_dir = "hea/arm_c_2026-10-07/" + SITE
    production, extension = tmp_path / "production", tmp_path / "r5"
    energies = {s: round(e / RY, 8) for s, e in ENERGIES_EV.items()}
    for state, energy in energies.items():
        write_fake(production / "runs" / site_dir, state + "__atomic", None if state in failed else energy,
                   moment=MOMENTS[state] if moment is not None else None)
    site = {"formula": "Fe25Co25Ni25Cr25", "seed": 25, "site_index": 2, "site_metal": "Cr",
            "roles": {"support_hi": {"weight": "4/5"}}, "eta_mlip_V": 0.557, "dir": site_dir,
            "dG_mlip_eV": {"OH": 1.8, "O": 3.2, "OOH": 4.6},
            "states": {s: {"job": s + "__atomic"} for s in readout.STATES}}
    gas = {g: hpr.gas_references()[g]["E_eV"] for g in ("H2O", "H2")}
    ext_dir = r5.RUN_ROOT + "/" + SITE
    job = "slab" + r5.JOB_SUFFIX
    write_fake(extension / "runs" / ext_dir, job,
               round(energies["slab"] + shift_meV / 1000 / RY, 8) if converged else None, iterations=iterations,
               moment=moment)
    row = {"site_dir": site_dir, "state": "slab", "dir": ext_dir, "job": job, "round": 5, "mixing": r5.MIXING,
           "seed": {"state": "slab", "job": "slab__atomic"}, "seed_density": "own_converged"}
    if second:
        row.update(second_start=True, first={"job": first_job})
    return readout.site_result(site, production, gas, {}, None, {"slab": row}, extension)


def test_a_second_start_replaces_the_slab_only_when_more_than_1_mev_lower(tmp_path):
    first = second_start(tmp_path / "a", +20.0)
    assert first["potential_limiting_step"] == 1 and abs(first["eta_dft_V"] - 0.8932) < 1e-3
    for shift, replaced in ((-5.0, True), (-0.5, False), (+20.0, False)):
        site = second_start(tmp_path / str(shift), shift)
        attempt = site["extension_attempts"][0]
        assert attempt["second_start"] and attempt["accepted"] and attempt["failure"] is None
        assert attempt["energy_vs_first_meV"] == pytest.approx(shift, abs=1e-3)
        assert attempt["lower"] is replaced and attempt["first_job"] == "slab__atomic"
        assert attempt["replaces"] == ("slab__atomic" if replaced else None)
        assert site["states"]["slab"]["job"] == ("slab" + r5.JOB_SUFFIX if replaced else "slab__atomic")
        # a lower slab raises dG1, the limiting step, one for one; the first slab's value is kept beside it
        assert site["eta_dft_V"] - first["eta_dft_V"] == pytest.approx(0.005 if replaced else 0.0, abs=1e-6)
        assert ("eta_dft_V_with_first" in site) is replaced
        if replaced:
            assert site["eta_dft_V_with_first"] == pytest.approx(first["eta_dft_V"], abs=1e-9)


def test_a_held_or_stopped_second_start_never_replaces_the_slab(tmp_path):
    held = second_start(tmp_path / "held", -50.0, iterations=5)["extension_attempts"][0]
    assert not held["accepted"] and held["held_occupations"] and held["failure"] == "HELD"
    assert held["energy_vs_first_meV"] is None and held["lower"] is False and held["replaces"] is None
    stopped = second_start(tmp_path / "stopped", 0.0, converged=False)
    assert stopped["extension_attempts"][0]["failure"] == "CEILING"
    assert stopped["states"]["slab"]["job"] == "slab__atomic"


def test_a_second_start_needs_its_accepted_first_run(tmp_path):
    with pytest.raises(ValueError, match="a second start needs the accepted first run"):
        second_start(tmp_path / "missing", -5.0, failed=("slab",))
    with pytest.raises(ValueError, match="a second start needs the accepted first run"):
        second_start(tmp_path / "other", -5.0, first_job="slab__atomic_ndim16")
    ordinary = second_start(tmp_path / "ordinary", -5.0, second=False)  # an ordinary row skips an accepted state
    assert ordinary["extension_attempts"] == [] and ordinary["states"]["slab"]["job"] == "slab__atomic"


def test_an_unused_second_start_never_flags_the_value_s_magnetic_state(tmp_path):
    kept = second_start(tmp_path / "kept", +20.0, moment=38.0)  # 5.4 uB from the nearest other state (OOH)
    attempt = kept["extension_attempts"][0]
    assert attempt["magnetization_vs_site"] == {"nearest_state": "OOH", "difference_uB": -5.4, "flag": True}
    assert attempt["magnetization_vs_first_uB"] == -3.98
    assert readout.magnetization_flags([kept]) == []
    used = second_start(tmp_path / "used", -5.0, moment=38.0)
    assert readout.magnetization_flags([used]) == ["s25/2 slab"]
    quiet = second_start(tmp_path / "quiet", -5.0, moment=42.1)
    assert quiet["extension_attempts"][0]["magnetization_vs_first_uB"] == 0.12
    assert readout.magnetization_flags([quiet]) == []


# ---------------------------------------------------------------- the round-5 terminal readout
def test_the_collection_matches_anvil_and_the_start_check_passed():
    collection = json.loads((PACKAGE / "terminal_collection.json").read_text(encoding="utf-8"))
    assert collection["all_match"] and len(collection["files"]) == 7
    kept = [f for f in collection["files"] if not f["path"].endswith(".projwfc.out")]  # projection: local only
    assert all(sha(PACKAGE / "raw_mirror" / f["path"]) == f["remote_sha256"] for f in kept)
    array = json.loads((PACKAGE / "submit_receipt.json").read_text(encoding="utf-8"))["jobs"]["r5_main"]
    job_line = collection["sacct"].splitlines()[0].split("|")
    assert (job_line[0], job_line[2], job_line[6]) == (array + "_1", "COMPLETED", "0:0")
    receipt = json.loads((PACKAGE / "start_check_20261011T003235Z.json").read_text(encoding="utf-8"))
    assert receipt["all_match"] and not receipt["any_mismatch"]
    job = receipt["jobs"][0]
    assert job["density_read"] and job["held"] and job["fe22_printed"] == job["fe22_expected"]


def test_the_round_5_readout_reproduces_the_committed_readout(tmp_path):
    mirrors = (ROOT / "results/arm_c_2026-10-07/raw_mirror", ROOT / "results/arm_c_2026-10-07_rerun/raw_mirror",
               ROOT / r2.PACKAGE / "raw_mirror", ROOT / r4.PACKAGE / "raw_mirror", PACKAGE / "raw_mirror")
    if not all(any(m.rglob("*.projwfc.out")) for m in mirrors):
        pytest.skip("projection outputs are kept local, outside git")
    out = tmp_path / "readout.json"
    readout.main(["--plan", str(ROOT / "results/arm_c_2026-10-07/site_plan.json"), "--mirror", str(mirrors[0]),
                  "--rerun-plan", str(ROOT / "results/arm_c_2026-10-07_rerun/rerun_plan.json"),
                  "--rerun-mirror", str(mirrors[1]),
                  "--ext-plan", str(ROOT / r2.PACKAGE / "ext_plan.json"), "--ext-mirror", str(mirrors[2]),
                  "--ext-plan", str(ROOT / r3.PACKAGE / "ext_plan.json"),
                  "--ext-mirror", str(ROOT / r3.PACKAGE / "raw_mirror"),
                  "--ext-plan", str(ROOT / r4.PACKAGE / "ext_plan.json"), "--ext-mirror", str(mirrors[3]),
                  "--ext-plan", str(PACKAGE / "ext_plan.json"), "--ext-mirror", str(mirrors[4]),
                  "--out", str(out)])
    assert out.read_bytes() == (PACKAGE / "readout.json").read_bytes()


def test_round_5_replaces_the_fe25_s25_2_slab_and_changes_nothing_else():
    stacked = json.loads((PACKAGE / "readout.json").read_text(encoding="utf-8"))
    before = json.loads((ROOT / r4.PACKAGE / "readout.json").read_text(encoding="utf-8"))
    changed = [k for k, (now, then) in enumerate(zip(stacked["sites"], before["sites"], strict=True)) if now != then]
    assert [Path(stacked["sites"][k]["dir"]).name for k in changed] == [SITE]
    site, then = stacked["sites"][changed[0]], before["sites"][changed[0]]
    attempt = site["extension_attempts"][-1]
    assert site["extension_attempts"][:-1] == then["extension_attempts"]
    assert (attempt["job"], attempt["round"], attempt["accepted"], attempt["iterations"], attempt["failure"]) == (
        "slab" + r5.JOB_SUFFIX, 5, True, 65, None)
    assert attempt["second_start"] and attempt["lower"] and attempt["replaces"] == attempt["first_job"] == "slab__atomic"
    assert attempt["energy_vs_first_meV"] == pytest.approx(-259.06, abs=0.01)
    assert attempt["magnetization_vs_first_uB"] == 0.98 and not attempt["magnetization_vs_site"]["flag"]
    assert attempt["seed_read"] and attempt["seed_density"] == "own_converged" and not attempt["severe_failures"]
    assert site["states"]["slab"] == {k: v for k, v in attempt.items() if k not in ("state", "failure")}
    assert {s: v for s, v in site["states"].items() if s != "slab"} == {
        s: v for s, v in then["states"].items() if s != "slab"}
    # the lower slab raises dG1, the limiting step, one for one; the production slab's value is kept beside it
    assert site["eta_dft_V_with_first"] == then["eta_dft_V"]
    assert site["eta_dft_V"] - then["eta_dft_V"] == pytest.approx(-attempt["energy_vs_first_meV"] / 1000, abs=1e-9)
    assert site["potential_limiting_step"] == then["potential_limiting_step"] == 1
    alloy = stacked["alloys"]["Fe25Co25Ni25Cr25"]
    assert alloy["status"] == "SINGLE_SITE" and alloy["C_V"] == site["eta_dft_V"] and alloy["uses_extension"]
    assert {k: v for k, v in stacked["alloys"].items() if k != "Fe25Co25Ni25Cr25"} == {
        k: v for k, v in before["alloys"].items() if k != "Fe25Co25Ni25Cr25"}
    assert stacked["counts"] == dict(before["counts"], ext_attempted=15, ext_accepted=5, ext_seed_read=15,
                                     ext_second_starts=1, ext_second_starts_used=1)
    predictions = stacked["exploratory_predictions"]
    assert predictions["order_all_with_values"] == ["Cu26Ni9Cr31Co33", "Ni31Cr29Cu5Mn35", "Cu22Fe30Co32Mn15",
                                                    "Fe25Co25Ni25Cr25", "Ni34Fe6Cu29Co31"]
    assert {k: v for k, v in predictions.items() if not k.startswith("order")} == {
        k: v for k, v in before["exploratory_predictions"].items() if not k.startswith("order")}
    rest = [k for k in before if k not in ("sites", "counts", "alloys", "exploratory_predictions")]
    assert sorted(stacked) == sorted(before) and all(stacked[k] == before[k] for k in rest)


def test_the_round_5_checks_reproduce_from_the_committed_mirrors():
    module = load("checks.py")
    built = module.build()
    assert json.dumps(built, indent=1) + "\n" == (PACKAGE / "checks.json").read_text(encoding="utf-8")
    run, energy, fe22, value = built["scf"], built["energy"], built["fe22"], built["value"]
    assert run["held_iterations"] == list(range(1, ROW["mixing"]["mixing_fixed_ns"] + 1)) and run["converged_in"] == 65
    assert energy["outcome"] == "lower" and energy["first_iteration_below_production"] == 2
    assert energy["hubbard_difference_meV"] > 0 > energy["rest_difference_meV"]  # the Hubbard term rises
    assert fe22["configuration"] == "OH" and fe22["all_states_share_it"] and fe22["end_to_state"]["slab"] > 0.9
    atoms = built["occupations"]["atoms"]
    assert [a["atom"] for a in atoms[:4]] == [22, 12, 15, 13] and all(a["end_to_production"] < 0.04 for a in atoms[4:])
    co12 = atoms[1]  # 3.5 A from Fe 22, now nearest the adsorbed states' configuration
    assert co12["nearest_state"] == "OOH" and co12["end_to_state"]["OOH"] < 0.1 < co12["end_to_production"]
    assert built["moments"]["total_change_uB"] == 0.98
    assert value["potential_limiting_step"] == 1 and value["rise_mV"] == pytest.approx(-energy["difference_meV"])
    low, high = value["E_O_shift_window_eV"]
    assert low < 0 < high and value["eta_floor_V"] < value["eta_with_production_slab_V"] < value["eta_V"]
