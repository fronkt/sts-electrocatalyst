"""Static guards on the prepared (never executed here) stage, submit, validation, release and watch scripts.

Nothing is run against Anvil.  The remote programs are compiled and inspected: each may issue only the commands its
step is allowed to issue, none may name the first trial's checkout, and the once-only guards are present.
"""
import importlib.util
import json
from pathlib import Path
import re

import pytest

ROOT = Path(__file__).resolve().parents[1]
PHASE = ROOT / "results/pa_catalyst_retest_2026-10-04"
OLD_ROOT = "sts_pa_catalyst_2026-10-03"
NEW_ROOT = "sts_pa_catalyst_retest_2026-10-04"
SCRIPTS = {name: PHASE / file for name, file in {
    "stage": "pa-catalyst-retest-remote-stage-2026-10-04.py", "submit": "pa-catalyst-retest-submit-held-2026-10-04.py",
    "validate": "pa-catalyst-retest-held-validation-2026-10-04.py", "release": "pa-catalyst-retest-release-2026-10-04.py",
    "watch": "watch_retest_readonly.py", "publish": "publish_reviewed_package.py"}.items()}


def load(name):
    spec = importlib.util.spec_from_file_location("retest_script_" + name, SCRIPTS[name])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def publication():
    pins = {"src/dft/pa_catalyst_retest.py": {"sha256": "a" * 64, "bytes": 1}, "anvil/90_pa_catalyst_retest.slurm": {"sha256": "b" * 64, "bytes": 1},
            "results/pa_catalyst_retest_2026-10-04/launch_spec.json": {"sha256": "c" * 64, "bytes": 1}}
    extra = {rel: {"sha256": "d" * 64, "bytes": 1} for rel in (".gitattributes", "src/dft/pa_checked_contract.py",
             "runs/hea/lowtail_low_state_restart_2026-09-22/Cu8Cr23Mn35Co34__s20_site2/slab_c5low__relax.in")}
    return {"successful": True, "commit": "e" * 40, "remote_commit": "e" * 40, "staged_blob_pins": pins, "additional_blob_pins": extra,
            "local_pins": {"results/pa_catalyst_retest_2026-10-04/launch_spec.json": "c" * 64}}


@pytest.mark.parametrize("name", sorted(SCRIPTS))
def test_every_prepared_script_parses_and_names_only_the_new_root(name):
    text = SCRIPTS[name].read_text(encoding="utf-8")
    compile(text, str(SCRIPTS[name]), "exec")
    assert OLD_ROOT not in text, "a prepared script must never name the first trial's checkout as a target"
    if name != "publish":
        assert "x-che260157" in text and (NEW_ROOT in text)


def test_stage_program_is_read_only_apart_from_the_new_isolated_checkout():
    module = load("stage")
    program, pins = module.build(publication())
    assert "commit=" + repr("e" * 40) in program and "spec_sha256=" + repr("c" * 64) in program
    for forbidden in ("sbatch", "scancel", "srun", "scontrol', 'release", "scontrol', 'update", "rmtree", "os.remove", "unlink"):
        assert forbidden not in program, forbidden
    assert "assert not root.exists()" in program and "git" in program and "'--preflight'" in program
    assert "pa_catalyst_retest.py" in program and "pa_catalyst_trial.py" not in program
    assert "real_control_replay" in program and "assert not list(root.glob('pa_replay_*'))" in program
    assert pins[".gitattributes"]["sha256"] == "d" * 64


def test_submit_program_is_once_only_and_submits_one_held_no_requeue_job():
    module = load("submit")
    program = module.build("e" * 40, "c" * 64)
    assert len(re.findall(r"\['sbatch'", program)) == 1
    assert "'--hold'" in program and "'--parsable'" in program and "'--no-requeue'" in program
    for forbidden in ("--array", "--dependency", "--requeue", "scancel", "scontrol', 'release", "srun"):
        assert forbidden not in program, forbidden
    assert "assert not intent.exists()" in program and "intent.open('x'" in program
    assert program.index("intent.open('x'") < program.index("'sbatch'"), "the once-only intent must be written before sbatch"
    assert "float(cpu[0][-1]) >= 2048" in program and "assert not queue.strip()" in program
    assert "real_control_replay" in program


