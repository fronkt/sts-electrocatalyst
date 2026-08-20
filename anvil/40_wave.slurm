#!/bin/bash
# Anvil wave runner -- ONE Slurm array task per deck.
#
# WHY AN ARRAY AND NOT NCONC>1:
#   * queue_r1.sh REFUSES any invocation whose NP/NCONC disagree with the
#     manifest's `# NP=<n> NCONC=<n>` directive (finding N6). Every registered
#     manifest declares NCONC=1. An array keeps that guard untouched: each task
#     runs the driver at exactly NP=20 NCONC=1, its declared shape.
#   * SU-wise an array is strictly cheaper than one fat allocation. A single
#     120-core job is billed 120 SU/h for its whole walltime including the tail
#     where 5 of 6 slots idle; 6 x 20-core tasks are billed only while each runs.
#   * A crashed deck kills one task, not the wave.
#
# Charging: `shared` bills max(cores, ceil(mem_GB/2)) SU per hour. 20 cores with
# the default ~2 GB/core is 20 SU/h; measured pw.x RSS is ~0.5 GB/rank, so cores
# dominate and the rate is 20 SU/h flat.
#SBATCH -p shared
#SBATCH -N 1
#SBATCH -n 20
#SBATCH -t 48:00:00
#SBATCH -o logs/wave_%A_%a.out
#SBATCH -e logs/wave_%A_%a.out

set -uo pipefail

: "${MANIFEST:?MANIFEST must be exported by the submit wrapper}"
: "${RUNS:?RUNS must be exported by the submit wrapper}"
: "${QE_PREFIX:?QE_PREFIX must be exported by the submit wrapper}"

LINES="${MANIFEST}.lines"
row=$(sed -n "${SLURM_ARRAY_TASK_ID}p" "$LINES")
[ -n "$row" ] || { echo "FATAL: no row ${SLURM_ARRAY_TASK_ID} in $LINES"; exit 1; }

# A one-line manifest carrying the SAME directive the parent declared, so the
# NP-vs-manifest guard is exercised per task rather than bypassed.
task_manifest="$(mktemp -p "${SCRATCH:-/tmp}" m_task_XXXXXX.txt)"
grep -m1 -E '^# NP=[0-9]+ NCONC=[0-9]+$' "$MANIFEST" > "$task_manifest"
echo "$row" >> "$task_manifest"

export QE_PREFIX RUNS
export LOG="${RUNS}/../logs/queue_r1.${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}.log"
mkdir -p "$(dirname "$LOG")"

echo "TASK ${SLURM_ARRAY_TASK_ID} row='${row}' node=$(hostname) $(date -u)"
bash "${DRIVER:?DRIVER must be exported}" "$task_manifest" 20 1
rc=$?
rm -f "$task_manifest"
echo "TASK ${SLURM_ARRAY_TASK_ID} driver_rc=$rc $(date -u)"
seff "${SLURM_JOB_ID}" 2>/dev/null || true
exit $rc
