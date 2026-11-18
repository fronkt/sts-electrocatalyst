#!/usr/bin/env bash
# Amendment 23: two follow-up checks of V1, as fixed-geometry single points on Anvil.
#   A  NiOOH configuration single points (U = 0): make_cfg_sp.sh's recipe (scf, conv_thr 1e-5, cold
#      start, the relaxation's own mixing) with the Ni(Fe)OOH candidates C1-C5 carried to NiOOH, the site
#      Ni (atom 6) in Fe's role. Ni0_OH: C1 C3 C4; Ni0_O: C1 C2 C3 C4 C5 (the amendment lists why).
#   B  PBE+U single points (Ni 6.2, Fe 5.3 eV) at the U = 0 geometry of each of the 8 V1 states, started
#      from that state's own converged U = 0 density (make_u_sp.py).
#   bash anvil_a23.sh stage     # local only: build the 16 inputs, check them, stage the densities
#   bash anvil_a23.sh deploy    # upload, md5-check, sbatch each (2 h limit)
set -u
# Git Bash rewrites /anvil/... arguments of native programs into C:/Program Files/Git/anvil/...; the
# Anvil paths handed to python (make_u_sp.py) must stay as written. /d/... paths still convert.
export MSYS2_ARG_CONV_EXCL="/anvil"
MODE=${1:?stage|deploy}
A=x-fcai3@anvil.rcac.purdue.edu; SO="-o BatchMode=yes -o ConnectTimeout=30"
SCR=/anvil/scratch/x-fcai3/film PSD=/anvil/projects/x-che260157/pseudo
L=/d/sts-electrocatalyst/film_pilot/out/runs K=/d/sts-electrocatalyst/film_pilot/out/densities/keep
S=/d/sts-electrocatalyst/film_pilot/anvil_stage_a23
PY=${PY:-D:/sts-electrocatalyst/.venv-isef/Scripts/python.exe}
H=$(cd "$(dirname "$0")" && pwd)
# A: run -> configurations; relabelled (Ni2, start -0.1) atoms per configuration, 1-based
A_RUNS="u0__NiOOH__Ni0_OH:C1,C3,C4 u0__NiOOH__Ni0_O_r2:C1,C2,C3,C4,C5"
neg_of() { case $1 in C1) echo 5,29,30 ;; C2) echo 6 ;; C3) echo 5,29 ;; C4) echo 30 ;; C5) echo 6,30 ;; esac; }
# B: run -> density source (keep = D: kept density; anvil:DIR = a save directory on Anvil scratch)
B_RUNS="u0__NiOOH__slab_r2:keep u0__NiOOH__Ni0_OH:keep u0__NiOOH__Ni0_O_r2:keep
  u0__NiOOH__Ni0_OOH_r7:anvil:$SCR/u0__NiOOH__Ni0_OOH_r7/tmp/u0__NiOOH__Ni0_OOH_r7.save
  u0__NiFeOOH__slab:keep u0__NiFeOOH__Fe0_OH_r11:anvil:$SCR/C2__u0__NiFeOOH__Fe0_OH_r11/tmp/C2__u0__NiFeOOH__Fe0_OH_r11.save
  u0__NiFeOOH__Fe0_O_r2:keep u0__NiFeOOH__Fe0_OOH:keep"
# geometry block of each run's output: the final block (0 = last), except Fe0_OH (amendment 22: r11's
# accepted step 2 = block 1; block 2 is step 3's trial geometry)
blk_of() { [ "$1" = u0__NiFeOOH__Fe0_OH_r11 ] && echo 1 || echo 0; }
names() {
  for e in $A_RUNS; do r=${e%%:*}; for c in $(echo "${e#*:}" | tr , ' '); do echo "A23${c}__$r"; done; done
  for e in $B_RUNS; do echo "A23U__${e%%:*}"; done
}

