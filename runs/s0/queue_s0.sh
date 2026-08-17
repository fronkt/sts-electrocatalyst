#!/usr/bin/env bash
# Throttled S0 queue: nine capability gates, 29 registered jobs (~35 box-h).
# Modeled on src/dft/queue_dft.sh; walks runs/s0/<gate>/ dirs with per-job nk
# taken from each gate's manifest.json (embedded below at assembly time).
# Launch preconditions (runs/s0/README.md): LIT-2/3 drain (TWO QUEUE_ALL_DONE
# lines) or campaign PARKED; Sn pseudo verified before the sno2 arm.
# NP must be a multiple of every nk in the list (4 and 2) -> default 20.
set -u
NP=${1:-20}
NCONC=${2:-4}
RUNS=/workspace/STS2027/runs
export PATH=/workspace/qe/env/bin:${PATH:-}
export LD_LIBRARY_PATH=/workspace/qe/env/lib:${LD_LIBRARY_PATH:-}
export OMP_NUM_THREADS=1
LOG=/workspace/queue_s0.log
echo "QUEUE_START $(date -u) NP=$NP NCONC=$NCONC" >> "$LOG"

run_one() {
  local dir=$1 job=$2 nk=$3
  local d=$RUNS/$dir
  cd "$d" || { echo "NODIR $dir" >> "$LOG"; return 2; }
  # Wave-2 decks (a_beef slab__beefhub = SELECT-WINNER) may not exist yet:
  # log and skip instead of aborting the whole queue.
  if [ ! -f "${job}.in" ]; then
    echo "SKIP_MISSING $dir/$job no-input $(date -u)" >> "$LOG"; return 0
  fi
  # Idempotent: relaunches skip anything already converged
  if grep -q "JOB DONE" "${job}.out" 2>/dev/null; then
    echo "SKIP $dir/$job already-done $(date -u)" >> "$LOG"; return 0
  fi
  rm -rf ./tmp 2>/dev/null
  local t0; t0=$(date +%s)
  # </dev/null is load-bearing: backgrounded mpirun otherwise drains the
  # here-string job list via OpenMPI stdin-forwarding -> queue exits early
  mpirun --allow-run-as-root --bind-to none -np "$NP" pw.x -nk "$nk" -in "${job}.in" > "${job}.out" 2>&1 < /dev/null
  local rc=$?
  local jd; jd=$(grep -c 'JOB DONE' "${job}.out")
  # JOB DONE alone is a false positive: pw.x prints it even when a mid-relax
  # SCF hits electron_maxstep and stops on an unconverged geometry
  local sf; sf=$(grep -c 'convergence NOT achieved' "${job}.out")
  local ff; ff=$(grep 'Total force' "${job}.out" | tail -1 | awk '{print $4}')
  # Elapsed-seconds field is a DELIVERABLE for gate (d) d_hess_timing and
  # gate (g) g_tio2_timing -- do not remove or reformat it.
  echo "DONE $dir/$job rc=$rc JOB_DONE=$jd SCF_FAIL=$sf F_LAST=${ff:-na} $(( $(date +%s)-t0 ))s $(date -u)" >> "$LOG"
  rm -rf ./tmp 2>/dev/null   # free scratch immediately -- small-disk boxes
}

# Job list: "<dir> <job> <nk>", nk from each gate's manifest.json.
# Order = the registered launch recommendation (runs/s0/README.md):
# b, e first (cheap acceptance gates that gate deck-building elsewhere);
# h early (longest pole, 8 box-h, drains in parallel); i TiO2 before g;
# i SnO2 pseudo-gated; a_beef slab__beefhub LAST (wave-2 SELECT-WINNER,
# skipped via SKIP_MISSING until the winner template is copied in).
# Gate (g) s0_OOH__2x1v_off is a RELAXATION with in-deck max_seconds=28800:
# a multi-hour wall clock is expected, not a hang -- this queue never kills
# slow jobs (no timeout logic; mpirun runs to completion or max_seconds).
JOBS=$(cat <<'EOF'
s0/b_noinv s0_OOH__2x1v_off__noinvT 4
s0/b_noinv s0_OOH__2x1v_off__noinvF 2
s0/e_proj s0_O__u715_atomic 4
s0/e_proj s0_O__u715_ortho 4
s0/h_afm_anchor ref__2x1v__afm 4
s0/h_afm_anchor s0_O__2x1v_off__afm 4
s0/h_afm_anchor s0_OH__2x1v_off__afm 4
s0/h_afm_anchor s0_OOH__2x1v_off__afm 4
s0/c_nosym_mir s0_OOH__2x1v_mir__nosym 4
s0/d_hess_timing s0_OOH__2x1v_mir__hess_a37xp 4
s0/i_cutoff_ladder tio2__ecut60 2
s0/i_cutoff_ladder tio2__ecut80 2
s0/i_cutoff_ladder tio2__ecut100 2
s0/i_cutoff_ladder tio2__ecut120 2
s0/a_beef slab__beefens 4
s0/a_beef slab__beefcalc 4
s0/a_beef slab__beefctl 4
s0/f_gate1_uladder s0_OOH__u0.0__g1 4
s0/f_gate1_uladder s0_OOH__u0.5__g1 4
s0/f_gate1_uladder s0_OOH__base__g1 4
s0/f_gate1_uladder s0_OOH__u1.35__g1 4
s0/f_gate1_uladder s0_OOH__u0.0+spin1.0__g1 4
s0/f_gate1_uladder s0_OOH__u1.35+spin1.0__g1 4
s0/g_tio2_timing s0_OOH__2x1v_off 4
s0/i_cutoff_ladder sno2__ecut60 2
s0/i_cutoff_ladder sno2__ecut80 2
s0/i_cutoff_ladder sno2__ecut100 2
s0/i_cutoff_ladder sno2__ecut120 2
s0/a_beef slab__beefhub 4
EOF
)

# Throttle to NCONC concurrent background jobs
while read -r dir j nk; do
  [ -z "$dir" ] && continue
  while [ "$(jobs -rp | wc -l)" -ge "$NCONC" ]; do wait -n; done
  run_one "$dir" "$j" "$nk" </dev/null &
done <<< "$JOBS"
wait
echo "QUEUE_ALL_DONE $(date -u)" >> "$LOG"
