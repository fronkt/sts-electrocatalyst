#!/usr/bin/env bash
# Idempotent QE 7.5 box setup. Recipe per feedback_vast_workflow #6:
# conda-forge via micromamba (apt QE 6.7 has the glibc buffer-overflow bug),
# SSSP pseudos shipped from the production box, PATH/LD_LIBRARY_PATH set by
# queue_r1.sh itself at runtime.
set -e
export DEBIAN_FRONTEND=noninteractive
command -v curl >/dev/null 2>&1 && command -v bzip2 >/dev/null 2>&1 && command -v tmux >/dev/null 2>&1 || {
  apt-get update -qq >/dev/null && apt-get install -y -qq curl bzip2 ca-certificates tmux >/dev/null
}
mkdir -p /workspace /usr/share/espresso /workspace/sts/runs
cd /workspace
if [ ! -x /workspace/qe/env/bin/pw.x ]; then
  [ -x /workspace/bin/micromamba ] || curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xj bin/micromamba
  /workspace/bin/micromamba create -y -q -p /workspace/qe/env -c conda-forge qe=7.5 >/dev/null
fi
[ -d /usr/share/espresso/pseudo ] || tar xzf /workspace/pseudo.tgz -C /usr/share/espresso
tar xzf /workspace/runs_week1.tgz -C /workspace/sts
ls /workspace/qe/env/bin/pw.x /workspace/qe/env/bin/mpirun >/dev/null
echo "SETUP_DONE nproc=$(nproc) quota=$(cat /sys/fs/cgroup/cpu.max 2>/dev/null)"
