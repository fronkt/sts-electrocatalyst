#!/usr/bin/env bash
# Amendment 16 (2026-11-16 ~20:40Z). u0__NiFeOOH__Fe0_OH_r5 (amendment 14) has not finished its
# first SCF at r4's step-46 trial geometry in 117 iterations. From iteration ~60 its accuracy sits at
# 3e-5 to 2e-4 Ry with the energy fixed to 0.1 mRy (-5161.31267 to -5161.31277): a floor 3-20x above
# conv_thr 5e-6, above amendment 10's 1e-5 test, so no registered rule covers it. r4's SCF at the
# same geometry (beta 0.1, ndim 12) wandered too, while r4's SCF at step 45's geometry converged in
# 13 iterations. The difficulty is at that geometry (a soft magnetic mode, most likely), and both
# SCFs started from a density 0.141 bohr (trust radius) away.
# r6, from r4's step-45 geometry (the last completed SCF) and its density (keep/, 17:27:10, written
# at that step's '!'), with
#   ion_dynamics = 'fire'              (as amendment 12's Ni0_OOH_r5: small steps, so each SCF starts
#                                       from a density at a nearby geometry)
#   mixing_beta 0.05, mixing_ndim 20   (as r5)
#   conv_thr 5e-6, upscale 1           (registered)
# Same model, cutoffs, smearing, dipole correction, forc_conv_thr 2e-3. r5 is stopped (RESCUE_HANDLED
# first, so no automatic rerun of it follows). r6 replaces r4 if its first energy, at step 45's
# geometry, is at most 1 mRy above r4's step-45 energy (-5161.31207972 Ry): the same solution.
# r6 is in cfg_watch.txt and rescue_watch.txt and goes to the top of cfg_queue.txt with its density
# staged, so post_relax.sh launches it into r5's slot.
#   DRY=1 bash amend16_fe0oh.sh   (build the input in /tmp and show the checks; touch nothing)
set -u
W=$HOME/film; cd "$W" || exit 1
P=u0__NiFeOOH__Fe0_OH_r4 R=u0__NiFeOOH__Fe0_OH_r5 N=u0__NiFeOOH__Fe0_OH_r6
od=inputs; [ "${DRY:-0}" = 1 ] && od=/tmp
log() { echo "$* $(date -u +%FT%TZ)" >> "$W/queue.log"; }
{ [ -e runs/$N ] || [ -e stage/$N ] || grep -qx "$N" cfg_queue.txt; } && { echo "$N exists"; exit 1; }
o=runs/$P/$P.out k=keep/$P
nb=$(grep -a -c '^!' "$o"); nblk=$(grep -a -c '^ATOMIC_POSITIONS' "$o")
# r4 started from its input geometry; block j is printed after step j, so block 44 is step 45's geometry
[ "$nb" = 45 ] && [ "$nblk" = 45 ] || { echo "unexpected: $nb steps, $nblk geometry blocks"; exit 1; }
L=$(grep -a -n '^ATOMIC_POSITIONS' "$o" | tail -1 | cut -d: -f1)
head -n $((L - 1)) "$o" > /tmp/${P}_to45.out   # its last block is then block 44
python3 qe_restart_input.py runs/$P/$P.in /tmp/${P}_to45.out $od/$N.in $N --conv-thr 5.0d-6 --upscale 1.d0 > /dev/null || exit 1
sed -i -e "s/^\( *\)mixing_beta = .*/\1mixing_beta = 0.05/" -e "s/^\( *\)mixing_ndim = .*/\1mixing_ndim = 20/" \
       -e "s/^\( *\)ion_dynamics = 'bfgs'/\1ion_dynamics = 'fire'/" $od/$N.in
