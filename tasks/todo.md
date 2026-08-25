# STS 2027 — TODO

## 2026-08-23 — current plan (the program board is docs/45 §E; this block is the day's checklist)

Compute: Purdue Anvil (ACCESS CHE260157), ~1,085 of 100,000 SU used; Vast box gone.

- [x] Block 1C Cr Hessian, both δ — banked, docs/49 (verdict label = Frank's σ_F decision, docs/47 A8.7)
- [x] σ_F estimator block split (docs/49 §4b, `hessian_asym_blocks.py`); lessons.md entry
- [x] Triage of the 51 staged decks without outputs — docs/51 (stale dupes moved aside; hp nosym / Co *OOH / Cu superseded; gate-(h) relaxations HOLD on A8)
- [x] S0 gate (i) SnO₂ arm — job 20094699 **PASS** 1.188 meV/atom (admission PENDING A7.5 Sep 1); TiO₂ record corrected to 1.092
- [x] A7.5 Mom-2014 cus-site condition — **CONFIRMED 2026-08-23** (docs/53; 2 adversarial refuters, 14/14 quote check); SI PDF filed; admission = Frank's declaration (no open dependency)
- [x] LIT-2: Cr outputs banked; Cr `__g1` children launched (20094768); Ru `cov_2OH` re-run as fresh realisation (20094762)
- [x] A8 draft complete incl. A8.7 instrument question + P-SYMCOV both-outcomes (docs/47) — **Frank re-authors thresholds + deposits by Aug 24**
- [x] A9 DRAFTED (docs/50) + 2026-08-15 sampling artefacts filed — **Frank: 15 listed decisions, then deposit (overdue since Aug 22)**
- [x] `src/dft/lit2_readout.py` (A5.2 scorer) built + reviewed; **LIT-2 READOUT COMPLETE: RuO2 benchmark FAIL** (ordering TRUE, both transitions ~0.45 V below Qiu) → Cr = vacuum-CHE-only; Cr flag OFF. Banked 9fd1771
- [x] 20094762 / 20094768 outputs mirrored + banked (md5 both ends)
- [ ] Gate (h) four RuO₂ 2×1v AFM relaxations (+ 4 `__g1`): build AFTER A8 deposit (needs a committed builder; A8.1/A8.5 collision to settle)
- [ ] S3 decks: build after A8 deposit, launch Aug 26 (docs/45 §E)
- [ ] S1 silentgate core: **Frank writes**; CI + in-house controls may be built now (A9.6)
- [ ] `--bind-to core` driver default — decision flagged in docs/48 (free 18 %, number-neutral)


## HEADLINE WITHDRAWN (2026-08-08) — read docs/41 §6c first

**"Earth-abundant rutiles (Cr, Co) outperform RuO₂/IrO₂ in this tier" is withdrawn.**
Pre-registered test P7 (docs/41 §5) triggered: η(Cr) moves **1.122 V** across
U ∈ {0, 0.5, 1, 1.35}× at fixed geometry, against a 0.15 V falsification threshold. The
trigger holds on GATE-1-clean states alone (0.313 V), so it does not depend on any
drifted number. Production U happens to place Cr's descriptor at 1.560 eV — essentially
on Man's 1.60 eV volcano apex — so η(Cr) = 0.330 V was a consequence of the U value, not
a prediction the method made. §5 says withdraw, not soften.

Two independent problems found the same day, both in docs/41 §6c:
- **Co never had an `s0_OOH` calculation at all** — the other headline metal's chain was
  a bounded inference, not a measurement.
- **Cu has essentially no usable data** (slab and `s0_O` missing, `s0_OH`/`s0_OOH`
  poisoned). Only Cr, Fe, Mn and the two anchors have all four states converged.
- **Cr's `*OOH` relaxation sat in a metastable magnetic state 175 meV high** (totmag
  11.80 vs 11.00 from a fresh SCF at identical coordinates). η(Cr) itself is unaffected
  (its limiting step is `pls = 2`, which never touches `*OOH`), but 24 tier states have
  never been checked for this and it took one probe to find one case.

Good news from the same batch: the **symmetry trap is real and fixes Ir** — the off-plane
`*OOH` restart pulls Ir's scaling from 3.652 (outside the 3.2 ± 0.2 universal band) to
**3.361 (inside)**, and η(Ir) from 0.781 → **0.490 V**, into the published IrO₂ range.
Ru's trap is only 82 meV and leaves its descriptor untouched, so the two anchors still
fail for different reasons. **P3 (vacuum) is now refuted by direct DFT** (Ru −0.0005 V,
Ir +0.0002 V at 32 Å), not merely by the MLIP argument.

### Running now (instance 47025043, 166.113.52.39:43442, $0.108/hr)
35 SCFs launched 2026-08-08, NP=4 NCONC=5, manifest `/workspace/m_followup.txt`:
- **Magnetic-metastability audit** (Fe 4, Mn 4, Ni 3) — GATE 1 *is* the test: a fresh
  `base` SCF vs the relaxation's own final energy. This is the highest-value item.
- **Co U-ladder** (12) — P7's other half; its `base` doubles as Co's audit.
- **P2 dipole** (8) — re-run with `tefield`/`dipfield` moved to `&CONTROL`.
- **P9 RPBE gas refs** (4) — re-run at `-nk 1`; unblocks 8 RPBE slabs already done.

Poll: `HOST=166.113.52.39 PORT=43442 bash src/dft/collect_probes.sh status`, then
`pull` and `score`. **Destroy when done: `vastai destroy instance 47025043`.**

## Status (2026-07-24)
**FRAMING: HEA-OER electrocatalyst campaign REVIVED; thermal lane DROPPED** (owner
decision 2026-07-23). Revival plan + literature synthesis in
[`docs/28`](../docs/28-electrocatalyst-revival-plan.md). Thermal-era todo archived at
[`todo-archive-2026-07-24-pre-catalysis-revival.md`](todo-archive-2026-07-24-pre-catalysis-revival.md);
thermal artifacts (docs/24, 27, runs_cpa/) preserved as-is. Catalysis trackers
`plan-catalysis-hea.md` / `plan-her-discovery.md` unchanged.

Key corrections to the parked-project record (docs/28 §1–2):
- The endmember DFT queue DID complete (2026-07-13, docs/26) — 4/6 converged.
- The "UMA cannot rank rutile OER" verdict is CONFOUNDED: parity used the `oc20`
  (RPBE-metals) task head; the correct `oc22` (PBE+U oxides) head was never tested.
- 5 of 6 rutile endmembers are not physically realizable electrodes — a stability
  gate (Pourbaix ΔG_pbx) is required before any screening claim.

## Gate G-R0 (blocks all compute — Frank's call)
- [ ] Approve/adjust the R0–R4 revival plan in docs/28 §7 (incl. vast.ai spend)
- [ ] Revoke old HF token (frankcai222), mint fresh one (needed for gated
      `facebook/UMA` checkpoint) — carried from docs/23 §9
- [ ] Decide branch strategy: catalysis revival off `main` vs continuing on
      `thermal-round0` (repo currently dirty on thermal-round0)

## R0 — Kill the artifact — DONE 2026-07-25 (docs/29); GATE NOT MET
- [x] Re-run UMA parity with `uma-s-1p2` (fairchem 2.21.0 doesn't register 1p2p1;
      1p2 is the on-plan oc22 carrier) + `oc22`/`oc20`/`oc25`; per-head CHE chain
- [x] Built RuO₂/IrO₂(110) in-distribution anchors (same builder, verified to 3e-9 Å)
- [x] GATE RESULT: **oc22 ρ = −0.80** (anti-correlated), oc20 ρ = 0.0, oc25 ρ = +0.2
      (QC-tainted), baseline +0.4 → "~0 → negative result is REAL". docs/28 §2
      confound hypothesis REFUTED; no out-of-box head ranks rutile OER. Anchors
      exonerate the pipeline (oc20/oc25 nail IrO₂ 0.52/0.57 V vs lit 0.56).

