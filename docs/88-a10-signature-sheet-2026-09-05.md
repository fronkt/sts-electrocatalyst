# 88 — Amendment 10 signature sheet: the S5 BEEF-vdW σ arm, decks built, thresholds blank

**Status: signature sheet. Nothing here is registered; every slot is the entrant's.**

**Date:** 2026-09-05. **Election of record:** docs/43 `:4366-4373` — the entrant elected to adopt
Amendment 10 (docs/74 v2) and run S5; *"every THRESHOLD there is re-authored by the entrant in his
own words (A7.7, :1441-1447) on the signature sheet docs/88 before A10 is appended here and
deposited, and the deposit precedes the first BEEF job"*; *"Until then the S5 decks may be BUILT and
carry NOT LICENSED; the submitter refuses them by construction (docs/66 §4)."* **Deadline:** the A10
row of docs/45 §D, `:55` — Sep 18.

**What this sheet is.** One row per line of docs/74 marked THRESHOLD, with the proposed value quoted
briefly beside a blank slot; the A10-X election and the ladder it selects; the build choices docs/74
leaves open; what was built; a cost section on measured numbers; and the list of what the build
could not determine. A slot has the form `[A10-<id> 2026-09-__: ____]` and is filled by the entrant,
not by this document. A value in a "proposed" column is docs/74's proposal and nothing more.

**What this sheet is not.** It does not adopt, append, deposit, licence or submit anything. The S5
manifest `runs/s5/m_s5.txt` carries a NOT LICENSED notice (`:5-11`) and `anvil/47_submit_a0.sh`
(`:55-60`) and `anvil/43_submit_s3_wave1.sh` (`:51-56`) refuse it with no override.

---

## 0. Facts the sheet stands on, each read from the tree

### 0.1 Does the Anvil production `pw.x` support BEEF-vdW? — VERBATIM

The production binary is `$QE_PREFIX/bin/pw.x` with `QE_PREFIX=$PROJECT/qe/env`
(`anvil/47_submit_a0.sh:24`; `anvil/46_a0.slurm:73-74` puts `$QE_PREFIX/bin` on PATH). Run on Anvil
2026-09-05, read-only:

```
$ ls -d $PROJECT/qe*
/anvil/projects/x-che260157/qe
$ strings /anvil/projects/x-che260157/qe/env/bin/pw.x | grep -i -m5 beef
{ "beefxH
 @ DRIVER MODE: BEEF-vdw
BEEFens 2000 ensemble energies
unknown BEEF type
unknown BEEF type number
$ find $PROJECT/qe -maxdepth 3 -iname '*beef*'
/anvil/projects/x-che260157/qe/env/lib/libqe_libbeef.a
$ ls -la $PROJECT/qe/env/bin/pw.x $PROJECT/qe/env/lib/libqe_libbeef.a
-rwxr-xr-x 2 x-fcai3 x-che260157 10798648 Dec 19  2025 /anvil/projects/x-che260157/qe/env/bin/pw.x
-rw-r--r-- 2 x-fcai3 x-che260157   119202 Dec 19  2025 /anvil/projects/x-che260157/qe/env/lib/libqe_libbeef.a
$ ldd $PROJECT/qe/env/bin/pw.x | grep -i beef
(no output -- libbeef is linked statically)
```

**Reading:** the Anvil binary carries libbeef and the exact emission string the S0(a) gate scored on
(`BEEFens 2000 ensemble energies`, `runs/s0/a_beef/slab__beefcalc.out:1076`). **It has never been
exercised.** All four S0(a) gate runs executed on a Vast box — every output prints
*"running on 20 processor cores"* (`slab__beefcalc.out:13`, `slab__beefctl.out:13`,
`slab__beefhub.out:13`) and the box ledger `runs/s0/queue_r1_box47662258.ledger.txt:62-64,77` records
them; `find $PROJECT/sts/runs -iname '*beef*'` on Anvil returns only the mirrored `s0/a_beef` files.
The Anvil parity certification (docs/43 `:1613-1621`, docs/46) was PBE-only. So: **capability
supported by the binary's contents; emission on Anvil not yet demonstrated.** See §6 U1.

### 0.2 The banked BEEF work

