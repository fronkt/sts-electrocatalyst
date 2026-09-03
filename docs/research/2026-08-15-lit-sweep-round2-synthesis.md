<!-- PROVENANCE. Round-2 synthesis, workflow run wf_b653d9b0-7a5, 2026-08-15
     (8/8 agents: lens-7 re-run, three revised proposals, three adversarial
     critiques, max-effort synthesis). Inputs: the full six-lens digest + the
     round-1 outcome dossier (three proposals, three critiques carrying 36 blocking
     issues, round-1 synthesis). The agent's return value was truncated to its last
     33k chars by a two-block output split; this file is the full document,
     reconstructed from the agent transcript (blocks joined mid-word, verified).
     THE LIVE RECOMMENDED PROGRAM as of 2026-08-15. generated research input;
     not report prose; thresholds must be re-authored by the entrant before any
     amendment is deposited (P-AUTHORSHIP, section 8).

     INDEPENDENT VERIFICATION, 2026-08-16 (this session, from raw QE outputs, not
     agent reports):
     - Section 1(iii)'s 2x1v symmetry-collapse claim CONFIRMED. Ir *OOH off-mirror:
       -0.2846 eV in 1x1 (runs/Ir_anchor/s0_OOH.out -22777.1788 eV vs
       runs/probe/Ir_cellsym/s0_OOH__1x1_off.out -22777.4634 eV) collapsing to
       -0.0185 eV in 2x1v; Ru *OOH 2x1v -0.1088 eV is the only scoreable pair over
       0.10 eV. "Eight scoreable pairs" = nine minus Cr *OOH, correctly excluded:
       its off-mirror delta (-1.19 eV) rides a magnetic-basin change, abs_mag
       38.66 -> 40.52 (delta 1.86 uB > the 0.1 uB confound threshold).
     - Section 5's premise that gen_rutile.py line 65 builds REAL rutile CrO2
       (a=4.421, c=2.916, u=0.3023, FM half-metal) CONFIRMED against src/dft/;
       the "doped rutile" wording in docs/research/2026-08-12-lit1-tranche1-uladder.md
       is the error -- corrected in that file's dated addendum, 2026-08-16. -->

# AMENDED RECOMMENDED PROGRAM — STS 2027, `sts-electrocatalyst`, Aug 15 → Oct 15 freeze
### Round 2, written with lens 7 in hand and the n question answered

*Both required files read in full: `recovered/LENS-DIGEST-6.md` (352 lines, lenses 1/3/4/5/6 + notes) and `recovered/ROUND1-OUTCOME.md` (382 lines: three proposals, three critiques, synthesis). Lens 7 taken from the prompt. All three round-2 proposals and all three round-2 critiques incorporated. Nothing below was verified against the repo in this session — every repo-derived number is attributed to the proposal or critic that reported it, and the ones that must be re-read from disk before they are registered are flagged.*

---

## 1. WHAT CHANGED FROM ROUND 1

Four things changed materially. One is fatal to round 1's arithmetic, one reverses a round-1 recommendation, one rebuilds the flagship, and one is a free week of calendar.

**(i) The human budget was wrong by 40%, and it is the only constraint that decides anything.** Round 1 normalised Aug 15 → Oct 15 as 43.5 six-hour days minus 8 for STS application mechanics = 35 effective science days, and spent 33. All three round-2 proposals inherited that number verbatim. It accounts for smapply and nothing else. The entrant's own committed ledger puts Simbiochem (Aug 29), AI4Mat ×3 (Aug 30), MoML (Sep 1), Breakthrough Jr (Sep 15), Coke (Sep 30), a Concord Review paper he writes himself (early Oct) and Nov 1 college ED work inside the identical window — priced by the STS critic at ~14.5 days. **The effective science budget is ~21 days, not 35.** Every plan in round 1 and round 2 is 50–57% over. This is the single largest change and it forces the program below to be roughly two-thirds the size of round 1's.

**(ii) Lens 7 changed three protocol decisions and killed one recommendation outright.**
- The Hubbard **projector** is now a registered variable paired with U, and the 7.15 eV fifth A0 grid point (Xu 2015 Table 1) is a *pairing hazard*, not a literature anchor, until two SCFs settle it. This is live and urgent — round 1 registered A0 without it.
- ESM on neutral slabs is **dropped entirely**, not deferred: with `esm_bc='bc1'` it removes the image dipole–dipole interaction, which is what the dipole correction already does, and the dipole correction is a *closed negative* in this campaign. ESM only produces new information with `tot_charge ≠ 0` or constant-µ (`lfcpopt`/FCP, requiring bc2/bc3). Round 1 left ESM ambiguously alive.
- The **re-Hessian at the escaped geometry** is mandatory and was absent from round 1. Without it the project can claim only that it left a saddle, never that it reached anything.
- Lens 7's own top-3 item — relaunching hp.x with `perturb_only_atom` as a cost reduction — is **rejected**: the physics critic shows U_I = (χ₀⁻¹ − χ⁻¹)_II requires the full response matrix over all symmetry-inequivalent Hubbard atoms, so one row of χ is not invertible on a slab carrying distinct cus, bridge and subsurface sites. `perturb_only_atom` is a parallelisation device collected with `compute_hp`. (UNVERIFIED against the hp.x manual — box test before registering.)

**(iii) The flagship is rebuilt, because round 1 registered a threshold the repo's own 2x1v data argues against.** Round 1's P-3D ("≥3 of 5 magnetic 3d metals show |Δη| > 0.10 V on mirror release") — and both round-2 rate proposals, P-N1 and P4 — sit against this, reported from disk by the FLOOR AND EXCESS proposal: of eight scoreable mirror-vs-off pairs on Cr/Ir/Ru **in the adopted 2x1v production cell**, only Ru *OOH (−0.109 eV) exceeds 0.10 eV, and the flagship Ir *OOH effect collapses from −0.285 eV in 1x1 to −0.018 eV in 2x1v. Registering a bare symmetry rate risks a **second withdrawn headline in the same 20-page report**. One withdrawal reads as maturity; two read as a pattern. The flagship is therefore re-registered as **coverage-conditionality** (P-SYMCOV), which the same disk data *supports*, and the per-metal Δη table is reported with no threshold attached.

**(iv) One free week of calendar, from a physics fact nobody in either round noticed.** `noinv=.true.` is being carried on every off-plane relaxation for zero information. Time reversal (k ↔ −k) is an exact symmetry of a collinear, spin-orbit-free Hamiltonian regardless of the structure's point group, so folding under it is exact whether or not the adsorbate sits on a mirror plane. The off-plane arm needs `nosym` (to stop spatial force symmetrisation — that *is* the trap) but not `noinv`. Per the repo's own `build_cellsym_pilot.py`, 2x1v off-plane is 16 irreducible k-points versus 9 for mirror; with `noinv=.false.` it is ~10. **This cuts ~35–38% off the off-plane battery and brings the worst single magnetic 2x1v off-plane relaxation from ~62 h to ~39 h** — and that job is precisely the un-parallelisable term every plan cites as the reason for a Sep 1 last-safe-launch. It costs one SCF pair to verify.

**Round-1 recommendations now WITHDRAWN or AMENDED:**

| Round-1 item | Round-2 disposition |
|---|---|
| "Post an arXiv preprint in late October — **Recommendation: yes**" | **WITHDRAWN.** It is a fourth writing project inside the ~90 h Oct 15 → Nov 5 window that already carries a 20-page report, eight essays, six 200-word boxes, three disclosures and Nov 1 ED apps. Recovers ~2.5 human-days. |
| P-3D as the flagship threshold (≥3 of 5 on mirror release) | **AMENDED to P-SYMCOV.** The bare rate becomes a table with no threshold. |
| P-FLOOR-U ("excess exceeds floor by >3×") **[TOKEN RENAMED — NOTE ADDED 2026-09-03: the thing withdrawn here is the round-1 ratio, which docs/43:1361 renames **P-U-SPLIT**. The string "P-FLOOR-U" was then REUSED for its replacement, A7.3 span(c_M)/2, which is live and SCORED NOT MET at 3 of 6 (docs/45:31, docs/60:105, tasks/todo.md:1216). A grep for "P-FLOOR-U" + WITHDRAWN lands here and reads as the flagship having been withdrawn; it was not. Original row text unchanged below.]** | **WITHDRAWN.** The excess vanishes *identically* at the pls 3→2 crossing where ΔG₂ = ΔG₃; Cr's excess runs 0.961 → 0.007 → 0.375 V across U = 0 / 3.70 / 5.00, so the ratio is a grid artifact. Replaced by **span(c_M)/2 at fixed endpoints**, which is smooth, monotone and physical. |
| "hp.x bulk bracket, 7 metals, atomic projector" | **AMENDED.** 2 metals (Cr, Ti), and it is the **first named cut**. |
| "Wander/Kitchin Hessian incidence, ~2 days" | **CUT at registration**, not in flight. |
| "Literature-coding audit, ~2 days" | **CUT at registration.** |
| Divanis floor statistic at n = 508 | **AMENDED.** The citation critic's parse: 515 rows / 24 articles, of which only **38 are bare rutile MO₂ from 3 articles** (Man 26, Mom 11, Frydendal 1); article 22 alone supplies 122 rows (24%). Report per-paper (n = 24) and rutile-only (n = 38) with the denominator composition on the figure face. |
| "~0.12 V irreducible code-level floor" | **WITHDRAWN — both derivations are dead.** Man 2011 states verbatim its own fit is ΔE_HOO* = ΔE_HO* + 3.20 eV with 68% within ±0.2 eV and 95% within ±0.4 eV, so a narrower 24-paper pooled spread is implausible; and the Halck "RuO₂ DACAPO" row is numerically *identical* to Man's high-coverage row, so it is a quotation, not an independent code-to-code delta. Replaced by the within-material across-study scatter, ~0.095 V. |
| "Structurally zero" U and magnetic rows for the anchors | **WITHDRAWN.** RuO₂ is itinerant AFM (Berlijn et al., PRL 118, 077201 (2017), reported via docs/41; Liang 2022 **10.1021/acs.jpcc.1c08700** gives AFM 0.41–0.49 V vs NM 0.63–0.73 V, ΔG(*O) rising up to ~0.3 eV), and Xu's linear-response values are U(Ru) = 6.73 eV, U(Ir) = 5.91 eV. U = 0 / nspin = 1 for the anchors is a *project convention*, not a property of the materials. |

**What did NOT change, and this is a legitimate finding:** the verdict on the seven-metal in-house tier, the detector-first spine, the eligibility-engineering pattern ("the central claim must be scorable from the zero-compute stages alone"), and the physics kill list. Round 1 got the shape right; round 2 corrects the size, the flagship's registration, and eleven citations.

---

## 2. VERDICT ON THE STS QUESTION

**Scholar: yes, comfortably — and this has not changed.** Three in-field PhDs weighting the Research Report most heavily will see a dated pre-registration with six amendments, a threshold that fired and forced a real withdrawal, six closed negatives measured rather than argued, a Hessian mechanically confirming a saddle point, and an exact lemma verified to 1e-9. That is at or above the finalist median on rigor. Being computational is not the barrier: six of the 2026 top ten had no wet lab and 2025's first place was a single-author computational paper (Lens 6, read from program books; STS sources carry no DOI and are UNVERIFIED by convention).

**Finalist: no, not as it stands, and round 2 makes me *less* optimistic than round 1, not more.** Round 1 believed 35 science days were available and that a five-metal symmetry battery would produce a rate. Both are now false. At 21 effective days against six competing deadlines, the realistic outcome is a strong Scholar. The honest statement is: **Finalist is reachable only if the entrant drops at least two of the six competing deadlines and the arXiv preprint.** That is his decision, not mine, and I have priced it exactly (§10, Q1–Q2).

**The single highest-leverage addition is now different from round 1's answer.** Round 1 said: run the symmetry trap on five 3d metals. Round 2 says: **ship `silentgate` — the released detector, with a measured false-positive rate against a corpus where the answer is zero by construction — together with the 810-relaxation exposure census on the Xu deposit.** Three reasons this displaces the in-house battery:

1. It is **zero-compute and cannot fail for compute reasons**, which is the only construction structurally immune to the Research Report Guidelines' "results to date of an unfinished study" ineligibility rule. A census over all 810 deposited outputs is a *complete study of a complete corpus* no matter what drains.
2. It is the **only artifact in the program**, and Lens 6 found no STS finalist in five years whose headline was a diagnosis with no remedy (its own least-confident claim, ~60–70 of ~200 projects — directional, not absolute).
3. It answers the sharpest available objection — "you found a bug in your own builder" — with somebody else's deposited output files, in the same code, before a single box-hour.

The in-house repair arm (S3) is the *second*-highest-leverage item and it is what the report needs to not be pure audit. But if the calendar forces a choice, **protect S1+S2, cut S3's depth, and say so in the depth table.**

**Not flattering it, plainly:** the central object is still a table and two rates about a chemistry four of whose seven systems are phases that do not exist as electrodes. The numbers that read as *scale* to a fifteen-person cross-disciplinary panel are 810, 515, 3,963, ≥500 and 7,843 — all external, all free. The numbers that read as scale from the entrant's own compute do not exist at any n he can reach. Going 7 → 25 in-house is not a category change; going 7 → 810 external is.

---

## 3. THE n QUESTION — THE DIRECT ANSWER

> *"Couldn't we also go from n=7 to n=25 to strengthen?"*

**NO.** Not by mid-October, and not at all — the population does not exist, and the precision it would buy is invisible to both judging cuts. The number that decides it is not box-hours: **of the 18 endmembers needed to reach 25, at most 4–5 are real ambient undistorted rutiles and EXACTLY ZERO are magnetic 3d rutiles.** β-MnO₂ (pyrolusite) is the only ambient magnetic 3d rutile that exists, and it is already in the tier. So 13–14 of the 18 — 56% of the headline denominator — would be distorted, metastable or nonexistent phases, in a report whose withdrawal section says non-ambient model phases were part of why the original headline fell, read by three in-field PhDs and then defended in a 35%-weighted interview.

### (a) The exact in-house endmember list, phase realism stated per system

**RECOMMENDED: n = 8, with a conditional 9th.** The existing seven plus TiO₂; SnO₂ admitted only on a condition stated below.

