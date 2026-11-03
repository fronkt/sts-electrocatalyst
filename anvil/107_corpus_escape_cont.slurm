#!/bin/bash
# Corpus escape continuation (docs/research/corpus-escape-2026-11-01.md, section "Tier 1a continuation"). The six tier 1a escape relaxations (nosym)
# restarted from their last computed geometry, one pw.x relaxation per array task through the pinned seeded runner as
# a stage of kind "relax". Resources, held state, time limit and the array throttle are set at submission and
# validated before release. No retry or requeue.
#SBATCH --account=che260157
#SBATCH --partition=wholenode
#SBATCH --nodes=1
#SBATCH --ntasks=128
#SBATCH --cpus-per-task=1
#SBATCH --mem=200G
#SBATCH --no-requeue
#SBATCH --output=/anvil/projects/x-che260157/sts_corpus_escape_cont_2026-11-02/logs/corpus_escape_cont_%A_%a.log
#SBATCH --error=/anvil/projects/x-che260157/sts_corpus_escape_cont_2026-11-02/logs/corpus_escape_cont_%A_%a.log
set -euo pipefail
PROJECT=/anvil/projects/x-che260157
ROOT="$PROJECT/sts_corpus_escape_cont_2026-11-02"
SPEC="$ROOT/results/corpus_escape_cont_2026-11-02/launch_spec.json"
RUNNER="$ROOT/src/dft/research_batch_seeded.py"
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
[ "${SLURM_NTASKS:-}" = 128 ] || { echo 'REFUSE: requires 128 ranks'; exit 2; }
case "${STAGE:-}" in tier1a_cont_escape) ;; *) echo 'REFUSE: stage'; exit 2;; esac
check_hash() { [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ] || { echo "REFUSE: hash $1"; exit 2; }; }
check_hash "$SPEC" 7c57d1f827805b61632efbd06954a18f29b0eb2359374ab5149f1bac18dcbc93
check_hash "$RUNNER" 32d705a5cda6467d6f0b48bbc274abd751ed6959e583375bd62de9d1ce0a7231
export OMP_NUM_THREADS=1 OMP_THREAD_LIMIT=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 OMP_DYNAMIC=FALSE MKL_DYNAMIC=FALSE
echo "STAGE $STAGE TASK ${SLURM_ARRAY_TASK_ID:?} NODE $(hostname) START $(date -u)"
exec "$PYTHON" "$RUNNER" --spec "$SPEC" --root "$ROOT" --stage "$STAGE" \
     --row "$SLURM_ARRAY_TASK_ID" --pseudo "$ROOT/pseudo" --qe "$PROJECT/qe/env"
