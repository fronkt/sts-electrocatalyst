#!/bin/bash
# Approved one-boundary diagnostic only: one128-core16h job, <=2048CPU SU.
# No array, dependency chain, retry, requeue, production relaxation or melt release.
#SBATCH --account=che260157
#SBATCH --partition=wholenode
#SBATCH --nodes=1
#SBATCH --ntasks=128
#SBATCH --cpus-per-task=1
#SBATCH --mem=200G
#SBATCH --time=16:00:00
#SBATCH --job-name=pa-catalyst-boundary
#SBATCH --no-requeue
#SBATCH --output=/anvil/projects/x-che260157/sts_pa_catalyst_2026-10-03/trial_%j.log
#SBATCH --error=/anvil/projects/x-che260157/sts_pa_catalyst_2026-10-03/trial_%j.log
set -euo pipefail
TRIAL_PARENT=/anvil/projects/x-che260157/sts_pa_catalyst_2026-10-03
PHASE="$TRIAL_PARENT/results/pa_catalyst_trial_2026-10-03"
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
QE_ENV=/anvil/projects/x-che260157/qe/env
SPEC="$PHASE/launch_spec.json"
[[ "${STS_PA_SPEC_SHA256:-}" =~ ^[0-9a-f]{64}$ ]] || { echo 'REFUSE: exact reviewed spec pin absent'; exit 2; }
[[ ! -e "$TRIAL_PARENT/trial_results" && ! -L "$TRIAL_PARENT/trial_results" ]] || { echo 'REFUSE: prior trial output'; exit 2; }
[[ "$(sha256sum "$SPEC" | awk '{print $1}')" = "$STS_PA_SPEC_SHA256" ]] || { echo 'REFUSE: spec byte drift'; exit 2; }
export PATH="$QE_ENV/bin:$PATH"
export LD_LIBRARY_PATH="$QE_ENV/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export OMP_NUM_THREADS=1 OMP_THREAD_LIMIT=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 OMP_DYNAMIC=FALSE MKL_DYNAMIC=FALSE MAX_XML_STEPS=0
# The controller verifies actual RUNNING AllocTRES, immutable dependencies and
# full per-call time before each pw.x invocation; requested resources are not proof.
exec "$PYTHON" "$TRIAL_PARENT/src/dft/pa_catalyst_trial.py" \
  --spec "$SPEC" --spec-sha256 "$STS_PA_SPEC_SHA256"
