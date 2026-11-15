#!/usr/bin/env bash
# Film-DFT pilot queue: every job in its own directory (own ./tmp), NCONC jobs at once,
# NP MPI ranks each, no core binding (concurrent mpiruns would otherwise share cores).
# Ends by packaging out.tgz, touching RUN_DONE, waiting up to 3 h for the local pull
# to touch PULLED, then shutting down (the instance is set to STOP, so the disk survives).
set -u
W=$HOME/film
RUNS=$W/runs
NP=${NP:-30}
NK=${NK:-3}
NCONC=${NCONC:-6}
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
  log "BEGIN $n np=$np nk=$nk"
  mpirun --bind-to none -np "$np" pw.x -nk "$nk" -in "$n.in" > "$n.out" 2>&1 < /dev/null
  local rc=$?
  log "DONE $n rc=$rc JOB_DONE=$(grep -c 'JOB DONE' "$n.out") SCF_FAIL=$(grep -c 'convergence NOT achieved' "$n.out") BFGS_END=$(grep -c 'End of BFGS' "$n.out") steps=$(grep -c '^!' "$n.out") $(( $(date +%s) - t0 ))s"
  rm -rf "$d/tmp"
}

package() {
  cd "$W" && tar czf out.tgz --exclude='*/tmp' runs queue.log start.log watchdog.log inputs/manifest.json 2>/dev/null
  md5sum out.tgz > out.tgz.md5
}

log "QUEUE_START NP=$NP NK=$NK NCONC=$NCONC"
JOBS=$(python3 - "$W/inputs/manifest.json" <<'PY'
import json, sys
jobs = json.load(open(sys.argv[1]))["jobs"]
for j in sorted(jobs, key=lambda j: (j["kind"] != "gas", j["kind"] != "slab", j["name"])):
    print(j["name"], j["kind"])
PY
)
while read -r name kind; do
  [ -z "$name" ] && continue
  while [ "$(jobs -rp | wc -l)" -ge "$NCONC" ]; do wait -n; done
  if [ "$kind" = gas ]; then
    run_one "$name" 8 1 < /dev/null &
  else
    run_one "$name" "$NP" "$NK" < /dev/null &
  fi
  sleep 2
done <<< "$JOBS"
wait
log "QUEUE_ALL_DONE"
package
touch "$W/RUN_DONE"
log "RUN_DONE"
for _ in $(seq 1 180); do [ -f "$W/PULLED" ] && break; sleep 60; done
log "SHUTDOWN pulled=$([ -f "$W/PULLED" ] && echo yes || echo no)"
sudo shutdown -h now