def test_validation_program_only_reads_the_job():
    module = load("validate")
    program = module.build("12345")
    commands = re.findall(r"\[('[^\]]*)\]", program)
    assert all(row.startswith("'scontrol', 'show', 'job'") for row in commands if "scontrol" in row)
    for forbidden in ("sbatch", "scancel", "release", "update", "srun"):
        assert forbidden not in program, forbidden
    assert "'1', '1-1'" in program, "both spellings of the pending one-node bound must be accepted"
    assert "'JobName': 'pa-catalyst-retest'" in program and "90_pa_catalyst_retest.slurm" in program


def test_release_program_releases_exactly_once_and_runs_preflight_first():
    module = load("release")
    program = module.build("12345", "e" * 40, "c" * 64)
    assert program.count("'scontrol', 'release'") == 1
    for forbidden in ("sbatch", "scancel", "srun", "--requeue"):
        assert forbidden not in program, forbidden
    assert "assert not receipt.exists()" in program
    assert program.index("fresh_preflight") < program.index("'scontrol', 'release'")
    assert "float(cpu[0][-1]) >= 2048" in program and "== [job]" in program


def test_stage_submit_validate_release_refuse_to_overwrite_their_receipts():
    for name, receipt in (("stage", "remote_stage.json"), ("submit", "submission.json"), ("validate", "held_validation_checked.json"),
                          ("release", "release.json")):
        text = SCRIPTS[name].read_text(encoding="utf-8")
        assert re.search(r"assert not target\.exists\(\)", text) and receipt in text, name


def test_watcher_is_read_only_and_points_at_the_new_root():
    text = SCRIPTS["watch"].read_text(encoding="utf-8")
    assert NEW_ROOT in text
    for forbidden in ("sbatch", "scancel", "scontrol release", "scontrol update", "srun", "pw.x"):
        assert forbidden not in text.replace("never submit, cancel, retry or invoke QE", ""), forbidden
    assert "retest_observations.jsonl" in text and "retest_watch_status.json" in text


def test_wrapper_requests_exactly_the_approved_shape():
    text = (ROOT / "anvil/90_pa_catalyst_retest.slurm").read_text(encoding="utf-8")
    for line in ("#SBATCH --account=che260157", "#SBATCH --partition=wholenode", "#SBATCH --nodes=1", "#SBATCH --ntasks=128",
                 "#SBATCH --cpus-per-task=1", "#SBATCH --mem=200G", "#SBATCH --time=16:00:00", "#SBATCH --no-requeue",
                 "#SBATCH --job-name=pa-catalyst-retest"):
        assert line in text
    for forbidden in ("--array", "--dependency", "--requeue", "--gres", "--gpus", "--exclusive=", "sbatch ", "scontrol"):
        assert forbidden not in text
    assert OLD_ROOT not in text and NEW_ROOT in text
    assert 'pa_catalyst_retest.py' in text and "REFUSE: prior re-test output" in text and "REFUSE: spec byte drift" in text
    assert "\r" not in text


def test_launch_spec_resources_equal_the_approved_trial_and_every_remote_target_is_new():
    spec = json.loads((PHASE / "launch_spec.json").read_text(encoding="utf-8"))
    old = json.loads((ROOT / "results/pa_catalyst_trial_2026-10-03/launch_spec.json").read_text(encoding="utf-8"))
    for key in ("allocation", "caps", "parallel_shape", "pw_x", "mpirun", "upfs", "initial_seed", "optional_negative_control", "target"):
        assert spec[key] == old[key], key
    assert spec["production_accepted"] is False
    assert spec["trial_parent"].endswith(NEW_ROOT) and spec["trial_root"] == spec["trial_parent"] + "/trial_results"
    written = [spec["trial_parent"], spec["trial_root"], spec["source_deck"]["path"], spec["source_review"]["path"]] + \
        [d["path"] for d in spec["dependencies"]] + [spec["preflight_replay"]["root"]]
    assert all(path.startswith(spec["trial_parent"]) for path in written)
    assert OLD_ROOT in spec["preflight_replay"]["logged_upf_dir"]  # a string recorded in the real control log, never a target
    assert spec["source_deck"]["sha256"] == old["source_deck"]["sha256"]
    assert spec["predecessor"]["spec_sha256"] == "4bed5002a88857515940230b20ad59e6adc345e29d8567d5b9c5f5511b0b28a2"


