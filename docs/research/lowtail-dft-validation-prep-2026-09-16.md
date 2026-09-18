# Low-tail Cr reconstruction: DFT at MACE coordinates and prepared relaxations — 2026-09-16

Historical preparation retained. The completed-panel population, repaired canonical parser, refreshed cost and September 18 launch supersede the pending-job and parser-workaround statements below. See [September 18 refresh](lowtail-dft-validation-refresh-2026-09-18.md) and [primary launch](lowtail-primary-launch-2026-09-18.md).

Only one banked DFT single point sits at a reconstructed MACE Cr endpoint: Ni31Cr29Cu5Mn35 seed 1/site 0 *O. There, Cr16 is lifted 0.845 Å, Cr16–O72 is 1.591 Å and the axial Cr16–O40 distance is 2.693 Å. At first order, that single point is ambiguous about whether the reconstruction persists:

- **Forces on Cr16 and O72.** DFT pushes Cr16 away from the slab (+1.066 eV/Å atomic, +1.067 ortho) and O72 toward it (−1.090 / −1.109). Together these compress the short Cr=O contact (bond stretch −2.156 / −2.176). The Cr16–O72 unit carries a net normal force of only −0.024 / −0.042 eV/Å, slightly toward the slab.
- **Axial contact.** O40 is pushed toward Cr16 (0.673 / 0.716 eV/Å) and the Cr16–O72 unit is pushed slightly toward O40 (+0.028 / +0.045), so the mass-weighted axial gap would close at first order. O40 carries a push of similar size toward Cr16 in the clean slab (0.651 / 0.928), where that contact is intact at 1.711 Å, so the force cannot be credited to re-forming the broken contact.

These are gradients at fixed MACE coordinates, not a relaxation. They neither establish nor exclude a restoring tendency.

Relaxation decks that decide the question were prepared, priced and given a tested readout for the three decisive sites. They were not submitted. Preparing them showed that the existing HEA scorer accepts none of the 43 banked HEA outputs as it stands. The readout therefore reads outputs with two recorded input corrections, and with those it matches every banked readout (43/43).

## (a) DFT vs MACE-MPA-0 at identical coordinates

**Population.** The population is every pw.x output under `runs/hea`: 43 outputs. Each takes the status its own readout recorded, and 31 are ACCEPTED (winner, pilot, follow-up, numerical, IEEE-replacement and sensitivity readouts). All 31 are used, and each passed four checks:

- the recorded output sha256 matches;
- one converged SCF and one complete total-force block are present;
- no failure marker from `src/dft/hea_followup_qc.py` appears;
- coordinates, cell, elements and FixAtoms mask equal a retained MACE endpoint exactly.

Twelve outputs are excluded with the reason on record. Eleven are REJECTED:

- two follow-up SCF time-limit nonconvergences;
- two numerical recovery nonconvergences;
- four capped probes;
- the IEEE-flagged atomic tight builder;
- the IEEE-flagged ortho smearing pull and its IEEE-reproducing diagnostic.

The twelfth is the setup-only `hi__…smearing_init`, which has no SCF. No output is unidentified.

Forces come only from the block after `Forces acting on atoms (cartesian axes, Ry/au)`. Per-term contribution blocks are counted (0 here) and never read. The winner *O parse reproduces the stored force audit to 1e-12 eV/Å.

**MACE side.** MACE was re-evaluated one structure at a time with checkpoint sha256 `75428afe…4fb638`, float64, on CPU. It reproduces the stored census energies of all 8 geometries with |ΔE| = 0 eV:

- the winner slab, OH, O and OOH;
- the seed-0 OOH builder and pull2.10 endpoints;
- H2O and H2.

The pull2.10 replay coordinates equal the census-selected seed-0 OOH. The builder replay energy equals the census start record to 1.1e-13 eV.

**Historical winner chain, Ni31Cr29Cu5Mn35 seed 1/site 0 (site Cr16, axial O40, appended O72).**

