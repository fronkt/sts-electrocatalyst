#!/usr/bin/env bash
# After the spend guard stops the box's runs (DEADLINE_HIT), copy the restart densities that out.tgz
# leaves out to D: (runs/u0__*/tmp/*.save: charge density, Hubbard occupations, PAW becsum, schema; and
# keep/, post_relax.sh's hardlinks), so any continuation can restart with startingpot = 'file', the
# start that got the stalled SCFs through on 2026-11-16. Never touches PULLED, so it cannot hold the
# box: the watchdog packages out.tgz 30 min after the last pw.x, and the pull loop releases the box.
#   bash density_pull.sh            (run_in_background; 2-min polls for up to 16 h)
#   DRY=1 FORCE_NOW=1 bash density_pull.sh   (list what would be copied, now)
set -u
B=/d/sts-electrocatalyst/film_pilot
S=(-o BatchMode=yes -o UserKnownHostsFile=$B/known_hosts -o ConnectTimeout=20)
H=ubuntu@44.204.146.192
D=${DENS_D:-$B/out/densities}
LIST=${LIST:-'ls -d runs/u0__*/tmp/*.save keep 2>/dev/null'}  # test knobs LIST, DENS_D; U = 0 runs only (the PBE+U saves carry wavefunctions, 5-6 GB each)
if [ "${FORCE_NOW:-0}" != 1 ]; then
  for i in $(seq 1 480); do
    st=$(timeout 60 ssh "${S[@]}" $H 'cd ~/film; [ -f PULLED ] && echo pulled; [ -f DEADLINE_HIT ] && echo hit' 2>/dev/null)
    case "$st" in *pulled*) echo "PULLED already set; box is being released; no density pull $(date -u +%FT%TZ)"; exit 2 ;; esac
    case "$st" in *hit*) break ;; esac
    sleep 120
  done
  case "$st" in *hit*) ;; *) echo "no DEADLINE_HIT after 16 h $(date -u +%FT%TZ)"; exit 3 ;; esac
  sleep 60  # deadline.sh has already pkilled pw.x before touching DEADLINE_HIT; margin for exits
fi
if [ "${DRY:-0}" = 1 ]; then
  ssh "${S[@]}" $H "cd ~/film; for p in \$($LIST); do echo \"\$(du -sh \$p | cut -f1) \$p\"; done; du -shc \$($LIST) | tail -1"
  exit 0
fi
mkdir -p "$D" || exit 1
for attempt in 1 2 3; do
  ssh "${S[@]}" $H "cd ~/film; tar cf densities.tar \$($LIST) && md5sum densities.tar > densities.tar.md5" \
    && scp "${S[@]}" $H:film/densities.tar $H:film/densities.tar.md5 "$D/" \
    && (cd "$D" && md5sum -c densities.tar.md5) && break
  sleep 30
done
if (cd "$D" && md5sum -c densities.tar.md5 > /dev/null 2>&1); then
  (cd "$D" && tar xf densities.tar) && echo "DENSITIES_PULLED $(du -sh "$D" | cut -f1) $(date -u +%FT%TZ)"
  exit 0
fi
echo "density pull failed md5 check $(date -u +%FT%TZ)"; exit 4
