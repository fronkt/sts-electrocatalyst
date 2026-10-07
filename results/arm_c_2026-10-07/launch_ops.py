"""Stage, preflight, held-submit, validate and release the S8 arm-C fixed-geometry batch.

Usage (local, background worker): python launch_ops.py <phase>
  stage     copy the committed bytes of a pushed commit to the dated Anvil root (inputs read-only), verify sha256
  preflight the unchanged runner's own --preflight for both stages, Python 3.9 imports, QE binaries,
            mybalance, an empty queue and the remote spec/Slurm sha256
  submit    two `sbatch --hold --parsable --no-requeue` arrays: arm_c_main (1-64%60) and arm_c_probe (1-2%2)
  validate  scontrol shape of both held arrays
  release   one `scontrol release` per array
Every phase writes its own receipt; no phase ever resubmits or retries a job. The intent files
block an automatic second submit or release: if a phase fails partway, a held array may remain on
Anvil, and it is inspected and then cancelled or released by hand, with the action recorded.
"""
import datetime as dt
import hashlib
import json
import posixpath
import shlex
import subprocess
import sys
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "results/arm_c_2026-10-07"
SPEC_REL = "results/arm_c_2026-10-07/launch_spec.json"
SLURM_REL = "anvil/94_arm_c_batch.slurm"
SPEC = json.loads((ROOT / SPEC_REL).read_text(encoding="utf-8"))
REMOTE = "/anvil/projects/x-che260157/sts_arm_c_2026-10-07"
PROJECT = "/anvil/projects/x-che260157"
PYTHON = "/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3"
ARRAYS = {"arm_c_main": {"array": "1-64%60", "tasks": 64, "throttle": "60", "name": "arm-c-main"},
          "arm_c_probe": {"array": "1-2%2", "tasks": 2, "throttle": "2", "name": "arm-c-probe"}}
MIN_FREE_PROJECT_TB = 1.5  # about 18 GB of retained wavefunctions per SCF, 66 SCFs plus a re-run round
TIME_LIMIT = "02:30:00"
# repo-relative path -> expected sha256 of the committed blob (None: recorded, not pre-pinned)
STAGE = dict(SPEC["files"])
STAGE[SPEC_REL] = None
STAGE[SLURM_REL] = None


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def write(name, value):
    with (HERE / name).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, indent=2) + "\n")


def connect():
    client = paramiko.SSHClient()
    client.load_host_keys(str(Path.home() / ".ssh/known_hosts"))
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect("anvil.rcac.purdue.edu", username="x-fcai3", key_filename=str(Path.home() / ".ssh/id_ed25519"),
                   allow_agent=False, look_for_keys=False, timeout=20, banner_timeout=20, auth_timeout=20)
    return client


def run(client, args, receipt, label, timeout=300, check=True):
    text = args if isinstance(args, str) else shlex.join(map(str, args))
    _, out, err = client.exec_command(text, timeout=timeout)
    row = {"command": text, "stdout": out.read().decode(), "stderr": err.read().decode(),
           "rc": out.channel.recv_exit_status(), "at": now()}
    receipt["commands"][label] = row
    if check and row["rc"]:
        raise RuntimeError(label + " failed: " + json.dumps(row)[:4000])
    return row


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def stage():
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    remote = subprocess.check_output(["git", "ls-remote", "origin", "refs/heads/r0-catalysis-revival"], cwd=ROOT, text=True).split()[0]
    if subprocess.run(["git", "merge-base", "--is-ancestor", commit, remote], cwd=ROOT).returncode:
        raise SystemExit("launch commit is not pushed")
    receipt = {"phase": "stage", "at": now(), "commit": commit, "files": [], "commands": {}, "completed": False}
    # Read and verify every committed blob before touching Anvil, so a pin or line-ending
    # mismatch can never leave a half-staged, read-only root behind.
    blobs = {}
    for rel, pin in sorted(STAGE.items()):
        data = subprocess.check_output(["git", "show", commit + ":" + rel], cwd=ROOT)
        digest = hashlib.sha256(data).hexdigest()
        if b"\r" in data or (pin and digest != pin) or digest != sha(rel):
            raise SystemExit("committed bytes differ from the pin or the working copy: " + rel)
        blobs[rel] = (REMOTE + "/" + rel, data, digest)
    client = connect()
    try:
        sftp = client.open_sftp()
        run(client, ["test", "!", "-e", REMOTE], receipt, "root_absent")
        for rel, (target, data, digest) in sorted(blobs.items()):
            run(client, ["mkdir", "-p", posixpath.dirname(target)], receipt, "mkdir:" + rel)
            with sftp.open(target, "wb") as stream:
                stream.write(data)
            row = run(client, ["sha256sum", target], receipt, "sha:" + rel)
            if row["stdout"].split()[0] != digest:
                raise SystemExit("remote bytes differ: " + rel)
            run(client, ["chmod", "0444", target], receipt, "chmod:" + rel)
            receipt["files"].append({"repo_path": rel, "remote_path": target, "sha256": digest})
        run(client, ["mkdir", REMOTE + "/logs"], receipt, "logs_dir")
        receipt["spec_sha256"] = sha(SPEC_REL)
        receipt["slurm_sha256"] = sha(SLURM_REL)
        receipt["completed"] = True
    except BaseException as error:
        receipt["error"] = repr(error)
        raise
    finally:
        client.close()
        write("stage_receipt.json", receipt)


