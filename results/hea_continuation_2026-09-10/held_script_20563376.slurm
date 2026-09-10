#!/bin/bash
# One isolated, rank-attributed reproduction. No requeue, retries or scratch deletion.
#SBATCH -p shared
#SBATCH -N 1
#SBATCH -n 128
#SBATCH --mem=237G
#SBATCH -t 04:00:00
#SBATCH -J hea-ieee-smearing
#SBATCH -o logs/hea_ieee_smearing_%A_%a.out
#SBATCH -e logs/hea_ieee_smearing_%A_%a.out
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
SPEC="$ROOT/results/hea_sensitivity_2026-09-09/launch_spec.json"
FROZEN="$ROOT/src/dft/hea_numerical_guard.py"
GUARD="$ROOT/src/dft/hea_ieee_smearing_diagnostic.py"
SENSITIVITY="$ROOT/src/dft/hea_sensitivity_guard.py"
QC="$ROOT/src/dft/hea_followup_qc.py"
FORCE_AUDIT="$ROOT/src/dft/hea_force_audit.py"
WRAPPER="$ROOT/anvil/hea_ieee_smearing_rank.sh"
export PATH="$QE_PREFIX/bin:$PATH"
export LD_LIBRARY_PATH="$QE_PREFIX/lib:${LD_LIBRARY_PATH:-}"
export OMP_NUM_THREADS=1
export ESPRESSO_PSEUDO="$PSEUDO_DIR"
MPI=$(command -v mpirun) || exit 2
PW="$QE_PREFIX/bin/pw.x"
PROJECTION="$QE_PREFIX/bin/projwfc.x"
check_hash() { [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ] || { echo "REFUSE: pinned file differs: $1" >&2; exit 2; }; }
check_hash "$SPEC" fdce4056bf45c0479c6b00c6084804955d6314fa243e66bac336a0724fb581b9
check_hash "$MANIFEST" 4fb9f7c92844f6ba85501fd64030d1be1abfef73a1443d5d78d2afe8415d5a1b
check_hash "$FROZEN" 98d866553566d9e8ab660535f5bbc0c33228f5160df59eda9f41de9c85ee5f9a
check_hash "$GUARD" 820fa225b5ea72ada09cda80d4929332754b1106f87c52417504f6eab590d813
check_hash "$SENSITIVITY" 6c59cb5986e39c5117be72f4c4dc8e7f7184b8f539ff6dc6d31e56b89a96f4e6
check_hash "$QC" ef9b50193f46034036b892263a3ee139426d912b2098ebdc5a897a82dc2769da
check_hash "$FORCE_AUDIT" bddbe7ba3bed9874e723d88f8bdab724bb4e83178f1f75bbc3a1f4034b9fd5d7
check_hash "$WRAPPER" 94f7290f5b2887b022cfa2363dea3301a0078491a22c03993c683fa1ff7dedfb
check_hash "$MPI" a256bdcef89bdc61ba870e823056c51df868b4db48ab345a14278a7fe79ed75d
check_hash "$PW" 1d66c7856f5d6b3cd9c66b8578e01512b16bbe907b4360e54234890712ccd6a1
check_hash "$PROJECTION" 456387be5ee32f358bc9835240b2e8bd1f8144a27a8e116731a1463dbf78ac85
[ "$MANIFEST" = "$ROOT/runs/hea/m_ieee_smearing_2026-09-10.txt" ] && [ "$RUNS" = "$ROOT/runs" ] || {
  echo "REFUSE: unexpected diagnostic paths"; exit 2
}
"$PYTHON" "$GUARD" --runs "$RUNS" --prepare || exit 2
cd "$RUNS/hea/ieee_smearing_2026-09-10" || exit 2
job=hd__leader_pull2.10__ortho__smearing_repro
prefix=hc__leader_pull2.10__ortho__fragment
scratch=./tmp_hs__leader_pull2.10__ortho__smearing
trap 'echo "INTERRUPTED: preserving diagnostic scratch and rank streams"; exit 143' TERM HUP
trap 'echo "INTERRUPTED: preserving diagnostic scratch and rank streams"; exit 130' INT
scfrc=255
prc=''
finish() {
  local code=$1
  local args=(--runs "$RUNS" --summarize --scf-exit "$scfrc")
  if [ "$code" = 0 ]; then args+=(--require-complete); fi
  if [ -n "$prc" ]; then args+=(--projection-exit "$prc"); fi
  "$PYTHON" "$GUARD" "${args[@]}" || { echo "DIAGNOSTIC REPORT FAILED: all evidence preserved"; exit 20; }
  if [ "$code" = 0 ]; then echo "CLEAN REPRODUCTION: current endpoint complete; prior flagged run remains rejected"; fi
  exit "$code"
}
echo "DIAGNOSTIC: one four-hour task; unchanged input, checkpoint, MPI128/pools8; rank stderr retained"
echo "node=$(hostname) started=$(date -u) mpi=$MPI"
export DIAG_RANK_DIR="$PWD/${job}.rank_stderr"
"$MPI" --oversubscribe -np 128 bash "$WRAPPER" "$PW" -nk 8 -in "${job}.run.in" \
  > "${job}.stdout" 2> "${job}.launcher.stderr" </dev/null
