"""Freeze the authorized primary relaxation launch; preserve September 16 preparation."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/lowtail_dft_2026-09-18"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = value if isinstance(value, str) else json.dumps(value, indent=2, allow_nan=False) + "\n"
    path.write_bytes(data.encode("utf-8"))


def main():
    if (OUT / "submission.json").exists():
        raise ValueError("refusing to change submitted launch")
    from lowtail_batch import DEPENDENCIES
    old = ROOT / "results/lowtail_dft_2026-09-16/deck_plan.json"
    plan = json.loads(old.read_text(encoding="utf-8"))
    decisions = json.loads((ROOT / plan["operating_decisions"]).read_text(encoding="utf-8"))
    jobs = [dict(d, projection_seconds=1800) for d in plan["decks"] if d["projector"] == "atomic"]
    if len(jobs) != 9:
        raise ValueError("expected nine primary decks")
    original = json.loads((ROOT / "results/research_launch_2026-09-16/launch_spec.json").read_text(encoding="utf-8"))
    manifest_path = "runs/hea/lowtail_validation_2026-09-16/m_primary_authorized_2026-09-18.txt"
    manifest = ["# AUTHORIZED 2026-09-18: user Continue after nine-primary relaxation proposal.",
                "# Three Cr sites; slab, reconstructed O and unreconstructed O; atomic projector only.",
                "# Original prepared manifests and all eighteen input decks remain preserved.",
                "# Stop when any SCF begins iteration 127 or the per-leg wall is reached; no automatic retry.",
                "# Retain scratch on every outcome. Ortho controls remain conditional and outside this launch.",
                "# Plan: results/lowtail_dft_2026-09-18/launch_spec.json",
                "# SUBMIT WITH EXCLUDE=" + original["exclusions"], "# NP=128 NCONC=1"]
    manifest.extend(f"{d['manifest_dir']} {d['job']} .in {d['nk']}" for d in jobs)
    write(ROOT / manifest_path, "\n".join(manifest) + "\n")
    decisions["revision"] = 3
    decisions["date"] = "2026-09-18"
    decisions["authorization"] = "User Continue: nine atomic legs; ortho controls conditional on readout."
    decisions["previous_decisions"] = dict(path=plan["operating_decisions"], sha256=sha(ROOT / plan["operating_decisions"]))
    decisions["acceptance"] = ("Canonical hea_panel_readout.parse_out(allow_relax=True), with no output rewriting; "
        "registered iteration and wall limits; complete final geometry and force evidence, unchanged fixed atoms; "
        "strict lt_readout checks. Online runner additionally retains projection and density/XML. "
        "Basin thresholds and input deck bytes remain those of September 16.")
    write(OUT / "operating_decisions.json", decisions)
    plan.update(date="2026-09-18", status="AUTHORIZED_PRIMARY_ONLY",
                preparation=dict(path=str(old.relative_to(ROOT)).replace("\\", "/"), sha256=sha(old)),
                operating_decisions="results/lowtail_dft_2026-09-18/operating_decisions.json")
    write(OUT / "deck_plan.json", plan)
    paths = list(DEPENDENCIES) + [manifest_path, "results/lowtail_dft_2026-09-18/deck_plan.json",
        "results/lowtail_dft_2026-09-18/operating_decisions.json"] + [j["path"] for j in jobs]
    spec = dict(schema="lowtail-relaxation-launch-v1", authorization="USER_CONTINUE_2026-09-18",
                np=128, concurrency=1, exclusions=original["exclusions"], manifest=manifest_path,
                files={p: sha(ROOT / p) for p in paths}, pseudo_md5=original["pseudo_md5"], jobs=jobs,
                scope="nine primary atomic-projector Cr relaxations; no retries or ortho controls",
                planning_core_hours=sum(d["cost"]["planning_core_h"] for d in jobs),
                relaxation_ceiling_core_hours=sum(d["supervisor_limits"]["leg_wall_ceiling_s"] for d in jobs)*128/3600,
                projection_ceiling_core_hours=9*1800*128/3600,
                wall_minutes=math.ceil((max(d["supervisor_limits"]["leg_wall_ceiling_s"] for d in jobs)+1800+120)/60))
    spec["scheduler_ceiling_core_hours"] = 9*spec["wall_minutes"]*128/60
    write(OUT / "launch_spec.json", spec)
    script = """#!/bin/bash
#SBATCH -p shared
#SBATCH -N 1
#SBATCH -n 128
#SBATCH -o logs/lowtail_%A_%a.out
#SBATCH -e logs/lowtail_%A_%a.out
set -euo pipefail
[ "${PROJECT:-}" = /anvil/projects/x-che260157 ] || { echo 'REFUSE: project'; exit 2; }
[ "${SLURM_NTASKS:-}" = 128 ] || { echo 'REFUSE: requires 128 ranks'; exit 2; }
ROOT="$PROJECT/sts"
SPEC="$ROOT/results/lowtail_dft_2026-09-18/launch_spec.json"
[ "$(sha256sum "$SPEC" | awk '{print $1}')" = 'SPEC_HASH' ] || { echo 'REFUSE: specification hash'; exit 2; }
RUNNER="$ROOT/src/dft/lowtail_batch.py"
[ "$(sha256sum "$RUNNER" | awk '{print $1}')" = 'RUNNER_HASH' ] || { echo 'REFUSE: runner hash'; exit 2; }
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
echo "LOWTAIL TASK ${SLURM_ARRAY_TASK_ID:?} NODE $(hostname) START $(date -u)"
exec "$PYTHON" "$RUNNER" --spec "$SPEC" --root "$ROOT" --row "$SLURM_ARRAY_TASK_ID" --pseudo "$PROJECT/pseudo" --qe "$PROJECT/qe/env"
"""
    script = script.replace("SPEC_HASH", sha(OUT / "launch_spec.json")).replace("RUNNER_HASH", sha(ROOT / "src/dft/lowtail_batch.py"))
    write(ROOT / "anvil/75_lowtail_relaxation.slurm", script)
    print(json.dumps({k: spec[k] for k in ("planning_core_hours", "relaxation_ceiling_core_hours",
                                         "projection_ceiling_core_hours", "scheduler_ceiling_core_hours", "wall_minutes")}, indent=2))


if __name__ == "__main__":
    main()
