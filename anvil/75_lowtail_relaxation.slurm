#!/bin/bash
#SBATCH -p shared
#SBATCH -N 1
#SBATCH -n 128
#SBATCH -o logs/lowtail_%A_%a.out
#SBATCH -e logs/lowtail_%A_%a.out
set -euo pipefail
[ "${PROJECT:-}" = /anvil/projects/x-che260157 ] || { echo 'REFUSE: project'; exit 2; }
[ "${SLURM_NTASKS:-}" = 128 ] || { echo 'REFUSE: requires 128 ranks'; exit 2; }
ROOT="$PROJECT/sts"
SPEC="$ROOT/results/lowtail_dft_2026-09-18/launch_spec.json"
[ "$(sha256sum "$SPEC" | awk '{print $1}')" = '4165c374c41e51d47d5e7e20f33d036a8bf2ff49f4122dc410d95060ec10ee8d' ] || { echo 'REFUSE: specification hash'; exit 2; }
RUNNER="$ROOT/src/dft/lowtail_batch.py"
[ "$(sha256sum "$RUNNER" | awk '{print $1}')" = '0b05bac07e95e5109f3baf02d32cbfb214efebd9bed0b1b01be1558145c3e5b7' ] || { echo 'REFUSE: runner hash'; exit 2; }
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
echo "LOWTAIL TASK ${SLURM_ARRAY_TASK_ID:?} NODE $(hostname) START $(date -u)"
exec "$PYTHON" "$RUNNER" --spec "$SPEC" --root "$ROOT" --row "$SLURM_ARRAY_TASK_ID" --pseudo "$PROJECT/pseudo" --qe "$PROJECT/qe/env"
