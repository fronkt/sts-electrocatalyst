#!/usr/bin/env bash
# Amendment 22: the C1-C7 fixed-geometry single points of an accepted (not pw.x-converged) Anvil
# relaxation, at its accepted step's geometry (the last step with forces), with make_cfg_sp.sh's
# recipe unchanged: scf, conv_thr 1e-5 (amendment 10), cold start, the same seven starting
# configurations and the same encoding check. Only outdir (user scratch) differs from that recipe.
#   bash anvil_cfg_sp.sh stage  RUN    # local: build CK__RUN.in from the pulled RUN.out
#   bash anvil_cfg_sp.sh deploy RUN    # upload, md5-check, sbatch each (4 h limit)
# RUN.in/.out must already be pulled to $L/RUN/ (md5-checked against Anvil).
set -u
MODE=${1:?stage|deploy} r=${2:?RUN}
A=x-fcai3@anvil.rcac.purdue.edu; SO="-o BatchMode=yes -o ConnectTimeout=30"
RR=/anvil/projects/x-che260157/film/runs SCR=/anvil/scratch/x-fcai3/film
L=/d/sts-electrocatalyst/film_pilot/out/runs
S=/d/sts-electrocatalyst/film_pilot/anvil_stage_cfgsp_$r
PY=${PY:-D:/sts-electrocatalyst/.venv-isef/Scripts/python.exe}
H=$(cd "$(dirname "$0")" && pwd)
CF=${CFGS:-C1 C2 C3 C4 C5 C6 C7}
if [ "$MODE" = deploy ]; then
  for c in $CF; do
    N=${c}__$r; m=$(md5sum < "$S/$N.in" | cut -d' ' -f1)
    ssh $SO $A "test -e $RR/$N && { echo $N EXISTS; exit 1; }; mkdir -p $RR/$N $SCR/$N/tmp" || exit 1
    scp -q $SO "$S/$N.in" "$A:$RR/$N/$N.in" || exit 1
    ssh $SO $A "set -e; cd $RR/$N; [ \$(md5sum < $N.in | cut -d' ' -f1) = $m ]; ! grep -q \$'\r' $N.in
      cd /anvil/projects/x-che260157/film && sbatch -t 04:00:00 -J $N --export=ALL,N=$N anvil_film.slurm" || exit 1
  done
  exit 0
