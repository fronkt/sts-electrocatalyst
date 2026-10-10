#!/bin/bash
# S8 arm C extension, round 5 (docs/research/s8-arm-c-extension-2026-10-08.md; Frank, 2026-10-10: "Just do the
# test since its so small"). A second start of the Fe25 s25/2 slab from its own converged density, with Fe 22's
# Hubbard occupations and PAW block from the converged OH state, the occupations held for the first 5 iterations
# (mixing_fixed_ns), one SCF in a one-task array through the pinned seeded runner (r5_main). Resources, held state and time limit are set at submission and validated before
# release. No retry or requeue.
#SBATCH --account=che260157
#SBATCH --partition=wholenode
#SBATCH --nodes=1
#SBATCH --ntasks=128
#SBATCH --cpus-per-task=1
#SBATCH --mem=200G
#SBATCH --no-requeue
#SBATCH --output=/anvil/projects/x-che260157/sts_arm_c_ext_r5_2026-10-10/logs/arm_c_ext_r5_%A_%a.log
#SBATCH --error=/anvil/projects/x-che260157/sts_arm_c_ext_r5_2026-10-10/logs/arm_c_ext_r5_%A_%a.log
set -euo pipefail
PROJECT=/anvil/projects/x-che260157
ROOT="$PROJECT/sts_arm_c_ext_r5_2026-10-10"
SPEC="$ROOT/results/arm_c_ext_r5_2026-10-10/launch_spec.json"
RUNNER="$ROOT/src/dft/research_batch_seeded.py"
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
[ "${SLURM_NTASKS:-}" = 128 ] || { echo 'REFUSE: requires 128 ranks'; exit 2; }
case "${STAGE:-}" in r5_main) ;; *) echo 'REFUSE: stage'; exit 2;; esac
check_hash() { [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ] || { echo "REFUSE: hash $1"; exit 2; }; }
check_hash "$SPEC" 309aed128870e430fb8c2c4b91ab53716d46c95bb54385d2be7bc61cb2b04d1b
check_hash "$RUNNER" 32d705a5cda6467d6f0b48bbc274abd751ed6959e583375bd62de9d1ce0a7231
export OMP_NUM_THREADS=1 OMP_THREAD_LIMIT=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 OMP_DYNAMIC=FALSE MKL_DYNAMIC=FALSE
echo "STAGE $STAGE TASK ${SLURM_ARRAY_TASK_ID:?} NODE $(hostname) START $(date -u)"
exec "$PYTHON" "$RUNNER" --spec "$SPEC" --root "$ROOT" --stage "$STAGE" \
     --row "$SLURM_ARRAY_TASK_ID" --pseudo "$PROJECT/pseudo" --qe "$PROJECT/qe/env"
