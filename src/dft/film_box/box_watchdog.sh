#!/usr/bin/env bash
# Idle watchdog: if no pw.x has run for 30 min and the queue has not finished, package what
# exists, touch RUN_STALLED, wait up to 3 h for PULLED, then shut down (instance STOPS).
set -u
W=$HOME/film
idle=0
while true; do
  [ -f "$W/RUN_DONE" ] && exit 0
  if pgrep -x pw.x > /dev/null; then idle=0; else idle=$((idle + 1)); fi
  if [ "$idle" -ge 6 ]; then
    echo "STALLED $(date -u +%FT%TZ)"
    cd "$W" && tar czf out.tgz --exclude='*/tmp' runs queue.log start.log watchdog.log inputs/manifest.json 2>/dev/null
    md5sum out.tgz > out.tgz.md5
    touch "$W/RUN_STALLED"
    for _ in $(seq 1 180); do [ -f "$W/PULLED" ] && break; sleep 60; done
    sudo shutdown -h now
    exit 0
  fi
  sleep 300
done