| file | ran where | date (`:2`) | nat (`:61`) | `input_dft` line | `BEEFens` | JOB DONE |
|---|---|---|---|---|---|---|
| `runs/s0/a_beef/slab__beefcalc.out` | Vast box 47662258, 20 cores | 21Aug2026 11:44 | 18 | `input_dft = 'BEEF-vdW'` (`slab__beefcalc.in:21`) | `:1076`, 2000 members | `:3164` |
| `runs/s0/a_beef/slab__beefhub.out` | Vast box 47662258, 20 cores | 22Aug2026 00:43 | 18 | `input_dft = 'BEEF-vdW'` + `HUBBARD (atomic)` / `U Ru-4d 3.7000` | `:1403`, 2000 members | `:3497` |
| `runs/s0/a_beef/slab__beefctl.out` (control) | same box | 21Aug2026 12:09 | 18 | `input_dft = 'BEEF-vdW'`, `calculation = 'scf'` | **none** | `:1078` |
| `runs/s0/a_beef/slab__beefens.out` | same box | 21Aug2026 | — | `ensemble_energies = .true.` | none | none — `Error in routine read_namelists (1)` (`:23`) |

Both ensembles are the bare 1×1 Ru slab (`Ru_ONCV_PBE-1.0.oncvpsp.upf` + `O.pbe-n-kjpaw_psl.0.1.UPF`,
K_POINTS 8 4 1, `slab__beefcalc.in`). Each output also prints the 32 `BEEF-vdW xc energy
contributions` after the member block (`slab__beefcalc.out:3078`, `slab__beefhub.out:3405`), and
`Initializing libbeef V0.1.2 with the BEEF-vdW functional.` (`:29` in all three). The control deck
without an emission switch took **longer** than the ensemble deck (35m31.04s WALL, `slab__beefctl.out:1072`,
vs 25m20.65s, `slab__beefcalc.out:3158`), which supports the stage spec's "the ~2000-member ensemble
is free post-processing" (round-2 `:289`).

### 0.3 What was built (§4 has the table)

14 decks under `runs/s5/` — `{Ru, Ir, Ti} × {ref, s0_O, s0_OH, s0_OOH}` + `gas/{H2, H2O}` — by
`src/dft/build_s5.py`, manifest `runs/s5/m_s5.txt`, **NOT LICENSED**, byte-identical on a second
run. Four Cr decks for the A10-X extension are **not** built (§6 U6).

---

## 1. Every line of docs/74 marked THRESHOLD

`grep -n "THRESHOLD" docs/74-amendment-10-DRAFT.md` returns eleven lines: nine THRESHOLD blocks, the
preamble sentence at `:6`, and `:411`, which refers to docs/43 `:1930`'s THRESHOLD (the body-ledger
displacement) rather than stating a new one. The nine blocks:

| id | docs/74 line | what it governs | proposed value (docs/74, quoted briefly) | entrant's own wording |
|---|---|---|---|---|
| A10-E | `:72` | which written source the P-BEEF criterion is (round-1 vs round-2) | *"the operative P-BEEF criterion is round-2's — its Amendment 10 block **and** its S5 stage spec at `:286-291` together — and round-1's is struck as superseded, with docs/43 `:1930`'s pointer as the reason of record"* (`:72-74`) | `[A10-E 2026-09-__: ____]` |
| A10-M | `:84` | the disposition of an outcome in neither band at n = 3 | *"any outcome in neither band maps to **SCORED — MIDDLE BAND / NOT MET** in the A11.R2 vocabulary (docs/43 :2088-2095): reported with its count and its per-metal σ attached, never quoted bare, licensing no registered consequence, and neither HELD, nor TRIGGERED, nor WITHDRAWN-UNSCORED"* (`:84-87`) | `[A10-M 2026-09-__: ____]` |
| A10-D | `:98` | the denominator ladder, fixed before any job, and the non-scoreable rule | *"which ladder applies is fixed by the A10-X election below, before any BEEF job runs, and never afterwards"* (`:98-99`); Ladder B (`:101-108`) and Ladder X (`:110-117`) are reproduced in §2; non-scoreable = *"prints 'convergence NOT achieved', carries an `Error in routine` block, or emits no `BEEFens` line"* (`:125-126`) | `[A10-D 2026-09-__: ____]` |
| A10-G | `:150` | closing the S0(a) gate on the record and striking "gated on S0(a)" | *"record gate (a) as **PASSED — SELECT-WINNER = deck (ii) `calculation='ensemble'`** ... and strike 'gated on S0(a)' from docs/43 `:2022` and docs/45 `:33`/`:55`/`:81` by dated erratum. No compute is owed."* (`:150-152`) — see §6 U1 on "no compute is owed" | `[A10-G 2026-09-__: ____]` |
| A10-σ | `:162` | the estimator: what σ_BEEF(η) is, longhand | per member *i* from all four states and both gas references at the same index (`:164-166`); ΔG per member by the production CHE ladder with member-independent ZPE/TS (`:167-170`); η_i = max(ΔG)/e − 1.23 V (`:171-174`); *"the **sample standard deviation** of {η_i} over the N members, in volts"* (`:175`); N mismatch across states = non-scoreable (`:178-179`); one script `src/dft/p_beef_readout.py` parsing thresholds out of docs/43 (`:180-183`); stated limit: fixed geometry (`:185-187`) | `[A10-σ 2026-09-__: ____]` |
| A10-C | `:226` | what σ may be compared against, and both directions pre-stated | bands untouched, < 0.25 / ≥ 0.30 V absolute (`:228`); primary comparison same-metal on η at fixed endpoints U = 0 → 9, *"Ru 0.497, Ti 0.246, Ir 0.027 V"*, max−min beside it, Ir's 7.4× gap stated (`:229-232`); 1.122 V never bare and named as Cr's (`:233-235`); symmetry pair never one end alone (`:236-237`); both directions (`:238-242`) | `[A10-C 2026-09-__: ____]` |
| A10-S | `:253` | scope label of the S5 row | *"the S5 row is labelled **'XC only, non-magnetic three'** ... and σ_BEEF may not be generalised beyond the scoreable set without the extension arm having run"* (`:253-255`) | `[A10-S 2026-09-__: ____]` |
| A10-X | `:257` | **the election:** is Cr added, selecting Ladder X over Ladder B | *"Cr is added, giving {Ru, Ir, Ti, Cr} and Ladder X"* (`:258`), with the against-case at `:262-273` | `[A10-X 2026-09-__: ____]` — see §2 |
| A10-K | `:388` | P-DISPOSITION by name, the submit-by date, the kill | *"P-BEEF is subject to P-DISPOSITION by name"* (`:389-390`); *"the decks are built and submitted within 7 days of the A10 deposit, and in no case later than Oct 10 2026. Past that, S5 is **CUT**"* (`:391-394`); deliberate withdrawal considered and not taken (`:395-399`) | `[A10-K 2026-09-__: ____]` |

