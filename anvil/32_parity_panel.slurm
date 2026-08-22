#!/bin/bash
# Anvil bring-up step 3c: parity PANEL -- one Slurm array task per banked deck.
#
# WHY THIS EXISTS. Steps 3 and 3b each asked the platform question of a single
# deck and got opposite answers:
#
#   30_parity.slurm   oosh__1x1_off_magp__g1  (nspin=2)  -8.2818 meV  FAIL
#   31_parity_any     s0_OOH__..._ns1__g1     (nspin=1)  +0.0143 meV  PASS
#
# Neither is enough on its own. The FAIL deck turned out to be one of the two
# rows the LIT-3 GATE-1 review had ALREADY flagged BASIN_DRIFT -- its Vast child
# sits 8.29 meV ABOVE its own Vast parent and carries totmag 14.90 where the
# parent, and every other Cr row in the family, carries 11.00. Asking parity of
# that child measures the drift. The PASS deck is spin-restricted, so it cannot
# rule out that spin polarization itself breaks parity.
#
# This panel closes both holes: three spin-POLARIZED AGREE rows (unique solution,
# parent and child agree to 0.002 meV on Vast) plus the two drifted rows scored
# against BOTH their child and their parent.
#
#   sbatch -A che260157 --array=1-5%5 anvil/32_parity_panel.slurm
#
# Each task is isolated in its own $PROJECT/parity3/t<id> tree, so no task can
# see, overwrite, or race another -- and no banked .out is ever in reach.
#SBATCH -p shared
#SBATCH -N 1
#SBATCH -n 20
#SBATCH -t 04:00:00
#SBATCH -J parity-panel
#SBATCH -o logs/panel_%A_%a.out
#SBATCH -e logs/panel_%A_%a.out

set -uo pipefail

TABLE=${TABLE:-$PROJECT/parity_panel.tsv}
TOL_RY=${TOL_RY:-1e-5}
QE_PREFIX=${QE_PREFIX:-$PROJECT/qe/env}
PSEUDO_DIR=${PSEUDO_DIR:-$PROJECT/pseudo}
SRC_RUNS=${SRC_RUNS:-$PROJECT/sts/runs}
DRIVER=${DRIVER:-$PROJECT/queue_r1.sh}

row=$(grep -vE '^\s*(#|$)' "$TABLE" | sed -n "${SLURM_ARRAY_TASK_ID}p")
[ -n "$row" ] || { echo "FATAL: no row ${SLURM_ARRAY_TASK_ID} in $TABLE"; exit 1; }
IFS=$'\t' read -r DECK_REL REF_CHILD REF_PARENT PAR_TM CLASS <<< "$row"

deck=$(basename "$DECK_REL")
fam=$(basename "$(dirname "$DECK_REL")")
BASE="$PROJECT/parity3/t${SLURM_ARRAY_TASK_ID}"
PDIR="$BASE/$fam"
mkdir -p "$PDIR" "$PROJECT/logs"
cp "$SRC_RUNS/$DECK_REL.in" "$PDIR/"

man="$BASE/m_parity.txt"
printf '# NP=20 NCONC=1\n%s %s .in 4\n' "$fam" "$deck" > "$man"

export QE_PREFIX PSEUDO_DIR
export RUNS="$BASE"
export LOG="$PROJECT/logs/panel_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}.log"

echo "== panel task ${SLURM_ARRAY_TASK_ID}: $DECK_REL  [$CLASS]"
echo "== starting $(date -u) on $(hostname)"
bash "$DRIVER" "$man" 20 1
echo "== driver log:"; cat "$LOG"

out="$PDIR/$deck.out"
got=$(grep -a '^!    total energy' "$out" | tail -1 | awk '{print $5}')
tm=$(grep -a 'total magnetization' "$out" | tail -1 | awk '{print $4}')
it1=$(grep -aE '^ *total energy *=' "$out" | head -1 | awk '{print $4}')
nit=$(grep -a 'convergence has been achieved' "$out" | tail -1 | awk '{print $6}')

echo "== PANEL RESULT"
echo "   deck            $DECK_REL   [$CLASS]"
echo "   anvil E         ${got:-NONE} Ry   totmag ${tm:-.}  (${nit:-?} iters, iter-1 ${it1:-?})"
echo "   vast child      $REF_CHILD Ry"
echo "   vast parent     $REF_PARENT Ry   totmag $PAR_TM"
[ -n "$got" ] || { echo "PANEL_FAIL no-total-energy"; exit 2; }

python3 - "$got" "$REF_CHILD" "$REF_PARENT" "$TOL_RY" "$CLASS" "$tm" "$PAR_TM" <<'PY'
import sys
got, rc, rp, tol = (float(x) for x in sys.argv[1:5])
cls, tm, ptm = sys.argv[5], sys.argv[6], sys.argv[7]
dc, dp = got - rc, got - rp
print(f"   d(vs child)   = {dc:+.3e} Ry  ({dc*13605.693:+.4f} meV)  {'in' if abs(dc)<=tol else 'OVER'} {tol:g}")
print(f"   d(vs parent)  = {dp:+.3e} Ry  ({dp*13605.693:+.4f} meV)  {'in' if abs(dp)<=tol else 'OVER'} {tol:g}")
print(f"   totmag anvil={tm}  vast-parent={ptm}")
# An AGREE row must reproduce its child: that is the platform test, full stop.
# A BASIN_DRIFT row has no trustworthy child, so it is scored against its parent
# and is INFORMATIVE ONLY -- it can never open the gate.
if cls == "AGREE":
    ok = abs(dc) <= tol
    print("PANEL_PASS" if ok else "PANEL_FAIL over-threshold")
    sys.exit(0 if ok else 3)
print("PANEL_INFO basin-drift row, not gate-bearing")
PY
