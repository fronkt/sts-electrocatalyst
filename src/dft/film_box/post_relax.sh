#!/usr/bin/env bash
# Amendment 9 launcher (replaces the side_queue_b.txt queue; the only launcher while it runs).
# v2 (2026-11-16 ~03:30Z) adds automatic reruns of relaxations whose SCF stops unconverged;
# v3 (~04:15Z) queues C4 too and applies amendment 10 (conv_thr 1e-5 at the noise floor);
# v4 (08:32Z) queues C5 too (amendment 11); v5 (10:39Z) gives waiting V1 work a running CoOOH
# run's cores (V1 before V2, as yield_co.sh did at 01:03Z) while >= 75 min remain to the deadline;
# v6 (16:40Z) queues C6 too (rule 1: the pattern Fe0_OOH's relaxation ended in);
# v7 (2026-11-17 ~00:30Z, amendment 17) queues C7 too (rule 3: the pattern Fe0_OH_r6's step-8 SCF entered).
# Every 30 s:
#   - keep/RUN holds hardlinks to the density files (charge-density.hdf5, occup.txt, paw.txt) of
#     every relaxation in rescue_watch.txt, so they survive run_side.sh deleting tmp/;
#   - a watched relaxation logged as DONE with SCF_FAIL>0 gets a rerun RUN_rK (amendment-9 rerun
#     rule): its last geometry (input geometry if it finished no step), startingpot='file' from its
#     kept density, staged in stage/RUN_rK for run_side.sh. The rerun goes to the top of
#     cfg_queue.txt (co_queue.txt for CoOOH) and inherits RUN's cfg_watch / rescue_watch entries.
#     At most 3 automatic reruns per chain; none for a rerun that again finishes no step;
#   - each relaxation listed in cfg_watch.txt that has converged gets its C1-C7 single points
#     (make_cfg_sp.sh), appended to cfg_queue.txt; one that ended without converging is skipped
#     (marker files CFG_QUEUED / CFG_SKIPPED in its run dir);
#   - when 24 cores are free, the next unlaunched run starts: cfg_queue.txt first (V1), then
#     co_queue.txt (CoOOH, V2). A run counts as launched once runs/NAME exists.
# Never starts a run at or after the DEADLINE. Exits when nothing is left to watch or launch.
#   setsid nohup bash post_relax.sh > /dev/null 2>&1 < /dev/null &
# Test knobs: PR_W (work dir), PR_MAXCORES (0 = never launch), PR_ONCE=1 (one cycle, no launch
# step), PR_ONCE=2 (one cycle including the launch/yield step).
set -u
W=${PR_W:-$HOME/film}
cd "$W" || exit 1
np=24 maxcores=${PR_MAXCORES:-192}
CFG_LIST="C1 C2 C3 C4 C5 C6 C7"  # must match make_cfg_sp.sh's default CFGS
log() { echo "$* $(date -u +%FT%TZ)" >> "$W/queue.log"; }
touch cfg_queue.txt co_queue.txt cfg_watch.txt rescue_watch.txt
mkdir -p keep stage
next() {  # first unlaunched name in the given queue files
  for q in "$@"; do
    while read -r n; do
      [ -n "$n" ] && [ ! -d "runs/$n" ] && { echo "$n"; return; }
    done < "$q"
  done
}
base_of() { echo "$1" | sed -E 's/_r[0-9]+$//'; }
refresh_keep() {
  local r s f
  while read -r r; do
    [ -z "$r" ] && continue
    s=runs/$r/tmp/$r.save
    [ -f "$s/charge-density.hdf5" ] || continue
    mkdir -p "keep/$r"
    for f in charge-density.hdf5 occup.txt paw.txt; do
      [ -f "$s/$f" ] && ln -f "$s/$f" "keep/$r/$f" 2>/dev/null
    done
  done < rescue_watch.txt
}
prepend() {  # name file
  { echo "$1"; cat "$2"; } > "$2.tmp" && mv "$2.tmp" "$2"
}
rescue() {  # $1 = watched relaxation that stopped with an unconverged SCF
  local r=$1 b k n steps q
  b=$(base_of "$r")
  steps=$(grep -a -c '^!' "runs/$r/$r.out")
  if [ "$(grep -c "^RESCUE .* -> ${b}_r[0-9]*:" queue.log)" -ge 3 ]; then
    log "RESCUE_GIVEUP $r: chain already has 3 automatic reruns"; return
  fi
  if [ "$steps" -eq 0 ] && grep -q "^RESCUE .* -> $r:" queue.log; then
    log "RESCUE_GIVEUP $r: an automatic rerun that again finished no step"; return
  fi
  for f in charge-density.hdf5 occup.txt paw.txt; do
    [ -f "keep/$r/$f" ] || { log "RESCUE_GIVEUP $r: no kept $f"; return; }
  done
  k=$(ls -d "runs/${b}_r"* "stage/${b}_r"* 2>/dev/null | sed -E 's/.*_r([0-9]+)$/\1/' | grep -E '^[0-9]+$' | sort -n | tail -1)
  k=$(( ${k:-1} + 1 ))
  n=${b}_r$k
  # amendment 10: an SCF whose last 30 iterations all sat below 1e-5 Ry is at this setup's noise
  # floor; its rerun uses conv_thr 1e-5 (the amendment-6 value)
  local L ct="" floor
  L=$(grep -a -n '^!' "runs/$r/$r.out" | tail -1 | cut -d: -f1)
  floor=$(tail -n +"${L:-1}" "runs/$r/$r.out" | grep -a 'estimated scf accuracy' | tail -30 \
    | awk '{n++; if ($5 + 0 >= 1e-5) bad = 1} END {print (n == 30 && !bad) ? 1 : 0}')
  [ "$floor" = 1 ] && ct=1.0d-5
  if [ "$steps" -ge 1 ]; then
    python3 qe_restart_input.py "runs/$r/$r.in" "runs/$r/$r.out" "inputs/$n.in" "$n" ${ct:+--conv-thr $ct} >> post_relax.log 2>&1 \
      || { log "RESCUE_FAIL $r: qe_restart_input.py (see post_relax.log)"; return; }
  else
    sed "s/prefix = '[^']*'/prefix = '$n'/" "runs/$r/$r.in" > "inputs/$n.in"
    [ -n "$ct" ] && sed -i "s/^\( *\)conv_thr = [^ ]*/\1conv_thr = $ct/" "inputs/$n.in"
  fi
  if [ -n "$ct" ] && [ "$(grep -c "conv_thr = $ct" "inputs/$n.in")" != 1 ]; then
    log "RESCUE_FAIL $r: conv_thr edit for $n"; return
  fi
  grep -q "startingpot = 'file'" "inputs/$n.in" \
    || sed -i "s/^\( *\)mixing_mode = /\1startingpot = 'file'\n&/" "inputs/$n.in"
  if [ "$(grep -c "startingpot = 'file'" "inputs/$n.in")" != 1 ] || [ "$(grep -c "prefix = '$n'" "inputs/$n.in")" != 1 ]; then
    log "RESCUE_FAIL $r: input edit for $n"; return
  fi
  mkdir -p "stage/$n" && cp -p "keep/$r/charge-density.hdf5" "keep/$r/occup.txt" "keep/$r/paw.txt" "stage/$n/" \
    || { log "RESCUE_FAIL $r: staging $n"; return; }
  case "$b" in *CoOOH*) q=co_queue.txt ;; *) q=cfg_queue.txt ;; esac
  prepend "$n" "$q"
  echo "$n" >> rescue_watch.txt
  grep -qx "$r" cfg_watch.txt && echo "$n" >> cfg_watch.txt
  local g="last geometry"; [ "$steps" -eq 0 ] && g="input geometry"
  log "RESCUE $r (SCF not converged at step $((steps + 1))) -> $n: $g, startingpot=file from its kept density${ct:+, conv_thr $ct (amendment 10)}; top of $q"
}
last_yield=0
yield_co() {  # $1 = waiting V1 run. V1 before V2: stop the most recently started running CoOOH run
  local c best="" pid i
  for c in $(sed -n 's/^BEGIN \(u0__CoOOH__[^ ]*\) .*/\1/p' queue.log); do
    pgrep -f "prterun .*-in $c[.]in" > /dev/null && best=$c
  done
  [ -n "$best" ] || return 1
  pid=$(pgrep -f "prterun .*-in $best[.]in" | head -1)
  kill "$pid" || return 1
  last_yield=$(date +%s)
  for i in $(seq 1 60); do pgrep -f "run_side[.]sh $best " > /dev/null || break; sleep 2; done
  pgrep -f "run_side[.]sh $best " > /dev/null && { log "YIELD_FAIL $best: run_side.sh still alive"; return 1; }
  mkdir -p runs_stopped && mv "runs/$best" "runs_stopped/${best}__stopped_$(date -u +%H%MZ)" \
    || { log "YIELD_FAIL $best: could not move its dir"; return 1; }
  log "YIELD $best (V1 before V2) for $1: stopped, dir moved to runs_stopped/, relaunches from co_queue.txt"
}
scan_failed() {
  local r
  while read -r r; do
    [ -z "$r" ] && continue
    [ -d "runs/$r" ] && [ ! -f "runs/$r/RESCUE_HANDLED" ] || continue
    if grep -q "^DONE $r .*SCF_FAIL=[1-9]" queue.log; then
      touch "runs/$r/RESCUE_HANDLED"; rescue "$r"
    fi
  done < <(cat rescue_watch.txt)
}
log "POST_RELAX v7 started (watch: $(tr '\n' ' ' < cfg_watch.txt); rescue: $(tr '\n' ' ' < rescue_watch.txt); CoOOH: $(tr '\n' ' ' < co_queue.txt))"
while true; do
  dl=$(cat DEADLINE 2>/dev/null || echo 0)
  if [ -f DEADLINE_HIT ] || { [ "$dl" -gt 0 ] && [ "$(date +%s)" -ge "$dl" ]; }; then
    log "POST_RELAX stopped at the deadline; not launched: $(next cfg_queue.txt) $(next co_queue.txt)"; exit 0
  fi
  refresh_keep
  scan_failed
  watching=0
  while read -r r; do
    [ -z "$r" ] && continue
    d=runs/$r
    [ -f "$d/CFG_QUEUED" ] || [ -f "$d/CFG_SKIPPED" ] && continue
    if grep -q "bfgs converged" "$d/$r.out" 2>/dev/null; then
      if bash make_cfg_sp.sh "$r" >> post_relax.log 2>&1; then
        for c in $CFG_LIST; do echo "${c}__$r"; done >> cfg_queue.txt; touch "$d/CFG_QUEUED"
        log "CFG_SP queued $(for c in $CFG_LIST; do printf '%s ' "${c}__$r"; done)"
      else
        touch "$d/CFG_SKIPPED"; log "CFG_SP input failed for $r (see post_relax.log)"
      fi
    elif grep -q "^DONE $r " queue.log; then
      touch "$d/CFG_SKIPPED"; log "CFG_SP skipped for $r: finished without a converged relaxation"
    else
      watching=1
    fi
  done < cfg_watch.txt
  [ "${PR_ONCE:-0}" = 1 ] && exit 0
  n=$(next cfg_queue.txt co_queue.txt)
  if [ -n "$n" ]; then
    if [ $(( $(pgrep -x pw.x | wc -l) + np )) -le "$maxcores" ]; then
      sleep 5; scan_failed  # a run that just died: its rerun goes first
      n=$(next cfg_queue.txt co_queue.txt)
      setsid nohup bash "$W/run_side.sh" "$n" "$np" 3 > /dev/null 2>&1 < /dev/null &
      sleep 90  # let the ranks appear before the next core count
      continue
    fi
    # v5: V1 work waiting and no cores: take a CoOOH slot, if the V1 run can finish (~66 min) before
    # the deadline kills it, and at most once per 5 min (the stopped ranks need a moment to exit)
    v=$(next cfg_queue.txt); now=$(date +%s)
    if [ -n "$v" ] && [ $(( now - last_yield )) -ge 300 ] && { [ "$dl" -eq 0 ] || [ $(( dl - now )) -ge 4500 ]; }; then
      yield_co "$v"
    fi
  elif [ "$watching" -eq 0 ] && ! pgrep -x pw.x > /dev/null; then
    log "POST_RELAX done: nothing left to watch or launch"; exit 0
  fi
  [ "${PR_ONCE:-0}" = 2 ] && exit 0
  sleep 30
done