grep -q "startingpot = 'file'" $od/$N.in || sed -i "s/^\( *\)mixing_mode = /\1startingpot = 'file'\n&/" $od/$N.in
ok=1
chk() { [ "$(grep -c "$2" "$1")" = 1 ] || { echo "CHECK FAILED: $1 lacks exactly one '$2'"; ok=0; }; }
for s in "prefix = '$N'" "conv_thr = 5.0d-6" "upscale = 1.d0" "mixing_beta = 0.05" "mixing_ndim = 20" \
         "startingpot = 'file'" "ion_dynamics = 'fire'" "calculation = 'relax'" "forc_conv_thr = 2.0d-3"; do chk $od/$N.in "$s"; done
for f in charge-density.hdf5 occup.txt paw.txt; do [ -f $k/$f ] || { echo "no kept $f"; ok=0; }; done
echo "== diff $P.in -> $N.in (non-position lines)"
diff <(sed '/^ATOMIC_POSITIONS/,$d' runs/$P/$P.in) <(sed '/^ATOMIC_POSITIONS/,$d' $od/$N.in)
python3 - "$o" $od/$N.in <<'EOF'
import re, sys
out = open(sys.argv[1], errors="replace").read(); inp = open(sys.argv[2]).read()
nat = int(re.search(r"nat = (\d+)", inp).group(1))
blocks = re.findall(r"ATOMIC_POSITIONS \(angstrom\)\n((?:.*\n){%d})" % nat, out)
new = [l.split()[1:4] for l in inp.split("ATOMIC_POSITIONS angstrom\n", 1)[1].split("\n")[:nat]]
def dx(b):
    rows = [l.split()[1:4] for l in b.strip().split("\n")]
    return max(abs(float(a) - float(c)) for r1, r2 in zip(rows, new) for a, c in zip(r1, r2))
print("   positions vs block 44 (step 45's geometry): max |dx| %.2e A; vs block 45 (step-46 trial): %.3f A" % (dx(blocks[-2]), dx(blocks[-1])))
EOF
echo "   kept density: $(stat -c '%y' $k/charge-density.hdf5 | cut -c1-19); r4 step 45: E $(grep -a '^!' "$o" | tail -1 | awk '{print $5}') Ry"
[ "$ok" = 1 ] || { rm -f $od/$N.in; exit 1; }
[ "${DRY:-0}" = 1 ] && { echo "DRY: input in /tmp, nothing touched"; exit 0; }
pid=$(pgrep -f "^prterun --bind-to none -np [0-9]+ pw[.]x -nk [0-9]+ -in $R[.]in$" | head -1)
[ -n "$pid" ] || { echo "no prterun for $R"; rm -f $od/$N.in; exit 1; }
its=$(grep -a -c 'iteration #' runs/$R/$R.out)
mkdir -p stage/$N && cp -p $k/charge-density.hdf5 $k/occup.txt $k/paw.txt stage/$N/ || exit 1
echo $N >> rescue_watch.txt
echo $N >> cfg_watch.txt
{ echo $N; cat cfg_queue.txt; } > cfg_queue.txt.tmp && mv cfg_queue.txt.tmp cfg_queue.txt || exit 1
touch runs/$R/RESCUE_HANDLED
kill "$pid"
for i in $(seq 1 60); do pgrep -f "^bash $W/run_side[.]sh $R " > /dev/null || break; sleep 2; done
log "STOPPED $R (amendment 16): first SCF at a floor of 3e-5 to 2e-4 Ry after $its iterations (energy fixed to 0.1 mRy) at r4's step-46 trial geometry; rerun $N (FIRE, beta 0.05, ndim 20, conv_thr 5e-6) from r4's step-45 geometry and density, top of cfg_queue.txt"
for i in $(seq 1 24); do [ -d runs/$N ] && break; sleep 5; done
sleep 30
echo "pw=$(pgrep -x pw.x | wc -l)"; tail -3 queue.log | cut -c1-200
echo "$N: $(grep -a -c 'iteration #' runs/$N/$N.out 2>/dev/null) iterations; $(grep -a -m1 -i 'error\|initial density' runs/$N/$N.out)"
