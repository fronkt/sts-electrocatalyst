#!/usr/bin/env bash
# Amendment 18 standing rule (2026-11-17 ~00:15Z, before any eta existed). Every 60 s, look at the newest
# member of the Fe-site *OH FIRE chain (r6, then r7, r8, r9). If it is running, has completed at
# least 2 steps, and its current SCF has passed 60 iterations, restart it from its last completed SCF
# as the next member (amend18_fe0oh.sh).
# Its regular SCFs take 8-13 iterations. The stalls (r4's step 46, r5, r6's step 9) were still
# unconverged at 60 and floored or failed by 120-200.
# Exits when the newest member has converged or ended, when the chain is used up (r9 is the last),
# or at DEADLINE_HIT.
#   setsid nohup bash amend18_watch.sh > /dev/null 2>&1 < /dev/null &
set -u
W=$HOME/film; cd "$W" || exit 1
log() { echo "$* $(date -u +%FT%TZ)" >> "$W/queue.log"; }
B=u0__NiFeOOH__Fe0_OH
chain="${B}_r6 ${B}_r7 ${B}_r8 ${B}_r9"
prt() { pgrep -f "^prterun --bind-to none -np [0-9]+ pw[.]x -nk [0-9]+ -in $1[.]in$" | head -1; }
log "AMEND18 watcher started: restarts the newest of $chain from its last completed SCF when its current SCF passes 60 iterations"
while true; do
  [ -f DEADLINE_HIT ] && { log "AMEND18 watcher: DEADLINE_HIT; exits"; exit 0; }
  cur="" nxt=""
  for n in $chain; do
    if [ -d "runs/$n" ] || [ -e "stage/$n" ] || grep -qx "$n" cfg_queue.txt; then cur=$n; nxt=""; elif [ -n "$cur" ] && [ -z "$nxt" ]; then nxt=$n; fi
  done
  o=runs/$cur/$cur.out
  if grep -q -e "FIRE: convergence achieved" -e "bfgs converged" "$o" 2>/dev/null; then
    log "AMEND18 watcher: $cur converged ($(grep -a -c '^!' "$o") steps); exits"; exit 0
  fi
  if [ -d "runs/$cur" ] && [ -z "$(prt "$cur")" ] && grep -q "^DONE $cur " queue.log; then
    log "AMEND18 watcher: $cur ended unconverged; exits (post_relax.sh's rerun rules apply)"; exit 0
  fi
  if [ -n "$(prt "$cur")" ]; then
    nb=$(grep -a -c '^!' "$o")
    its=$(tail -n +$(( $(grep -a -n '^!' "$o" | tail -1 | cut -d: -f1) + 1 )) "$o" | grep -a -c 'iteration #')
    if [ "$nb" -ge 2 ] && [ "$its" -ge 60 ]; then
      [ -n "$nxt" ] || { log "AMEND18 watcher: $cur's step $((nb + 1)) SCF passed 60 iterations; chain used up; exits"; exit 0; }
      P=$cur N=$nxt bash amend18_fe0oh.sh >> post_relax.log 2>&1 || { log "AMEND18 watcher: restart $cur -> $nxt failed (see post_relax.log); exits"; exit 1; }
    fi
  fi
  sleep 60
done
