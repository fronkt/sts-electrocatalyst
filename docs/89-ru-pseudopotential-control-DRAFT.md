# RU-PP — the Ru second-pseudopotential control, as an anchor-pair comparability control

**Status: DRAFT — a proposal; nothing here is registered.** Built 2026-09-05 on the entrant's
instruction to build (not license, not submit) the "12-SCF Ru GBRV control at the three Ru
anchors" offered at docs/70:291-292 and carried as an open decision at docs/45:3173-3181. Every
threshold below is marked **Proposed** and carries a blank entrant slot of the form
`[RU-PP <id> 2026-09-__: ____]`. Until those slots are filled in a dated line, the manifest
carries a `NOT LICENSED` notice and `anvil/47_submit_a0.sh` refuses it (anvil/47_submit_a0.sh:55-60;
docs/66:98-104).

## 0. What exists in the tree as of this draft

| object | path | state |
|---|---|---|
| builder | `src/dft/build_ru_pp.py` | deterministic; two consecutive builds byte-identical over all 13 emitted files; `--check` verifies without writing |
| decks | `runs/a0/ru_pp/Ru/<state>__<u>_gbrv.in`, 12 files | each differs from `runs/a0/main/Ru/<state>__<u>.in` in exactly 2 lines (§5) |
| manifest | `runs/a0/m_ru_pp.txt` | `NOT LICENSED FOR SUBMISSION` notice (:11); `# SUBMIT WITH EXCLUDE=a024,a049,a050,a088,a196,a220,a223,a171,a120,a200` (:20, inherited from `runs/a0/m_eproj_np128.txt:20`); per-deck md5 beside its source deck's md5 (:26-37); 12 runnable rows at nk = 4 (:39-50) |
| pseudopotential record | `runs/a0/ru_pp/PSEUDO_PROVENANCE.md` | source URL, size 680598 bytes, md5 `7158a806dd851261a58e6920c40ebe78`, header facts, staging |
| staged file | `$PROJECT/pseudo/ru_pbe_v1.2.uspp.F.UPF` on Anvil | md5 `7158a806dd851261a58e6920c40ebe78` both ends; no row yet in `anvil/pseudo_md5_preflight_2026-08-23.md` |
| deck directory on Anvil | `$PROJECT/sts/runs/a0/ru_pp/Ru/` | created, empty |
| submitted | — | **nothing.** No sbatch was run. |

## 1. What the control measures, and what it does not

The A0 roster is on three pseudopotential families: ultrasoft GBRV for Cr, Mn, Ti, Ir; PAW for
Fe; norm-conserving ONCV for Ru alone (docs/45:35; docs/70:283-286). The A6.3 headline,
η(Ir) − η(Ru) = +0.464 V at U = 9 (docs/58:91), is therefore a cross-family comparison, and
the A7.3 verdict turns on the one row whose family is unreplicated: Ru sits under the
registered 0.100 V floor (docs/43:1368-1371) by 7.8 meV as-built and 4.3 meV equalised
(docs/45:3156-3157).

**Measured by this control.** The same twelve fixed-geometry SCFs — {slab, s0_O, s0_OH, s0_OOH}
at three U rungs — with the Ru pseudopotential swapped from `Ru_ONCV_PBE-1.0.oncvpsp.upf` to
GBRV `ru_pbe_v1.2.uspp.F.UPF`, the family Ir already runs on (`Ir_pbe_v1.2.uspp.F.UPF`,
anvil/pseudo_md5_preflight_2026-08-23.md:18). Two readings come out of it:

1. **A7.3's Ru quantity under a second family** — span(c_M)/2 at the fixed endpoints U = 0 and
   U = 9 (§3), against the floor and against the banked ONCV number.
2. **Anchor-pair comparability** — η(Ru) at the three rungs under GBRV against the banked ONCV
   η(Ru) and against the banked GBRV η(Ir), so that the Ir–Ru pair is read on ONE family for
   the first time.