## QC AUDIT — DONE 2026-07-31 (docs/30, commit 1a3a77b, $0 spent)
- [x] Strict QC tooling (`src/dft/qe_qc.py`); `parse_qe_energy` can no longer
      return an energy from a run that failed SCF or never converged
- [x] **η(NiO₂) = 1.751 V RETRACTED** — `s0_O`/`s0_OH` both died on a failed SCF
      while printing JOB DONE, at 7× and 13× the force threshold, energy still
      falling 0.013/0.040 eV per step and accelerating. The `.in.restart` files
      prepared in docs/26 §4 were never run. docs/29 §4b "NiO₂ breaks *OOH/*OH
      scaling" withdrawn — the bias runs in exactly that direction.
- [x] R0 restated at n=3: oc22 goes −0.80 → **−1.00**. Verdict SURVIVES and
      sharpens; but n=3 has no power (a perfect ordering gives p=1/3), so the
      campaign is short of DATA POINTS, not of another task head.
- [x] Slab constraint float-tie fixed (the mid-plane layer was decided by
      rounding: 11 free atoms for Cr/Mn/Fe/Cu/Ru, 10 Ir, 8 Co, 7 Ni — Co and Ir
      split symmetry-equivalent atoms). Does not affect the R0 parity; does bias
      the cross-metal η ranking.
- [x] Ru/Ir anchors made reproducible from committed code (byte-exact for Ru),
      wired for `eta`, and patched ~4× cheaper (nspin=1 for the non-magnetic
      anchors; nosym on the clean slab only). CRLF trap closed for `*.in`.
- [x] 785-frame MLIP training set extracted + validated (`src/dft/qe_frames.py`);
      ASE's espresso-out reader fails on 33 of 44 archived slab outputs

## REFERENCE REPAIR — RUN AND CLOSED 2026-08-02 (docs/33 §5b, $2.64, instance destroyed)
- [x] Three structures that passed `qe_qc` were chemically wrong; all three re-run, all
      three superseded. **η(CrO₂) 1.726 → 0.491 V** (Cr–O 2.016 → 1.572 Å, −1.396 eV);
      Fe/Mn `*OOH` finally bound at 2.552/2.480 Å. η(Fe), η(Mn) unchanged (both pls=2).
- [x] MACE-MPA-0 had predicted all three: η(Cr) to **9 mV**, Fe–O to 0.013 Å, Mn–O to
      0.06 Å. **The MLIP was right and our DFT reference was wrong.**
- [x] `src/dft/adsorbate_qc.py` added (chemical validity, which `qe_qc` is blind to by
      construction). Two of its own thresholds were then falsified by the repair results
      and corrected — both pinned in `tests/test_adsorbate_qc.py`.
- [x] **2026-08-03: the repaired outputs had been written NEXT TO the reference**
      (`.out.shortbond` / `.out.bound`) so `dft_reference()` still returned the trapped Cr
      for a day. Files swapped, defective ones kept as `.out.trapped-*`/`.out.desorbed-*`,
      `tests/test_dft_reference.py` added to pin it. 59 tests pass.
- [x] Docs 29/30/32/33 corrected; pre-repair versions archived with provenance headers.
      **R0 headline changes shape**: oc22 goes ρ = −1.000 → **0.000** (n=5) / **+0.500**
      (n=3). "No out-of-box UMA head ranks rutile OER" SURVIVES (best is oc25 at +0.400,
      p = 0.52). "oc22 ranks them *backwards*" is WITHDRAWN — and a material part of that
      anti-correlation was our own trapped Cr. docs/29 §8.
- [ ] Cost overrun to note: $2.64 vs a $0.6–1.1 estimate. Magnetic 3d slabs with 32–36
      k-points run 10–12 h, not the 3–5 h projected off the non-magnetic anchors.

## R1 CAMPAIGN — RUN AND CLOSED 2026-08-01 (docs/32, $4.42, instance destroyed)
- [x] Ru/Ir DFT anchors, 8/8 jobs TRUSTWORTHY, geometries verified textbook.
      **η(RuO₂) = 0.787 V, η(IrO₂) = 0.781 V.**
- [x] **GATE NOT MET** (docs/30 §7): both η land inside 0.30–0.90 V (clauses 1–2
      PASS) but η(Ru) < η(Ir) **FAILS** — by 6 mV, which is a tie, not a
      mis-ordering. Absolute error +0.39 V (Ru) / +0.22 V (Ir) vs literature.
- [x] **The deliverable is the tier's measured resolution**: differential error
      between two similar rutiles ≈ 0.17 V, versus a true Ru–Ir gap of ~0.15 V.
      Supports **Cr > Fe > {Mn ≈ Ru ≈ Ir}** — three distinguishable levels over
      five materials. R0's negative result is untouched (ρ = −1.00 is far larger
      than any resolution question).
- [x] IrO₂ `*OOH`/`*OH` scaling = 3.652 eV (+0.45 outside band) while Ru = 3.180
      (textbook) — so not a pipeline systematic. H-bond explanation tested and
      REFUTED (both `*OH` near-identical, neither H-bonded). Unresolved, recorded
      both ways, η unaffected (`pls = 3` never touches ΔG_OH).
- [x] Ni rescue FAILED: `s0_O` stalled and was killed, `s0_OH` orphaned. Ni stays
      retracted, **n = 5**.
- [ ] ~~**Frank's call — Ni rescue round 2, ~$5–9?**~~ **SUPERSEDED 2026-08-03 — this is
      now the top-priority spend, re-costed at ~$4, and it beats the fine-tune.** See
      docs/32 §5 and docs/33 §6. Three changes:
      - **Price**: measured, not guessed — 4 concurrent magnetic-3d jobs ≈ $4 (from the
        repair run's 3 jobs / 12.1 h / $2.64), inside the $8.46 credit.
      - **Scope**: run Ni (`s0_O`, `s0_OH`) **and** Co (`s0_O`, `s0_OOH`) together. Both
        died on the same SCF-plateau pathology, so both need the two-stage `degauss`
        protocol and neither is safe alone; running both means one failure still gives
        n = 6, and success on both gives n = 7.
      - **Why it beats the $1.9 fine-tune**: at n = 5 *only* a perfect ordering reaches
        p < 0.05, and MACE's single error is the Ru/Ir pair our own DFT separates by
        6 mV — so the gate asks a model to reproduce an ordering the reference cannot
        resolve, and a perfect score would be indistinguishable from luck. At n = 6 the
        **free** model, keeping the error it already has, gives ρ = 0.943, p = 0.017.
- [x] **DONE 2026-08-03, $0 — predictions frozen in [docs/34](../docs/34-prereg-sixth-point.md).**
      Protocol validated on the five knowns from BUILDER geometries with zero DFT input:
      ρ(η) = **+0.900**, η MAE = **0.150 V**. Predictions: **Ni 1.200 V (outside the
      cluster — BUY)**, Co 0.883 V (inside, 9 mV from Mn), Cu 1.373 V (outside but needs
      4 jobs and has no working `slab.out`). All three pls = 2, descriptors 2.11–2.60.
- [x] **DONE 2026-08-03 — the constraint float-tie is 1–4 mV and does NOT matter.**
      Same metal, same geometries, mask swapped: Ni 1.200 → 1.196, Co 0.883 → 0.882,
      against a 0.17 V tier resolution. So Ni/Co **reuse their existing TRUSTWORTHY
      states — 2 jobs each, not 4** — and docs/30 §3's ranking concern is largely retired.
- [x] **LAUNCHED 2026-08-03 — instance 46726365 (Norway, 96 vCPU, $0.268/hr), 5 jobs.**
      Became 5 jobs not 4: `adsorbate_qc` found `Ni_slab/s0_OOH` **desorbed at 3.080 A**
      despite 39 converged ionic steps and a TRUSTWORTHY verdict — a fourth instance of
      the same defect. Every job starts from the MACE minimum, not the builder placement,
      because the builder's ~3.1 A `*OOH` has now failed on Mn, Fe AND Ni (and MACE says
      Co would follow: builder 2.983 A vs pulled-in 2.105 A at 0.427 eV lower).
      Two-stage SCF: `scf` at degauss 0.03 -> `relax` at production 0.01 with
      `startingpot='file'`. **Both metals that had never converged passed stage A**
      (Co 6134 s, Ni 6957 s) — the plateau that killed three prior attempts is beaten.
      All four pseudopotential MD5s verified identical to the archived runs.
      Infra cost of getting there: $0.044 on a broken box (3 new lessons in lessons.md).
