#!/bin/bash
# A6.5(2)(i) repair runner -- 46_a0.slurm plus EXACTLY ONE new step: before
# pw.x runs, the scratch is seeded with the converged neighbouring-U point's
# retained density (dens/<parent>.save, density-only -- 46 trimmed the
# wavefunctions after projwfc), renamed to the child's prefix so the child's
# `startingpot = 'file'` reads it. That is escalation rung (i) of the ladder
# A6.5(2) registered for non-convergent A0 points:
#
#   "restart from the converged neighbouring-U density as `startingpot`;
#    (ii) halve the mixing beta; (iii) failing both, the point is recorded
#    NOT_CONVERGED and plotted as a gap".
#
# WHY NOT 44_chain.slurm: the S3 chain runner replays the parent (wasteful --
# the parent's density is already retained here) and, decisively, runs NO
# projwfc, which would strip the repaired point of its Loewdin populations and
# reproduce exactly the LIT-1 failure A6.5(1) exists to prevent. This runner
# keeps 46's inline projwfc and density-trim behaviour byte-for-byte.
#
# Manifest row: dir job suffix nk parent_density_prefix   (five fields; the
# parent save must exist at $RUNS/<dir>/dens/<parent>.save).
#SBATCH -p shared
#SBATCH -N 1
#SBATCH -n 128
#SBATCH -t 48:00:00
#SBATCH -J a0-repair
#SBATCH -o logs/a0rep_%A_%a.out
#SBATCH -e logs/a0rep_%A_%a.out

set -uo pipefail

: "${MANIFEST:?MANIFEST must be exported by the submitter}"
: "${RUNS:?RUNS must be exported by the submitter}"
: "${QE_PREFIX:?QE_PREFIX must be exported by the submitter}"
: "${PSEUDO_DIR:?PSEUDO_DIR must be exported by the submitter}"
NP=${NP:-128}

LINES="${MANIFEST}.lines"
row=$(sed -n "${SLURM_ARRAY_TASK_ID}p" "$LINES")
[ -n "$row" ] || { echo "FATAL: no row ${SLURM_ARRAY_TASK_ID} in $LINES"; exit 1; }
read -r d job suf nk parent extra <<< "$row"
[ -n "${parent:-}" ] || { echo "FATAL: malformed row '$row' (need 5 fields)"; exit 1; }
[ -z "${extra:-}" ] || { echo "FATAL: trailing fields in row '$row'"; exit 1; }
case "$nk" in ''|*[!0-9]*) echo "FATAL: nk '$nk' not a number"; exit 1;; esac
[ $((NP % nk)) -eq 0 ] || { echo "FATAL: NP=$NP not an exact multiple of nk=$nk"; exit 1; }

dir="$RUNS/$d"
inp="$dir/${job}${suf}"
[ -f "$inp" ] || { echo "FATAL: missing $inp"; exit 1; }
out="$dir/${job}.out"
if [ -f "$out" ] && grep -aq "JOB DONE" "$out"; then
  echo "REFUSE: $out already exists and carries JOB DONE -- not overwriting"; exit 2
fi

cd "$dir" || exit 1
scratch="./tmp_${job}"
rm -rf "$scratch"; mkdir -p "$scratch"

sed -e "s#outdir *= *'[^']*'#outdir = '${scratch}'#" \
    -e "s#pseudo_dir *= *'[^']*'#pseudo_dir = '${PSEUDO_DIR}'#" \
    "${job}${suf}" | sed 's/\r$//' > "${job}.run.in"

grep -q "startingpot = 'file'" "${job}.run.in" || {
  echo "FATAL: ${job}${suf} carries no startingpot = 'file' -- this runner is"
  echo "       only for A6.5(2)(i) repair decks"; exit 1; }
prefix=$(sed -n "s/^[[:space:]]*prefix[[:space:]]*=[[:space:]]*'\([^']*\)'.*/\1/p" "${job}.run.in" | head -1)
[ -n "${prefix:-}" ] || { echo "FATAL: no prefix in ${job}.run.in"; exit 1; }

# --- THE ONE NEW STEP: seed the child's save with the parent's density -------
psave="./dens/${parent}.save"
[ -d "$psave" ] || { echo "FATAL: parent density $d/dens/${parent}.save missing"; exit 1; }
[ -f "$psave/charge-density.dat" ] || [ -f "$psave/charge-density.hdf5" ] || {
  echo "FATAL: $psave carries no charge density"; exit 1; }