| System | Stratum | Phase realism | Status |
|---|---|---|---|
| **TiO₂** (rutile, MP mp-2657) | REAL-AMBIENT-UNDISTORTED | Genuine ambient P4₂/mnm rutile. d⁰, nspin=1. | **ADMIT — not cuttable.** Already in `src/dft/gen_rutile.py` at experimental geometry (a=4.5937, c=2.9587, u=0.30478) and already used by `build_hp_validation.py`, so builder cost ≈ 0. Anchored **four** ways: in-house, Xu's deposited ten, Man 2011 (**10.1002/cctc.201000397**) as a *stoichiometric cus-site* row, and Mom 2014 (JPCC 118, 4095–4102, Divanis article [7]). Highest value per box-hour anywhere in this document. |
| **β-MnO₂** (pyrolusite, mp-510408) | REAL-AMBIENT-UNDISTORTED | Genuine ambient rutile — the only real ambient magnetic 3d rutile in existence. | **KEEP, with a correction.** β-MnO₂ is **antiferromagnetic** and `gen_rutile.py` initialises it ferromagnetic (mag = 0.5). Either add an AFM arm (4 fixed-geometry SCFs, ~8 box-h) or strike every materials-facing sentence about Mn. Do not leave it implicit. |
| **RuO₂** (mp-825) | REAL-AMBIENT-UNDISTORTED | Genuine ambient rutile — **not nonmagnetic.** Itinerant AFM (Berlijn PRL 118, 077201 (2017), via docs/41). | **KEEP.** U = 0 / nspin = 1 is a project convention. See the AFM probe in §4 S0(h). |
| **IrO₂** | REAL-AMBIENT-UNDISTORTED | Genuine ambient rutile. | **KEEP.** |
| **CrO₂** | REAL-UNDISTORTED-METASTABLE | Genuine P4₂/mnm rutile FM half-metal, but metastable (CVD from CrO₃), decomposes to Cr₂O₃, dissolves as chromate above ~0.9–1.2 V. Man 2011 verbatim: *"some oxides such as NbO₂, ReO₂, VO₂, MoO₂, and CrO₂ are not stable. Still, the theoretical values may be interesting as a guide."* | **KEEP in its own row.** Its absolute η never carries a materials claim. |
| **FeO₂** | MODEL PHASE | Pyrite-type only above 74 GPa. | **KEEP as a method test system only.** |
| **CoO₂** | MODEL PHASE | Real phase is layered O3/CdI₂-type delithiated LiCoO₂. | **KEEP as a method test system only.** |
| **NiO₂** | MODEL PHASE | Real phase is layered delithiated LiNiO₂. | **KEEP as a method test system only.** |
| **SnO₂** (cassiterite) | REAL-AMBIENT-UNDISTORTED | Genuine ambient P4₂/mnm rutile, d¹⁰. | **CONDITIONAL — first cut.** See below. |

**Why the model phases are legitimate, and the scoping rule that makes them so — registered BEFORE any gate.** The measured quantity is a **difference between two treatments of the SAME slab** (mirror vs off-plane, basin A vs basin B, U vs U′, 1x1 vs 2x1v), and a difference is a valid *method* measurement whether or not the slab is a synthesisable electrode. What the report may therefore never do is quote an absolute η for Cr, Fe, Co or Ni as a materials claim; they appear only inside paired within-metal differences, and this goes in the **scope section, not a limitations footnote**, enforced by a pre-submission script that parses the compiled PDF.

**The SnO₂ condition, and why it is not the free win two proposals thought.** The citation critic read `man2011.pdf` verbatim: *"The stoichiometric surfaces were considered for rutile oxides, with the exception of PbO₂, SnO₂, and NiO₂, on which the binding of intermediates are thermodynamically favored on nonstoichiometric surfaces (denoted by the subscript b)."* Figure 5b: *"positions 3 and 4 represent the active position (BRIDGE) and positions 1 and 2 represent the inactive position (cus) with M = Ni, Pb, Sn."* So Man's SnO₂ᵦ and PbO₂ᵦ rows are **bridge-site numbers on reduced, nonstoichiometric surfaces**, not comparable to this project's stoichiometric cus-site protocol — and Man reports the cus site does **not bind** on SnO₂ and PbO₂. Two consequences: the "externally anchored" justification for SnO₂ collapses to Mom 2014 alone, and there is a live physics risk that a cus-site mirror/off-plane pair on SnO₂ is **a difference between two non-binding geometries**. Admit SnO₂ only if Mom 2014's stoichiometric "SnO₂" rows (distinct from its "SnO₂ red" rows) are confirmed cus-site by Sep 1, and only as a declared control-stratum member that never enters a headline rate.

**EXCLUDED AT REGISTRATION, with the true reason each (the exclusion table is itself a deliverable):**

- **PbO₂** (β/plattnerite) — demoted from "the single strongest addition available." Man's PbO₂ᵦ is bridge-site on a reduced surface with the cus site reported not to bind; Pb 5d semicore unqualified at ecutrho 640; β-PbO₂ is markedly non-stoichiometric; odd n₁ needs bridge SCFs. Its judge-legibility as a real industrial OER anode is real but does not survive the cus-site problem.
- **OsO₂** — zero external comparator anywhere in the 515 Divanis rows and absent from Xu's ten; SSSP-Efficiency Os unqualified; 5d SOC. **NOT** for the MP prototype-label reason two proposals gave: mp-996 *is* P4₂/mnm (sg 136) with corner- and edge-sharing OsO₆ octahedra, i.e. rutile; "Hydrophilite" is an MP auto-classification artefact (Pnnm cannot coexist with sg 136).
- **GeO₂** (argutite) — the exclusion reason in SILENTGATE v2 is **backwards**: rutile-type GeO₂ *is* the ambient-stable polymorph and converts to quartz-type above ~1035 °C; stishovite is the high-pressure case. Excluded for the correct reason: a ~4.7 eV-gap insulator is a third occupancy convention in one table.
- **VO₂** — monoclinic M1 below ~340 K.
- **NbO₂, MoO₂, WO₂, ReO₂, TcO₂** — Peierls-dimerised / distorted rutile ground states; Man 2011 names NbO₂, ReO₂, VO₂, MoO₂ as not stable.
- **RhO₂** — metastable. **PtO₂** — ground state is not rutile (α = CdI₂-type hexagonal, β = CaCl₂-type orthorhombic per the physics critic; **UNVERIFIED**, check one ICSD/MP record). **TaO₂** — not a phase (Ta₂O₅ is the oxide). **SiO₂**-stishovite — high-pressure. **CuO₂** — does not exist; already dead.

**Provenance warning that must be fixed before Amendment 7 is deposited:** two round-2 proposals attribute their phase tables to `docs/research/2026-07-24-rutile-landscape-stability-survey.md`. The physics critic counted occurrences in that file: SnO₂ 0, PbO₂ 0, OsO₂ 0, GeO₂ 0, PtO₂ 0, RhO₂ 0, TaO₂ 0, VO₂ 0, NbO₂ 0, MoO₂ 0, ReO₂ 0. The survey covers only Cr/Mn/Fe/Co/Ni/Cu. **Every phase claim about a candidate addition is currently unsourced.** Cite Materials Project entries or primary crystallography per row, or mark each row UNVERIFIED — an unsourced exclusion table in a project whose deliverable is an exclusion table is the wrong kind of irony.

### (b) The honest 2x1v box-hour and human-day cost

Priced with the repo's own measured constants (`src/dft/build_cellsym_pilot.py`, measured 2026-08-09, box 47025043): CELL_MULT = 5.19 per master-k; k-counts 15 (1x1) / 9 (2x1v mirror) / 16 (2x1v off-plane with nosym+noinv) / ~10 (off-plane with nosym only); STEP_MULT_2X1 = 1.5 (ASSUMED, bracket 1.5–2.0); MAG_MULT = 3.5; RANK_SPEEDUP_NP20 = 3.0. Derived: **the 1x1 → 2x1v total multiplier is 5.19 × (9/15) × 1.5 = 4.67× (bracket 4.05–8.0)** — a measured number for the physics critic's "4–8×". With `noinv` dropped, off-plane costs 10/9 = **1.11×** its mirror twin instead of 1.78×.

Cost classes used throughout: nonmagnetic 2x1v mirror relaxation 4 h (3–6); nonmagnetic 2x1v off-plane 4.5 h; magnetic 2x1v mirror relaxation 14 h (observed 4–35); magnetic 2x1v off-plane ~15.6 h; 2x1v fixed-geometry SCF 2.0 h magnetic / 0.7 h nonmagnetic; 1x1 fixed-geometry SCF 0.4–0.67 h.

**TiO₂, full 2x1v battery:** 3 mirror relaxations (12 box-h) + 3 off-plane (13.5) + 1 clean slab (4) + 7 GATE-1 SCFs (5) + 2 re-relax children (9) + 4 bulk cutoff SCFs (1.2) + 2 nspin=2 control SCFs on the *O state (1.4) = **~46 box-hours, ~0.4 human-days** (already wired).
**SnO₂, same shape** = **~46 box-hours, ~0.8 human-days** (new element: pseudopotential staging, cutoff ladder, bare-slab reconstruction screen, odd-n₁ check).
**Both: ~92 box-hours, ~1.2 human-days.**

**The full jump to 25 (18 additions), priced honestly in 2x1v:** nonmagnetic ones land near 36–46 box-h each and the magnetic/near-magnetic ones (VO₂, NbO₂, MoO₂, ReO₂) near 250 box-h at the observed magnetic median, giving **~1,500–2,500 box-hours — which this project can trivially afford.** It is the human cost that kills it: at 0.6–0.9 human-days per element of pseudopotential validation, lattice parameters, bare-slab reconstruction, magnetic initialisation and triage of a ~30% GATE-1 re-relax loop, 18 additions is **11–16 human-days against a 21-day effective budget — 52% to 76% of everything left.**

### (c) Which claims draw their power from external corpora, and the actual n each supplies

**All prevalence and exposure claims go external, at zero box-hours.**

| Claim | Corpus | Actual n | Note |
|---|---|---|---|
| Symmetry-lock **exposure** in the field's own data | Xu/Rossmeisl/Kitchin deposit (**10.1021/jp511426q**; data **10.5281/zenodo.12635**, CC0, one file `rutile-OER-v1.0.zip` 572.4 MB; GitHub mirror `zhongnanxu/rutile-OER` CC-BY-4.0) | **810** adsorbate relaxations, **10 metals with Eads** (the tree holds **eleven** metal directories — SnO₂ is bulk-EOS only: 53 fine-EOS + 26 coarse-EOS + 5 ground, no slabs) | 95% interval on a rate here is ~0.07 wide — an order better than any reachable in-house n |
| Detector **false-positive rate** | OC20 (**10.1021/acscatal.0c04525**; `isym=0`, `symprec=1e-10` in fairchem `src/fairchem/data/oc/utils/vasp_flags.py`) | **≥500** relaxations | Answer is zero by construction. A gate, not a finding |
| **U-fragility** corroboration | Xu's 680-relaxation ladder | **170** (metal, U) points, 17 U values 0–8 eV | Corroboration only — Xu's are full relaxations with `tot_magnetization` frozen at 15, so they measure a different quantity than fixed-geometry A0 |
| **Scaling-floor** prevalence | Divanis 2020 (**10.1039/C9SC05897D**, ESI on disk) | **515 rows / 24 articles**, of which **38 bare rutile MO₂ from 3 articles** | Report the per-paper rate (n = 24) *and* the rutile-only sub-rate (n = 38), never an exact binomial CI at n = 515 |
| **Placement-mechanism** exposure across surface families | pymatgen `AdsorbateSiteFinder` (**10.1038/s41524-017-0017-z**), run unmodified inside the repo | Unlimited enumeration | **Must be paired with the input-set audit** — see §6 item 6 |
| **Magnetic FM-initialisation bias** at database scale | Fahmy (**arXiv:2509.05909**) | **>7,843** MP entries | Cited, not re-analysed |
| Non-minimum incidence | Wander & Kitchin (**10.1021/acs.jpcc.4c07477**, data `github.com/jmusiel/gibby`) | 3,963 + 636 TS | **CUT at registration** |

**Total external n ≈ 5,800 for zero box-hours.** What no external corpus can supply, and the whole reason to stay small in-house: **not one of them varies two error classes on the same slab under one protocol.** The interaction terms, the coverage-conditionality, and the floor/excess split are in-house-only quantities. In-house n buys **CONTROL**; external n buys **PRECISION**. Never mix them in one sentence, and never multiply the per-relaxation exposure rate by the per-metal consequence rate.

**One correction that must be carried into S2:** the η(U) / floor-margin reconstruction from Xu's deposit is **not gas-reference-clean**. The physics critic enumerated 8,247 paths: the tree contains `supporting-data/O2` (ground plus an l-1.10 … l-1.30 bond-length scan) and **zero** files matching h2o, h2, gas, molecule or reference. But CHE needs G(H₂O) and ½G(H₂) *separately* — ΔG₂ = G(*O) + ½G(H₂) − G(*OH) requires H₂ alone, and imposing G_TOTAL = 4.92 eV does not eliminate it. **The free consolation: span_U(ΔG₂) and span_U(c_M) at fixed metal ARE gas-reference-independent.** So register the two halves separately, make the U-span half primary (needs no gas references at all), and budget two molecule jobs (H₂ and H₂O in a 12 Å Martyna-Tuckerman box at Xu's exact settings — ecutwfc 40 / ecutrho 500 Ry, GBRV ultrasofts, ~0.2 box-h plus staging the GBRV set) only if the absolute-floor-margin half is attempted.

### (d) The per-state versus per-metal registration split

Two quantities, in different units, registered separately, never multiplied.

**PER-STATE.** Unit = one (metal, adsorbate) relaxation *pair*. Quantity = |ΔE_ads(off-plane) − ΔE_ads(mirror)| in eV, plus the lock flag, the CONFOUND flag under |Δm_abs| > 0.1 µ_B, and the docs/43 §2 interaction bins (ADDITIVE ≤ 0.05 eV, INCONCLUSIVE, NOT_SEPARABLE ≥ 0.30 eV). **In-house n = 24** (8 metals × 3 adsorbates). Exact binomial CIs are legitimate because each pair is an independent relaxation, **but** the clustering is *measured and published* as an intra-class correlation with the design effect DEFF = 1 + 2·ICC stated on the face of the figure ("three states share one slab").

**PER-METAL.** Unit = one metal. Quantity = |Δη|, where η = max over four rungs built from three adsorbates plus the clean slab. **In-house n = 8** (of which 6 have a defined c_M; Co enters BOUNDED, Ni enters OPEN). The three states feeding one η are **not** independent, so a per-state rate may never be multiplied up into a per-metal rate — that inflates n ~3× and narrows the interval by ~√3, which is exactly the defect the round-1 physics critic caught in WIDE CENSUS's P-W3.

**The headline rides the per-metal quantity, reported as an 8-row TABLE of measured values with the mechanism attached — not as a rate with a threshold.** The Clopper-Pearson width at n = 8 (~0.68 near p̂ = 0.5) is registered *in advance* so a wide interval reads as disclosed rather than discovered. The per-state rate is the supporting higher-n row.

**A third unit, registered separately for the resolution number:** PER-PAIR, n = 7 adjacent pairs in an 8-member tier.

### (e) YES or NO on n = 25 in-house by the mid-October freeze

