#!/usr/bin/env bash
# Amendment 13 (2026-11-16 ~16:45Z): u0__NiFeOOH__Fe0_O has run since 2026-11-15 19:03Z without
# amendment 4's upscale = 1.d0 (every other U = 0 relaxation has it). pw.x's default upscale (100)
# has tightened its SCF target to 7e-8 to 1.3e-7 Ry, so each step takes 20-32 iterations (~60 s
# each). Its step-43 SCF has wandered for 50+ iterations (3e-4 to 2e-2 Ry, total moment 6.0-7.2
# muB). Rerun r2 (amendment-9 rerun rule): its last printed geometry and its kept step-42 density
# (startingpot = 'file'), with
#   upscale = 1.d0, conv_thr 5e-6        (amendment 4's registered settings)
#   mixing_beta 0.05, mixing_ndim 20     (SCF numerics, as amendment 12's r4)
# Same model, cutoffs, smearing, dipole correction, forc_conv_thr 2e-3. r2 goes to the top of
# cfg_queue.txt with its density staged, so post_relax.sh launches it into the freed slot; it is in
# cfg_watch.txt (C1-C6 when it converges) and rescue_watch.txt (automatic rerun if an SCF fails).
#   DRY=1 bash amend13_fe0o.sh   (write the input to /tmp, show the diff; touch nothing)
set -u
W=$HOME/film; cd "$W" || exit 1
R=u0__NiFeOOH__Fe0_O N=u0__NiFeOOH__Fe0_O_r2
od=inputs; [ "${DRY:-0}" = 1 ] && od=/tmp
{ [ -e runs/$N ] || [ -e stage/$N ] || grep -qx "$N" cfg_queue.txt; } && { echo "$N exists"; exit 1; }
python3 qe_restart_input.py runs/$R/$R.in runs/$R/$R.out $od/$N.in $N --conv-thr 5.0d-6 --upscale 1.d0 > /dev/null || exit 1
sed -i -e "s/^\( *\)mixing_beta = .*/\1mixing_beta = 0.05/" -e "s/^\( *\)mixing_ndim = .*/\1mixing_ndim = 20/" $od/$N.in
grep -q "startingpot = 'file'" $od/$N.in || sed -i "s/^\( *\)mixing_mode = /\1startingpot = 'file'\n&/" $od/$N.in
ok=1
chk() { [ "$(grep -c "$2" "$1")" = 1 ] || { echo "CHECK FAILED: $1 lacks exactly one '$2'"; ok=0; }; }
for s in "prefix = '$N'" "conv_thr = 5.0d-6" "upscale = 1.d0" "mixing_beta = 0.05" "mixing_ndim = 20" \
         "startingpot = 'file'" "ion_dynamics = 'bfgs'" "calculation = 'relax'"; do chk $od/$N.in "$s"; done
echo "== diff $R.in -> $N.in (non-position lines)"
diff <(sed '/^ATOMIC_POSITIONS/,$d' runs/$R/$R.in) <(sed '/^ATOMIC_POSITIONS/,$d' $od/$N.in)
echo "   positions vs $R's last printed geometry: max |dx| $(python3 - runs/$R/$R.out $od/$N.in <<'EOF'
import re, sys
out = open(sys.argv[1], errors="replace").read(); inp = open(sys.argv[2]).read()
nat = int(re.search(r"nat = (\d+)", inp).group(1))
last = re.findall(r"ATOMIC_POSITIONS \(angstrom\)\n((?:.*\n){%d})" % nat, out)[-1].strip().split("\n")
new = inp.split("ATOMIC_POSITIONS angstrom\n", 1)[1].split("\n")[:nat]
print("%.2e A" % max(abs(float(a) - float(b)) for l1, l2 in zip(last, new) for a, b in zip(l1.split()[1:4], l2.split()[1:4])))
EOF
)"
k=keep/$R
for f in charge-density.hdf5 occup.txt paw.txt; do [ -f $k/$f ] || { echo "no kept $f"; ok=0; }; done
echo "   kept density: $(stat -c '%y' $k/charge-density.hdf5 | cut -c1-19); $(grep -a -c '^!' runs/$R/$R.out) completed steps, last E $(grep -a '^!' runs/$R/$R.out | tail -1 | awk '{print $5}') Ry"
[ "$ok" = 1 ] || exit 1
[ "${DRY:-0}" = 1 ] && { echo "DRY: input in /tmp, nothing touched"; exit 0; }
pid=$(pgrep -f "prterun .*-in $R[.]in" | head -1); [ -n "$pid" ] || { echo "no prterun for $R"; exit 1; }
mkdir -p stage/$N && cp -p $k/charge-density.hdf5 $k/occup.txt $k/paw.txt stage/$N/ || exit 1
echo $N >> rescue_watch.txt
echo $N >> cfg_watch.txt
{ echo $N; cat cfg_queue.txt; } > cfg_queue.txt.tmp && mv cfg_queue.txt.tmp cfg_queue.txt || exit 1
touch runs/$R/RESCUE_HANDLED
kill "$pid"
for i in $(seq 1 60); do pgrep -f "run_side[.]sh $R " > /dev/null || break; sleep 2; done
pgrep -f "run_side[.]sh $R " > /dev/null && { echo "run_side for $R still alive"; exit 1; }
echo "STOPPED $R (amendment 13: no upscale since launch, SCF target 1e-7 Ry; step-43 SCF wandering at 3e-4 to 2e-2 Ry after 50+ iterations); rerun $N (upscale 1, conv_thr 5e-6, beta 0.05, ndim 20) from its last geometry and step-42 density, top of cfg_queue.txt $(date -u +%FT%TZ)" >> queue.log
for i in $(seq 1 24); do [ -d runs/$N ] && break; sleep 5; done
sleep 60
echo "pw=$(pgrep -x pw.x | wc -l)"; tail -4 queue.log | cut -c1-220
echo "$N: $(grep -a -c 'iteration #' runs/$N/$N.out 2>/dev/null) iterations; $(grep -a -m1 -i 'error\|starting charge\|initial density' runs/$N/$N.out)"