def project_free_tb(text):
    """Free space of the x-che260157 project space from `myquota` (its Size and Limit columns)."""
    units = {"KB": 1e-9, "MB": 1e-6, "GB": 1e-3, "TB": 1.0, "PB": 1e3}
    rows = [line.split() for line in text.splitlines() if line.split()[:2] == ["projects", "x-che260157"]]
    if len(rows) != 1:
        return None
    try:
        size, limit = (float(token[:-2]) * units[token[-2:]] for token in rows[0][2:4])
    except (KeyError, ValueError, IndexError):
        return None
    return limit - size


def preflight():
    staged = json.loads((HERE / "stage_receipt.json").read_text(encoding="utf-8"))
    if not staged.get("completed") or staged.get("spec_sha256") != sha(SPEC_REL):
        raise SystemExit("staging is not complete for this spec")
    receipt = {"phase": "preflight", "at": now(), "commands": {}, "spec_sha256": sha(SPEC_REL),
               "slurm_sha256": sha(SLURM_REL)}
    client = connect()
    runner = REMOTE + "/src/dft/research_batch.py"
    spec = REMOTE + "/" + SPEC_REL
    for stage_name in ARRAYS:
        run(client, [PYTHON, "-B", runner, "--spec", spec, "--root", REMOTE, "--stage", stage_name,
                     "--pseudo", PROJECT + "/pseudo", "--preflight"], receipt, "preflight:" + stage_name, timeout=900)
    run(client, [PYTHON, "-B", "-c", "import sys; sys.path.insert(0, sys.argv[1]); "
                 "import research_batch, projection_qc, hea_force_audit, hea_followup_qc; print('IMPORTS_OK')",
                 REMOTE + "/src/dft"], receipt, "imports")
    run(client, ["test", "-x", PROJECT + "/qe/env/bin/pw.x", "-a", "-x", PROJECT + "/qe/env/bin/projwfc.x",
                 "-a", "-x", PROJECT + "/qe/env/bin/mpirun"], receipt, "qe_binaries")
    run(client, ["test", "-d", REMOTE + "/logs", "-a", "-w", REMOTE + "/logs"], receipt, "logs_dir")
    binaries = run(client, ["sha256sum"] + [PROJECT + "/qe/env/bin/" + name for name in SPEC["qe_binaries_sha256"]],
                   receipt, "qe_sha")
    run(client, "bash -lc myquota", receipt, "myquota")
    run(client, "mybalance", receipt, "mybalance")
    queue = run(client, ["squeue", "-u", "x-fcai3", "-h", "-o", "%i|%j|%T"], receipt, "squeue")
    run(client, ["sha256sum", spec, REMOTE + "/" + SLURM_REL], receipt, "remote_sha")
    run(client, ["bash", "-n", REMOTE + "/" + SLURM_REL], receipt, "slurm_syntax")
    client.close()
    shas = dict(reversed(line.split()) for line in receipt["commands"]["remote_sha"]["stdout"].splitlines())
    balance = [line.split() for line in receipt["commands"]["mybalance"]["stdout"].splitlines() if line.startswith("che260157 ")]
    receipt["balance_su"] = float(balance[0][-1]) if balance else None
    receipt["queued_jobs"] = [line for line in queue["stdout"].splitlines() if line.strip()]
    found = {line.split()[1].rsplit("/", 1)[-1]: line.split()[0]
             for line in binaries["stdout"].splitlines() if line.strip()}
    receipt["qe_binaries_match"] = found == SPEC["qe_binaries_sha256"]
    receipt["project_free_TB"] = project_free_tb(receipt["commands"]["myquota"]["stdout"])
    receipt["passed"] = (all(receipt["commands"]["preflight:" + s]["stdout"].strip() == "VALID" for s in ARRAYS)
                         and receipt["commands"]["imports"]["stdout"].strip() == "IMPORTS_OK"
                         and shas.get(spec) == receipt["spec_sha256"]
                         and shas.get(REMOTE + "/" + SLURM_REL) == receipt["slurm_sha256"]
                         and not receipt["queued_jobs"]
                         and receipt["balance_su"] is not None
                         and receipt["balance_su"] >= SPEC["allocation"]["approved_campaign_ceiling_cpu_su"]
                         and receipt["qe_binaries_match"]
                         and receipt["project_free_TB"] is not None
                         and receipt["project_free_TB"] >= MIN_FREE_PROJECT_TB)
    write("preflight_receipt.json", receipt)
    if not receipt["passed"]:
        raise SystemExit("preflight did not pass")


