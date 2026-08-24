#!/usr/bin/env bash
# Submit the A8.3 retention chains (runs/chains/m_chains.txt) via 44_chain.slurm.
#   bash 45_submit_chains.sh [manifest] [max_concurrent]
# Gates identical in spirit to 43: PARITY_PASS hard, pseudo preflight evidence
# beside this script, EXCLUDE=nodelist supported (sick nodes a024/a088).
set -euo pipefail
MANIFEST=${1:-$PROJECT/sts/runs/chains/m_chains.txt}
CONC=${2:-3}
NP=${NP:-128}
export QE_PREFIX=${QE_PREFIX:-$PROJECT/qe/env}
export PSEUDO_DIR=${PSEUDO_DIR:-$PROJECT/pseudo}
export RUNS_ROOT=${RUNS_ROOT:-$PROJECT/sts}
export MANIFEST NP
[ -f "$MANIFEST" ] || { echo "REFUSE: no manifest" >&2; exit 2; }
[ -f "$PROJECT/parity/PARITY_PASS" ] || { echo "REFUSE: PARITY_PASS absent" >&2; exit 2; }
[ -f "$(dirname "$0")/pseudo_md5_preflight_2026-08-23.md" ] || { echo "REFUSE: pseudo preflight evidence missing" >&2; exit 2; }
ACCT=${ACCT:-$(set +o pipefail; mybalance 2>/dev/null | awk '$2=="CPU" {print $1; exit}')}
[ -n "${ACCT:-}" ] || { echo "REFUSE: no account" >&2; exit 2; }
grep -vE '^\s*(#|$)' "$MANIFEST" > "${MANIFEST}.lines"
N=$(wc -l < "${MANIFEST}.lines")
[ "$N" -gt 0 ] || { echo "REFUSE: empty" >&2; exit 2; }
while read -r d rdeck rprefix fdeck fprefix nk extra; do
  [ -z "${extra:-}" ] || { echo "REFUSE: trailing fields" >&2; exit 2; }
  case "$nk" in ''|*[!0-9]*) echo "REFUSE: bad nk" >&2; exit 2;; esac
  [ $((NP % nk)) -eq 0 ] || { echo "REFUSE: NP%nk ($d)" >&2; exit 2; }
  [ -f "$RUNS_ROOT/$d/$rdeck" ] || { echo "REFUSE: missing $d/$rdeck" >&2; exit 2; }
  [ -f "$RUNS_ROOT/$d/$fdeck" ] || { echo "REFUSE: missing $d/$fdeck" >&2; exit 2; }
done < "${MANIFEST}.lines"
mkdir -p logs
echo "== submitting chains 1-$N%$CONC (acct $ACCT${EXCLUDE:+, exclude $EXCLUDE})"
sbatch -A "$ACCT" -N 1 -n "$NP" ${EXCLUDE:+--exclude="$EXCLUDE"} --array=1-"$N"%"$CONC" \
       --export=ALL,MANIFEST,RUNS_ROOT,QE_PREFIX,PSEUDO_DIR,NP \
       "$(dirname "$0")/44_chain.slurm"
