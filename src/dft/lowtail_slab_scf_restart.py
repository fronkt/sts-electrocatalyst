"""Two discriminating SCFs on the Cu8 clean-slab stall, from the retained density — decks, manifest, specification, wrappers.

Array 20813525 task 1 (Cu8Cr23Mn35Co34 seed20 site2, clean slab, relax) stopped at the SCF
iteration ceiling in its fifth cycle with the energy stagnating at −7551.85937 Ry and an
estimated accuracy near 4e-7 Ry.  A fresh-start SCF at the identical geometry (array
20840139 task 2) converged at 8.08e-8 Ry to −7551.86633525 Ry, 94.7 meV lower, with the
same total magnetization and Hubbard occupation traces.  Two readings remain: a second
self-consistent solution, or a stagnating density that is not self-consistent.

The two runs here start from the relaxation's own retained density, Hubbard occupations
and PAW terms (``startingpot = 'file'``; the save directory is copied into a fresh scratch
by the runner and pinned by content) with fresh wavefunctions, at the production threshold
and production mixing (0.3, local-TF) in one leg and with ``mixing_mode = 'plain'`` in the
other.  Every other line of the pinned clean-slab deck is unchanged.

    slab_c5__rho_ltf     cycle-5 coordinates, density from file, local-TF, beta 0.30
    slab_c5__rho_plain   cycle-5 coordinates, density from file, plain,    beta 0.30

Reading of a COMPLETE receipt: a converged energy near −7551.866 Ry means the stagnating
density lay in the basin of the fresh-start solution; near −7551.859 Ry means a second
self-consistent solution exists; a KILLED receipt repeats the production condition.
Numerical diagnostic only: no relaxed slab, adsorption reference or census result.

Usage:
    python src/dft/lowtail_slab_scf_restart.py           # build decks, manifest, spec, wrappers (stage slab_scf_seeded)
    python src/dft/lowtail_slab_scf_restart.py --check   # verify a rebuild is byte-identical
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from lowtail_slab_scf_diag import (BASE_SPEC, CONCURRENCY, MAX_ITERATIONS, NK, POSITIONS,
                                   PROJECTION_SECONDS, SCF_SECONDS, SRC, WALL_MINUTES, derive, sha,
                                   write_or_check)

DST = Path("runs/hea/lowtail_slab_scf_restart_2026-09-22")
RES = Path("results/lowtail_slab_scf_seeded_2026-09-22")
MANIFEST = Path("runs/m_lowtail_slab_scf_seeded_2026-09-22.txt")
SPEC = RES / "launch_spec.json"
SLURM = Path("anvil/78_slab_scf_seeded.slurm")
SUBMIT = Path("anvil/79_submit_slab_scf_seeded.sh")
STAGE = "slab_scf_seeded"
# The seeded runner is its own pinned file; the original runner is pinned beside it unchanged
# because the 2026-09-18 relaxation array and the 2026-09-19 diagnostic verify its bytes.
RUNNER = "src/dft/research_batch_seeded.py"
PINNED = [RUNNER, "src/dft/research_batch.py", "src/dft/projection_qc.py", "src/dft/hea_force_audit.py",
          "src/dft/queue_r1.sh"]
# Attempt 1 of this batch (stage slab_scf_restart, held job 20845265, never released) was withdrawn on
# 2026-09-22 05:40 UTC because its wrappers executed src/dft/research_batch.py, whose bytes the running
# relaxation array pins; its receipts stay under results/lowtail_slab_scf_restart_2026-09-22/.
SITE = "Cu8Cr23Mn35Co34__s20_site2"
DIAG_SPEC = Path("results/lowtail_slab_scf_diag_2026-09-19/launch_spec.json")

JOBS = [
    ("slab_c5__rho_ltf", "local-TF"),
    ("slab_c5__rho_plain", "plain"),
]

# The retained scratch of array 20813525 task 1 (QC status KILLED, scratch_retained), hashed on
# Anvil on 2026-09-22 05:30 UTC.  The runner copies these four files into <job>.save inside a
# fresh scratch and refuses the job if any byte differs; the source is never written.
SCRATCH_SOURCE = {
    "save_dir": ("runs/hea/lowtail_validation_2026-09-16/Cu8Cr23Mn35Co34__s20_site2/tmp_slab__atomic/"
                 "lt__Cu8Cr23Mn35Co34__s20_site2__slab__atomic.save"),
    "files": {
        "charge-density.hdf5": "91682dc33d92c7a394e7bbd3c5b9358f6f83b17e925b7700c93f0cbb8903044f",
        "data-file-schema.xml": "771ab929dc7badaaf0ec704d19d80d674339a623cc2ca16f56e0598683ba77de",
        "occup.txt": "7898f1004b5956f547ce4f705a5334ebed999c0a39782618199f9c8beb874e15",
        "paw.txt": "c52ea589615ddb5d6fe673520ae9bed20cc1d33066c2bdf2eaed95be28512039",
    },
    "bytes": {"charge-density.hdf5": 149764564, "data-file-schema.xml": 452286, "occup.txt": 93601, "paw.txt": 640225},
    "written_by": "array 20813525 task 1, pw.x clean stop on the supervisor's EXIT file, 2026-09-18 04:46 EDT",
    "observed_utc": "2026-09-22T05:30:00+00:00",
}
REFERENCE_ENERGIES_RY = {
    "fresh_start_converged_array_20840139_task_2": -7551.86633525,
    "relaxation_cycle5_stagnating_last_estimate": -7551.85936520,
    "relaxation_cycle4_converged": -7551.85641872,
}
PROVENANCE_INFORMATIONAL = ["docs/research/lowtail-clean-slab-scf-stall-2026-09-19.md",
                            "docs/research/lowtail-generalization-sizing-2026-09-22.md"]


def derive_restart(text: str, job: str, mixing_mode: str) -> str:
    text = derive(text, job, 0.30, "cycle5")
    text, k = re.subn(r"  startingpot = 'atomic'\n", "  startingpot = 'file'\n", text)
    if k != 1:
        raise ValueError("startingpot substitution not unique")
    if mixing_mode != "local-TF":
        text, k = re.subn(r"  mixing_mode = 'local-TF'\n", f"  mixing_mode = '{mixing_mode}'\n", text)
        if k != 1:
            raise ValueError("mixing_mode substitution not unique")
    return text


def build(check: bool) -> None:
    seen: list = []
    jobs, files, manifest_rows = [], {}, []
    src = SRC / SITE / "slab__atomic.in"
    for job, mixing_mode in JOBS:
        deck = derive_restart(src.read_text(encoding="utf-8"), job, mixing_mode)
        dst = DST / SITE / f"{job}.in"
        write_or_check(dst, deck, check, seen)
        digest = hashlib.sha256(deck.encode("utf-8")).hexdigest()
        rel_dir = str(DST / SITE).replace("\\", "/").replace("runs/", "", 1)
        jobs.append({"dir": rel_dir, "job": job, "nk": NK, "sha256": digest, "scf_seconds": SCF_SECONDS,
                     "projection_seconds": PROJECTION_SECONDS, "max_iterations": MAX_ITERATIONS,
                     "site": SITE, "geometry": "cycle5", "mixing_beta": 0.30, "mixing_mode": mixing_mode,
                     "startingpot": "file", "startingwfc": "atomic+random",
                     "scratch_source": {"save_dir": SCRATCH_SOURCE["save_dir"], "files": SCRATCH_SOURCE["files"]},
                     "source_deck": str(src).replace("\\", "/"), "source_sha256": sha(src)})
        files[str(dst).replace("\\", "/")] = digest
        manifest_rows.append(f"{rel_dir} {job} .in {NK}")
    manifest = "\n".join([
        "# LICENSED 2026-09-22: two discriminating fixed-geometry SCFs on the Cu8 clean-slab stall, from the retained density (attempt 2, seeded runner);",
        "# the entrant's election of 2026-09-22 (\"License both legs\"), dated A11.R3 line in docs/43, addendum of 2026-09-22.",
        "# Separate from arrays 20813525 and 20840139; cycle-5 coordinates; startingpot file (copied, pinned by content);",
        "# target 8.08e-8 Ry; ceiling 126 iterations / 7200 s; no retries; a stopped SCF is no result.",
        "# SUBMIT WITH EXCLUDE=a024,a049,a050,a088,a196,a220,a223,a171,a120,a200",
        "# NP=128 NCONC=1",
    ] + manifest_rows) + "\n"
    write_or_check(MANIFEST, manifest, check, seen)
    files[MANIFEST.as_posix()] = hashlib.sha256(manifest.encode("utf-8")).hexdigest()
    for helper in PINNED:
        files[helper] = sha(Path(helper))
    for positions in (POSITIONS, POSITIONS.with_suffix(".json")):
        files[positions.as_posix()] = sha(positions)
    base = json.loads(BASE_SPEC.read_text(encoding="utf-8"))
    upf = set(re.findall(r"[A-Za-z0-9_.+-]+\.(?:UPF|upf)", src.read_text(encoding="utf-8")))
    pseudo_md5 = {name: base["pseudo_md5"][name] for name in sorted(upf)}
    diag = json.loads(DIAG_SPEC.read_text(encoding="utf-8"))
    spec = {
        "schema": "research-batch-2026-09-16",
        "np": 128,
        "exclusions": base["exclusions"],
        "authorization": ("Entrant's election of 2026-09-22, from the session record: \"License both legs\"; "
                          "A11.R3 dated line in docs/43, addendum of 2026-09-22 (two legs, planning 260 core-hours "
                          "on the observed 128 core-hour SCF, ceiling 576, scheduler cap 640)."),
        "scope": ("Fixed-geometry numerical diagnostic from the retained density of array 20813525 task 1; not a "
                  "relaxation, adsorption reference or census result; arrays 20813525 and 20840139 untouched; the "
                  "retained scratch is read by copy and never written."),
        "acceptance": dict(diag["acceptance"], discrimination=(
            "COMPLETE near -7551.866 Ry: the stagnating density lies in the basin of the fresh-start solution; "
            "COMPLETE near -7551.859 Ry: a second self-consistent solution exists at this geometry; "
            "KILLED: the production condition repeats from its own density")),
        "reference_energies_Ry": REFERENCE_ENERGIES_RY,
        "scratch_source": SCRATCH_SOURCE,
        "provenance_informational_sha256": {p: sha(Path(p)) for p in PROVENANCE_INFORMATIONAL},
        "files": files,
        "pseudo_md5": pseudo_md5,
        "stages": {STAGE: {"kind": STAGE, "manifest": MANIFEST.as_posix(), "concurrency": CONCURRENCY,
                           "wall_minutes": WALL_MINUTES, "jobs": jobs}},
        "ceiling": {"per_job_core_hours": round((SCF_SECONDS + PROJECTION_SECONDS) * 128 / 3600, 1),
                    "scheduler_core_hours": round(WALL_MINUTES * 60 * 128 / 3600 * len(jobs), 1),
                    "planning_core_hours": 260.0},
    }
    spec_text = json.dumps(spec, indent=1) + "\n"
    write_or_check(SPEC, spec_text, check, seen)
    spec_hash = hashlib.sha256(spec_text.encode("utf-8")).hexdigest()
    runner_hash = files[RUNNER]
    slurm = f"""#!/bin/bash
