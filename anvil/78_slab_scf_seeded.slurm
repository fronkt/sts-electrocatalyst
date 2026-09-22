#!/bin/bash
# Discriminating SCFs from the retained density, 2026-09-22; scheduler resources set at submission.
#SBATCH -p shared
#SBATCH -N 1
#SBATCH -n 128
#SBATCH -o logs/slabrestart_%A_%a.out
#SBATCH -e logs/slabrestart_%A_%a.out
set -euo pipefail
[ "${PROJECT:-}" = /anvil/projects/x-che260157 ] || { echo 'REFUSE: project'; exit 2; }
[ "${SLURM_NTASKS:-}" = 128 ] || { echo 'REFUSE: requires 128 ranks'; exit 2; }
[ "${STAGE:-}" = slab_scf_seeded ] || exit 2
ROOT="$PROJECT/sts"
SPEC="$ROOT/results/lowtail_slab_scf_seeded_2026-09-22/launch_spec.json"
RUNNER="$ROOT/src/dft/research_batch_seeded.py"
check_hash() { [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ] || { echo "REFUSE: hash $1"; exit 2; }; }
check_hash "$SPEC" 28fef16439e658101ae50c1a59628666767fca7684cf8c03e3a43ddaa4a1ec75
check_hash "$RUNNER" ef4116f6e46f6168c958466a93324b673ca89599be30c2b1dc9fb8f3915064d0
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
echo "STAGE $STAGE TASK ${SLURM_ARRAY_TASK_ID:?} NODE $(hostname) START $(date -u)"
exec "$PYTHON" "$RUNNER" --spec "$SPEC" --root "$ROOT" --stage "$STAGE" \
     --row "$SLURM_ARRAY_TASK_ID" --pseudo "$PROJECT/pseudo" --qe "$PROJECT/qe/env"
