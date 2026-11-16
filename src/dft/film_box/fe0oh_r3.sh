#!/usr/bin/env bash
# Amendment 9 rerun of u0__NiFeOOH__Fe0_OH (r2 stopped in read_scf: no occup.txt). Same input
# and geometry; startingpot='file' from the converged u0__NiFeOOH__slab save, with occup.txt and
# paw.txt mapped atom-by-atom onto the 50-atom adslab (map_restart.py). Started next to the
# running jobs so the read can be checked before the CoOOH slab is stopped.
set -u
W=$HOME/film; cd "$W" || exit 1
n=u0__NiFeOOH__Fe0_OH_r3 s=runs/u0__NiFeOOH__slab sv=runs/u0__NiFeOOH__slab/tmp/u0__NiFeOOH__slab.save
[ -e "runs/$n" ] && { echo "runs/$n exists"; exit 1; }
age=$(( $(date +%s) - $(stat -c %Y "$sv/charge-density.hdf5") )); [ "$age" -ge 60 ] || { echo "slab density written ${age}s ago; retry"; exit 1; }
sed -e "s/prefix = 'u0__NiFeOOH__Fe0_OH'/prefix = '$n'/" \
    -e "s/^\( *\)mixing_mode = 'local-TF'/\1startingpot = 'file'\n\1mixing_mode = 'local-TF'/" \
    runs/u0__NiFeOOH__Fe0_OH/u0__NiFeOOH__Fe0_OH.in > "inputs/$n.in"
[ "$(grep -c "startingpot = 'file'" "inputs/$n.in")" = 1 ] && [ "$(grep -c "prefix = '$n'" "inputs/$n.in")" = 1 ] || { echo "input edit failed"; exit 1; }
d=runs/$n/tmp/$n.save; mkdir -p "$d"
T=$(mktemp -d); cp -p "$sv/charge-density.hdf5" "$sv/occup.txt" "$sv/paw.txt" "$T/"
cp -p "$T/charge-density.hdf5" "$d/"
python3 map_restart.py "$s/u0__NiFeOOH__slab.in" "$s/u0__NiFeOOH__slab.out" "$T" "inputs/$n.in" "$d" || { echo "map failed"; rm -rf "runs/$n"; exit 1; }
echo "rerun $n: r2 stopped in read_scf (no occup.txt); startingpot=file from u0__NiFeOOH__slab save (step $(grep -a -c '^!' $s/u0__NiFeOOH__slab.out)), occup/paw mapped by map_restart.py $(date -u +%FT%TZ)" >> queue.log
setsid nohup bash "$W/run_side.sh" "$n" 24 3 > /dev/null 2>&1 < /dev/null &
echo launched
