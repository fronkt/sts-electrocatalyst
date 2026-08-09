#!/usr/bin/env bash
# Throttled hp.x queue. Modelled on queue_r1.sh, which cannot drive hp.x for four reasons --
# each one is a real failure, not a style preference:
#
#   1. queue_r1.sh invokes `pw.x` by name. hp.x is a different binary.
#   2. hp.x is a POST-PROCESSOR: it reads `<outdir>/<prefix>.save` written by a preceding
#      pw.x SCF. queue_r1.sh gives every job its OWN `./tmp_<job>` scratch and `rm -rf`s it
#      the moment the job returns, so a pw.x job followed by an hp.x job would find nothing.
#      Here the SCF and every hp.x rung that reads it share ONE scratch, and the scratch is
#      removed only after the last rung for that ground state.
#   3. The q-mesh ladder is N hp.x runs against ONE ground state. Re-running the SCF per rung
#      would triple the bill for an identical density. So the manifest names the SCF on every
#      line and this script runs it once, keyed on the scratch directory.
#   4. `JOB DONE` is even weaker for hp.x than for pw.x -- and it was already worthless there
#      (docs/26 s4, docs/30, tasks/lessons.md 2026-07-31: pw.x prints it after SCF failure,
#      after nstep exhaustion and after a user .EXIT). hp.x prints `JOB DONE.` after ALL of:
#        * "Convergence has not been reached after N iterations!"   (measured, FeO2, 08-09)
#        * "Not all q points were considered. Stopping smoothly..." (start_q/last_q)
#        * the gapped-system refusal "...should NOT be treated as a metal ... Stopping..."
#          (measured, TiO2 under smearing, 08-09)
#        * determine_num_pert_only / determine_q_mesh_only, which compute no U at all
#
# THE THREE THINGS THE 2026-08-09 REVIEW FOUND IN THIS FILE, AND WHAT REPLACED THEM
# ---------------------------------------------------------------------------------
# [17] The gate was dead. `grep 'Hubbard U parameters:' <hp>.out` returns 0 on a run that
#      produced U = 4.1543 eV, because **the U never appears in stdout at all**. It is in
#      `<cwd>/<prefix>.Hubbard_parameters.dat` (opened by name, no path, in HP/src/
#      hp_postproc.f90:alloc_pp) and in `<outdir>/HP/<prefix>.chi*.dat`. The `udat` fallback
#      was a directory-wide `ls | wc -l`, so after the first rung wrote a .dat every later
#      job reported UDAT=1 including the 3-second counting decks. A fully-successful batch
#      and a fully-failed one emitted byte-identical log signatures -- the campaign's oldest
#      lesson, re-committed in the file written to prevent it. Now: pre-clean, run, rename
#      the artifact onto the DECK basename, and gate on the artifact.
# [16] hp.x names every result from the prefix ALONE, so eight U determinations at one prefix
#      leave two files. Measured: nq 1x1x1 gave 4.1543, then nq 2x2x2 in the same outdir
#      overwrote it in place with 4.1786 and grew chi.dat from 208 to 1440 bytes. The rename
#      below happens between the hp.x call and the next job, keyed on `$hp`, which already
#      encodes the q-mesh.
# [9][18] Two hp.x runs at one prefix+outdir collide. hp.x writes `<outdir>/HP/<prefix>.
#      dvwfc1..N`, `.dwfc*`, `.hubnoS*`, `.mixd*` and `<outdir>/<prefix>.wfc1..N`, named from
#      prefix and MPI rank only -- no run identifier. MEASURED: two simultaneous runs at one
#      prefix, run A finished, run B died with 12 error lines and exit code 2. The bad case
#      is not the crash; it is both surviving on each other's half-written buffers and
#      emitting a plausible, wrong U. Now: an flock on (dir, prefix) held across the SCF AND
#      the hp.x call, plus a pre-flight that refuses NCONC > 1 when a prefix repeats.
#      Parallelism is supposed to come from DIFFERENT prefixes (atomic vs ortho, sym vs
#      nosym), and that still works.
# [20] `/workspace/sts/runs` contained exactly one directory (`probe`). Launching as shipped
#      would have written 22 `NODIR` lines and then `QUEUE_HP_ALL_DONE` -- a success banner
#      on a queue that did nothing. Now nothing launches until the pre-flight has read the
#      whole manifest and found every directory and every input.
#
# Carried over unchanged from queue_r1.sh because they were paid for:
#   * size ranks to /sys/fs/cgroup/cpu.max, never nproc (docs/23 s8 -- a 12x thrash);
#   * `--bind-to none`, never --bind-to core/--map-by numa (hwloc cannot see a Vast container);
#   * `</dev/null` on the backgrounded mpirun, or OpenMPI's stdin forwarding drains the job
#     list and the queue exits after one job;
#   * `grep -c ... || true`, never `|| echo 0` -- the latter appends a SECOND zero and breaks
#     the machine-checkable acceptance line.
#
# Manifest lines:  <dir-under-runs> <scf-basename> <hp-basename> <nk>
#   e.g.  hp_tio2 scf__atomic hp__atomic_q333 4
#         hp_costmodel crslab_sym__scf crslab_sym__hp_1atomq_a5_q3 6
# Reads $RUNS/<dir>/<scf>.in and $RUNS/<dir>/<hp>.in, writes <scf>.out and <hp>.out.
#
# NP must be an EXACT MULTIPLE of nk for BOTH binaries or they abort in mp_startup, and
# NP x NCONC must fit the cgroup (23.04 usable cores on box 47025043; nproc says 48).
#
# Usage: bash queue_hp.sh <manifest> <NP> <NCONC>
#        bash queue_hp.sh <manifest> <NP> <NCONC> --preflight-only    # checks, launches nothing
set -u
MANIFEST=${1:?manifest file}
NP=${2:-12}
NCONC=${3:-1}
MODE=${4:-run}
RUNS=${RUNS:-/workspace/sts/runs}
MAXCORES=${MAXCORES:-23}
export PATH=/workspace/qe/env/bin:${PATH:-}
export LD_LIBRARY_PATH=/workspace/qe/env/lib:${LD_LIBRARY_PATH:-}
export OMP_NUM_THREADS=1
LOG=${LOG:-/workspace/queue_hp.log}

