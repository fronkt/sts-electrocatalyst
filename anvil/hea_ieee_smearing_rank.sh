#!/bin/bash
# Open MPI supplies world rank/size; exec preserves the launched process identity.
# https://docs.open-mpi.org/en/main/tuning-apps/environment-var.html
set -euo pipefail
set -C
: "${QE_PREFIX:?QE_PREFIX required}"
: "${DIAG_RANK_DIR:?DIAG_RANK_DIR required}"
[ "${OMPI_COMM_WORLD_SIZE:-}" = 128 ] || { echo "REFUSE: world size differs" >&2; exit 90; }
rank=${OMPI_COMM_WORLD_RANK:-}
[[ "$rank" =~ ^(0|[1-9][0-9]*)$ ]] && [ "$rank" -lt 128 ] || {
  echo "REFUSE: invalid MPI rank" >&2; exit 90
}
[ "$#" = 5 ] && [ "$2" = -nk ] && [ "$3" = 8 ] && [ "$4" = -in ] || {
  echo "REFUSE: diagnostic command differs" >&2; exit 90
}
case "$1:$5" in
  "$QE_PREFIX/bin/pw.x:hd__leader_pull2.10__ortho__smearing_repro.run.in") ;;
  "$QE_PREFIX/bin/projwfc.x:hd__leader_pull2.10__ortho__smearing_repro.projwfc.in") ;;
  *) echo "REFUSE: unexpected diagnostic executable/input" >&2; exit 90 ;;
esac
[ -d "$DIAG_RANK_DIR" ] && [ ! -L "$DIAG_RANK_DIR" ] || {
  echo "REFUSE: rank capture directory invalid" >&2; exit 90
}
printf -v name 'rank%03d.stderr' "$rank"
path="$DIAG_RANK_DIR/$name"
[ ! -e "$path" ] && [ ! -L "$path" ] || { echo "REFUSE: rank stderr exists" >&2; exit 90; }
exec "$@" 2> "$path"
