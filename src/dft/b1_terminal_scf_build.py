"""Build B1, stage 2: a fresh-start SCF at each converged stage-1 endpoint (GATE-1, docs/43:310-313).

Registration: docs/research/b1-relaxed-projector-2026-10-16.md. Each deck is its stage-1 relaxation deck with only
calculation 'relax' -> 'scf', the prefix -> `<stem>__u715_<leg>_scf`, max_seconds -> MAX_SECONDS, and the
ATOMIC_POSITIONS coordinates replaced by the relaxation's "Begin final coordinates" block. Species order and every
if_pos flag are kept from the relaxation deck; fixed atoms must not have moved. Each leg's relaxation is the first
COMPLETE, BFGS-converged one of stage 1 (`_relax`), T1 (`_relax_t1`) and T2 (`_relax_t2`) (registered Repair,
2026-10-18); its mixing is inherited. A leg with none gets no deck. Writes the decks, a manifest and launch_spec.json
once (refuses to overwrite).

Usage: python src/dft/b1_terminal_scf_build.py [--check]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELAX_SPEC = ROOT / "results/b1_relaxed_projector_2026-10-16/launch_spec.json"
TAG = "b1_terminal_scf_2026-10-17"
MANIFEST_REL = f"runs/m_{TAG}.txt"
RESULTS_REL = f"results/{TAG}"
WALL_MINUTES = 45
PROJECTION_SECONDS = 600
SCF_SECONDS = WALL_MINUTES * 60 - PROJECTION_SECONDS - 120
MAX_SECONDS = SCF_SECONDS - 100
SRC_PINS = ["src/dft/research_batch_seeded.py", "src/dft/projection_qc.py", "src/dft/hea_force_audit.py"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def final_coordinates(out_text):
    m = re.search(r"Begin final coordinates\s*\n(?:.*\n)*?ATOMIC_POSITIONS \(angstrom\)\s*\n(.*?)\nEnd final coordinates",
                  out_text, re.S)
    assert m, "no final-coordinates block"
    rows = [r.split() for r in m.group(1).splitlines() if r.strip()]
    return [(r[0], [float(x) for x in r[1:4]], r[4:]) for r in rows]


def build(job, name):
    relax_deck = ROOT / "runs" / job["dir"] / (job["job"] + ".in")
    out = ROOT / "runs" / job["dir"] / (job["job"] + ".out")
    text = relax_deck.read_text(encoding="utf-8")
    final = final_coordinates(out.read_text(encoding="utf-8", errors="strict"))
    block = re.search(r"(?ms)^ATOMIC_POSITIONS angstrom\s*\n(.*?)^K_POINTS", text)
    rows = [r for r in block.group(1).splitlines() if r.split()]
    assert len(rows) == len(final), "atom count differs"
    new_rows = []
    for row, (sym, xyz, flags) in zip(rows, final):
        parts = row.split()
        assert parts[0] == sym, f"species order differs: {parts[0]} vs {sym}"
        if parts[4:] == ["0", "0", "0"]:
            assert flags == ["0", "0", "0"], "fixed flags differ"
            assert all(abs(a - float(b)) < 1e-6 for a, b in zip(xyz, parts[1:4])), "a fixed atom moved"
        new_rows.append(f"  {sym}  {xyz[0]:.8f}  {xyz[1]:.8f}  {xyz[2]:.8f}  {' '.join(parts[4:])}")
    assert name.endswith("_scf") and name != job["job"]
    new = text[:block.start(1)] + "\n".join(new_rows) + "\n" + text[block.end(1):]
    for key, value in (("prefix", f"'{name}'"), ("calculation", "'scf'"), ("max_seconds", str(MAX_SECONDS))):
        new, n = re.subn(rf"(?m)^(\s*{key}\s*=\s*).*$", lambda m, v=value: m[1] + v, new)
        assert n == 1, key
    return name, new


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    relax = json.loads(RELAX_SPEC.read_text(encoding="utf-8"))
    decks, skipped = [], []
    for stage1 in relax["stages"]["b1_relax"]["jobs"]:
        tried = []
        for suffix in ("", "_t1", "_t2"):
            job = dict(stage1, job=stage1["job"] + suffix)
            qc = ROOT / "runs" / job["dir"] / (job["job"] + ".qc.json")
            rec = json.loads(qc.read_text(encoding="utf-8")) if qc.exists() else {}
            if rec.get("status") == "COMPLETE" and rec.get("relaxation", {}).get("bfgs_converged"):
                break
            tried.append(f"{job['job']}: {rec.get('status', 'no receipt')} {rec.get('reason') or ''}".strip())
        else:
            skipped.append("; ".join(tried))
            continue
        name, text = build(job, stage1["job"].replace("_relax", "_scf"))
        decks.append((job, name, text))
        print(f"{name}: from {job['job']} ({rec['relaxation']['ionic_steps']} ionic steps)")
    for s in skipped:
        print("SKIPPED", s)
    if args.check or not decks:
        return 0
    results = ROOT / RESULTS_REL
    assert not (results / "launch_spec.json").exists(), "refusing to overwrite the spec"
    results.mkdir(parents=True, exist_ok=True)
    jobs = []
    for job, name, text in decks:
        path = ROOT / "runs" / job["dir"] / f"{name}.in"
        with path.open("x", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        jobs.append(dict(dir=job["dir"], job=name, sha256=sha(path), nk=job["nk"], scf_seconds=SCF_SECONDS,
                         projection_seconds=PROJECTION_SECONDS, recipe="terminal_scf", role="b1",
                         source_relaxation=f"runs/{job['dir']}/{job['job']}.out",
                         source_relaxation_sha256=sha(ROOT / "runs" / job["dir"] / (job["job"] + ".out"))))
    manifest = ROOT / MANIFEST_REL
    with manifest.open("x", encoding="utf-8", newline="\n") as fh:
        fh.write("# APPROVED 2026-10-16: docs/research/b1-relaxed-projector-2026-10-16.md (Frank: \"Go ahead\"; "
                 "\"launch B1 on Anvil\"; 2026-10-18 \"Repair\")\n")
        fh.write("# B1 stage 2: fresh-start SCF at each selected relaxation endpoint (GATE-1); no automatic retries.\n")
        fh.write(f"# SUBMIT WITH EXCLUDE={relax['exclusions']}\n# NP=128 NCONC=1\n")
        for j in jobs:
            fh.write(f"{j['dir']} {j['job']} .in {j['nk']}\n")
    files = {f"runs/{j['dir']}/{j['job']}.in": j["sha256"] for j in jobs}
    files[MANIFEST_REL] = sha(manifest)
    for rel in SRC_PINS:
        files[rel] = sha(ROOT / rel)
    ceiling = len(jobs) * WALL_MINUTES * 128 // 60
    spec = dict(schema="research-batch-2026-09-16", np=128, exclusions=relax["exclusions"], date="2026-10-17",
                design=relax["design"], decision_ref=relax["decision_ref"],
                allocation=dict(account="che260157", partition="wholenode", cores_per_task=128,
                                launch_ceiling_cpu_su=ceiling, stage_ceilings_cpu_su={"b1_scf": ceiling},
                                b1_total_ceiling_cpu_su=relax["allocation"]["launch_ceiling_cpu_su"]),
                qe_binaries_sha256=relax["qe_binaries_sha256"], files=dict(sorted(files.items())),
                pseudo_md5=relax["pseudo_md5"],
                stages={"b1_scf": dict(kind="scf", manifest=MANIFEST_REL, concurrency=len(jobs),
                                       wall_minutes=WALL_MINUTES, jobs=jobs)})
    with (results / "launch_spec.json").open("x", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(spec, indent=2) + "\n")
    print(f"wrote {len(jobs)} decks, {MANIFEST_REL}, {RESULTS_REL}/launch_spec.json "
          f"(sha256 {sha(results / 'launch_spec.json')}); ceiling {ceiling} SU")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
