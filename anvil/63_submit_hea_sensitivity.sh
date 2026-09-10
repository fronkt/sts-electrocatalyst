#!/usr/bin/env bash
# Guarded six-job HEA sensitivity submission; original 47 checks retained.
# Submit held at 128 ranks, concurrency 1, four hours/task and no requeue.
# Inspect held resources and exact input hashes before release; this script never releases.
set -euo pipefail

MANIFEST=${1:-$PROJECT/sts/runs/hea/m_sensitivity_2026-09-09.txt}
CONC=${2:-1}
NP=${NP:-128}
export NP

export QE_PREFIX=${QE_PREFIX:-$PROJECT/qe/env}
export PSEUDO_DIR=${PSEUDO_DIR:-$PROJECT/pseudo}
export RUNS=${RUNS:-$PROJECT/sts/runs}
export DRIVER=${DRIVER:-$PROJECT/queue_r1.sh}
export MANIFEST

[ "$NP" = 128 ] && [ "$CONC" = 1 ] || { echo "REFUSE: sensitivity requires NP=128 CONC=1" >&2; exit 2; }
[ "$(basename "$MANIFEST")" = m_sensitivity_2026-09-09.txt ] || {
  echo "REFUSE: sensitivity requires the exact approved manifest filename" >&2; exit 2;
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
[ "$N" -gt 0 ] || { echo "REFUSE: no runnable lines in $MANIFEST" >&2; exit 2; }


# Slurm copies the script; resolve helpers from the staged project.
ROOT="$PROJECT/sts"
PYTHON="/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3"
SPEC="$ROOT/results/hea_sensitivity_2026-09-09/launch_spec.json"
GUARD="$ROOT/src/dft/hea_sensitivity_guard.py"
QC="$ROOT/src/dft/hea_followup_qc.py"
FORCE_AUDIT="$ROOT/src/dft/hea_force_audit.py"
COMMON_GUARD="$ROOT/src/dft/hea_numerical_guard.py"
check_hash() { [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ] || { echo "REFUSE: pinned file differs: $1" >&2; exit 2; }; }
PW_BIN="$QE_PREFIX/bin/pw.x"
PROJ_BIN="$QE_PREFIX/bin/projwfc.x"
MPI_BIN="$QE_PREFIX/bin/mpirun"
check_hash "$PW_BIN" 1d66c7856f5d6b3cd9c66b8578e01512b16bbe907b4360e54234890712ccd6a1
check_hash "$PROJ_BIN" 456387be5ee32f358bc9835240b2e8bd1f8144a27a8e116731a1463dbf78ac85
check_hash "$MPI_BIN" a256bdcef89bdc61ba870e823056c51df868b4db48ab345a14278a7fe79ed75d
check_hash "$SPEC" fdce4056bf45c0479c6b00c6084804955d6314fa243e66bac336a0724fb581b9
check_hash "$GUARD" 6c59cb5986e39c5117be72f4c4dc8e7f7184b8f539ff6dc6d31e56b89a96f4e6
check_hash "$COMMON_GUARD" 98d866553566d9e8ab660535f5bbc0c33228f5160df59eda9f41de9c85ee5f9a
check_hash "$QC" ef9b50193f46034036b892263a3ee139426d912b2098ebdc5a897a82dc2769da
check_hash "$FORCE_AUDIT" bddbe7ba3bed9874e723d88f8bdab724bb4e83178f1f75bbc3a1f4034b9fd5d7
[ "$MANIFEST" = "$ROOT/runs/hea/m_sensitivity_2026-09-09.txt" ] || { echo "REFUSE: unexpected manifest path"; exit 2; }
[ "$RUNS" = "$ROOT/runs" ] || { echo "REFUSE: unexpected runs path"; exit 2; }
"$PYTHON" "$GUARD" --spec "$SPEC" --runs "$RUNS" || exit 2

# --- the driver's own dry preflight (nothing launched) -----------------------
# Catches stale .out, CRLF decks, missing pseudopotentials and the NP-vs-
# manifest-directive mismatch, exactly as 41_submit_wave.sh does. The driver is
# used here for its CHECKS only; the launch path is 62_hea_sensitivity.slurm.
echo "== preflight (nothing launched)"
PREFLIGHT_ONLY=1 LOG=/dev/stdout bash "$DRIVER" "$MANIFEST" "$NP" 1 || {
  echo "REFUSE: preflight failed -- fix the refusals above before submitting." >&2; exit 2; }

# --- Slurm stdout dir: 42's `#SBATCH -o logs/...` is relative to THIS cwd, and
# Slurm fails a task whose output file cannot be opened -- create it here so the
# launch does not depend on 20_stage.sh having run from $PROJECT.
mkdir -p logs

echo "== submitting HELD sensitivity array 1-$N%$CONC ($NP cores each); inspect before release"
echo "   requested four-hour cores*time bound: $((N * NP * 4)) core-hours (3072 for six jobs)"
# EXCLUDE=nodelist skips sick nodes (Anvil sbatch silently ignores the
# SBATCH_EXCLUDE env var -- learned on array 20101963, node a024)
sbatch --hold --mem=237G --time=04:00:00 --no-requeue --job-name=hea-sensitivity -A "$ACCT" -N 1 -n "$NP" ${EXCLUDE:+--exclude="$EXCLUDE"} --array=1-"$N"%"$CONC" \
       --export=ALL,PROJECT,MANIFEST,RUNS,QE_PREFIX,PSEUDO_DIR,NP \
       "$(dirname "$0")/62_hea_sensitivity.slurm"
