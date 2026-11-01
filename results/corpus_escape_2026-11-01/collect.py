"""Download the corpus-escape artifacts from Anvil (read-only there) and apply the decision rule fixed in
docs/research/corpus-escape-2026-11-01.md before any run.

For every job: .out, .qc.json, .run.in, .projwfc.in, .projwfc.out and any .KILLED/.REJECTED marker, plus the array
logs. Local copies are created, never overwritten. The readout is written to a new timestamped file
(readout_<UTC>.json) and printed; every case is listed, whatever it shows.

Usage: python results/corpus_escape_2026-11-01/collect.py            # download, then read out
       python results/corpus_escape_2026-11-01/collect.py --local    # read out what is already on disk
"""
import datetime as dt
import json
import math
import posixpath
import re
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "results/corpus_escape_2026-11-01"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src/dft"))
from silentgate.classify import classify  # noqa: E402
from silentgate.readers.qe import read_force_blocks, read_header  # noqa: E402
import hea_panel_readout  # noqa: E402

SPEC = json.loads((HERE / "launch_spec.json").read_text(encoding="utf-8"))
CASES = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))
REMOTE = "/anvil/projects/x-che260157/sts_corpus_escape_2026-11-01"
SUFFIXES = (".out", ".qc.json", ".run.in", ".projwfc.in", ".projwfc.out", ".KILLED", ".REJECTED")
RY_MEV = 13605.693122
# Decision rule (design note, "Comparison and decision rule"); fixed 2026-11-01 before any run.
HARM_MEV, BENIGN_MEV = -10.0, 10.0
HARM_OFF_A, BENIGN_OFF_A = 0.10, 0.05
ABSMAG_TOL = 1.0


def download():
    import paramiko
    client = paramiko.SSHClient()
    client.load_host_keys(str(Path.home() / ".ssh/known_hosts"))
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect("anvil.rcac.purdue.edu", username="x-fcai3", key_filename=str(Path.home() / ".ssh/id_ed25519"),
                   allow_agent=False, look_for_keys=False, timeout=30, banner_timeout=30, auth_timeout=30)
    sftp = client.open_sftp()
    got = []
    try:
        for job in [j for g in SPEC["stages"].values() for j in g["jobs"]]:
            rdir = posixpath.join(REMOTE, "runs", job["dir"])
            ldir = ROOT / "runs" / job["dir"]
            for suffix in SUFFIXES:
                remote = posixpath.join(rdir, job["job"] + suffix)
                local = ldir / (job["job"] + suffix)
                try:
                    sftp.stat(remote)
                except FileNotFoundError:
                    continue
                if not local.exists():
                    sftp.get(remote, str(local))
                    got.append(local.relative_to(ROOT).as_posix())
        logs = HERE / "logs"
        logs.mkdir(exist_ok=True)
        try:
            entries = sftp.listdir_attr(posixpath.join(REMOTE, "logs"))
        except FileNotFoundError:
            entries = []
        for entry in entries:
            if stat.S_ISREG(entry.st_mode) and not (logs / entry.filename).exists():
                sftp.get(posixpath.join(REMOTE, "logs", entry.filename), str(logs / entry.filename))
                got.append("results/corpus_escape_2026-11-01/logs/" + entry.filename)
    finally:
        client.close()
    return got


def final_crystal(text, nat, lengths):
    """Final coordinates in crystal units (the decks are crystal; angstrom output is converted on the diagonal cell)."""
    if "Begin final coordinates" not in text:
        return None
    block = text[text.index("Begin final coordinates"):text.index("End final coordinates")]
    parts = re.split(r"ATOMIC_POSITIONS \((crystal|angstrom)\)\s*\n", block)
    if len(parts) != 3:
        return None
    unit, body = parts[1], parts[2]
    rows = [line.split() for line in body.splitlines()[:nat]]
    pos = [[float(v) for v in r[1:4]] for r in rows]
    return pos if unit == "crystal" else [[p[k] / lengths[k] for k in range(3)] for p in pos]


def arm_record(case, arm):
    path = ROOT / case["decks"][arm]
    out = path.with_suffix(".out")
    qc = path.with_suffix(".qc.json")
    rec = {"job": path.stem, "present": out.exists()}
    if not out.exists():
        rec["status"] = "KILLED" if path.with_suffix(".KILLED").exists() else "MISSING"
        return rec
    text = out.read_text(encoding="utf-8", errors="replace")
    receipt = json.loads(qc.read_text(encoding="utf-8")) if qc.exists() else {}
    score = hea_panel_readout.parse_out(out, allow_relax=True)
    header = read_header(text)
    steps, _, issues = read_force_blocks(text)
    lock = classify({"adsorbate_indices": case["adsorbate_index1"], "force_steps": steps, "force_issues": issues,
                     "n_symops": header["n_symops"], "forc_conv_thr": 1e-4})
    rec.update(receipt_status=receipt.get("status"), receipt_reason=receipt.get("reason"),
               readout_status=score["status"], E_Ry=score["E_Ry"], absmag=score["absmag"], totmag=score["totmag"],
               n_symops=header["n_symops"], header_form=header["header_form"],
               silentgate_verdict=lock["verdict"], locked_axes=lock.get("locked_axes"),
               n_force_steps=len(steps), bfgs_converged="bfgs converged" in text)
    pos = final_crystal(text, case["nat"], case["cell_lengths_A"])
    if pos is not None:
        axis = {"x": 0, "y": 1}[case["locked_axis"]]
        L = case["cell_lengths_A"][axis]
        offs = {str(i): abs((pos[i - 1][axis] - case["plane_crystal"]) - round(pos[i - 1][axis] - case["plane_crystal"])) * L
                for i in case["adsorbate_index1"]}
        rec["final_off_plane_A"] = {k: round(v, 4) for k, v in offs.items()}
        rec["d_off_A"] = round(max(offs.values()), 4)
    return rec


