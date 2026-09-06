# READOUT — The two small arms of 2026-09-05: CrO₂ linear-response U at q = 3×3×3 under both projectors (A12b rider), and the S0 gate-(e) pair re-realised on Anvil at np = 128

> **NOT YET COUNTERSIGNED.** Sequence of record: adopted in docs/43's dated addendum of 2026-09-05
> (session 2), item 5(a)–(b) (`docs/43:4380-4410`; item 5(c), the Ru control, is `:4412-4416` and is
> not part of these arms), committed `a8c3218` (2026-09-05 13:17:04 −0400) → decks built and
> md5-manifested at `ca5b33e` (13:17:04 −0400; `runs/hp_cro2_q333/MANIFEST.txt`,
> `runs/a0/m_eproj_np128.txt`) → submitted at `19732a2` (13:19:23 −0400; the two hp jobs started
> 17:19:50 UTC, `anvil/logs/hp_20419730.out:1`, `anvil/logs/hp_20419731.out:1`; the two a0 tasks
> 19:39:46 and 19:43:30 UTC, `anvil/logs/a0_20419733_1.out:1`, `anvil/logs/a0_20419733_2.out:1`) →
> scorers committed at `b502beb` (13:29:55 −0400), ten minutes after submission. By then the two
> hp-job SCFs had already terminated on Anvil — 13:20:36 and 13:20:54 local
> (`runs/hp_cro2_q333/scf__cro2_atomic_q333.out:3831`, `scf__cro2_ortho_q333.out:3832`), 9 min
> before that commit — though nothing had been pulled (every output under `runs/hp_cro2_q333/` and
> `runs/a0/eproj_np128/` carries a local file time of 2026-09-06 00:01–00:03 −0400); the scorer's
> SCF-isolation branch (`src/dft/hp_cro2_q333_readout.py:90` names those two files) was therefore
> committed after its SCF inputs existed on the remote. The first pw.x arm output terminated
> 2 h 12 min after the commit (15:42:04 local, `runs/a0/eproj_np128/s0_O__u715_atomic.out:1775`), the
> two hp.x outputs 7 h 16 min and 8 h 15 min after it (20:46:16 and 21:45:15,
> `hp__cro2_ortho_q333.out:12952`, `hp__cro2_atomic_q333.out:13066`)
> → outputs read 2026-09-06 (`docs/figs/hp_cro2_q333.json` written 00:02:04 −0400,
> `docs/figs/eproj_np128.json` 00:03:19 −0400; both scorers exit 0 when re-run print-only).
> The adoption line does not discharge the countersignature at the foot, and nothing here does.

## Verdict against what was registered

Two arms, four pre-stated readout rules, nothing elective (`docs/43:4389-4395`, `:4406-4409`).

**(a) CrO₂ q-mesh check.** The inherited bar is the deposited q-mesh row, `docs/43:276`:
"ΔU < 0.2 eV vs the next finer mesh"; A12b.R2 (`:3499-3505`) inherits it unchanged and registers
**no threshold on the size of the split** (`:3503-3505`). Read from the `Hubbard_parameters.dat`
files on disk:

- atomic: U(q333) = 6.1777 eV, U(q222) = 6.1635 eV, ΔU = +0.0142 eV → **PASS** (7.1 % of the bar).
- ortho-atomic: U(q333) = 7.3008 eV, U(q222) = 7.2677 eV, ΔU = +0.0331 eV → **PASS** (16.6 % of the bar).
- split re-formed at q333: **+1.1231 eV**, beside the q222 split of **+1.1042 eV**; change +0.0189 eV.
  A measurement, not a verdict: no bar exists on the split, and the 0.2 eV at `:276` is a per-leg bar.

The A12b.R3 named risk (nspin = 2 × ortho-atomic, `docs/43:3507-3512`) did not fire a second time:
`Convergence has not been reached` appears **0** times in either hp.x output, `CONVERGENCE HAS BEEN
REACHED` **8** times in each (once per q-point), `JOB DONE` once in each. The SCF isolation check
registered at `:4392-4395` holds on both legs: ortho q333 against the Anvil q222 leg (job 20382206)
**MATCH** on the printed energy string, magnetisation and iteration count; atomic q333 against the
Vast q222 leg **AGREES** under A8.5's 1e-5 Ry (`docs/43:1613-1614`) with ΔE = 0 at the printed
eight decimals.

**(b) Gate-(e) pair at np = 128.** The inherited bar is A8.5, `docs/43:1613-1614`: "an Anvil re-run
of a banked deck agrees when |ΔE| ≤ 1e-5 Ry".

- s0_O__u715_atomic: Anvil −1592.51110033 Ry, banked −1592.51110015 Ry, ΔE = −1.8e-7 Ry → **AGREES** (1.8 % of the bar).
- s0_O__u715_ortho: Anvil −1592.78131334 Ry, banked −1592.78131312 Ry, ΔE = −2.2e-7 Ry → **AGREES** (2.2 % of the bar).
- paired difference E(atomic) − E(ortho): Anvil **0.27021301 Ry**, beside the banked **0.27021297 Ry**;
  they differ by 4e-8 Ry. No banked value moves (`docs/43:4409`).

The registered outcome on every rule is the pass branch. What that does and does not license is
stated in its own sections below.

## The grid, with the CrO₂ q-mesh column now filled

