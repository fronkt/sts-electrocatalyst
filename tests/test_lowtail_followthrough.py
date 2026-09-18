"""Read-only accounting, byte preservation and bounded follow-through regressions."""
import datetime as dt
import io
import json
from pathlib import Path
import shlex
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src/dft"))
import lowtail_followthrough as follow


def accounting(count=9,state="COMPLETED"):
    return "\n".join(f"20813525_{i}|{state}|0:0|3600|128|" for i in range(1,count+1))


def test_terminal_gate_requires_all_nine_exact_array_tasks():
    snapshot=follow.parse_sacct(accounting()+"\n20813525_1.batch|FAILED|1:0|30|128|",20813525)
    assert snapshot["all_terminal"] and snapshot["terminal_count"]==9
    assert snapshot["allocated_core_hours"]==1152
    incomplete=follow.parse_sacct(accounting(8),20813525)
    assert not incomplete["all_terminal"] and incomplete["missing_tasks"]==[9]
    assert not follow.parse_sacct(accounting(state="RUNNING"),20813525)["all_terminal"]


def test_held_array_is_not_mistaken_for_nine_finished_tasks():
    snapshot=follow.parse_sacct("20813525_[1-9%1]|PENDING|0:0|0|128|",20813525)
    assert snapshot["missing_tasks"]==list(range(1,10)) and not snapshot["all_terminal"]


def test_observe_requests_expanded_array_aware_job_ids():
    commands=[]
    # JobIDRaw instead yields unrelated internal IDs such as 20813536.
    raw=(accounting(state="PENDING").replace("20813525_1|PENDING", "20813525_1|RUNNING")
         + "\n20813525|PENDING|0:0|0|128|")
    def exec_command(command,timeout):
        commands.append(shlex.split(command))
        assert timeout==60
        out=SimpleNamespace(read=lambda:raw.encode(),channel=SimpleNamespace(recv_exit_status=lambda:0))
        return None,out,SimpleNamespace(read=lambda:b"")
    snapshot=follow.observe(SimpleNamespace(exec_command=exec_command),20813525)
    assert commands==[["sacct","--array","-n","-P","-X","-j","20813525",
                       "--format=JobID%80,State%30,ExitCode,ElapsedRaw,AllocCPUS"]]
    assert snapshot["command"]==commands[0] and snapshot["raw_stdout"]==raw
    assert len(snapshot["tasks"])==9 and snapshot["missing_tasks"]==[]
    assert snapshot["tasks"][0]["state"]=="RUNNING" and not snapshot["all_terminal"]
    numeric=follow.parse_sacct("20813536|COMPLETED|0:0|701|128|",20813525)
    assert numeric["missing_tasks"]==list(range(1,10)) and not numeric["all_terminal"]


def test_cancelled_reason_and_conflicting_rows():
    snap=follow.parse_sacct(accounting().replace("COMPLETED","CANCELLED by 1234"),20813525)
    assert snap["all_terminal"] and all(t["state"]=="CANCELLED" for t in snap["tasks"])
    with pytest.raises(ValueError,match="conflicting"):
        follow.parse_sacct(accounting()+"\n20813525_1|RUNNING|0:0|1|128|",20813525)


def test_conflicting_local_evidence_is_never_overwritten(tmp_path):
    target=tmp_path/"job.out"
    assert follow.preserve_bytes(target,b"original")=="MIRRORED"
    assert follow.preserve_bytes(target,b"original")=="ALREADY_IDENTICAL"
    with pytest.raises(ValueError,match="not overwritten"):
        follow.preserve_bytes(target,b"replacement")
    assert target.read_bytes()==b"original"


def artifact_set(job):
    artifacts={".out":b"pw.x output", ".run.in":b"runtime input", ".projwfc.in":b"projection input",
               ".projwfc.out":b"Lowdin Charges\nAtom # 1: total charge = 6.0, s = 2.0\nAtom # 2: total charge = 6.0, s = 2.0\nSpilling Parameter: 0.001\nJOB DONE.\n"}
    qc=dict(job=job["job"],site=job["site"],status="COMPLETE",input_sha256=job["sha256"],
            output_sha256=follow.sha(artifacts[".out"]),runtime_sha256=follow.sha(artifacts[".run.in"]))
    artifacts[".qc.json"]=json.dumps(qc).encode()
    return artifacts


