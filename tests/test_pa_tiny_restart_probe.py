"""Pure safety and input-generation checks for the tiny QE restart probe."""

import os
import json
import unittest
from pathlib import Path
from types import SimpleNamespace

import pytest
from src.dft import pa_tiny_restart_probe as probe

from src.dft.pa_tiny_restart_probe import (
    H_UPF_NAME,
    H_UPF_SHA256,
    QE_SHA256,
    last_logged_h2_positions,
    ProbeError,
    input_text,
    nonzero_move_observed,
    parse_slurm_time,
    set_single_rank_environment,
    validate_allocation,
    validate_paths,
)


class ParseSlurmTimeTests(unittest.TestCase):
    def test_supported_formats(self):
        self.assertEqual(parse_slurm_time("120"), 7200)
        self.assertEqual(parse_slurm_time("120:00"), 7200)
        self.assertEqual(parse_slurm_time("02:00:00"), 7200)
        self.assertEqual(parse_slurm_time("1-02:00:00"), 93600)

    def test_rejects_bad_ranges_and_syntax(self):
        for value in ("1:60", "2:00:00:00", "abc", "-1:00:00"):
            with self.subTest(value=value), self.assertRaises(ProbeError):
                parse_slurm_time(value)


class AllocationTests(unittest.TestCase):
    def test_requires_four_cores_and_two_hour_limit(self):
        self.assertEqual(validate_allocation({
            "SLURM_CPUS_PER_TASK": "4", "SLURM_CPUS_ON_NODE": "4",
            "SLURM_NTASKS": "1", "SLURM_JOB_PARTITION": "shared",
            "SLURM_JOB_ACCOUNT": "che260157", "SLURM_JOB_ID": "12345",
            "SLURM_JOB_TIME_LIMIT": "02:00:00"
        }), (4, 7200))
        for env in (
            {},
            {"SLURM_CPUS_PER_TASK": "2", "SLURM_JOB_TIME_LIMIT": "02:00:00"},
            {"SLURM_CPUS_PER_TASK": "4", "SLURM_JOB_TIME_LIMIT": "02:00:01"},
        ):
            with self.subTest(env=env), self.assertRaises(ProbeError):
                validate_allocation(env)


class InputDeckTests(unittest.TestCase):
    def test_fixed_h2_settings_and_single_restart_toggle(self):
        base = input_text("h2_probe", Path("/work/scratch"), Path("/work/pseudo"), fresh=True)
        resumed = input_text("h2_probe", Path("/work/resume"), Path("/work/pseudo"), restart=True, nstep=29)
        for token in ("calculation = 'relax'", "ecutwfc = 40.0", "ecutrho = 320.0",
                      "conv_thr = 1.0d-10", "diago_thr_init = 1.0d-7",
                      "electron_maxstep = 100", "forc_conv_thr = 1.0d-4",
                      "nstep = 30", "disk_io = 'low'", "ion_dynamics = 'bfgs'",
                      "ATOMIC_POSITIONS bohr", "H 0.000000000000 0.000000000000 2.000000000000", "K_POINTS gamma",
                      "CELL_PARAMETERS bohr"):
            self.assertIn(token, base)
        self.assertIn("restart_mode = 'from_scratch'", base)
        self.assertIn("restart_mode = 'restart'", resumed)
        self.assertIn("nstep = 29", resumed)
        self.assertEqual(base.count("restart_mode"), 1)
        self.assertEqual(resumed.count("restart_mode"), 1)
        self.assertIn(H_UPF_NAME, base)

    def test_negative_control_uses_proposal_geometry_and_fresh_mode(self):
        geometry = ((0.0, 0.0, 0.1), (0.0, 0.0, 2.1))
        fresh = input_text("h2_probe", Path("/work/fresh"), Path("/work/pseudo"),
                           fresh=True, positions=geometry)
        self.assertIn("restart_mode = 'from_scratch'", fresh)
        self.assertIn("H 0.000000000000 0.000000000000 0.100000000000", fresh)
        self.assertIn("H 0.000000000000 0.000000000000 2.100000000000", fresh)