TiO₂ values as registered at `docs/43:3523`; CrO₂ q222 values as registered at `:3524` (the 2×2
table is `:3521-3524`); CrO₂ q333 values from
`runs/hp_cro2_q333/cro2_{atomic,ortho}_q333.Hubbard_parameters.dat:7-8`.

| | **atomic** | **ortho-atomic** | **split** |
|---|---|---|---|
| **TiO₂** (nspin = 1, d⁰) | 4.2245 (q222) · 4.2251 (q333) · 4.2245 (q444) | 5.6688 · 5.6743 · 5.6741 | +1.4443 · +1.4492 · +1.4496 |
| **CrO₂** (nspin = 2, magnetic 3d) | 6.1635 (q222) · **6.1777 (q333)** | 7.2677 (q222) · **7.3008 (q333)** | +1.1042 (q222) · **+1.1231 (q333)** |

Relative to the atomic value the CrO₂ split is 18.2 % at q333 (1.1231/6.1777) against the 17.9 %
registered at q222 (`docs/43:3528`). Against the larger of the two CrO₂ leg sensitivities
(0.0331 eV) the split is 34× the q-mesh sensitivity; the TiO₂ figure registered at `:3531` was
≈ 263×. Both CrO₂ legs moved upward with the finer mesh; the ortho leg moved 2.3× as far as the
atomic leg. Those are the measured facts; no interpretation of the direction is registered or offered.

## What this costs, stated first

The hp pair missed its planning figure by **5.8×**; the a0 pair came in at 1.14× of its figure.

| job | what | Slurm Elapsed (sacct 2026-09-06, as supplied) | NCPUS | CPUTimeRAW | core-h | planned (`docs/43`) | miss |
|---|---|---|---|---|---|---|---|
| 20419730 | hp atomic q333 | 08:25:33 | 20 | 606 660 s | **168.5** | ~27 per leg (`:4397`) | 6.2× |
| 20419731 | hp ortho q333 | 07:26:37 | 20 | 535 940 s | **148.9** | ~27 per leg (`:4397`) | 5.5× |
| pair | | | | 1 142 600 s | **317.4** | ~55 (`:4397`) | **5.8×** |
| 20419733_1 | a0 atomic np = 128 | 00:02:44 | 128 | | 5.83 | | |
| 20419733_2 | a0 ortho np = 128 | 00:02:37 | 128 | | 5.58 | | |
| pair | | | | | **11.41** | ~10 SU (`:4410`) | 1.14× |

The sacct figures (606 660 s, 535 940 s, 08:25:33, 07:26:37) appear in none of `docs/*.md`,
`tasks/*.md`, `anvil/*.slurm`, the four Slurm logs or the two manifests (`grep -a`, 2026-09-06);
the file-backed equivalents are the wrappers' own wall lines and agree: pw.x 51 s + hp.x 30 276 s
= 30 327 s inside the 30 333 s Elapsed of 20419730 (`anvil/logs/hp_20419730.out:3-4`;
30 333 × 20 = 606 660); pw.x 65 s + hp.x 26 725 s = 26 790 s inside the 26 797 s Elapsed of
20419731 (`anvil/logs/hp_20419731.out:3-4`; 26 797 × 20 = 535 940). The wrappers' own integer
estimates print 168 and 148 core-h (`hp_20419730.out:5`, `hp_20419731.out:5`; formula
`anvil/52_hp.slurm:107`). For the a0 tasks the logs' `Job Wall-clock time` lines read 00:02:44 and
00:02:37 (`a0_20419733_1.out:15`, `a0_20419733_2.out:15`) at `Cores per node: 128` (`:12`), and
their `core-walltime` lines read 05:49:52 and 05:34:56 (`:14` of each) — 20 992 s and 20 096 s,
which are 164 × 128 and 157 × 128, i.e. the 5.83 and 5.58 core-h in the table are file-backed.
pw.x alone took 141 s and 137 s (`a0_20419733_{1,2}.out:2`), which is 9.88 core-h for the pair.
The 1.14× is the Elapsed beyond pw.x — 23 s and 20 s per task, inside which the inline projwfc took
11.40 s and 12.17 s (`runs/a0/eproj_np128/s0_O__u715_{atomic,ortho}.projwfc.out:22701/:22267`)
and the rest is wrapper steps; Slurm Elapsed excludes queue time. Whether the "~10 SU at the
measured a0 rate" of `docs/43:4410` was meant as a pw.x-only figure is not stated there; that it
matches the pw.x figure is an observation, not a reading of the plan. 1 SU is taken as 1 core-hour,
as `docs/43:3548` does. The realised figures are to be written beside the planning figures in the
dated line docs/43 owes (`tasks/todo.md:2092-2093`); the ~27/~55 sentence is corrected in the last
section.

**Where the 5.8× came from — MEASURED, then INFERRED.** The planning sentence at `docs/43:4396-4397`
scaled the ortho q222 cost (7.86 core-h, `:3548`) by "27 q-points against 8". hp.x prints the
irreducible count it actually iterates: **8 q-points at q = 3×3×3** (`runs/hp_cro2_q333/hp__cro2_atomic_q333.out:130`,
`hp__cro2_ortho_q333.out:130`, weights `:132-139` summing to 27/27) against **6 at q = 2×2×2**
(`runs/hp_cro2_ortho/hp__cro2_ortho_q222.out:130`, `runs/hp_tio2/hp__cro2_q222.out:131`, weights
summing to 8/8). The q-point ratio is 1.33, not 3.375. The measured drivers were elsewhere, and
the ortho leg gives the like-for-like comparison because both its meshes ran on Anvil with the same
hp.x layout (no k-point pools: `R & G space division: proc/nbgrp/npool/nimage = 20`, no
`K-points division` line, `hp__cro2_ortho_q222.out:18`, `hp__cro2_ortho_q333.out:18`):

