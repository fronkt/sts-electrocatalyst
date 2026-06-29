#!/usr/bin/env bash
export PATH=/workspace/qe/env/bin:$PATH
export LD_LIBRARY_PATH=/workspace/qe/env/lib:$LD_LIBRARY_PATH
cd /workspace/qe/runs/Cr_slab || exit 1
echo "START $(date)"
for inp in H2.in H2O.in slab.in s0_OH.in s0_O.in s0_OOH.in; do
  [ -f "$inp" ] || continue
  out="${inp%.in}.out"
  if grep -q "JOB DONE" "$out" 2>/dev/null; then echo "skip $inp (done)"; continue; fi
  case "$inp" in H2.in|H2O.in) nk=1;; *) nk=8;; esac
  echo "=== $inp (nk=$nk) $(date +%H:%M:%S) ==="
  t0=$(date +%s)
  mpirun --allow-run-as-root -np 16 pw.x -nk $nk -in "$inp" > "$out" 2>&1
  echo "  exit=$? JOB_DONE=$(grep -c "JOB DONE" "$out" 2>/dev/null) ions=$(grep -c "Final" "$out" 2>/dev/null) $(( $(date +%s)-t0 ))s"
done
echo "ALL_SLAB_DONE $(date)"
