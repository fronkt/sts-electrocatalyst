#!/bin/bash
# Submit the discriminating SCFs held; caller verifies scheduler fields before release. No retry/override.
set -euo pipefail
export PROJECT=/anvil/projects/x-che260157
export STAGE=slab_scf_seeded
ROOT="$PROJECT/sts"
SPEC="$ROOT/results/lowtail_slab_scf_seeded_2026-09-22/launch_spec.json"
RUNNER="$ROOT/src/dft/research_batch_seeded.py"
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
check_hash() { [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ] || { echo "REFUSE: hash $1"; exit 2; }; }
check_hash "$SPEC" 28fef16439e658101ae50c1a59628666767fca7684cf8c03e3a43ddaa4a1ec75
check_hash "$RUNNER" ef4116f6e46f6168c958466a93324b673ca89599be30c2b1dc9fb8f3915064d0
[ -f "$PROJECT/parity/PARITY_PASS" ] || { echo 'REFUSE: parity absent'; exit 2; }
[ -f "$ROOT/anvil/pseudo_md5_preflight_2026-08-23.md" ] || exit 2
"$PYTHON" "$RUNNER" --spec "$SPEC" --root "$ROOT" --stage "$STAGE" --pseudo "$PROJECT/pseudo" --preflight
read -r MANIFEST N CONC MINUTES EXCLUDE < <("$PYTHON" -c 'import json,sys; s=json.load(open(sys.argv[1])); g=s["stages"][sys.argv[2]]; print(g["manifest"],len(g["jobs"]),g["concurrency"],g["wall_minutes"],s["exclusions"])' "$SPEC" "$STAGE")
export RUNS="$ROOT/runs" QE_PREFIX="$PROJECT/qe/env" PSEUDO_DIR="$PROJECT/pseudo"
PREFLIGHT_ONLY=1 LOG=/dev/stdout bash "$ROOT/src/dft/queue_r1.sh" "$ROOT/$MANIFEST" 128 1
cd "$PROJECT"
mkdir -p logs
echo "HELD $STAGE tasks=$N concurrency=$CONC minutes=$MINUTES cores=128"
sbatch --parsable --hold --no-requeue -A che260157 -p shared -N 1 -n 128 \
    --cpus-per-task=1 --mem=237G --time="$MINUTES" --exclude="$EXCLUDE" \
    --job-name="research-$STAGE" --array="1-$N%$CONC" \
    --export=ALL,PROJECT,STAGE "$ROOT/anvil/78_slab_scf_seeded.slurm"