| quantity, ortho leg | q222 | q333 | ratio | source |
|---|---|---|---|---|
| irreducible q-points | 6 | 8 | 1.33 | `..._q222.out:130`, `..._q333.out:130` |
| Σ over q of "Number of k (and k+q)" points | 1 710 | 4 602 | 2.69 | q222 `:543,1268,2181,3398,4629,5592`; q333 `:545,1212,2455,4324,7043,8294,10053,11298` |
| largest single k+q set | 400 | 1 152 | 2.88 | `..._q222.out:2181`, `..._q333.out:4324` |
| response iterations, all q (= `sth_kernel` calls) | 83 | 168 | 2.02 | `..._q222.out:6313`, `..._q333.out:12926` |
| point-iterations Σ (k+q × iters) | 24 100 | 99 024 | 4.11 | computed from the rows above |
| `cgsolve` calls | 12 960 | 50 422 | 3.89 | `..._q222.out:6316`, `..._q333.out:12929` |
| `hp_solve_lin` wall | 1 092.76 s | 15 225.75 s | 13.9 | `..._q222.out:6298`, `..._q333.out:12911` |
| `hp_solve_lin` wall per `cgsolve` call | 0.0843 s | 0.302 s | 3.58 | derived from the two rows above |
| `cgsolve` wall per call | 0.0714 s | 0.269 s | 3.76 | `..._q222.out:6316` (925.69 s / 12 960), `..._q333.out:12929` (13 558.36 s / 50 422) |
| `hp_run_nscf` wall | 269.23 s | 11 437.64 s | 42.5 | `..._q222.out:6307`, `..._q333.out:12920` |
| `davcio` CPU / wall | 12.69 / 25.18 s | 33.84 / 300.97 s | | `..._q222.out:6279`, `..._q333.out:12892` |
| hp.x total wall | 22m50.41s | 7h25m | 19.5 | `..._q222.out:6336`, `..._q333.out:12949` |

On the atomic leg the q222 reference ran on the Vast box with `K-points division: npool = 4`
(`runs/hp_tio2/hp__cro2_q222.out:18`), so its per-rank call counts (`cgsolve` 2 851 calls, `:6257`)
are not comparable; the q333 internals are: `hp_solve_lin` 28 394.14 s wall over 8 calls (`:13025`),
`hp_run_nscf` 1 841.19 s (`:13034`), `cgsolve` 58 062 calls in 22 691.50 s (`:13043`), 187 response
iterations (`sth_kernel`, `:13040`), `davcio` 42.17 s CPU against 902.77 s wall (`:13006`).

The per-q-point structure (k+q sets are identical on the two legs; the k-mesh is 6 6 8,
`runs/hp_cro2_q333/scf__cro2_atomic_q333.in:42`). "CPU per point-iteration" is the block's
last-minus-first `Total CPU time` stamp divided by (iterations − 1) and by the k+q count; "NSCF gap"
is the first stamp of a block minus the last stamp of the previous one, i.e. that q's NSCF plus its
first response iteration — defined for q2–q8 only, since q1 has no preceding block. Stamp lines: atomic
`:826,930,2063,2225,3944,4106,6677,6851,7992,8136,9759,9855,10996,11134,12757,12877`;
ortho `:826,930,2063,2195,3914,4076,6647,6761,7902,8034,9657,9771,10912,11038,12661,12763`.

| q | q (2π/alat) | k / k+q | iters atomic / ortho | CPU per point-iteration atomic / ortho (s) | NSCF gap atomic / ortho (CPU s) |
|---|---|---|---|---|---|
| 1 | (0, 0, 0) | 65 / 130 | 14 / 14 | 0.090 / 0.178 | — |
| 2 | (0, 0, 0.5054) | 208 / 416 | 28 / 23 | **0.372** / 0.054 | 225 / 291 |
| 3 | (0, ⅓, 0) | 360 / 720 | 28 / 28 | **0.428** / 0.046 | 390 / **10 148** |
| 4 | (0, ⅓, 0.5054) | 576 / 1 152 | 30 / 20 | **0.383** / 0.061 | 1 523 / 515 |
| 5 | (⅓, ⅓, 0) | 210 / 420 | 25 / 23 | 0.038 / 0.057 | 110 / 250 |
| 6 | (⅓, ⅓, 0.5054) | 336 / 672 | 17 / 20 | 0.042 / **0.251** | 188 / **6 921** |
| 7 | (⅓, −⅓, 0) | 210 / 420 | 24 / 22 | 0.039 / 0.051 | 379 / 229 |
| 8 | (⅓, −⅓, 0.5054) | 336 / 672 | 21 / 18 | 0.041 / 0.063 | 180 / 326 |

