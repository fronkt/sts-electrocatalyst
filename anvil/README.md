# Anvil bring-up — ACCESS CHE260157

Purdue Anvil replaces the paid Vast.ai box for STS DFT from S3 onward.
Status as of **2026-08-20**: allocation **provisioned and Active**, account exists,
login node reachable. One human step remains before anything can run.

| Fact | Value |
|---|---|
| ACCESS project | `CHE260157` — Active, 2026-08-13 → 2027-08-12 |
| Anvil CPU | **100,000 SU**, 100% remaining |
| Anvil GPU | 150 GPU-h, 100% remaining — **no consumer; hold unspent** |
| Anvil username | `x-fcai3` |
| Login | `ssh x-fcai3@anvil.rcac.purdue.edu` (publickey only) |
| OnDemand | `ondemand.anvil.rcac.purdue.edu` (ACCESS credentials) |
| Credits still unexchanged | 89,903 |

## Step 0 — the one thing only Frank can do

Anvil has **no password SSH and no "Anvil password"**. The public key must be
installed through OnDemand, which needs ACCESS credentials.

1. Open <https://ondemand.anvil.rcac.purdue.edu> and sign in with **ACCESS**
   credentials (not a Purdue account).
2. *Clusters → Anvil Shell Access*.
3. Paste:

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBQNXF/VQZvRHzBPmBe/Lib/FVLbbui3jZf3KsPZ3+R1 frankyc11223@gmail.com' >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

4. Verify from this machine — this must print a hostname, not a permission error:

```bash
ssh x-fcai3@anvil.rcac.purdue.edu hostname
```

Everything below is scripted and needs no further human input.

## Steps 1–4

```bash
# 1. rebuild the exact numerical stack (run ON Anvil)
bash $PROJECT/anvil/10_bootstrap.sh

# 2. stage decks + pseudopotentials + driver (run LOCALLY)
bash anvil/20_stage.sh

# 3. THE GATE — re-run a banked deck, compare to Vast (run ON Anvil)
sbatch -A <acct> anvil/30_parity.slurm
#    on PARITY_PASS:  touch $PROJECT/parity/PARITY_PASS

# 4. submit a registered manifest as a Slurm array (run ON Anvil)
bash $PROJECT/anvil/41_submit_wave.sh $PROJECT/sts/runs/s0/m_s0_np20.txt 8
```

## Design decisions, and why

**QE 7.5 is pinned; the Anvil module is not used.** Anvil provides QE 6.7 / 7.2 /
7.3. Every number banked in this campaign came from `qe-7.5-h19104ac_2` against
openmpi 5.0.10 / openblas 0.3.34-pthreads / scalapack 2.2.0 / elpa 2025.06.001.
`qe75-explicit.txt` pins all 51 conda-forge builds by URL, so Anvil rebuilds the
identical stack. Taking the module instead would inject an unmeasured
minor-version change into the middle of a campaign whose entire thesis is that
unmeasured numerical changes are how DFT screens lie.

**Concurrency comes from Slurm arrays, not from raising NCONC.** `queue_r1.sh`
refuses any invocation whose NP/NCONC disagrees with the manifest's
`# NP=<n> NCONC=<n>` directive (finding N6), and every registered manifest
declares `NCONC=1`. An array runs each deck at exactly its declared shape, so
the guard stays armed. It is also cheaper: one 120-core allocation bills 120 SU/h
across its whole walltime including the tail where five of six slots idle, while
six 20-core tasks bill only while each runs. And a crashed deck kills one task,
not the wave.

**NP stays at 20.** Changing rank count changes reduction order and therefore the
last digits. NP=20 is what every banked number used, and the decks' `max_seconds`
values were sized at it.

**The driver is patched, not rewritten.** Three changes, all defaulting to the
Vast values so an un-set environment behaves bit-identically:
`QE_PREFIX`, `LOG`, and a `PSEUDO_DIR` rewrite of the derived `.run.in` (the
decks name an absolute `pseudo_dir`, there is no root on a cluster, and an
explicit `pseudo_dir` overrides `$ESPRESSO_PSEUDO`). The registered `.in` files
are never touched. A fourth change adds a **missing-pseudopotential refusal** to
the preflight — see below.

## SU budget

`shared` bills `max(cores, ceil(mem_GB/2))` SU per hour. At 20 cores with ~0.5 GB
per rank measured, cores dominate: **20 SU/h flat**.

**Superseded 2026-08-22 by measurement — see docs/48.** The table below was built on a
4 h/relax estimate that S0 gate (g) had already falsified (8 h at 20 ranks and not
converged). The measured figures are:

| Stage | Work | SU |
|---|---|---|
| S0 remainder | 19 Cr Hessian SCFs, ~2.7 h each at 20 ranks | ~1,030 |
| one 2×1v relax | 25–35 ionic steps | **~200–270** |
| S3–S5 | deck count is A8's to fix; the allocation buys ~370 relaxes | ≤ 99,707 |
| Parity + sizing + bring-up | actually spent | **293** |

**~99.7% of the allocation is still unspent.** Compute stopped being the binding
constraint on this project; the deck count and the Oct 15 freeze are what bind now.

The wall-clock win is larger than the SU win, and larger than first assumed. Per ionic
step the SU cost is flat from 40 to 128 ranks (6.6–7.5 SU) while wall-clock falls 3×, so
a relax that takes ~12 h at today's 20-rank shape takes **~2 h on a whole node for about
the same spend**. Zen 3 alone is 1.52× Zen 2 at identical shape, and `--bind-to core`
is a further 18% for free. Against the Oct 15 freeze that is the whole difference.

## Governance

Migration off Vast is an **S3+ decision that must be registered in A8** (owed
Aug 24). S0 stays on Vast as registered. Nothing here changes that — this tree
is infrastructure, staged and gated so it is ready the moment A8 lands.