- [x] **CLOSED 2026-08-04 — [docs/35](../docs/35-n7-campaign-result.md). GATE MET.**
      n=5 -> **n=7**. MACE-MPA-0, free and un-fine-tuned: rho=+0.857, exact p=**0.0238**.
      (n=6 with Ni alone: rho=+0.886, p=0.0333.) The binding constraint was n, exactly as
      docs/34 argued. **eta(Ni)=1.084 V, eta(Co)=0.544 V.**
      - Pre-registered test **1 hit / 1 miss**: Ni +0.116 V (within the 0.150 bar), Co
        **+0.339 V (2.3x out)** — and MACE's "Co is inside the cluster" call was wrong too.
      - Both `*OOH` jobs FAILED (Ni SCF diverged 3x; Co ran out of credit at 16 ionic).
        eta survives via `src/dft/eta_bounded.py`: dG3+dG4 = 4.92 - dG_O contains no
        dG_OOH, so eta is bounded from measured quantities. Co's tight high edge closed by
        its partial relax (a run stopped early sits ABOVE its minimum -> upper bound).
      - **Fourth desorbed `*OOH` found** (Ni, 3.080 A, TRUSTWORTHY by qe_qc, 39 ionic).
        Archived; it would have given dG4 = -0.282 eV.
      - **Spend $8.17 vs a $3.20 projection — 2.5x over.** docs/35 s6. The three jobs that
        mattered cost ~$4; the two `*OOH` jobs were worth $0 because the bound made them
        unnecessary. Deriving that bound BEFORE renting would have saved half the money. Not Cu. Rationale in docs/34 §4: no
      candidate lands in clear space (Ni is 0.063 V from Fe, Co 0.009 V from Mn), so each
      brings its own unresolvable pair — which is exactly why n = 7 beats n = 6. If all
      three unresolvable pairs swap: n=7 → ρ 0.893, p **0.0123** (clears comfortably);
      n=6 → ρ 0.886, p **0.0333** (clears, zero margin); n=5 → p 0.083 (fails, as today).
      Both metals need the two-stage `degauss` protocol; both died on the same SCF plateau,
      so running both is the hedge against one failing.

## R4-PREP — MELT-LIST REGENERATION (started 2026-08-05; potentiostat BOOKED)
The docs/15 melt set was ranked by **UMA rutile**, and R0 voided that ranking (no
out-of-box UMA head ranks rutile OER; best oc25 ρ=+0.400, p=0.52). The compositions
are still meltable objects, but "ML-predicted best" is not a supportable claim about
them. Regenerating the list is free (MACE + MP), needs no Vast credit, and must
happen before a melt slot is spent — a frozen prediction table built on a void
ranking would contaminate the campaign's central contribution.
- [x] **A. DONE 2026-08-05 (commit 10189d0).** Multi-start adsorbate placement.
      places at 1.85–1.90 Å above the slab's TOPMOST atoms; on rutile(110) those are
      the bridging-O rows, so the adsorbate lands 3.07–3.13 Å off the cus metal —
      the exact defect docs/34 §4b priced at $2.64 and four wrong structures. The
      HEA path (`add_oer_adsorbate_at`) inherits it verbatim. Port the proven
      remedy: builder start + rigid pull-in to M–O 1.70/2.10 Å, lowest energy wins.
      Measured on the HEA path: `*O` 3.080 Å, `*OH`/`*OOH` 3.130 Å off the cus metal
      — every adsorbate started **past the 3.00 Å desorption cut**. Remedy = builder
      start + rigid pull-ins to M–O 1.70/2.10 Å, lowest energy wins; winning bond
      length recorded so a desorbed "minimum" cannot enter a melt list silently.
      Both pull-in and builder starts win on different states, so all three are kept.
- [x] **B. DONE 2026-08-05 (commit 10189d0).** MACE-MPA-0 backend
      (`relax.make_mace_calculator`, `"mace"` in the registry), CPU, float64.
- [x] **B2. DONE 2026-08-05 (commit 294fb01).** Pool cus sites over 3 decorations.
      A 2×2 slab has only 4 cus sites and seed 0 puts *only* Co/Fe on them for
      Fe32Ni17Co34Mn18 — Ni and Mn (34 at.%) never appear at an active site. The
      2026-06 UMA sweep had the same weakness.
- [x] **E. DONE 2026-08-05.** Multi-element Pourbaix (`src/dft/pourbaix_multi.py`,
      9 tests). Metric = **soluble cation fraction at pH 14 / 1.53 V vs RHE**, which
      avoids inventing a ΔG_pbx for an HEA oxide MP does not hold. Quaternary hull
      reproduces docs/31 §4's per-element assignments exactly (Fe→Fe₂O₃(s),
      Co→CoOOH(s), Mn→MnO₄⁻, Ni→Ni(OH)₃⁻). **docs/15 melt set, soluble fraction:**
      FeCoNi 33.3% < Fe32Ni17Co34Mn18 34.0% < Cr19Co28Fe25Ni28 47.0% <
      Co20Ni20Cr20Mn20Cu20 60.0% < Cr6Fe33Ni27Mn34 67.0% < Mn19Fe12Ni35Co16Cr18 72.0%.
      Every candidate ≥33% soluble; Ni soluble in all, Cr soluble in all Cr-bearing.
      Concentration sensitivity checked: Ni stays Ni(OH)₃⁻ from 1e-8 to 1e-4 M and
      only passivates as NiO at 1e-2 M, so the **ordering is robust** across the
      dilute range but the absolute % is not a physical constant.
- [x] **C. DONE 2026-08-05 — GATE MET ([docs/36](../docs/36-screen-validation-and-stability-gate.md)).**
      Pipeline scored on its OWN slabs vs the n=7 DFT tier: **ρ = +0.8571, exact
      p = 0.0238, η MAE = 0.130 V** — 42 mV BETTER than docs/35's 0.172 V, which
      scored the same model on the DFT tier's own geometries. Letting the MLIP find
      its own minimum beats scoring it on someone else's. Worst point is **IrO₂
      (−0.254 V)**, which moved from +0.131 in docs/35 — a caveat on any "beats
      IrO₂" claim. Two rank errors, both on pairs the reference cannot resolve
      (Co/Ir, Mn/Ni; tier resolution ~0.17 V).
- [x] **D. DONE 2026-08-05 ([docs/37](../docs/37-hea-screen-result-and-melt-list.md)).**
      12 candidates on a Vast Tesla V100 (~$0.25, instance DESTROYED). **6 of 12 are
      chemically invalid** (desorbed states) — including one that would have ranked
      4th-best. Best site runs **0.44–0.60 V below the site mean** = the high-entropy
      hypothesis quantified, and the top candidate's winning site came from the THIRD
      decoration. **Bit-level CPU/GPU parity** (η identical to 4 dp). Original note: — `screen_mace.py screen`, 12 diverse
      single-phase candidates (3339/4000 passed the Hume-Rothery/Ω–δ filter),
      4 cus sites × 3 decorations, checkpointed per candidate to
      `results/r4_screen.json`. ~15–20 h on this CPU-only box; partial results
      ranked and usable throughout. A GPU box does it in <1 h for ~$1 —
      **Vast credit is $0.295**, so that is a top-up decision, not a technical one.