# Discriminating SCFs from the retained density, 2026-09-22; scheduler resources set at submission.
#SBATCH -p shared
#SBATCH -N 1
#SBATCH -n 128
#SBATCH -o logs/slabrestart_%A_%a.out
#SBATCH -e logs/slabrestart_%A_%a.out
set -euo pipefail
[ "${{PROJECT:-}}" = /anvil/projects/x-che260157 ] || {{ echo 'REFUSE: project'; exit 2; }}
[ "${{SLURM_NTASKS:-}}" = 128 ] || {{ echo 'REFUSE: requires 128 ranks'; exit 2; }}
[ "${{STAGE:-}}" = {STAGE} ] || exit 2
ROOT="$PROJECT/sts"
SPEC="$ROOT/{SPEC.as_posix()}"
RUNNER="$ROOT/{RUNNER}"
check_hash() {{ [ "$(sha256sum "$1" | awk '{{print $1}}')" = "$2" ] || {{ echo "REFUSE: hash $1"; exit 2; }}; }}
check_hash "$SPEC" {spec_hash}
check_hash "$RUNNER" {runner_hash}
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
echo "STAGE $STAGE TASK ${{SLURM_ARRAY_TASK_ID:?}} NODE $(hostname) START $(date -u)"
exec "$PYTHON" "$RUNNER" --spec "$SPEC" --root "$ROOT" --stage "$STAGE" \\
     --row "$SLURM_ARRAY_TASK_ID" --pseudo "$PROJECT/pseudo" --qe "$PROJECT/qe/env"
