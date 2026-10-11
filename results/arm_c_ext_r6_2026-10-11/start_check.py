"""Read-only start check of round 6, run a few minutes after the jobs start.

QE must read each run's occupations as built and hold them. Its "STARTING HUBBARD OCCUPATIONS" block prints each
Hubbard atom's Tr[ns] (up, down, total) to 5 decimals and each occupation matrix to 3, and round 3's Fe25 O printed
its occup.txt that way to within 5e-6 and 5e-4 (tests/test_arm_c_ext_r4.py). So every printed atom's traces must
match the built occup.txt within 1e-5, and the replaced atom's two 5x5 matrices within 1.5e-3: that atom (Cr 19)
carries the other state's block, every other atom the run's own converged occupations. Once the first iteration has
finished, QE must also have reported reading the density from file and printed "RESET ns to initial values
(iter <= mixing_fixed_ns)".

The script reads the first lines of each job's output on Anvil (head only) and writes start_check_<UTC stamp>.json
beside itself (never overwrites). match is None while the first iteration is still running and the starting block
agrees; False on any disagreement. It also records the replaced atom's occupations as QE printed them after the
first iteration, before the reset. On a mismatch that job is cancelled by hand and the mismatch investigated (design
record, Round 6).
"""
import datetime as dt
import json
import posixpath
import re
import shlex
import sys
from pathlib import Path

import paramiko

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src/dft"))
import arm_c_ext_build as r1  # noqa: E402

PLAN = json.loads((HERE / "ext_plan.json").read_text(encoding="utf-8"))
REMOTE = "/anvil/projects/x-che260157/sts_arm_c_ext_r6_2026-10-11"
TOLERANCE = 1e-5
MATRIX_TOLERANCE = 1.5e-3
HEAD_LINES = 4000
TRACE = re.compile(r"Tr\[ns\(\s*(\d+)\)\] \(up, down, total\) =\s+(\S+)\s+(\S+)\s+(\S+)")
MATRIX = "occupation matrix ns (before diag.):"
BLOCK_END = "Number of occupied Hubbard levels"
STARTING = "STARTING HUBBARD OCCUPATIONS:"
RESET = "RESET ns to initial values (iter <= mixing_fixed_ns)"
READ = "The initial density is read from file"


def blocks_of(occup_text):
    values = r1.numbers(occup_text)
    return [values[k:k + r1.NS_BLOCK] for k in range(0, len(values), r1.NS_BLOCK)]


def traces(occup_text):
    """Tr[ns] (up, down, total) of every atom with a nonzero block, numbered from 1."""
    found = {}
    for atom, block in enumerate(blocks_of(occup_text), 1):
        if any(block):
            up, down = sum(block[k * 6] for k in range(5)), sum(block[25 + k * 6] for k in range(5))
            found[atom] = (up, down, up + down)
    return found


def matrices(occup_text, atom):
    """One atom's ns(m1, m2) for spin 1 and spin 2 (the file is Fortran-ordered, m1 fastest)."""
    block = blocks_of(occup_text)[atom - 1]
    return [[[block[25 * spin + m1 + 5 * m2] for m2 in range(5)] for m1 in range(5)] for spin in range(2)]


def printed_blocks(text):
    """Each printed occupation block, in order, as (start, end) offsets; the first follows STARTING."""
    spans, start = [], text.find(STARTING)
    while start >= 0:
        end = text.find(BLOCK_END, start)
        if end < 0:
            break
        spans.append((start, end))
        start = text.find("HUBBARD OCCUPATIONS", end)
    return spans


def printed_traces(text, span):
    return {int(m.group(1)): tuple(float(x) for x in m.group(2, 3, 4)) for m in TRACE.finditer(text, *span)}


def printed_matrices(text, span, atom):
    """The atom's two printed 'occupation matrix ns (before diag.)' blocks within one printed block."""
    head = text.find(f"ATOM {atom:4d} ", *span)
    if head < 0:
        return None
    tail = text.find("------------------------ ATOM", head + 1, span[1])
    section = text[head:tail if tail >= 0 else span[1]].split("\n")
    found = []
    for i, line in enumerate(section):
        if line.strip() == MATRIX:
            found.append([[float(x) for x in row.split()] for row in section[i + 1:i + 6]])
    return found if len(found) == 2 else None


def check(text, expected_text, atom):
    """Compare the starting block with the built occupations; confirm the read and the hold."""
    expected = traces(expected_text)
    spans = printed_blocks(text) if STARTING in text else []
    accuracy = re.search(r"estimated scf accuracy\s+<.*", text)
    result = {"density_read": READ in text, "held": RESET in text,
              "first_accuracy": " ".join(accuracy.group(0).split()) if accuracy else None,
              "starting_printed": bool(spans)}
    if not spans:
        return dict(result, match=None if accuracy is None else False)
    start = printed_traces(text, spans[0])
    differences = {a: max(abs(p - e) for p, e in zip(start[a], expected[a])) for a in set(start) & set(expected)}
    printed = printed_matrices(text, spans[0], atom)
    built = matrices(expected_text, atom)
    matrix_difference = None if printed is None else max(
        abs(printed[s][i][j] - built[s][i][j]) for s in range(2) for i in range(5) for j in range(5))
    after = printed_traces(text, spans[1]).get(atom) if len(spans) > 1 else None
    result.update(same_atoms=set(start) == set(expected),
                  max_difference=max(differences.values()) if differences else None,
                  over_tolerance=sorted(a for a, d in differences.items() if d > TOLERANCE),
                  atom=atom, atom_matrix_max_difference=matrix_difference,
                  atom_printed=start.get(atom), atom_expected=expected.get(atom), atom_after_iteration_1=after)
    agrees = (result["same_atoms"] and not result["over_tolerance"] and matrix_difference is not None
              and matrix_difference <= MATRIX_TOLERANCE)
    if not agrees:
        result["match"] = False
    elif accuracy is None:
        result["match"] = None  # the first iteration is still running
    else:
        result["match"] = result["density_read"] and result["held"]
    return result


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
            command = "if [ -e {0} ]; then head -n {1} {0}; else echo ABSENT; fi".format(shlex.quote(out), HEAD_LINES)
            _, stdout, stderr = client.exec_command(command, timeout=120)
            text, err = stdout.read().decode(errors="replace"), stderr.read().decode()
            if text.strip() == "ABSENT":
                jobs.append({"job": row["job"], "dir": row["dir"], "started": False, "stderr": err, "match": None})
                continue
            atom, = row["occupations"]["atoms_replaced"]
            result = check(text, (ROOT / row["bundle"] / "occup.txt").read_text(encoding="ascii"), atom)
            jobs.append(dict(result, job=row["job"], dir=row["dir"], started=result["first_accuracy"] is not None,
                             stderr=err))
    finally:
        client.close()
    for job in jobs:
        for key in ("atom_printed", "atom_expected", "atom_after_iteration_1"):
            if job.get(key) is not None:
                job[key] = [round(x, 5) for x in job[key]]
    receipt = {"at": dt.datetime.now(dt.timezone.utc).isoformat(), "readonly": True, "tolerance": TOLERANCE,
               "matrix_tolerance": MATRIX_TOLERANCE, "jobs": jobs,
               "all_started": all(j["started"] for j in jobs),
               "all_match": all(j["match"] for j in jobs),
               "any_mismatch": any(j["match"] is False for j in jobs)}
    with (HERE / ("start_check_" + stamp + ".json")).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({k: receipt[k] for k in ("all_started", "all_match", "any_mismatch")}), flush=True)


if __name__ == "__main__":
    main()
