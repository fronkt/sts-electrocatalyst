#!/usr/bin/env bash
# Start the side runs listed in a file, one at a time, as cores free up (amendment 8b). Never
# starts a run at or after the epoch in ~/film/DEADLINE, so the spend guard stays final.
#   setsid nohup bash side_queue.sh LIST [NP] > /dev/null 2>&1 < /dev/null &
set -u
W=$HOME/film
list=$1 np=${2:-24} maxcores=192
cd "$W" || exit 1
while read -r n; do
  [ -z "$n" ] && continue
  while true; do
    dl=$(cat "$W/DEADLINE" 2>/dev/null || echo 0)
    if [ -f "$W/DEADLINE_HIT" ] || { [ "$dl" -gt 0 ] && [ "$(date +%s)" -ge "$dl" ]; }; then
      echo "SIDE_QUEUE stopped at the deadline before $n $(date -u +%FT%TZ)" >> "$W/queue.log"; exit 0
    fi
    [ $(( $(pgrep -x pw.x | wc -l) + np )) -le "$maxcores" ] && break
    sleep 60
  done
  setsid nohup bash "$W/run_side.sh" "$n" "$np" 3 > /dev/null 2>&1 < /dev/null &
  sleep 90  # let the ranks appear before the next core count
done < "$list"
