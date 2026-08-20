#!/usr/bin/env bash
# Anvil bring-up step 1: rebuild the EXACT numerical stack the campaign has been
# running on Vast box 47662258, from an explicit conda-forge lock.
#
# WHY NOT the Anvil `quantum-espresso` module: Anvil provides QE 6.7 / 7.2 / 7.3.
# This campaign has run every banked number on QE 7.5 (qe-7.5-h19104ac_2) against
# openmpi 5.0.10 / openblas 0.3.34-pthreads / scalapack 2.2.0 / elpa 2025.06.001.
# Swapping the QE minor version mid-campaign would inject exactly the class of
# silent, unmeasured numerical change this project exists to indict. So we pin.
#
# $HOME on Anvil is 25 GB and is NOT the place for a conda prefix -- use $PROJECT.
set -euo pipefail

PREFIX=${PREFIX:-$PROJECT/qe/env}
MAMBA_ROOT=${MAMBA_ROOT:-$PROJECT/.micromamba}
LOCK=${LOCK:-$(dirname "$0")/qe75-explicit.txt}

[ -n "${PROJECT:-}" ] || { echo "FATAL: \$PROJECT unset -- are you on an Anvil node?" >&2; exit 1; }
[ -r "$LOCK" ] || { echo "FATAL: lock file not readable: $LOCK" >&2; exit 1; }

echo "== prefix:  $PREFIX"
echo "== lock:    $LOCK ($(grep -c conda-forge "$LOCK") packages)"

# --- micromamba (single static binary, no root, no base env) -------------------
mkdir -p "$MAMBA_ROOT/bin"
if [ ! -x "$MAMBA_ROOT/bin/micromamba" ]; then
  echo "== fetching micromamba"
  curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest \
    | tar -xj -C "$MAMBA_ROOT" bin/micromamba
fi
export MAMBA_ROOT_PREFIX="$MAMBA_ROOT"
MM="$MAMBA_ROOT/bin/micromamba"

# --- the env ------------------------------------------------------------------
if [ -x "$PREFIX/bin/pw.x" ]; then
  echo "== env already present, skipping create"
else
  echo "== creating env from explicit lock (byte-identical builds)"
  "$MM" create -y -p "$PREFIX" --file "$LOCK"
fi

# --- verify -------------------------------------------------------------------
echo "== verifying"
"$PREFIX/bin/pw.x" -h 2>&1 | grep -m1 "PWSCF" || true
ver=$("$PREFIX/bin/pw.x" -h 2>&1 | grep -om1 "v\.[0-9.]*" | head -1)
echo "== pw.x reports: ${ver:-UNKNOWN}"
if [ "$ver" != "v.7.5" ]; then
  echo "REFUSE: expected v.7.5, got '${ver:-UNKNOWN}' -- do not run science on this env" >&2
  exit 2
fi
echo "BOOTSTRAP_OK $(date -u)"
