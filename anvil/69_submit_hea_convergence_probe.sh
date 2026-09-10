#!/usr/bin/env bash
# Submit four 1-hour probes held, serially, behind the smearing diagnostic.
# The caller verifies the held allocation and runner bytes before release.
set -euo pipefail
: "${PROJECT:?PROJECT required}"
: "${AFTERANY:?smearing diagnostic job id required}"
[[ "$AFTERANY" =~ ^[1-9][0-9]*$ ]] || { echo "REFUSE: invalid predecessor" >&2; exit 2; }
MANIFEST=${1:-$PROJECT/sts/runs/hea/m_convergence_probe_2026-09-10.txt}
CONC=${2:-1}
NP=${NP:-128}
export MANIFEST NP
export QE_PREFIX=${QE_PREFIX:-$PROJECT/qe/env}
export PSEUDO_DIR=${PSEUDO_DIR:-$PROJECT/pseudo}
export RUNS=${RUNS:-$PROJECT/sts/runs}
export DRIVER=${DRIVER:-$PROJECT/queue_r1.sh}
ROOT="$PROJECT/sts"
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
SPEC="$ROOT/results/hea_convergence_probe_2026-09-10/launch_spec.json"
GUARD="$ROOT/src/dft/hea_convergence_probe_guard.py"
RUNNER="$ROOT/anvil/68_hea_convergence_probe.slurm"
[ "$NP" = 128 ] && [ "$CONC" = 1 ] || { echo "REFUSE: NP128, concurrency1 required" >&2; exit 2; }
[ "$MANIFEST" = "$ROOT/runs/hea/m_convergence_probe_2026-09-10.txt" ] && [ "$RUNS" = "$ROOT/runs" ] || exit 2
[ "$PSEUDO_DIR" = /anvil/projects/x-che260157/pseudo ] || exit 2
[ -f "$PROJECT/parity/PARITY_PASS" ] || { echo "REFUSE: parity evidence absent" >&2; exit 2; }
[ -f "$(dirname "$0")/pseudo_md5_preflight_2026-08-23.md" ] || exit 2
check_hash() { [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ] || { echo "REFUSE: pinned file differs: $1" >&2; exit 2; }; }
check_hash "$SPEC" ea15fcd9030b568b35f98ac0444b8883295d6be229ecf74070ac48f661964f08
check_hash "$MANIFEST" 433715a994fa1511a83e963c55722bc0dc928e0cd06d568cc9c824d80a8423a0
check_hash "$GUARD" 32e0e7a816ad74af8f836f5cfe442182ce778142dcec33bb0c1e659c21f12828
if grep -qai 'NOT LICENSED' "$MANIFEST"; then echo "REFUSE: manifest NOT LICENSED" >&2; exit 2; fi
MEXCL=$(awk -F= '/^# SUBMIT WITH EXCLUDE=/{gsub(/[ \r]/,"",$2); print $2; exit}' "$MANIFEST")
[ -n "$MEXCL" ] || { echo "REFUSE: exclusions header absent" >&2; exit 2; }
_have=",$(printf '%s' "${EXCLUDE:-}" | tr -d ' '),"
for _node in $(printf '%s\n' "$MEXCL" | tr ',' ' '); do
  case "$_have" in *,"$_node",*) ;; *) echo "REFUSE: missing excluded node $_node" >&2; exit 2 ;; esac
done
"$PYTHON" "$GUARD" --spec "$SPEC" --runs "$RUNS"
PREFLIGHT_ONLY=1 LOG=/dev/stdout bash "$DRIVER" "$MANIFEST" "$NP" 1
ACCT=${ACCT:-$(set +o pipefail; mybalance 2>/dev/null | awk '$2=="CPU" {print $1; exit}')}
[ -n "$ACCT" ] || { echo "REFUSE: account absent" >&2; exit 2; }
mkdir -p logs
echo "Submitting HELD 4x1h probes, 512 core-h ceiling, serial afterany:$AFTERANY; no automatic retries"
sbatch --hold --partition=shared --mem=237G --time=01:00:00 --no-requeue --job-name=hea-convergence-probe \
  -A "$ACCT" -N 1 -n "$NP" --exclude="$EXCLUDE" --array=1-4%1 --dependency="afterany:$AFTERANY" \
  --export=ALL,PROJECT,MANIFEST,RUNS,QE_PREFIX,PSEUDO_DIR,NP "$RUNNER"