- Forces are in eV/Å.
- Lift is measured from the same decoration's census clean slab.
- Bond stretch is (F_O72 − F_Cr16)·u, with u from Cr to O; a negative value shortens the contact.
- Axial stretch is the same two-atom construction for Cr16–O40.

| State | Projector | DFT free fmax | MACE free fmax | Cr16 lift | Cr16–O72 | Cr16–O40 | DFT F_z Cr16 | MACE F_z Cr16 | DFT F_z O72 | DFT bond stretch | DFT pair F_z | DFT F_z O40 | DFT axial stretch | Cr16 rank / free atoms | Largest DFT free force |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| slab | atomic | 1.562 | 0.045 | reference | n/a | 1.711 | −0.674 | +0.043 | n/a | n/a | n/a | +0.646 | −1.338 | 9 / 44 | O71 1.562 |
| slab | ortho | 1.530 | 0.045 | reference | n/a | 1.711 | −0.870 | +0.043 | n/a | n/a | n/a | +0.923 | −1.812 | 6 / 44 | O71 1.530 |
| OH | atomic | 1.660 | 0.047 | +0.350 | 1.864 | 2.036 | +0.084 | +0.016 | −0.483 | −0.575 | −0.398 | −0.176 | +0.259 | 39 / 46 | O71 1.660 |
| OH | ortho | 1.588 | 0.047 | +0.350 | 1.864 | 2.036 | +0.176 | +0.016 | −0.593 | −0.777 | −0.417 | −0.059 | +0.234 | 40 / 46 | O71 1.588 |
| O | atomic | 1.583 | 0.038 | +0.845 | 1.591 | 2.693 | +1.066 | −0.023 | −1.090 | −2.156 | −0.024 | +0.633 | +0.391 | 7 / 45 | O71 1.583 |
| O | ortho | 1.519 | 0.038 | +0.845 | 1.591 | 2.693 | +1.067 | −0.023 | −1.109 | −2.176 | −0.042 | +0.679 | +0.349 | 8 / 45 | O71 1.519 |
| OOH | atomic | 1.566 | 0.048 | +0.194 | 1.971 | 1.878 | +0.094 | +0.013 | +0.159 | +0.025 | +0.253 | −0.579 | +0.674 | 41 / 47 | O71 1.566 |
| OOH | ortho | 1.505 | 0.048 | +0.194 | 1.971 | 1.878 | +0.039 | +0.013 | +0.270 | +0.187 | +0.309 | −0.517 | +0.558 | 44 / 47 | O71 1.505 |

The MACE geometry is far from a DFT stationary point throughout the slab, not only at the site. In every state the largest DFT free force (1.505–1.660 eV/Å) sits on top-layer bridging O71, including the clean slab, which has no adsorbate. MACE forces at its own endpoints are relaxation residuals below 0.05 eV/Å, so DFT−MACE force metrics mostly measure the DFT force.

Against that background, *O is the only adsorbate state with a large force on the site Cr: rank 7–8 of 45 free atoms, against 39–44 in OH and OOH. That *O force is the Cr=O72 compression. In the clean slab, which has no appended O, Cr16 also ranks high (6–9 of 44), pushed toward the slab while O40 is pushed up. DFT therefore favours a shorter axial Cr–O than MACE's 1.711 Å there. Both projectors give the same signs everywhere.

**The axial contact as two bodies.** The two-atom axial stretch mixes two forces: the Cr=O72 compression acting on Cr16, and the force on O40. Separating them treats O40 and the site unit (Cr16, plus O72 when it is bonded) as two bodies along u from Cr16 to O40 (u_z ≈ −1). The relative acceleration is F_O40·u/m_O40 − F_unit·u/m_unit, in eV Å⁻¹ amu⁻¹; a negative value closes the gap. Masses come from `ase.data`.