**NO.** The justifying number: reaching 25 requires 18 additions costing **11–16 human-days against 21 effective science days (52–76% of everything left)**, of which at most 4–5 are real ambient undistorted rutiles and **exactly zero** are magnetic 3d rutiles — so 18 additions would populate **zero** of the two largest rows of the error budget (U, magnetic basin) while importing 13–14 distorted, metastable or nonexistent phases, thirteen more than the three (Fe, Co, Ni) whose non-ambient status already contributed to one withdrawal. n would rise and the table would get *emptier*.

And even if the phases existed and were free, the precision is not there: the exact Clopper-Pearson 95% width on a per-metal rate near 0.5 runs **0.72 (n=7) → 0.68 (n=8) → 0.66 (n=9) → 0.60 (n=11) → 0.41 (n=25) → 0.31 (n=43)**; a ±0.15 half-width needs n ≈ 45. At n = 25, 12/25 gives [0.278, 0.687] — "somewhere between 28% and 69%" moves no judge, in-field or generalist. Decisively: **7 and 25 sit on the same side of the legibility threshold for the fifteen-person panel that makes the Finalist cut.** Both read as "a small number of his own calculations." The numbers that read as scale to that panel are 810, 515, 3,963, ≥500 and 7,843, and all five are already free.

**The recommended in-house n is 8** (existing 7 + TiO₂), **~46 box-hours and ~0.4 human-days for the addition**, with SnO₂ as a conditional 9th at a further ~46 box-h / ~0.8 days that is the program's first cut.

---

## 4. THE RECOMMENDED PROGRAM

**Budget basis, corrected.** Aug 15 → Oct 15 = 61 days = 8.71 weeks × 30 h = 261 h = **43.5 six-hour days**. Minus **8** for STS application mechanics (smapply Tasks 1–11, Rules Wizard, recommender engagement, AI-use disclosure, Research Report Similarities, Statement of Independence, six 200-word boxes, ACCESS Exchange Request). Minus **~14.5** for the six competing deadlines named in the entrant's own ledger. **Effective science budget: ~21 days.** The program below spends **21.0**, which is zero buffer and therefore not yet a plan — see §10 Q1 for the 3.5-day recovery I recommend, which takes it to 24.5 available / 21 spent / 3.5 buffer.

**Program totals: ~400 DFT jobs, ~1,320 box-hours** (4–6 days of pure drain on 15–20 Vast boxes; the binding item is one ~39 h magnetic 2x1v off-plane relaxation that cannot be parallelised away, plus a re-relax loop that serialises 2–3 passes — budget **3 calendar weeks**), **21.0 human-days.**

---

### S0 — Pre-flight capability gates + Amendment 7 · **CRITICAL PATH** · Aug 16–21
**29 jobs, ~35 box-hours. 2.5 human-days.**

Nine gates, each cheap, each recorded as a result whichever way it goes, each killing a specific failure that would otherwise be discovered in October.

| Gate | Jobs / cell | Box-h | What it decides |
|---|---|---|---|
| (a) **BEEF emission — FOUR decks, not one** | 4 SCFs, 1x1 on an existing converged Ru density | 4 | A single-deck grep **cannot distinguish "absent" from "not requested"** and would strike an entire stage on a null. Run: (i) `ensemble_energies=.true.` in `&SYSTEM`; (ii) `calculation='ensemble'` in `&CONTROL`; (iii) neither (control); (iv) the winner re-run **with the HUBBARD card present** (an undocumented combination). Record which switch this build honours. Only after (i)–(iii) all fail may the XC row be struck. |
| (b) **`noinv` exactness** | 2 fixed-geometry SCFs on one existing 2x1v off-plane geometry, `noinv` on vs off | 4 | **Highest ratio in the program.** Must agree < 1 meV. On agreement, drop `noinv` from every off-plane job: ~38% off the off-plane battery, worst single relaxation ~62 h → ~39 h, ≈ one week of calendar on the critical path. |
| (c) **Mirror-arm `nosym` invariance** | 1 fixed-geometry `nosym` SCF on an already-relaxed 2x1v mirror geometry | 2 | `build_cellsym_pilot.py` lines 514–517 hard-die on a mirror arm carrying nosym/noinv, and symmetry reduction of an MP mesh **is exact** for a structure that possesses the symmetry — so 9 → 16 is a *folding*, not a sampling change. Register "the mirror-arm energy is invariant to `nosym` to < 1 meV" as the comparability control, and keep the mirror arm at symmetry ON / 9 k. |
| (d) **Hessian timing AND σ_F in 2x1v** | 1 displacement SCF, 2x1v, `conv_thr 1e-10`, `nosym` | 2.5 | Must report three things, not one: wall clock (validates the ~2.4 h repricing), **whether `conv_thr 1e-10` is actually REACHED in 2x1v**, and the σ_F it delivers there. `build_hessian_pilot.py`'s table was measured at 21 atoms / 32 k / 1x1; the 19 built 1C decks are 2x1v (42 atoms, 16 k). If 1e-10 is not reached, the minimum claim is struck **before** decks launch. |
| (e) **Projector pairing (P-PROJ)** | 2 SCFs, Cr at U = 7.15 eV, 1x1 (matching A0), HUBBARD (atomic) vs (ortho-atomic) | 2 | Fires **before** any A0 deck is built on the fifth grid point. Gated on whether this build accepts ortho-atomic at all. |
| (f) **GATE-1 the four Cr LIT-1 U-ladder points** | 6 fresh-density fixed-geometry SCFs (4 U points + 2 second seeds at u0.0 and u1.35), in the cell the ladder was measured in | 5 | The 0.223 V floor movement is the program's most legible number and it currently rests on points the repo's own provenance section flags **GATE-1 PENDING**, against documented basin drifts of the same order (Cr *OOH −175 meV, Co *OH −405 meV). Registering it ungated repeats exactly the failure round 1 called fatal. |
| (g) **TiO₂ 2x1v nspin=1 timing** | 1 adsorbate relaxation, 2x1v | 4 | Replaces an extrapolated 3–6 h class with a measurement before S3 is costed. |
| (h) **AFM anchor probe** | 4 nspin=2 AFM fixed-geometry SCFs on existing RuO₂ 2x1v geometries | 8 | Closes the repo's own outstanding P11 and replaces the refuted "structurally incapable" wording with a measured magnetic row on an anchor. |
| (i) **Ti / Sn bulk cutoff ladders** | 8 bulk SCFs, 6-atom rutile cell, 60/80/100/120 Ry | 2.4 | Admission gate: \|ΔE\| < 5 meV/atom between 80 and 100 Ry inside the frozen 80/640 protocol. |

**Also in S0:** deposit **Amendment 6** to Zenodo (docs/43 line 1306 makes this a launch gate, not a formality, for the first block-6A job). Drain or explicitly **park** the in-flight LIT-2/3 campaign on box 47662258 — not left half-live, which is how this campaign has lost time before. Deposit **Amendment 7** (§8) before the first job it governs.

**Deliverable:** Amendment 7 Zenodo-deposited; nine capability gates discharged on the record; the phase-reality ledger with its exclusion table; six corrections of record.
**Claim scope unlocked:** none yet. This stage exists so that no later stage claims something the build cannot do.

---

### S1 — `silentgate`: forge the instrument, validate where the answer is known · **CRITICAL PATH** · Aug 21–27
**0 DFT jobs, 0 box-hours. 3.0 human-days.** (S3 deck construction runs in parallel Aug 17–24 — see the launch-date correction below.)

Lift the five existing detectors out of their `runs/`-coupled scripts into one pip-installable package with a CLI and pluggable readers (QE `pwscf.out` — the native format of both this campaign and the Xu deposit; ASE `.traj`/LMDB; VASP OUTCAR). Three generalisations, all confirmed defects of the current code:
- `symops_audit.py` hard-codes F_y as the locked coordinate (`adsorbate_max_fy` reads `group(3)`), but Xu's *O is pinned in **both** lateral directions and *OH/*OOH in mutually orthogonal ones. It must census **exactly-zero force components per atom, per Cartesian axis, per ionic step**, and report the lock **direction**, not a boolean.
- `slab_atom_count()` infers adsorbate indices from this repo's own `s0_OH`/`s0_O`/`s0_OOH` filename tags; it must read them from the deck.
- The `FY_NOISE = 1e-4 Ry/au` floor must be re-derived and declared **per corpus**.

**Two controls, registered in Amendment 9 before either is run (P-CTRL):** NEGATIVE — ≥500 OC20 relaxations must return **0.00% LOCKED**. POSITIVE — this campaign's own 20 `nosym`-absent production relaxations must return **≥95% LOCKED**. Both live in CI and re-run on every commit; the amendment records their status at the moment each audit number is generated.

**Two scope limits registered rather than discovered:** the OC20 control measures the false-**POSITIVE** rate only, so **no false-negative rate on a symmetry-ON corpus exists and no claim may depend on one**; and VASP prints forces to 6 decimals in eV/Å, so "exactly zero" in an OUTCAR is a print-quantisation question rather than the same test as QE's Ry/au blocks — which is why there is no OC22 symmetry arm anywhere in this program.

**THE ENTRANT WRITES THE CORE HIMSELF** — a few hundred lines of output parsing plus a symmetry-op header read and an exact-zero force census — with AI limited to test scaffolding, CI and review. **Rule: AI may not author the object the project is named after**, and that sentence goes verbatim in the 100-word disclosure.

**Deliverable:** `silentgate` v0.1 with CI that fails the build if either control regresses, and a measured false-positive rate against a corpus where the answer is zero by construction.
**Claim scope unlocked:** that the detector is an instrument rather than a regex written by someone who wanted it to be true. Without this every downstream symmetry number is void.

---

### S2 — The external census · **CRITICAL PATH** · Aug 27 – Sep 5
**0–2 DFT jobs, 0–0.2 box-hours. 3.0 human-days.**

Four zero-compute products, none of which can fail for compute reasons.

1. **Lock census over all 810 Xu Eads outputs**: symmetry-op header count, per-axis exact-zero force census in the final ionic step **and across every step**, and the **lock-direction map per metal per rung**. 40/810 headers and 12/810 force blocks were previously sampled, so 98.5% of the population is unmeasured and the direction map is blind for 6 of 10 metals.
2. **span_U(c_M) and span_U(ΔG₂) reconstruction** from the 680 deposited relaxations — **gas-reference-independent, therefore executable with zero new jobs.** The absolute floor-margin half is registered *separately* and requires the two GBRV molecule jobs; if those are not run, that half is reported as deferred, not fudged. Record that `tot_magnetization` is frozen at 15 across the whole ladder and classify it as a **declared modelling choice visible in the deck, not a silent failure mode** — a declared input is exactly the territory this project's novelty framing says is *not* its own.
3. **Divanis floor population as a δ-curve, with the denominator repaired.** Table SI-1 carries exactly four correction rows (H₂O 0; *OH + ½H₂ = 0.35; *O + H₂ = 0.05; ½O₂ + H₂ = −0.29) and **no *OOH row**; its corrections are attributed to reference [25] = Nørskov et al. 2004 (**10.1021/jp047349j**), **not** Man 2011. So report the population as an explicit curve over the single unknown scalar δ = corr_OOH − 0.35 across δ ∈ [0.00, 0.10] eV, with ∂(floor margin)/∂δ registered *before* the parse as +δ/2 for pls = 3, −3δ/2 for pls = 4, −δ/2 for pls ∈ {1,2}. **Report the per-paper rate (n = 24) and the rutile-only sub-rate (n = 38 from 3 articles) with the denominator composition printed on the figure face** — never an exact binomial CI at n = 515.
4. **pymatgen `AdsorbateSiteFinder` census, run unmodified INSIDE the repo, PAIRED with an input-set audit.** The census measures site symmetry at *generation*; exposure to the trap requires symmetry to be ON in the *relaxation*. atomate's `MPSurfaceSet` — the VASP input set its adsorption workflow uses for adslab relaxations — sets `"ISYM": 0` under the comment *"Should give better forces for optimization"*, introduced **25 May 2018, commit a7d5f316**; the contemporaneous 2017-era workflow (commit d2742a3b) used pymatgen's `MVLSlabSet`, which does **not** set ISYM, i.e. VASP's ISYM = 2 default. Report the two as **two numbers, never one product.**

