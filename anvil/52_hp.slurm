#!/bin/bash
# hp.x runner -- ONE job, SCF then linear response, against one shared scratch.
#
# WHY THIS FILE EXISTS. docs/51:22 recorded "No hp.x path exists on Anvil (driver
# is pw.x-only; queue_hp.sh hardcodes Vast paths; array semantics would race one
# shared SCF)". That was read for two weeks as "hp.x cannot run on Anvil", which
# is false: $PROJECT/qe/env/bin/hp.x is present and reports "Program HP v.7.5".
# Only the driver was missing. This is the driver, and it is ~40 lines.
#
# It resolves each of the three obstacles by construction:
#   * pw.x-only driver  -> this runs pw.x and then hp.x, gated on the SCF, the
#     same way 46_a0.slurm runs pw.x and then projwfc.x in one job.
#   * hardcoded Vast paths -> pseudo_dir and outdir are rewritten at run time
#     from $PSEUDO_DIR and the job's own scratch, exactly as 46_a0.slurm:70 does.
#     Nothing machine-specific is baked into a deck.
#   * "array semantics would race one shared SCF" -> there is no array. hp.x
#     reads the wavefunctions pw.x wrote; one job owns one scratch, start to end.
#
# A8.8 ISOLATION. This writes only under $RUNS/$DIR, which for the CrO2 ortho arm
# is runs/hp_cro2_ortho -- never the banked runs/hp_tio2. It also refuses to
# overwrite any .out that already carries JOB DONE.
#
# NAMED RISK, PRE-STATED. nspin = 2 crossed with ortho-atomic has never been run
# in this campaign. If the linear response does not converge, this job returns NO
# NUMBER and that is the reportable outcome -- a methods limit, not a delta-U.
# hp.x writes its .dat even after non-convergence, so the presence of an artifact
# is NOT a pass; the convergence check below is what decides.
#
#   sbatch --export=ALL,RUNS,QE_PREFIX,PSEUDO_DIR,DIR,SCF,HP 52_hp.slurm
#
#SBATCH -p shared
#SBATCH -N 1
#SBATCH -n 20
#SBATCH -t 12:00:00
#SBATCH -J hp
#SBATCH -o logs/hp_%j.out
#SBATCH -e logs/hp_%j.out

set -uo pipefail

: "${RUNS:?RUNS must be exported by the submitter}"
: "${QE_PREFIX:?QE_PREFIX must be exported by the submitter}"
: "${PSEUDO_DIR:?PSEUDO_DIR must be exported by the submitter}"
: "${DIR:?DIR must be exported (path under RUNS)}"
: "${SCF:?SCF must be exported (scf deck filename)}"
: "${HP:?HP must be exported (hp deck filename)}"

NP=${NP:-20}
NK=${NK:-4}
[ $((NP % NK)) -eq 0 ] || { echo "FATAL: NP=$NP not a multiple of NK=$NK"; exit 1; }

dir="$RUNS/$DIR"
[ -d "$dir" ] || { echo "FATAL: missing $dir"; exit 1; }
cd "$dir" || exit 1
[ -f "$SCF" ] || { echo "FATAL: missing $dir/$SCF"; exit 1; }
[ -f "$HP" ]  || { echo "FATAL: missing $dir/$HP"; exit 1; }

scf_out="${SCF%.in}.out"
hp_out="${HP%.in}.out"
for f in "$scf_out" "$hp_out"; do
  if [ -f "$f" ] && grep -aq "JOB DONE" "$f"; then
    echo "REFUSE: $dir/$f already carries JOB DONE -- not overwriting (A8.8)"; exit 2
  fi
done

scratch="./tmp_hp_${SLURM_JOB_ID:-manual}"
rm -rf "$scratch"; mkdir -p "$scratch"

# Both decks must point at the SAME scratch, or hp.x cannot find the SCF.
sed -e "s#outdir *= *'[^']*'#outdir = '${scratch}'#" \
    -e "s#pseudo_dir *= *'[^']*'#pseudo_dir = '${PSEUDO_DIR}'#" \
    "$SCF" | sed 's/\r$//' > "${SCF%.in}.run.in"
sed -e "s#outdir *= *'[^']*'#outdir = '${scratch}'#" \
    "$HP" | sed 's/\r$//' > "${HP%.in}.run.in"

export PATH="$QE_PREFIX/bin:$PATH"
export LD_LIBRARY_PATH="$QE_PREFIX/lib:${LD_LIBRARY_PATH:-}"
export OMP_NUM_THREADS=1
export ESPRESSO_PSEUDO="$PSEUDO_DIR"

echo "HP JOB ${SLURM_JOB_ID:-manual} $DIR np=$NP nk=$NK node=$(hostname) $(date -u)"
echo "  qe: $(command -v pw.x) / $(command -v hp.x)"

t0=$(date +%s)
mpirun --oversubscribe -np "$NP" pw.x -nk "$NK" -in "${SCF%.in}.run.in" \
       > "$scf_out" 2>&1 </dev/null
scf_rc=$?
t1=$(date +%s)
scf_done=$(grep -ac "JOB DONE" "$scf_out" || true)
scf_bad=$(grep -ac "convergence NOT achieved" "$scf_out" || true)
echo "  SCF rc=$scf_rc job_done=$scf_done not_achieved=$scf_bad wall=$((t1-t0))s"

if [ "$scf_rc" -ne 0 ] || [ "${scf_done:-0}" -lt 1 ] || [ "${scf_bad:-0}" -gt 0 ]; then
  echo "  SCF FAILED -- hp.x not attempted. No number is produced; this is the"
  echo "  reportable outcome, not a retry trigger."
  exit 3
fi

t2=$(date +%s)
mpirun --oversubscribe -np "$NP" hp.x -in "${HP%.in}.run.in" \
       > "$hp_out" 2>&1 </dev/null
hp_rc=$?
t3=$(date +%s)
hp_done=$(grep -ac "JOB DONE" "$hp_out" || true)
hp_bad=$(grep -ac "Convergence has not been reached" "$hp_out" || true)
echo "  HP  rc=$hp_rc job_done=$hp_done not_reached=$hp_bad wall=$((t3-t2))s"
echo "  SU (this job) = $(( (t3-t0) * NP / 3600 )) core-h approx"

# Pull the Hubbard parameters out of scratch beside the deck, named for the deck.
for f in "$scratch"/*.Hubbard_parameters.dat "$scratch"/*/*.Hubbard_parameters.dat \
         "$scratch"/*.chi*.dat "$scratch"/*/*.chi*.dat HP/*.dat; do
  [ -e "$f" ] || continue
  cp -p "$f" "./${HP%.in}.$(basename "$f")" 2>/dev/null || true
done
ls -1 "${HP%.in}."*.dat 2>/dev/null | sed 's/^/  artifact: /' || echo "  artifact: NONE"

if [ "${hp_bad:-0}" -gt 0 ]; then
  echo "  HP DID NOT CONVERGE ($hp_bad blocks). Per the pre-stated risk this"
  echo "  returns NO U and is written up as a methods limit. The .dat existing"
  echo "  is NOT a pass."
  exit 4
fi
[ "$hp_rc" -eq 0 ] && [ "${hp_done:-0}" -ge 1 ] || exit 5

grep -aA6 "Hubbard U parameters" "$hp_out" | tail -5
echo "HP JOB COMPLETE $(date -u)"