| State | Projector | Site unit | Cr16–O40 | Two-atom axial stretch | Cr16 away from O40 | O40 toward Cr16 | Unit toward O40 | Relative acceleration | DFT gap, first order | MACE relative acceleration |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| slab | atomic | Cr16 | 1.711 | −1.338 | −0.686 | +0.651 | +0.686 | −0.0539 | closing | +0.0026 |
| slab | ortho | Cr16 | 1.711 | −1.812 | −0.883 | +0.928 | +0.883 | −0.0750 | closing | +0.0026 |
| OH | atomic | Cr16+O72 | 2.036 | +0.259 | +0.087 | −0.172 | +0.396 | +0.0049 | opening | −0.0001 |
| OH | ortho | Cr16+O72 | 2.036 | +0.234 | +0.178 | −0.056 | +0.415 | −0.0026 | closing | −0.0001 |
| O | atomic | Cr16+O72 | 2.693 | +0.391 | +1.064 | +0.673 | +0.028 | −0.0425 | closing | +0.0019 |
| O | ortho | Cr16+O72 | 2.693 | +0.349 | +1.065 | +0.716 | +0.045 | −0.0454 | closing | +0.0019 |
| OOH | atomic | Cr16+O72 | 1.878 | +0.674 | +0.095 | −0.579 | −0.251 | +0.0399 | opening | −0.0004 |
| OOH | ortho | Cr16+O72 | 1.878 | +0.558 | +0.041 | −0.517 | −0.308 | +0.0368 | opening | −0.0004 |

At the lifted *O geometry, the positive two-atom stretch (+0.391 / +0.349) comes entirely from the Cr=O72 compression force on Cr16 (1.064 / 1.065 away from O40). O40 itself is pushed toward Cr16, and the unit is pushed slightly toward O40, so the mass-weighted gap closes (−0.0425 / −0.0454).

O40 is pushed toward Cr16 even harder in the clean slab (0.651 / 0.928), where the contact is intact. The push on O40 therefore belongs to the slab-wide residual field at MACE coordinates as much as to the broken contact. The single point is ambiguous about the axial contact: it neither supports nor argues against its re-forming.

**Seed-0 OOH endpoints (no Cr–O bond).** Both geometries hold a desorbed fragment. For builder, the nearest metal to O72 is Cr16 at 4.557 Å; for pull2.10 it is Ni18 at 3.400 Å. They test pair energies, not the reconstruction.

| Seed-0 OOH endpoint | Projector | Accepted realizations | DFT free fmax | MACE free fmax | DFT F_z Cr16 |
|---|---|---:|---:|---:|---:|
| builder | atomic | 5 | 1.443 to 1.641 | 0.049 | −0.454 to −0.332 |
| builder | ortho | 7 | 1.446 to 1.511 | 0.049 | −0.983 to −0.613 |
| pull2.10 | atomic | 5 | 1.412 to 1.673 | 0.037 | −0.880 to −0.467 |
| pull2.10 | ortho | 6 | 1.412 to 1.591 | 0.037 | −1.135 to −0.720 |

Ten matched pairs can be formed:

- nine share series, projector and spin start or setting;
- the tenth is the replacement pair that the atomic-replacement readout names.

Across the ten pairs:

- DFT E(pull2.10) − E(builder) ranges from −1.9581 to −2.4392 eV; MACE gives −2.2818 eV.
- DFT − MACE ranges from −0.1574 eV (atomic, metal-alternating start) to +0.3237 eV (atomic, metal-alternating fragment start).
- The sign agrees in all 10 pairs.
- The six follow-up gaps reproduce the banked values to 1e-9 eV.
- Across spin starts the gap spans 0.4811 eV; tightening SCF, the wavefunction cutoff or the density cutoff moves it by at most 0.0004 eV.

Three accepted realizations have no accepted partner and enter no pair: ortho baseline builder, ortho metal-alternating pull and ortho smearing builder.

**Winner-chain electronic energies.** These use the banked DFT H2/H2O references (`runs/Cr_slab`) and the census MACE references. No ZPE/TS correction is added; they are not free energies or overpotentials.