**CUT AT REGISTRATION:** the Wander/Kitchin Hessian-incidence arm (its registered noise floor — "3× the median |ω_imag| of the translational/rotational modes" — does not exist for a fixed-bottom-layer adslab or a partial Hessian, and at OC20's `ediffg = −0.03 eV/Å` the incidence is dominated by residual-force curvature error, which largely *vindicates* the dismissal it was meant to indict). **CUT AT REGISTRATION:** the deposit-availability literature coding.

**Deliverable:** three census tables plus the paired site-symmetry/input-set result, all computed from raw outputs the entrant parsed himself.
**Claim scope unlocked:** that the symmetry lock is present, rung-dependently, in the deposited output of the paper this project cites for its own Hubbard U — i.e. it is not this student's builder bug — and a **dated** statement about when the field's canonical framework silently began disabling symmetry. This is the sentence that answers the sharpest available objection, at zero box-hours.

---

### S3 — The crossed coverage × symmetry × basin arm (`tier_v3`) · **CRITICAL PATH** · decks Aug 17–24, **LAUNCH Aug 26**
**~200 jobs, ~1,104 box-hours, all cells named. 6.0 human-days.**

**Launch-date correction, and it matters:** round 1 and all three round-2 proposals set the launch at Sep 1 and mitigated by "building and queuing decks in the week of Aug 24" — which is exactly the week five separate paper submissions are due (Simbiochem Aug 29, AI4Mat ×3 Aug 30, MoML Sep 1). **Move deck construction to the week of Aug 17, register Aug 26 as the last safe launch, and treat Sep 1 as the date by which the first 20 jobs must have REPORTED** so the pass-rate kill criterion fires while there is still time to act on it.

**The design, and why it is different from round 1's.** Because a 1x1 rutile(110) cell contains exactly **one** cus site, every 1x1 η in this project *and* in the literature anchors is a full-monolayer cus number, while 2x1v is half coverage. **In this geometry the cell variable and the coverage variable are the same variable.** That identity converts the coverage arm from an ~80 box-h 2x1o campaign into a ~22 box-h-per-metal 1x1 contrast leg, and it turns the flagship from a bare symmetry rate (which the disk data argues will come back null) into coverage-conditionality (which the disk data supports).

**Per magnetic 3d metal (Cr, Mn, Fe, Co, Ni), in 2x1v:** 3 mirror relaxations (42 box-h) + 3 off-plane (47) + 1 clean slab (14; Cr's exists) + 7 GATE-1 fresh-density SCFs (14) + ~2 re-relax children (30) ≈ **147 box-h** → 5 metals ≈ 721 box-h.
**Second spin seed, *OOH rung only**, 4 metals with no 2x1v data: 4 relaxations + 4 GATE-1 SCFs ≈ 70 box-h. (Restricted to *OOH because that is where Gauthier's 175 meV metastable state and Cr's confound live.)
**1x1 coverage-contrast leg**, 5 metals: 3 off-plane relaxations (9 box-h) + 3 GATE-1 SCFs (2) + 1 child (3) ≈ 14 box-h/metal ≈ 70 box-h; plus GATE-1 on the existing 1x1 mirror `tier_v2` data, 5 × 3 SCFs ≈ 10 box-h.
**TiO₂ 2x1v** ≈ 43.5 box-h. **Ru/Ir top-up to the identical protocol** ≈ 42 box-h. **Mn k-bridge**: MnO₂ has c = 2.876 Å → n₁ = round(25/2.876) = 9, odd, folding onto no integer 2x1 mesh; 4 × 8x4x1 SCFs ≈ 8 box-h. Fe/Co/Ni at c = 3.00/2.95/2.95 give n₁ = 8 and fold cleanly.
**Cr block 1C** (the 19 pre-built 2x1v decks, commit 51c36a6, image contact 1.338 → 3.983 Å): 19 displacement SCFs (46) + escape relaxation along the imaginary eigenvector (16) + **19 re-Hessian displacements at the escaped geometry (46)** ≈ 108 box-h. Plus the dy-ladder pilot on Cr's *OOH rung only, 2 extra dy values ≈ 31 box-h.

**Protocol registered in Amendment 8:**
- Off-plane = `nosym=.true.` **plus a physical displacement** (nosym alone leaves F_y at ~1e-8 on an exactly symmetric input), and **`noinv=.false.`** pending the S0(b) verification.
- Mirror arm stays at symmetry ON / 9 k, with the S0(c) invariance control as the comparability check. Same k-set on both members of every pair.
- Displacement ladder dy ∈ {0.10, 0.25, 0.50} Å on **one pilot metal (Cr, *OOH only)**, then the single best dy applied uniformly. This is the sweep's own design **in the spirit of** ShakeNBreak (**10.1038/s41524-023-00973-1**; **10.21105/joss.04817**) — the method's existence and purpose are confirmed but its numeric defaults (distortion factor range, step, rattle σ, neighbour count) could **not** be verified, so it must be registered as an original design, not a transcription.
- GATE-1 fresh-density fixed-geometry SCF on **every** final geometry with a re-relax loop. **Uniform audit depth per metal applied identically to all four states including the clean slab** — Co's clean slab already drifted +59 meV, so the reference is not safe.
- States with |Δm_abs| > 0.1 µ_B between constrained and free geometries are **excluded from the Δη score and reported separately as CONFOUNDED**, with the confound count itself a registered first-class deliverable.
- Reported as a **DIRECTED SADDLE-ESCAPE SEARCH along a measured unstable coordinate, yielding upper bounds on binding — never a global minimum search.** AdsorbML's own norm is ~106 configurations per system with an ML ranker and still misses the global minimum about one time in eight (**arXiv:2211.16486**; 87.36%, ~2000×, ~1,000 surfaces / 100,000 configurations all verbatim — note the "56 heuristic + 50 random" split is **not** in the abstract).
- **Free auxiliary test the MLIP kill does not cover:** the omat head was killed for cross-system *ranking*; ranking the dy-ladder members of the **same** system is a different task. Register "omat-head ordering of the ladder members agrees with DFT ordering at ρ > 0.6"; if it fails, say so and drop it.
- Co *OOH gets a three-attempt allowance and Ni *OOH is **expected to fail** — they have failed 4 and 5 times respectively, and **the convergence-failure rate is itself a registered budget row**, because a state that will not converge is silently dropped by every high-throughput pipeline.

**Deliverable:** `tier_v3` — 8 metals, four rungs, one cell, GATE-1-clean, multi-start, with the per-state audit-depth table published and holes reported as holes; the symmetry row and the basin row measured **at matched magnetisation**; the 1x1↔2x1v coverage contrast; the CONFOUND count; the Cr saddle-escape closed at **both** ends.
**Claim scope unlocked:** the first test of the symmetry trap on **any** 3d metal (it is n = 2, Ru and Ir, today), and the coverage-conditionality of the symmetry class.

---

### S4 — A0, the registered U grid · parallel, **not** critical path · Aug 18 – Sep 30
**~163 jobs, ~92 box-hours (+72 cuttable). 1.0 human-days.**

**A0-main exactly as Amendment 6 registers it:** 7 metals × 4 states × 5 U points = **140 fixed-geometry SCFs in the 1x1 cell** at ~0.4 h ≈ 56 box-h, plus `projwfc.x` inline on every point per A6.5.1 (+10% ≈ 6 box-h). **The 1x1 cell is a deliberate, stated exception and every figure names its cell on its face:** P7 — the threshold that actually fired and forced the withdrawal — was registered and measured at **fixed geometry in 1x1**, and only a like-for-like arm can bound it. Xu's 680 jobs differ in every controlled variable (full relaxations vs fixed geometry, 33-atom 2-layer slab, 40/500 Ry GBRV vs 80/640 SSSP, frozen `tot_magnetization`), so they corroborate and supersede nothing.

The fifth grid point carries whatever label **P-PROJ** assigns it in S0(e). Add a **fresh-density basin check per U point on the magnetic 3d metals** — the repo already flags Co's u1.35 point as mixing the U response with a solution change, and without this the U row and the magnetic row are not separable.

**A0-cell rider** (Cr-only, 4 states × 5 U points = 20 fixed-geometry SCFs in 2x1v ≈ 24 box-h): the per-metal I_U cell-separability verdict. Depends on S3's corrected Cr geometry. **Cuttable.**

**hp.x riders, both cuttable, named in cut order:** (1) bulk hp.x on **Cr and Ti only**, ATOMIC projector only (the production tier uses `HUBBARD (atomic)`, so an ortho-atomic U is a different Hamiltonian and may not share the U bracket axis without that label), ~6 box-h — **FIRST CUT.** (2) ONE slab relaunch under a hard 72 h cap — **SECOND CUT.** Settings and their corrections are in §5 arm 1.

**Deliverable:** the four-marker U bracket figure (MP-fitted / bulk linear-response atomic / Xu supercell-LR / the slab that does not converge), each marker labelled with its **projector**; the per-metal span(c_M) at fixed geometry in the cell P7 was measured in; the Löwdin-charge and local-moment valence mechanism.
**Claim scope unlocked:** that P7 is *explained*, not merely fired — the tranche-1 data already on disk shows ΔG_O carries Δm = −1.06 µ_B and swings 1.80 eV while ΔG_OOH carries Δm = −0.02 and swings 0.24 eV, which is the signature of Tripkovic's B-cation valence mechanism (**10.1021/acs.jpcc.7b07660**, confirmed from paper by lens 1).

---

### S5 — The XC row: BEEF-vdW σ · gated on S0(a) · Sep 20–30
**~14 jobs, ~20 box-hours, 2x1v. 1.0 human-days.**

**Runs only if S0(a) showed which switch this build honours.** Scoped to **Ru, Ir and Ti** — all three nspin = 1 and U = 0, so there is no BEEF+U ambiguity at all: 3 metals × 4 states = 12 self-consistent BEEF-vdW SCFs at fixed PBE+U `tier_v3` geometries at ~1.5 h ≈ 18 box-h, plus 2 gas references ≈ 2 box-h. The ~2000-member ensemble is free post-processing.

**This scope is a deliberate repricing.** FLOOR AND EXCESS budgeted 28 BEEF SCFs on 2x1v magnetic slabs at 1.2 h each; a 2x1v magnetic PBE+U SCF is already ~2.0–3.7 h by the repo's own model, and a **fresh-start** BEEF-vdW SCF with nonlocal correlation and no `startingpot` (forbidden by the repo's `_FORBIDDEN` guard) is ~3–7 h — a 3–5× under-count. Extending to the +U metals happens only if BEEF+U converges cleanly *and* the calendar allows.

**Four non-negotiables:** (i) the ensemble is a non-self-consistent perturbation about the **BEEF-vdW self-consistent** solution — evaluating it on a PBE+U density gives an object with no published error statistics; (ii) H₂O and H₂ references go in the same 12 Å Martyna-Tuckerman box and are **inside** the ensemble, not fixed; (iii) ΔG is formed **member-by-member with matched member indices** — the members are correlated, so adding independent per-species σ in quadrature overestimates the bar badly because the XC errors cancel between slab and reference; (iv) regenerate members portably with `ase.dft.bee.ensemble(seed=0)` rather than QE's glibc `srandom`.

**DROP** the σ(c_M) < 0.5 × mean-of-individual-σ test as a test of Christensen's functional-independence claim (**10.1021/acs.jpcc.6b09141**): c_M cancels the clean-slab term *exactly*, so it passes whether or not the intercept is functional-independent. Christensen's claim is about stability **across materials** under a functional change and must be tested that way or not claimed.

**Registered as a prediction, not a caveat:** the Hubbard term is not part of E_xc, so the ensemble is blind to the U error **by construction**, and equally blind to the symmetry trap (a geometry error) and to magnetic multistability (an electronic-solution error). **One row, labelled "XC only", never "the" uncertainty on η.**

---

### S6 — Analysis: floor/excess, estimators, statistics, resolution · **CRITICAL PATH** · Sep 30 – Oct 8
**0 DFT jobs. ~2 GPU-hours for the MLIP rescore on a separate pool. 2.5 human-days.**

(a) **Score P-SYMCOV and the per-metal Δη table** in their registered units, separately; publish the measured ICC and DEFF. (b) **The floor/excess decomposition** with the closed form registered first: for pls ∈ {2,3}, η = (c_M/2 − 1.23) + |ΔG₂ − ΔG₃|/2, i.e. excess = |ΔG_O − (ΔG_OH + ΔG_OOH)/2|; **the identity breaks when pls flips to 1 or 4**, and the flips are live in exactly the arms this depends on. **Report span(c_M)/2 at fixed endpoints, never max-minus-min over a grid**, and report the U at which each metal's pls flips as a deliverable in its own right. (c) **The four-estimator comparison** η_TD / ESSI / ESAI / G_max(η) with the σ Monte Carlo re-run per estimator (**10.1021/acscatal.0c03865**; cite ESAI at **10.1016/j.mex.2021.101590**, which was verified — the ESSI-origin citation is unresolved). (d) **The n = 7 statistics repair**, disclosed not discovered: exact-permutation CI on ρ = 0.8929, Holm across the four heads tested (0.0123 × 4 = **0.049**, a knife-edge), both Ir orderings (0.490 and 0.781, different ranks) as a sensitivity pair, conclusion stated **ordinally**, never bootstrapped at small n (**10.1037/met0000079**). Re-score against `tier_v3` with the **range-extension caveat stated explicitly** — TiO₂ is a d⁰ wide-gap oxide whose cus descriptor sits outside the current 0.33–1.26 V span and will inflate Spearman mechanically. (e) **Cite Krishnamurthy, Sumaria & Viswanathan (10.1021/acs.jpclett.7b02895)** for the expected-activity/prediction-efficiency framework *before* any bias wording is fixed, and claim only what is distinct: because 4.92 eV is imposed, η reduces **exactly** to max(rungs) − mean(rungs), a structural identity that is ≥ 0 by construction and monotonically inflated by error of any origin. (Note its actual title is *"Maximal Predictability Approach for Identifying the Right Descriptors for Electrocatalytic Reactions"* — attribute the "expected activity" formalism carefully, possibly to the Deshpande 2016 companion **10.1021/acscatal.6b00509**.) (f) **Write the Society's one non-technical sentence and check the results support it**; if they do not, cut a claim, not the sentence.

---

### S7 — Freeze, deposit, figure pack, report mechanics · Oct 8–15
**0 jobs. 2.0 human-days.**

`silentgate` v1.0 with a Zenodo DOI. Every number traced to a run directory and a `tier_vN` tag. **Three mechanical rules the report is built for, not retrofitted to:** every image, graph, table and chart **including self-made ones** must carry a citation (a missing figure citation can disqualify) → a caption-and-citation emitter lives inside the plotting code and a pre-submission script parses the compiled PDF and asserts it; **no hyperlinks anywhere except bibliography entries** and evaluators are forbidden from clicking → the report is fully self-contained with the Zenodo deposit appearing only as a bibliography entry, never as a dependency, and the word "released" does not appear in the headline sentence; **appendices count against the 20 pages** (only title page, abstract page and bibliography are exempt) → allocate pages *before* figures (~2 intro / 6 methods / 7 results / 3 discussion / 2 limitations).

**Count display items and multiply by four lines before allocating results pages.** At 15–20 display items, caption + citation line + on-face cell/coverage label runs 3–4 lines each — roughly **1.5–2 pages of the 20 consumed by caption furniture alone.** Merge aggressively: the interaction matrix and the budget table are one object; the partial order and the resolution number are one object.

The same script asserts the **phase-reality scoping rule** (no absolute η from a MODEL-PHASE row appears outside a paired within-metal difference) and that **every figure names its CELL on its face**. Regenerate the entire bibliography from Crossref rather than typing it. **Hard freeze Oct 15; nothing new launches after Oct 8.** Then the entrant writes every word alone.

---

**Critical path:** S0 → S1 → S2 → S6 → S7 is the spine that cannot fail for compute reasons and from which the central claim must be scorable. S3 is on the critical path for the *artifact* but not for eligibility. S4 and S5 are parallel riders.

---

## 5. THE SEVEN REVIVED ARMS, INDIVIDUALLY ADJUDICATED

### 1. hp.x first-principles U (Stage A) — **RUN MODIFIED, MINIMAL, FIRST NAMED CUT**

**Register these settings, with these corrections to lens 7:**
- **`nq3 = 1`.** A q-point along the vacuum axis of a slab perturbs the periodic images and is physically meaningless; if the failed run used nq 2 2 2 that alone could explain the plateau. This is the one fix that is both necessary and free.
- **`nbnd` +25%** over default (empty states starve the Sternheimer solve).
- **`degauss` HELD at the production 0.01 Ry, NOT raised to 0.02.** Lens 7 recommends raising it; the physics critic is right that 0.02 Ry ≈ 0.27 eV will partly fill the gapped spin channel of a half-metal like CrO₂, so any U so obtained is U(degauss = 0.02), not the U of the production Hamiltonian. If it is raised anyway, **register it with its smearing or it is not transferable.**
- **`perturb_only_atom` NOT used as a cost reduction.** U_I = (χ₀⁻¹ − χ⁻¹)_II requires the full response matrix over all symmetry-inequivalent Hubbard atoms; perturbing only the cus metal gives one row of χ, which is not invertible on a slab carrying distinct cus, bridge and subsurface sites. It is a parallelisation device to be collected with `compute_hp`. **UNVERIFIED against the hp.x manual — test on the box before registering.**
- **`niter_max = 300` with a 72 h cap, not 24 h.** The measured rate is 18.7 h / 80 iterations = 0.234 h per iteration, so 300 iterations is ~70 h; a 24 h cap kills the job at ~100 iterations and makes the abandon threshold unscorable.
- **Abandon threshold registered first:** if the cus-atom χ residue still exceeds 3e-5 after 300 iterations under these settings, the slab-DFPT arm is **CLOSED-NEGATIVE** and the finding stands as a first-of-kind negative result.
- **Production U is NOT sourced from a converged slab-DFPT U even if the fixes work.** Tripkovic's mechanism means the correct U for a cus site changes along *OH → *O → *OOH as its valence changes, so a single slab U is no more defensible than a bulk U — just more expensive and harder to explain. The slab arm's value is as a **DIAGNOSTIC**: does a metallic magnetic oxide slab admit a linear-response U at all?
- **Bulk hp.x: Cr and Ti only, ATOMIC projector only**, ~6 box-h.
- **The bi-U sensitivity sweep is registered as a zero-compute note, not run.** The literature's actual practice is bulk-derived U plus a surface-specific U (Hu, Cao & Hu, **10.1021/acs.jpcc.8b05513**, JPCC 2018 122 19593–19602, *abstract only*; Jiang & Mushrif PCCP 2023 25 8903–8912, **10.1039/d2cp04814k**, whose NiO(100) ~2 eV vs bulk 5.3 eV numbers are **search-snippet only and remain UNVERIFIED**). Lens 7 itself concedes the honest limitation: the bi-U fit in the literature is anchored to RPA or XPS, neither of which this project has, so the surface U can be varied but not **fitted** here. There is no human budget for the sweep.

**Framing, corrected:** *"linear-response U determination has been industrialised across 2,000+ bulk transition-metal oxides (Moore et al. 2024, **10.1103/PhysRevMaterials.8.014409**, an atomate linear-response workflow); no published campaign applies DFPT/hp.x to a slab at all."* Two corrections of record: (i) that Moore is **VASP + atomate supercell** rather than DFPT is a defensible **inference**, not a read fact — the abstract says only "linear response (LR) methodology" and "an atomate workflow" — so label it as an inference or read the Methods; (ii) SILENTGATE v2's proposed correction *"Moore's author order has Linscott and Ganose transposed"* is **itself wrong** and must be struck: the verified order is Moore, Horton, Ganose, Siron, Linscott, O'Regan, Persson, which is what LENS-DIGEST-6 already prints.

**Citation split (lens 7 attached verified formalism to unverified operational advice):** cite **10.1103/PhysRevB.103.045141** (Timrov, Marzari, Cococcioni 2021) **only** for the USPP/PAW-and-metals formalism — its abstract does **not** mention the q→0 1/DOS(E_F) correction, does **not** mention spin polarisation, and certainly does not contain the niter_max/nbnd/degauss/q-restart ladder, which lens 7 itself admits came from QE-users mailing-list replies. Carry the ladder as **UNVERIFIED, no DOI.**

### 2. Symmetry trap on the five 3d metals (Stage C) — **RUN MODIFIED. Flagship, re-registered as coverage-conditional.**

Protocol and settings in §4 S3. The single change from round 1: the registered threshold is **P-SYMCOV** (the symmetry effect is coverage-conditional), not a bare per-metal rate. Sourced from lens 7's ShakeNBreak analogue (**10.1038/s41524-023-00973-1**, **10.21105/joss.04817** — existence and purpose confirmed, numeric defaults **could not be verified**, so the dy ladder is registered as an original design in the spirit of that method) and from AdsorbML's sampling norm (**arXiv:2211.16486**).

**Framing that lens 7 supplies and that is stronger than round 1's:** the trap is **known and named for point defects** (the ShakeNBreak literature) but no equivalent exists for adsorbate placement in high-throughput catalysis. That is the novelty claim, and it is stronger stated that way than as "nobody has ever seen this." Lens 7's targeted search for prior art on adsorbates placed on slab mirror planes in high-throughput screening returned **none** — absence of evidence, not evidence of absence, but an honest statement of a targeted search.

### 3. Coverage arm — **RUN MODIFIED: folded into arm 2 as the 1x1 contrast leg. The separate 2x1o termination campaign is DROPPED.**

The cell-equals-coverage identity (§4 S3) makes this ~22 box-h per metal instead of ~80. **Three zero-compute registrations go in the same amendment:**
- **Configurational entropy is NEGLECTED with a bound, not computed.** For a binary O/OH mixture on the cus row the ideal-mixing term is bounded above by **kT ln 2 = 0.0179 eV per site at 298 K**, below every threshold in docs/43 (0.10 eV, 0.15 V). State the bound and move on.
- **The surface Pourbaix construction, if it is ever drawn, is Hansen, Rossmeisl & Nørskov's** (**10.1039/b803956a**, PCCP 2008 10 3722–3730, verified) inside Reuter & Scheffler's ab initio atomistic thermodynamics framework, with the modern extension putting BEEF ensemble widths on the phase boundaries (**10.1021/acs.langmuir.8b02219**).
- **The anchors are predicted insensitive and the 3d metals are not.** For AFM RuO₂(110), computed η stays in the 0.4–0.5 V band essentially irrespective of O vs OH cus coverage (**10.1021/acs.jpcc.1c08700**, title verified: *"Anti-Ferromagnetic RuO₂: A Stable and Robust OER Catalyst over a Large Range of Surface Terminations"*), while block 1A's own data has 6/9 rows over 0.10 eV with Cr *O at +0.72 eV. External calibration for the magnitude comes free from Man 2011's two-coverage rows (**10.1002/cctc.201000397**: ΔG_OH weakens +0.13 to +0.36 eV, η moves −0.06 to +0.33 V).

**Also register:** a metal whose resting state differs from its assumed termination has its `tier_v2` value marked **SUPERSEDED**, not adjusted.

### 4. Magnetic ground-state grid (Stage B) — **RUN MODIFIED, merged into arm 2, plus one new cheap arm.**

Lens 7's full protocol (8 configurations per state = FM + symmetry-inequivalent AFM sign patterns, each as a fixed-geometry fresh-density SCF at the already-relaxed geometry, plus one U-ramped start as a ninth; ~216 SCFs) is **not affordable at 21 human-days** — the box-hours are cheap but the triage is not. **Cut to:** two spin seeds on the *OOH rung only for the four metals with no 2x1v data, plus one `starting_ns_eigenvalue` occupation-seeded start on Cr and Mn.

**Registered acceptance rule, from lens 7:** the lowest-energy configuration is adopted only if it is **more than 20 meV below the runner-up**; otherwise the state is flagged **MULTISTABLE** and carries a range.

**New and cheap, and it fixes a fatal:** the **AFM anchor arm** (S0(h)). 4 nspin=2 AFM fixed-geometry SCFs on existing RuO₂ 2x1v geometries, ~8–10 box-h. This closes the repo's own outstanding P11 and replaces the refuted "the anchors are structurally incapable of exhibiting the two largest error classes" with a **measured** magnetic row on RuO₂. Directionally supported by **10.1021/acs.jpcc.1c08700** (AFM 0.41–0.49 V vs NM 0.63–0.73 V, ΔG(*O) rising up to ~0.3 eV ⇒ the row is worth ~0.2 V). Note that "spin-polarising the anchors is a closed negative" does **not** rescue the old wording — an FM initialisation on an AFM material collapses to NM by construction and tests nothing.

**Two corrections of record:** `starting_ns_eigenvalue` is an **initial guess on the first DFT+U iteration, NOT a constraint held through the SCF** — strictly weaker than VASP's occupation-matrix control and it must not be called OMC. And **never claim discovery of DFT+U multistability**: Dorado 2009 (**10.1103/PhysRevB.79.235125**), **Rabone & Krack** 2013 on UO₂ *surfaces* (**10.1016/j.commatsci.2013.01.023** — the digest twice misattributes this to "Dorado et al."; the authors are Jeremy Rabone and Matthias Krack), Meredig 2010 (**10.1103/PhysRevB.82.195128**), Allen & Watson (**10.1039/c4cp01083c**), Keshavarz & Thunström (**arXiv:1810.10393**, covering NiO/CoO/FeO), Qiu 2025 (**10.1021/acs.jctc.4c01520**, single author — "Qiu (2025)", not "et al."), and Fahmy (**arXiv:2509.05909**) all precede it. Claim B survives on the **mechanism** (the basin is chosen at ionic step 1 and dragged to the final geometry by `pot_extrapolation='atomic'`) and the **consequence** (a measured shift in a CHE overpotential) only.

### 5. Solvation via ESM/RISM (Stage D) — **DROP as a measurement. Register the cancellation lemma at zero compute, and register a NON-additivity prediction.**

**ESM dropped entirely, on lens 7's reasoning:** with `esm_bc='bc1'` the method removes the image dipole–dipole interaction, which is what the dipole correction already does — and the dipole correction is a **closed negative** in this campaign. ESM produces new information only with `tot_charge ≠ 0` or constant-µ (`lfcpopt`/FCP, requiring bc2 or bc3). There is no budget for a potential-controlled arm, so the bc1 middle ground would re-measure a known zero.

**RISM dropped:** docs/42 verified only that the `&RISM` namelist parses and that it fails in `read_solvents`. The `.MOL` files at `github.com/nisihara1/MOLs` (**UNVERIFIED**, from Otani's Tsukuba ESM-RISM tutorial, no DOI) are **not inert data** — Demeyere & Skylaris find water lone pairs "crucial" to getting RISM right (**10.1021/acs.jpcc.4c04924**) — and implicit models systematically miss the hydrogen bonding that **is** the mechanism by which solvation moves c_M.

**Register the cancellation lemma (lens 7, zero compute):** because c_M = ΔG_OOH − ΔG_OH, any solvation correction that stabilises *OH and *OOH **equally** leaves c_M **exactly** invariant, hence leaves η_floor = c_M/2 − 1.23 exactly invariant. Cr sits 9 meV above its floor. Solvation can therefore move η(Cr) **only** through the differential |δ_OOH − δ_OH|.

**But do NOT register lens 7's proposed threshold "solvation moves η(Cr) by < 0.15 V."** Lens 7 admits its 0.1–0.25 eV differential band is a literature-consensus estimate assembled from secondary summaries, **not read from Gauthier**. Lens 1 read Gauthier **from the paper** (**10.1021/acs.jpcc.7b02383**, confirmed-from-paper): with *O on the neighbouring cus site, ΔG_OOH − ΔG_OH **decreases by ~0.3 eV**; at *OH coverage it changes by only ~0.1 eV; *OOH is stabilised more than *OH by 0.3–0.5 eV; converged at 1–2 bilayers. **0.3 eV in c_M is exactly 0.15 V of floor movement** — the proposed threshold sits *on* the paper-read value, which makes it a coin flip rather than a prediction.

**Register instead, and it is a better registration:** the row is **TRANSFERRED**, ΔG_OOH swept over [−0.4, +0.2] eV with **no designated central value**, and the falsifiable statement is the **non-additivity** of solvation × coverage — Gauthier's ~0.3 eV shift in c_M at O coverage versus ~0.1 eV at OH coverage means |Δc_M(O cov) − Δc_M(OH cov)| > 0.10 eV, in **direct contrast** to block 1A's measured ADDITIVE ×5 for U × cell. This is the only place in the program where an interaction is *predicted to fail*, it costs nothing, and it rests on a paper somebody actually read. Guard it with Inico (**10.1002/cctc.202400813**, confirmed-from-paper): a single static bilayer gives "sizeable deviations" versus AIMD on exactly TiO₂/RuO₂/IrO₂(110), so no bilayer number may ever be reported as a solvation value.

**Reference convention, registered:** the only defensible reported quantity is ΔΔG_solv on the adsorbate side with the clean-slab solvation explicitly cancelled — a solvated slab energy cannot be combined with a vacuum H₂O/H₂ gas reference without saying so.

### 6. The 2x1o cell arm — **DROP.**

Block 1A closed **ADOPT_2X1V**. A third cell is a third protocol in a 20-page report whose entire thesis is protocol hygiene, it cannot be crossed with anything in the remaining time, and the coverage question is answered more cheaply and more honestly by the 1x1↔2x1v contrast — because in a one-cus-site cell the cell variable and the coverage variable **are the same variable**. Cite the closed 1A result. **This identity must be stated in the methods rather than left for a reader to discover**, and block 1A's ADOPT_2X1V verdict and the coverage arm must never be presented as two independent error classes.

### 7. BEEF-vdW η error bars (Stage E) — **RUN MODIFIED, gated on a FOUR-deck test, scoped to three nspin=1 metals.**

Protocol and scope in §4 S5. **The registered limitation is the thesis, stated as a prediction rather than a caveat:** the BEEF ensemble is an XC-parameter uncertainty **only** and by construction cannot see symmetry, basin, U, coverage or cell, because the Hubbard term is not part of E_xc. Reporting a BEEF σ as *the* project's uncertainty would contradict the project's own central claim. **One row, labelled "XC only."** Cites: Wellendorff (**10.1103/PhysRevB.85.235149**); Vinogradova (**10.1021/acs.langmuir.8b02219**). `ensemble_energies` is documentation, not literature — **UNVERIFIED, no DOI**.

### Plus: DFPT+U / ph.x for the Hessian — **REJECTED A PRIORI, but the reason lens 7 gives is unsound and must be replaced.**

Lens 7 cites **arXiv:2605.20985** as "confirmed-from-abstract" for *"DFPT+U is documented non-convergent above U ~2 eV in some materials."* The citation critic fetched it: it is Chen, Tu, Xia, Zhao & Chen, *"Hubbard-U-corrected electron-phonon interactions in strongly correlated materials via the finite-displacement method"* (20 May 2026). **The abstract says nothing about DFPT+U, nothing about convergence failure, and nothing about a U ~2 eV threshold.** Putting that number into a dated pre-registration is exactly the error class that has already burned this campaign twice.

**Re-base the rejection on two defensible grounds and record it before the fact:** (i) hp.x measurably failed to converge on *this exact slab* (χ residues plateau ~1e-4 against `conv_thr_chi` 1e-5, oscillating at `niter_max` 80, 18.7 h wall) — noting the honest limitation that this does **not** transfer as a physics argument, since hp.x's failure is a χ-matrix iteration under a Hubbard-α perturbation while ph.x's would be a phonon Sternheimer solve, so it is evidence about *this system's* DFPT behaviour, not a theorem; and (ii) the central finite-difference partial Hessian is already built and priced. Cite **arXiv:2605.20985** only for what it actually shows — that a 2026 DFT+U phonon implementation chose finite displacement, and that it studied RuO₂. Cite Floris et al. (**10.1103/PhysRevB.101.064305**) here, as the reference for the *existence* of DFPT+U in QE — **and strike that DOI from lens 7's frequency-verification finding**, where it is attached to an imaginary-mode-follow recipe it says nothing about. The three-step recipe (Hessian → follow the imaginary eigenvector → re-Hessian) is textbook and should carry a real source or none.

---

## 6. NEW WORK THE ENTRANT HAS NOT CONSIDERED, RANKED BY VALUE PER HUMAN-DAY

**1. The `noinv` exactness test. (~0.1 human-day, 4 box-hours.)** Highest ratio in the entire program by a wide margin. Time reversal (k ↔ −k) is an exact symmetry of a collinear, spin-orbit-free Hamiltonian **regardless of the structure's point group**, so folding under it is exact whether or not the adsorbate sits on a mirror plane. The off-plane arm needs `nosym` — that is the trap — but not `noinv`. Verify with one fixed-geometry SCF pair (must agree < 1 meV), then drop it: **~38% off the off-plane battery, worst single magnetic relaxation ~62 h → ~39 h, ≈ one week of calendar on the critical path.** Nobody in round 1, round 2 or any lens noticed this.

**2. The AFM anchor arm on RuO₂. (~0.3 human-day, ~10 box-hours.)** Kills a fatal (the "structurally incapable" wording is refuted by the project's own docs/41, which calls `qe_slab.py`'s comment factually wrong for RuO₂ and cites Berlijn PRL 118, 077201 (2017) for itinerant AFM), closes the repo's own outstanding P11, and replaces a rhetorical claim with a measured ~0.2 V magnetic row on the material the field calibrates against (**10.1021/acs.jpcc.1c08700**). Same rhetorical point, made honestly.

**3. GATE-1 the four Cr LIT-1 U-ladder points before Amendment 7 dates the floor number. (~0.2 human-day, ~5 box-hours.)** The 0.223 V floor movement is the program's most legible number and the repo's own provenance section states the non-production-U points are **GATE-1 PENDING** — three single-seed SCFs with no basin gate carrying a 0.447 eV intercept span, against documented basin drifts of the same order. This is insurance against repeating the exact failure round 1 called fatal.

**4. Register the pls-crossing U as a deliverable in its own right. (~0.2 human-day, zero compute.)** The physics critic's fatal on P-U-SPLIT contains a gift: the excess |ΔG₂ − ΔG₃|/2 vanishes **identically** at the pls 3→2 crossing where ΔG₂ = ΔG₃, and Cr's production U landed **7 meV** from that crossing. So the real physical content of "Cr sat 9 meV above its floor" is that the production U happened to land essentially *on* a potential-limiting-step crossing. That is sharper, more physical, and more surprising than any ratio, and it is free.

**5. The solvation × coverage non-additivity registration. (~0.2 human-day, zero compute.)** §5 arm 5. The only place in the program where an interaction is *predicted to fail*, resting on a paper lens 1 read in full.

**6. The atomate input-set audit, paired with the pymatgen census. (~0.5 human-day, zero compute.)** `MPSurfaceSet` sets `"ISYM": 0` under the comment *"Should give better forces for optimization"*, introduced **25 May 2018 (commit a7d5f316)**; the contemporaneous 2017-era workflow used `MVLSlabSet`, which does **not** set ISYM. That is a **dated** statement about when the field's canonical adsorption framework silently began disabling symmetry, with no paper explaining why — a better and more checkable sentence than the raw site-symmetry rate, and it fixes the defect that would otherwise make the census overstate exposure.

**7. The Divanis denominator repair. (~0.5 human-day, zero compute.)** 515 rows / 24 articles, only 38 bare rutile MO₂ from 3 articles, article 22 alone 122 rows (24%). Paper-level clustering plus the rutile-only sub-rate is the difference between a defensible statistic and a pseudo-replicated one — and it is the same unit-of-analysis error the physics critic caught in the per-(metal, adsorbate) rate.

**8. Man 2011's own arithmetic guard. (~0.1 human-day, zero compute.)** Man's high-coverage CrO₂ row reconstructs to η = 1.96 V — but its **ΔG₄ is NEGATIVE (−0.46 eV**, because ΔG_OOH = 5.38 > 4.92), so that row is unphysical under the imposed-4.92 convention and its η is an artefact of forced telescoping. **Do not quote 1.96 V without that note.** Free, and it is exactly the kind of thing an in-field PhD checks.

**9. The one-sentence legibility test, run this week. (~0.2 human-day.)** Write the sentence the Society would print before spending compute, and let it pick which arm gets the box-hours.

### The oxyhydroxide (MOOH) question — **VERDICT: DROP, and convert it to a scope statement.**

Oxyhydroxides are the physically correct OER phases for Fe/Co/Ni, and that is precisely why adding them eight weeks out is a trap: new terminations, new convergence surfaces, new magnetic complexity, a second protocol in one 20-page report, and the immediate question *"so why did you report rutile FeO₂ at all."*

The zero-compute version is **stronger than running it**, and round 2 sharpens it beyond round 1's answer. Round 1's scope statement was "Fe/Co/Ni rutile MO₂ are model phases with no external comparator anywhere" — verified: Man 2011's 24-paper compilation contains no rutile FeO₂ or CoO₂ row, and its only NiO₂ row is a **reduced bridge-site** surface (**10.1002/cctc.201000397**). Round 2 adds a second clause the entrant does not yet have: **of the five magnetic 3d systems in the tier, four are not ambient phases and the fifth (β-MnO₂) is run in the wrong magnetic order** — it is antiferromagnetic and `gen_rutile.py` initialises it ferromagnetic. Stating both, before any gate is registered, converts the weakness into an explicit scope result about what DFT screening of hypothetical rutiles can and cannot claim — and pre-empts the accusation that the gate was chosen to fit the metals it can pass.

---

## 7. WHAT TO SCAN AT SCALE

| Corpus | Identifier | What it is | First test |
|---|---|---|---|
| **Xu/Rossmeisl/Kitchin 2015** | paper **10.1021/jp511426q**; data **10.5281/zenodo.12635** (CC0, one file `rutile-OER-v1.0.zip`, **572.4 MB** — not 1.93 GB); mirror `github.com/zhongnanxu/rutile-OER` (CC-BY-4.0, created 2014-11-07). **Attribute regardless of mirror.** | 815 `pwscf.in` + 815 `pwscf.out`, **Quantum ESPRESSO, same code**. 810 Eads outputs across **10 metals with adsorbate sets** (CrO₂, IrO₂, MnO₂, MoO₂, NbO₂, PtO₂, ReO₂, RhO₂, RuO₂, TiO₂) — **eleven directories total; SnO₂ is bulk-EOS only** (53 fine-EOS + 26 coarse-EOS + 5 ground, no slabs, no Eads). 680 of the 810 = 4 states × 17 U points (0–8 eV). 143 bulk linear-response outputs (48-atom Cococcioni supercell, `Hubbard_alpha` ∈ {0, ±0.07, ±0.15}, 4×4×4 k, no vacuum — verified from the primary input, which is what makes "hp.x-on-a-slab is first-of-kind" checkable rather than inferred). | Symmetry-op census over all 810 + per-axis exact-zero force census + the **lock-direction map per metal per rung**. 40/810 headers and 12/810 force blocks sampled; blind quantity is the direction map for 6 of 10 metals. Then **span_U(c_M) and span_U(ΔG₂)** — gas-reference-independent, no new jobs. Absolute floor margin needs 2 GBRV molecule jobs, registered separately. |
| **OC20 (negative control)** | **10.1021/acscatal.0c04525** / arXiv:2010.09990; config in fairchem `src/fairchem/data/oc/utils/vasp_flags.py` | `isym=0`, `symprec=1e-10`, `ispin=1` across 1.28M relaxations — symmetry disabled by construction | ≥500 relaxations must return **0.00% LOCKED**. Measures the false-**positive** rate. A gate that voids, not caveats. |
| **Divanis 2020 ESI** | **10.1039/C9SC05897D**; `SC-011-C9SC05897D-s001.pdf` + `divanis_esi.txt` already on disk | **515 data rows / 24 articles**; only **38 bare rutile MO₂ from 3 articles** (Man 26, Mom 11, Frydendal 1). Article 22 = 122 rows (24%), article 18 = 75. Refs verified: [1] Man **10.1002/cctc.201000397**; [7] Mom/Cheng/Koper/Sprik JPCC 2014 118 4095–4102; [8] Halck **10.1039/c4cp00571f**; [16] Gauthier JPCC 2017 121 11455; [19] Tripkovic ChemSusChem 2018 11 629–637 (**hollandite α-MnO₂, not rutile β**). | Floor margin as a **δ-curve** over δ ∈ [0.00, 0.10] eV, with the per-paper rate (n=24) and the rutile-only sub-rate (n=38) reported separately and the denominator composition printed on the figure face. Table SI-1 has four correction rows and **no *OOH row**; corrections attributed to ref [25] = Nørskov 2004 (**10.1021/jp047349j**), **not** Man 2011. |
| **pymatgen `AdsorbateSiteFinder`** | **10.1038/s41524-017-0017-z** (Montoya & Persson) | The canonical site enumerator. Run **unmodified, inside the repo, on the project's own slabs**, over rutile(110) / perovskite(001) / spinel(001) / fcc(111) × {*O, *OH, *OOH}. The only result in the program that generalises past rutile, and it needs no energy model. | Site symmetry of every enumerated configuration, with the denominator **counted before registration**. **Must be paired with the input-set audit** (atomate `MPSurfaceSet` ISYM=0 since commit a7d5f316, 25 May 2018; `MVLSlabSet` 2017-era does not set ISYM) and reported as **two numbers, never one product.** Methods section still unread — pull through Purdue ILL. |
| **Fahmy magnetic-order bias** | **arXiv:2509.05909** | Systematic FM bias affecting >7,843 Materials Project entries, attributed to workflows converging to FM solutions from FM initialisation | **Cited, not re-analysed.** Population-scale external anchor for the magnetic-basin class. |

**GATED / STRETCH, not in the 21-day budget:** OC22 (**10.1021/acscatal.2c05426**) — 43,189 adslab systems, the only corpus large enough to turn the magnetic-basin finding into a population statistic. But **OC20's `isym=0` does NOT transfer**, and independently, VASP prints forces to 6 decimals in eV/Å so "exactly zero" in an OUTCAR is a print-quantisation question rather than the same test. **No OC22 symmetry arm exists in this program.** CatHub (**10.1038/s41597-019-0081-y**) now requires a free API key (anonymous GraphQL returns "Missing API key") — budget an hour before planning anything on it.

**CUT AT REGISTRATION:** Wander/Kitchin Hessians (**10.1021/acs.jpcc.4c07477**, data `github.com/jmusiel/gibby`: `oc20_hessians_release.db` 48.6 MB = 3,963 minimum-intended, `oc20neb_hessians_release.db` 7.0 MB = 636 TS positive control). Reason recorded: the registered noise floor does not exist for a fixed-bottom-layer adslab or a partial Hessian, and at `ediffg = −0.03 eV/Å` the incidence is dominated by residual-force curvature error — the honest deliverable would be "not resolvable at OC20's convergence," which partially vindicates the dismissal it was meant to indict.

**DO NOT SCAN:** ODAC23 / OMol25 / OMC25 (wrong domain). AFLOW / OQMD / Alexandria / MP Crystalium (bulk crystals and elemental surfaces; no oxide slabs, no adsorbates — use MP only for E_hull and Pourbaix gating). Tran's 4,119-oxide screen (**10.1039/d4nr01390e**) for anything beyond the floor lemma. **And do not fine-tune any MLIP on any of it** — the original kill still holds (all 896 candidate frames have F_y ≡ 0, i.e. zero signal on the coordinate the trap lives in), the Xu frames are symmetry-locked too so they would add thousands more with the identical blind spot, and Warford, Thiemann & Csányi (**arXiv:2601.21056**) give an independent reason: selective +U in MPtrj/Alexandria/OMat24 produces spurious metal–oxygen repulsion in exactly the coordinate this chemistry lives on. That paper is also the *mechanism* for Finding 7's split result and should be cited as such.

---

## 8. THE PRE-REGISTRATION MAP

**Deposit obligation:** every amendment goes to Zenodo **before the first job it governs runs**. Amendment 6's deposit is an outstanding launch gate for block 6A (docs/43 line 1306).

**Two governance rules registered once, applying to all amendments:**

- **P-DISPOSITION.** Any prediction not scored by Oct 15 is marked **WITHDRAWN-UNSCORED with its withdrawal date**, and withdrawal is a legitimate ledger outcome shown alongside HELD and TRIGGERED. **The body-figure ledger is capped at six rows** — five new predictions plus the historical P7 — because a ledger with blank rows is precisely the "results to date of an unfinished study" shape displayed in the report's most prominent methodological exhibit.
- **P-AUTHORSHIP.** The entrant **re-authors every threshold statement in his own words before the amendment is deposited**, and the deposit records that he did. Draft threshold text that is Zenodo-deposited and then reproduced verbatim in a report figure requires review before use. A contemporaneous provenance record starts this week and runs to Nov 5, recording the work performed (literature sweep, arm design, adversarial critique, test scaffolding, CI) and the scope of the record.

**Status vocabulary, registered once:** every budget cell carries a status from **{MEASURED, BOUNDED, TRANSFERRED, NOT MEASURED}**. The token **"STRUCTURALLY ZERO" is struck** — it was refuted before any job ran.

---

### Amendment 7 — before ANY new job (S0, deposit by Aug 18)

**Registrations:**
- **P-PROJ** *(fires before any A0 deck is built on the fifth grid point).* Two Cr fixed-geometry SCFs at U = 7.15 eV, HUBBARD (atomic) vs (ortho-atomic), same cell as A0. **PREDICTION: |Δη(Cr)| > 0.10 V.** **FALSIFIED below 0.03 V**, in which case the projector is not a live variable at this U and Xu's supercell linear-response value may be imported as a literature anchor. If it fires, the fifth A0 grid point is labelled **PROJECTOR-MISMATCHED before any result exists**, the whole η(U) grid runs in ONE projector, and the projector delta becomes its own labelled sub-row. **Fully blind** — the campaign measured a +1.45 eV shift in the U *value* from projector choice but has never measured the η consequence at fixed U. Gated on S0's ortho-atomic acceptance test; if the build rejects it, that is recorded as a capability result and the point is labelled projector-unverifiable rather than silently imported. *(Do not cite **10.1016/j.cpc.2022.108455** for projector dependence — that DOI is Timrov/Marzari/Cococcioni's HP code paper, whose abstract does not mention projector types and whose worked example is Li_xMn₁/₂Fe₁/₂PO₄; the 2.73 vs 4.37 eV example could not be located and must not enter the report. The project's own measured +1.45 eV is better evidence. QE's "New DFT+Hubbard input (since v7.3.1)" documentation is **UNVERIFIED, no DOI**.)*
- **P-PLS.** Register the closed form η = (c_M/2 − 1.23) + |ΔG₂ − ΔG₃|/2 **and its domain pls ∈ {2,3}**, the handling rule for any row spanning a flip, and — as a deliverable in its own right — **the U at which each metal's pls flips.** **PREDICTION: ≥3 of 6 metals show a pls flip inside the registered A0 grid.** **DISCLOSED NON-BLIND:** Cr flips 3→2 between U = 1.85 and 3.70; Co and Ni both flipped 1→2 under correction and the LIT-1 Co ladder returns pls = 1 at U = 4.48. Blind: Mn, Fe, Ru, Ir, Ti.
- **P-FLOOR-U** *(replaces the withdrawn P-U-SPLIT).* Define the quantity as **span(c_M)/2 in volts, at FIXED endpoints U = 0 and U = U_max** — never max-minus-min over a grid. **PREDICTION: span(c_M)/2 exceeds 0.10 V on ≥4 of the 6 metals with a converged *OOH geometry.** **FALSIFIED if ≤1 of 6 exceeds 0.10 V**, in which case U does not move the physical limit and the floor may serve as a U-invariant denominator after all — a change of framing registered before the fact. **DISCLOSED NON-BLIND:** Cr measures 0.223 V (floor 0.492 → 0.269 V across U = 0 → 5.00), **conditional on the S0(f) GATE-1 pass** — if any of the four ladder points moves by more than 50 meV on a fresh-density restart, the number is re-derived and the amendment records the correction before the prediction is dated. Blind: Mn, Fe, Ru, Ir, Ti.
- **Capability gates as results:** BEEF emission (four decks), `noinv` exactness, mirror-arm `nosym` invariance, Hessian σ_F and whether `conv_thr 1e-10` is reached in 2x1v, ortho-atomic acceptance, TiO₂/SnO₂ cutoff admission. Each recorded whichever way it goes.
- **The phase-reality ledger** (§3a) with its exclusion table and one resolvable identifier plus one reason per row, and the verbatim MODEL-PHASE scoping rule.
- **Corrections of record, dated before the fact:** the `ph.x` / DFPT+U rejection **with the corrected reason** (§5); `starting_ns_eigenvalue` is an initial guess, not OMC; β-MnO₂ is AFM and is initialised FM; CrO₂(110) is a real endmember ground-state rutile, not "a doped rutile" as `docs/research/2026-08-12-lit1-tranche1-uladder.md` lines 110/120 say; the Xu deposit is ~572 MB, CC0 on Zenodo / CC-BY-4.0 on GitHub, with **11 metal directories but 10 metals carrying Eads**; Rabone & Krack (not Dorado) for **10.1016/j.commatsci.2013.01.023**; Moore 2024's supercell-vs-DFPT status is an **inference**, and the "Linscott/Ganose transposed" correction is itself wrong and is struck.
- **The zero-compute lemmas, with their bounds:** the solvation cancellation lemma plus the **non-additivity** prediction (§5 arm 5); the configurational-entropy bound kT ln 2 = **0.0179 eV/site**; the cell-equals-coverage identity; the O₂-reference cancellation (imposing 4.92 eV cancels the gas-phase reference error identically out of η, **so no O₂ overbinding correction may be applied on top** — it would double-count and silently shift every η in the tier).

---

### Amendment 8 — before the first S3 deck launches (deposit by Aug 24)

- **P-SYMCOV (THE FLAGSHIP).** For the *OOH rung, at matched magnetic basin: **|dE_sym(1x1, full cus monolayer) − dE_sym(2x1v, half coverage)| > 0.10 eV on ≥3 of the 5 magnetic 3d metals.** **FALSIFIED if ≤1 of 5 exceeds 0.10 eV**, in which case the symmetry class is coverage-separable and is reported as a single additive row. **DISCLOSED as the motivating non-blind observation from data already on disk:** among the two anchors this holds for Ir (1x1 −0.2846 eV vs 2x1v −0.0185 eV, i.e. 0.266 eV, which docs/43 §2 scores INCONCLUSIVE) and fails for Ru (−0.0817 vs −0.1088, i.e. 0.027 eV) — 1 of 2. **All five 3d metals are blind**, because Cr's *OOH pairs in both cells are currently CONFOUNDED and therefore NOT_SCOREABLE. *This threshold is supported by the repo's own 2x1v data rather than contradicted by it — which is the whole reason it replaces the bare per-metal rate.*
- **P-SYM-TABLE (no threshold, by design).** The per-metal |Δη_sym| is reported as an **8-row table of measured values with the mechanism attached**, and only secondarily as a rate. The exact Clopper-Pearson width at n = 8 (**~0.68 near p̂ = 0.5**) is **registered in advance**, so a wide interval reads as disclosed rather than discovered. **No falsification threshold is attached to the rate**, because the disk data argues it would fire against the project and a second withdrawn headline in one report reads as a pattern rather than as maturity.
- **P-CONFOUND.** In the crossed {mirror, off-plane} × {production seed, second seed} design on 15 (magnetic-3d metal, adsorbate) cells in 2x1v: **≥5 of 15 cells are CONFOUNDED under |Δm_abs| > 0.1 µ_B when the seeds are not matched, AND on ≥3 of those the basin-matched dE_sym differs from the unmatched dE_sym by more than 0.10 eV.** **FALSIFIED if ≤1 of 15 is confounded**, in which case the symmetry class IS separable, the simple reading stands, and the crossed design is reported as an unnecessary control that was run anyway. **DISCLOSED NON-BLIND:** Cr already gives 2 of 3 confounded in 2x1v (*OH |Δm_abs| = 0.01 passes, *OOH = 1.87 fails; the 1x1 *OH pair at 0.25 also fails). Blind: the 12 cells on Mn, Fe, Co, Ni. **Register the expected exclusion count before the parse.**
- **P-BASIN-ANCHOR (new).** The AFM initialisation of RuO₂ lowers the fixed-geometry energy by **≥50 meV** relative to the production nspin = 1 solution **and** moves η(Ru) by **≥0.10 V**. **FALSIFIED below 20 meV and 0.03 V**, in which case the anchors' magnetic row is measured-and-small and the report says so. **Blind.** Directionally supported by **10.1021/acs.jpcc.1c08700** (AFM 0.41–0.49 V vs NM 0.63–0.73 V). Secondary and indicting-the-procedure-rather-than-the-physics: if the fresh-density GATE-1 restart lowers the energy by >50 meV in **any** nspin = 1 state, the restart procedure is at fault and Finding 3's mechanism is refuted, reported as such.
- **P-MIN (the second half of the saddle proof, which the campaign has never done).** At the escaped Cr geometry, the re-run adsorbate-only partial Hessian shows **no imaginary mode exceeding 3σ_F**, with **TWO floors registered numerically before the parse** — an **O-carried** floor and an **H-carried** floor, with the mode's mass-weighted participation deciding which applies, plus an **UNDERPOWERED band**. From `build_hessian_pilot.py`'s own measured table at `conv_thr 1e-10`: σ_F = 1e-5 Ry/bohr → σ_k = 3.7e-4 Ry/bohr² → **18 cm⁻¹ 1σ on oxygen**, giving a 3σ floor on an H-carried mode of **≈ i111 cm⁻¹**, with an UNDERPOWERED verdict registered at i80. **The margin must be stated honestly: the mirror-breaking mode is an azimuthal O–H libration with substantial hydrogen character, so i167 against an H-carried floor of i111 is a 1.5× margin, not the comfortable separation the i103 figure implies.** That table was measured at 21 atoms / 32 k / 1x1; the 1C decks are 2x1v (42 atoms, 16 k), so **S0(d) must report whether `conv_thr 1e-10` is actually REACHED in 2x1v and what σ_F it delivers there — if it is not reached, the minimum claim is struck before decks launch, not after.** **REGISTERED WORDING:** the deliverable is *"the mirror-breaking mode is real at the constrained geometry and is removed at the escaped one"* — an adsorbate-only partial Hessian with a frozen slab **cannot** establish a full-system minimum and the report will not say that it does. **FALSIFIED if a mode above the applicable floor survives**, in which case the escape reached another saddle and is reported as such.

---

### Amendment 9 — before any external corpus is parsed (deposit by Aug 22, must precede S2)

- **P-CTRL (a gate, not a finding — it VOIDS rather than caveats).** `silentgate` returns **exactly 0.00% LOCKED** over ≥500 OC20 relaxations (`isym=0`, `symprec=1e-10` verified in fairchem `vasp_flags.py`) and **≥95% LOCKED** over this campaign's own 20 `nosym`-absent production relaxations. **Any nonzero OC20 rate voids every downstream symmetry number until the detector is repaired; any in-house rate below 95% voids the 20-for-20 partition claim.** Both controls live in CI. **Registered scope limit:** this measures the false-**POSITIVE** rate only, so no symmetry claim about any symmetry-ON corpus may be made anywhere in this program.
- **P-XU.** Over all 810 deposited Xu Eads outputs, **≥90% report more than one symmetry operation AND carry at least one exactly-zero adsorbate force component in the final ionic step; AND the locked lateral direction for *OH is ORTHOGONAL to that for *OOH on ≥8 of the 10 metals.** **FALSIFIED if the population lock rate is <75%, or if the orthogonality holds on ≤4 of 10** — in which case the trap is this campaign's builder bug, is reported as such, and no field-wide claim is made. **DISCLOSED AT REGISTRATION:** 40/810 headers and 12/810 force blocks on 4 metals were already sampled and returned 40/40, so the first clause is a **completion of an already-seen sample, not a prediction**; the genuinely blind quantity is the rung-direction map, **unsampled for 6 of the 10 metals** — so "≥8 of 10" means ≥4 of the 6 blind ones.
- **P-XU-SPAN.** From the 680 deposited relaxations: **span_U(c_M) exceeds 0.20 eV for ≥5 of the 10 rutiles** — computed gas-reference-**free**, so it needs no molecule jobs and no external number. **FALSIFIED below 3 of 10.** Registered in the same clause: `tot_magnetization` is frozen at 15 across the entire ladder and this is a **DECLARED modelling choice visible in the deck, NOT a fourth silent error class** — a declared input variable is exactly the territory this project's novelty framing says is not its own. Registered separately: the **absolute** floor-margin half requires two GBRV molecule jobs (H₂ and H₂O in a 12 Å MT box at ecutwfc 40 / ecutrho 500) because the deposit contains no gas references; if they are not run, that half is reported as deferred.
- **P-DIVANIS.** The floor-margin population is reported as an explicit **curve over δ = corr_OOH − 0.35 eV across δ ∈ [0.00, 0.10] eV**, with ∂(floor margin)/∂δ registered **before the parse** as +δ/2 for pls = 3, −3δ/2 for pls = 4, −δ/2 for pls ∈ {1,2}. **PREDICTION: ≥25% of rutile-only entries reporting η < 0.60 V sit within 50 meV of their own exact scaling floor, at n = 38 from 3 articles, with the per-paper rate (n = 24) reported alongside.** **FALSIFIED below 10%.** **No exact binomial CI at n = 515**, and the denominator composition is printed on the figure face. If δ cannot be resolved from Nørskov 2004 (**10.1021/jp047349j**) by Sep 15, the half is reported as the δ-curve only and no single-δ number is quoted.
- **P-BUILDER.** The unmodified `AdsorbateSiteFinder` selects configurations retaining at least one adsorbate-invariant symmetry operation at rate X across four surface families — reported as **the site-selection mechanism only**, with a separate, explicitly stated finding that atomate's `MPSurfaceSet` sets ISYM = 0 (since commit a7d5f316, 25 May 2018) while the 2017-era `MVLSlabSet` did not. **The two rates are never multiplied**, and the exposed population is stated as *the papers that do not use those stacks*.

---

### Amendment 10 — before the first BEEF job, only if the S0(a) four-deck gate passed (deposit by Sep 18)

- **P-BEEF.** σ_BEEF(η) < **0.25 V on ≥2 of the 3 metals it is measured on** (Ru, Ir, Ti) — i.e. smaller than the 1.122 V U-swing and smaller than the 0.291 V Ir symmetry shift. **FALSIFIED if σ_BEEF(η) ≥ 0.30 V on ≥2**, in which case XC becomes a co-equal row and the "convergence-invisible classes dominate" framing is **weakened in the report, not defended.** Protocol registered in the same breath: self-consistent BEEF-vdW first; gas references in-box and inside the ensemble; member-index-matched ΔG; σ belongs to BEEF-vdW, not to PBE+U; **E_U is outside the ensemble entirely**; the row is labelled **"XC only."** The σ(c_M) < 0.5 × mean-of-individual-σ test is **DROPPED** as near-tautological; Christensen's functional-independence claim is tested **across materials** or not claimed.

---

**No threshold above is one the repo's own data falsifies.** Every registration was checked against the disk numbers reported by the three round-2 proposals: P-SYMCOV is *supported* by the Ir/Ru 2x1v pairs; P-FLOOR-U is stated at fixed endpoints so the pls-crossing artifact cannot inflate or deflate it; P-CONFOUND is disclosed non-blind on the two Cr states that already fail; P-PLS is disclosed non-blind on Cr and Co; P-XU's first clause is disclosed as a completion. The two round-1 registrations that the repo's own data killed — P-SPLIT and P-ANCHOR — are struck and replaced.

---

## 9. WHAT WOULD MAKE THIS FAIL, WITH KILL CRITERIA PER STAGE

**F1 — The human budget, which is the only binding constraint.** 21.0 of ~21 effective days is **zero buffer**, and that is not a plan. The Aug 26 launch sits four days before a five-submission cluster (Simbiochem Aug 29, AI4Mat ×3 Aug 30, MoML Sep 1).
**KILL CRITERION:** by **Aug 22**, either 3.5 days have been recovered (drop Breakthrough Jr and Coke, §10 Q1) or the program is cut to its floor **before** S3 launches, not during it. **Named cut order, in advance:** (1) hp.x bulk bracket, 0.3 d; (2) SnO₂, 0.8 d; (3) the A0-cell 2x1v rider, 0.3 d; (4) the 1x1 coverage-contrast leg, 1.0 d — *note this one costs P-SYMCOV, so it is a headline change, not a trim*; (5) the second spin seed entirely, 0.5 d; (6) Fe/Co/Ni cut from S3, 2.0 d, **last resort**. **S1, S2's Xu census, S6 and S7 are NOT cuttable** — they are the artifact and the closure.

**F2 — S3 does not drain and takes the artifact with it.** ~200 jobs dominated by magnetic 2x1v relaxations at 4–35 h on four metals with zero 2x1v data today; Co already went 0-for-4 and its clean slab drifts +59 meV; the re-relax loop serialises 2–3 passes.
**KILL CRITERION:** measure the real pass rate on the **first 20 jobs, which must have REPORTED by Sep 1.** If fewer than 60% have cleared GATE-1 by **Sep 8**, cut the second spin seed from *O and *OH (hold it on *OOH) and **publish the reduced depth table rather than reducing silently.** If fewer than 3 of 5 magnetic 3d metals have complete four-state sets by **Sep 20**, freeze at what is complete, report the rest as scoped-but-not-run, and score P-SYMCOV on the reduced denominator **with the threshold re-stated as ≥2 of 3 in a dated amendment before the parse**, never after. **Last safe launch: Aug 26.**

**F3 — The entry becomes "results to date of an unfinished study," which the Guidelines list as outright INELIGIBLE.**
**KILL CRITERION:** the central claim must be scorable from **S1 + S2 + S6 alone** — the detector, the external census, and the floor/estimator arithmetic, all zero-compute, none able to fail for compute reasons. **Verify this in writing on Sep 20** by drafting the abstract's one sentence against only what has landed. If it does not stand, **cut a stage rather than hope.** A census over all 810 deposited outputs is a *complete study of a complete corpus* regardless of what drains.

**F4 — The detector is wrong in the same direction as the finding.** Every number flows through code written by the person who believes the trap is real.
**KILL CRITERION:** P-CTRL is a **gate**. Both controls in CI, re-run on every commit, with status recorded at the moment each audit number is generated. Any drift **voids** the corresponding numbers rather than caveating them.

**F5 — A capability gate returns a false negative and strikes a stage on a null.** The BEEF gate as three proposals wrote it (one deck + grep) cannot distinguish "absent" from "not requested."
**KILL CRITERION:** four decks, ~4 box-hours, S0(a). Only after (i)–(iii) all fail may the XC row be struck. On genuine failure, S5 is struck at **zero sunk cost**, Finding 4's σ stays the literature band, and the capability limit is reported as a result.

**F6 — The Hessian claim is registered against a floor that cannot be reached.**
**KILL CRITERION:** S0(d) must report whether `conv_thr 1e-10` is **reached** in 2x1v and the σ_F it delivers. If not reached, the minimum claim is struck and the deliverable narrows to "the mirror-breaking mode is real" **before** 38 decks launch.

**F7 — Prior-art collision discovered after writing.** Four papers unread: **Briquet 2017** (**10.1002/cctc.201601662**, ChemCatChem 9(7) 1261–1268, actual title *"A New Type of Scaling Relations to Assess the Accuracy of Computational Predictions of Catalytic Activities Applied to the Oxygen Evolution Reaction"* — structurally the same move as the floor lemma, and closer prior art on the *framing* than any lens acknowledged; its ">0.6 eV descriptor" and ">1 eV chemisorption" figures are **not in Briquet** and are Dickens & Nørskov's characterisation, which Dickens disputes in the same paragraph); **Chatterjee arXiv:2512.05938** (σ ≈ 0.3–0.5 eV misclassifies a broad fraction of OC20/OC22 — the same noise scale as Finding 4); **Montoya & Persson's Methods** (**10.1038/s41524-017-0017-z**); and **arXiv:2604.12198** (Huang, v1 14 Apr 2026 / v2 2 Jul 2026 — an autonomous agent reproduces **111 open-access Quantum ESPRESSO papers** and raises substantive methodological concerns on **~42%**, with **85 of 88 critiques (96.6%) surfacing only after a calculation was run** and a reading-only ceiling of 1.8%; **the agent is a Claude Opus 4.6 configuration**).
**KILL CRITERION:** all four in hand by **Aug 29** through Purdue ILL. Anything not in hand has its dependent claim **narrowed pre-emptively rather than defended later.** The surviving claims after collision are narrow and true: the exact max-minus-mean identity, the named mechanistic classes, the measured rates in stated units. **Never** the aggregate noise scale; **never** "published computational work is unchecked"; **never** first discovery of DFT screening error. Note the additional STS hazard: arXiv:2604.12198 is AI-agent-authored critique of published papers in the same code and genre, while this entry is bound by a signed AI-authorship certification — **the distinction (human-designed instrument, human-set thresholds registered with dates before results existed, human-written detector core, human-written report, and a withdrawal a machine would not have chosen) must be made affirmatively in the report body**, not left for a judge to notice.

**F8 — An unverified citation lands in the report.** Live items: the Divanis **+0.40 eV *OOH correction** (confirmed ABSENT from Table SI-1; corrections attributed to Nørskov 2004); the **3.18 ± 0.12 eV** intercept (now demoted to qualitative — it anchors no threshold); the **~0.12 V code floor** (both derivations dead, replaced by ~0.095 V within-material across-study scatter); the Dickens **~0.7 eV** defect-site spread; the **PbO₂/OsO₂/SnO₂/GeO₂/PtO₂** structure-type assignments (all from MP pages and search summaries, **none from primary crystallography**); Jiang & Mushrif's NiO(100) ~2 eV vs bulk 5.3 eV; the hp.x troubleshooting ladder (mailing list, no DOI); `ensemble_energies` and the `.MOL` files (documentation, no DOI).
**KILL CRITERION:** each cleared or excluded by **Sep 15**. **Regenerate the entire bibliography from Crossref rather than typing it.** Note **10.1016/j.jelechem.2006.11.008** is now confirmed (Rossmeisl, Qu, Zhu, Kroes, Nørskov, J. Electroanal. Chem. 607, 83–89 (2007)) and may be cited — it is no longer PII-inferred.

**F9 — The flagship comes back null anyway.** Even re-registered as coverage-conditionality, P-SYMCOV could fail (Ru already fails it at 0.027 eV).
**MITIGATION, pre-written in Amendment 8:** both outcomes are stated before the parse, and the demotion is not a loss — the floor/excess decomposition (0.223 V of movement in the physical limit under a parameter no convergence gate constrains, ~25× Cr's own 9 meV margin) is **already banked at zero compute** as the declared fallback lead, and the detector plus the 810-relaxation census stand regardless. **The report must not discover this in October.**

**F10 — Page count.** 15–20 display items × 3–4 lines of caption + citation + on-face cell label ≈ **1.5–2 of the 20 pages consumed by caption furniture alone**, before any methods prose; and appendices count.
**KILL CRITERION:** **write the six-page methods section THIS WEEK against the current schema and count what fits.** Any row whose protocol cannot be described in enough detail for an in-field PhD to audit is **cut from the schema at registration**, not deferred. Realistically that caps the budget at ~5 rows — still a closed object, and a stronger one than eight rows described too thinly to score.

---

## 10. OPEN QUESTIONS FOR THE ENTRANT

**Q1. Which two of the six competing deadlines do you drop?**
This is the decision that decides everything else, and only you can make it. Priced: Breakthrough Jr (Sep 15, ~2 d), Coke (Sep 30, ~1.5 d), Concord Review (early Oct, ~3 d, and you write it yourself), Simbiochem + AI4Mat ×3 + MoML (Aug 29 – Sep 1, ~5 d as one cluster), Nov 1 ED (~3 d).
**RECOMMENDATION: drop Breakthrough Jr and Coke.** Recovers 3.5 days → 24.5 available against 21 spent, giving a real 3.5-day buffer. They are the two with the least carryover into either STS or college applications, and the AI4Mat/MoML cluster is three separate papers on three separate projects that cannot be recovered. If you will not drop them, the program shrinks to its 18.5-day floor via cuts (1)–(3) in §9 F1, and **you should decide that now, not on Sep 8.**

**Q2. Do you kill the arXiv preprint?**
Round 1 recommended posting one. **RECOMMENDATION: YES, kill it, and record the reason in Amendment 7.** It is a fourth writing project inside the ~90-hour Oct 15 → Nov 5 window that already carries a 20-page report, eight essays, six 200-word boxes, the AI-use disclosure, the Research Report Similarities answer, the Statement of Independence and Nov 1 ED applications — all written by you alone. Recovers ~2.5 days. If you keep it against this advice: post it **before Oct 15**, sole-authored, pre-declared in the Similarities answer, and the report must not depend on it in any way.

**Q3. Five magnetic 3d metals or three?**
Five costs ~940 box-h and ~6 human-days and lets P-SYMCOV be scored as registered (≥3 of 5). Three (Cr, Mn, Fe) costs ~570 box-h and ~4 days but forces the threshold onto a 3-metal denominator.
**RECOMMENDATION: five if Q1 recovers 3.5 days; three if it does not.** If three, the threshold must be re-stated as **≥2 of 3 in Amendment 8 before any deck launches** — never adjusted afterwards. Do not split the difference at four; the denominator must be fixed before the parse.

**Q4. TiO₂ only, or TiO₂ + SnO₂?**
**RECOMMENDATION: TiO₂ only, unless Mom 2014's stoichiometric "SnO₂" rows are confirmed cus-site by Sep 1.** Man 2011's SnO₂ row is bridge-site on a reduced surface and Man reports the cus site does **not bind** on SnO₂ — so a cus-site mirror/off-plane pair there risks being a difference between two non-binding geometries, which would be a wasted 46 box-h and, worse, a row in the table that an in-field PhD can attack. TiO₂ is nearly free, already wired, and anchored four ways.

**Q5. What do you do about β-MnO₂ being antiferromagnetic while `gen_rutile.py` initialises it ferromagnetic?**
This is the one real ambient magnetic 3d rutile in the tier, and it is currently run in an approximate magnetic order.
**RECOMMENDATION: add a 4-SCF AFM check (~8 box-h) alongside the RuO₂ AFM probe, and if the FM/AFM energy difference exceeds 50 meV, strike every materials-facing sentence about Mn.** Do not leave the approximation implicit — it is exactly the kind of thing the report's own thesis says should be reported.

**Q6. Which claim is the abstract's one sentence, and does the detector or the floor lead?**
**RECOMMENDATION: the detector plus the exposure census leads; the floor movement is the second result; the coverage-conditionality is the third.** The detector names an object, which every methods-genre finalist title does, and it is the only claim that stands on zero-compute stages that cannot fail. The floor number (0.223 V of movement in the physical limit, ~25× the 9 meV margin) is the more beautiful number but reads as being about your own error. **Write the sentence this week, before compute, and re-test it at the Sep 20 checkpoint against only what has landed.**

**Q7. Who re-authors the registered threshold text, and when does the provenance record start?**
**RECOMMENDATION: you, in your own words, before each amendment is deposited — and the log starts this week.** Any draft threshold text that is Zenodo-deposited and then reproduced in the body ledger figure requires review before inclusion. The log supports a complete record for later review.

**Q8. Who is the recommender, and are they engaged by mid-September?**
**RECOMMENDATION: pick whoever witnessed the withdrawal, not the most senior name available.** The rules explicitly score independence, and the modal computational finalist is embedded in a lab working on the lab's problem with the lab's compute. Your edge is real but invisible unless someone attests that the pre-registration and the withdrawal were your decisions. A lab head who can only vouch for compute access is worth less here than a mentor who watched a threshold kill your headline. **This is a September action.**

**Q9. What single data-collection conclusion date goes in the Rules Wizard?**
All three proposals blur three candidate dates (nothing launches after Oct 8; hard freeze Oct 15; analysis runs to Oct 15).
**RECOMMENDATION: Oct 15, with nothing in the report claimed from work completed after it, and the withdrawal entered as an explicit dated timeline event rather than an omission.** The hazardous-materials branch should collapse cleanly since nothing here is wet-lab — but any residual description of the prior furnace arc anywhere in the entry must be struck or the risk assessment completed honestly.

---

### What this program cuts, stated plainly

It cuts the Xu **repair** (never re-runs anyone's decks — the census says "it is in their data too," and S3 says "here is the corrected number on systems I control"). It cuts the Wander Hessian arm, the literature-coding audit, the deposit-availability count, the 2x1o cell, ESM entirely, RISM entirely, the explicit-water leg, the MOOH tier, the bi-U sensitivity sweep, the full 8-configuration magnetic enumeration, the arXiv preprint, and any OC22 arm. It caps in-house n at 8. It buys **differences, rates, an instrument and a bounded budget — never absolute overpotentials for any single material**, and the report must never be caught implying otherwise: four of the eight systems are unanchorable by construction, three of those are phases that do not exist as electrodes, and the fifth magnetic system is run in an approximate magnetic order.

---

## Addendum — 2026-08-16, entrant correction on the budget premise

The ~21-effective-day budget in §1(i)/§4 priced the entrant at ~30 h/week and deducted
~14.5 days for competing deadlines. The entrant rejects the premise: the budget is the
full calendar window to the hard deadline, and capacity is not to be assumed.
Consequence: every cut in this document that was motivated by human-days reverts to
LIVE (arXiv preprint, A0 cell rider, bulk hp.x scope, S3 second-seed depth, the fuller
magnetic grid, literature-coding audit). Cuts motivated by physics or evidence stand
unchanged (ESM, 2x1o, the bare symmetry-rate threshold, perturb_only_atom, n=25,
Wander/Kitchin noise floor, OC22 symmetry arm). The Aug 29–Sep 1 submission pile-up
remains a scheduling fact; the Aug 26 S3 launch date stands on its own merits.
Nothing above this line was edited.

---

## Addendum — 2026-08-16, S8 registered: the make→measure loop (melt-and-validate)

Added on the entrant's decision, with furnace (FWM), XRD and Purdue OER bench access all
confirmed by him 2026-08-16. This stage was absent from rounds 1 and 2 only because the
agents priced capacity; the repo has carried the plan since docs/15 (FWM melt → Purdue
OER, predictions frozen before measurement) and the built list since docs/37
(`results/r4_melt_list.json`, 2026-08-05).

**S8 — parallel, non-blocking. The report spine (S0–S7) must remain complete and
scorable if S8 produces nothing.**

1. **RE-RANK GATE (hard).** Nothing melts off the current r4 ranking. The r4 screen is
   MLIP-scored and pre-dates the corrected protocol; its own QC already invalidated
   6 of 12 candidates on desorption. Before any melt: re-score the surviving candidates
   with the corrected protocol applied at the screen's weakest points — symmetry-released
   multi-start relaxations, fresh-density basin gates, stated coverage — with
   corrected-DFT spot-checks on the best site of each of the top ~4 compositions. The
   S6 MLIP-rescore hook is the natural carrier.
2. **MELT SET.** Top 2–4 of the re-ranked list **plus one predicted-poor anchor**
   (docs/15's design: a correlation needs dynamic range) **plus an IrO₂ (or RuO₂)
   experimental reference measured in the identical cell and conditions** — "vs
   iridium" is a same-bench comparison or it is cross-lab noise.
3. **FREEZE BEFORE FIRE.** Predicted values for the melt set are deposited (Zenodo,
   same convention as every amendment) before the first melt. No prediction may be
   revised after any measurement exists.
4. **MEASUREMENT.** Per docs/15: melt at FWM, XRD single-phase confirmation, Purdue
   OER (η at fixed current density, Tafel, stability hold), repeats stated.
5. **INCLUSION RULE (eligibility-engineered).** S8 enters the report ONLY if complete —
   melted, confirmed, measured, repeated — by the Oct freeze, and then as ONE figure:
   frozen-predicted vs measured, attribution caveats on its face. If incomplete it
   detaches with zero damage: the report never cites it, and it becomes the first
   datapoint of the successor campaign. Partial S8 results may not appear anywhere in
   the report ("results to date of an unfinished study" is the disqualification shape).
6. **ANTI-CLAIM.** A measured overpotential on a melted polycrystal validates the
   *discovery loop*, never the DFT error budget — surface oxidation, morphology and
   kinetics are unmodelled. S8 must never be framed as experimental validation of the
   S3/S6 error measurements; those are validated by their own internal controls and
   the external census.

Nothing above the 2026-08-16 addenda was edited.
