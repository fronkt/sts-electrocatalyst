#!/usr/bin/env bash
# Amendment 12 (2026-11-16 ~14:10Z): u0__NiOOH__Ni0_OOH_r3 is stuck in a BFGS 4-cycle (SCF noise at
# conv_thr 1e-5 against forces of 0.035 Ry/bohr). Two reruns from r3's last geometry and r3's
# last-step density (the save dir is not rewritten mid-SCF), side by side:
#   r4  BFGS, conv_thr 5e-6 (the registered value), mixing_beta 0.05 / mixing_ndim 20 (SCF numerics)
#   r5  FIRE (ion_dynamics = 'fire', force-only), conv_thr 1e-5 (converges at this geometry)
# Same model, cutoffs, smearing, dipole correction, forc_conv_thr 2e-3. The first to converge stands
# and the other is stopped. Neither gets an automatic post_relax rerun (RESCUE_HANDLED); both are
# in rescue_watch.txt only so their densities stay in keep/.
#   DRY=1 bash amend12_ni0ooh.sh   (write both inputs to /tmp, show diffs; touch nothing)
set -u
W=$HOME/film; cd "$W" || exit 1
R3=u0__NiOOH__Ni0_OOH_r3 R4=u0__NiOOH__Ni0_OOH_r4 R5=u0__NiOOH__Ni0_OOH_r5
od=inputs; [ "${DRY:-0}" = 1 ] && od=/tmp
for n in $R4 $R5; do { [ -e runs/$n ] || [ -e stage/$n ]; } && { echo "$n exists"; exit 1; }; done
python3 qe_restart_input.py runs/$R3/$R3.in runs/$R3/$R3.out $od/$R4.in $R4 --conv-thr 5.0d-6 > /dev/null || exit 1
sed -i -e "s/^\( *\)mixing_beta = .*/\1mixing_beta = 0.05/" -e "s/^\( *\)mixing_ndim = .*/\1mixing_ndim = 20/" $od/$R4.in
python3 qe_restart_input.py runs/$R3/$R3.in runs/$R3/$R3.out $od/$R5.in $R5 > /dev/null || exit 1
sed -i "s/^\( *\)ion_dynamics = 'bfgs'/\1ion_dynamics = 'fire'/" $od/$R5.in
ok=1
chk() { [ "$(grep -c "$2" "$1")" = 1 ] || { echo "CHECK FAILED: $1 lacks exactly one '$2'"; ok=0; }; }
chk $od/$R4.in "prefix = '$R4'"; chk $od/$R4.in "conv_thr = 5.0d-6"; chk $od/$R4.in "mixing_beta = 0.05"
chk $od/$R4.in "mixing_ndim = 20"; chk $od/$R4.in "ion_dynamics = 'bfgs'"; chk $od/$R4.in "startingpot = 'file'"
chk $od/$R5.in "prefix = '$R5'"; chk $od/$R5.in "conv_thr = 1.0d-5"; chk $od/$R5.in "mixing_beta = 0.1"
chk $od/$R5.in "ion_dynamics = 'fire'"; chk $od/$R5.in "startingpot = 'file'"
for n in $R4 $R5; do
  echo "== diff $R3.in -> $n.in (non-position lines)"
  diff <(sed '/^ATOMIC_POSITIONS/,$d' runs/$R3/$R3.in) <(sed '/^ATOMIC_POSITIONS/,$d' $od/$n.in)
  echo "   positions vs r3's last printed geometry: max |dx| $(python3 - runs/$R3/$R3.out $od/$n.in <<'EOF'
import re, sys
out = open(sys.argv[1], errors="replace").read(); inp = open(sys.argv[2]).read()
nat = int(re.search(r"nat = (\d+)", inp).group(1))
last = re.findall(r"ATOMIC_POSITIONS \(angstrom\)\n((?:.*\n){%d})" % nat, out)[-1].strip().split("\n")
new = inp.split("ATOMIC_POSITIONS angstrom\n", 1)[1].split("\n")[:nat]
print("%.2e A" % max(abs(float(a) - float(b)) for l1, l2 in zip(last, new) for a, b in zip(l1.split()[1:4], l2.split()[1:4])))
EOF
)"
done
[ "$ok" = 1 ] || exit 1
[ "${DRY:-0}" = 1 ] && { echo "DRY: inputs in /tmp, nothing touched"; exit 0; }
pid=$(pgrep -f "prterun .*-in $R3[.]in" | head -1); [ -n "$pid" ] || { echo "no prterun for $R3"; exit 1; }
s=runs/$R3/tmp/$R3.save
for n in $R4 $R5; do mkdir -p stage/$n && cp -p $s/charge-density.hdf5 $s/occup.txt $s/paw.txt stage/$n/ || exit 1; done
kill "$pid"
for i in $(seq 1 60); do pgrep -f "run_side[.]sh $R3 " > /dev/null || break; sleep 2; done
pgrep -f "run_side[.]sh $R3 " > /dev/null && { echo "run_side for $R3 still alive"; exit 1; }
touch runs/$R3/RESCUE_HANDLED
echo "STOPPED $R3 (amendment 12: BFGS 4-cycle, SCF noise vs forces at conv_thr 1e-5); reruns $R4 (BFGS, conv_thr 5e-6, beta 0.05, ndim 20) and $R5 (FIRE, conv_thr 1e-5) from its last geometry and density $(date -u +%FT%TZ)" >> queue.log
for n in $R4 $R5; do
  echo $n >> rescue_watch.txt
  setsid nohup bash "$W/run_side.sh" $n 24 3 > /dev/null 2>&1 < /dev/null &
done
sleep 20
for n in $R4 $R5; do touch runs/$n/RESCUE_HANDLED; done
sleep 70
echo "pw=$(pgrep -x pw.x | wc -l)"; tail -4 queue.log | cut -c1-220
for n in $R4 $R5; do echo "$n: $(grep -a -c 'iteration #' runs/$n/$n.out 2>/dev/null) iterations; $(grep -a -m1 -i 'error\|FIRE input' runs/$n/$n.out)"; done