**Required order** per docs/74 `:426-430`: (1) the nine slots above in the entrant's words, dated;
(2) append to docs/43 as AMENDMENT 10 and re-deposit, DOI and commit recorded; (3) only then submit —
the decks already exist and their md5s are in `runs/s5/m_s5.txt:30-87`; (4) the A10-G erratum.

---

## 2. The A10-X election and the ladder it selects

A10-D says the ladder is chosen by A10-X **before any BEEF job runs** (`:98-99`). Both ladders are
reproduced here from docs/74 so the election can be written against them; neither is registered.

**Ladder B — base set {Ru, Ir, Ti}, n = 3** (docs/74 `:101-108`, proposed)

| scoreable σ | confirmation | falsification | else |
|---|---|---|---|
| 3 | ≥2 below 0.25 V (0.667) | ≥2 at/above 0.30 V | MIDDLE BAND |
| 2 | both below 0.25 V (1.000) | ≥2 at/above 0.30 V | MIDDLE BAND |
| 1 | not scoreable — single σ reported with its metal named, no verdict | | |
| 0 | WITHDRAWN-UNSCORED with its date | | |

**Ladder X — extended set {Ru, Ir, Ti, Cr}, n = 4** (docs/74 `:110-117`, proposed; applies only if
A10-X elects Cr)

| scoreable σ | confirmation | falsification | else |
|---|---|---|---|
| 4 | ≥3 below 0.25 V (0.750) | ≥2 at/above 0.30 V | MIDDLE BAND |
| 3 | ≥3 of 3 below 0.25 V (1.000) | ≥2 at/above 0.30 V | MIDDLE BAND |
| 2 | both below 0.25 V (1.000) | ≥2 at/above 0.30 V | MIDDLE BAND |
| 1 / 0 | as Ladder B | | |

Falsification is ≥2 at every rung of both (A11.R2 rule (ii), docs/74 `:95-96`).

| slot | consequence in the tree |
|---|---|
| `[A10-X 2026-09-__: ____]` — Cr added, or not | if Cr: **four more decks** (Cr is nspin = 2 with `U Cr-3d 3.7`, docs/54 `:81`); the HUBBARD-card evidence is `slab__beefhub.out:1403` (docs/74 `:263-264`); sources would be `runs/probe/Cr_cellsym/{ref__2x1v, s0_O__2x1v_mir, s0_OH__2x1v_mir}` and `runs/s3/Cr/s0_OOH__2x1v_escape` on the `runs/a0/cell/manifest.json:64-68` precedent (the mir relax sits on a saddle 150.8 meV above the escape). Not built (§6 U6). |
| `[A10-D 2026-09-__: ____]` — the ladder, in the entrant's words | fixes the denominator for scoring; must precede the first job (`:98-99`) |

---

