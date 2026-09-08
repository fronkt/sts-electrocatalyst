#!/bin/bash
# Paired spin/projector follow-up, exact frozen specification checked at execution.
# Four-hour allocation. Failures preserve scratch; originals remain unchanged.
#SBATCH -p shared
#SBATCH -N 1
#SBATCH -n 128
#SBATCH -t 04:00:00
#SBATCH -J hea-followup
#SBATCH -o logs/hea_followup_%A_%a.out
#SBATCH -e logs/hea_followup_%A_%a.out

set -uo pipefail
: "${PROJECT:?PROJECT must be exported}"
set -C  # noclobber: never replace a racing or preexisting output
export LC_ALL=C
: "${MANIFEST:?MANIFEST must be exported by the submitter}"
: "${RUNS:?RUNS must be exported by the submitter}"
: "${QE_PREFIX:?QE_PREFIX must be exported by the submitter}"
: "${PSEUDO_DIR:?PSEUDO_DIR must be exported by the submitter}"
NP=${NP:-128}
[ "$NP" = 128 ] || { echo "REFUSE: follow-up requires NP=128"; exit 2; }
# Slurm copies the script; resolve helpers from the staged project.
ROOT="$PROJECT/sts"
PYTHON="/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3"
SPEC="$ROOT/results/hea_followup_2026-09-07/launch_spec.json"
GUARD="$ROOT/src/dft/hea_followup_guard.py"
QC="$ROOT/src/dft/hea_followup_qc.py"
FORCE_AUDIT="$ROOT/src/dft/hea_force_audit.py"
check_hash() { [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ] || { echo "REFUSE: pinned file differs: $1" >&2; exit 2; }; }
check_hash "$SPEC" 6cd1454eab4ccf2186eca472d1d23a8c0ab69fdd325dafc3324c3bc7f0f9c2e7
check_hash "$GUARD" 0a98be0da473ef05caebab3a2c8a8c5bb1aef92bd88e3c33cc76f0bb167550b7
check_hash "$QC" ef9b50193f46034036b892263a3ee139426d912b2098ebdc5a897a82dc2769da
check_hash "$FORCE_AUDIT" bddbe7ba3bed9874e723d88f8bdab724bb4e83178f1f75bbc3a1f4034b9fd5d7
[ "$MANIFEST" = "$ROOT/runs/hea/m_controls_2026-09-07_followup_approved.txt" ] || { echo "REFUSE: unexpected manifest path"; exit 2; }
[ "$RUNS" = "$ROOT/runs" ] || { echo "REFUSE: unexpected runs path"; exit 2; }
row=$("$PYTHON" "$GUARD" --spec "$SPEC" --runs "$RUNS" --row "${SLURM_ARRAY_TASK_ID:-}") || exit 2
read -r d job suf nk extra <<< "$row"

dir="$RUNS/$d"
[ -d "$dir" ] && [ -f "$dir/${job}${suf}" ] || { echo "REFUSE: missing follow-up directory/input"; exit 2; }
cd "$dir" || exit 2
inp="${job}${suf}"
out="$dir/${job}.out"
pout="$dir/${job}.projwfc.out"
scratch="./tmp_${job}"
prefix=$(sed -n "s#^[[:space:]]*prefix[[:space:]]*=[[:space:]]*'\([^']*\)'.*#\1#p" "$inp")
[ "$prefix" = "$job" ] || { echo "REFUSE: input prefix differs from approved job"; exit 2; }
for path in "$out" "$pout" "${job}.run.in" "${job}.projwfc.in" "${job}.scf_qc.json" "${job}.qc.json" "$scratch" "./dens/${prefix}.save" "./dens/${prefix}.save.new"; do
  if [ -e "$path" ] || [ -L "$path" ]; then
    echo "REFUSE: preexisting follow-up artifact $path; nothing removed"; exit 2
  fi
done
# Atomic mkdir is the ownership boundary: never remove another attempt's scratch.
mkdir "$scratch" || { echo "REFUSE: could not claim fresh scratch $scratch"; exit 2; }
trap 'echo "INTERRUPTED: preserving follow-up scratch $scratch"; exit 143' TERM HUP
trap 'echo "INTERRUPTED: preserving follow-up scratch $scratch"; exit 130' INT
if ! sed -e "s#outdir *= *'[^']*'#outdir = '${scratch}'#" \
         -e "s#^[[:space:]]*max_seconds[[:space:]]*=.*#  max_seconds = 13200#" \
         -e "s#pseudo_dir *= *'[^']*'#pseudo_dir = '${PSEUDO_DIR}'#" "$inp" \
         | sed 's/\r$//' > "${job}.run.in"; then
  echo "FAILED: runtime input preparation; preserving $scratch"; exit 3
fi
export PATH="$QE_PREFIX/bin:$PATH"
export LD_LIBRARY_PATH="$QE_PREFIX/lib:${LD_LIBRARY_PATH:-}"
export OMP_NUM_THREADS=1
export ESPRESSO_PSEUDO="$PSEUDO_DIR"
echo "TASK ${SLURM_ARRAY_TASK_ID} $d/$job np=$NP nk=$nk node=$(hostname) cpus=${SLURM_CPUS_ON_NODE:-?} $(date -u)"
echo "FOLLOWUP: four-hour allocation; QE max_seconds=13200 reserves nominal 20min for exit/projection; no automatic retries"
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
  echo "PROJWFC FAILED: preserving complete wavefunctions in $scratch; SCF is not a complete follow-up result"
  exit 12
fi
# A Lowdin header alone is insufficient: require every atom charge and spin.
if ! "$PYTHON" "$QC" --input "${job}.run.in" --output "$out" --projection "$pout" --json "${job}.qc.json"; then
  echo "COMPLETE OUTPUT QC FAILED: preserving wavefunctions in $scratch"; exit 17
fi
# Same density-only retention as 46, only after successful projection. No replacement.
if [ ! -d "$scratch/${prefix}.save" ]; then
  echo "RETENTION FAILED: missing save directory; preserving $scratch"; exit 13
fi
if mkdir -p ./dens && mkdir "./dens/${prefix}.save.new" && \
   find "$scratch/${prefix}.save" -maxdepth 1 -type f ! -name 'wfc*' \
     -exec cp -p -t "./dens/${prefix}.save.new" -- {} + && \
   [ -s "./dens/${prefix}.save.new/data-file-schema.xml" ] && \
   { [ -s "./dens/${prefix}.save.new/charge-density.dat" ] || \
     [ -s "./dens/${prefix}.save.new/charge-density.hdf5" ]; } && \
   mv -T "./dens/${prefix}.save.new" "./dens/${prefix}.save"; then
  echo "   retained density: $d/dens/${prefix}.save ($(du -sh "./dens/${prefix}.save" | cut -f1), wavefunctions dropped after successful projwfc)"
else
  echo "RETENTION FAILED: preserving complete scratch $scratch and any partial density copy"; exit 14
fi
# The fixed approved scratch basename was exclusively created above.
rm -rf -- "$scratch" || { echo "CLEANUP FAILED: inspect remaining $scratch"; exit 15; }
echo "FOLLOWUP COMPLETE: converged SCF, complete projection/Lowdin and retained density"
seff "${SLURM_JOB_ID:-unknown}" 2>/dev/null || true
exit 0