| Projector | Quantity (eV) | DFT | MACE | DFT − MACE |
|---|---|---:|---:|---:|
| atomic | ΔE_ads(OH) | 1.6478 | 1.3200 | +0.3278 |
| atomic | ΔE_ads(O) | 3.2491 | 3.1190 | +0.1300 |
| atomic | ΔE_ads(OOH) | 4.4183 | 4.0702 | +0.3481 |
| atomic | O − OH | 1.6013 | 1.7990 | −0.1977 |
| atomic | OOH − O | 1.1692 | 0.9512 | +0.2181 |
| ortho | ΔE_ads(OH) | 1.6951 | 1.3200 | +0.3751 |
| ortho | ΔE_ads(O) | 3.3542 | 3.1190 | +0.2351 |
| ortho | ΔE_ads(OOH) | 4.4519 | 4.0702 | +0.3817 |
| ortho | O − OH | 1.6590 | 1.7990 | −0.1400 |
| ortho | OOH − O | 1.0977 | 0.9512 | +0.1466 |

The DFT values equal the banked winner readout exactly. At identical coordinates, DFT places the lifted *O 0.1400–0.1977 eV lower relative to *OH than MACE does, and *OOH 0.1466–0.2181 eV higher relative to *O. Each fixed geometry also carries its own unknown DFT relaxation energy, so these differences are not relaxed step energies.

**What single points can and cannot establish.** A single point gives the DFT energy and the local energy gradient at one configuration. It cannot show whether Cr returns, stays or lifts further after relaxation:

- The site forces are coupled to 44–47 other free atoms.
- Every atom sits in a large residual-force field.
- The Cr16 force is dominated by the Cr=O72 compression.
- The Cr16–O72 unit's net normal force is near zero.
- The first-order closing of the axial gap rests on a force that O40 also carries in the intact clean slab.

A single point does not locate the DFT minimum, does not rule a nearby unlifted basin in or out, and does not decide the energy order between basins. Magnetic state is sampled, not established: across spin starts, pair energies span 0.4811 eV. Persistence of the reconstruction needs relaxations from both basins.

**Pending single points already approved.** Four decks in the approved pilot manifest (`runs/m_research_2026-09-16_hea_pilot.txt`) have coordinates identical to census reconstructed *O endpoints:

- Fe25Co25Ni25Cr25 seed 2/site 0 *O (Cr lift 0.799 Å), atomic and ortho;
- Ni31Cr29Cu5Mn35 seed 0/site 0 *O (Cr lift 0.950 Å), atomic and ortho.

No local output exists. A read-only scheduler snapshot requested 2026-09-17 03:18:08 UTC shows:

- **20781971_1 FAILED, exit 10.** This task is `hea/branch_panel/equiatomic_pull2.10__atomic`. Its receipt says REJECTED, "SCF not complete/clean: ['IEEE_INVALID_FLAG']": the SCF converged in 52 iterations in a 3154 s process, and the exit note lists IEEE_INVALID_FLAG.
- **20781971_2 and 20781972_1 RUNNING.**
- **All other tasks PENDING.**

When these four single points are accepted, adding their geometries to `lt_zero_compute.py` extends (a) to two more reconstructed sites.

## (b) Prepared relaxation decks (not submitted)

**Sites and starts.** Every value in this section comes from `results/lowtail_dft_2026-09-16/deck_plan.json` and `operating_decisions.json`.

| Site | Census result (sha256) | Cr | Axial O | Recon start: lift / Cr–O / Cr–O(axial) | Unrecon start: Cr–O / nearest other atom | Fixed atoms |
|---|---|---:|---:|---|---|---:|
| Cu8Cr23Mn35Co34 s20/site 2 | `mpa0_ext__Cu8Cr23Mn35Co34__s18-20_result.json` (412b4170…d88b7a) | 18 | 42 | 0.791 / 1.593 / 2.705 | 1.635 / 2.198 | 28 |
| Ni31Cr29Cu5Mn35 s1/site 0 | `mpa0__Ni31Cr29Cu5Mn35_result.json` (5ba521d6…ddf950) | 16 | 40 | 0.845 / 1.591 / 2.693 | 1.635 / 2.138 | 28 |
| Fe25Co25Ni25Cr25 s2/site 0 | `mpa0__Fe25Co25Ni25Cr25_result.json` (dd596f1b…ea29a) | 16 | 40 | 0.799 / 1.589 / 2.758 | 1.635 / 2.196 | 28 |

