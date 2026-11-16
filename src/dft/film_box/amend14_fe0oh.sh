#!/usr/bin/env bash
# Amendment 14 (2026-11-16 ~18:20Z): u0__NiFeOOH__Fe0_OH_r4's step-46 SCF (after a BFGS step with
# trust radius 0.141 bohr) reached 5.4e-5 Ry at iteration 22 and then drifted back to 3e-4 to 1e-3 Ry
# for 20 iterations, with the total moment wandering 11.0-11.2 muB. That matches Fe0_O's step-43 SCF
# (amendment 13). Its settings are the registered ones (conv_thr 5e-6, upscale 1, beta 0.1, ndim 12).
# The registered automatic rerun waits for electron_maxstep (200), about 2.5 h at ~1 min per iteration.
# Rule: if any SCF of r4 reaches MAXIT (60) iterations without converging (Fe0_OH_r4's steps take 10-21;
# Fe0_O was stopped at 54), r4 is stopped and rerun as r5 (amendment-9 rerun rule) from its last printed
# geometry and its kept density (the last converged SCF), with
#   upscale = 1.d0, conv_thr 5e-6      (amendment 4's registered settings, unchanged)
#   mixing_beta 0.05, mixing_ndim 20   (SCF numerics, as amendment 12's r4 and amendment 13's r2)
# Same model, cutoffs, smearing, dipole correction, forc_conv_thr 2e-3. r5 goes to the top of
# cfg_queue.txt with its density staged, so post_relax.sh launches it into the freed slot; it is in
# cfg_watch.txt (C1-C6 when it converges) and rescue_watch.txt. If r4 converges or ends, nothing happens.
#   DRY=1 bash amend14_fe0oh.sh                    (build r5's input in /tmp now, show the diff; touch nothing)
#   setsid nohup bash amend14_fe0oh.sh > /dev/null 2>&1 < /dev/null &   (watch, polls every 60 s, up to 10 h)
set -u
W=$HOME/film; cd "$W" || exit 1
R=u0__NiFeOOH__Fe0_OH_r4 N=u0__NiFeOOH__Fe0_OH_r5 MAXIT=${MAXIT:-60}
o=runs/$R/$R.out k=keep/$R
log() { echo "$* $(date -u +%FT%TZ)" >> "$W/queue.log"; }
prt() { pgrep -f "^prterun --bind-to none -np [0-9]+ pw[.]x -nk [0-9]+ -in $R[.]in$" | head -1; }
cur_its() {  # SCF iterations after the last '!' (the SCF in progress)
  local L; L=$(grep -a -n '^!' "$o" | tail -1 | cut -d: -f1)
  tail -n +"$(( ${L:-0} + 1 ))" "$o" | grep -a -c 'iteration #'
}
build() {  # $1 = output dir; builds $1/$N.in and checks it
  python3 qe_restart_input.py runs/$R/$R.in "$o" "$1/$N.in" $N --conv-thr 5.0d-6 --upscale 1.d0 > /dev/null || return 1
  sed -i -e "s/^\( *\)mixing_beta = .*/\1mixing_beta = 0.05/" -e "s/^\( *\)mixing_ndim = .*/\1mixing_ndim = 20/" "$1/$N.in"
  grep -q "startingpot = 'file'" "$1/$N.in" || sed -i "s/^\( *\)mixing_mode = /\1startingpot = 'file'\n&/" "$1/$N.in"
  local ok=1 s
  for s in "prefix = '$N'" "conv_thr = 5.0d-6" "upscale = 1.d0" "mixing_beta = 0.05" "mixing_ndim = 20" \
           "startingpot = 'file'" "ion_dynamics = 'bfgs'" "calculation = 'relax'" "forc_conv_thr = 2.0d-3"; do
    [ "$(grep -c "$s" "$1/$N.in")" = 1 ] || { echo "CHECK FAILED: $1/$N.in lacks exactly one '$s'"; ok=0; }
  done
  for s in charge-density.hdf5 occup.txt paw.txt; do [ -f $k/$s ] || { echo "no kept $s"; ok=0; }; done
  [ "$ok" = 1 ]
}
maxdx() {  # $1 = input; max |dx| against r4's last printed geometry
  python3 - "$o" "$1" <<'EOF'
import re, sys
out = open(sys.argv[1], errors="replace").read(); inp = open(sys.argv[2]).read()
nat = int(re.search(r"nat = (\d+)", inp).group(1))
last = re.findall(r"ATOMIC_POSITIONS \(angstrom\)\n((?:.*\n){%d})" % nat, out)[-1].strip().split("\n")
new = inp.split("ATOMIC_POSITIONS angstrom\n", 1)[1].split("\n")[:nat]
print("%.2e A" % max(abs(float(a) - float(b)) for l1, l2 in zip(last, new) for a, b in zip(l1.split()[1:4], l2.split()[1:4])))
EOF
}
{ [ -e runs/$N ] || [ -e stage/$N ] || grep -qx "$N" cfg_queue.txt; } && { echo "$N exists"; exit 1; }
if [ "${DRY:-0}" = 1 ]; then
  build /tmp || exit 1
  echo "== diff $R.in -> $N.in (non-position lines)"
  diff <(sed '/^ATOMIC_POSITIONS/,$d' runs/$R/$R.in) <(sed '/^ATOMIC_POSITIONS/,$d' /tmp/$N.in)
  echo "   positions vs $R's last printed geometry: max |dx| $(maxdx /tmp/$N.in)"
  echo "   kept density: $(stat -c '%y' $k/charge-density.hdf5 | cut -c1-19); last '!' of $R: $(grep -a -c '^!' "$o") steps, E $(grep -a '^!' "$o" | tail -1 | awk '{print $5}') Ry"
  echo "   SCF in progress: $(cur_its) iterations (trigger at $MAXIT); prterun pid $(prt)"
  echo "DRY: input in /tmp, nothing touched"; exit 0
