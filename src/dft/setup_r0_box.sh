#!/usr/bin/env bash
# R0 re-parity box setup (docs/29). Runs on a fresh Vast.ai
# pytorch/pytorch:2.7.1-cuda12.8-cudnn9-runtime box. Expects /workspace/r0_payload.tgz
# (src/hea_oer + src/dft/uma_oc22_parity.py + runs/*/*.in + manifests) already scp'd in.
set -e
LOG=/workspace/setup_r0.log
echo "SETUP_START $(date -u)" | tee -a "$LOG"
cd /workspace
# fairchem-core + ase + scipy for the runner. pandas is pulled in transitively by
# hea_oer/__init__.py -> pipeline.py (round-1 screener) the moment the runner does
# `from hea_oer.referencing import delta_G`; a static audit of src/hea_oer/*.py shows
# numpy+pandas+ase is the COMPLETE top-level third-party set (pymatgen is imported
# lazily inside surfaces_rutile functions we never call — the .in files are pre-built).
pip install --no-cache-dir fairchem-core ase scipy pandas 2>&1 | tail -3 | tee -a "$LOG"
mkdir -p /workspace/sts
tar -xzf /workspace/r0_payload.tgz -C /workspace/sts
echo "payload dirs: $(ls /workspace/sts/runs | tr '\n' ' ')" | tee -a "$LOG"
python - <<'EOF' 2>&1 | tee -a "$LOG"
import torch, fairchem.core
print("torch", torch.__version__, "| cuda_ok", torch.cuda.is_available(),
      "|", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "-")
print("fairchem-core", fairchem.core.__version__)
EOF
# fail fast if the runner's exact import chain can't resolve (post-extract)
PYTHONPATH=/workspace/sts/src python -c "from hea_oer.referencing import delta_G; from hea_oer.descriptors import oer_overpotential; print('hea_oer import chain OK')" 2>&1 | tee -a "$LOG"
echo "SETUP_DONE $(date -u)" | tee -a "$LOG"
