#!/usr/bin/env bash
# Second-stage queue that takes over from box_run.sh mid-run (amendment 3).
# Schedules by free cores (counts live pw.x ranks), so jobs left running by the first queue and
# side reruns are respected. Job list: $JOBS_FILE (default $W/jobs2.txt) (one name per line, inputs in $W/inputs/).
# At the end it waits until NO pw.x is left anywhere, then packages, touches RUN_DONE, waits up
# to 3 h for PULLED, and shuts down (instance STOPS).
set -u
W=$HOME/film
RUNS=$W/runs
NP=${NP:-30}
NK=${NK:-3}
MAXCORES=${MAXCORES:-192}
JOBS=${JOBS_FILE:-$W/jobs2.txt}
export PATH=$W/qe/env/bin:$PATH
export LD_LIBRARY_PATH=$W/qe/env/lib:${LD_LIBRARY_PATH:-}
export OMP_NUM_THREADS=1
LOG=$W/queue.log
log() { echo "$* $(date -u +%FT%TZ)" >> "$LOG"; }

run_one() {
  local n=$1 np=$2 nk=$3 d=$RUNS/$1
  mkdir -p "$d"
  cd "$d" || return 2
  if grep -q "JOB DONE" "$n.out" 2>/dev/null && ! grep -q "convergence NOT achieved" "$n.out"; then
    log "SKIP $n"; return 0
  fi
  cp -f "$W/inputs/$n.in" "$d/$n.in"
  local t0; t0=$(date +%s)
  log "BEGIN $n np=$np nk=$nk (queue2)"
  mpirun --bind-to none -np "$np" pw.x -nk "$nk" -in "$n.in" > "$n.out" 2>&1 < /dev/null
  local rc=$?
  log "DONE $n rc=$rc JOB_DONE=$(grep -c 'JOB DONE' "$n.out") SCF_FAIL=$(grep -c 'convergence NOT achieved' "$n.out") BFGS_END=$(grep -c 'End of BFGS' "$n.out") steps=$(grep -c '^!' "$n.out") $(( $(date +%s) - t0 ))s"
  rm -rf "$d/tmp"
}

log "QUEUE2_START NP=$NP MAXCORES=$MAXCORES jobs=$(grep -c . "$JOBS")"
PIDS=""
while read -r name; do
  [ -z "$name" ] && continue
  while [ $(( $(pgrep -x pw.x | wc -l) + NP )) -gt "$MAXCORES" ]; do sleep 60; done
  run_one "$name" "$NP" "$NK" < /dev/null &
  PIDS="$PIDS $!"
  sleep 30            # let the ranks appear before the next core count
done < "$JOBS"
# shellcheck disable=SC2086
wait $PIDS
while pgrep -x pw.x > /dev/null; do sleep 60; done
log "QUEUE_ALL_DONE (queue2; no pw.x left)"
cd "$W" && tar czf out.tgz --exclude='*/tmp' runs queue.log start.log watchdog.log inputs attempt1 2>/dev/null
md5sum out.tgz > out.tgz.md5
touch "$W/RUN_DONE"
log "RUN_DONE"
for _ in $(seq 1 180); do [ -f "$W/PULLED" ] && break; sleep 60; done
log "SHUTDOWN pulled=$([ -f "$W/PULLED" ] && echo yes || echo no)"
sudo shutdown -h now
