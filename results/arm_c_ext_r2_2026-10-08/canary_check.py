"""Read-only check of the two round-2 canary SCFs before the main array is released (no writes on Anvil).

A canary passes when:
- QE read the rebuilt seed ("The initial density is read from file") and printed no error;
- QE read the moved density as built: before its first iteration it printed no "renormalised" line, and its
  "negative rho (up, down)" matches canary_expectations.json within 1% (an FFT of the staged file);
- no IEEE_INVALID/OVERFLOW/DIVIDE_BY_ZERO note was raised (such a note would reject every main run);
- it ran at least three SCF iterations and either stopped at the registered eight-iteration ceiling or
  completed with a COMPLETE runner receipt;
- its accuracy at its last iteration is below the production run's at the same iteration (production
  started from atomic densities and stalled; the seed must at least get ahead of it).
Both canaries must pass. Nothing is written until both canaries have runner receipts, so running this
early never blocks the gate. The seeded run's moments are recorded next to the seed's, and so is whether
QE stopped gracefully ("JOB DONE."): gfortran prints its IEEE notes only then, so for a killed run the
IEEE criterion shows nothing.
"""
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

import paramiko

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REMOTE = "/anvil/projects/x-che260157/sts_arm_c_ext_r2_2026-10-08"
SPEC = json.loads((HERE / "launch_spec.json").read_text(encoding="utf-8"))
MIRRORS = {"sts_arm_c_2026-10-07": ROOT / "results/arm_c_2026-10-07/raw_mirror",
           "sts_arm_c_2026-10-07_rerun": ROOT / "results/arm_c_2026-10-07_rerun/raw_mirror"}
ERRORS = re.compile(r"Error in routine|MPI_ABORT|SIGSEGV|Segmentation fault|forrtl:\s*severe")
SEVERE = re.compile(r"IEEE_(?:INVALID_FLAG|OVERFLOW_FLAG|DIVIDE_BY_ZERO)")
ACCURACY = re.compile(r"estimated scf accuracy\s+<\s+([0-9.Ee+-]+) Ry")
NEGATIVE = re.compile(r"negative rho \(up, ?down\):\s+([0-9.Ee+-]+)\s+([0-9.Ee+-]+)")
EXPECTED = HERE / "canary_expectations.json"


def summarize(text):
    iterations = [int(x) for x in re.findall(r"iteration\s*#\s*(\d+)", text)]
    accuracy = [float(x) for x in ACCURACY.findall(text)]
    charge = re.search(r"starting charge\s+([0-9.]+), renormalised to\s+([0-9.]+)", text)
    total = re.findall(r"total magnetization\s+=\s+(-?[0-9.]+)", text)
    absolute = re.findall(r"absolute magnetization\s+=\s+(-?[0-9.]+)", text)
    start = text.split("The initial density is read from file", 1)[1] if "The initial density is read from file" in text else ""
    start = re.split(r"iteration\s*#\s*1\b", start, maxsplit=1)[0]
    negative = NEGATIVE.search(start)
    return {"density_read": "The initial density is read from file" in text,
            "starting_charge": [float(charge[1]), float(charge[2])] if charge else None,
            "renormalised": "renormalised to" in start,
            "start_negative_rho": [float(negative[1]), float(negative[2])] if negative else None,
            "graceful_stop": "JOB DONE." in text,
            "errors": sorted(set(ERRORS.findall(text))),
            "ieee": sorted(set(SEVERE.findall(text))),
            "iterations": max(iterations) if iterations else 0,
            "accuracy_Ry": accuracy,
            "last_total_magnetization": float(total[-1]) if total else None,
            "last_absolute_magnetization": float(absolute[-1]) if absolute else None}


def as_built(seeded, expected):
    """QE printed no rescale before its first iteration and the predicted negative charge, within 1%."""
    found = seeded["start_negative_rho"]
    return bool(expected is not None and found is not None and not seeded["renormalised"]
                and all(abs(a - b) <= 0.01 * b for a, b in zip(found, expected)))


def judge(seeded, production, receipt, expected):
    """True if a canary passed (see the module docstring); expected = predicted negative rho (up, down)."""
    stopped = receipt.get("reason") == "SCF iteration ceiling" or receipt.get("status") == "COMPLETE"
    k = min(len(seeded["accuracy_Ry"]), len(production["accuracy_Ry"]))
    ahead = k > 0 and seeded["accuracy_Ry"][k - 1] < production["accuracy_Ry"][k - 1]
    return bool(seeded["density_read"] and as_built(seeded, expected) and not seeded["errors"] and not seeded["ieee"]
                and seeded["iterations"] >= 3 and stopped and ahead)


