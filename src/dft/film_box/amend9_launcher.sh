#!/usr/bin/env bash
# Amendment 9, run once on the box: replace the side_queue_b.txt queue (still waiting to start
# u0__CoOOH__slab) with post_relax.sh, which puts the configuration single points of the Ni(Fe)OOH
# relaxations ahead of the CoOOH runs.
set -u
W=$HOME/film
cd "$W" || exit 1
log() { echo "$* $(date -u +%FT%TZ)" >> "$W/queue.log"; }
for p in $(pgrep -f "side_queue.sh side_queue[_.]"); do
  echo "stopping queue $p: $(tr '\0' ' ' < /proc/$p/cmdline)"; kill "$p"
done
sleep 2
pgrep -f "side_queue.sh side_queue[_.]" && { echo "a queue is still running; not starting post_relax"; exit 1; }
printf '%s\n' u0__NiFeOOH__slab u0__NiFeOOH__Fe0_O u0__NiFeOOH__Fe0_OH u0__NiFeOOH__Fe0_OOH > cfg_watch.txt
printf '%s\n' u0__CoOOH__slab u0__CoOOH__Co0_O u0__CoOOH__Co0_OH u0__CoOOH__Co0_OOH > co_queue.txt
for n in $(cat co_queue.txt); do [ -f "inputs/$n.in" ] || { echo "missing inputs/$n.in"; exit 1; }; done
log "STOPPED side_queue_b.txt queue (amendment 9); post_relax.sh takes over: C1-C3 single points first, then CoOOH"
setsid nohup bash "$W/post_relax.sh" > /dev/null 2>&1 < /dev/null &
sleep 5
pgrep -f "post_relax[.]sh" > /dev/null && echo "post_relax running" || echo "POST_RELAX NOT RUNNING"
for p in deadline.sh box_watchdog.sh; do pgrep -f "$p" > /dev/null && echo "$p alive" || echo "$p DEAD"; done
echo "pw.x ranks: $(pgrep -x pw.x | wc -l)"
tail -3 queue.log