The ortho q222 reference ran its blocks q2–q6 at 0.038–0.040 s per point-iteration (stamps
`runs/hp_cro2_ortho/hp__cro2_ortho_q222.out:824,928,1807,1885,3000,3102,4217,4289,5168,5252,6131,6179`)
and the Vast q222 reference its q2–q6 at 0.041–0.043 s (stamps
`runs/hp_tio2/hp__cro2_q222.out:1808,1856,2971,3037,4152,4230,5109,5187,6066,6120`); the q = 0
block is slower per point-iteration in every run — 0.078 s (Anvil q222, `:824,928`), 0.086 s (Vast
q222, `:825,929`), 0.090 s and 0.178 s (the two q333 legs). The cumulative `HP` wall lines confirm
where the time went: atomic 31.05 s → 6m17s → 1h20m → 3h54m → 7h42m → 7h51m → 8h05m → 8h14m → 8h24m
(`:814,2053,3934,6667,7982,9749,10986,12747,13063`); ortho 33.49 s → 10m39s → 3h07m → 3h29m →
3h57m → 4h11m → 6h59m → 7h11m → 7h25m (`:814,2053,3904,6637,7892,9647,10902,12651,12949`).

**MEASURED.** (i) The irreducible q-count grew 1.33×, not 3.375×. (ii) The linear-response work
(point-iterations) grew 4.1× on the ortho leg and 5.5× on the atomic leg (114 304 against the Vast
reference's 20 800), because the k+q sets summed over the irreducible q-points are 2.7× larger
(4 602 against 1 710 — a sum that already carries the 8-against-6 q-count) and the total number of
response iterations grew 2.0× (168 against 83, ortho) and 2.6× (187 against 73, atomic), which per
q-point is a mean rise of 1.5× (21.0 against 13.8) and 1.9× (23.4 against 12.2); the inner-solver
depth did not change — the block-mean of hp.x's printed "Average number of iter. to solve lin.
system" is 15.6–17.6 on every block of all four runs (the per-iteration values run 11.2–42.0, the
first iteration of every block being 34.8–42.0). (iii) Throughput inside each q333 run was not uniform:
the atomic leg's blocks q2–q4 ran 8.7–11.2× slower per unit of work than its own blocks q5–q8 and than
the q ≠ 0 blocks of both q222 runs (0.038–0.043 s), the q = 0 blocks being excluded from that
comparison; the ortho leg's q6 block ran 4.4–4.9× slower than its neighbours q5 and q7 (0.251 s
against 0.057 and 0.051 s; 4.0–5.4× against its other q ≠ 0 blocks), and two of its seven measurable
NSCF gaps (q2–q8) took 10 148 and 6 921 CPU-s where the other five took 229–515. (iv) The ortho leg's
NSCF diagonalisations took 10 436.81 s wall (`electrons`, `hp__cro2_ortho_q333.out:12844`) against
1 084.29 s on the atomic leg (`hp__cro2_atomic_q333.out:12958`) for identical k+q sets. (v) Both
jobs were submitted under `#SBATCH -p shared` with 20 tasks (`anvil/52_hp.slurm:31,33`); the logs
record np = 20 and the nodes a104 and a119 (`anvil/logs/hp_2041973{0,1}.out:1`), and none of the
places searched prints the partition actually assigned — `anvil/logs/hp_2041973{0,1}.out`,
`anvil/logs/a0_20419733_{1,2}.out`, the four `runs/hp_cro2_q333/*_q333.out`,
`runs/hp_cro2_q333/MANIFEST.txt`, `tasks/todo.md` (`grep -a -i 'partition|wholenode|shared'` against
the job ids, 2026-09-06); hp.x was launched without `-nk` (`52_hp.slurm:100`;
only pw.x receives it, `:85`).

**INFERRED, labelled as such.** The non-uniform throughput is not in the decks or the physics (the
two legs share the k+q sets and U = 1e-8); it is consistent with contention on the shared node or
the shared filesystem (`davcio` wall 21× its CPU on the atomic q333 run and 9× on the ortho q333
run, against 2.0× on the Anvil q222 run and 1.2× on the Vast q222 run, `runs/hp_tio2/hp__cro2_q222.out:6220`)
and with the absence of k-point pools in hp.x, and the files do not separate those. As a
counterfactual only: at the ≈ 0.040 s per point-iteration that the atomic leg's blocks q5–q8 and the
q ≠ 0 blocks of both q222 runs delivered, the atomic leg's 114 304 point-iterations would be
≈ 4 570 s; the ortho leg's unstalled blocks ran at 0.046–0.063 s, at which its 99 024 point-iterations
would be ≈ 4 600–6 200 s. With NSCF at the atomic leg's realised 1 841 s that is ≈ 6 400 s and
≈ 6 400–8 100 s of wall at 20 cores, ≈ 36 and ≈ 36–45 core-h — 1.3–1.7× the ~27 planned. That figure
rests on a rate assumption and is not a planning number; what it says is that the work grew 4–5.5×
where the plan said 3.4×, and the remaining ≈ 4× of the miss sits in throughput whose cause is not
established.

## What this buys

- The two CrO₂ legs of the registered 2×2 table (`docs/43:3523-3524`) are now q-mesh-verified at the
  deposited 0.2 eV bar, closing the limit registered at `docs/43:3542-3543` and `docs/79:69-72`
  ("CrO₂ q-mesh convergence is NOT measured — only q222 exists"). The registered claim that the split
  is protected because both legs sit at the same mesh is now backed on both meshes.
- The split re-formed at q333 is +1.1231 eV, printed beside the q222 split of +1.1042 eV (change
  +0.0189 eV), as `docs/43:4390-4391` requires; the same sign and order of magnitude at both meshes
  is a description, not a pass — no bar on the split is registered (`docs/43:3503`).
