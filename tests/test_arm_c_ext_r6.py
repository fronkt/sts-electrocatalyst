"""Offline checks for round 6 of the S8 arm-C extension (second starts of the slab and the OH at Ni31 s1/0 and Cu26
s1/0, each from its own converged density with Cr 19's Hubbard occupations and PAW block from the other state, the
occupations held for the first 5 iterations), for the screen that selected them and for the readout's second-start
rule applied to an OH; never launch QE/Slurm or open a network connection. The stacked readout with round 6 as its
last layer needs the local projection outputs of the earlier layers and skips without them."""
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
import arm_c_ext_r6_build as r6  # noqa: E402
import arm_c_readout as readout  # noqa: E402
import hea_panel_readout as hpr  # noqa: E402
import research_batch_seeded as runner  # noqa: E402

PACKAGE = ROOT / r6.PACKAGE
SPEC = json.loads((PACKAGE / "launch_spec.json").read_text(encoding="utf-8"))
PLAN = json.loads((PACKAGE / "ext_plan.json").read_text(encoding="utf-8"))
R5_SPEC = json.loads((ROOT / r6.R5_SPEC).read_text(encoding="utf-8"))
R5_READOUT = json.loads((ROOT / r6.R5_READOUT).read_text(encoding="utf-8"))
PINS = json.loads((ROOT / r6.START_SOURCES).read_text(encoding="utf-8"))
JOBS = [job for stage in SPEC["stages"].values() for job in stage["jobs"]]
ROWS = PLAN["selection"]
SITES = ("Ni31Cr29Cu5Mn35__s1_site0", "Cu26Ni9Cr31Co33__s1_site0")
SLURM = ROOT / "anvil/101_arm_c_ext_r6.slurm"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(name):
    spec = importlib.util.spec_from_file_location("arm_c_ext_r6_" + Path(name).stem, PACKAGE / name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # the network parts run only under __main__
    return module


def blocks(path, size=r1.NS_BLOCK):
    values = r1.numbers(Path(path).read_text(encoding="ascii"))
    assert len(values) % size == 0
    return [values[k:k + size] for k in range(0, len(values), size)]


def site_row(name, readout_json=R5_READOUT):
    return next(s for s in readout_json["sites"] if r1.site_name(s["dir"]) == name)


# ---------------------------------------------------------------- the screen
def test_the_screen_covers_every_value_site_and_selects_only_cr19_at_the_two_s1_0_sites():
    screened = PLAN["screen"]["sites"]
    values = {(a, s["site"]) for a, alloy in R5_READOUT["alloys"].items() for s in alloy["supports"]
              if s["eta_dft_V"] is not None}
    assert len(screened) == len(values) == 6
    assert {(site_row(n)["formula"], f"s{site_row(n)['seed']}/{site_row(n)['site_index']}") for n in screened} == values
    selected = {n: [(r["atom"], r["species"]) for r in s["selected"]] for n, s in screened.items()}
    assert selected == {n: ([(19, "Cr")] if n in SITES else []) for n in screened}
    picked = [r["slab_to_OH"] for s in screened.values() for r in s["selected"]]
    passed_over = [s["largest_unselected"]["slab_to_OH"] for s in screened.values()]
    # any threshold in the gap selects the same atoms
    assert max(passed_over) < 0.17 < 0.2 < 0.28 < min(picked)
    for name, s in screened.items():
        assert s["potential_limiting_step"] == 1 and s["bonded"]["distance_to_O1_A"] < 1.9
        assert s["largest_unselected"]["distance_to_O1_A"] > 3.0
        assert max(s["printed_final_max_difference"].values()) <= r6.PRINT_TOLERANCE
    assert [(r["atom"], round(r["slab_to_OH"], 2), round(r["distance_to_O1_A"], 1)) for n in SITES
            for r in screened[n]["selected"]] == [(19, 0.41, 3.7), (19, 0.28, 3.7)]


def test_the_screen_reads_the_accepted_runs():
    for name, s in PLAN["screen"]["sites"].items():
        for state in r6.STATES:
            assert s["jobs"][state] == site_row(name)["states"][state]["job"]
    fe25 = PLAN["screen"]["sites"][r6.FE25]
    assert fe25["jobs"] == {"slab": "slab" + r5.JOB_SUFFIX, "OH": "OH__atomic_moved"}  # round 5's slab
    assert PLAN["screen"]["sites"]["Ni31Cr29Cu5Mn35__s10_site2"]["jobs"]["slab"] == "slab__atomic_ndim16"


# ---------------------------------------------------------------- the round-6 package
def test_build_reproduces_every_committed_file_byte_for_byte():
    built = r6.build()
    assert len(built) == 16  # 4 decks, 4 occup.txt, 4 paw.txt, 2 manifests, plan, spec
    for relative, data in built.items():
        assert (ROOT / relative).read_bytes() == data, relative
        assert b"\r" not in data


def test_the_transplant_reproduces_rounds_4_and_5_byte_for_byte():
    r5_row = json.loads((ROOT / r5.PACKAGE / "ext_plan.json").read_text(encoding="utf-8"))["selection"][0]
    start, source = (ROOT / r5_row["occupations"]["start"]).read_bytes(), (ROOT / r5_row["occupations"]["from"]["path"]).read_bytes()
    assert r6.occupations(start, source, 72, 22) == (ROOT / r5_row["bundle"] / "occup.txt").read_bytes()
    paw_start, paw_source = (ROOT / r5_row["paw"]["start"]).read_bytes(), (ROOT / r5_row["paw"]["from"]["path"]).read_bytes()
    assert r6.paw(paw_start, paw_source, 72, 74, 22) == (ROOT / r5_row["bundle"] / "paw.txt").read_bytes()
    r4_row = json.loads((ROOT / r4.PACKAGE / "ext_plan.json").read_text(encoding="utf-8"))["selection"][0]
    bundle = ROOT / r4_row["bundle"]
    assert r6.occupations((ROOT / r4_row["occupations"]["start"]).read_bytes(),
                          (ROOT / r4_row["occupations"]["from"]["path"]).read_bytes(), 73, 22) == (bundle / "occup.txt").read_bytes()
    assert r6.paw((ROOT / r4_row["paw"]["start"]).read_bytes(), (ROOT / r4_row["paw"]["from"]["path"]).read_bytes(),
                  73, 74, 22) == (bundle / "paw.txt").read_bytes()


def test_each_deck_is_production_s_with_round_5_s_changes_and_a_shorter_qe_stop():
    assert [(r["site_dir"].rsplit("/", 1)[1], r["state"], r["job"]) for r in ROWS] == [
        (SITES[0], "slab", "slab__atomic_cr19oh_fixns5"), (SITES[0], "OH", "OH__atomic_cr19slab_fixns5"),
        (SITES[1], "slab", "slab__atomic_cr19oh_fixns5"), (SITES[1], "OH", "OH__atomic_cr19slab_fixns5")]
    added = ["  mixing_ndim = 16", "  mixing_fixed_ns = 5", "  startingpot = 'file'"]
    for job, row in zip(JOBS, ROWS, strict=True):
        new = (ROOT / f"runs/{job['dir']}/{job['job']}.in").read_text(encoding="utf-8").split("\n")
        old = (ROOT / job["source_deck"]).read_text(encoding="utf-8").split("\n")
        assert job["source_deck"] == f"runs/{row['site_dir']}/{row['state']}__atomic.in"
        assert len(new) == len(old) + 3 and all(new.count(line) == 1 for line in added)
        rest = [line for line in new if line not in added]
        stop = r6.QE_MAX_SECONDS[row["stage"]]
        assert stop == row["qe_max_seconds"] == {"r6_ni31": 4900, "r6_cu26": 8500}[row["stage"]]
        assert [(a, b) for a, b in zip(old, rest) if a != b] == [
            (f"  prefix = '{row['state']}__atomic'", f"  prefix = '{job['job']}'"),
            ("  max_seconds = 165000", f"  max_seconds = {stop}")]
        # round 5's deck for this state, but for QE's own stop
        assert r6.r6_deck("\n".join(old), job["job"], stop) == r5.r5_deck("\n".join(old), job["job"]).replace(
            "  max_seconds = 18400", f"  max_seconds = {stop}")


def test_each_bundle_is_its_own_save_with_cr19_from_the_other_state():
    for job, row in zip(JOBS, ROWS, strict=True):
        other = "OH" if row["state"] == "slab" else "slab"
        nat, nat_other = r1.nat_of(row["state"]), r1.nat_of(other)
        built = blocks(ROOT / row["bundle"] / "occup.txt")
        start, source = blocks(ROOT / row["occupations"]["start"]), blocks(ROOT / row["occupations"]["from"]["path"])
        assert len(built) == len(start) == nat and len(source) == nat_other
        assert [k + 1 for k in range(nat) if built[k] != start[k]] == [19] and built[18] == source[18]
        bec = r1.numbers((ROOT / row["bundle"] / "paw.txt").read_text(encoding="ascii"))
        bec_start = r1.numbers((ROOT / row["paw"]["start"]).read_text(encoding="ascii"))
        bec_source = r1.numbers((ROOT / row["paw"]["from"]["path"]).read_text(encoding="ascii"))
        b = r1.BEC_BLOCK
        assert sorted({(k // b) % nat + 1 for k in range(len(bec)) if bec[k] != bec_start[k]}) == [19]
        for spin in range(2):
            lo, src = b * (spin * nat + 18), b * (spin * nat_other + 18)
            assert bec[lo:lo + b] == bec_source[src:src + b] != bec_start[lo:lo + b]
        assert row["occupations"]["from"]["state"] == row["paw"]["from"]["state"] == other
        assert row["occupations"]["atoms_replaced"] == row["paw"]["atoms_replaced"] == [19]
        _, atoms = r1.geometry((ROOT / job["source_deck"]).read_text(encoding="utf-8"))
        assert atoms[18][0] == "Cr" and row["screen"]["species"] == "Cr" and row["screen"]["atom"] == 19
        files = job["scratch_source"]["files"]
        assert files["occup.txt"] == sha(ROOT / row["bundle"] / "occup.txt") == row["occupations"]["sha256"]
        assert files["paw.txt"] == sha(ROOT / row["bundle"] / "paw.txt") == row["paw"]["sha256"]


def test_each_start_is_the_accepted_run_s_own_save_pinned_on_anvil():
    assert PINS["all_match"] and len(PINS["saves"]) == 10
    for job, row in zip(JOBS, ROWS, strict=True):
        name = r1.site_name(row["site_dir"])
        own, src = PINS["saves"][f"{name}/{row['state']}"], PINS["saves"][f"{name}/{'OH' if row['state'] == 'slab' else 'slab'}"]
        receipt = json.loads((ROOT / "results/arm_c_2026-10-07/raw_mirror/runs" / row["site_dir"] /
                              (row["first"]["job"] + ".qc.json")).read_text(encoding="utf-8"))
        assert own["save"] == receipt["scratch_retained"] + "/" + row["first"]["job"] + ".save" == job["seed"]["save_dir"]
        assert own["layer"] == "production" and own["all_match"] and src["all_match"]
        for name_ in (r2.DENSITY, r2.XML):
            assert job["scratch_source"]["files"][name_] == own["files"][name_]["sha256"]
            assert row["remote_copy"][name_] == own["save"] + "/" + name_
        assert own["files"][r2.DENSITY]["bytes"] > 1e8 and row["seed_density"] == "own_converged"
        assert row["occupations"]["start_sha256"] == own["files"]["occup.txt"]["sha256"] == sha(ROOT / row["occupations"]["start"])
        assert row["paw"]["start_sha256"] == own["files"]["paw.txt"]["sha256"] == sha(ROOT / row["paw"]["start"])
        assert row["occupations"]["from"]["sha256"] == src["files"]["occup.txt"]["sha256"]
        assert (job["seed"]["state"], job["seed"]["job"], job["seed"]["recipe"], job["nk"], job["recipe"]) == (
            row["state"], row["state"] + "__atomic", "production", 8, "seeded")


def test_limits_follow_each_site_s_production_iterations_and_fit_the_campaign():
    walls = {"r6_ni31": (120, 5500, 4900), "r6_cu26": (180, 9100, 8500)}
    assert {s: v["concurrency"] for s, v in SPEC["stages"].items()} == {"r6_ni31": 2, "r6_cu26": 2}
    for stage, (minutes, scf, stop) in walls.items():
        assert SPEC["stages"][stage]["wall_minutes"] == minutes and r6.QE_MAX_SECONDS[stage] == stop
        for job in SPEC["stages"][stage]["jobs"]:
            assert (job["max_iterations"], job["scf_seconds"], job["projection_seconds"]) == (300, scf, 600)
            assert job["scf_seconds"] <= runner.SCF_SECONDS
            # rounds 3-5 left 600 s between QE's stop and the SCF wall, and 1,100 s of the job wall for the rest
            assert scf - stop == r3.LIMITS["r3_main"]["scf_seconds"] - r3.QE_MAX_SECONDS == 600
            assert minutes * 60 - job["scf_seconds"] - job["projection_seconds"] == 1100
            assert job["dir"].endswith({"r6_ni31": SITES[0], "r6_cu26": SITES[1]}[stage])
    # the production runs these restart took 38 and 38 iterations (Ni31 s1/0), 76 and 119 (Cu26 s1/0)
    for name, counts in ((SITES[0], (38, 38)), (SITES[1], (76, 119))):
        site = site_row(name)
        assert (site["states"]["slab"]["iterations"], site["states"]["OH"]["iterations"]) == counts
    allocation = SPEC["allocation"]
    assert allocation["stage_ceilings_cpu_su"] == {"r6_ni31": 512, "r6_cu26": 768} == {
        "r6_ni31": 2 * 120 * 128 // 60, "r6_cu26": 2 * 180 * 128 // 60}
    assert allocation["this_launch_ceiling_cpu_su"] == 1280
    # 22,179.7 before round 5 + round 5's sacct CPU time (484,608 core-seconds = 134.61 SU)
    assert allocation["spent_before_this_launch_cpu_su"] == 22314.3 == round(22179.7 + 484608 / 3600, 1)
    assert allocation["spent_before_this_launch_cpu_su"] + 1280 <= allocation["approved_campaign_ceiling_cpu_su"] == 23680
    for key in ("pseudo_md5", "qe_binaries_sha256", "exclusions"):
        assert SPEC[key] == R5_SPEC[key]
    for relative in r1.RUNNER_FILES:
        assert SPEC["files"][relative] == R5_SPEC["files"][relative]
    for relative, pin in SPEC["files"].items():
        assert sha(ROOT / relative) == pin, relative


def test_plan_marks_second_starts_of_the_accepted_slab_and_oh():
    assert PLAN["round"] == 6 and PLAN["mixing"] == {"mixing_beta": 0.3, "mixing_ndim": 16, "mixing_fixed_ns": 5}
    assert PLAN["source_readout"] == SPEC["source_readout"] and PLAN["source_readout"]["sha256"] == sha(ROOT / r6.R5_READOUT)
    assert PLAN["round_5"]["spec_sha256"] == sha(ROOT / r6.R5_SPEC)
    for row in ROWS:
        first = site_row(r1.site_name(row["site_dir"]))["states"][row["state"]]
        assert row["second_start"] and row["round"] == 6 and first["accepted"]
        assert row["first"] == {"job": first["job"], "recipe": "production", "E_eV": first["E_eV"],
                                "total_magnetization": first["total_magnetization"]}
        assert row["screen"]["half_way"] == round(row["screen"]["slab_to_OH"] / 2, 4)
        assert row["stage"] == r6.STAGES[r1.site_name(row["site_dir"])]


def test_the_unchanged_runner_validates_the_stage(tmp_path):
    """The densities and XMLs live only on Anvil; stand-ins with their own pins exercise everything else."""
    for relative in SPEC["files"]:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    spec = json.loads(json.dumps(SPEC))
    for stage in spec["stages"].values():
        for job in stage["jobs"]:
            source = job["scratch_source"]
            for name in (r2.DENSITY, r2.XML):
                stand_in = tmp_path / source["save_dir"] / name
                stand_in.write_bytes(b"stand-in for " + source["save_dir"].encode() + name.encode())
                source["files"][name] = sha(stand_in)
    for stage, name in (("r6_ni31", SITES[0]), ("r6_cu26", SITES[1])):
        group = runner.validate(spec, tmp_path, stage)
        assert [(j["dir"].rsplit("/", 1)[1], j["job"]) for j in group["jobs"]] == [
            (name, "slab__atomic_cr19oh_fixns5"), (name, "OH__atomic_cr19slab_fixns5")]
    drifted = spec["stages"]["r6_cu26"]["jobs"][1]["scratch_source"]["save_dir"]
    (tmp_path / drifted / r2.XML).write_bytes(b"drifted stand-in")
    with pytest.raises(ValueError, match="drifted: " + r2.XML):
        runner.validate(spec, tmp_path, "r6_cu26")


def test_slurm_script_pins_the_spec_and_runner_and_keeps_round_5_resources():
    text = SLURM.read_text(encoding="utf-8")
    assert "\r" not in text
    assert f'check_hash "$SPEC" {sha(PACKAGE / "launch_spec.json")}' in text
    assert f'check_hash "$RUNNER" {sha(ROOT / "src/dft/research_batch_seeded.py")}' in text
    assert "r6_ni31|r6_cu26) ;;" in text and 'ROOT="$PROJECT/sts_arm_c_ext_r6_2026-10-11"' in text
    old = (ROOT / "anvil/100_arm_c_ext_r5.slurm").read_text(encoding="utf-8")
    assert [l for l in text.split("\n") if l.startswith("#SBATCH") and "log" not in l] == [
        l for l in old.split("\n") if l.startswith("#SBATCH") and "log" not in l]
    assert text.split("export OMP_NUM_THREADS", 1)[1] == old.split("export OMP_NUM_THREADS", 1)[1]
    bash = shutil.which("bash")
    if bash:
        assert subprocess.run([bash, "-n", str(SLURM)]).returncode == 0


def test_ops_target_the_round_6_root_and_copy_each_run_s_own_save():
    module = load("launch_ops.py")
    assert module.REMOTE == "/anvil/projects/x-che260157/sts_arm_c_ext_r6_2026-10-11"
    assert module.SLURM_REL == "anvil/101_arm_c_ext_r6.slurm"
    assert {k: (v["array"], v["tasks"], v["throttle"], v["time"], v["minutes"]) for k, v in module.ARRAYS.items()} == {
        "r6_ni31": ("1-2%2", 2, "2", "02:00:00", 120), "r6_cu26": ("1-2%2", 2, "2", "03:00:00", 180)}
    assert module.RELEASE == {"ni31": "r6_ni31", "cu26": "r6_cu26"}
    for stage, shape in module.ARRAYS.items():
        assert shape["tasks"] == len(SPEC["stages"][stage]["jobs"])
        assert shape["minutes"] == SPEC["stages"][stage]["wall_minutes"]
        assert shape["tasks"] * shape["minutes"] * 128 // 60 == SPEC["allocation"]["stage_ceilings_cpu_su"][stage]
    copies = module.seed_copies()
    assert len(copies) == 8
    for row in ROWS:
        own = PINS["saves"][f"{r1.site_name(row['site_dir'])}/{row['state']}"]
        for name in (r2.DENSITY, r2.XML):
            assert (own["save"] + "/" + name, module.REMOTE + "/" + row["bundle"] + "/" + name,
                    own["files"][name]["sha256"]) in copies
        for name in ("occup.txt", "paw.txt"):
            assert row["bundle"] + "/" + name in module.STAGE
    old = (ROOT / r5.PACKAGE / "launch_ops.py").read_text(encoding="utf-8")
    new = (PACKAGE / "launch_ops.py").read_text(encoding="utf-8")
    assert old.split("def stage():", 1)[1].split("def validate():", 1)[0] == new.split("def stage():", 1)[1].split(
        "def validate():", 1)[0]
    r3_validate = (ROOT / r3.PACKAGE / "launch_ops.py").read_text(encoding="utf-8").split("def validate():", 1)[1]
    assert r3_validate.split("def release", 1)[0] in new  # round 3's check of a multi-task array
    for name in ("status_once.py", "collect_terminal.py", "start_check.py"):
        text = (PACKAGE / name).read_text(encoding="utf-8")
        assert '/anvil/projects/x-che260157/sts_arm_c_ext_r6_2026-10-11"' in text and "sts_arm_c_ext_r5" not in text


def test_the_start_check_reproduces_round_5_s_on_its_output_with_atom_22():
    module = load("start_check.py")
    r5_row = json.loads((ROOT / r5.PACKAGE / "ext_plan.json").read_text(encoding="utf-8"))["selection"][0]
    out = (ROOT / r5.PACKAGE / "raw_mirror/runs" / r5_row["dir"] / (r5_row["job"] + ".out")).read_text(errors="replace")
    result = module.check(out, (ROOT / r5_row["bundle"] / "occup.txt").read_text(encoding="ascii"), 22)
    receipt = json.loads((ROOT / r5.PACKAGE / "start_check_20261011T003235Z.json").read_text(encoding="utf-8"))["jobs"][0]
    assert result["match"] and result["max_difference"] == receipt["max_difference"]
    assert result["atom_matrix_max_difference"] == receipt["fe22_matrix_max_difference"]
    assert [round(x, 5) for x in result["atom_after_iteration_1"]] == receipt["fe22_after_iteration_1"]
    for row in ROWS:
        built = (ROOT / row["bundle"] / "occup.txt").read_text(encoding="ascii")
        source = blocks(ROOT / row["occupations"]["from"]["path"])[18]
        up, down = sum(source[k * 6] for k in range(5)), sum(source[25 + k * 6] for k in range(5))
        assert module.traces(built)[19] == pytest.approx((up, down, up + down), abs=1e-12)


# ---------------------------------------------------------------- the readout's second-start rule on an OH
RY = hpr.RY_EV


def write_fake(run_dir, job, energy_Ry=None, iterations=40):
    """A converged run, or (energy_Ry None) QE's own stop at max_seconds with its last density written."""
    run_dir.mkdir(parents=True, exist_ok=True)
    lines = ["     running on   128 processor cores", "     The initial density is read from file :"]
    if energy_Ry is not None:
        lines += [f"     convergence has been achieved in {iterations:3d} iterations",
                  f"!    total energy              =   {energy_Ry:.8f} Ry",
                  f"     Writing all to output data dir /x/{run_dir.name}/tmp_{job}/{job}.save/ :"]
    else:
        lines += ["     Maximum CPU time exceeded",
                  f"     Writing config to output data dir /x/{run_dir.name}/tmp_{job}/{job}.save/"]
    lines.append("   JOB DONE.")
    (run_dir / (job + ".out")).write_text("\n".join(lines) + "\n", encoding="utf-8")
    receipt = {"status": "REJECTED", "reason": "numerical failure marker"} if energy_Ry is None else {
        "status": "COMPLETE", "reason": None, "scf": {"energy_Ry": energy_Ry, "iterations": iterations}}
    (run_dir / (job + ".qc.json")).write_text(json.dumps(receipt), encoding="utf-8")


def fake_round_6(mirror, shifts_meV, iterations=30):
    """Round 6's runs at their first runs' readout energies plus a shift (meV); None is QE's own stop."""
    for row in ROWS:
        name = r1.site_name(row["site_dir"])
        if (name, row["state"]) in shifts_meV:
            shift = shifts_meV[(name, row["state"])]
            energy = None if shift is None else round((row["first"]["E_eV"] + shift / 1000) / RY, 8)
            write_fake(mirror / "runs" / row["dir"], row["job"], energy, iterations)


def second_starts(tmp_path, name, shifts_meV, iterations=30):
    """One value site with production runs at its readout energies and second starts of the given states."""
    site = site_row(name)
    production, extension = tmp_path / "production", tmp_path / "r6"
    for state in readout.STATES:
        write_fake(production / "runs" / site["dir"], state + "__atomic", round(site["states"][state]["E_eV"] / RY, 8))
    plan_site = {k: site[k] for k in ("formula", "seed", "site_index", "site_metal", "roles", "eta_mlip_V", "dir")}
    plan_site.update(dG_mlip_eV={"OH": 1.8, "O": 3.2, "OOH": 4.6},
                     states={s: {"job": s + "__atomic"} for s in readout.STATES})
    gas = {g: hpr.gas_references()[g]["E_eV"] for g in ("H2O", "H2")}
    fake_round_6(extension, {(name, state): shift for state, shift in shifts_meV.items()}, iterations)
    rows = {row["state"]: dict(row) for row in ROWS
            if r1.site_name(row["site_dir"]) == name and row["state"] in shifts_meV}
    return site, readout.site_result(plan_site, production, gas, {}, None, rows, extension)


@pytest.mark.parametrize("name", SITES)
def test_a_lower_oh_lowers_the_value_and_a_lower_slab_raises_it(tmp_path, name):
    site, base = second_starts(tmp_path / "none", name, {})
    assert base["eta_dft_V"] == pytest.approx(site["eta_dft_V"], abs=1e-6) and base["potential_limiting_step"] == 1
    _, oh = second_starts(tmp_path / "oh", name, {"OH": -50.0})
    attempt = oh["extension_attempts"][0]
    assert attempt["state"] == "OH" and attempt["lower"] and attempt["replaces"] == "OH__atomic"
    assert oh["eta_dft_V"] == pytest.approx(base["eta_dft_V"] - 0.050, abs=1e-6)
    assert oh["eta_dft_V_with_first"] == pytest.approx(base["eta_dft_V"], abs=1e-9)
    _, slab = second_starts(tmp_path / "slab", name, {"slab": -50.0})
    assert slab["eta_dft_V"] == pytest.approx(base["eta_dft_V"] + 0.050, abs=1e-6)
    _, both = second_starts(tmp_path / "both", name, {"slab": -30.0, "OH": -50.0})
    assert [a["lower"] for a in both["extension_attempts"]] == [True, True]
    assert both["eta_dft_V"] == pytest.approx(base["eta_dft_V"] - 0.020, abs=1e-6)  # dG1 moves by OH's minus slab's
    assert both["eta_dft_V_with_first"] == pytest.approx(base["eta_dft_V"], abs=1e-9)
    _, kept = second_starts(tmp_path / "kept", name, {"slab": +5.0, "OH": -0.5})
    assert not any(a["lower"] for a in kept["extension_attempts"]) and "eta_dft_V_with_first" not in kept
    assert kept["eta_dft_V"] == pytest.approx(base["eta_dft_V"], abs=1e-9)


@pytest.mark.parametrize("name", SITES)
def test_a_time_stop_or_a_held_oh_never_replaces_it(tmp_path, name):
    _, base = second_starts(tmp_path / "none", name, {})
    _, held = second_starts(tmp_path / "held", name, {"OH": -50.0}, iterations=4)  # converged while held
    attempt = held["extension_attempts"][0]
    assert (attempt["state"], attempt["accepted"], attempt["failure"], attempt["lower"]) == ("OH", False, "HELD", False)
    assert held["states"]["OH"]["job"] == "OH__atomic" and "eta_dft_V_with_first" not in held
    assert held["eta_dft_V"] == pytest.approx(base["eta_dft_V"], abs=1e-9)
    _, stopped = second_starts(tmp_path / "stopped", name, {"OH": None, "slab": None})
    for attempt in stopped["extension_attempts"]:
        assert (attempt["failure"], attempt["qe_stop"], attempt["config_written"], attempt["lower"]) == (
            "CEILING", "time", True, False)
        assert attempt["energy_vs_first_meV"] is None and attempt["replaces"] is None
    assert stopped["eta_dft_V"] == pytest.approx(base["eta_dft_V"], abs=1e-9)


def test_the_stacked_readout_takes_round_6_as_its_last_layer(tmp_path):
    packages = ("results/arm_c_2026-10-07", "results/arm_c_2026-10-07_rerun", r2.PACKAGE, r4.PACKAGE, r5.PACKAGE)
    if not all(any((ROOT / p / "raw_mirror").rglob("*.projwfc.out")) for p in packages):
        pytest.skip("projection outputs are kept local, outside git")
    mirror = tmp_path / "r6_mirror"
    fake_round_6(mirror, {(SITES[0], "slab"): -40.0, (SITES[0], "OH"): +3.0,
                          (SITES[1], "slab"): -0.4, (SITES[1], "OH"): -60.0})
    out = tmp_path / "readout.json"
    args = ["--plan", "results/arm_c_2026-10-07/site_plan.json", "--mirror", "results/arm_c_2026-10-07/raw_mirror",
            "--rerun-plan", "results/arm_c_2026-10-07_rerun/rerun_plan.json",
            "--rerun-mirror", "results/arm_c_2026-10-07_rerun/raw_mirror"]
    for package in (r2.PACKAGE, r3.PACKAGE, r4.PACKAGE, r5.PACKAGE):
        args += ["--ext-plan", package + "/ext_plan.json", "--ext-mirror", package + "/raw_mirror"]
    args += ["--ext-plan", r6.PACKAGE + "/ext_plan.json", "--ext-mirror", str(mirror), "--out", str(out)]
    readout.main([a if a.startswith(("--", str(tmp_path))) else str(ROOT / a) for a in args])
    stacked = json.loads(out.read_text(encoding="utf-8"))
    changed = [k for k, (now, then) in enumerate(zip(stacked["sites"], R5_READOUT["sites"], strict=True)) if now != then]
    assert [r1.site_name(stacked["sites"][k]["dir"]) for k in changed] == list(SITES)
    ni31, cu26 = (stacked["sites"][k] for k in changed)
    then = {r1.site_name(R5_READOUT["sites"][k]["dir"]): R5_READOUT["sites"][k] for k in changed}
    assert [(a["state"], a["lower"]) for a in ni31["extension_attempts"]] == [("slab", True), ("OH", False)]
    assert [(a["state"], a["lower"]) for a in cu26["extension_attempts"]] == [("slab", False), ("OH", True)]
    assert ni31["eta_dft_V"] == pytest.approx(then[SITES[0]]["eta_dft_V"] + 0.040, abs=1e-6)
    assert cu26["eta_dft_V"] == pytest.approx(then[SITES[1]]["eta_dft_V"] - 0.060, abs=1e-6)
    alloys, before = stacked["alloys"], R5_READOUT["alloys"]
    assert alloys["Ni31Cr29Cu5Mn35"]["C_V"] == pytest.approx(before["Ni31Cr29Cu5Mn35"]["C_V"] + 0.3 * 0.040, abs=1e-6)
    assert alloys["Cu26Ni9Cr31Co33"]["C_V"] == pytest.approx(before["Cu26Ni9Cr31Co33"]["C_V"] - 0.060, abs=1e-6)
    assert {k: v for k, v in alloys.items() if k not in ("Ni31Cr29Cu5Mn35", "Cu26Ni9Cr31Co33")} == {
        k: v for k, v in before.items() if k not in ("Ni31Cr29Cu5Mn35", "Cu26Ni9Cr31Co33")}  # Fe25 keeps round 5's slab
    assert stacked["counts"] == dict(R5_READOUT["counts"], ext_attempted=19, ext_accepted=9, ext_seed_read=19,
                                     ext_second_starts=5, ext_second_starts_used=3)
