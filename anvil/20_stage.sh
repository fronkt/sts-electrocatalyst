#!/usr/bin/env bash
# Anvil bring-up step 2: stage the run tree, the pseudopotentials and the driver
# from Vast box 47662258 onto Anvil. Runs on the LOCAL machine (git-bash), which
# is the only host holding keys to both sides.
#
# tar-over-ssh rather than rsync: git-bash ships no rsync. Payload is ~35 MB.
set -euo pipefail

VAST=${VAST:-root@ssh8.vast.ai}
VAST_PORT=${VAST_PORT:-22258}
ANVIL_USER=${ANVIL_USER:-x-fcai3}
ANVIL=${ANVIL:-anvil.rcac.purdue.edu}
STAGE=${STAGE:-$(mktemp -d)}

echo "== staging dir: $STAGE"

echo "== [1/4] pulling run tree from Vast"
ssh -p "$VAST_PORT" "$VAST" 'tar czf - -C /workspace/sts runs' > "$STAGE/runs.tgz"
echo "   $(du -h "$STAGE/runs.tgz" | cut -f1)"

echo "== [2/4] pulling pseudopotentials from Vast"
# The FULL SSSP tree, not the five-file live dir. The 2026-08-20 Ti incident was
# caused precisely by a thin pseudo dir; ship everything and let the preflight's
# missing-pseudo refusal be the guard rather than a manual copy nobody repeats.
ssh -p "$VAST_PORT" "$VAST" 'tar czf - -C /root/sssp_full/usr/share/espresso pseudo' > "$STAGE/pseudo.tgz"
echo "   $(du -h "$STAGE/pseudo.tgz" | cut -f1)"

echo "== [3/4] pushing to Anvil \$PROJECT"
ssh "$ANVIL_USER@$ANVIL" 'mkdir -p $PROJECT/sts $PROJECT/logs'
cat "$STAGE/runs.tgz"   | ssh "$ANVIL_USER@$ANVIL" 'tar xzf - -C $PROJECT/sts'
cat "$STAGE/pseudo.tgz" | ssh "$ANVIL_USER@$ANVIL" 'tar xzf - -C $PROJECT'

echo "== [4/4] pushing the driver + anvil scripts"
scp -q ../src/dft/queue_r1.sh "$ANVIL_USER@$ANVIL:"'$PROJECT/queue_r1.sh'
scp -q ./*.slurm ./*.sh ./qe75-explicit.txt "$ANVIL_USER@$ANVIL:"'$PROJECT/anvil/' 2>/dev/null \
  || { ssh "$ANVIL_USER@$ANVIL" 'mkdir -p $PROJECT/anvil'; \
       scp -q ./*.slurm ./*.sh ./qe75-explicit.txt "$ANVIL_USER@$ANVIL:"'$PROJECT/anvil/'; }

echo "== verifying on Anvil"
ssh "$ANVIL_USER@$ANVIL" 'echo "  PROJECT=$PROJECT"; echo "  decks: $(find $PROJECT/sts/runs -name "*.in" | wc -l)"; echo "  UPFs:  $(ls $PROJECT/pseudo | wc -l)"; echo "  driver: $(test -f $PROJECT/queue_r1.sh && echo present || echo MISSING)"'
echo "STAGE_OK $(date -u)"
