#!/bin/bash
# Low-state relaxation restart, 2026-09-22; scheduler resources set at submission.
#SBATCH -p shared
#SBATCH -N 1
#SBATCH -n 128
#SBATCH -o logs/slabrelaxseed_%A_%a.out
#SBATCH -e logs/slabrelaxseed_%A_%a.out
set -euo pipefail
[ "${PROJECT:-}" = /anvil/projects/x-che260157 ] || { echo 'REFUSE: project'; exit 2; }
[ "${SLURM_NTASKS:-}" = 128 ] || { echo 'REFUSE: requires 128 ranks'; exit 2; }
[ "${STAGE:-}" = slab_relax_seeded ] || exit 2
ROOT="$PROJECT/sts"
SPEC="$ROOT/results/lowtail_low_state_restart_2026-09-22/relax/launch_spec.json"
RUNNER="$ROOT/src/dft/research_batch_seeded.py"
check_hash() { [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ] || { echo "REFUSE: hash $1"; exit 2; }; }
check_hash "$SPEC" 1aac528de88e568eee87543f551555fc98f980e42260106ad9b6cdd2ca7c1ec6
check_hash "$RUNNER" 32d705a5cda6467d6f0b48bbc274abd751ed6959e583375bd62de9d1ce0a7231
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
echo "STAGE $STAGE TASK ${SLURM_ARRAY_TASK_ID:?} NODE $(hostname) START $(date -u)"
exec "$PYTHON" "$RUNNER" --spec "$SPEC" --root "$ROOT" --stage "$STAGE" \
     --row "$SLURM_ARRAY_TASK_ID" --pseudo "$PROJECT/pseudo" --qe "$PROJECT/qe/env"
