#!/bin/bash
# Focused clean-slab SCF diagnostic, 2026-09-19; scheduler resources set at submission.
#SBATCH -p shared
#SBATCH -N 1
#SBATCH -n 128
#SBATCH -o logs/slabdiag_%A_%a.out
#SBATCH -e logs/slabdiag_%A_%a.out
set -euo pipefail
[ "${PROJECT:-}" = /anvil/projects/x-che260157 ] || { echo 'REFUSE: project'; exit 2; }
[ "${SLURM_NTASKS:-}" = 128 ] || { echo 'REFUSE: requires 128 ranks'; exit 2; }
[ "${STAGE:-}" = slab_scf_diag ] || exit 2
ROOT="$PROJECT/sts"
SPEC="$ROOT/results\lowtail_slab_scf_diag_2026-09-19\launch_spec.json"
RUNNER="$ROOT/src/dft/research_batch.py"
check_hash() { [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ] || { echo "REFUSE: hash $1"; exit 2; }; }
check_hash "$SPEC" 14726d4d0583b3c3c6a757c6d79df487b5e041e0e88e19b43b892d91048c125b
check_hash "$RUNNER" 4195ef7b7b23096c982d78f80b5a8d78884bc8d9b7e2fc8a150f747e1cf2c404
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
echo "STAGE $STAGE TASK ${SLURM_ARRAY_TASK_ID:?} NODE $(hostname) START $(date -u)"
exec "$PYTHON" "$RUNNER" --spec "$SPEC" --root "$ROOT" --stage "$STAGE" \
     --row "$SLURM_ARRAY_TASK_ID" --pseudo "$PROJECT/pseudo" --qe "$PROJECT/qe/env"
