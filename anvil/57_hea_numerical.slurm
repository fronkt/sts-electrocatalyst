#!/bin/bash
# Six numerical checks from protected checkpoint clones; frozen at execution.
# Four-hour allocation. All outcomes retain complete old and new scratch.
#SBATCH -p shared
#SBATCH -N 1
#SBATCH -n 128
#SBATCH -t 04:00:00
#SBATCH -J hea-numerical
#SBATCH -o logs/hea_numerical_%A_%a.out
#SBATCH -e logs/hea_numerical_%A_%a.out

set -uo pipefail
: "${PROJECT:?PROJECT must be exported}"
set -C  # noclobber: never replace a racing or preexisting output
export LC_ALL=C
: "${MANIFEST:?MANIFEST must be exported by the submitter}"
: "${RUNS:?RUNS must be exported by the submitter}"
: "${QE_PREFIX:?QE_PREFIX must be exported by the submitter}"
: "${PSEUDO_DIR:?PSEUDO_DIR must be exported by the submitter}"
NP=${NP:-128}
[ "$NP" = 128 ] || { echo "REFUSE: numerical requires NP=128"; exit 2; }
# Slurm copies the script; resolve helpers from the staged project.
ROOT="$PROJECT/sts"
PYTHON="/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3"
SPEC="$ROOT/results/hea_numerical_2026-09-08/launch_spec.json"
GUARD="$ROOT/src/dft/hea_numerical_guard.py"
QC="$ROOT/src/dft/hea_followup_qc.py"
FORCE_AUDIT="$ROOT/src/dft/hea_force_audit.py"
check_hash() { [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ] || { echo "REFUSE: pinned file differs: $1" >&2; exit 2; }; }
check_hash "$SPEC" 3326e14e7b25ec0d84576f42b7f3eaf11bff53b36f33b8a7d9416cd96758406a
check_hash "$GUARD" 98d866553566d9e8ab660535f5bbc0c33228f5160df59eda9f41de9c85ee5f9a
check_hash "$QC" ef9b50193f46034036b892263a3ee139426d912b2098ebdc5a897a82dc2769da
check_hash "$FORCE_AUDIT" bddbe7ba3bed9874e723d88f8bdab724bb4e83178f1f75bbc3a1f4034b9fd5d7
[ "$MANIFEST" = "$ROOT/runs/hea/m_numerical_2026-09-08.txt" ] || { echo "REFUSE: unexpected manifest path"; exit 2; }
[ "$RUNS" = "$ROOT/runs" ] || { echo "REFUSE: unexpected runs path"; exit 2; }
row=$("$PYTHON" "$GUARD" --spec "$SPEC" --runs "$RUNS" --prepare-row "${SLURM_ARRAY_TASK_ID:-}") || exit 2
read -r d job suf nk source_prefix mode extra <<< "$row"

dir="$RUNS/$d"
[ -d "$dir" ] && [ -f "$dir/${job}${suf}" ] || { echo "REFUSE: missing numerical directory/input"; exit 2; }
cd "$dir" || exit 2
inp="${job}${suf}"
out="$dir/${job}.out"
pout="$dir/${job}.projwfc.out"
scratch="./tmp_${job}"
prefix=$(sed -n "s#^[[:space:]]*prefix[[:space:]]*=[[:space:]]*'\([^']*\)'.*#\1#p" "$inp")
[ "$prefix" = "$source_prefix" ] || { echo "REFUSE: input prefix differs from approved source"; exit 2; }
# --prepare-row has claimed and verified this independent clone exclusively.
[ -d "$scratch/$prefix.save" ] && [ -s "${job}.clone_receipt.json" ] || {
  echo "REFUSE: verified clone/receipt absent"; exit 2
}
trap 'echo "INTERRUPTED: preserving numerical scratch $scratch"; exit 143' TERM HUP
trap 'echo "INTERRUPTED: preserving numerical scratch $scratch"; exit 130' INT
[ "$PSEUDO_DIR" = "/anvil/projects/x-che260157/pseudo" ] || {
  echo "REFUSE: pseudo directory differs from frozen runtime input"; exit 2
}
[ -s "${job}.run.in" ] || { echo "REFUSE: frozen runtime input absent"; exit 2; }
export PATH="$QE_PREFIX/bin:$PATH"
export LD_LIBRARY_PATH="$QE_PREFIX/lib:${LD_LIBRARY_PATH:-}"
export OMP_NUM_THREADS=1
export ESPRESSO_PSEUDO="$PSEUDO_DIR"
echo "TASK ${SLURM_ARRAY_TASK_ID} $d/$job np=$NP nk=$nk node=$(hostname) cpus=${SLURM_CPUS_ON_NODE:-?} $(date -u)"
echo "NUMERICAL: four-hour allocation; QE max_seconds=13200 reserves nominal 20min for exit/projection; no automatic retries"
t0=$(date +%s)
mpirun --oversubscribe -np "$NP" pw.x -nk "$nk" -in "${job}.run.in" > "$out" 2>&1 </dev/null
rc=$?
t1=$(date +%s)
# JOB DONE alone also appears after non-convergence/max_seconds/user stops.
number='[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)([eEdD][+-]?[0-9]+)?'
energies=$(grep -acE "^![[:space:]]+total energy[[:space:]]*=[[:space:]]*$number[[:space:]]+Ry[[:space:]]*$" "$out" || true)
converged=$(grep -acE 'convergence has been achieved in[[:space:]]+[0-9]+ iterations' "$out" || true)
done_=$(grep -ac 'JOB DONE' "$out" || true)
fail_pattern='convergence NOT achieved|Maximum (CPU|wall) time exceeded|Program stopped by user request|Error in routine|MPI_ABORT|SIGTERM|SIGINT|SIGSEGV'
failed=$(grep -acE "$fail_pattern" "$out" || true)
final=$(grep -a '^!' "$out" | tail -1)
echo "TASK ${SLURM_ARRAY_TASK_ID} $d/$job rc=$rc wall=$((t1-t0))s converged=$converged energies=$energies job_done=$done_ failures=$failed $(date -u)"
echo "   final: ${final:-NA}"
if [ "$rc" -ne 0 ] || [ "${energies:-0}" -ne 1 ] || [ "${converged:-0}" -ne 1 ] || [ "${done_:-0}" -ne 1 ] || [ "${failed:-1}" -ne 0 ]; then
  echo "SCF FAILED: preserving $scratch, runtime input and output; no projection or retry"
  [ "$rc" -ne 0 ] && exit "$rc"
  exit 10
