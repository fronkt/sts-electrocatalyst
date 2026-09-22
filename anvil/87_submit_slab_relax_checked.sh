#!/bin/bash
# Submit Arm A: checked low-state relaxation, 2026-09-22 held; caller verifies scheduler fields before release. No retry/override.
set -euo pipefail
export PROJECT=/anvil/projects/x-che260157
export STAGE=slab_relax_checked
ROOT="$PROJECT/sts"
SPEC="$ROOT/results/lowtail_low_state_restart_2026-09-22/checked/launch_spec.json"
RUNNER="$ROOT/src/dft/research_batch_checked.py"
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
check_hash() { [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ] || { echo "REFUSE: hash $1"; exit 2; }; }
check_hash "$SPEC" d361aa8080f131e2db0e48be9e973b212afac97a464b9a28c0ead881ee3f5454
check_hash "$RUNNER" b8744a14b064e8313d4e64b6542314faf0405539bf6ba1c74e22654304ceb75a
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
    --export=ALL,PROJECT,STAGE "$ROOT/anvil/86_slab_relax_checked.slurm"
