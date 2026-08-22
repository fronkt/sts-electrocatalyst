#!/bin/bash
# Anvil bring-up step 3b: PARAMETERIZED parity gate.
#
# WHY THIS EXISTS. 30_parity.slurm ran probe/Cr_lit3/oosh__1x1_off_magp__g1 and
# returned PARITY_FAIL at -8.28 meV. Diagnosis (2026-08-22, job 20082478):
#
#   iter 1  total energy   anvil -1638.41386991   vast -1638.41386986   -> 5e-8 Ry
#   iter 13 magnetization  anvil 11.10            vast 11.00            -> paths split
#   final   totmag         anvil 11.00            vast 14.90            -> 8.28 meV
#
# The 5e-8 Ry seed is the expected Zen2->Zen3 OpenBLAS kernel difference. The
# 8.28 meV is NOT platform noise: that deck is nspin=2 with free magnetization and
# has (at least) two self-consistent magnetic solutions, so an arbitrarily small
# perturbation selects a different basin. A spin-multistable deck cannot measure
# platform parity -- it measures its own multistability.
#
# So the platform question gets asked of a deck with a UNIQUE solution. Default is
# the nspin=1 sibling from the same family and size class.
#
# Override any of DECK_REL / REF_E / TOL_RY at submit time:
#   sbatch -A che260157 --export=ALL,DECK_REL=probe/X/y,REF_E=-1.0 anvil/31_parity_any.slurm
#SBATCH -p shared
#SBATCH -N 1
#SBATCH -n 20
#SBATCH -t 04:00:00
#SBATCH -J anvil-parity2
#SBATCH -o logs/parity2_%j.out
#SBATCH -e logs/parity2_%j.out

set -uo pipefail

DECK_REL=${DECK_REL:-probe/Cr_lit3/s0_OOH__1x1_yaw90_ns1__g1}
REF_E=${REF_E:--1635.73491496}
TOL_RY=${TOL_RY:-1e-5}

QE_PREFIX=${QE_PREFIX:-$PROJECT/qe/env}
PSEUDO_DIR=${PSEUDO_DIR:-$PROJECT/pseudo}
RUNS=${RUNS:-$PROJECT/sts/runs}
DRIVER=${DRIVER:-$PROJECT/queue_r1.sh}

deck=$(basename "$DECK_REL")
fam=$(basename "$(dirname "$DECK_REL")")
PDIR="$PROJECT/parity2/$fam"
mkdir -p "$PDIR" "$PROJECT/logs"
cp "$RUNS/$DECK_REL.in" "$PDIR/"

man="$PROJECT/parity2/m_parity.txt"
printf '# NP=20 NCONC=1\n%s %s .in 4\n' "$fam" "$deck" > "$man"

export QE_PREFIX PSEUDO_DIR
export RUNS="$PROJECT/parity2"
export LOG="$PROJECT/logs/parity2_${SLURM_JOB_ID}.log"

echo "== parity2 deck: $DECK_REL"
echo "== starting $(date -u) on $(hostname)"
bash "$DRIVER" "$man" 20 1
echo "== driver log:"; cat "$LOG"

out="$PDIR/$deck.out"
got=$(grep -a '^!    total energy' "$out" | tail -1 | awk '{print $5}')
it1=$(grep -aE '^ *total energy *=' "$out" | head -1 | awk '{print $4}')

echo "== PARITY RESULT ($DECK_REL)"
echo "   reference (Vast):  $REF_E Ry"
echo "   measured  (Anvil): ${got:-NONE} Ry"
echo "   anvil iter-1 E:    ${it1:-NONE} Ry"
[ -n "$got" ] || { echo "PARITY_FAIL no-total-energy"; exit 2; }

python3 - "$got" "$REF_E" "$TOL_RY" <<'PY'
import sys
got, ref, tol = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])
d = got - ref
print(f"   delta = {d:+.3e} Ry  ({d*13605.693:+.4f} meV)")
print("PARITY_PASS" if abs(d) <= tol else "PARITY_FAIL over-threshold")
sys.exit(0 if abs(d) <= tol else 3)
PY