def expected_start(job):
    """Predicted negative rho (up, down) of the density a canary job reads (canary_expectations.json)."""
    targets = json.loads(EXPECTED.read_text(encoding="utf-8"))["targets"]
    row = targets[job["job"] + "@" + job["dir"].rsplit("/", 1)[-1]]
    if row["density_sha256"] != job["scratch_source"]["files"]["charge-density.hdf5"]:
        raise SystemExit("expectation is for a different density: " + job["dir"])
    return [row["negative_rho_up"], row["negative_rho_down"]]


def production_output(source_deck):
    """Local mirror path of the production run's output, from its deck path (runs/...)."""
    return ROOT / "results/arm_c_2026-10-07/raw_mirror" / Path(source_deck).with_suffix(".out")


def seed_output(save_dir):
    """Local mirror path of the seed's own output, from its Anvil save directory."""
    project = save_dir.split("/")[4]
    relative = save_dir.split("/runs/", 1)[1].rsplit("/tmp_", 1)[0]
    job = save_dir.rsplit("/", 1)[1][:-len(".save")]
    return MIRRORS[project] / "runs" / relative / (job + ".out")


def main():
    expected = {job["dir"]: expected_start(job) for job in SPEC["stages"]["r2_canary"]["jobs"]}
    client = paramiko.SSHClient()
    client.load_host_keys(str(Path.home() / ".ssh/known_hosts"))
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect("anvil.rcac.purdue.edu", username="x-fcai3", key_filename=str(Path.home() / ".ssh/id_ed25519"),
                   allow_agent=False, look_for_keys=False, timeout=20, banner_timeout=20, auth_timeout=20)
    receipt = {"at": dt.datetime.now(dt.timezone.utc).isoformat(), "readonly": True, "canaries": [], "passed": False}
    try:
        sftp = client.open_sftp()
        for job in SPEC["stages"]["r2_canary"]["jobs"]:
            base = f"{REMOTE}/runs/{job['dir']}/{job['job']}"
            try:
                sftp.stat(base + ".qc.json")
            except FileNotFoundError:
                print(json.dumps({"finished": False, "job": job["dir"]}), flush=True)
                sys.exit(3)  # not finished: write nothing, so the gate is never blocked by an early run
            local = HERE / "canary_mirror" / job["dir"]
            local.mkdir(parents=True, exist_ok=True)
            files = {}
            for suffix in (".out", ".qc.json", ".KILLED", ".REJECTED"):
                try:
                    sftp.stat(base + suffix)
                except FileNotFoundError:
                    continue
                target = local / (job["job"] + suffix)
                sftp.get(base + suffix, str(target))
                files[suffix] = hashlib.sha256(target.read_bytes()).hexdigest()
            text = (local / (job["job"] + ".out")).read_text(errors="replace") if ".out" in files else ""
            runner = json.loads((local / (job["job"] + ".qc.json")).read_text())
            production = summarize(production_output(job["source_deck"]).read_text(errors="replace"))
            seed = summarize(seed_output(job["seed"]["save_dir"]).read_text(errors="replace"))
            seeded = summarize(text)
            receipt["canaries"].append({
                "dir": job["dir"], "job": job["job"], "files_sha256": files, "seeded": seeded,
                "runner_status": runner.get("status"), "runner_reason": runner.get("reason"),
                "production_accuracy_Ry": production["accuracy_Ry"][:max(seeded["iterations"], 1)],
                "expected_start_negative_rho": expected[job["dir"]], "read_as_built": as_built(seeded, expected[job["dir"]]),
                "seed": {"job": job["seed"]["job"], "total_magnetization": seed["last_total_magnetization"],
                         "absolute_magnetization": seed["last_absolute_magnetization"]},
                "passed": judge(seeded, production, runner, expected[job["dir"]])})
    finally:
        client.close()
    receipt["passed"] = len(receipt["canaries"]) == 2 and all(c["passed"] for c in receipt["canaries"])
    with (HERE / "canary_check.json").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"passed": receipt["passed"],
                      "canaries": [{k: c[k] for k in ("job", "passed", "runner_reason", "read_as_built")} for c in receipt["canaries"]]}),
          flush=True)


if __name__ == "__main__":
    main()
