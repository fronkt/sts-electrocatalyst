#!/usr/bin/env bash
# Amendment 8, run once on the box. The magnetic diagnostics show the NiOOH slab relaxation
# followed a metastable configuration (all-low-spin is 1.52 eV lower at the r4 start geometry),
# the Fe-site *O rerun sits in a solution >= 0.30 eV above the original's, and the Fe-site *OOH
# rerun has three flipped Ni. Those three runs are not usable under any fix and are stopped.
# Their cores go to provisional runs for both fixes under consideration (nothing is evaluated
# until the fix is registered):
#   A (PBE+U, low-spin start): NiOOH__slab_r5 (= slab_magLS input as a relaxation),
#      NiOOH__Ni0_O_r3, NiOOH__Ni0_OOH_r3 (cold start, Ni 0.05, from the input geometry)
#   B (U = 0): u0__NiOOH__slab (r4 start geometry), u0__NiFeOOH__slab (slab_r2 final geometry)
# Then a spend guard: every run stops at 2026-11-16T08:00Z unless DEADLINE is extended.
set -u
W=$HOME/film
cd "$W" || exit 1
log() { echo "$* $(date -u +%FT%TZ)" >> "$W/queue.log"; }

# 1. stop three runs: job shell first, then the launcher
for n in NiOOH__slab_r4 NiFeOOH__Fe0_O_r2 NiFeOOH__Fe0_OOH_r2; do
  D=$W/runs/$n
  for p in $(pgrep -x bash); do [ "$(readlink "/proc/$p/cwd")" = "$D" ] && kill "$p" && echo "stopped job shell $p ($n)"; done
  for p in $(pgrep -x prterun; pgrep -x mpirun); do [ "$(readlink "/proc/$p/cwd")" = "$D" ] && kill "$p" && echo "stopped launcher $p ($n)"; done
done
sleep 20
echo "pw.x ranks after stop: $(pgrep -x pw.x | wc -l)"
log "STOPPED NiOOH__slab_r4 (metastable, 1.52 eV above all-low-spin), NiFeOOH__Fe0_O_r2 (>=0.30 eV above the original's solution), NiFeOOH__Fe0_OOH_r2 (three flipped Ni) (amendment 8)"

# 2. inputs
python3 make_variant.py inputs/NiOOH__slab_r4.in inputs/NiOOH__slab_r5.in NiOOH__slab_r5 --species-mag 2=0.05 || exit 1
d=$(diff inputs/NiOOH__slab_magLS.in inputs/NiOOH__slab_r5.in | grep -c '^[<>]')
[ "$d" -eq 4 ] || { echo "slab_r5 differs from slab_magLS in more than calculation + prefix; not launching"; exit 1; }
for s in O OOH; do
  python3 make_variant.py "runs/NiOOH__Ni0_${s}_r2/NiOOH__Ni0_${s}_r2.in" "inputs/NiOOH__Ni0_${s}_r3.in" "NiOOH__Ni0_${s}_r3" --species-mag 2=0.05 || exit 1
done
python3 make_variant.py inputs/NiOOH__slab_r4.in inputs/u0__NiOOH__slab.in u0__NiOOH__slab --u0 --conv-thr 5.0d-6 || exit 1
python3 qe_restart_input.py runs/NiFeOOH__slab_r2/NiFeOOH__slab_r2.in runs/NiFeOOH__slab_r2/NiFeOOH__slab_r2.out /tmp/fe_slab_last.in x || exit 1
python3 make_variant.py /tmp/fe_slab_last.in inputs/u0__NiFeOOH__slab.in u0__NiFeOOH__slab --u0 || exit 1

# 3. launch on the 144 freed cores
setsid nohup bash "$W/run_side.sh" NiOOH__slab_r5 48 3 > /dev/null 2>&1 < /dev/null &
for n in NiOOH__Ni0_O_r3 NiOOH__Ni0_OOH_r3 u0__NiOOH__slab u0__NiFeOOH__slab; do
  sleep 2
  setsid nohup bash "$W/run_side.sh" "$n" 24 3 > /dev/null 2>&1 < /dev/null &
done
log "PROVISIONAL (amendment 8, pending the A/B choice): A NiOOH__slab_r5 NiOOH__Ni0_O_r3 NiOOH__Ni0_OOH_r3; B u0__NiOOH__slab u0__NiFeOOH__slab"
printf '%s\n' NiOOH__slab_r5 NiOOH__Ni0_O_r3 NiOOH__Ni0_OOH_r3 u0__NiOOH__slab u0__NiFeOOH__slab > side.txt
sleep 60
echo "pw.x ranks: $(pgrep -x pw.x | wc -l)"

# 4. spend guard
date -u -d 2026-11-16T08:00:00Z +%s > DEADLINE
pgrep -f deadline.sh > /dev/null || setsid nohup bash "$W/deadline.sh" > /dev/null 2>&1 < /dev/null &
sleep 2
pgrep -f deadline.sh > /dev/null && echo "deadline guard running (stops runs at $(date -u -d @"$(cat DEADLINE)" +%FT%TZ))" || echo "DEADLINE GUARD NOT RUNNING"
log "DEADLINE set to 2026-11-16T08:00:00Z (amendment 8 spend guard)"
pgrep -f box_watchdog.sh > /dev/null && echo "watchdog running" || echo "WATCHDOG NOT RUNNING"
tail -4 queue.log
for n in NiOOH__slab_r5 NiOOH__Ni0_O_r3 NiOOH__Ni0_OOH_r3 u0__NiOOH__slab u0__NiFeOOH__slab; do
  echo "== $n: $(grep -a -m1 -c Error runs/$n/$n.out) errors"; grep -a -A4 "Starting magnetic structure" runs/$n/$n.out | head -6
done