## 3. Choices docs/74 does not fix, which the build had to make — slots because they are the entrant's

| slot | what the build did, and why | the alternative on disk |
|---|---|---|
| `[A10-ARM 2026-09-__: ____]` — which tier_v3 symmetry arm supplies the fixed geometry | docs/74 `:281-282` names the cell (2×1v) and the tier but not the arm; tier_v3 carries two per adsorbate state, mir = symmetry ON and off = `nosym` + displacement (docs/54 `:18-21`). The build takes **mir**, on the precedent of the only other fixed-geometry 2×1v single-point arm, `runs/a0/cell/manifest.json:42,55` (*"mir arm = symmetry-ON, the counterpart of the symmetry-ON 1x1 ladder"*), and the bare `ref__2x1v` (nosym + noinv, 16 k, docs/54 `:129`). | the off-arm relaxations are banked and converged for all nine adsorbate states (`runs/probe/{Ru,Ir}_cellsym/s0_*__2x1v_off.out`, `runs/s3/Ti/s0_*__2x1v_off.out`). PBE gaps E(mir) − E(off), from the last `!` energy of each pair of source outputs (the mir energies are in the §4 table; the off energies are the corresponding `s0_*__2x1v_off.out`; Ru/Ir pairs also tabulated at docs/54 `:242-251`, `:261-265`; 1 Ry = 13.6057 eV): Ru *O +0.0000, *OH −0.0130, *OOH **+0.1088** eV; Ir *O −0.0001, *OH +0.0372, *OOH +0.0185 eV; Ti *O −0.0012, *OH +0.0381, *OOH **−0.1346** eV. Switching arm is one constant in `build_s5.py` (`ARM`). |
| `[A10-ENS 2026-09-__: ____]` — which emitted object the members are read from | the decks emit both the 2000 `BEEFens` energies (QE's own member draw) and the 32 `BEEF-vdW xc energy contributions` (`slab__beefcalc.out:1076`, `:3078`). The stage spec's non-negotiable (iv) says *"regenerate members portably with `ase.dft.bee.ensemble(seed=0)` rather than QE's glibc `srandom`"* (round-2 `:293`), which reads the contributions; A10-σ item 4 says N *"must equal the emitted member count"* (docs/74 `:175-177`), which reads the `BEEFens` block. The build decides nothing here; the readout must. | both blocks are in every output either way |
| submitter path (lead's/entrant's, not a threshold) | the manifest is in `anvil/47_submit_a0.sh` form; that path runs `anvil/46_a0.slurm`, which runs `projwfc.x` after `pw.x` and hard-fails on `PROJWFC FAILED` (`:115`) — a Löwdin readout S5 does not use. `anvil/43_submit_s3_wave1.sh` carries the same two guards (`:51-72`) and no projwfc. Either accepts the manifest once the notice is replaced. | — |

The remaining entrant items of docs/74 `:438-445` that are not thresholds: `[A10-DISP 2026-09-__: ____]`
the body-ledger displacement before Sep 20 (docs/43 `:1930`, docs/74 `:442`); `[A10-A74 2026-09-__: ____]`
whether the A7.4 gate table gains a result column (docs/74 `:443`); `[A10-CHR 2026-09-__: ____]`
Christensen's functional-independence claim, proposed *not claimed* (docs/74 `:444`);
`[A10-DEP 2026-09-__: ____]` whether the deposit also carries the terminology change (docs/74 `:445`).

---

## 4. What was built

`src/dft/build_s5.py` clones each source deck and replaces exactly: `calculation = 'relax'` →
`'ensemble'`; `prefix` → `<stem>__beef`; one inserted line `input_dft = 'BEEF-vdW'` as the last line
of `&SYSTEM`; the `ATOMIC_POSITIONS` coordinates → the source `.out`'s `Begin final coordinates`
block at 8 decimals, species and `if_pos` flags preserved line by line. The builder diffs source
against product and refuses on any other difference; refuses a source whose `.out` lacks `JOB DONE`
or `bfgs converged`, carries `convergence NOT achieved`, or has other than one final-coordinates
block; refuses a source with a HUBBARD card, an `nspin = 2` line, an existing `input_dft`, or any
`startingpot`/`startingwfc`/`restart_mode`. Two consecutive builds are byte-identical (md5 over all
15 emitted files, checked 2026-09-05). All emitted files are LF.

**Why `calculation = 'ensemble'` and not `'scf'`.** docs/43 `:1497-1498` (deposited): *"BEEF is
reachable only through `calculation='ensemble'`."* The S0(a) control deck — `calculation = 'scf'`
plus `input_dft` — reached JOB DONE with no `BEEFens` block (`runs/s0/a_beef/slab__beefctl.out`,
0 matches); the `'ensemble'` deck emitted 2000 members (`slab__beefcalc.out:1076`). In QE 7.5
`'ensemble'` is an SCF followed by the non-self-consistent ensemble on the converged BEEF-vdW
density — the stage spec's non-negotiable (i) (round-2 `:293`). An `'scf'` deck would be a
self-consistent BEEF-vdW energy with no σ.

| group | job (`runs/s5/<group>/<job>.in`) | source deck | source `.out` (all: JOB DONE, `bfgs converged`, one final block, 0 `convergence NOT achieved`) | nat | k | nk | lines differing (coords) | deck md5 |
|---|---|---|---|---|---|---|---|---|
| Ru | `ref__2x1v__beef` | `runs/probe/Ru_cellsym/ref__2x1v.in` | `…/ref__2x1v.out` — 11Aug2026, 4 cores, −3261.33545254 Ry | 36 | 16 | 16 | 4 (1) | `a28b777e3dff5c98696525ac00533e36` |
| Ru | `s0_O__2x1v_mir__beef` | `…/s0_O__2x1v_mir.in` | `…/s0_O__2x1v_mir.out` — 11Aug2026, 4 cores, −3302.93178672 Ry | 37 | 9 | 8 | 26 (23) | `8f5f884f6cfbebd3317bcea0eab3d7be` |
| Ru | `s0_OH__2x1v_mir__beef` | `…/s0_OH__2x1v_mir.in` | `…/s0_OH__2x1v_mir.out` — 10Aug2026, 20 cores, −3304.19810638 Ry | 38 | 9 | 8 | 27 (24) | `244c2bb3ec7a039b85fdfe4f53066356` |
| Ru | `s0_OOH__2x1v_mir__beef` | `…/s0_OOH__2x1v_mir.in` | `…/s0_OOH__2x1v_mir.out` — 11Aug2026, 20 cores, −3345.67264760 Ry | 39 | 9 | 8 | 28 (25) | `04cc4a13b1db236b940e03dfcbe04906` |
| Ir | `ref__2x1v__beef` | `runs/probe/Ir_cellsym/ref__2x1v.in` | `…/ref__2x1v.out` — 11Aug2026, 4 cores, −3179.49645246 Ry | 36 | 16 | 16 | 3 (0) | `1d40961b9d4a8ccf605d388a6796f2aa` |
| Ir | `s0_O__2x1v_mir__beef` | `…/s0_O__2x1v_mir.in` | `…/s0_O__2x1v_mir.out` — 13Aug2026, 20 cores, −3221.09584906 Ry | 37 | 9 | 8 | 26 (23) | `cd00aebc3682ace5e5a3468c107a2d37` |
| Ir | `s0_OH__2x1v_mir__beef` | `…/s0_OH__2x1v_mir.in` | `…/s0_OH__2x1v_mir.out` — 11Aug2026, 4 cores, −3222.38878145 Ry | 38 | 9 | 8 | 27 (24) | `40f47e66724cff06c5f84eebe4f8432a` |
| Ir | `s0_OOH__2x1v_mir__beef` | `…/s0_OOH__2x1v_mir.in` | `…/s0_OOH__2x1v_mir.out` — 12Aug2026, 20 cores, −3263.87194671 Ry | 39 | 9 | 8 | 28 (25) | `ad6d19cf5648baf4000deb6c04707902` |
| Ti | `ref__2x1v__beef` | `runs/s3/Ti/ref__2x1v.in` | `…/ref__2x1v.out` — 23Aug2026, 128 cores (Anvil), −2435.23315746 Ry | 36 | 16 | 16 | 25 (22) | `ffdb854b1131020c56af3dc5c9d9d74b` |
| Ti | `s0_O__2x1v_mir__beef` | `…/s0_O__2x1v_mir.in` | `…/s0_O__2x1v_mir.out` — 24Aug2026, 128 cores, −2476.62219381 Ry | 37 | 9 | 8 | 26 (23) | `edb366d2100218b3a859724c01e57551` |
| Ti | `s0_OH__2x1v_mir__beef` | `…/s0_OH__2x1v_mir.in` | `…/s0_OH__2x1v_mir.out` — 24Aug2026, 128 cores, −2478.00635822 Ry | 38 | 9 | 8 | 27 (24) | `3498abc0477889667b60a2376201f0a3` |
| Ti | `s0_OOH__2x1v_mir__beef` | `…/s0_OOH__2x1v_mir.in` | `…/s0_OOH__2x1v_mir.out` — 24Aug2026, 128 cores, −2519.46826336 Ry | 39 | 9 | 8 | 28 (25) | `3b0212dd449123c81badf3d29b57c80e` |
| gas | `H2__beef` | `runs/Ru_anchor/H2.in` | `…/H2.out` — 27Jun2026, 32 cores, −2.33323818 Ry | 2 | Γ | 1 | 5 (2) | `d4346ec96fa5ac703d5eb2888ce158de` |
| gas | `H2O__beef` | `runs/Ru_anchor/H2O.in` | `…/H2O.out` — 27Jun2026, 32 cores, −44.04119711 Ry | 3 | Γ | 1 | 6 (3) | `acb52dbcdedb5038619cb5c6742fc1a6` |

Every differing line is written out in `runs/s5/m_s5.txt:89-391`; the source-deck and source-`.out`
md5s are at `:30-87`; the runnable rows are `:393-406`. Ru/Ir `ref__2x1v` changed 1 and 0 coordinate
lines because those relaxations started from already-relaxed production coordinates and converged
where they stood (docs/54 `:239`, `:259`); the one Ru line is `-0.00000000` → `0.00000000`
(`m_s5.txt:95`), a sign of zero, not a displacement. nk per row follows the source `.out`'s k-point count and
reproduces `runs/s3/m_s3_wave1.txt:81-87` for Ti; NP = 128 is a multiple of 16, 8 and 1.

**Gas references.** `H2.in` and `H2O.in` are byte-identical in all nine `runs/*_slab` and
`runs/*_anchor` directories (md5 `5c48465f33f83474ef0a4b22b36673e9` and `73ed19be6f1a16b4ed190b68dfc22348`),
which is what docs/74 `:291-292` relies on for index matching; the builder asserts it, and asserts
that all eight banked `.out` finals agree to 1e-8 Å. They are `ibrav = 1`, `celldm(1) = 22.67671`
bohr = 12.00 Å, `assume_isolated = 'mt'`, `nspin = 1`, K_POINTS gamma — the 12 Å Martyna-Tuckerman
box of round-2 `:293`. Their banked decks and outputs are **CRLF** in every copy (32 CR / 32 LF in
`runs/Ru_anchor/H2.in`), unlike every other banked deck; the builder reads them with CRLF normalised
and emits LF, and the manifest says so (`m_s5.txt:82`, `:87`).

**Inherited, unchanged:** ecutwfc 80 / ecutrho 640, mv 0.01, `local-TF` 0.3, `conv_thr 1.0d-6`,
`electron_maxstep 200`, `tprnfor`, `nstep`, the `&IONS` block (also carried by both S0(a) decks
that ran to JOB DONE), `max_seconds` (the source relax budgets; the smallest is 75,670 s = 21.0 h on
Ru `s0_OH`, under the 48 h of `anvil/46_a0.slurm:35`), pseudopotentials (`Ru_ONCV_PBE-1.0.oncvpsp.upf`,
`Ir_pbe_v1.2.uspp.F.UPF`, `ti_pbe_v1.4.uspp.F.UPF`, `O.pbe-n-kjpaw_psl.0.1.UPF`, `H.pbe-rrkjus_psl.1.0.0.UPF`),
and the absence of any HUBBARD card and any `nspin` line on the slabs (nspin = 1 by default; docs/54
`:86-88`). `input_dft` is on the frozen recipe's `_FORBIDDEN` list (`src/dft/build_cellsym_pilot.py:318`);
the S0(a) README recorded that as a registered deviation for the gate (`runs/s0/a_beef/README.md:107`),
and the same deviation applies to every S5 deck (§7 C3).

---

## 5. Cost

**Decks:** 14 built (12 slab + 2 gas). With A10-X: +4 Cr, not built.

**5.1 The measured pw.x cost model, September arms.** docs/43 `:4059`: P-PROJ-6, 24 decks, *"1.394 h
WALL at 128 cores = 178.4 core-hours"* → 7.4 SU per deck (1×1, nat 18, nspin = 2, +U). docs/43
`:4099`: P-PROJ-CELL, 4 decks, *"0.554 h WALL at 128 cores = 70.9 core-hours"* → 17.7 SU per deck
(2×1v, nat 36–39, nspin = 2, +U, ortho-atomic). tasks/todo.md `:1845-1850` tabulates both against
their estimates: *"The pw.x cost model runs conservative on P-PROJ-6 and is accurate on P-PROJ-CELL."*

**5.2 The closest banked analogues to an S5 deck.** nspin = 1, 2×1v, PBE, U = 0, 128 ranks, Anvil,
fixed-geometry SCF: `runs/s3/Ti/ref__2x1v__g1.out` 3m45.39s WALL = 8.0 SU (23 SCF iterations);
`s0_OH__2x1v_mir__g1.out` 3m26.23s = 7.3 SU (28); `s0_OOH__2x1v_mir__g1.out` 5m26.11s = 11.6 SU (42).
The BEEF-vdW overhead at a matched system: the S0(a) probe (1×1 Ru bare slab, nspin = 1, U = 0)
cost 25m20.65s × 20 cores = 8.4 core-h (`slab__beefcalc.out:3158`, 21 iterations) and 35m31.04s × 20
= 11.8 core-h for the control (`slab__beefctl.out:1072`, 22 iterations), against the same slab in PBE
on Anvil, `runs/a0/main/Ru/slab__u000.out` 2m53.98s × 128 = 6.2 core-h (21 iterations) — a ratio of
**1.4–1.9×**, cross-machine (Vast 20-core vs Anvil 128-rank; docs/43 `:1662`'s "SU per ionic step is
flat from 40 to 128 ranks" is the only basis for comparing core-hours across rank counts, and it was
measured on Anvil alone).

**5.3 Estimate on that basis.** 12 slab decks × (7.3–11.6 SU) × (1.4–1.9) ≈ **120–270 SU**, plus two
gas decks at well under 5 SU together: **≈ 125–275 SU ≈ 0.2–0.5 % of the 59,473.5 SU balance**
(`mybalance`, Anvil, 2026-09-05: 40,526.5 used of 100,000). With A10-X's four nspin = 2 Cr decks at
the P-PROJ-CELL rate × the same ratio, +100–135 SU.

**5.4 docs/74 §A10.5's range** (`:318-324`): base 12 decks **~360–1,700 SU**, gas ~10–40, Cr extension
~170–800, *"total with extension ~540–2,540"*, against *"59,761.1 SU"*. Its anchors are the stage
spec's box-hours — *"~1.5 h"* per deck (round-2 `:289`) and *"~3–7 h — a 3–5× under-count"* (`:291`) —
converted at 20 cores per box-hour (`:311-312`).

**5.5 Which basis is better, and why.** §5.2–5.3. It is built from runs of the same cell, the same
spin treatment, the same machine and the same rank count as S5 will use, and from the only measured
BEEF-vs-PBE ratio in the tree; docs/74's is built from a planning guess that the stage spec itself
flags as a 3–5× under-count and then widens. The two disagree by ~3–6× in the same direction — docs/74
is the conservative one — so no decision turns on the difference: both say compute is not the
constraint on S5. **What neither basis has:** a BEEF-vdW SCF at 128 ranks, on a 2×1v cell, or on
Anvil at all. The first S5 deck to complete replaces both.

---

## 6. What the build could not determine — UNKNOWN

| # | UNKNOWN | what resolves it |
|---|---|---|
| U1 | **Whether the Anvil `pw.x` emits the ensemble.** The binary carries libbeef and the `BEEFens 2000 ensemble energies` string (§0.1), but every BEEF run in the campaign executed on a Vast box; docs/43 `:1384`'s gate question — *"which switch this build honours"* — was answered for that build. docs/74 `:152`'s *"No compute is owed"* is true of the gate as registered and untested for the production binary. | a re-run of `runs/s0/a_beef/slab__beefcalc.in` on Anvil (18 atoms; ~8.5 core-h at the Vast rate), which is a job and therefore not this build's to launch; or accepting the strings/libbeef evidence in the A10-G slot. |
| U2 | **The symmetry arm** (§3, `[A10-ARM]`). docs/74 is silent; the build took mir by precedent. | the entrant's slot. |
| U3 | **The scored member object** (§3, `[A10-ENS]`): QE's `BEEFens` block or members regenerated from the 32 contributions with `ase.dft.bee.ensemble(seed=0)`. docs/74 `:175-177` and round-2 `:293` point at different objects. | the entrant's slot; then `src/dft/p_beef_readout.py`, which does not exist (docs/74 `:180`) and, by A10-σ item 6, cannot until A10's thresholds are in docs/43 to parse. |
| U4 | **Pseudopotential/functional mismatch as a stated limit.** All five UPFs are PBE-generated; BEEF-vdW is applied by `input_dft` override — pw.x prints *"IMPORTANT: XC functional enforced from input"* (`slab__beefcalc.out:34`). The S0(a) gate ran the same way. Whether A10 states this beside A10-σ's fixed-geometry limit (`:185-187`) is not decided by any document. | the entrant's A10-σ wording. |
| U5 | **Anvil-side facts the build could only read, not verify by a run:** `H.pbe-rrkjus_psl.1.0.0.UPF` is staged (the Ti `s0_OH`/`s0_OOH` S3 decks that carry it ran on Anvil 24Aug2026); `PARITY_PASS` exists; `$PROJECT/sts/runs/s5` does not exist on Anvil — the decks are local only. | `anvil/20_stage.sh` or the lead's mirror step, after licensing. |
| U6 | **A10-X's four Cr decks are not built.** If elected, `build_s5.py` needs a Cr entry that admits a HUBBARD card and `nspin = 2` (both refused today by design) and takes `s0_OOH` from `runs/s3/Cr/s0_OOH__2x1v_escape` per `runs/a0/cell/manifest.json:64-68`. | the `[A10-X]` slot, then a ~20-line extension of the builder. |
| U7 | **Whether a member-by-member ΔG can be formed with the H2/H2O references under `calculation = 'ensemble'` at Γ with `assume_isolated = 'mt'`.** Nothing in the tree has run BEEF-vdW on an isolated molecule; the ensemble is a density functional of the converged density and the Martyna-Tuckerman correction acts on the Hartree term, so no conflict is expected, but it is unmeasured. | the two gas decks themselves — they are the cheapest rows in the manifest. |

---

## 7. Where docs/74 and the tree disagree

| # | docs/74 | the tree |
|---|---|---|
| C1 | `:281` *"nat ≈ 36–38"* | nat is 36 / 37 / 38 / **39** — `runs/probe/Ru_cellsym/s0_OOH__2x1v_mir.out:61` *"number of atoms/cell = 39"*, likewise Ir and Ti `s0_OOH` (§4 table). |
| C2 | `:150-152` A10-G: gate (a) PASSED for *"this build"*, *"No compute is owed"* | the four gate outputs ran on Vast box 47662258 (`runs/s0/a_beef/*.out:13`, ledger `:62-64,77`); the Anvil binary has libbeef linked (§0.1) and has never emitted a BEEFens block. docs/43 `:1384` asks which switch *"this build"* honours. |
| C3 | `:288-289` cites the `_FORBIDDEN` guard for `startingpot` only | the same list forbids `input_dft` itself (`src/dft/build_cellsym_pilot.py:318`); `runs/s0/a_beef/README.md:107` records that as a DEVIATION for the gate. Every S5 deck carries the same deviation and docs/74 does not carry it forward. |
| C4 | `:16` cites the docs/45 S5 row at `:81`; `:152` strikes *"gated on S0(a)"* from docs/45 `:81` | the S5 row is at docs/45 `:90` as of 2026-09-05 (nine lines were added above it in commit `a8c3218`); `:33` and `:55` still hold. |
| C5 | `:324` *"59,761.1 SU"* | 59,473.5 SU on 2026-09-05 (`mybalance`). Drift, not error. |
| C6 | `:357` *"banked and have been since 2026-08-21"* | `slab__beefcalc.out:2` 21Aug2026 11:44; `slab__beefhub.out:2` **22Aug2026** 00:43 (ledger `:77`). |
| C7 | `:282-283` *"fixed PBE+U tier_v3"* geometries for the base set | none of the twelve Ru/Ir/Ti source decks carries a HUBBARD card (docs/54 `:86-88`; verified by the builder) — the base-set geometries are PBE, which `:283-286` itself says. Wording only. |
| C8 | `:291-292` *"One H₂ and one H₂O are reused across metals (identical md5 per species)"* | true (§4), with a fact docs/74 does not record: all nine copies, and their outputs, are CRLF. |
| C9 | `:13` *"Today is 2026-09-03 — 15 days"* | 13 days on 2026-09-05. |

No line of docs/74's thresholds is contradicted by a banked number; C1–C9 are provenance, wording and
staleness. C2 is the one that changes an action: whether A10-G's *"No compute is owed"* is written as
proposed depends on whether the entrant accepts §0.1 as capability evidence for the production binary.

---

## 8. Files

- `src/dft/build_s5.py` — the builder (`--check` verifies without writing).
- `runs/s5/Ru/*.in`, `runs/s5/Ir/*.in`, `runs/s5/Ti/*.in` (4 each), `runs/s5/gas/H2__beef.in`,
  `runs/s5/gas/H2O__beef.in` — the 14 decks.
- `runs/s5/m_s5.txt` — the manifest: NOT LICENSED notice (`:5-11`), `# SUBMIT WITH EXCLUDE=` (`:13`,
  the list of `runs/a0/m_pproj6.txt:15` and `runs/a0/m_pproj_cell.txt:26`; docs/66 `:106-107` adds
  a120 and a200 at submit time), md5s (`:30-87`), every differing line (`:89-391`), rows (`:393-406`).
- This sheet.

Nothing was committed, staged, mirrored to Anvil, or submitted.
