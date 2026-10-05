"""Stage, preflight, held-submit, validate and release the fixed-geometry diagnostic.

Usage (local, background worker): python launch_ops.py <phase>
  stage     copy the pinned bytes of a pushed commit to Anvil (read-only), verify sha256
  preflight remote Python 3.9 import + every pin + checkpoint listing; no QE, no Slurm writes
  submit    three `sbatch --hold --parsable --no-requeue` calls (once-only)
  validate  scontrol shape of each held job
  release   one `scontrol release` per held job (once-only)
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
HERE = ROOT / "results/pa_fixed_geometry_diag_2026-10-05"
SPEC_REL = "results/pa_fixed_geometry_diag_2026-10-05/launch_spec.json"
SPEC = json.loads((ROOT / SPEC_REL).read_text(encoding="utf-8"))
BASE = SPEC["base"]
PYTHON = "/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3"
STAGE = {
    "src/dft/pa_fixed_geometry_diag.py": SPEC["controller"],
    "src/dft/pa_catalyst_retest.py": SPEC["helper"],
    "anvil/91_pa_fixed_geometry_diag.slurm": SPEC["slurm"],
    SPEC_REL: {"path": BASE + "/launch_spec.json", "sha256": None},
}
for group in SPEC["groups"].values():
    for row in group["calls"]:
        STAGE["runs/hea/pa_fixed_geometry_diag_2026-10-05/decks/" + row["name"] + ".in"] = row["deck"]


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
        raise RuntimeError(label + " failed: " + json.dumps(row))
    return row


def spec_sha():
    return hashlib.sha256((ROOT / SPEC_REL).read_bytes()).hexdigest()


def stage():
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    remote = subprocess.check_output(["git", "ls-remote", "origin", "refs/heads/r0-catalysis-revival"], cwd=ROOT, text=True).split()[0]
    if subprocess.run(["git", "merge-base", "--is-ancestor", commit, remote], cwd=ROOT).returncode:
        raise SystemExit("launch commit is not pushed")
    receipt = {"phase": "stage", "at": now(), "commit": commit, "files": [], "commands": {}}
    client = connect()
    sftp = client.open_sftp()
    run(client, ["test", "!", "-e", BASE + "/groups"], receipt, "no_prior_groups")
    for rel, pin in sorted(STAGE.items()):
        data = subprocess.check_output(["git", "show", commit + ":" + rel], cwd=ROOT)
        digest = hashlib.sha256(data).hexdigest()
        if b"\r" in data or (pin["sha256"] and digest != pin["sha256"]):
            raise SystemExit("committed bytes differ from the spec pin: " + rel)
        target = pin["path"]
        run(client, ["mkdir", "-p", posixpath.dirname(target)], receipt, "mkdir:" + rel)
        run(client, ["test", "!", "-e", target], receipt, "absent:" + rel)
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


PREFLIGHT = r'''
import json, sys
sys.path.insert(0, "{base}/src/dft")
import pa_fixed_geometry_diag as d
spec = json.load(open("{base}/launch_spec.json"))
out = {{"python": sys.version}}
for g in d.GROUPS:
    d.validate_spec(spec, g)
    d.Group(spec, g).verify_sources()
    out[g] = "sources verified"
import os
root = spec["checkpoint"]["outdir"]
files = [os.path.join(c, f) for c, _, fs in os.walk(root) for f in fs]
out["checkpoint_files"] = len(files)
out["checkpoint_bytes"] = sum(os.lstat(f).st_size for f in files)
out["checkpoint_matches_pinned_count_and_bytes"] = (out["checkpoint_files"] == spec["checkpoint"]["files"]
                                                  and out["checkpoint_bytes"] == spec["checkpoint"]["bytes"])
print(json.dumps(out))
'''


def preflight():
    receipt = {"phase": "preflight", "at": now(), "commands": {}, "spec_sha256": spec_sha()}
    client = connect()
    script = PREFLIGHT.format(base=BASE)
    row = run(client, PYTHON + " -B -c " + shlex.quote(script), receipt, "preflight", timeout=600)
    result = json.loads(row["stdout"])
    run(client, "mybalance", receipt, "mybalance")
    run(client, ["squeue", "-u", "x-fcai3", "-h", "-o", "%i|%j|%T"], receipt, "squeue")
    run(client, ["sha256sum", BASE + "/launch_spec.json"], receipt, "remote_spec_sha")
    client.close()
    receipt["result"] = result
    receipt["passed"] = (all(result[g] == "sources verified" for g in SPEC["groups"])
                         and result["checkpoint_matches_pinned_count_and_bytes"]
                         and receipt["commands"]["remote_spec_sha"]["stdout"].split()[0] == receipt["spec_sha256"]
                         and receipt["commands"]["squeue"]["stdout"].strip() == "")
    write("preflight_receipt.json", receipt)
    if not receipt["passed"]:
        raise SystemExit("preflight did not pass")


def submit():
    if not json.loads((HERE / "preflight_receipt.json").read_text())["passed"]:
        raise SystemExit("preflight has not passed")
    receipt = {"phase": "submit", "at": now(), "commands": {}, "jobs": {}, "spec_sha256": spec_sha()}
    with (HERE / "submit_intent.json").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps({"at": now(), "groups": list(SPEC["groups"])}) + "\n")
    client = connect()
    try:
        for name, group in SPEC["groups"].items():
            args = ["sbatch", "--hold", "--parsable", "--no-requeue", "--time=" + group["time_limit"],
                    "--job-name=pa-fgd-" + name,
                    "--export=ALL,STS_DIAG_GROUP=" + name + ",STS_DIAG_SPEC_SHA256=" + receipt["spec_sha256"],
                    SPEC["slurm"]["path"]]
            row = run(client, args, receipt, "sbatch:" + name)
            job = row["stdout"].strip().split(";")[0]
            if not job.isdigit():
                raise RuntimeError("sbatch returned no numeric job id")
            receipt["jobs"][name] = job
    finally:
        client.close()
        write("submit_receipt.json", receipt)


def validate():
    jobs = json.loads((HERE / "submit_receipt.json").read_text())["jobs"]
    receipt = {"phase": "validate", "at": now(), "commands": {}, "checks": {}}
    client = connect()
    for name, job in jobs.items():
        row = run(client, ["scontrol", "show", "job", job, "-o"], receipt, "held:" + name)
        fields = dict(part.split("=", 1) for part in row["stdout"].split() if "=" in part)
        group = SPEC["groups"][name]
        # A pending job shows its node bounds as "1-1" (same rule as the retest's held validation);
        # ReqTRES must still request exactly one node.
        expected = {"JobState": "PENDING", "Account": "che260157", "Partition": "wholenode",
                    "NumCPUs": "128", "NumTasks": "128", "CPUs/Task": "1", "Requeue": "0",
                    "Dependency": "(null)", "TimeLimit": group["time_limit"], "JobName": "pa-fgd-" + name,
                    "Command": SPEC["slurm"]["path"]}
        bad = {k: fields.get(k) for k, v in expected.items() if fields.get(k) != v}
        if fields.get("NumNodes") not in {"1", "1-1"}:
            bad["NumNodes"] = fields.get("NumNodes")
        tres = dict(part.split("=", 1) for part in fields.get("ReqTRES", "").split(",") if "=" in part)
        if tres.get("node") != "1" or tres.get("cpu") != "128" or tres.get("billing") != "128":
            bad["ReqTRES"] = fields.get("ReqTRES")
        # SubmitLine contains spaces, so check the raw record rather than the split fields.
        export = "--export=ALL,STS_DIAG_GROUP=" + name + ",STS_DIAG_SPEC_SHA256=" + spec_sha() + " "
        if row["stdout"].count(export) != 1:
            bad["SubmitLine"] = "group/spec pin absent from the submitted environment"
        held = fields.get("Reason") == "JobHeldUser" or fields.get("Priority") == "0"
        receipt["checks"][name] = {"job": job, "mismatches": bad, "held": held,
                                   "max_cpu_su": group["max_cpu_su"]}
    client.close()
    receipt["passed"] = all(not c["mismatches"] and c["held"] for c in receipt["checks"].values())
    receipt["supersedes"] = ["validate_receipt.json (refused on the pending NumNodes=1-1 representation)",
                             "validate_receipt_v2.json (refused by a whitespace-split SubmitLine parse)"]
    write("validate_receipt_v3.json", receipt)
    if not receipt["passed"]:
        raise SystemExit("held shape differs")


def release():
    if not json.loads((HERE / "validate_receipt_v3.json").read_text())["passed"]:
        raise SystemExit("held shape not validated")
    jobs = json.loads((HERE / "submit_receipt.json").read_text())["jobs"]
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
