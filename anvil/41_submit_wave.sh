#!/usr/bin/env bash
# Anvil bring-up step 4: submit a registered manifest as a Slurm array.
#
#   bash 41_submit_wave.sh $PROJECT/sts/runs/s0/m_s0_np20.txt [max_concurrent] [ranks]
#
# Refuses unless the parity gate has passed, because the ONLY thing that makes
# an Anvil number comparable to a Vast number is that gate.
set -euo pipefail

MANIFEST=${1:?usage: 41_submit_wave.sh <manifest> [max_concurrent] [ranks]}
CONC=${2:-8}
# Ranks per deck. The driver refuses any NP that disagrees with the manifest's
# own '# NP=<n> NCONC=<n>' directive, so widening a wave is a deliberate two-step:
# edit the directive, then pass the matching NP here. That is the guard working,
# not an obstacle -- a manifest's max_seconds were sized at its declared NP.
NP=${3:-20}
export NP

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
# mybalance prints a blank line, then a two-line header, then '====', then the
# rows; 'NR>1' landed on the word "Allocation". Key on the CPU row instead.
ACCT=${ACCT:-$(mybalance 2>/dev/null | awk '$2=="CPU" {print $1; exit}')}
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

# --- runnable lines -----------------------------------------------------------
grep -vE '^\s*(#|$)' "$MANIFEST" > "${MANIFEST}.lines"
N=$(wc -l < "${MANIFEST}.lines")
[ "$N" -gt 0 ] || { echo "REFUSE: no runnable lines in $MANIFEST" >&2; exit 2; }

# --- dry preflight before spending a single SU --------------------------------
# The driver's own preflight, run once over the WHOLE manifest, on the login
# node, launching nothing. Catches missing dirs, stale .out, CRLF decks, bad nk
# and missing pseudopotentials before the array exists.
echo "== preflight (nothing launched)"
PREFLIGHT_ONLY=1 LOG=/dev/stdout bash "$DRIVER" "$MANIFEST" "$NP" 1 || {
  echo "REFUSE: preflight failed -- fix the refusals above before submitting." >&2; exit 2; }

echo "== submitting array 1-$N%$CONC  ($NP cores each, $NP SU/h each)"
echo "   worst-case burn at 48 h walltime: $((N * NP * 48)) SU"
sbatch -A "$ACCT" -n "$NP" ${EXCLUDE:+--exclude="$EXCLUDE"} --array=1-"$N"%"$CONC" \
       --export=ALL,MANIFEST,RUNS,QE_PREFIX,PSEUDO_DIR,DRIVER,NP \
       "$(dirname "$0")/40_wave.slurm"