fi
# Use the same positive startup contract as the independent readout.
if ! "$PYTHON" "$GUARD" --startup-output "$out" --mode "$mode"; then
  echo "STARTUP QC FAILED: preserving all scratch"; exit 18
fi
# Validate ordered finite forces before projection; large residual force is recorded.
if ! "$PYTHON" "$QC" --input "${job}.run.in" --output "$out" --json "${job}.scf_qc.json"; then
  echo "SCF FORCE QC FAILED: preserving $scratch"; exit 16
fi
# Project with the identical rank/pool layout before any wavefunction trimming.
if ! cat > "${job}.projwfc.in" <<PWF
&PROJWFC
  prefix = '${prefix}'
  outdir = '${scratch}'
  lsym = .true.
/
PWF
then
  echo "PROJECTION INPUT FAILED: preserving $scratch"; exit 11
fi
mpirun --oversubscribe -np "$NP" projwfc.x -nk "$nk" -in "${job}.projwfc.in" > "$pout" 2>&1 </dev/null
prc=$?
pdone=$(grep -ac 'JOB DONE' "$pout" || true)
nlow=$(grep -ac 'Lowdin Charges' "$pout" || true)
pfailed=$(grep -acE "$fail_pattern" "$pout" || true)
echo "   projwfc rc=$prc job_done=$pdone lowdin_blocks=$nlow failures=$pfailed -> $(basename "$pout")"
if [ "$prc" -ne 0 ] || [ "${pdone:-0}" -ne 1 ] || [ "${nlow:-0}" -lt 1 ] || [ "${pfailed:-1}" -ne 0 ]; then
  echo "PROJWFC FAILED: preserving complete wavefunctions in $scratch; SCF is not a complete numerical result"
  exit 12
fi
# A Lowdin header alone is insufficient: require every atom charge and spin.
if ! "$PYTHON" "$QC" --input "${job}.run.in" --output "$out" --projection "$pout" --json "${job}.qc.json"; then
  echo "COMPLETE OUTPUT QC FAILED: preserving wavefunctions in $scratch"; exit 17
fi
# Keep the full new checkpoint, including every wavefunction, on all outcomes.
for required in data-file-schema.xml charge-density.hdf5 occup.txt paw.txt; do
  [ -s "$scratch/$prefix.save/$required" ] || {
    echo "RETENTION QC FAILED: missing/empty $required; all scratch preserved"; exit 13
  }
done
for spin in up dw; do
  for k in 1 2 3 4 5 6 7 8; do
    [ -s "$scratch/$prefix.save/wfc${spin}${k}.hdf5" ] || {
      echo "RETENTION QC FAILED: missing spin/k-point wavefunction; all scratch preserved"; exit 14
    }
  done
done
echo "NUMERICAL COMPLETE: converged SCF, required file startup, complete projection/Lowdin; all scratch retained"
seff "${SLURM_JOB_ID:-unknown}" 2>/dev/null || true
exit 0