@pytest.mark.parametrize('name, intent_name', [('submit', 'intent'), ('release', None)])
def test_remote_intent_creation_is_atomic_under_concurrent_invocations(tmp_path, name, intent_name):
    import ast
    import concurrent.futures
    import os
    import threading
    module = load(name)
    program = module.build('e' * 40, 'c' * 64) if name == 'submit' else module.build('12345', 'e' * 40, 'c' * 64)
    tree = ast.parse(program)
    claim = next(n for n in tree.body if isinstance(n, ast.With))
    compiled = compile(ast.Module(body=[claim], type_ignores=[]), '<real-exclusive-intent>', 'exec')
    barrier = threading.Barrier(8)
    def invoke(_):
        env = {'intent': tmp_path / 'submission_intent_remote.json', 'phase': tmp_path,
               'job': '12345', 'commit': 'e' * 40, 'json': json, 'os': os}
        barrier.wait()
        try:
            exec(compiled, env)
            return True
        except FileExistsError:
            return False
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        winners = list(pool.map(invoke, range(8)))
    assert winners.count(True) == 1
    intent = tmp_path / ('submission_intent_remote.json' if name == 'submit' else 'release_intent_remote.json')
    recorded = json.loads(intent.read_text())
    assert recorded.get('published_commit', recorded.get('commit')) == 'e' * 40


@pytest.mark.parametrize('name', ['submit', 'release'])
def test_local_launch_refuses_existing_intent_before_ssh(tmp_path, monkeypatch, name):
    import types
    module = load(name)
    monkeypatch.setattr(module, 'PHASE', tmp_path)
    published = publication()
    (tmp_path / 'publication_final.json').write_text(json.dumps(published))
    (tmp_path / 'remote_stage.json').write_text(json.dumps({'returncode':0, 'stdout':json.dumps({'successful':True})}))
    (tmp_path / 'submission.json').write_text(json.dumps({'job_id':'12345'})) if name == 'release' else None
    (tmp_path / 'held_validation_checked.json').write_text(json.dumps({'returncode':0,'stdout':json.dumps({'held_shape_validated':True})}))
    intent=tmp_path / ('submission_intent.json' if name == 'submit' else 'release_intent.json')
    intent.write_text('prior intent')
    calls=[]
    monkeypatch.setattr(module, 'subprocess', types.SimpleNamespace(run=lambda *a, **k: calls.append((a,k))))
    with pytest.raises(FileExistsError):
        module.main()
    assert calls == [] and intent.read_text() == 'prior intent'


def test_watcher_stops_after_three_inner_scheduler_collection_failures(tmp_path, monkeypatch):
    import types
    module=load('watch')
    monkeypatch.setattr(module,'PHASE',tmp_path)
    (tmp_path/'submission.json').write_text(json.dumps({'job_id':'12345'}))
    data={'commands':{name:{'returncode': 1 if name=='accounting' else 0, 'stdout':'', 'stderr':'accounting unavailable'}
                      for name in ('accounting','queue','job')}}
    calls=[]
    def run(*args,**kwargs):
        calls.append(args)
        return types.SimpleNamespace(returncode=0,stdout=json.dumps(data),stderr='')
    monkeypatch.setattr(module,'subprocess',types.SimpleNamespace(run=run))
    monkeypatch.setattr(module.time,'sleep',lambda seconds: None)
    module.main('12345')
    status=json.loads((tmp_path/'retest_watch_status.json').read_text())
    assert len(calls)==3 and status['state']=='COLLECTION_ERROR'
    assert status['consecutive_collection_failures']==3


def test_watcher_can_finish_from_terminal_accounting_after_slurm_purges_job():
    module=load('watch')
    data={'commands':{name:{'returncode':1 if name in ('job','queue') else 0, 'stdout':'12345|COMPLETED|0:0|10|128|200G||1280\n'
        if name=='accounting' else '', 'stderr':''} for name in ('accounting','queue','job')}}
    assert module.collection_state(data,'12345')=='COMPLETED'