class TriggerTests(unittest.TestCase):
    def test_first_count0_is_the_source_supported_trigger(self):
        match = probe.first_bfgs_trigger("     number of bfgs steps = 0\n")
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "0")

    def test_later_counter_reset_cannot_supply_first_move_trigger(self):
        self.assertIsNone(probe.first_bfgs_trigger(
            "number of bfgs steps = 1\nnumber of bfgs steps = 0\n"))

    def test_wolfe_trust_marker_is_not_a_first_move_trigger(self):
        self.assertIsNone(probe.first_bfgs_trigger("new trust radius = 0.05\n"))

    def test_requires_a_nonzero_change_between_two_logged_positions(self):
        unchanged = """ATOMIC_POSITIONS (bohr)
H 0 0 0
H 0 0 2
ATOMIC_POSITIONS (bohr)
H 0 0 0
H 0 0 2
"""
        moved = """ATOMIC_POSITIONS (bohr)
H 0 0 0
H 0 0 2
ATOMIC_POSITIONS (bohr)
H 0 0 0.1
H 0 0 2.1
"""
        self.assertFalse(nonzero_move_observed(unchanged))
        self.assertFalse(nonzero_move_observed(moved.split("ATOMIC_POSITIONS")[0]))
        self.assertTrue(nonzero_move_observed(moved))
        self.assertEqual(last_logged_h2_positions(moved), ((0.0, 0.0, 0.1), (0.0, 0.0, 2.1)))


class EnvironmentTests(unittest.TestCase):
    def test_campaign_runtime_paths_are_identical_across_arms(self):
        binary = Path("/anvil/projects/x-che260157/qe/env/bin/pw.x")
        env = set_single_rank_environment(binary)
        self.assertEqual(env["PATH"].split(os.pathsep)[0], str(binary.parent))
        self.assertEqual(env["LD_LIBRARY_PATH"].split(os.pathsep)[0], str(binary.parent.parent / "lib"))

    def test_single_rank_thread_settings(self):
        env = set_single_rank_environment()
        for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                     "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
            self.assertEqual(env[name], "1")
        self.assertEqual(env["OMP_DYNAMIC"], "FALSE")

    def test_path_validation_requires_fresh_output_and_pinned_names(self):
        with self.assertRaises(ProbeError):
            validate_paths(Path.cwd(), Path(__file__), Path(__file__))
        self.assertEqual(len(QE_SHA256), 64)
        self.assertEqual(len(H_UPF_SHA256), 64)


if __name__ == "__main__":
    unittest.main()


SLURM = {"SLURM_CPUS_PER_TASK": "4", "SLURM_CPUS_ON_NODE": "4",
         "SLURM_NTASKS": "1", "SLURM_JOB_PARTITION": "shared",
         "SLURM_JOB_ACCOUNT": "che260157", "SLURM_JOB_ID": "12345",
         "SLURM_JOB_TIME_LIMIT": "02:00:00"}


def xml_checkpoint(status=255, steps=1):
    structure = ('<atomic_structure nat="2"><atomic_positions>'
                 '<atom name="H">0 0 0.1</atom><atom name="H">0 0 1.9</atom>'
                 '</atomic_positions></atomic_structure>')
    return ('<espresso Units="Hartree atomic units">' + ('<step>'+structure+'</step>')*steps +
            '<output><atomic_structure nat="2"><atomic_positions>'
            '<atom name="H">0 0 0.1</atom><atom name="H">0 0 1.9</atom>'
            '</atomic_positions></atomic_structure><atomic_species><species name="H">'
            f'<pseudo_file>{probe.H_UPF_NAME}</pseudo_file></species></atomic_species></output>'
            f'<exit_status>{status}</exit_status></espresso>')


def bfgs_checkpoint():
    values = [0.]*326
    values[32:35] = [1,1,0]
    return ' '.join(map(str,values)).encode()


