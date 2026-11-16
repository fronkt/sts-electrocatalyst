#!/usr/bin/env bash
# Amendment 9: fixed-geometry single points of a finished Ni(Fe)OOH U = 0 relaxation in each candidate
# magnetic configuration (pw.x 1-based atoms; Fe = atom 6, the Fe site):
#   C1  Fe +, Ni 5, 29, 30 -   (the clean slab's relaxed configuration)
#   C2  Fe -, every Ni +       (the Fe-site *O relaxation's configuration)
#   C3  Fe +, Ni 5, 29 -       (the Fe-site *OOH relaxation's configuration)
#   C4  Fe +, Ni 30 -          (Fe0_OH_r4's first SCF, 2026-11-16; rule 1 adds every pattern seen)
# Writes inputs/C{1,2,3,4}__RUN.in (scf, conv_thr 1e-5 per amendment 10, cold start) from RUN's last printed geometry.
#   bash make_cfg_sp.sh RUN [OUTDIR]      (FORCE=1 skips the converged-relaxation check, for dry runs)
set -u
W=$HOME/film
cd "$W" || exit 1
r=$1 od=${2:-inputs}
f=runs/$r/$r.out
[ "${FORCE:-0}" = 1 ] || grep -q "bfgs converged" "$f" || { echo "$r: relaxation has not converged; no single points"; exit 1; }
python3 qe_restart_input.py "runs/$r/$r.in" "$f" "/tmp/${r}_last.in" x > /dev/null || exit 1
sp=$(sed -n '/^ATOMIC_SPECIES/,+5p' "/tmp/${r}_last.in" | awk 'NR > 1 {print $1}' | tr '\n' ' ')
case "$sp" in
  "Fe H Ni O Ni2 ") has2=1 ;;
  "Fe H Ni O "*) has2=0 ;;
  *) echo "$r: unexpected species order: $sp"; exit 1 ;;
esac
L=$(grep -n "^ATOMIC_POSITIONS angstrom" "/tmp/${r}_last.in" | cut -d: -f1)
for c in C1 C2 C3 C4; do
  N=${c}__$r
  a=/tmp/${N}_a.in
  cp "/tmp/${r}_last.in" "$a"
  if [ "$has2" -eq 1 ]; then  # Ni 5, 29, 30 are already species 5 (Ni2)
    case $c in
      C1) m="--species-mag 1=0.3 --species-mag 5=-0.1" ;;
      C2) m="--species-mag 1=-0.3 --species-mag 5=0.1" ;;
      C3) sed -i "$((L + 30))s/ Ni2 / Ni /" "$a"; m="--species-mag 1=0.3 --species-mag 5=-0.1" ;;
      C4) sed -i -e "$((L + 5))s/ Ni2 / Ni /" -e "$((L + 29))s/ Ni2 / Ni /" "$a"; m="--species-mag 1=0.3 --species-mag 5=-0.1" ;;
    esac
  else
    case $c in
      C1) m="--species-mag 1=0.3 --relabel 5,29,30:Ni2:-0.1" ;;
      C2) m="--species-mag 1=-0.3 --species-mag 3=0.1" ;;
      C3) m="--species-mag 1=0.3 --relabel 5,29:Ni2:-0.1" ;;
      C4) m="--species-mag 1=0.3 --relabel 30:Ni2:-0.1" ;;
    esac
  fi
  # shellcheck disable=SC2086
  python3 make_magdiag.py "$a" "/tmp/${N}_b.in" x $m > /dev/null || exit 1
  python3 make_variant.py "/tmp/${N}_b.in" "$od/$N.in" "$N" --conv-thr 1.0d-5 > /dev/null || exit 1
  # check: Fe start sign, and which of atoms 5, 29, 30 carry the negative species
  neg="" L2=$(grep -n "^ATOMIC_POSITIONS angstrom" "$od/$N.in" | cut -d: -f1)
  for at in 5 29 30; do
    sed -n "$((L2 + at))p" "$od/$N.in" | grep -q '^ *Ni2 ' && neg="$neg$at,"
  done
  fe=$(grep -o "starting_magnetization(1) = \S*" "$od/$N.in" | awk '{print $3}')
  n2=$(grep -o "starting_magnetization(5) = \S*" "$od/$N.in" | awk '{print $3}')
  calc=$(grep -o "calculation = '[a-z]*'" "$od/$N.in")
  echo "$od/$N.in: $calc, Fe start $fe, Ni2 start ${n2:-none} on atoms ${neg:-none}"
  case "$c:$fe:$n2:$neg" in
    C1:0.3:-0.1:5,29,30,|C2:-0.3:0.1:5,29,30,|C2:-0.3::|C3:0.3:-0.1:5,29,|C4:0.3:-0.1:30,) ;;
    *) echo "$N: input does not encode $c; removing it"; rm -f "$od/$N.in"; exit 1 ;;
  esac
done
