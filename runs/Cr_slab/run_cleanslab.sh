#!/usr/bin/env bash
# Run the clean CrO2(110) slab alone on all 32 cores, AFTER both adslabs finish,
# so it is not starved. nosym + local-TF mixing already baked into slab.in.
cd /workspace/qe/runs/Cr_slab
export PATH=/workspace/qe/env/bin:$PATH
export LD_LIBRARY_PATH=/workspace/qe/env/lib:$LD_LIBRARY_PATH
export OMP_NUM_THREADS=1
echo "WAIT_FOR_ADSLABS $(date -u)" >> cleanslab.log
while true; do
  a=0; [ -f s0_O.out ]   && grep -q "JOB DONE" s0_O.out   && a=1
  b=0; [ -f s0_OOH.out ] && grep -q "JOB DONE" s0_OOH.out && b=1
  [ "$a" = 1 ] && [ "$b" = 1 ] && break
  sleep 60
done
echo "START_CLEANSLAB_NP32 $(date -u)" >> cleanslab.log
t0=$(date +%s)
mpirun --allow-run-as-root -np 32 pw.x -nk 8 -in slab.in > slab.out 2>&1
ec=$?
dn=$(grep -c "JOB DONE" slab.out 2>/dev/null)
echo "CLEANSLAB_DONE exit=$ec JOB_DONE=$dn $(( $(date +%s)-t0 ))s $(date -u)" >> cleanslab.log