fi
log "SCFWATCH $R (amendment 14): watching; an SCF reaching $MAXIT iterations without converging starts $N"
for i in $(seq 1 600); do
  pid=$(prt)
  [ -n "$pid" ] || { log "SCFWATCH $R: not running; exits, nothing done"; exit 0; }
  grep -q "bfgs converged" "$o" && { log "SCFWATCH $R: converged; exits, nothing done"; exit 0; }
  it=$(cur_its)
  if [ "$it" -ge "$MAXIT" ]; then
    step=$(( $(grep -a -c '^!' "$o") + 1 ))
    acc=$(grep -a 'estimated scf accuracy' "$o" | tail -10 | awk '{print $5}' | sort -g | sed -n '1p;$p' | tr '\n' ' ')
    build inputs || { log "SCFWATCH $R: step-$step SCF at $it iterations, but $N's input failed its checks; nothing done"; exit 1; }
    dens=$(stat -c '%y' $k/charge-density.hdf5 | cut -c1-19)
    mkdir -p stage/$N && cp -p $k/charge-density.hdf5 $k/occup.txt $k/paw.txt stage/$N/ \
      || { log "SCFWATCH $R: staging $N's density failed; nothing done"; rm -f inputs/$N.in; exit 1; }
    echo $N >> rescue_watch.txt
    echo $N >> cfg_watch.txt
    { echo $N; cat cfg_queue.txt; } > cfg_queue.txt.tmp && mv cfg_queue.txt.tmp cfg_queue.txt || exit 1
    touch runs/$R/RESCUE_HANDLED
    kill "$pid"
    for j in $(seq 1 60); do pgrep -f "^bash $W/run_side[.]sh $R " > /dev/null || break; sleep 2; done
    log "STOPPED $R (amendment 14): step-$step SCF at $it iterations without converging (last 10 accuracies ${acc% } Ry); rerun $N (upscale 1, conv_thr 5e-6, beta 0.05, ndim 20) from its last printed geometry (max |dx| $(maxdx inputs/$N.in)) and its kept density ($dens), top of cfg_queue.txt"
    exit 0
  fi
  sleep 60
done
log "SCFWATCH $R: 10 h without the trigger firing; exits"
