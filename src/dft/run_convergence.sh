#!/usr/bin/env bash
# Convergence test for the DFT calibration tier (docs/22): on one rutile MO2 endmember,
# sweep ecutwfc (fixed k-points) then the k-grid (fixed ecutwfc), record total energy.
# Target: ecutwfc/k-grid where the per-atom energy changes < ~1 meV (a tight proxy for the
# <50 meV eta target once slabs are run). Geometry is FIXED (scf only) so deltas are pure
# basis/k convergence. Writes a CSV; safe to re-run (idempotent per tag).
#
# Env (override as needed):
#   FORMULA=CrO2  NP=16  NK=4  PSEUDO_DIR=...  M_UPF=...  O_UPF=...  GEN=gen_rutile.py
set -u
FORMULA="${FORMULA:-CrO2}"
NP="${NP:-16}"                 # MPI ranks (Threadripper 32C/64T -> 16 leaves headroom)
NK="${NK:-4}"                  # k-point pools (-nk); NP must be divisible by NK
PSEUDO_DIR="${PSEUDO_DIR:-/workspace/qe/pseudo}"
M_UPF="${M_UPF:?set M_UPF to the metal pseudopotential filename}"
O_UPF="${O_UPF:?set O_UPF to the oxygen pseudopotential filename}"
GEN="${GEN:-gen_rutile.py}"
PWX="${PWX:-pw.x}"
WORK="${WORK:-/workspace/qe/runs/${FORMULA}_conv}"
DUAL="${DUAL:-8}"              # ecutrho = DUAL * ecutwfc during the wfc sweep
RYDBERG_EV=13.605693

mkdir -p "$WORK"; cd "$WORK" || exit 1
CSV="$WORK/convergence.csv"
echo "sweep,ecutwfc_Ry,ecutrho_Ry,kx,ky,kz,total_energy_Ry,energy_per_atom_eV,total_mag,converged,walltime_s" > "$CSV"

run_one () {
  local sweep="$1" ecutwfc="$2" ecutrho="$3" kx="$4" ky="$5" kz="$6"
  local tag="${sweep}_w${ecutwfc}_k${kx}${ky}${kz}"
  local inp="$WORK/${tag}.in" out="$WORK/${tag}.out"
  python3 "$GEN" "$FORMULA" --ecutwfc "$ecutwfc" --ecutrho "$ecutrho" \
      --kpts "$kx" "$ky" "$kz" --pseudo-dir "$PSEUDO_DIR" \
      --m-upf "$M_UPF" --o-upf "$O_UPF" -o "$inp" >/dev/null
  local t0 t1; t0=$(date +%s)
  mpirun --allow-run-as-root -np "$NP" "$PWX" -nk "$NK" -in "$inp" > "$out" 2>&1
  t1=$(date +%s)
  local etot conv mag epa
  etot=$(grep '^!' "$out" | tail -1 | awk '{print $(NF-1)}')
  conv=$(grep -q "convergence has been achieved" "$out" && echo 1 || echo 0)
  mag=$(grep "total magnetization" "$out" | tail -1 | awk '{print $(NF-2)}')
  if [ -n "$etot" ]; then epa=$(awk -v e="$etot" -v r="$RYDBERG_EV" 'BEGIN{printf "%.4f", e*r/6.0}'); else epa="NA"; etot="NA"; fi
  echo "${sweep},${ecutwfc},${ecutrho},${kx},${ky},${kz},${etot},${epa},${mag:-NA},${conv},$((t1-t0))" >> "$CSV"
  echo "[$tag] Etot=${etot} Ry  E/atom=${epa} eV  mag=${mag:-NA}  conv=${conv}  $((t1-t0))s"
}

echo "=== ecutwfc sweep (k fixed 6x6x8, dual=${DUAL}) ==="
for w in 40 50 60 70 80 90 100; do
  run_one ecut "$w" "$(( w * DUAL ))" 6 6 8
done

echo "=== k-point sweep (ecutwfc fixed 80, ecutrho 640) ==="
for k in "2 2 3" "4 4 6" "6 6 8" "8 8 12"; do
  set -- $k; run_one kpts 80 640 "$1" "$2" "$3"
done

echo "=== DONE -> $CSV ==="
cat "$CSV"
