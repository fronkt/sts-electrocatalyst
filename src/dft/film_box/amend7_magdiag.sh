#!/usr/bin/env bash
# Amendment 7, run once on the box. Slab and adslab states of a film sit in different magnetic
# configurations (NiOOH slab: four middle-layer Ni at high moment, 20 muB total; its adslabs at
# 11-12 muB). Stop new launches; stop the two NiOOH Ni-site first SCFs that have stalled (no
# geometry yet) and NiFeOOH__Ni1_O (not a V1/V2 state); use their cores for two single points:
#   D1  NiOOH__slab_magLS   : NiOOH slab at the r4 start geometry, all Ni started low-spin (0.05)
#   D1b NiOOH__Ni0_OH_magHS : NiOOH *OH at Ni0_OH_r2's current geometry, the four middle Ni
#                             started high-spin (0.17), the rest as before (0.10)
# Each is compared with the same geometry's energy from the running relaxation (r4 step 1, and
# the next '!' of Ni0_OH_r2). Relaxations that are making geometry progress keep running.
set -u
W=$HOME/film
cd "$W" || exit 1

# 1. stop the queue-5 main shell (cwd = $W; its run_one subshells sit in runs/<job>)
for p in $(pgrep -f 'box_run3\.sh$'); do
  [ "$(readlink "/proc/$p/cwd")" = "$W" ] && kill "$p" && echo "stopped queue main shell $p"
done
# 2. stop three jobs: run_one subshell first, then the launcher
for n in NiOOH__Ni0_O_r2 NiOOH__Ni0_OOH_r2 NiFeOOH__Ni1_O; do
  D=$W/runs/$n
  for p in $(pgrep -x bash); do [ "$(readlink "/proc/$p/cwd")" = "$D" ] && kill "$p" && echo "stopped run_one $p ($n)"; done
  for p in $(pgrep -x prterun; pgrep -x mpirun); do [ "$(readlink "/proc/$p/cwd")" = "$D" ] && kill "$p" && echo "stopped launcher $p ($n)"; done
done
sleep 15
echo "pw.x ranks: $(pgrep -x pw.x | wc -l)"
echo "STOPPED queue-5 launches and NiOOH__Ni0_O_r2, NiOOH__Ni0_OOH_r2, NiFeOOH__Ni1_O (amendment 7: magnetic-configuration check) $(date -u +%FT%TZ)" >> queue.log

# 3. diagnostic inputs
python3 make_magdiag.py inputs/NiOOH__slab_r4.in inputs/NiOOH__slab_magLS.in NiOOH__slab_magLS --species-mag 2=0.05 || exit 1
O=runs/NiOOH__Ni0_OH_r2/NiOOH__Ni0_OH_r2.out
K=$(grep -c '^!' "$O")
python3 qe_restart_input.py runs/NiOOH__Ni0_OH_r2/NiOOH__Ni0_OH_r2.in "$O" /tmp/oh_last.in x || exit 1
python3 make_magdiag.py /tmp/oh_last.in inputs/NiOOH__Ni0_OH_magHS.in NiOOH__Ni0_OH_magHS --relabel 3,4,27,28:Ni2:0.17 || exit 1
echo "MAGDIAG pairs: NiOOH__slab_magLS <-> NiOOH__slab_r4 '!' #1; NiOOH__Ni0_OH_magHS <-> NiOOH__Ni0_OH_r2 '!' #$((K + 1)) $(date -u +%FT%TZ)" >> queue.log

# 4. launch (48 + 24 ranks on the 72 freed cores)
setsid nohup bash "$W/run_side.sh" NiOOH__slab_magLS 48 3 > /dev/null 2>&1 < /dev/null &
setsid nohup bash "$W/run_side.sh" NiOOH__Ni0_OH_magHS 24 3 > /dev/null 2>&1 < /dev/null &
sleep 60
echo "pw.x ranks: $(pgrep -x pw.x | wc -l)"
printf '%s\n' NiOOH__slab_r4 NiOOH__slab_magLS NiOOH__Ni0_OH_magHS > side.txt
pgrep -f box_watchdog.sh > /dev/null && echo "watchdog running" || echo "WATCHDOG NOT RUNNING"
tail -4 queue.log
for n in NiOOH__slab_magLS NiOOH__Ni0_OH_magHS; do grep -a -m3 -E "Error|starting magnetization|Hubbard U" runs/$n/$n.out; done
