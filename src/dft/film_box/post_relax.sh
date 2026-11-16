#!/usr/bin/env bash
# Amendment 9 launcher (replaces the side_queue_b.txt queue; the only launcher while it runs).
# v2 (2026-11-16 ~03:30Z) adds automatic reruns of relaxations whose SCF stops unconverged.
# Every 30 s:
#   - keep/RUN holds hardlinks to the density files (charge-density.hdf5, occup.txt, paw.txt) of
#     every relaxation in rescue_watch.txt, so they survive run_side.sh deleting tmp/;
#   - a watched relaxation logged as DONE with SCF_FAIL>0 gets a rerun RUN_rK (amendment-9 rerun
#     rule): its last geometry (input geometry if it finished no step), startingpot='file' from its
#     kept density, staged in stage/RUN_rK for run_side.sh. The rerun goes to the top of
#     cfg_queue.txt (co_queue.txt for CoOOH) and inherits RUN's cfg_watch / rescue_watch entries.
#     At most 3 automatic reruns per chain; none for a rerun that again finishes no step;
#   - each relaxation listed in cfg_watch.txt that has converged gets its C1-C3 single points
#     (make_cfg_sp.sh), appended to cfg_queue.txt; one that ended without converging is skipped
#     (marker files CFG_QUEUED / CFG_SKIPPED in its run dir);
#   - when 24 cores are free, the next unlaunched run starts: cfg_queue.txt first (V1), then
#     co_queue.txt (CoOOH, V2). A run counts as launched once runs/NAME exists.
# Never starts a run at or after the DEADLINE. Exits when nothing is left to watch or launch.
#   setsid nohup bash post_relax.sh > /dev/null 2>&1 < /dev/null &
# Test knobs: PR_W (work dir), PR_MAXCORES (0 = never launch), PR_ONCE=1 (one cycle).
set -u
W=${PR_W:-$HOME/film}
cd "$W" || exit 1
np=24 maxcores=${PR_MAXCORES:-192}
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
  if [ "$steps" -ge 1 ]; then
    python3 qe_restart_input.py "runs/$r/$r.in" "runs/$r/$r.out" "inputs/$n.in" "$n" >> post_relax.log 2>&1 \
      || { log "RESCUE_FAIL $r: qe_restart_input.py (see post_relax.log)"; return; }
  else
    sed "s/prefix = '[^']*'/prefix = '$n'/" "runs/$r/$r.in" > "inputs/$n.in"
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
  log "RESCUE $r (SCF not converged at step $((steps + 1))) -> $n: $g, startingpot=file from its kept density; top of $q"
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
log "POST_RELAX v2 started (watch: $(tr '\n' ' ' < cfg_watch.txt); rescue: $(tr '\n' ' ' < rescue_watch.txt); CoOOH: $(tr '\n' ' ' < co_queue.txt))"
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
  elif [ "$watching" -eq 0 ] && ! pgrep -x pw.x > /dev/null; then
    log "POST_RELAX done: nothing left to watch or launch"; exit 0
  fi
  sleep 30
done