Each site gets three decks:

- `slab`: the census relaxed clean slab;
- `O_recon`: the census selected *O endpoint, unchanged;
- `O_unrecon`: the census clean slab, unchanged, plus one O 1.635 Å directly above the site Cr (inside the specified 1.62–1.65 Å range).

`src/dft/hea_deck.py` `render_deck` renders every deck with the docs/92 settings of record:

- MP U set: Cr 3.7, Mn 3.9, Fe 5.3, Co 3.32, Ni 6.2; no U on Cu;
- ferromagnetic starts of record;
- 80/640 Ry, MV 0.01 Ry, conv_thr 1e-6;
- local-TF mixing at beta 0.3;
- k-mesh 4 2 1 with nosym/noinv and nk 8;
- electron_maxstep 300, max_seconds 165000;
- census FixAtoms as `if_pos 0 0 0`, with coordinates that re-parse exactly.

The deck is then changed in one asserted line, `calculation = 'scf'` → `'relax'`, so the template's `&IONS bfgs`, `forc_conv_thr = 2.0d-3` and `nstep = 200` apply. The Fe25 `slab` and `O_recon` decks differ from the approved pilot decks only in `calculation` and `prefix`. Regenerating the plan left all 18 deck files byte-identical (`lt_decks.py --check`: CHECK OK).

There are two manifests:

- `runs/hea/lowtail_validation_2026-09-16/m_lowtail_validation_2026-09-16.txt` holds the 9 atomic decks (primary).
- `m_lowtail_validation_projector_control_2026-09-16.txt` holds the 9 ortho decks.

Both begin with the required PREPARED header and carry a "Not licensed for submission" line, which `anvil/47_submit_a0.sh:57` refuses. Both pass the `hea_deck.check_manifest_text` submitter checks and print the kill rule and per-deck ceiling walls. The approved research batch runner is fixed-geometry only (`src/dft/research_batch.py:3`), so a relaxation route has to be named at approval. `anvil/46_a0.slurm` (48 h, `bfgs converged` accounting) is the existing relax-capable one.

**MACE from the same starts** (census protocol: fmax 0.05, 300 steps, FixAtoms). Both starts reach the lifted basin at all three sites. The unreconstructed starts converge in 33–37 BFGS steps and end 0.0012–0.0019 eV above the census *O. MACE therefore predicts no local unlifted minimum at the deck height; the DFT decks test that prediction.

| Site | Start | MACE basin | Cr lift | Cr–O(axial) | Cr–O(ads) | Steps | E − E(census *O), eV |
|---|---|---|---:|---:|---:|---:|---:|
| Cu8 s20/2 | O_recon | RECONSTRUCTED | 0.791 | 2.705 | 1.593 | 0 | +0.0000 |
| Cu8 s20/2 | O_unrecon | RECONSTRUCTED | 0.783 | 2.696 | 1.593 | 33 | +0.0019 |
| Ni31 s1/0 | O_recon | RECONSTRUCTED | 0.845 | 2.693 | 1.591 | 0 | +0.0000 |
| Ni31 s1/0 | O_unrecon | RECONSTRUCTED | 0.843 | 2.689 | 1.591 | 37 | +0.0012 |
| Fe25 s2/0 | O_recon | RECONSTRUCTED | 0.799 | 2.758 | 1.589 | 0 | +0.0000 |
| Fe25 s2/0 | O_unrecon | RECONSTRUCTED | 0.792 | 2.747 | 1.589 | 36 | +0.0014 |

**Operating decisions, fixed before any output** (`results/lowtail_dft_2026-09-16/operating_decisions.json`, revision 2). docs/43 registers no threshold for this question; A6.6 at `docs/43-prereg-week1-factorial.md:1283-1288` registers fixed-geometry SCFs and zero relaxations. The authority for relaxations is `docs/research/research-decisions-2026-09-16.md:55`. Revision 2 is still earlier than any relaxation output. It adds the lift-definition record, the kill rule and the 3-D displacement flag, and changes no threshold value. The code reads each value from its source file.

