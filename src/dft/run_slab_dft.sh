#!/usr/bin/env bash
# Drive the rutile(110) slab+adsorbate DFT for one composition (docs/22, docs/23):
# build QE inputs (qe_slab.py build) -> relax each -> compute the OER overpotential.
# Heavy: a clean slab + 3 adslabs/site + 2 gas refs, each a magnetic +U relaxation.
#
# Prereqs on the box: conda-forge QE 7.x on PATH (pw.x, mpirun), SSSP pseudos in
# PSEUDO_DIR, and a python with `ase`+`pymatgen` plus the repo (PYTHONPATH=$REPO/src).
#
#   NP=24 NK=4 NSITES=1 REPO=/workspace/STS2027 bash run_slab_dft.sh Cr
set -u
COMP="${1:?usage: run_slab_dft.sh <composition> [outdir]   e.g. Cr  or  Fe32Ni17Co34Mn18}"
OUTDIR="${2:-/workspace/qe/runs/${COMP}_slab}"
NP="${NP:-24}"; NK="${NK:-4}"
PSEUDO_DIR="${PSEUDO_DIR:-/usr/share/espresso/pseudo}"
NSITES="${NSITES:-1}"
REPO="${REPO:-/workspace/STS2027}"
PWX="${PWX:-pw.x}"
PY="${PY:-python3}"

export PYTHONPATH="$REPO/src"
"$PY" "$REPO/src/dft/qe_slab.py" build "$COMP" --outdir "$OUTDIR" \
    --pseudo-dir "$PSEUDO_DIR" --n-sites "$NSITES" --ecutwfc 80 --ecutrho 640 || exit 1

# fail fast if any referenced pseudopotential is missing (e.g. the H UPF name differs)
for upf in $(grep -hoE "[A-Za-z0-9._-]+\.(UPF|upf)" "$OUTDIR"/*.in | sort -u); do
  [ -f "$PSEUDO_DIR/$upf" ] || { echo "MISSING pseudo: $PSEUDO_DIR/$upf -- fix ELEMENTS in qe_slab.py"; exit 2; }
done

cd "$OUTDIR" || exit 1
for inp in slab.in H2O.in H2.in s*_*.in; do
  [ -f "$inp" ] || continue
  out="${inp%.in}.out"
  if grep -q "JOB DONE" "$out" 2>/dev/null; then echo "skip $inp (already done)"; continue; fi
  echo "=== $inp  ($(date +%H:%M:%S)) ==="
  t0=$(date +%s)
  mpirun --allow-run-as-root -np "$NP" "$PWX" -nk "$NK" -in "$inp" > "$out" 2>&1
  ec=$?; dn=$(grep -c "JOB DONE" "$out" 2>/dev/null)
  echo "  exit=$ec  JOB_DONE=${dn:-0}  $(( $(date +%s)-t0 ))s"
done

"$PY" "$REPO/src/dft/qe_slab.py" eta --outdir "$OUTDIR"
