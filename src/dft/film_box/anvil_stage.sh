#!/usr/bin/env bash
# Amendment 21 (2026-11-17, before any eta existed): stage V1's two open relaxations for Anvil
# (CHE260157), from the AWS outputs and kept densities pulled to D: on 2026-11-17.
#   u0__NiOOH__Ni0_OOH_r6    = r4 (BFGS) restarted from its last completed geometry (step 44) and that
#                              step's kept density; r4's input otherwise unchanged (conv_thr 5e-6)
#   u0__NiFeOOH__Fe0_OH_r11  = r7 (FIRE) restarted from its last completed geometry (step 2) and that
#                              step's kept density; conv_thr 1e-5 (amendment 10's noise-floor value)
#                              in place of 5e-6; r7's input otherwise unchanged
# Only pseudo_dir changes besides prefix, positions and (r11) conv_thr. Writes STAGE/NAME/NAME.in and
# STAGE/NAME/tmp/NAME.save/{charge-density.hdf5,occup.txt,paw.txt}, then STAGE.tar + md5. Touches
# nothing on Anvil.
#   bash anvil_stage.sh
set -u
B=/d/sts-electrocatalyst/film_pilot/out
R=$B/runs K=$B/densities/keep
S=${STAGE:-/d/sts-electrocatalyst/film_pilot/anvil_stage}
PY=${PY:-D:/sts-electrocatalyst/.venv-isef/Scripts/python.exe}
H=$(cd "$(dirname "$0")" && pwd)
PSEUDO=/anvil/projects/x-che260157/pseudo
rm -rf "$S" "$S.tar" "$S.tar.md5" && mkdir -p "$S" || exit 1
ok=1
for spec in "u0__NiOOH__Ni0_OOH_r6 u0__NiOOH__Ni0_OOH_r4 5.0d-6" \
            "u0__NiFeOOH__Fe0_OH_r11 u0__NiFeOOH__Fe0_OH_r7 1.0d-5"; do
  set -- $spec; N=$1 P=$2 CT=$3
  o=$R/$P/$P.out
  nb=$(grep -a -c '^!' "$o"); nblk=$(grep -a -c '^ATOMIC_POSITIONS' "$o")
  # stopped in step nb+1's SCF: nb blocks, the last is that step's trial geometry
  [ "$nb" -ge 2 ] && [ "$nblk" = "$nb" ] || { echo "$P: $nb steps, $nblk blocks: no restart"; exit 1; }
  L=$(grep -a -n '^ATOMIC_POSITIONS' "$o" | tail -1 | cut -d: -f1)
  mkdir -p "$S/$N/tmp/$N.save" || exit 1
  head -n $((L - 1)) "$o" > "$S/${P}_done.out"
  "$PY" "$H/qe_restart_input.py" "$R/$P/$P.in" "$S/${P}_done.out" "$S/$N/$N.in" "$N" --conv-thr "$CT" > /dev/null || exit 1
  rm -f "$S/${P}_done.out"
  sed -i "s#pseudo_dir = '[^']*'#pseudo_dir = '$PSEUDO'#" "$S/$N/$N.in"
  for s in "prefix = '$N'" "conv_thr = $CT" "pseudo_dir = '$PSEUDO'" "startingpot = 'file'" \
           "mixing_beta = 0.05" "mixing_ndim = 20" "forc_conv_thr = 2.0d-3" "upscale = 1.d0" "outdir = './tmp'"; do
    [ "$(grep -c "$s" "$S/$N/$N.in")" = 1 ] || { echo "CHECK FAILED: $N.in lacks exactly one '$s'"; ok=0; }
  done
  grep -q $'\r' "$S/$N/$N.in" && { echo "CHECK FAILED: CRLF in $N.in"; ok=0; }
  for f in charge-density.hdf5 occup.txt paw.txt; do
    cp -p "$K/$P/$f" "$S/$N/tmp/$N.save/" || { echo "no kept $f for $P"; ok=0; }
  done
  echo "== $P.in -> $N.in (non-position lines)"
  diff <(sed '/^ATOMIC_POSITIONS/,$d' "$R/$P/$P.in") <(sed '/^ATOMIC_POSITIONS/,$d' "$S/$N/$N.in")
  "$PY" - "$o" "$S/$N/$N.in" "$K/$P/charge-density.hdf5" <<'EOF'
import os, re, sys, datetime as dt
out = open(sys.argv[1], errors="replace").read(); inp = open(sys.argv[2]).read()
nat = int(re.search(r"nat = (\d+)", inp).group(1))
blocks = re.findall(r"ATOMIC_POSITIONS \(angstrom\)\n((?:.*\n){%d})" % nat, out)
new = [l.split()[1:4] for l in inp.split("ATOMIC_POSITIONS angstrom\n", 1)[1].split("\n")[:nat]]
def dx(b):
    rows = [l.split()[1:4] for l in b.strip().split("\n")]
    return max(abs(float(a) - float(c)) for r1, r2 in zip(rows, new) for a, c in zip(r1, r2))
E = re.findall(r"^!\s+total energy\s+=\s+(\S+) Ry", out, re.M)
t0 = re.search(r"Program PWSCF v\.\S+ starts on (\S+) at\s+(\d+:\s*\d+:\s*\d+)", out)
cpu = re.findall(r"total cpu time spent up to now is\s+([\d.]+) secs", out[:out.rfind("\n!")])
start = dt.datetime.strptime(t0.group(1) + " " + t0.group(2).replace(" ", ""), "%d%b%Y %H:%M:%S")
mt = dt.datetime.fromtimestamp(os.path.getmtime(sys.argv[3]), dt.timezone.utc)
print("   positions vs block %d (last completed step): max |dx| %.2e A; vs block %d (stalled trial): %.4f A"
      % (len(blocks) - 1, dx(blocks[-2]), len(blocks), dx(blocks[-1])))
print("   last completed step %d: E %s Ry; reached about %s UTC (start + cpu time); kept density written %s UTC"
      % (len(E), E[-1], (start + dt.timedelta(seconds=float(cpu[-1]))).strftime("%H:%M:%S"), mt.strftime("%m-%d %H:%M:%S")))
EOF
done
[ "$ok" = 1 ] || exit 1
(cd "$(dirname "$S")" && tar cf "$(basename "$S").tar" "$(basename "$S")" && md5sum "$(basename "$S").tar" > "$(basename "$S").tar.md5") || exit 1
echo "STAGED $(du -sh "$S.tar" | cut -f1) $(cat "$S.tar.md5")"
