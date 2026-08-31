#!/usr/bin/env bash
# Submit an A6.5(2)(i) repair manifest (5-field rows: dir job suffix nk
# parent_density_prefix) via 48_a0_repair.slurm. Cloned from 47_submit_a0.sh;
# the generic driver preflight is REPLACED by explicit per-row checks because
# the driver's parser assumes 4-field rows -- everything it would have caught
# (missing deck, stale .out, CRLF) is checked here directly, plus the two
# things only a repair row can get wrong: a deck without startingpot='file',
# and a parent density that is not on disk.
#
#   bash 49_submit_repairs.sh [manifest] [max_concurrent]
#
# REFUSES unless $PROJECT/parity/PARITY_PASS exists (docs/43:1613-1621).
# No FORCE override: every repair deck is bank-bound.
set -euo pipefail

MANIFEST=${1:-$PROJECT/sts/runs/a0/m_a0_repairs.txt}
CONC=${2:-2}
NP=${NP:-128}
export NP

export QE_PREFIX=${QE_PREFIX:-$PROJECT/qe/env}
export PSEUDO_DIR=${PSEUDO_DIR:-$PROJECT/pseudo}
export RUNS=${RUNS:-$PROJECT/sts/runs}
export MANIFEST

[ -f "$MANIFEST" ] || { echo "REFUSE: manifest $MANIFEST not found" >&2; exit 2; }

# --- parity gate (hard; no override) -----------------------------------------
if [ ! -f "$PROJECT/parity/PARITY_PASS" ]; then
  echo "REFUSE: $PROJECT/parity/PARITY_PASS absent." >&2
  exit 2
fi

# --- pseudo preflight evidence must be present beside this script ------------
if [ ! -f "$(dirname "$0")/pseudo_md5_preflight_2026-08-23.md" ]; then
  echo "REFUSE: anvil/pseudo_md5_preflight_2026-08-23.md missing -- A8.5 md5" >&2
  echo "        byte-identity evidence must ride with the launch scripts." >&2
  exit 2
fi

# --- account (same mechanics as 47) ------------------------------------------
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

# --- per-row checks before spending a single SU ------------------------------
while read -r d job suf nk parent extra; do
  [ -n "${parent:-}" ] || { echo "REFUSE: row '$d $job $suf $nk' needs 5 fields" >&2; exit 2; }
  [ -z "${extra:-}" ] || { echo "REFUSE: trailing fields in row '$d $job ... $extra'" >&2; exit 2; }
  case "$nk" in ''|*[!0-9]*) echo "REFUSE: bad nk in row '$d $job'" >&2; exit 2;; esac
  [ $((NP % nk)) -eq 0 ] || { echo "REFUSE: NP=$NP not a multiple of nk=$nk ($d/$job)" >&2; exit 2; }
  deck="$RUNS/$d/${job}${suf}"
  [ -f "$deck" ] || { echo "REFUSE: missing deck $deck" >&2; exit 2; }
  grep -q "startingpot = 'file'" "$deck" || {
    echo "REFUSE: $deck has no startingpot='file' -- not a repair deck" >&2; exit 2; }
  psave="$RUNS/$d/dens/${parent}.save"
  [ -d "$psave" ] || { echo "REFUSE: parent density $psave missing" >&2; exit 2; }
  [ -f "$psave/charge-density.dat" ] || [ -f "$psave/charge-density.hdf5" ] || {
    echo "REFUSE: $psave carries no charge density" >&2; exit 2; }
  out="$RUNS/$d/${job}.out"
  if [ -f "$out" ] && grep -aq "JOB DONE" "$out"; then
    echo "REFUSE: stale $out already carries JOB DONE" >&2; exit 2
  fi
  if grep -q $'\r' "$deck"; then
    echo "REFUSE: CRLF line endings in $deck" >&2; exit 2
  fi
done < "${MANIFEST}.lines"

mkdir -p logs

echo "== submitting repair array 1-$N%$CONC  ($NP cores each, $NP SU/h each)"
sbatch -A "$ACCT" -N 1 -n "$NP" ${EXCLUDE:+--exclude="$EXCLUDE"} --array=1-"$N"%"$CONC" \
       --export=ALL,MANIFEST,RUNS,QE_PREFIX,PSEUDO_DIR,NP \
       "$(dirname "$0")/48_a0_repair.slurm"
