#!/usr/bin/env bash
# Amendment 19 (2026-11-17 02:05Z, before any eta existed): one diagnostic SCF that enters no
# criterion. Fe-site *OH at r7's step-3 trial geometry (the SCF that floored; r7's last printed
# block), from r7's step-2 kept density, with mixing_beta 0.02 in place of 0.05. Everything else is
# r7's input: local-TF, ndim 20, conv_thr 5e-6, MV 0.01 Ry, cutoffs, dipole correction,
# electron_maxstep, tprnfor. calculation = 'scf', so the &IONS namelist is dropped.
# Goes to the top of co_queue.txt: it takes the first 24 free cores after cfg_queue.txt's entries
# (V1 first), ahead of CoOOH's relaunches. Its name has no u0__ prefix, so v1done.sh does not count
# it as V1 work and film_pilot_readout.py never reads it.
#   DRY=1 bash diag19.sh   (build the input in /tmp and show the checks; touch nothing)
set -u
W=$HOME/film; cd "$W" || exit 1
P=u0__NiFeOOH__Fe0_OH_r7 N=diag19__NiFeOOH__Fe0_OH_r7s3
od=inputs; [ "${DRY:-0}" = 1 ] && od=/tmp
log() { echo "$* $(date -u +%FT%TZ)" >> "$W/queue.log"; }
{ [ -e runs/$N ] || [ -e stage/$N ] || grep -qx "$N" co_queue.txt cfg_queue.txt; } && { echo "$N exists"; exit 1; }
o=runs/$P/$P.out k=keep/$P
nb=$(grep -a -c '^!' "$o"); nblk=$(grep -a -c '^ATOMIC_POSITIONS' "$o")
[ "$nb" = 2 ] && [ "$nblk" = 2 ] || { echo "$P: $nb steps, $nblk blocks (expected 2 and 2)"; exit 1; }
python3 qe_restart_input.py runs/$P/$P.in "$o" $od/$N.in $N --conv-thr 5.0d-6 > /dev/null || exit 1
sed -i -e "s/calculation = 'relax'/calculation = 'scf'/" -e "s/mixing_beta = 0.05/mixing_beta = 0.02/" \
       -e '/^&IONS/,/^\//d' $od/$N.in
ok=1
chk() { [ "$(grep -c "$2" "$1")" = 1 ] || { echo "CHECK FAILED: $1 lacks exactly one '$2'"; ok=0; }; }
for s in "prefix = '$N'" "calculation = 'scf'" "conv_thr = 5.0d-6" "mixing_beta = 0.02" "mixing_ndim = 20" \
         "mixing_mode = 'local-TF'" "startingpot = 'file'" "tprnfor = .true." "electron_maxstep = 200"; do chk $od/$N.in "$s"; done
grep -q "^&IONS" $od/$N.in && { echo "CHECK FAILED: &IONS still present"; ok=0; }
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
print("   positions vs block 2 (r7's step-3 trial): max |dx| %.2e A; vs block 1 (r7's step-2 geometry): %.4f A"
      % (dx(blocks[1]), dx(blocks[0])))
EOF
echo "   kept density: $(stat -c '%y' $k/charge-density.hdf5 | cut -c1-19); $P step 2: E $(grep -a '^!' "$o" | tail -1 | awk '{print $5}') Ry"
[ "$ok" = 1 ] || { rm -f $od/$N.in; exit 1; }
[ "${DRY:-0}" = 1 ] && { echo "DRY: input in /tmp, nothing touched"; exit 0; }
mkdir -p stage/$N && cp -p $k/charge-density.hdf5 $k/occup.txt $k/paw.txt stage/$N/ || exit 1
{ echo $N; cat co_queue.txt; } > co_queue.txt.tmp && mv co_queue.txt.tmp co_queue.txt || exit 1
log "DIAG19 queued $N (amendment 19, enters no criterion): SCF at $P's step-3 trial geometry from its step-2 density, mixing_beta 0.02; top of co_queue.txt"
