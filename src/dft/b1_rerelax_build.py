"""Build the B1 GATE-1 re-relaxation of both *OOH legs (registered 2026-10-19).

Registration: docs/research/b1-relaxed-projector-2026-10-16.md, "GATE-1 re-relaxation of *OOH". Each deck is the
leg's stage-2 terminal SCF deck with only `calculation` ('scf' -> 'relax'), the prefix and `max_seconds` changed;
positions, if_pos flags, mixing, thresholds and &IONS are kept. A fresh start, so the first SCF has the terminal SCF's
inputs. Writes the decks, a manifest and launch_spec.json once (refuses to overwrite).

Usage: python src/dft/b1_rerelax_build.py [--check]
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
SCF_SPEC = ROOT / "results/b1_terminal_scf_2026-10-17/launch_spec.json"
TAG = "b1_rerelax_2026-10-19"
STAGE = "b1_rerelax"
MANIFEST_REL = f"runs/m_{TAG}.txt"
RESULTS_REL = f"results/{TAG}"
WALL_MINUTES = 360
SCF_SECONDS = WALL_MINUTES * 60 - 900
MAX_SECONDS = SCF_SECONDS - 700
PROJECTION_SECONDS = 600
SRC_PINS = ["src/dft/research_batch_seeded.py", "src/dft/projection_qc.py", "src/dft/hea_panel_readout.py",
            "src/dft/hea_geometry.py"]
LEGS = ("s0_OOH__2x1v_escape__u715_atomic", "s0_OOH__2x1v_escape__u715_ortho")
B1_USED_SU = 4113.0  # stage 1 1,653.2 + repair 2,261.0 + stage 2 198.8 (mybalance 15,124.2 -> 11,011.2)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build(scf_job):
    deck = ROOT / "runs" / scf_job["dir"] / (scf_job["job"] + ".in")
    assert sha(deck) == scf_job["sha256"], "terminal SCF deck changed"
    receipt = json.loads((ROOT / "runs" / scf_job["dir"] / (scf_job["job"] + ".qc.json")).read_text(encoding="utf-8"))
    assert receipt.get("status") == "COMPLETE", f"{scf_job['job']}: terminal SCF not COMPLETE"
    text = deck.read_text(encoding="utf-8")
    name = scf_job["job"].replace("_scf", "_rerelax")
    new = text
    for key, old, value in (("calculation", "'scf'", "'relax'"), ("prefix", f"'{scf_job['job']}'", f"'{name}'"),
                            ("max_seconds", None, str(MAX_SECONDS))):
        pattern = rf"(?m)^(\s*{key}\s*=\s*)" + (re.escape(old) if old else r"\S+") + r"\s*$"
        new, n = re.subn(pattern, lambda m, v=value: m[1] + v, new)
        assert n == 1, key
    assert re.search(r"(?m)^\s*&IONS", new) and re.search(r"(?m)^\s*forc_conv_thr\s*=", new), "relax namelist missing"
    assert not re.search(r"(?m)^\s*startingpot\s*=\s*'file'|^\s*startingwfc\s*=\s*'file'", new), "must start fresh"
    changed = [(a, b) for a, b in zip(text.splitlines(), new.splitlines()) if a != b]
    assert len(text.splitlines()) == len(new.splitlines()) and len(changed) == 3, changed
    return name, new


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    relax = json.loads(RELAX_SPEC.read_text(encoding="utf-8"))
    scf = {j["job"]: j for j in json.loads(SCF_SPEC.read_text(encoding="utf-8"))["stages"]["b1_scf"]["jobs"]}
    built = []
    for leg in LEGS:
        job = scf[leg + "_scf"]
        name, text = build(job)
        built.append((job, name, text))
        print(f"{name}: from {job['job']} (relaxation {job['source_relaxation']})")
    if args.check:
        return 0
    results = ROOT / RESULTS_REL
    assert not (results / "launch_spec.json").exists(), "refusing to overwrite the spec"
    results.mkdir(parents=True, exist_ok=True)
    jobs, files = [], {}
    for job, name, text in built:
        path = ROOT / "runs" / job["dir"] / f"{name}.in"
        with path.open("x", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        src = ROOT / "runs" / job["dir"] / (job["job"] + ".out")
        jobs.append(dict(dir=job["dir"], job=name, sha256=sha(path), nk=job["nk"], scf_seconds=SCF_SECONDS,
                         projection_seconds=PROJECTION_SECONDS, max_iterations=126, recipe="relax", role="b1",
                         gate1_source_scf=f"runs/{job['dir']}/{job['job']}.out", gate1_source_scf_sha256=sha(src),
                         source_deck=f"runs/{job['dir']}/{job['job']}.in", source_deck_sha256=job["sha256"]))
        files[f"runs/{job['dir']}/{name}.in"] = sha(path)
    with (ROOT / MANIFEST_REL).open("x", encoding="utf-8", newline="\n") as fh:
        fh.write("# APPROVED 2026-10-19: docs/research/b1-relaxed-projector-2026-10-16.md, GATE-1 re-relaxation "
                 "(Frank: \"do the extra OOH relaxation\")\n")
        fh.write("# B1 GATE-1 re-relaxation of both *OOH legs from their terminal SCFs; no automatic retries.\n")
        fh.write(f"# SUBMIT WITH EXCLUDE={relax['exclusions']}\n# NP=128 NCONC=1\n")
        for j in jobs:
            fh.write(f"{j['dir']} {j['job']} .in {j['nk']}\n")
    files[MANIFEST_REL] = sha(ROOT / MANIFEST_REL)
    for rel in SRC_PINS:
        files[rel] = sha(ROOT / rel)
    ceiling = len(jobs) * WALL_MINUTES * 128 // 60
    spec = dict(schema="research-batch-2026-09-16", np=128, exclusions=relax["exclusions"], date="2026-10-19",
                design=relax["design"], decision_ref='Frank, 2026-10-19: "do the extra OOH relaxation"',
                allocation=dict(account="che260157", partition="wholenode", cores_per_task=128,
                                launch_ceiling_cpu_su=ceiling, stage_ceilings_cpu_su={STAGE: ceiling},
                                b1_total_ceiling_cpu_su=relax["allocation"]["launch_ceiling_cpu_su"],
                                b1_used_cpu_su=B1_USED_SU),
                qe_binaries_sha256=relax["qe_binaries_sha256"], files=dict(sorted(files.items())),
                pseudo_md5=relax["pseudo_md5"],
                stages={STAGE: dict(kind="relax", manifest=MANIFEST_REL, concurrency=len(jobs),
                                    wall_minutes=WALL_MINUTES, jobs=jobs)})
    assert B1_USED_SU + ceiling <= relax["allocation"]["launch_ceiling_cpu_su"], "B1 ceiling"
    with (results / "launch_spec.json").open("x", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(spec, indent=2) + "\n")
    print(f"wrote {len(jobs)} decks, {MANIFEST_REL}, {RESULTS_REL}/launch_spec.json "
          f"(sha256 {sha(results / 'launch_spec.json')}); ceiling {ceiling} SU")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