def test_qc_hashes_projection_and_scheduler_are_checked():
    job=dict(job="O_recon__atomic",site="site",sha256="input-hash",nat=2)
    good=artifact_set(job)
    task=dict(state="COMPLETED",exit_code="0:0")
    assert follow.qc_problems(job,good,task)==(None,[])
    wrong=dict(good, **{".out":b"different"})
    assert follow.qc_problems(job,wrong,task)[0]=="QC_EVIDENCE_INVALID"
    wrong=dict(good, **{".projwfc.out":b"JOB DONE.\n"})
    assert follow.qc_problems(job,wrong,task)[0]=="QC_EVIDENCE_INVALID"
    assert follow.qc_problems(job,good,dict(state="FAILED",exit_code="1:0"))[0]=="SCHEDULER_FAILED"
    assert follow.qc_problems(job,{".qc.json":good[".qc.json"]},task)[0]=="TERMINAL_OUTPUT_MISSING"
    assert follow.qc_problems(job,{".out":good[".out"]},task)[0]=="TERMINAL_QC_MISSING"


class SFTP:
    def __init__(self,files):
        self.files=files
        self.opened=[]
    def get_channel(self):
        return SimpleNamespace(settimeout=lambda seconds:None)
    def stat(self,path):
        if path not in self.files:
            raise FileNotFoundError(path)
        return SimpleNamespace(st_size=len(self.files[path]),st_mtime=100)
    def open(self,path,mode):
        assert mode=="rb"
        self.opened.append(path)
        return io.BytesIO(self.files[path])
    def close(self):
        pass


class Client:
    def __init__(self,sftp):
        self.sftp=sftp
        self.closed=False
    def open_sftp(self):
        return self.sftp
    def close(self):
        self.closed=True


def nine_jobs():
    return [dict(job=f"O_{i}__atomic",site=f"site{i}",manifest_dir=f"hea/site{i}",sha256=f"input{i}",nat=2)
            for i in range(1,10)]


def test_terminal_missing_outputs_are_explicit_and_no_scratch_is_read(tmp_path):
    jobs=nine_jobs()
    files={}
    for job in jobs[:-1]:
        for suffix,data in artifact_set(job).items():
            files[follow.REMOTE+"/runs/"+job["manifest_dir"]+"/"+job["job"]+suffix]=data
    sftp=SFTP(files)
    mirror=follow.mirror_terminal(Client(sftp),tmp_path,dict(jobs=jobs),
                                  follow.parse_sacct(accounting(),20813525),tmp_path/"result")
    assert len(mirror["legs"])==9
    assert mirror["terminal_failures"]["site9/O_9__atomic"]["status"]=="TERMINAL_OUTPUT_MISSING"
    assert not (tmp_path/"runs/hea/site9/O_9__atomic.out").exists()
    assert not any("tmp_" in p or ".save/" in p for p in sftp.opened)
    for remote,data in files.items():
        assert (tmp_path/remote.split(follow.REMOTE+"/",1)[1]).read_bytes()==data


def test_mirror_conflict_preserves_both_versions_without_overwrite(tmp_path):
    jobs=nine_jobs()
    path="runs/"+jobs[0]["manifest_dir"]+"/"+jobs[0]["job"]+".out"
    target=tmp_path/path
    target.parent.mkdir(parents=True)
    target.write_bytes(b"local original")
    client=Client(SFTP({follow.REMOTE+"/"+path:b"remote evidence"}))
    with pytest.raises(ValueError,match="not overwritten"):
        follow.mirror_terminal(client,tmp_path,dict(jobs=jobs),follow.parse_sacct(accounting(),20813525),tmp_path/"result")
    assert target.read_bytes()==b"local original"
    assert [p.read_bytes() for p in (tmp_path/"result/conflicts").iterdir()]==[b"remote evidence"]