**Not measured, not claimed.** It is not a new error class (docs/70:291-292; docs/45:35 "not a
new error class"); it does not replace any banked row (A8.8, docs/43:1759-1761: a re-run "is a
new measurement reported alongside … never a silent overwrite"); it does not re-run the cutoff
or k-mesh legs (docs/70:293-296); and it does not touch A7.3's count. **Whatever this control
shows, A7.3 stays NOT MET at 3 of 6 as banked (docs/43:2029; docs/45:3162-3163) and A6.3
stays INVERTED (docs/58:93). This licenses no rescue.**

## 2. The three Ru anchors — the reading built, with a slot to change it

docs/70:291 and docs/45:3174 say "the three Ru anchors" and list none. The word "anchor"
attaches to Ru in the tree in three senses, and each names one U rung:

| rung | token | U (eV) | why it is an anchor | evidence |
|---|---|---|---|---|
| production | `u000` | 0.00 | the registered production convention for Ru and Ir is U = 0; the fixed lower endpoint of A7.3's quantity; the U at which the 3d results are reported against the Ru/Ir "reference anchors" | docs/43:1758; docs/43:1368; `src/dft/a0main_readout.py:95` (`production_u=0.0`); docs/58:18-19 |
| Xu | `u673` | 6.73 | the Xu 2015 declared anchor point for Ru, PROJECTOR-MISMATCHED, whose banked row corroborates Xu's ordering | `runs/a0/m_a0main.txt:19`, `:50`; `src/dft/a0main_readout.py:95` (`anchor=6.73`); docs/58:47-50; docs/58:112-114 |
| U_max | `u900` | 9.00 | the fixed upper endpoint of A7.3's quantity; the single rung that carries A6.3's INVERTED verdict outright | docs/43:1368; docs/58:91, :97-100 |

So the arm is 3 rungs × 4 CHE states = 12 SCFs, sources `runs/a0/main/Ru/{slab,s0_O,s0_OH,s0_OOH}__{u000,u673,u900}.in`
(manifest rows `runs/a0/m_a0main.txt:129-160`), all twelve banked with `JOB DONE`, no
`convergence NOT achieved`, and each printing the staged ONCV file's md5
`be037bb81c227cfb9b1461a9f099f4bd` (checked by the builder, `src/dft/build_ru_pp.py`
`source_is_banked()`).

The alternative third rung is U = 7.50, the P-PROJ-6 rung where a Ru ortho-atomic leg already
exists under ONCV (`runs/a0/pproj6/Ru/*__u750_ortho.in`); it would open a pseudopotential ×
projector reading but only with four more GBRV ortho decks, which this arm does not build.
Changing `RUNGS` in the builder rebuilds the arm deterministically.

> **Proposed:** the three anchors are U = 0.00, 6.73, 9.00 as tabulated.
> `[RU-PP-1 2026-09-__: ____]`

## 3. The quantity, and the code path that scores it

A7.3's registered quantity is "span(c_M)/2 in volts, at FIXED endpoints U = 0 and U = U_max —
never max-minus-min over a grid" with c_M = ΔG_OOH − ΔG_OH (docs/43:1368-1369). The scorer
is `src/dft/a0main_readout.py:915-956`: it takes the U = 0 and U = 9 rows, forms
`c_lo = dG_OOH − dG_OH`, `c_hi` likewise, and `half = abs(c_lo − c_hi) / 2` (:937-939), with
`A73_FLOOR = 0.10` (:923). Each ΔG comes from `hea_oer.referencing.delta_G(E_slab, E_adslab,
species, E_H2O, E_H2)` (`src/hea_oer/referencing.py:30-33`; called at `a0main_readout.py:429`)
with the gas references read from `runs/Ru_anchor/H2O.out` and `H2.out` (`a0main_readout.py:240-241`).

Two consequences for the control, both read off that code:

- **The gas references, the slab energy and the ZPE/TS constants cancel in the span.** The
  spin census proves the same thing as its CEN-k gate: c_M(U) − (E_OOH − E_OH) is one constant
  over all banked endpoint rows (`src/dft/a0spin_census.py:812-813`, docstring :157). So A7.3's
  Ru quantity under GBRV is decided by **four** of the twelve decks — `s0_OH` and `s0_OOH` at
  `u000` and `u900` — and needs no new gas-phase run (H₂ and H₂O contain no Ru). The other eight
  decks give η(U) at the three rungs for §6.2.
- **The banked readout cannot score the control as-is.** `a0main_readout.py` hard-codes
  `runs/a0/main/<metal>` (:339, :255) and writes `docs/figs/a0main_readout.json`. Scoring the
  control means a sibling readout that points `delta_G` and the :937-939 arithmetic at
  `runs/a0/ru_pp/Ru/*_gbrv.out` and writes its own JSON under `docs/figs/`, never into the
  banked file. That sibling is **not written here**; it is pre-stated as part of licensing
  (§10), so the arithmetic cannot be chosen after the outputs exist.

The comparator is the **as-built** Ru row, `docs/figs/a0main_readout.json`
`a7_3.per_metal.Ru`: `c_M_lo` 3.1801 eV, `c_M_hi` 2.9956 eV, `span_over_2_V` 0.09225,
`delta_to_floor_eV` 0.0155, `pls_lo` 3, `pls_hi` 2. The equalised value 0.09574 V
(`tasks/review/a7_3_spin_census_2026-09-02_FINAL.json`, `a7_3_spin.per_metal.Ru.equalised.span_over_2_V`)
is quoted in docs/45:35 and :3156-3157 as the 4.3 meV margin, but the same artifact flags that
row `REVIEW-REQUIRED — endpoint winners differ in seed` (winner seeds 0.1 at U = 0, 0.0 at U = 9),
and docs/43:2817-2818 rules Ru's equalised span BRANCH-CONDITIONAL and "not scoreable into a
span" (docs/43:2632: "With Ru and Ir unscoreable"). The control therefore compares against the
scoreable as-built number and its 7.8 meV margin; the 4.3 meV figure is reported beside it,
never as the comparator.

> **Proposed:** comparator = as-built `span_over_2_V` 0.09225 V, margin 7.8 meV; the equalised
> 0.09574 V / 4.3 meV is quoted alongside, not compared against.
> `[RU-PP-2 2026-09-__: ____]`

## 4. The pseudopotential

Full record in `runs/a0/ru_pp/PSEUDO_PROVENANCE.md`. In one line: GBRV v1.2 PBE ultrasoft
`ru_pbe_v1.2.uspp.F.UPF` from `https://www.physics.rutgers.edu/gbrv/`, downloaded 2026-09-05,
680598 bytes, md5 `7158a806dd851261a58e6920c40ebe78` locally and on Anvil; Z valence 16 — the
same 16 electrons per Ru as the ONCV file (`runs/a0/main/Ru/slab__u000.out`: "number of
electrons = 168.00" for 6 Ru + 12 O) — with a 4D pseudo-wavefunction, so the `U Ru-4d` HUBBARD
card resolves without edit. Before the download, `find $PROJECT -iname '*ru*.upf'` on Anvil and
a search of this checkout and `C:\Users\frank` found no GBRV Ru file anywhere.

## 5. Differences from the source decks — two lines, and the cutoff disclosure

Each control deck differs from its source in exactly these two lines (diffed at build time;
the builder dies on any third difference; `diff` on all twelve reproduces this):

```
prefix = '<state>__<u>'                    ->  prefix = '<state>__<u>_gbrv'
Ru  101.070  Ru_ONCV_PBE-1.0.oncvpsp.upf   ->  Ru  101.070  ru_pbe_v1.2.uspp.F.UPF
```

**The cutoff difference the brief anticipated does not exist at the deck level, and that is
itself the disclosure.** The ONCV Ru decks run at `ecutwfc = 80.0` / `ecutrho = 640.0`
(`runs/a0/main/Ru/slab__u000.in:14-15`), and so does every GBRV metal in the tree
(`runs/a0/main/Ir/s0_OH__u000.in:14-15`, `runs/a0/main/Cr/slab__u000.in:14-15`,
`runs/a0/main/Ti/slab__u000.in:14-15`): 80/640 is the frozen protocol, dual 8, which docs/45:392-393
records as "8x, correct for ultrasoft". The control inherits it unchanged, so the pair is a
single-variable change. What must be said with it:

- The 80/640 lock was measured on bulk CrO₂ with the Cr GBRV ultrasoft and O PAW files
  (docs/23:16, :42-44, :71-73), and gate (i) laddered Ti/Sn (docs/43:1392). **No cutoff ladder
  exists in the tree for Ru under either pseudopotential.** The control is exactly as laddered
  as its source — no more, no less — and docs/70:293-296 instructs that the cutoff and k-mesh
  legs are not to be re-run. This draft follows that instruction and records that, for Ru,
  "already answered" means "answered on CrO₂ and Ti/Sn under the same protocol".
- The GBRV file records no suggested cutoff (header `0.00000 0.00000`); the repo's own reference
  to GBRV usage elsewhere is Xu's 40/500 Ry (docs/43:1894), so 80/640 is above the family's
  usual operating point, not below it.
- The FFT grids are set by `ecutrho`, unchanged; an ultrasoft file adds augmentation work the
  norm-conserving file does not have, so wall time is expected to differ from the source rows
  (§8) without any input change.

## 6. Pre-stated outcome bands — Proposed, every one with a blank slot

All bands are read on the control's own outputs against banked numbers; none moves a banked
verdict (§7). "Δ" is control minus banked ONCV.

### 6.1 Primary — A7.3's Ru quantity under GBRV

Let Q = span(c_M)/2 from the four GBRV decks (§3), and Δ_Q = Q − 0.09225 V.

| band | condition (Proposed) | consequence for how A7.3's Ru line is quoted |
|---|---|---|
| **CONFIRMS-COMPARABILITY** | Q < 0.100 V **and** \|Δ_Q\| ≤ 7.8 meV (a shift smaller than the as-built margin could not have crossed the floor in either direction) | the Ru line gains "replicated under GBRV ultrasoft within \|Δ_Q\| meV"; the PP-singleton caveat that docs/45:3169-3171 attaches to the 4.3 meV margin is **discharged for this line**; the family census sentence (docs/45:3166-3168) stays for A6.3 unless §6.2 also lands in its top band. Count unchanged: 3 of 6 |
| **MIDDLE** | Q < 0.100 V **and** \|Δ_Q\| > 7.8 meV (either direction) | Ru is under the floor on both families, but the margin is not PP-robust: the line quotes both numbers and never the 7.8 / 4.3 meV margin bare; the PP caveat stays. Count unchanged: 3 of 6 |
| **PP-SENSITIVE** | Q ≥ 0.100 V | A7.3 stays **NOT MET at 3 of 6** — the registered pseudopotential is the ONCV file, and a rung or file chosen after seeing a result cannot replace a banked row (docs/43:1759-1761; docs/43:2029). The Ru line is quoted as **PP-CONDITIONAL** wherever the margin appears, with Q beside it; the docs/45:3159-3160 sentence "the single metal that could flip the headline is the single metal whose family is unreplicated" is replaced by "…crosses the floor under GBRV; the banked verdict stands on the registered pseudopotential" |

> `[RU-PP-3 2026-09-__: ____]` (the three bands above, or the entrant's own)

### 6.2 Secondary — the anchor pair at the three rungs

Banked ONCV η(Ru): 0.787 V at U = 0, 0.413 V at U = 6.73, 0.290 V at U = 9; banked GBRV η(Ir):
0.781 V at U = 0, 0.754 V at U = 9, 0.637 V at its Xu anchor U = 5.91 (docs/58:85, :91, :112-113).
Error-class widths used as band edges, all measured: the 1×1 cell/coverage class 0.11–0.36 eV
and the NM-vs-AFM class 0.033–0.064 eV (docs/58:98-99); A5.1(b)'s 0.20 eV distinguishability
floor (docs/58:102-103).

| rung | statistic | Proposed bands | consequence |
|---|---|---|---|
| U = 9 | m₉ = 0.754 − η_Ru,GBRV(9); banked +0.464 V | m₉ > 0.36 V / 0.20 ≤ m₉ ≤ 0.36 V / m₉ < 0.20 V or sign change | top: A6.3's carrier may be quoted as "clears every error class this campaign measured, on a single pseudopotential family for the Ir–Ru pair" (the narrowed form at docs/45:3166-3168 is then complete rather than open); middle: INVERTED but inside the cell class — the narrowed qualifier stays exactly as written; bottom: the carrier is **PP-CONDITIONAL**; A6.3 stays INVERTED as banked and every quotation of +0.464 V carries the flag |
| U = 0 | \|η_Ru,GBRV(0) − 0.787\| | ≤ 0.20 V / > 0.20 V | the production-U Ru anchor is / is not comparable across families at the registered distinguishability floor; in the second case every 3d-vs-Ru sentence at production U carries the flag |
| U = 6.73 | sign of 0.637 − η_Ru,GBRV(6.73); banked +0.224 V | same sign / opposite sign | the Xu corroboration sentence (docs/58:112-114) is PP-robust / is struck and replaced by the measured sign |

> `[RU-PP-4 2026-09-__: ____]` (U = 9 bands) `[RU-PP-5 2026-09-__: ____]` (U = 0 band)
> `[RU-PP-6 2026-09-__: ____]` (U = 6.73 band)

### 6.3 Diagnostic only, no band

- Potential-limiting step at the endpoints: banked pls 3 at U = 0 and 2 at U = 9
  (`docs/figs/a0main_readout.json` `a7_3.per_metal.Ru.pls_lo/pls_hi`); the Ru A7.2 flip bracket
  [7.5, 9.0] (docs/58:117) is not resolvable from three rungs and is not re-scored.
- Löwdin populations from the inline `projwfc.x` (anvil/46_a0.slurm:97-99) are **not
  comparable** across the pair: the ONCV file projects onto four Ru manifolds (s, p, s, d —
  `runs/a0/pproj6/Ru/*.pdos_atm#1(Ru)_wfc#1(s)` … `_wfc#4(d)`), the GBRV file carries five
  (4S, 4P, 4D, 5S, 5P; `runs/a0/ru_pp/PSEUDO_PROVENANCE.md`). They are banked, not compared.

## 7. What this licenses

Nothing. In the registration's own vocabulary: A7.3 stays **NOT MET at 3 of 6** as banked and
scored (docs/43:2029; docs/45:3162-3163), A6.3 stays **INVERTED** (docs/58:93), no banked A0 row
is replaced (docs/43:1759-1761), and the only power of any band in §6 is to select which caveat
sentence travels with the Ru line. A PP-SENSITIVE outcome is a disclosure of conditionality, not
a fourth metal over the floor.

## 8. Cost — measured, then the board's figures beside it

1 SU = 1 core-hour at the launch shape (anvil/47_submit_a0.sh:108, "$NP SU/h each", NP = 128).

| basis | measurement | 12-SCF figure |
|---|---|---|
| the twelve ONCV source decks themselves, pw.x `WALL` lines, 128 cores | 920.29 s total (`runs/a0/main/Ru/{slab,s0_O,s0_OH,s0_OOH}__{u000,u673,u900}.out`; slab u000 173.98 s is the longest, s0_OOH u000 49.97 s the shortest) | **32.7 core-h**, pw.x only, no projwfc, no Slurm overhead |
| the banked Ru row of P-PROJ-6 at u750 (ONCV, ortho-atomic), pw.x + projwfc `WALL`, 128 cores | 442.81 s + 28.45 s for 4 SCFs (`runs/a0/pproj6/Ru/*__u750_ortho.out`, `*.projwfc.out`) = 16.76 core-h | **50.3 core-h** (×3 rungs), projwfc included |
| the measured a0 cost model, six-metal mean | P-PROJ-6: 24 decks, 1.394 h WALL @128 = 178.4 core-h (tasks/todo.md:1849; docs/43:4058-4059), i.e. 7.43 core-h per SCF including the nspin = 2 metals | **89 core-h** as an upper bound |
| board figures | ~30–60 SU (docs/70:291-292; docs/45:35; tasks/todo.md:1873) and ~50–100 SU (docs/78:117) | — |

The ultrasoft-vs-norm-conserving wall difference at identical cutoffs is **not measured** on
this system; the honest planning band is 33–90 core-h, with 50 the central figure. The
submitter's printed worst case at the 48 h walltime cap is 12 × 128 × 48 SU and is a cap, not
a forecast.

> **Proposed:** planning figure 50 core-h, ceiling 90. `[RU-PP-7 2026-09-__: ____]`

## 9. Confounds, with the values read from the decks

| confound | value in all 12 decks | what it means for the reading |
|---|---|---|
| spin convention | no `nspin` line (nspin = 1); asserted by the builder | inherited; the control cannot inform the nspin = 2 / nspin = 1 partition that A7.3's split is confounded with (docs/43:2777-2778), and does not touch the RuO₂ magnetic-ground-state correction docs/70:95-110 asks for |
| k-mesh | `8 4 1 0 0 0` (`runs/a0/main/Ru/slab__u000.in:57-58`) | inherited; not re-laddered (docs/70:293-296) |
| cutoffs | 80 / 640 Ry (:14-15) | inherited; §5 |
| smearing, mixing, threshold | `mv`, `degauss = 0.01`, `local-TF`, `mixing_beta = 0.3`, `conv_thr = 1.0d-6`, `electron_maxstep = 200` (:16-25) | inherited; a control deck that hits `convergence NOT achieved` is UNSCORED for every band that needs it — no repair ladder is registered for this arm |
| geometry | fixed, the ONCV-relaxed `runs/Ru_anchor` geometry (docs/58:20-22: nothing in A0 is a relaxed result) | the GBRV control sits on an ONCV geometry; a PP-consistent relaxation is out of scope and is not what an anchor-pair comparability control asks |
| Hubbard manifold | `U Ru-4d` at 6.7300 / 9.0000, `HUBBARD (atomic)`; no card at u000 (asserted) | the U value is inherited nominally, but the atomic projector is the file's own 4D pseudo-wavefunction, which differs between the two files — "same U" is a statement about the input, not about the projected occupation |
| projector | atomic in all 12 | the PP × projector cross is **not** covered (§2) |
| Löwdin basis | 4 vs 5 manifolds | §6.3 |
| the 6.73 rung | PROJECTOR-MISMATCHED (docs/58:47-50) | reads only as the Xu corroboration in §6.2, never as an A7.3 endpoint |

## 10. Ordering, and the path from this draft to a licensed arm

The decks and manifest exist and are md5-manifested **before** any threshold above is adopted —
the P-PROJ-6 ordering (built at c2e9a18, licensed at 8aba0ae; `src/dft/build_pproj6.py` docstring)
— so the objects submitted are provably the objects built. What licensing needs, in order:

1. The entrant's dated line adopting or replacing slots RU-PP-1 … RU-PP-7 (a docs/43 addendum
   in the form of A12/A13; nothing in this file is that line).
2. A dated row for `ru_pbe_v1.2.uspp.F.UPF` (md5 `7158a806dd851261a58e6920c40ebe78`, both
   ends) in the pseudo md5 preflight record that anvil/47_submit_a0.sh:41-45 requires beside it.
3. The sibling readout of §3, written and committed before submission.
4. The lead session lifts the `NOT LICENSED` notice in `runs/a0/m_ru_pp.txt` and submits with
   `EXCLUDE` containing every node in the header (anvil/47_submit_a0.sh:62-80).
5. Scored before Oct 15 or marked WITHDRAWN-UNSCORED with its date (A7.7, docs/43:1435-1440).

## 11. Where the tree does not match the notes this draft rests on

- **"The three Ru anchors" are unlisted.** docs/70:291 and docs/45:3174 use the phrase; neither
  names the rungs. §2 is a reading with evidence, not a quotation, and carries slot RU-PP-1.
- **The 4.3 meV margin is quoted from a row the registration calls unscoreable.** docs/45:35 and
  :3156-3157 give Ru's margin as 4.3 meV equalised; docs/43:2817-2818 and :2632 rule Ru's
  equalised span BRANCH-CONDITIONAL and not scoreable, and the artifact itself flags the row
  (`tasks/review/a7_3_spin_census_2026-09-02_FINAL.json`, `branch_guard.flag`). The scoreable
  margin is the as-built 7.8 meV. §3 uses it and quotes 4.3 beside it.
- **"Cutoff and k-mesh legs already answered" is CrO₂- and Ti/Sn-specific.** docs/70:293-296
  and docs/45:35 cite docs/23 §4 and gate (i); docs/23:16, :42-44 show the ladder was Cr GBRV +
  O PAW on bulk CrO₂, and docs/43:1392 shows gate (i) was Ti/Sn. No Ru ladder exists under
  either pseudopotential. Not re-run here (§5), but stated.
- **Cost figures disagree with each other and with the measurement.** docs/70:291-292 and
  docs/45:35 say ~30–60 SU; docs/78:117 says ~50–100 SU; tasks/todo.md:1873 notes the
  discrepancy. The measured Ru rows give 32.7 (pw.x only) to 50.3 (with projwfc) core-h (§8).
- **Pseudo count.** anvil/pseudo_md5_preflight_2026-08-23.md:23 says "13 files in
  `$PROJECT/pseudo`"; the directory held 12 (the table's own 12 rows) before this staging and
  13 after it.
- **docs/70:285-286 "docs/45 §A has no pseudopotential row" is now closed by docs/45 §B row 10
  (docs/45:35)** — a later closure, not a contradiction; recorded so the two are read together.

## 12. Entrant slots, collected

| id | decides | draft proposal |
|---|---|---|
| RU-PP-1 | the three rungs | U = 0.00, 6.73, 9.00 (§2) |
| RU-PP-2 | the comparator for A7.3's Ru quantity | as-built 0.09225 V, margin 7.8 meV (§3) |
| RU-PP-3 | the primary bands | CONFIRMS-COMPARABILITY / MIDDLE / PP-SENSITIVE at ±7.8 meV and the 0.100 V floor (§6.1) |
| RU-PP-4 | the U = 9 anchor-pair bands | 0.36 V / 0.20 V edges (§6.2) |
| RU-PP-5 | the U = 0 anchor band | 0.20 V (§6.2) |
| RU-PP-6 | the U = 6.73 corroboration band | sign of 0.637 − η_Ru,GBRV(6.73) (§6.2) |
| RU-PP-7 | the cost figure | 50 core-h planning, 90 ceiling (§8) |

Nothing above is registered until each slot carries a date and a decision.
