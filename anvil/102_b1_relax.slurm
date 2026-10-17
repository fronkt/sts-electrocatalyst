#!/bin/bash
# B1 stage 1 (docs/research/b1-relaxed-projector-2026-10-16.md; Frank, 2026-10-16: "Go ahead"). Eight U = 7.15 eV
# relaxations of the 2x1 CrO2(110) slab, *O, *OH and escaped *OOH under the atomic and ortho-atomic Hubbard
# projectors, one per array task, through the pinned seeded runner as a stage of kind "relax". Resources, held state
# and time limit are set at submission and validated before release. No retry or requeue.
#SBATCH --account=che260157
#SBATCH --partition=wholenode
#SBATCH --nodes=1
#SBATCH --ntasks=128
#SBATCH --cpus-per-task=1
#SBATCH --mem=200G
#SBATCH --no-requeue
#SBATCH --output=/anvil/projects/x-che260157/sts_b1_relaxed_projector_2026-10-16/logs/b1_relax_%A_%a.log
#SBATCH --error=/anvil/projects/x-che260157/sts_b1_relaxed_projector_2026-10-16/logs/b1_relax_%A_%a.log
set -euo pipefail
PROJECT=/anvil/projects/x-che260157
ROOT="$PROJECT/sts_b1_relaxed_projector_2026-10-16"
SPEC="$ROOT/results/b1_relaxed_projector_2026-10-16/launch_spec.json"
RUNNER="$ROOT/src/dft/research_batch_seeded.py"
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
[ "${SLURM_NTASKS:-}" = 128 ] || { echo 'REFUSE: requires 128 ranks'; exit 2; }
case "${STAGE:-}" in b1_relax) ;; *) echo 'REFUSE: stage'; exit 2;; esac
check_hash() { [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ] || { echo "REFUSE: hash $1"; exit 2; }; }
check_hash "$SPEC" 5d445c40ce34cf44da3cb533fdb10bf40e6e7789ec84db8ad64727e1ccfb63ba
check_hash "$RUNNER" 32d705a5cda6467d6f0b48bbc274abd751ed6959e583375bd62de9d1ce0a7231
export OMP_NUM_THREADS=1 OMP_THREAD_LIMIT=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 OMP_DYNAMIC=FALSE MKL_DYNAMIC=FALSE
echo "STAGE $STAGE TASK ${SLURM_ARRAY_TASK_ID:?} NODE $(hostname) START $(date -u)"
exec "$PYTHON" "$RUNNER" --spec "$SPEC" --root "$ROOT" --stage "$STAGE" \
     --row "$SLURM_ARRAY_TASK_ID" --pseudo "$PROJECT/pseudo" --qe "$PROJECT/qe/env"