@pytest.fixture
def fake_probe(tmp_path, monkeypatch):
    for k,v in SLURM.items(): monkeypatch.setenv(k,v)
    binary = tmp_path / "pw.x"
    binary.write_bytes(b"fixture binary; never executed")
    binary.chmod(0o755)
    pseudo = tmp_path / probe.H_UPF_NAME
    pseudo.write_bytes(b"fixture UPF; never used by QE")
    digest = probe.sha256_file
    monkeypatch.setattr(probe, "sha256_file", lambda p: probe.QE_SHA256 if p == binary else
                        probe.H_UPF_SHA256 if p.name == probe.H_UPF_NAME and p.read_bytes() == pseudo.read_bytes() else digest(p))
    monkeypatch.setattr(probe, "allocation_receipt", lambda job: {"fixture": True})
    args = SimpleNamespace(output_dir=tmp_path/"fresh_probe", qe_binary=binary,
                           pseudo=pseudo, expected_qe_sha256=probe.QE_SHA256,
                           expected_pseudo_sha256=probe.H_UPF_SHA256)
    calls = []
    def arm(name, argv, cwd, env, timeout, trigger_move=False):
        calls.append(name)
        assert timeout <= probe.MAX_ARM_SECONDS
        scratch = cwd / "scratch"
        scratch.mkdir(exist_ok=True)
        save = scratch / "h2_probe.save"
        save.mkdir(exist_ok=True)
        (save/probe.H_UPF_NAME).write_bytes(pseudo.read_bytes())
        log = "Program PWSCF v.7.5 starts\n"
        if name == "candidate-stop":
            (scratch/"h2_probe.bfgs").write_bytes(bfgs_checkpoint())
            (scratch/"h2_probe.update").write_bytes(b"retained sibling state")
            (save/"wfc1.dat").write_bytes(b"retained wavefunction")
            (save/"data-file-schema.xml").write_text(xml_checkpoint(),encoding="utf-8")
            log += "Program stopped by user request\n"
        elif name in ("negative-fresh", "resumed"):
            # Both receive the whole tree with sibling history, not a nested save.
            assert (scratch/"h2_probe.bfgs").read_bytes() == bfgs_checkpoint()
            assert (scratch/"h2_probe.update").read_bytes() == b"retained sibling state"
            assert (save/"wfc1.dat").read_bytes() == b"retained wavefunction"
            assert not (save/"h2_probe.save").exists()
            deck = (cwd/"input.in").read_text(encoding="utf-8")
            assert "H 0.000000000000 0.000000000000 0.100000000000" in deck
            if name == "negative-fresh":
                assert "restart_mode = 'from_scratch'" in deck
                (scratch/"h2_probe.bfgs").write_bytes(b"negative mutated only its own copy")
                log += "h2_probe.bfgs deleted, as requested\nnumber of bfgs steps = 0\n"
            else:
                assert "restart_mode = 'restart'" in deck and "nstep = 29" in deck
                log += "number of bfgs steps = 1\nnumber of scf cycles = 2\n"
            (save/"data-file-schema.xml").write_text(xml_checkpoint(0,3),encoding="utf-8")
            log += "bfgs converged in 3 steps\n"
        else:
            (save/"data-file-schema.xml").write_text(xml_checkpoint(0,3),encoding="utf-8")
            log += "bfgs converged in 3 steps\n"
        (cwd/"stdout.log").write_text(log+"JOB DONE.\n",encoding="utf-8")
        (cwd/"stderr.log").write_text("",encoding="utf-8")
        return {"arm": name, "returncode": 0, "timed_out": False,
                "move_trigger_observed": trigger_move, "elapsed_seconds": .01}
    monkeypatch.setattr(probe, "run_arm", arm)
    return args,calls,arm


def test_full_pipeline_doubles_preserve_sibling_history_and_separate_copies(fake_probe):
    args,calls,_ = fake_probe
    assert probe.run_probe(args) == 0
    assert calls == ["continuous", "candidate-stop", "negative-fresh", "resumed"]
    original = args.output_dir/"checkpoint-stopped/h2_probe.bfgs"
    assert original.read_bytes() == bfgs_checkpoint()
    report = json.loads((args.output_dir/"report.json").read_text(encoding="utf-8"))
    assert report["completed_moves_at_stop"] == 1 and report["resumed_nstep_budget"] == 29
    assert "manual review" in report["interpretation"]
    for name in calls:
        arm=args.output_dir/name
        assert f"pseudo_dir = '{arm.as_posix()}/'" in (arm/"input.in").read_text(encoding="utf-8")
        manifest=json.loads((arm/"input_manifest.json").read_text(encoding="utf-8"))
        assert manifest["upf_path"]==str(arm/probe.H_UPF_NAME)
        assert manifest["upf_sha256"]==probe.H_UPF_SHA256