cp -r "$psave" "$scratch/${prefix}.save"
echo "SEED: $d/dens/${parent}.save -> tmp/${prefix}.save (startingpot='file')"

export PATH="$QE_PREFIX/bin:$PATH"
export LD_LIBRARY_PATH="$QE_PREFIX/lib:${LD_LIBRARY_PATH:-}"
export OMP_NUM_THREADS=1
export ESPRESSO_PSEUDO="$PSEUDO_DIR"

echo "TASK ${SLURM_ARRAY_TASK_ID} $d/$job np=$NP nk=$nk parent=$parent node=$(hostname) cpus=${SLURM_CPUS_ON_NODE:-?} $(date -u)"
t0=$(date +%s)
mpirun --oversubscribe -np "$NP" pw.x -nk "$nk" -in "${job}.run.in" \
       > "$out" 2>&1 </dev/null
rc=$?
t1=$(date +%s)

conv=$(grep -ac "bfgs converged" "$out" || true)
scffail=$(grep -ac "convergence NOT achieved" "$out" || true)
done_=$(grep -ac "JOB DONE" "$out" || true)
final=$(grep -a "^!" "$out" | tail -1)
echo "TASK ${SLURM_ARRAY_TASK_ID} $d/$job rc=$rc wall=$((t1-t0))s bfgs_conv=$conv scf_fail=$scffail job_done=$done_ $(date -u)"
echo "   final: ${final:-NA}"

# --- A6.5(1): project WHILE the wavefunctions still exist ---------------------
# Only on a converged point: projecting a non-convergent state would produce a
# population table for a state the campaign does not bank.
pout="$dir/${job}.projwfc.out"
if [ "${scffail:-1}" -eq 0 ] && [ "${done_:-0}" -ge 1 ] && [ -n "${prefix:-}" ]; then
  cat > "${job}.projwfc.in" <<PWF
&PROJWFC
  prefix = '${prefix}'
  outdir = '${scratch}'
  lsym = .true.
/
PWF
  # Same rank count and pool layout as the SCF: projwfc.x must read the same
  # distributed wavefunctions pw.x wrote.
  mpirun --oversubscribe -np "$NP" projwfc.x -nk "$nk" -in "${job}.projwfc.in" \
         > "$pout" 2>&1 </dev/null
  prc=$?
  pdone=$(grep -ac "JOB DONE" "$pout" || true)
  nlow=$(grep -ac "Lowdin Charges" "$pout" || true)
  echo "   projwfc rc=$prc job_done=$pdone lowdin_blocks=$nlow -> $(basename "$pout")"
  if [ "$prc" -ne 0 ] || [ "${pdone:-0}" -lt 1 ]; then
    echo "   PROJWFC FAILED -- A6.5(1) requires a charge readout for every A0 point;"
    echo "   this point has moments only until it is repaired."
  fi
else
  echo "   no projwfc (scf_fail=${scffail:-?} job_done=${done_:-?}) -- A6.5(1) applies to converged points"
fi

# --- density retention, identical to 42_s3_wave1.slurm ------------------------
if [ "${scffail:-1}" -eq 0 ] && [ "${done_:-0}" -ge 1 ] && [ -n "${prefix:-}" ] && [ -d "$scratch/${prefix}.save" ]; then
  mkdir -p ./dens
  rm -rf "./dens/${prefix}.save.new"
  if mkdir -p "./dens/${prefix}.save.new" && \
     find "$scratch/${prefix}.save" -maxdepth 1 -type f ! -name 'wfc*' \
          -exec cp -p {} "./dens/${prefix}.save.new/" \; && \
     [ -f "./dens/${prefix}.save.new/data-file-schema.xml" ]; then
    rm -rf "./dens/${prefix}.save"
    mv "./dens/${prefix}.save.new" "./dens/${prefix}.save"
    echo "   retained density: $d/dens/${prefix}.save ($(du -sh "./dens/${prefix}.save" | cut -f1), wavefunctions dropped AFTER projwfc)"
  else
    rm -rf "./dens/${prefix}.save.new"
    echo "   density retention FAILED for ${prefix} (any previous copy left intact)"
  fi
else
  echo "   no density retained (scf_fail=${scffail:-?} job_done=${done_:-?} prefix=${prefix:-NA})"
fi
rm -rf "$scratch"
seff "${SLURM_JOB_ID}" 2>/dev/null || true
exit $rc
