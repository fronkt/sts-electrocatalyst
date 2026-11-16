#!/usr/bin/env bash
# Amendment 9 rerun of u0__NiFeOOH__Fe0_OH (first SCF flat at ~4e-5 Ry for 200 iterations, no SCF
# completed, density deleted by run_side.sh). Same input and geometry; startingpot='file' from the
# converged u0__NiFeOOH__slab density (C1, the pattern the original run was seeded with). Only the
# charge density is copied: occup.txt / paw.txt are per-atom and the slab has 48 atoms, not 50.
# Started next to the running jobs (24 extra ranks for a few minutes) so the read can be checked
# before the CoOOH slab is stopped.
set -u
W=$HOME/film; cd "$W" || exit 1
n=u0__NiFeOOH__Fe0_OH_r2 src=runs/u0__NiFeOOH__slab/tmp/u0__NiFeOOH__slab.save/charge-density.hdf5
[ -e "runs/$n" ] && { echo "runs/$n exists"; exit 1; }
age=$(( $(date +%s) - $(stat -c %Y "$src") )); [ "$age" -ge 60 ] || { echo "slab density written ${age}s ago; retry"; exit 1; }
sed -e "s/prefix = 'u0__NiFeOOH__Fe0_OH'/prefix = '$n'/" \
    -e "s/^\( *\)mixing_mode = 'local-TF'/\1startingpot = 'file'\n\1mixing_mode = 'local-TF'/" \
    runs/u0__NiFeOOH__Fe0_OH/u0__NiFeOOH__Fe0_OH.in > "inputs/$n.in"
grep -c "startingpot = 'file'" "inputs/$n.in" | grep -qx 1 || { echo "startingpot edit failed"; exit 1; }
grep -c "prefix = '$n'" "inputs/$n.in" | grep -qx 1 || { echo "prefix edit failed"; exit 1; }
mkdir -p "runs/$n/tmp/$n.save" && cp -p "$src" "runs/$n/tmp/$n.save/"
cmp -s "$src" "runs/$n/tmp/$n.save/charge-density.hdf5" || { echo "copy differs"; exit 1; }
diff runs/u0__NiFeOOH__Fe0_OH/u0__NiFeOOH__Fe0_OH.in "inputs/$n.in"
echo "rerun $n: startingpot=file from u0__NiFeOOH__slab density (slab step $(grep -a -c '^!' runs/u0__NiFeOOH__slab/u0__NiFeOOH__slab.out)); predecessor completed no SCF $(date -u +%FT%TZ)" >> queue.log
setsid nohup bash "$W/run_side.sh" "$n" 24 3 > /dev/null 2>&1 < /dev/null &
echo launched
