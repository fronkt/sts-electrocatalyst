#!/usr/bin/env bash
# Amendment 9 reruns, 2026-11-16 ~03:20Z.
#  - u0__NiOOH__slab: step-26 SCF flat at 4e-5..1.5e-3 Ry for 173 iterations (conv_thr 5e-6).
#    -> u0__NiOOH__slab_r2 from its last geometry, startingpot='file' from its own step-25 density
#       (hardlinked to keep/ before run_side.sh could delete it). Same atoms, nothing mapped.
#  - u0__NiFeOOH__Fe0_OH_r3 (mapped slab density) started 93 Ry low with large negative rho and was at
#    6.5 Ry after 108 iterations. -> u0__NiFeOOH__Fe0_OH_r4: the original input and geometry,
#    startingpot='file' from the PBE+U NiFeOOH__Fe0_OH save (same 50 atoms, step-6 density).
# Reruns start first (briefly 240 ranks) so post_relax.sh cannot take the cores freed after.
set -u
W=$HOME/film; cd "$W" || exit 1
addpot() { sed -i "s/^\( *\)mixing_mode = 'local-TF'/\1startingpot = 'file'\n\1mixing_mode = 'local-TF'/" "$1"; [ "$(grep -c "startingpot = 'file'" "$1")" = 1 ]; }
stage() { # name srcdir
  local d=runs/$1/tmp/$1.save; mkdir -p "$d" && cp -p "$2"/charge-density.hdf5 "$2"/occup.txt "$2"/paw.txt "$d/"; }
A=u0__NiOOH__slab_r2 F=u0__NiFeOOH__Fe0_OH_r4
for n in $A $F; do [ -e runs/$n ] && { echo "runs/$n exists"; exit 1; }; done
# A: last geometry + own density
python3 qe_restart_input.py runs/u0__NiOOH__slab/u0__NiOOH__slab.in runs/u0__NiOOH__slab/u0__NiOOH__slab.out inputs/$A.in $A || exit 1
addpot inputs/$A.in || { echo "A startingpot edit failed"; exit 1; }
diff runs/u0__NiOOH__slab/u0__NiOOH__slab.in inputs/$A.in | grep '^[<>]' | grep -v -E '^[<>] +(Ni|O|H) +[-0-9.]+ +[-0-9.]+ +[-0-9.]+ +[01] [01] [01]$'
# F: original input + PBE+U density (check same atom count and identical geometry)
P=runs/NiFeOOH__Fe0_OH/tmp/NiFeOOH__Fe0_OH.save
[ "$(tr -s ' ' '\n' < $P/occup.txt | grep -c .)" = 2500 ] || { echo "PBE+U occup size"; exit 1; }
[ "$(tr -s ' ' '\n' < $P/paw.txt | grep -c .)" = 17100 ] || { echo "PBE+U paw size"; exit 1; }
sed -e "s/prefix = 'u0__NiFeOOH__Fe0_OH'/prefix = '$F'/" runs/u0__NiFeOOH__Fe0_OH/u0__NiFeOOH__Fe0_OH.in > inputs/$F.in
addpot inputs/$F.in || { echo "F startingpot edit failed"; exit 1; }
diff runs/u0__NiFeOOH__Fe0_OH/u0__NiFeOOH__Fe0_OH.in inputs/$F.in
stage $A keep/u0__NiOOH__slab && stage $F $P || { echo "staging failed"; exit 1; }
cmp keep/u0__NiOOH__slab/charge-density.hdf5 runs/$A/tmp/$A.save/charge-density.hdf5 && cmp $P/paw.txt runs/$F/tmp/$F.save/paw.txt || exit 1
echo "rerun $A: u0__NiOOH__slab step-26 SCF flat (4e-5..1.5e-3 Ry, 173 it); last geometry, startingpot=file from its step-25 density $(date -u +%FT%TZ)" >> queue.log
echo "rerun $F: r3 (mapped slab density) started 93 Ry low, 6.5 Ry after 108 it; original geometry, startingpot=file from the PBE+U NiFeOOH__Fe0_OH save $(date -u +%FT%TZ)" >> queue.log
for n in $A $F; do setsid nohup bash "$W/run_side.sh" "$n" 24 3 > /dev/null 2>&1 < /dev/null & done
sleep 30
for n in u0__NiOOH__slab u0__NiFeOOH__Fe0_OH_r3; do
  pid=$(pgrep -f "prterun .*-in $n.in" | head -1); [ -n "$pid" ] && kill "$pid" && echo "stopped $n"
done
sleep 20
for n in u0__NiOOH__slab u0__NiFeOOH__Fe0_OH_r3; do echo "STOPPED $n (SCF not converging; rerun started) $(date -u +%FT%TZ)" >> queue.log; done
grep -qx $F cfg_watch.txt || echo $F >> cfg_watch.txt
echo "pw=$(pgrep -x pw.x | wc -l)"; tail -8 queue.log; cat cfg_watch.txt
