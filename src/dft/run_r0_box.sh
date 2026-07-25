#!/usr/bin/env bash
# Launch the R0 parity run on the box (docs/29). Usage: HF_TOKEN=hf_xxx bash run_r0_box.sh
# HF_TOKEN needs READ scope + accepted facebook/UMA license (gated checkpoint).
set -e
[ -n "$HF_TOKEN" ] || { echo "FATAL: HF_TOKEN not set"; exit 1; }
export HF_TOKEN
cd /workspace/sts
echo "RUN_START $(date -u)"
PYTHONPATH=src python src/dft/uma_oc22_parity.py runs --tasks oc22,oc20,oc25 2>&1 | tee /workspace/r0_run.log
echo "RUN_DONE $(date -u)"
# tag-agnostic globs (runner derives the tag from the checkpoint name)
tar -czf /workspace/r0_results.tgz \
  runs/*/uma_eta_*.json runs/*/relaxed_*.extxyz runs/uma_*_summary.json \
  /workspace/r0_run.log 2>/dev/null || tar -czf /workspace/r0_results.tgz runs/uma_*_summary.json
echo "RESULTS: /workspace/r0_results.tgz"
