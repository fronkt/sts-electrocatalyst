#!/usr/bin/env bash
# Run the Cu(1-x)Fe(x) KKR-CPA + Kubo validation ladder (src/thermo/README.md)
# on a box with MuST built at /workspace/MuST. Expects the run dirs from
# gen_cpa_ladder.py at /workspace/cpa/CuFe_x*/ (scp the runs_cpa/ tree there)
# and runs them sequentially: mst2 SCF -> kubo, logging everything.
#   NP sized to the cgroup quota (cpu.max), NOT nproc - tasks/lessons.md.
set -u
NP=${1:-8}
# Docker/seccomp blocks CMA; OpenMPI 4.1's default one-sided (RMA) component
# then dies in MPI_Win_create (MPI_ERR_WIN) inside mst2. Force the safe pair:
export OMPI_MCA_btl_vader_single_copy_mechanism=none
export OMPI_MCA_osc=pt2pt
MUST=/workspace/MuST
CPA=/workspace/cpa
LOG=$CPA/ladder.log
POT=$MUST/Potentials
echo "LADDER_START NP=$NP $(date -u)" >> "$LOG"

for d in "$CPA"/CuFe_x*/; do
  tag=$(basename "$d")
  cd "$d" || continue
  # starting potentials (idempotent)
  cp -n "$POT/29-Cu/Cu_mt_v" . 2>/dev/null
  cp -n "$POT/26-Fe/Fe_mt_v" . 2>/dev/null
  if [ -f kubo_done ]; then echo "SKIP $tag $(date -u)" >> "$LOG"; continue; fi

  t0=$(date +%s)
  if [ ! -f CuFe_mt_w ]; then
    # NOTE: mst2/kubo read the parameter file from stdin - do NOT add the
    # </dev/null guard here (this is a for-glob loop, no stdin-drain risk)
    mpirun --allow-run-as-root -np "$NP" "$MUST/bin/mst2" < i_scf > mst2.log 2>&1
    rc=$?
    echo "SCF $tag rc=$rc $(( $(date +%s)-t0 ))s $(date -u)" >> "$LOG"
    [ $rc -ne 0 ] && continue
    [ ! -f CuFe_mt_w ] && { echo "SCF $tag NO_POTENTIAL_OUT" >> "$LOG"; continue; }
  fi

  t1=$(date +%s)
  mpirun --allow-run-as-root -np "$NP" "$MUST/bin/kubo" < i_kubo > kubo.log 2>&1
  rc=$?
  echo "KUBO $tag rc=$rc $(( $(date +%s)-t1 ))s $(date -u)" >> "$LOG"
  if [ $rc -eq 0 ]; then
    touch kubo_done
    # harvest: o_* files carry "RESISTIVITY TENSOR (muOhm-cm)"
    grep -A6 -h "RESISTIVITY TENSOR" o_* 2>/dev/null | sed "s/^/$tag: /" >> "$CPA/results.txt"
  fi
done
echo "LADDER_ALL_DONE $(date -u)" >> "$LOG"
