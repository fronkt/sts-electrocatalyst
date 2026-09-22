#!/bin/bash
# Arm A: checked low-state relaxation, 2026-09-22; scheduler resources set at submission.
#SBATCH -p shared
#SBATCH -N 1
#SBATCH -n 128
#SBATCH -o logs/slabrelaxchecked_%A_%a.out
#SBATCH -e logs/slabrelaxchecked_%A_%a.out
set -euo pipefail
[ "${PROJECT:-}" = /anvil/projects/x-che260157 ] || { echo 'REFUSE: project'; exit 2; }
[ "${SLURM_NTASKS:-}" = 128 ] || { echo 'REFUSE: requires 128 ranks'; exit 2; }
[ "${STAGE:-}" = slab_relax_checked ] || exit 2
ROOT="$PROJECT/sts"
SPEC="$ROOT/results/lowtail_low_state_restart_2026-09-22/checked/launch_spec.json"
RUNNER="$ROOT/src/dft/research_batch_checked.py"
check_hash() { [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ] || { echo "REFUSE: hash $1"; exit 2; }; }
check_hash "$SPEC" d361aa8080f131e2db0e48be9e973b212afac97a464b9a28c0ead881ee3f5454
check_hash "$RUNNER" b8744a14b064e8313d4e64b6542314faf0405539bf6ba1c74e22654304ceb75a
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
echo "STAGE $STAGE TASK ${SLURM_ARRAY_TASK_ID:?} NODE $(hostname) START $(date -u)"
exec "$PYTHON" "$RUNNER" --spec "$SPEC" --root "$ROOT" --stage "$STAGE" \
     --row "$SLURM_ARRAY_TASK_ID" --pseudo "$PROJECT/pseudo" --qe "$PROJECT/qe/env"
