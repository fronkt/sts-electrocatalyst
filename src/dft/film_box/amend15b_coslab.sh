#!/usr/bin/env bash
# Amendment 15b (2026-11-16 ~21:25Z; V2, before any V2 eta exists). Amendment 15's bootstrap SCF
# u0__CoOOH__slab_smear3 (MV 0.03 Ry, numerics only) converged in 79 iterations at 21:13Z (total
# magnetization 1.33 muB; density in keep/). The slab's registered relaxation starts from it:
# u0__CoOOH__slab_r2 = u0__CoOOH__slab's input (relax, MV 0.01, local-TF, beta 0.05, ndim 20,
# conv_thr 5e-6, its input geometry, since the slab finished no step) with
#   startingpot = 'file'   (smear3's density, staged in stage/)
#   upscale = 1.d0         (amendment 4; the slab's input lacked it, 12:48Z / amendment 13 notes)
# Amendment-9 rerun rule: u0__CoOOH__slab completed no SCF, so r2 replaces it. In rescue_watch.txt
# (kept density, automatic rerun on an SCF failure); top of co_queue.txt, so post_relax.sh launches it
# into the free slot and yield_co can stop it for V1 work.
#   DRY=1 bash amend15b_coslab.sh   (build the input in /tmp and show the diff; touch nothing)
set -u
W=$HOME/film; cd "$W" || exit 1
B=u0__CoOOH__slab A=u0__CoOOH__slab_smear3 N=u0__CoOOH__slab_r2
od=inputs; [ "${DRY:-0}" = 1 ] && od=/tmp
log() { echo "$* $(date -u +%FT%TZ)" >> "$W/queue.log"; }
{ [ -e runs/$N ] || [ -e stage/$N ] || grep -qx "$N" co_queue.txt; } && { echo "$N exists"; exit 1; }
grep -q "^KEPT $A: converged" queue.log || { echo "$A has no converged, kept density"; exit 1; }
[ "$(grep -a -c '^!' runs/$B/$B.out)" = 0 ] || { echo "$B completed an SCF; this script assumes it did not"; exit 1; }
k=keep/$A
sed -e "s/^\( *\)prefix = .*/\1prefix = '$N'/" \
    -e "s/^\( *\)mixing_mode = /\1startingpot = 'file'\n&/" \
    -e "s/^\( *\)ion_dynamics = 'bfgs'/&\n\1upscale = 1.d0/" inputs/$B.in > $od/$N.in || exit 1
ok=1
chk() { [ "$(grep -c "$2" "$1")" = 1 ] || { echo "CHECK FAILED: $1 lacks exactly one '$2'"; ok=0; }; }
for s in "prefix = '$N'" "calculation = 'relax'" "degauss = 0.01" "conv_thr = 5.0d-6" "upscale = 1.d0" \
         "startingpot = 'file'" "mixing_beta = 0.05" "mixing_ndim = 20" "ion_dynamics = 'bfgs'" "forc_conv_thr = 2.0d-3"; do
  chk $od/$N.in "$s"
done
for f in charge-density.hdf5 occup.txt paw.txt; do [ -f $k/$f ] || { echo "no kept $f"; ok=0; }; done
echo "== diff $B.in -> $N.in"
diff inputs/$B.in $od/$N.in
[ "$(sed -n '/^ATOMIC_POSITIONS/,$p' inputs/$B.in | md5sum)" = "$(sed -n '/^ATOMIC_POSITIONS/,$p' $od/$N.in | md5sum)" ] \
  && echo "   positions and k-points: identical to $B.in" || { echo "CHECK FAILED: positions differ"; ok=0; }
echo "   starting density: $k ($(stat -c '%y' $k/charge-density.hdf5 | cut -c1-19))"
[ "$ok" = 1 ] || { rm -f $od/$N.in; exit 1; }
[ "${DRY:-0}" = 1 ] && { echo "DRY: input in /tmp, nothing touched"; exit 0; }
mkdir -p stage/$N && cp -p $k/charge-density.hdf5 $k/occup.txt $k/paw.txt stage/$N/ || exit 1
echo $N >> rescue_watch.txt
{ echo $N; cat co_queue.txt; } > co_queue.txt.tmp && mv co_queue.txt.tmp co_queue.txt || exit 1
log "QUEUED $N (amendment 15b, V2): $B's registered relaxation (MV 0.01, upscale 1) from $A's density, top of co_queue.txt"
for i in $(seq 1 30); do [ -d runs/$N ] && break; sleep 5; done
sleep 20
echo "pw=$(pgrep -x pw.x | wc -l)"; tail -2 queue.log | cut -c1-200
echo "$N: $(grep -a -c 'iteration #' runs/$N/$N.out 2>/dev/null) iterations; $(grep -a -m1 -i 'error\|initial density' runs/$N/$N.out)"