- The isolation signature reproduces on a third and fourth SCF, across machines: four SCF ground
  states with `U Cr-3d 1.d-8` print the same −517.92950441 Ry, 4.00 / 4.68 μB and 19 iterations, while
  the projector is demonstrably different (Number of occupied Hubbard levels 9.6510 atomic against
  8.1923 ortho-atomic, `runs/hp_cro2_q333/scf__cro2_{atomic,ortho}_q333.out:2345`).
- The gate-(e) pair exists on Anvil at np = 128 with nk = 4, the shape of its p_proj siblings. Both
  legs AGREE under A8.5 at 1.8–2.2 % of the bar and the paired difference re-formed on Anvil,
  0.27021301 Ry, sits beside the banked 0.27021297 Ry; the cross-machine-composite description at
  `docs/43:4400-4403` stands as written (`:4409`), with those numbers now printed beside it.
- The A6.5(1) charge readout for the gate-(e) states exists for the first time (two `.lowdin.txt`;
  the banked `runs/s0/e_proj/` holds none).
- INFERRED: the planning model scaled by q-count and missed by 5.8×; Σ(k+q × iterations) tracked the
  work better on these four runs (4.1× and 5.5× against the 1.33× q-count ratio), but the
  per-point-iteration rate itself varied tenfold between blocks, so no replacement cost model is
  established here — only the realised figures are reported, as `docs/43:4398` requires.

## What this does NOT license

- **Nothing on the size of the split.** No bar is registered (`docs/43:3503-3505`); 0.0189 eV of
  movement is a number in a table, not a pass.
- **Which U is quoted.** The registered rule certifies the q222 value against the next finer mesh
  (`:276`); it prints the q333 values beside, and substitutes nothing. Which value a report quotes is
  not decided by this readout. q333 itself is not checked against q444 for CrO₂.
- **The atomic-leg ΔU carries a confound.** Its q222 reference ran on the Vast box with hp.x
  k-point pools (npool = 4); the q333 leg ran on Anvil without pools. The 0.0142 eV is measured across
  machine and hp.x layout as well as mesh. The SCF agrees to eight decimals across the same change,
  which bounds the ground-state part; no like-for-like q222 re-run on Anvil exists for the atomic
  leg to separate mesh from layout in χ. The ortho-leg ΔU has no such confound.
- **Bulk, not slab; n = 2.** Unchanged from `docs/43:3544-3546`. The A12b.R5 post-hoc reading
  (`:3551 ff.`) is not advanced by a q-mesh check.
- **Gate-(e) agreement moves no banked value** (`docs/43:4409`) and says nothing about the P-PROJ
  flagship numbers beyond this pair. The `.lowdin.txt` files are recorded as existing; nothing is
  read from them here, and no charge claim is made.
- **Cost.** The planning model is shown wrong for hp.x; this readout does not re-plan any other arm.
  The counterfactual 36–45 core-h is an inference and must not be quoted as a measured rate.
- **Countersignature.** Not discharged by anything here. The mirror audit owed before countersigning (`tasks/todo.md:2091`; the `docs/43:4148` rule) HAS been run: `src/dft/mirror_audit.py` run 2026-09-06 over the whole run tree after the pull: 32554 remote / 4606 local files; SAME 4176, ANVIL-ONLY 28135 (all out of git by design), LOCAL-ONLY 187, DIFFER 243; **ANVIL-ONLY pw.x outputs 0, DIFFERING outputs 0**, exit 0. The class lists were saved outside the tree.

## A. CrO₂ q333 pair — the record

**Decks.** As-run decks differ from their banked sources in exactly the audited lines: SCF in
`prefix` and `outdir`; hp in `prefix`, `outdir` and `nq1 = 3, nq2 = 3, nq3 = 3` (diffs reproduced
locally; recorded with md5s and diffs in `runs/hp_cro2_q333/MANIFEST.txt:12-36`, md5s at
`:13,18,25,30`; md5s re-verified: 9f8f359d…, 8c0919e7…, 34730061…, b761edb6…). hp deck parameters
otherwise unchanged: `conv_thr_chi = 1.0d-5`, `iverbosity = 2`, `find_atpert = 1`, `niter_max = 80`
(`runs/hp_cro2_q333/hp__cro2_atomic_q333.in:5-8`). One perturbed atom (only `atom # 1` appears; one
`chi.pert_1.dat` per leg). SCF: nspin = 2, ecutwfc = 80, conv_thr = 1.0d-10, K_POINTS 6 6 8
(`scf__cro2_atomic_q333.in:22,17,27,42`), `U Cr-3d 1.d-8` (`:44`), 50 irreducible k-points
(`scf__cro2_atomic_q333.out:359`).

**Per-leg U and the check** — `runs/hp_cro2_q333/cro2_atomic_q333.Hubbard_parameters.dat:7-8`
(6.1777, both Cr sites), `cro2_ortho_q333.Hubbard_parameters.dat:7-8` (7.3008),
`runs/hp_tio2/hp__cro2_q222.Hubbard_parameters.dat:7-8` (6.1635),
`runs/hp_cro2_ortho/cro2_ortho.Hubbard_parameters.dat:7-8` (7.2677); scorer output
`docs/figs/hp_cro2_q333.json:16-19,59-62,95-96`.

| leg | U(q222) | U(q333) | ΔU | ΔU / 0.2 eV | check (`:276`) |
|---|---|---|---|---|---|
| atomic | 6.1635 | 6.1777 | +0.0142 | 7.1 % | PASS |
| ortho-atomic | 7.2677 | 7.3008 | +0.0331 | 16.6 % | PASS |
| split (ortho − atomic) | +1.1042 | +1.1231 | +0.0189 | — (no bar) | measurement only |

