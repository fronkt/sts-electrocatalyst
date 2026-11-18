#!/usr/bin/env bash
# Amendment 24: the five amendment-23 B states whose PBE+U SCF did not converge, rerun in two stages.
#   stage 1 (A24S__RUN; Fe0_OH and Fe0_OOH only): the A23U input unchanged (conv_thr 1e-5) but run to its
#     electron_maxstep (Fe0_OH 200, Fe0_OOH 400) with a wall long enough to reach it (4 h, 6 h), from the
#     same U = 0 density as in amendment 23. For the three NiOOH states, stage 1 is the A23U run itself
#     (it ran to 200 iterations and wrote its density).
#   stage 2 (A24U__RUN; all five): the A23U input with conv_thr 1.0d-3 and electron_maxstep 100, restarted
#     from stage 1's written density; 30 min wall.
#   bash anvil_a24.sh stage            # local: build the 7 inputs from the staged A23U inputs and check them
#   bash anvil_a24.sh deploy1          # A24S x2 and the three NiOOH A24U (their stage 1 is done)
#   bash anvil_a24.sh deploy2 RUN      # A24U for RUN after its A24S stage 1 has ended at its maxstep
set -u
export MSYS2_ARG_CONV_EXCL="/anvil"
MODE=${1:?stage|deploy1|deploy2}
A=x-fcai3@anvil.rcac.purdue.edu; SO="-o BatchMode=yes -o ConnectTimeout=30"
SCR=/anvil/scratch/x-fcai3/film
S23=/d/sts-electrocatalyst/film_pilot/anvil_stage_a23 S=/d/sts-electrocatalyst/film_pilot/anvil_stage_a24
NIOOH="u0__NiOOH__Ni0_OH u0__NiOOH__Ni0_O_r2 u0__NiOOH__Ni0_OOH_r7"
NIFE="u0__NiFeOOH__Fe0_OH_r11 u0__NiFeOOH__Fe0_OOH"
ms1() { [ "$1" = u0__NiFeOOH__Fe0_OOH ] && echo 400 || echo 200; }
wall1() { [ "$1" = u0__NiFeOOH__Fe0_OOH ] && echo 06:00:00 || echo 04:00:00; }
# the density each Fe-side stage 1 starts from: amendment 23's own source (unchanged on Anvil; TIMEOUT
# wrote nothing over it)
src1() { case $1 in
  u0__NiFeOOH__Fe0_OH_r11) echo $SCR/C2__u0__NiFeOOH__Fe0_OH_r11/tmp/C2__u0__NiFeOOH__Fe0_OH_r11.save ;;
  u0__NiFeOOH__Fe0_OOH) echo $SCR/A23U__u0__NiFeOOH__Fe0_OOH/tmp/A23U__u0__NiFeOOH__Fe0_OOH.save ;; esac; }

put() {  # put NAME SRC_SAVE_DIR WALL : make the run dir, upload NAME.in, copy the density, md5/cmp, sbatch
  local N=$1 src=$2 w=$3 m
  m=$(md5sum < "$S/$N.in" | cut -d' ' -f1)
  ssh $SO $A "test -e $SCR/$N && { echo $N EXISTS; exit 1; }; mkdir -p $SCR/$N/tmp/$N.save" || return 1
  scp -q $SO "$S/$N.in" "$A:$SCR/$N/$N.in" || return 1
  ssh $SO $A "set -e; cd $SCR/$N/tmp/$N.save
    for f in charge-density.hdf5 occup.txt paw.txt; do cp -p $src/\$f .; cmp \$f $src/\$f; done
    md5sum charge-density.hdf5 occup.txt paw.txt | cut -c1-8 | tr '\n' ' '; echo
    cd $SCR/$N; [ \$(md5sum < $N.in | cut -d' ' -f1) = $m ]; ! grep -q \$'\r' $N.in
    cd $SCR && sbatch -t $w -J $N --export=ALL,N=$N anvil_film_scr.slurm" || return 1
}

case $MODE in
stage)
  rm -rf "$S" && mkdir -p "$S" || exit 1
  ok=1
  for r in $NIFE; do
    N=A24S__$r
    sed -e "s#prefix = 'A23U__$r'#prefix = '$N'#" -e "s#film/A23U__$r/tmp#film/$N/tmp#" \
        -e "s#electron_maxstep = 200#electron_maxstep = $(ms1 $r)#" "$S23/A23U__$r.in" > "$S/$N.in"
  done
  for r in $NIOOH $NIFE; do
    N=A24U__$r
    sed -e "s#prefix = 'A23U__$r'#prefix = '$N'#" -e "s#film/A23U__$r/tmp#film/$N/tmp#" \
        -e "s#conv_thr = 1.0d-5#conv_thr = 1.0d-3#" -e "s#electron_maxstep = 200#electron_maxstep = 100#" \
        "$S23/A23U__$r.in" > "$S/$N.in"
  done
  for f in "$S"/*.in; do
    N=$(basename "$f" .in) r=${N#A24?__}
    case $N in A24S__*) want="conv_thr = 1.0d-5|electron_maxstep = $(ms1 $r)" ;;
               *) want="conv_thr = 1.0d-3|electron_maxstep = 100" ;; esac
    for s in "prefix = '$N'" "outdir = '$SCR/$N/tmp'" "startingpot = 'file'" "${want%%|*}" "${want##*|}"; do
      [ "$(grep -c "$s" "$f")" = 1 ] || { echo "CHECK FAILED: $N lacks exactly one '$s'"; ok=0; }
    done
    grep -q $'\r' "$f" && { echo "CHECK FAILED: CRLF in $N"; ok=0; }
    d=$(diff "$S23/A23U__$r.in" "$f" | grep -c '^>')
    echo "$N: $d lines differ from A23U__$r.in: $(diff "$S23/A23U__$r.in" "$f" | grep '^>' | tr -s ' ' | tr '\n' ';')"
  done
  [ "$ok" = 1 ] || { echo "STAGE FAILED"; exit 1; }
  (cd "$S" && md5sum ./*.in) | tee "$S/inputs.md5"
  date -u +%FT%TZ > "$S/STAGED"; echo "STAGED $S" ;;
deploy1)
  [ -f "$S/STAGED" ] || { echo "not staged"; exit 1; }
  for r in $NIFE; do put "A24S__$r" "$(src1 $r)" "$(wall1 $r)" || exit 1; done
  for r in $NIOOH; do put "A24U__$r" "$SCR/A23U__$r/tmp/A23U__$r.save" 00:30:00 || exit 1; done ;;
deploy2)
  r=${2:?RUN}; o=$SCR/A24S__$r/A24S__$r.out
  ssh $SO $A "grep -q 'convergence NOT achieved after *$(ms1 $r) iterations' $o || grep -q 'convergence has been achieved' $o" \
    || { echo "A24S__$r has not ended at its maxstep or converged; no stage 2"; exit 1; }
  put "A24U__$r" "$SCR/A24S__$r/tmp/A24S__$r.save" 00:30:00 ;;
*) echo "mode?"; exit 1 ;;
esac
