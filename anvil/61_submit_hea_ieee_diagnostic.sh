#!/usr/bin/env bash
# Guarded one-job HEA numerical submission; original 47 checks retained.
# Submit held at 128 ranks, concurrency 1, four hours/task and no requeue.
# Inspect held resources and exact input hashes before release; this script never releases.
set -euo pipefail

MANIFEST=${1:-$PROJECT/sts/runs/hea/m_ieee_2026-09-09.txt}
CONC=${2:-1}
NP=${NP:-128}
export NP

export QE_PREFIX=${QE_PREFIX:-$PROJECT/qe/env}
export PSEUDO_DIR=${PSEUDO_DIR:-$PROJECT/pseudo}
export RUNS=${RUNS:-$PROJECT/sts/runs}
export DRIVER=${DRIVER:-$PROJECT/queue_r1.sh}
export MANIFEST

[ "$NP" = 128 ] && [ "$CONC" = 1 ] || { echo "REFUSE: numerical requires NP=128 CONC=1" >&2; exit 2; }
[ "$(basename "$MANIFEST")" = m_ieee_2026-09-09.txt ] || {
  echo "REFUSE: numerical requires the exact approved manifest filename" >&2; exit 2;
}

[ -f "$MANIFEST" ] || { echo "REFUSE: manifest $MANIFEST not found" >&2; exit 2; }

# --- parity gate (hard; no override) -----------------------------------------
if [ ! -f "$PROJECT/parity/PARITY_PASS" ]; then
  echo "REFUSE: $PROJECT/parity/PARITY_PASS absent." >&2
  echo "        Run 30_parity.slurm and, if it passes, touch that file." >&2
  echo "        S3 wave-1 decks are all bank-bound; there is no FORCE path." >&2
  exit 2
fi

# --- pseudo preflight evidence must be present beside this script ------------
if [ ! -f "$(dirname "$0")/pseudo_md5_preflight_2026-08-23.md" ]; then
  echo "REFUSE: anvil/pseudo_md5_preflight_2026-08-23.md missing -- A8.5 md5" >&2
  echo "        byte-identity evidence must ride with the launch scripts." >&2
  exit 2
fi

# --- account (same mechanics as 41_submit_wave.sh) ---------------------------
# set +o pipefail inside the substitution: awk's early exit SIGPIPEs mybalance
# (141) and under set -e/pipefail that killed the whole script on non-tty ssh
ACCT=${ACCT:-$(set +o pipefail; mybalance 2>/dev/null | awk '$2=="CPU" {print $1; exit}')}
[ -n "${ACCT:-}" ] || { echo "REFUSE: could not resolve account; set ACCT=..." >&2; exit 2; }
echo "== account:  $ACCT"

# --- licence + EXCLUDE guards (docs/66 section 4, PIPELINE-GUARDS 2026-08-31) --
# (1) a manifest whose header carries a NOT LICENSED notice never submits.
#     Fail-closed; there is NO override variable (the no-FORCE posture).
if grep -qai 'NOT LICENSED' "$MANIFEST"; then
  echo "REFUSE: manifest $MANIFEST carries a 'NOT LICENSED' notice." >&2
  echo "        No override exists; licence the manifest first (docs/66 section 4)." >&2
  exit 2
fi
# (2) the manifest MUST name its sick-node list ('# SUBMIT WITH EXCLUDE=<list>')
#     and this invocation's $EXCLUDE must contain every node named there
#     (submit-time list additionally + a120,a200 per docs/66 section 4).
#     Fail-closed: a manifest LACKING the header is refused, not waved through.
MEXCL=$(awk -F= '/^# SUBMIT WITH EXCLUDE=/{gsub(/[ \r]/,"",$2); print $2; exit}' "$MANIFEST")
if [ -z "$MEXCL" ]; then
  echo "REFUSE: manifest $MANIFEST lacks a '# SUBMIT WITH EXCLUDE=' header." >&2
  exit 2
fi
_have=",$(printf '%s' "${EXCLUDE:-}" | tr -d ' '),"
for _node in $(printf '%s\n' "$MEXCL" | tr ',' ' '); do
  case "$_have" in
    *,"$_node",*) ;;
    *)
      echo "REFUSE: EXCLUDE=${EXCLUDE:-<unset>} is missing node $_node" >&2
      echo "        (manifest requires EXCLUDE to contain: $MEXCL)." >&2
      exit 2 ;;
  esac
done

# --- runnable lines ----------------------------------------------------------
grep -vE '^\s*(#|$)' "$MANIFEST" > "${MANIFEST}.lines"
N=$(wc -l < "${MANIFEST}.lines")
[ "$N" -eq 1 ] || { echo "REFUSE: expected exactly one runnable line in $MANIFEST" >&2; exit 2; }


