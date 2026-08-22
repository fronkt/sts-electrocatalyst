#!/usr/bin/env bash
# Submit the five S3 sizing arms, each with -n matching its own rank count.
#
# Cost: (20+40+80+80+128) ranks x ~0.72 h = ~250 SU of 100,000. The number it
# buys -- what one S3 relax actually costs on Anvil -- currently does not exist.
set -euo pipefail
ACCT=${ACCT:-che260157}
HERE=$(cd "$(dirname "$0")" && pwd)
submit() { # np nk bind
  local np=$1 nk=$2 bind=$3
  echo -n "arm np=$np nk=$nk bind=$bind -> "
  sbatch -A "$ACCT" -n "$np" \
    --export=ALL,NP="$np",NK="$nk",BIND="$bind",ARM="np${np}_nk${nk}_${bind}" \
    "$HERE/50_scaling.slurm"
}
submit 20  4  none    # production shape today -- the Anvil baseline that is missing
submit 40  8  none    # 2x pools
submit 80  16 none    # 4x pools, the deck's full 16-point mesh, one pool per k-point
submit 80  16 core    # same, but ranks pinned: isolates NUMA migration cost
submit 128 16 core    # whole node, 8 cores per pool
