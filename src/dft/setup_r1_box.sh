#!/usr/bin/env bash
# One-shot Quantum ESPRESSO 7.5 setup for the R1 campaign (Ru/Ir anchors + Ni rescue).
#
# Differences from setup_newbox.sh: pseudopotentials come from apt
# `quantum-espresso-data-sssp` instead of a scp'd tarball (it ships all four UPFs we
# need, including Ru_ONCV_PBE-1.0.oncvpsp.upf and Ir_pbe_v1.2.uspp.F.UPF, at exactly
# the /usr/share/espresso/pseudo path the inputs hardcode), and the script HARD-FAILS
# if any required UPF is missing rather than discovering it mid-queue.
#
# QE is pinned to 7.5: the gas references (H2/H2O) are being reused verbatim from the
# 2026-06 campaign, so mixing code versions would silently break the CHE chain.
#
# Usage:  bash setup_r1_box.sh          (expects /workspace/r1_inputs.tgz already scp'd)
set -u
LOG=/workspace/setup.log
mkdir -p /workspace
echo "SETUP_START $(date -u)" | tee -a "$LOG"

# 0. The real core budget. docs/23 s8: nproc and cpuset LIE on a rented container;
#    the binding limit is the cgroup-v2 quota. Sizing MPI to nproc cost 12x once.
CPUMAX=$(cat /sys/fs/cgroup/cpu.max 2>/dev/null || echo "unknown")
echo "cpu.max=$CPUMAX  nproc=$(nproc)  mem=$(free -g | awk '/Mem/{print $2}')GB  disk=$(df -BG /workspace 2>/dev/null | awk 'NR==2{print $4}')" | tee -a "$LOG"

# 1. pseudopotentials (small, fast, and the thing most likely to be missing).
#    `quantum-espresso-data-sssp` is its OWN source package and only exists from
#    Ubuntu 24.04 / Debian trixie onwards -- `apt install` fails silently on a 22.04
#    box. It is arch:all (pure data), so pulling the .deb straight from the pool and
#    unpacking it is release-independent and safe. Verified: the O/H/Cr/Ni UPFs in
#    1.3.0-3build1 are byte-identical (MD5) to the ones the 2026-06 campaign used, so
#    new runs stay on exactly the archive's footing.
export DEBIAN_FRONTEND=noninteractive
if [ ! -f /usr/share/espresso/pseudo/Ru_ONCV_PBE-1.0.oncvpsp.upf ]; then
  echo "installing SSSP pseudopotentials ..." | tee -a "$LOG"
  apt-get update -qq 2>&1 | tail -2 | tee -a "$LOG"
  if ! apt-get install -y -qq quantum-espresso-data-sssp 2>/dev/null; then
    echo "  apt has no quantum-espresso-data-sssp (pre-24.04); fetching the .deb" | tee -a "$LOG"
    B=http://archive.ubuntu.com/ubuntu/pool/universe/q/quantum-espresso-data-sssp/
    F=$(curl -fsSL "$B" | grep -o 'quantum-espresso-data-sssp_[^"]*_all\.deb' | sort -u | tail -1)
    echo "  pool file: ${F:-NONE}" | tee -a "$LOG"
    [ -n "$F" ] || { echo "FATAL: cannot locate the SSSP .deb" | tee -a "$LOG"; exit 1; }
    curl -fsSL -o /tmp/sssp.deb "$B$F" || { echo "FATAL: SSSP download failed" | tee -a "$LOG"; exit 1; }
    mkdir -p /tmp/sssp && dpkg -x /tmp/sssp.deb /tmp/sssp
    mkdir -p /usr/share/espresso/pseudo
    cp -n /tmp/sssp/usr/share/espresso/pseudo/* /usr/share/espresso/pseudo/
  fi
  echo "  pseudo dir now holds $(ls /usr/share/espresso/pseudo | wc -l) files" | tee -a "$LOG"
fi
MISSING=0
for p in Ru_ONCV_PBE-1.0.oncvpsp.upf Ir_pbe_v1.2.uspp.F.UPF O.pbe-n-kjpaw_psl.0.1.UPF \
         H.pbe-rrkjus_psl.1.0.0.UPF ni_pbe_v1.4.uspp.F.UPF; do
  if [ -f "/usr/share/espresso/pseudo/$p" ]; then
    echo "  OK   $p" | tee -a "$LOG"
  else
    echo "  MISS $p" | tee -a "$LOG"; MISSING=1
  fi
done
[ "$MISSING" -eq 0 ] || { echo "FATAL: pseudopotentials missing -- do not launch the queue" | tee -a "$LOG"; exit 1; }

# 2. Quantum ESPRESSO 7.5 (conda-forge; apt's QE 6.7 binary has the glibc
#    buffer-overflow bug documented in docs/23 s1 and is unusable)
cd /workspace
if [ ! -x /workspace/qe/env/bin/pw.x ]; then
  echo "installing micromamba + qe=7.5 ..." | tee -a "$LOG"
  curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xj bin/micromamba
  ./bin/micromamba create -y -p /workspace/qe/env -c conda-forge "qe=7.5" 2>&1 | tail -6 | tee -a "$LOG"
fi
export PATH=/workspace/qe/env/bin:$PATH
export LD_LIBRARY_PATH=/workspace/qe/env/lib:${LD_LIBRARY_PATH:-}
VER=$(pw.x --version 2>/dev/null | grep -io "v\.\?[0-9.]*" | head -1)
echo "pw.x version: ${VER:-MISSING}" | tee -a "$LOG"
[ -n "$VER" ] || { echo "FATAL: pw.x not runnable" | tee -a "$LOG"; exit 1; }

# 3. inputs
if [ -f /workspace/r1_inputs.tgz ]; then
  mkdir -p /workspace/sts
  tar -xzf /workspace/r1_inputs.tgz -C /workspace/sts
  echo "input dirs: $(ls /workspace/sts/runs 2>/dev/null | tr '\n' ' ')" | tee -a "$LOG"
  echo "inputs: $(find /workspace/sts/runs -name '*.in*' | wc -l) files" | tee -a "$LOG"
fi
echo "SETUP_DONE $(date -u)" | tee -a "$LOG"
