#!/bin/bash
# Four independent 60-iteration probes; no retries, requeue or scratch deletion.
#SBATCH -p shared
#SBATCH -N 1
#SBATCH -n 128
#SBATCH --mem=237G
#SBATCH -t 01:00:00
#SBATCH -J hea-convergence-probe
#SBATCH -o logs/hea_convergence_probe_%A_%a.out
#SBATCH -e logs/hea_convergence_probe_%A_%a.out
set -uo pipefail
set -C
export LC_ALL=C
: "${PROJECT:?PROJECT required}"
: "${RUNS:?RUNS required}"
: "${MANIFEST:?MANIFEST required}"
: "${QE_PREFIX:?QE_PREFIX required}"
: "${PSEUDO_DIR:?PSEUDO_DIR required}"
[ "${NP:-}" = 128 ] || exit 2
ROOT="$PROJECT/sts"
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
SPEC="$ROOT/results/hea_convergence_probe_2026-09-10/launch_spec.json"
GUARD="$ROOT/src/dft/hea_convergence_probe_guard.py"
FROZEN="$ROOT/src/dft/hea_numerical_guard.py"
QC="$ROOT/src/dft/hea_followup_qc.py"
FORCE="$ROOT/src/dft/hea_force_audit.py"
[ "$RUNS" = "$ROOT/runs" ] && [ "$MANIFEST" = "$ROOT/runs/hea/m_convergence_probe_2026-09-10.txt" ] || exit 2
[ "$PSEUDO_DIR" = /anvil/projects/x-che260157/pseudo ] || exit 2
export PATH="$QE_PREFIX/bin:$PATH"
export LD_LIBRARY_PATH="$QE_PREFIX/lib:${LD_LIBRARY_PATH:-}"
export OMP_NUM_THREADS=1 ESPRESSO_PSEUDO="$PSEUDO_DIR"
MPI=$(command -v mpirun) || exit 2
PW="$QE_PREFIX/bin/pw.x"
PROJECTION="$QE_PREFIX/bin/projwfc.x"
check_hash() { [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ] || { echo "REFUSE: pinned file differs: $1" >&2; exit 2; }; }
check_hash "$SPEC" ea15fcd9030b568b35f98ac0444b8883295d6be229ecf74070ac48f661964f08
check_hash "$MANIFEST" 433715a994fa1511a83e963c55722bc0dc928e0cd06d568cc9c824d80a8423a0
check_hash "$GUARD" 32e0e7a816ad74af8f836f5cfe442182ce778142dcec33bb0c1e659c21f12828
check_hash "$FROZEN" 98d866553566d9e8ab660535f5bbc0c33228f5160df59eda9f41de9c85ee5f9a
check_hash "$QC" ef9b50193f46034036b892263a3ee139426d912b2098ebdc5a897a82dc2769da
check_hash "$FORCE" bddbe7ba3bed9874e723d88f8bdab724bb4e83178f1f75bbc3a1f4034b9fd5d7
check_hash "$MPI" a256bdcef89bdc61ba870e823056c51df868b4db48ab345a14278a7fe79ed75d
check_hash "$PW" 1d66c7856f5d6b3cd9c66b8578e01512b16bbe907b4360e54234890712ccd6a1
check_hash "$PROJECTION" 456387be5ee32f358bc9835240b2e8bd1f8144a27a8e116731a1463dbf78ac85
row=${SLURM_ARRAY_TASK_ID:-}
[[ "$row" =~ ^[1-4]$ ]] || exit 2
prepared=$("$PYTHON" "$GUARD" --spec "$SPEC" --runs "$RUNS" --row "$row" --prepare) || exit 2
read -r dir job suffix nk prefix arm <<< "$prepared"
cd "$RUNS/$dir" || exit 2
scfrc=255
prc=''
finish() {
  local code=$1
  local args=(--spec "$SPEC" --runs "$RUNS" --row "$row" --summarize --scf-exit "$scfrc")
  [ -z "$prc" ] || args+=(--projection-exit "$prc")
  [ "$code" != 0 ] || args+=(--require-complete)
  "$PYTHON" "$GUARD" "${args[@]}" || { echo "PROBE EVIDENCE CHECK FAILED; all scratch retained"; exit 20; }
  exit "$code"
}
trap 'echo "INTERRUPTED; preserving probe evidence"; finish 143' TERM HUP
trap 'echo "INTERRUPTED; preserving probe evidence"; finish 130' INT
echo "PROBE $job arm=$arm: 60 iterations, max_seconds3300, one-hour allocation, no retry"
echo "node=$(hostname) started=$(date -u)"
"$MPI" --oversubscribe -np 128 "$PW" -nk 8 -in "${job}.run.in" > "${job}.out" 2>&1 </dev/null
scfrc=$?
"$PYTHON" "$FROZEN" --startup-output "${job}.out" --mode recovery
startup_rc=$?
"$PYTHON" "$QC" --input "${job}.run.in" --output "${job}.out" --json "${job}.scf_qc.json"
qc_rc=$?
if [ "$scfrc" -ne 0 ] || [ "$startup_rc" -ne 0 ] || [ "$qc_rc" -ne 0 ]; then
  echo "SCF REJECTED; diagnostic history retained, no projection"
  finish 16
fi
printf "&PROJWFC\n  prefix = '%s'\n  outdir = './tmp_%s'\n  lsym = .true.\n/\n" "$prefix" "$job" > "${job}.projwfc.in" || finish 17
"$MPI" --oversubscribe -np 128 "$PROJECTION" -nk 8 -in "${job}.projwfc.in" > "${job}.projwfc.out" 2>&1 </dev/null
prc=$?
"$PYTHON" "$QC" --input "${job}.run.in" --output "${job}.out" --projection "${job}.projwfc.out" --json "${job}.qc.json"
qc_rc=$?
if [ "$prc" -ne 0 ] || [ "$qc_rc" -ne 0 ]; then finish 17; fi
finish 0
