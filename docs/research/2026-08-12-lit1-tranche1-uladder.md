# LIT-1 tranche 1 — U-robustness of the P7 fixed-geometry U-ladders

*Generated 2026-08-11 by `src/dft/lit1_urobustness.py`. Registered under docs/43-prereg-week1-factorial.md AMENDMENT 5, A5.1 (items a/c/d), tranche 1.*

## Scope, tier context, approximation

- **These fixed-geometry ladder points are NOT tier entries.** `tier_v2` (docs/41 §6f, frozen in `data/tiers/tier_v2.json` under docs/43 §0) is the baseline and is unchanged by anything in this document. `tier_v3` does not exist.
- **Fixed-geometry approximation, stated per A5.1(b)3:** every point is a single-point SCF at the production-U relaxed geometry (docs/41 §5 P7 protocol). Relaxation under the perturbed Hamiltonian is excluded by construction; these are leading-order sensitivities, not relaxed η values.
- Inputs: `runs/probe/Cr/` (4 states × 4 U) and `runs/probe/Co_uladder/` (3 states × 4 U — **Co has no `*OOH` at any U; that hole is registered**, docs/41 §6d/§6e, docs/43 A5.5 firewall). Zero new DFT.
- Conventions reused from the production pipeline: CHE ΔG via `hea_oer.referencing.delta_G` (ZPE−TΔS: OH +0.35, O +0.05, OOH +0.40 eV; `src/hea_oer/referencing.py:17-21`, Man 2011/Valdés 2008); η via `hea_oer.descriptors.oer_overpotential` (G_TOTAL = 4.92 eV, `src/hea_oer/descriptors.py:34`); `g_max()` **imported** from `src/dft/volcano_r1.py` (session-verified against Razzaq–Exner 2023 eqs 10–25); Co bounded-η via `src/dft/eta_bounded.py`. Gas references reused from each metal's source run — exact across the ladder, since no Hubbard channel touches H₂O/H₂ (`src/dft/probe_eta.py:23-27`).
- Löwdin populations (projwfc.x) are **not in this tranche**: no `.save` directories survive, and the regeneration SCFs are part of the A0 budget (A5.1a). The Hubbard-projector occupations Tr[ns] printed by pw.x at U > 0 are recorded as a free supplementary column; they are atomic-projector occupations, not Löwdin charges.

## GATE-1 provenance of the ladder energies (Amendment 4 §2 wording)

| metal | state | base SCF (eV) | production relax (eV) | drift (meV) | status |
|---|---|---|---|---|---|
| Cr | slab | -21118.9145 | -21118.9146 | +0.01 | GATE-1 PASS (≤5 meV round-trip) |
| Cr | s0_OH | -21701.0848 | -21701.0849 | +0.00 | GATE-1 PASS (≤5 meV round-trip) |
| Cr | s0_O | -21683.3519 | -21683.3519 | +0.00 | GATE-1 PASS (≤5 meV round-trip) |
| Cr | s0_OOH | -22265.4947 | -22265.3196 | -175.11 | **production relax failed GATE-1; the base SCF here IS the GATE-1/corrected-basin energy** |
| Co | slab | -31146.1540 | -31146.2133 | +59.39 | **base SCF landed in a HIGHER solution than the production relax** (audit-side trap; production value is the good one) |
| Co | s0_OH | -31728.5322 | -31728.1277 | -404.52 | **production relax failed GATE-1; the base SCF here IS the GATE-1/corrected-basin energy** |
| Co | s0_O | -31710.3473 | -31710.3473 | +0.01 | GATE-1 PASS (≤5 meV round-trip) |

- **Cr `*OOH` (the docs/41 §6f production-basin issue):** the production relaxation carried a metastable magnetic state 175 meV high; the ladder's base SCF reproduces the basin re-relaxation final (`runs/probe/Cr_basin/s0_OOH.out`) to **+3.46 meV**, i.e. it is the GATE-1-passed (tier_v2-corrected) value within the ≤4 meV residual docs/43 P16 licenses.
- **Co `*OH`:** same situation — base SCF vs basin re-relax final (`runs/probe/Co_basin/s0_OH.out`): **+1.99 meV**. GATE-1-passed value.
- **Co `slab`:** the ladder's clean-slab SCF sits in the *higher* of Co's two known slab solutions (+59 meV, docs/41 §6e); the production relaxation holds the lower one. The ladder is internally consistent (same recipe at every U), but every Co ΔG below carries this ~59 meV slab-reference offset at base U relative to `tier_v2` — the descriptor ΔG(*O)−ΔG(*OH) and η bound (pls 2) are immune because the slab energy cancels in ΔG2.
- **Non-production-U points (u0.0/u0.5/u1.35): GATE-1 status PENDING verification.** GATE-1 compares a fresh SCF against a relaxation at the same Hamiltonian; no relaxation exists at the off-production U values, and nothing on disk tests whether each single-seed SCF found the ground SCF solution at its U. The magnetization columns below are the available witness, not a gate.

