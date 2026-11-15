#!/usr/bin/env bash
# Amendment 4, run once on the box: pw.x's default upscale (100) tightened conv_thr to ~8e-7 Ry
# as forces fell, below the ~2e-6 Ry SCF noise floor, so relaxations stalled. Restart every live
# relaxation from its last geometry with upscale = 1 and conv_thr 5e-6, add upscale to the inputs
# not yet started, and run everything through one core-counting queue (NP 24, 8 at a time).
set -u
W=$HOME/film
cd "$W" || exit 1

# 1. snapshot first (lesson: a dead parent makes its children look parentless), then stop
Q=$(ps -eo pid,args | awk '$2=="bash" && $3 ~ /box_run2?\.sh$/ {print $1}')
L=$(ps -eo pid,comm | awk '$2 ~ /^(prterun|mpirun)$/ {print $1}')
declare -A CWD
for p in $L; do CWD[$p]=$(readlink "/proc/$p/cwd"); done
# shellcheck disable=SC2086
kill $Q 2>/dev/null; echo "stopped queue shells: $(echo $Q | wc -w)"
for p in $L; do kill "$p" 2>/dev/null && echo "stopped launcher $p in ${CWD[$p]##*/}"; done
for _ in $(seq 1 30); do [ "$(pgrep -x pw.x | wc -l)" -eq 0 ] && break; sleep 2; done
echo "pw.x left: $(pgrep -x pw.x | wc -l)"
echo "STOPPED all jobs for amendment 4 (upscale = 1) $(date -u +%FT%TZ)" >> queue.log

# 2. restarts from the last geometry
restart() {
  python3 qe_restart_input.py "inputs/$1.in" "runs/$1/$1.out" "inputs/$2.in" "$2" \
          --conv-thr 5.0d-6 --upscale 1.d0 || echo "RESTART FAILED $1"
}
restart NiOOH__slab_r2 NiOOH__slab_r3
restart NiFeOOH__slab NiFeOOH__slab_r2
restart NiFeOOH__Fe0_O NiFeOOH__Fe0_O_r2
restart CoOOH__Co0_O CoOOH__Co0_O_r2
restart CoOOH__Co0_OH CoOOH__Co0_OH_r2
restart CoOOH__Co0_OOH CoOOH__Co0_OOH_r2
# CoOOH clean slab never finished an SCF: same geometry, CG diagonalization, beta 0.02, moment 8
sed -e "s/prefix = 'CoOOH__slab_r3'/prefix = 'CoOOH__slab_r4'/" \
    -e "s/^  conv_thr = 1.0d-6$/  conv_thr = 5.0d-6/" \
    -e "s/^  mixing_beta = 0.05$/  mixing_beta = 0.02/" \
    -e "s/^  ion_dynamics = 'bfgs'$/  ion_dynamics = 'bfgs'\n  upscale = 1.d0/" \
    -e "s/^&ELECTRONS$/\&ELECTRONS\n  diagonalization = 'cg'/" \
    inputs/CoOOH__slab_r3.in > inputs/CoOOH__slab_r4.in

# 3. inputs not yet started get upscale (they already have conv_thr 5e-6)
for n in NiFeOOH__Fe0_OH NiFeOOH__Fe0_OOH NiOOH__Ni0_O NiOOH__Ni0_OH NiOOH__Ni0_OOH \
         NiFeOOH__Ni1_O NiFeOOH__Ni1_OH NiFeOOH__Ni1_OOH; do
  [ -d "runs/$n" ] && echo "WARNING $n had started"
  grep -q upscale "inputs/$n.in" || sed -i "s/^  ion_dynamics = 'bfgs'$/  ion_dynamics = 'bfgs'\n  upscale = 1.d0/" "inputs/$n.in"
done

# 4. one queue: V1-critical states first, then the Ni site next to Fe, then CoOOH
cat > jobs3.txt <<'LIST'
NiOOH__slab_r3
NiFeOOH__slab_r2
NiFeOOH__Fe0_O_r2
NiFeOOH__Fe0_OH
NiFeOOH__Fe0_OOH
NiOOH__Ni0_O
NiOOH__Ni0_OH
NiOOH__Ni0_OOH
NiFeOOH__Ni1_O
NiFeOOH__Ni1_OH
NiFeOOH__Ni1_OOH
CoOOH__Co0_O_r2
CoOOH__Co0_OH_r2
CoOOH__Co0_OOH_r2
CoOOH__slab_r4
LIST
for n in $(cat jobs3.txt); do [ -f "inputs/$n.in" ] || echo "MISSING INPUT $n"; done
echo "upscale = 1.d0 in $(grep -l 'upscale = 1.d0' inputs/*.in | wc -l) inputs; conv_thr 5e-6 in $(grep -l '^  conv_thr = 5.0d-6' inputs/*.in | wc -l)"
JOBS_FILE=$W/jobs3.txt NP=24 NK=3 setsid nohup bash "$W/box_run2.sh" > "$W/queue3.log" 2>&1 < /dev/null &
sleep 45
echo "pw.x ranks: $(pgrep -x pw.x | wc -l)"; tail -3 queue.log
