#!/bin/bash
# S8 arm C extension, round 4 (docs/research/s8-arm-c-extension-2026-10-08.md; Frank, 2026-10-10: "Do the
# Fe25 O run"). The Fe25 s25/2 O from round 3's stopped density, with Fe 22's Hubbard occupations and PAW block
# from the converged OH state, the occupations held for the first 5 iterations (mixing_fixed_ns), one SCF in a
# one-task array through the pinned seeded runner (r4_main). Resources, held state and time limit are set at submission and validated before
# release. No retry or requeue.
#SBATCH --account=che260157
#SBATCH --partition=wholenode
#SBATCH --nodes=1
#SBATCH --ntasks=128
#SBATCH --cpus-per-task=1
#SBATCH --mem=200G
#SBATCH --no-requeue
#SBATCH --output=/anvil/projects/x-che260157/sts_arm_c_ext_r4_2026-10-10/logs/arm_c_ext_r4_%A_%a.log
#SBATCH --error=/anvil/projects/x-che260157/sts_arm_c_ext_r4_2026-10-10/logs/arm_c_ext_r4_%A_%a.log
set -euo pipefail
PROJECT=/anvil/projects/x-che260157
ROOT="$PROJECT/sts_arm_c_ext_r4_2026-10-10"
SPEC="$ROOT/results/arm_c_ext_r4_2026-10-10/launch_spec.json"
RUNNER="$ROOT/src/dft/research_batch_seeded.py"
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
[ "${SLURM_NTASKS:-}" = 128 ] || { echo 'REFUSE: requires 128 ranks'; exit 2; }
case "${STAGE:-}" in r4_main) ;; *) echo 'REFUSE: stage'; exit 2;; esac
check_hash() { [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ] || { echo "REFUSE: hash $1"; exit 2; }; }
check_hash "$SPEC" 78cef35f84ac14a2049fa97df603a01a1df5f5e99e33ba76f03f02beafd48511
check_hash "$RUNNER" 32d705a5cda6467d6f0b48bbc274abd751ed6959e583375bd62de9d1ce0a7231
export OMP_NUM_THREADS=1 OMP_THREAD_LIMIT=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 OMP_DYNAMIC=FALSE MKL_DYNAMIC=FALSE
echo "STAGE $STAGE TASK ${SLURM_ARRAY_TASK_ID:?} NODE $(hostname) START $(date -u)"
exec "$PYTHON" "$RUNNER" --spec "$SPEC" --root "$ROOT" --stage "$STAGE" \
     --row "$SLURM_ARRAY_TASK_ID" --pseudo "$PROJECT/pseudo" --qe "$PROJECT/qe/env"
