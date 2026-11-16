#!/usr/bin/env bash
# 2026-11-16 10:39Z: post_relax.sh v5. Waiting V1 work takes a running CoOOH run's cores (V1 before
# V2, as yield_co.sh did by hand at 01:03Z) while >= 75 min remain to the deadline. Sandbox-tested
# (yield of the later-started CoOOH run; no yield < 75 min before the deadline or with no V1 waiting).
set -u
W=$HOME/film; cd "$W" || exit 1
[ -f post_relax.sh.new ] && bash -n post_relax.sh.new || { echo "missing or bad post_relax.sh.new"; exit 1; }
old=$(pgrep -f "^bash $W/post_relax[.]sh$")
[ "$(echo "$old" | grep -c .)" = 1 ] || { echo "expected one post_relax, got: $old"; exit 1; }
kill "$old"; sleep 1; kill -0 "$old" 2>/dev/null && { echo "old post_relax alive"; exit 1; }
cp -p post_relax.sh post_relax.sh.v4 && mv post_relax.sh.new post_relax.sh || exit 1
setsid nohup bash "$W/post_relax.sh" > /dev/null 2>&1 < /dev/null &
sleep 3
echo "post_relax: $(pgrep -f "^bash $W/post_relax[.]sh$")"; tail -2 queue.log
