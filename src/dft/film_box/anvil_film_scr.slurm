#!/bin/bash
# anvil_film.slurm with nothing written to the project fileset: the run directory and the slurm log are
# on user scratch. By 2026-11-18 04:54Z the project fileset refused to create new files (ENOSPC
# at 91.7% of its 5 TB quota; C4's log was still created at 04:51:46Z), so C5-C7 failed at launch
# before pw.x started. Reads (the QE env, pseudopotentials) stay on the project fileset. The run
# directory /anvil/scratch/x-fcai3/film/NAME holds NAME.in and the outdir tmp/ that the input already
# names. Same launch recipe otherwise.
#   sbatch -t 04:00:00 -J NAME --export=ALL,N=NAME anvil_film_scr.slurm
#SBATCH -A che260157
#SBATCH -p shared
#SBATCH -N 1
#SBATCH -n 48
#SBATCH -t 08:00:00
#SBATCH -x a171
#SBATCH -o /anvil/scratch/x-fcai3/film/logs/%x_%j.out
set -u
N=${N:?}
E=/anvil/projects/x-che260157/qe/env
export PATH=$E/bin:$PATH LD_LIBRARY_PATH=$E/lib:${LD_LIBRARY_PATH:-} OMP_NUM_THREADS=1
cd /anvil/scratch/x-fcai3/film/$N || exit 2
grep -q $'\r' "$N.in" && { echo "CRLF in $N.in"; exit 3; }
echo "BEGIN $N np=$SLURM_NTASKS node=$(hostname) $(date -u +%FT%TZ)"
mpirun --bind-to none --oversubscribe -np "$SLURM_NTASKS" pw.x -nk 3 -in "$N.in" > "$N.out" 2>&1 < /dev/null
rc=$?
echo "DONE $N rc=$rc JOB_DONE=$(grep -c 'JOB DONE' "$N.out") SCF_FAIL=$(grep -c 'convergence NOT achieved' "$N.out") steps=$(grep -c '^!' "$N.out") $(date -u +%FT%TZ)"
seff "$SLURM_JOB_ID" 2>/dev/null | grep -E "CPU Efficiency|Wall-clock|Memory Utilized" || true