# Read one `key = 'value'` out of a QE namelist. hp.x resolves its artifacts from the deck's
# own prefix/outdir, so the queue has to read them from the deck too -- inferring them from
# the filename is how the wrong file gets renamed onto the right name.
deck_field() { sed -n "s/^[[:space:]]*$1[[:space:]]*=[[:space:]]*'\([^']*\)'.*/\1/p" "$2" | head -1; }

# ------------------------------------------------------------------------- pre-flight ---
# Reads the manifest ONCE, checks everything that can be checked without spending a core,
# and returns non-zero before a single rank is launched. Finding [20]: the failure it exists
# to stop is a queue that logs its own success banner having run nothing.
preflight() {
  local fails=0 lineno=0 nrun=0 d scf hp nk dir p_scf p_hp o_hp
  local -a prefixes=() timing=()
  while read -r d scf hp nk _rest; do
    lineno=$((lineno+1))
    case "${d:-}" in ""|\#*) continue;; esac
    nrun=$((nrun+1))
    if [ -z "${nk:-}" ]; then
      echo "PREFLIGHT line $lineno: needs 4 fields <dir> <scf> <hp> <nk>, got: $d $scf ${hp:-} ${nk:-}"; fails=$((fails+1)); continue
    fi
    dir=$RUNS/$d
    if [ ! -d "$dir" ]; then
      echo "PREFLIGHT line $lineno: missing directory $dir"; fails=$((fails+1)); continue
    fi
    local ok=1
    for f in "$dir/$scf.in" "$dir/$hp.in"; do
      if [ ! -s "$f" ]; then echo "PREFLIGHT line $lineno: missing or empty $f"; fails=$((fails+1)); ok=0; continue; fi
      # A CRLF deck dies silently inside the box's tmux (tasks/lessons.md 2026-07-31).
      if LC_ALL=C grep -qc $'\r' "$f" 2>/dev/null; then
        echo "PREFLIGHT line $lineno: $f contains CR bytes (CRLF deck)"; fails=$((fails+1)); ok=0
      fi
    done
    [ "$ok" = 1 ] || continue
    case "$nk" in ''|*[!0-9]*) echo "PREFLIGHT line $lineno: nk=$nk is not an integer"; fails=$((fails+1)); continue;; esac
    if [ "$nk" -lt 1 ] || [ $((NP % nk)) -ne 0 ]; then
      echo "PREFLIGHT line $lineno: NP=$NP is not an exact multiple of nk=$nk; pw.x and hp.x both abort in mp_startup"
      fails=$((fails+1))
    fi
    p_scf=$(deck_field prefix "$dir/$scf.in"); p_hp=$(deck_field prefix "$dir/$hp.in")
    o_hp=$(deck_field outdir "$dir/$hp.in")
    if [ -z "$p_hp" ] || [ -z "$o_hp" ]; then
      echo "PREFLIGHT line $lineno: $hp.in does not set both prefix and outdir"; fails=$((fails+1)); continue
    fi
    if [ "$p_scf" != "$p_hp" ]; then
      echo "PREFLIGHT line $lineno: prefix mismatch, $scf.in has '$p_scf' but $hp.in has '$p_hp'; hp.x would not find the .save"
      fails=$((fails+1))
    fi
    if [ "$(deck_field outdir "$dir/$scf.in")" != "$o_hp" ]; then
      echo "PREFLIGHT line $lineno: outdir mismatch between $scf.in and $hp.in"; fails=$((fails+1))
    fi
    prefixes+=("$d/$p_hp")
    case "$hp" in *hp_1atomq*) timing+=("$hp");; esac
  done < "$MANIFEST"

  if [ "$nrun" -eq 0 ]; then
    echo "PREFLIGHT: manifest $MANIFEST has no runnable lines (only comments/blanks)"
    fails=$((fails+1))
  elif [ "${#prefixes[@]}" -eq 0 ]; then
    echo "PREFLIGHT: all $nrun runnable lines failed a check above"
  fi
  # [19] cores. NP x NCONC against the cgroup, not against nproc.
  if [ $((NP * NCONC)) -gt "$MAXCORES" ]; then
    echo "PREFLIGHT: NP($NP) x NCONC($NCONC) = $((NP*NCONC)) exceeds $MAXCORES usable cores"
    fails=$((fails+1))
  fi
  # [9] [18] shared prefix + concurrency. The flock below makes this safe anyway; the refusal
  # stays because the adjudication requires it and because a serialised NCONC>1 just means
  # ranks sitting idle behind a lock while the operator believes they are working.
  local dupes
  dupes=$(printf '%s\n' "${prefixes[@]:-}" | sort | uniq -d | tr '\n' ' ')
  if [ "$NCONC" -gt 1 ] && [ -n "${dupes// /}" ]; then
    echo "PREFLIGHT: NCONC=$NCONC but these (dir, prefix) pairs appear more than once: $dupes"
    echo "PREFLIGHT: hp.x names its Sternheimer buffers from prefix + MPI rank alone; two"
    echo "PREFLIGHT: rungs at one prefix were MEASURED colliding (run B exit code 2). Use NCONC=1."
    fails=$((fails+1))
  fi
  # [19] a wall clock taken under contention is not a cost basis.
  if [ "$NCONC" -gt 1 ] && [ "${#timing[@]}" -gt 0 ]; then
    echo "PREFLIGHT: NCONC=$NCONC but the manifest contains timing decks (${timing[*]}); these"
    echo "PREFLIGHT: are the numbers block 3Y is costed from and must be run alone."
    fails=$((fails+1))
  fi
  if [ "$fails" -ne 0 ]; then
    echo "PREFLIGHT_FAIL $fails problem(s); nothing launched $(date -u)" | tee -a "$LOG"
    return 1
  fi
  echo "PREFLIGHT_OK $nrun runnable lines, $(printf '%s\n' "${prefixes[@]}" | sort -u | wc -l) distinct (dir,prefix), NP=$NP NCONC=$NCONC $(date -u)" | tee -a "$LOG"
  return 0
}

