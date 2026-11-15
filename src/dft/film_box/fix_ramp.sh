#!/usr/bin/env bash
# Amendment 5b, run once on the box. The PBE+U relax could not start from the U=0 save directory
# ("read_scf: Reading ldaU ns": no Hubbard occupations were written without a HUBBARD card).
# The U=0 stage now keeps the card with U = 1e-8 eV, so ns is written. Before relaunching, a short
# two-stage test on one input must pass: a 3-iteration stage A, then stage B reading it.
set -u
W=$HOME/film
cd "$W" || exit 1
export PATH=$W/qe/env/bin:$PATH LD_LIBRARY_PATH=$W/qe/env/lib:${LD_LIBRARY_PATH:-} OMP_NUM_THREADS=1
JOBS="NiOOH__Ni0_O_r2 NiOOH__Ni0_OH_r2 NiOOH__Ni0_OOH_r2 NiFeOOH__Fe0_OOH_r2 NiFeOOH__Ni1_O NiFeOOH__Ni1_OH NiFeOOH__Ni1_OOH CoOOH__Co0_O_r2 CoOOH__Co0_OH_r2 CoOOH__Co0_OOH_r2 CoOOH__slab_r4"

# 1. snapshot, then stop queue-4 shells and the launchers of queue-4 jobs (healthy jobs untouched)
Q=$(ps -eo pid,args | awk '$2=="bash" && $3 ~ /box_run[23]?\.sh$/ {print $1}')
L=$(ps -eo pid,comm | awk '$2 ~ /^(prterun|mpirun)$/ {print $1}')
declare -A CWD
for p in $L; do CWD[$p]=$(readlink "/proc/$p/cwd"); done
# shellcheck disable=SC2086
kill $Q 2>/dev/null; echo "stopped queue shells: $(echo $Q | wc -w)"
for p in $L; do
  b=${CWD[$p]##*/}
  for n in $JOBS; do [ "$b" = "$n" ] && kill "$p" && echo "stopped launcher $p in $n"; done
done
sleep 10
echo "STOPPED queue-4 jobs for amendment 5b (U=1e-8 ramp stage) $(date -u +%FT%TZ)" >> queue.log

# 2. rebuild every stage-A input from the untouched relax input: scf, conv_thr 1e-5, U -> 1e-8
for n in $JOBS; do
  sed -e "s/calculation = 'relax'/calculation = 'scf'/" \
      -e "s/^  conv_thr = .*/  conv_thr = 1.0d-5/" \
      -e "s/^\(U [A-Z][a-z]*-3d\) .*/\1 1.0d-8/" \
      "inputs/${n}_nofile.in" > "inputs/${n}_u0.in"
  grep -q "^U .* 1.0d-8$" "inputs/${n}_u0.in" || echo "NO TINY U in ${n}_u0.in"
  rm -rf "runs/$n/tmp"
done

# 3. two-stage handoff test on NiOOH__Ni0_O_r2 (3 iterations each way, scf only)
T=$W/ramptest; rm -rf "$T"; mkdir -p "$T"; cd "$T" || exit 1
sed -e "s/^  electron_maxstep = .*/  electron_maxstep = 3\n  scf_must_converge = .false./" "$W/inputs/NiOOH__Ni0_O_r2_u0.in" > a.in
sed -e "s/calculation = 'relax'/calculation = 'scf'/" \
    -e "s/^  electron_maxstep = .*/  electron_maxstep = 2\n  scf_must_converge = .false./" "$W/inputs/NiOOH__Ni0_O_r2.in" > b.in
mpirun --bind-to none -np 24 pw.x -nk 3 -in a.in > a.out 2>&1 < /dev/null
mpirun --bind-to none -np 24 pw.x -nk 3 -in b.in > b.out 2>&1 < /dev/null
echo "stage A: $(grep -c 'JOB DONE' a.out) job-done, hubbard ns written: $(grep -c -i 'enter write_ns' a.out)"
echo "stage B: $(grep -c 'JOB DONE' b.out) job-done, crash: $([ -f CRASH ] && echo yes || echo no)"
grep -a -i -E "starting wfc|from file|read_scf" b.out | head -4
if grep -q "JOB DONE" b.out && [ ! -f CRASH ]; then
  echo RAMPTEST_PASS
  cd "$W" || exit 1
  echo "$JOBS" | tr ' ' '\n' > jobs5.txt
  JOBS_FILE=$W/jobs5.txt NP=24 NK=3 setsid nohup bash "$W/box_run3.sh" > "$W/queue5.log" 2>&1 < /dev/null &
  sleep 40; echo "pw.x ranks: $(pgrep -x pw.x | wc -l)"; tail -2 queue.log
else
  echo RAMPTEST_FAIL; tail -20 b.out
fi
