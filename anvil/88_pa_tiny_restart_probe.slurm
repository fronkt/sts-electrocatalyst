#!/bin/bash
# Tiny optimizer test only: one shared job, total ceiling8SU, no requeue/retry.
#SBATCH --account=che260157
#SBATCH --partition=shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=6G
#SBATCH --time=02:00:00
#SBATCH --job-name=pa-tiny-restart
#SBATCH --no-requeue
#SBATCH --output=/anvil/projects/x-che260157/sts_pa_probe_2026-10-03/probe_%j.log
#SBATCH --error=/anvil/projects/x-che260157/sts_pa_probe_2026-10-03/probe_%j.log
set -euo pipefail
PROBE_ROOT=/anvil/projects/x-che260157/sts_pa_probe_2026-10-03
RUNNER="$PROBE_ROOT/src/dft/pa_tiny_restart_probe.py"
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
QE=/anvil/projects/x-che260157/qe/env/bin/pw.x
UPF=/anvil/projects/x-che260157/pseudo/H.pbe-rrkjus_psl.1.0.0.UPF
OUTPUT=/anvil/projects/x-che260157/sts_pa_probe_2026-10-03/tiny_results
[[ ! -e "$OUTPUT" && ! -L "$OUTPUT" ]] || { echo 'REFUSE: prior output'; exit 2; }
[[ "$(sha256sum "$RUNNER" | awk '{print $1}')" = 5cec00a14827111161d90a5b41cf01dff8e06a1b1bc9c21ccfe4529f56e0cf3a ]] || { echo 'REFUSE: runner hash'; exit 2; }
# The runner checks the actual scheduler job and AllocTRES before any QE call.
export SLURM_JOB_TIME_LIMIT=02:00:00
export SLURM_JOB_ACCOUNT=che260157
export SLURM_JOB_PARTITION=shared
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_DYNAMIC=FALSE
exec "$PYTHON" "$RUNNER" --output-dir "$OUTPUT" --qe-binary "$QE" --pseudo "$UPF" \
  --expected-qe-sha256 1d66c7856f5d6b3cd9c66b8578e01512b16bbe907b4360e54234890712ccd6a1 \
  --expected-pseudo-sha256 27f8a7e87851d59a2698237d6ab4578d62950640f4f175781b015a0ce731f962