# ---------------------------------------------------------------------------- the SCF ---
# [N23] the converged string alone proves a PROCESS once converged, not that the ground
# state is still on disk: this file's own footer tells the operator to rm -rf the tmp_*
# scratch when the batch is scored, after which a string-only skip sends every rung into
# hp.x with no charge density -- 23 crashes from a "passing" gate. Skip (and success)
# require the string AND the charge-density file hp.x will actually read.
_scf_density_ok() {
  # $1 = outdir, $2 = prefix. QE writes charge-density.dat (or .hdf5 builds).
  [ -s "$1/$2.save/charge-density.dat" ] || [ -s "$1/$2.save/charge-density.hdf5" ]
}
# [N24] total/absolute magnetisation, read from the .out and logged on BOTH paths. The
# CrO2 arm exists to exercise the magnetic branch (docs/43 s4-A.3); an SCF that lands on a
# zero-moment solution is a second closed-shell run and its arm licenses nothing -- the
# builder's recorded pass condition requires MAG here to be non-zero. Block 1A's
# adjudication [3] set the record-magnetisation rule this follows.
_scf_mags() {
  MAG=$(grep -a 'total magnetization'    "$1" 2>/dev/null | tail -1 | awk '{print $4}')
  ABSMAG=$(grep -a 'absolute magnetization' "$1" 2>/dev/null | tail -1 | awk '{print $4}')
  MAG=${MAG:-na}; ABSMAG=${ABSMAG:-na}
}
scf_once() {
  local dir=$1 scf=$2 nk=$3
  local sprefix soutdir
  sprefix=$(deck_field prefix "${scf}.in"); soutdir=$(deck_field outdir "${scf}.in")
  if grep -aq "convergence has been achieved" "${scf}.out" 2>/dev/null \
     && _scf_density_ok "$soutdir" "$sprefix"; then
    _scf_mags "${scf}.out"
    echo "SCF_SKIP $dir/$scf already-converged MAG=$MAG ABSMAG=$ABSMAG $(date -u)" >> "$LOG"
  else
    local t0; t0=$(date +%s)
    mpirun --allow-run-as-root --bind-to none -np "$NP" \
           pw.x -nk "$nk" -in "${scf}.in" > "${scf}.out" 2>&1 </dev/null
    local rc=$? conv fail
    conv=$(grep -ac 'convergence has been achieved' "${scf}.out" 2>/dev/null || true)
    fail=$(grep -ac 'convergence NOT achieved'      "${scf}.out" 2>/dev/null || true)
    _scf_mags "${scf}.out"
    echo "SCF_DONE $dir/$scf rc=$rc CONV=$conv SCF_FAIL=$fail MAG=$MAG ABSMAG=$ABSMAG $(( $(date +%s)-t0 ))s $(date -u)" >> "$LOG"
  fi
  grep -aq 'convergence has been achieved' "${scf}.out" 2>/dev/null \
    && _scf_density_ok "$soutdir" "$sprefix"    # [N23] both, or the rung aborts
}

