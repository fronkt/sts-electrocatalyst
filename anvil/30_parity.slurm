#!/bin/bash
# Anvil bring-up step 3: THE GATE. Nothing science-bearing runs on Anvil until
# this passes.
#
# Re-runs one already-banked deck -- probe/Cr_lit3/oosh__1x1_off_magp__g1, the
# fixed-geometry GATE-1 child finished on Vast at 11:44Z on 2026-08-20 -- and
# compares the total energy against the Vast number.
#
# An SCF at fixed geometry is the right parity probe: no BFGS path to diverge,
# one deterministic number out.
#
# WHAT A NON-ZERO DELTA MEANS: the conda builds are byte-identical, so any
# difference is microarchitecture, not software -- Vast is EPYC 7B12 (Zen 2),
# Anvil is EPYC 7763 (Zen 3), and OpenBLAS dispatches different kernels. Expect
# ~1e-8 to 1e-6 Ry. The point is to MEASURE it, not to assume it is zero: this
# project's whole claim is that unmeasured numerical changes are how screens lie.
#
# THRESHOLD BELOW IS A PROPOSAL. The entrant sets thresholds (A7 authorship
# rule); 1e-5 Ry is offered because it is ~30x tighter than GATE-1's own 5 meV
# (3.7e-4 Ry) science tolerance, so platform noise cannot masquerade as drift.
#SBATCH -p shared
#SBATCH -N 1
#SBATCH -n 20
#SBATCH -t 04:00:00
#SBATCH -J anvil-parity
#SBATCH -o logs/parity_%j.out
#SBATCH -e logs/parity_%j.out

set -uo pipefail

REF_E=-1636.57057718            # Ry, Vast box 47662258, 2026-08-20 11:44:23Z
REF_TOTMAG=14.90
REF_ABSMAG=21.28
TOL_RY=${TOL_RY:-1e-5}

QE_PREFIX=${QE_PREFIX:-$PROJECT/qe/env}
PSEUDO_DIR=${PSEUDO_DIR:-$PROJECT/pseudo}
RUNS=${RUNS:-$PROJECT/sts/runs}
DRIVER=${DRIVER:-$PROJECT/queue_r1.sh}

# Parity runs in a COPY. The banked .out must not be touched -- run_one would
# otherwise SKIP on its "JOB DONE", and a parity run must never be able to
# overwrite evidence.
PDIR="$PROJECT/parity/Cr_lit3"
mkdir -p "$PDIR" "$PROJECT/logs"
cp "$RUNS/probe/Cr_lit3/oosh__1x1_off_magp__g1.in" "$PDIR/"

man="$PROJECT/parity/m_parity.txt"
printf '# NP=20 NCONC=1\nCr_lit3 oosh__1x1_off_magp__g1 .in 4\n' > "$man"

export QE_PREFIX PSEUDO_DIR
export RUNS="$PROJECT/parity"
export LOG="$PROJECT/logs/parity_${SLURM_JOB_ID}.log"

echo "== parity run starting $(date -u) on $(hostname)"
bash "$DRIVER" "$man" 20 1
echo "== driver log:"; cat "$LOG"

out="$PDIR/oosh__1x1_off_magp__g1.out"
got=$(grep -a '^!    total energy' "$out" | tail -1 | awk '{print $5}')
tm=$(grep -a 'total magnetization' "$out" | tail -1 | awk '{print $4}')
am=$(grep -a 'absolute magnetization' "$out" | tail -1 | awk '{print $4}')

echo "== PARITY RESULT"
echo "   reference (Vast):  $REF_E Ry   totmag $REF_TOTMAG  absmag $REF_ABSMAG"
echo "   measured  (Anvil): ${got:-NONE} Ry   totmag ${tm:-NONE}  absmag ${am:-NONE}"
[ -n "$got" ] || { echo "PARITY_FAIL no-total-energy"; exit 2; }

python3 - "$got" "$REF_E" "$TOL_RY" <<'PY'
import sys
got, ref, tol = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])
d = got - ref
print(f"   delta = {d:+.3e} Ry  ({d*13605.693:+.4f} meV)")
print("PARITY_PASS" if abs(d) <= tol else "PARITY_FAIL over-threshold")
sys.exit(0 if abs(d) <= tol else 3)
PY