"""
    submit = f"""#!/bin/bash
# Submit the discriminating SCFs held; caller verifies scheduler fields before release. No retry/override.
set -euo pipefail
export PROJECT=/anvil/projects/x-che260157
export STAGE={STAGE}
ROOT="$PROJECT/sts"
SPEC="$ROOT/{SPEC.as_posix()}"
RUNNER="$ROOT/{RUNNER}"
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
check_hash() {{ [ "$(sha256sum "$1" | awk '{{print $1}}')" = "$2" ] || {{ echo "REFUSE: hash $1"; exit 2; }}; }}
check_hash "$SPEC" {spec_hash}
check_hash "$RUNNER" {runner_hash}
[ -f "$PROJECT/parity/PARITY_PASS" ] || {{ echo 'REFUSE: parity absent'; exit 2; }}
[ -f "$ROOT/anvil/pseudo_md5_preflight_2026-08-23.md" ] || exit 2
"$PYTHON" "$RUNNER" --spec "$SPEC" --root "$ROOT" --stage "$STAGE" --pseudo "$PROJECT/pseudo" --preflight
read -r MANIFEST N CONC MINUTES EXCLUDE < <("$PYTHON" -c 'import json,sys; s=json.load(open(sys.argv[1])); g=s["stages"][sys.argv[2]]; print(g["manifest"],len(g["jobs"]),g["concurrency"],g["wall_minutes"],s["exclusions"])' "$SPEC" "$STAGE")
export RUNS="$ROOT/runs" QE_PREFIX="$PROJECT/qe/env" PSEUDO_DIR="$PROJECT/pseudo"
PREFLIGHT_ONLY=1 LOG=/dev/stdout bash "$ROOT/src/dft/queue_r1.sh" "$ROOT/$MANIFEST" 128 1
cd "$PROJECT"
mkdir -p logs
echo "HELD $STAGE tasks=$N concurrency=$CONC minutes=$MINUTES cores=128"
sbatch --parsable --hold --no-requeue -A che260157 -p shared -N 1 -n 128 \\
    --cpus-per-task=1 --mem=237G --time="$MINUTES" --exclude="$EXCLUDE" \\
    --job-name="research-$STAGE" --array="1-$N%$CONC" \\
    --export=ALL,PROJECT,STAGE "$ROOT/{SLURM.as_posix()}"
"""
    write_or_check(SLURM, slurm, check, seen)
    write_or_check(SUBMIT, submit, check, seen)
    receipt = {"spec_sha256": spec_hash, "runner_sha256": runner_hash, "written": seen,
               "slurm_sha256": hashlib.sha256(slurm.encode()).hexdigest(),
               "submit_sha256": hashlib.sha256(submit.encode()).hexdigest()}
    print(("CHECK OK " if check else "built ") + json.dumps(receipt, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    build(ap.parse_args().check)
