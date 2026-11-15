#!/usr/bin/env bash
# Spend guard (amendment 8): at the epoch in ~/film/DEADLINE, stop every run on the box. The idle
# watchdog then packages the outputs (30 min with no pw.x), the local loop pulls them, and the box
# shuts down. The file is re-read every 5 min, so writing a later epoch to it extends the run.
#   echo $(date -u -d 2026-11-16T08:00:00Z +%s) > ~/film/DEADLINE
#   setsid nohup bash deadline.sh > /dev/null 2>&1 < /dev/null &
set -u
W=$HOME/film
while true; do
  [ -f "$W/RUN_DONE" ] && exit 0
  dl=$(cat "$W/DEADLINE" 2>/dev/null || echo 0)
  if [ "$dl" -gt 0 ] && [ "$(date +%s)" -ge "$dl" ]; then
    echo "DEADLINE reached ($(date -u -d @"$dl" +%FT%TZ)); stopping every run $(date -u +%FT%TZ)" >> "$W/queue.log"
    # job shells first (a queue subshell would otherwise move on to a fallback start), then launchers
    for p in $(pgrep -x bash); do
      case "$(readlink "/proc/$p/cwd")" in "$W"/runs/*) kill "$p" ;; esac
    done
    for p in $(pgrep -x prterun; pgrep -x mpirun); do
      case "$(readlink "/proc/$p/cwd")" in "$W"/runs/*) kill "$p" ;; esac
    done
    sleep 30
    pkill -x pw.x
    touch "$W/DEADLINE_HIT"
    exit 0
  fi
  sleep 300
done