if [ "$MODE" = deploy ]; then
  [ -f "$S/STAGED" ] || { echo "not staged"; exit 1; }
  # ONLY="NAME ..." deploys a subset (a resumed deploy); default: all 16
  for N in ${ONLY:-$(names)}; do
    ssh $SO $A "test -e $SCR/$N && { echo $N EXISTS; exit 1; }; mkdir -p $SCR/$N/tmp" || exit 1
    scp -q $SO "$S/$N.in" "$A:$SCR/$N/$N.in" || exit 1
    if [ -d "$S/dens/$N" ]; then  # B, kept density from D:
      ssh $SO $A "mkdir -p $SCR/$N/tmp/$N.save" || exit 1
      scp -q $SO "$S/dens/$N/charge-density.hdf5" "$S/dens/$N/occup.txt" "$S/dens/$N/paw.txt" "$A:$SCR/$N/tmp/$N.save/" || exit 1
      ssh $SO $A "cd $SCR/$N/tmp/$N.save && md5sum charge-density.hdf5 occup.txt paw.txt" > "$S/dens/$N/remote.md5" || exit 1
      # Windows md5sum marks binary mode with '*' before the name; Linux does not
      diff <(awk '{sub(/^\*/, "", $2); print $1, $2}' "$S/dens/$N/local.md5") \
           <(awk '{sub(/^\*/, "", $2); print $1, $2}' "$S/dens/$N/remote.md5") || { echo "$N: density md5 mismatch"; exit 1; }
    elif [ -f "$S/src_$N" ]; then  # B, density already on Anvil
      src=$(cat "$S/src_$N")
      ssh $SO $A "set -e; mkdir -p $SCR/$N/tmp/$N.save; cd $SCR/$N/tmp/$N.save
        for f in charge-density.hdf5 occup.txt paw.txt; do cp -p $src/\$f .; cmp \$f $src/\$f; done" || { echo "$N: copy failed"; exit 1; }
    fi
    m=$(md5sum < "$S/$N.in" | cut -d' ' -f1)
    ssh $SO $A "set -e; cd $SCR/$N; [ \$(md5sum < $N.in | cut -d' ' -f1) = $m ]; ! grep -q \$'\r' $N.in
      cd $SCR && sbatch -t 02:00:00 -J $N --export=ALL,N=$N anvil_film_scr.slurm" || exit 1
  done
  exit 0
fi

[ "$MODE" = stage ] || { echo "mode?"; exit 1; }
rm -rf "$S" && mkdir -p "$S/dens" || exit 1
ok=1
# ---- A
for e in $A_RUNS; do
  r=${e%%:*}
  "$PY" "$H/qe_restart_input.py" "$L/$r/$r.in" "$L/$r/$r.out" "$S/last_$r.in" x > /dev/null || exit 1
  sp=$(sed -n '/^ATOMIC_SPECIES/,+3p' "$S/last_$r.in" | awk 'NR > 1 {print $1}' | tr '\n' ' ')
  [ "$sp" = "H Ni O " ] || { echo "$r: unexpected species order: $sp"; exit 1; }
  for c in $(echo "${e#*:}" | tr , ' '); do
    N=A23${c}__$r neg=$(neg_of "$c")
    "$PY" "$H/make_magdiag.py" "$S/last_$r.in" "$S/${N}_b.in" x --relabel "$neg:Ni2:-0.1" > /dev/null || exit 1
    "$PY" "$H/make_variant.py" "$S/${N}_b.in" "$S/$N.in" "$N" --conv-thr 1.0d-5 > /dev/null || exit 1
    rm -f "$S/${N}_b.in"
    sed -i -e "s#outdir = '[^']*'#outdir = '$SCR/$N/tmp'#" -e "s#pseudo_dir = '[^']*'#pseudo_dir = '$PSD'#" "$S/$N.in"
    got="" L2=$(grep -n "^ATOMIC_POSITIONS angstrom" "$S/$N.in" | cut -d: -f1)
    for at in $(seq 1 30); do sed -n "$((L2 + at))p" "$S/$N.in" | grep -q '^ *Ni2 ' && got="$got$at,"; done
    m2=$(grep -o "starting_magnetization(2) = \S*" "$S/$N.in" | awk '{print $3}')
    m4=$(grep -o "starting_magnetization(4) = \S*" "$S/$N.in" | awk '{print $3}')
    echo "$N: Ni start $m2, Ni2 start $m4 on atoms ${got:-none}; $(grep -o "U Ni2-3d \S*" "$S/$N.in")"
    [ "$got" = "$neg," ] && [ "$m2" = 0.1 ] && [ "$m4" = -0.1 ] || { echo "CHECK FAILED: $N does not encode $c"; ok=0; }
    for s in "prefix = '$N'" "calculation = 'scf'" "conv_thr = 1.0d-5" "outdir = '$SCR/$N/tmp'" "pseudo_dir = '$PSD'" \
             "mixing_beta = 0.1" "mixing_ndim = 12" "mixing_mode = 'local-TF'" "electron_maxstep = 200" \
             "U Ni-3d 1.0d-8" "U Ni2-3d 1.0d-8" "ntyp = 4"; do
      [ "$(grep -c "$s" "$S/$N.in")" = 1 ] || { echo "CHECK FAILED: $N.in lacks exactly one '$s'"; ok=0; }
    done
    grep -q "startingpot\|startingwfc" "$S/$N.in" && { echo "CHECK FAILED: $N.in is not a cold start"; ok=0; }
    grep -q $'\r' "$S/$N.in" && { echo "CHECK FAILED: CRLF in $N.in"; ok=0; }
    "$PY" "$H/a23_check.py" pos "$L/$r/$r.out" 0 "$S/$N.in" || ok=0
  done
  rm -f "$S/last_$r.in"
