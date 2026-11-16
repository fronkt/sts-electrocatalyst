#!/usr/bin/env bash
# Amendment 17 (2026-11-17 ~00:30Z, before any eta existed): candidate configuration C7 = Fe +, every
# Ni + (rule 3 of amendment 11: a pattern that a relaxation's SCF enters adds a candidate, as C4 did).
# u0__NiFeOOH__Fe0_OH_r6's step-8 SCF (22:05Z) converged with Ni30 at -0.2442 muB, under the 0.25 muB
# cutoff, so its pattern is Fe +, no Ni antiparallel: none of C1-C6.
#   - make_cfg_sp.sh: C7 encoding, default CFGS C1-C7;
#   - post_relax.sh v7: queues C1-C7 for each relaxation that converges from now on (Fe0_OH_r6);
#   - C7 inputs for the three converged states (the clean slab, Fe0_OOH, Fe0_O_r2), appended to
#     cfg_queue.txt.
#   DRY=1 bash deploy_pr7.sh   (build every C7 input and one full C1-C7 set in /tmp; touch nothing)
set -u
W=$HOME/film; cd "$W" || exit 1
for f in post_relax.sh.new make_cfg_sp.sh.new; do
  [ -f $f ] && bash -n $f || { echo "missing or bad $f"; exit 1; }
done
SL=u0__NiFeOOH__slab FE=u0__NiFeOOH__Fe0_OOH FO=u0__NiFeOOH__Fe0_O_r2 OH=u0__NiFeOOH__Fe0_OH_r6
mkdir -p /tmp/pr7
echo "== dry: C7 for $SL, $FE and $FO; C1-C7 for the running $OH (FORCE=1)"
for r in $SL $FE $FO; do CFGS=C7 bash make_cfg_sp.sh.new $r /tmp/pr7 || exit 1; done
FORCE=1 bash make_cfg_sp.sh.new $OH /tmp/pr7 || exit 1
# C7 must differ from the queued C2 input of the same state only in Fe's starting sign and the prefix
for r in $SL $FE $FO; do
  echo "== C2 vs C7 input diff for $r:"
  diff inputs/C2__$r.in /tmp/pr7/C7__$r.in
done
[ "${DRY:-0}" = 1 ] && { echo "DRY: nothing touched"; exit 0; }
for r in $SL $FE $FO; do
  n=C7__$r
  { [ -e runs/$n ] || [ -e inputs/$n.in ] || grep -qx "$n" cfg_queue.txt; } && { echo "$n exists"; exit 1; }
done
[ -e runs/$OH/CFG_QUEUED ] || [ -e runs/$OH/CFG_SKIPPED ] && { echo "$OH already has its single points decided"; exit 1; }
old=$(pgrep -f "^bash $W/post_relax[.]sh$")
[ "$(echo "$old" | grep -c .)" = 1 ] || { echo "expected one post_relax, got: $old"; exit 1; }
kill "$old"; sleep 1; kill -0 "$old" 2>/dev/null && { echo "old post_relax alive"; exit 1; }
cp -p make_cfg_sp.sh make_cfg_sp.sh.v6 && mv make_cfg_sp.sh.new make_cfg_sp.sh || exit 1
cp -p post_relax.sh post_relax.sh.v6 && mv post_relax.sh.new post_relax.sh || exit 1
for r in $SL $FE $FO; do CFGS=C7 bash make_cfg_sp.sh $r inputs || exit 1; done
printf '%s\n' C7__$SL C7__$FE C7__$FO >> cfg_queue.txt
echo "C7 (amendment 17, rule 3: Fe +, every Ni +, the pattern $OH's step-8 SCF entered) joins the Ni(Fe)OOH candidates; queued C7__$SL C7__$FE C7__$FO; post_relax v7 queues C1-C7 $(date -u +%FT%TZ)" >> queue.log
setsid nohup bash "$W/post_relax.sh" > /dev/null 2>&1 < /dev/null &
sleep 3
echo "post_relax: $(pgrep -f "^bash $W/post_relax[.]sh$")"; tail -3 queue.log | cut -c1-250; tail -5 cfg_queue.txt
