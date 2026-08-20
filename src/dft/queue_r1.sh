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
# QE_PREFIX/LOG overridable so the SAME driver runs unchanged on Anvil, where
# there is no /workspace and $HOME is 25 GB (anvil/README.md). Defaults are
# the Vast box's exact paths, so an un-set environment behaves bit-identically
# to every wave banked so far -- the migration must not change a number.
QE_PREFIX=${QE_PREFIX:-/workspace/qe/env}
export PATH=$QE_PREFIX/bin:${PATH:-}
export LD_LIBRARY_PATH=$QE_PREFIX/lib:${LD_LIBRARY_PATH:-}
export OMP_NUM_THREADS=1
LOG=${LOG:-/workspace/queue_r1.log}

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
  local d job suf nk extra dir inp out calc ok seen mesh nprod
  local pdir upf ppbad
  local want_np want_nconc expect_cap cores quota period

  # Manifest directives (finding N6): every max_seconds in the decks was
  # computed at the NP the builder intended, and NP is a runtime argument.
  # Running manifest B's NP=20 caps at NP=4 silently truncates each job at
  # ~20% of its work -- after days of box time. The builder stamps
  # `# NP=<n> NCONC=<n>` into the manifest; a mismatch is a refusal, not a
  # warning. `# EXPECT_CAP` (finding N7) marks a manifest whose legs are
  # DESIGNED to stop on max_seconds (the CELL_MULT timing wave): there a
  # capped .out is the deliverable, never stale, and must never be deleted.
  # A NEAR-MISS directive must refuse, not silently disarm the guard (verify
  # round: '# NP=x NCONC=', '#NP=20 NCONC=1', '# NCONC=1 NP=20' all failed the
  # strict regex and PREFLIGHT_OK'd with no protection). Any comment line that
  # mentions NP= or NCONC= must match the exact form, and there may be at most
  # one, so a conflicting duplicate cannot silently win by being first.
  # start-anchored: prose header lines legitimately mention NP=4 mid-sentence;
  # only a line that BEGINS like a directive is held to the directive form.
  ndirect=$(grep -acE '^# *N(P|CONC)=' "$MANIFEST" || true)
  nstrict=$(grep -acE '^# NP=[0-9]+ NCONC=[0-9]+$' "$MANIFEST" || true)
  if [ "$ndirect" != "$nstrict" ]; then
    echo "PREFLIGHT_BAD malformed-np-directive: $MANIFEST has $ndirect comment line(s) mentioning NP=/NCONC= but only $nstrict in the exact form '# NP=<n> NCONC=<n>' -- a typo here would silently disarm the wrong-NP refusal (finding N6)"
    nbad=$((nbad + 1))
  elif [ "$nstrict" -gt 1 ]; then
    echo "PREFLIGHT_BAD duplicate-np-directive: $MANIFEST carries $nstrict NP/NCONC directives; with more than one, which applies is ambiguous"
    nbad=$((nbad + 1))
  fi
  want_np=$(grep -am1 -oE '^# NP=[0-9]+ NCONC=[0-9]+$' "$MANIFEST" | grep -oE 'NP=[0-9]+' | cut -d= -f2)
  want_nconc=$(grep -am1 -oE '^# NP=[0-9]+ NCONC=[0-9]+$' "$MANIFEST" | grep -oE 'NCONC=[0-9]+' | cut -d= -f2)
  expect_cap=0
  # exact line only -- '# EXPECT_CAPRICIOUS' must not arm it (verify round)
  grep -qaxE '# EXPECT_CAP' "$MANIFEST" && expect_cap=1
  if [ -n "${want_np:-}" ]; then
    if [ "$want_np" != "$NP" ] || [ "$want_nconc" != "$NCONC" ]; then
      echo "PREFLIGHT_BAD wrong-np-for-manifest: $MANIFEST declares NP=$want_np NCONC=$want_nconc, invoked with NP=$NP NCONC=$NCONC -- the decks' max_seconds were sized at the declared NP (finding N6)"
      nbad=$((nbad + 1))
    fi
  fi

  # Oversubscription (finding N5(c)): NP x NCONC against the cgroup quota.
  # docs/23 s8 measured a 12x thrash from exactly this. Only checkable where
  # cgroup v2 exposes cpu.max; skipped elsewhere. Both fields are validated as
  # integers so garbage content fails CLOSED with a named refusal, not an
  # arithmetic error that empties the report (verify round).
  if [ -r /sys/fs/cgroup/cpu.max ]; then
    read -r quota period < /sys/fs/cgroup/cpu.max
    if [ "${quota:-max}" != "max" ]; then
      case "$quota$period" in
        *[!0-9]*)
          echo "PREFLIGHT_BAD unreadable-cpu-quota: /sys/fs/cgroup/cpu.max says '$quota $period'"
          nbad=$((nbad + 1));;
        *)
          cores=$((quota / period))
          if [ $((NP * NCONC)) -gt $((cores + 1)) ]; then
            echo "PREFLIGHT_BAD oversubscribed: NP=$NP x NCONC=$NCONC = $((NP * NCONC)) ranks against a $cores-core cgroup quota (docs/23 s8: 12x thrash)"
            nbad=$((nbad + 1))
          fi;;
      esac
    fi
  fi

  seen=" "
  while read -r d job suf nk extra; do
    case "${d:-}" in ""|\#*) continue;; esac
    nline=$((nline + 1))
    if [ -z "${job:-}" ] || [ -z "${suf:-}" ] || [ -z "${nk:-}" ]; then
      echo "PREFLIGHT_BAD malformed-line '$d ${job:-} ${suf:-} ${nk:-}'"; nbad=$((nbad + 1)); continue
    fi
    # verify round: preflight read 5 fields but the DRIVER reads 4, so a 5th
    # token used to fold into run_one's nk and reach pw.x as `-nk '4 junk'` --
    # a runtime abort mid-wave, the exact class this pre-flight exists to stop.
    if [ -n "${extra:-}" ]; then
      echo "PREFLIGHT_BAD trailing-token $d/$job: '$extra' -- the driver reads 4 fields and would pass this to pw.x inside -nk"
      nbad=$((nbad + 1)); continue
    fi
    case "$nk" in ''|*[!0-9]*) echo "PREFLIGHT_BAD nk-not-an-integer $d/$job nk='$nk'"
                               nbad=$((nbad + 1)); continue;; esac
    if [ "$nk" -lt 1 ] || [ $((NP % nk)) -ne 0 ]; then
      echo "PREFLIGHT_BAD np-not-a-multiple-of-nk $d/$job NP=$NP nk=$nk (hard rule 4: pw.x aborts)"
      nbad=$((nbad + 1)); continue
    fi
    # duplicate lines (finding N5(b)): two concurrent runs of the same job
    # share one cwd/outdir and the first to finish rm -rf's the other's
    # scratch mid-run.
    case "$seen" in *" $d/$job "*)
      echo "PREFLIGHT_BAD duplicate-job $d/$job appears twice in $MANIFEST"
      nbad=$((nbad + 1)); continue;;
    esac
    seen="$seen$d/$job "
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
    # missing pseudopotential (MEASURED 2026-08-20). The S0 TiO2 legs name
    # ti_pbe_v1.4.uspp.F.UPF, but the live pseudo_dir held only five UPFs --
    # H/Ir/O/Ru/Cr. Five queued decks would each have taken a slot and died at
    # ATOMIC_SPECIES, two to four days into the wave, one after another. Nothing
    # upstream looked: the dir existed, the deck existed, the deck parsed clean.
    # Checked against the EFFECTIVE dir (PSEUDO_DIR if set, else the deck's own),
    # because a freshly staged cluster tree is exactly where a UPF goes missing.
    pdir=${PSEUDO_DIR:-$(grep -am1 'pseudo_dir' "$inp" | sed "s/.*= *'\([^']*\)'.*/\1/")}
    ppbad=0
    if [ -n "$pdir" ]; then
      for upf in $(grep -aoE '[A-Za-z0-9_.+-]+\.(UPF|upf)' "$inp" | sort -u); do
        if [ ! -f "$pdir/$upf" ]; then
          echo "PREFLIGHT_BAD missing-pseudo $d/$job: '$upf' not found in $pdir"
          ppbad=1
        fi
      done
    fi
    if [ "$ppbad" = 1 ]; then nbad=$((nbad + 1)); continue; fi
    # gross nk sanity (finding N5(a)): nk can never exceed the full k-mesh
    # product (symmetry only ever reduces it further). This is a LOWER bound
    # on trouble -- a symmetric deck can still have fewer irreducible points
    # than the product -- but it catches the coarse-mesh case measured on the
    # box (nk=8 on a 6-point mesh) before pw.x aborts mid-wave.
    mesh=$(grep -aA1 'K_POINTS' "$inp" | tail -1 | awk '{print $1, $2, $3}')
    if [ -n "$mesh" ]; then
      nprod=$(echo "$mesh" | awk '{print $1 * $2 * $3}')
      if [ "${nprod:-0}" -gt 0 ] && [ "$nk" -gt "$nprod" ]; then
        echo "PREFLIGHT_BAD nk-exceeds-kmesh $d/$job nk=$nk > $nprod = full mesh product (pw.x aborts)"
        nbad=$((nbad + 1)); continue
      fi
    fi
    out=$dir/${job}.out
    if [ -f "$out" ] && grep -qa 'JOB DONE' "$out"; then
      # finding N4: the old single-quote-only extraction returned '' on a
      # double-quoted deck and the empty calc fell into the PERMISSIVE branch,
      # so a truncated relaxation written `calculation = "relax"` was
      # classified complete. Both quote styles are read, an unreadable
      # calculation is a refusal, and the unknown branch is the STRICT one.
      calc=$(grep -am1 -oE 'calculation[[:space:]]*=[[:space:]]*["'"'"'][a-z-]+["'"'"']' "$inp" \
             | grep -oE '[a-z-]+' | tail -1)
      if [ -z "${calc:-}" ]; then
        echo "PREFLIGHT_BAD unreadable-calculation $d/$job: cannot classify $out without it (finding N4)"
        nbad=$((nbad + 1)); continue
      fi
      ok=0
      case "$calc" in
        scf|nscf|bands)
          if [ "$expect_cap" = 1 ] && grep -qa 'Maximum CPU time exceeded' "$out"; then
            # finding N7: this manifest's legs are designed to stop on the
            # cap; the partial .out IS the measurement.
            ok=1
          elif grep -qa '^!    total energy' "$out" && \
               ! grep -qa 'convergence NOT achieved' "$out"; then
            ok=1
          fi;;
        *) # relax, vc-relax, and anything unrecognised: STRICT (finding N4)
           grep -qa 'bfgs converged' "$out" && ok=1;;
      esac
      if [ "$ok" = 1 ]; then
        nskip=$((nskip + 1))
      else
        nstale=$((nstale + 1))
        # calculation-aware instruction (finding N7): an SCF has no `Begin
        # final coordinates`, and telling an operator to delete one destroys
        # the artifact; only a relaxation is rebuilt-and-requeued.
        if [ "$calc" = "scf" ] || [ "$calc" = "nscf" ] || [ "$calc" = "bands" ]; then
          fixmsg="-- run_one would SKIP it forever; INSPECT $out (do not delete it blindly: a partial SCF may itself be data), then requeue after removing or renaming it, or set ALLOW_STALE_SKIP=1"
        else
          fixmsg="-- run_one would SKIP it forever; rebuild the deck from its own \`Begin final coordinates\`, delete $out, requeue, or set ALLOW_STALE_SKIP=1"
        fi
        echo "PREFLIGHT_STALE $d/$job calc=$calc JOB_DONE-without-a-defensible-result:" \
             "bfgs=$(grep -ac 'bfgs converged' "$out" 2>/dev/null || true)" \
             "scf_fail=$(grep -ac 'convergence NOT achieved' "$out" 2>/dev/null || true)" \
             "maxsec=$(grep -ac 'Maximum CPU time exceeded' "$out" 2>/dev/null || true)" \
             "$fixmsg"
      fi
    else
      nrun=$((nrun + 1))
    fi
  done < "$MANIFEST"

  echo "PREFLIGHT manifest=$MANIFEST lines=$nline to_run=$nrun already_done=$nskip stale=$nstale bad=$nbad NP=$NP NCONC=$NCONC expect_cap=$expect_cap"
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
  # PSEUDO_DIR (Anvil): the decks name an ABSOLUTE pseudo_dir, there is no root
  # on a cluster to create it, and an explicit pseudo_dir in the input overrides
  # $ESPRESSO_PSEUDO -- so the only correct rewrite point is here, in the same
  # derived .run.in that already carries the outdir rewrite. The registered .in
  # is never touched. Unset => byte-identical to every wave banked so far.
  local -a sedargs=( -e "s#outdir *= *'[^']*'#outdir = '${scratch}'#" )
  if [ -n "${PSEUDO_DIR:-}" ]; then
    sedargs+=( -e "s#pseudo_dir *= *'[^']*'#pseudo_dir = '${PSEUDO_DIR}'#" )
  fi
  sed "${sedargs[@]}" "${job}${suf}" > "${job}.run.in"
  # --bind-to none, NOT --bind-to core/--map-by numa: hwloc cannot see the real
  # topology inside a Vast container, so PRTE fails the bind ("tried to bind a
  # process but failed") and the ranks end up migrating across sockets and
  # blocking in collectives -- the host sat 87% idle while pw.x crawled, with a
  # 245-CPU cgroup quota we were nowhere near using. docs/23 s8 measured 99% core
  # efficiency with --bind-to none, which is what the endmember campaign shipped.
  # --oversubscribe: PRRTE's default slot count is PHYSICAL cores, so on an SMT
  # box with 14 physical / 28 threads a -np 20 launch dies in 1 s with rc=1 and
  # burns the whole manifest (2026-08-09 fleet launch: 3 boxes, 20 jobs each,
  # all rc=1 in under 30 s). The docs/23 s8 thrash was about exceeding the
  # CGROUP QUOTA, which the pre-flight refuses separately; ranks within the
  # quota but above the physical-core count just share SMT threads.
  mpirun --allow-run-as-root --bind-to none --oversubscribe -np "$NP" \
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