done
# ---- B
for e in $B_RUNS; do
  r=${e%%:*} src=${e#*:} N=A23U__${e%%:*} k=$(blk_of "${e%%:*}")
  o=$L/$r/$r.out
  if [ "$k" != 0 ]; then  # the accepted step's geometry: cut the output before block k + 1
    Lc=$(grep -a -n '^ATOMIC_POSITIONS' "$o" | sed -n "$((k + 1))p" | cut -d: -f1)
    head -n $((Lc - 1)) "$o" > "$S/done_$r.out"; o=$S/done_$r.out
  fi
  "$PY" "$H/qe_restart_input.py" "$L/$r/$r.in" "$o" "$S/last_$r.in" x > /dev/null || exit 1
  "$PY" "$H/make_u_sp.py" "$S/last_$r.in" "$S/$N.in" "$N" "$SCR/$N/tmp" "$PSD" || exit 1
  rm -f "$S/last_$r.in" "$S/done_$r.out"
  case $r in *NiFeOOH*) want="U Fe-3d 5.3 U Ni-3d 6.2" ;; *) want="U Ni-3d 6.2" ;; esac
  grep -q "^ATOMIC_SPECIES" "$S/$N.in" && sed -n '/^ATOMIC_SPECIES/,+5p' "$S/$N.in" | grep -q '^ *Ni2 ' && want="$want U Ni2-3d 6.2"
  [ "$(sed -n '/^HUBBARD/,$p' "$S/$N.in" | grep '^U ' | tr '\n' ' ')" = "$want " ] || { echo "CHECK FAILED: $N U card"; ok=0; }
  for s in "prefix = '$N'" "calculation = 'scf'" "conv_thr = 1.0d-5" "outdir = '$SCR/$N/tmp'" "pseudo_dir = '$PSD'" \
           "startingpot = 'file'" "mixing_beta = 0.05" "mixing_ndim = 20" "mixing_mode = 'local-TF'" "electron_maxstep = 200"; do
    [ "$(grep -c "$s" "$S/$N.in")" = 1 ] || { echo "CHECK FAILED: $N.in lacks exactly one '$s'"; ok=0; }
  done
  grep -q "startingwfc" "$S/$N.in" && { echo "CHECK FAILED: $N.in sets startingwfc"; ok=0; }
  grep -q $'\r' "$S/$N.in" && { echo "CHECK FAILED: CRLF in $N.in"; ok=0; }
  # only the intended lines differ from the U = 0 input (positions aside)
  diff <(sed '/^ATOMIC_POSITIONS/,/^K_POINTS/d' "$L/$r/$r.in") <(sed '/^ATOMIC_POSITIONS/,/^K_POINTS/d' "$S/$N.in") \
    | grep '^[<>]' | sed 's/^/    diff /'
  "$PY" "$H/a23_check.py" pos "$L/$r/$r.out" "$k" "$S/$N.in" || ok=0
  if [ "$src" = keep ]; then
    mkdir -p "$S/dens/$N" && cp -p "$K/$r/charge-density.hdf5" "$K/$r/occup.txt" "$K/$r/paw.txt" "$S/dens/$N/" || exit 1
    (cd "$S/dens/$N" && md5sum charge-density.hdf5 occup.txt paw.txt > local.md5)
    [ -f "$K/$r/data-file-schema.xml" ] && { "$PY" "$H/a23_check.py" xml "$L/$r/$r.out" "$k" "$K/$r/data-file-schema.xml" || ok=0; }
  else
    d=${src#anvil:}; echo "$d" > "$S/src_$N"
    scp -q $SO "$A:$d/data-file-schema.xml" "$S/xml_$N.xml" || exit 1
    ssh $SO $A "cd $d && ls charge-density.hdf5 occup.txt paw.txt" > /dev/null || { echo "$N: density files missing on Anvil"; ok=0; }
    "$PY" "$H/a23_check.py" xml "$L/$r/$r.out" "$k" "$S/xml_$N.xml" || ok=0
  fi
done
[ "$ok" = 1 ] || { echo "STAGE FAILED"; exit 1; }
(cd "$S" && md5sum ./*.in) | tee "$S/inputs.md5"
date -u +%FT%TZ > "$S/STAGED"
echo "STAGED $S: $(names | wc -l) inputs"
