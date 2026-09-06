# STS 2027 — TODO

## Documentation maintenance (2026-09-03)

- [x] Add the standing project wording rule to `CLAUDE.md`.
- [x] Remove authorship and provenance labels from project documentation.
- [x] Record the wording lesson, validate the cleanup, and push the scoped changes.

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
- [x] **R4 — LAUNCHED 2026-08-25, Anvil array `20135148` (5 rows, `1-5%3`, `EXCLUDE=a024,a088`, balance 83,845.8 SU at launch; est. ~1,000-2,000 SU).** 4 STALLED → A8.4 rung (i) restart-from-density; 2 BRANCH → A8.3 chains. `Co s0_O__1x1_off__g1` + `Ni s0_OH__2x1v_off__g1` both have banked converged parents → proper parent→child chains → **this is the path that closes GATE-1 UNVERIFIED to zero**
- [ ] **Methods correction owed (FRANK re-authors — threshold claim, not infrastructure):** the protocol text says SCF threshold 1e-6 Ry; the runs met 1e-8 almost uniformly
- [x] **ROUND 4 COMPLETE — array 20135148, 1,132.8 SU (83,845.8 → 82,713.0).** 1 of 5 rows did what the manifest said: row 2 AGREE. Row 1 produced the branch finding instead; rows 3-5 retired the self-seed idea. Row 5 failed at the SEED (loose `conv_thr` → 30× loose `ethr`), not at the child as I predicted. A8.8 clean, no banked result touched. Full tally in `docs/45`
- [ ] **Housekeeping:** `runs/s3/Co/tmp_chain_s0_OOH__2x1v_off__fs` (5.6 GB) kept on `$PROJECT` by the runner's CHAIN-FAIL rule; no diagnostic value beyond the `.out`. Safe to delete, left in place
- [ ] **R5 (FRANK, registered parameter, NEW — recommended).** Add `mixing_ndim = 16` to the three STALLED Co decks. `mixing_ndim` is unset in EVERY S3 deck (QE default 8) — the same shape of omission as `upscale` — and the A8.4 ladder escalated `mixing_beta` three times without ever touching the history depth, which is the parameter the "saturated history" diagnosis actually names. This repo's earlier R1 slab campaign used `mixing_ndim=12` as standard and **`mixing_ndim=16` + `mixing_beta=0.05` as its "attempt4" escalation, which converged `Cr_slab/s0_OH`, `Mn_slab/s0_OOH`, `Co_slab/s0_O`**. ~3 tasks. No `docs/` rationale exists for the value, so it needs registering not inheriting
- [x] **Round 4 rows 3-4 FAILED — rung (i) self-seed could not have worked.** `SEED_CONV_THR = 1.0d-4` was 5.4×-15.7× LOOSER than the floor these decks already reach cold (1.836e-5 / 6.37e-6 / 1.132e-5), so the seed handed over a density worse than the failing run's own endpoint. My builder's feasibility assertion proved the seed would converge and never asked whether converging there was worth anything. The saturated-Broyden hypothesis is **untested, not refuted** — the run changed two things at once. See `docs/45` §Round 4 rows 2-4 scored
- [x] **Row 2 CLOSED: `Ni s0_OH__2x1v_off__g1` UNVERIFIED → AGREE.** Converged in 12 iterations from the parent density at **+0.005 meV** vs banked, and in the correct magnetic branch (14.41 vs the cold start's 12.24)
- [ ] **R3 NOW COVERS THREE ROWS (FRANK).** Round 4 chain 1 added `Co s0_O__1x1_off`: the parent's OWN deck, re-run unmodified, reached a state **−76.69 meV** below the banked energy, in a different magnetic branch (11.24 vs 11.69 μB), and the `__fp` child stayed in it (−77.01 meV vs banked, −0.32 meV vs its density source). Unlike Fe/Mn this did not come from a `__basin` deck built to find something deeper — same deck, same machine, different answer. The ruling now has a second half: can a banked relax whose deck is demonstrably branch-unstable stand on a single run? See `docs/45` §Round 4 chain 1 RESULT
- [ ] **A8.6 `--bind-to` is no longer only a performance question (FRANK).** Parent ran on a081, replay on a156; the two SCFs were bit-identical for 5 iterations and split at the 6th. Reduction order is what selected the 78 meV branch. Deciding binding is now a reproducibility control, not an 18% speedup
- [ ] **Score round 4 on land** (`docs/45` §Round 4 LAUNCHED). Replay parity targets: `Co s0_O__1x1_off` = -2330.66171228 Ry, `Ni s0_OH__2x1v_off` = -5157.23065359 Ry — replay energies are evidence, never banked (A8.8). Row 1 does NOT close its UNVERIFIED — it converted one into a below-parent question (see the R3 item above). Row 2 (`Ni s0_OH__2x1v_off`, replay parity −0.07 meV) can still close its own.
- [ ] **Send the RCAC ticket** — `anvil/rcac_ticket_draft_2026-08-24.md`. a024 and a088 were both `MIXED` (back in the general pool) at the 2026-08-25 launch, so every array still has to carry `EXCLUDE=a024,a088` by hand. Documented kill rates 11/12 and 5/5 vs 0/51 elsewhere
- [ ] `Ni s0_OOH__2x1v_off` (BRANCH, dM 2.41 μB): primary relax, NO parent to seed from — the one row with no registered remedy in hand; A8.4 rung-(iii) NOT_CONVERGED gap candidate if a self-seeded staged restart fails
- [ ] Wave-4 `__g1` children still owed for the 4 round-3 converged relaxes — build with the R1/R2 array so one submission carries everything

## 2026-08-26 — round 5 scored, round 6 launched. `mixing_ndim = 16` is confirmed on the rows a bad node let run.
- [x] **R5 ANSWERED — `mixing_ndim = 16` converged `Co s0_OH__2x1v_mir`**, which had failed three cold attempts and a self-seed. 18 BFGS steps, final SCF 8.5e-09. QE echoes the parameter, so the control is in the outputs: `number of iterations used` = 8 (attempt3, failed) vs 16 (round 5, converged) at identical beta 0.15 / threshold 1e-6 / local-TF. **The saturated-Broyden hypothesis, recorded "untested" after round 4 confounded it, is now supported** — by the test that varies only the one thing
- [x] **Wave-4 `__g1` children built and run** (the 4 owed): `Co ref__2x1v` (still running), `Co s0_OH__1x1_off` **AGREE +0.026 meV**, `Co s0_OOH__2x1v_mir` and `Fe s0_OOH__1x1_off__basin` both BRANCH MISMATCH
- [x] **Node a196 destroyed four of eleven round-5 rows.** `State=ALLOCATED+DRAIN`, `Reason=NHC: Terminated by signal SIGTERM [root@2026-08-25T19:55:48]`, `FreeMem=384` MB on 128 cores at load 166. Three rows OOM-killed at MaxRSS 8.65–8.70 GB while the array's healthy runs peaked at 30.8–46.8 GB — killed for the node's lack of memory, not their own use. A fourth (`Mn basin`) was scheduled onto it anyway, wrote a 9,912-byte header and produced **zero SCF iterations in 1h45m**; I cancelled it rather than let it burn ~5,900 SU of its remaining 46 h walltime. **None of the four is evidence about `mixing_ndim`** — they re-run unchanged
- [x] **RCAC ticket draft updated** with a196 — the first of the three incidents that carries a Slurm-side diagnosis rather than only the identical-input/different-node contrast. Also asks whether a node in DRAIN after an NHC SIGTERM should still receive newly scheduled array tasks, which is what turned three lost jobs into four
- [x] **ROUND 6 LAUNCHED 2026-08-26**, both arrays with `EXCLUDE=a024,a088,a196`, balance 81,204.0 SU at launch:
      - **`20143254`** wave, 5 rows `1-5%3` (`runs/s3/m_s3_round6.txt`) — 4 unchanged re-runs of the a196 victims + `Co s0_OOH__2x1v_off` at `mixing_beta` 0.15 → 0.05
      - **`20143262`** chains, 2 rows `1-2%2` (`runs/chains/m_round6.txt`) — A8.3 density retention for the two wrong-branch `__g1` children
      - preflight `lines=5 to_run=5 already_done=0 stale=0 bad=0`; all 7 pushed files md5-verified local↔Anvil; built by `src/dft/build_s3_round6.py`
- [ ] **Score round 6 on land.** Wave: did the 4 re-runs converge with ndim=16 on healthy nodes, and did beta 0.05 rescue `Co s0_OOH__2x1v_off`? Chains: do the two `__fp` children reproduce their banked parents within ±1 meV **and in the parent's magnetic branch** — magnetization is not optional, see below
- [ ] **Score `20141568_1` and `_8` when they land.** Row 1 (`Co s0_O__2x1v_mir`, ndim16 + maxstep 1500) already answers **R2 in the negative and reclassifies its own triage**: at 746 iterations its minimum is 1.628e-05 (vs 4.287e-05 cold) reached near iteration 100, and it has drifted up to ~3.5e-04 since. **The deck is STALLED, not SLOW.** Left running deliberately — a pre-registered test on a healthy node, ~384 SU to finish
- [ ] **`Ni s0_OOH__2x1v_off` now HAS a registered remedy in hand** — it is in the round-6 re-run set at ndim=16 and no longer needs the cross-arm seed the round-4 manifest gated on R1
- [x] **The branch rule is 9 for 9 and has never failed.** Matching magnetization → energy reproduces to ≤0.52 meV; differing magnetization → tens to hundreds of meV. Round 5's three children are pairs 7-9: +0.026 meV at Δmag +0.00, +7.395 meV at **Δmagtot +4.00 / Δmagabs +0.03** (≈2 μB flipped down-to-up at unchanged local moment size — a ferrimagnetic rearrangement, not a convergence artifact), +747.449 meV at Δmagtot +4.73. **No `__g1` child may be banked on energy alone**
- [ ] **A8.8 note for the record:** the five round-5 `.out` files round 6 overwrites were archived to `.out.attempt<N+1>` on both sides, guarded on source-exists and target-free before anything moved (`git mv` locally, `mv -n` on Anvil). Nothing banked was touched

## 2026-08-26 (later) — round 6 scored, round 7 launched. The ladder was re-running the hardest step and discarding converged ones.
- [x] **CORRECTION to my round-5 claim.** I called `mixing_ndim = 16` a confirmed fix off one row. With five more decks tested it is **1 converged of 6** — it helped two, made `Co s0_OH__2x1v_off` worse (2.470e-05 vs 1.836e-05 cold), and did not generalise. The narrow round-5 fact still stands (`Co s0_OH__2x1v_mir` converged at 8.5e-09 with the depth as the only change); the general claim does not
- [x] **THE FINDING: score failures by IONIC steps, not SCF accuracy.** `Co s0_OOH__2x1v_off` completed **14 converged BFGS steps** on attempt2 at the ORIGINAL beta 0.3. Every rung since (beta 0.15/200, 0.15/500, ndim16, ndim16+beta0.05) restarted from the original geometry and stalled in the first SCF — four escalations, ~1,000 SU, re-running the hardest step of a trajectory whose 14th step was already on disk. `Ni s0_OOH__2x1v_off` is the same shape at 1 step
- [x] **My builder defect:** `build_s3_round5.py` splices from `job + '.out'` and never scans `job + '.out.attempt*'` — the LAST attempt, not the DEEPEST. Right for Mn (19, attempt1) and Ni `_mir` (3, attempt3) by luck; wrong for the one deck whose best attempt had been archived several rungs earlier. `build_s3_round7.py` picks by max ionic steps across all attempts
- [x] **And attempt2 was never a mixing failure.** It stopped holding `new conv_thr = 4.10e-8` — the unset `upscale` tightening its registered 1e-6 by **24×** — having reached 3e-8. That is UNREG_THR, so the STALLED triage for this row rested on later attempts crippled by starting over
- [ ] **R1 (FRANK) is now the highest-value open call.** Declaring `upscale` is the cleaner fix for `Co s0_OOH__2x1v_off` and `Ni s0_OOH__2x1v_mir`, both of which are being failed against a threshold 24×/3.6× tighter than the one they registered. Round 7 does what can be done without a ruling
- [ ] **Two decks have NEVER completed an ionic step** — `Co s0_O__2x1v_mir` (4 attempts, 200/200/500/1500 iters) and `Co s0_OH__2x1v_off` (5 attempts). No geometry to resume from, mixing ladder exhausted. Need R1, a new registered call (starting magnetization / diagonalization), or A8.4 rung-(iii) NOT_CONVERGED acceptance. **Deliberately not built into round 7**
- [x] **R2 ANSWERED, NEGATIVE.** `Co s0_O__2x1v_mir` ran the full 1500 iterations, hit its minimum near iteration 100 and drifted up for the remaining 1400. **Misclassified SLOW; it is STALLED**
- [x] **`Fe s0_OOH__1x1_off__basin__g1` GATE-1 CLOSED** by the A8.3 chain: replay −0.049 meV, child **+0.004 meV**, magnetization 22.98/27.59 identical across banked / replay / child. A +7.395 meV branch mismatch closed to 4 μeV — second clean demonstration of the remedy after round 4's Ni row
- [ ] **`Co s0_OOH__2x1v_mir` CHAIN FAILED — the banked energy cannot currently be reproduced.** The parent's own deck, re-run, matched its magnetization trajectory bit-for-bit for three values (53.79/55.78/25.00) then failed to converge at all (500 iters in cycle 1, min 2.477e-5, magtot 19.98) where the parent converged cycle 1 in 135 iterations and completed 22. **This is R3's second half**, and another argument for settling A8.6 (`--bind-to`)
- [x] **Wave-4 children stand at 2 closed of 4.** `Co ref__2x1v__g1` also failed (500 iters, no convergence, magtot 24.11 vs parent 21.66) — takes the A8.3 remedy in round 7
- [x] **Node a220 is a fourth bad node**, OOM-killing two rows at MaxRSS 35.1 GB against a granted `mem=237G`. No DRAIN, no NHC record — the a024/a088 shape, not a196's. **Ruled out:** our own tasks were not co-scheduled — every task on a196 and a220 started within 10 s of the previous one *ending* on that node
- [x] **ROUND 7 LAUNCHED 2026-08-26**, `EXCLUDE=a024,a088,a196,a220`, balance 79,275.4 SU at launch:
      - **`20148093`** wave, 4 rows `1-4%3` — 2 unchanged a220 re-runs + 2 resume-from-deepest (`Co s0_OOH__2x1v_off` from its 14th BFGS step, `Ni s0_OOH__2x1v_off` from its 1st), both at the beta that got there (0.3) plus ndim 16 and maxstep 500
      - **`20148101`** chains, 2 rows `1-2%2` — `Co s0_OOH__2x1v_mir` replay **with ndim 16 added** (deliberate deviation, recorded; convergence-path parameters cannot move the fixed point) and `Co ref__2x1v` → its owed `__g1` child (replay ≈996 SU, the parent took 7h47m)
      - preflight `lines=4 to_run=4 already_done=0 stale=0 bad=0`; 7 files md5-verified; both splices reproduce their source `.out` block to 0/39 mismatch with **zero frozen (`0 0 0`) atoms moved**
- [ ] **SCORING RULE for chain 1 (`20148101_1`):** if the replay converges at a different magnetization than the banked parent (20.13 / 22.91), the chain is **VOID** and the child must not be banked — the density it inherits would be the wrong branch's
- [x] **Branch rule now 10 for 10** with the Fe chain

## 2026-08-26 (round 7 scored, round 8 launched) — the resume idea works; the cluster is the bigger problem
- [x] **`Co s0_OOH__2x1v_off` CONVERGED.** 22 ionic steps, `bfgs converged`, min accuracy 3.9e-09, **1h34m / ~201 SU**. Resumed from attempt2's 14th BFGS geometry at the ORIGINAL beta 0.3 + ndim 16 + maxstep 500, and descended a further **392 meV** below attempt2's last banked ionic energy. Six attempts and ~1,000 SU of mixing escalation had failed on this deck. **It was never a mixing problem — it was a restart problem**
- [ ] **`Co s0_OOH__2x1v_mir` — TWO independent replays of the parent's own deck have now failed to converge.** ndim 16 made the replay WORSE (min 4.24e-04 vs the round-6 replay's 2.477e-05 at default ndim 8). Not a tuning problem any more: **the banked energy cannot be reproduced on demand.** R3 second half + A8.6 (FRANK). Deliberately NOT re-run in round 8
- [x] **The a223 measurement identifies the cluster fault.** Each bad node kills at its own tight ceiling — a196 at 8.65–8.70 GB (0.5% spread), a220 at 35.06–35.14 (0.24%), **a223 at 16.93–16.95 GB (0.1%)** — while every job was granted `mem=237G` and the same work on a healthy node peaks at 30–48 GB and finishes (`20148093_3`: 47.7 GB on a157, converged). That is a per-node shortfall between what Slurm believes is allocatable and what the node delivers
- [ ] **Exclusion is not converging: 5 nodes now (a024, a088, a196, a220, a223), a new one on each of the last three submissions.** ~1,100 SU lost to kills so far. **Deliberately NOT mitigated by shrinking the job** — the obvious lever, `-nk` pooling, changes MPI reduction order, and round 4 established reduction order is what selects the magnetic branch. `disk_io` is the one memory knob that cannot move a number; held in reserve
- [x] **RCAC ticket rewritten around the ceiling table** — five nodes, the MaxRSS clustering, the not-co-scheduled check, and the DRAIN-still-scheduling question. Still FRANK's to send
- [x] **ROUND 8 LAUNCHED**: **`20149862`** wave 3 rows `1-3%3` (Ni `_mir` + Mn basin unchanged, Ni `s0_OOH__2x1v_off .resume.in`) and **`20149866`** chain 1 row (`Co ref__2x1v` → the last owed wave-4 child). Decks unchanged, `EXCLUDE=a024,a088,a196,a220,a223`, preflight clean
- [x] **A8.8 near-miss caught:** `runs/s3/Co/ref__2x1v.out` is the BANKED PARENT (1,847,613 B), not a dead chain file — the chain's dead output is `ref__2x1v.replay.out` (10,131 B). Archived the latter only; verified both the banked parent and the newly converged `s0_OOH__2x1v_off.out` intact afterwards

## 2026-08-26 (round 8 scored, round 9 launched) — two-for-two on resumes; the S3 tail is nearly closed
- [x] **`Ni s0_OOH__2x1v_off` CONVERGED** — 41 ionic steps, `bfgs converged`, min 5.0e-09, E = −5198.77050468, magtot 7.89 / magabs 22.05. **This was the row recorded as "BRANCH, no parent to seed from, the one row with no registered remedy in hand."** It had ONE banked ionic step in attempt2 that four later rungs discarded; resuming from it ran 41 more. It never needed a remedy, it needed a restart
- [x] **Resume recipe is 2 for 2** on decks that between them survived ten failed attempts (`Co s0_OOH__2x1v_off` 22 steps, `Ni s0_OOH__2x1v_off` 41 steps)
- [x] **Round-7 selector was wrong and is fixed.** `deepest_attempt()` chose by MOST IONIC STEPS; for Mn that picks attempt1 (19 steps, E −3617.10180292) over the round-8 continuation (3 steps, E **−3617.10197097**) and discards three steps. **Once resumes chain, step count stops tracking depth.** `build_s3_round9.py` selects by lowest final energy within a magnetic branch, asserts no same-branch run is deeper, and prints the full census
- [x] **`mixing_ndim = 16` running score: 1 converged of 7, and two decks made measurably worse.** `Ni s0_OOH__2x1v_mir` collapsed to magtot −0.27 / magabs 25.70 (large moments cancelling) with 0 ionic steps at ndim 16, where three ndim-8 attempts all sat at 9.9–13.8 μB and descended to 3.2e-07. **Do not add ndim 16 to further decks without a specific reason.** Round 9 resumes it with ndim removed
- [x] **`Co ref__2x1v` replay is SLOW, not STALLED** — still descending monotonically (4.56e-06 → 3.81e-06) at iteration 500 against a 1e-06 target, where the parent converged cycle 1 in 324 iterations. Round 9 re-runs at maxstep 1500 (exactly two lines differ from the parent deck)
- [x] **Cheap explanation tested and DISCARDED:** that the banked parents were warm started from leftover scratch, which would have explained every replay failure and put the banked numbers' provenance in doubt. False — parents and replays all report `Initial potential from superposition of free atoms`, and `anvil/42_s3_wave1.slurm:59` `rm -rf`s scratch before every job. **The parents are genuine cold starts; the replay failures are real**
- [x] **ROUND 9 LAUNCHED**: **`20150995`** wave 2 rows (Mn second-generation resume; Ni `_mir` resume with ndim removed) + **`20151000`** chain 1 row (`Co ref__2x1v` replay at maxstep 1500 → the last owed wave-4 child). `EXCLUDE=a024,a088,a196,a220,a223`, preflight clean, 5 files md5-verified, zero frozen atoms moved in either splice
- [ ] **FRANK — the S3 tail is now three registered calls, not a compute problem:**
      - **R1 `upscale`** — would directly close `Ni s0_OOH__2x1v_mir` (held to 2.79e-07, reached 3.2e-07) and the `Co s0_OOH__2x1v_off` class
      - **R3 / A8.6** — `Co s0_OOH__2x1v_mir`: two independent replays of the parent's own deck failed to converge, and ndim 16 made it worse. The banked energy cannot be reproduced on demand
      - **`Co s0_O__2x1v_mir` + `Co s0_OH__2x1v_off`** — zero ionic steps in 4 and 5 attempts, no geometry to resume from, mixing ladder exhausted. R1, a new registered call (starting magnetization / diagonalization), or A8.4 rung-(iii) NOT_CONVERGED acceptance

