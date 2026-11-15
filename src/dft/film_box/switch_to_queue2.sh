#!/usr/bin/env bash
# Amendment 3 switch-over, run once on the box:
#  1. stop the first queue's scheduling loop (its running jobs keep going as orphans),
#  2. stop the stuck NiOOH__slab job and write NiOOH__slab_r2.in from its last geometry,
#  3. loosen conv_thr to 5e-6 in every input whose job has not started,
#  4. start box_run2.sh with NiOOH__slab_r2 first, then the not-started jobs.
set -u
W=$HOME/film
cd "$W" || exit 1

# 1. parent box_run.sh = the box_run.sh process whose parent is not itself box_run.sh
for pid in $(ps -eo pid,args | awk '$2=="bash" && $3 ~ /box_run\.sh$/ {print $1}'); do
  ppid=$(ps -o ppid= -p "$pid" | tr -d ' ')
  if ! ps -o args= -p "$ppid" | grep -q "box_run\.sh"; then
    kill "$pid" && echo "stopped queue-1 loop $pid"
  fi
done
sleep 2

# 2. stuck NiOOH__slab (launcher runs as prterun)
for pid in $(ps -eo pid,comm | awk '$2 ~ /^(prterun|mpirun)$/ {print $1}'); do
  [ "$(readlink /proc/$pid/cwd)" = "$W/runs/NiOOH__slab" ] && kill "$pid" && echo "stopped NiOOH__slab launcher $pid"
done
sleep 8
python3 "$W/qe_restart_input.py" "$W/inputs/NiOOH__slab.in" "$W/runs/NiOOH__slab/NiOOH__slab.out" \
        "$W/inputs/NiOOH__slab_r2.in" NiOOH__slab_r2 --conv-thr 5.0d-6 || exit 2

# 3 + 4. not-started jobs (no runs/<name> directory yet), in manifest order
echo NiOOH__slab_r2 > "$W/jobs2.txt"
python3 - "$W/inputs/manifest.json" "$W/runs" >> "$W/jobs2.txt" <<'PY'
import json, os, sys
jobs = json.load(open(sys.argv[1]))["jobs"]
for j in sorted(jobs, key=lambda j: (j["kind"] != "gas", j["kind"] != "slab", j["name"])):
    if not os.path.isdir(os.path.join(sys.argv[2], j["name"])):
        print(j["name"])
PY
while read -r n; do
  [ "$n" = NiOOH__slab_r2 ] && continue
  sed -i 's/^  conv_thr = 1.0d-6$/  conv_thr = 5.0d-6/' "$W/inputs/$n.in"
done < "$W/jobs2.txt"
echo "queue2 jobs: $(tr '\n' ' ' < "$W/jobs2.txt")"
echo "conv_thr 5e-6 in: $(grep -l '^  conv_thr = 5.0d-6' inputs/*.in | wc -l) inputs"
setsid nohup bash "$W/box_run2.sh" > "$W/queue2.log" 2>&1 < /dev/null &
sleep 40
echo "pw.x ranks now: $(pgrep -x pw.x | wc -l)"; tail -3 "$W/queue.log"
