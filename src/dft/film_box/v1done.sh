#!/usr/bin/env bash
# 2026-11-16 ~20:25Z, with the cap extended to 2026-11-17T06:00Z: bring the deadline forward when V1's
# last run finishes (the 13:10Z / 20:20Z spend notes), so the box does not idle on the extension.
# Every 60 s:
#   - amendment 12, Ni0_OOH: the first of r4 / r5 to converge stands; the other is stopped then and
#     reported (RESCUE_HANDLED first, as amendment 13 did, so no rerun follows);
#   - V1 is done when, for 5 consecutive polls:
#       (a) no V1 pw.x job runs (u0__NiOOH__*, u0__NiFeOOH__*, CK__u0__NiFeOOH__*);
#       (b) cfg_queue.txt has no unlaunched entry (single points and V1 reruns are queued there);
#       (c) every relaxation in cfg_watch.txt carries CFG_QUEUED or CFG_SKIPPED (post_relax.sh has
#           handled it, so no single points are still to be queued);
#     then DEADLINE is set to now. deadline.sh (5 min poll) stops every run, the V2 (CoOOH) runs
#     included, as registered (V2 continues off AWS); the watchdog packages after 30 min, the
#     local loop pulls and terminates, density_pull.sh copies keep/.
# Exits at DEADLINE_HIT or once it has set the deadline.
#   DRY=1 bash v1done.sh     (evaluate every condition once and print it; touch nothing)
#   setsid nohup bash v1done.sh > /dev/null 2>&1 < /dev/null &
set -u
W=$HOME/film; cd "$W" || exit 1
log() { echo "$* $(date -u +%FT%TZ)" >> "$W/queue.log"; }
N4=u0__NiOOH__Ni0_OOH_r4 N5=u0__NiOOH__Ni0_OOH_r5
prt() { pgrep -f "^prterun --bind-to none -np [0-9]+ pw[.]x -nk [0-9]+ -in $1[.]in$" | head -1; }
v1_running() {  # names of running V1 jobs
  pgrep -af "^prterun --bind-to none -np [0-9]+ pw[.]x -nk [0-9]+ -in " | sed -E 's/.* -in (.*)[.]in$/\1/' \
    | grep -E '^(C[0-9]+__)?u0__Ni(Fe)?OOH__' | tr '\n' ' '
}
unlaunched() { while read -r n; do [ -n "$n" ] && [ ! -d "runs/$n" ] && printf '%s ' "$n"; done < cfg_queue.txt; }
unhandled() {
  while read -r r; do
    [ -z "$r" ] && continue
    [ -f "runs/$r/CFG_QUEUED" ] || [ -f "runs/$r/CFG_SKIPPED" ] || printf '%s ' "$r"
  done < cfg_watch.txt
}
first_converged() {  # amendment 12: stop the other Ni0_OOH run once one has converged
  local a b p
  for a in $N4 $N5; do
    b=$N5; [ "$a" = "$N5" ] && b=$N4
    grep -q "bfgs converged" "runs/$a/$a.out" 2>/dev/null || continue
    p=$(prt $b); [ -n "$p" ] || continue
    if [ "${DRY:-0}" = 1 ]; then echo "would stop $b ($a converged)"; return; fi
    touch "runs/$b/RESCUE_HANDLED"; kill "$p"
    log "STOPPED $b (amendment 12: $a converged first, $(grep -a -c '^!' "runs/$a/$a.out") steps, E $(grep -a '^!' "runs/$a/$a.out" | tail -1 | awk '{print $5}') Ry; $b was at step $(grep -a -c '^!' "runs/$b/$b.out"), E $(grep -a '^!' "runs/$b/$b.out" | tail -1 | awk '{print $5}') Ry)"
    return
  done
}
if [ "${DRY:-0}" = 1 ]; then
  echo "V1 running: $(v1_running)"; echo "cfg_queue unlaunched: $(unlaunched)"; echo "cfg_watch unhandled: $(unhandled)"
  first_converged; echo "DEADLINE $(date -u -d @"$(cat DEADLINE)" +%FT%TZ); DRY: nothing touched"; exit 0
fi
log "V1DONE watcher started: sets DEADLINE to now once no V1 job runs or waits for 5 consecutive minutes; stops the second Ni0_OOH run when the first converges (amendment 12)"
ok=0
while true; do
  [ -f DEADLINE_HIT ] && { log "V1DONE watcher: DEADLINE_HIT; exits"; exit 0; }
  first_converged
  if [ -z "$(v1_running)" ] && [ -z "$(unlaunched)" ] && [ -z "$(unhandled)" ]; then ok=$((ok + 1)); else ok=0; fi
  if [ "$ok" -ge 5 ]; then
    now=$(date +%s)
    [ "$now" -lt "$(cat DEADLINE)" ] && echo "$now" > DEADLINE.tmp && mv DEADLINE.tmp DEADLINE
    log "V1 DONE: no V1 job running or queued for 5 min; DEADLINE brought forward to $(date -u -d @"$(cat DEADLINE)" +%FT%TZ) (V2 runs stop with it)"
    exit 0
  fi
  sleep 60
done
