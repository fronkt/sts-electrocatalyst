#!/bin/bash
# S8 arm C fixed-geometry DFT+U single points (docs/research/s8-arm-c-dft-design-2026-10-07.md).
# One SCF per array task through the unchanged September runner; resources, held state and the
# array throttle are set at submission and validated before release. No retry or requeue.
#SBATCH --account=che260157
#SBATCH --partition=wholenode
#SBATCH --nodes=1
#SBATCH --ntasks=128
#SBATCH --cpus-per-task=1
#SBATCH --mem=200G
#SBATCH --no-requeue
#SBATCH --output=/anvil/projects/x-che260157/sts_arm_c_2026-10-07/logs/arm_c_%A_%a.log
#SBATCH --error=/anvil/projects/x-che260157/sts_arm_c_2026-10-07/logs/arm_c_%A_%a.log
set -euo pipefail
PROJECT=/anvil/projects/x-che260157
ROOT="$PROJECT/sts_arm_c_2026-10-07"
SPEC="$ROOT/results/arm_c_2026-10-07/launch_spec.json"
RUNNER="$ROOT/src/dft/research_batch.py"
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
[ "${SLURM_NTASKS:-}" = 128 ] || { echo 'REFUSE: requires 128 ranks'; exit 2; }
case "${STAGE:-}" in arm_c_main|arm_c_probe) ;; *) echo 'REFUSE: stage'; exit 2;; esac
check_hash() { [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ] || { echo "REFUSE: hash $1"; exit 2; }; }
check_hash "$SPEC" 48c7cb686d2cc73cd3f6f1e89a9fd02d7904b8181c78241f22cee6cf90ad66f4
check_hash "$RUNNER" 4195ef7b7b23096c982d78f80b5a8d78884bc8d9b7e2fc8a150f747e1cf2c404
export OMP_NUM_THREADS=1 OMP_THREAD_LIMIT=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 OMP_DYNAMIC=FALSE MKL_DYNAMIC=FALSE
echo "STAGE $STAGE TASK ${SLURM_ARRAY_TASK_ID:?} NODE $(hostname) START $(date -u)"
exec "$PYTHON" "$RUNNER" --spec "$SPEC" --root "$ROOT" --stage "$STAGE" \
     --row "$SLURM_ARRAY_TASK_ID" --pseudo "$PROJECT/pseudo" --qe "$PROJECT/qe/env"