fi
[ "$MODE" = stage ] || { echo "mode?"; exit 1; }
o=$L/$r/$r.out
nf=$(grep -a -c 'Forces acting on atoms' "$o"); nblk=$(grep -a -c '^ATOMIC_POSITIONS' "$o")
[ "$nf" -ge 2 ] && [ "$nblk" -ge "$nf" ] || { echo "$r: $nf force blocks, $nblk blocks"; exit 1; }
Lc=$(grep -a -n '^ATOMIC_POSITIONS' "$o" | sed -n "${nf}p" | cut -d: -f1)
rm -rf "$S" && mkdir -p "$S" || exit 1
head -n $((Lc - 1)) "$o" > "$S/done.out"
"$PY" "$H/qe_restart_input.py" "$L/$r/$r.in" "$S/done.out" "$S/last.in" x > /dev/null || exit 1
sp=$(sed -n '/^ATOMIC_SPECIES/,+5p' "$S/last.in" | awk 'NR > 1 {print $1}' | tr '\n' ' ')
[ "$sp" = "Fe H Ni O Ni2 " ] || { echo "$r: unexpected species order: $sp"; exit 1; }
L0=$(grep -n "^ATOMIC_POSITIONS angstrom" "$S/last.in" | cut -d: -f1)
ok=1
for c in $CF; do
  N=${c}__$r a=$S/${N}_a.in
  cp "$S/last.in" "$a"
  case $c in  # make_cfg_sp.sh, has2 = 1 branch (Ni 5, 29, 30 are species 5, Ni2)
    C1) m="--species-mag 1=0.3 --species-mag 5=-0.1" ;;
    C2) m="--species-mag 1=-0.3 --species-mag 5=0.1" ;;
    C3) sed -i "$((L0 + 30))s/ Ni2 / Ni /" "$a"; m="--species-mag 1=0.3 --species-mag 5=-0.1" ;;
    C4) sed -i -e "$((L0 + 5))s/ Ni2 / Ni /" -e "$((L0 + 29))s/ Ni2 / Ni /" "$a"; m="--species-mag 1=0.3 --species-mag 5=-0.1" ;;
    C5) sed -i -e "$((L0 + 5))s/ Ni2 / Ni /" -e "$((L0 + 29))s/ Ni2 / Ni /" "$a"; m="--species-mag 1=-0.3 --species-mag 5=-0.1" ;;
    C6) sed -i -e "$((L0 + 29))s/ Ni2 / Ni /" -e "$((L0 + 30))s/ Ni2 / Ni /" "$a"; m="--species-mag 1=0.3 --species-mag 5=-0.1" ;;
    C7) m="--species-mag 1=0.3 --species-mag 5=0.1" ;;
  esac
  # shellcheck disable=SC2086
  "$PY" "$H/make_magdiag.py" "$a" "$S/${N}_b.in" x $m > /dev/null || exit 1
  "$PY" "$H/make_variant.py" "$S/${N}_b.in" "$S/$N.in" "$N" --conv-thr 1.0d-5 > /dev/null || exit 1
  rm -f "$a" "$S/${N}_b.in"
  sed -i "s#outdir = '[^']*'#outdir = '$SCR/$N/tmp'#" "$S/$N.in"
  neg="" L2=$(grep -n "^ATOMIC_POSITIONS angstrom" "$S/$N.in" | cut -d: -f1)
  for at in 5 29 30; do
    sed -n "$((L2 + at))p" "$S/$N.in" | grep -q '^ *Ni2 ' && neg="$neg$at,"
  done
  fe=$(grep -o "starting_magnetization(1) = \S*" "$S/$N.in" | awk '{print $3}')
  n2=$(grep -o "starting_magnetization(5) = \S*" "$S/$N.in" | awk '{print $3}')
  echo "$N: $(grep -o "calculation = '[a-z]*'" "$S/$N.in"), Fe start $fe, Ni2 start ${n2:-none} on atoms ${neg:-none}"
  case "$c:$fe:$n2:$neg" in
    C1:0.3:-0.1:5,29,30,|C2:-0.3:0.1:5,29,30,|C3:0.3:-0.1:5,29,|C4:0.3:-0.1:30,|C5:-0.3:-0.1:30,|C6:0.3:-0.1:5,|C7:0.3:0.1:5,29,30,) ;;
    *) echo "CHECK FAILED: $N does not encode $c"; ok=0 ;;
  esac
  for s in "prefix = '$N'" "calculation = 'scf'" "conv_thr = 1.0d-5" "outdir = '$SCR/$N/tmp'" \
           "pseudo_dir = '/anvil/projects/x-che260157/pseudo'" "mixing_beta = 0.05" "electron_maxstep = 200"; do
    [ "$(grep -c "$s" "$S/$N.in")" = 1 ] || { echo "CHECK FAILED: $N.in lacks exactly one '$s'"; ok=0; }
  done
  grep -q "startingpot\|startingwfc" "$S/$N.in" && { echo "CHECK FAILED: $N.in is not a cold start"; ok=0; }
  grep -q $'\r' "$S/$N.in" && { echo "CHECK FAILED: CRLF in $N.in"; ok=0; }
done
# positions: every input equals the accepted step's geometry (block nf-1 of RUN.out)
"$PY" - "$o" "$nf" "$S" $CF <<'EOF' || ok=0
import re, sys
out = open(sys.argv[1], errors="replace").read(); k = int(sys.argv[2]); S = sys.argv[3]
nat0 = int(re.search(r"number of atoms/cell\s+=\s+(\d+)", out).group(1))
blocks = re.findall(r"ATOMIC_POSITIONS \(angstrom\)\n((?:.*\n){%d})" % nat0, out)
ref = [[float(v) for v in l.split()[1:4]] for l in blocks[k - 2].strip().split("\n")]
worst = 0.0
for c in sys.argv[4:]:
    t = open("%s/%s__%s.in" % (S, c, S.split("cfgsp_")[1])).read()
    nat = int(re.search(r"nat = (\d+)", t).group(1)); assert nat == nat0, (nat, nat0)
    rows = [l.split()[1:4] for l in t.split("ATOMIC_POSITIONS angstrom\n", 1)[1].split("\n")[:nat]]
    worst = max(worst, max(abs(float(a) - b) for r1, r2 in zip(rows, ref) for a, b in zip(r1, r2)))
print("positions vs block %d (step %d's geometry): max |dx| %.2e A over all inputs" % (k - 1, k, worst))
sys.exit(0 if worst < 1e-6 else 1)
EOF
rm -f "$S/done.out" "$S/last.in"
[ "$ok" = 1 ] || { echo "STAGE FAILED"; exit 1; }
(cd "$S" && md5sum ./*.in)
echo "STAGED $S"