def submit():
    if not json.loads((HERE / "preflight_receipt.json").read_text())["passed"]:
        raise SystemExit("preflight has not passed")
    receipt = {"phase": "submit", "at": now(), "commands": {}, "jobs": {}, "spec_sha256": sha(SPEC_REL)}
    with (HERE / "submit_intent.json").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps({"at": now(), "arrays": ARRAYS}) + "\n")
    client = connect()
    try:
        for stage_name, shape in ARRAYS.items():
            args = ["sbatch", "--hold", "--parsable", "--no-requeue", "--array=" + shape["array"],
                    "--time=" + TIME_LIMIT, "--job-name=" + shape["name"],
                    "--export=ALL,STAGE=" + stage_name, REMOTE + "/" + SLURM_REL]
            row = run(client, args, receipt, "sbatch:" + stage_name)
            job = row["stdout"].strip().split(";")[0]
            if not job.isdigit():
                raise RuntimeError("sbatch returned no numeric job id")
            receipt["jobs"][stage_name] = job
    finally:
        client.close()
        write("submit_receipt.json", receipt)


def validate():
    jobs = json.loads((HERE / "submit_receipt.json").read_text())["jobs"]
    if set(jobs) != set(ARRAYS):
        raise SystemExit("exactly the two registered arrays are required, found " + json.dumps(jobs))
    receipt = {"phase": "validate", "at": now(), "commands": {}, "checks": {}}
    client = connect()
    for stage_name, job in jobs.items():
        shape = ARRAYS[stage_name]
        row = run(client, ["scontrol", "show", "job", job, "-o"], receipt, "held:" + stage_name)
        records = [line for line in row["stdout"].splitlines() if line.strip()]
        bad = {}
        if len(records) != 1:
            bad["records"] = len(records)
        fields = dict(part.split("=", 1) for part in records[0].split() if "=" in part) if records else {}
        expected = {"JobState": "PENDING", "Account": "che260157", "Partition": "wholenode",
                    "NumCPUs": "128", "NumTasks": "128", "CPUs/Task": "1", "Requeue": "0",
                    "Dependency": "(null)", "TimeLimit": TIME_LIMIT, "JobName": shape["name"],
                    "Command": REMOTE + "/" + SLURM_REL, "ArrayTaskId": shape["array"],
                    "ArrayTaskThrottle": shape["throttle"]}
        bad.update({k: fields.get(k) for k, v in expected.items() if fields.get(k) != v})
        if fields.get("NumNodes") not in {"1", "1-1"}:
            bad["NumNodes"] = fields.get("NumNodes")
        tres = dict(part.split("=", 1) for part in fields.get("ReqTRES", "").split(",") if "=" in part)
        if tres.get("node") != "1" or tres.get("cpu") != "128" or tres.get("billing") != "128":
            bad["ReqTRES"] = fields.get("ReqTRES")
        if row["stdout"].count("--export=ALL,STAGE=" + stage_name + " ") != 1:
            bad["SubmitLine"] = "stage export absent from the submit line"
        held = fields.get("Reason") == "JobHeldUser" or fields.get("Priority") == "0"
        su = shape["tasks"] * 150 * 128 // 60
        receipt["checks"][stage_name] = {"job": job, "mismatches": bad, "held": held, "ceiling_cpu_su": su}
    client.close()
    total = sum(c["ceiling_cpu_su"] for c in receipt["checks"].values())
    receipt["launch_ceiling_cpu_su"] = total
    receipt["passed"] = (len(receipt["checks"]) == 2 and total == SPEC["allocation"]["this_launch_ceiling_cpu_su"]
                         and all(not c["mismatches"] and c["held"] for c in receipt["checks"].values()))
    write("validate_receipt.json", receipt)
    if not receipt["passed"]:
        raise SystemExit("held shape differs")


def release():
    if not json.loads((HERE / "validate_receipt.json").read_text())["passed"]:
        raise SystemExit("held shape not validated")
    jobs = json.loads((HERE / "submit_receipt.json").read_text())["jobs"]
    if set(jobs) != set(ARRAYS):
        raise SystemExit("exactly the two registered arrays are required")
    receipt = {"phase": "release", "at": now(), "commands": {}, "released": {}}
    with (HERE / "release_intent.json").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps({"at": now(), "jobs": jobs}) + "\n")
    client = connect()
    try:
        for stage_name, job in jobs.items():
            run(client, ["scontrol", "release", job], receipt, "release:" + stage_name)
            receipt["released"][stage_name] = job
        run(client, ["squeue", "-u", "x-fcai3", "-o", "%i|%j|%T|%M|%l|%R"], receipt, "after")
    finally:
        client.close()
        write("release_receipt.json", receipt)


if __name__ == "__main__":
    {"stage": stage, "preflight": preflight, "submit": submit, "validate": validate, "release": release}[sys.argv[1]]()
