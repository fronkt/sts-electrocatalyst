#!/bin/bash
# B1 stage 2 (docs/research/b1-relaxed-projector-2026-10-16.md; Frank, 2026-10-16: "Go ahead"; 2026-10-18: "Repair").
# Eight fresh-start U = 7.15 eV SCFs at the selected relaxation endpoints (GATE-1), one per array task, through the
# pinned seeded runner as a stage of kind "scf". Resources, held state
# and time limit are set at submission and validated before release. No retry or requeue.
#SBATCH --account=che260157
#SBATCH --partition=wholenode
#SBATCH --nodes=1
#SBATCH --ntasks=128
#SBATCH --cpus-per-task=1
#SBATCH --mem=200G
#SBATCH --no-requeue
#SBATCH --output=/anvil/projects/x-che260157/sts_b1_terminal_scf_2026-10-17/logs/b1_scf_%A_%a.log
#SBATCH --error=/anvil/projects/x-che260157/sts_b1_terminal_scf_2026-10-17/logs/b1_scf_%A_%a.log
set -euo pipefail
PROJECT=/anvil/projects/x-che260157
ROOT="$PROJECT/sts_b1_terminal_scf_2026-10-17"
SPEC="$ROOT/results/b1_terminal_scf_2026-10-17/launch_spec.json"
RUNNER="$ROOT/src/dft/research_batch_seeded.py"
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
[ "${SLURM_NTASKS:-}" = 128 ] || { echo 'REFUSE: requires 128 ranks'; exit 2; }
case "${STAGE:-}" in b1_scf) ;; *) echo 'REFUSE: stage'; exit 2;; esac
check_hash() { [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ] || { echo "REFUSE: hash $1"; exit 2; }; }
check_hash "$SPEC" 9b945f97a67debc4c9287e33984d033b0d451d3fd7bc620c45abceb1080f40d6
check_hash "$RUNNER" 32d705a5cda6467d6f0b48bbc274abd751ed6959e583375bd62de9d1ce0a7231
export OMP_NUM_THREADS=1 OMP_THREAD_LIMIT=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 OMP_DYNAMIC=FALSE MKL_DYNAMIC=FALSE
echo "STAGE $STAGE TASK ${SLURM_ARRAY_TASK_ID:?} NODE $(hostname) START $(date -u)"
exec "$PYTHON" "$RUNNER" --spec "$SPEC" --root "$ROOT" --stage "$STAGE" \
     --row "$SLURM_ARRAY_TASK_ID" --pseudo "$PROJECT/pseudo" --qe "$PROJECT/qe/env"
