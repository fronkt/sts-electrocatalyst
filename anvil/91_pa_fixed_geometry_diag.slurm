#!/bin/bash
# Fixed-geometry diagnostic: one registered group per singleton 128-core job.
# No array, dependency chain, retry, requeue, production relaxation or melt release.
# The group's --time and --job-name are given on the sbatch line; the controller
# refuses a live TimeLimit above the group's registered limit.
#SBATCH --account=che260157
#SBATCH --partition=wholenode
#SBATCH --nodes=1
#SBATCH --ntasks=128
#SBATCH --cpus-per-task=1
#SBATCH --mem=200G
#SBATCH --no-requeue
#SBATCH --output=/anvil/projects/x-che260157/sts_pa_fixed_geometry_diag_2026-10-05/diag_%x_%j.log
#SBATCH --error=/anvil/projects/x-che260157/sts_pa_fixed_geometry_diag_2026-10-05/diag_%x_%j.log
set -euo pipefail
BASE=/anvil/projects/x-che260157/sts_pa_fixed_geometry_diag_2026-10-05
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
QE_ENV=/anvil/projects/x-che260157/qe/env
SPEC="$BASE/launch_spec.json"
case "${STS_DIAG_GROUP:-}" in replay|ladder|fresh) ;; *) echo 'REFUSE: registered group absent'; exit 2 ;; esac
[[ "${STS_DIAG_SPEC_SHA256:-}" =~ ^[0-9a-f]{64}$ ]] || { echo 'REFUSE: exact reviewed spec pin absent'; exit 2; }
[[ ! -e "$BASE/groups/$STS_DIAG_GROUP" && ! -L "$BASE/groups/$STS_DIAG_GROUP" ]] || { echo 'REFUSE: group already ran'; exit 2; }
[[ "$(sha256sum "$SPEC" | awk '{print $1}')" = "$STS_DIAG_SPEC_SHA256" ]] || { echo 'REFUSE: spec byte drift'; exit 2; }
export PATH="$QE_ENV/bin:$PATH"
export LD_LIBRARY_PATH="$QE_ENV/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export OMP_NUM_THREADS=1 OMP_THREAD_LIMIT=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 OMP_DYNAMIC=FALSE MKL_DYNAMIC=FALSE MAX_XML_STEPS=0
exec "$PYTHON" "$BASE/src/dft/pa_fixed_geometry_diag.py" \
  --spec "$SPEC" --spec-sha256 "$STS_DIAG_SPEC_SHA256" --group "$STS_DIAG_GROUP"