- [x] **E2. DONE** — stability joined onto the ranking (`pourbaix_multi.py gate`).
      **ρ(η, soluble) = −0.657, p = 0.175, n = 6** — activity and stability
      ANTI-correlate across the screen. Suggestive, NOT significant; must not be
      written up as established. Found + fixed a real bug doing it:
      `exact_two_sided_p` counted only the upper tail, correct solely for positive ρ.
      No published number changes (verified exhaustively at n = 5, 6, 7).
- [~] **F. BUILT, awaiting Frank's freeze decision** — `results/r4_melt_list.json`.
      Two stated limitations: **role collapse** (least-active candidate is also the
      most stable → no independent low-activity point) and **0.356 V predicted span
      against a 0.130 V screener MAE** — under 3 MAE of dynamic range. Remedy is
      ~$0.50 / ~3 h for 24–36 more candidates; cheap now, expensive after the melt.
      THEN: weigh sheet (docs/17) + dated Cr(VI) risk assessment BEFORE the first melt.
      Framing: activity ORDERS, stability GATES, and since every candidate is ≥33%
      soluble the list should deliberately SPAN the activity/stability tension rather
      than scalarize it away — that tension is the HEA thesis's subject (docs/31 §8).
      Must retain a predicted-poor anchor for correlation dynamic range (docs/15 §6).
      **UPDATE 2026-08-06 (commit eec7a75): a selector bug was hiding a free
      improvement.** `select()`'s "spread along the front by activity" used a stride
      of `len(interior)//k_interior`, which is `max(1, 3//2) == 1` — a contiguous
      PREFIX at the low-η end, the opposite of a spread. The shipped list was
      0.440 / 0.453 / 0.479 / 0.796: three picks inside 39 mV, then a 0.317 V gap,
      i.e. two activity levels wearing four labels. Fixed to evenly-spaced indices:
      **0.440 / 0.453 / 0.726 / 0.796** — identical span, identical cost, three
      resolvable levels, and it recovers Ni34Fe6Cu29Co31, a Pareto-front point that
      was being dropped. `results/r4_melt_list.json` is deliberately NOT regenerated;
      re-run `melt_list.py build --out results/r4_melt_list.json` at freeze time.
      This does not fix the role collapse or the span-vs-MAE problem, and the
      resolvability arithmetic is still the binding constraint: the min-over-12-sites
      descriptor carries sd 0.08–0.19 V, so the two lowest picks are ~0.05σ apart and
      even the widest pair is only ~1.7σ. Widening the pool remains the real remedy.

## R4-PREP ADDENDUM — the model comparison, put on one footing (2026-08-06, docs/38)
- [x] **G. MACE vs UMA was never a matched comparison** — and every unmatched axis
      (defective reference, n, start geometry, multi-start, dtype, mask) flattered
      MACE. Fixed by running it: `mace_uma_protocol.py` restores the original builder
      inputs and re-runs MACE single-start under UMA's exact docs/29 protocol;
      `parity_matched.py` scores every stored UMA head **and** that run against
      `eta_bounded.reference_tier()`. **MACE +0.857 / p 0.0238 / MAE 0.173 V vs UMA's
      best head (oc25) +0.357 / 0.4444 / 0.438 V.** Conclusion survives; the published
      MACE η reproduce to within 5 mV from raw builder geometry, so no protocol
      advantage was load-bearing. Artifact: `docs/figs/parity_matched.{json,png}`.
