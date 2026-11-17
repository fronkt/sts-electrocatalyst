#!/usr/bin/env bash
# Amendment 20 (2026-11-17, before any eta existed). r8's first SCF repeats r7's step 2 (same
# geometry, same starting density) and has not converged. If it passes 60 iterations unconverged
# (amendment 18's stall threshold), stop r8 and start r9: r8's input unchanged except prefix and
# mixing_beta 0.02 in place of 0.05. That is a mixing-only change, which amendment 2 lets stand for
# the same state. Same geometry (r7's step 2, r8's input) and same density (keep/r7, r7's step-2
# density, which r8 was staged from). r9 is the last member of amendment 18's chain; amend18_watch.sh follows it as usual.
# Exits with no action if r8's first SCF converges, if r8 ends, or at DEADLINE_HIT.
#   DRY=1 bash amend20_r9.sh   (build r9's input in /tmp and show the checks; touch nothing)
#   setsid nohup bash amend20_r9.sh > /dev/null 2>&1 < /dev/null &
set -u
W=$HOME/film; cd "$W" || exit 1
B=u0__NiFeOOH__Fe0_OH; P=${B}_r8 N=${B}_r9
od=inputs; [ "${DRY:-0}" = 1 ] && od=/tmp
log() { echo "$* $(date -u +%FT%TZ)" >> "$W/queue.log"; }
prt() { pgrep -f "^prterun --bind-to none -np [0-9]+ pw[.]x -nk [0-9]+ -in $1[.]in$" | head -1; }
o=runs/$P/$P.out k=keep/${B}_r7   # r7's step-2 density (keep/r8 is a hard link into r8's live save dir)
build() {
  { [ -e runs/$N ] || [ -e stage/$N ] || grep -qx "$N" cfg_queue.txt; } && { echo "$N exists"; return 1; }
  sed -e "s/prefix = '$P'/prefix = '$N'/" -e "s/mixing_beta = 0.05/mixing_beta = 0.02/" runs/$P/$P.in > $od/$N.in
  local ok=1 s f
  chk() { [ "$(grep -c "$2" "$1")" = 1 ] || { echo "CHECK FAILED: $1 lacks exactly one '$2'"; ok=0; }; }
  for s in "prefix = '$N'" "mixing_beta = 0.02" "mixing_ndim = 20" "conv_thr = 5.0d-6" "upscale = 1.d0" \
           "startingpot = 'file'" "ion_dynamics = 'fire'" "calculation = 'relax'" "forc_conv_thr = 2.0d-3"; do chk $od/$N.in "$s"; done
  cmp -s <(sed -n '/^ATOMIC_POSITIONS/,$p' runs/$P/$P.in) <(sed -n '/^ATOMIC_POSITIONS/,$p' $od/$N.in) \
    || { echo "CHECK FAILED: positions differ from $P.in"; ok=0; }
  for f in charge-density.hdf5 occup.txt paw.txt; do [ -f $k/$f ] || { echo "no kept $f"; ok=0; }; done
  [ "$(stat -c '%Y' $k/charge-density.hdf5)" -lt "$(stat -c '%Y' runs/$P/$P.in)" ]     || { echo "CHECK FAILED: $k is newer than $P's start"; ok=0; }
  echo "== diff $P.in -> $N.in"
  diff runs/$P/$P.in $od/$N.in
  echo "   kept density: $(stat -c '%y' $k/charge-density.hdf5 | cut -c1-19) (r7's step 2, $(grep -a '^!' runs/${B}_r7/${B}_r7.out | tail -1 | awk '{print $5}') Ry)"
  [ "$ok" = 1 ] || { rm -f $od/$N.in; return 1; }
}
if [ "${DRY:-0}" = 1 ]; then build && echo "DRY: input in /tmp, nothing touched"; exit $?; fi
log "AMEND20 watcher started: stops $P and starts $N (mixing_beta 0.02) if $P's first SCF passes 60 iterations unconverged"
while true; do
  [ -f DEADLINE_HIT ] && { log "AMEND20 watcher: DEADLINE_HIT; exits"; exit 0; }
  grep -a -q '^!' "$o" && { log "AMEND20 watcher: $P's first SCF converged; no action; exits"; exit 0; }
  if [ -z "$(prt $P)" ] && grep -q "^DONE $P " queue.log; then log "AMEND20 watcher: $P ended; no action; exits"; exit 0; fi
  its=$(grep -a -c 'iteration #' "$o")
  if [ "$its" -ge 60 ] && [ -n "$(prt $P)" ]; then
    build >> post_relax.log 2>&1 || { log "AMEND20 watcher: building $N failed (see post_relax.log); exits"; exit 1; }
    mkdir -p stage/$N && cp -p $k/charge-density.hdf5 $k/occup.txt $k/paw.txt stage/$N/ || exit 1
    echo $N >> rescue_watch.txt
    echo $N >> cfg_watch.txt
    { echo $N; cat cfg_queue.txt; } > cfg_queue.txt.tmp && mv cfg_queue.txt.tmp cfg_queue.txt || exit 1
    touch runs/$P/RESCUE_HANDLED
    kill "$(prt $P)"
    for i in $(seq 1 60); do pgrep -f "^bash $W/run_side[.]sh $P " > /dev/null || break; sleep 2; done
    log "STOPPED $P (amendment 20): first SCF at $its iterations; rerun $N (mixing_beta 0.02, otherwise $P's input) from r7's step-2 geometry and density, top of cfg_queue.txt"
    exit 0
  fi
  sleep 60
done
