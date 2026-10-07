#!/bin/bash
# S8 arm C re-run round (docs/research/s8-arm-c-dft-design-2026-10-07.md section 6; Frank, 2026-10-07:
# "Go with the full rerun."). Every failed production SCF once under its registered recipe, plus two
# recipe controls, one SCF per array task through the unchanged September runner. Resources, held
# state and the array throttle are set at submission and validated before release. No retry or requeue.
#SBATCH --account=che260157
#SBATCH --partition=wholenode
#SBATCH --nodes=1
#SBATCH --ntasks=128
#SBATCH --cpus-per-task=1
#SBATCH --mem=200G
#SBATCH --no-requeue
#SBATCH --output=/anvil/projects/x-che260157/sts_arm_c_2026-10-07_rerun/logs/arm_c_rerun_%A_%a.log
#SBATCH --error=/anvil/projects/x-che260157/sts_arm_c_2026-10-07_rerun/logs/arm_c_rerun_%A_%a.log
set -euo pipefail
PROJECT=/anvil/projects/x-che260157
ROOT="$PROJECT/sts_arm_c_2026-10-07_rerun"
SPEC="$ROOT/results/arm_c_2026-10-07_rerun/launch_spec.json"
RUNNER="$ROOT/src/dft/research_batch.py"
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
[ "${SLURM_NTASKS:-}" = 128 ] || { echo 'REFUSE: requires 128 ranks'; exit 2; }
case "${STAGE:-}" in arm_c_rerun) ;; *) echo 'REFUSE: stage'; exit 2;; esac
check_hash() { [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ] || { echo "REFUSE: hash $1"; exit 2; }; }
check_hash "$SPEC" 6a6a0b708f759174743bd7ae0166f5d036375b33e3d46f6a5d064e48a2bef354
check_hash "$RUNNER" 4195ef7b7b23096c982d78f80b5a8d78884bc8d9b7e2fc8a150f747e1cf2c404
export OMP_NUM_THREADS=1 OMP_THREAD_LIMIT=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 OMP_DYNAMIC=FALSE MKL_DYNAMIC=FALSE
echo "STAGE $STAGE TASK ${SLURM_ARRAY_TASK_ID:?} NODE $(hostname) START $(date -u)"
exec "$PYTHON" "$RUNNER" --spec "$SPEC" --root "$ROOT" --stage "$STAGE" \
     --row "$SLURM_ARRAY_TASK_ID" --pseudo "$PROJECT/pseudo" --qe "$PROJECT/qe/env"