- [x] **H. Gate is NOT met at n = 5** — drop Ni and Co (bounded η; DFT restarts seeded
      from MACE's own minima, docs/34 §4b) and MACE is ρ +0.900 at **p = 0.0833**.
      `parity_matched.py` prints both cuts by default and a test locks the behaviour,
      so a rho above threshold can never be reported as a met gate again.
- [x] **I. Four false/stale statements retracted in place** — docs/26 headline (never
      amended for the repair), docs/29 §2 (OC22 coverage), docs/33 §3 ("like-for-like"),
      docs/34 §2 ("no DFT input of any kind"), plus the `evaluate_relaxed` docstring.
      Three `docs/figs/uma_*.json` stamped `SUPERSEDED_BY` — they still published the
      retracted `dft_eta` Cr = 1.726.
- [x] **J. CLOSED NEGATIVE — `mp-1095353` is not rutile.** The audit's one external
      validation lead (15 OC22 systems at (110) with a complete `*OOH`/`*O`/`*OH` triad)
      is **Pa-3 (205), cubic a = 4.90 Å**, a pyrite-type polymorph — against canonical
      rutile IrO₂ (mp-2723) at P4₂/mnm (136), a = 4.505, c = 3.177 Å. Identical at
      symprec 0.01 and 0.1. Its (110) has no bridging-O-row / cus-metal motif, so the
      energies are not comparable and scoring against them would be a FALSE validation.
      **OC22 holds no usable external validation for rutile MO₂(110) OER on our metals**
      — which retires "just validate against public data" instead of leaving it vague.
      Verified via MP OPTIMADE (no API key) + spglib; docs/38 §3b.
- [x] **K. DONE — `omat` MEETS the gate. R0's headline claim is FALSIFIED.**
      Criterion frozen and pushed FIRST (docs/39, commit `e084af8`, 07:46:27-04:00),
      then run: **ρ = +0.964, exact p = 0.0028, η MAE 0.125 V at n = 7** — beating
      MACE (+0.857 / 0.0238 / 0.173 V) and holding at n = 5 (ρ = +1.000, p = 0.0167)
      where MACE fails. One adjacent ranking swap, on a 53 mV DFT gap.
      **"No out-of-the-box UMA head ranks rutile OER" is wrong** — R0 tested three
      *adsorption* heads and never tried the *bulk-energetics* head, which is trained on
      PBE/PBE+U VASP data, the same functional family as our own reference.
      docs/26, docs/29 and docs/38 §4 all bannered as falsified in part.
      **The screen and melt list are UNAFFECTED** — both rest on MACE, validated
      independently by three routes (docs/38 §2). No candidate moves.
      **Counter-caveat:** `omat` desorbs `*OOH` on 5 of 7 metals (3.78–4.01 Å vs MACE's
      marginal 3.0), but only Cr is `pls=3`, so exactly ONE η is contaminated — the
      desorption cannot rescue R0. It also means `omat` ranks this tier better while
      being worse at the chemistry the HEA screen depends on (docs/37: 6 of 12
      candidates invalid from this failure mode). **Do NOT re-screen on `omat`** — it
      re-opens a met gate ten weeks from freeze. Cost: $0, ~9 min laptop CPU.
- [ ] ~~**K(old). UMA `omat` head, never tested**~~ — one CLI argument
      (`uma_oc22_parity.py --tasks omat`), the only untested attack on R0. Either
      pre-register the acceptance criterion in a doc **first** and run it, or state in
      one sentence that it was not run and why. Silence is the unacceptable option.
- [x] **L. DONE — [docs/40](../docs/40-predictor-reference-independence.md).** The
      audit found **twelve** contacts, not three, and corrected two of the three:
      * **NEW, and the largest: selection on the target.** `screen_mace.dft_tier()` and
        `parity_matched.py` make the identical `reference_tier()` call, and
        `r4_validate.json`'s `dft` block is element-for-element identical to it. MACE was
        SELECTED on this tier. So docs/35 / 36 / 38's three "routes" are **three
        predictor-side protocols against ONE target — 7 distinct DFT η, not 21.**
        Held-out DFT points in the project: **zero**. docs/38 §2 corrected in place.
      * **NEW, load-bearing: the Cr `*O` basin came from MACE** (`s0_O.in` rms 0.000000 Å
        vs the archived MACE geometry) and Cr is `pls=3`. Reverting Cr to its pre-repair
        1.726 V takes MACE +0.857/p0.0238 → +0.107/p0.8397 and omat +0.964/p0.0028 →
        +0.464/p0.3024 — **both models, both cuts, fail without it.** NB this is a
        load-bearing measurement, NOT a live alternative: 1.726 was a trapped stationary
        point and the restart converged 1.396 eV LOWER. docs/38 §5(iii) never named Cr.
      * **CORRECTED: Co was overstated.** `Co_slab/s0_OH.in` is NOT MACE-seeded (rms
        0.502 Å) and Co is `pls=1`, so Co's η rests on no seeded basin — dropping Co
        *improves* MACE (+0.886, p 0.0333).
      * **Leave-one-out published in full: MACE meets the gate on 3 of 7 cuts, omat on
        7 of 7.** MACE's significance rests on Ni.
      * **U convention CONFIRMED and `omat` does not break it.** Our U values match
        pymatgen `MPRelaxSet` `LDAUU['O']` exactly (Cr 3.7 / Mn 3.9 / Fe 5.3 / Co 3.32 /
        Ni 6.2; Cu/Ru/Ir absent = our zeros), and OMat24 follows "Materials Project
        defaults" via `MPRelaxSet`. Independence gained by MACE → omat on this axis: ZERO.
      * **`omat` DOES repair checkpoint/seeding independence** — different vendor,
        architecture, corpus; seeded nothing; and from unseeded builder starts it reaches
        every seeded basin to max |Δ| = 0.023 Å.
      * **A limitation we declined to overstate:** omat's `*OOH` desorption partitions
        exactly on the U line (p = 0.048), but that is reported as a coincidence in our
        own artifacts, NOT as reproducing Warford/Thiemann/Csányi — that paper has no
        rutile, no OER, never evaluates UMA, and predicts our fully-oxidised regime is
        exempt.
- [ ] **L-followup (cheap, high value): compute ONE held-out metal at DFT and
      pre-register it before scoring any model on it.** Cu is already in `RUTILE_AC` and
      carries no Hubbard U. Converts "zero held-out points" into "one" — a categorical
      change in what the report may claim.
- [ ] **L-followup: re-check before the mid-Oct freeze** whether the shipped
      `uma-s-1p2` `omat` head carries MPtrj+sAlex fine-tuning. If it does, omat's corpus
      independence collapses and docs/40 §2 must be rewritten.

## DECISION FORK (docs/29 §7) — now effectively A **and** B; confirm
- [x] **Path A** banked and QC-hardened (the negative is stronger after the audit)
- [ ] **Path B** R3 fine-tune: data extracted, MACE-OMAT recipe costed at ~$1.9,
      leave-one-metal-out CV drafted. Free Stage 0 (E0-only recalibration on the
      laptop CPU) may settle it for $0 — run that first.

## R1 — DFT hygiene
- [x] Free reanalysis: volcano positions, G_max, ±0.3 V error bars (DONE, docs/29
      §4b): all 4 on the scaling line far off-apex, step-2 limited; Mn only one near
      a real-electrode band; NiO₂ breaks OOH/OH scaling −0.51 eV (hypothesis only)
- [x] **Anchor-failure decomposition — FREE, and it changes the diagnosis**
      (2026-08-06, docs/41 §2, $0). The working hypothesis was ONE tier-wide
      systematic offset, because Ru (+0.39 V) and Ir (+0.22 V) both miss positive.
      Decomposing against the Man 2011 invariants refutes it:
      Ru is broken ONLY in the descriptor (ΔG_O−ΔG_OH = 1.163 vs apex 1.60, miss
      −0.437) while its *OOH scaling is perfect (3.180 vs band 3.2); Ir is broken
      ONLY in the *OOH scaling (3.652, miss +0.452) while its descriptor is at the
      apex (1.642). They reach the same η through different steps — **the shared
      sign is a coincidence, not a shared cause.**
      Corollary, also free: the gas references are ruled out algebraically. An
      E(H₂O) error cannot move the descriptor at all, and the single shift that
      pulls Ir onto the band drives Ru off it (3.180 → 2.728). No one-parameter
      repair exists, including uniform solvation of the H-bearing adsorbates.
      Also: ΔG_OH(Ir) = −0.0005 eV ⇒ the bare cus site is unstable to
      hydroxylation at U = 0, so it is not the resting state Ir is referenced to.
- [x] Probe tooling built and verified (`src/dft/probe_decks.py`, `probe_eta.py`,
      commit b8b2c7a). All four states of both anchors are ALREADY relaxed, so each
      protocol variable can be tested at FIXED GEOMETRY as a single SCF — cents, not
      dollars. Gated on a `base` control that must reproduce the relaxation's own
      final energy to 5 meV or the batch is void; verified field-by-field
      (species/cell/k-points/Hubbard/nspin/mags/if_pos/positions) to be
      physics-identical to the production decks. Emits queue_r1.sh manifests rather
      than a second runner.
- [~] **PROBES RUNNING on Vast box 47025043 (166.113.52.39:43442), launched
      2026-08-06.** Credit topped to ~$19.7; ~$0.3 spent; box is $0.108/hr.
      Check/collect with `src/dft/collect_probes.sh {status|pull|score}`
      (`HOST=166.113.52.39 PORT=43442`). Two detached queues:
      `queue_orient.log` (P10 relaxations) and `queue_r1.log` (SCF probes).
      **DESTROY THE INSTANCE when done: `vastai destroy instance 47025043`.**
      - Measured throughput: **47 min** per Ru spin SCF, **109 min** per Cr +U SCF at
        4 ranks; ~37 min per ionic step for the orient relaxations. The original
        84-job plan was ~14 core-days on a 23-core box, so scope was cut to the
        decisive subset (32 SCF + 2 relaxations). ETA ~14 h for P11+P7,
        1–2 days for P10.
      - `cpu.max` on this box is **23.04 vCPUs** though `nproc` reports 48 — the
        docs/23 §8 trap, caught before sizing MPI.
      - Two setup gotchas for next time: bare `ubuntu:24.04` has no `bzip2`, so the
        micromamba tarball in `setup_r1_box.sh` cannot unpack; and `NP` must be an
        exact multiple of `-nk` or `pw.x` aborts in `mp_start_pools`.
      - `yaw90` and `yaw270` are **mirror images across the plane under test** —
        energies agreed to <1e-5 Ry. The duplicates were killed; only `yaw90` runs.
      - DEFERRED, not cancelled: P9 RPBE (20 jobs, downgraded by Briquet) and
        P2/P3 dipole/vacuum (32 jobs, predicted NULL on three independent grounds).
        Decks are built and staged on the box under `probe/{Ru,Ir}_rpbe` and
        `probe/{Ru,Ir}`; re-queue with `m_all.txt` if wanted.
- [ ] **Score the probes when they land.** Acceptance criteria are pre-registered
      in docs/41 §5 and must not be revised after seeing numbers.
      - [ ] P7 U-ladder on **Cr only** (16 SCF) — Co cannot be laddered until its
            `s0_OOH` exists (see below). Can falsify the headline claim. If η(Cr) or η(Co) moves > 0.15 V across
            U ∈ {0, 0.5×, 1×, 1.35×}, "earth-abundant rutiles beat the noble
            anchors" is WITHDRAWN, not softened.
      - [ ] P2–P5 dipole/vacuum probe on Ru + Ir (32 SCF, ~$3). A variant only
            counts as explaining Ru if it raises the descriptor ≥ 0.30 eV, or Ir if
            it lowers ΔG_OOH−ΔG_OH ≥ 0.30 eV. P6: if no single variant does both,
            the registered conclusion is TWO independent mechanisms — assembling a
            per-metal "corrected" tier after the fact is the circularity docs/40
            exists to catch.
      - [ ] Vast credit is **$0.295**, less than either step. A ~$25 top-up is the
            single blocking action for the entire DFT arm.
- [ ] AFM β-MnO₂ (~$0.15) — still unrun; FM-only starts on an experimentally AFM oxide

## R2 — Stability gate (mostly free)
- [ ] MP Pourbaix ΔG_pbx for all 6 endmembers + candidate HEA oxide products
- [ ] Integrate stability into the screening objective (Tran-2024-style)

## R3 — Fine-tuned screener (single GPU-days)
- [x] Convert archived QE trajectories (78396b5) → training set (785 frames,
      `src/dft/qe_frames.py`). **Verified uncontaminated 2026-07-31**: pw.x emits
      `!  total energy` only for a converged SCF, so a failed cycle contributes no
      frame. Checked on all four POISONED trajectories — `n_energies == n_scf_ok`
      exactly. They still donate their *good* frames (17 from Ni s0_O, 36 from Ni
      s0_OH, 6 from Cu s0_OOH): rejected for η, salvaged for training.
- [x] **Stage 0 CLOSED analytically — do not run it** (`src/dft/e0_stage0.py`).
      The CHE reference is stoichiometrically closed, so an arbitrary per-element
      E0 shift leaves every ΔG unchanged (verified through the real referencing
      path, max |Δη| = 3.6e-15 eV over 8 systems). Therefore the oc22 ρ = −1.00 is
      **not** a reference-energy artefact — the whole composition-linear subspace of
      model error is projected out of the descriptor, and being force-free it does
      not move geometries either. The failure is geometry-dependent local chemistry:
      relative *O vs *OH binding across metals.
- [ ] Fine-tune MACE-OMAT (naive, LR 1e-3, E0 reestimated) and/or UMA-small
      head-only (LR 4e-4). **Gate must be the CHE observable, not energy MAE** —
      E0 alone can cut total-energy MAE a long way while leaving every η identical.
- [ ] **Gate arithmetic (exact permutation, not asymptotic).** LOMO CV yields one
      held-out η per metal; Spearman is computed across those. At the n available:
      | n | ρ needed for p<0.05 | ranking errors tolerated |
      |---|---------------------|--------------------------|
      | 4 | unreachable (ρ=1 → p=0.083) | — |
      | 5 | **1.000 only** (p=0.017); ρ=0.9 → p=0.083 | **zero** |
      | 6 | 0.886 (p=0.033); ρ=1 → p=0.0028 | two |
      So "Spearman ≥ 0.8" is only a meaningful gate at n ≥ 6. At n = 5 the fine-tune
      must rank all five *perfectly* to claim anything.
- [ ] Re-screen HEA space: activity × stability × cost; optional AL loop
      (3–10 DFT/loop)

## R4 — HEA tier + write (Sep → data freeze ~mid-Oct)
- [ ] SQS approximants of top-3 compositions, DFT-blessed
- [ ] Oxyhydroxide-termination spot-check (alkaline active-surface story)
- [ ] Melt decision at FWM — Frank's call
- [ ] STS report framing (AI-assistance rules per docs/25) — Frank writes

## Standing non-technical (carried over)
- [ ] STS sponsor of record still unresolved (docs/16 §10) — highest-priority
      non-technical item; **application due Nov 5, 2026, 8pm ET**

---
2026-08-23 (evening): **docs/52-decision-sheet-2026-08-23.md** is the walkable index of every open decision above — 66 rows, 52 verdict-bearing, each with file:line + options as drafted. Compiled by 9-agent workflow, adversarially verified (19 findings applied). Line-number citations in it were verified against THIS file at 2026-08-23; insert new todo lines at the very end only.

## 2026-08-23 — A8+A9 adopted and DEPOSITED
- [x] Frank reviewed docs/52 sections 1-2 and adopted every drafted proposal ("they pass with me")
- [x] A8+A9 appended to docs/43 (2e61bf0), adversarially verified (1 blocker + 6 minors fixed, 1c09c38)
- [x] **Zenodo DOI 10.5281/zenodo.22072991** (A1-A9, restricted, md5 7e10c620..., 187,187 B)
- [ ] Frank: AFM-scope collision dated line (A8.1 second-seed vs A8.5 standalone four) — gate-(h) HOLD until then
- [ ] Frank: LIT-2 C1-C10 sign-offs + SnO2 admission declaration (docs/52 sections 3-5 were NOT covered by the adoption)
- [ ] Frank: silentgate core (S1); Xu repair (a)/(b); OC20 CI mechanism; P-BUILDER/P-LIT values; six-row + claim sentence by Sep 20
- [ ] Unblocked now: S3 tier_v3 deck build (launch Aug 26); A9.7 post-DOI acts in order (zip fetch+listing compare, header validation, OC20 download)

## 2026-08-23 — A9.7 acts 1-3 executed + 1C re-scored (post-adoption compute go-ahead)
- [x] A9.7 act 1: zip fetched on Anvil (md5 matches Zenodo), listing compared — 6,989/6,989 paths+sizes, 815/815 pwscf.out git-blob SHA-1s match; zip = mirror snapshot at c4cb892 (docs/research/xu-verification-2026-08-23/)
- [x] A9.7 act 2: header-format validation — RuO2 4-layer bare/O-relax/OH-relax/OOH-relax, all four count-first form; no reader fix needed (dated line in docs/43 A9.7)
- [x] A9.7 act 3: OC20 val_id downloaded (md5 matches registered), 24,945 members, first-500 lexical draw extracted, sha256 manifest committed, stored precision = fixed 8-decimal text eV/A (docs/research/oc20-val_id/)
- [x] block 1C re-scored under adopted reading (b): CONFIRMED at both delta against i50 floor, reading-(a) label (UNDERPOWERED/VOID) alongside (docs/49 s7; hessian_analyze.py now implements (b))
- [x] A5.2 LIT-2 readout: confirmed already scored+committed at 9fd1771 (RuO2 benchmark FAIL -> Cr column vacuum-CHE-only, flag OFF); no action needed
- [ ] A9.7 act 4 (census): waits on Frank's silentgate core (entrant-written)
- [x] corpora durability copies to $PROJECT/corpora/ verified (both md5 match after copy)
- [x] docs/54 S3 deck matrix composed + adversarially verified (3cbd192); A8.5 pseudo md5 preflight 12/12 MATCH (anvil/pseudo_md5_preflight_2026-08-23.md)
- [ ] S3 wave 1 (46 production-seed relax + 9 SCFs) building via workflow; parked for Frank: __magm/__ns (second-seed recipe sign-off), dy-pilot rungs, Co/Ni *OOH 1x1-off, BUILD-T 55, HOLD 14 (gate-(h) line), Ru/Ir g1 top-up scope, Mn AFM arm, Ti nspin=2 controls, mirror-member ruling (docs/54 s6)

## 2026-08-23 (late) — S3 wave 1 LAUNCHED on Anvil
- [x] wave-1 tree built: 55 decks (46 relax + 9 SCF), 2x1v mir starts mirror-symmetrized to exact reflection (max shift 0.2338 A < 0.30 refuse bound; off = same base + banked kick, independently verified 3-edit diff); Ti template already exact (1.8e-15 A)
- [x] orchestrator ruling recorded in manifest + builder: off rows LAUNCH with banked 0.35 A / 90 deg constants (A8.8 no-replacement — results stand as the banked-constant arm; Frank may override by dated line, added rungs = new decks never replacements); dy-pilot rungs remain Frank's
- [x] committed 2fd3fc1 (61 files) + pushed; staged to Anvil via tarball md5-matched both ends (55b429fb...), LF-fixed, 55/55 decks present
- [x] canary array 20097663 (Fe s0_O__2x1v_mir / Mn s0_O__1x1_off / Ti ref__2x1v): ALL PASS — Fe mir shows "2 Sym. Ops. (no inversion) found" (the mirror is real), Mn/Ti nosym as registered, k-counts 9/19/16 match the -nk pricing, pseudo MD5s match A8.5 preflight, SCF iterating cleanly
- [x] rest fleet array 20097688 submitted: 52 decks %6 concurrency, preflight 52/52 clean; PARITY_PASS gate enforced on both submissions; account che260157 (98,840 SU before launch)
- [x] 43_submit SIGPIPE fix (mybalance|awk under pipefail on non-tty ssh) committed da38d2a, restaged
- [ ] wave-1 monitoring: __g1 ≥5 meV re-relax loop + A8.4 escalation ladder apply as parents converge; wave 2 (46 __g1 children + 19 Cr re-Hessian SCFs at escaped geometry) builds after parents/escape converge

## 2026-08-24 — wave-1 drained: 37/55 clean; retry array up
- [x] status sweep (all 55 outs pulled local, md5-matched): 37 converged clean incl. every mir arm live-verified (2 Sym. Ops.) + Cr escape (35 BFGS steps); mir-vs-off deltas range 0.4 meV (Ni OH) to ~1.8-1.9 eV (Mn/Fe OOH — the yaw-90 kick found different conformers; feeds the parked oosh conformer question)
- [x] 11 OOM = node a024 (11/12 kill rate vs 0/43 elsewhere) — resubmitted unmodified, array 20101963, ExcNodeList=a024 via scontrol (SBATCH_EXCLUDE env silently ignored); attempts preserved as .out.attempt1
- [x] 7 Co/Ni SCF non-convergences (healthy nodes) -> A8.4 rung (ii) .retry_bh.in beta 0.15 (rung (i) unavailable: runner deletes scratch densities — recorded docs/45); commit 0f530a7
- [ ] when 20101963 drains: re-sweep; any .retry_bh failure -> rung (iii) NOT_CONVERGED gap; then __g1 children build (wave 2) + Cr 19 re-Hessian SCFs at escaped geometry
- [ ] entrant call parked: scratch-retention rider for wave 2 (density survival would make rung (i) real)

## 2026-08-24 (later) — retry-1 drained: 46/55; rung (iii) invoked; retry-2 up
- [x] retry-1 (20101963) 18/18 Slurm-complete, 0 OOM (exclusion held): 9 converged -> 46/55 total; Ti fully green (a024 was its only problem)
- [x] rung (iii) NOT_CONVERGED gaps recorded (docs/45): Co OH-1x1off, Co O/OH/OOH-2x1v-mir, Ni OOH-2x1v-mir
- [x] retry-2 (20107835, 4 decks): a024-masked Co ref / Co OH-off / Co OOH-off / Ni OOH-off at rung (ii) beta 0.15; EXCLUDE hook in 43_submit (73fa710); attempts preserved .attempt1/.attempt2
- [ ] when 20107835 drains: final sweep; failures -> rung (iii); then wave-2 build (__g1 children of converged parents + Cr 19 re-Hessian SCFs); Co ref outcome decides whether the Co 2x1v column has a reference

## 2026-08-24 (final) — wave 1 CLOSED at 46/55; 9 registered gaps
- [x] retry-2 0/4: ladder exhausted -> rung (iii); gap census: Co x7 (ref, OH-1x1off, O/OH/OOH-mir, OH/OOH-off), Ni x2 (OOH mir+off)
- [x] failure signatures recorded (docs/45): Co ref = NEAR-MISS creep 2.6e-6 vs 1e-6 at step 200 (stable 22.92 mu_B) — an entrant electron_maxstep line would likely rescue the whole Co 2x1v column; the other three = genuine stall/oscillation
- [ ] ENTRANT DECISION (new, high-leverage): raise electron_maxstep for Co ref__2x1v re-run? One dated line; restores the Co 2x1v reference
- [ ] next: wave-2 build — 37 __g1 children of converged relax parents + Cr 19 re-Hessian SCFs (1e-10) at the escaped geometry

## 2026-08-24 (wave 2) — LAUNCHED: array 20114094
- [x] wave-2 built via workflow wf_dc0c2bfc (implementer + 4 adversarial auditors + fixer, zero MAJOR): 37 __g1 children (parent-cloned verbatim incl. two beta-0.15 retry parents; Cr escape gets a child) + 19 Cr re-Hessian SCFs at escaped geometry (1e-10, delta exactly 0.01 A, hessian_analyze.py needs ZERO code change — analysis-stage hess_manifest.json is a deliberate deferral: mirror_plane must be declared at the mirror-BROKEN geometry)
- [x] committed 6e7be4c (58 files), staged md5-matched, submitted with ExcNodeList=a024 baked in; preflight 56/56 clean
- [ ] when 20114094 drains: A8.3 scoring (child >1 meV above parent -> refused; re-run needs parent density -> density-retention runner, same piece as the 2 deferred Cr_lit3 re-runs); then the re-Hessian sigma_F readout (docs/49 instrument) and the S3 P-SYMCOV/CONFOUND analysis over the full tree

## 2026-08-24 (wave-2 drained) — 49/56 in hand; A8.3 verdicts; chains launched
- [x] wave-2 sweep: 34/36 __g1 conv + 15/15 hess conv; 33/34 AGREE <= +1 meV; 5 OOM = node a088 (second sick node) -> retry 20118525 (EXCLUDE=a024,a088) with 2 rung-(ii) beta-halved children
- [x] A8.3: Ni s0_O__1x1_off__g1 REFUSED (+85.1 meV) -> retention chain; Fe s0_OOH__1x1_off__g1 (-384.3 meV!) and Mn s0_OOH__2x1v_off__g1 (-20.6 meV) BELOW parents = metastable-parent evidence, banking = ENTRANT call
- [x] retention chains built+launched (20119469): Ni refusal + 2 Cr_lit3 owed re-runs; replay = parity evidence only
- [ ] on drains: final census; hess sigma_F readout needs analysis-stage hess_manifest.json (mirror_plane at broken geometry); S6 P-SYMCOV/CONFOUND analysis; failure rates per A8.4

## 2026-08-24 (w2 retry drained) — hess 19/19; child census closed 34/1/2
- [x] a088 victims 5/5 conv elsewhere; Ti child AGREE +0.002 meV; hess displaced E +~0.9 meV over minimum (sane)
- [x] rung (iii) for Co s0_O__1x1_off__g1 + Ni s0_OH__2x1v_off__g1 -> parents GATE-1 UNVERIFIED (S6 flag)
- [ ] awaiting chains 20119469 (Ni A8.3 second attempt + 2 Cr_lit3); then sigma_F readout + S6 analysis

## 2026-08-24 (chains drained) — ALL A8.3 verdicts AGREE; S3 GATE-1 census FINAL
- [x] chains 3/3: Ni +0.019 meV, Cr oosh +0.002, Cr yaw90 +0.001 vs banked parents -> no MULTISTABLE; LIT-3 BASIN_DRIFT closed; banked energies stand
- [x] S3 GATE-1 final: 35 AGREE / 0 REFUSED / 2 UNVERIFIED (Co s0_O__1x1_off, Ni s0_OH__2x1v_off — children unconvergeable)
- [x] all evidence banked (2b93340); Ni replay branch-divergence recorded (>=2 electronic branches on Ni 1x1_off)
- [ ] in flight: esc re-Hessian sigma_F readout (agent); then S6 P-SYMCOV/CONFOUND analysis + A8.4 failure-rate table

## 2026-08-24 (readout) — 1C CLOSES: escape is a real minimum
- [x] esc re-Hessian: i244.7 GONE, 9/9 modes real, gate-clean, floor-robust; M=23.00 unchanged (geometric descent, not magnetic); analysis files banked
- [ ] S6/entrant: Cr *OOH 2x1v banking (mir saddle / esc minimum / off -76 meV deeper); P-SYMCOV/CONFOUND analysis + A8.4 rate table = next analysis block

## 2026-08-24 — round 3 + S6 analysis block (post-arc)
- [x] Node check: a024/a088 back in pool, never drained — NOT fixed
- [x] docs/55 decision sheet (delegated criterion): R1 §5-strict re-relax, R2 maxstep 500, R3 Cr esc minimum, R4 RCAC draft
- [x] Round 3 built (13 decks, assert-verified) + launched: array 20123293, EXCLUDE verified
- [x] RCAC ticket drafted (anvil/rcac_ticket_draft_2026-08-24.md) — FRANK SENDS
- [x] S6 analysis block (wf_2ca82c9d-eaa): readout + 4 dimensions + adversarial verify -> docs/56
- [x] GATE-1 census correction: Ni s0_OH__basin_g1 REFUSED-candidate +177.10 meV -> chain-2 job 20124032
- [ ] Bank round 3 on drain; build wave-4 __g1 children for newly converged relaxes
- [ ] Score chain-2 on land (AGREE / MULTISTABLE)
- [ ] Refresh docs/56 PENDING rows after round 3 + chain-2
- [ ] FRANK: mirror-member ruling (docs/54:406-411) — P-SYMCOV 5-of-8 hinges on it; A8.4 basis choice; A8.1 bin-scheme naming; Cr OH 1x1 CONFOUND check; RCAC ticket send

## 2026-08-25 — round 3 drained + banked: 4/13, failure mode NAMED (creep vs branch-flip)
- [x] Queue empty; array 20123293 13/13 Slurm-COMPLETED (last 06:01:34); outputs pulled md5-matched (265d71ab...) into the 13 A8.8-vacated slots
- [x] **Co ref__2x1v CONVERGED** — the entrant maxstep-500 ruling delivered; the Co 2x1v reference exists
- [x] Also converged: Co s0_OH__1x1_off, Co s0_OOH__2x1v_mir, Fe s0_OOH__1x1_off__basin
- [x] 9 failures triaged (docs/45): **6 creepers** (500 it., 1.1e-5–8.8e-5 Ry vs 1e-6 — iteration ceiling, no oscillation), **1 registration slip** (Mn basin re-relax never got maxstep 500; died at 5.3e-7 on QE's ethr restart, bfgs 17, still descending), **2 branch-flips** (Ni OOH-2x1v-off M 4.19 vs ~13; Co O-1x1-off-g1 at beta 0.07)
- [x] **Both below-parent findings CONFIRMED and DEEPER than their __g1 children**: Fe s0_OOH__1x1_off basin converged at **−428.5 meV vs banked parent** (−44.2 vs child); Mn at −42.4 meV (−21.8 vs child, unconverged)
- [x] GATE-1 census unchanged 38 / 0 / 2 — both round-3 __g1 rescues failed again
- [x] ~~**ENTRANT DECISION 1**~~ **REFUTED same day** — see docs/45 CORRECTION. Only 1 of the 6 is iteration-limited; the other 5 are STALLED/BRANCH and a maxstep bump buys them nothing. Superseded by R2.
- [x] ~~**ENTRANT DECISION 2**~~ **REFUTED same day** — the Mn basin was held to an effective conv_thr of **1.0e-8** (QE `upscale`=100 default) and reached 5.0e-7; maxstep 200 was never the binding constraint. Superseded by R1.
- [ ] **ENTRANT DECISION 3 (A8.8):** the Fe/Mn below-parent minima — replace the banked energies-of-record, or bank as a second arm? Round 3 removes "it might be noise"; the −428.5 meV Fe gap is 400x the A8.3 gate width
- [ ] **ENTRANT DECISION 4:** the 2 branch-flips go to the density-retention instrument (build_retention_chain2.py), not to more iterations
- [ ] Wave-4 __g1 children owed for the 4 newly converged relaxes (Co ref__2x1v, Co s0_OH__1x1_off, Co s0_OOH__2x1v_mir, Fe basin) — build after decisions 1-3 so one array carries everything
- [ ] Refresh docs/56 PENDING rows (round 3 + chain-2 both now in hand)
- [ ] FRANK, still open from 2026-08-24: mirror-member ruling (docs/54:406-411), A8.4 basis choice, A8.1 bin-scheme naming, Cr OH 1x1 CONFOUND check, RCAC ticket send (a024/a088 still in pool, never drained)

## 2026-08-25 (later) — CORRECTION: the round-3 failure mode was an UNREGISTERED PARAMETER, not an iteration ceiling
- [x] Tried to *size* decision 1 by fitting tail decay rates → the fit refused to converge → found the cause
- [x] **`upscale` is set in ZERO decks in this repo.** QE's default 100 silently TIGHTENS conv_thr during `relax` toward a 1e-8 floor, printing `new conv_thr` each BFGS step. Runs reporting "NOT achieved" at 3.2e-7 were being held to 2.79e-7, not to the deck's 1e-6.
- [x] Ruled out `ecutrho` (640 = 8x ecutwfc, correct for USPP) and `negative rho` (same 3-5e-4 in converged rows) — **the fixed point IS reachable in these cells**
- [x] Census: **39 of 42 banked converged relaxes met 1e-8, not the registered 1e-6.** Nothing invalidated — everything is converged tighter than advertised
- [x] Wrote `src/dft/scf_triage.py` — classifies on progress rate of the running minimum against the *effective* threshold. Corrected triage: **1 SLOW / 4 STALLED / 2 BRANCH / 2 UNREG_THR** (was "6 creepers")
- [x] docs/45 CORRECTION section appended (retracts the creeper + registration-slip readings)
- [ ] **R1 (FRANK, registered parameter, NEW):** declare `upscale` explicitly. `upscale = 1.0` holds relaxes to the registered conv_thr = 1e-6 and is what both UNREG_THR rows need (they are already at 5.0e-7 / 3.2e-7). Weigh: 39 banked rows met 1e-8, so new rows at 1e-6 are 100x looser than siblings — numerically irrelevant vs a 1 meV = 7.35e-5 Ry gate, but it is a protocol-uniformity claim
- [ ] **R2 (FRANK, registered parameter):** electron_maxstep 500 → 1500 for **`Co s0_O__2x1v_mir` ONLY** — 1 deck / ~500 SU, replacing the refuted 6-deck / ~3,000 SU decision
- [ ] **R3 (FRANK, A8.8, unchanged):** Fe/Mn below-parent minima — replace the banked energies-of-record or bank as a second arm? Fe gap = 428.5 meV = 400x the gate width. Mn is now better qualified: it was *converged by the registered criterion* (5.0e-7 < 1e-6) when cut off, and still descending
- [ ] **R4 (no ruling needed — registered mechanics, buildable now):** 4 STALLED → A8.4 rung (i) restart-from-density; 2 BRANCH → A8.3 chains. `Co s0_O__1x1_off__g1` + `Ni s0_OH__2x1v_off__g1` both have banked converged parents → proper parent→child chains → **this is the path that closes GATE-1 UNVERIFIED to zero**
- [ ] **Methods correction owed (FRANK re-authors — threshold claim, not infrastructure):** the protocol text says SCF threshold 1e-6 Ry; the runs met 1e-8 almost uniformly
- [ ] `Ni s0_OOH__2x1v_off` (BRANCH, dM 2.41 μB): primary relax, NO parent to seed from — the one row with no registered remedy in hand; A8.4 rung-(iii) NOT_CONVERGED gap candidate if a self-seeded staged restart fails
- [ ] Wave-4 `__g1` children still owed for the 4 round-3 converged relaxes — build with the R1/R2 array so one submission carries everything
