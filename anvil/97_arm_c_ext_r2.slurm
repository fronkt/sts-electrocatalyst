#!/bin/bash
# S8 arm C extension, round 2 (docs/research/s8-arm-c-extension-2026-10-08.md; Frank, 2026-10-08: "repair",
# after the round-1 canary failed). Seeded fixed-geometry SCFs at the Cu8 and Fe25 support sites, each reading
# its seed density moved onto the target's atoms, one SCF per array task through the pinned seeded runner:
# a two-task canary (r2_canary), then the main array (r2_main). Resources, held state, time limit and the
# array throttle are set at submission and validated before release. No retry or requeue.
#SBATCH --account=che260157
#SBATCH --partition=wholenode
#SBATCH --nodes=1
#SBATCH --ntasks=128
#SBATCH --cpus-per-task=1
#SBATCH --mem=200G
#SBATCH --no-requeue
#SBATCH --output=/anvil/projects/x-che260157/sts_arm_c_ext_r2_2026-10-08/logs/arm_c_ext_r2_%A_%a.log
#SBATCH --error=/anvil/projects/x-che260157/sts_arm_c_ext_r2_2026-10-08/logs/arm_c_ext_r2_%A_%a.log
set -euo pipefail
PROJECT=/anvil/projects/x-che260157
ROOT="$PROJECT/sts_arm_c_ext_r2_2026-10-08"
SPEC="$ROOT/results/arm_c_ext_r2_2026-10-08/launch_spec.json"
RUNNER="$ROOT/src/dft/research_batch_seeded.py"
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
[ "${SLURM_NTASKS:-}" = 128 ] || { echo 'REFUSE: requires 128 ranks'; exit 2; }
case "${STAGE:-}" in r2_canary|r2_main) ;; *) echo 'REFUSE: stage'; exit 2;; esac
check_hash() { [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ] || { echo "REFUSE: hash $1"; exit 2; }; }
check_hash "$SPEC" 6e9c7058e96c1dd60b10a5e9b8b6a0e401a650a586a1ea19ec4074398872a06b
check_hash "$RUNNER" 32d705a5cda6467d6f0b48bbc274abd751ed6959e583375bd62de9d1ce0a7231
export OMP_NUM_THREADS=1 OMP_THREAD_LIMIT=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 OMP_DYNAMIC=FALSE MKL_DYNAMIC=FALSE
echo "STAGE $STAGE TASK ${SLURM_ARRAY_TASK_ID:?} NODE $(hostname) START $(date -u)"
exec "$PYTHON" "$RUNNER" --spec "$SPEC" --root "$ROOT" --stage "$STAGE" \
     --row "$SLURM_ARRAY_TASK_ID" --pseudo "$PROJECT/pseudo" --qe "$PROJECT/qe/env"
