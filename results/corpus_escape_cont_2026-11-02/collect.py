"""Download the continuation artifacts from Anvil (read-only there) and apply the tier 1a decision rule, unchanged, to
each case: held = the tier 1a held output, escape = the continuation output.

The rule's functions are imported from results/corpus_escape_2026-11-01/collect.py (arm_record, decide), so the
scoring is the same code that read tier 1a. Beside each class it reports, without changing it:
  - continuity: the continuation's first SCF energy minus the tier 1a escape's last energy (same geometry), in meV;
  - the final O-O distance and the distal O's nearest slab atom (a broken O-O bond is a change of intermediate);
  - the BFGS steps used here and in tier 1a.
The readout is written to a new timestamped file (readout_<UTC>.json) and printed; every case is listed.

Usage: python results/corpus_escape_cont_2026-11-02/collect.py            # download, then read out
       python results/corpus_escape_cont_2026-11-02/collect.py --local    # read out what is already on disk
"""
import datetime as dt
import importlib.util
import json
import posixpath
import re
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "results/corpus_escape_cont_2026-11-02"
SPEC = json.loads((HERE / "launch_spec.json").read_text(encoding="utf-8"))
CASES = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))
REMOTE = "/anvil/projects/x-che260157/sts_corpus_escape_cont_2026-11-02"
SUFFIXES = (".out", ".qc.json", ".run.in", ".projwfc.in", ".projwfc.out", ".KILLED", ".REJECTED")
_spec = importlib.util.spec_from_file_location("collect_tier1a", ROOT / "results/corpus_escape_2026-11-01/collect.py")
TIER1A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TIER1A)
ENERGY = re.compile(r"^!\s+total energy\s+=\s+([-0-9.]+)\s+Ry", re.M)


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
                remote, local = posixpath.join(rdir, job["job"] + suffix), ldir / (job["job"] + suffix)
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
                got.append("results/corpus_escape_cont_2026-11-02/logs/" + entry.filename)
    finally:
        client.close()
    return got


def dist(a, b, L):
    d = [(a[k] - b[k] - (round(a[k] - b[k]) if k < 2 else 0)) * L[k] for k in range(3)]
    return sum(v * v for v in d) ** 0.5


def side_facts(case):
    """Continuity, step counts and the final adsorbate bonds; reported beside the class, never used by it."""
    out_path = (ROOT / case["decks"]["escape"]).with_suffix(".out")
    if not out_path.exists():
        return {}
    text = out_path.read_text(encoding="utf-8", errors="replace")
    energies = [float(v) for v in ENERGY.findall(text)]
    facts = {"bfgs_steps_cont": len(energies), "bfgs_steps_tier1a": case["continues"]["n_scf"]}
    if energies:
        facts["continuity_first_scf_minus_tier1a_last_meV"] = round(
            (energies[0] - case["continues"]["last_E_Ry"]) * TIER1A.RY_MEV, 3)
    pos = TIER1A.final_crystal(text, case["nat"], case["cell_lengths_A"])
    if pos is not None:
        L = case["cell_lengths_A"]
        role = {v["role"]: int(k) for k, v in case["displacement"].items()}
        ob, od = pos[role["O_bind"] - 1], pos[role["O_distal"] - 1]
        deck = (ROOT / case["decks"]["escape"]).read_text(encoding="utf-8")
        labels = [line.split()[0] for line in deck.split("ATOMIC_POSITIONS")[1].splitlines()[1:case["nat"] + 1]]
        ads = set(case["adsorbate_index1"])
        near = min((dist(od, pos[j], L), j + 1) for j in range(case["nat"]) if j + 1 not in ads)
        facts.update({"final_O_O_A": round(dist(ob, od, L), 3),
                      "final_distal_O_nearest_slab": {"atom": near[1], "species": labels[near[1] - 1],
                                                      "A": round(near[0], 3)}})
    return facts


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    got = [] if "--local" in sys.argv else download()
    rows = []
    for case in CASES["cases"]:
        held, esc = TIER1A.arm_record(case, "held"), TIER1A.arm_record(case, "escape")
        row = {"metal": case["metal"], "job": case["job"], "held": held, "escape_cont": esc}
        row["decision"] = TIER1A.decide(case, held, esc) if esc["present"] else {"class": "NOT RUN"}
        row["side"] = side_facts(case)
        rows.append(row)
    counts = {}
    for r in rows:
        counts[r["decision"]["class"]] = counts.get(r["decision"]["class"], 0) + 1
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report = {"schema": "corpus-escape-cont-readout-v1", "at": stamp, "design": CASES["design"],
              "rule": "results/corpus_escape_2026-11-01/collect.py decide(), unchanged; held = tier 1a held output, "
                      "escape = this continuation", "downloaded": got, "counts": counts, "rows": rows}
    with (HERE / ("readout_%s.json" % stamp)).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(report, indent=2) + "\n")
    for r in rows:
        d, s = r["decision"], r["side"]
        print("%-5s %-10s dE %9s meV  d_off %6s A  O-O %5s  cont %3s steps  continuity %8s meV  %s" % (
            r["metal"], d["class"], d.get("dE_meV", "-"), d.get("d_off_A", "-"), s.get("final_O_O_A", "-"),
            s.get("bfgs_steps_cont", "-"), s.get("continuity_first_scf_minus_tier1a_last_meV", "-"),
            "; ".join(d.get("reasons", []))))
    print(json.dumps(counts, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
