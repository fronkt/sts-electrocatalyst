#!/usr/bin/env bash
# Amendment 11 (2026-11-16 08:32Z): post_relax.sh v4 (queues C1-C5 single points) and make_cfg_sp.sh
# with C5 (Fe -, Ni 30 -: where the clean slab's C2 single point landed). No run is stopped or
# requeued; the slab keeps its C1-C4 set (its C2 point stands as its C5 point).
set -u
W=$HOME/film; cd "$W" || exit 1
[ -f make_cfg_sp.sh.new ] && [ -f post_relax.sh.new ] || { echo "missing .new files"; exit 1; }
bash -n make_cfg_sp.sh.new && bash -n post_relax.sh.new || { echo "syntax"; exit 1; }
old=$(pgrep -f "^bash $W/post_relax[.]sh$")
[ "$(echo "$old" | grep -c .)" = 1 ] || { echo "expected one post_relax, got: $old"; exit 1; }
kill "$old"; sleep 1; kill -0 "$old" 2>/dev/null && { echo "old post_relax alive"; exit 1; }
cp -p make_cfg_sp.sh make_cfg_sp.sh.v3 && cp -p post_relax.sh post_relax.sh.v3
mv make_cfg_sp.sh.new make_cfg_sp.sh && mv post_relax.sh.new post_relax.sh || exit 1
echo "AMENDMENT 11: C5 (Fe -, Ni 30 -) added; single points count as the configuration they land in; post_relax v4 queues C1-C5 $(date -u +%FT%TZ)" >> queue.log
setsid nohup bash "$W/post_relax.sh" > /dev/null 2>&1 < /dev/null &
sleep 3
echo "post_relax: $(pgrep -f "^bash $W/post_relax[.]sh$")"; tail -3 queue.log; head -5 cfg_queue.txt