The parity threshold in `30_parity.slurm` (`1e-5` Ry) is a **proposal**; per the
A7 authorship rule the entrant sets thresholds. It is offered because it is ~30×
tighter than GATE-1's own 5 meV science tolerance.

These scripts are AI-drafted infrastructure and must be disclosed as such.

## Incident folded in: the missing Ti pseudopotential (2026-08-20)

While surveying the box, the live `pseudo_dir` was found to hold five UPFs
(H, Ir, O, Ru, Cr) while five queued S0 decks named `ti_pbe_v1.4.uspp.F.UPF`:
`i_cutoff_ladder/tio2__ecut{60,80,100,120}` and `g_tio2_timing/s0_OOH__2x1v_off`.
The file existed in `/root/sssp_full` and had simply never been copied. Each deck
would have taken a queue slot and died at `ATOMIC_SPECIES`, two to four days into
the wave. Nothing upstream looked: the directory existed, the decks existed, the
decks parsed clean.

Copied and md5-verified in place (`88a00a67…`), and the preflight now refuses on
a missing pseudopotential. Replaying the pre-fix pseudo dir against
`m_s0_np20.txt` reproduces exactly those five refusals and aborts the wave.

Still open: SSSP ships `Sn_pbe_v1.uspp.F.UPF` (capital S) while the deferred
SnO2 decks name `sn_pbe_v1.uspp.F.UPF` (lowercase). Left alone — un-deferring
SnO2 is a registered decision, not a staging step — but it will bite on a
case-sensitive filesystem the moment those decks go live.


## First-run log (2026-08-22) -- what the runbook got wrong

Recorded because a runbook that hides its own misses is worth less than one that
does not.

**1. The OnDemand shell URL was wrong.** Step 0 said
`ondemand.anvil.rcac.purdue.edu/pun/sys/shell/ssh/anvil`. That path resolves but the
terminal then dies with *"Failed to establish a websocket connection."* The cluster is
registered under its FQDN; the working URL is
`/pun/sys/shell/ssh/anvil.rcac.purdue.edu`. Do not hand-write it -- open the dashboard
and use **Clusters -> Anvil Shell Access**, which carries the correct href.

**2. The ACCESS-profile SSH key is not the Anvil key.** Adding a public key to the
ACCESS profile does nothing for Anvil. The only path is `~/.ssh/authorized_keys`
created from the OnDemand shell (Step 0). Verified working: `x-fcai3@login03`,
`$PROJECT=/anvil/projects/x-che260157`, `$SCRATCH=/anvil/scratch/x-fcai3`.

**3. `10_bootstrap.sh` verified the env with `pw.x -h`, which is not a flag.** pw.x
starts anyway, reads stdin, hits EOF and exits non-zero; under `set -euo pipefail`
that aborted the script *after* the env had built correctly, so it never printed
`BOOTSTRAP_OK`. Fixed to feed empty stdin and swallow the status. The env itself was
always fine: pw.x **v.7.5**, OpenBLAS 0.3.34, ELPA 19.4.1, Open MPI 5.0.10, 1.6 GB at
`$PROJECT/qe/env`.

**4. `20_stage.sh` is now dead as written.** It pulls `runs/` and the pseudopotential
tree *from Vast box 47662258* -- which was destroyed after S0 drained (zero instances,
confirmed 2026-08-22). Staging is now local -> Anvil:

    tar -czf /tmp/sts_runs.tgz runs src/dft/queue_r1.sh
    scp /tmp/sts_runs.tgz x-fcai3@anvil.rcac.purdue.edu:$PROJECT/
    ssh ... 'tar -xzf $PROJECT/sts_runs.tgz -C $PROJECT/sts'

Verify by md5 on both ends, and count (`342 .out`, `524 .in`, 345 MB) -- a live
`tar | ssh` pipe silently truncated at 56 MB on the first attempt and reported success.

**5. Line endings.** This checkout has `core.autocrlf=true`, so 33 `.in` files sit in
the worktree as CRLF even though `.gitattributes` says `eol=lf` and the index holds LF
(`git ls-files --eol` shows `i/lf w/crlf`). The driver refuses CRLF inputs by design.
After extracting on Anvil, run:

    find runs \( -name '*.in' -o -name '*.in.*' -o -name 'm_*.txt' \) -print0 | xargs -0 sed -i 's/$//'

This restores the exact bytes the box ran; it is not a content change.

**6. Pseudopotentials were recovered, not re-approximated.** They lived only on the
destroyed box. Refetched on Anvil from the same source the box used --
`quantum-espresso-data-sssp` **1.3.0-3build1** from the Ubuntu universe pool (a zstd
`.deb`; `tar --zstd` is unavailable on Anvil, use `ar x` + `unzstd`). 11 of the 12
required UPFs came straight out of it, and the check that matters:

    ti_pbe_v1.4.uspp.F.UPF   md5 88a00a6731bd790ddea75d31a80cb452

is **byte-identical** to the file hashed on the Vast box on 2026-08-20. Staged at
`$PROJECT/pseudo` (12 files).

**7. The Sn filename mismatch is now staged but still unfixed.** SSSP ships
`Sn_pbe_v1.uspp.F.UPF` (capital S, md5 `4cf58ce39ec5d5d420df3dd08604eb00`); the four
`runs/s0/i_cutoff_ladder/sno2__ecut*.in` decks name `sn_pbe_v1.uspp.F.UPF` (lowercase).
Those decks have **no `.out`** -- they never ran, so no banked number depends on the
resolution. The capital-S file is staged; the decks still need editing (or a lowercase
link) before SnO2 un-defers. The driver's missing-pseudo preflight will refuse them
until then, which is the intended behaviour.
