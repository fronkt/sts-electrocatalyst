#!/usr/bin/env bash
# Amendment 10 (2026-11-16 ~04:20Z): post_relax.sh v3 (C4 single points; conv_thr 1e-5 for reruns at
# the noise floor), make_cfg_sp.sh with C4 and conv_thr 1e-5, and u0__NiOOH__Ni0_OOH_r3: r2's input
# and geometry (Ni0_OOH's step-8 geometry) with conv_thr 1e-5, from r2's starting density. r2 is
# stopped after r3 is queued at the top of cfg_queue.txt, so the freed cores go to r3.
set -u
W=$HOME/film; cd "$W" || exit 1
R2=u0__NiOOH__Ni0_OOH_r2 R3=u0__NiOOH__Ni0_OOH_r3
[ -e runs/$R3 ] || [ -e stage/$R3 ] && { echo "$R3 exists"; exit 1; }
sed -e "s/prefix = '$R2'/prefix = '$R3'/" -e "s/^\( *\)conv_thr = 5.0d-6/\1conv_thr = 1.0d-5/" runs/$R2/$R2.in > inputs/$R3.in
diff runs/$R2/$R2.in inputs/$R3.in
[ "$(diff runs/$R2/$R2.in inputs/$R3.in | grep -c '^[<>]')" = 4 ] || { echo "unexpected diff"; exit 1; }
mkdir -p stage/$R3 && cp -p keep/$R2/charge-density.hdf5 keep/$R2/occup.txt keep/$R2/paw.txt stage/$R3/ || exit 1
old=$(pgrep -f "^bash $W/post_relax[.]sh$")
[ "$(echo "$old" | grep -c .)" = 1 ] || { echo "expected one post_relax, got: $old"; exit 1; }
kill "$old"; sleep 1; kill -0 "$old" 2>/dev/null && { echo "old post_relax alive"; exit 1; }
mv make_cfg_sp.sh.new make_cfg_sp.sh && mv post_relax.sh.new post_relax.sh || exit 1
{ echo $R3; cat cfg_queue.txt; } > cfg_queue.tmp && mv cfg_queue.tmp cfg_queue.txt
echo $R3 >> rescue_watch.txt
echo "rerun $R3 (amendment 10): $R2 sat at 5.1-6.2e-6 Ry (energy within 0.003 mRy) after Ni0_OOH's 190 iterations at 5.3-8e-6 at the same geometry; conv_thr 1e-5, same geometry and density $(date -u +%FT%TZ)" >> queue.log
setsid nohup bash "$W/post_relax.sh" > /dev/null 2>&1 < /dev/null &
sleep 3
pid=$(pgrep -f "prterun .*-in $R2.in" | head -1); [ -n "$pid" ] && kill "$pid" && echo "stopped $R2"
sleep 15
echo "STOPPED $R2 (noise floor; amendment-10 rerun $R3 queued first) $(date -u +%FT%TZ)" >> queue.log
echo "post_relax: $(pgrep -f "^bash $W/post_relax[.]sh$")"; head -3 cfg_queue.txt; tail -5 queue.log
