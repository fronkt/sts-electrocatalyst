#!/usr/bin/env bash
# 2026-11-16 ~16:40Z: candidate configuration C6 = Fe +, Ni 5 - (rule 1). u0__NiFeOOH__Fe0_OOH's
# relaxation converged at 16:18Z in that pattern (Ni29 -0.18 to -0.23 since step 40, under the
# 0.25 muB cutoff), which is none of C1-C5. Rule 1: every state gets a single point in a new pattern
# a Ni(Fe)OOH relaxation ends in.
#   - make_cfg_sp.sh: C6 encoding, default CFGS C1-C6;
#   - post_relax.sh v6: queues C1-C6 for each relaxation that converges from now on;
#   - C6 inputs for the two converged states (Fe0_OOH, where C6 is the own-configuration check, and
#     the clean slab), appended to cfg_queue.txt.
#   DRY=1 bash deploy_pr6.sh   (build every C6 input and one full C1-C6 set in /tmp; touch nothing)
set -u
W=$HOME/film; cd "$W" || exit 1
for f in post_relax.sh.new make_cfg_sp.sh.new; do
  [ -f $f ] && bash -n $f || { echo "missing or bad $f"; exit 1; }
done
FE=u0__NiFeOOH__Fe0_OOH SL=u0__NiFeOOH__slab
mkdir -p /tmp/pr6
echo "== dry: C6 for $FE and $SL; C1-C6 for the running Fe0_O and Fe0_OH_r4 (FORCE=1)"
CFGS=C6 bash make_cfg_sp.sh.new $FE /tmp/pr6 || exit 1
CFGS=C6 bash make_cfg_sp.sh.new $SL /tmp/pr6 || exit 1
FORCE=1 bash make_cfg_sp.sh.new u0__NiFeOOH__Fe0_O /tmp/pr6 || exit 1
FORCE=1 bash make_cfg_sp.sh.new u0__NiFeOOH__Fe0_OH_r4 /tmp/pr6 || exit 1
# C6 must differ from the queued C3 input only in atom 29's species (both Fe +, Ni 5 -)
echo "== C3 vs C6 input diff for $FE:"
diff inputs/C3__$FE.in /tmp/pr6/C6__$FE.in
[ "${DRY:-0}" = 1 ] && { echo "DRY: nothing touched"; exit 0; }
for n in C6__$FE C6__$SL; do
  { [ -e runs/$n ] || [ -e inputs/$n.in ] || grep -qx "$n" cfg_queue.txt; } && { echo "$n exists"; exit 1; }
done
old=$(pgrep -f "^bash $W/post_relax[.]sh$")
[ "$(echo "$old" | grep -c .)" = 1 ] || { echo "expected one post_relax, got: $old"; exit 1; }
kill "$old"; sleep 1; kill -0 "$old" 2>/dev/null && { echo "old post_relax alive"; exit 1; }
cp -p make_cfg_sp.sh make_cfg_sp.sh.v5 && mv make_cfg_sp.sh.new make_cfg_sp.sh || exit 1
cp -p post_relax.sh post_relax.sh.v5 && mv post_relax.sh.new post_relax.sh || exit 1
CFGS=C6 bash make_cfg_sp.sh $FE inputs || exit 1
CFGS=C6 bash make_cfg_sp.sh $SL inputs || exit 1
printf '%s\n' C6__$FE C6__$SL >> cfg_queue.txt
echo "C6 (rule 1: Fe +, Ni 5 -, the pattern $FE's relaxation ended in) joins the Ni(Fe)OOH candidates; queued C6__$FE C6__$SL; post_relax v6 queues C1-C6 $(date -u +%FT%TZ)" >> queue.log
setsid nohup bash "$W/post_relax.sh" > /dev/null 2>&1 < /dev/null &
sleep 3
echo "post_relax: $(pgrep -f "^bash $W/post_relax[.]sh$")"; tail -3 queue.log | cut -c1-250; tail -4 cfg_queue.txt
