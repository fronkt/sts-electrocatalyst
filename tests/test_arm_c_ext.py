"""Offline checks for the S8 arm-C extension (seeded SCFs at the Cu8 and Fe25 support sites); never
launch QE/Slurm or open a network connection."""
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
import arm_c_ext_build as ext  # noqa: E402
import arm_c_readout as readout  # noqa: E402
import hea_panel_readout as hpr  # noqa: E402
import research_batch_seeded as rbs  # noqa: E402

PACKAGE = ROOT / "results/arm_c_ext_2026-10-08"
SPEC = json.loads((PACKAGE / "launch_spec.json").read_text(encoding="utf-8"))
PLAN = json.loads((PACKAGE / "ext_plan.json").read_text(encoding="utf-8"))
FETCH = json.loads((PACKAGE / "seed_fetch.json").read_text(encoding="utf-8"))
SOURCE = json.loads((ROOT / "results/arm_c_2026-10-07_rerun/readout.json").read_text(encoding="utf-8"))
SOURCE_SPEC = json.loads((ROOT / "results/arm_c_2026-10-07/launch_spec.json").read_text(encoding="utf-8"))
SLURM = ROOT / "anvil/96_arm_c_ext.slurm"
MAIN = SPEC["stages"]["ext_main"]["jobs"]
CANARY = SPEC["stages"]["ext_canary"]["jobs"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def numbers(path):
    return [float(x) for x in Path(path).read_text(encoding="ascii").split()]


def test_build_reproduces_every_committed_file_byte_for_byte():
    built = ext.build()
    assert len(built) == 39  # 11 + 2 decks, 22 seed files, 2 manifests, plan, spec
    for relative, data in built.items():
        assert (ROOT / relative).read_bytes() == data, relative
        assert b"\r" not in data


def test_targets_are_every_failed_support_state_of_cu8_and_fe25_with_the_nearest_seed():
    failed = {(s["dir"].rsplit("/", 1)[-1], state) for s in SOURCE["sites"]
              if s["formula"] in ext.ALLOYS and {"support_lo", "support_hi"} & set(s["roles"])
              for state in s["failures"]}
    chosen = {(r["site_dir"].rsplit("/", 1)[-1], r["state"]): r for r in PLAN["selection"]}
    assert set(chosen) == failed and len(chosen) == 11
    expected_seed = {"Cu8Cr23Mn35Co34__s16_site2": "O", "Cu8Cr23Mn35Co34__s26_site1": "OH",
                     "Fe25Co25Ni25Cr25__s13_site0": "slab"}
    for (site, state), row in chosen.items():
        seed = row["seed"]["state"]
        if site in expected_seed:
            assert seed == expected_seed[site]
        else:  # Fe25 s25/2 has two accepted states: OH takes OOH (one atom away), O takes the slab
            assert seed == {"OH": "OOH", "O": "slab"}[state]
        assert row["job"] == state + "__atomic_seeded" and row["dir"] == ext.RUN_ROOT + "/" + site
        assert row["failure"] == "CEILING"
    assert PLAN["source_readout"] == SPEC["source_readout"]
    assert PLAN["source_readout"]["sha256"] == sha(ROOT / PLAN["source_readout"]["path"])


def test_decks_are_the_production_deck_with_its_prefix_and_one_added_line():
    for job in MAIN + CANARY:
        source = ROOT / job["source_deck"]
        assert sha(source) == SOURCE_SPEC["files"][job["source_deck"]]
        deck = ROOT / "runs" / job["dir"] / (job["job"] + ".in")
        assert sha(deck) == job["sha256"] == SPEC["files"]["runs/" + job["dir"] + "/" + job["job"] + ".in"]
        changed = sorted(d for d in difflib.ndiff(source.read_text(encoding="utf-8").split("\n"),
                                                  deck.read_text(encoding="utf-8").split("\n")) if d[:2] in ("- ", "+ "))
        assert changed == sorted(["-   prefix = '" + Path(job["source_deck"]).stem + "'",
                                  "+   prefix = '" + job["job"] + "'", "+   startingpot = 'file'"])
    for job in CANARY:
        twin = next(j for j in MAIN if j["job"] == job["job"] and j["dir"].endswith(job["dir"].rsplit("/", 1)[-1]))
        assert job["sha256"] == twin["sha256"] and job["scratch_source"] == twin["scratch_source"]


def test_rebuilt_seed_files_keep_the_seed_slab_blocks_and_match_the_target_layout():
    for row in PLAN["selection"]:
        bundle = ROOT / row["bundle"]
        nat, nat_seed = ext.nat_of(row["state"]), ext.nat_of(row["seed"]["state"])
        occ, paw = numbers(bundle / "occup.txt"), numbers(bundle / "paw.txt")
        seed = PACKAGE / "seed_files" / row["seed"]["id"]
        socc, spaw = numbers(seed / "occup.txt"), numbers(seed / "paw.txt")
        assert len(occ) == 50 * nat and len(paw) == 171 * nat * 2
        assert occ[:50 * 72] == socc[:50 * 72]
        for spin in range(2):
            for atom in range(72):
                assert paw[171 * (spin * nat + atom):171 * (spin * nat + atom + 1)] == \
                    spaw[171 * (spin * nat_seed + atom):171 * (spin * nat_seed + atom + 1)]
        assert not any(occ[50 * 72:])  # adsorbate atoms carry no Hubbard U
        for k, source in enumerate(row["atom_sources"]):
            blocks = [paw[171 * (spin * nat + 72 + k):171 * (spin * nat + 73 + k)] for spin in range(2)]
            if source["from"] == "zero":
                assert source["role"] == "H" and not any(blocks[0] + blocks[1])
            else:
                assert source["role"] in ("O1", "O2", "H") and any(blocks[0])
        reference = PACKAGE / "reference_files" / (row["site_dir"].rsplit("/", 1)[-1] + "__" + row["state"] + "__atomic_ndim16")
        if (reference / "paw.txt").exists():  # local layout references (not committed)
            rpaw, rocc = numbers(reference / "paw.txt"), numbers(reference / "occup.txt")
            assert len(rpaw) == len(paw) and len(rocc) == len(occ)
            zero = {72 + k for k, source in enumerate(row["atom_sources"]) if source["from"] == "zero"}

            def extents(values, atom):
                return [max((i for i, v in enumerate(values[171 * (s * nat + atom):171 * (s * nat + atom + 1)]) if v), default=-1)
                        for s in range(2)]
            for atom in range(nat):
                assert bool(any(occ[50 * atom:50 * atom + 50])) == bool(any(rocc[50 * atom:50 * atom + 50]))
                if atom not in zero:  # a new H starts at zero by design
                    assert extents(paw, atom) == extents(rpaw, atom), (row["bundle"], atom)


def test_atom_mapping_on_tagged_arrays():
    """Tag every seed block with its atom and spin and check where each target block comes from."""
    deck = (ROOT / "runs/hea/arm_c_2026-10-07/Fe25Co25Ni25Cr25__s13_site0/OOH__atomic.in").read_text(encoding="utf-8")
    sources = ext.atom_sources("OOH", "slab", deck)
    assert [label for _, label in sources[72:]][2] == "zero"
    assert all(label.startswith("nearest slab O") for _, label in sources[72:74])
    species = [s for s, _ in ext.geometry(deck)[1]]
    seed_ns = " ".join(("0" if species[a] == "O" else str(a + 1)) for a in range(72) for _ in range(50))
    seed_bec = " ".join(str(1000 * s + a + 1) for s in range(2) for a in range(72) for _ in range(171))
    built = ext.rebuilt_files(seed_ns, seed_bec, "slab", sources)
    bec = [float(x) for x in built["paw.txt"].decode().split()]
    for spin in range(2):
        for target, (source, _) in enumerate(sources):
            block = set(bec[171 * (spin * 75 + target):171 * (spin * 75 + target + 1)])
            assert block == ({0.0} if source is None else {float(1000 * spin + source + 1)})
    with pytest.raises(ValueError):
        ext.rebuilt_files(seed_ns, seed_bec, "O", sources)  # sizes must match the seed state


def test_spec_shape_ceilings_and_campaign():
    assert SPEC["schema"] == "research-batch-2026-09-16" and SPEC["np"] == 128
    for relative, digest in SPEC["files"].items():
        assert sha(ROOT / relative) == digest, relative
    for relative in ext.SHARED_HELPERS:
        assert SPEC["files"][relative] == SOURCE_SPEC["files"][relative]
    assert SPEC["files"]["src/dft/research_batch_seeded.py"] == sha(ROOT / "src/dft/research_batch_seeded.py")
    assert (len(CANARY), len(MAIN)) == (2, 11)
    for job in CANARY:
        assert (job["nk"], job["scf_seconds"], job["projection_seconds"], job["max_iterations"]) == (8, 1200, 600, 8)
    for job in MAIN:
        assert (job["nk"], job["scf_seconds"], job["projection_seconds"], job["max_iterations"]) == (8, 12600, 600, 200)
        files = job["scratch_source"]["files"]
        fetched = FETCH["seeds"][job["source_deck"].split("/")[3] + "__" + job["seed"]["job"]]["sha256"]
        assert {k: files[k] for k in ("charge-density.hdf5", "data-file-schema.xml")} == \
            {k: fetched[k] for k in ("charge-density.hdf5", "data-file-schema.xml")}
        for name in ("occup.txt", "paw.txt"):
            assert files[name] == sha(ROOT / job["scratch_source"]["save_dir"] / name)
    allocation = SPEC["allocation"]
    assert allocation["stage_ceilings_cpu_su"] == {"ext_canary": 2 * 25 * 128 // 60, "ext_main": 11 * 225 * 128 // 60}
    assert allocation["this_launch_ceiling_cpu_su"] == 106 + 5280 == 5386
    assert allocation["spent_before_this_launch_cpu_su"] == 17399.8
    assert (allocation["spent_before_this_launch_cpu_su"] + allocation["this_launch_ceiling_cpu_su"]
            <= allocation["approved_campaign_ceiling_cpu_su"] == 23680)
    assert SPEC["decision_ref"] == "Frank, 2026-10-08: \"Let's rerun DFT for those and get values for them.\""


def test_seeded_runner_accepts_both_stages_and_refuses_a_drifted_seed(tmp_path):
    spec = json.loads(json.dumps(SPEC))
    for relative in spec["files"]:
        (tmp_path / relative).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, tmp_path / relative)
    stand_in = {}
    for job in MAIN:
        bundle = tmp_path / job["scratch_source"]["save_dir"]
        for name in ("charge-density.hdf5", "data-file-schema.xml"):
            (bundle / name).write_bytes((job["job"] + name).encode())
            stand_in[(job["scratch_source"]["save_dir"], name)] = sha(bundle / name)
    for stage in spec["stages"].values():
        for job in stage["jobs"]:
            for name in ("charge-density.hdf5", "data-file-schema.xml"):
                job["scratch_source"]["files"][name] = stand_in[(job["scratch_source"]["save_dir"], name)]
    for stage in ("ext_canary", "ext_main"):
        assert rbs.validate(spec, tmp_path, stage)["kind"] == "hea"
    (tmp_path / MAIN[0]["scratch_source"]["save_dir"] / "occup.txt").write_text("0\n")
    with pytest.raises(ValueError, match="pinned file changed|scratch source file drifted"):
        rbs.validate(spec, tmp_path, "ext_main")


def test_slurm_script_pins_the_spec_and_seeded_runner_and_keeps_production_resources():
    text = SLURM.read_text(encoding="utf-8")
    assert "\r" not in text
    pins = re.findall(r'check_hash "\$(\w+)" ([0-9a-f]{64})', text)
    assert dict(pins) == {"SPEC": sha(PACKAGE / "launch_spec.json"), "RUNNER": sha(ROOT / "src/dft/research_batch_seeded.py")}
    assert 'case "${STAGE:-}" in ext_canary|ext_main)' in text
    assert text.count("/anvil/projects/x-che260157/sts_arm_c_ext_2026-10-08/logs/arm_c_ext_%A_%a.log") == 2
    production = (ROOT / "anvil/94_arm_c_batch.slurm").read_text(encoding="utf-8")

    def resources(t):
        return [line for line in t.splitlines() if line.startswith("#SBATCH") and "--output" not in line
                and "--error" not in line]
    assert resources(text) == resources(production)
    rerun = (ROOT / "anvil/95_arm_c_rerun.slurm").read_text(encoding="utf-8")
    assert text.split("export OMP_NUM_THREADS", 1)[1] == rerun.split("export OMP_NUM_THREADS", 1)[1]
    bash = shutil.which("bash")
    if bash:
        assert subprocess.run([bash, "-n", str(SLURM)]).returncode == 0


def test_ops_target_the_extension_root_and_gate_the_main_release_on_the_canary():
    spec = importlib.util.spec_from_file_location("arm_c_ext_launch_ops", PACKAGE / "launch_ops.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.REMOTE == "/anvil/projects/x-che260157/sts_arm_c_ext_2026-10-08"
    assert module.SLURM_REL == "anvil/96_arm_c_ext.slurm"
    assert {k: (v["array"], v["tasks"], v["time"], v["minutes"]) for k, v in module.ARRAYS.items()} == {
        "ext_canary": ("1-2%2", 2, "00:25:00", 25), "ext_main": ("1-11%11", 11, "03:45:00", 225)}
    for name, shape in module.ARRAYS.items():
        assert shape["tasks"] * shape["minutes"] * 128 // 60 == SPEC["allocation"]["stage_ceilings_cpu_su"][name]
        assert shape["tasks"] == len(SPEC["stages"][name]["jobs"])
    copies = module.seed_copies()
    assert len(copies) == 22 and all(target.startswith(module.REMOTE + "/results/arm_c_ext_2026-10-08/seeds/")
                                     for _, target, _ in copies)
    ops = (PACKAGE / "launch_ops.py").read_text(encoding="utf-8")
    assert "the canary has not passed" in ops
    assert '"--exclude=" + SPEC["exclusions"]' in ops and 'bad["ExcNodeList"]' in ops
    for name in ("status_once.py", "collect_terminal.py", "canary_check.py"):
        source = (PACKAGE / name).read_text(encoding="utf-8")
        assert "/anvil/projects/x-che260157/sts_arm_c_ext_2026-10-08\"" in source


def test_canary_summary_reads_the_seed_line_charge_and_accuracy():
    spec = importlib.util.spec_from_file_location("arm_c_ext_canary_check", PACKAGE / "canary_check.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # the network part runs only under __main__
    text = ("     The initial density is read from file :\n     /x/slab__atomic_seeded.save/charge-density\n"
            "     starting charge     691.99812, renormalised to     692.00000\n"
            "     iteration #  1     ecut=    80.00 Ry     beta= 0.30\n"
            "     estimated scf accuracy    <       1.23456789 Ry\n"
            "     iteration #  2     ecut=    80.00 Ry     beta= 0.30\n"
            "     estimated scf accuracy    <       0.12345678 Ry\n")
    summary = module.summarize(text)
    assert summary["density_read"] and summary["starting_charge"] == [691.99812, 692.0]
    assert summary["iterations"] == 2 and summary["accuracy_Ry"] == [1.23456789, 0.12345678] and not summary["errors"]
    assert module.summarize("Error in routine read_scf (1):\n")["errors"] == ["Error in routine"]
    assert module.summarize("Note: ... signalling: IEEE_INVALID_FLAG IEEE_DENORMAL\n")["ieee"] == ["IEEE_INVALID_FLAG"]
    assert module.summarize("Note: ... signalling: IEEE_UNDERFLOW_FLAG IEEE_DENORMAL\n")["ieee"] == []


def test_canary_gate_needs_the_seed_line_no_severe_note_and_a_lead_over_production():
    spec = importlib.util.spec_from_file_location("arm_c_ext_canary_gate", PACKAGE / "canary_check.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    production = {"accuracy_Ry": [460.2, 120.0, 60.0, 30.0, 20.0, 10.0, 6.0, 4.60]}
    good = {"density_read": True, "errors": [], "ieee": [], "iterations": 9,
            "accuracy_Ry": [3.0, 1.0, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01]}
    ceiling = {"status": "REJECTED", "reason": "SCF iteration ceiling"}
    assert module.judge(good, production, ceiling)
    assert module.judge(dict(good, accuracy_Ry=[3.0, 1.0, 0.5]), production, {"status": "COMPLETE"})
    assert not module.judge(dict(good, density_read=False), production, ceiling)
    assert not module.judge(dict(good, ieee=["IEEE_INVALID_FLAG"]), production, ceiling)
    assert not module.judge(dict(good, accuracy_Ry=good["accuracy_Ry"][:-1] + [5.0]), production, ceiling)
    assert not module.judge(good, production, {"status": "REJECTED", "reason": "numerical failure marker"})
    assert module.seed_output("/anvil/projects/x-che260157/sts_arm_c_2026-10-07_rerun/runs/hea/arm_c_2026-10-07_rerun/"
                              "Cu8Cr23Mn35Co34__s16_site2/tmp_O__atomic_ndim16/O__atomic_ndim16.save") == (
        ROOT / "results/arm_c_2026-10-07_rerun/raw_mirror/runs/hea/arm_c_2026-10-07_rerun/Cu8Cr23Mn35Co34__s16_site2/O__atomic_ndim16.out")
    for job in CANARY:
        assert module.seed_output(job["seed"]["save_dir"]).exists()


# ---------------------------------------------------------------- the readout's extension layer
ENERGIES_RY = {"slab": -7872.00022049, "OH": -7914.75368997, "O": -7913.46937673, "OOH": -7956.25801633}


def write_fake(run_dir, job, energy_Ry=None, ceiling=False, seeded=False, iterations=40):
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


def fake_site(tmp_path, seeded):
    site_dir = "hea/arm_c_2026-10-07/Cu8Cr23Mn35Co34__s26_site1"
    rerun_dir = readout.RERUN_ROOT + "/Cu8Cr23Mn35Co34__s26_site1"
    ext_dir = ext.RUN_ROOT + "/Cu8Cr23Mn35Co34__s26_site1"
    production, repeat, extension = tmp_path / "production", tmp_path / "rerun", tmp_path / "ext"
    for state, energy in ENERGIES_RY.items():
        write_fake(production / "runs" / site_dir, state + "__atomic", None if state == "O" else energy, ceiling=state == "O")
    write_fake(repeat / "runs" / rerun_dir, "O__atomic_ndim16", ceiling=True)
    write_fake(extension / "runs" / ext_dir, "O__atomic_seeded", ENERGIES_RY["O"], seeded=seeded, iterations=150)
    site = {"formula": "Cu8Cr23Mn35Co34", "seed": 26, "site_index": 1, "site_metal": "Cr",
            "roles": {"support_hi": {"weight": "1/2"}}, "eta_mlip_V": 0.386,
            "dG_mlip_eV": {"OH": 1.0, "O": 2.0, "OOH": 4.0}, "dir": site_dir,
            "states": {s: {"job": s + "__atomic"} for s in readout.STATES}}
    rerun_sub = {"O": {"site_dir": site_dir, "state": "O", "failure": "CEILING", "recipe": "ndim16",
                       "dir": rerun_dir, "job": "O__atomic_ndim16"}}
    ext_sub = {"O": {"site_dir": site_dir, "state": "O", "dir": ext_dir, "job": "O__atomic_seeded",
                     "seed": {"state": "OH", "job": "OH__atomic"}}}
    return site, production, repeat, extension, rerun_sub, ext_sub


def test_the_extension_completes_a_chain_after_a_failed_rerun_and_records_its_seed(tmp_path):
    site, production, repeat, extension, rerun_sub, ext_sub = fake_site(tmp_path, seeded=True)
    gas = {g: hpr.gas_references()[g]["E_eV"] for g in ("H2O", "H2")}
    before = readout.site_result(site, production, gas, rerun_sub, repeat)
    assert before["complete"] is False and "extension_attempts" not in before
    after = readout.site_result(site, production, gas, rerun_sub, repeat, ext_sub, extension)
    assert after["complete"] and after["recipes"] == ["production", "seeded"]
    attempt = after["extension_attempts"][0]
    assert (attempt["state"], attempt["accepted"], attempt["seed"], attempt["seed_read"]) == ("O", True, "OH__atomic", True)
    assert attempt["save_written"] and attempt["beyond_registered_cap"] and attempt["iterations"] == 150
    assert after["rerun_attempts"][0]["accepted"] is False and after["states"]["O"]["replaces"] == "O__atomic"


def test_an_unread_seed_is_labelled_as_a_fallback(tmp_path):
    site, production, repeat, extension, rerun_sub, ext_sub = fake_site(tmp_path, seeded=False)
    gas = {g: hpr.gas_references()[g]["E_eV"] for g in ("H2O", "H2")}
    after = readout.site_result(site, production, gas, rerun_sub, repeat, ext_sub, extension)
    assert after["complete"] and after["states"]["O"]["recipe"] == "unseeded_fallback"


def test_an_extension_readout_needs_the_rerun_layer_and_a_mirror(tmp_path):
    base = ["--plan", str(ROOT / "results/arm_c_2026-10-07/site_plan.json"),
            "--mirror", str(ROOT / "results/arm_c_2026-10-07/raw_mirror"), "--out", str(tmp_path / "out.json")]
    with pytest.raises(SystemExit):
        readout.main(base + ["--ext-plan", str(PACKAGE / "ext_plan.json"), "--ext-mirror", str(tmp_path)])
    with pytest.raises(SystemExit):
        readout.main(base + ["--rerun-plan", str(ROOT / "results/arm_c_2026-10-07_rerun/rerun_plan.json"),
                             "--rerun-mirror", str(ROOT / "results/arm_c_2026-10-07_rerun/raw_mirror"),
                             "--ext-plan", str(PACKAGE / "ext_plan.json"), "--ext-mirror", str(tmp_path / "absent")])
    assert not (tmp_path / "out.json").exists()
