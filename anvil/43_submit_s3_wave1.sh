#!/usr/bin/env bash
# Submit the S3 wave-1 manifest (runs/s3/m_s3_wave1.txt, 55 decks: 46 relax +
# 9 SCF) as a Slurm array at the A8.6 shape: 128 ranks, -nk per row, -N 1, 48 h.
# Adapted from 41_submit_wave.sh; the runner is 42_s3_wave1.slurm (direct
# mpirun, NO --bind-to flag anywhere -- binding is an undecided registration
# item, A8.6 / docs/48).
#
#   bash 43_submit_s3_wave1.sh [manifest] [max_concurrent]
#
# REFUSES unless $PROJECT/parity/PARITY_PASS exists -- the only thing that makes
# an Anvil number comparable to a Vast number is that gate (docs/43:1613-1621).
# No FORCE override here: every deck in this manifest is intended to be banked.
set -euo pipefail

MANIFEST=${1:-$PROJECT/sts/runs/s3/m_s3_wave1.txt}
CONC=${2:-6}
NP=${NP:-128}
export NP

export QE_PREFIX=${QE_PREFIX:-$PROJECT/qe/env}
export PSEUDO_DIR=${PSEUDO_DIR:-$PROJECT/pseudo}
export RUNS=${RUNS:-$PROJECT/sts/runs}
export DRIVER=${DRIVER:-$PROJECT/queue_r1.sh}
export MANIFEST

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
ACCT=${ACCT:-$(mybalance 2>/dev/null | awk '$2=="CPU" {print $1; exit}')}
[ -n "${ACCT:-}" ] || { echo "REFUSE: could not resolve account; set ACCT=..." >&2; exit 2; }
echo "== account:  $ACCT"

# --- runnable lines ----------------------------------------------------------
grep -vE '^\s*(#|$)' "$MANIFEST" > "${MANIFEST}.lines"
N=$(wc -l < "${MANIFEST}.lines")
[ "$N" -gt 0 ] || { echo "REFUSE: no runnable lines in $MANIFEST" >&2; exit 2; }

# --- per-row nk sanity before spending a single SU ---------------------------
while read -r d job suf nk extra; do
  [ -z "${extra:-}" ] || { echo "REFUSE: trailing fields in row '$d $job $suf $nk $extra'" >&2; exit 2; }
  case "$nk" in ''|*[!0-9]*) echo "REFUSE: bad nk in row '$d $job $suf $nk'" >&2; exit 2;; esac
  [ $((NP % nk)) -eq 0 ] || { echo "REFUSE: NP=$NP not a multiple of nk=$nk ($d/$job)" >&2; exit 2; }
  [ -f "$RUNS/$d/${job}${suf}" ] || { echo "REFUSE: missing deck $RUNS/$d/${job}${suf}" >&2; exit 2; }
done < "${MANIFEST}.lines"

# --- the driver's own dry preflight (nothing launched) -----------------------
# Catches stale .out, CRLF decks, missing pseudopotentials and the NP-vs-
# manifest-directive mismatch, exactly as 41_submit_wave.sh does. The driver is
# used here for its CHECKS only; the launch path is 42_s3_wave1.slurm.
echo "== preflight (nothing launched)"
PREFLIGHT_ONLY=1 LOG=/dev/stdout bash "$DRIVER" "$MANIFEST" "$NP" 1 || {
  echo "REFUSE: preflight failed -- fix the refusals above before submitting." >&2; exit 2; }

# --- Slurm stdout dir: 42's `#SBATCH -o logs/...` is relative to THIS cwd, and
# Slurm fails a task whose output file cannot be opened -- create it here so the
# launch does not depend on 20_stage.sh having run from $PROJECT.
mkdir -p logs

echo "== submitting array 1-$N%$CONC  ($NP cores each, $NP SU/h each)"
echo "   worst-case burn at 48 h walltime: $((N * NP * 48)) SU"
sbatch -A "$ACCT" -N 1 -n "$NP" --array=1-"$N"%"$CONC" \
       --export=ALL,MANIFEST,RUNS,QE_PREFIX,PSEUDO_DIR,NP \
       "$(dirname "$0")/42_s3_wave1.slurm"
