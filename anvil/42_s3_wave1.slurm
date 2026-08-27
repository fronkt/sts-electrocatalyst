#!/bin/bash
# S3 wave-1 runner -- ONE Slurm array task per deck at the A8.6 launch shape:
# 128 ranks, -nk from the manifest row (16 only where >= 16 irreducible
# k-points exist: noinv-kept refs, 1x1_off rows, parent-cloning SCFs; 8 on the
# 10-k noinv-dropped 4x4x1 off/escape rows and on mirror-arm rows -- pw.x
# refuses more pools than k-points), -N 1,
# 48 h. Adapted from 40_wave.slurm (array-per-deck mechanics, stale-.out rule)
# and 50_scaling.slurm (direct mpirun + the driver's sed rewrites) -- direct
# mpirun here because queue_r1.sh hardcodes `--bind-to none`, and rank BINDING
# IS AN UNDECIDED REGISTRATION ITEM (A8.6, docs/43:1668-1679; docs/48): no
# --bind-to flag appears anywhere in the S3 wave-1 launch path, so mpirun runs
# at its own default.
#
# Launched ONLY by 43_submit_s3_wave1.sh, which enforces the PARITY_PASS gate
# (docs/43:1613-1621) before a single SU is spent.
#
# Charging: `shared` bills cores x hours; 128 ranks = 128 SU/h while the task
# runs. Worst case per deck at the 48 h cap: 6144 SU; each deck also carries
# max_seconds = 165000 (~45.8 h) so pw.x stops cleanly and restartably inside
# the Slurm cap instead of being SIGKILLed at it.
#SBATCH -p shared
#SBATCH -N 1
#SBATCH -n 128
#SBATCH -t 48:00:00
#SBATCH -J s3-wave1
#SBATCH -o logs/s3w1_%A_%a.out
#SBATCH -e logs/s3w1_%A_%a.out

set -uo pipefail

: "${MANIFEST:?MANIFEST must be exported by 43_submit_s3_wave1.sh}"
: "${RUNS:?RUNS must be exported by 43_submit_s3_wave1.sh}"
: "${QE_PREFIX:?QE_PREFIX must be exported by 43_submit_s3_wave1.sh}"
: "${PSEUDO_DIR:?PSEUDO_DIR must be exported by 43_submit_s3_wave1.sh}"
NP=${NP:-128}

LINES="${MANIFEST}.lines"
row=$(sed -n "${SLURM_ARRAY_TASK_ID}p" "$LINES")
[ -n "$row" ] || { echo "FATAL: no row ${SLURM_ARRAY_TASK_ID} in $LINES"; exit 1; }
read -r d job suf nk extra <<< "$row"
[ -n "${nk:-}" ] || { echo "FATAL: malformed row '$row'"; exit 1; }
[ -z "${extra:-}" ] || { echo "FATAL: trailing fields in row '$row'"; exit 1; }
case "$nk" in ''|*[!0-9]*) echo "FATAL: nk '$nk' not a number"; exit 1;; esac
[ $((NP % nk)) -eq 0 ] || { echo "FATAL: NP=$NP not an exact multiple of nk=$nk (hard rule 4)"; exit 1; }

dir="$RUNS/$d"
inp="$dir/${job}${suf}"
[ -f "$inp" ] || { echo "FATAL: missing $inp"; exit 1; }
out="$dir/${job}.out"
if [ -f "$out" ] && grep -aq "JOB DONE" "$out"; then
  # Stale-.out rule (queue_r1.sh preflight; hard rule 3): JOB DONE alone is NOT
  # success, and overwriting a banked result is the A8.8 silent replacement.
  # Either way this task must not touch it.
  echo "REFUSE: $out already exists and carries JOB DONE -- not overwriting"; exit 2
fi

cd "$dir" || exit 1
scratch="./tmp_${job}"
rm -rf "$scratch"; mkdir -p "$scratch"

# The driver's own per-job rewrites (queue_r1.sh:285-295 / 50_scaling.slurm):
# outdir to a per-job scratch so concurrent tasks cannot collide, pseudo_dir to
# the Anvil tree, CR stripped (a deck containing CR dies silently -- hard rule 1).
sed -e "s#outdir *= *'[^']*'#outdir = '${scratch}'#" \
    -e "s#pseudo_dir *= *'[^']*'#pseudo_dir = '${PSEUDO_DIR}'#" \
    "${job}${suf}" | sed 's/\r$//' > "${job}.run.in"