## Cr ladder — η_TD(U) and G_max(U) (A5.1c)

| U point | U (eV) | ΔG_OH | ΔG_O | ΔG_OOH | x = ΔG_O−ΔG_OH | η_TD (V) | pls | G_max(0.1 V) | G_max(0.2 V) | G_max(0.3 V) |
|---|---|---|---|---|---|---|---|---|---|---|
| u0.0 | 0.00 | 0.988 | 1.749 | 4.432 | 0.761 | **1.452** | 3 | 1.352 (dG3) | 1.252 (dG3) | 1.152 (dG3) |
| u0.5 | 1.85 | 1.270 | 2.404 | 4.538 | 1.133 | **0.904** | 3 | 0.804 (dG3) | 0.704 (dG3) | 0.604 (dG3) |
| base | 3.70 | 1.518 | 3.078 | 4.624 | 1.560 | **0.330** | 2 | 0.634 (dG1..dG3) | 0.334 (dG1..dG3) | 0.046 (dG2+dG3) |
| u1.35 | 5.00 | 1.676 | 3.549 | 4.673 | 1.873 | **0.643** | 2 | 0.889 (dG1+dG2) | 0.689 (dG1+dG2) | 0.489 (dG1+dG2) |

- η(Cr, base U) = **0.3303 V** vs the frozen tier_v2 value 0.3303 V — difference 0.0 mV. The match is exact because Cr's limiting step at base U is ΔG2 (pls 2), built solely from the cleanly round-tripping `s0_O`/`s0_OH`; the `*OOH` energy (3.5 meV above the basin re-relax final, GATE-1 table) does not enter η at base U.
- η(Cr) swing across the ladder: **1.122 V** (docs/41 §6c P7: 1.122 V — same states, same pipeline).
- Cr `*OOH` magnetic state: total magnetization 11/11/11/11 μ_B at u0.0/u0.5/base/u1.35 — every ladder point sits in the 11.0 μ_B solution family (the corrected basin of docs/41 §6f), never the metastable 11.8 μ_B one the production relaxation carried. That is an observed-magnetization statement, not a gate (see GATE-1 note on non-production U).
- `*OOH` O–O distance: **1.36 Å**, computed from the deck geometry — which is the parent (production-U) relaxation by construction, so it is one number for the whole ladder, not a per-U observable. (hydroperoxo *O–OH reference band ~1.37–1.45 Å, superoxo ~1.30–1.32 Å, Inico 2024 via docs/43 A5.3a — full fingerprint classification is LIT-3, not this tranche.)

## Co ladder — bounded η_TD(U) (no `*OOH` at any U)

η for Co uses the bounded identity of `src/dft/eta_bounded.py` (ΔG3+ΔG4 = 4.92 − ΔG_O contains no ΔG_OOH): η = max(ΔG1, ΔG2) − 1.23, valid provided ΔG_OOH lies inside the stated window. G_max values are **lower bounds** over the ΔG_OOH-free spans only.

| U point | U (eV) | ΔG_OH | ΔG_O | x = ΔG_O−ΔG_OH | η bound (V) | pls | valid ΔG_OOH window (eV) | margin vs observed [3.65, 4.94] | G_max LB(0.1) | G_max LB(0.2) | G_max LB(0.3) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| u0.0 | 0.00 | 1.407 | 3.335 | 1.928 | **0.698** | 2 | (2.99, 5.26) | lo +0.66 / hi +0.32 | 0.675 (dG1+dG2) | 0.498 (dG2) | 0.398 (dG2) |
| u0.5 | 1.66 | 1.421 | 3.386 | 1.966 | **0.736** | 2 | (2.95, 5.35) | lo +0.70 / hi +0.41 | 0.726 (dG1+dG2) | 0.535 (dG2) | 0.435 (dG2) |
| base | 3.32 | 1.310 | 3.322 | 2.012 | **0.782** | 2 | (2.91, 5.33) | lo +0.74 / hi +0.39 | 0.682 (dG2) | 0.582 (dG2) | 0.482 (dG2) |
| u1.35 | 4.48 | 2.140 | 4.061 | 1.920 | **0.910** | 1 | (2.78, 6.20) | lo +0.87 / hi +1.26 | 1.401 (dG1+dG2) | 1.200 (dG1+dG2) | 1.000 (dG1+dG2) |