scfrc=$?
"$PYTHON" "$GUARD" --runs "$RUNS" --assemble scf
capture_rc=$?
"$PYTHON" "$FROZEN" --startup-output "${job}.out" --mode tight
startup_rc=$?
"$PYTHON" "$QC" --input "${job}.run.in" --output "${job}.out" --json "${job}.scf_qc.json"
qc_rc=$?
if [ "$scfrc" -ne 0 ] || [ "$capture_rc" -ne 0 ] || [ "$startup_rc" -ne 0 ] || [ "$qc_rc" -ne 0 ]; then
  echo "DIAGNOSTIC SCF REJECTED: no projection; all source/clone/rank evidence retained"
  finish 16
fi
# Projection is conditional on a clean SCF; capture every projection rank too.
mkdir "${job}.projwfc.rank_stderr" || finish 17
if ! cat > "${job}.projwfc.in" <<PWF
&PROJWFC
  prefix = '${prefix}'
  outdir = '${scratch}'
  lsym = .true.
/
PWF
then
  echo "PROJECTION INPUT FAILED"; finish 17
fi
export DIAG_RANK_DIR="$PWD/${job}.projwfc.rank_stderr"
"$MPI" --oversubscribe -np 128 bash "$WRAPPER" "$PROJECTION" -nk 8 -in "${job}.projwfc.in" \
  > "${job}.projwfc.stdout" 2> "${job}.projwfc.launcher.stderr" </dev/null
prc=$?
"$PYTHON" "$GUARD" --runs "$RUNS" --assemble projection
capture_rc=$?
"$PYTHON" "$QC" --input "${job}.run.in" --output "${job}.out" \
  --projection "${job}.projwfc.out" --json "${job}.qc.json"
qc_rc=$?
if [ "$prc" -ne 0 ] || [ "$capture_rc" -ne 0 ] || [ "$qc_rc" -ne 0 ]; then
  echo "PROJECTION REJECTED: clean SCF diagnosis retained; new endpoint incomplete"
  finish 17
fi
for member in data-file-schema.xml charge-density.hdf5 occup.txt paw.txt; do
  [ -s "$scratch/$prefix.save/$member" ] || { echo "RETENTION INCOMPLETE"; finish 18; }
done
for spin in up dw; do
  for k in 1 2 3 4 5 6 7 8; do
    [ -s "$scratch/$prefix.save/wfc${spin}${k}.hdf5" ] || { echo "RETENTION INCOMPLETE"; finish 18; }
  done
done
finish 0
