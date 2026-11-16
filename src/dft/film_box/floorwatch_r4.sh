#!/usr/bin/env bash
# Amendment 12: u0__NiOOH__Ni0_OOH_r4 (BFGS at conv_thr 5e-6, mixing beta 0.05 / ndim 20) tests
# whether new mixing gets Ni0_OOH's SCF under its noise floor. If its current SCF meets amendment
# 10's noise-floor test (last 30 iterations all < 1e-5 Ry, not converged), it cannot converge at
# 5e-6: stop it, and r5 (FIRE) carries Ni0_OOH. Exits without stopping it if the SCF converges.
# Runs on the box (setsid), so a lost SSH connection does not affect it. Polls every 60 s, up to 4 h.
set -u
W=$HOME/film; cd "$W" || exit 1
n=u0__NiOOH__Ni0_OOH_r4; o=runs/$n/$n.out
log() { echo "$* $(date -u +%FT%TZ)" >> "$W/queue.log"; }
for i in $(seq 1 240); do
  pid=$(pgrep -f "prterun .*-in $n[.]in" | head -1)
  [ -n "$pid" ] || { log "FLOORWATCH $n: not running; nothing to do"; exit 0; }
  L=$(grep -a -n '^!' "$o" | tail -1 | cut -d: -f1)
  # only the SCF in progress counts: lines after the last '!' (all lines before the first one)
  cur=$(tail -n +"$(( ${L:-0} + 1 ))" "$o")
  floor=$(echo "$cur" | grep -a 'estimated scf accuracy' | tail -30 \
    | awk '{n++; if ($5 + 0 >= 1e-5) bad = 1} END {print (n == 30 && !bad) ? 1 : 0}')
  if [ "$floor" = 1 ]; then
    spread=$(echo "$cur" | grep -a 'total energy  *=' | tail -30 | awk '{print $4}' | sort -g | sed -n '1p;$p' \
      | tr '\n' ' ' | awk '{printf "%.3f", ($2 - $1) * 1000}')
    lo=$(echo "$cur" | grep -a 'estimated scf accuracy' | tail -30 | awk '{print $5}' | sort -g | sed -n '1p;$p' | tr '\n' ' ')
    kill "$pid"
    log "STOPPED $n (amendment 12): SCF of step $(( $(grep -a -c '^!' "$o") + 1 )) at the noise floor (last 30 iterations ${lo% } Ry against conv_thr 5e-6; energy spread ${spread} mRy); r5 (FIRE) carries Ni0_OOH"
    exit 0
  fi
  sleep 60
done
log "FLOORWATCH $n: 4 h without the floor test firing; exits"
