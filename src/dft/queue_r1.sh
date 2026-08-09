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
# overridable ONLY so the pre-flight below can be exercised against a scratch
# tree without writing into the real runs mirror. Default is unchanged.
RUNS=${RUNS:-/workspace/sts/runs}
export PATH=/workspace/qe/env/bin:${PATH:-}
export LD_LIBRARY_PATH=/workspace/qe/env/lib:${LD_LIBRARY_PATH:-}
export OMP_NUM_THREADS=1
LOG=/workspace/queue_r1.log

# ------------------------------------------------------------------ preflight ---
# Finding [8](ii), adjudications 2026-08-09. Read the manifest ONCE and refuse to
# launch ANYTHING if a single line cannot run. Before this existed, launching a
# manifest whose run directories had never been uploaded wrote one `NODIR` line
# per job and then `QUEUE_ALL_DONE`, all inside one second -- which reads exactly
# like a completed wave. Verified on the box 2026-08-09: /workspace/sts/runs/
# probe/{Cr,Ir,Ru}_cellsym did not exist while a 37-line manifest was ready to go.
#
# It also refuses on a STALE `.out`. run_one() SKIPs any job whose .out contains
# `JOB DONE`, and pw.x prints JOB DONE after `convergence NOT achieved`, after
# nstep exhaustion, after a `max_seconds` stop and after a user `.EXIT` (hard
# rule 3; lessons.md 2026-07-31, where a killed job logged rc=0 JOB_DONE=1). A
# skip on one of those is permanent and silent. The test is calculation-aware:
# a relax must carry `bfgs converged`; anything else must carry a final
# `!    total energy` and no `convergence NOT achieved`.
#
#   MEASURED BLAST RADIUS, 2026-08-09, /workspace/sts/runs on box 47025043:
#   105 .out files carry `JOB DONE`; 0 of them trip this test. So aborting by
#   default cannot invalidate work already banked -- it only fires on a file
#   that really is stale.
#
# Two other refusals, both hard rules with a history in this project:
#   * NP must be an exact multiple of -nk or pw.x aborts (hard rule 4);
#   * a deck containing CR dies silently inside tmux (hard rule 1).
#
# Overrides:
#   ALLOW_STALE_SKIP=1   proceed despite stale .out files (they stay SKIPped)
#   PREFLIGHT_ONLY=1     run the checks, write the report, do not launch
ALLOW_STALE_SKIP=${ALLOW_STALE_SKIP:-0}
PREFLIGHT_ONLY=${PREFLIGHT_ONLY:-0}

