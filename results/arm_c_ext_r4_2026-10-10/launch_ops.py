"""Stage, preflight, held-submit, validate and release round 4 of the S8 arm-C extension.

Decisions of record: Frank, 2026-10-08, "Let's rerun DFT for those and get values for them." and "repair";
Frank, 2026-10-09, "Lets do a round 3"; Frank, 2026-10-10, "Do the Fe25 O run"
(docs/research/s8-arm-c-extension-2026-10-08.md).

Usage (local, background worker): python launch_ops.py <phase> [array]
  stage     copy the committed bytes of a pushed commit to the dated Anvil root (inputs read-only), verify
            sha256; copy the bundle's density and XML from round 3's stopped save on Anvil, verifying the
            source before and the copy after against the spec's scratch_source pins (the rebuilt occup.txt and
            paw.txt are uploaded with the other committed files)
  preflight the seeded runner's own --preflight (it re-verifies every bundle file), Python 3.9 imports, QE
            binaries, mybalance, an empty queue, free project space and the remote spec/Slurm sha256
  submit    one `sbatch --hold --parsable --no-requeue --exclude=<spec exclusions>` array: r4_main (1-1%1, 345 min)
  validate  scontrol shape of the held array
  release   `release main`, only after validate has passed (no canary in this round)
Every phase writes its own receipt; no phase ever resubmits or retries a job. The intent files block an
automatic second submit or release: if a phase fails partway, a held array may remain on Anvil, and it is
inspected and then cancelled or released by hand, with the action recorded.
Receipts are created, never overwritten. Before a failed phase is run again, its receipt is moved aside under a
dated name and the move recorded; a stage that failed after its first upload leaves a partial read-only root,
which is inspected, removed by hand (chmod u+w, rm -r) and recorded before staging again, since stage refuses an
existing root. Preflight refuses any queued job of the user's, including unrelated ones: wait, or record why not.
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
HERE = ROOT / "results/arm_c_ext_r4_2026-10-10"
SPEC_REL = "results/arm_c_ext_r4_2026-10-10/launch_spec.json"
PLAN_REL = "results/arm_c_ext_r4_2026-10-10/ext_plan.json"
SLURM_REL = "anvil/99_arm_c_ext_r4.slurm"
SPEC = json.loads((ROOT / SPEC_REL).read_text(encoding="utf-8"))
PLAN = json.loads((ROOT / PLAN_REL).read_text(encoding="utf-8"))
REMOTE = "/anvil/projects/x-che260157/sts_arm_c_ext_r4_2026-10-10"
PROJECT = "/anvil/projects/x-che260157"
PYTHON = "/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3"
ARRAYS = {"r4_main": {"array": "1-1%1", "tasks": 1, "throttle": "1", "name": "arm-c-ext-r4-main",
                      "time": "05:45:00", "minutes": 345}}
RELEASE = {"main": "r4_main"}
MIN_FREE_PROJECT_TB = 0.1  # about 18 GB of retained wavefunctions per SCF
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


def bundle_pins():
    return {job["scratch_source"]["save_dir"]: job["scratch_source"]["files"] for job in SPEC["stages"]["r4_main"]["jobs"]}


def seed_copies():
    """(remote source in round 3's save, remote target, pinned sha256) for every file the bundle copies on Anvil."""
    pins = bundle_pins()
    copies = []
    for row in PLAN["selection"]:
        for name, source in row["remote_copy"].items():
            copies.append((source, REMOTE + "/" + row["bundle"] + "/" + name, pins[row["bundle"]][name]))
    return copies


def stage():
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    remote = subprocess.check_output(["git", "ls-remote", "origin", "refs/heads/r0-catalysis-revival"], cwd=ROOT, text=True).split()[0]
    if subprocess.run(["git", "merge-base", "--is-ancestor", commit, remote], cwd=ROOT).returncode:
        raise SystemExit("launch commit is not pushed")
    receipt = {"phase": "stage", "at": now(), "commit": commit, "files": [], "seed_copies": [],
               "commands": {}, "completed": False}
    # Read and verify every committed blob before touching Anvil, so a pin or line-ending
    # mismatch can never leave a half-staged, read-only root behind.
    blobs = {}
    for rel, pin in sorted(STAGE.items()):
        data = subprocess.check_output(["git", "show", commit + ":" + rel], cwd=ROOT)
        digest = hashlib.sha256(data).hexdigest()
        if b"\r" in data or (pin and digest != pin) or digest != sha(rel):
            raise SystemExit("committed bytes differ from the pin or the working copy: " + rel)
        blobs[rel] = (REMOTE + "/" + rel, data, digest)
    copies = seed_copies()
    client = connect()
    client.get_transport().set_keepalive(30)
    try:
        sftp = client.open_sftp()
        run(client, ["test", "!", "-e", REMOTE], receipt, "root_absent")
        for source, _, pin in copies:  # every source must still match its pin before staging starts
            row = run(client, ["sha256sum", source], receipt, "source_sha:" + source, timeout=900)
            if row["stdout"].split()[0] != pin:
                raise SystemExit("round-3 save file drifted on Anvil: " + source)
        for rel, (target, data, digest) in sorted(blobs.items()):
            run(client, ["mkdir", "-p", posixpath.dirname(target)], receipt, "mkdir:" + rel)
            with sftp.open(target, "wb") as stream:
                stream.write(data)
            row = run(client, ["sha256sum", target], receipt, "sha:" + rel)
            if row["stdout"].split()[0] != digest:
                raise SystemExit("remote bytes differ: " + rel)
            run(client, ["chmod", "0444", target], receipt, "chmod:" + rel)
            receipt["files"].append({"repo_path": rel, "remote_path": target, "sha256": digest})
        for source, target, pin in copies:
            run(client, ["test", "!", "-e", target], receipt, "absent:" + target)
            run(client, ["cp", "--no-preserve=mode,ownership", source, target], receipt, "copy:" + target, timeout=900)
            row = run(client, ["sha256sum", target], receipt, "copy_sha:" + target, timeout=900)
            if row["stdout"].split()[0] != pin:
                raise SystemExit("copy differs from its pin: " + target)
            run(client, ["chmod", "0444", target], receipt, "copy_chmod:" + target)
            receipt["seed_copies"].append({"source": source, "target": target, "sha256": pin})
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
    runner = REMOTE + "/src/dft/research_batch_seeded.py"
    spec = REMOTE + "/" + SPEC_REL
    for stage_name in ARRAYS:
        run(client, [PYTHON, "-B", runner, "--spec", spec, "--root", REMOTE, "--stage", stage_name,
                     "--pseudo", PROJECT + "/pseudo", "--preflight"], receipt, "preflight:" + stage_name, timeout=900)
    run(client, [PYTHON, "-B", "-c", "import sys; sys.path.insert(0, sys.argv[1]); "
                 "import research_batch_seeded, projection_qc, hea_force_audit, hea_followup_qc; print('IMPORTS_OK')",
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
                         and receipt["balance_su"] >= SPEC["allocation"]["this_launch_ceiling_cpu_su"]
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
                    "--time=" + shape["time"], "--job-name=" + shape["name"], "--exclude=" + SPEC["exclusions"],
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
        raise SystemExit("exactly the registered array is required, found " + json.dumps(jobs))
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
                    "Dependency": "(null)", "TimeLimit": shape["time"], "JobName": shape["name"],
                    "Command": REMOTE + "/" + SLURM_REL}
        bad.update({k: fields.get(k) for k, v in expected.items() if fields.get(k) != v})
        # one task: Slurm may print the range as 1, 1-1 or with the throttle appended; it must be task 1 only
        if fields.get("ArrayTaskId", "").split("%")[0] not in {"1", "1-1"}:
            bad["ArrayTaskId"] = fields.get("ArrayTaskId")
        if fields.get("NumNodes") not in {"1", "1-1"}:
            bad["NumNodes"] = fields.get("NumNodes")
        tres = dict(part.split("=", 1) for part in fields.get("ReqTRES", "").split(",") if "=" in part)
        if tres.get("node") != "1" or tres.get("cpu") != "128" or tres.get("billing") != "128":
            bad["ReqTRES"] = fields.get("ReqTRES")
        if row["stdout"].count("--export=ALL,STAGE=" + stage_name + " ") != 1:
            bad["SubmitLine"] = "stage export absent from the submit line"
        if row["stdout"].count("--exclude=" + SPEC["exclusions"] + " ") != 1 or fields.get("ExcNodeList") in (None, "(null)"):
            bad["ExcNodeList"] = fields.get("ExcNodeList")
        held = fields.get("Reason") == "JobHeldUser" or fields.get("Priority") == "0"
        su = shape["tasks"] * shape["minutes"] * 128 // 60
        if su != SPEC["allocation"]["stage_ceilings_cpu_su"][stage_name]:
            bad["ceiling"] = su
        receipt["checks"][stage_name] = {"job": job, "mismatches": bad, "held": held, "ceiling_cpu_su": su}
    client.close()
    total = sum(c["ceiling_cpu_su"] for c in receipt["checks"].values())
    receipt["launch_ceiling_cpu_su"] = total
    receipt["passed"] = (len(receipt["checks"]) == len(ARRAYS) and total == SPEC["allocation"]["this_launch_ceiling_cpu_su"]
                         and all(not c["mismatches"] and c["held"] for c in receipt["checks"].values()))
    write("validate_receipt.json", receipt)
    if not receipt["passed"]:
        raise SystemExit("held shape differs")


def release(which):
    stage_name = RELEASE[which]
    if not json.loads((HERE / "validate_receipt.json").read_text())["passed"]:
        raise SystemExit("held shape not validated")
    jobs = json.loads((HERE / "submit_receipt.json").read_text())["jobs"]
    if set(jobs) != set(ARRAYS):
        raise SystemExit("exactly the registered array is required")
    receipt = {"phase": "release", "array": stage_name, "at": now(), "commands": {}, "released": {}}
    with (HERE / ("release_" + which + "_intent.json")).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps({"at": now(), "job": jobs[stage_name], "stage": stage_name}) + "\n")
    client = connect()
    try:
        run(client, ["scontrol", "release", jobs[stage_name]], receipt, "release:" + stage_name)
        receipt["released"][stage_name] = jobs[stage_name]
        run(client, ["squeue", "-u", "x-fcai3", "-o", "%i|%j|%T|%M|%l|%R"], receipt, "after")
    finally:
        client.close()
        write("release_" + which + "_receipt.json", receipt)


if __name__ == "__main__":
    phase = sys.argv[1]
    if phase == "release":
        release(sys.argv[2])
    else:
        {"stage": stage, "preflight": preflight, "submit": submit, "validate": validate}[phase]()