| Value | Setting | Source |
|---|---:|---|
| Lift threshold | 0.50 Å | Value of `src/hea_oer/site_integrity.py:84`. There it bounds the largest free-slab-atom 3-D displacement with a strict ">" (`:278`, docs/91:58); here it is re-used for the site-Cr z-lift with ≥. |
| Axial break | 2.1758 Å | Midpoint of the largest clean (1.804 Å) and smallest *O (2.547 Å) Cr–O(axial) distance over the four census Cr minima |
| O off site | nearest metal is not the site Cr, or distance ≥ 3.00 Å | `src/hea_oer/data.py:20` |
| Magnetization flag | 0.5 μB | `src/dft/hea_panel_readout.py:68` |
| Energy-order margin | 0.4811 eV | Spread of accepted matched pull2.10 − builder gaps across spin starts (follow-up readout) |
| Kill rule | stop once iteration 127 begins, or the leg wall exceeds its ceiling | `docs/research/research-decisions-2026-09-16.md:81` (HEA-4); 126 = `runs/hea/COST_MODEL.md:18` = `max_iterations` of all 22 approved HEA jobs |

The four census Cr minima are Ni31 s1/0, Fe25 s2/0, Cu26 s5/2 and Cu8 s20/2:

| Measure | Ni31 s1/0 | Fe25 s2/0 | Cu26 s5/2 | Cu8 s20/2 |
|---|---:|---:|---:|---:|
| Clean axial distance (Å) | 1.711 | 1.726 | 1.804 | 1.798 |
| *O axial distance (Å) | 2.693 | 2.758 | 2.547 | 2.705 |
| Cr lift / 3-D displacement (Å) | 0.845 / 0.847 | 0.799 / 0.799 | 0.592 / 0.597 | 0.791 / 0.793 |

The two lift definitions agree on all four minima. The axial-O indices match `endpoint_audit.json` in all four.

**Kill rule for relaxation legs.** HEA-4 is carried over unchanged in substance:

- `electron_maxstep = 300` stays in every deck.
- A leg stops once any SCF of any ionic step begins iteration 127, the `iteration #` maximum the supervisor in `src/dft/research_batch.py` watches.
- A relaxation is one pw.x process, so the per-deck SCF ceiling becomes a per-leg ceiling: the deck's unrounded ceiling wall, rounded up to the next second. That is 54236–58347 s for the atomic decks and 95865–103140 s for the ortho decks.
- A stopped leg is recorded KILLED, scratch is preserved, and there is no automatic restart. A stopped leg yields no energy, geometry or basin. Restarting from the last ionic geometry needs its own dated decision.
- The readout applies both limits to every output, whatever route ran it: an otherwise converged leg that breaks either limit is KILL_RULE_EXCEEDED.

**Readout** (`src/s2/lowtail_dft/lt_readout.py`). The existing HEA scorer `hea_panel_readout.parse_out` cannot be used unmodified on real pw.x outputs. Run on the 43 banked HEA outputs (`results/lowtail_dft_2026-09-16/scorer_crosscheck.json`), it gives:

| Scorer version | Result on the 43 banked outputs |
|---|---|
| Unmodified | Stops (Fatal) on 12 outputs and REJECTS the other 31; accepts none |
| Wall parser corrected only | REJECTS all 43 |
| Both corrections | 31 CONVERGED, 8 NOT CONVERGED, 4 REJECTED; matches the recorded readout status for 43/43 |

The two failures have separate causes:

- **Wall tokens.** Its wall parser requires a seconds field, but pw.x prints `1h 5m` for runs of an hour or more.
- **gfortran exit note.** Its severe pattern `floating.point exception` matches the note every gfortran-built pw.x prints at exit: `Note: The following floating-point exceptions are signalling: IEEE_UNDERFLOW_FLAG IEEE_DENORMAL`. That contradicts its own rule that ordinary underflow/denormal notices are not fatal. Thirty-nine of the 43 REJECTIONS come from that note alone.

