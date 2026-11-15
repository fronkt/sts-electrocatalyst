#!/usr/bin/env bash
# One line per job: BFGS energies, SCF iterations since the last energy, last accuracy, moment, force.
# Flags: STALL (>=120 iterations since the last energy), SCFFAIL, DONE (JOB DONE written).
cd ~/film/runs || exit 1
for d in */; do
  n=${d%/}; f=$n/$n.out; [ -f "$f" ] || continue
  case $n in gas*) continue;; esac
  awk -v n="$n" '
    /^!/ {e++; since=0}
    /total cpu time spent/ {since++}
    /estimated scf accuracy/ {acc=$5}
    /total magnetization/ {mag=$4}
    /Total force/ {force=$4}
    /convergence NOT achieved/ {fail=1}
    /JOB DONE/ {done=1}
    /End of BFGS/ {bfgs=1}
    END {
      flag = fail ? "SCFFAIL" : (done ? (bfgs ? "DONE" : "STOPPED") : (since >= 120 ? "STALL" : "run"))
      printf "%-20s %-8s steps=%-3d since=%-4d acc=%-11s mag=%-6s F=%s\n", n, flag, e, since, acc, mag, force
    }' "$f"
done
echo "pw.x=$(pgrep -x pw.x | wc -l) $(date -u +%FT%TZ)"
