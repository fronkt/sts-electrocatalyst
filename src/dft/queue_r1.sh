#!/usr/bin/env bash
# Throttled pw.x queue driven by an explicit job manifest, so one box can carry the
# Ru/Ir anchors and the Ni rescue in a single wave.
#
# Manifest lines:  <dir> <job-basename> <input-suffix> <nk>
#   e.g.  Ru_anchor slab .in 4     ->  runs/Ru_anchor/slab.in     -> slab.out
#         Ni_slab   s0_OH .in.restart 4 -> runs/Ni_slab/s0_OH.in.restart -> s0_OH.out
#
# Carries forward three hard-won rules:
#   * size ranks to /sys/fs/cgroup/cpu.max, never nproc (docs/23 s8 -- 12x thrash);
#   * `</dev/null` on the backgrounded mpirun, or OpenMPI's stdin forwarding drains
#     the job list and the queue exits after one job;
#   * `JOB DONE` alone is NOT success -- log SCF_FAIL and the free-atom force too,
#     because pw.x prints JOB DONE after `convergence NOT achieved ... stopping`
#     (docs/26 s4, and again for Ni in docs/30).
#
# Usage: bash queue_r1.sh <manifest> <NP> <NCONC>
set -u
MANIFEST=${1:?manifest file}
NP=${2:-16}
NCONC=${3:-8}
RUNS=/workspace/sts/runs
export PATH=/workspace/qe/env/bin:${PATH:-}
export LD_LIBRARY_PATH=/workspace/qe/env/lib:${LD_LIBRARY_PATH:-}
export OMP_NUM_THREADS=1
LOG=/workspace/queue_r1.log
echo "QUEUE_START $(date -u) NP=$NP NCONC=$NCONC manifest=$MANIFEST cpu.max=$(cat /sys/fs/cgroup/cpu.max 2>/dev/null)" >> "$LOG"

run_one() {
  local d=$1 job=$2 suf=$3 nk=$4
  local dir=$RUNS/$d
  cd "$dir" || { echo "NODIR $d" >> "$LOG"; return 2; }
  if grep -q "JOB DONE" "${job}.out" 2>/dev/null; then
    echo "SKIP $d/$job already-done $(date -u)" >> "$LOG"; return 0
  fi
  local scratch="./tmp_${job}"
  rm -rf "$scratch"; mkdir -p "$scratch"
  local t0; t0=$(date +%s)
  # each job gets its own outdir so concurrent jobs cannot collide on ./tmp
  sed "s#outdir *= *'[^']*'#outdir = '${scratch}'#" "${job}${suf}" > "${job}.run.in"
  # --bind-to none, NOT --bind-to core/--map-by numa: hwloc cannot see the real
  # topology inside a Vast container, so PRTE fails the bind ("tried to bind a
  # process but failed") and the ranks end up migrating across sockets and
  # blocking in collectives -- the host sat 87% idle while pw.x crawled, with a
  # 245-CPU cgroup quota we were nowhere near using. docs/23 s8 measured 99% core
  # efficiency with --bind-to none, which is what the endmember campaign shipped.
  mpirun --allow-run-as-root --bind-to none -np "$NP" \
         pw.x -nk "$nk" -in "${job}.run.in" > "${job}.out" 2>&1 </dev/null
  local rc=$?
  local jd sf ff nkp
  # `grep -c` already prints 0 on no-match AND exits 1, so `|| echo 0` appends a
  # SECOND zero and the DONE line comes out as "JOB_DONE=0\n0 SCF_FAIL=0\n0 ..." --
  # which breaks the machine-checkable acceptance criterion in docs/30 s7.
  # `|| true` keeps `set -u`-safe non-zero exits from aborting without adding output.
  jd=$(grep -ac 'JOB DONE' "${job}.out" 2>/dev/null || true)
  sf=$(grep -ac 'convergence NOT achieved' "${job}.out" 2>/dev/null || true)
  ff=$(grep -a 'Total force' "${job}.out" 2>/dev/null | tail -1 | awk '{print $4}')
  nkp=$(grep -am1 'number of k points' "${job}.out" 2>/dev/null | awk '{print $5}')
  echo "DONE $d/$job rc=$rc JOB_DONE=$jd SCF_FAIL=$sf F_LAST=${ff:-na} NK=${nkp:-na} $(( $(date +%s)-t0 ))s $(date -u)" >> "$LOG"
  rm -rf "$scratch"
}

while read -r d job suf nk; do
  case "${d:-}" in ""|\#*) continue;; esac
  while [ "$(jobs -rp | wc -l)" -ge "$NCONC" ]; do wait -n; done
  run_one "$d" "$job" "$suf" "$nk" </dev/null &
done < "$MANIFEST"
wait
echo "QUEUE_ALL_DONE $(date -u)" >> "$LOG"
