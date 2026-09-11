#!/bin/bash
# One isolated, rank-attributed reproduction. No requeue, retries or scratch deletion.
#SBATCH -p shared
#SBATCH -N 1
#SBATCH -n 128
#SBATCH --mem=237G
#SBATCH -t 00:10:00
#SBATCH -J hea-ieee-init
#SBATCH -o logs/hea_ieee_initialization_%A_%a.out
#SBATCH -e logs/hea_ieee_initialization_%A_%a.out
set -uo pipefail
set -C
export LC_ALL=C
: "${PROJECT:?PROJECT required}"
: "${RUNS:?RUNS required}"
: "${MANIFEST:?MANIFEST required}"
: "${QE_PREFIX:?QE_PREFIX required}"
: "${PSEUDO_DIR:?PSEUDO_DIR required}"
[ "${NP:-128}" = 128 ] && [ "${SLURM_ARRAY_TASK_ID:-}" = 1 ] || {
  echo "REFUSE: diagnostic requires one task and NP128"; exit 2
}
[ "$PSEUDO_DIR" = /anvil/projects/x-che260157/pseudo ] || { echo "REFUSE: pseudo path differs"; exit 2; }
ROOT="$PROJECT/sts"
PYTHON="/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3"
SPEC="$ROOT/results/hea_ieee_init_2026-09-11/launch_spec.json"
FROZEN="$ROOT/src/dft/hea_numerical_guard.py"
GUARD="$ROOT/src/dft/hea_ieee_initialization_probe.py"
SENSITIVITY="$ROOT/src/dft/hea_sensitivity_guard.py"
QC="$ROOT/src/dft/hea_followup_qc.py"
FORCE_AUDIT="$ROOT/src/dft/hea_force_audit.py"
WRAPPER="$ROOT/anvil/hea_ieee_initialization_rank.sh"
export PATH="$QE_PREFIX/bin:$PATH"
export LD_LIBRARY_PATH="$QE_PREFIX/lib:${LD_LIBRARY_PATH:-}"
export OMP_NUM_THREADS=1
export ESPRESSO_PSEUDO="$PSEUDO_DIR"
MPI=$(command -v mpirun) || exit 2
PW="$QE_PREFIX/bin/pw.x"
check_hash() { [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ] || { echo "REFUSE: pinned file differs: $1" >&2; exit 2; }; }
check_hash "$SPEC" c5ad77a2b8764a856fad90721b5702c568c0fe87e6034f4c7c378075c59826bd
check_hash "$MANIFEST" 349214e2a4775a6c1e30d5c33f83578357eccd74480575e0f7cbb08b0a74880c
check_hash "$FROZEN" 98d866553566d9e8ab660535f5bbc0c33228f5160df59eda9f41de9c85ee5f9a
check_hash "$GUARD" 7b58317aa8d23e2ba7ee4bc4ffc989244ebfd799f8ec94210d20d18e5d6eb11f
check_hash "$SENSITIVITY" 6c59cb5986e39c5117be72f4c4dc8e7f7184b8f539ff6dc6d31e56b89a96f4e6
check_hash "$QC" ef9b50193f46034036b892263a3ee139426d912b2098ebdc5a897a82dc2769da
check_hash "$FORCE_AUDIT" bddbe7ba3bed9874e723d88f8bdab724bb4e83178f1f75bbc3a1f4034b9fd5d7
check_hash "$WRAPPER" 902d6a7527362679e00578590a37e795a7e31b0e5477a51079544a9820911edd
check_hash "$MPI" a256bdcef89bdc61ba870e823056c51df868b4db48ab345a14278a7fe79ed75d
check_hash "$PW" 1d66c7856f5d6b3cd9c66b8578e01512b16bbe907b4360e54234890712ccd6a1
[ "$MANIFEST" = "$ROOT/runs/hea/m_ieee_init_2026-09-11.txt" ] && [ "$RUNS" = "$ROOT/runs" ] || {
  echo "REFUSE: unexpected diagnostic paths"; exit 2
}
"$PYTHON" "$GUARD" --runs "$RUNS" --pseudo-dir "$PSEUDO_DIR" --prepare || exit 2
cd "$RUNS/hea/ieee_init_2026-09-11" || exit 2
job=hi__leader_pull2.10__ortho__smearing_init
trap 'echo "INTERRUPTED: preserving setup probe scratch and rank streams"; exit 143' TERM HUP
trap 'echo "INTERRUPTED: preserving setup probe scratch and rank streams"; exit 130' INT
echo "SETUP PROBE: one ten-minute NP128/pools8 task; nstep=0, max_seconds=480; diagnostic only"
echo "node=$(hostname) started=$(date -u) mpi=$MPI"
export DIAG_RANK_DIR="$PWD/${job}.rank_stderr"
"$MPI" --oversubscribe -np 128 bash "$WRAPPER" "$PW" -nk 8 -in "${job}.run.in" \
  > "${job}.stdout" 2> "${job}.launcher.stderr" </dev/null
process_rc=$?
"$PYTHON" "$GUARD" --runs "$RUNS" --pseudo-dir "$PSEUDO_DIR" --assemble
capture_rc=$?
"$PYTHON" "$GUARD" --runs "$RUNS" --pseudo-dir "$PSEUDO_DIR" --summarize --process-exit "$process_rc"
report_rc=$?
if [ "$capture_rc" -ne 0 ] || [ "$report_rc" -ne 0 ]; then
  echo "SETUP PROBE FLAGGED/INCOMPLETE: no retry or projection; all evidence retained"
  exit 16
fi
echo "SETUP_ONLY_CLEAN: diagnostic only; no endpoint or checkpoint-read acceptance"
exit 0
