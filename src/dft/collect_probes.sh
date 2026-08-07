#!/usr/bin/env bash
# Pull probe outputs off the rented box and score them (docs/41).
#
# The probes are fixed-geometry single points (P7/P9/P11) plus two off-plane *OOH
# relaxations (P10). They run detached under nohup, so this script is safe to run
# repeatedly while they are still going -- probe_eta.py reports what is finished and
# names what is not, and refuses to score a batch whose `base` control has drifted.
#
#   HOST=166.113.52.39 PORT=43442 bash src/dft/collect_probes.sh status
#   HOST=166.113.52.39 PORT=43442 bash src/dft/collect_probes.sh pull
#   bash src/dft/collect_probes.sh score
#
# `status` needs no local state; `score` works entirely offline on what `pull` fetched.
set -u
CMD=${1:-status}
HOST=${HOST:-166.113.52.39}
PORT=${PORT:-43442}
KEY=${KEY:-$HOME/.ssh/id_ed25519}
REMOTE=${REMOTE:-/workspace/sts/runs/probe}
SSHOPT="-o StrictHostKeyChecking=no -o ConnectTimeout=25 -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -i $KEY"

case "$CMD" in
status)
  ssh $SSHOPT -p "$PORT" "root@$HOST" '
    echo "ranks: $(pgrep -c pw.x)   load:$(uptime | sed "s/.*load average://")"
    # `grep -c` already prints 0 on no-match AND exits 1, so `|| echo 0` appends a
    # SECOND zero -- the same trap queue_r1.sh documents. Use `|| true`.
    echo "SCF finished: $(grep -ac "^DONE" /workspace/queue_r1.log 2>/dev/null || true)"
    for d in '"$REMOTE"'/*/; do
      # exclude the .run.in scratch copies queue_r1.sh writes per running job
      n=$(ls "$d"*.in 2>/dev/null | grep -vc "\.run\.in$" || true)
      k=$(grep -l "JOB DONE" "$d"*.out 2>/dev/null | wc -l)
      f=$(grep -l "convergence NOT achieved" "$d"*.out 2>/dev/null | wc -l)
      printf "  %-14s %2d/%2d done  %d scf-fail\n" "$(basename $d)" "$k" "$n" "$f"
    done
    echo "--- P10 orient trajectories (relaxations, still running) ---"
    for f in '"$REMOTE"'/*orient/*yaw90.out; do
      [ -f "$f" ] || continue
      printf "  %-10s %3d ionic steps  last E = %s Ry  JOB_DONE=%s\n" \
        "$(basename $(dirname $f))" "$(grep -c "^!" $f)" \
        "$(grep "^!" $f | tail -1 | awk "{print \$5}")" "$(grep -c "JOB DONE" $f)"
    done'
  ;;
pull)
  mkdir -p runs/probe
  # -q so a long transfer does not spam; only .out/.json come back, never the huge
  # scratch dirs (tmp_*) that pw.x leaves behind.
  scp $SSHOPT -P "$PORT" -q -r "root@$HOST:$REMOTE/*" runs/probe/ 2>/dev/null || true
  ssh $SSHOPT -p "$PORT" "root@$HOST" 'cat /workspace/queue_r1.log 2>/dev/null' > runs/probe/queue_scf.log || true
  ssh $SSHOPT -p "$PORT" "root@$HOST" 'cat /workspace/queue_orient.log 2>/dev/null' > runs/probe/queue_orient.log || true
  echo "pulled $(find runs/probe -name '*.out' | wc -l) outputs -> runs/probe/"
  ;;
score)
  for d in runs/probe/*/; do
    b=$(basename "$d")
    case "$b" in *orient) continue;; esac
    [ -f "$d/probe_manifest.json" ] || continue
    echo "=============================== $b"
    PYTHONPATH=src python src/dft/probe_eta.py "$d" 2>&1 | sed 's/^/  /'
  done
  # P10 is a pair of relaxations, not a variant batch -- score it directly against the
  # on-record energy recorded in its manifest at build time.
  for d in runs/probe/*orient/; do
    [ -f "$d/probe_manifest.json" ] || continue
    echo "=============================== $(basename $d)  (P10)"
    PYTHONPATH=src python - "$d" <<'PY'
import json, os, re, sys
RY = 13.605693122
d = sys.argv[1]
man = json.load(open(os.path.join(d, "probe_manifest.json")))
ref = man.get("on_record_energy_ev")
print(f"  on-record relaxed E = {ref:.4f} eV")
for j in man["jobs"]:
    p = os.path.join(d, j["file"][:-3] + ".out")
    if not os.path.exists(p):
        print(f"  {j['variant']:12s} not run yet"); continue
    txt = open(p, errors="replace").read()
    hits = re.findall(r"^!\s+total energy\s+=\s+([-\d.]+)\s+Ry", txt, re.M)
    done = "JOB DONE" in txt
    if not hits:
        print(f"  {j['variant']:12s} no energy yet"); continue
    e = float(hits[-1]) * RY
    tag = "CONVERGED" if done else f"RUNNING ({len(hits)} steps)"
    print(f"  {j['variant']:12s} E = {e:.4f} eV   dE vs on-record = {e-ref:+.4f} eV   [{tag}]")
    if done:
        print("     P10: drop >= 0.30 eV => symmetry-trapped basin, tier-wide *OH/*OOH suspect.")
        print("          drop <  0.10 eV => trap exonerated at DFT level.")
PY
  done
  ;;
*)
  echo "usage: collect_probes.sh {status|pull|score}"; exit 2;;
esac
