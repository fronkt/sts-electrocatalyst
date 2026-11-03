"""Stage, preflight, held-submit, validate and release the corpus-escape continuation: the six tier 1a escape
relaxations restarted from their last computed geometry (results/corpus_escape_2026-11-01/launch_ops.py, the same
operations, on a new dated Anvil root).

Design note: docs/research/corpus-escape-2026-11-01.md, section "Tier 1a continuation". One launch group, tier1a_cont,
with one stage (one array, six tasks); the held arms are not rerun.

Usage (local, background worker): python results/corpus_escape_cont_2026-11-02/launch_ops.py <phase> [arg]
  stage <upf_dir>   copy the committed bytes of a pushed commit to the dated Anvil root (inputs read-only), verify
                    sha256; upload the 12 deposited UPF files from <upf_dir> into <root>/pseudo after checking each
                    against the MD5 the deposited Xu outputs print (a differing file refuses before Anvil is touched)
  preflight <group> the runner's own --preflight for both stages of the group (decks, manifests, runner files and
                    UPF MD5s), Python 3.9 imports, QE binaries, mybalance >= the group's reservation, no corpus-escape
                    job already queued, free project space, remote spec/Slurm sha256, Slurm syntax
  submit <group>    `sbatch --hold --parsable --no-requeue --exclude=<spec exclusions>`, one array per stage
  validate <group>  scontrol shape of the held arrays
  release <group>   `scontrol release` of both arrays, only after validate has passed
Every phase writes its own receipt; no phase ever resubmits or retries a job. Intent files block an automatic second
submit or release of a group: if a phase fails partway, a held array may remain on Anvil, and it is inspected and
then cancelled or released by hand, with the action recorded.
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
HERE = ROOT / "results/corpus_escape_cont_2026-11-02"
SPEC_REL = "results/corpus_escape_cont_2026-11-02/launch_spec.json"
SLURM_REL = "anvil/107_corpus_escape_cont.slurm"
SPEC = json.loads((ROOT / SPEC_REL).read_text(encoding="utf-8"))
REMOTE = "/anvil/projects/x-che260157/sts_corpus_escape_cont_2026-11-02"
PROJECT = "/anvil/projects/x-che260157"
PYTHON = "/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3"
GROUPS = SPEC["launch_groups"]
NAMES = {"held": "ce-held", "escape": "ce-esc"}
MIN_FREE_PROJECT_TB = 0.1  # retained wavefunctions are about 1.5-3 GB per run at the default band count
STAGE = dict(SPEC["files"])
STAGE[SPEC_REL] = None
STAGE[SLURM_REL] = None


def arrays(group, rows=None):
    """Stage name -> Slurm shape for one launch group (all rows of a stage run at once).

    rows (2026-11-01, Frank: "run tier 1b if there's room"): an optional subset of the group's 1-based rows, the same
    rows in both stages, for when the balance holds less than the whole group's reservation. Rows keep their manifest
    numbers, so the runner, manifests, decks and spec are unchanged."""
    out = {}
    for stage in GROUPS[group]["stages"]:
        g = SPEC["stages"][stage]
        n, minutes = len(g["jobs"]), g["wall_minutes"]
        if rows:
            array, tasks = ",".join(map(str, rows)) + "%%%d" % len(rows), len(rows)
        else:
            array, tasks = "1-%d%%%d" % (n, n), n
        out[stage] = {"array": array, "tasks": tasks, "throttle": str(tasks), "minutes": minutes,
                      "time": "%02d:%02d:00" % divmod(minutes, 60),
                      "name": "%s-%s" % (NAMES[stage.rsplit("_", 1)[1]], group)}
    return out


def ceiling(shape):
    """Slurm reservation of a shape in CPU SU: tasks x wall minutes x 128 cores."""
    return sum(s["tasks"] * s["minutes"] * 128 // 60 for s in shape.values())


def rows_arg(group, value):
    """'3,4' -> [3, 4]: distinct rows of the group, in manifest order."""
    n = len(SPEC["stages"][GROUPS[group]["stages"][0]]["jobs"])
    rows = sorted({int(x) for x in value.split(",") if x.strip()})
    if not rows or rows[0] < 1 or rows[-1] > n or len(rows) == n:
        raise SystemExit("rows must be a proper subset of 1-%d" % n)
    return rows


def chosen_rows(group):
    """The rows the passed preflight receipt recorded; submit, validate and release cannot choose others."""
    return json.loads((HERE / ("preflight_%s_receipt.json" % group)).read_text()).get("rows")   # absent before rows


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


def group_arg(value):
    if value not in GROUPS:
        raise SystemExit("launch group must be one of " + ", ".join(GROUPS))
    return value


def stage(upf_dir):
    upf_dir = Path(upf_dir)
    upfs = {}
    for name, md5 in SPEC["pseudo_md5"].items():  # every deposited UPF, verified before Anvil is touched
        path = upf_dir / name
        if not path.is_file():
            raise SystemExit("missing deposited UPF: " + str(path))
        data = path.read_bytes()
        if hashlib.md5(data).hexdigest() != md5:
            raise SystemExit("UPF differs from the MD5 the deposited outputs print: " + name)
        upfs[name] = (data, md5)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    remote = subprocess.check_output(["git", "ls-remote", "origin", "refs/heads/r0-catalysis-revival"], cwd=ROOT,
                                     text=True).split()[0]
    if subprocess.run(["git", "merge-base", "--is-ancestor", commit, remote], cwd=ROOT).returncode:
        raise SystemExit("launch commit is not pushed")
    receipt = {"phase": "stage", "at": now(), "commit": commit, "files": [], "pseudo": [], "commands": {},
               "completed": False}
    blobs = {}
    for rel, pin in sorted(STAGE.items()):
        data = subprocess.check_output(["git", "show", commit + ":" + rel], cwd=ROOT)
        digest = hashlib.sha256(data).hexdigest()
        if b"\r" in data or (pin and digest != pin) or digest != sha(rel):
            raise SystemExit("committed bytes differ from the pin or the working copy: " + rel)
        blobs[rel] = (REMOTE + "/" + rel, data, digest)
    client = connect()
    client.get_transport().set_keepalive(30)
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
        run(client, ["mkdir", REMOTE + "/pseudo"], receipt, "pseudo_dir")
        for name, (data, md5) in sorted(upfs.items()):
            target = REMOTE + "/pseudo/" + name
            with sftp.open(target, "wb") as stream:
                stream.write(data)
            row = run(client, ["md5sum", target], receipt, "md5:" + name)
            if row["stdout"].split()[0] != md5:
                raise SystemExit("remote UPF differs: " + name)
            run(client, ["chmod", "0444", target], receipt, "chmod:" + name)
            receipt["pseudo"].append({"name": name, "remote_path": target, "md5": md5,
                                      "sha256": hashlib.sha256(data).hexdigest()})
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


def preflight(group, rows=None):
    staged = json.loads((HERE / "stage_receipt.json").read_text(encoding="utf-8"))
    if not staged.get("completed") or staged.get("spec_sha256") != sha(SPEC_REL):
        raise SystemExit("staging is not complete for this spec")
    shape = arrays(group, rows)
    receipt = {"phase": "preflight", "group": group, "rows": rows, "at": now(), "commands": {},
               "spec_sha256": sha(SPEC_REL), "slurm_sha256": sha(SLURM_REL)}
    client = connect()
    runner = REMOTE + "/src/dft/research_batch_seeded.py"
    spec = REMOTE + "/" + SPEC_REL
    for stage_name in shape:
        run(client, [PYTHON, "-B", runner, "--spec", spec, "--root", REMOTE, "--stage", stage_name,
                     "--pseudo", REMOTE + "/pseudo", "--preflight"], receipt, "preflight:" + stage_name, timeout=900)
    run(client, [PYTHON, "-B", "-c", "import sys; sys.path.insert(0, sys.argv[1]); "
                 "import research_batch_seeded, projection_qc, hea_panel_readout, hea_geometry; print('IMPORTS_OK')",
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
    balance = [line.split() for line in receipt["commands"]["mybalance"]["stdout"].splitlines()
               if line.startswith("che260157 ")]
    receipt["balance_su"] = float(balance[0][-1]) if balance else None
    receipt["reservation_su"] = ceiling(shape)
    if not rows and receipt["reservation_su"] != SPEC["allocation"]["group_ceilings_cpu_su"][group]:
        raise SystemExit("whole-group reservation differs from the spec")
    receipt["queued_jobs"] = [line for line in queue["stdout"].splitlines() if line.strip()]
    receipt["queued_corpus_escape_jobs"] = [line for line in receipt["queued_jobs"]
                                            if "|ce-held-" in line or "|ce-esc-" in line]
    found = {line.split()[1].rsplit("/", 1)[-1]: line.split()[0]
             for line in binaries["stdout"].splitlines() if line.strip()}
    receipt["qe_binaries_match"] = found == SPEC["qe_binaries_sha256"]
    receipt["project_free_TB"] = project_free_tb(receipt["commands"]["myquota"]["stdout"])
    receipt["passed"] = (all(receipt["commands"]["preflight:" + s]["stdout"].strip() == "VALID" for s in shape)
                         and receipt["commands"]["imports"]["stdout"].strip() == "IMPORTS_OK"
                         and shas.get(spec) == receipt["spec_sha256"]
                         and shas.get(REMOTE + "/" + SLURM_REL) == receipt["slurm_sha256"]
                         and not receipt["queued_corpus_escape_jobs"]
                         and receipt["balance_su"] is not None
                         and receipt["balance_su"] >= receipt["reservation_su"]
                         and receipt["qe_binaries_match"]
                         and receipt["project_free_TB"] is not None
                         and receipt["project_free_TB"] >= MIN_FREE_PROJECT_TB)
    write("preflight_%s_receipt.json" % group, receipt)
    if not receipt["passed"]:
        raise SystemExit("preflight did not pass")


def submit(group):
    if not json.loads((HERE / ("preflight_%s_receipt.json" % group)).read_text())["passed"]:
        raise SystemExit("preflight has not passed for " + group)
    rows = chosen_rows(group)
    shape = arrays(group, rows)
    receipt = {"phase": "submit", "group": group, "rows": rows, "at": now(), "commands": {}, "jobs": {},
               "spec_sha256": sha(SPEC_REL)}
    with (HERE / ("submit_%s_intent.json" % group)).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps({"at": now(), "arrays": shape}) + "\n")
    client = connect()
    try:
        for stage_name, s in shape.items():
            args = ["sbatch", "--hold", "--parsable", "--no-requeue", "--array=" + s["array"],
                    "--time=" + s["time"], "--job-name=" + s["name"], "--exclude=" + SPEC["exclusions"],
                    "--export=ALL,STAGE=" + stage_name, REMOTE + "/" + SLURM_REL]
            row = run(client, args, receipt, "sbatch:" + stage_name)
            job = row["stdout"].strip().split(";")[0]
            if not job.isdigit():
                raise RuntimeError("sbatch returned no numeric job id")
            receipt["jobs"][stage_name] = job
    finally:
        client.close()
        write("submit_%s_receipt.json" % group, receipt)


def validate(group):
    rows = chosen_rows(group)
    shape = arrays(group, rows)
    jobs = json.loads((HERE / ("submit_%s_receipt.json" % group)).read_text())["jobs"]
    if set(jobs) != set(shape):
        raise SystemExit("exactly the group's arrays are required, found " + json.dumps(jobs))
    receipt = {"phase": "validate", "group": group, "rows": rows, "at": now(), "commands": {}, "checks": {}}
    client = connect()
    for stage_name, job in jobs.items():
        s = shape[stage_name]
        row = run(client, ["scontrol", "show", "job", job, "-o"], receipt, "held:" + stage_name)
        records = [line for line in row["stdout"].splitlines() if line.strip()]
        bad = {}
        if len(records) != 1:
            bad["records"] = len(records)
        fields = dict(part.split("=", 1) for part in records[0].split() if "=" in part) if records else {}
        expected = {"JobState": "PENDING", "Account": "che260157", "Partition": "wholenode",
                    "NumCPUs": "128", "NumTasks": "128", "CPUs/Task": "1", "Requeue": "0",
                    "Dependency": "(null)", "TimeLimit": s["time"], "JobName": s["name"],
                    "Command": REMOTE + "/" + SLURM_REL, "ArrayTaskThrottle": s["throttle"]}
        bad.update({k: fields.get(k) for k, v in expected.items() if fields.get(k) != v})
        # A pending array prints its task list with the throttle ("1-6%6"); a one-task subset may print it bare.
        if fields.get("ArrayTaskId") not in ({s["array"], s["array"].split("%")[0]} if rows else {s["array"]}):
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
        su = s["tasks"] * s["minutes"] * 128 // 60
        full = SPEC["allocation"]["stage_ceilings_cpu_su"][stage_name]
        if su != (full * s["tasks"] // len(SPEC["stages"][stage_name]["jobs"]) if rows else full):
            bad["ceiling"] = su
        receipt["checks"][stage_name] = {"job": job, "mismatches": bad, "held": held, "ceiling_cpu_su": su}
    client.close()
    total = sum(c["ceiling_cpu_su"] for c in receipt["checks"].values())
    receipt["group_ceiling_cpu_su"] = total
    receipt["passed"] = (len(receipt["checks"]) == len(shape)
                         and total == (ceiling(shape) if rows else SPEC["allocation"]["group_ceilings_cpu_su"][group])
                         and all(not c["mismatches"] and c["held"] for c in receipt["checks"].values()))
    write("validate_%s_receipt.json" % group, receipt)
    if not receipt["passed"]:
        raise SystemExit("held shape differs")


def release(group):
    if not json.loads((HERE / ("validate_%s_receipt.json" % group)).read_text())["passed"]:
        raise SystemExit("held shape not validated")
    shape = arrays(group, chosen_rows(group))
    jobs = json.loads((HERE / ("submit_%s_receipt.json" % group)).read_text())["jobs"]
    if set(jobs) != set(shape):
        raise SystemExit("exactly the group's arrays are required")
    receipt = {"phase": "release", "group": group, "at": now(), "commands": {}, "released": {}}
    with (HERE / ("release_%s_intent.json" % group)).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps({"at": now(), "jobs": jobs}) + "\n")
    client = connect()
    try:
        for stage_name, job in jobs.items():
            run(client, ["scontrol", "release", job], receipt, "release:" + stage_name)
            receipt["released"][stage_name] = job
        run(client, ["squeue", "-u", "x-fcai3", "-o", "%i|%j|%T|%M|%l|%R"], receipt, "after")
    finally:
        client.close()
        write("release_%s_receipt.json" % group, receipt)


if __name__ == "__main__":
    phase = sys.argv[1]
    if phase == "stage":
        stage(sys.argv[2])
    elif phase == "preflight" and len(sys.argv) > 3:
        preflight(group_arg(sys.argv[2]), rows_arg(sys.argv[2], sys.argv[3]))
    else:
        {"preflight": preflight, "submit": submit, "validate": validate, "release": release}[phase](group_arg(sys.argv[2]))
