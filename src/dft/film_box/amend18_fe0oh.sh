#!/usr/bin/env bash
# Amendment 18 (2026-11-17 ~00:15Z, before any eta existed). Restart a stalled FIRE relaxation of
# Fe-site *OH from its last completed SCF, as amendment 16 did for r4 -> r6. The new run P -> N:
#   - P's last completed geometry (step nb; P is in step nb+1's SCF) and its density (keep/P, written
#     at step nb's '!');
#   - P's input otherwise: FIRE, mixing_beta 0.05, mixing_ndim 20, conv_thr 5e-6, upscale 1,
#     startingpot 'file'; same model, cutoffs, smearing, dipole correction, forc_conv_thr 2e-3.
# A FIRE restart starts with zero velocity and the initial time step, so its first move is much
# smaller than P's accelerated step nb+1. That is the step whose SCF stalled.
# P is stopped with RESCUE_HANDLED first, so post_relax.sh's automatic rerun at P's trial geometry
# (where r5's SCF floored, amendment 16) does not follow. N is in cfg_watch.txt and rescue_watch.txt and
# goes to the top of cfg_queue.txt with its density staged. Amendment-9 rerun rule: N replaces P
# if its first energy, at P's step-nb geometry, is at most 1 mRy above P's step-nb energy.
# Needs nb >= 2: from nb = 1 a restart would repeat P's first FIRE move exactly.
#   P=RUN N=NEW DRY=1 bash amend18_fe0oh.sh   (build the input in /tmp and show the checks; touch nothing)
set -u
W=$HOME/film; cd "$W" || exit 1
P=${P:?} N=${N:?}
od=inputs; [ "${DRY:-0}" = 1 ] && od=/tmp
log() { echo "$* $(date -u +%FT%TZ)" >> "$W/queue.log"; }
{ [ -e runs/$N ] || [ -e stage/$N ] || grep -qx "$N" cfg_queue.txt; } && { echo "$N exists"; exit 1; }
o=runs/$P/$P.out k=keep/$P
nb=$(grep -a -c '^!' "$o"); nblk=$(grep -a -c '^ATOMIC_POSITIONS' "$o")
# P started from its input geometry and prints block j after step j: in step nb+1's SCF it has nb
# blocks, the last being step nb+1's trial geometry and block nb-1 step nb's geometry
[ "$nb" -ge 2 ] && [ "$nblk" = "$nb" ] || { echo "$P: $nb steps, $nblk geometry blocks: no restart"; exit 1; }
L=$(grep -a -n '^ATOMIC_POSITIONS' "$o" | tail -1 | cut -d: -f1)
head -n $((L - 1)) "$o" > /tmp/${P}_done.out   # its last block is then step nb's geometry
python3 qe_restart_input.py runs/$P/$P.in /tmp/${P}_done.out $od/$N.in $N --conv-thr 5.0d-6 --upscale 1.d0 > /dev/null || exit 1
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
print("   positions vs block %d (the last completed step's geometry): max |dx| %.2e A; vs block %d (the stalled trial): %.4f A"
      % (len(blocks) - 1, dx(blocks[-2]), len(blocks), dx(blocks[-1])))
EOF
its=$(tail -n +$(( $(grep -a -n '^!' "$o" | tail -1 | cut -d: -f1) + 1 )) "$o" | grep -a -c 'iteration #')
echo "   kept density: $(stat -c '%y' $k/charge-density.hdf5 | cut -c1-19); $P step $nb: E $(grep -a '^!' "$o" | tail -1 | awk '{print $5}') Ry; step $((nb + 1))'s SCF at $its iterations"
[ "$ok" = 1 ] || { rm -f $od/$N.in; exit 1; }
[ "${DRY:-0}" = 1 ] && { echo "DRY: input in /tmp, nothing touched"; exit 0; }
pid=$(pgrep -f "^prterun --bind-to none -np [0-9]+ pw[.]x -nk [0-9]+ -in $P[.]in$" | head -1)
[ -n "$pid" ] || { echo "no prterun for $P"; rm -f $od/$N.in; exit 1; }
mkdir -p stage/$N && cp -p $k/charge-density.hdf5 $k/occup.txt $k/paw.txt stage/$N/ || exit 1
echo $N >> rescue_watch.txt
echo $N >> cfg_watch.txt
{ echo $N; cat cfg_queue.txt; } > cfg_queue.txt.tmp && mv cfg_queue.txt.tmp cfg_queue.txt || exit 1
touch runs/$P/RESCUE_HANDLED
kill "$pid"
for i in $(seq 1 60); do pgrep -f "^bash $W/run_side[.]sh $P " > /dev/null || break; sleep 2; done
log "STOPPED $P (amendment 18): step $((nb + 1))'s SCF at $its iterations; rerun $N (FIRE restart, same parameters) from step $nb's geometry and density, top of cfg_queue.txt"
