#!/bin/bash
# Amendment 21 (2026-11-17): one film-pilot pw.x run on Anvil, in its own directory under
# $PROJECT/film/runs/NAME (staged by anvil_stage.sh: NAME.in + tmp/NAME.save/). Same launch recipe as
# the earlier Anvil campaigns (queue_r1.sh): conda-forge QE 7.5 env, OMP 1, mpirun --bind-to none.
# -nk 3 as on the AWS box; 48 ranks = 16 per pool. `shared` bills 48 SU/h; the 8 h limit caps a job
# at 384 SU. Node a171 is excluded (it hung a job in September).
#   sbatch -J NAME --export=ALL,N=NAME anvil_film.slurm
#SBATCH -A che260157
#SBATCH -p shared
#SBATCH -N 1
#SBATCH -n 48
#SBATCH -t 08:00:00
#SBATCH -x a171
#SBATCH -o /anvil/projects/x-che260157/film/logs/%x_%j.out
set -u
N=${N:?}
E=/anvil/projects/x-che260157/qe/env
export PATH=$E/bin:$PATH LD_LIBRARY_PATH=$E/lib:${LD_LIBRARY_PATH:-} OMP_NUM_THREADS=1
cd /anvil/projects/x-che260157/film/runs/$N || exit 2
grep -q $'\r' "$N.in" && { echo "CRLF in $N.in"; exit 3; }
echo "BEGIN $N np=$SLURM_NTASKS node=$(hostname) $(date -u +%FT%TZ)"
mpirun --bind-to none --oversubscribe -np "$SLURM_NTASKS" pw.x -nk 3 -in "$N.in" > "$N.out" 2>&1 < /dev/null
rc=$?
echo "DONE $N rc=$rc JOB_DONE=$(grep -c 'JOB DONE' "$N.out") SCF_FAIL=$(grep -c 'convergence NOT achieved' "$N.out") steps=$(grep -c '^!' "$N.out") $(date -u +%FT%TZ)"
seff "$SLURM_JOB_ID" 2>/dev/null | grep -E "CPU Efficiency|Wall-clock|Memory Utilized" || true
