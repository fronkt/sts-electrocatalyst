#!/usr/bin/env bash
# Two-stage runner for the five n=6/7 rescue jobs (docs/34).
#
# Each job is: stage A `scf` at degauss = 0.03 Ry to get a converged charge density past
# the SCF plateau that killed Ni and Co, then stage B `relax` at the production
# degauss = 0.01 Ry with `startingpot = 'file'` picking that density up from the shared
# outdir. Only stage B produces an energy anything downstream is allowed to use.
#
# Job order is eta-critical first. Both metals are predicted pls = 2, so dG_O and dG_OH
# are what the gate needs; the two *OOH jobs buy the complete CHE chain and are the ones
# to drop if the box misbehaves.
#
#   RANKS=24 NK=8 bash run_rescue.sh
set -u
export PATH=/workspace/qe/env/bin:$PATH
export LD_LIBRARY_PATH=/workspace/qe/env/lib:${LD_LIBRARY_PATH:-}
export OMP_NUM_THREADS=1

RANKS=${RANKS:-24}
NK=${NK:-8}
STATUS=/workspace/status.log
: > "$STATUS"

# docs/23 s8: nproc and cpuset LIE inside a rented container; the binding limit is the
# cgroup quota. Sizing MPI to nproc cost 12x once.
CPUMAX=$(cat /sys/fs/cgroup/cpu.max 2>/dev/null || echo unknown)
echo "cpu.max=$CPUMAX nproc=$(nproc) ranks=$RANKS x 5 jobs nk=$NK" | tee -a "$STATUS"

run_job() {
  local d=$1 s=$2
  cd /workspace/sts/runs/"$d" || { echo "MISSING_DIR $d" >>"$STATUS"; return 1; }
  local t0=$SECONDS

  mpirun -np "$RANKS" --bind-to none --allow-run-as-root \
         pw.x -nk "$NK" -in "${s}.in.stageA" > "${s}.outA" 2>&1
  if grep -q "convergence has been achieved" "${s}.outA"; then
    echo "STAGE_A_OK   $d/$s  $((SECONDS-t0))s" >>"$STATUS"
  else
    # Not fatal: even a partly converged 0.03-degauss density beats atomic superposition.
    # Recorded so the QC pass knows this job started from a weaker guess.
    echo "STAGE_A_WEAK $d/$s  $((SECONDS-t0))s" >>"$STATUS"
  fi

  local t1=$SECONDS
  mpirun -np "$RANKS" --bind-to none --allow-run-as-root \
         pw.x -nk "$NK" -in "${s}.in.stageB" > "${s}.out" 2>&1
  local verdict=INCOMPLETE
  grep -q "convergence NOT achieved" "${s}.out" && verdict=SCF_FAILED
  grep -q "bfgs converged" "${s}.out" && verdict=CONVERGED
  echo "STAGE_B $verdict $d/$s  $((SECONDS-t1))s  total $((SECONDS-t0))s" >>"$STATUS"
}

for job in "Ni_slab s0_O" "Ni_slab s0_OH" "Co_slab s0_O" "Ni_slab s0_OOH" "Co_slab s0_OOH"; do
  # shellcheck disable=SC2086
  run_job $job &
done
wait
echo "ALL_DONE $(date -u)" >>"$STATUS"
cat "$STATUS"