## 2026-08-26 (round 9 scored, round 10 launched) — the retry ladder was chasing an undeclared threshold
- [x] **THE FINDING: three rows that consumed the entire retry ladder had already met the registered `conv_thr = 1.0e-06` and were refused by QE's undeclared `upscale` tightening.** Measured from the raw iteration traces: `Ni s0_OOH__2x1v_mir` att3 cycle 4 met it on **40 of 500** iterations (first at 52, min 3.2e-07, held to 2.791e-07); `Mn s0_OOH__2x1v_off__basin` att1 cycle 20 on **124 of 200** (first at 11, held to 1.0e-08); att5 cycle 4 on **489 of 500** (first at 9, held to 1.0e-08). QE exits at the FIRST crossing, so with `upscale = 1.0` Ni closes at cycle 4 iteration 52 and Mn closes at cycle 20 iteration 11 — **in the 34.76 branch, the lower one.** Rounds 4–9 spent ~6,800 SU on beta/ndim scans, resumes, replays and chains against rows that were converging all along
- [ ] **FRANK — R1 (`upscale = 1.0`) is now the single highest-value call in the campaign.** One line in `&IONS`. Changes no functional, cell, cutoff or k-mesh; it restores conformance with the `conv_thr` the protocol deposited rather than departing from it. A confirming pilot is ~50 SU and ~15 minutes if you want one before ruling
- [x] **GATE-1 measured across all 35 pairs on disk.** Child and parent are at byte-identical coordinates by construction, so every pair is an exact replicate. **29 rows at dmagtot ≤ 0.01 agree to ≤ 0.044 meV; 6 rows at dmagtot ≥ 0.18 disagree by ≥ 7.394 meV. Zero overlap, factor 168.** The branch rule is no longer a tally — it is a measured bimodal separation, and the 0.05 μB tolerance sits inside the empty gap
- [ ] **THREE BANKED PARENTS ARE IN AN EXCITED MAGNETIC BRANCH** — the fixed-geometry child lands BELOW its own parent, both sides converged, geometry verified byte-identical to full precision: `Fe s0_OOH__1x1_off` **−384.300 meV**, `Co s0_O__1x1_off` **−77.009 meV**, `Mn s0_OOH__2x1v_off` **−20.616 meV**. This is the pre-registered BASIN_DRIFT case (`docs/43:311-314`): ≥ 5 meV lower → re-relax from the child, loop until GATE-1 passes, and the child's energy is the corrected value. All three clear the trigger by 4×, 15× and 77×. **Every ΔG built on those three inherits the error**; the Fe row is 0.384 eV, larger than the overpotential differences the study exists to resolve **[2026-09-03, measured by `src/dft/gate1_census.py`: only TWO of the three reproduce from this repository. Fe (−384.300) and Mn (−20.616) re-derive exactly. The Co −77.009 meV does NOT: `s0_O__1x1_off__g1.out` and both its `.attempt` files say "convergence NOT achieved" and print no `!` total energy, and `s0_O__1x1_off__g1.fromparent.in` has no `.out` — the fromparent run happened on Anvil and its output was never pulled. The claim is not withdrawn; what may be SAID changes, and the fix is a file transfer, not compute. Do this before dispositioning R3/A8.8.]** **[SUPERSEDED SAME DAY 2026-09-03 — 'the fix is a file transfer, not compute' is WITHDRAWN. Anvil was searched exhaustively (every $HOME tarball listed): `s0_O__1x1_off__g1.fromparent.out` exists for Ni and two Cr_lit3 rows and NOT for Co, and the round-3 copy of the parent was extracted and reads 'convergence NOT achieved' with no `!` energy (md5 cffbcfd2a2e9df3dfb4afd73b8aed646). The remedy was NEVER EXECUTED, not merely never retrieved; the docs/43:317-320 affordability escape is also unavailable, since there is no converged GATE-1 energy to quote. Recorded as a RECORDED GAP. Closing it = ~5-19 SU + Frank's own A11.R3 dated line. See docs/43 Item 7.]** **[THAT SUPERSESSION IS ITSELF WITHDRAWN 2026-09-03 — the artifact EXISTS at /anvil/projects/x-che260157/sts/runs/s3/Co/s0_O__1x1_off__g1.fromparent.out (md5 b0d7c43ddb10c546819e2e9672231de8, converged, JOB DONE). The 'exhaustive' search had covered $HOME tarballs and /anvil/scratch but NOT /anvil/projects, where the run tree actually lives. PULLED and md5-verified both ends; -77.0089 meV re-derives exactly. The parent REPLAY was pulled too and independently lands in the same 11.24 branch at -76.691 meV, agreeing to 0.318 meV. Census now 89 children, THREE BASIN_DRIFT rows all re-deriving. THIS LINE'S ORIGINAL THREE-ROW CLAIM IS VINDICATED AS WRITTEN. See docs/43 'Item 7 CLOSED'.]**
- [x] **Contradiction RECONCILED 2026-09-03** (`src/dft/gate1_census.py`, `docs/figs/gate1_census.json`, `docs/research/2026-09-03-gate1-census.md`, 9 tests). The two counts answered different questions: docs/45 counted **A8.3 refusals post-discharge**, the line above counted **branch changes in either direction** — and a child 384 meV *below* its parent is BASIN_DRIFT, not a refusal. Measured over all **88** `__g1` children, zero orphans: 77 AGREE / 2 BASIN_DRIFT / 6 REFUSED (5 discharged by their `.fromparent` second attempt) / 3 UNVERIFIED. **"0 REFUSED" is now stale**: `s3/Co s0_OOH__2x1v_mir__g1` stands refused at +747.449 meV. Bimodality holds on 77 scored pairs (same-branch max 0.0439 meV strictly below the next band's 0.0903), and the census re-derives docs/45's hand-recorded Ni chain-2 discharge at +0.012 meV
- [x] **Round 9 `Mn s0_OOH__2x1v_off__basin` converged — and should be REFUSED, not banked.** 13 ionic steps, `bfgs converged`, min 3.3e-09 — but at magtot **35.00** against the 34.76 it was spliced from, with step 1 landing **+54.395 meV** above attempt5's step 3 at essentially the same geometry. A descending BFGS step cannot raise the energy 54 meV. A8.3 refuses anything > 1 meV above; this is 39× that
- [x] **Round 9 `Ni s0_OOH__2x1v_mir` failed informatively** — resuming from attempt3's own geometry and deck collapsed magtot 27.94 → 3.23 inside 41 iterations, then oscillated 1.37–2.16 for ~460 more with no ionic step completed
- [x] **Chain `20151000` KILLED at 9h50m (~1,250 SU, was heading for 6,144).** Its step-1 SCF is bit-identical to the banked parent for three iterations and splits at **iteration 4 of 325** — 496 iterations before `electron_maxstep` could ever bind, so the raised maxstep was never the operative variable. By step 3 it sat **110.839 meV above** the banked energy of record. `docs/43:1584-1588` already rules that a fixed-geometry re-run sitting above its parent "is a diagnostic, not a result". Replay preserved as `ref__2x1v.replay_ms.out.attempt1`; banked parent verified intact at 1,847,613 B / md5 `0a81fd3a86484b988c4fb476fbcf2521`
- [x] **INFRASTRUCTURE AMENDMENT — converged densities are now retained.** `anvil/42_s3_wave1.slurm` and `anvil/44_chain.slurm` were deleting every charge density they ever produced (unconditional `rm -rf` on scratch). That density is the only thing that pins a magnetic branch, so A8.3 has had to re-derive it by replaying a whole parent relax: **41 min–7h47m (~1,000 SU) against a median 6 min (~13 SU) for the child SCF itself**, landing in the parent's branch 2 times in 5. Both scripts now keep `<prefix>.save` (~76 MB; the multi-GB `.mix*`/`.wfc*` bulk still goes) for any run whose every SCF converged. ~0.0015% of quota per run, currently 0.8% used. **No calculation changes**
- [x] **That explains the one A8.3 chain that failed.** `Co s0_O__1x1_off__g1.fromparent` came back −77.009 meV at dmagtot **0.45** — and its replay was **0.45** off the parent. The seeded child faithfully inherited the replay's branch, exactly as a correctly seeded child should. Seeding works; the replay it depends on is the weak link
- [x] **ROUND 10 LAUNCHED — array `20161825`, 5 rows, `1-5%1`.** Every row is a GATE-1 child re-rolled under a new prefix; each deck differs from the one on disk in exactly one line, the prefix, verified line-by-line at build time, so nothing is overwritten (A8.8). Preflight `lines=5 to_run=5 already_done=0 stale=0 bad=0`; 8 files md5-verified both sides. **Group A** (3 rows) banks the anchor density on the BASIN_DRIFT rows; **Group B** (2 rolls) re-rolls `Co s0_OOH__2x1v_mir__g1`, the mirror case where the parent is right (magtot 20.13) and the child sits 747.449 meV above it at 24.86
- [ ] **`Co ref__2x1v__g1` still not built.** Its cold child ran 500 iterations, completed no SCF cycle, sat at magtot 24.11 against the parent's 21.66; three later attempts have all fallen into a 23.5–24.1 region that will not converge. It wants a `starting_magnetization` near the parent's converged moments — **a new registered call, FRANK's**
- [ ] **Untried lever, noted by the refutation pass:** every resume deck in this campaign kept the COLD `starting_magnetization` (Co 0.4, Ni 0.3, Mn 0.5) — not one carries its parent's converged moment. That is a one-line input change nobody has tested
- [x] **FOUR OF MY OWN CLAIMS WERE OVERTURNED by an adversarial pass and are corrected in `docs/45`:** (1) "R1 would not close `Ni s0_OOH__2x1v_mir`" — withdrawn, I read the tail of a non-monotonic series as its minimum; the ledger's original claim was right. (2) "The lower 34.76 branch will not converge" — withdrawn, it shows 19 consecutive converged cycles at the 1e-08 floor in 9–15 iterations each. (3) "`Co ref__2x1v` cannot be reproduced" — withdrawn as stated; round 8's replay reproduces it to **0.167 meV and 0.08 μB**, and I never opened that file. (4) The branch rule's tight bound was quoted as 0.52 meV; measured it is **0.044 meV**
- [ ] **Housekeeping:** ~11.5 GB of dead scratch under `runs/s3/Co/tmp_chain_*` (the `.save` inside each is only 76 MB; the rest is `.mix*`). Cleanup was blocked by the sandbox and is not urgent at 0.8% of a 5 TB quota
- [ ] **Still owed and unchanged:** RCAC ticket (`anvil/rcac_ticket_draft_2026-08-24.md`, FRANK to send); methods correction on the 1e-6 vs 1e-8 SCF threshold (FRANK re-authors — the `upscale` measurement above is the evidence for it); S0(h) RuO2 AFM re-anchors; S4 (`runs/probe/Co_uladder` has 12 built-but-unrun decks); A10 Sep 18; Oct 15 hard freeze

## 2026-08-28 (A0 wave 1 scored, A0-main actually launched) — P-PROJ fires at 5x threshold; "A0 done" was only 22 of 162 SCFs
- [x] **CORRECTION OF RECORD: A0-main had never been submitted.** The 140 decks were staged 2026-08-27 (`74323dd` says so: "staged, not yet submitted") but no array existed — `sacct` since 08-27 shows only 22 `a0` tasks (16 cell + 6 p_proj) and an empty queue, `main/` had 140 `.in` and zero `.out`. **Submitted 2026-08-28 as array `20183040`, 1-140%6**, preflight `lines=140 to_run=140 stale=0 bad=0`, `EXCLUDE=a024,a049,a050,a088,a196,a220,a223`
- [x] **P-PROJ SCORED — THE A7.1 PREDICTION FIRES, |Δη(Cr)| = 0.487 V vs the 0.10 V threshold.** atomic η 1.155 V (pls 2) vs ortho-atomic η 1.642 V (pls 1) at identical geometry and U = 7.15: the projector choice moves the eta by half a volt AND flips the potential-limiting step. All four pairs branch-matched (magtot 12/12, 11/11, 10/10, 11/11 — no mismatch to average away); per-state dE = +3.0 to +4.0 eV, atomic above ortho every state; banked *O pair reproduced to <0.0001 meV. Per A7.1: **the fifth grid point is PROJECTOR-MISMATCHED, the whole η(U) grid runs in ONE projector (atomic), the 0.487 V delta is its own labelled sub-row, and Xu's linear-response U values may NOT be silently imported as anchors.** `src/dft/pproj_readout.py`, `docs/figs/pproj_readout.json`
- [x] **A0-cell wave 1 banked: 15 of 16 converged clean**, extraction control ≤0.01 meV on all four states (base SCF vs source relaxation — the 2x1v geometry round trip is faithful). Magnetization U-flat per state (ref 24, s0_O 22, s0_OH 23, s0_OOH 23 across U = 0→5), consistent with the A6.2 additive prior's mechanism
- [x] **Task 9 (`s0_OH__2x1v_mir__u0.0`) died OUT_OF_MEMORY on a049** — 3 oom_kills at SCF iteration 5, QE's own estimate 29.21 GB on a 237 GB grant, identical siblings passed on other nodes in 6–13 min. **a049 is bad-node #7** (pattern of docs/45's per-node ceilings). Attempt preserved as `.out.oom_attempt1`; **retry = array `20183041_9`**, a049 added to EXCLUDE
- [x] **A0-cell fifth rung built AFTER P-PROJ scored, exactly as A6.1(b)/A7.1 sequence requires**: 4 decks, each byte-asserted = its state's `__base` deck + {prefix, U 3.7000→7.1500}, run in the ladder's own atomic projector, every future row labelled PROJECTOR-MISMATCHED. `src/dft/build_a0cell_u715.py`, `runs/a0/m_a0cell_u715.txt`, **array `20183150`, 1-4%4**
- [x] **A6.2 partial signal (VERDICT WITHHELD until u0.0 retry + u715 land):** dD = D(2x1v) − D(1x1) at the three complete shared points is systematically negative and growing: −0.233, −0.304, −0.346 eV at U = 1.85, 3.70, 5.00. If the trend holds at the end points, span(2x1v) < span(1x1) and I_U lands negative, possibly past the −0.30 "not separable" bin — **the additive prior is under pressure.** `src/dft/a0cell_readout.py` (runs on partials, withholds the registered quantity)
- [x] **The 1x1 leg reproduces P7's swing exactly: η(U=0) − η(base) = 1.452 − 0.330 = 1.122 V** on the inherited ladder + P-PROJ atomic fifth point — the withdrawn headline's number, now bracketed on 5 points; A0-main's 19-point Cr grid will locate the crossing
- [x] Löwdin banking choice: projwfc.x ran inline per A6.5(1); the registered artifact ("a few kB of text") is banked as `<job>.lowdin.txt` per deck; the ~4.3 MB full projection bodies + pdos files are retained on Anvil beside the decks, not in git
- [x] **When `20183040`/`20183041_9`/`20183150` complete:** pull, QC, escalation ladder on any non-convergent point (A6.5(2): startingpot from converged neighbour → halve beta → NOT_CONVERGED gap); then the registered readouts — P7 bound + crossing location (Cr 19-point), Ir < Ru ordering across U ∈ [0,9] with Xu anchors labelled (A6.3), pls-flip census (A7.2: ≥3 of 6 metals predicted), I_U verdict + crossing-shift (A6.2)
- [ ] Pre-existing dirty files NOT touched by this session: `.github/ci/run_oc20.py`, `.github/workflows/s1-controls.yml` (S1 CI handoff, docs/57) — FRANK/other session to commit or drop

## 2026-08-28 later (wave 2: cell CLOSED, Cr arm scored + verified, Ru/Ir tail queued)

- [x] Cell arrays landed: retry `20183041_9` converged (same SCF branch as the OOM-killed attempt), `20183150_1-4` u715 rung converged -- **A0-cell 20/20, zero SCF failures**; A0-main `20183040` Cr 76/76 + Ru 15/32 pulled; Löwdin extracted remotely, only the registered few-kB extracts pulled
- [x] **A6.2 VERDICT: I_U = -0.201 eV -> INCONCLUSIVE** (prior on record was additive; clean-point robustness -0.155, same bin); **crossing shift 1.47 eV -> the located-crossing claim is CELL-CONDITIONAL** (clean-point lower bound 1.13 eV > 1.0, so the verdict does not rest on the PROJECTOR-MISMATCHED u715 rung)
- [x] **Cr location arm (trusted, 19/19): eta(U) V-shape, min 0.381 V at U=3.5; apex crossing inside [3.5, 4.0], interpolation 3.87 eV [CELL-CONDITIONAL per A6.2]; pls flip 3->2 in that bracket; swing 1.177 V over [0,9] (edge-limited, eta still rising at U=9) vs 1.072 V restricted to P7's own [0,7.15] window -- neither confirms the withdrawn 1.122 V headline, windows differ**
- [x] Four-verifier adversarial audit BEFORE banking (docs/figs/a0_verification_findings_2026-08-28.txt): 0 BLOCKERs, every number reproduced to 1e-10; 5 distinct MAJORs all fixed same-day (grep-masked crash/version skew, label-travel into JSONs, window-mismatch phrasing, circular determinism-only control renamed, vacuous A6.3 line -> WITHHELD); ledger updated (docs/45)
- [x] cell manifest.json updated to 20/20 with the A7.1 gate outcome on the u715 rung
- [x] **Array 20183040 COMPLETE 140/140** (zero failures, zero A6.5(2) events; Ru s0_O u673 confirmed run) -- pulled, QC'd 64/64, Löwdin extracted + provenance headers restored
- [x] **A6.3 VERDICT: INVERTED at U = {4.5, 6.0, 7.5, 9.0}** (margins +0.021/+0.177/+0.340/+0.464 V; only U=9.0 clears every measured error class; holds-side margins all below the registered 0.20 eV floor -- ordering never positively resolved anywhere). **A7.2: CONFIRMED** (Cr/Ir/Ru all flip; Ir bracket saddle-conditional). Refuter: INVERTED SURVIVES, in-model volcano physics
- [x] Gas-reference disclosure shipped (md5-identical H2O/H2 across metals, measured live; sentence scoped -- different-pls comparisons inherit the absolute H2O reference)
- [x] Wave-3 four-verifier audit BEFORE banking (wf_5bd5616f-7e4): 0 BLOCKER / 6 MAJOR, all fixed same-day (margins banked, labels into JSON, A6.4 + spin-state + saddle + coverage caveats travel, RY_EV single-sourced); findings appended to docs/figs/a0_verification_findings_2026-08-28.txt; ledger updated (docs/45 wave 3, 5 new traps)
- [x] **A0 tranche 2+3 BUILT 2026-08-28 (entrant direction: "Do them over Mn/Fe/Ti then")** -- Mn 32 (REF_GRID + u390 production control) + Fe 24 + 3 s0_OOH branch pilots (u530, mags 0.1/0.3/0.7, selection rule REGISTERED in build_a0main_w2.py before launch: |E - (-34804.1641)| <= 5 meV, else BRANCH-CONDITIONAL at 0.5); Ti chain stage 1 = 4 TiO2(110) relaxes (qe_slab build Ti --supercell 1, d0/nspin=1/U=0, S0-verified pseudo); docs/59 = the dated roster correction DRAFT
- [ ] **Frank: countersign + deposit docs/59** (covers the 2026-08-27 allocation AND the 2026-08-28 extension; own record or with A10 Sep 18)
- [x] **Tranche 2 LANDED 2026-08-29** (20196817 59/59 COMPLETED): QC 57/59 clean, 57 Löwdin extracted, pulled (md5-verified tar). **Fe pilot verdict: ALL THREE PASS** (0.019-0.023 meV vs -34804.1641 eV; totmag 22.98 = relax branch) -> closest wins m010, ladder at mag 0.1; u530 rung = byte-identical determinism control vs the pilot deck. **First A0 SCF failures: Fe s0_O u300/u450** (200-iter magnetic oscillation) -> A6.5(2)(i) `__r1` restarts from retained u150/u530 densities, runner 48_a0_repair.slurm (46 + density seed, projwfc KEPT). Ledger updated (docs/45, traps 6-7: byte-claims need byte-compares; repair paths must carry the main path's invariants)
- [x] **Ti stage 1 LANDED 2026-08-29** (20196856 4/4 COMPLETED): slab/s0_O/s0_OH bfgs-converged; **s0_OOH FAILED** (step-2 SCF, 200 iters, 0.0097 Ry) -> A6.5(2)(ii) s0_OOH_r1 (beta 0.15, last trajectory geometry spliced verbatim). Stage 2 BUILT (build_a0main_w3.py): 3 probe-style bases (probe/Ti_audit, provenance "final") + 21 REF_GRID rungs (u000 = byte-identical production/determinism control; nonzero rungs append HUBBARD U Ti-3d); s0_OOH base+rungs GATED on r1
- [x] **Tranches 2b/3-stage-2 LANDED 2026-08-29** (20204305/6/7/8, 35/35 COMPLETED): **Fe *OOH ladder 8/8** (u530 = the pilot rerun, totmag 22.98 relax branch), **Ti stage 2 21/21 + 3 bases** (u000 rungs reproduce their bases to <=3.3e-7 Ry), **Fe s0_O u300 REPAIRED by rung (i)** (seed u150 -> totmag 22.90, 202 s). 33 new Lowdin extracted; pulled md5-verified (577dca09), zero committed decks altered; commit 7c84ec9
- [x] **Tranche 2c REGISTERED + LAUNCHED 2026-08-29** (build_a0main_w2c.py, committed before submit). **Fe u450 rung (i) FAILED** (held totmag 21.98, plateau ~1.5e-5 Ry vs conv_thr 1e-6, 200 iters) -- it is the CROSSING between the 22.90 branch (u300) and the 21.98 branch (u530+), so rung (ii) halves beta from BOTH legal converged parents (`__r2` u530, `__r2b` u300__r1); lower converged energy pre-declared as the banked point, difference reported as the branch splitting at U=4.5. **Ti s0_OOH rung (ii) FAILED and the cause is GEOMETRIC**: qe_slab starts every Ti adsorbate ~3.2 A off the nearest Ti; *O and *OH walked DOWN to 1.735/1.829 A over 36/56 steps, *OOH walked UP (3.167->3.414 A) into the desorbed-radical region nspin=1 cannot describe. local-TF was ALREADY on campaign-wide (qe_slab.py:175), so the ladder is exhausted -> `s0_OOH_r2` (continue the walk) + `s0_OOH_r3` (re-anchored to mean(1.734553, 1.829256) = 1.781905 A, adsorbate translated rigidly, substrate untouched), both +mixing_ndim 16 / maxstep 400 as a DATED, BOUNDED ladder extension (docs/59 s3c: can only FILL the gap (iii) would leave). Ledger traps 8-10
- [x] **Tranche 2c LANDED 2026-08-29** (20214003, 20214014): both pre-declared selection rules applied mechanically. **Fe u450: exactly one converged** -- r2b (22.90-branch seed) in 18 iters at totmag 23.44; r2 (21.98-branch seed) failed, the THIRD failure on that branch -> the 21.98 solution does not exist at U=4.5. **Fe now 8/8, no holes.** **Ti s0_OOH: r3 (re-anchored) CONVERGED** (52 ionic steps, zero SCF failures, force 0.0031), r2 (plain continuation) failed again -> **TiO2 BINDS *OOH at d(O,Ti)=2.041 A** (vs *O 1.735, *OH 1.829); the 'desorption' was a start 1.1 A outside the bond. Commits 903f15f, bae6cd2
- [x] **Wave-4 audit before banking** (59 agents; 53 raised / 38 refuted / 15 survived + 9 sweep; docs/figs/a0_verification_findings_2026-08-29.txt). BLOCKER: pending repairs were reported as convergence failures (found by 3 dimensions independently). **A7.3 was never scored while its sibling A7.2 was** -- now scored: **3 of 5 vs registered >=4, NOT YET MET, Ti deciding**. Plus Ti gap-causality, the Ti spin caveat's false 'no moment to order' (151/157 electrons = odd), a control regression I introduced yesterday, Mn's unmet A7.5 AFM condition, provenance stamping, and 5 corrections to my own numbers. Ledger traps 12-17
- [x] **Ti stage 3 LANDED 2026-08-29** (20215155, 8/8 COMPLETED exit 0:0, 2:58-7:20). All converged, zero SCF failures, Lowdin extracted; md5-verified both ends (45df475e), zero tracked files altered. **Determinism control: base vs u000 byte-identical decks except prefix, DIFFERENT nodes (a211/a215), agree to 4.1e-7 Ry = 5.6 ueV.** Geometry-splice control: base SCF reproduces the r3 relax final energy to 1.6e-7 Ry. E(U) smooth+monotone (dE/rung 0.654->0.562 Ry). Independent CHE re-derivation of all 7 Ti rows reproduces the scorer exactly. Regression vs bae6cd2: Cr/Ru/Ir/Mn/Fe **bit-identical** (max|delta| 0.000e+00)
- [x] **A7.2 CLOSED: CONFIRMED at 5 of 6** (Ti is FLAT -- no flip, so the census is 5/6 not 6/6). Robustness now banked: Fe and Ru each rest on a SINGLE row inside a measured error class, leaving **exactly 3 robust members (Cr, Ir, Mn) against the registered >=3 -- zero margin**
- [x] **A7.3 DECIDED: NOT MET at 3 of 6** (Ti span/2 = 0.0438 V, below the 0.10 floor). A REGISTERED PREDICTION FAILS. Five conditionality facts banked in a7_3.conditionality: (1) the 3-over/3-under split is **exactly** the nspin=2/nspin=1 partition -- perfectly confounded; (2) **Ru is 15.5 meV from flipping the verdict**, inside the still-open NM-vs-AFM class (33-64 meV) whose S0(h) re-run is owed and acts on exactly that metal; (3) Fe and Mn set c_M(9) on pls-1 rows with negative dG3; (4) 3-of-6 is in a band the registration does not define and 'NOT MET' is not in A7.7's vocabulary; (5) the Ti rows are contingent on an UNGRANTED A6.6 licence -- if withheld, denominator 6->5 and status reverts to NOT YET MET
- [x] **Wave-5 audit before banking** (47 agents; 38 raised / 26 refuted / 7 survived + 7 critic; 5 verifiers died on API safeguards and were re-checked by hand, not counted as refuted). Fixed: my gen_rutile.py misattribution (the module emits no slabs at all -- it is qe_slab.py + surfaces_rutile), my corrupted w2c registration docstring (a botched edit inverted which Fe branch converged), the missing s0_OOH probe_manifest record (GATE 1 could not see the state that DECIDES A7.3), and **A5.1(b) had been applying its registered 0.20 eV G_max-gap floor to eta margins -- the wrong quantity -- with leg 1 never evaluated**. Ledger traps 18-24
- [x] **docs/60 written** (blind-metal extension, end to end) + dated supersession notes in docs/58 SS4/SS5/SS7/SS8
- [x] **A0-SPIN REGISTERED + STAGE 0 LAUNCHED 2026-08-29** (commit 87ea24e, pushed BEFORE submit; array 20221409, 10 jobs). docs/61 = Amendment 11 DRAFT; src/dft/build_a0spin.py = the builder, 12 fatal build-time assertions. **THE REFRAME: A7.3 scores span(c_M)/2 at FIXED endpoints, so a U-INDEPENDENT spin offset CANCELS EXACTLY** -- the arm moves the score only through D_M = dc_M(9) - dc_M(0), never through the size of the spin effect. **The arm's free half already existed**: 8 nspin=2 SCFs banked at runs/probe/{Ru,Ir}_spin/ (P11 FM leg, 2026-08-07), geometries verified byte-identical to the A0 u000 decks -> **dc_M(0) = Ru +7.145 / Ir -8.705 meV** while individual state energies move up to 174 meV. **Ru crosses the floor iff dc_M(9.0) <= -8.35 meV.** **BLOCKER CAUGHT IN DESIGN: the metal's species index is STATE-dependent** (slab/s0_O = [M,O] -> 1; s0_OH/s0_OOH = [H,M,O] -> 2); a per-metal constant would have seeded OXYGEN on half of every ladder and returned the nspin=1 answer at 2x cost. Same trap for nosym/noinv (Ru/Ir carry them on slab only)
- [ ] **When 20221409 drains: read Stage 0 before Stage 1 is built.** 8 decks must reproduce the banked P11 energies (also the campaign's ONLY cross-machine determinism control on a spin-polarised code path); 2 null-seed decks -- one of EACH ntyp class -- must reproduce the banked nspin=1 Ti energies at totmag ~0. An all-ntyp-3 control set would be structurally blind to the index rule
- [ ] **FRANK, items 1-4 of docs/61 gate the first SCORED deck:** (1) the headline-census election -- **recommended: the as-built 3-of-6 STAYS the headline and the equalised census is a sensitivity**, because trading "a registered prediction that failed" for a contested 4-of-6 across a 15.5 meV line, under a convention chosen after reading the failure, is a bad trade for the STS package; (2) the seed set {0.10, 0.30, 0.50} + selection tolerances; (3) P-SPIN-DELTA's movement threshold (proposed >=0.033 eV on >=2 of 3, the bottom of gate (h)'s measured class); (4) **docs/59 SS3c countersignature, which sets the denominator and gates every Ti deck beyond Stage 0**
- [ ] **Frank: the A6.6 licence decision (docs/59 SS3c) now has a MEASURED consequence** -- granting or withholding it moves A7.3's denominator 6<->5 and its status. Countersign + deposit docs/59
- [ ] **Frank's call, deliberately not made here: should the Ti arm run nspin=2 throughout?** Strictly more general (closed shell -> totmag 0 -> the nspin=1 answer) and removes the *OOH radical pathology at the root, but it is a CONVENTION change across 4 states + 24 banked SCFs. docs/59 s3c
- [ ] Registered zero-DFT readouts still unscored: **A5.1(a)** valence classification -- the Ti Lowdin extracts complete the coverage and **no script in the repo reads a .lowdin.txt at all**; for Ru/Ir/Ti the nspin=1 decks make the moment tracker structurally unavailable, so Lowdin is their ONLY valence tracker, and those three are exactly A7.3's under-the-floor set. **A5.1(c)** G_max maps (the g_max machinery now exists in the readout). ~~A5.1(d) intercept test~~ -- **its number is already banked** in a7_3.per_metal (the scaling intercept IS c_M): cross-metal mean 3.478 -> 2.883 eV, spread 3.03x, against the registered prior that the intercept stays U-robust. ~~A7.3~~ SCORED
- [ ] **NO LONGER OPTIONAL: the S0(h) RuO2 AFM re-anchors act on Ru, which sits 15.5 meV from flipping A7.3 from NOT MET to CONFIRMED.** This re-run can change a banked verdict. Bundle the AFM spot-check of the U=4.5 ordering point (margin 0.021 V, same class) with it
- [x] Analysis doc: docs/58 covers waves 1-3; **docs/60 covers the blind-metal extension and both verdicts**, with dated supersession notes added to docs/58 where the landing made it false
- [ ] Frank: RCAC ticket; `.github/ci/run_oc20.py` + `.github/workflows/s1-controls.yml` still dirty (S1 CI handoff, docs/57)

## 2026-08-30 (A0-SPIN Stage 0 READ) — the machinery passes, one registered criterion was unsatisfiable, and the arm's live metal is Ti

- [x] **Array `20221409` DRAINED 10/10 COMPLETED exit 0:0** (02:22-08:41, nodes a161/a224/a225/a227/a229). Outputs pulled and committed under `runs/a0/spin/`, md5-verified both ends (tar `ccfe1ab3af1f04f8be47e8e1430f082c`, 20/20 per-file match); zero tracked files altered. **docs/62 = the readout**
- [x] **The index rule HELD on both `ntyp` classes.** Read from the decks as run: `slab`/`s0_O` carry `starting_magnetization(1)=0.50, (2)=0.0`; `s0_OH`/`s0_OOH` carry `(1)=0.0, (2)=0.50, (3)=0.0`. The metal, and only the metal, was seeded on all 8 decks. The blocker `build_a0spin.py` exists to prevent did not occur
- [x] **Control set 1: 8/8 reproduce the banked P11 energies to <= 3.21e-6 Ry = 0.0437 meV.** Stronger than the "different nodes" control the campaign has been quoting: P11 ran **7 Aug on 4 MPI cores**, Stage 0 ran **29 Aug on 128 cores** — same QE v7.5, a **32x different FFT/band decomposition** (completely different summation order), 22 days apart. **The derived quantity reproduces to 0.052 meV: Δc_M(0) = Ru +7.094 / Ir −8.727 meV vs docs/61's banked +7.145 / −8.705.** Measurement floor sits **~300x below** the 15.5 meV that decides Ru
- [x] **Guard 1 (symmetry/k-set): 10/10 PASS** — every equalised deck matches its as-built twin on both the `Sym. Ops.` line and the k-point count (slab 32; s0_O 15 at 4 ops; s0_OH/s0_OOH 15 at 2 ops; Ti 32). No row is disqualified from being differenced
- [x] **Guard 2 (variational floor): 7/8 PASS, and the 8th fired exactly where docs/61 said it would.** Ir slab at seed 0.50 lands **+0.583 meV ABOVE** its nspin=1 counterpart at absmag 0.16 — docs/61 §A11.7 predicted +0.592 from the banked P11 data, so the search failure reproduces cross-decomposition and is a property of the SEED, not the machine. **Scope: E_slab cancels identically in c_M, so A7.3 is untouched; it binds on every ΔG/η and therefore on any A7.2 re-read (decision item 8).** Seeds 0.10/0.30 are two more shots in Stage 1
- [x] **CONTROL SET 2 DID NOT DO WHAT IT WAS REGISTERED TO DO, and what it did instead is worth more.** Both Ti decks ran every `starting_magnetization = 0.0`. **Ti `slab` (144 e, EVEN): totmag −0.00 at all 25 iterations, energy within +0.339 meV — the repo's "null seed is a fixed point" claim is CONFIRMED for closed-shell decks.** **Ti `s0_OOH` (157 e, ODD): the SCF SPONTANEOUSLY BROKE SPIN SYMMETRY** — totmag 0.01, 0.00, 0.10, 0.20, −0.03, 0.00, 0.00, **0.43, 1.00**, ... locking at 1.04 over 47 iterations, driven by nothing but QE's own `Starting wfcs are 117 randomized atomic wfcs` — and landed **153.072 meV BELOW** the banked nspin=1 row
- [ ] **CORRECTION OF RECORD (docs/62 §5.2, FRANK to authorise): docs/61 §A11.7's criterion for the `ntyp=3` null-seed deck is UNSATISFIABLE AS WRITTEN.** "Reproduce the banked nspin=1 Ti energies with totmag ≈ 0" cannot be met by any converged nspin=2 run on a state whose unpolarised solution is unstable. Proposed replacement in two legs: **(a) index-rule leg — PASSES as run; (b) stability leg, reported not scored — Ti `s0_OOH` at U=9.0 BREAKS, >= 153.07 meV, label the banked row SPIN-UNSTABLE.** Must be authorised before any Stage-1 row is scored against §A11.7
- [x] **153.07 meV is a LOWER BOUND, not an estimate** — no moment was ever requested and no registered seed search was run; the SCF found whichever branch numerical noise pointed at. A seeded search can only go lower
- [x] **The parity is STRUCTURAL and it lands on exactly the two states c_M is built from.** Read from the as-built decks: `slab` 168/162/144 and `s0_O` 174/168/150 are EVEN on Ru/Ir/Ti; `s0_OH` 175/169/151 and `s0_OOH` 181/175/157 are ODD. c_M = ΔG_OOH − ΔG_OH keeps exactly the two odd-electron states and cancels exactly the two even ones. **So on all three nspin=1 metals every term entering A7.3's quantity is an odd-electron state described as a closed shell** — docs/61 §A11.8 item 1 said "three-metal problem"; it is a problem confined to, and unavoidable in, the numerator
- [ ] **THE ARM'S LIVE METAL IS Ti, NOT Ru — and docs/61 was written around Ru.** Ti needs **D_Ti <= −112.5 meV** to cross the 0.10 V floor (docs/60 §6). One of D_Ti's four state-endpoint legs is now measured at **−153.07 meV — larger than the whole distance Ti has to travel — and it is a lower bound.** Ru's entire measured spin effect on c_M at U=0 is +7.094 meV; Ti's single-state effect at U=9 is **~22x larger**
- [ ] **BUT THE A11.1 REFRAME BINDS AND MUST TRAVEL WITH THAT SENTENCE.** D_M = Δc_M(U_max) − Δc_M(0), so **a U-independent offset cancels EXACTLY**. Three of D_Ti's four terms are unrun (Ti \*OH at U=9; both states at U=0). If Ti \*OH at U=9 shifts comparably, Δc_M(9) is small; if Ti \*OOH at U=0 shifts comparably, D_Ti is small. **Stage 0 licenses NO statement about D_Ti's sign or magnitude** — only that the SCALE on Ti is ~150 meV rather than the ~10 meV seen on Ru/Ir, so Ti's leg is a live measurement and the cancellation is the entire question
- [ ] **GOVERNANCE CONSEQUENCE, and it is the awkward one: the most informative half of the arm is the half gated on docs/59 §3c, which is still uncountersigned.** docs/61 §A11.10 sequenced Ti LAST on a governance argument that is unchanged and still correct — physics interest does not license spending SCFs on rows that may be WITHDRAWN-UNSCORED. But **decision item 4 has moved from bookkeeping onto the critical path**, against an Oct 15 hard freeze
- [ ] **Stage 1's Ti leg, once licensed: `s0_OH` + `s0_OOH` at u000 and u900 x 3 seeds = 12 SCFs.** `Ti s0_OH__u900` is the single highest-information deck in the arm — it is the term that decides whether the 153 meV cancels. If ANY Ti compute is licensed, license that one first. (A re-read of A7.2 on equalised Ti rows needs `slab` + `s0_O` at both endpoints, 12 more.) The null-seed run already supplies a free fifth candidate at (s0_OOH, u900): −1298.17043625 Ry at totmag 1.04, admissible to the §A11.6 selection rule
- [ ] **NEW open item: the Ir-slab contingency.** If none of {0.10, 0.30, 0.50} clears the variational floor on the Ir slab, Ir has no spin-equalised slab row and therefore no equalised η. docs/61 does not cover this. Decide: WITHDRAWN row, extended seed set, or stated omission
- [ ] **Frank's "should the Ti arm run nspin=2 throughout?" (docs/60 §11) now HAS EVIDENCE:** >= 153.07 meV is the measured cost of the nspin=1 convention at one point of the Ti ladder. Still a convention change across 4 states and 24 banked SCFs; still Frank's call
- [ ] **Ledger-cap collision, deadline Sep 20 (docs/43:1930).** The six-row body-figure ledger is ALREADY at cap (P7, P-PROJ, P-PLS, P-FLOOR-U, P-SYMCOV, P-BEEF) and A11 adds **two more** predictions (P-FLOOR-U-SPIN, P-SPIN-DELTA) — docs/61 decision item 11. The displacement decision is owed in writing before Sep 20 and now has two more claimants than when it was adopted

## 2026-08-30 later (the owed S0(h) AFM compute) — built, held by the deposited registration, and the 33-64 meV class re-projected

- [x] **THE OWED COMPUTE IS BLOCKED IN THE DEPOSITED TEXT, NOT BY SCHEDULING.** docs/43:1645 (ADOPTION NOTE 2026-08-23, inside the deposited amendment) leaves the gate-(h) AFM family's scope open: four standalone S3-class relaxations, or the Ru second seed inside tier_v3's crossed magnetic-basin factor (**up to 16**), and says in terms **"No default was drafted ... the resolution is the entrant's to write in a dated line. Until he does, the gate-(h) AFM relaxations remain HOLD."** A 4x deck-count and SU difference. **Not mine to resolve.** (docs/51's older "HOLD on A8 / undeposited" line is STALE — A8 was adopted 2026-08-23; it is this family specifically that the amendment left open. Superseded in docs/63 §2)
- [x] **THE HOLD IS NOW ENFORCED BY CODE, NOT BY MEMORY.** `src/dft/build_h_afm_relax.py` writes the DECKS unconditionally (they cost no SU and the 2x1v/off arm is common to BOTH readings) and **refuses to write the launch manifest** until a dated line appears in docs/43 whose machine-readable head is exactly `[AFM-SCOPE RESOLVED YYYY-MM-DD: STANDALONE_FOUR]` or `[... : SECOND_SEED_CROSSED]`. Frank's own sentence goes on the same line; only the bracketed head is parsed. Exit 2 = held
- [x] **All four relaxation decks BUILT and assertion-checked** (`runs/s0/h_afm_relax/`). 13 fatal build-time assertions in the build_a0spin.py idiom. The transformation is deliberately trivial and therefore auditable: the banked SCF parents already carry `&IONS ion_dynamics='bfgs'`, `tprnfor`, `forc_conv_thr=2.0d-3`, `nstep=200`, so **each relaxation is its parent with EXACTLY TWO LINES CHANGED — `calculation` and `prefix`** — and A10 pins the diff to exactly those two rather than trusting it. Verified by diff on all four
- [x] **FIXED: `probe_decks.py` could not see a single atom of an AFM deck.** `_ELEMENT_RE = ^[A-Z][a-z]?$` was applied to every ATOMIC_POSITIONS line; the registered AFM idiom splits the metal into two species LABELS `Ru1`/`Ru2` (identical mass + pseudo, opposite seed) and neither is an element symbol. Every position line was skipped and the deck parsed to **ZERO ATOMS, silently** — no exception, no warning. Now keys off the labels the deck DECLARES in its own ATOMIC_SPECIES (the read-it-from-the-deck rule); widened pattern kept only as the `.out` fallback. All four now parse at nat=36/37/38/39, matching each deck's own `nat`. **154 passed + 20 new, no regressions**
- [x] **The state-dependent species-index trap is present in this family too, and the banked parents got it RIGHT.** ref/s0_O are ntyp=3 [Ru1,Ru2,O] -> sublattices at 1,2; s0_OH/s0_OOH are ntyp=4 [H,Ru1,Ru2,O] -> at **2,3** (H sorts first). A per-deck constant would have seeded H or O. All four checked -> **the 4/4 ADOPT_AFM result stands.** A3/A4 re-derive the pair from each deck's own block anyway, and refuse if it is not unique
- [x] **ZERO-COMPUTE RESULT: the 33-64 meV NM-vs-AFM class is an ADSORPTION-ENERGY class; A7.3 scores c_M. Projected onto c_M the same banked data gives −25.9 meV.** ΔE = −144.0 (clean slab) / −80.3 (*O) / −85.3 (*OH) / −111.3 (*OOH) meV; Δc_M = ΔE(*OOH) − ΔE(*OH) = **−25.9 meV**. **Why it shrinks: the largest component sits on the CLEAN SLAB, which c_M cancels** — commit 946c3aa already saw the shape ("NM anchor error concentrates in *->*OH", the one step c_M does not contain). Internal check: the four implied CHE step shifts are +58.7/+5.0/−31.0/−32.7 meV, reproducing 946c3aa's recorded +58.6/+5.0/−30.9/−32.7 to 0.1 meV
- [x] **docs/60's CONCLUSION SURVIVES** — 25.9 meV still exceeds Ru's 15.5 meV, so "A7.3 NOT MET is not settled while S0(h) is owed" holds, and now on the right quantity
- [ ] **BUT docs/60 §6 fact 2's SENTENCE compares two different kinds of number and must be restated.** 15.5 meV is a required **swing in Δc_M across U=0->9**; 33-64 meV is a **level shift at a single U** (gate (h) ran U=0 only). By the A11.1 arithmetic governing this family, **a U-independent offset cancels EXACTLY at any size** — so neither 33-64 nor 25.9 meV bounds A7.3's error. Both are levels; A7.3 scores a difference of two. Honest form: the AFM treatment moves c_M by 25.9 meV at U=0 and **its U-dependence has never been measured**
- [ ] **FRANK, docs/61 decision item 3 is anchored to the wrong quantity.** P-SPIN-DELTA's PROPOSED `|D_M| >= 0.033 eV` is justified as "the bottom of gate (h)'s measured 33-64 meV class" — but that is the adsorption-energy class and D_M is a c_M quantity. Re-anchored through c_M the figure is **0.026 eV**, and it is still a level standing proxy for a swing. Recommend: re-anchor to 0.026 eV and say it is a level-derived proxy, or drop the gate-(h) anchoring — but it should not stay at 0.033 citing a justification pointing at a different quantity
- [ ] **LIMIT ON WHAT THE OWED COMPUTE CAN SETTLE, stated so nothing is sequenced on a false belief:** the four relaxations discharge P11 limit (ii) and firm up the anchor's magnetic row — **they do NOT bound A7.3's error, and no version of this family can**, because they are all at U=0 in the 2x1v cell while A7.3's rows are the 1x1 A0 grid across U ∈ [0,9]. The deck set that acts on A7.3 is docs/61 item 10's Ru AFM probe, and even that needs BOTH U endpoints to make a D_M
- [x] **SU balance measured 2026-08-30: 70,851.6 of 100,000 remaining** (29,148.3 used). STANDALONE_FOUR ~4,000-7,600 SU (6-11%); SECOND_SEED_CROSSED ~16,000-30,000 SU (23-42%). Both fit; the second does not fit comfortably alongside A0-SPIN Stage 1 + the Ru AFM probe + whatever S3 owes, six weeks from the freeze — **so the scope call is a schedule call too**
- [ ] **FRANK: the AFM scope line is the ONLY thing between here and launch.** Add one dated line to docs/43 (`[AFM-SCOPE RESOLVED YYYY-MM-DD: STANDALONE_FOUR]` or `SECOND_SEED_CROSSED]`) and the builder emits the manifest on the next run
- [ ] Mine, unblocked once they land: the GATE-1 `__g1` children (deposited rule docs/43:311-314) build from each relaxation's converged final geometry — `--gate1`, which refuses today and says why. Family is **>= 8 decks**, not four

## 2026-08-30 latest (S0(h) AFM relaxations LAUNCHED)

- [x] **Frank RESOLVED the AFM scope: STANDALONE_FOUR** (explicit in-session choice; dated addendum appended at the bottom of docs/43 per its own correction rule, machine-readable head `[AFM-SCOPE RESOLVED 2026-08-30: STANDALONE_FOUR]`). A8.1's crossed reading is DEFERRED with three stated reasons (SU vs the freeze; no registered scorer consumes an AFM crossing; docs/63 §4.3 — no version of the family bounds A7.3). If wanted later it is a NEW dated line, not a reinterpretation. Builder gate lifted -> manifest emitted; tests updated to PIN the resolution (a botched docs/43 edit can no longer silently change scope or re-open the HOLD); 13 pass
- [x] **Manifest re-emitted in the 42-runner's 4-field format** (`dir job suffix nk`), nk per m_s3_wave1.txt's measured 2x1v convention: clean ref 16, adsorbate rows 8 (same cell, same 4 4 1 mesh, same nspin=2 class as the S3 Mn/Fe rows the convention was measured on)
- [x] **Registration-before-launch order kept:** resolution + manifest + tests committed and pushed (`7994533`) BEFORE any deck was staged. Then staged to Anvil (tar `92ee9565...`, 5/5 md5-verified on both ends), PARITY_PASS + pseudo preflight + driver dry preflight all green (`lines=4 to_run=4 stale=0 bad=0`)
- [x] **ARRAY `20238023` SUBMITTED 2026-08-30, 1-4%4, 128 ranks, EXCLUDE=a024,a049,a050,a088,a196,a220,a223.** Worst-case cap 24,576 SU at the 48h walltime; realistic well under (banked cold SCFs ran 1.4-3.3h on 20 cores; these start from the banked AFM densities' own converged branch via the same seeds, warm BFGS extrapolation after step 1)
- [ ] **When `20238023` drains:** QC each .out (converged / no "convergence NOT achieved" / JOB DONE; totmag & absmag trajectory vs the parent SCF's -2.09/-1.62/-1.21/-0.24 — a basin flip mid-relax is the A8.3 CONFOUND case); pull md5-verified; then `build_h_afm_relax.py --gate1` builds the 4 fresh-density `__g1` children (deposited rule docs/43:311-314, >= 5 meV BASIN_DRIFT re-relax loop, A8.3's 1 meV above-parent refusal); THEN re-derive the relaxed Δc_M against docs/63 §4's fixed-geometry −25.9 meV — the P11-limit-(ii) lower bound becomes a measured relaxed number
- [ ] **Scoring reminder (docs/63 §4.3, unchanged by the launch):** these four CANNOT bound A7.3's error — U=0, 2x1v. Only docs/61 item 10's Ru AFM probe acts on A7.3, and it needs both U endpoints

## 2026-08-30 landing (wave 1 of the S0(h) AFM relaxations)

- [x] **Array 20238023 drained 3/4.** ref/s0_OH/s0_OOH COMPLETED (17m/45m/2h49m); all three
  `bfgs converged` in 2-3 steps, no `convergence NOT achieved`, JOB DONE. Basin continuity
  CLEAN (per-ionic-step converged totmag): ref -2.09→-2.11, s0_OH -1.23→-1.27,
  s0_OOH -0.22→-0.12 — same sign throughout, no A8.3 CONFOUND.
- [x] **Task 2 (s0_O) OOM-killed on a120 at 07:46** during first-SCF wfc init (last line
  "Starting wfcs are 220 randomized atomic wfcs"; MaxRSS sampled 18G of 237G — spike or
  node fault, NOT a deck problem: both bigger adsorbate decks finished at ~50G on other
  nodes). Partial .out preserved as `.out.attempt1-oom-a120`; **retry = array 20241317**,
  1-row manifest (mirrored at runs/s0/m_h_afm_relax_retry2.txt), a120 added to EXCLUDE.
  Running healthy on a131 (past the kill point).
- [x] **Three .outs pulled md5-verified** (tar 57f8f7e7... 5/5 match) and banked.
- [x] **Relaxed panel derived** (comparators verified against primary sources — README E_NM
  = final BFGS energies of runs/probe/Ru_cellsym/*.out, all four match to every digit):
  gains vs the anchor SCFs -2.4/-2.2/-8.8 meV (ref/OH/OOH), max displacement
  0.006/0.007/0.023 A. P11 limit (ii)'s "lower bound" is now a measured 2-9 meV correction.
- [x] **Relaxed Δc_M = -32.5 meV** (vs docs/63 §4's fixed-geometry -25.9; deepened -6.6 meV
  because *OOH relaxes 4x more than *OH). Still a LEVEL at U=0 — the §4.1 swing-vs-level
  caveat travels unchanged; still cannot bound A7.3.
- [x] **P-SPIN-DELTA wrinkle for docs/61 item 3** (Frank's decision): the relaxed c_M level
  is 0.033 eV — numerically the ORIGINAL proposed threshold, but via the correct quantity.
  Options now: 0.026 (fixed-geom c_M level) or 0.033 (relaxed c_M level, keeps the number,
  fixes the justification). Both are levels standing proxy for a swing; say so either way.
- [x] **--gate1 IMPLEMENTED** (was a stub that refused unconditionally): each __g1 child =
  the ANCHOR deck at the relaxation's final coordinates, fresh prefix, nothing else — G1-G10
  assertions (scoreability, committed-blob, label sequence, frozen rows byte-identical +
  unmoved <1e-5 A, moving rows <0.1 A, diff shape, prefix==stem, byte hygiene, destination,
  totmag basin continuity). All-four-or-none refusal (lit2 idiom). Manifest carries the
  relaxation comparators + the landing scoring rules (>=5 meV below -> BASIN_DRIFT re-relax;
  >1 meV above -> A8.3 refusal; >0.1 mu_B totmag move -> CONFOUNDED). Tests: refusal pinned
  on a synthetic tree; the build-path test auto-activates when all four land. 167 pass.
- [ ] **When 20241317 drains:** QC s0_O (same checks; parent totmag -1.62), pull md5-verified,
  run --gate1 (builds 4 children + m_h_afm_g1.txt), COMMIT+PUSH, stage, submit the g1 array,
  extend the relaxed panel with the s0_O row.

## 2026-08-30 s0_O casualty + GATE-1 wave (post-retry)

- [x] **Retry 20241317 "COMPLETED" but FAILED QC:** 3rd SCF hit electron_maxstep=200
  ("convergence NOT achieved ... stopping"; JOB DONE still printed — the docs/26 §4 trap).
  Moment walked −1.62→−1.70→−1.98 over steps 1-2; the 3rd SCF touched acc 1.45e-6 at it 21
  (conv_thr 1e-6), bounced, spin-sloshed −1.6↔−2.6 for 180 iterations. Magnetic-solution
  oscillation = the campaign's 2nd state-property SCF instability (trap-25 pattern, cf. Ti).
  Evidence banked md5-verified as `.out.attempt2-scf-maxstep`.
- [x] **--gate1 extended with --quarantine** (Q1-Q3: must be a recorded casualty with
  .out.attempt* evidence and NO scoreable .out — never a shortcut past an unrun job) and
  **--repair-mixing** (R1-R8: committed relax deck + mixing_beta halved + fresh prefix,
  exactly 2 lines — A6.5(2) rung (ii) BY ANALOGY, stated as such; rung (iii) NOT_CONVERGED
  is the exit if r1 fails, no third solver attempt). Full attempt history + governance
  framing in runs/s0/h_afm_relax/README.md.
- [x] **3 GATE-1 children built** (ref/OH/OOH at their relaxed geometries, quarantine
  recorded in m_h_afm_g1.txt header with comparators) **+ 1 repair deck** __relax__r1
  (m_h_afm_relax_repair.txt). s0_O's g1 child DEFERRED, owed iff r1 converges.
- [x] **BOTH ARRAYS SUBMITTED 2026-08-30:** g1 children = 20243152 (1-3%3), s0_O r1 repair = 20243153 (1-1%1); preflights green, a120 stays excluded, decks md5-verified both ends (g1 md5s = the sandbox dry-run md5s exactly — deterministic construction).
- [ ] **When the g1 children drain:** score vs manifest comparators (BASIN_DRIFT ≥5 meV
  below → re-relax loop; >1 meV above → A8.3 refusal; >0.1 μ_B totmag → CONFOUNDED).
- [ ] **When r1 drains:** converged → QC (moment drift goes to the A8.3/CONFOUND discussion
  regardless), pull, --gate1 for the s0_O child, extend the relaxed panel; failed →
  rung (iii): s0_O relaxed row recorded NOT_CONVERGED, family reports 3+1 gap.

## 2026-08-30 g1 wave interim

- [x] **ref g1 (20243152_1) OOM-killed on a200 at 03:52** — third early-phase OOM, third
  distinct node (a120, a200), sampled RSS well under the allocation each time; node-fault
  pattern. Evidence preserved as `.out.attempt1-oom-a200`; **retry = array 20243319**
  (m_h_afm_g1_retry1.txt), a200 added to EXCLUDE. OH/OOH g1 children still running.
- [ ] Consider an RCAC ticket naming a120+a200 if a fourth early OOM lands (the draft at
  anvil/rcac_ticket_draft_2026-08-24.md already exists for an earlier node issue).

## 2026-08-30 GATE-1 verdicts

- [x] **GATE-1 PASSES 3/3:** E_g1 − E_relax = +0.028 / −0.090 / +0.302 meV (ref/OH/OOH),
  Δtotmag ≤ 0.03 μ_B. No BASIN_DRIFT, no A8.3, no CONFOUND. The relaxed panel incl.
  Δc_M = −32.5 meV is now GATE-1-confirmed. Outputs pulled md5-verified and banked.
  (ref g1 needed the 20243319 retry after the a200 OOM; completed 9m25s.)
- [ ] **Still pending: r1 repair (20243153)** — monitor armed; converged → QC + pull +
  s0_O g1 child; failed → rung (iii) NOT_CONVERGED recorded, family reports 3+1 gap.

## 2026-08-30 family CLOSED OUT (docs/64)

- [x] **r1 repair FAILED (rung iii EXECUTED):** 2nd SCF hit 200-iteration ceiling; first SCF
  "converged" at totmag −1.90 with the moment still drifting. **s0_O relaxed row = NOT_CONVERGED,
  recorded gap, no third attempt** (pre-stated exit). s0_O g1 child never owed. Family final:
  3 relaxed+GATE-1-confirmed rows + 1 recorded gap. Cost 1,067.9 SU.
- [x] **6-agent verification workflow over docs/64 (78 findings):** all banked numbers CONFIRMED
  independently (panel, Δc_M −32.5 fixed −25.9, GATE-1 verdicts, citations, comparator premise).
  **One load-bearing inference REFUTED and corrected:** trap 27's "mixing selects a distinct
  solution" → actually ONE flat magnetization landscape (3 converged flags at one geometry span
  0.28 μ_B across 0.71 meV; r1's moment non-stationary at the flag). Trap 27 rewritten; README
  + docs/64 reframed. Also fixed: my OOM miscount (2 on 2 nodes, not "three/third" — caught
  pre-workflow), sloshing band extremes (−1.29↔−2.61), rounding chain digits, elapsed-vs-clock
  wording, sacct/mybalance transcription sourcing, QE WALL times substituted for Slurm elapsed.
- [ ] **Frank:** docs/61 item 3 gains a third option (0.033 eV via the RELAXED c_M level —
  keeps the registered number, fixes the justification; vs 0.026 fixed-geom); the s0_O
  flat-moment finding is new evidence for the docs/59 §3c discussion; docs/61 item 10 (Ru AFM
  probe, both U endpoints) remains the only live path to A7.3.

## 2026-08-31 launch-readiness session (plan)

All scored compute is entrant-gated (docs/59 §3c uncountersigned; docs/61 decisions 1-4 open;
item 10 open). Anvil queue EMPTY, 69,783.7 SU. Plan: submit NOTHING; make every arm launch-ready.

- [x] CI: S1_OC20_ASSET_SHA256 pin FINISHED + hardened (pin-unset now refuses BEFORE the
      download; verbatim-quote discipline vs docs/43:1868). All 5 registered paths + 5
      adversarial variants proven locally; silentgate suite 46 passed / 7 skipped (the
      docs/57 §7 baseline). Verify verdict CLEAN, 0 edits needed.
- [x] Stage-1 A0-SPIN decks: 20 built (10 Ru + 10 Ir; s0_OH/s0_OOH × u000/u900 × proposed
      seeds, minus the 4 banked Stage-0 u000-sp050 rungs) by src/dft/build_a0spin_s1.py
      under A1–A12 + S1-a..g; manifest runs/a0/m_a0spin_s1.txt (4-field row grammar,
      md5s as header comments). Ti hard-refused pending §3c. Verify CLEAN: every deck =
      exactly prefix-line + (1+ntyp) inserted lines vs parent; determinism re-proven. NOT submitted.
- [x] Ru AFM probe: 4 decks ({s0_OH,s0_OOH} × {AFM,NM} @ U=9.0, 2×1v NM-relaxed fixed
      geometry; U=0 legs banked, not re-run) by src/dft/build_ru_afm_probe.py; manifest
      runs/s0/m_h_afm_probe.txt with a QUESTION-FOR-THE-ENTRANT (the 4-SCF enumeration is
      DERIVED; geometry choice is a live option). AFM HUBBARD card names BOTH sublattice
      labels (Ru1/Ru2). Verify CLEAN. NOT submitted.
- [x] Löwdin extractor: src/dft/extract_lowdin.py + tests/test_extract_lowdin.py; both
      nspin shapes, validated over all committed Stage-0 *.projwfc.out; nothing written
      under runs/ (registered ordering: extract only after the commit). Verify FIXED
      (one --check --report KeyError on a mismatching artifact — fixed).
- [x] docs/65-decision-sheet-2026-08-31.md: 19 rows + 3 FYI — every owed signature
      (docs/59 both acts incl. §3c; docs/61 items 1–12; docs/62 §9; A7.7; A7.5 Mn arm;
      Ti nspin=2 question; deposit vehicle), each with the one dated line that discharges
      it; SU arithmetic re-derived (76 gated SCFs ≈ 380–1,420 SU ≈ 0.5–2% of balance).
      Citation-audited adversarially (5 findings, all fixed at assembly). Assets section filled.
- [x] Assembly done 2026-08-31: 15-agent workflow (recon→build→verify × 5 tracks),
      0 agent errors; committed per-deliverable + pushed.

### Review — what the entrant should read first
docs/65 top-to-bottom, then sign rows in the critical-path order it opens with:
Row 1 (docs/59 §3c — gates Ti, the arm's most informative half, docs/62 §6) →
Rows 3–5 (Stage-1 Ru/Ir submit) → Row 15 (the ONLY deck set that acts on A7.3).
The queue is empty and every deck is pre-staged: each signature is ≈20–370 SU from data.

## 2026-08-31 (later) — the entrant's directive: freeze amended, all elections executed

- Directive verbatim + election record: **docs/66**. Freeze: P-DISPOSITION Oct 15 →
  REPORT LOCK, backstop Nov 5 2026 8:00 pm ET (docs/43 dated addendum). docs/59 §3c
  GRANTED (retroactive over the 7 banked Ti relaxations, non-precedent clause).
  docs/43 AMENDMENT 11 appended (all docs/61 elections + A11.4 re-word + middle-band
  token + denominator table + CMF / re-read+Family-C / probe-robustness / Mn-arm
  licences + scale disclosure ~356→~395). Mn AFM arm design of record: **docs/67**.
  Verification: 13-agent session wf_3866bd01-d35 (3 candidates AMENDED, adopted) +
  4-auditor pre-commit pass wf_4ac7a2ec-f94 (44 findings, all applied — incl. the
  legitimacy one: §3c is EXECUTED-UNDER-DIRECTIVE, completes at Frank's own
  confirmation line in docs/59 §5; no Ti deck submits before it).
- Facts of record for docs/66 §5: Anvil checks this session (ssh): queue EMPTY
  (`squeue -u $USER -h | wc -l` → 0), balance 69,783.7 CPU SU + 150 GPU-h
  (mybalance), remote tree `/anvil/projects/x-che260157/sts` present (sacct
  WorkDir of the a0 arrays + ls: anvil/ logs/ runs/ src/).
- [ ] **FRANK: one dated line in docs/59 §5** — `[§3c CONFIRMED 2026-__-__ — read
      docs/66 §2; the grant stands]` (or override any docs/66 row). Ti submits then.
- [ ] Zenodo deposit (OWN VERSION NOW, new version off id 22072991, restricted) →
      DOI lines filled in docs/59 §5 + docs/43 A11.R5, with per-file manifest
- [x] builders + decks DONE 2026-08-31 (commit f4ba6e9): 74 new decks / 6 families
      — Ti S1 12 (m_a0spin_s1_ti.txt, s0_OH@u900 rows first, nk 8 = the banked Ti
      convention, deviation flagged), re-read Ru/Ir 20 (m_a0spin_reread.txt, Ir
      slab rows carry the Row-7 contingency comment) + Ti 12 (m_a0spin_reread_ti),
      CMF 28 (m_cmf_seed_search), probe robustness 6 (m_h_afm_robust), Mn AFM
      order 4 (m_mn_afm_order); shared licence gate src/dft/a0spin_ti_licence.py;
      fail-closed guards on all five submitters (41/43/45/47/49, full refusal
      matrix proven vs a stubbed sbatch); a7_3_spin census readout + 16 tests.
      EVERY family independently adversarially verified (4 CLEAN, Ti-families
      FIXED: the S1 builder's stale header repaired, 21/21 byte-identical again).
      Suite 210 passed / 8 skipped.
- [x] STAGED TO ANVIL 2026-08-31: 119 files (all decks + manifests + guarded
      submitters + the 2 relicensed manifests) tar→scp→extracted at
      /anvil/projects/x-che260157/sts; per-file md5 ALL_119_FILES_MATCH both
      ends; submitters chmod +x, bash -n clean remotely; PARITY_PASS present.
      NOTHING SUBMITTED — A11.R5 gates every deck on the deposit publishing.
- [x] DEPOSIT PUBLISHED by Frank 2026-08-31: **DOI 10.5281/zenodo.22213117**
      (all 9 file md5s verified against the published record); DOI lines filled
      in docs/43 A11.R5 + docs/59 §5 (commit ad19bdf). §3c CONFIRMED by Frank's
      in-session line ("i published the deposit, submit everything", verbatim,
      recorded in docs/59 §5 with its context). Every submission gate discharged.
- [x] **ALL EIGHT ARRAYS SUBMITTED 2026-08-31 (106 SCFs), EXCLUDE=
      a024,a049,a050,a088,a196,a220,a223,a120,a200:**
      **20262064** m_a0spin_s1 (Ru/Ir S1, 1-20%6) · **20262088** m_a0spin_reread
      (Ru/Ir slab/s0_O, 1-20%6) · **20262090** m_cmf_seed_search (1-28%6) ·
      **20262091** m_a0spin_s1_ti (1-12%6, s0_OH@u900 rows lead) · **20262104**
      m_a0spin_reread_ti (1-12%6) · **20262287** m_h_afm_probe (1-4%4) ·
      **20262289** m_h_afm_robust (1-6%4) · **20262290** m_mn_afm_order (1-4%4).
      squeue confirmed 27 queued entries (arrays collapsed), all PD/Priority at
      submit time. Two infra facts found at launch: (a) anvil/41_submit_wave.sh
      still carries the mybalance-SIGPIPE ACCT bug 43/47 fixed (silent exit on
      non-tty ssh) — worked around with ACCT=che260157 env; a one-line fix is
      owed next maintenance pass; (b) 40_wave.slurm was absent from
      $PROJECT/sts/anvil/ — the repo's NP-argument version (cdb9fd5, md5
      03620b63…) scp'd there; the old $PROJECT/anvil/ copy hard-codes 20 ranks
      and must not be used with NP=128 manifests.
- [ ] Collect outputs when arrays land (tar/scp + md5 both ends, the docs/62
      shape); extract via a0spin_census.py (Ti now scorable — the §3c CONFIRMED
      line exists) + extract_lowdin.py --check; bank + readout docs.
- [x] ~~Mn AFM: when 20262290 lands, execute the E1 adoption rule (±20 meV,
      pre-stated in m_mn_afm_order.txt) → countersign the measured pattern
      (docs/67 §7 item 3) → build MN-AFM-CORE on its trigger.~~ **ALL THREE DONE.**
      20262290 landed 4/4 converged (docs/68:24); the ±20 meV rule executed to a
      **measured null** (AFM +664.6 / +1,219.5 meV above FM, solutions genuinely held);
      countersigned `[MN E1 COUNTERSIGNED 2026-09-02]` (docs/67:140) on the entrant's
      "Sign D3"; **MN-AFM-CORE did not trigger and will not be built.** One residue,
      §7 item 1 — see the open item below.
- [ ] Row-7 watch: if Ir slab 0.10/0.30 (in 20262088) fail the floor, the
      pre-named 0.05 extension fires (2 decks), then EQUALISED-BY-SELECTION.

## 2026-09-01 — A11 wave 1 DRAINED (docs/68): 102/106 ran, 86 converged, Ru spin@U=9 = 0/15, a171 sick

- [x] sacct census of all 8 arrays: 102 COMPLETED, 3 OOM (a171), 1 hung 19h11m at 0 iterations
      (a171) → **scancel 20262091_1** (≈2,450 SU idle burn); partial .outs preserved as
      `.out.a171_2026-08-31`; balance **65,096.2 SU**.
- [x] Retry of the 4 a171 casualties, byte-identical: `runs/a0/m_a11w1_retry_a171.txt`
      (commit a077ab2) → **array 20300641** (1-4%4, EXCLUDE + a171). PENDING (Priority) at 19:20 EDT.
- [x] Pull: 484 files, per-file md5 ALL MATCH; `.run.in` over-pull deleted; slurm logs to scratchpad.
- [x] Löwdin: 76 new + 10 Stage-0 `.lowdin.txt` extracted, 86/86 `--check` PASS.
- [x] Census run A (as committed, sidecars aside) = run B2 (CEN-d widened by class, test S8,
      115 passed) on every scored field. Reports: `tasks/review/a7_3_spin_census_2026-09-01_run{A,B2,C}*.json`.
      Mn/Fe FINAL = as-built; Ir FINAL-provisional span/2 0.0591 V (guard-3 REVIEW-REQUIRED);
      Cr/Ru/Ti PENDING on the 4 retry rows only.
- [x] **0 of 16 spin-polarised Ru SCFs converge at U=9** (12 FM 1×1 + 4 AFM 2×1v; sloshing, not
      creep) → every (Ru,*,u900) cell EQUALISED-BY-SELECTION(nspin=1); Ru will be BRANCH-CONDITIONAL
      when final; A7.3 fact (2) is now a measured sentence (docs/68 §2). NOT a rescue target.
- [x] Ir slab u000 contingency FIRES (+0.590/+0.597/+0.583 meV) → `src/dft/build_ir_slab_ext.py`
      built `slab__u000__sp2m005` (census CEN-d PASS, run C identical on per_metal); manifest
      `runs/a0/m_ir_slab_ext005.txt`; u900 does NOT fire (Rider 1: no deck).
- [x] Mn E1 executed: P-A +664.6 meV, P-B1/2 +1,219.5 meV above FM, AFM held (M_abs 42–43) →
      measured null, FM stands, MN-AFM-CORE does not trigger, arm stops; A7.5 strike lifts by running.
- [x] Submitted `m_ir_slab_ext005.txt` (1 SCF, commit 9d5d7d6) → **array 20301497** (1-1%1, EXCLUDE + a171); deck md5 verified on Anvil (3bd9fd10…). At 19:33 EDT: 20300641_1 RUNNING on a113, _2/_3/_4 PD (Resources), 20301497 PD.
- [x] **2026-09-02 01:10 UTC — ALL LANDED, FINAL CENSUS BANKED** (docs/68 §8;
      `tasks/review/a7_3_spin_census_2026-09-02_FINAL.json`, n_final_rows 6, 119 tests pass).
      Ru s0_OH u900 m010: 200 iters NOT converged → **Ru 0/16 final**; Ir slab 0.05 → +0.474 meV
      REJECT → cell EQUALISED-BY-SELECTION(nspin=1) with 4 rejects; delta pull 18 files md5 ALL MATCH;
      90 Löwdin artifacts. **Equalised sensitivity = {Cr, Mn, Fe} over the floor = the same 3 of 6**
      (Ru 0.0957 V, Ir 0.0591 V, Ti 0.0522 V under); guard 3 flags Cr/Ru/Ir/Ti REVIEW-REQUIRED.
      Balance **64,977.8 SU**; queue EMPTY; nothing in AMENDMENT 11 remains unrun.
- [x] Pointer notes appended: docs/58 §8, docs/60 §11, docs/63 §6 → docs/68.
- [ ] **FRANK D1:** β-rung on the 16 Ru U=9 spin rows → **LICENSED 2026-09-02 as A11.R6** (Frank: "Lets go ahead with B").
- [ ] **FRANK D2:** guard-3 adjudication for Ir (and Ru once final) — one dated line each.
- [ ] **FRANK D3:** Mn E1 countersign (docs/67 §7 item 3) — one dated line; then update
      `a0main_readout.py` mn_afm text ("RUN 2026-09-01 — FM stands (measured null)").
- [ ] **FRANK D4:** RCAC ticket on a171 (text in docs/45) — send or skip.
- [ ] docs/58 fact (2) restatement; docs/60 §6 / docs/63 §6 pointers to docs/68 §2.

## 2026-09-02 — A11.R6 rung 1 LAUNCHED; D3 signed; D2 held; D4 drafted; lit/ideation workflow running

- [x] **A11.R6 registered (f4ae5d3) BEFORE any deck**: two pre-named rungs on the 16 unconverged
      Ru U=9 spin rows (12 nspin=2 + 4 AFM 2×1v). Rung 1 β 0.15 / maxstep 400; rung 2 β 0.075 /
      ndim 16 / maxstep 600 only on rung-1 failures. Pool widens only inside the twelve
      (Ru,*,u900) cells; AFM rows → docs/63 readout only. **Count corrected 15→16** everywhere.
- [x] Census extension (2183a5e): `__rung[12]` stems parsed, table-checked, twelve-cell scope,
      rung-2-only-after-rung-1-failed; tests S9/S9b; 121 passed. `build_ru_rung.py 1` → 16 decks
      byte-identical except the licensed lines; census CEN-d PASS on the 12 a0 decks.
- [x] **SUBMITTED 2026-09-02 00:48 UTC: array 20305768** (`m_ru_rung1`, 12 rows, 1-12%6, via 47)
      and **array 20305769** (`m_h_afm_rung1`, 4 rows, 1-4%4, via 41/40_wave); 18 files md5-verified
      on Anvil; EXCLUDE + a171. Expected 30–70 min per 1×1 row, ~2.5 h per AFM row.
- [x] **D3 SIGNED** (docs/67 §7 dated line; docs/43 A11.R3 pointer; `a0main_readout.py` mn_afm
      text; banked JSON not regenerated). **D2 HELD** (docs/43 line). **D4 drafted** as Gmail
      draft r1072822063942699521 to rcac-help@purdue.edu — FRANK SENDS.
- [x] External note audited: Co U-ladder RAN (12/12 converged; no s0_OOH row); RPBE 10/10 per
      metal; ZPE−TΔS already in referencing.py; upscale already downgraded in docs/45. Lessons added.
- [ ] Workflow `wf_10c6483e-8a7` (lit review ×10 dims + source-verification + 6 ideation lenses +
      critics + synthesis) → writes docs/70; read its completeness critic before trusting it.
- [ ] When 20305768 + 20305769 drain: pull (delta shape) → census (rung-1 rows enter the twelve
      cells) → per A11.R6: rows still unconverged → `build_ru_rung.py 2` → commit → submit;
      converged rows → floor/guard verdicts; AFM rows → docs/63 U=9 level. Then docs/68 §11.
- [ ] **FRANK D2** after the ladder returns (Cr/Ti SAME-BRANCH, Ir BRANCH-CONDITIONAL likely; Ru
      depends on rung outcome).

## 2026-09-02 05:30 UTC — rung 1 LANDED (0/16 converged); rung 2 LAUNCHED; workflow resumed

- [x] **Rung 1: 16/16 still unconverged** at β 0.15 / 400 steps (scf accuracy ~1e-2 Ry at step 400,
      moments 19–24 μB on 1×1, 2.6–3.5 on 2×1v AFM); ~2,170 SU; outputs pulled (32 files md5 ALL
      MATCH), census records rung-1 UNCONVERGED, Ru row unchanged at 0.0957 V (5fa695a).
- [x] **Rung 2 built and SUBMITTED per A11.R6** (β 0.075, ndim 16, maxstep 600, all 16 rows):
      arrays **20315861** (12 a0 rows, 1-12%6) + **20315873** (4 AFM rows, 1-4%4); 18 files
      md5-verified on Anvil. Ladder ENDS here: a row unconverged after rung 2 is NOT_CONVERGED
      (A6.5 rung iii); no further rung may be run without a new dated line. Balance 62,807 SU
      before rung 2; worst case ~3,300 SU more.
- [x] Workflow wf_10c6483e-8a7 first pass: 61/100 agents done, 39 died on the session limit
      (31 verifiers, all 6 ideation lenses, synthesis, critic) → docs/70 NOT written. Resumed
      2026-09-02 05:32 UTC from cache (only the 39 re-run). Read its completeness critic first.
- [ ] When 20315861 + 20315873 drain: pull → census (`..._rung2-landed.json`) → docs/68 §11:
      either the sentence hardens to "β 0.3 / 0.15 / 0.075 with local-TF, up to 600 steps" or a
      converged candidate meets the floor + guards → D2 on Ru.

## 2026-09-02 — A11.R6 LADDER EXHAUSTED (docs/68 §11): 0/16 at both rungs; AMENDMENT 11 fully run

- [x] Rung 2 (β 0.075 / ndim 16 / 600 steps, arrays 20315861 + 20315873): **0 of 16 converged**,
      3,045.9 SU. Ladder total 5,216.7 SU. Pulled, md5 ALL MATCH, installed, banked.
- [x] **A6.5(2)(iii) NOT_CONVERGED** on all 16; every (Ru,*,u900) cell stays
      EQUALISED-BY-SELECTION(nspin=1); census `..._LADDER-EXHAUSTED.json` is byte-identical to
      the pre-ladder FINAL table — {Cr, Mn, Fe} over the floor, 3 of 6. Outcome (a) of A11.R6.
- [x] Key measurement: 19,200 SCF iterations, closest approach **595× the threshold**, while the
      **nspin=1 twins in the same cell converge in 25 iterations at 5.9e-7 Ry**. Rung 2 beat rung 1
      on 10 of 16 rows and was worse on 6 → no systematic gain from deeper damping.
- [x] **THE LADDER ENDS HERE.** A third rung (occupation-matrix control, U-ramp, different mixer)
      requires a NEW dated line and must disclose it was chosen after seeing this outcome.
- [x] Balance **59,761.1 SU**; queue EMPTY; **nothing in AMENDMENT 11 is unrun** (A11.R4 total ~388).
- [ ] **FRANK D2 (now unblocked, one dated line):** Ru **BRANCH-CONDITIONAL** (magnetic at U=0,
      no spin-polarised solution obtainable at U=9 under three mixing settings), Ir
      BRANCH-CONDITIONAL, Cr and Ti SAME-BRANCH. Suggested line in docs/68 §11.
- [ ] Report methods sentence: the hardened docs/68 §11 wording (48 attempts / 19,200 iterations /
      0 converged / 595× / NM twins 25 iterations) replaces the docs/68 §2 draft.
- [ ] docs/70 (workflow wf_10c6483e-8a7) — third resume running; read its completeness critic first.

## 2026-09-02 — docs/70 landed (135 agents), critiqued, and corrected; docs/68 convention error fixed

- [x] Workflow `wf_10c6483e-8a7` COMPLETE after 3 resumes (2 session-limit stalls): 135/135 agents,
      10 lit dimensions, **64 claims survived source-verification / 16 refuted**, 35 ideas, 18 surviving.
      **docs/70** (832 lines) + **§8 corrections** appended after I re-verified the critic against the tree.
- [x] **MY ERROR, corrected in place:** docs/68 §8 quoted Ru "4.3 meV short" — half-distance in the volt
      convention, not commensurate with docs/60's 15.5 meV. Correct: **Ru 15.5 → 8.5 meV, Ti 112.5 → 95.6,
      Ir 72.6 → 81.7; each change is exactly D_M.** Ledger entry added (convention errors survive every
      numerical check).
- [x] docs/70 §8.1 kills 9 of its own claims, incl. a **mis-scoped load-bearing citation** (Lee *Adv. Sci.*
      is hollandite IrO2 grand-canonical, cited backwards to support a KILL) and **6 unverified STS-precedent
      attributions** that all carry Q-5. **Do not mine §§2-7 without §8.**
- [ ] **NEW TOP HOLE, verified, 0 SU to disposition: BASIN_DRIFT.** Three banked parents sit in an excited **[2026-09-03, measured by `src/dft/gate1_census.py`: only TWO of the three reproduce from this repository. Fe (−384.300) and Mn (−20.616) re-derive exactly. The Co −77.009 meV does NOT: `s0_O__1x1_off__g1.out` and both its `.attempt` files say "convergence NOT achieved" and print no `!` total energy, and `s0_O__1x1_off__g1.fromparent.in` has no `.out` — the fromparent run happened on Anvil and its output was never pulled. The claim is not withdrawn; what may be SAID changes, and the fix is a file transfer, not compute. Do this before dispositioning R3/A8.8.]** **[SUPERSEDED SAME DAY 2026-09-03 — 'the fix is a file transfer, not compute' is WITHDRAWN. Anvil was searched exhaustively (every $HOME tarball listed): `s0_O__1x1_off__g1.fromparent.out` exists for Ni and two Cr_lit3 rows and NOT for Co, and the round-3 copy of the parent was extracted and reads 'convergence NOT achieved' with no `!` energy (md5 cffbcfd2a2e9df3dfb4afd73b8aed646). The remedy was NEVER EXECUTED, not merely never retrieved; the docs/43:317-320 affordability escape is also unavailable, since there is no converged GATE-1 energy to quote. Recorded as a RECORDED GAP. Closing it = ~5-19 SU + Frank's own A11.R3 dated line. See docs/43 Item 7.]** **[THAT SUPERSESSION IS ITSELF WITHDRAWN 2026-09-03 — the artifact EXISTS at /anvil/projects/x-che260157/sts/runs/s3/Co/s0_O__1x1_off__g1.fromparent.out (md5 b0d7c43ddb10c546819e2e9672231de8, converged, JOB DONE). The 'exhaustive' search had covered $HOME tarballs and /anvil/scratch but NOT /anvil/projects, where the run tree actually lives. PULLED and md5-verified both ends; -77.0089 meV re-derives exactly. The parent REPLAY was pulled too and independently lands in the same 11.24 branch at -76.691 meV, agreeing to 0.318 meV. Census now 89 children, THREE BASIN_DRIFT rows all re-deriving. THIS LINE'S ORIGINAL THREE-ROW CLAIM IS VINDICATED AS WRITTEN. See docs/43 'Item 7 CLOSED'.]**
      magnetic branch (Fe `s0_OOH__1x1_off` **−384.3 meV**, Co −77.0, Mn −20.6), clearing the registered
      5 meV trigger by 77x/15x/4x; the deposited remedy (docs/43:311-314 re-relax loop) is **not executed**;
      every ΔG built on those three inherits it; the Fe row is **~45x the Ru-to-floor distance**. This is
      entrant decisions R3/A8.8 (todo:593, :608, :683) and docs/70 missed it entirely.
- [x] ~~Also owed, 0 SU: A5.1(a)+(c) (no script reads a `.lowdin.txt`; Ru/Ir/Ti have no other valence
      tracker and are exactly A7.3's under-floor set); the docs/45:255-256 census contradiction, to be
      reconciled **before any readout is quoted**.~~ **BOTH DISCHARGED 2026-09-03.** The parenthetical
      was **false as written** — `src/dft/extract_lowdin.py` both produces and validates `.lowdin.txt`,
      and `lit1_urobustness.py` has scored A5.1(a)/(c) for tranche 1 since 2026-08-12. The real hole
      was narrower and better: the **A0 grid** had no valence readout, and Ti/Ru/Ir's A0 decks carry
      **no `nspin` card at all** (0/28, 0/32, 0/32), so A5.1(a)'s primary moment tracker cannot exist
      on exactly the failing set. Discharged by **A11.R7** (registered `afb9692`, scored `dbe3104`) on
      the Löwdin d-occupancy, the one valence quantity that spans the nspin confound — **R7-P3 fired,
      the tracker is falsified as an explanation of the A7.3 split.** Census reconciled at `316ae31`
      (88 `__g1` children, zero orphans; the two counts answered different questions).
- [ ] **S-4 (crossing-locator spike) must be re-specified before it is offered**: registers a 9th ledger
      claimant over cap, prediction not evaluable by its own decks, denominator 5 vs 6, ±0.2 eV
      near-unfalsifiable on Cr's 0.5 eV bracket, and drops the spin-equalisation docs/66 §6 item 1 requires.
- [ ] **FRANK D2** still the only banked-verdict line owed (Ru + Ir BRANCH-CONDITIONAL, Cr + Ti SAME-BRANCH).

## 2026-09-03 — S-1 executed: five holes closed at 0 SU, one new registered analysis run, and three of my own claims corrected

**Compute: none. Balance unchanged at 59,761.1 SU. Queue empty. Suite 293 → 321 passed / 8 skipped.**

### Closed

- [x] **H-1 — the RuO₂ antiferromagnetism premise** (`c1011e2`). docs/41's "RuO₂ is
      antiferromagnetic … for `qe_slab.py` that is **factually wrong**" is **WITHDRAWN**. Three
      sources opened and read this session: Hiraishi PRL 132, 166702 (2024) bounds the bulk
      ordered moment at **≤ 4.8(2)×10⁻⁴ μ_B** by μSR; Keßler arXiv:2405.10820 at **≤ 1.4×10⁻⁴ μ_B**
      and re-assigns Berlijn's neutron peak to **multiple scattering**; Smolyanyuk PRB 109, 134424
      supplies the mechanism. That is **67–357× below** the 0.05 μ_B diffraction value. Scope is
      **bulk** — surface (110) moments are not excluded, and the correction says so instead of
      over-claiming the other way. docs/41 correction of record (appended, not edited — it is a
      pre-registration), docs/45 §A **row 6**, and comment-only annotations in `probe_decks.py` +
      `qe_slab.py` (**28 insertions, 0 deletions, 0 non-comment lines**). **It strengthens the
      campaign:** gate (h) put AFM **80–144 meV below** NM under this Hamiltonian and moved
      adsorption energies **33–64 meV** — the campaign's own thesis on its benchmark anchor, with
      an independent experimental check.
- [x] **H-2 — a deposited prediction on a refuted premise** (`eecc887`). docs/43 §7 prediction 3
      registers "`omat` … does not share that convention"; **docs/40 §1.4, dated three days
      earlier**, had quoted OMat24's own paper ("following Materials Project defaults",
      "MPRelaxSet") and concluded in bold "Independence gained on the U axis by switching
      MACE → omat is **zero**". Warford arXiv:2601.21056 (opened today) inverts the direction
      further: **"OMAT-trained models are most affected."** Closed as a **disclosure, not a
      revision** (§7 forbids revision after deposit): the differential test **cannot score the
      mechanism in either direction**, §7's own "if MACE degrades less … that refutes our
      mechanism" clause is **unsound and unavailable**, and **no joint replacement is registered**
      — writing one now would be fitting a prediction to what is already known.
- [x] **H-3 — A7.2's undelivered "first-class deliverable"** (`4826875`). All six pls crossings
      **located**: Mn **0.733**, Cr **3.674**, Ir **4.017**, Mn **6.098**, Fe **8.183**, Ru
      **8.665**; Ti has none. `src/dft/a7_2_crossings.py`, 8 tests. The three-rung guard is the
      point — a synthetic dominated bracket is asserted to be **refused**, and Cr's margin
      (**0.0396 eV**) is an order of magnitude below every other row. pls recomputed here matches
      the readout's own `pls` on **all 58 rows**. Three conditionalities on the face of the table:
      Ru's U\* sits in the equalised region, Ir's bracket is saddle-conditional, and Cr's A0 row is
      **not** the probe-ladder crossing docs/43:1356 discloses.
- [x] **H-10 — a banked "conformer" is a desorbed O₂** (`191a1de`). Ir (O–O 1.286, O–Ir 1.948) and
      Ru (1.297, 1.905) relax to **bound superoxo**; Cr relaxes to **O–O 1.227 Å with both oxygens
      3.09 / 3.78 Å from the nearest Cr** (measured Cr–O bond: 1.856 Å) and **the H on a different
      oxygen** — no O–O–H unit at all, both spin seeds agreeing to 0.0004 Å over 41 and 42 ionic
      steps. It sits 0.021 eV below the `*OOH` minimum, so **scoring it would have put an
      O₂-release energy into c_Cr — the A7.3 quantity.** Erratum markers + dated correction in
      docs/54.
- [x] **The GATE-1 census contradiction** (`316ae31`), which `tasks/todo.md` marked *blocking*
      — "reconcile before any readout is quoted". Both counts were right about **different
      questions**: docs/45 counted **A8.3 refusals post-discharge**, the todo counted **branch
      changes in either direction**, and a child 384 meV *below* its parent is BASIN_DRIFT, not a
      refusal. Measured over all **88** `__g1` children, zero orphans: 77 AGREE / 2 BASIN_DRIFT /
      6 REFUSED (5 discharged) / 3 UNVERIFIED. **"0 REFUSED" is now stale** — `s3/Co
      s0_OOH__2x1v_mir__g1` stands refused at +747.449 meV.

### New, registered before it ran

- [x] **A11.R7** — A5.1(a)'s valence tracker on the A0 grid, from **235 already-banked Löwdin
      artifacts**. Registered at `afb9692` **with no script and no result**; scored at `dbe3104`.
      The two hashes are the proof of order. **0 SU.**
      - **R7-P3 fires.** |δq_c| **interleaves** the two A7.3 groups completely — Mn 0.0069 OVER,
        Ti 0.0096 under, Ir 0.0165 under, Cr 0.0399 OVER, Ru 0.0695 under, Fe 0.0735 OVER — while
        their spans do not overlap at all (largest under-floor 0.1845 eV, smallest over-floor 0.6869 eV — a **3.7× gap**). The metal with the largest U-span has the smallest valence
        change. **The valence-change explanation of the A7.3 split is falsified on this tracker.**
      - What still separates the six perfectly is **nspin = 2 / nspin = 1**, and the one valence
        quantity that exists on both sides does not track it — a sharper statement of the confound
        than docs/60 or docs/63 could make.
      - **My registered stability rule was malformed** (it compares a U-swing to a fixed-U state
        difference) and flagged 4 of 6 metals, gutting R7-P1. The verdict is reported **as
        registered** (REFUTED, ρ −0.257) with the all-six figure labelled **POST-HOC** (ρ −0.381,
        p 0.121, n = 18 — same sign).

### Three of my own claims corrected

- docs/70 §8.2's "**no script in the repo reads a `.lowdin.txt`**" — false; `extract_lowdin.py`
  produces *and validates* them, with a test over the whole bank of 265.
- docs/70 §8.2's "A5.1(a)/(c) **unscored**" — false; `lit1_urobustness.py` has scored them since
  2026-08-12 for tranche 1 (Cr + Co on the P7 ladders). The true hole was narrower and better: the
  **A0 grid** had no readout, and Ti/Ru/Ir's decks carry **no `nspin` card at all** (0/28, 0/32,
  0/32), so the primary tracker cannot exist on exactly the failing set.
- `tasks/todo.md:683`'s **three** BASIN_DRIFT rows are **two** on disk. Fe (−384.300) and Mn
  (−20.616) re-derive exactly; **Co's −77.009 meV has no artifact here** — `__g1.out` and both
  `.attempt` files say "convergence NOT achieved" with no `!` total energy, and
  `__g1.fromparent.in` has no `.out`. Not withdrawn; ~~**the fix is a file transfer, not compute**~~ ~~**WITHDRAWN 2026-09-03 — no converged artifact exists anywhere**~~ **THAT WITHDRAWAL IS ITSELF WITHDRAWN — the artifact exists on /anvil/projects and has been pulled and md5-verified; the fix WAS a file transfer, exactly as first stated**,
  and it must happen before R3/A8.8 are dispositioned.

### Still owed — the entrant's, not mine

- [ ] **D2 — the guard-3 adjudication.** Still the only line owed on a banked verdict
      (Ru + Ir BRANCH-CONDITIONAL, Cr + Ti SAME-BRANCH). Released by A11.R6 returning.
- [ ] **Countersign A11.R7.** If declined, the readout is withdrawn from the report and A11.R7
      stands as the record of what was registered and not used.
- [x] ~~**Countersign docs/59** — its §3c licence decision moves a banked verdict.~~
      **DONE 2026-08-31, and this line was stale for three days.** `[§3c CONFIRMED
      2026-08-31]` at docs/59:309 completes the countersignature on the entrant's verbatim
      "i published the deposit, submit everything"; DOI 10.5281/zenodo.22213117. **A7.3's
      denominator stays 6 and the banked NOT MET 3/6 stands scored.** The "UNGRANTED"
      wording surviving at docs/60:141 and in this file's 2026-08-29 fact 5 predates it
      (docs/60 now carries a dated erratum).
- [ ] **BASIN_DRIFT disposition (R3 / A8.8)** — pull the Co `.fromparent` output from Anvil first.
- [ ] **A7.7 middle-band disposition** — **the text already exists**, written 2026-08-31
      (docs/43:2086-2095, `[A7.7 MIDDLE-BAND DISPOSITION 2026-08-31]`: a middle count is
      "SCORED — MIDDLE BAND / NOT MET", never quoted bare, licensing nothing). It was
      EXECUTED UNDER DIRECTIVE via docs/66 and the entrant's own confirmation is not
      recorded. What is owed is a **countersignature on existing text**, not a new mapping —
      and it was written with the 3-of-6 outcome already known, which docs/43:2108-2111
      discloses on its face. Blocks every report sentence that scores A7.3.
- [ ] **A7.5's Mn AFM arm — ONE residue only:** docs/67 §7 item 1, *"verify the §3
      literature citations before the report quotes them"* (Yoshimori 1959 screw structure,
      ≈129°/c, T_N ≈ 92 K, Regulski). No verification exists in the repo. Stage 1 is
      countersigned and closed; the core never triggered. **0 SU** — VERIFIED / STRUCK /
      DEFERRED.
- [ ] **The Ti nspin = 2 call** — the docs/66 row-9 revisit trigger **has now fired**:
      row 9 elected "NSPIN=1 STANDS, **pending the equalised census** … revisit ONLY after
      D_Ti is measured", and D_Ti is measured at **−0.0169 V** (docs/68:209). So the call is
      live. **No verdict flips either way** — equalising moves Ti 0.0438 → 0.0522 span/2,
      still under the 0.10 V floor. NSPIN=1 STANDS costs 0 SU; THROUGHOUT costs a 28-SCF
      re-run (~140–532 SU at the repo's 5–19 SU/SCF band, never priced for Ti in the repo)
      plus a fresh A6.6 disclosure and a new relaxation licence — and would still leave
      Ru 0/32 and Ir 0/32 without an `nspin` card.
- [ ] **Gate-(h) AFM relaxations** — still HOLD, and H-1 changes their justification: they are now
      a **sensitivity arm**, not a ground-state adoption.
- [ ] **Cr `oosh`** — finding (no bridge-protonated `*OOH` at 1×1) or artifact of the cell?
- [ ] **RCAC ticket** — Gmail draft `r1072822063942699521`, Frank to send.
- [ ] **S-4 must be re-specified before it is offered** — docs/70 §8.1 C-7 records four defects,
      including a **ninth ledger claimant against a cap of eight** and a prediction not evaluable
      by its own decks. H-3 discharged A7.2's registered obligation **without** it.

### Registered compute still ahead

S5 BEEF-vdW (A10, **Sep 18**); S8 make-and-measure (the largest open fork, Q-5 in docs/70 §7);
**Oct 15 hard freeze**.

## 2026-09-03 (second block) — the nine-item review executed under Frank's directive

**Directive, verbatim:** *"make the decisions in that it ends in best rigor and STS placements.
I agree with the fixes fir A11.R7 but should we do a higher n=?. I confirm A7.7. Continue items
6, 7, 8 (send) and relable 9. Write 1. Your call on 3. Continue with 4."*

**Compute: none. Balance unchanged at 59,761.1 SU. Suite 321 -> 332 passed / 8 skipped.**

### The owed-list was half stale — four items were already discharged

- [x] **docs/59 §3c** — CONFIRMED **2026-08-31** (docs/59:309, Frank's verbatim "i published the
      deposit, submit everything"; DOI 10.5281/zenodo.22213117). **A7.3's denominator is 6,
      permanently.** Every "UNGRANTED" note (docs/60:141, this file, MEMORY.md) was stale and is
      now corrected.
- [x] **The AFM scope line** — RESOLVED **2026-08-30** (STANDALONE_FOUR), and the family already
      RAN: 3 BANKED all GATE-1 PASS, s0_O NOT_CONVERGED, **1,067.9 SU**. docs/41 and docs/45
      asserted "remain on HOLD (0 built)" earlier the same day — **false when written**, corrected.
- [x] **Mn E1** — countersigned 2026-09-02; MN-AFM-CORE never triggered.
- [x] **A7.7 middle band** — the text already existed (docs/43:2086, 2026-08-31); only the
      countersignature was missing. **Frank confirmed it; written.**

### Decisions written

- [x] **Item 1 — D2 GUARD-3 ADJUDICATED**: Ru + Ir BRANCH-CONDITIONAL, Cr + Ti SAME-BRANCH. Also
      resolves docs/68's internal conflict (:235 "Cr and Ir" vs :326) **in favour of :326**, with
      the reason on the face of the line. Acts only on the equalised sensitivity; the as-built
      headline is untouched.
- [x] **Item 4 — A7.7 CONFIRMED.** Its own post-hoc disclosure travels with every A7.3 sentence.
- [x] **Item 3 (delegated) — TI CONVENTION: NSPIN=1 STANDS, FINAL.** The docs/66 row-9 trigger had
      fired (D_Ti = −0.0169 eV), so the revisit was live for the first time; it resolves against a
      re-run that cannot change a verdict, on an instrument that already exists.
- [x] **Item 9 — gate-(h) family RELABELLED a sensitivity arm.**
- [x] **Item 2 — A11.R7 COUNTERSIGNED**, with R7-P1 bound to its defect disclosure.
- [x] **Item 6 — Cr `oosh`: 1x1-CONDITIONAL OBSERVATION, not a finding.** The surface claim is
      **refused** — one cell cannot carry it, and the 2x1v deck that would decide it does not exist.
- [x] **Item 8 — RCAC.** a171 section added, node-count drift fixed (the ticket said "two /
      three / five / sixth" while listing seven), Gmail draft `r1072822063942699521` updated with
      the systemic context. **NOT SENT — Frank sends.**

### The higher-n question: answered NO, and it opened something better

**n = 18 is the design ceiling** (6 metals x 3 steps), not a budget choice; R7-P1 ran at n = 6
only because the malformed rule excluded four metals. Recovering 18 on the same data is post-hoc
and is already labelled so. **Inflating to n = 126 by reading every U rung is pseudo-replication**
— span_U is one number per (metal, step) — and is refused in advance in the registration.

**What buys rigor is a sample without the confound in it**, and it was already banked: **90
Löwdin artifacts in the A0-SPIN arm**, covering Ti/Ru/Ir — the exact three metals whose main decks
carry no `nspin` card — with slab + all three adsorbates at u000, the point A11.R7 registers its
predictor at.

- [x] **A11.R8 REGISTERED** (`07cfc4f`, no script, no result) **and SCORED** (`7434e81`). 0 SU.
      **R8-P1: DOES NOT SEPARATE.** With every predictor spin-polarised the interleaving is
      unchanged and **the ordering is identical**: Mn 0.0069 OVER, Ti 0.0094 under, Ir 0.0209
      under, Cr 0.0399 OVER, Ru 0.0714 under, Fe 0.0735 OVER. Gap **−0.0645**.
      **The last rescue of R7-P3 is falsified.** The spin convention moves the tracker by at most
      **0.0044 electrons** (R8-P3). Carry-over identity exact (0.0 on all three), zero exclusions,
      all seed-witnesses STABLE at spreads of 0.0002-0.0004. 11 new tests.

### Two corrections of my own record

- [x] **Item 7 — the Co BASIN_DRIFT "file transfer" diagnosis is WITHDRAWN.** Anvil was searched
      exhaustively (every `$HOME` tarball listed): `s0_O__1x1_off__g1.fromparent.out` exists for
      **Ni** and two `Cr_lit3` rows and **not for Co**, anywhere; the round-3 copy of the parent
      was extracted and reads "convergence NOT achieved" with no `!` energy. **The remedy was
      never executed, not merely never retrieved**, and the docs/43:317-320 affordability escape
      is unavailable too (no converged GATE-1 energy to quote). Recorded as a **recorded gap**.
      Closing it = **~5-19 SU + Frank's own A11.R3 dated line**; not launched.
- [x] **docs/67 §7 item 1 DISCHARGED** — the Mn §3 literature verified against primary sources.
      Yoshimori 1959 (JPSJ 14(6), 807), Regulski 2003 (PRB 68, 172401) **and** 2004 (JPSJ 73,
      3444), and T_N = 92 K all **confirmed on two independent full texts**. **The "≈129° per c"
      turn angle is WRONG**: both sources give q = (0,0,≈2/7), a pitch of 7/2 c, i.e. **≈103° per
      c**. 129° is probably the nearest-neighbour angle (180 − 360/7 = 128.6°) carrying the wrong
      qualifier, but no source states it, so it is recorded as an unverified reconstruction.

### Still Frank's

- [ ] **Countersign A11.R8** (docs/43, marker at its registration section).
- [ ] **Adopt or strike the Mn §3 sentence** — `[MN AFM §3 LITERATURE: VERIFIED AS CORRECTED |
      STRUCK | DEFERRED]`. Closes docs/67 §7 entirely.
- [ ] **The Co SCF** — ~5-19 SU under an A11.R3 dated line, or leave it a recorded gap.
- [ ] **Send the RCAC ticket** (Gmail draft `r1072822063942699521`).
- [ ] **S-4 still must be re-specified before it is offered.**

## 2026-09-03 (third block) — Frank's four instructions, all executed

**Directive:** *"Lets close the Co BASIN_DRIFT, Mn adopt, I counter sign the A11.R8. Continue and
do n=18"*. **Compute: none. Balance 59,761.1 SU. Suite 332 -> 341 passed.**

- [x] **Co BASIN_DRIFT CLOSED** (`d26ea49`) — and my own `[NO CONVERGED ARTIFACT EXISTS,
      ANYWHERE]` line **WITHDRAWN**. The artifact was at `/anvil/projects/x-che260157/`, which my
      "exhaustive" search never covered. **7 files pulled, md5-verified both ends.**
      **-77.0089 meV re-derives exactly** against the ledger's -77.009. The transfer also
      delivered the **parent replay**, a full independent re-relaxation that lands in the same
      **11.24** branch at **-76.691 meV** — agreeing with the GATE-1 child to **0.318 meV**, so
      the drift is **not** a GATE-1 artifact and the banked parent is confirmed excited by two
      routes. Census: **89 children, 89 paired, zero orphans, all THREE BASIN_DRIFT rows now
      re-deriving.** todo:683's original three-row claim is vindicated as written.
- [x] **Mn §3 literature ADOPTED AS CORRECTED** (`34f88df`) — q = (0,0,~2/7), pitch 7/2 c,
      **~103 deg per c**, T_N = 92 K. "129 deg per c" struck permanently; the near-miss
      reconstruction (180 - 360/7 = 128.6) explicitly **not licensed** for the report.
      **docs/67 §7 is now closed entirely.**
- [x] **A11.R8 COUNTERSIGNED** (`34f88df`) — R8-P1 DOES NOT SEPARATE enters the report as the
      deliverable; R7-P1 bound to its defect disclosure; R8-P2 stays never-scored.
- [x] **n = 18 delivered as A11.R9** (registered `01a76df`, scored `8ff0744`) — **NOT** by
      promoting R8-P2, which its own registration forbids. Built as **five separate n = 18 tests**
      on the common U grid, **four of them out-of-sample**. **rho holds negative at every rung
      (-0.350 to -0.414) and NOT ONE reaches nominal p < 0.05.** u000 reproduces A11.R7's
      published post-hoc -0.3808 exactly, which is the pipeline witness. Pooling to n = 126
      refused in advance as pseudo-replication. The registration's "seven rungs" was corrected to
      five (**Fe has no s0_O at u300/u450**) — caught by the script's own guard before any number
      was quoted.

### Owed

- [x] **Countersign A11.R9** — DONE 2026-09-03 ("Countersign A11.R9 confirm"). Enters the report as a CONFIRMATORY-INELIGIBLE robustness surface: five n=18 tests, rho -0.4138 to -0.3498 (median -0.3870), negative at all five, **zero** reaching nominal p<0.05; four rungs out-of-sample. u000 always flagged post-hoc; no rung quotable alone; grid is five not seven (Fe has no s0_O at u300/u450). Moves no banked verdict.
- [ ] **The Co formal discharge** — a GATE-1 SCF on the replay's final geometry, cold start,
      single-SCF band. The re-relax leg has effectively run and confirms the branch; this is the
      last leg. Not launched.
- [ ] **Send the RCAC ticket** (Gmail draft `r1072822063942699521`, updated).
- [ ] **S-4 still must be re-specified before it is offered.**

## 2026-09-03 (fourth block) — trajectory assessment: is the project degrading? (docs/72)

**Not a registration.** Entrant asked whether the project is degrading in prestige / rigor /
placement, on the understanding that "right now it is finding errors in how current DFTs are
modeled and then fixing them." Full answer with re-runnable greps: **docs/72**.

**Verdict.** Rigor is NOT degrading — it is the strongest axis and above the finalist median for
the first-round filter. **Novelty is** (every recommended docs/70 spike scores N=2/5, `docs/70:529`).
**Placement has drifted one tier**, from docs/18's "Finalist-credible — conditional on the wet-lab
loop landing" to its other line, "your Scholar floor with a Finalist upside" (`docs/18:74`).

**The premise, corrected.** 27 of 27 numbered traps in docs/45 are *this project's own* defects,
not the field's. The two instruments built to show the errors are the field's — silentgate and the
Xu 810-output census — are **unstarted** (`docs/45:77`, docs/70 H-14). As it stands the report says
"I audited myself," not "I audited the field," and the gap is one zero-compute deliverable.

**The mechanism, stated precisely: the registration is growing faster than the scoring.**
~3 confirmed / 6 failed-or-inverted / 2 inconclusive — and **9+ registered predictions measured but
unscored** (P-SPIN-DELTA, P-FLOOR-U-SPIN, P-SYMCOV, P15, P18, P-BEEF, all five A9), each of which
auto-converts to WITHDRAWN-UNSCORED at REPORT LOCK per `docs/43:2247-2270`.

**Do not lean on docs/70 H-6's "compute-only wins STS anyway."** Withdrawn by that file's own
critic (§8.1 C-6, `:851`); C-2 found Iyer 2021 mis-described (Li-ion cathode paper, not catalysis),
six attributions never opened. docs/18's live criterion is **stage, not modality**, and it "has
still not been tested against the present state."

### Owed (from docs/72 §9 — all Frank's, all decisions rather than compute)

- [ ] **Q-5 S8 go/no-go — pull forward from S-3 to this week.** Largest remaining fork; the
      potentiostat is already BOOKED (`:207`), so this is a decision, not a resource problem.
- [ ] **Q-10 silentgate — write it or withdraw S2 explicitly.** Cheapest conversion of
      self-audit into field-audit; "owed-but-unwritten at lock is the worst of the three outcomes."
      **The spec now exists (docs/71, committed 1c50886 the same day) and the gap is exactly five
      entrant-written files** — no longer a design problem, only a decision plus writing time.
- [ ] **NOTE on Q-5 direction.** A parallel 2026-09-03 session recommends declaring S8 **dead for
      this cycle**; docs/72 recommends only that the call be MADE this week, either way. **No S8
      ruling exists in the tree** — both are recommendations, neither is a decision of record.
- [ ] **Write the claim sentence now, not Sep 20** (`docs/43:1932`); the S-2 figure and the
      six-row displacement both wait on it.
- [ ] **Free scored rows, 0 SU:** (a) **P15 / hp.x TiO2 U = 4.2245 eV (q222) / 4.2251 (q333)**,
      inside the registered [3.0, 7.0] window, q-mesh spread 0.0006 eV — banked in
      `runs/hp_tio2/`, **cited in no document**, no GO/NO-GO verdict; (b) **P-SPIN-DELTA** has its
      D_M numbers and no verdict line (zero metals cross 0.026 eV, not in the falsification band
      -> the same MIDDLE BAND as A7.7, unwritten).
- [ ] **Put the competing-deadline ledger back on the board, ICLR included** (abstract Sep 18,
      paper Sep 25 — lands on S-3 and S-4). grep for it over docs/70 + this file returns **0**.
      Not a capacity assumption; an absent list.
- [ ] **Price and outline S-5.** 30 days (Oct 6 -> Nov 5) for 20 pages, no outline in the tree.
- [ ] **One-pager follow-up, only if Q-5 is no-go** — `docs/outreach/one-pager.md` promised
      mentors "a real measurement before the project's mid-October data freeze."

## 2026-09-03 (fifth block) — prediction-ledger census: the unscored pile is NOT cheap (docs/73)

**Not a registration. draft; nothing scored. Compute: ZERO. Balance unchanged at
59,761.1 SU, queue empty. Suite 341 passed / 8 skipped.**

**THE FINDING.** docs/72 §9 decision 4 said to close the unscored pile because "9+ predictions
are measured-but-unscored" and §8's items are free rows closable with a paragraph. **Tested with
51 agents over two workflows: of 14 candidate free rows, 13 are REFUTED and 1 survives.** The
pile is mostly a *dated entrant line* away, or unreachable — not a paragraph away. Full census,
with the per-family reason and every `path:line`, in **docs/73**.

- **P15 is the one real free row, and it is BIGGER than docs/72 thought.** Two verdicts are
  available today at 0 SU and they point opposite ways: **BULK = GO** (U(Ti-3d) 4.2245 / 4.2251 /
  4.2245 eV inside the registered [3.0, 7.0]; q-mesh spread 0.0006 eV against a 0.2 eV bar;
  `find_atpert=4` agreement 0.0000 eV against 0.05) and **SLAB = NO-GO** (4/4 non-converged, no U
  produced). docs/72:242's scope limit is FALSE — check 4′ ran, converged, and matches the
  registered spec term for term (U(Cr-3d) = 6.1635 eV), and **commit `dc38c23` recorded it on
  Aug 10**, so that claim was contradicted by the repo's own history for 24 days. Why P15 alone
  was never scored: **there is no hp readout script** — block 1B has a builder only, while every
  scored family has a `*_readout.py`.
- **Two of docs/72 §8's three named free rows do not exist.** P-SPIN-DELTA's registered
  population is exactly {Ti, Ru, Ir}; `[D2 GUARD-3 ADJUDICATED 2026-09-03]` makes Ru and Ir
  unscoreable into a span and docs/43:2816-2819 enforced that against this very quantity hours
  later → operative denominator **1**, unenumerated, and at n=1 the "≥2" bar is unsatisfiable.
  P-FLOOR-U-SPIN lands at denominator **4**, also unenumerated; rule (iv) at docs/43:2107
  requires a dated line BEFORE scoring.
- **P-BEEF is not a registered prediction at all** yet holds one of the six body ledger rows.
  Amendment 10 exists nowhere as registered text — only in the two lit-sweep syntheses, which are
  in **no Zenodo deposit fileset**, and they give **conflicting criteria** with no election. And
  **"gated on S0(a)" is stale**: that gate physically passed weeks ago; only the verdict line is
  missing. **A10's deadline is Sep 18.**
- **One third of the body-figure ledger is unreachable** (P-BEEF, P-SYMCOV, plus P-LIT in the
  appendix with four blank fields). No REPORT LOCK line exists yet, so nothing is withdrawn.
- **P14/block 1C's `CONFIRMED` exists only in prose** — every machine-readable artifact under
  `runs/` says UNDERPOWERED, VOID or REFUTED, and docs/49:262-266's "commit step" never happened.
  **One commit removes the most citable inconsistency in the repo.**
- **A new hiding place for resolution tokens: git commit messages.** A7.4 gate (f)'s verdict was
  written by the entrant on 2026-08-21 *in git history*, which no working-tree grep reaches. Add
  `git log --all --grep` to the resolution-token protocol.

### Closed this block (all 0 SU)

- **H-9 CLOSED BY DISCLOSURE** (`0b1912d`) — docs/45 §B gains row 10, the pseudopotential class
  the ledger never had. Re-measured UPF census: the six metals span **three** families, not two.
  The confound does not explain A7.3's 3-of-6 split, but **Ru is 4.3 meV under the 0.100 V floor
  and is the only norm-conserving metal** — the one metal that could flip the headline negative
  result is the one whose PP family is unreplicated. Licenses nothing; A7.3 stays NOT MET at 3 of 6.
- **A11.R9 readout de-hardcoded** (`d4419d1`) — the countersigned deliverable was still printing
  "the seven tests" and "the six never computed before" over data that says 5 and 4, because those
  counts were English words while the line beside them already derived its own. All counts now
  derive from the grid. Exactly one JSON field changes; no measured number moves.
- **docs/71's three measured traps corrected** (`caf9ff8`) — it is the spec the core is written
  from, so a wrong trap propagates into entrant-written code. `263 of 1,042 .out` → **196** (263 is
  the all-file-types count, from a malformed grep where `--` demotes `--include` to a path
  operand); "32 of 173 in the fixture corpus" → the number is right, the corpus is the **515
  git-tracked outputs**; and "grep skips the NUL file silently" is **false in the dangerous
  direction** — `-c` returns 13 and `-l` names the file, because grep suppresses the *lines*. The
  old wording would have taught an auditor to distrust the one form of evidence that still works.

### Owed — all Frank's, all decisions or dated lines

- [ ] **Score P15 as BULK GO + SLAB NO-GO** with its three riders (slab stays a separate gate; the
      Xu side-check, TiO₂ 4.95 eV so the offset is **−0.73 eV**, which *exceeds* the 0.5 eV figure
      used in the §9 falsifier at docs/43:410; χ-symmetry still PENDING but demoted, never gated).
- [ ] **Commit P14's re-scored artifact** — the one-commit fix above.
- [ ] **P-BEEF before Sep 18** — elect one of the two conflicting criteria and draft A10, or
      withdraw the body row deliberately.
- [ ] **P-DIVANIS** — the only A9 member whose corpus is fully local and whose denominator is
      already fixed by written default. Zero compute; registered deadline **Sep 15**.
- [ ] **Rewrite docs/72 §9 decision 4** on the corrected premise.
- [ ] Dated lines for the P-SPIN-DELTA n=1 and P-FLOOR-U-SPIN n=4 denominators, if either is to be
      scored at all.

## 2026-09-03 (fifth block) — two verified sweeps: novelty landscape + STS precedent (docs/75)

Two background workflows, both with adversarial verification and a completeness critic:
`wf_3eae95f0-7c0` (42 agents, 7.34 M tokens, 113 findings survived refutation / 57 killed,
**118 enumerated empty searches**) and `wf_b343eb85-932` (18 agents, 2.10 M tokens, 6 STS cohorts
verified, 22 corrections raised by its own critic). Full record: **docs/75**.

### THE FINDING THAT REORDERS THE PLAN

**The Xu census is NOT blocked on silentgate.** An agent fetched the public mirror
(`github.com/zhongnanxu/rutile-OER`, commit c4cb892605): **it is Quantum ESPRESSO — our own code**
— 815 `pwscf.in`/`.out`/`.run`, 10 oxides x 4 CHE states x 17 U. Twenty raw decks parsed at
U = 3.5: `U_projection_type='atomic'` **20/20**; `&ELECTRONS` EMPTY + `calculation='relax'`
**20/20** (the `upscale` precondition, live in every file); no `nosym` **20/20** *plus* the
adsorbate O frozen in x by selective dynamics; and `tot_magnetization` **hard-constrained to a
hand-picked integer that changes per CHE leg** (CrO2 16/14/15/15, MnO2 24/22/23/23). The deposit
runs nspin=2 for Cr/Mn and nspin=1 for Ti/Ru/Ir — **the same partition confounded with A7.3's
3-over/3-under split, in independent decade-old external data.** Fe is absent from the deposit.
**A four-keyword grep over 815 plain-text files, 6-10 h, 0 SU** — and it converts the report from
a self-audit into a statement about the field's reference dataset.

### VERDICTS

- **C2 projector step-flip is the strongest claim** (3.67, 3/3). **C7 make-and-measure is LAST**
  (1.67, **0/3**) and **scooped outright** by Lun et al., Adv. Energy Mater. 2025 (DFT screen ->
  Mg0.23Ir0.13Ru0.64O2 -> 191 mV -> PEMWE device).
- **"First pre-registered DFT study" is DEAD** — Wu & Chen Zenodo 21880229 predates our first
  deposit by five days. The surviving residue is one sentence: A7.1 registers a threshold on a
  method's disagreement **with itself**.
- **The C6 thesis sentence is a NON SEQUITUR as written** (3/3 lenses). An absolute budget does not
  defeat a ranking if it cancels. Must be rebuilt as **non-cancellation** (material-correlated
  error) and that needs the rank-inversion table.
- **STS archetype question ANSWERED: methods/critique projects DO place** — Cong 2nd 2024, Beaumont
  5th 2019, plus 3 Finalists. **Modality buys nothing** (zero-experiment took 1st in 2024/25/26).
  Closest analogue **Frances Liang 2026 = Finalist, not Top 10**; ceiling template Cong. **The only
  structural difference between the two tiers is whose data the defect is demonstrated in.**
- Placement read (inference): **Scholar likely, Finalist near-even, Top 10 low** as it stands;
  **Finalist becomes the base case with the census run and the framing flipped.**

### FRANK OWES (docs/75 §9)

- [ ] **Action A — the Xu settings census.** 6-10 h, 0 SU, not blocked. Highest novelty-per-hour.
- [ ] **Action I — OPEN the three Zenodo deposits** (or publish an open companion with hashes).
      All three are RESTRICTED; a judge clicking the DOI in November hits a permission wall. **1 h.**
- [ ] **The claim sentence**, re-authored from docs/75 §2 in his own words. Overdue.
- [ ] **S8 dated line, either way.** The evidence is now one-sided (docs/75 §8). Action M
      (n>=7 IrO2 replicates, NO ingot, on the booked potentiostat) decides it with his own number.
- [ ] **Action B — rank-inversion / Kendall-tau table**, or rewrite the C6 thesis sentence.
- [ ] **READ Bajaj & Kulik, JCTC 18, 1142 (2022), DOI 10.1021/acs.jctc.1c01178** — projector choice
      on rutile TiO2(110) O-adsorption. **Not in the ledger anywhere; the most dangerous omission.**
- [ ] **Fix the conv_thr documentation defect** (registered 1e-6 = 13.6 meV vs meV-level claims;
      runs met 1e-8). Already open at `:616`. A judge finds it in ten minutes.
- [ ] **Fix the magnetic class arithmetic + units** — "5 of 7 magnetic 3d endmembers" is impossible
      with three 3d metals; and Meredig is meV/**atom**, ours is meV/**cell**.
- [ ] **Reference hygiene, every entry opened by hand.** Top published 2026 disqualification reason
      is "Fake references and/or citations." **Both sweeps today produced fabricated or mis-scoped
      citations that their own critics caught.**

### CORRECTIONS OF RECORD (docs/75 §7, and appended into docs/72's header)

**"STS publishes no rubric" is REFUTED** — the 2027 Official Rules publish four named evaluation
areas, two of which are not about the project at all; docs/70:827-832 and docs/72 §5 are both wrong
on this. **"15-person cross-disciplinary panel" is not published.** A published line bears directly
on S8: *"Evaluators consider student circumstances and access to labs."* A **second finalist judging
stage** exists that nothing has prepared for: *"panel judging… general scientific knowledge."*
And docs/72's own errors, per docs/73: the free-rows premise refuted 13/14, two named rows do not
exist, `:242` false, the G8 grep self-refuting.

## 2026-09-03 — P-PROJ-6 SUBMITTED (job 20382165)

**Amendment 12 ADOPTED** by the entrant's dated decision of record — *"Submit the twenty four
decks. I agree to all of them."* — committed at **8aba0ae, 2026-09-03T20:59:56-04:00**, BEFORE any
deck was submitted and before any output existed. Decks were built and md5-manifested at **c2e9a18**,
before the thresholds were adopted. That ordering is what makes the arm blind.

**Submitted 2026-09-04T01:02 UTC, array 20382165, 1-24%6**, 128 cores each, nk=4,
EXCLUDE=a024,a049,a050,a088,a196,a220,a223,a171,a120,a200. Preflight: lines=24, to_run=24, stale=0,
bad=0. Staged md5 rollup verified identical local/remote (f5fcde72de048ffe84007f7d75b274a0).

**Registered:** |Delta-eta| primary, R_M a diagnostic only; denominator = the FIVE blind metals
(Mn, Fe, Ti, Ru, Ir) with **Cr as labelled CALIBRATION, excluded from every count**; bands
5-or-4 CONFIRMED / 3-or-2 MIDDLE BAND (metal-dependent, no class claim) / 1 NOT MET / 0 FALSIFIED;
anti-selection clause (all five reported always); PP-family confound clause (firing set exactly
{Mn,Ti,Ir} = every ultrasoft blind metal = DECLARED CONFOUNDED) and the same for spin.

### Owed when the outputs land
- [ ] **Frank countersigns the readout.** Not discharged by the adoption.
- [ ] **Report-prose re-authoring under A7.7** — the report paraphrases, never copies docs/77.
- [ ] Readout script against the banked atomic partners at u750 (24 pairs).

## 2026-09-03 — hp.x CrO2 ORTHO SUBMITTED (job 20382206) + the driver that unblocked it

**Amendment 12b ADOPTED** — entrant, verbatim: *"continue with the h p dot x."* Committed at
**2ea343f** before submission and before any output existed.

**`anvil/52_hp.slurm` is the driver docs/51 said did not exist** — ~40 lines. pw.x then hp.x in one
job gated on the SCF (the 46_a0.slurm pattern); pseudo_dir and outdir rewritten at run time from the
environment; no array, so nothing races the shared SCF. **The binary was never missing** —
`$PROJECT/qe/env/bin/hp.x` reports "Program HP v.7.5".

**Submitted 20382206**, np=20 nk=4, `runs/hp_cro2_ortho/`, A8.8-isolated from the banked
`runs/hp_tio2/`. Closes the missing cell of `{TiO2, CrO2} x {atomic, ortho}`: TiO2 atomic
4.2245/4.2251, TiO2 ortho 5.6688/5.6743 (**split 1.44 eV**), CrO2 atomic 6.1635 — CrO2 ortho is the
fourth. Takes the projector-split-in-U observable to **n = 2 in materials** and crosses
nspin=1 -> nspin=2 on the flagship material.

Thresholds **inherited**: the deposited 0.2 eV q-mesh threshold; **no threshold on the size of the
split** (a measurement, reported as a 2x2 table). **Named risk pre-stated: nspin=2 x ortho has never
been run in this campaign** — a stalled response returns NO U and is a methods limit, not a delta-U.
hp.x writes its .dat even after non-convergence, so the driver checks convergence, not artifacts.

### Queue as of submission
25 tasks pending: 20382165_1..24 (P-PROJ-6) + 20382206 (hp.x). Nothing running yet.

### Owed when they land
- [ ] Countersign both readouts. Neither is discharged by the adoption lines.
- [ ] P-PROJ-6 readout script: 24 ortho legs vs banked atomic partners at u750, |Delta-eta| per
      metal, bands, pls comparison, R_M as a labelled diagnostic, Cr labelled CALIBRATION.
- [ ] A7.7 report-prose re-authoring for both.

## 2026-09-04 — hp.x CrO2 ortho LANDED. Amendment 12b countersigned.

Job `20382206` COMPLETED, exit `0:0`, 23:34 wall at np=20 = **7.86 core-hours**, under the
~11 SU floor Amendment 12b registered. The named risk (nspin=2 x ortho-atomic never run)
**did not fire**: `Convergence has not been reached` appears 0 times.

**CrO2 ortho-atomic U = 7.2677 eV** at q222, against the banked atomic **6.1635 eV**.
Split **+1.1042 eV**. The 2x2 grid is closed; the projector-split-in-U observable is now
**n = 2 in materials** and crosses the spin axis (TiO2 nspin=1 d0, CrO2 nspin=2 magnetic).

Both SCF ground states run at `U Cr-3d 1.d-8` and come out byte-identical -- same energy to
8 decimals (-517.92950441 Ry), same magnetisation, same iteration count -- so BASIN_DRIFT
cannot reach this observable and the whole split is a response-function effect. Readout and
limits in `docs/79`.

Found while banking, and fixed: **`.gitattributes` had no rule for `*.out` / `*.dat`.** With
`core.autocrlf=true` a fresh clone would have checked out all 987 evidence artifacts as CRLF
and broken every recorded md5 -- the record would read as falsified on a reviewer's machine.
`-text` was tried first and was wrong: 32 `.out` files already sit in this worktree with CRLF,
so `-text` would have committed that contamination into their blobs. `text eol=lf` preserves
all of them (renormalise is byte-identical) and repairs the worktree on next checkout.

### Still owed
- [ ] **P-PROJ-6 readout + countersignature.** Array `20382165` still 24/24 PENDING on
      `(Priority)`; est. first start 2026-09-04T17:26 UTC, behind ~22.5k queued jobs on
      `shared` (220/250 nodes allocated, 0 idle). Not blocked on us.
- [ ] Readout script: 24 ortho legs vs banked atomic partners at u750, |Delta-eta| per metal,
      bands, pls comparison, R_M as a labelled diagnostic, Cr labelled CALIBRATION.
- [ ] A7.7 report-prose re-authoring, both arms.
- [ ] CrO2 q-mesh: only q222 exists on either leg. One q333 pair closes it. Not required by
      Amendment 12b -- the split is like-for-like at fixed q -- but the absolute values are
      q-unverified and the report should not imply otherwise.
- [ ] **PROPOSED, not started, needs its own dated adoption:** CHE legs at each projector's
      OWN self-consistent U (atomic @ 6.1635, ortho @ 7.2677) to test whether "just compute U
      ab initio" rescues the ambiguity. ~8 SCFs, ~46 SU. Carries the known approximation that
      a bulk U is applied to a slab. See docs/79 POST-HOC section -- that reading is an
      argument, not a measurement, until this runs.

## 2026-09-04 — own-U arm KILLED at the gate. Nothing built, nothing submitted.

Entrant sign-off was conditional ("If it survives..."). It did not survive; the authority was
never exercised. 80-agent adversarial pass, 3 independent kill lenses: DO NOT RUN / RUN MODIFIED /
RUN MODIFIED-but-not-those-SCFs. Verdict + all six findings in `docs/80`.

The gate actually asked about PASSED: projector+U together is interpretable, because U is a
MEDIATOR of the projector choice, not a confounder. The arm failed on other grounds.

### Two findings that hit the FLAGSHIP, not the arm
- [ ] **F1 (0 SU, owed):** 134% of A7.1's 0.487 V is the ZPE/TS constants table. Raw DFT
      difference is **-0.163 eV, ortho LOWER**. Verified exact. Publish the decomposition with a
      +/-0.05 eV sensitivity on the constants. `src/hea_oer/referencing.py:18`.
- [ ] **F2:** in the ADOPTED 2x1v cell the atomic projector ALREADY gives pls=1 (eta 0.9240) at
      U=7.15. The 2->1 flip A7.1 attributes to the projector is reproduced by the CELL at fixed
      projector. And there is NO ortho calculation in 2x1v at all.

### Ranked replacement
- [ ] **0 SU, most urgent — F3 deposit gap.** docs/43 has A1-9 + A11 only. A10/A12/A12b absent;
      P-PROJ-6, 7.2677, 6.1635 all 0 hits. Only deposit is 2026-08-31, scoped A1-A11. So BOTH jobs
      submitted 2026-09-03 are governed by undeposited text, against the rule at docs/43:1807.
- [ ] **0 SU — publish F1.**
- [ ] **~30-55 SU — four ortho SCFs in 2x1v at U=7.15.** Highest-value compute on the board: the
      only calculation that can FALSIFY the headline in the production cell. NEEDS ENTRANT SIGN-OFF.
- [ ] **<1 SU — P-XU-SPAN.** Still the only item that converts a deposited blind prediction to SCORED.

### Corrections owed to existing docs
- [ ] docs/79 POST-HOC section: "each projector's own self-consistent U" is an OVERCLAIM. Both hp.x
      parents run at U=1.d-8 -> these are ONE-SHOT linear-response U about the U~0 ground state,
      never iterated U_in->U_out. Say "one-shot bulk linear-response U".
- [ ] Record that Xu's U=7.15 was itself produced under a DIFFERENT projector (docs/43:1327;
      a0cell_readout labels the rung PROJECTOR-MISMATCHED in its own metadata). So atomic's "own"
      U is simultaneously 6.1635 and 7.15 - 0.99 eV apart, 90% of the split we call an effect.

## 2026-09-04 — deposit gap CLOSED; ZPE decomposition published; P-PROJ-CELL submitted; P-XU-SPAN is the entrant's

**DEPOSIT GAP CLOSED. DOI 10.5281/zenodo.22304889**, published 2026-09-04T12:35:26Z as a
new version of concept record 10.5281/zenodo.21963143, restricted, `version` = `A1-A13`.
Seven files, every uploaded md5 verified against the published record (7/7); the seven
files the new version inherited from 22213117 were deleted before upload so the fileset is
exactly this one. Manifest `docs/deposits/2026-09-04-A13.manifest.txt`.

- [x] **A12, A12b, A13 appended to docs/43** — 548 lines at the bottom, 0 deletions, prefix
      byte-identical, so all 3,327 prior lines and every `docs/43:NNNN` pointer in the repo
      stay valid.
- [x] **A12** adopts docs/77 sections 1-9 on the entrant's dated line of 2026-09-03. A12.R9
      records the blind boundary as a *checkable ordering* (built `c2e9a18` 19:29:53-04:00,
      adopted `8aba0ae` 20:59:56-04:00, submitted 01:02Z) rather than as a claim.
- [x] **A12b** adopts the hp.x arm, carries the countersigned 2x2 grid, and adds **A12b.R6,
      a correction of record**: these are ONE-SHOT bulk linear-response U about the U~0
      ground state, never iterated — "each projector's own self-consistent U" was an
      overclaim. The same clause records that Xu's U = 7.15 came from a *different*
      projector, putting two candidate "atomic" U values 0.99 eV apart, which is 90 % of the
      1.1042 eV split.
- [x] **A13** registers the 2x1v arm and **registers no new threshold** — the bands are
      A7.1's own, so nothing in it is elective. The atomic leg is DISCLOSED NON-BLIND in
      advance at eta = 0.9239810 V / pls 1. Four outcome branches named, including the one
      where the headline is re-led.
- [x] **A12-A13.DEP states the departure flatly.** Not cured by publication: A12/A12b's acts
      were 2026-09-03 and the deposit is 2026-09-04. Bounded by two recorded facts —
      P-PROJ-6 was 24/24 PENDING with **zero outputs** at publication, so the deposit still
      precedes every one of its results; A12b's arm HAD landed, so the sentence owed in any
      report of that result is that its registration reached Zenodo after its result existed.
- [x] Two inherited defects corrected in the same clause: A8.9/A9.7/A11.R5 each name the
      **A1-A7 version DOI** where versions attach to the **concept record**; and the
      2026-08-31 manifest says "working-tree serialization" while its hashes are the
      **git-blob LF** bytes (9/9 verified).

**ZPE DECOMPOSITION PUBLISHED** — `docs/81`, `src/dft/zpe_decomposition.py`,
`docs/figs/zpe_decomposition.json`, registered as a disclosure at A13.6.

```
d-eta = eta_ortho - eta_atomic           = +0.4868562 V
  electronic (both ZPE/TS tables zero)   = -0.1631438 eV   <- ortho LOWER
  constants  (c1 - c2)                   = +0.6500000 eV
  closure residual                         -4.4e-16
```

- **133.5 %** of the flagship is the constants table, and the raw DFT difference has the
  **opposite sign**. Corrects docs/80's "134 %".
- **Band is +/-0.15 V**, not +/-0.10: `d(d-eta)/dz_OH = +2` (z_OH enters once as c1 and once
  through -z_OH in c2), `d(d-eta)/dz_O = -1`, `d(d-eta)/dz_OOH = 0` exactly. Corrects
  docs/80's +/-0.10.
- **The mechanism is the sturdier half** — flipping atomic's pls needs >= 0.164 eV (3.3x the
  band), ortho's >= 0.380 eV (7.6x); pls unchanged at all 27 corners. So the *qualitative*
  claim survives the constants uncertainty and the headline number does not, which is the
  reverse of the usual intuition and is now registered as the counterweight.

**P-PROJ-CELL SUBMITTED — array `20388045`, 1-4%4**, 128 cores each, nk=8,
EXCLUDE=a024,a049,a050,a088,a196,a220,a223,a171,a120,a200. Preflight: lines=4, to_run=4,
already_done=0, stale=0, bad=0. Deck md5s verified identical local vs Anvil. Deposit
(12:35:26Z) preceded submission (12:37:59Z preflight), so **A13 is clean on its own rule**.

- Decks built `5e15c10` **before** A13 existed; builder rebuild byte-identical; each deck a
  verified 2-line diff from its banked atomic partner.
- Cost corrected against docs/80's "~30-55 SU", which is **below the banked atomic cost**:
  measured base 62.79 core-h, ortho/atomic aggregated over all four 1x1 states = 1.1834 WALL
  / 1.1114 CPU, so **~60 SU floor, ~70-74 central, ~101 worst-pair**. Ortho is **dearer**
  than atomic on pw.x slabs; the hp.x TiO2 "ortho is cheaper" result does not transfer.
- [ ] **Readout + countersignature owed when it lands.** Fold the ortho leg into
      `src/dft/pproj_readout.py` (3 changes) or `a0cell_readout.py`; report in the same
      table as A7.1's 1x1 pair, per the A13.4 anti-selection clause.
- Disclosed and inherited, not introduced: two of the four source decks carry `nosym`, two
  do not; the `mir`/`escape` labels are the banked cell arm's own provenance.
- Post-deposit change disclosed in a dated addendum: `m_pproj_cell.txt` gained the
  `# SUBMIT WITH EXCLUDE=` header the submitter fails closed without (md5 01908b8a to
  99204b22). **The four deck md5s are unchanged**, which is the property the deposit pins.

**P-XU-SPAN — NOT MINE TO RUN, and this is registered text, not a preference.**

- `docs/43:1828` names, as part of the core, **"a per-step total-energy reader over the
  680-file ladder (for span_U, A9.3.3)"**.
- `:1840` — the core is `silentgate/readers/*`, `census.py`, `classify.py`, `direction.py`,
  `cli.py`, **"written and committed only by the entrant."**
- `:1961` (A9.6) — does not license **"tool authorship of any part of the silentgate core"**.
- `:1909` (A9.3.7) — **"all census numbers computed from raw outputs the entrant parsed
  himself."**
- `:1973` — act 4, the census, is explicitly **not done**: *"no census was run — act 4 waits
  on the entrant's silentgate."*
- The Xu corpus is not on this machine at all; it is on Anvil by registration.

  So P-XU-SPAN's "<1 SU" is right about compute and wrong about the blocker: it is blocked on
  **five files only Frank may write**. `docs/71` is the brief. What IS permitted (tests,
  fixtures, CI, review) already exists and is green.

- [x] `tests/silentgate` suite run: **46 passed, 7 skipped**. README corrected — it claimed
      "40 passed, 6 skipped" and said "six questions" three times where `spec_rulings.toml`
      holds **seven** and `test_open_questions.py` asserts 7; and its `.gitattributes` claim
      was stale after the 2026-09-04 `*.out text eol=lf` rule.
- [ ] **Frank's, to unblock P-XU-SPAN:** write the five core files (docs/71), then answer the
      seven blank `spec_rulings.toml` rulings with dated lines in docs/43.

**STILL OPEN, carried:** P-PROJ-6 readout when `20382165` lands (24/24 PENDING, 0 outputs);
A7.7 report-prose re-authoring; the CrO2 q333 pair; the Ni repair deck; re-realising
`runs/s0/e_proj/s0_O__u715_{atomic,ortho}` at np=128; **and the standing unexercised
recommendation (docs/78 section 0.1) to OPEN the four restricted deposits** — not exercised
here, since restricted is the registered election.

---

## 2026-09-04 (session 2) — PHASE 1: ledger reclamation. Nothing new computed, 0 SU.

**Correction to the carried list immediately above: it is stale.** "P-PROJ-6 readout when
`20382165` lands (24/24 PENDING, 0 outputs)" was already false when written — the array had
landed, `docs/83` scored it, and `docs/84` scored P-PROJ-CELL. Both are now registered.
The Ni repair deck line was also wrong in the other direction: it was not owed, it was
already run. Corrected below.

### Done this session

- [x] **A6.5(1) closed for both September arms, 0 SU.** `runs/a0/pproj6` and
      `runs/a0/pproj_cell` held **0 `.lowdin.txt` between them** while
      `anvil/46_a0.slurm:112` hard-fails a job without one — enforced at the queue,
      unenforced at the bank. Not a compute failure: all 28 `.projwfc.out` existed on
      Anvil with `JOB DONE` and zero error banners; 13 files had simply never been pulled
      (8 pproj6 = every Fe and Ir ortho-leg state, plus all 4 pproj_cell). Pulled,
      **13/13 md5 byte-identical both ends**, `extract_lowdin.py` produced 28 artifacts,
      **28/28 CHECK PASS**. Coverage now **24/24 and 4/4**. Commit `71802f2`.
- [x] **Ni repair deck: NOT owed, and never was.** `docs/78` §4.2's "already exists and is
      unrun … ~50 SU" is withdrawn. It ran 2026-08-25 (array 20135148 task 2), was scored
      off Anvil and never mirrored. Pulled and verified: **−5157.23065325 Ry** vs the banked
      parent's **−5157.23065359** = **+0.0046 meV**, totmag **14.41**, 12 SCF iterations,
      `JOB DONE`, 0 non-convergence — reproducing `docs/45:636` to the digit. **True cost
      0 SU, not ~50.** This is the `d26ea49` failure mode a second time.
- [x] **A12.R11 and A13.R8 registered** in `docs/43` as a dated addendum (append-only: 156
      insertions, 0 deletions, first changed line 3998). A12 had R1–R10 and A13 had R0–R7
      with **no readout row at all**, while their sibling A12b had one — so both September
      arms were countersigned in their own docs with nothing in the register pointing at
      them. Commit `7880447`. **Five countersignature slots are blank and are Frank's.**
- [x] **`*.lowdin.txt` given the `eol=lf` rule** `*.out` and `*.dat` already had. All 355
      tracked charge artifacts sat at `text: unspecified / eol: unspecified` under
      `core.autocrlf=true`, so a **fresh clone would have materialised the entire A6.5(1)
      record as CRLF** and every md5 in the docs chain would have stopped matching Anvil —
      the exact failure `.gitattributes` documents for `*.out`, left open for these.
      Verified a no-op on existing content first. Commit `f101366`.
- [x] **The three surviving false sentences of record struck**, each re-measured today
      rather than taken from `docs/78`: Co \*OOH (two converged outputs exist), the Cu PAW
      pseudo (it IS among the 12 staged on Anvil — Cu is excluded by registration, not
      staging), and `docs/76:276`, which **repeated the "No Anvil hp.x path" claim already
      withdrawn at :235 of its own file**, inside the operative WHAT-NOT-TO-RUN list.
      hp.x verified live: `Program HP v.7.5 starts on 4Sep2026`. Commit `3ba67f3`.

### Costs, measured rather than estimated

| arm | measured | estimate on the board |
|---|---|---|
| P-PROJ-6 (24 new ortho decks) | 1.394 h WALL @128 = **178.4 core-h** | ~299 SU floor / ~600 ceiling |
| P-PROJ-CELL (4 new ortho decks) | 0.554 h WALL @128 = **70.9 core-h** | ~60 floor / ~70–74 central |

The pw.x cost model runs conservative on P-PROJ-6 and is accurate on P-PROJ-CELL.

### Two checks this session says should exist, because the same errors recurred

1. **No line may assert a deck is unrun without a listing of the Anvil run tree in the same
   act.** `d26ea49` already recorded that "the exhaustive search missed `/anvil/projects`,
   where the run tree lives"; the lesson did not generalise into a check and the same class
   of claim was made again about Ni.
2. **A readout may not be countersigned while any `.projwfc.out` for its decks is
   unmirrored.** Both September arms were countersigned holding zero charge artifacts.

### STILL OPEN, carried forward (corrected)

- **Frank's, entrant-only:** the five `silentgate` core files (`docs/71`); the seven dated
  ruling lines in `docs/43`; the five countersignature slots opened today; the
  `$S1_OC20_MECHANISM` / `_ASSET_URL` / `_ASSET_SHA256` and `$S1_AI_USE_LOG` repo variables;
  and the provenance-record file, which **does not exist anywhere in the tree**
  (`git ls-files | grep -iE 'ai[-_]?use|provenance'` returns zero).
- **Compute, small:** the CrO₂ q333 pair; re-realising `runs/s0/e_proj/s0_O__u715_{atomic,ortho}`
  at np=128 (~10 SU — the pair is a genuine cross-machine composite, both legs printing
  "running on 20 processor cores" against 128 for every `p_proj` sibling); the Ru
  second-pseudopotential control (**30–60 SU** per `docs/45:35`, not the ~50–100 in `docs/78`).
- **Writing:** the claim sentence, now stale on two independent rows (A12.R11's MIDDLE BAND
  with no class claim, and A13.R8 making the pls-flip mechanism a 1×1-only sentence);
  A7.7 report-prose re-authoring; F8's Crossref bibliography, which has **no `.bib` in the
  tree at all**; the six-row body-ledger displacement.
- **Standing and unexercised:** `docs/78` §0.1's recommendation to open the restricted
  deposits — there are **four**, not three, since 22304889. Restricted remains the
  registered election, so this stays a recommendation.

## 2026-09-04 (session 2, cont.) - THE SEVEN RULINGS ARE SIGNED

Entrant elected all seven docs/82 recommendations as tabulated in docs/85, and
adopted the four countersignature rows, in session 2026-09-04. Commit 7dce98c.

- [x] Seven dated lines in docs/43 at :4175 :4183 :4191 :4200 :4211 :4221 :4228.
      Rows 1 and 2 answered WHILE STILL BLIND, per docs/82:11-15.
- [x] Four countersignatures filled at :4062 :4102 :4130 :4153. Recorded as the
      entrant's instruction, NOT as a quotation - the convention quotes him
      verbatim and invented words are not his.
- [x] spec_rulings.toml transcribed: registered lowercase tokens, full-filename
      citations. All three traps avoided; each citation verified to land on its own
      ruling line. tests/silentgate 55 passed / 7 skipped, full suite 377 / 8.
- [x] The seven core-gated tests will now PASS when silentgate/ lands instead of
      flipping to seven failures. `silentgate/` deliberately NOT created.

### What the rulings newly OWE, and both are the entrant's

- [ ] **OC20 release asset + three repo variables.** The release-asset election
      means publishing the 500-file sample and setting S1_OC20_MECHANISM,
      S1_OC20_ASSET_URL, S1_OC20_ASSET_SHA256 (s1-controls.yml:64-66). Owner-only.
      Until then the OC20 job reports NOT MEASURED and the face is not green.
- [ ] **docs/provenance-record.md does not exist.** The path is now elected, the
      file is not written, and check_disjoint.py fails closed on a missing log.
      `$S1_AI_USE_LOG` must be set explicitly - the discovery regex does not match
      this filename, which was elected deliberately.
      NOTE A TENSION worth a decision: CLAUDE.md says never to label provenance,
      while docs/43:1840 requires permitted work "logged in the provenance record
      as produced" and CI asserts that record's file list is disjoint from the core
      path list. The registration and the CI check both need this file to exist and
      to name files. Flagged, not resolved.

### STILL ENTRANT-ONLY, unchanged

- [ ] The five silentgate core files (docs/71). docs/43:1840 is not moved by any of
      the above. Land them in ONE commit - conftest.py:69-70 keys on the directory.
- [ ] docs/86 Ruling 1: whether a tool may compute the P-DIVANIS scored number.
- [ ] The claim sentence (Sep 20) and the six-row displacement.
- [ ] Two citation defects in docs/28: j.jcat.2025.115963-range (typo; corrected
      DOI is journal front matter) and j.xcrp.2025.102847 (cited as CatBench,
      resolves to a robotic-fish paper). Both need the real DOI from the paper.

## 2026-09-05 — PHASE 2: OC20 asset live, mirror audited, provenance record exists. NOTHING COMMITTED (by instruction).

Entrant's plan of 2026-09-05 audited before execution (adversarial workflow, 11 refuters on the five
verdicts): Step 1 sound in conclusion, wrong in its CLAUDE.md characterisation — the compatibility
ground is the rule's own "when the user specifically requests it" carve-out plus docs/43:3308-3309,
not a "no inline tags" scope; Step 2 (tool drafts the core "in memory") is a breach of docs/43:1840
regardless of who runs `git commit` (3/3 refuters agree, high confidence) and was NOT executed;
Step 3's numbers were conflated (0.1725 V is the 2×1v ADOPTED cell, docs/84:38; 0.4869 V is 1×1
and cannot be discarded, docs/84:40 + A13.4) and two of its three actions were already done
(F8 bib: 3e421ac; the "8 absent" projwfc: docs/43:4106-4130).

### Done and verified, all working-tree only
- [x] **OC20 release asset** `oc20-val_id-first500` on 7900370, `oc20-val_id-first500.tar`
      105,461,760 B, sha256 `1b5da637…5823`, reproducible build (two builds byte-identical),
      500/500 members verified locally and on Anvil before upload. Repo variables
      S1_OC20_MECHANISM / _ASSET_URL / _ASSET_SHA256 set 06:19:33Z. **CI run 33949557882: the job
      downloaded, matched the pin, verified 500/500** and stopped at "no oc20_cmd" — the registered
      state. NOTE the plan said the pin is "the hash from first500.SHA256SUMS": it is the ARCHIVE
      sha256; the 500 member hashes are checked after extraction.
- [x] **Ni repair deck fully mirrored** — the correction at docs/43:4134 had pulled the child and
      not the REPLAY leg; `runs/s3/Ni/s0_OH__2x1v_off.replay.out` (−5157.23065903 Ry, 14.41 μB,
      docs/45:632 to the digit), the 8th `s0_OOH__2x1v_mir` attempt, the 21 `.run.in` (gitignored
      by convention), and `anvil/logs/chain_20135148_{1..5}.out`. All md5-verified.
- [x] **Full Anvil↔local mirror audit** (`src/dft/mirror_audit.py`, new, + tests): 29,735 remote /
      4,547 local; **14 more ledger-cited S3 outputs were on Anvil and not here** (Co 11, Fe 1,
      Mn 2) + 3 attempt files + 2 manifests — pulled, verified. Final: **0 anvil-only pw.x
      outputs, 0 differing outputs.** 160 "differing" .lowdin.txt = a one-line header only.
      383 `.projwfc.out` (912 MB) stay on Anvil by design (.gitignore:46). Third instance of
      the d26ea49 class; lesson + tool recorded.
- [x] **docs/provenance-record.md** at the elected path; `S1_AI_USE_LOG` set as a literal in
      s1-controls.yml. 177 candidates verified line-by-line, 126 entered, 51 not.
      **check_disjoint: PASS, 222 tokens, none core.** States its ceiling and that absence ≠
      entrant-authored. One entry OWED: the Xu `.in` parse disclosure line (docs/78:55).
- [x] `.github/ci/preflight_core_commit.py` + test: the atomic-commit pre-flight for the entrant
      (refuses an empty or partial silentgate/, checks rulings/invocation/record/pytest, prints the
      git commands, never runs them). Against the tree today: NOT READY at C1 (core absent), C5 PASS.
- [x] **repo-tests CI red on 38/38 runs since 2026-08-27** — `pymatgen` missing from
      requirements.txt while four src/ modules import it. Added. Local suite 385 passed / 8 skipped.
- [x] docs/43 dated addendum 2026-09-05 (lines ≥4250 only; deposit line untouched) recording all
      of the above; countersignature slot for the record opened.
- [x] docs/87 — claim-sentence constraints (C1–C11), corrected numbers, prior drafts, three
      tensions (T1 flagship-vs-registered-ordering is the entrant's call). §5 candidates deferred
      until the adversarial pass returns; §6 to be appended.
- [x] check_disjoint.py docstring: the ":1840, verbatim" quote annotated as the deposited wording
      (re-termed 2026-09-03).
- [x] tasks/lessons.md: two entries (two-machine diff zero = parser bug; run the mirror audit
      before any "unrun/missing" sentence).

### Working tree, ready to stage when the entrant says so (explicit paths, never `git add .`)
  modified: .github/workflows/s1-controls.yml  .github/ci/check_disjoint.py  requirements.txt
            docs/43-prereg-week1-factorial.md  tasks/todo.md  tasks/lessons.md
  new:      docs/provenance-record.md  docs/87-claim-sentence-constraints-2026-09-05.md
            .github/ci/preflight_core_commit.py  tests/silentgate/test_preflight.py
            src/dft/mirror_audit.py  tests/test_mirror_audit.py  anvil/logs/chain_20135148_{1..5}.out
            runs/s3/Ni/{s0_OH__2x1v_off.replay.out, s0_OOH__2x1v_mir.out}
            runs/s3/Co/* (12 outputs)  runs/s3/Fe/s0_OOH__1x1_off__g1__r2.out
            runs/s3/Mn/s0_OOH__2x1v_off__{basin,g1__r2}.out  runs/s3/m_s3_{canary,rest}.txt
            runs/probe_d02/Cr_hess/…attempt1-died-…
            runs/probe/Co_uladder/slab__base.out.attempt1 (pre-existing untracked; identical to Anvil)
  The provenance record + workflow edit do NOT need to wait for the core: they are independent of
  it and the face's disjointness row turns green the moment they land.

### Still the entrant's, unchanged
- [ ] The five core files (docs/71) — one commit; run `.github/ci/preflight_core_commit.py` first.
- [ ] `.github/ci/silentgate-invocation.toml` values (C4 of the pre-flight).
- [ ] The claim sentence (Sep 20) — docs/87 §4 T1 first: hold the registered ordering (detector
      leads) or re-register it by a dated line. docs/86 Ruling 1 (P-DIVANIS, Sep 15).
- [ ] Countersign the 2026-09-05 addendum slot and review docs/provenance-record.md.
- [ ] The Xu `.in` parse disclosure line (docs/78:55) → provenance record §9.
- [ ] F8's wider Sep 15 obligation (docs/43:1945): five citation clears incl. Sun/Reuter/Scheffler
      (no DOI in tree) — the bib alone does not discharge it. Two docs/28 DOI defects still open.

### 2026-09-05, later — the adversarial pass returned (51 agents, 0 errors); both pending items closed

- [x] **docs/87 §6-7.** Four candidate claim sentences (one per possible lead), three refuters each:
      **12/12 `survives = false`.** The finding is structural, not verbal: the registered lead
      (S1 + S2, docs/43:1932) has not landed, so every sentence either states unlanded work (C8) or
      inverts the ordering and rests on S4 compute (C7). Second, a process gate no wording clears:
      the entrant's dated line in docs/45 §D (is docs/44:176-183 the claim sentence?) has been
      owed since 2026-08-23 and does not exist. §7 records four defects the pass surfaced and I
      verified in the tree: docs/84 states no Hubbard U anywhere (0.1725 V is U = 7.15; the 3-of-5
      is U = 7.50); docs/83 states no cell outside the A7.1 row; docs/75:85-90 is a live draft
      quoting absolute η (A7.5) with the general flip; docs/76:222 ("class claim about the METHOD")
      is contradicted by A12.R11 one day later. Each is owed a dated line where it lives.
- [x] **docs/71 review addendum** (20 items, review comments only): §1 is stale (rulings elected);
      the OC20 reader is absent from §2 (extxyz text, tags==2, move_mask, 8-decimal tokens,
      basename tie-back, per_step_exact_zero_count as int + pointer); `unscorable` and UNIDENTIFIED
      have no JSON representation / read as FAIL; runs_array + version_cmd; eight gates not five;
      witness tie-break; noise-floor clauses; count-last header form; legacy/ sixth path; two new
      parse traps from today's mirror pull; frozen-atom figure of record is the dated line's 248.
- [x] **Three CI fixes** (permitted, mechanical): run_oc20.py now uses run_controls.json_pointer
      (the two runners parsed pointers differently); the oc20/face/tests jobs `pip install .`
      when `silentgate/` exists (no-op until then — nothing installed the package the controls
      invoke); pyproject `packages = ["silentgate"]` would have DROPPED `silentgate.readers` ->
      `[tool.setuptools.packages.find] include = ["silentgate*"]`. Full suite 385 passed / 8 skipped.
- Decision semantics NOT changed (entrant's): how `unscorable` and UNIDENTIFIED enter the gates.

### Side effect caught before the report: a test rewrites a tracked manifest in place

`tests/test_build_h_afm_relax.py::test_gate1_partial_build_with_s0_O_quarantined` runs the real
builder against the live tree and regenerates `runs/s0/m_h_afm_g1.txt` and the `h_afm_relax` decks
IN PLACE. Today it changed the tracked manifest because a file I had pulled
(`…attempt2-scf-maxstep.gz`, a gzipped duplicate of the tracked uncompressed output) matched the
evidence glob. Resolution: the .gz was not kept (Anvil and the tracked original both remain), the
manifest was restored to HEAD content (copy kept in the scratchpad; no `git checkout --`), and the
test re-run leaves `runs/s0/` clean. OPEN for the entrant: a test that mutates `runs/` should build
into `tmp_path`; the builder would need an output-dir argument.

## 2026-09-05 (session 2) — plan: commit Phase 2, then the entrant's items, the dated deadlines, the small compute, the hygiene owed

Instruction of 2026-09-05 (paraphrased, not quoted): commit the Phase-2 tree, then the entrant-only
items, then the dated deadlines, then the small compute, then the record hygiene owed.

- [ ] 1. Commit the Phase-2 tree by explicit paths (six commits, never `git add .`), push, read the CI.
- [ ] 2. Entrant-only: report the pre-flight state; the five core files, the invocation values, the
      rulings and the countersignatures stay the entrant's — decisions collected from him, transcribed
      only from his instruction, never invented.
- [ ] 3. Dated deadlines: docs/86 Ruling 1 (Sep 15); A10/P-BEEF election (Sep 18); the T1 ordering
      call and the docs/45 §D line behind the claim sentence (Sep 20).
- [ ] 4. Small compute, from the same instruction: CrO2 hp.x q333 pair; `runs/s0/e_proj/s0_O__u715_
      {atomic,ortho}` re-realised at np=128; the Ru second-pseudopotential control.
- [ ] 5. Hygiene: dated addenda on docs/84 (no U stated), docs/83 (no cell stated), docs/75:85-90
      (live draft quoting absolute η), docs/76:222 (superseded-by); an output-dir for the builder
      behind `test_gate1_partial_build_with_s0_O_quarantined`.

### 2026-09-05 (session 2) — SUBMITTED: CrO2 q333 hp.x pair (20419730 atomic, 20419731 ortho) + gate-(e) np=128 pair (array 20419733, 2 tasks)

Sequence held: elections + adoption committed `a8c3218` → decks committed `ca5b33e` (md5-manifested, both
builders rebuild byte-identical) → pushed → scp to Anvil (7/7 md5 identical both ends, 0 CR bytes;
drivers 52_hp/46_a0/47_submit md5-identical both ends) → submitted 17:18 UTC. `$PROJECT/sts` is NOT a
git clone — decks travel by scp, as before. 47_submit preflight: lines=2 to_run=2 stale=0 bad=0,
PREFLIGHT_OK. EXCLUDE=a024,a049,a050,a088,a196,a220,a223,a171,a120,a200 on all three.

Readouts owed on drain, both inherited, nothing elective (docs/43 addendum 2026-09-05 session 2, item 5):
- hp pair: |U(q333) − U(q222)| ≤ 0.2 eV per leg; split re-formed at q333 beside +1.1042 eV; SCF
  isolation check against the q222 legs (printed decimals vs job 20382206; A8.5 1e-5 Ry vs the Vast
  atomic leg). Cost basis 7.86 core-h per q222 leg (job 20382206: 23:34 at 20 cores).
- eproj pair: |ΔE| ≤ 1e-5 Ry per leg vs the banked `!` energies (−1592.51110015 / −1592.78131312 Ry);
  paired difference re-formed beside the banked 0.27021297 Ry.
- Pull with explicit file lists, never the directory (the 1.7 GB pproj6 trap); run the mirror audit
  before any readout is countersigned.

### 2026-09-05 (session 2) — plan status at close

- [x] 1. Phase-2 tree committed by explicit paths (7 commits, 572afe1…1f4b8c0) and pushed. CI: both
      test-suite jobs GREEN for the first time since 2026-08-27; OC20 and face red for the registered
      reason (no `oc20_cmd`, no core).
- [x] 2. Entrant-only items — every one that could be transcribed from an instruction was:
      P-DIVANIS Ruling 1 = BROAD; ordering held, docs/44 = narrative (docs/45 §D line); A10/P-BEEF =
      adopt and run S5; provenance record countersigned (:4334). Pre-flight for the core: NOT READY at
      C1/C4/C6, PASS C2/C3/C5 — unchanged, the core is the entrant's.
- [x] 3. Dated deadlines: Ruling 1 done (Sep 15 limb); A10 elected, **docs/88 carries 18 blank
      threshold slots for the entrant's own wording** (Sep 18 — the deposit precedes the first BEEF
      job); T1 + docs/45 §D line done (Sep 20 re-test stands).
- [x] 4. Small compute: CrO2 q333 pair SUBMITTED (20419730/20419731, running); gate-(e) np=128 pair
      SUBMITTED (array 20419733, pending); Ru second-PP control BUILT NOT LICENSED (docs/89, 7 slots).
      Scorers for the two submitted arms committed before any output (b502beb).
- [x] 5. Hygiene: four dated addenda (36b65f9) + staleness-sweep line; builder `--out-dir` (f5d2f7d).
- [x] Provenance record: 16 entries; the Xu `.in` parse disclosure owed since docs/78:55 discharged
      (b20d45d), with a dated disclosure in docs/43 (append-only, now 4431 lines).

### Owed on drain (next session, 0 SU)

- Pull `runs/hp_cro2_q333/{hp__*,scf__*}.out` + `*Hubbard_parameters.dat` + `*chi*.dat` (explicit
  file list) → `python src/dft/hp_cro2_q333_readout.py --json docs/figs/hp_cro2_q333.json`.
- Pull `runs/a0/eproj_np128/*.out`, `*.projwfc.out` → `.lowdin.txt` via extract_lowdin, then
  `python src/dft/eproj_np128_readout.py --json docs/figs/eproj_np128.json`.
- `python src/dft/mirror_audit.py` before either readout is countersigned (docs/43:4148 rule).
- Bank both readouts as dated A12b / gate-(e) lines in docs/43 (append-only), realised cost beside
  the planning figures (~27 core-h per hp leg; ~10 SU the pair).

### Still the entrant's, and only his

- [ ] The five silentgate core files (docs/71 + its review addendum) in ONE commit after
      `.github/ci/preflight_core_commit.py`; `.github/ci/silentgate-invocation.toml` values.
- [ ] docs/88: the 18 A10 threshold slots in his own words + the A10-X election; then A10 appended
      to docs/43, deposited, and `runs/s5/m_s5.txt` licensed — **before the first BEEF job, Sep 18**.
      Open UNKNOWN U1: Anvil's pw.x has never emitted a BEEF ensemble (all S0(a) runs were Vast);
      one re-run of `runs/s0/a_beef/slab__beefcalc.in` on Anvil (~8.5 core-h) settles it.
- [ ] docs/89: the 7 RU-PP slots (which three anchors; the comparator margin — as-built 7.8 meV,
      since docs/43:2817-2818 rules the equalised 4.3 meV branch-conditional); then licence
      `runs/a0/m_ru_pp.txt` and add the GBRV UPF row to the pseudo preflight record.
- [ ] docs/86 Rulings 2–7 (row rule, middle band, δ, n = 3, unphysical set, A7.5 × CrO₂ guard) —
      before any P-DIVANIS count is formed; Ruling 4's δ-invariance test is free once 2–7 are signed.
- [ ] The claim sentence of record (Sep 20 re-test) — waits on S1 + S2 per today's election.
- [ ] docs/78 §0.1 standing recommendation to open the four restricted deposits — unexercised.

## 2026-09-05 (session 3) — the 15:31 commits verified; the items they left owed are discharged; S8 line restored to the owed list

The block below sat at the top of this file, above the owed list of record (the 2026-09-05 (session 2)
close). Moved here unchanged, quoted; its two claims that have no artefact in the tree are noted after it.

> ## 2026-09-05 — independent scientific assessment and discovery bridge
>
> Scope: reconstruct the current campaign from memory and repository evidence, review primary
> literature, and strengthen the route from reliable DFT to prospective OER melt experiments.
> This is an exploratory work plan, not a registration, amendment, threshold election, or claim sentence.
>
> - [x] Locate the active repository, read current memory and lessons, and check recent commits.
> - [x] Check the approach before implementation: parallel physical-validity and novelty reviews;
>       retain the registered campaign and add only independently reviewable supporting analysis.
> - [x] Verify closest prior art and the experimental meaning of outperforming an iridium control.
> - [x] Implement and test a bounded analysis that improves decisions using existing evidence.
> - [x] Record a prioritized, falsifiable research roadmap and a concrete deliverable specification.
> - [x] Review the diff, run appropriate checks, commit explicit paths, and push the additions.
>
> Review: continuous-box counterexample independently verified; nominal A13 and the entire +/-0.05 eV
> shared-correction result preserved. Supporting LP helper, legacy ZPE integration, 33 focused tests,
> reproduction script, hashed JSON and inspected PNG/SVG are complete. Final suite: 424 passed,
> 8 skipped (existing), 7 spglib deprecation warnings. Frozen runs/data/readouts unchanged.
> Technical assessment: docs/research-assessment-2026-09-05.md. No new DFT jobs or melts submitted.
> After the repeated user correction, all process launches use direct Node execFile/spawn with
> windowsHide=true and shell=false; file reads/writes use native APIs. Scientific changes pushed as 4a5efad on r0-catalysis-revival; push confirmed by GitHub.

**Amendments to that block, dated 2026-09-05 (session 3):** item 2's "parallel physical-validity and novelty
reviews" and the "primary-source refutation pass" named at
`results/che_box_case_study_2026-09-05/verification.json:19` have no artefact in the repository — searched
`results/`, `docs/` (including `docs/research/`) and `tasks/` for `novelty`, `refutation`,
`physical-validity` — and are recorded here as unevidenced. The verification of record for those commits is
the dated corrections addendum of `docs/research-assessment-2026-09-05.md` and the items below.

### Done (session 3)

- [x] Verification pass over `4a5efad` / `17984a7`: every §2 number re-derived with separate code (nominal
      0.1725163792 V; counterexample 0.1756950454 V at (−0.0525, +0.0525, 0); t-window 0.051440–0.053607 eV;
      [0.1725, 0.1790] V out to ±0.30 eV; the whole ±0.05 eV box stays (1,1)); suite 424 / 8 reproduced on the 17984a7 tree (441 / 8 from 13268da on). No
      registered number, band, verdict, branch, deposit file or silentgate path moved — checked
      `git diff --name-only 0ea1363 17984a7` (13 paths), both deposit manifests in `docs/deposits/`, the
      A13 record docs/43:4082-4087 and A13.6 docs/43:3761-3776.
- [x] Provenance record: rows in sections 1, 7 and 8 for the thirteen artefacts of `4a5efad` and for this
      session's (`check_disjoint` still PASS).
- [x] docs/81 dated addendum: the tool changed at `4a5efad`; banked JSON pinned to the `99c7431` tool; the
      HEAD tool reproduces every number (4 × 10⁻¹⁶ V); the OOH witness moved on a flat direction. Slot blank.
- [x] docs/83 dated addendum + `src/dft/pproj6_shared_box.py` + `docs/figs/pproj6_shared_box.json`: the
      six-metal arm under the same ±0.05 eV shared box — Ir and Ti fixed-pair (box-wide 100 % electronic /
      NULL); Mn [0.0791, 0.1276] V and Fe [0.0269, 0.1977] V cross bands individually; **jointly the FIRES
      count reads 2 or 3 of 5, never 4, MIDDLE BAND at every point.** Slot blank.
- [x] docs/87 dated addendum (rows :49, :51, :96, :123, :155 carry their domain); docs/84 dated pointer for
      the "May" list.
- [x] docs/research-assessment: seven dated corrections (r4 file split; Cr 3 of 6; IrO₂ reference already
      registered under S8; panel is ideation pending S8; Geiger over-stated; lab access is on record; Nov 5).
- [x] `tests/test_pproj6_shared_box.py`: pins the six-metal ranges and the joint count, the 2×1v
      counterexample literals and the 0.15 / 0.30 boxes, the 1×1 vertex rule, and that the HEAD ZPE tool
      reproduces the banked JSON.

- [x] Verification pass on the session-3 material (six refuters, every number re-derived): five citation slips
      in the docs/83 addendum, six in the docs/81 addendum (its heading's "the banked JSON did not" was false —
      99c7431 re-banked it 30 min after the deposit) and the 22-line todo anchor shift corrected by dated lines;
      provenance rows for the zpe edit and the session-3 material amended.

- [x] Second verification pass (all 19 agents, 2026-09-06): b7d5228 had rewritten two provenance rows IN PLACE against
      the record's own :33-34 rule — restored to their 376a3c7 text, amended wording now in dated rows; its docs/83 item 3
      (":253 only for pls-differing rows") was itself wrong and is corrected by a dated line; smaller anchor slips
      (docs/81 :252-253, docs/87 heading and the "cannot differ" quote, docs/76:296-298, the 424/8 tree, Geiger's own
      wording) corrected by dated lines. Numbers untouched throughout.

**Note (session 3, after CI):** a SHA-256 recorded on this Windows working copy is the hash of CRLF bytes; git stores and CI checks out LF. `results/che_box_case_study_2026-09-05/audit.json:4` records `18cb291e…` for `docs/figs/pproj_cell_readout.json`, whose committed bytes hash to `964b271b…`; nothing tests that value, so nothing fails, but a Linux verifier will not reproduce it. `docs/figs/pproj6_shared_box.json` hashes CRLF-normalised bytes for this reason (`sha256_of` key).

### Owed — restored or new

- [ ] **S8 dated line, either way** (:1415-1417, :1550-1551; owed the week of Sep 8, docs/76:296-298).
      Until it exists no session plans materials milestones on S8, and the assessment's §5 panel stays ideation.
- [ ] Countersign or strike the two session-3 addenda (docs/81, docs/83 — blank slots).
- [ ] Elect: re-bank `docs/figs/zpe_decomposition.json` from the HEAD tool, or leave it pinned (docs/81).
- [ ] Optional: move `docs/research-assessment-2026-09-05.md` into the numbered series at the next free
      number when no other session is creating one.
- The readouts owed on drain and the entrant-only list above are unchanged.

## 2026-09-06 — Current-session assessment and next-step review

Scope: review the Claude handoffs, current committed evidence, and local Anvil readouts. Keep concurrent-session files intact; all process execution uses hidden direct executables.

- [x] Reconcile recent session records and repository status, including newer uncommitted evidence.
- [x] Independently check the shared-constants claim and the two small-arm readouts.
- [x] Identify the next scientific decision, deliverable, and experiment; distinguish numerical robustness from predictive accuracy.
- [x] Record the review outcome and verify that concurrent-session artifacts remain intact.

Review outcome (snapshot HEAD 934b584; local readout state inspected 2026-09-06):

- Claude's session-3 review/repair is complete through 934b584. The Anvil session's latest log is still closing its mirror audit and banking; docs/90-small-arms-readout-2026-09-06.md, both small-arm JSONs, and the raw drain outputs are present but untracked. This review does not take ownership of those files.
- Shared box: all six extrema independently re-derived by intersections of the step-switch and box-boundary planes, agreeing within about 2e-16 V. With y = delta_O - 2*delta_OH, Mn FIRES iff y > 0.108359049853 eV and Fe FIRES iff y < 0.029325498658 eV inside this box. Ru/Ir always fire; Ti never does. Thus 2 or 3 of 5 is continuous, including boundary cases. Claude's session log already contains the algebra; this is confirmation, not a new invalid-result finding.
- Small reproducibility improvement still available: src/dft/pproj6_shared_box.py currently gets joint counts from grid samples (the per-metal bounds use LP). Bank/test the analytic disjointness certificate and label grid witnesses as sampled. The present default-box conclusion is valid.
- Raw hp and SCF files confirm atomic U(q333)=6.1777 eV and ortho=7.3008 eV; changes +0.0142/+0.0331 eV both pass the 0.2 eV bar. Split=1.1231 eV. np128 energies differ from the banked values by -1.8e-7/-2.2e-7 Ry, both within 1e-5 Ry. These close numerical checks, not accuracy or self-consistent U: the starting bulk U remains 1e-8 eV.
- The hp pair used approximately 317.4 core-hours against about 55 planned. Use measured cost; neither q444 nor the rejected Cr own-U square is automatically justified by this pass.
- Main priority: S1 core + invocation -> eight control gates -> S2 external evaluation. Seven specification rulings, OC20 asset/variables, P-DIVANIS Ruling 1=BROAD, detector-led ordering, and the decision to run A10 are already settled. Do not re-ask them. The core and scored census remain the entrant's under the current registration.
- Near-term decisions: S8 go/no-go this week; P-DIVANIS Rulings 2-7 before scoring and the September 15 correction-source limb; A10 thresholds/ensemble object/symmetry-arm choices and deposit before jobs (September 18); September 20 claim retest. Ru second-PP follows its remaining choices. Retain the historical ZPE JSON pin unless a separately versioned re-bank has a clear use.
- Before the P-DIVANIS scored count: docs/86 Ruling 4 (lines 103-106 at this snapshot) cannot infer continuous invariance from delta=0,0.05,0.10 alone. Audit all active-step and decision-threshold breakpoints, their endpoints and open intervals, including eta<0.60 V and the 50 meV margin. No scored corpus count was computed in this review.
- Two bounded implementation repairs to assign before reuse: hp_cro2_q333_readout.py's isolation verdict checks energy agreement without requiring clean SCF flags; anvil/46_a0.slurm logs projwfc failure and does not reject zero Lowdin blocks. Actual small-arm raw outputs are clean, so neither finding changes this readout. The case-study audit's CRLF-only hash remains a portability repair.
- S8 scientific limitation: docs/76's reported sole inversion uses Ni's open upper bound; all six determining-site metals are restricted from absolute materials claims; only one of five adjacent gaps exceeds the stated pipeline MAE. The ranking is not evidence for an iridium-beating melt. Mock-judge scores and generic prior-art claims do not establish that every prospective melt experiment lacks value.
- After S1/S2, a narrowly scoped Ir cell/coverage counterpart would challenge the cleanest blind projector result; distinguish a coverage change from a size check at constant coverage. A real accuracy comparison needs externally held-out physical targets and a coherent protocol. MOOH phases/MLIP fine-tuning are currently cut (docs/45 program board); revisiting them is an explicit new research choice. Primary context: https://www.quantum-espresso.org/Doc/user_guide_PDF/Hubbard_input.pdf ; https://www.nature.com/articles/s41467-020-16237-1 .

Verification: three independent focused reviews plus direct source/raw-file checks. No new DFT, cloud submission, scored external census, or code change. Full pytest was not re-run for this assessment. Registered readouts, registration, runs, implementation and concurrent-session files were not edited; git diff --check passed.

### 2026-09-06 — the two small arms LANDED and SCORED (docs/90); banked with outputs, md5 both ends

- hp pair: jobs 20419730 (atomic, 08:25:33) and 20419731 (ortho, 07:26:37) COMPLETED; 10 artefacts
  pulled by explicit list, md5 identical both ends, 0 CR bytes. **PASS / PASS** at the inherited 0.2 eV
  bar: ΔU +0.0142 / +0.0331 eV; split at q333 **+1.1231 eV** beside +1.1042. Four SCFs identical to eight
  decimals across machines. **Cost 317.4 core-h vs ~55 planned (5.8×)** — irreducible q-points are 8
  vs 6, not 27 vs 8; the linear-response work grew 4–5.5× and throughput fell non-uniformly (cause
  INFERRED, not established). Balance after: see `mybalance` at next login.
- gate-(e) pair: array 20419733 COMPLETED in 2:44 + 2:37 at 128 cores; **AGREES / AGREES** under A8.5
  (ΔE −1.8e-7 / −2.2e-7 Ry); pair 0.27021301 vs banked 0.27021297 Ry; `.lowdin.txt` now exist; 11.41
  core-h vs ~10.
- Readout drafted → 4-lens adversarial pass (174 claims, 75 refuted+corrected, 3 rejected) → fixed →
  2 verifiers (6 residual wording issues, all applied) → docs/90. Mirror audit run after the pull:
  `src/dft/mirror_audit.py` run 2026-09-06 over the whole run tree after the pull: 32554 remote / 4606 local files; SAME 4176, ANVIL-ONLY 28135 (all out of git by design), LOCAL-ONLY 187, DIFFER 243; **ANVIL-ONLY pw.x outputs 0, DIFFERING outputs 0**, exit 0. The class lists were saved outside the tree.
- docs/43 dated addendum 2026-09-06 (append-only) carries the readout line, the cost correction of
  :4396-4397 and a countersignature slot. **Countersignature is the entrant's** (docs/90 foot and the
  docs/43 slot).
- Lesson (→ tasks/lessons.md): never price an hp.x q-mesh by the full-mesh count; hp.x iterates the
  irreducible set, and the k+q set size and per-block throughput dominate.
