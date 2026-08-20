#!/usr/bin/env bash
# Anvil bring-up step 4: submit a registered manifest as a Slurm array.
#
#   bash 41_submit_wave.sh $PROJECT/sts/runs/s0/m_s0_np20.txt [max_concurrent]
#
# Refuses unless the parity gate has passed, because the ONLY thing that makes
# an Anvil number comparable to a Vast number is that gate.
set -euo pipefail

MANIFEST=${1:?usage: 41_submit_wave.sh <manifest> [max_concurrent]}
CONC=${2:-8}

export QE_PREFIX=${QE_PREFIX:-$PROJECT/qe/env}
export PSEUDO_DIR=${PSEUDO_DIR:-$PROJECT/pseudo}
export RUNS=${RUNS:-$PROJECT/sts/runs}
export DRIVER=${DRIVER:-$PROJECT/queue_r1.sh}
export MANIFEST

# --- gate ---------------------------------------------------------------------
if [ ! -f "$PROJECT/parity/PARITY_PASS" ]; then
  echo "REFUSE: $PROJECT/parity/PARITY_PASS absent." >&2
  echo "        Run 30_parity.slurm and, if it passes, touch that file." >&2
  echo "        Override with FORCE=1 only for a run you will not bank." >&2
  [ "${FORCE:-0}" = 1 ] || exit 2
fi

# --- account ------------------------------------------------------------------
ACCT=${ACCT:-$(mybalance 2>/dev/null | awk 'NR>1 && $1 !~ /^-/ {print $1; exit}')}
[ -n "${ACCT:-}" ] || { echo "REFUSE: could not resolve account; set ACCT=..." >&2; exit 2; }
echo "== account:  $ACCT"

# --- runnable lines -----------------------------------------------------------
grep -vE '^\s*(#|$)' "$MANIFEST" > "${MANIFEST}.lines"
N=$(wc -l < "${MANIFEST}.lines")
[ "$N" -gt 0 ] || { echo "REFUSE: no runnable lines in $MANIFEST" >&2; exit 2; }

# --- dry preflight before spending a single SU --------------------------------
# The driver's own preflight, run once over the WHOLE manifest, on the login
# node, launching nothing. Catches missing dirs, stale .out, CRLF decks, bad nk
# and missing pseudopotentials before the array exists.
echo "== preflight (nothing launched)"
PREFLIGHT_ONLY=1 LOG=/dev/stdout bash "$DRIVER" "$MANIFEST" 20 1 || {
  echo "REFUSE: preflight failed -- fix the refusals above before submitting." >&2; exit 2; }

echo "== submitting array 1-$N%$CONC  (20 cores each, 20 SU/h each)"
echo "   worst-case burn at 48 h walltime: $((N * 20 * 48)) SU"
sbatch -A "$ACCT" --array=1-"$N"%"$CONC" \
       --export=ALL,MANIFEST,RUNS,QE_PREFIX,PSEUDO_DIR,DRIVER \
       "$(dirname "$0")/40_wave.slurm"
