"""Stage, preflight, held-submit, validate and release the O1 one-boundary re-test.

Usage (local, background worker): python launch_ops.py <phase>
  stage     copy the pinned bytes of a pushed commit to the dated Anvil parent (read-only), verify sha256
  preflight the controller's own --preflight (real-control replay, every pin) + mybalance + queue + spec sha
  submit    one `sbatch --hold --parsable --no-requeue` (once-only)
  validate  scontrol shape of the held job
  release   one `scontrol release` (once-only)
Every phase writes its own receipt; no phase ever resubmits or retries a job.
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
HERE = ROOT / "results/pa_catalyst_o1_2026-10-07"
SPEC_REL = "results/pa_catalyst_o1_2026-10-07/launch_spec.json"
SPEC = json.loads((ROOT / SPEC_REL).read_text(encoding="utf-8"))
PARENT = SPEC["trial_parent"]
PYTHON = "/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3"
SLURM = PARENT + "/anvil/93_pa_catalyst_o1.slurm"
CONTROLLER = PARENT + "/src/dft/pa_catalyst_o1.py"
# Jobs of this account that may already be in the queue (the 2026-10-07 reproducibility probe).
KNOWN_JOBS = set(json.loads((ROOT / "results/pa_repro_probe_2026-10-07/submit_receipt.json").read_text())["jobs"].values())


def relative(path):
    if not path.startswith(PARENT + "/"):
        raise SystemExit("pinned path outside the dated parent: " + path)
    return path[len(PARENT) + 1:]


# repo-relative path -> (remote path, sha256 or None, text?)
STAGE = {SPEC_REL: (PARENT + "/" + SPEC_REL, None, True)}
for key in ("source_deck", "source_review"):
    STAGE[relative(SPEC[key]["path"])] = (SPEC[key]["path"], SPEC[key]["sha256"], True)
for pin in SPEC["dependencies"]:
    STAGE[relative(pin["path"])] = (pin["path"], pin["sha256"], True)
for entry in SPEC["preflight_replay"]["files"]:
    remote = SPEC["preflight_replay"]["root"] + "/" + entry["path"]
    STAGE[relative(remote)] = (remote, entry["sha256"], not entry["path"].endswith(".gz"))


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def write(name, value):
    path = HERE / name
    with path.open("x", encoding="utf-8", newline="\n") as stream:
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


def spec_sha():
    return hashlib.sha256((ROOT / SPEC_REL).read_bytes()).hexdigest()


def stage():
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    remote = subprocess.check_output(["git", "ls-remote", "origin", "refs/heads/r0-catalysis-revival"], cwd=ROOT, text=True).split()[0]
    if subprocess.run(["git", "merge-base", "--is-ancestor", commit, remote], cwd=ROOT).returncode:
        raise SystemExit("launch commit is not pushed")
    receipt = {"phase": "stage", "at": now(), "commit": commit, "files": [], "commands": {}}
    # Read and verify every committed blob before touching Anvil, so a pin or line-ending
    # mismatch can never leave a half-staged, read-only parent behind.
    blobs = {}
    for rel, (target, pin, text) in sorted(STAGE.items()):
        data = subprocess.check_output(["git", "show", commit + ":" + rel], cwd=ROOT)
        digest = hashlib.sha256(data).hexdigest()
        if (text and b"\r" in data) or (pin and digest != pin):
            raise SystemExit("committed bytes differ from the spec pin: " + rel)
        blobs[rel] = (target, data, digest)
    client = connect()
    sftp = client.open_sftp()
    run(client, ["test", "!", "-e", PARENT + "/trial_results"], receipt, "no_prior_output")
    for rel, (target, data, digest) in sorted(blobs.items()):
        run(client, ["test", "!", "-e", target], receipt, "absent:" + rel)
    for rel, (target, data, digest) in sorted(blobs.items()):
        run(client, ["mkdir", "-p", posixpath.dirname(target)], receipt, "mkdir:" + rel)
        with sftp.open(target, "wb") as stream:
            stream.write(data)
        row = run(client, ["sha256sum", target], receipt, "sha:" + rel)
        if row["stdout"].split()[0] != digest:
            raise SystemExit("remote bytes differ: " + rel)
        run(client, ["chmod", "0444", target], receipt, "chmod:" + rel)
        receipt["files"].append({"repo_path": rel, "remote_path": target, "sha256": digest})
    receipt["spec_sha256"] = spec_sha()
    client.close()
    write("stage_receipt.json", receipt)


def preflight():
    receipt = {"phase": "preflight", "at": now(), "commands": {}, "spec_sha256": spec_sha()}
    client = connect()
    row = run(client, [PYTHON, "-B", CONTROLLER, "--spec", PARENT + "/" + SPEC_REL,
                       "--spec-sha256", receipt["spec_sha256"], "--preflight"], receipt, "preflight", timeout=900, check=False)
    run(client, "mybalance", receipt, "mybalance")
    queue = run(client, ["squeue", "-u", "x-fcai3", "-h", "-o", "%i|%j|%T"], receipt, "squeue")
    run(client, ["sha256sum", PARENT + "/" + SPEC_REL], receipt, "remote_spec_sha")
    client.close()
    try:
        result = json.loads(row["stdout"])
    except ValueError:
        result = {}
    queued = {line.split("|")[0] for line in queue["stdout"].splitlines() if line.strip()}
    receipt["result_status"] = result.get("status")
    receipt["real_control_replay"] = result.get("real_control_replay")
    receipt["queued_jobs"] = sorted(queued)
    receipt["passed"] = (row["rc"] == 0 and result.get("status") == "PREFLIGHT_PASS"
                         and (result.get("real_control_replay") or {}).get("replayed") is True
                         and receipt["commands"]["remote_spec_sha"]["stdout"].split()[0] == receipt["spec_sha256"]
                         and queued <= KNOWN_JOBS)
    write("preflight_receipt.json", receipt)
    if not receipt["passed"]:
        raise SystemExit("preflight did not pass")


def submit():
    if not json.loads((HERE / "preflight_receipt.json").read_text())["passed"]:
        raise SystemExit("preflight has not passed")
    receipt = {"phase": "submit", "at": now(), "commands": {}, "jobs": {}, "spec_sha256": spec_sha()}
    with (HERE / "submit_intent.json").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps({"at": now(), "slurm": SLURM}) + "\n")
    client = connect()
    try:
        args = ["sbatch", "--hold", "--parsable", "--no-requeue",
                "--export=ALL,STS_PA_SPEC_SHA256=" + receipt["spec_sha256"], SLURM]
        row = run(client, args, receipt, "sbatch:o1")
        job = row["stdout"].strip().split(";")[0]
        if not job.isdigit():
            raise RuntimeError("sbatch returned no numeric job id")
        receipt["jobs"]["o1"] = job
    finally:
        client.close()
        write("submit_receipt.json", receipt)


def validate():
    jobs = json.loads((HERE / "submit_receipt.json").read_text())["jobs"]
    if len(jobs) != 1:
        raise SystemExit("exactly one submitted job required, found " + json.dumps(jobs))
    receipt = {"phase": "validate", "at": now(), "commands": {}, "checks": {}}
    client = connect()
    for name, job in jobs.items():
        row = run(client, ["scontrol", "show", "job", job, "-o"], receipt, "held:" + name)
        fields = dict(part.split("=", 1) for part in row["stdout"].split() if "=" in part)
        # A pending job shows its node bounds as "1-1"; ReqTRES must still request exactly one node.
        expected = {"JobState": "PENDING", "Account": "che260157", "Partition": "wholenode",
                    "NumCPUs": "128", "NumTasks": "128", "CPUs/Task": "1", "Requeue": "0",
                    "Dependency": "(null)", "TimeLimit": "08:00:00", "JobName": "pa-catalyst-o1",
                    "Command": SLURM}
        bad = {k: fields.get(k) for k, v in expected.items() if fields.get(k) != v}
        if fields.get("NumNodes") not in {"1", "1-1"}:
            bad["NumNodes"] = fields.get("NumNodes")
        tres = dict(part.split("=", 1) for part in fields.get("ReqTRES", "").split(",") if "=" in part)
        if tres.get("node") != "1" or tres.get("cpu") != "128" or tres.get("billing") != "128":
            bad["ReqTRES"] = fields.get("ReqTRES")
        # SubmitLine contains spaces, so check the raw record rather than the split fields.
        export = "--export=ALL,STS_PA_SPEC_SHA256=" + spec_sha() + " "
        if row["stdout"].count(export) != 1:
            bad["SubmitLine"] = "spec pin absent from the submitted environment"
        held = fields.get("Reason") == "JobHeldUser" or fields.get("Priority") == "0"
        receipt["checks"][name] = {"job": job, "mismatches": bad, "held": held,
                                   "max_cpu_su": SPEC["allocation"]["max_cpu_su"]}
    client.close()
    receipt["passed"] = len(receipt["checks"]) == 1 and all(
        not c["mismatches"] and c["held"] for c in receipt["checks"].values())
    write("validate_receipt.json", receipt)
    if not receipt["passed"]:
        raise SystemExit("held shape differs")


def release():
    if not json.loads((HERE / "validate_receipt.json").read_text())["passed"]:
        raise SystemExit("held shape not validated")
    jobs = json.loads((HERE / "submit_receipt.json").read_text())["jobs"]
    if len(jobs) != 1:
        raise SystemExit("exactly one submitted job required, found " + json.dumps(jobs))
    receipt = {"phase": "release", "at": now(), "commands": {}, "released": {}}
    with (HERE / "release_intent.json").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps({"at": now(), "jobs": jobs}) + "\n")
    client = connect()
    try:
        for name, job in jobs.items():
            run(client, ["scontrol", "release", job], receipt, "release:" + name)
            receipt["released"][name] = job
        run(client, ["squeue", "-u", "x-fcai3", "-o", "%i|%j|%T|%M|%l|%R"], receipt, "after")
    finally:
        client.close()
        write("release_receipt.json", receipt)


if __name__ == "__main__":
    {"stage": stage, "preflight": preflight, "submit": submit, "validate": validate, "release": release}[sys.argv[1]]()
