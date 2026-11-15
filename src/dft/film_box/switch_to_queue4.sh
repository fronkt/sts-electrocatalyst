#!/usr/bin/env bash
# Amendment 5, run once on the box: jobs whose FIRST SCF has not converged are restarted with a
# U-ramp (U=0 SCF, then the PBE+U relax from that wavefunction/density); the jobs not yet started
# get the ramp too. Jobs with at least one converged energy keep running untouched.
set -u
W=$HOME/film
cd "$W" || exit 1
CAND="NiOOH__Ni0_O NiOOH__Ni0_OH NiOOH__Ni0_OOH NiFeOOH__Fe0_OOH"

# 1. snapshot, then stop the queue shells and the launchers of jobs with no converged SCF yet
Q=$(ps -eo pid,args | awk '$2=="bash" && $3 ~ /box_run[23]?\.sh$/ {print $1}')
L=$(ps -eo pid,comm | awk '$2 ~ /^(prterun|mpirun)$/ {print $1}')
declare -A CWD
for p in $L; do CWD[$p]=$(readlink "/proc/$p/cwd"); done
RESTART=""
for n in $CAND; do
  if grep -q "^!" "runs/$n/$n.out" 2>/dev/null; then
    echo "keep $n (first SCF converged meanwhile)"
  else
    RESTART="$RESTART $n"
  fi
done
# shellcheck disable=SC2086
kill $Q 2>/dev/null; echo "stopped queue shells: $(echo $Q | wc -w)"
for p in $L; do
  b=${CWD[$p]##*/}
  for n in $RESTART; do [ "$b" = "$n" ] && kill "$p" && echo "stopped launcher $p in $n"; done
done
sleep 10
echo "STOPPED first-SCF failures for amendment 5 (U-ramp):$RESTART $(date -u +%FT%TZ)" >> queue.log

# 2. ramp inputs
: > jobs4.txt
for n in $RESTART; do
  python3 make_ramp.py "inputs/$n.in" "${n}_r2" && echo "${n}_r2" >> jobs4.txt
done
for n in NiFeOOH__Ni1_O NiFeOOH__Ni1_OH NiFeOOH__Ni1_OOH CoOOH__Co0_O_r2 CoOOH__Co0_OH_r2 CoOOH__Co0_OOH_r2 CoOOH__slab_r4; do
  if [ -d "runs/$n" ]; then echo "WARNING $n had started; left out"; continue; fi
  python3 make_ramp.py "inputs/$n.in" && echo "$n" >> jobs4.txt
done
for n in $(cat jobs4.txt); do
  for f in "inputs/$n.in" "inputs/${n}_u0.in" "inputs/${n}_nofile.in"; do [ -f "$f" ] || echo "MISSING $f"; done
  grep -q "startingpot = 'file'" "inputs/$n.in" || echo "NO FILE START in $n"
  grep -q "upscale = 1.d0" "inputs/$n.in" || echo "NO UPSCALE in $n"
done
echo "queue4 jobs: $(tr '\n' ' ' < jobs4.txt)"
JOBS_FILE=$W/jobs4.txt NP=24 NK=3 setsid nohup bash "$W/box_run3.sh" > "$W/queue4.log" 2>&1 < /dev/null &
sleep 45
echo "pw.x ranks: $(pgrep -x pw.x | wc -l)"; tail -4 queue.log
