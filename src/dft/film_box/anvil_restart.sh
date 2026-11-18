#!/usr/bin/env bash
# Amendment 21's restart rule for a run that ended on Anvil: NEW restarts PRED from PRED's last
# completed step (the last step with forces) and that step's density, with PRED's input otherwise
# unchanged except prefix, positions and OUTDIR (pw.x scratch; physics untouched).
#   bash anvil_restart.sh stage  NEW PRED OUTDIR   # local only: build NEW.in from the pulled PRED.out
#   bash anvil_restart.sh deploy NEW PRED OUTDIR   # upload NEW.in, copy PRED's density, sbatch
# PRED.in/.out must already be pulled to $L/PRED/ (md5-checked against Anvil).
set -u
MODE=${1:?stage|deploy} N=${2:?NEW} P=${3:?PRED} OD=${4:?OUTDIR}
A=x-fcai3@anvil.rcac.purdue.edu; SO="-o BatchMode=yes -o ConnectTimeout=30"
RR=/anvil/projects/x-che260157/film/runs
L=/d/sts-electrocatalyst/film_pilot/out/runs
S=/d/sts-electrocatalyst/film_pilot/anvil_stage_$N
PY=${PY:-D:/sts-electrocatalyst/.venv-isef/Scripts/python.exe}
H=$(cd "$(dirname "$0")" && pwd)
o=$L/$P/$P.out
nb=$(grep -a -c '^!' "$o"); nf=$(grep -a -c 'Forces acting on atoms' "$o"); nblk=$(grep -a -c '^ATOMIC_POSITIONS' "$o")
# block k (1-based) is the geometry of step k+1; the last completed step is nf, so cut before block nf
[ "$nf" -ge 2 ] && [ "$nblk" -ge "$nf" ] || { echo "$P: $nb SCFs, $nf force blocks, $nblk blocks: no restart"; exit 1; }
Lc=$(grep -a -n '^ATOMIC_POSITIONS' "$o" | sed -n "${nf}p" | cut -d: -f1)
if [ "$MODE" = stage ]; then
  rm -rf "$S" && mkdir -p "$S" || exit 1
  head -n $((Lc - 1)) "$o" > "$S/${P}_done.out"
  "$PY" "$H/qe_restart_input.py" "$L/$P/$P.in" "$S/${P}_done.out" "$S/$N.in" "$N" > /dev/null || exit 1
  rm -f "$S/${P}_done.out"
  sed -i "s#outdir = '[^']*'#outdir = '$OD'#" "$S/$N.in"
  ok=1
  for s in "prefix = '$N'" "outdir = '$OD'" "startingpot = 'file'"; do
    [ "$(grep -c "$s" "$S/$N.in")" = 1 ] || { echo "CHECK FAILED: $N.in lacks exactly one '$s'"; ok=0; }
  done
  grep -q $'\r' "$S/$N.in" && { echo "CHECK FAILED: CRLF in $N.in"; ok=0; }
  echo "== $P: $nb SCFs, $nf force blocks, $nblk geometry blocks; last completed step $nf"
  echo "== $P.in -> $N.in (non-position lines)"
  diff <(sed '/^ATOMIC_POSITIONS/,$d' "$L/$P/$P.in") <(sed '/^ATOMIC_POSITIONS/,$d' "$S/$N.in")
  "$PY" - "$o" "$S/$N.in" "$nf" <<'EOF'
import re, sys, datetime as dt
out = open(sys.argv[1], errors="replace").read(); inp = open(sys.argv[2]).read(); k = int(sys.argv[3])
nat = int(re.search(r"nat = (\d+)", inp).group(1))
blocks = re.findall(r"ATOMIC_POSITIONS \(angstrom\)\n((?:.*\n){%d})" % nat, out)
new = [l.split()[1:4] for l in inp.split("ATOMIC_POSITIONS angstrom\n", 1)[1].split("\n")[:nat]]
def dx(b):
    rows = [l.split()[1:4] for l in b.strip().split("\n")]
    return max(abs(float(a) - float(c)) for r1, r2 in zip(rows, new) for a, c in zip(r1, r2))
E = re.findall(r"^!\s+total energy\s+=\s+(\S+) Ry", out, re.M)
msg = "   positions vs block %d (step %d's geometry): max |dx| %.2e A" % (k - 1, k, dx(blocks[k - 2]))
if len(blocks) >= k:
    msg += "; vs block %d (step %d's geometry): %.4f A" % (k, k + 1, dx(blocks[k - 1]))
print(msg)
t0 = re.search(r"Program PWSCF v\.\S+ starts on (\S+) at\s+(\d+:\s*\d+:\s*\d+)", out)
start = dt.datetime.strptime(t0.group(1) + " " + t0.group(2).replace(" ", ""), "%d%b%Y %H:%M:%S")
ends = [m.start() for m in re.finditer(r"^!", out, re.M)]
for j in range(len(ends)):
    if j + 1 >= k - 1:
        cpu = re.findall(r"total cpu time spent up to now is\s+([\d.]+) secs", out[:ends[j]])
        print("   step %d: E %s Ry, SCF done at about %s local (start + cpu time)"
              % (j + 1, E[j], (start + dt.timedelta(seconds=float(cpu[-1]))).strftime("%H:%M:%S")))
EOF
  [ "$ok" = 1 ] || exit 1
  md5sum "$S/$N.in"
  echo "STAGED $S/$N.in"
  exit 0
fi
[ "$MODE" = deploy ] || { echo "mode?"; exit 1; }
[ -f "$S/$N.in" ] || { echo "stage first"; exit 1; }
m=$(md5sum < "$S/$N.in" | cut -d' ' -f1)
ssh $SO $A "test -e $RR/$N && { echo EXISTS; exit 1; }; mkdir -p $RR/$N" || exit 1
scp -q $SO "$S/$N.in" "$A:$RR/$N/$N.in" || exit 1
ssh $SO $A "set -e; cd $RR/$N; [ \$(md5sum < $N.in | cut -d' ' -f1) = $m ]; ! grep -q \$'\r' $N.in
  mkdir -p $OD/$N.save; D=$RR/$P/tmp/$P.save
  ls -l --time-style=full-iso \$D/charge-density.hdf5 \$D/occup.txt \$D/paw.txt
  cp -p \$D/charge-density.hdf5 \$D/occup.txt \$D/paw.txt $OD/$N.save/
  for f in charge-density.hdf5 occup.txt paw.txt; do cmp \$D/\$f $OD/$N.save/\$f; done
  cd /anvil/projects/x-che260157/film && md5sum anvil_film.slurm && sbatch -J $N --export=ALL,N=$N anvil_film.slurm" || exit 1
