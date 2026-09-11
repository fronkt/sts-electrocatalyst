#!/usr/bin/env bash
# Guarded one-job HEA setup-only diagnostic submission; original 47 checks retained.
# Submit held at 128 ranks, concurrency 1, ten minutes/task and no requeue.
# Inspect held resources and exact input hashes before release; this script never releases.
set -euo pipefail

MANIFEST=${1:-$PROJECT/sts/runs/hea/m_ieee_init_2026-09-11.txt}
CONC=${2:-1}
NP=${NP:-128}
export NP

export QE_PREFIX=${QE_PREFIX:-$PROJECT/qe/env}
export PSEUDO_DIR=${PSEUDO_DIR:-$PROJECT/pseudo}
export RUNS=${RUNS:-$PROJECT/sts/runs}
export DRIVER=${DRIVER:-$PROJECT/queue_r1.sh}
export MANIFEST

[ "$PSEUDO_DIR" = /anvil/projects/x-che260157/pseudo ] || { echo "REFUSE: pseudo path differs"; exit 2; }

[ "$NP" = 128 ] && [ "$CONC" = 1 ] || { echo "REFUSE: setup-only diagnostic requires NP=128 CONC=1" >&2; exit 2; }
[ "$(basename "$MANIFEST")" = m_ieee_init_2026-09-11.txt ] || {
  echo "REFUSE: setup-only diagnostic requires the exact approved manifest filename" >&2; exit 2;
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
[ -f "${MANIFEST}.lines" ] || { echo "REFUSE: frozen manifest rows absent"; exit 2; }
N=$(wc -l < "${MANIFEST}.lines")
[ "$N" -eq 1 ] || { echo "REFUSE: expected exactly one runnable line in $MANIFEST" >&2; exit 2; }


# Slurm copies the script; resolve helpers from the staged project.
ROOT="$PROJECT/sts"
PYTHON="/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3"
SPEC="$ROOT/results/hea_ieee_init_2026-09-11/launch_spec.json"
FROZEN="$ROOT/src/dft/hea_numerical_guard.py"
GUARD="$ROOT/src/dft/hea_ieee_initialization_probe.py"
SENSITIVITY="$ROOT/src/dft/hea_sensitivity_guard.py"
WRAPPER="$ROOT/anvil/hea_ieee_initialization_rank.sh"
QC="$ROOT/src/dft/hea_followup_qc.py"
FORCE_AUDIT="$ROOT/src/dft/hea_force_audit.py"
check_hash() { [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ] || { echo "REFUSE: pinned file differs: $1" >&2; exit 2; }; }
export PATH="$QE_PREFIX/bin:$PATH"
MPI=$(command -v mpirun) || exit 2
PW="$QE_PREFIX/bin/pw.x"
check_hash "$SPEC" c5ad77a2b8764a856fad90721b5702c568c0fe87e6034f4c7c378075c59826bd
check_hash "$MANIFEST" 349214e2a4775a6c1e30d5c33f83578357eccd74480575e0f7cbb08b0a74880c
check_hash "$FROZEN" 98d866553566d9e8ab660535f5bbc0c33228f5160df59eda9f41de9c85ee5f9a
check_hash "$GUARD" 7b58317aa8d23e2ba7ee4bc4ffc989244ebfd799f8ec94210d20d18e5d6eb11f
check_hash "$SENSITIVITY" 6c59cb5986e39c5117be72f4c4dc8e7f7184b8f539ff6dc6d31e56b89a96f4e6
check_hash "$QC" ef9b50193f46034036b892263a3ee139426d912b2098ebdc5a897a82dc2769da
check_hash "$FORCE_AUDIT" bddbe7ba3bed9874e723d88f8bdab724bb4e83178f1f75bbc3a1f4034b9fd5d7
check_hash "$WRAPPER" 902d6a7527362679e00578590a37e795a7e31b0e5477a51079544a9820911edd
check_hash "$MPI" a256bdcef89bdc61ba870e823056c51df868b4db48ab345a14278a7fe79ed75d
check_hash "$PW" 1d66c7856f5d6b3cd9c66b8578e01512b16bbe907b4360e54234890712ccd6a1
[ "$MANIFEST" = "$ROOT/runs/hea/m_ieee_init_2026-09-11.txt" ] || { echo "REFUSE: unexpected manifest path"; exit 2; }
[ "$RUNS" = "$ROOT/runs" ] || { echo "REFUSE: unexpected runs path"; exit 2; }
"$PYTHON" "$GUARD" --runs "$RUNS" --pseudo-dir "$PSEUDO_DIR" || exit 2

# --- the driver's own dry preflight (nothing launched) -----------------------
# Catches stale .out, CRLF decks, missing pseudopotentials and the NP-vs-
# manifest-directive mismatch, exactly as 41_submit_wave.sh does. The driver is
# used here for its CHECKS only; the launch path is 70_hea_ieee_initialization.slurm.
echo "== preflight (nothing launched)"
PREFLIGHT_ONLY=1 LOG=/dev/stdout bash "$DRIVER" "$MANIFEST" "$NP" 1 || {
  echo "REFUSE: preflight failed -- fix the refusals above before submitting." >&2; exit 2; }

# --- Slurm stdout dir: 42's `#SBATCH -o logs/...` is relative to THIS cwd, and
# Slurm fails a task whose output file cannot be opened -- create it here so the
# launch does not depend on 20_stage.sh having run from $PROJECT.
mkdir -p logs

echo "== submitting HELD setup-only diagnostic array 1-$N%$CONC ($NP cores each); inspect before release"
echo "   allocation cap: 128 * 10 / 60 = 21.333333 core-hours; diagnostic only"
# EXCLUDE=nodelist skips sick nodes (Anvil sbatch silently ignores the
# SBATCH_EXCLUDE env var -- learned on array 20101963, node a024)
sbatch --hold --mem=237G --time=00:10:00 --no-requeue --job-name=hea-ieee-init -A "$ACCT" -N 1 -n "$NP" ${EXCLUDE:+--exclude="$EXCLUDE"} --array=1-"$N"%"$CONC" \
       --export=ALL,PROJECT,MANIFEST,RUNS,QE_PREFIX,PSEUDO_DIR,NP \
       "$(dirname "$0")/70_hea_ieee_initialization.slurm"
