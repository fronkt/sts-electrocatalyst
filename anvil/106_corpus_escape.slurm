#!/bin/bash
# Corpus escape (docs/research/corpus-escape-2026-11-01.md). Held (symmetry on) and escape (nosym, adsorbate displaced along the locked
# axis) relaxations of locked Xu four-layer *OOH (tier 1) and *OH (tier 2) outputs, one pw.x relaxation per array
# task through the pinned seeded runner as stages of kind "relax". Resources, held state, time limit and the array
# throttle are set at submission and validated before release. No retry or requeue.
#SBATCH --account=che260157
#SBATCH --partition=wholenode
#SBATCH --nodes=1
#SBATCH --ntasks=128
#SBATCH --cpus-per-task=1
#SBATCH --mem=200G
#SBATCH --no-requeue
#SBATCH --output=/anvil/projects/x-che260157/sts_corpus_escape_2026-11-01/logs/corpus_escape_%A_%a.log
#SBATCH --error=/anvil/projects/x-che260157/sts_corpus_escape_2026-11-01/logs/corpus_escape_%A_%a.log
set -euo pipefail
PROJECT=/anvil/projects/x-che260157
ROOT="$PROJECT/sts_corpus_escape_2026-11-01"
SPEC="$ROOT/results/corpus_escape_2026-11-01/launch_spec.json"
RUNNER="$ROOT/src/dft/research_batch_seeded.py"
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
[ "${SLURM_NTASKS:-}" = 128 ] || { echo 'REFUSE: requires 128 ranks'; exit 2; }
case "${STAGE:-}" in tier1a_held|tier1a_escape|tier1b_held|tier1b_escape|tier2_held|tier2_escape) ;; *) echo 'REFUSE: stage'; exit 2;; esac
check_hash() { [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ] || { echo "REFUSE: hash $1"; exit 2; }; }
check_hash "$SPEC" 32558d0bdca3bfc13cd1e8a8c5109efd496182e2390da12c2d79ceaab556c094
check_hash "$RUNNER" 32d705a5cda6467d6f0b48bbc274abd751ed6959e583375bd62de9d1ce0a7231
export OMP_NUM_THREADS=1 OMP_THREAD_LIMIT=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 OMP_DYNAMIC=FALSE MKL_DYNAMIC=FALSE
echo "STAGE $STAGE TASK ${SLURM_ARRAY_TASK_ID:?} NODE $(hostname) START $(date -u)"
exec "$PYTHON" "$RUNNER" --spec "$SPEC" --root "$ROOT" --stage "$STAGE" \
     --row "$SLURM_ARRAY_TASK_ID" --pseudo "$ROOT/pseudo" --qe "$PROJECT/qe/env"