def test_no_automatic_retry_if_clean_stop_boundary_is_missed(fake_probe,monkeypatch):
    args,calls,arm = fake_probe
    def missed(*a,**kw):
        r = arm(*a,**kw)
        if a[0] == "candidate-stop":
            p = a[2]/"scratch/h2_probe.save/data-file-schema.xml"
            p.write_text(xml_checkpoint(steps=2),encoding="utf-8")
        return r
    monkeypatch.setattr(probe,"run_arm",missed)
    with pytest.raises(probe.ProbeError,match="single-move"): probe.run_probe(args)
    assert calls == ["continuous", "candidate-stop"]


@pytest.mark.parametrize("bad", ["wholenode", "gpu"])
def test_actual_scheduler_partition_cannot_be_spoofed_by_env(monkeypatch,bad):
    text = (f"JobId=12345 Account=che260157 Partition={bad} JobState=RUNNING "
            "NumCPUs=4 NumTasks=1 CPUs/Task=4 TimeLimit=02:00:00 "
            "AllocTRES=cpu=4,mem=6G,node=1,billing=4")
    monkeypatch.setattr(probe.subprocess,"run",lambda *a,**kw: SimpleNamespace(stdout=text,stderr="",args=a[0]))
    with pytest.raises(probe.ProbeError,match="scheduler allocation"): probe.allocation_receipt("12345")


def test_actual_scheduler_billing_guard(monkeypatch):
    text = ("JobId=12345 Account=che260157 Partition=shared JobState=RUNNING "
            "NumCPUs=4 NumTasks=1 CPUs/Task=4 TimeLimit=02:00:00 "
            "AllocTRES=cpu=4,mem=6G,node=1,billing=128")
    monkeypatch.setattr(probe.subprocess,"run",lambda *a,**kw: SimpleNamespace(stdout=text,stderr="",args=a[0]))
    with pytest.raises(probe.ProbeError,match="billing"): probe.allocation_receipt("12345")


@pytest.mark.parametrize("mutation", [lambda t:t.replace("Hartree atomic units","unknown"),
    lambda t:t.replace('name="H"','name="He"'), lambda t:t.replace("0 0 1.9","nan 0 1.9"),
    lambda t:t.replace("<exit_status>255", "<exit_status>0")])
def test_saved_proposal_requires_units_identity_finite_and_interruption_status(tmp_path,mutation):
    d = tmp_path/"h2_probe.save"
    d.mkdir()
    (d/"data-file-schema.xml").write_text(mutation(xml_checkpoint()),encoding="utf-8")
    with pytest.raises(probe.ProbeError): probe.checkpoint_geometry(tmp_path)


@pytest.mark.parametrize("mutation", ["fallback","reset","timeout","no_job_done","failed_scf","wrong_geometry"])
def test_resumed_failure_never_completes_probe(fake_probe,monkeypatch,mutation):
    args,calls,arm = fake_probe
    def corrupt(*a,**kw):
        r = arm(*a,**kw)
        if a[0] == "resumed":
            log = a[2]/"stdout.log"
            text = log.read_text(encoding="utf-8")
            if mutation == "fallback": text += "restart disabled: needed files not found\n"
            elif mutation == "reset": text = text.replace("number of bfgs steps = 1", "number of bfgs steps = 0")
            elif mutation == "timeout": r["timed_out"] = True
            elif mutation == "no_job_done": text = text.replace("JOB DONE.", "")
            elif mutation == "failed_scf": text += "convergence NOT achieved\n"
            elif mutation == "wrong_geometry":
                p=a[2]/"scratch/h2_probe.save/data-file-schema.xml"
                p.write_text(xml_checkpoint(0,3).replace("0 0 0.1","0 0 0.5"),encoding="utf-8")
            log.write_text(text,encoding="utf-8")
        return r
    monkeypatch.setattr(probe,"run_arm",corrupt)
    with pytest.raises(probe.ProbeError): probe.run_probe(args)
    assert len(calls)==4
    assert not (args.output_dir/"report.json").exists()