preflight() {
  local nline=0 nbad=0 nstale=0 nskip=0 nrun=0
  local d job suf nk extra dir inp out calc ok
  while read -r d job suf nk extra; do
    case "${d:-}" in ""|\#*) continue;; esac
    nline=$((nline + 1))
    if [ -z "${job:-}" ] || [ -z "${suf:-}" ] || [ -z "${nk:-}" ]; then
      echo "PREFLIGHT_BAD malformed-line '$d ${job:-} ${suf:-} ${nk:-}'"; nbad=$((nbad + 1)); continue
    fi
    case "$nk" in ''|*[!0-9]*) echo "PREFLIGHT_BAD nk-not-an-integer $d/$job nk='$nk'"
                               nbad=$((nbad + 1)); continue;; esac
    if [ "$nk" -lt 1 ] || [ $((NP % nk)) -ne 0 ]; then
      echo "PREFLIGHT_BAD np-not-a-multiple-of-nk $d/$job NP=$NP nk=$nk (hard rule 4: pw.x aborts)"
      nbad=$((nbad + 1)); continue
    fi
    dir=$RUNS/$d
    if [ ! -d "$dir" ]; then
      echo "PREFLIGHT_BAD missing-dir $dir"; nbad=$((nbad + 1)); continue
    fi
    inp=$dir/${job}${suf}
    if [ ! -f "$inp" ]; then
      echo "PREFLIGHT_BAD missing-input $inp"; nbad=$((nbad + 1)); continue
    fi
    if LC_ALL=C grep -qa $'\r' "$inp"; then
      echo "PREFLIGHT_BAD crlf-input $inp (hard rule 1: a CRLF deck dies silently)"
      nbad=$((nbad + 1)); continue
    fi
    out=$dir/${job}.out
    if [ -f "$out" ] && grep -qa 'JOB DONE' "$out"; then
      calc=$(grep -am1 -oE "calculation[[:space:]]*=[[:space:]]*'[a-z-]+'" "$inp" \
             | sed "s/.*'\(.*\)'/\1/")
      ok=0
      case "${calc:-unknown}" in
        relax|vc-relax) grep -qa 'bfgs converged' "$out" && ok=1;;
        *) grep -qa '^!    total energy' "$out" && \
           ! grep -qa 'convergence NOT achieved' "$out" && ok=1;;
      esac
      if [ "$ok" = 1 ]; then
        nskip=$((nskip + 1))
      else
        nstale=$((nstale + 1))
        echo "PREFLIGHT_STALE $d/$job calc=${calc:-?} JOB_DONE-without-a-defensible-result:" \
             "bfgs=$(grep -ac 'bfgs converged' "$out" 2>/dev/null || true)" \
             "scf_fail=$(grep -ac 'convergence NOT achieved' "$out" 2>/dev/null || true)" \
             "maxsec=$(grep -ac 'Maximum CPU time exceeded' "$out" 2>/dev/null || true)" \
             "-- run_one would SKIP it forever; delete $out and requeue from its own" \
             "\`Begin final coordinates\`, or set ALLOW_STALE_SKIP=1"
      fi
    else
      nrun=$((nrun + 1))
    fi
  done < "$MANIFEST"

  echo "PREFLIGHT manifest=$MANIFEST lines=$nline to_run=$nrun already_done=$nskip stale=$nstale bad=$nbad NP=$NP NCONC=$NCONC"
  [ "$nline" -gt 0 ] || { echo "PREFLIGHT_BAD manifest-has-no-job-lines $MANIFEST"; return 2; }
  [ "$nbad" -eq 0 ] || return 2
  if [ "$nstale" -gt 0 ] && [ "$ALLOW_STALE_SKIP" != "1" ]; then return 3; fi
  return 0
}

pf_out=$(preflight); pf_rc=$?
printf '%s\n' "$pf_out"
printf '%s\n' "$pf_out" >> "$LOG"
if [ "$pf_rc" -ne 0 ]; then
  echo "PREFLIGHT_ABORT rc=$pf_rc -- nothing launched $(date -u)" | tee -a "$LOG"
  exit "$pf_rc"
fi
if [ "$PREFLIGHT_ONLY" = "1" ]; then
  echo "PREFLIGHT_OK (PREFLIGHT_ONLY=1, nothing launched) $(date -u)" | tee -a "$LOG"
  exit 0
fi
echo "PREFLIGHT_OK $(date -u)" >> "$LOG"

echo "QUEUE_START $(date -u) NP=$NP NCONC=$NCONC manifest=$MANIFEST cpu.max=$(cat /sys/fs/cgroup/cpu.max 2>/dev/null)" >> "$LOG"

run_one() {
  local d=$1 job=$2 suf=$3 nk=$4
  local dir=$RUNS/$d
  cd "$dir" || { echo "NODIR $d" >> "$LOG"; return 2; }
  if grep -q "JOB DONE" "${job}.out" 2>/dev/null; then
    # the pre-flight has already classified this .out; record WHY it was skipped
    # so a skip is auditable after the fact instead of being a bare line.
    echo "SKIP $d/$job already-done bfgs=$(grep -ac 'bfgs converged' "${job}.out" 2>/dev/null || true) scf_fail=$(grep -ac 'convergence NOT achieved' "${job}.out" 2>/dev/null || true) $(date -u)" >> "$LOG"; return 0
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
