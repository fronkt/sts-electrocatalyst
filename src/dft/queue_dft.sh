#!/usr/bin/env bash
# Throttled DFT queue for the 5 rutile MO2 endmembers.
# Replaces the 240-rank parallel-5 layout that thrashed memory bandwidth
# (only ~30/256 cores doing useful work, ~8.75 min/SCF-iter).
# 20 jobs = 5 endmembers x {s0_O, s0_OH, s0_OOH, slab}; NP ranks each,
# at most NCONC concurrent. Gas refs (H2/H2O) already done -> not touched.
set -u
NP=${1:-24}
NCONC=${2:-4}
RUNS=/workspace/STS2027/runs
export PATH=/workspace/qe/env/bin:${PATH:-}
export LD_LIBRARY_PATH=/workspace/qe/env/lib:${LD_LIBRARY_PATH:-}
export OMP_NUM_THREADS=1
LOG=/workspace/queue_dft.log
echo "QUEUE_START $(date -u) NP=$NP NCONC=$NCONC" >> "$LOG"

run_one() {
  local M=$1 job=$2 nk=$3
  local d=$RUNS/${M}_slab
  cd "$d" || { echo "NODIR $M" >> "$LOG"; return 2; }
  # Idempotent: relaunches skip anything already converged
  if grep -q "JOB DONE" "${job}.out" 2>/dev/null; then
    echo "SKIP $M/$job already-done $(date -u)" >> "$LOG"; return 0
  fi
  rm -rf ./tmp 2>/dev/null
  local t0; t0=$(date +%s)
  # </dev/null is load-bearing: backgrounded mpirun otherwise drains the
  # here-string job list via OpenMPI stdin-forwarding -> queue exits early
  mpirun --allow-run-as-root --bind-to none -np "$NP" pw.x -nk "$nk" -in "${job}.in" > "${job}.out" 2>&1 < /dev/null
  local rc=$?
  local jd; jd=$(grep -c 'JOB DONE' "${job}.out")
  echo "DONE $M/$job rc=$rc JOB_DONE=$jd $(( $(date +%s)-t0 ))s $(date -u)" >> "$LOG"
  rm -rf ./tmp 2>/dev/null   # free scratch immediately — small-disk (16 GB) boxes
}

# Build job list (adslabs nk=4, clean slab nk=6)
JOBS=$(for M in Mn Fe Co Ni Cu; do
  for j in s0_O s0_OH s0_OOH; do echo "$M $j 4"; done
  echo "$M slab 6"
done)

# Throttle to NCONC concurrent background jobs
while read -r M j nk; do
  [ -z "$M" ] && continue
  while [ "$(jobs -rp | wc -l)" -ge "$NCONC" ]; do wait -n; done
  run_one "$M" "$j" "$nk" </dev/null &
done <<< "$JOBS"
wait
echo "QUEUE_ALL_DONE $(date -u)" >> "$LOG"
