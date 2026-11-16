#!/usr/bin/env bash
# Swap in post_relax.sh v2 (automatic SCF-failure reruns) and run_side.sh v2 (stage/ handling).
# Running run_side.sh instances keep their open copy; the rename only affects new launches.
set -u
W=$HOME/film; cd "$W" || exit 1
old=$(pgrep -f "^bash $W/post_relax[.]sh$")
[ "$(echo "$old" | grep -c .)" = 1 ] || { echo "expected one old post_relax, got: $old"; exit 1; }
kill "$old"; sleep 1
kill -0 "$old" 2>/dev/null && { echo "old post_relax $old still alive"; exit 1; }
mv run_side.sh.new run_side.sh && mv post_relax.sh.new post_relax.sh || exit 1
setsid nohup bash "$W/post_relax.sh" > /dev/null 2>&1 < /dev/null &
sleep 5
echo "old $old stopped; new: $(pgrep -f "^bash $W/post_relax[.]sh$")"
tail -2 queue.log