**hp.x convergence.**

| leg | `JOB DONE` | `Convergence has not been reached` | `CONVERGENCE HAS BEEN REACHED` | q-points | iterations per q | total |
|---|---|---|---|---|---|---|
| atomic q333 | 1 (`:13069`) | 0 | 8 (`:933,2228,4109,6854,8139,9858,11137,12880`) | 8 (`:130`) | 14, 28, 28, 30, 25, 17, 24, 21 | 187 (`:13040`) |
| ortho q333 | 1 (`:12955`) | 0 | 8 (`:933,2198,4079,6764,8037,9774,11041,12766`) | 8 (`:130`) | 14, 23, 28, 20, 23, 20, 22, 18 | 168 (`:12926`) |
| atomic q222 (banked, Vast) | 1 (`:6283`) | 0 | 6 | 6 (`:131`) | 14, 9, 12, 14, 14, 10 | 73 (`:6254`) |
| ortho q222 (banked, Anvil) | 1 (`:6342`) | 0 | 6 | 6 (`:130`) | 14, 14, 18, 13, 15, 9 | 83 (`:6313`) |

Wrapper lines agree: `HP rc=0 job_done=1 not_reached=0` (`anvil/logs/hp_20419730.out:4`,
`hp_20419731.out:4`); `HP JOB COMPLETE` 01:45:17 UTC and 00:46:20 UTC on 2026-09-06 (`:8` of each).
hp.x's own termination stamps: 21:45:15 and 20:46:16 local on 5Sep2026
(`hp__cro2_atomic_q333.out:13066`, `hp__cro2_ortho_q333.out:12952`).

**The SCF isolation check — four SCFs.** QE prints no hostname. The machine is read from the
pseudopotential directory each run printed (the Anvil wrapper rewrites `pseudo_dir` to the exported
`$PSEUDO_DIR`, `anvil/52_hp.slurm:71`, `:43`; the literal `/anvil/projects/x-che260157/pseudo/` is what
each Anvil output then prints at its `:82`), the start date, the hp.x pool line
and the Slurm logs' node names for the new jobs. The `.run.in` input name shows only that a wrapper
was used — the banked Vast gate-(e) legs also read `.run.in`
(`runs/s0/e_proj/s0_O__u715_{atomic,ortho}.out:20`) — so it does not discriminate machines.