def decide(case, held, esc):
    reasons = []
    if held.get("receipt_status") != "COMPLETE" or held.get("readout_status") != "CONVERGED":
        reasons.append("held not COMPLETE/CONVERGED (%s, %s)" % (held.get("receipt_status") or held.get("status"),
                                                               held.get("readout_status")))
    elif held.get("n_symops") != case["deposited_n_symops"]:
        reasons.append("held header %r operations, deposited %d" % (held.get("n_symops"), case["deposited_n_symops"]))
    elif held.get("silentgate_verdict") != "LOCKED" or held.get("locked_axes") != [case["locked_axis"]]:
        reasons.append("held did not reproduce the lock (%s %s)" % (held.get("silentgate_verdict"), held.get("locked_axes")))
    if esc.get("receipt_status") != "COMPLETE" or esc.get("readout_status") != "CONVERGED":
        reasons.append("escape not COMPLETE/CONVERGED (%s, %s)" % (esc.get("receipt_status") or esc.get("status"),
                                                                 esc.get("readout_status")))
    elif esc.get("header_form") != "no-symmetry":
        reasons.append("escape header is %s, not 'No symmetry found'" % esc.get("header_form"))
    elif esc.get("d_off_A") is None:
        reasons.append("escape final coordinates not readable")
    if reasons:
        return {"class": "INVALID", "reasons": reasons}
    dE = (esc["E_Ry"] - held["E_Ry"]) * RY_MEV
    out = {"dE_meV": round(dE, 2), "d_off_A": esc.get("d_off_A"), "held_d_off_A": held.get("d_off_A")}
    if case["nspin"] == 2 and (held["absmag"] is None or esc["absmag"] is None
                               or abs(held["absmag"] - esc["absmag"]) > ABSMAG_TOL):
        out.update({"class": "UNRESOLVED", "reasons": ["absolute magnetization differs by more than %.1f muB "
                                                       "(%s vs %s): change of electronic state" %
                                                       (ABSMAG_TOL, held["absmag"], esc["absmag"])]})
        return out
    if dE < HARM_MEV and esc["d_off_A"] > HARM_OFF_A:
        out["class"] = "HARMFUL"
    elif abs(dE) <= BENIGN_MEV and esc["d_off_A"] <= BENIGN_OFF_A:
        out["class"] = "BENIGN"
    else:
        out["class"] = "UNRESOLVED"
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    got = [] if "--local" in sys.argv else download()
    rows = []
    for case in CASES["cases"]:
        held, esc = arm_record(case, "held"), arm_record(case, "escape")
        row = {"tier": case["tier"], "launch_group": case["launch_group"], "metal": case["metal"], "job": case["job"],
               "state": case["state"], "locked_axis": case["locked_axis"], "held": held, "escape": esc}
        if held["present"] or esc["present"]:
            row["decision"] = decide(case, held, esc)
        else:
            row["decision"] = {"class": "NOT RUN"}
        rows.append(row)
    counts = {}
    for r in rows:
        key = (r["tier"], r["decision"]["class"])
        counts["%s %s" % key] = counts.get("%s %s" % key, 0) + 1
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report = {"schema": "corpus-escape-readout-v1", "at": stamp, "design": CASES["design"],
              "rule": {"harmful": "dE < %.0f meV and d_off > %.2f A" % (HARM_MEV, HARM_OFF_A),
                       "benign": "|dE| <= %.0f meV and d_off <= %.2f A" % (BENIGN_MEV, BENIGN_OFF_A),
                       "unresolved": "every other valid outcome; nspin 2 with |d absmag| > %.1f muB" % ABSMAG_TOL},
              "downloaded": got, "counts": counts, "rows": rows}
    with (HERE / ("readout_%s.json" % stamp)).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(report, indent=2) + "\n")
    for r in rows:
        d = r["decision"]
        print("%-6s %-5s %-10s %-10s dE %8s meV  d_off %6s A  %s" % (
            r["launch_group"], r["metal"], r["job"], d["class"], d.get("dE_meV", "-"), d.get("d_off_A", "-"),
            "; ".join(d.get("reasons", []))))
    print(json.dumps(counts, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
