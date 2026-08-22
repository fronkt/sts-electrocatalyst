#!/bin/bash
# Anvil sizing test: how fast is ONE S3-class relax, and does it get cheaper wide?
#
# WHY. S0 gate (g) measured the 2x1v TiO2 relax at 8h00m WALL on 20 ranks and it
# was STILL NOT CONVERGED -- 11 ionic steps, total force 0.0298 against a 0.005
# target, stopped clean on max_seconds. That measurement was taken on Vast box
# 47662258 (EPYC 7B12 / Zen 2), which no longer exists. Every S3 schedule and SU
# figure in anvil/README.md descends from a 4 h/relax estimate that gate (g)
# already falsified, and none of it has ever been measured on Anvil hardware.
#
# Two questions, one job:
#   1. What is a 2x1v relax ionic step worth on Anvil at the production shape
#      (20 ranks, -nk 4)? That re-prices S3 in SU and in days-to-Oct-15.
#   2. Does going wide help? `shared` bills cores x hours, so if pw.x scales
#      linearly the SU cost is FLAT and the wall-clock is divided. The deck has a
#      4x4x1 mesh = 16 k-points with nosym, so -nk can go to 16: four times the
#      pools at the same plane-wave decomposition, which is the cheap axis.
#      If that holds, S3's wall-clock drops ~4x for the same spend.
#
# Also tests `--bind-to none` (the driver's setting, inherited from Vast's
# container where binding failed) against `--bind-to core` on a dual-socket
# 64-core-per-socket EPYC 7763, where letting ranks migrate across NUMA domains
# is a real cost. Binding changes placement, not rank count or reduction order,
# so it cannot change a number -- only the clock.
#
# NOTHING HERE IS BANKED. No .out from this job is science; the decks write into
# $PROJECT/scaling and are never mirrored back. That is why it does not need the
# parity gate: it measures the machine, not the chemistry.
#
# Submitted one job per arm by 51_submit_scaling.sh, because -n must MATCH the
# arm's rank count: a 128-core allocation running 20 ranks is billed for 128.
#SBATCH -p shared
#SBATCH -N 1
#SBATCH -t 01:10:00
#SBATCH -J s3-scaling
#SBATCH -o logs/scaling_%j.out
#SBATCH -e logs/scaling_%j.out

set -uo pipefail

NP=${NP:?NP must be exported}
NK=${NK:?NK must be exported}
BIND=${BIND:-none}
ARM=${ARM:-np${NP}_nk${NK}_${BIND}}

QE_PREFIX=${QE_PREFIX:-$PROJECT/qe/env}
PSEUDO_DIR=${PSEUDO_DIR:-$PROJECT/pseudo}
SRC=${SRC:-$PROJECT/sts/runs/s0/g_tio2_timing/s0_OOH__2x1v_off.in}
CAP=${CAP:-2400}

WD="$PROJECT/scaling/$ARM"
rm -rf "$WD"; mkdir -p "$WD"; cd "$WD" || exit 1

# Same rewrites the driver makes, applied here so this harness is independent of
# it: pseudo_dir to the Anvil tree, outdir local, and a short cap so every arm
# does the same kind of work for the same clock.
sed -e "s|^\( *pseudo_dir *=\).*|\1 '$PSEUDO_DIR'|" \
    -e "s|^\( *outdir *=\).*|\1 './tmp'|" \
    -e "s|^\( *max_seconds *=\).*|\1 $CAP|" \
    "$SRC" | sed 's/\r$//' > run.in
grep -E "pseudo_dir|outdir|max_seconds|calculation|nstep" run.in

export PATH="$QE_PREFIX/bin:$PATH"
export LD_LIBRARY_PATH="$QE_PREFIX/lib:${LD_LIBRARY_PATH:-}"
export OMP_NUM_THREADS=1
export ESPRESSO_PSEUDO="$PSEUDO_DIR"

echo "== arm $ARM: NP=$NP NK=$NK bind=$BIND cap=${CAP}s job=$SLURM_JOB_ID"
echo "== node $(hostname)  alloc_cpus=${SLURM_CPUS_ON_NODE:-?}  $(date -u)"
t0=$(date +%s)
mpirun --bind-to "$BIND" --oversubscribe -np "$NP" \
       pw.x -nk "$NK" -in run.in > run.out 2>&1 </dev/null
rc=$?
t1=$(date +%s)

# Seconds to finish ionic step 1 is the comparable unit: identical work in every
# arm, unaffected by how many steps each got through before the cap.
python3 - "$NP" "$NK" "$BIND" "$rc" "$((t1-t0))" <<'PY'
import re, sys
np_, nk, bind, rc, wall = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5])
txt = open("run.out", errors="replace").read()
cum = [float(x) for x in re.findall(r"total cpu time spent up to now is\s+([0-9.]+) secs", txt)]
steps = [m.start() for m in re.finditer(r"Self-consistent Calculation", txt)]
forces = re.findall(r"Total force =\s+([0-9.]+)", txt)
scf_done = txt.count("convergence has been achieved")
# cumulative clock at the end of the first ionic step = last timestamp before step 2
t_step1 = None
if len(steps) >= 2:
    n_before = len(re.findall(r"total cpu time spent up to now is", txt[:steps[1]]))
    if n_before: t_step1 = cum[n_before-1]
elif cum:
    t_step1 = cum[-1]
kpts = re.search(r"number of k points=\s*(\d+)", txt)
print(f"SCALING np={np_} nk={nk} bind={bind} rc={rc} wall={wall}s "
      f"kpts={kpts.group(1) if kpts else '?'} ionic_steps={len(steps)} scf_conv={scf_done} "
      f"t_ionic_step1={t_step1 if t_step1 else 'NA'}s "
      f"steps_per_hour={(len(steps)-1)*3600/cum[-1]:.2f}" if cum and len(steps)>1 else
      f"SCALING np={np_} nk={nk} bind={bind} rc={rc} wall={wall}s ionic_steps={len(steps)} INCOMPLETE")
print("   last force:", forces[-1] if forces else "NA")
err = re.search(r"%{5,}[\s\S]{0,400}", txt)
if rc != 0 and err: print("   pw.x error head:", err.group(0)[:400].replace("\n"," | "))
PY
tail -3 run.out
