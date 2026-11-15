#!/usr/bin/env bash
# Amendment 6, run once on the box. NiOOH__slab_r3 stopped at its 11th SCF (flat at 5.06-5.18e-6 Ry
# for 200 iterations against conv_thr 5e-6). Restart from its last geometry as NiOOH__slab_r4 with
# conv_thr 1e-5, on the cores of NiFeOOH__Ni1_OH (not a V1/V2 state; 19 min into its U=0 stage),
# which goes back to the end of the queue-5 list.
set -u
W=$HOME/film
cd "$W" || exit 1
R3=runs/NiOOH__slab_r3

# 1. r4 input; it may differ from r3 only in positions, prefix and conv_thr
python3 qe_restart_input.py "$R3/NiOOH__slab_r3.in" "$R3/NiOOH__slab_r3.out" inputs/NiOOH__slab_r4.in NiOOH__slab_r4 --conv-thr 1.0d-5 || exit 1
OTHER=$(diff "$R3/NiOOH__slab_r3.in" inputs/NiOOH__slab_r4.in | grep '^[<>]' | grep -v -E '^[<>] +(Ni|O|H) +[-0-9.]+ +[-0-9.]+ +[-0-9.]+ +[01] [01] [01]$')
echo "$OTHER"
if [ "$(echo "$OTHER" | grep -c .)" -ne 4 ] || ! echo "$OTHER" | grep -q "conv_thr = 1.0d-5" || ! echo "$OTHER" | grep -q "prefix = 'NiOOH__slab_r4'"; then
  echo "UNEXPECTED DIFF; not launching"; exit 1
fi
grep -q "upscale = 1.d0" inputs/NiOOH__slab_r4.in || { echo "NO UPSCALE; not launching"; exit 1; }

# 2. launch r4 first (briefly 216 ranks), so the queue cannot take the cores freed in step 3
setsid nohup bash "$W/run_side.sh" NiOOH__slab_r4 24 3 > /dev/null 2>&1 < /dev/null &
sleep 40
echo "pw.x ranks after r4 launch: $(pgrep -x pw.x | wc -l)"

# 3. stop NiFeOOH__Ni1_OH: its run_one subshell first (or it would fall through to a plain start)
D=$W/runs/NiFeOOH__Ni1_OH
for p in $(pgrep -x bash); do [ "$(readlink "/proc/$p/cwd")" = "$D" ] && kill "$p" && echo "stopped run_one $p"; done
for p in $(pgrep -x prterun; pgrep -x mpirun); do [ "$(readlink "/proc/$p/cwd")" = "$D" ] && kill "$p" && echo "stopped launcher $p"; done
sleep 15
echo "pw.x ranks after stop: $(pgrep -x pw.x | wc -l)"
mv "$D" "runs/_stopped_NiFeOOH__Ni1_OH_$(date -u +%H%M)"
echo NiFeOOH__Ni1_OH >> jobs5.txt
echo "STOPPED NiFeOOH__Ni1_OH (19 min into U=0 stage) for NiOOH__slab_r4; re-queued last (amendment 6) $(date -u +%FT%TZ)" >> queue.log
echo "NiOOH__slab_r4" > side.txt
tail -3 queue.log; tail -3 jobs5.txt
