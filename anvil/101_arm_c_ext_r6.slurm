#!/bin/bash
# S8 arm C extension, round 6 (docs/research/s8-arm-c-extension-2026-10-08.md; Frank, 2026-10-10: "Go ahead with
# other values"). Second starts of the slab and the OH at Ni31 s1/0 and Cu26 s1/0, each from its own converged
# density with Cr 19's Hubbard occupations and PAW block from the other state, the occupations held for the first 5
# iterations (mixing_fixed_ns): two SCFs per site in one two-task array each through the pinned seeded runner
# (r6_ni31, 120 min; r6_cu26, 180 min). Resources, held state and time limit are set at submission and validated
# before release. No retry or requeue.
#SBATCH --account=che260157
#SBATCH --partition=wholenode
#SBATCH --nodes=1
#SBATCH --ntasks=128
#SBATCH --cpus-per-task=1
#SBATCH --mem=200G
#SBATCH --no-requeue
#SBATCH --output=/anvil/projects/x-che260157/sts_arm_c_ext_r6_2026-10-11/logs/arm_c_ext_r6_%A_%a.log
#SBATCH --error=/anvil/projects/x-che260157/sts_arm_c_ext_r6_2026-10-11/logs/arm_c_ext_r6_%A_%a.log
set -euo pipefail
PROJECT=/anvil/projects/x-che260157
ROOT="$PROJECT/sts_arm_c_ext_r6_2026-10-11"
SPEC="$ROOT/results/arm_c_ext_r6_2026-10-11/launch_spec.json"
RUNNER="$ROOT/src/dft/research_batch_seeded.py"
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
[ "${SLURM_NTASKS:-}" = 128 ] || { echo 'REFUSE: requires 128 ranks'; exit 2; }
case "${STAGE:-}" in r6_ni31|r6_cu26) ;; *) echo 'REFUSE: stage'; exit 2;; esac
check_hash() { [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ] || { echo "REFUSE: hash $1"; exit 2; }; }
check_hash "$SPEC" ae56df7eed746f8989bc0c9bec0cd9b3ed325aa1ce4c98577d52185deaa1846d
check_hash "$RUNNER" 32d705a5cda6467d6f0b48bbc274abd751ed6959e583375bd62de9d1ce0a7231
export OMP_NUM_THREADS=1 OMP_THREAD_LIMIT=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 OMP_DYNAMIC=FALSE MKL_DYNAMIC=FALSE
echo "STAGE $STAGE TASK ${SLURM_ARRAY_TASK_ID:?} NODE $(hostname) START $(date -u)"
exec "$PYTHON" "$RUNNER" --spec "$SPEC" --root "$ROOT" --stage "$STAGE" \
     --row "$SLURM_ARRAY_TASK_ID" --pseudo "$PROJECT/pseudo" --qe "$PROJECT/qe/env"
