#!/usr/bin/env bash
# Amendment 8b, run once on the box. The A-path tests answered: NiOOH *O at PBE+U does not converge
# from a low-spin cold start either (SCF error 0.17-5 Ry over 150 iterations), and *OOH converges
# with two Ni flipped (inconsistent with the all-parallel slab). Stop both. Provisional U = 0
# relaxations of the six V1 adslab states, each started in its film's U = 0 slab configuration:
#   NiOOH: all Ni parallel (u0__NiOOH__slab); Ni(Fe)OOH: Ni 5, 29, 30 antiparallel
#   (u0__NiFeOOH__slab, the same pattern its *OOH shows at U = 0 and at PBE+U).
# Three start now on the freed cores; three start as cores free up (side_queue.sh), never after
# the DEADLINE.
set -u
W=$HOME/film
cd "$W" || exit 1
log() { echo "$* $(date -u +%FT%TZ)" >> "$W/queue.log"; }

# 1. stop the two A-path adslab tests
for n in NiOOH__Ni0_O_r3 NiOOH__Ni0_OOH_r3; do
  D=$W/runs/$n
  for p in $(pgrep -x bash); do [ "$(readlink "/proc/$p/cwd")" = "$D" ] && kill "$p" && echo "stopped job shell $p ($n)"; done
  for p in $(pgrep -x prterun; pgrep -x mpirun); do [ "$(readlink "/proc/$p/cwd")" = "$D" ] && kill "$p" && echo "stopped launcher $p ($n)"; done
done
sleep 20
echo "pw.x ranks after stop: $(pgrep -x pw.x | wc -l)"
log "STOPPED NiOOH__Ni0_O_r3 (PBE+U SCF 0.17-5 Ry after 150 iterations), NiOOH__Ni0_OOH_r3 (Ni 5, 29 flipped) (amendment 8b). NiFeOOH__Fe0_OH stopped itself 16:57Z (7th SCF at 5.6-6.4e-6 vs 5e-6)"

# 2. inputs (U = 1e-8, cold start, conv_thr 5e-6)
mk_ni() {  # name, source input
  python3 make_variant.py "$2" "inputs/$1.in" "$1" --u0 --conv-thr 5.0d-6 || exit 1
}
mk_fe() {  # name, source input: Ni 5, 29, 30 relabelled Ni2 with a negative start
  python3 make_magdiag.py "$2" "/tmp/$1_lab.in" x --relabel 5,29,30:Ni2:-0.1 > /dev/null || exit 1
  python3 make_variant.py "/tmp/$1_lab.in" "inputs/$1.in" "$1" --calc relax --u0 --conv-thr 5.0d-6 || exit 1
}
last() {  # run dir name -> /tmp/<run>_last.in from its last printed geometry
  python3 qe_restart_input.py "runs/$1/$1.in" "runs/$1/$1.out" "/tmp/$1_last.in" x > /dev/null || exit 1
}
last NiFeOOH__Fe0_O; last NiFeOOH__Fe0_OOH_r2; last NiFeOOH__Fe0_OH; last NiOOH__Ni0_OH_r2
mk_ni u0__NiOOH__Ni0_O runs/NiOOH__Ni0_O_r2/NiOOH__Ni0_O_r2.in
mk_ni u0__NiOOH__Ni0_OOH runs/NiOOH__Ni0_OOH_r2/NiOOH__Ni0_OOH_r2.in
mk_ni u0__NiOOH__Ni0_OH /tmp/NiOOH__Ni0_OH_r2_last.in
mk_fe u0__NiFeOOH__Fe0_O /tmp/NiFeOOH__Fe0_O_last.in
mk_fe u0__NiFeOOH__Fe0_OOH /tmp/NiFeOOH__Fe0_OOH_r2_last.in
mk_fe u0__NiFeOOH__Fe0_OH /tmp/NiFeOOH__Fe0_OH_last.in
for n in u0__NiFeOOH__Fe0_O u0__NiFeOOH__Fe0_OOH u0__NiFeOOH__Fe0_OH; do
  for a in 5 29 30; do
    sed -n '/^ATOMIC_POSITIONS/,$p' "inputs/$n.in" | sed -n "$((a + 1))p" | grep -q '^ *Ni2 ' || { echo "$n atom $a is not Ni2; not launching"; exit 1; }
  done
done

# 3. launch three now, queue three
for n in u0__NiOOH__Ni0_O u0__NiFeOOH__Fe0_O u0__NiFeOOH__Fe0_OOH; do
  setsid nohup bash "$W/run_side.sh" "$n" 24 3 > /dev/null 2>&1 < /dev/null &
  sleep 2
done
printf '%s\n' u0__NiOOH__Ni0_OH u0__NiOOH__Ni0_OOH u0__NiFeOOH__Fe0_OH > side_queue.txt
setsid nohup bash "$W/side_queue.sh" side_queue.txt 24 > /dev/null 2>&1 < /dev/null &
log "PROVISIONAL U=0 adslabs (amendment 8b): started u0__NiOOH__Ni0_O u0__NiFeOOH__Fe0_O u0__NiFeOOH__Fe0_OOH; queued u0__NiOOH__Ni0_OH u0__NiOOH__Ni0_OOH u0__NiFeOOH__Fe0_OH"
printf '%s\n' NiOOH__slab_r5 u0__NiOOH__slab u0__NiFeOOH__slab u0__NiOOH__Ni0_O u0__NiFeOOH__Fe0_O u0__NiFeOOH__Fe0_OOH u0__NiOOH__Ni0_OH u0__NiOOH__Ni0_OOH u0__NiFeOOH__Fe0_OH > side.txt
sleep 60
echo "pw.x ranks: $(pgrep -x pw.x | wc -l)"
tail -3 queue.log
for n in u0__NiOOH__Ni0_O u0__NiFeOOH__Fe0_O u0__NiFeOOH__Fe0_OOH; do
  echo "== $n: $(grep -a -c Error runs/$n/$n.out) errors"; grep -a -A7 "Starting magnetic structure" runs/$n/$n.out | tail -6
  grep -a -m2 "Hubbard U\|U(" runs/$n/$n.out
done
