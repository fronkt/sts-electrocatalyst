#!/usr/bin/env bash
# Amendment 9: fixed-geometry single points of a finished Ni(Fe)OOH U = 0 relaxation in each candidate
# magnetic configuration (pw.x 1-based atoms; Fe = atom 6, the Fe site):
#   C1  Fe +, Ni 5, 29, 30 -   (the clean slab's relaxed configuration)
#   C2  Fe -, every Ni +       (the Fe-site *O relaxation's configuration)
#   C3  Fe +, Ni 5, 29 -       (the Fe-site *OOH relaxation's configuration)
#   C4  Fe +, Ni 30 -          (Fe0_OH_r4's first SCF, 2026-11-16; rule 1 adds every pattern seen)
#   C5  Fe -, Ni 30 -          (where the clean slab's C2 single point landed, 2026-11-16; amendment 11)
#   C6  Fe +, Ni 5 -           (the pattern Fe0_OOH's relaxation ended in, 2026-11-16 16:18Z; rule 1)
#   C7  Fe +, every Ni +       (the pattern Fe0_OH_r6's step-8 SCF entered, 2026-11-16 22:05Z; rule 3)
# Writes inputs/CK__RUN.in for K in $CFGS (default C1-C7; scf, conv_thr 1e-5 per amendment 10, cold
# start) from RUN's last printed geometry.
#   bash make_cfg_sp.sh RUN [OUTDIR]      (FORCE=1 skips the converged-relaxation check, for dry runs)
set -u
W=$HOME/film
cd "$W" || exit 1
r=$1 od=${2:-inputs}
f=runs/$r/$r.out
[ "${FORCE:-0}" = 1 ] || grep -q -e "bfgs converged" -e "FIRE: convergence achieved" "$f" || { echo "$r: relaxation has not converged; no single points"; exit 1; }
python3 qe_restart_input.py "runs/$r/$r.in" "$f" "/tmp/${r}_last.in" x > /dev/null || exit 1
sp=$(sed -n '/^ATOMIC_SPECIES/,+5p' "/tmp/${r}_last.in" | awk 'NR > 1 {print $1}' | tr '\n' ' ')
case "$sp" in
  "Fe H Ni O Ni2 ") has2=1 ;;
  "Fe H Ni O "*) has2=0 ;;
  *) echo "$r: unexpected species order: $sp"; exit 1 ;;
esac
L=$(grep -n "^ATOMIC_POSITIONS angstrom" "/tmp/${r}_last.in" | cut -d: -f1)
for c in ${CFGS:-C1 C2 C3 C4 C5 C6 C7}; do
  N=${c}__$r
  a=/tmp/${N}_a.in
  cp "/tmp/${r}_last.in" "$a"
  if [ "$has2" -eq 1 ]; then  # Ni 5, 29, 30 are already species 5 (Ni2)
    case $c in
      C1) m="--species-mag 1=0.3 --species-mag 5=-0.1" ;;
      C2) m="--species-mag 1=-0.3 --species-mag 5=0.1" ;;
      C3) sed -i "$((L + 30))s/ Ni2 / Ni /" "$a"; m="--species-mag 1=0.3 --species-mag 5=-0.1" ;;
      C4) sed -i -e "$((L + 5))s/ Ni2 / Ni /" -e "$((L + 29))s/ Ni2 / Ni /" "$a"; m="--species-mag 1=0.3 --species-mag 5=-0.1" ;;
      C5) sed -i -e "$((L + 5))s/ Ni2 / Ni /" -e "$((L + 29))s/ Ni2 / Ni /" "$a"; m="--species-mag 1=-0.3 --species-mag 5=-0.1" ;;
      C6) sed -i -e "$((L + 29))s/ Ni2 / Ni /" -e "$((L + 30))s/ Ni2 / Ni /" "$a"; m="--species-mag 1=0.3 --species-mag 5=-0.1" ;;
      C7) m="--species-mag 1=0.3 --species-mag 5=0.1" ;;
    esac
  else
    case $c in
      C1) m="--species-mag 1=0.3 --relabel 5,29,30:Ni2:-0.1" ;;
      C2) m="--species-mag 1=-0.3 --species-mag 3=0.1" ;;
      C3) m="--species-mag 1=0.3 --relabel 5,29:Ni2:-0.1" ;;
      C4) m="--species-mag 1=0.3 --relabel 30:Ni2:-0.1" ;;
      C5) m="--species-mag 1=-0.3 --relabel 30:Ni2:-0.1" ;;
      C6) m="--species-mag 1=0.3 --relabel 5:Ni2:-0.1" ;;
      C7) m="--species-mag 1=0.3 --species-mag 3=0.1" ;;
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
    C1:0.3:-0.1:5,29,30,|C2:-0.3:0.1:5,29,30,|C2:-0.3::|C3:0.3:-0.1:5,29,|C4:0.3:-0.1:30,|C5:-0.3:-0.1:30,|C6:0.3:-0.1:5,|C7:0.3:0.1:5,29,30,|C7:0.3::) ;;
    *) echo "$N: input does not encode $c; removing it"; rm -f "$od/$N.in"; exit 1 ;;
  esac
done
