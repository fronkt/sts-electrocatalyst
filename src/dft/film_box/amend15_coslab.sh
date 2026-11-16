#!/usr/bin/env bash
# Amendment 15 (2026-11-16 ~20:20Z; V2, before any V2 eta exists). u0__CoOOH__slab's cold SCF
# (Co 0.05; local-TF, beta 0.05, ndim 20) finished no SCF by 12:48Z. From iteration 40 to 200 it sat
# at 5e-3 to 1e-2 Ry, with the energy steady to 0.4 mRy and the total moment at -0.20 to -0.26 muB.
# A steady energy with a residual that will not fall is the usual sign of fractional occupations
# flipping near the Fermi level. Larger smearing damps that.
# Test, in a 24-rank slot that is idle until the 22:00Z deadline: the same input as an SCF with MV
# smearing 0.03 Ry (registered: 0.01).
#   - numerics only: its density is a starting density for the registered relaxation
#     (startingpot = 'file', degauss 0.01), and its energy enters nothing;
#   - outdir in scratch/, so run_side.sh's rm -rf of the run's tmp/ cannot delete the density, and a
#     waiter copies the density into keep/ (pulled at the deadline) if the SCF converged;
#   - queued at the top of co_queue.txt, so post_relax.sh launches it and yield_co stops it first if
#     V1 work waits for cores.
#   DRY=1 bash amend15_coslab.sh   (build the input in /tmp and show the diff; touch nothing)
set -u
W=$HOME/film; cd "$W" || exit 1
B=u0__CoOOH__slab A=u0__CoOOH__slab_smear3
S=$W/scratch/$A
od=inputs; [ "${DRY:-0}" = 1 ] && od=/tmp
log() { echo "$* $(date -u +%FT%TZ)" >> "$W/queue.log"; }
{ [ -e runs/$A ] || [ -e "$S" ] || grep -qx "$A" co_queue.txt; } && { echo "$A exists"; exit 1; }
sed -e "s/^\( *\)calculation = .*/\1calculation = 'scf'/" \
    -e "s/^\( *\)prefix = .*/\1prefix = '$A'/" \
    -e "s|^\( *\)outdir = .*|\1outdir = '$S'|" \
    -e "s/^\( *\)degauss = .*/\1degauss = 0.03/" \
    -e '/^&IONS/,/^\//d' inputs/$B.in > $od/$A.in || exit 1
ok=1
chk() { [ "$(grep -c "$2" "$1")" = "$3" ] || { echo "CHECK FAILED: $1 has $(grep -c "$2" "$1") x '$2', want $3"; ok=0; }; }
for s in "calculation = 'scf'" "prefix = '$A'" "outdir = '$S'" "degauss = 0.03" "smearing = 'mv'" \
         "conv_thr = 5.0d-6" "mixing_beta = 0.05" "mixing_ndim = 20" "nspin = 2" "dipfield = .true."; do
  chk $od/$A.in "$s" 1
done
chk $od/$A.in "&IONS" 0
echo "== diff $B.in -> $A.in"
diff inputs/$B.in $od/$A.in
[ "$(sed -n '/^ATOMIC_POSITIONS/,$p' inputs/$B.in | md5sum)" = "$(sed -n '/^ATOMIC_POSITIONS/,$p' $od/$A.in | md5sum)" ] \
  && echo "   positions and k-points: identical to $B.in" || { echo "CHECK FAILED: positions differ"; ok=0; }
[ "$ok" = 1 ] || { rm -f $od/$A.in; exit 1; }
[ "${DRY:-0}" = 1 ] && { echo "DRY: input in /tmp, nothing touched"; exit 0; }
mkdir -p "$S"
{ echo $A; cat co_queue.txt; } > co_queue.txt.tmp && mv co_queue.txt.tmp co_queue.txt || exit 1
log "QUEUED $A (amendment 15, V2): $B's input as an SCF with MV 0.03 Ry, a starting density for its registered relaxation; outdir scratch/$A; top of co_queue.txt"
# waiter: after the SCF ends, copy its density into keep/ if it converged
setsid nohup bash -c '
  W='"$W"' A='"$A"' S='"$S"'
  log() { echo "$* $(date -u +%FT%TZ)" >> "$W/queue.log"; }
  for i in $(seq 1 720); do grep -q "^DONE $A " "$W/queue.log" && break; sleep 20; done
  o=$W/runs/$A/$A.out; s=$S/$A.save
  if grep -q "convergence has been achieved" "$o" 2>/dev/null && [ -f "$s/charge-density.hdf5" ]; then
    mkdir -p "$W/keep/$A" && for f in charge-density.hdf5 occup.txt paw.txt; do [ -f "$s/$f" ] && cp -p "$s/$f" "$W/keep/$A/"; done
    log "KEPT $A: converged in $(grep -a -c "iteration #" "$o") iterations, E $(grep -a "^!" "$o" | awk "{print \$5}") Ry (MV 0.03; numerics only), total magnetization $(grep -a "total magnetization" "$o" | tail -1 | awk "{print \$4}"); density in keep/$A"
  else
    log "NOT_KEPT $A: no converged SCF ($(grep -a -c "iteration #" "$o" 2>/dev/null) iterations)"
  fi' > /dev/null 2>&1 < /dev/null &
sleep 2
echo "queued; waiter $(pgrep -f "grep -q .\^DONE $A " | head -1)"; tail -1 queue.log | cut -c1-220; head -3 co_queue.txt