@pytest.mark.parametrize("mutation", ["bad_upf","zero_move","wrong_counter","wrong_pseudo_name"])
def test_bad_checkpoint_blocks_both_copied_arms(fake_probe,monkeypatch,mutation):
    args,calls,arm = fake_probe
    def corrupt(*a,**kw):
        r=arm(*a,**kw)
        if a[0]=="candidate-stop":
            scratch=a[2]/"scratch"
            if mutation=="bad_upf": (scratch/"h2_probe.save"/probe.H_UPF_NAME).write_bytes(b"wrong checkpoint UPF")
            elif mutation=="zero_move":
                p=scratch/"h2_probe.save/data-file-schema.xml"
                p.write_text(xml_checkpoint().replace("0 0 0.1","0 0 0").replace("0 0 1.9","0 0 2"),encoding="utf-8")
            elif mutation=="wrong_counter":
                values=bfgs_checkpoint().decode().split();values[33]="0"
                (scratch/"h2_probe.bfgs").write_text(' '.join(values),encoding="utf-8")
            else:
                p=scratch/"h2_probe.save/data-file-schema.xml"
                p.write_text(xml_checkpoint().replace(probe.H_UPF_NAME,"wrong.UPF"),encoding="utf-8")
        return r
    monkeypatch.setattr(probe,"run_arm",corrupt)
    with pytest.raises(probe.ProbeError): probe.run_probe(args)
    assert calls == ["continuous","candidate-stop"]


def test_clean_stop_without_local_upf_uses_pinned_external_fallback(fake_probe,monkeypatch):
    args,calls,arm=fake_probe
    def no_local(*a,**kw):
        r=arm(*a,**kw)
        if a[0]=="candidate-stop":
            (a[2]/"scratch/h2_probe.save"/probe.H_UPF_NAME).unlink()
        return r
    monkeypatch.setattr(probe,"run_arm",no_local)
    assert probe.run_probe(args)==0
    report=json.loads((args.output_dir/"report.json").read_text(encoding="utf-8"))
    assert report["saved_optimizer"]["saved_upf_present"] is False
    assert report["saved_optimizer"]["saved_upf_sha256"] is None
    assert report["saved_optimizer"]["external_upf_sha256"]==probe.H_UPF_SHA256
    assert report["saved_optimizer"]["pinned_external_upf_fallback"] is True
    assert calls==["continuous","candidate-stop","negative-fresh","resumed"]


def test_changed_external_upf_blocks_copied_arms(fake_probe,monkeypatch):
    args,calls,arm=fake_probe
    digest=probe.sha256_file
    changed=[False]
    monkeypatch.setattr(probe,"sha256_file",lambda p:"0"*64 if changed[0] and p==args.pseudo else digest(p))
    def corrupt(*a,**kw):
        r=arm(*a,**kw)
        if a[0]=="candidate-stop":changed[0]=True
        return r
    monkeypatch.setattr(probe,"run_arm",corrupt)
    with pytest.raises(probe.ProbeError,match="external hydrogen"):probe.run_probe(args)
    assert calls==["continuous","candidate-stop"]


def test_corrupt_arm_local_copy_cannot_reach_qe(fake_probe,monkeypatch):
    args,calls,_=fake_probe
    copy=probe.shutil.copy2
    def corrupt(src,dst):
        result=copy(src,dst)
        if Path(dst).name==probe.H_UPF_NAME:Path(dst).write_bytes(b"corrupted arm copy")
        return result
    monkeypatch.setattr(probe.shutil,"copy2",corrupt)
    with pytest.raises(probe.ProbeError,match="arm-local hydrogen"):probe.run_probe(args)
    assert calls==[]