def test_lock_refuses_duplicates_and_only_owner_releases(tmp_path):
    lock=tmp_path/"active.lock"
    first=follow.acquire_lock(lock)
    with pytest.raises(RuntimeError,match="no duplicate"):
        follow.acquire_lock(lock)
    follow.release_lock(lock,dict(token="not-owner"))
    assert lock.exists()
    follow.release_lock(lock,first)
    assert not lock.exists()


def test_status_calls_stale_observation_stale():
    current=dt.datetime(2026,9,19,tzinfo=dt.timezone.utc)
    view=follow.status_view(dict(state="WATCHING",last_observed_at=(current-dt.timedelta(minutes=20)).isoformat(),poll_seconds=300),current)
    assert view["observation_is_stale"] and view["display_state"].startswith("STALE_OBSERVATION")
    done=follow.status_view(dict(state="READY_FOR_REVIEW",last_observed_at=(current-dt.timedelta(days=1)).isoformat()),current)
    assert done["display_state"]=="READY_FOR_REVIEW"


@pytest.fixture
def setup(tmp_path):
    files={}
    for relative in (*follow.READOUT_SOURCES,follow.RELATIVE+"/deck_plan.json",follow.RELATIVE+"/operating_decisions.json"):
        p=tmp_path/relative
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(b"pinned source or configuration")
        files[relative]=follow.sha(p.read_bytes())
    jobs=[]
    for i in range(9):
        relative=f"runs/hea/site{i}/job.in"
        p=tmp_path/relative
        p.parent.mkdir(parents=True)
        p.write_bytes(b"pinned input")
        files[relative]=follow.sha(p.read_bytes())
        jobs.append(dict(path=relative,sha256=files[relative],projector="atomic",role="primary"))
    spec=dict(files=files,jobs=jobs)
    follow.write_json(tmp_path/follow.RELATIVE/"launch_spec.json",spec)
    follow.write_json(tmp_path/follow.RELATIVE/"submission.json",dict(job_id="20813525"))
    return tmp_path,spec


def test_parser_or_input_changes_invalidate_startup_pins(setup):
    root,spec=setup
    pins=follow.startup_pins(root,spec)
    follow.assert_pins(root,pins)
    (root/follow.READOUT_SOURCES[2]).write_bytes(b"changed parser")
    with pytest.raises(ValueError,match="changed"):
        follow.assert_pins(root,pins)


def test_one_observation_is_bounded_and_does_not_invent_completion(setup,monkeypatch):
    root,spec=setup
    client=Client(SFTP({}))
    monkeypatch.setattr(follow,"connect",lambda:client)
    monkeypatch.setattr(follow,"observe",lambda c,a:follow.parse_sacct(accounting(state="PENDING"),a))
    assert follow.watch(root,20813525,once=True)==3
    status=json.loads((root/follow.RELATIVE/"followthrough/status.json").read_text())
    assert status["state"]=="STOPPED_AFTER_ONE_OBSERVATION" and status["terminal_count"]==0
    assert client.closed and not (root/follow.RELATIVE/"followthrough/active.lock").exists()


def test_completed_mirror_stops_at_ready_for_independent_review(setup,monkeypatch):
    root,spec=setup
    monkeypatch.setattr(follow,"connect",lambda:Client(SFTP({})))
    monkeypatch.setattr(follow,"observe",lambda c,a:follow.parse_sacct(accounting(),a))
    monkeypatch.setattr(follow,"mirror_terminal",lambda *args:dict(array_id="20813525",terminal_failures={}))
    monkeypatch.setattr(follow,"primary_readout",lambda *args:dict(leg_counts={"ACCEPTED":8,"TERMINAL_OUTPUT_MISSING":1}))
    assert follow.watch(root,20813525,once=True)==0
    status=json.loads((root/follow.RELATIVE/"followthrough/status.json").read_text())
    assert status["state"]=="READY_FOR_REVIEW" and status["independent_scientific_review"]=="PENDING"
    assert status["conditional_ortho_controls"]=="UNRUN"
