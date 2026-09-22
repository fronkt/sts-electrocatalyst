#!/bin/bash
# Arm B: low-state relaxation with mixing_fixed_ns = 15, 2026-09-22; scheduler resources set at submission.
#SBATCH -p shared
#SBATCH -N 1
#SBATCH -n 128
#SBATCH -o logs/slabrelaxfixedns_%A_%a.out
#SBATCH -e logs/slabrelaxfixedns_%A_%a.out
set -euo pipefail
[ "${PROJECT:-}" = /anvil/projects/x-che260157 ] || { echo 'REFUSE: project'; exit 2; }
[ "${SLURM_NTASKS:-}" = 128 ] || { echo 'REFUSE: requires 128 ranks'; exit 2; }
[ "${STAGE:-}" = slab_relax_fixedns ] || exit 2
ROOT="$PROJECT/sts"
SPEC="$ROOT/results/lowtail_low_state_restart_2026-09-22/fixedns/launch_spec.json"
RUNNER="$ROOT/src/dft/research_batch_seeded.py"
check_hash() { [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ] || { echo "REFUSE: hash $1"; exit 2; }; }
check_hash "$SPEC" b6a8337a6add990e79e3b0043257174e4077eeb5112416edae29914b8235323e
check_hash "$RUNNER" 32d705a5cda6467d6f0b48bbc274abd751ed6959e583375bd62de9d1ce0a7231
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
echo "STAGE $STAGE TASK ${SLURM_ARRAY_TASK_ID:?} NODE $(hostname) START $(date -u)"
exec "$PYTHON" "$RUNNER" --spec "$SPEC" --root "$ROOT" --stage "$STAGE" \
     --row "$SLURM_ARRAY_TASK_ID" --pseudo "$PROJECT/pseudo" --qe "$PROJECT/qe/env"
