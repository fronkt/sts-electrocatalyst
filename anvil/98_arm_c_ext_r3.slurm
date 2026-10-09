#!/bin/bash
# S8 arm C extension, round 3 (docs/research/s8-arm-c-extension-2026-10-08.md; Frank, 2026-10-09: "Lets do a
# round 3", then "0.3 + longer memory"). The last missing state of one Cu8 and one Fe25 support site, each from
# round 2's moved density with mixing_ndim 16 at mixing_beta 0.3, one SCF per array task through the pinned
# seeded runner (r3_main). Resources, held state, time limit and the array throttle are set at submission and
# validated before release. No retry or requeue.
#SBATCH --account=che260157
#SBATCH --partition=wholenode
#SBATCH --nodes=1
#SBATCH --ntasks=128
#SBATCH --cpus-per-task=1
#SBATCH --mem=200G
#SBATCH --no-requeue
#SBATCH --output=/anvil/projects/x-che260157/sts_arm_c_ext_r3_2026-10-09/logs/arm_c_ext_r3_%A_%a.log
#SBATCH --error=/anvil/projects/x-che260157/sts_arm_c_ext_r3_2026-10-09/logs/arm_c_ext_r3_%A_%a.log
set -euo pipefail
PROJECT=/anvil/projects/x-che260157
ROOT="$PROJECT/sts_arm_c_ext_r3_2026-10-09"
SPEC="$ROOT/results/arm_c_ext_r3_2026-10-09/launch_spec.json"
RUNNER="$ROOT/src/dft/research_batch_seeded.py"
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
[ "${SLURM_NTASKS:-}" = 128 ] || { echo 'REFUSE: requires 128 ranks'; exit 2; }
case "${STAGE:-}" in r3_main) ;; *) echo 'REFUSE: stage'; exit 2;; esac
check_hash() { [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ] || { echo "REFUSE: hash $1"; exit 2; }; }
check_hash "$SPEC" 0fda5b375b40b7fbe61a15f35e101dbc47c4d84cb450523cbe593942a5224f45
check_hash "$RUNNER" 32d705a5cda6467d6f0b48bbc274abd751ed6959e583375bd62de9d1ce0a7231
export OMP_NUM_THREADS=1 OMP_THREAD_LIMIT=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 OMP_DYNAMIC=FALSE MKL_DYNAMIC=FALSE
echo "STAGE $STAGE TASK ${SLURM_ARRAY_TASK_ID:?} NODE $(hostname) START $(date -u)"
exec "$PYTHON" "$RUNNER" --spec "$SPEC" --root "$ROOT" --stage "$STAGE" \
     --row "$SLURM_ARRAY_TASK_ID" --pseudo "$PROJECT/pseudo" --qe "$PROJECT/qe/env"
