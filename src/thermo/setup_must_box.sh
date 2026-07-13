#!/usr/bin/env bash
# One-shot MuST (KKR-CPA + Kubo-Greenwood) build on a fresh Vast.ai CPU box —
# the kappa_e half of the docs/24 Spike-1 oracle. Style/idempotency mirrors
# src/dft/setup_newbox.sh. Run inside a detached tmux session (build ~15-30 min;
# SSH may drop). NOT yet validated on a live box (both DFT boxes were torn down
# 2026-07-13 before this could run) — expect to adapt the ARCH pick on first use.
#
# Usage on the box:   bash setup_must_box.sh            (auto-picks arch file)
#                     ARCH=linux-gnu-nogpu bash setup_must_box.sh
set -e
LOG=/workspace/setup_must.log
echo "MUST_SETUP_START $(date -u)" | tee -a "$LOG"

# 0. real core budget first — size MPI to cpu.max, NOT nproc (tasks/lessons.md)
echo "cpu.max=$(cat /sys/fs/cgroup/cpu.max 2>/dev/null)  nproc=$(nproc)  mem=$(free -g | awk '/Mem/{print $2}')GB  disk=$(df -h /workspace | awk 'NR==2{print $4}') free" | tee -a "$LOG"

# 1. toolchain via apt (MuST's external/ builds FFTW/LibXC/Lua/P3DFFT itself,
#    so only compilers + MPI + BLAS/LAPACK + HDF5 + XDR are needed from the OS)
if ! command -v mpif90 >/dev/null 2>&1; then
  echo "installing toolchain ..." | tee -a "$LOG"
  apt-get update -qq
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    build-essential gfortran git make cmake m4 autoconf pkg-config \
    openmpi-bin libopenmpi-dev libopenblas-dev liblapack-dev \
    libscalapack-openmpi-dev libhdf5-dev libtirpc-dev 2>&1 | tail -2 | tee -a "$LOG"
fi
echo "gfortran=$(gfortran --version | head -1)  mpi=$(mpirun --version | head -1)" | tee -a "$LOG"

# 2. clone + build (full install: MST/mst2 + KUBO + tools -> MuST/bin)
cd /workspace
if [ ! -d /workspace/MuST ]; then
  git clone --depth 1 https://github.com/mstsuite/MuST.git
  # MST/Makefile builds git_version.h from `git tag` via a bashism that fails
  # under dash AND a shallow clone has no tags -> empty version -> truncated
  # Fortran WRITE in keep.F90. Any tag makes the fallback pipeline emit a
  # valid quoted string.
  git -C /workspace/MuST tag v0-shallow 2>/dev/null || true
fi
cd /workspace/MuST
# real -x check must target the actual binary, not the ./bin symlink (make
# install creates links even after a failed make -> dangling = looks built)
if [ ! -x MST/bin/mst2 ]; then
  # Use the repo's proven arch file (GNU+OpenMPI+OpenBLAS/ScaLAPACK, bundled
  # LibXC/FFTW, NotUse_P3DFFT): scp src/thermo/arch-vast-gnu-openblas to
  # /workspace/ alongside this script. The stock arch files all assume
  # supercomputer library paths (the auto-picked linux-gnu-aocl cost a build).
  if [ -f /workspace/arch-vast-gnu-openblas ]; then
    sed 's/\r$//' /workspace/arch-vast-gnu-openblas > architecture/vast-gnu-openblas
    ARCH=${ARCH:-vast-gnu-openblas}
  fi
  if [ -z "${ARCH:-}" ]; then
    echo "NO ARCH FILE — scp arch-vast-gnu-openblas to /workspace or set ARCH=; options:" | tee -a "$LOG"
    ls architecture | tee -a "$LOG"
    exit 1
  fi
  echo "building with architecture file: $ARCH" | tee -a "$LOG"
  # full log to file; NEVER pipe make through tail — it masks the exit code
  make "$ARCH" > /workspace/must_build.log 2>&1
  echo "MAKE_EXIT=$?" | tee -a "$LOG"
  make install >> /workspace/must_build.log 2>&1
  echo "INSTALL_EXIT=$?" | tee -a "$LOG"
  if [ ! -x MST/bin/mst2 ] || [ ! -x KUBO/bin/kubo ]; then
    echo "BUILD FAILED — real binaries missing; see /workspace/must_build.log" | tee -a "$LOG"
    exit 1
  fi
fi

# 3. report what we got (expect mst2 = KKR/KKR-CPA driver, kubo = conductivity)
echo "binaries: $(ls bin 2>/dev/null | tr '\n' ' ')" | tee -a "$LOG"
echo "tutorials: $(ls Tutorials 2>/dev/null | tr '\n' ' ')" | tee -a "$LOG"
echo "MUST_SETUP_DONE $(date -u)" | tee -a "$LOG"
echo "NEXT: run the validation ladder in src/thermo/README.md (fcc Cu SCF -> Cu-Fe CPA -> kubo rho_res vs Linde)" | tee -a "$LOG"