export PATH="$QE_PREFIX/bin:$PATH"
export LD_LIBRARY_PATH="$QE_PREFIX/lib:${LD_LIBRARY_PATH:-}"
export OMP_NUM_THREADS=1
export ESPRESSO_PSEUDO="$PSEUDO_DIR"

echo "TASK ${SLURM_ARRAY_TASK_ID} $d/$job np=$NP nk=$nk node=$(hostname) cpus=${SLURM_CPUS_ON_NODE:-?} $(date -u)"
t0=$(date +%s)
# `</dev/null` or OpenMPI's stdin forwarding misbehaves (queue_r1.sh hard rule).
mpirun --oversubscribe -np "$NP" pw.x -nk "$nk" -in "${job}.run.in" \
       > "$out" 2>&1 </dev/null
rc=$?
t1=$(date +%s)

# JOB DONE is never success by itself (docs/26 s4): report the real markers.
conv=$(grep -ac "bfgs converged" "$out" || true)
scffail=$(grep -ac "convergence NOT achieved" "$out" || true)
done_=$(grep -ac "JOB DONE" "$out" || true)
final=$(grep -a "^!" "$out" | tail -1)
echo "TASK ${SLURM_ARRAY_TASK_ID} $d/$job rc=$rc wall=$((t1-t0))s bfgs_conv=$conv scf_fail=$scffail job_done=$done_ $(date -u)"
echo "   final: ${final:-NA}"

# A8.3 enabler (infrastructure amendment, 2026-08-26; corrected same day). The
# converged charge density is the only thing that pins the magnetic branch for a
# child run: across all 35 GATE-1 pairs, dmagtot <= 0.01 gives |dE| <= 0.044 meV
# and dmagtot >= 0.18 gives |dE| >= 7.394 meV, with no overlap (docs/45).
# Until now this line deleted every density we ever produced, which is why
# re-deriving one costs a 500-1000 SU parent replay against ~13 SU for the child.
#
# Retain the DENSITY ONLY, never the wavefunctions. Measured on the first
# retention (Fe s0_OOH__1x1_off__g1__r2): the whole .save is 2.4 GB, of which
# wfc*.hdf5 is 2.505 GB across 36 files and the density payload
# (charge-density.hdf5 + data-file-schema.xml + paw.txt + occup.txt + the UPFs)
# is 42 MB; Mn's is 72 MB. `startingpot='file'` reads only the charge density --
# wavefunctions serve `startingwfc='file'` and `restart_mode='restart'`, both of
# which this campaign FORBIDS (build_s3_wave2.py:FORBIDDEN_RESTART). So dropping
# them is 30-60x cheaper AND removes the ability to accidentally restart from a
# forbidden source. Changes no calculation.
prefix=$(sed -n "s/^[[:space:]]*prefix[[:space:]]*=[[:space:]]*'\([^']*\)'.*/\1/p" "${job}.run.in" | head -1)
if [ "${scffail:-1}" -eq 0 ] && [ "${done_:-0}" -ge 1 ] && [ -n "${prefix:-}" ] && [ -d "$scratch/${prefix}.save" ]; then
  mkdir -p ./dens
  rm -rf "./dens/${prefix}.save.new"
  if mkdir -p "./dens/${prefix}.save.new" && \
     find "$scratch/${prefix}.save" -maxdepth 1 -type f ! -name 'wfc*' \
          -exec cp -p {} "./dens/${prefix}.save.new/" \; && \
     [ -f "./dens/${prefix}.save.new/data-file-schema.xml" ]; then
    rm -rf "./dens/${prefix}.save"
    mv "./dens/${prefix}.save.new" "./dens/${prefix}.save"
    echo "   retained density: $d/dens/${prefix}.save ($(du -sh "./dens/${prefix}.save" | cut -f1), wavefunctions dropped)"
  else
    rm -rf "./dens/${prefix}.save.new"
    echo "   density retention FAILED for ${prefix} (any previous copy left intact)"
  fi
else
  echo "   no density retained (scf_fail=${scffail:-?} job_done=${done_:-?} prefix=${prefix:-NA})"
fi
rm -rf "$scratch"
seff "${SLURM_JOB_ID}" 2>/dev/null || true
exit $rc
