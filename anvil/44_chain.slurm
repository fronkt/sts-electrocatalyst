#!/bin/bash
# A8.3 density-retention chain runner -- ONE array task per row of
# runs/chains/m_chains.txt: replay the parent deck to convergence with scratch
# RETAINED, copy its .save under the child __fp prefix, then run the child SCF
# with startingpot='file'. Launched only by 45_submit_chains.sh (PARITY_PASS +
# pseudo-preflight gates). Same shape rules as 42: direct mpirun, NO --bind-to
# (A8.6 undecided), 128 ranks, -nk from the row.
#SBATCH -p shared
#SBATCH -N 1
#SBATCH -n 128
#SBATCH -t 48:00:00
#SBATCH -J s3-chain
#SBATCH -o logs/chain_%A_%a.out
#SBATCH -e logs/chain_%A_%a.out

set -uo pipefail
: "${MANIFEST:?}" ; : "${RUNS_ROOT:?}" ; : "${QE_PREFIX:?}" ; : "${PSEUDO_DIR:?}"
NP=${NP:-128}

LINES="${MANIFEST}.lines"
row=$(sed -n "${SLURM_ARRAY_TASK_ID}p" "$LINES")
[ -n "$row" ] || { echo "FATAL: no row ${SLURM_ARRAY_TASK_ID}"; exit 1; }
read -r d rdeck rprefix fdeck fprefix nk extra <<< "$row"
[ -z "${extra:-}" ] || { echo "FATAL: trailing fields '$row'"; exit 1; }
case "$nk" in ''|*[!0-9]*) echo "FATAL: bad nk '$nk'"; exit 1;; esac
[ $((NP % nk)) -eq 0 ] || { echo "FATAL: NP%nk"; exit 1; }

dir="$RUNS_ROOT/$d"
cd "$dir" || exit 1
rout="${rdeck%.in}.out"          # replay evidence, never banked (A8.8)
fout="${fdeck%.in}.out"          # the A8.3 second attempt
for o in "$rout" "$fout"; do
  if [ -f "$o" ] && grep -aq "JOB DONE" "$o"; then
    echo "REFUSE: $o already exists with JOB DONE"; exit 2
  fi
done

scratch="./tmp_chain_${fprefix}"
rm -rf "$scratch"; mkdir -p "$scratch"
export PATH="$QE_PREFIX/bin:$PATH"
export LD_LIBRARY_PATH="$QE_PREFIX/lib:${LD_LIBRARY_PATH:-}"
export OMP_NUM_THREADS=1

prep() {  # $1 deck -> $2 run.in : outdir/pseudo_dir rewrite + CRLF strip (42 convention)
  sed -e "s#outdir *= *'[^']*'#outdir = '${scratch}'#" \
      -e "s#pseudo_dir *= *'[^']*'#pseudo_dir = '${PSEUDO_DIR}'#" \
      "$1" | sed 's/\r$//' > "$2"
}

echo "CHAIN ${SLURM_ARRAY_TASK_ID} $d $rprefix -> $fprefix node=$(hostname) $(date -u)"
prep "$rdeck" "${rdeck%.in}.run.in"
mpirun --oversubscribe -np "$NP" pw.x -nk "$nk" -in "${rdeck%.in}.run.in" > "$rout" 2>&1 </dev/null
grep -aq "JOB DONE" "$rout" || { echo "CHAIN FAIL: replay died (scratch kept)"; exit 1; }
grep -aq "convergence NOT achieved" "$rout" && { echo "CHAIN FAIL: replay non-convergent (scratch kept)"; exit 1; }
rE=$(grep -a "^!" "$rout" | tail -1)
echo "   replay final: $rE"

[ -d "$scratch/${rprefix}.save" ] || { echo "CHAIN FAIL: no ${rprefix}.save retained"; exit 1; }
cp -r "$scratch/${rprefix}.save" "$scratch/${fprefix}.save"

prep "$fdeck" "${fdeck%.in}.run.in"
mpirun --oversubscribe -np "$NP" pw.x -nk "$nk" -in "${fdeck%.in}.run.in" > "$fout" 2>&1 </dev/null
grep -aq "JOB DONE" "$fout" || { echo "CHAIN FAIL: child died (scratch kept)"; exit 1; }
fE=$(grep -a "^!" "$fout" | tail -1)
echo "   child-from-density final: $fE"
rm -rf "$scratch"
echo "CHAIN ${SLURM_ARRAY_TASK_ID} DONE $(date -u)"
