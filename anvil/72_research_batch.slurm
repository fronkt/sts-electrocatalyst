#!/bin/bash
# Exact September 16 fixed-geometry program; scheduler resources set at submission.
#SBATCH -p shared
#SBATCH -N 1
#SBATCH -n 128
#SBATCH -o logs/research_%A_%a.out
#SBATCH -e logs/research_%A_%a.out
set -euo pipefail
[ "${PROJECT:-}" = /anvil/projects/x-che260157 ] || { echo 'REFUSE: project'; exit 2; }
[ "${SLURM_NTASKS:-}" = 128 ] || { echo 'REFUSE: requires 128 ranks'; exit 2; }
case "${STAGE:-}" in hea_panel|hea_pilot|ru_pp|beef_preflight|beef_remaining) ;; *) exit 2;; esac
ROOT="$PROJECT/sts"
SPEC="$ROOT/results/research_launch_2026-09-16/launch_spec.json"
RUNNER="$ROOT/src/dft/research_batch.py"
check_hash() { [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ] || { echo "REFUSE: hash $1"; exit 2; }; }
check_hash "$SPEC" 9fbbb29e2e582700323dedc646b17afa00fe61ab6713e9896ee8c58635fc74c8
check_hash "$RUNNER" 1b91cc959c49d1de5f90e39fecb1df2bba13fd18f466451d11595bfc31952e1b
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
echo "STAGE $STAGE TASK ${SLURM_ARRAY_TASK_ID:?} NODE $(hostname) START $(date -u)"
exec "$PYTHON" "$RUNNER" --spec "$SPEC" --root "$ROOT" --stage "$STAGE" \
     --row "$SLURM_ARRAY_TASK_ID" --pseudo "$PROJECT/pseudo" --qe "$PROJECT/qe/env"
