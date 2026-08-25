# RCAC support ticket draft — repeat OOM kills isolated to nodes a024 and a088

*(Draft for Frank to paste into the RCAC help desk — do not send as-is without
reading; assistant never submits tickets.)*

Subject: Anvil CPU nodes a024 and a088 — reproducible OOM kills of jobs that
succeed unmodified on other nodes (account che260157)

Hello RCAC,

We believe compute nodes **a024** and **a088** have a hardware or configuration
fault. Across four Slurm array submissions on 2026-08-24 (account che260157, user
x-fcai3), Quantum ESPRESSO pw.x tasks (128 MPI ranks, -N 1, ~standard memory
footprint for a 36-atom slab at 80 Ry) were OOM-killed on these two nodes and on
no others — and every killed task later completed on a different node with the
input unmodified:

- Arrays 20097663 + 20097688 (55 tasks over 22 nodes): **a024 OOM-killed 11 of
  its 12 tasks; the 21 other nodes killed 0 of 43.** The one a024 survivor was
  the smallest SCF in the set.
- Array 20101963 (resubmission with ExcNodeList=a024): all former a024 victims
  that were pure OOM cases **converged unmodified** on other nodes.
- Array 20114094 (56 tasks): **a088 OOM-killed all 5 of its tasks; 0 kills on
  every other node.**
- Array 20118525 (resubmission with --exclude=a024,a088): **all 5 former a088
  tasks converged unmodified.**

The identical-input/different-node contrast rules out a workload explanation.
Both nodes are back in the general pool today (a024 ALLOCATED, a088 MIXED as of
2026-08-24), so other users' jobs are presumably exposed to the same failure.

Could you check these two nodes (memory DIMMs / leftover memory pressure from a
prior tenant / cgroup memory limits)? Happy to provide job scripts and full
slurmd logs timestamps if useful.

Thanks,
Frank Cai (x-fcai3), allocation CHE260157

One operational note in case it is intended behavior: `sbatch` on Anvil appears
to silently ignore the `SBATCH_EXCLUDE` environment variable (job submitted with
ExcNodeList=(null)); only the `--exclude` flag works. If that is a known quirk,
a note in the Anvil docs would save users a round of failed jobs.