| SCF | machine, by fingerprint | started (local) | cores / npool | `!` total energy (Ry) | total / absolute mag (μB) | iters | wall |
|---|---|---|---|---|---|---|---|
| atomic q222, banked — `runs/hp_tio2/scf__cro2.out` | header names no machine; unrewritten deck (`Reading input from scf__cro2.in`, `:20`; pseudo path `/usr/share/espresso/pseudo/` at `:82` equals the deck's own `pseudo_dir`, `scf__cro2.in:5`); its hp.x ran `npool = 4` (`hp__cro2_q222.out:18`) — i.e. not the Anvil `52_hp.slurm` path. **Vast** is the registered attribution (`docs/43:4394`), consistent with the `queue_hp.sh`/cgroup notes at `runs/hp_tio2/m_hp_tio2.txt:24-27`, and is not established by the output itself | 10Aug2026 06:48:15 (`:2`) | 20 (`:13`) / 4 (`:28`) | −517.92950441 (`:3671`) | 4.00 / 4.68 (`:3690-3691`) | 19 (`:3693`) | 37.44 s (`:3828`) |
| ortho q222, banked, job 20382206 — `runs/hp_cro2_ortho/scf__cro2_ortho.out` | **Anvil**: `/anvil/projects/x-che260157/pseudo/` (`:82`); reads `scf__cro2_ortho.run.in` (`:20`); scratch dir `./tmp_hp_20382206/` (`:3755`) carries the job id | 3Sep2026 21:08:53 (`:2`) | 20 / 4 | −517.92950441 (`:3671`) | 4.00 / 4.68 (`:3690-3691`) | 19 (`:3693`) | 30.22 s (`:3829`) |
| atomic q333, new — `runs/hp_cro2_q333/scf__cro2_atomic_q333.out` | **Anvil** a104 (`anvil/logs/hp_20419730.out:1`); `/anvil/...` (`:82`); `.run.in` (`:20`) | 5Sep2026 13:20:05 (`:2`) | 20 (`:13`) / 4 (`:28`) | −517.92950441 (`:3671`) | 4.00 / 4.68 (`:3690-3691`) | 19 (`:3693`) | 30.45 s (`:3828`) |
| ortho q333, new — `runs/hp_cro2_q333/scf__cro2_ortho_q333.out` | **Anvil** a119 (`anvil/logs/hp_20419731.out:1`); `/anvil/...` (`:82`); `.run.in` (`:20`) | 5Sep2026 13:20:06 (`:2`) | 20 / 4 | −517.92950441 (`:3671`) | 4.00 / 4.68 (`:3690-3691`) | 19 (`:3693`) | 48.23 s (`:3829`) |

Verdicts as registered at `docs/43:4392-4395`: ortho, Anvil against Anvil, energy string,
magnetisation and iteration count identical → **MATCH** (`docs/figs/hp_cro2_q333.json:88-90`);
atomic, Anvil against Vast, ΔE = 0.0 Ry at the printed decimals against the 1e-5 Ry bar →
**AGREES (A8.5)** (`:45-47`). `JOB DONE` 1 and `convergence NOT achieved` 0 on both new SCFs
(wrapper lines `hp_2041973{0,1}.out:3`). Hubbard energy 0.00000000 Ry on every leg (`:3681`).
A8.8 isolation held: the outputs sit in `runs/hp_cro2_q333/` only; `runs/hp_tio2/` and
`runs/hp_cro2_ortho/` carry their original files and dates (10 Aug, 3 Sep).

## B. Gate-(e) pair at np = 128 — the record

**Decks.** Byte-identical to the banked sources: md5 `edb3aae651d1064d908a0e66970db4bf` (atomic)
and `6f36bd88bed6521fdb771ae321032c5e` (ortho) recorded at `runs/a0/m_eproj_np128.txt:23-24` and
re-verified equal on `runs/s0/e_proj/s0_O__u715_{atomic,ortho}.in`; `diff` empty. Both new runs
print `running on 128 processor cores` (`runs/a0/eproj_np128/s0_O__u715_{atomic,ortho}.out:13`),
`K-points division: npool = 4` (`:30`), 15 k-points (`:148`), node a144 (`anvil/logs/a0_20419733_{1,2}.out:1`),
pseudopotentials from `/anvil/projects/x-che260157/pseudo/` (`:84`). The banked legs print
`running on 20 processor cores` (`runs/s0/e_proj/s0_O__u715_{atomic,ortho}.out:13`) with
`/usr/share/espresso/pseudo/` (`:84`) — the Vast box, as `docs/43:4401` states.

| leg | run | started | E (Ry) | total / abs mag (μB) | SCF iters | est. scf accuracy | wall | `JOB DONE` |
|---|---|---|---|---|---|---|---|---|
| atomic | Anvil np = 128 | 5Sep2026 15:40:07 (`:2`) | −1592.51110033 (`:1673`) | 10.00 / 23.46 (`:1686-1687`) | 26 (`:1689`) | < 3.8e-7 Ry (`:1674`) | 1m56.44s (`:1772`) | 1 (`:1778`) |
| atomic | banked Vast np = 20 | 20Aug2026 19:18:18 (`:2`) | −1592.51110015 (`:1659`) | 10.00 / 23.45 (`:1672-1673`) | 25 (`:1675`) | < 8.8e-7 Ry (`:1660`) | 12m 2.24s (`:1758`) | 1 (`:1764`) |
| ortho | Anvil np = 128 | 5Sep2026 15:43:31 (`:2`) | −1592.78131334 (`:1687`) | 10.00 / 22.86 (`:1700-1701`) | 27 (`:1703`) | < 5.5e-7 Ry (`:1688`) | 2m14.02s (`:1787`) | 1 (`:1793`) |
| ortho | banked Vast np = 20 | 20Aug2026 19:30:23 (`:2`) | −1592.78131312 (`:1688`) | 10.00 / 22.86 (`:1701-1702`) | 27 (`:1704`) | < 8.9e-7 Ry (`:1689`) | 13m 2.18s (`:1788`) | 1 (`:1794`) |

Scorer (`docs/figs/eproj_np128.json`): ΔE atomic −1.8e-7 Ry (`:20`), ortho −2.2e-7 Ry (`:39`),
both **AGREES** (`:21`, `:40`) against the 1e-5 Ry bar; `pair_new_Ry` 0.27021301 (`:44`),
`pair_banked_Ry` 0.27021297 (`:45`). Total magnetisation is 10.00 μB on all four; absolute
magnetisation differs by 0.01 μB on the atomic leg (23.46 against 23.45) and not at all on the
ortho leg; the atomic leg took one more SCF iteration on Anvil (26 against 25), the ortho leg the
same 27. `convergence NOT achieved` 0 on both new outputs; wrapper lines `rc=0 … scf_fail=0
job_done=1` (`a0_20419733_{1,2}.out:2`).

**A6.5(1) charge readout — now exists.** `runs/a0/eproj_np128/s0_O__u715_atomic.lowdin.txt` and
`s0_O__u715_ortho.lowdin.txt` (292 lines each; header `:1`, `Lowdin Charges:` at `:2`, 19 `Atom #`
blocks, spilling parameter 0.0032 and 0.0033 at `:156`), extracted from the inline projwfc runs
(`PROJWFC v.7.5` on 128 cores, `s0_O__u715_{atomic,ortho}.projwfc.out:2,13`; `Lowdin Charges:` at
`:22545` / `:22111`; `JOB DONE` at `:22707` / `:22273`; 11.40 s / 12.17 s wall at `:22701` / `:22267`;
`projwfc rc=0 job_done=1 lowdin_blocks=1` at `a0_20419733_{1,2}.out:4`). The rule is `docs/43:4106-4112`
("A6.5(1) requires a charge readout for every A0 point"); in the wrapper the check sits at
`anvil/46_a0.slurm:114-117` — it prints `PROJWFC FAILED -- A6.5(1) requires a charge readout for
every A0 point` (`:115`) when projwfc returns non-zero or prints no `JOB DONE` (`:114`), and it
echoes without exiting; `docs/43:4111` cites `:112`, which is the `Lowdin Charges` count line, and
calls it a hard-fail (the script's last change is `5d30449`, 2026-08-27, before that line was
written). The banked `runs/s0/e_proj/` directory holds six files and no `.lowdin.txt`. Nothing is
read from the Löwdin tables here.

**Realised cost.** 164 s and 157 s of Slurm Elapsed at 128 cores = 5.83 + 5.58 = **11.41 core-h**
for the pair (`core-walltime` 05:49:52 and 05:34:56, `a0_20419733_{1,2}.out:14`) against "~10 SU"
(`docs/43:4410`); pw.x alone (141 s + 137 s, `a0_20419733_{1,2}.out:2`) is 9.88 core-h. Wall on
128 cores was 6.2× shorter than the banked 20-core runs (116 s against 722 s on the atomic leg) for
6.4× the cores.

## Corrections to the planning text

Each is a sentence the outputs contradict, with its line; the sentences stay in place as dated
record and are corrected by this readout, not edited.

1. `docs/43:4396-4397` — "the q333 mesh has 27 q-points against 8, so the planning figure is scaled
   by that count, ~27 core-h per leg and ~55 for the pair". Two errors. The counts are the full
   meshes; hp.x iterates the irreducible sets, **8 against 6** (`hp__cro2_{atomic,ortho}_q333.out:130`;
   `hp__cro2_ortho_q222.out:130`; `runs/hp_tio2/hp__cro2_q222.out:131`), a ratio of 1.33. And cost
   did not scale with q-count: the linear-response work (point-iterations) grew 4.1× (ortho) and
   5.5× (atomic) and throughput fell inside both runs, so the realised figures are **168.5 and 148.9
   core-h per leg, 317.4 for the pair** — 5.8× the pair figure. INFERRED, not a prescription: on
   this k-mesh the q = ⅓ k+q sets were 2.69× the q = ½ sets (4 602 against 1 710); a cost model built
   on Σ(k+q × iterations) would also need a per-point-iteration rate, and the two q333 runs did not
   deliver one uniformly (item iii above).
2. `docs/43:4410` — "Cost: ~10 SU at the measured a0 rate". Realised 11.41 core-h of Elapsed; the
   pw.x part is 9.88. Inside the tilde; recorded beside, not contradicted.
3. `runs/hp_cro2_q333/MANIFEST.txt:9` ("np=20 nk=4") and `anvil/logs/hp_2041973{0,1}.out:1`
   ("np=20 nk=4") describe pw.x only: `anvil/52_hp.slurm:85` passes `-nk` to pw.x and `:100` launches
   hp.x without it, and both q333 hp.x outputs print `R & G space division: proc/nbgrp/npool/nimage
   = 20` with no `K-points division` line (`:18`). The same holds for the banked ortho q222 leg
   (`runs/hp_cro2_ortho/hp__cro2_ortho_q222.out:18`), so A12b's "np = 20, nk = 4, matching the banked
   atomic leg's shape" (`docs/43:3491`, outside item 5 but in this arm's lineage) was true of pw.x and
   not of hp.x: the banked atomic q222 hp.x ran with `K-points division: npool = 4`
   (`runs/hp_tio2/hp__cro2_q222.out:18`). A record correction; no number moves. Whether pools would
   change hp.x's throughput is the INFERRED item above, not established.
