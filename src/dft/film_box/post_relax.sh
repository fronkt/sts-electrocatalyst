#!/usr/bin/env bash
# Amendment 9 launcher (replaces the side_queue_b.txt queue; the only launcher while it runs).
# Every 2 min:
#   - each relaxation listed in cfg_watch.txt that has converged gets its C1-C3 single points
#     (make_cfg_sp.sh), appended to cfg_queue.txt; one that ended without converging is skipped
#     (marker files CFG_QUEUED / CFG_SKIPPED in its run dir);
#   - when 24 cores are free, the next unlaunched run starts: cfg_queue.txt first (V1), then
#     co_queue.txt (CoOOH, V2). A run counts as launched once runs/NAME exists.
# Never starts a run at or after the DEADLINE. Exits when nothing is left to watch or launch.
#   setsid nohup bash post_relax.sh > /dev/null 2>&1 < /dev/null &
set -u
W=$HOME/film
cd "$W" || exit 1
np=24 maxcores=192
log() { echo "$* $(date -u +%FT%TZ)" >> "$W/queue.log"; }
touch cfg_queue.txt co_queue.txt cfg_watch.txt
next() {  # first unlaunched name in the given queue files
  for q in "$@"; do
    while read -r n; do
      [ -n "$n" ] && [ ! -d "runs/$n" ] && { echo "$n"; return; }
    done < "$q"
  done
}
log "POST_RELAX started (watch: $(tr '\n' ' ' < cfg_watch.txt); CoOOH: $(tr '\n' ' ' < co_queue.txt))"
while true; do
  dl=$(cat DEADLINE 2>/dev/null || echo 0)
  if [ -f DEADLINE_HIT ] || { [ "$dl" -gt 0 ] && [ "$(date +%s)" -ge "$dl" ]; }; then
    log "POST_RELAX stopped at the deadline; not launched: $(next cfg_queue.txt) $(next co_queue.txt)"; exit 0
  fi
  watching=0
  while read -r r; do
    [ -z "$r" ] && continue
    d=runs/$r
    [ -f "$d/CFG_QUEUED" ] || [ -f "$d/CFG_SKIPPED" ] && continue
    if grep -q "bfgs converged" "$d/$r.out" 2>/dev/null; then
      if bash make_cfg_sp.sh "$r" >> post_relax.log 2>&1; then
        printf '%s\n' "C1__$r" "C2__$r" "C3__$r" >> cfg_queue.txt; touch "$d/CFG_QUEUED"
        log "CFG_SP queued C1__$r C2__$r C3__$r"
      else
        touch "$d/CFG_SKIPPED"; log "CFG_SP input failed for $r (see post_relax.log)"
      fi
    elif grep -q "^DONE $r " queue.log; then
      touch "$d/CFG_SKIPPED"; log "CFG_SP skipped for $r: finished without a converged relaxation"
    else
      watching=1
    fi
  done < cfg_watch.txt
  n=$(next cfg_queue.txt co_queue.txt)
  if [ -n "$n" ]; then
    if [ $(( $(pgrep -x pw.x | wc -l) + np )) -le "$maxcores" ]; then
      setsid nohup bash "$W/run_side.sh" "$n" "$np" 3 > /dev/null 2>&1 < /dev/null &
      sleep 90  # let the ranks appear before the next core count
      continue
    fi
  elif [ "$watching" -eq 0 ]; then
    log "POST_RELAX done: nothing left to watch or launch"; exit 0
  fi
  sleep 120
done
