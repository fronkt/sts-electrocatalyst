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

| Stage | Work | SU |
|---|---|---|
| S0 | 24 decks × ~6 h | ~2,900 |
| S3–S5 | 300–500 box-h | 6,000–10,000 |
| Parity + bring-up | | <100 |
| **Total** | | **~13,000 of 100,000** |

**~87% headroom.** Compute stopped being the binding constraint on this project.

The wall-clock win is larger than the SU win: S0 is ~6 days serial on Vast and
about a day as an array; S3's 300–500 box-hours go from ~2–3 weeks to ~2–3 days.
Against the Oct 15 freeze that is the whole difference.

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
