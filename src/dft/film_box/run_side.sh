#!/usr/bin/env bash
# Run one relax outside the queue (amendment 6): same mpirun line and queue.log BEGIN/DONE records
# as box_run3.sh's run_one, no U-ramp stage. The queue schedules by live pw.x ranks, so it leaves
# these cores alone, and its final "no pw.x left" wait covers this job too.
#   setsid nohup bash run_side.sh NAME [NP] [NK] > /dev/null 2>&1 < /dev/null &
set -u
n=$1 np=${2:-24} nk=${3:-3}
W=$HOME/film
d=$W/runs/$n
export PATH=$W/qe/env/bin:$PATH LD_LIBRARY_PATH=$W/qe/env/lib:${LD_LIBRARY_PATH:-} OMP_NUM_THREADS=1
log() { echo "$* $(date -u +%FT%TZ)" >> "$W/queue.log"; }
[ -f "$W/inputs/$n.in" ] || { log "SIDE_MISSING_INPUT $n"; exit 1; }
mkdir -p "$d" && cd "$d" || exit 2
cp -f "$W/inputs/$n.in" "$n.in"
# a rerun staged by post_relax.sh (amendment 9): its starting density becomes tmp/NAME.save
if [ -d "$W/stage/$n" ]; then
  mkdir -p tmp && rm -rf "tmp/$n.save" && mv "$W/stage/$n" "tmp/$n.save" || { log "SIDE_STAGE_FAIL $n"; exit 3; }
fi
t0=$(date +%s)
log "BEGIN $n np=$np nk=$nk (side run)"
mpirun --bind-to none -np "$np" pw.x -nk "$nk" -in "$n.in" > "$n.out" 2>&1 < /dev/null
rc=$?
log "DONE $n rc=$rc JOB_DONE=$(grep -c 'JOB DONE' "$n.out") SCF_FAIL=$(grep -c 'convergence NOT achieved' "$n.out") BFGS_END=$(grep -c 'End of BFGS' "$n.out") steps=$(grep -c '^!' "$n.out") $(( $(date +%s) - t0 ))s"
rm -rf "$d/tmp"