# Slurm copies the script; resolve helpers from the staged project.
ROOT="$PROJECT/sts"
PYTHON="/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3"
SPEC="$ROOT/results/hea_numerical_2026-09-08/launch_spec.json"
FROZEN="$ROOT/src/dft/hea_numerical_guard.py"
GUARD="$ROOT/src/dft/hea_ieee_diagnostic.py"
WRAPPER="$ROOT/anvil/59_hea_ieee_rank.sh"
QC="$ROOT/src/dft/hea_followup_qc.py"
FORCE_AUDIT="$ROOT/src/dft/hea_force_audit.py"
check_hash() { [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ] || { echo "REFUSE: pinned file differs: $1" >&2; exit 2; }; }
export PATH="$QE_PREFIX/bin:$PATH"
MPI=$(command -v mpirun) || exit 2
PW="$QE_PREFIX/bin/pw.x"
PROJECTION="$QE_PREFIX/bin/projwfc.x"
check_hash "$SPEC" 3326e14e7b25ec0d84576f42b7f3eaf11bff53b36f33b8a7d9416cd96758406a
check_hash "$MANIFEST" dbf8f25a42297c74b8a339c1e25838019a10b8544a90b848b0b2ea1842a9b34f
check_hash "$FROZEN" 98d866553566d9e8ab660535f5bbc0c33228f5160df59eda9f41de9c85ee5f9a
check_hash "$GUARD" 742f35af2b7a4eaf085a9a1e8bb079887f7e1bf27db93d63adb32d9e41d85b82
check_hash "$QC" ef9b50193f46034036b892263a3ee139426d912b2098ebdc5a897a82dc2769da
check_hash "$FORCE_AUDIT" bddbe7ba3bed9874e723d88f8bdab724bb4e83178f1f75bbc3a1f4034b9fd5d7
check_hash "$WRAPPER" d226d707392142755a1dc1c3838fd702598a71004d28829b7eb48479382e21f1
check_hash "$MPI" a256bdcef89bdc61ba870e823056c51df868b4db48ab345a14278a7fe79ed75d
check_hash "$PW" 1d66c7856f5d6b3cd9c66b8578e01512b16bbe907b4360e54234890712ccd6a1
check_hash "$PROJECTION" 456387be5ee32f358bc9835240b2e8bd1f8144a27a8e116731a1463dbf78ac85
[ "$MANIFEST" = "$ROOT/runs/hea/m_ieee_2026-09-09.txt" ] || { echo "REFUSE: unexpected manifest path"; exit 2; }
[ "$RUNS" = "$ROOT/runs" ] || { echo "REFUSE: unexpected runs path"; exit 2; }
"$PYTHON" "$GUARD" --runs "$RUNS" || exit 2

# --- the driver's own dry preflight (nothing launched) -----------------------
# Catches stale .out, CRLF decks, missing pseudopotentials and the NP-vs-
# manifest-directive mismatch, exactly as 41_submit_wave.sh does. The driver is
# used here for its CHECKS only; the launch path is 60_hea_ieee_diagnostic.slurm.
echo "== preflight (nothing launched)"
PREFLIGHT_ONLY=1 LOG=/dev/stdout bash "$DRIVER" "$MANIFEST" "$NP" 1 || {
  echo "REFUSE: preflight failed -- fix the refusals above before submitting." >&2; exit 2; }

# --- Slurm stdout dir: 42's `#SBATCH -o logs/...` is relative to THIS cwd, and
# Slurm fails a task whose output file cannot be opened -- create it here so the
# launch does not depend on 20_stage.sh having run from $PROJECT.
mkdir -p logs

echo "== submitting HELD numerical array 1-$N%$CONC ($NP cores each); inspect before release"
echo "   requested four-hour cores*time bound: $((N * NP * 4)) core-hours (512 for one job)"
# EXCLUDE=nodelist skips sick nodes (Anvil sbatch silently ignores the
# SBATCH_EXCLUDE env var -- learned on array 20101963, node a024)
sbatch --hold --mem=237G --time=04:00:00 --no-requeue --job-name=hea-ieee-diagnostic -A "$ACCT" -N 1 -n "$NP" ${EXCLUDE:+--exclude="$EXCLUDE"} --array=1-"$N"%"$CONC" \
       --export=ALL,PROJECT,MANIFEST,RUNS,QE_PREFIX,PSEUDO_DIR,NP \
       "$(dirname "$0")/60_hea_ieee_diagnostic.slurm"