- Co η-bound swing across the ladder: **0.212 V**. All margins in the table are positive, so at every U the validity window contains the tier's whole observed ΔG_OOH range [3.65, 4.94 eV] — the bound is safe *given that range*; a Co ΔG_OOH outside it cannot be excluded by any data on disk (the registered hole).
- **The u1.35 row is not pure U-sensitivity.** Co `s0_OH` total magnetization runs 10.07/9.95/9.94/12.69 μ_B across u0.0/u0.5/base/u1.35: the u1.35 SCF jumped to a different electronic solution (Co's documented multistability, docs/41 §6e), and its ΔG_OH (+0.83 eV vs base) mixes the U response with that solution change. The valence-tracking table below carries the matching flag.
- These bounds inherit the +59 meV slab-solution offset noted above only through ΔG1 (pls 1 rows, i.e. u1.35); ΔG2 is slab-independent.

## Valence tracking (A5.1a)

Criterion, stated (Tripkovic 2018 V(B) step classification): with Δm(U) = m(active site, adsorbate state, U) − m(same site, bare slab, U) (sphere-integrated moments from pw.x), a ΔG is **valence-changing** — its adsorption step changes the active-site oxidation state, hence expected **U-fragile** — when |Δm(production U)| ≥ 0.5 μ_B; otherwise **valence-conserving** (expected U-robust). Rationale: a one-electron redox at a high-spin 3d site moves the sphere moment by ~1 μ_B; half that separates it from covalent/hybridisation transfer and sits well above the ~0.05–0.1 μ_B integration scatter and the 0.1 μ_B channel resolution of docs/43 P16 / Amendment 4 §3. Stability check: if Δm ranges by ≥ 0.5 μ_B *across the four U points*, the tracker itself is unstable (an SCF-solution change on the ladder) and the classification is flagged rather than trusted.

| metal | state | U point | U (eV) | E total mag (μ_B) | abs mag | m(site) | m(site, bare slab) | Δm | Tr[ns] site |
|---|---|---|---|---|---|---|---|---|---|
| Cr | slab | u0.0 | 0.00 | 12.0 | 14.23 | — | — | — | — |
| Cr | s0_OH | u0.0 | 0.00 | 11.0 | 13.66 | 1.5547 | 1.8326 | -0.2779 | — |
| Cr | s0_O | u0.0 | 0.00 | 10.0 | 12.63 | 0.8152 | 1.8326 | -1.0174 | — |
| Cr | s0_OOH | u0.0 | 0.00 | 11.0 | 14.59 | 1.7618 | 1.8326 | -0.0708 | — |
| Cr | slab | u0.5 | 1.85 | 12.0 | 16.88 | — | — | — | — |
| Cr | s0_OH | u0.5 | 1.85 | 11.0 | 16.65 | 1.739 | 1.9773 | -0.2383 | 4.77774 |
| Cr | s0_O | u0.5 | 1.85 | 10.0 | 15.55 | 0.9105 | 1.9773 | -1.0668 | 4.97332 |
| Cr | s0_OOH | u0.5 | 1.85 | 11.0 | 17.44 | 1.9373 | 1.9773 | -0.04 | 4.76982 |
| Cr | slab | base | 3.70 | 12.0 | 19.38 | — | — | — | — |
| Cr | s0_OH | base | 3.70 | 11.0 | 19.45 | 1.9231 | 2.1177 | -0.1946 | 4.74479 |
| Cr | s0_O | base | 3.70 | 10.0 | 18.44 | 1.0568 | 2.1177 | -1.0609 | 4.94877 |
| Cr | s0_OOH | base | 3.70 | 11.0 | 20.09 | 2.0959 | 2.1177 | -0.0218 | 4.73705 |
| Cr | slab | u1.35 | 5.00 | 12.0 | 20.99 | — | — | — | — |
| Cr | s0_OH | u1.35 | 5.00 | 11.0 | 21.28 | 2.0511 | 2.2058 | -0.1547 | 4.72675 |
| Cr | s0_O | u1.35 | 5.00 | 10.0 | 20.43 | 1.2091 | 2.2058 | -0.9967 | 4.92707 |
| Cr | s0_OOH | u1.35 | 5.00 | 11.0 | 21.77 | 2.1929 | 2.2058 | -0.0129 | 4.71426 |
| Co | slab | u0.0 | 0.00 | 9.96 | 10.31 | — | — | — | — |
| Co | s0_OH | u0.0 | 0.00 | 10.07 | 10.41 | 0.8684 | 1.2755 | -0.4071 | — |
| Co | s0_O | u0.0 | 0.00 | 11.11 | 11.45 | 1.019 | 1.2755 | -0.2565 | — |
| Co | slab | u0.5 | 1.66 | 10.39 | 10.91 | — | — | — | — |
| Co | s0_OH | u0.5 | 1.66 | 9.95 | 10.42 | 0.7997 | 1.5995 | -0.7998 | 7.66661 |
| Co | s0_O | u0.5 | 1.66 | 11.19 | 11.67 | 1.0434 | 1.5995 | -0.5561 | 7.68192 |
| Co | slab | base | 3.32 | 11.51 | 12.89 | — | — | — | — |
| Co | s0_OH | base | 3.32 | 9.94 | 10.63 | 0.8027 | 1.7565 | -0.9538 | 7.67349 |
| Co | s0_O | base | 3.32 | 11.24 | 12.03 | 1.1295 | 1.7565 | -0.627 | 7.69358 |
| Co | slab | u1.35 | 4.48 | 12.68 | 14.89 | — | — | — | — |
| Co | s0_OH | u1.35 | 4.48 | 12.69 | 14.72 | 1.8374 | 1.9398 | -0.1024 | 7.52398 |
| Co | s0_O | u1.35 | 4.48 | 13.85 | 15.6 | 1.2217 | 1.9398 | -0.7181 | 7.69595 |

### Classification per ΔG

| metal | ΔG | Δm at production U (μ_B) | class (expected) | ΔG swing across ladder (eV) | Δm range across U (μ_B) | tracker stable? |
|---|---|---|---|---|---|---|
| Cr | dG_OH | -0.1946 | **valence-conserving** (U-robust) | 0.6884 | 0.1232 | yes |
| Cr | dG_O | -1.0609 | **valence-changing** (U-fragile) | 1.7998 | 0.0701 | yes |
| Cr | dG_OOH | -0.0218 | **valence-conserving** (U-robust) | 0.2418 | 0.0579 | yes |
| Co | dG_OH | -0.9538 | **valence-changing** (U-fragile) | 0.8303 | 0.8514 | **NO — SCF-solution change on the ladder (docs/41 §6e); classification flagged** |
| Co | dG_O | -0.627 | **valence-changing** (U-fragile) | 0.7381 | 0.4616 | yes |

### A5.1a mechanism-test readout (registered: either outcome is reported)

The registered expectation was that the 1.122 V η(Cr) swing should correlate with a Cr oxidation-state change under *O/*OOH, with U-flat quantities showing none. At this 4-point fixed-geometry resolution the pattern is observed: the per-ΔG U-swings rank exactly with the step's |Δm| — ΔG_O (Δm -1.06 μ_B, valence-changing) swings 1.80 eV, ΔG_OH (Δm -0.19) swings 0.69 eV, ΔG_OOH (Δm -0.02) swings 0.24 eV. The one valence-changing step (*O: the site is oxidised by ~1 μ_B-equivalent relative to the bare slab at every U) is the U-fragile axis, and it sits in the descriptor ΔG_O−ΔG_OH — which is what P7 measured as the η(Cr) swing. Δm itself is U-flat for every Cr state (range ≤ 0.12 μ_B), so the swing is the smooth U-response of a valence-changing step, not a basin/valence step *along* the U axis. Caveat: four points cannot exclude a step between them; the dense A0 grid is the real test. Co's classification is degraded by the tracker instability flagged above and its `*OOH` hole; it supports no mechanism claim either way.

## Intercept-vs-descriptor U-test (A5.1d)

Motivating prior, updated after the 2026-08-12 Xu read (sweep memo §10): the on-rutile prior is **Xu, Rossmeisl & Kitchin 2015** (10.1021/jp511426q) — U = 0–8 eV scans on undoped rutile MO₂(110), including CrO₂, found scaling relations preserved and compounds moving *along* the volcano, so this test is a replication-and-extension of their result on a **doped** rutile under our protocol. Tripkovic 2018 Table 3 is the counterpoint on perovskites: LaCrO₃ ΔE(*OOH)−ΔE(*OH) moves 2.94→2.93 eV over U = 0–5 eV (flat) while ΔE(*O)−ΔE(*OH) moves +1.06 eV.

| U point | U (eV) | Cr intercept ΔG_OOH−ΔG_OH (eV) | Cr descriptor ΔG_O−ΔG_OH (eV) |
|---|---|---|---|
| u0.0 | 0.00 | 3.444 | 0.761 |
| u0.5 | 1.85 | 3.268 | 1.133 |
| base | 3.70 | 3.106 | 1.560 |
| u1.35 | 5.00 | 2.997 | 1.873 |

- Cr intercept span across the ladder: **0.447 eV**; Cr descriptor span: **1.111 eV**. Ratio 0.40.
- Readout: the descriptor axis is confirmed U-fragile (1.11 eV), and the intercept is ~2.5× more U-robust — but at 0.447 eV over the ladder it is **not** Tripkovic-flat (LaCrO₃: 0.01 eV over U = 0–5). Cr(110) is therefore *partially* a move-along-the-volcano case: U dominantly slides Cr along the descriptor axis while also drifting the scaling intercept through the 3.2 eV band (3.44 → 3.00 eV, crossing 3.2 between u0.5 and base). Consistent with this, both intercept-forming states (*OH, *OOH) are valence-conserving while the descriptor contains the one valence-changing state (*O). The 0.447 eV intercept drift is itself a measured deviation from Xu 2015's clean scaling preservation on the undoped rutiles — a doped-Cr-specific effect at this resolution, to be confirmed or bounded on the dense A0 grid.
- Co descriptor span: **0.092 eV**. Co intercept: not computable: no Co *OOH at any U (registered hole).

## What A0 adds

Everything above rests on four U points per metal — 0, 0.5×, 1×, 1.35× of the MP-fitted production U — inherited from the P7 probe. The registered A0 grid (docs/43 §4, block 6A: ~140 fixed-geometry SCFs spanning U = 0–9 eV, pw.x only, independent of the hp.x gate) extends each of these 4-point ladders to a dense grid over the full physically defensible U range. That buys: (i) η_TD(U) and G_max(U) as *curves*, so the volcano-apex crossing that produced the withdrawn Cr headline is located rather than bracketed; (ii) valence tracking with enough resolution to see *where* the active-site moment steps, not just that it differs between endpoints; (iii) the intercept test on a dense axis, directly comparable to Tripkovic's 0–5 eV span; and (iv) the U-band leg of the A5.1(b) ranking-claim rule ({U = 0, MP U, hp.x U if 1B returns GO}) evaluated from measured curves instead of interpolation. Per A5.1a, Löwdin populations from projwfc.x ride along wherever A0 regenerates charge densities (≤ ~150 cheap SCFs), upgrading the moment-based valence tracker with a charge-based one. The fixed-geometry approximation is unchanged in A0 and is stated wherever the grid is used.

---

## Correction of record — 2026-08-16

**What is corrected.** Two sentences above call the LIT-1 Cr system a "**doped** rutile"
(the motivating-prior paragraph: "a replication-and-extension of their result on a
**doped** rutile under our protocol") and attribute the 0.447 eV intercept drift to
"a doped-Cr-specific effect at this resolution."

**The correction.** The system is not doped. `src/dft/gen_rutile.py` line 65 builds
**stoichiometric rutile CrO₂** at the experimental lattice (a = 4.421 Å, c = 2.916 Å,
u = 0.3023) and tags it `# real rutile (FM half-metal)` — the same undoped CrO₂(110)
that appears in Xu, Rossmeisl & Kitchin 2015's own ten-metal set. There is no dopant
anywhere in the tier; the model-rutile tags in that file (Fe/Co/Ni/Cu) mark hypothetical
*phases*, not doping. Verified against `src/dft/gen_rutile.py` and the deck headers in
`runs/Cr_slab/` on 2026-08-16.

**What survives and what does not.** The measured numbers in this memo are untouched —
the ladder, the 0.447 eV intercept span, the 1.111 eV descriptor span, and the
valence-conserving/valence-changing split all stand. What falls is the *interpretive*
clause: the intercept drift cannot be "doped-Cr-specific" because nothing is doped. The
correct statement is that our fixed-geometry, SSSP 80/640, 2-D-ladder protocol measures
a 0.447 eV intercept drift on the same undoped CrO₂ where Xu's full-relaxation,
GBRV 40/500, frozen-`tot_magnetization` protocol reported clean scaling preservation —
i.e. the discrepancy is a **protocol-difference or U-response finding on the identical
material**, which is *more* interesting for this project's thesis, not less. To be
confirmed or bounded on the dense A0 grid, as already registered.

**Why the error matters enough to date.** "Doped" would have handed the report a false
escape hatch ("Xu's preserved scaling doesn't apply — ours is doped"). The lit-sweep
round-2 synthesis (2026-08-15-lit-sweep-round2-synthesis.md) flagged the contradiction;
the repo read above confirmed which side is wrong. Nothing before this line was edited.
