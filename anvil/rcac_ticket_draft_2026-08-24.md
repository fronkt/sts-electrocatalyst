# RCAC support ticket draft — repeat OOM kills isolated to nodes a024 and a088

*(Draft for Frank to paste into the RCAC help desk — do not send as-is without
reading; assistant never submits tickets.)*

Subject: Anvil CPU nodes a024 and a088 — reproducible OOM kills of jobs that
succeed unmodified on other nodes (account che260157)

Hello RCAC,

We believe compute nodes **a024**, **a088** and **a196** have a hardware or configuration
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

- Array 20141568 on 2026-08-25 (11 tasks, submitted with --exclude=a024,a088):
  **a196 OOM-killed all three of the tasks it received, and hung a fourth.** The
  other six nodes in that array killed 0 of 8. Details below, because this one
  carries a node-side diagnosis we could not obtain for a024/a088.

The identical-input/different-node contrast rules out a workload explanation.

### a196 on 2026-08-25 — what `scontrol` shows

Tasks 3, 5 and 6 of array 20141568 were killed `OUT_OF_MEMORY` (exit 0:125) on
a196 at **MaxRSS 8.65-8.70 GB**, while the *successful* tasks of the same array
on other nodes peaked at **30.8-46.8 GB**. The killed jobs were therefore using
roughly a fifth of what a healthy run of the same code uses — they were killed
for the node's lack of free memory, not their own consumption.

At the time of writing, `scontrol show node a196` reports:

```
NodeName=a196  State=ALLOCATED+DRAIN  CPULoad=166.18
RealMemory=257400  AllocMem=242688  FreeMem=384  MemSpecLimit=12000
Reason=NHC: Terminated by signal SIGTERM. [root@2026-08-25T19:55:48]
```

A 128-core node reporting **384 MB free** and a load average of 166. Note that
Slurm was still scheduling our array onto a196 while it was in this state: task 7
was placed there, wrote its ~10 KB QE header and then produced **zero SCF
iterations in 1 h 45 min** before we cancelled it manually. Its output file is
byte-comparable in size (9,912 B) to the two OOM'd siblings on the same node
(9,905 B and 9,986 B), i.e. all four died at the same point.

The four lost tasks cost roughly **430 SU**, and the hung one would have burned a
further ~5,900 SU had it run out its 48 h walltime rather than being caught.

a024 and a088 were back in the general pool as of 2026-08-24 (a024 ALLOCATED,
a088 MIXED), so other users' jobs are presumably exposed to the same failure.

Could you check these three nodes (memory DIMMs / leftover memory pressure from
a prior tenant / cgroup memory limits)? For a196 specifically, we would also ask
whether a node in `DRAIN` after an NHC SIGTERM should still be receiving newly
scheduled array tasks, since that is what turned three lost jobs into four. Happy to provide job scripts and full
slurmd logs timestamps if useful.

Thanks,
Frank Cai (x-fcai3), allocation CHE260157

One operational note in case it is intended behavior: `sbatch` on Anvil appears
to silently ignore the `SBATCH_EXCLUDE` environment variable (job submitted with
ExcNodeList=(null)); only the `--exclude` flag works. If that is a known quirk,
a note in the Anvil docs would save users a round of failed jobs.
