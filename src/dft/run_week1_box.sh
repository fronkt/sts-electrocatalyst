#!/usr/bin/env bash
# Week-1 chain on box 47025043, launched 2026-08-09 (user-approved).
# Stages are independent blocks: a preflight abort in one does not block the
# next. Each queue's own preflight is the safety; gate on `bfgs converged`.
cd /workspace
banner() { echo "=== STAGE $1 START $(date -u) ===" | tee -a /workspace/week1_chain.log; }
banner "1C m_hess (queue_r1, 20 1)"
bash /workspace/queue_r1.sh m_hess.txt 20 1
banner "1B m_hp_tio2 (queue_hp, 20 1)"
bash /workspace/queue_hp.sh m_hp_tio2.txt 20 1
banner "1B m_hp_costmodel_sym (queue_hp, 18 1)"
bash /workspace/queue_hp.sh m_hp_costmodel_sym.txt 18 1
# m_hp_costmodel_nosym.txt is DELIBERATELY not here: its launch is gated on
# reading the sym arm's wall clock (N13).
banner "1A manifest A (queue_r1, 4 5)"
bash /workspace/queue_r1.sh m_cellsym_a_np4.txt 4 5
banner "ALL STAGES DONE"
