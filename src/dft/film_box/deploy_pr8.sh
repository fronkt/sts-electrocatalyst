#!/usr/bin/env bash
# 2026-11-17 ~00:05Z: FIRE convergence counts as convergence. pw.x's FIRE prints "FIRE: convergence
# achieved in N steps" and "End of FIRE minimization", never "bfgs converged". post_relax.sh,
# make_cfg_sp.sh and v1done.sh tested only for "bfgs converged", so a converged FIRE relaxation
# (Fe0_OH_r6, amendment 16; Ni0_OOH_r5, amendment 12) would have been taken as unconverged:
# post_relax would mark it CFG_SKIPPED and queue no single points, and v1done would not stop the
# other Ni0_OOH run. qe_qc.py and film_pilot_readout.py already accept both lines. No FIRE run had
# converged when this was found (00:02Z).
#   - post_relax.sh v8, make_cfg_sp.sh, v1done.sh v2: accept either line;
#   - a cfg_watch run marked CFG_SKIPPED whose output has the FIRE line gets its marker removed (none
#     expected), so v8 queues its single points.
#   DRY=1 bash deploy_pr8.sh   (pattern test and v1done dry run; touch nothing)
set -u
W=$HOME/film; cd "$W" || exit 1
for f in post_relax.sh.new make_cfg_sp.sh.new v1done.sh.new; do
  [ -f $f ] && bash -n $f || { echo "missing or bad $f"; exit 1; }
done
t=/tmp/pr8; mkdir -p $t
printf '     FIRE: convergence achieved in 12 steps\n\n     End of FIRE minimization\n' > $t/fire.out
printf '     bfgs converged in  28 scf cycles and  27 bfgs steps\n' > $t/bfgs.out
printf '     convergence has been achieved in  12 iterations\n' > $t/scf.out
for f in post_relax.sh.new make_cfg_sp.sh.new v1done.sh.new; do
  pat=$(grep -o -- '-e "bfgs converged" -e "FIRE: convergence achieved"' $f | head -1)
  [ -n "$pat" ] || { echo "$f lacks the two-pattern test"; exit 1; }
  [ "$(grep -c 'grep -q "bfgs converged"' $f)" = 0 ] || { echo "$f still has a BFGS-only test"; exit 1; }
  r=""; for o in fire bfgs scf; do grep -q -e "bfgs converged" -e "FIRE: convergence achieved" $t/$o.out && r="$r$o=1 " || r="$r$o=0 "; done
  echo "$f: $r"
done
DRY=1 bash v1done.sh.new
skipped_fire=""
while read -r r; do
  [ -n "$r" ] && [ -f runs/$r/CFG_SKIPPED ] && grep -q "FIRE: convergence achieved" runs/$r/$r.out 2>/dev/null && skipped_fire="$skipped_fire$r "
done < cfg_watch.txt
echo "CFG_SKIPPED FIRE-converged runs: ${skipped_fire:-none}"
[ "${DRY:-0}" = 1 ] && { echo "DRY: nothing touched"; exit 0; }
for d in post_relax v1done; do
  old=$(pgrep -f "^bash $W/$d[.]sh$")
  [ "$(echo "$old" | grep -c .)" = 1 ] || { echo "expected one $d, got: $old"; exit 1; }
  kill "$old"; sleep 1; kill -0 "$old" 2>/dev/null && { echo "old $d alive"; exit 1; }
done
cp -p make_cfg_sp.sh make_cfg_sp.sh.v7 && mv make_cfg_sp.sh.new make_cfg_sp.sh || exit 1
cp -p post_relax.sh post_relax.sh.v7 && mv post_relax.sh.new post_relax.sh || exit 1
cp -p v1done.sh v1done.sh.v1 && mv v1done.sh.new v1done.sh || exit 1
for r in $skipped_fire; do rm -f runs/$r/CFG_SKIPPED; done
echo "FIRE convergence ('FIRE: convergence achieved') now counts in post_relax.sh v8, make_cfg_sp.sh and v1done.sh v2 (they tested only 'bfgs converged'); CFG_SKIPPED removed from: ${skipped_fire:-none} $(date -u +%FT%TZ)" >> queue.log
setsid nohup bash "$W/post_relax.sh" > /dev/null 2>&1 < /dev/null &
setsid nohup bash "$W/v1done.sh" > /dev/null 2>&1 < /dev/null &
sleep 3
echo "post_relax: $(pgrep -f "^bash $W/post_relax[.]sh$")  v1done: $(pgrep -f "^bash $W/v1done[.]sh$")"; tail -3 queue.log | cut -c1-250
