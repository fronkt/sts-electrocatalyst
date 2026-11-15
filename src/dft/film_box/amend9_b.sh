#!/usr/bin/env bash
# Amendment 9, run once on the box. Frank chose B: the pilot runs at U = 0 (PBE, spin-polarized).
# 1. Stop NiOOH__Ni0_OH_r2 (PBE+U, no longer needed) and u0__NiOOH__Ni0_O, whose first SCF has sat
#    at 2.4-3.5e-4 Ry for ~60 iterations (146 of 200).
# 2. u0__NiOOH__Ni0_O_r2: the same input and geometry, started from the converged U = 0 density at
#    that geometry (NiOOH__Ni0_O_r2's U-ramp stage: -5173.76319 Ry, every non-site Ni parallel),
#    copied into its own tmp. Its first energy must reproduce that value.
# 3. CoOOH at U = 0 (V2): slab from the slab_r2 input (beta 0.05, ndim 20); Co-site *O, *OH, *OOH
#    from their PBE+U runs' last geometries; cold start, Co 0.05.
# 4. One launcher after the amendment-8b queue exits: Ni0_O_r2 first (V1), then CoOOH. Never starts
#    a run after the DEADLINE (side_queue.sh).
set -u
W=$HOME/film
cd "$W" || exit 1
log() { echo "$* $(date -u +%FT%TZ)" >> "$W/queue.log"; }

# 2a. check the saved density before stopping anything
S=$W/runs/NiOOH__Ni0_O_r2/tmp/NiOOH__Ni0_O_r2.save
u=$(grep -o 'label="3d">[^<]*' "$S/data-file-schema.xml" | head -1 | cut -d'>' -f2)
python3 -c "import sys; sys.exit(0 if abs(float('$u')) < 1e-6 else 1)" || { echo "saved density has U = $u, not the U = 0 stage; not launching"; exit 1; }
e=$(grep -o '<etot>[^<]*' "$S/data-file-schema.xml" | cut -d'>' -f2)
echo "saved density: U = $u Ry, etot = $e Ha"
d=$(diff <(sed -n '/^ATOMIC_POSITIONS/,$p' runs/NiOOH__Ni0_O_r2/NiOOH__Ni0_O_r2_u0.in) <(sed -n '/^ATOMIC_POSITIONS/,$p' inputs/u0__NiOOH__Ni0_O.in) | grep -c '^[<>]')
[ "$d" -eq 0 ] || { echo "u0__NiOOH__Ni0_O geometry differs from the U = 0 stage's; not launching"; exit 1; }

# 1. stop two runs: job shell first, then the launcher
for n in NiOOH__Ni0_OH_r2 u0__NiOOH__Ni0_O; do
  D=$W/runs/$n
  for p in $(pgrep -x bash); do [ "$(readlink "/proc/$p/cwd")" = "$D" ] && kill "$p" && echo "stopped job shell $p ($n)"; done
  for p in $(pgrep -x prterun; pgrep -x mpirun); do [ "$(readlink "/proc/$p/cwd")" = "$D" ] && kill "$p" && echo "stopped launcher $p ($n)"; done
done
sleep 20
echo "pw.x ranks after stop: $(pgrep -x pw.x | wc -l)"

# 2b. input and density for u0__NiOOH__Ni0_O_r2
N=u0__NiOOH__Ni0_O_r2
sed -e "s/prefix = 'u0__NiOOH__Ni0_O'/prefix = '$N'/" -e "s/^&ELECTRONS$/\&ELECTRONS\n  startingpot = 'file'/" \
  inputs/u0__NiOOH__Ni0_O.in > "inputs/$N.in"
d=$(diff inputs/u0__NiOOH__Ni0_O.in "inputs/$N.in" | grep -c '^[<>]')
[ "$d" -eq 3 ] && grep -q "startingpot = 'file'" "inputs/$N.in" || { echo "$N input differs in more than prefix + startingpot; not launching"; exit 1; }
mkdir -p "runs/$N/tmp/$N.save"
cp "$S"/charge-density.hdf5 "$S"/data-file-schema.xml "$S"/paw.txt "$S"/occup.txt "$S"/*.UPF "runs/$N/tmp/$N.save/" || exit 1

# 3. CoOOH inputs
python3 make_variant.py inputs/CoOOH__slab_r2.in inputs/u0__CoOOH__slab.in u0__CoOOH__slab --u0 --conv-thr 5.0d-6 || exit 1
for s in O OH OOH; do
  r=CoOOH__Co0_$s
  python3 qe_restart_input.py "runs/$r/$r.in" "runs/$r/$r.out" "/tmp/${r}_last.in" x > /dev/null || exit 1
  python3 make_variant.py "/tmp/${r}_last.in" "inputs/u0__$r.in" "u0__$r" --u0 --conv-thr 5.0d-6 || exit 1
done
grep -c "tot_magnetization" inputs/u0__CoOOH__*.in

# 4. launcher
printf '%s\n' "$N" u0__CoOOH__slab u0__CoOOH__Co0_O u0__CoOOH__Co0_OH u0__CoOOH__Co0_OOH > side_queue_b.txt
q=$(pgrep -f "side_queue.sh side_queue.txt" | head -1)
echo "amendment-8b queue pid: ${q:-none}"
setsid nohup bash -c "while [ -n '$q' ] && kill -0 '$q' 2>/dev/null; do sleep 20; done; exec bash $W/side_queue.sh side_queue_b.txt 24" > /dev/null 2>&1 < /dev/null &
printf '%s\n' u0__NiOOH__slab u0__NiFeOOH__slab "$N" u0__NiOOH__Ni0_OH u0__NiOOH__Ni0_OOH u0__NiFeOOH__Fe0_O \
  u0__NiFeOOH__Fe0_OH u0__NiFeOOH__Fe0_OOH u0__CoOOH__slab u0__CoOOH__Co0_O u0__CoOOH__Co0_OH u0__CoOOH__Co0_OOH > side.txt
log "AMENDMENT 9 (B, U = 0): STOPPED NiOOH__Ni0_OH_r2 (PBE+U, not needed) and u0__NiOOH__Ni0_O (first SCF flat at 2.4-3.5e-4 Ry, 146/200 iterations). Queued after side_queue.txt: $N (from the converged U = 0 density at its geometry), u0__CoOOH__slab, u0__CoOOH__Co0_O, u0__CoOOH__Co0_OH, u0__CoOOH__Co0_OOH"
sleep 240
echo "pw.x ranks: $(pgrep -x pw.x | wc -l)"
tail -4 queue.log
for n in u0__NiFeOOH__Fe0_OH "$N"; do
  f=runs/$n/$n.out
  [ -f "$f" ] || { echo "== $n not started"; continue; }
  echo "== $n: $(grep -a -c Error "$f") errors"
  grep -a -m1 "initial density\|Initial potential" "$f"
  grep -a -A7 "Starting magnetic structure" "$f" | tail -6
done
