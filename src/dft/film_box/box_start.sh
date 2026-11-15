#!/usr/bin/env bash
# Film-DFT pilot, on the AWS box: install QE 7.5, start the watchdog, run the queue.
# Launched detached by aws_launch.sh:  cd ~/film; setsid nohup bash box_start.sh > start.log 2>&1 < /dev/null &
set -u
W=$HOME/film
cd "$W"
echo "START $(date -u +%FT%TZ) nproc=$(nproc) mem=$(free -g | awk '/Mem/{print $2}')G"
command -v bzip2 >/dev/null || { sudo apt-get update -qq && sudo apt-get install -y -qq bzip2 >/dev/null; }
if [ ! -x "$W/qe/env/bin/pw.x" ]; then
  [ -x "$W/bin/micromamba" ] || curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xj bin/micromamba
  "$W/bin/micromamba" create -y -q -p "$W/qe/env" -c conda-forge qe=7.5 >/dev/null
fi
if [ ! -x "$W/qe/env/bin/pw.x" ]; then
  echo "SETUP_FAILED $(date -u +%FT%TZ)"; touch "$W/RUN_STALLED"; exit 1
fi
echo "SETUP_DONE $(date -u +%FT%TZ) $("$W/qe/env/bin/pw.x" -h 2>&1 | head -0)"
setsid nohup bash "$W/box_watchdog.sh" > "$W/watchdog.log" 2>&1 < /dev/null &
bash "$W/box_run.sh"
