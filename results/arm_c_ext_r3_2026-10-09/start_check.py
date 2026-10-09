"""Read-only start check of round 3, run a few minutes after release in place of a canary.

QE must read each moved density exactly as round 2 did. The first iteration's accuracy is computed before
any mixing, and round 2's canary and main array printed it to the same 8 digits on different nodes, so each
round-3 job must print round 2's first "negative rho (up, down)" line and first "estimated scf accuracy" line
for the same state. This script reads those two lines from each job's output on Anvil (grep only) and from
round 2's committed mirror, and writes start_check_<UTC stamp>.json beside itself (never overwrites).
On a mismatch the array is cancelled by hand and the mismatch investigated (design record, Round 3).
"""
import datetime as dt
import json
import posixpath
import re
import shlex
from pathlib import Path

import paramiko

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PLAN = json.loads((HERE / "ext_plan.json").read_text(encoding="utf-8"))
REMOTE = "/anvil/projects/x-che260157/sts_arm_c_ext_r3_2026-10-09"
R2_MIRROR = ROOT / "results/arm_c_ext_r2_2026-10-08/raw_mirror/runs"
PATTERNS = {"negative_rho": r"negative rho \(up, down\):.*", "accuracy": r"estimated scf accuracy\s+<.*"}


def first_lines(text):
    """The first line matching each pattern, whitespace-normalised; None where absent."""
    found = {}
    for key, pattern in PATTERNS.items():
        match = re.search(pattern, text)
        found[key] = " ".join(match.group(0).split()) if match else None
    return found


def expected(row):
    site = row["dir"].rsplit("/", 1)[-1]
    out = R2_MIRROR / "hea/arm_c_ext_r2_2026-10-08" / site / (row["round_2_job"] + ".out")
    return first_lines(out.read_text(errors="replace"))


def main():
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    client = paramiko.SSHClient()
    client.load_host_keys(str(Path.home() / ".ssh/known_hosts"))
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect("anvil.rcac.purdue.edu", username="x-fcai3", key_filename=str(Path.home() / ".ssh/id_ed25519"),
                   allow_agent=False, look_for_keys=False, timeout=20, banner_timeout=20, auth_timeout=20)
    jobs = []
    try:
        for row in PLAN["selection"]:
            out = posixpath.join(REMOTE, "runs", row["dir"], row["job"] + ".out")
            command = ("if [ -e {0} ]; then grep -m1 -E 'negative rho \\(up, down\\):' {0}; "
                       "grep -m1 'estimated scf accuracy' {0}; else echo ABSENT; fi").format(shlex.quote(out))
            _, stdout, stderr = client.exec_command(command, timeout=60)
            text, err = stdout.read().decode(), stderr.read().decode()
            found = None if text.strip() == "ABSENT" else first_lines(text)
            want = expected(row)
            jobs.append({"job": row["job"], "dir": row["dir"], "expected": want, "found": found, "stderr": err,
                         "match": None if found is None or found["accuracy"] is None else found == want})
    finally:
        client.close()
    receipt = {"at": dt.datetime.now(dt.timezone.utc).isoformat(), "readonly": True, "jobs": jobs,
               "all_started": all(j["match"] is not None for j in jobs),
               "all_match": all(j["match"] for j in jobs)}
    with (HERE / ("start_check_" + stamp + ".json")).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"all_started": receipt["all_started"], "all_match": receipt["all_match"]}), flush=True)


if __name__ == "__main__":
    main()