4. `docs/43:3542-3543` and `docs/79:69-72` — "CrO₂ q-mesh convergence is NOT measured — only q222
   exists, on both legs … Closing this is one more q333 pair." Now measured and closed by this readout;
   the sentences remain as the dated record of the limit as it stood on 2026-09-04.

Confirmed, not corrected: `docs/43:4393` (job 20382206, Anvil, np = 20 — Anvil and np = 20 by
fingerprint, `runs/hp_cro2_ortho/scf__cro2_ortho.out:82,20,13`; the job id by the scratch directory
`./tmp_hp_20382206/` that output and its hp.x output print, `scf__cro2_ortho.out:3755`,
`hp__cro2_ortho_q222.out:50`); `:4394` (the atomic q222 leg ran on the Vast box — consistent with
the fingerprint, which establishes only that the run did not go through the Anvil wrapper); `:4401`
(the banked gate-(e) legs print 20 cores); `:4405` (nk = 4 on the np = 128 pair — `npool = 4` at
`:30` of both new outputs); `:4386-4388` (deck diffs exactly {prefix, outdir} and {prefix, outdir,
nq}).

## Artifacts on disk at the time of writing

`runs/hp_cro2_q333/` — 15 files: the four decks and `MANIFEST.txt` tracked at `ca5b33e`; the two SCF
outputs, two hp.x outputs (844 271 and 839 262 bytes), two `Hubbard_parameters.dat` (177 710 bytes
each) and four `chi` files untracked. The executed `.run.in` pair was not pulled (absent from the
listing; the wrapper writes it at `52_hp.slurm:72,74`). `runs/a0/eproj_np128/` — the two decks
tracked; two `.out`, two `.lowdin.txt`, two `.projwfc.in` untracked; the two `.projwfc.out`
(1 412 468 and 1 379 496 bytes) present and excluded by `.gitignore:46` (`*.projwfc.out`). The four
Slurm logs and the two readout JSONs are untracked. No output from either arm is committed yet — the
decks, manifests and build scripts (`ca5b33e`) and the scorers (`b502beb`) are; the 22 output, log
and JSON paths are untracked (`git status --porcelain`, 2026-09-06). The banked directories
`runs/hp_tio2/`, `runs/hp_cro2_ortho/` and `runs/s0/e_proj/` received nothing.

> `[SMALL ARMS READOUT COUNTERSIGNED 2026-09-__]` — countersignature slot for the entrant. Until it
> is filled by a dated line the verdicts above are the scorers' output on the record, not countersigned.