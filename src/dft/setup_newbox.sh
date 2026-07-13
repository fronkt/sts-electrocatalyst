#!/usr/bin/env bash
# One-shot QE 7.5 setup on a fresh CPU box for the STS2027 DFT endmember queue.
# Run in a detached tmux session (the conda install is long; SSH may drop).
# Expects /workspace/{pseudos.tgz,dft_inputs.tgz,queue_dft.sh} already scp'd in.
set -e
LOG=/workspace/setup.log
echo "SETUP_START $(date -u)" | tee -a "$LOG"

cd /workspace
# 1. micromamba + Quantum ESPRESSO 7.5 (conda-forge — apt QE 6.7 has the glibc bug)
if [ ! -x /workspace/qe/env/bin/pw.x ]; then
  echo "installing micromamba + qe ..." | tee -a "$LOG"
  curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xj bin/micromamba
  ./bin/micromamba create -y -p /workspace/qe/env -c conda-forge qe 2>&1 | tail -5 | tee -a "$LOG"
fi

# 2. pseudopotentials -> the path the .in files hardcode
mkdir -p /usr/share/espresso/pseudo
tar -xzf /workspace/pseudos.tgz -C /usr/share/espresso/pseudo
echo "pseudos: $(ls /usr/share/espresso/pseudo | wc -l) files" | tee -a "$LOG"

# 3. inputs (extract to runs/<M>_slab/*.in)
mkdir -p /workspace/STS2027
tar -xzf /workspace/dft_inputs.tgz -C /workspace/STS2027
echo "input dirs: $(ls /workspace/STS2027/runs | tr '\n' ' ')" | tee -a "$LOG"

# 4. report the real core budget (size ranks to cpu.max, NOT nproc) + sanity
echo "cpu.max=$(cat /sys/fs/cgroup/cpu.max 2>/dev/null)  nproc=$(nproc)  mem=$(free -g | awk '/Mem/{print $2}')GB" | tee -a "$LOG"
echo "pw.x=$(/workspace/qe/env/bin/pw.x --version 2>/dev/null | grep -i version | head -1 || echo MISSING)" | tee -a "$LOG"
echo "SETUP_DONE $(date -u)" | tee -a "$LOG"
