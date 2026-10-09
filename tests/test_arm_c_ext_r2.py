"""Offline checks for round 2 of the S8 arm-C extension (seed densities moved onto the target's atoms) and
for the density-move module; never launch QE/Slurm or open a network connection. Checks that need the
fetched seed densities (about 1.4 GB, never in git) skip when they are absent."""
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import h5py
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/dft"))
import arm_c_ext_build as r1  # noqa: E402
import arm_c_ext_r2_build as r2  # noqa: E402
import arm_c_readout as readout  # noqa: E402
import hea_panel_readout as hpr  # noqa: E402
import qe_density_move as move  # noqa: E402

PACKAGE = ROOT / r2.PACKAGE
R1_PACKAGE = ROOT / r1.PACKAGE
SPEC = json.loads((PACKAGE / "launch_spec.json").read_text(encoding="utf-8"))
PLAN = json.loads((PACKAGE / "ext_plan.json").read_text(encoding="utf-8"))
R1_SPEC = json.loads((R1_PACKAGE / "launch_spec.json").read_text(encoding="utf-8"))
SLURM = ROOT / "anvil/97_arm_c_ext_r2.slurm"
MAIN = SPEC["stages"]["r2_main"]["jobs"]
CANARY = SPEC["stages"]["r2_canary"]["jobs"]
INPUTS = ROOT / r2.INPUTS
HAVE_INPUTS = INPUTS.is_dir()
needs_inputs = pytest.mark.skipif(not HAVE_INPUTS, reason="fetched seed densities absent (density_fetch.py)")