With both corrections applied, the 4 REJECTED are the three IEEE_INVALID outputs and the setup-only output. The readout therefore runs the unchanged scorer with two recorded input corrections:

1. the pw.x clock parser replaces its wall-token helper during the call;
2. the scorer reads a temporary copy of the output in which only the words "floating-point exceptions" of those note lines are replaced.

IEEE_INVALID, DIVIDE_BY_ZERO and OVERFLOW flags listed in the note still reject, as does any other floating-point exception message. Each leg records both the unmodified and the corrected status.

A leg is accepted only if all of the following hold:

1. The corrected scorer returns CONVERGED with `allow_relax=True`.
2. The kill rule holds.
3. One final-coordinate block exists, its elements match the deck, and the fixed atoms are unmoved to within 1e-6 Å.
4. The final free force components are within forc_conv_thr.

Basin assignment uses the Cr lift relative to the DFT-relaxed clean slab of the same site and projector. When that slab leg is not accepted, the census clean slab is used and the leg is flagged REFERENCE_MACE_SLAB. The assignment also uses Cr–O(axial) and Cr–O(ads). The 3-D displacement of the site Cr is printed beside the lift, with LIFT_DEFINITIONS_DISAGREE when the two definitions differ.

Basin labels:

- **RECONSTRUCTED:** lift ≥ 0.50 Å and axial distance ≥ 2.1758 Å.
- **UNRECONSTRUCTED:** both below.
- **MIXED_UNASSIGNED:** exactly one criterion met.
- **O_OFF_SITE:** as defined in the operating-decisions table.

Site outcomes:

- **RECONSTRUCTION_SUPPORTED:** both *O starts end reconstructed.
- **RECONSTRUCTION_NOT_SUPPORTED:** both end unreconstructed.
- **TWO_LOCAL_BASINS:** each start stays in its own basin. The energy order is LIFTED_LOWER or UNLIFTED_LOWER only when |E_recon − E_unrecon| > 0.4811 eV, otherwise ORDER_WITHIN_SPIN_START_SPREAD. MAGNETIZATION_DIFFERS is flagged when |ΔM| ≥ 0.5 μB.
- **BASINS_CROSSED:** each start ends in the other basin.
- **UNDECIDED:** anything else, with the leg status named.

Run against the prepared plan with no outputs, the readout reports 18 PENDING legs and exits 3.

**Cost.** Pricing uses measured anchors from the accepted HEA single points at settings of record:

- **Per SCF iteration.** 6.994e-5 s (atomic) and 6.971e-5 s (ortho) per Å³ × KS state, or 50.3–54.1 s and 50.2–54.0 s on these decks.
- **Per force evaluation.** 7.713e-5 s (atomic) and 115.424e-5 s (ortho) per Å³ × KS state, or 55.5–59.7 s and 830.4–893.6 s on these decks.
- **Force/iteration ratio.** The median ratio of force wall to iteration wall is 1.10 (atomic) and 16.56 (ortho), so ortho forces dominate every ionic step.
- **First-SCF iterations.** Ferromagnetic from-scratch first SCFs took 36, 37, 37, 40, 53 and 87 iterations with the atomic projector (p50 37, p90 87), and 37, 38, 38, 38 and 78 with ortho (p50 38, p90 78).

Ionic steps come from banked nspin = 2 slab relaxations outside `runs/hea`. Every surveyed and excluded output and its input is hashed in `results/lowtail_dft_2026-09-16/relax_survey_manifest.json` (102 used, 11 excluded because no force block was reached). The survey is restricted to starts whose initial free fmax lies within a factor of two of the (a) DFT fmax at the matching winner state (1.519–1.583 eV/Å).

Within that band:

- Between 49 and 51 relaxations fall in the band, and all are BFGS-converged.
- Five to six carry IEEE_INVALID_FLAG, which the scorer rejects: `runs/probe/Cr_cellsym/s0_O__2x1o_off`, `s0_O__2x1v_mir` and `s0_OOH__2x1o_mir`; `runs/s3/Fe/s0_O__2x1v_mir` and `s0_OH__2x1v_mir`; and, in the *O atomic band only, `runs/s3/Fe/s0_OOH__2x1v_off`.
- Step statistics use the 44–45 scorer-CONVERGED members: SCF cycles p50 20, p90 50, maximum 82; later-step iterations p50 14, p90 19.
- These statistics are identical with or without the rejected members.

