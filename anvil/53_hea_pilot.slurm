#!/bin/bash
# Two-job HEA pilot, same np/nk launch and inline projection as 46_a0.slurm.
# Four-hour allocation. Failures preserve scratch; originals remain unchanged.
#SBATCH -p shared
#SBATCH -N 1
#SBATCH -n 128
#SBATCH -t 04:00:00
#SBATCH -J hea-pilot
#SBATCH -o logs/hea_pilot_%A_%a.out
#SBATCH -e logs/hea_pilot_%A_%a.out

set -uo pipefail
set -C  # noclobber: never replace a racing or preexisting output
export LC_ALL=C
: "${MANIFEST:?MANIFEST must be exported by the submitter}"
: "${RUNS:?RUNS must be exported by the submitter}"
: "${QE_PREFIX:?QE_PREFIX must be exported by the submitter}"
: "${PSEUDO_DIR:?PSEUDO_DIR must be exported by the submitter}"
NP=${NP:-128}
[ "$NP" = 128 ] || { echo "REFUSE: pilot requires NP=128"; exit 2; }
case "${SLURM_ARRAY_TASK_ID:-}" in 1|2) ;; *) echo "REFUSE: pilot array task must be 1 or 2"; exit 2;; esac
LINES="${MANIFEST}.lines"
[ -f "$LINES" ] || { echo "REFUSE: missing $LINES"; exit 2; }
[ "$(wc -l < "$LINES")" -eq 2 ] || { echo "REFUSE: pilot requires exactly two runnable rows"; exit 2; }
row=$(sed -n "${SLURM_ARRAY_TASK_ID}p" "$LINES")
read -r d job suf nk extra <<< "$row"
[ -z "${extra:-}" ] && [ "${d:-}" = "hea/controls_2026-09-07" ] && [ "${suf:-}" = .in ] && [ "${nk:-}" = 8 ] || {
  echo "REFUSE: unexpected pilot row '$row' (directory, suffix and nk=8 are fixed)"; exit 2;
}
case "${job:-}" in hc__leader_builder__atomic__baseline|hc__leader_pull2.10__atomic__baseline) ;;
  *) echo "REFUSE: job is outside the two approved pilot endpoints"; exit 2;; esac
[ "$(awk '{print $2}' "$LINES" | sort -u | wc -l)" -eq 2 ] || {
  echo "REFUSE: duplicate pilot job"; exit 2;
}

dir="$RUNS/$d"
[ -d "$dir" ] && [ -f "$dir/${job}${suf}" ] || { echo "REFUSE: missing pilot directory/input"; exit 2; }
cd "$dir" || exit 2
inp="${job}${suf}"
out="$dir/${job}.out"
pout="$dir/${job}.projwfc.out"
scratch="./tmp_${job}"
prefix=$(sed -n "s#^[[:space:]]*prefix[[:space:]]*=[[:space:]]*'\([^']*\)'.*#\1#p" "$inp")
[ "$prefix" = "$job" ] || { echo "REFUSE: input prefix differs from approved job"; exit 2; }
for path in "$out" "$pout" "${job}.run.in" "${job}.projwfc.in" "$scratch" "./dens/${prefix}.save" "./dens/${prefix}.save.new"; do
  if [ -e "$path" ] || [ -L "$path" ]; then
    echo "REFUSE: preexisting pilot artifact $path; nothing removed"; exit 2
  fi
done
# Atomic mkdir is the ownership boundary: never remove another attempt's scratch.
mkdir "$scratch" || { echo "REFUSE: could not claim fresh scratch $scratch"; exit 2; }
trap 'echo "INTERRUPTED: preserving pilot scratch $scratch"; exit 143' TERM HUP
trap 'echo "INTERRUPTED: preserving pilot scratch $scratch"; exit 130' INT
if ! sed -e "s#outdir *= *'[^']*'#outdir = '${scratch}'#" \
         -e "s#pseudo_dir *= *'[^']*'#pseudo_dir = '${PSEUDO_DIR}'#" "$inp" \
         | sed 's/\r$//' > "${job}.run.in"; then
  echo "FAILED: runtime input preparation; preserving $scratch"; exit 3
fi
export PATH="$QE_PREFIX/bin:$PATH"
export LD_LIBRARY_PATH="$QE_PREFIX/lib:${LD_LIBRARY_PATH:-}"
export OMP_NUM_THREADS=1
export ESPRESSO_PSEUDO="$PSEUDO_DIR"
echo "TASK ${SLURM_ARRAY_TASK_ID} $d/$job np=$NP nk=$nk node=$(hostname) cpus=${SLURM_CPUS_ON_NODE:-?} $(date -u)"
echo "PILOT: four-hour allocation includes SCF, projection and retention; no automatic retries"
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
  echo "PROJWFC FAILED: preserving complete wavefunctions in $scratch; SCF is not a complete pilot result"
  exit 12
fi
# Same density-only retention as 46, only after successful projection. No replacement.
if [ ! -d "$scratch/${prefix}.save" ]; then
  echo "RETENTION FAILED: missing save directory; preserving $scratch"; exit 13
fi
if mkdir -p ./dens && mkdir "./dens/${prefix}.save.new" && \
   find "$scratch/${prefix}.save" -maxdepth 1 -type f ! -name 'wfc*' \
     -exec cp -p -t "./dens/${prefix}.save.new" -- {} + && \
   [ -f "./dens/${prefix}.save.new/data-file-schema.xml" ] && \
   mv -T "./dens/${prefix}.save.new" "./dens/${prefix}.save"; then
  echo "   retained density: $d/dens/${prefix}.save ($(du -sh "./dens/${prefix}.save" | cut -f1), wavefunctions dropped after successful projwfc)"
else
  echo "RETENTION FAILED: preserving complete scratch $scratch and any partial density copy"; exit 14
fi
# The fixed approved scratch basename was exclusively created above.
rm -rf -- "$scratch" || { echo "CLEANUP FAILED: inspect remaining $scratch"; exit 15; }
echo "PILOT COMPLETE: converged SCF, complete projection/Lowdin and retained density"
seff "${SLURM_JOB_ID:-unknown}" 2>/dev/null || true
exit 0