# ---------------------------------------------------------------------------- one rung ---
run_one() {
  local d=$1 scf=$2 hp=$3 nk=$4
  local dir=$RUNS/$d
  cd "$dir" || { echo "NODIR $d" >> "$LOG"; return 2; }
  local prefix outdir expect
  prefix=$(deck_field prefix "${hp}.in")
  outdir=$(deck_field outdir "${hp}.in")
  # A deck in either determine_*_only mode computes no U by design, so "no artifact" is the
  # correct outcome for it and must not read as a failure -- and, just as important, a deck
  # that is NOT in one of those modes and produces no artifact must not read as a success.
  if grep -aqE '^\s*determine_(num_pert|q_mesh)_only\s*=\s*\.true\.' "${hp}.in"; then
    expect=COUNT
  else
    expect=U
  fi

  # Everything that touches this (dir, prefix) is serialised: the SCF that builds
  # <outdir>/<prefix>.save and every hp.x rung that reads it and writes into
  # <outdir>/HP/<prefix>.*. flock, not a mkdir sentinel, because the kernel releases it when
  # the process dies -- the old mkdir lock survived a crash and blocked the next batch for
  # 12 h. Different prefixes never contend.
  (
    # [N18] if flock is missing (a rebuilt container image would do it -- the util is not
    # part of the QE env), the old bare call fell through and the rung ran completely
    # unserialised, the exact state findings [9]/[18] describe, with nothing in the log.
    # A lock that cannot be taken is now a loud abort.
    flock -x 9 || { echo "HP_ABORT $d/$hp reason=no_flock $(date -u)" >> "$LOG"; exit 4; }
    if ! scf_once "$dir" "$scf" "$nk"; then
      echo "HP_ABORT $d/$hp reason=scf_not_converged $(date -u)" >> "$LOG"; exit 3
    fi

    # PRE-CLEAN. hp.x keys every output on the prefix, so without this a rung that produces
    # nothing inherits the previous rung's .dat and reports its U as its own. This is the
    # actual fix for [16]/[17]: after the clean, anything present was written by THIS rung.
    rm -f "${prefix}.Hubbard_parameters.dat"
    rm -f "${outdir}/HP/${prefix}".chi*.dat

    local t0; t0=$(date +%s)
    mpirun --allow-run-as-root --bind-to none -np "$NP" \
           hp.x -nk "$nk" -in "${hp}.in" > "${hp}.out" 2>&1 </dev/null
    local rc=$? secs
    secs=$(( $(date +%s)-t0 ))

    # CAPTURE, onto the deck basename, which already encodes the q-mesh and the arm.
    local nchi=0 f base
    if [ -s "${prefix}.Hubbard_parameters.dat" ]; then
      mv -f "${prefix}.Hubbard_parameters.dat" "${hp}.Hubbard_parameters.dat"
    fi
    for f in "${outdir}/HP/${prefix}".chi*.dat; do
      [ -e "$f" ] || continue
      base=${f##*/}; base=${base#"${prefix}."}
      cp -a "$f" "${hp}.${base}" && nchi=$((nchi+1))
    done

    # GATE ON THE ARTIFACT. `Hubbard U parameters:` is a real string but it lives in the .dat,
    # never in stdout -- measured 0 on a run that produced 4.1543 eV.
    local hasu=0 nu=0 uval=na
    if [ -s "${hp}.Hubbard_parameters.dat" ]; then
      hasu=$(grep -ac 'Hubbard U parameters:' "${hp}.Hubbard_parameters.dat" 2>/dev/null || true)
      # [N15] NU counts U-table rows ONLY: the count stops at the first line after the
      # table that is not a data row (blank line or the next section header). The old awk
      # ran to EOF and swept up the chi0/chi/inverse/Hubbard matrices that follow in the
      # same file -- a 2-Ti .dat reported NU=12 for 2 U values, a number shaped to be
      # copied into a table later.
      nu=$(awk '/Hubbard U parameters:/{f=1;next}
                f && c>0 && $NF !~ /^-?[0-9]+\.[0-9]+$/ {exit}
                f && $NF ~ /^-?[0-9]+\.[0-9]+$/ {c++}
                END{print c+0}' \
             "${hp}.Hubbard_parameters.dat")
      uval=$(awk '/Hubbard U parameters:/{f=1;next} f && $NF ~ /^-?[0-9]+\.[0-9]+$/ {print $NF; exit}' \
             "${hp}.Hubbard_parameters.dat")
      [ -n "$uval" ] || uval=na
    fi
    local artifact=0
    [ "$hasu" -gt 0 ] && [ "$nu" -gt 0 ] && artifact=1

    local jd notconv smooth gapstop npert nq klist
    jd=$(grep -ac 'JOB DONE'                                   "${hp}.out" 2>/dev/null || true)
    notconv=$(grep -ac 'Convergence has not been reached'      "${hp}.out" 2>/dev/null || true)
    smooth=$(grep -ac 'Not all q points were considered'       "${hp}.out" 2>/dev/null || true)
    gapstop=$(grep -ac 'should NOT be treated as a metal'      "${hp}.out" 2>/dev/null || true)
    npert=$(grep -aoE '^ +List of +[0-9]+ atoms which will be' "${hp}.out" 2>/dev/null | awk '{print $3}' | head -1)
    nq=$(grep -aoE '\( +[0-9]+ q-points \)'                    "${hp}.out" 2>/dev/null | head -1 | tr -dc '0-9')
    # [10] the cost model is per (atom, q) and scales with the k-count hp.x prints for EACH q.
    # Capturing it here is what turns the model's predictions into a measurement next time.
    klist=$(grep -aoE 'number of k points=[ ]*[0-9]+'          "${hp}.out" 2>/dev/null \
            | grep -oE '[0-9]+$' | head -40 | paste -sd, -)

    echo "HP_DONE $d/$hp rc=$rc EXPECT=$expect ARTIFACT=$artifact U=${uval} NU=$nu HAS_U=$hasu CHI=$nchi JOB_DONE=$jd NOTCONV=$notconv SMOOTHSTOP=$smooth GAPSTOP=$gapstop NPERT=${npert:-1} NQ=${nq:-na} NKLIST=${klist:-na} ${secs}s $(date -u)" >> "$LOG"
  ) 9>"$dir/.hp_${prefix}.lock"
}

# ------------------------------------------------------------------------------ driver ---
echo "QUEUE_HP_START $(date -u) NP=$NP NCONC=$NCONC manifest=$MANIFEST cpu.max=$(cat /sys/fs/cgroup/cpu.max 2>/dev/null)" >> "$LOG"
# [N14][N21] the log is append-only and shared by every manifest and every re-run, so any
# count taken over the whole file describes history, not this batch. Capture the byte
# offset now; the banner greps only what THIS run appended after this point.
BATCH_OFF=$(wc -c < "$LOG")
if ! preflight; then
  echo "QUEUE_HP_ABORTED_PREFLIGHT $(date -u)" >> "$LOG"
  exit 1
fi
if [ "$MODE" = "--preflight-only" ]; then
  echo "QUEUE_HP_PREFLIGHT_ONLY $(date -u)" >> "$LOG"
  exit 0
fi

while read -r d scf hp nk _rest; do
  case "${d:-}" in ""|\#*) continue;; esac
  while [ "$(jobs -rp | wc -l)" -ge "$NCONC" ]; do wait -n; done
  run_one "$d" "$scf" "$hp" "$nk" </dev/null &
done < "$MANIFEST"
wait

# The banner is not allowed to be the only thing at the end of the log, and it counts
# THIS BATCH ONLY ([N14][N21]): every grep below runs on the bytes appended after the
# QUEUE_HP_START offset, so a re-run cannot inherit an earlier batch's successes and the
# TiO2 batch's counts cannot leak into the costmodel batch's banner.
# [U11] NOTCONV is carried, and CLEAN_ARTIFACT requires NOTCONV=0: hp.x writes the
# .Hubbard_parameters.dat even after "Convergence has not been reached" (measured, FeO2),
# so ARTIFACT=1 alone is reachable on a stalled linear response -- which is precisely the
# CrO2 arm's registered failure mode (docs/43 s4-A.3: a finite U with ZERO such lines).
# A batch whose every U came from a stalled response must not print a clean tail.
batch=$(tail -c +$((BATCH_OFF + 1)) "$LOG" 2>/dev/null || true)
want=$(printf '%s\n' "$batch" | grep -ac 'HP_DONE .* EXPECT=U ' || true)
gotany=$(printf '%s\n' "$batch" | grep -ac 'HP_DONE .* EXPECT=U ARTIFACT=1 ' || true)
clean=$(printf '%s\n' "$batch" | { grep -a 'HP_DONE .* EXPECT=U ARTIFACT=1 ' || true; } | grep -ac ' NOTCONV=0 ' || true)
nconv=$(printf '%s\n' "$batch" | { grep -a 'HP_DONE .* EXPECT=U ' || true; } | grep -ac ' NOTCONV=[1-9]' || true)
aborts=$(printf '%s\n' "$batch" | grep -ac 'HP_ABORT ' || true)
echo "QUEUE_HP_ALL_DONE U_DECKS=$want WITH_ARTIFACT=$gotany CLEAN_ARTIFACT=$clean NOTCONV_RUNGS=$nconv ABORTS=$aborts (this batch only) $(date -u)" >> "$LOG"
# The scratch dirs are deliberately NOT removed: an hp.x rerun (compute_hp=.true.
# post-processing, or an extra q-mesh rung) needs the same .save, and re-running a 30-minute
# slab SCF to recover it is the expensive mistake this whole script exists to avoid. Note
# that a compute_hp rerun also needs <outdir>/HP/<prefix>.chi.dat back under its PREFIX name;
# the per-rung copies here are named after the deck.
# Clean them by hand when the batch is scored: rm -rf $RUNS/*/tmp_* $RUNS/*/.hp_*.lock
# (After that cleanup a re-run pays each SCF again: scf_once requires the charge density
# on disk, not just the converged string in the .out, so it re-runs instead of letting
# hp.x crash 23 times on a missing .save -- [N23].)
