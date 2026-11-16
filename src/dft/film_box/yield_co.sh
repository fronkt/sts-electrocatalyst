#!/usr/bin/env bash
# Amendment 9: V1 before V2. Stop the CoOOH slab (started 00:47Z, first SCF unfinished) so
# u0__NiFeOOH__Fe0_OH_r3 has its 24 cores; move its dir aside so post_relax.sh relaunches it from
# co_queue.txt when cores free; watch r3 for its C1-C3 single points.
set -u
W=$HOME/film; cd "$W" || exit 1
n=u0__CoOOH__slab
pid=$(pgrep -f "prterun .*-in $n.in" | head -1)
[ -n "$pid" ] || { echo "no prterun for $n"; exit 1; }
kill "$pid"
for i in $(seq 1 60); do pgrep -f "run_side.sh $n " > /dev/null || break; sleep 2; done
pgrep -f "run_side.sh $n " > /dev/null && { echo "run_side for $n still alive"; exit 1; }
mkdir -p runs_stopped && mv "runs/$n" "runs_stopped/${n}__stopped_0103Z"
grep -qx u0__NiFeOOH__Fe0_OH_r3 cfg_watch.txt || echo u0__NiFeOOH__Fe0_OH_r3 >> cfg_watch.txt
echo "STOPPED $n (first SCF unfinished) to give u0__NiFeOOH__Fe0_OH_r3 its cores (V1 before V2); dir moved to runs_stopped/, relaunches from co_queue.txt; r3 added to cfg_watch.txt $(date -u +%FT%TZ)" >> queue.log
tail -3 queue.log; cat cfg_watch.txt; echo "pw=$(pgrep -x pw.x | wc -l)"; ls runs | grep -c CoOOH