def sha(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


# ---------------------------------------------------------------- the density-move module
def test_simpson_is_qe_s_rule_and_exact_for_cubics():
    assert move.simpson_weights(5).tolist() == pytest.approx([1 / 3, 4 / 3, 2 / 3, 4 / 3, 1 / 3])
    x = np.linspace(0.0, 2.0, 21)
    assert np.sum(x ** 3 * (x[1] - x[0]) * move.simpson_weights(21)) == pytest.approx(4.0, abs=1e-12)
    with pytest.raises(ValueError):
        move.simpson_weights(4)


def test_msh_is_the_first_point_beyond_10_bohr_rounded_down_to_odd():
    assert move.msh(np.arange(21.0)) == 11          # first r > 10 is the 12th point -> 11
    assert move.msh(np.arange(21.0) * 10 / 11.5) == 13   # first r > 10 is the 13th point
    assert move.msh(np.linspace(0, 5, 9)) == 9      # no point beyond: the whole (odd) mesh


def test_form_factor_of_a_gaussian_matches_its_analytic_transform():
    alpha, z = 1.7, 6.0
    r = np.linspace(0.0, 12.0, 4801)
    upf = {"r": r, "rab": np.full_like(r, r[1] - r[0]),
           "rho_atom": 4 * np.pi * r ** 2 * z * (alpha / np.pi) ** 1.5 * np.exp(-alpha * r ** 2), "z_valence": z}
    q = np.array([0.0, 0.5, 2.0, 6.0])
    assert move.form_factor(upf, q) == pytest.approx(z * np.exp(-q ** 2 / (4 * alpha)), abs=1e-9)


def test_structure_factor_tables_equal_the_direct_sum():
    rng = np.random.default_rng(1)
    miller = rng.integers(-7, 8, size=(500, 3))
    positions = [rng.random(3) for _ in range(4)]
    direct = sum(np.exp(-2j * np.pi * miller @ f) for f in positions)
    assert np.allclose(move.structure_factor(miller, positions), direct, atol=1e-12)


def test_moving_onto_the_same_atoms_is_the_identity_and_an_added_atom_adds_its_charge():
    rng = np.random.default_rng(2)
    miller = np.vstack([[0, 0, 0], rng.integers(-5, 6, size=(300, 3))])
    factors = {"O": rng.random(len(miller)) + 1.0, "H": rng.random(len(miller))}
    seed = {"miller": miller, "rho": rng.standard_normal(len(miller)) + 1j * rng.standard_normal(len(miller))}
    atoms = [("O", rng.random(3)), ("H", rng.random(3))]
    assert np.allclose(move.moved_charge(seed, atoms, atoms, factors), seed["rho"], atol=1e-13)
    extra = ("O", rng.random(3))
    added = move.moved_charge(seed, atoms, atoms + [extra], factors)
    assert added[0] - seed["rho"][0] == pytest.approx(factors["O"][0])


def write_qe_layout(path, miller, rho, mag):
    with h5py.File(path, "w") as f:
        f.attrs.create("gamma_only", np.bytes_(b".FALSE."))
        f.attrs.create("ngm_g", np.int32(len(miller)))
        f.attrs.create("nspin", np.int32(2))
        ds = f.create_dataset("MillerIndices", data=miller.astype(np.int32))
        ds.attrs["bg1"] = np.array([1.0, 0, 0])
        f.create_dataset("rhodiff_g", data=mag.view(np.float64))
        f.create_dataset("rhotot_g", data=rho.view(np.float64))


def test_a_moved_file_differs_from_its_seed_only_in_the_rhotot_g_values(tmp_path):
    rng = np.random.default_rng(3)
    miller = np.vstack([[0, 0, 0], rng.integers(-4, 5, size=(99, 3))])
    rho = rng.standard_normal(100) + 1j * rng.standard_normal(100)
    mag = rng.standard_normal(100) + 1j * rng.standard_normal(100)
    seed = tmp_path / "seed.hdf5"
    write_qe_layout(seed, miller, rho, mag)
    new = rho * 1.5
    data = move.moved_file_bytes(seed, new)
    moved = tmp_path / "moved.hdf5"
    moved.write_bytes(data)
    read = move.read_density(moved)
    assert np.array_equal(read["rho"], new) and np.array_equal(read["mag"], mag) and np.array_equal(read["miller"], miller)
    raw = np.frombuffer(seed.read_bytes(), np.uint8)
    with h5py.File(seed, "r") as f:
        start, size = f["rhotot_g"].id.get_offset(), f["rhotot_g"].id.get_storage_size()
    changed = np.nonzero(np.frombuffer(data, np.uint8) != raw)[0]
    assert len(data) == len(raw) and changed.min() >= start and changed.max() < start + size
    assert move.moved_file_bytes(seed, new) == data
    with pytest.raises(ValueError):
        move.moved_file_bytes(seed, new[:-1])


def test_qe_density_distance_has_the_hartree_and_magnetization_terms():
    cell = np.diag([10.0, 10.0, 10.0])
    miller = np.array([[0, 0, 0], [1, 0, 0]])
    g2 = (2 * np.pi / 10.0) ** 2
    d_rho, d_mag = np.array([0.0, 0.01 + 0j]), np.array([0.02 + 0j, 0.0])
    expected = (2 * 4 * np.pi * 0.01 ** 2 / g2 + 2 * 4 * np.pi / (2 * np.pi) ** 2 * 0.02 ** 2) * 1000.0 * 0.5
    assert move.hartree_distance(d_rho, d_mag, miller, cell) == pytest.approx(expected)
    assert move.hartree_distance(np.zeros(2, complex), None, miller, cell) == 0.0


def test_upf_v1_and_v2_blocks_are_read(tmp_path):
    mesh = "\n".join("%.6E" % x for x in (0.0, 0.5, 1.0))
    v2 = tmp_path / "v2.UPF"
    v2.write_text(f'<UPF version="2.0.1"><PP_HEADER z_valence="6.0" /><PP_MESH><PP_R type="real" size="3">{mesh}</PP_R>'
                  f'<PP_RAB type="real" size="3">{mesh}</PP_RAB></PP_MESH><PP_RHOATOM size="3">{mesh}</PP_RHOATOM></UPF>')
    v1 = tmp_path / "v1.UPF"
    v1.write_text("<PP_HEADER>\n   14.00000000000    Z valence\n</PP_HEADER>\n<PP_MESH>\n<PP_R>\n" + mesh +
                  "\n</PP_R>\n<PP_RAB>\n" + mesh + "\n</PP_RAB>\n</PP_MESH>\n<PP_RHOATOM>\n" + mesh + "\n</PP_RHOATOM>\n")
    assert move.read_upf(v2)["z_valence"] == 6.0 and move.read_upf(v1)["z_valence"] == 14.0
    assert move.read_upf(v1)["rho_atom"].tolist() == [0.0, 0.5, 1.0]


@needs_inputs
def test_atomic_charges_reproduce_qe_s_printed_starting_charge():
    for site in ("Cu8Cr23Mn35Co34__s20_site2", "Fe25Co25Ni25Cr25__s25_site2"):
        for state in ("slab", "O", "OH", "OOH"):
            deck = (ROOT / f"runs/hea/arm_c_2026-10-07/{site}/{state}__atomic.in").read_text()
            files = r2.species_files(deck)
            charge = {s: move.form_factor(move.read_upf(INPUTS / "pseudo" / u), np.array([0.0]))[0] for s, u in files.items()}
            out = (ROOT / f"results/arm_c_2026-10-07/raw_mirror/runs/hea/arm_c_2026-10-07/{site}/{state}__atomic.out").read_text(errors="replace")
            printed = float(re.search(r"starting charge\s+([0-9.]+)", out).group(1))
            assert sum(charge[s] for s, _ in r1.geometry(deck)[1]) == pytest.approx(printed, abs=5e-5)


# ---------------------------------------------------------------- the round-2 package
def test_build_reproduces_every_committed_file_byte_for_byte():
    built = r2.build(densities=False)
    assert len(built) == 39  # 11 + 2 decks, 22 seed files, 2 manifests, plan, spec
    for relative, data in built.items():
        assert (ROOT / relative).read_bytes() == data, relative
        assert b"\r" not in data


@needs_inputs
def test_local_moved_densities_match_their_pins_and_one_rebuilds_byte_for_byte():
    for job in MAIN:
        path = ROOT / job["scratch_source"]["save_dir"] / r2.DENSITY
        assert sha(path) == job["scratch_source"]["files"][r2.DENSITY]
    row = next(r for r in r1.targets(json.loads((ROOT / r1.READOUT).read_text(encoding="utf-8")))
               if r["site_dir"].endswith("Fe25Co25Ni25Cr25__s13_site0") and r["state"] == "OOH")
    fetch = json.loads((ROOT / r1.FETCH).read_text(encoding="utf-8"))["seeds"][row["seed"]["id"]]
    deck = (ROOT / f"runs/{row['site_dir']}/OOH__atomic.in").read_text()
    data, record = r2.moved_density(ROOT, row, deck, fetch, R1_SPEC, {})
    job = next(j for j in MAIN if j["dir"].endswith("Fe25Co25Ni25Cr25__s13_site0") and j["job"] == "OOH__atomic_moved")
    assert record["sha256"] == job["scratch_source"]["files"][r2.DENSITY] == hashlib.sha256(data).hexdigest()
    assert record["electrons"] == pytest.approx(691.0, abs=1e-3) and record["seed_electrons"] == pytest.approx(678.0)


def test_only_the_density_and_the_job_name_differ_from_round_1():
    r1_jobs = {(j["dir"].rsplit("/", 1)[-1], j["job"].replace(r1.JOB_SUFFIX, "")): j for j in R1_SPEC["stages"]["ext_main"]["jobs"]}
    assert len(MAIN) == len(r1_jobs) == 11
    for job in MAIN:
        old = r1_jobs[(job["dir"].rsplit("/", 1)[-1], job["job"].replace(r2.JOB_SUFFIX, ""))]
        new_deck = (ROOT / f"runs/{job['dir']}/{job['job']}.in").read_text(encoding="utf-8").split("\n")
        old_deck = (ROOT / f"runs/{old['dir']}/{old['job']}.in").read_text(encoding="utf-8").split("\n")
        assert [(a, b) for a, b in zip(old_deck, new_deck) if a != b] == [
            (f"  prefix = '{old['job']}'", f"  prefix = '{job['job']}'")] and len(old_deck) == len(new_deck)
        for name in ("occup.txt", "paw.txt", "data-file-schema.xml"):
            assert job["scratch_source"]["files"][name] == old["scratch_source"]["files"][name]
        for name in ("occup.txt", "paw.txt"):
            assert (ROOT / job["scratch_source"]["save_dir"] / name).read_bytes() == (
                ROOT / old["scratch_source"]["save_dir"] / name).read_bytes()
        assert job["scratch_source"]["files"][r2.DENSITY] != old["scratch_source"]["files"][r2.DENSITY]
        assert (job["source_deck"], job["seed"], job["nk"]) == (old["source_deck"], old["seed"], old["nk"])
        assert (job["max_iterations"], job["scf_seconds"]) == (old["max_iterations"], old["scf_seconds"])


def test_spec_shape_ceilings_and_campaign():
    assert [(j["dir"].rsplit("/", 1)[-1], j["job"]) for j in CANARY] == [
        ("Cu8Cr23Mn35Co34__s16_site2", "slab__atomic_moved"), ("Fe25Co25Ni25Cr25__s13_site0", "OOH__atomic_moved")]
    assert all((j["max_iterations"], j["scf_seconds"]) == (8, 2400) for j in CANARY)
    assert all((j["max_iterations"], j["scf_seconds"]) == (200, 12600) for j in MAIN)
    allocation = SPEC["allocation"]
    assert allocation["stage_ceilings_cpu_su"] == {"r2_canary": 192, "r2_main": 5280}
    assert allocation["this_launch_ceiling_cpu_su"] == 5472
    assert allocation["spent_before_this_launch_cpu_su"] == 17471.8  # arm C 17,399.8 + round-1 canary 72.0
    assert allocation["spent_before_this_launch_cpu_su"] + 5472 <= allocation["approved_campaign_ceiling_cpu_su"] == 23680
    assert SPEC["pseudo_md5"] == R1_SPEC["pseudo_md5"] and SPEC["qe_binaries_sha256"] == R1_SPEC["qe_binaries_sha256"]
    assert SPEC["exclusions"] == R1_SPEC["exclusions"]
    for relative, pin in SPEC["files"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == pin, relative


def test_plan_records_the_move_for_every_target():
    assert len(PLAN["selection"]) == 11 and PLAN["round"] == 2
    assert PLAN["density_move"]["sha256"] == sha(ROOT / "src/dft/qe_density_move.py")
    for row in PLAN["selection"]:
        roles_seed, roles_target = r1.ROLES[row["seed"]["state"]], r1.ROLES[row["state"]]
        assert row["seed_density"] == "moved" and list(row["remote_copy"]) == ["data-file-schema.xml"]
        assert row["atoms_removed"] == [r for r in roles_seed if r not in roles_target]
        assert row["atoms_added"] == [r for r in roles_target if r not in roles_seed]
        density = row["density"]
        assert abs(density["electrons"] - density["target_valence_electrons"]) < 1e-3
        assert density["seed_density_sha256"] != density["sha256"]


def test_the_offline_validation_puts_every_moved_start_closest_to_the_converged_density():
    report = json.loads((PACKAGE / "density_validation.json").read_text(encoding="utf-8"))
    assert len(report["pairs"]) == 14 and report["independent_moved_distances"] == 7
    moved = {(p["site"], p["seed"], p["target"]): p["distance_Ry_moved"] for p in report["pairs"]}
    for (site, seed, target), value in moved.items():  # the moved residual only changes sign with direction
        assert moved[(site, target, seed)] == pytest.approx(value, rel=1e-9)
    for pair in report["pairs"]:
        assert pair["distance_Ry_moved"] < 1.0 < pair["distance_Ry_atomic"] < pair["distance_Ry_copied"]
        assert abs(pair["moved_electrons"] - pair["target_electrons"]) < 1e-3
    for key, state in report["states"].items():
        assert state["density_electrons"] == pytest.approx(state["electrons_valence"], abs=1e-6)
        assert state["positions_vs_xml_max_frac"] < 1e-9 and state["species_match_xml"]
        assert state["density_moment"] == pytest.approx(state["run_last_total_magnetization"], abs=0.006)
    assert "arm_c_2026-10-07_rerun" in report["states"]["Fe25Co25Ni25Cr25__s25_site2/OOH"]["run_output"]


def load_canary_check():
    spec = importlib.util.spec_from_file_location("arm_c_ext_r2_canary_check", PACKAGE / "canary_check.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # the network part runs only under __main__
    return module


def test_the_canary_gate_needs_the_moved_density_read_as_built():
    module = load_canary_check()
    text = ("     The initial density is read from file :\n     /x/slab__atomic_moved.save/charge-density\n\n"
            "     negative rho (up, down):  7.515E-02 3.168E-01\n"
            "     iteration #  1     ecut=    80.00 Ry     beta= 0.30\n     estimated scf accuracy    <       3.00000000 Ry\n"
            "     iteration #  2     ecut=    80.00 Ry     beta= 0.30\n     estimated scf accuracy    <       1.00000000 Ry\n"
            "     iteration #  3     ecut=    80.00 Ry     beta= 0.30\n     estimated scf accuracy    <       0.50000000 Ry\n"
            "     negative rho (up, down):  9.000E-01 9.000E-01\n   JOB DONE.\n")
    seeded = module.summarize(text)
    assert seeded["start_negative_rho"] == [7.515e-2, 3.168e-1] and not seeded["renormalised"] and seeded["graceful_stop"]
    production = {"accuracy_Ry": [460.2, 213.9, 88.3]}
    ceiling = {"status": "REJECTED", "reason": "SCF iteration ceiling"}
    expected = [0.075152, 0.316813]
    assert module.judge(seeded, production, ceiling, expected)
    assert not module.judge(seeded, production, ceiling, [0.0040, 0.0226])          # a different file was read
    assert not module.judge(seeded, production, ceiling, None)
    rescaled = module.summarize(text.replace("\n\n     negative", "\n     starting charge 656.0000, renormalised to 650.0000\n     negative"))
    assert rescaled["renormalised"] and not module.judge(rescaled, production, ceiling, expected)
    killed = module.summarize(text.replace("   JOB DONE.\n", ""))
    assert not killed["graceful_stop"] and module.judge(killed, production, ceiling, expected)  # recorded, not gated


def test_canary_expectations_cover_every_moved_density_and_reproduce_round_1_s_printout():
    report = json.loads((PACKAGE / "canary_expectations.json").read_text(encoding="utf-8"))
    pins = {j["job"] + "@" + j["dir"].rsplit("/", 1)[-1]: j["scratch_source"]["files"][r2.DENSITY] for j in MAIN}
    assert {k: v["density_sha256"] for k, v in report["targets"].items()} == pins
    module = load_canary_check()
    assert [module.expected_start(j) for j in CANARY] == [
        [report["targets"]["slab__atomic_moved@Cu8Cr23Mn35Co34__s16_site2"]["negative_rho_up"],
         report["targets"]["slab__atomic_moved@Cu8Cr23Mn35Co34__s16_site2"]["negative_rho_down"]],
        [report["targets"]["OOH__atomic_moved@Fe25Co25Ni25Cr25__s13_site0"]["negative_rho_up"],
         report["targets"]["OOH__atomic_moved@Fe25Co25Ni25Cr25__s13_site0"]["negative_rho_down"]]]
    # the same FFT, rescaled as QE did in round 1, gives what QE printed then for the copied seeds
    seeds = report["seeds"]
    cu8 = seeds["Cu8Cr23Mn35Co34__s16_site2__O__atomic_ndim16"]
    fe25 = seeds["Fe25Co25Ni25Cr25__s13_site0__slab__atomic_ndim16"]
    assert "%.3E %.3E" % (cu8["negative_rho_up"] * 650 / 656, cu8["negative_rho_down"] * 650 / 656) == "6.936E-03 2.243E-02"
    assert "%.3E %.3E" % (fe25["negative_rho_up"] * 691 / 678, fe25["negative_rho_down"] * 691 / 678) == "4.593E-03 2.202E-02"
    for row in PLAN["selection"]:
        assert report["targets"][row["job"] + "@" + row["dir"].rsplit("/", 1)[-1]]["fft_grid"] == seeds[row["seed"]["id"]]["fft_grid"]


def test_slurm_script_pins_the_spec_and_seeded_runner_and_keeps_round_1_resources():
    text = SLURM.read_text(encoding="utf-8")
    assert "\r" not in text
    assert f'check_hash "$SPEC" {sha(PACKAGE / "launch_spec.json")}' in text
    assert f'check_hash "$RUNNER" {sha(ROOT / "src/dft/research_batch_seeded.py")}' in text
    assert "r2_canary|r2_main) ;;" in text and 'ROOT="$PROJECT/sts_arm_c_ext_r2_2026-10-08"' in text
    old = (ROOT / "anvil/96_arm_c_ext.slurm").read_text(encoding="utf-8")
    assert [l for l in text.split("\n") if l.startswith("#SBATCH") and "log" not in l] == [
        l for l in old.split("\n") if l.startswith("#SBATCH") and "log" not in l]
    assert text.split("export OMP_NUM_THREADS", 1)[1] == old.split("export OMP_NUM_THREADS", 1)[1]
    bash = shutil.which("bash")
    if bash:
        assert subprocess.run([bash, "-n", str(SLURM)]).returncode == 0


def test_ops_target_the_round_2_root_upload_the_moved_densities_and_gate_main_on_the_canary():
    spec = importlib.util.spec_from_file_location("arm_c_ext_r2_launch_ops", PACKAGE / "launch_ops.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.REMOTE == "/anvil/projects/x-che260157/sts_arm_c_ext_r2_2026-10-08"
    assert module.SLURM_REL == "anvil/97_arm_c_ext_r2.slurm"
    assert {k: (v["array"], v["tasks"], v["time"], v["minutes"]) for k, v in module.ARRAYS.items()} == {
        "r2_canary": ("1-2%2", 2, "00:45:00", 45), "r2_main": ("1-11%11", 11, "03:45:00", 225)}
    for name, shape in module.ARRAYS.items():
        assert shape["tasks"] * shape["minutes"] * 128 // 60 == SPEC["allocation"]["stage_ceilings_cpu_su"][name]
        assert shape["tasks"] == len(SPEC["stages"][name]["jobs"])
    copies, uploads = module.seed_copies(), module.uploads()
    assert len(copies) == 11 and all(t.endswith("/data-file-schema.xml") for _, t, _ in copies)
    assert len(uploads) == 11 and all(t.startswith(module.REMOTE + "/results/arm_c_ext_r2_2026-10-08/seeds/")
                                      and t.endswith("/charge-density.hdf5") for _, t, _ in uploads)
    pins = {j["scratch_source"]["save_dir"]: j["scratch_source"]["files"] for j in MAIN}
    assert {pin for _, _, pin in uploads} == {p["charge-density.hdf5"] for p in pins.values()}
    ops = (PACKAGE / "launch_ops.py").read_text(encoding="utf-8")
    assert "the canary has not passed" in ops and 'stage_name == "r2_main"' in ops
    assert '"--exclude=" + SPEC["exclusions"]' in ops and 'bad["ExcNodeList"]' in ops
    for name in ("status_once.py", "collect_terminal.py", "canary_check.py"):
        source = (PACKAGE / name).read_text(encoding="utf-8")
        assert "/anvil/projects/x-che260157/sts_arm_c_ext_r2_2026-10-08\"" in source
    assert 'SPEC["stages"]["r2_canary"]["jobs"]' in (PACKAGE / "canary_check.py").read_text(encoding="utf-8")


def write_fake(run_dir, job, energy_Ry=None, ceiling=False, seeded=False, iterations=40):
    """The QE output and runner receipt shapes of tests/test_arm_c_ext.py."""
    run_dir.mkdir(parents=True, exist_ok=True)
    lines = ["     running on   128 processor cores"]
    if seeded:
        lines.append("     The initial density is read from file :")
    if energy_Ry is not None:
        lines += [f"     convergence has been achieved in {iterations:3d} iterations",
                  f"!    total energy              =   {energy_Ry:.8f} Ry",
                  f"     Writing all to output data dir /x/{run_dir.name}/tmp_{job}/{job}.save/ :"]
    lines.append("   JOB DONE.")
    (run_dir / (job + ".out")).write_text("\n".join(lines) + "\n", encoding="utf-8")
    receipt = {"status": "REJECTED", "reason": "SCF iteration ceiling"} if ceiling else {
        "status": "COMPLETE", "reason": None, "scf": {"energy_Ry": energy_Ry, "iterations": 40}}
    (run_dir / (job + ".qc.json")).write_text(json.dumps(receipt), encoding="utf-8")
    if ceiling:
        (run_dir / (job + ".KILLED")).write_text("SCF iteration ceiling\n", encoding="utf-8")


def test_resuming_an_interrupted_stage_keeps_seals_replaces_and_refuses():
    spec = importlib.util.spec_from_file_location("arm_c_ext_r2_launch_ops_resume", PACKAGE / "launch_ops.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    pin = "a" * 64
    assert module.resume_action(None, pin) == "upload"
    assert module.resume_action((pin, "444"), pin) == "keep"
    assert module.resume_action((pin, "664"), pin) == "seal"
    assert module.resume_action(("b" * 64, "664"), pin) == "replace"  # the interrupted transfer
    with pytest.raises(SystemExit):
        module.resume_action(("b" * 64, "444"), pin)  # a sealed file never changes silently
    assert module.RESUME_BUDGET_SECONDS <= 300
    source = (PACKAGE / "launch_ops.py").read_text(encoding="utf-8")
    assert '"resume": resume' in source and 'raise SystemExit("staging already has a receipt")' in source


def test_the_readout_records_whether_the_seed_density_was_copied_or_moved(tmp_path):
    site_dir = "hea/arm_c_2026-10-07/Cu8Cr23Mn35Co34__s26_site1"
    ext_dir = r2.RUN_ROOT + "/Cu8Cr23Mn35Co34__s26_site1"
    production, extension = tmp_path / "production", tmp_path / "ext"
    energies = {"slab": -7872.00022049, "OH": -7914.75368997, "O": -7913.46937673, "OOH": -7956.25801633}
    for state, energy in energies.items():
        write_fake(production / "runs" / site_dir, state + "__atomic", None if state == "O" else energy, ceiling=state == "O")
    job = "O" + r2.JOB_SUFFIX
    write_fake(extension / "runs" / ext_dir, job, energies["O"], seeded=True, iterations=30)
    site = {"formula": "Cu8Cr23Mn35Co34", "seed": 26, "site_index": 1, "site_metal": "Cr",
            "roles": {"support_hi": {"weight": "1/2"}}, "eta_mlip_V": 0.386,
            "dG_mlip_eV": {"OH": 1.0, "O": 2.0, "OOH": 4.0}, "dir": site_dir,
            "states": {s: {"job": s + "__atomic"} for s in readout.STATES}}
    gas = {g: hpr.gas_references()[g]["E_eV"] for g in ("H2O", "H2")}
    row = {"site_dir": site_dir, "state": "O", "dir": ext_dir, "job": job, "seed": {"state": "OH", "job": "OH__atomic"}}
    moved = readout.site_result(site, production, gas, {}, None, {"O": dict(row, seed_density="moved")}, extension)
    copied = readout.site_result(site, production, gas, {}, None, {"O": row}, extension)
    assert moved["complete"] and moved["extension_attempts"][0]["seed_density"] == "moved"
    assert copied["extension_attempts"][0]["seed_density"] == "copied"


# ---------------------------------------------------------------- the round-2 terminal readout
def test_the_round_2_readout_reproduces_the_committed_readout(tmp_path):
    mirrors = (ROOT / "results/arm_c_2026-10-07/raw_mirror", ROOT / "results/arm_c_2026-10-07_rerun/raw_mirror",
               PACKAGE / "raw_mirror")
    if not all(any(m.rglob("*.projwfc.out")) for m in mirrors):
        pytest.skip("projection outputs are kept local, outside git")
    out = tmp_path / "readout.json"
    readout.main(["--plan", str(ROOT / "results/arm_c_2026-10-07/site_plan.json"), "--mirror", str(mirrors[0]),
                  "--rerun-plan", str(ROOT / "results/arm_c_2026-10-07_rerun/rerun_plan.json"),
                  "--rerun-mirror", str(mirrors[1]), "--ext-plan", str(PACKAGE / "ext_plan.json"),
                  "--ext-mirror", str(mirrors[2]), "--out", str(out)])
    assert out.read_bytes() == (PACKAGE / "readout.json").read_bytes()


def test_the_trajectory_comparison_reproduces_from_the_committed_mirrors():
    spec = importlib.util.spec_from_file_location("arm_c_ext_r2_trajectories", PACKAGE / "trajectories.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    built = module.build()
    assert json.dumps(built, indent=1) + "\n" == (PACKAGE / "trajectories.json").read_text(encoding="utf-8")
    ends = [t["round_2"]["end"] for t in built["targets"]]
    assert len(ends) == 11 and ends.count("converged") == 3
    assert all(e == "converged" or e == "killed: SCF iteration ceiling" for e in ends)