Across all 102 surveyed relaxations the corrected scorer returns 86 CONVERGED, 14 REJECTED, 1 NOT CONVERGED and 1 PENDING, and IEEE_INVALID appears in 14. That is the rejection risk each relaxation leg carries. Among the 43 banked HEA single-point outputs, 3 carry IEEE_INVALID, and so does the first finished task of the new panel.

The cost formulas are:

- **Planning:** t_init + (I_first + (S−1)·I_sub)·t_iter + S·(t_force + t_rest).
- **Ceiling:** max(3 × planning, the same formula at p90), with the ceiling factor of `runs/hea/COST_MODEL.md`.
- **Memory:** scaled from the printed dynamical-RAM estimate and the scheduler MaxRSS of the accepted winner tasks.

| Manifest | Decks | Planning core-h | Ceiling core-h | Per deck, planning | Per deck, ceiling | Wall h, planning / ceiling | Leg wall ceiling s | Memory GB, printed basis / GiB MaxRSS basis |
|---|---:|---:|---:|---:|---:|---|---|---|
| primary (atomic) | 9 | 5443.2 | 17925.0 | 585.6 to 629.9 | 1928.4 to 2074.5 | 4.58–4.92 / 15.07–16.21 | 54236–58347 | 103.4–111.3 / 113.5–122.1 |
| projector control (ortho) | 9 | 10561.7 | 31685.0 | 1136.2 to 1222.4 | 3408.5 to 3667.2 | 8.88–9.55 / 26.63–28.65 | 95865–103140 | 103.4–111.3 / 116.7–125.6 |

Every deck fits the 237 GB node, and every ceiling wall is below the decks' 165000 s max_seconds and the 48 h route. Per-deck values, ceiling seconds and md5s are printed in both manifests. The primary set alone decides the question at the atomic projector.

## Limits

- One banked site carries a lifted Cr in DFT. Its forces are local gradients at MACE coordinates, in a slab whose residual DFT force field is large everywhere, and they are ambiguous about persistence at first order.
- The relaxation step statistics come from single-metal slabs with at most 26 free atoms; these decks have 44–45. Multi-3d-species nspin = 2 relaxations have no banked precedent. The SCF iteration and nonconvergence risks of `runs/hea/COST_MODEL.md` §5, the kill rule and the IEEE_INVALID rejection rate (14 of 102 surveyed relaxations) apply to every leg.
- Basins are assigned under DFT+U with ferromagnetic starts. A different magnetic solution can change geometry and energy order, and a basin reached from one start does not exclude others.
- No overpotential, melt ranking or experimental surface chemistry follows from these calculations.

## Files

- Code: `src/s2/lowtail_dft/`: `lt_qe.py`, `lt_geometry.py`, `lt_sources.py`, `lt_mace.py`, `lt_zero_compute.py`, `lt_decisions.py`, `lt_cost.py`, `lt_decks.py`, `lt_readout.py`, `lt_anvil_snapshot.py`, `lt_report.py`, `lt_common.py`.
- Tests: `tests/s2/test_lowtail_{qe,geometry,sources,cost,decks,zero_compute,readout}.py`.
- Results in `results/lowtail_dft_2026-09-16/`:
  - `zero_compute/zero_compute_readout.json` and `zero_compute/input_manifest.json`;
  - `operating_decisions.json`, `deck_plan.json`, `relax_survey_manifest.json` and `mace_start_check.json`;
  - `scorer_crosscheck.json`;
  - `anvil_queue_snapshot.json` (02:36:15 UTC) and `anvil_queue_snapshot_r2.json` (03:18:08 UTC);
  - `tests_junit.xml`.
- Decks and manifests: `runs/hea/lowtail_validation_2026-09-16/`.
