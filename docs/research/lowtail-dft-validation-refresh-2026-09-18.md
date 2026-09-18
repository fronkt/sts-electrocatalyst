# Low-tail Cr DFT evidence refresh — 2026-09-18

The completed HEA batch extends the fixed-coordinate force comparison from one reconstructed Cr site to three. At all five accepted site/projector realizations, DFT pushes the short Cr–O contact to compress. The axial-contact response differs between sites, and large forces remain elsewhere in the slab. These calculations therefore support proceeding to the prepared paired-start DFT relaxations; they do not establish that a reconstructed DFT minimum exists or select a census winner.

This is an additive refresh of [the September 16 preparation](lowtail-dft-validation-prep-2026-09-16.md). Its decks, source results, operating decisions and original cost estimates remain preserved. The final scientific artifact for this refresh is [zero_compute_reviewed/zero_compute_readout.json](../../results/lowtail_dft_2026-09-18/zero_compute_reviewed/zero_compute_readout.json), with [its input manifest](../../results/lowtail_dft_2026-09-18/zero_compute_reviewed/input_manifest.json). The earlier September 18 `zero_compute` directory preserves the new MACE evaluations before the final provenance review.

Every physical HEA output is counted: 65 banked outputs = 46 accepted and used + 19 excluded + 0 unidentified. This adds exactly 22 physical outputs to the historical 43. The final batch contributes 15 accepted outputs, five stopped at the SCF iteration ceiling and two rejected for IEEE_INVALID. Four pilot *OOH labels reuse branch-panel outputs and remain visible as aliases; they add no outputs to the denominator. Final acceptance comes from [the September 17 HEA readout](../../results/hea_readout_2026-09-17/readout.json), with accepted input/output bytes checked against the completion QC receipts. Rejected/stopped files retain their statuses, reasons and hashes.

All 15 new accepted DFT inputs match retained MACE coordinates, cells, species and constraints exactly. [Independent parsing of the raw total-force blocks and energy lines](../../results/lowtail_dft_2026-09-18/independent_refresh_force_check.json) reproduced every reported Cartesian force component and energy for these 15 outputs with zero numerical difference. Per-term force-contribution blocks are excluded. The stricter parser also preserves rejection of invalid, mixed and unknown numerical-exception notices while accepting only the complete known-benign underflow/denormal notice.

Sixteen unique MACE geometries were compared with the census MPA-0 checkpoint in float64. The first refresh reused the eight historical evaluations after checking the checkpoint, source pointers, source hashes and evaluator bytes, then evaluated eight additional geometries. All 16 energies reproduce their stored endpoint energies exactly at the recorded precision; all free-force maxima remain below 0.05 eV/Å. The reviewed output reuses all 16, with exact geometry checks, and performs no additional MACE calculation.

| Reconstructed *O endpoint | Cr lift relative to its clean slab (Å) | Cr–O adsorbate (Å) | Cr–O axial, clean → *O (Å) | Accepted projectors |
| --- | ---: | ---: | ---: | --- |
| Ni31Cr29Cu5Mn35, seed 1/site 0 | 0.845492 | 1.590711 | 1.711258 → 2.693166 | atomic, ortho |
| Fe25Co25Ni25Cr25, seed 2/site 0 | 0.798923 | 1.589462 | 1.725519 → 2.758158 | atomic; ortho stopped |
| Ni31Cr29Cu5Mn35, seed 0/site 0 | 0.949962 | 1.591920 | 1.672694 → 2.852296 | atomic, ortho |

The seed-0 Ni31 site is an additional mechanistic comparison, not an additional member of the prepared three-site relaxation set. Its retained *OOH endpoint desorbed/dissociated, so its fixed-coordinate chain still provides no ordinary AEM overpotential. Cu8Cr23Mn35Co34 seed 20/site 2 remains unmeasured by DFT in this force population.

Positive normal force points away from the slab. The bond projection is `(F_O − F_Cr)·u`, with `u` directed from Cr to adsorbed O; a negative value compresses that contact. The pair normal is the total normal force on Cr plus adsorbed O. All force entries below are eV/Å.

| Site / projector | Cr normal | Adsorbed O normal | Cr–O bond projection | Pair normal | Maximum free force |
| --- | ---: | ---: | ---: | ---: | ---: |
| Ni31 seed 1 / atomic | +1.066340 | −1.089884 | −2.156084 | −0.023544 | 1.582560 |
| Ni31 seed 1 / ortho | +1.067095 | −1.108686 | −2.175585 | −0.041591 | 1.518581 |
| Fe25 seed 2 / atomic | +1.039752 | −1.152111 | −2.194178 | −0.112359 | 1.391153 |
| Ni31 seed 0 / atomic | +0.985373 | −0.919756 | −1.921120 | +0.065616 | 1.499240 |
| Ni31 seed 0 / ortho | +1.341785 | −0.750452 | −2.087716 | +0.591333 | 1.412260 |

The positive force on Cr alone is not evidence that DFT preserves the lifted site: it is coupled to the opposing force on adsorbed O and to motion in the rest of the slab. In particular, the Ni31 seed-0 pair has a substantially larger net outward force with the ortho projector than with atomic. This is a local projector sensitivity, not an energy ranking of relaxed basins.

The mass-weighted first-order axial-gap response is closing for Ni31 seed 1 (−0.042469 atomic / −0.045440 ortho eV/(Å amu)) and Fe25 seed 2 (−0.029019 atomic), but weakly opening for Ni31 seed 0 (+0.000870 atomic / +0.000792 ortho). This sign difference prevents extending the historical single-site axial interpretation to every Cr site. The corresponding clean slabs also carry substantial forces, and these local accelerations do not predict the final relaxed contact. For the 15 newly accepted outputs, maximum free forces range from 1.261837 to 1.570643 eV/Å; none is a DFT stationary point.

The scientific next experiment remains the prepared nine atomic-projector relaxations: clean slab, reconstructed *O start and unreconstructed *O start at each of Cu8 seed 20/site 2, Ni31 seed 1/site 0 and Fe25 seed 2/site 0. The two starts test whether the lifted short-bond structure persists or is recovered under DFT. Acceptance requires the frozen convergence, force, integrity and basin rules. The nine ortho decks are a conditional follow-up after the atomic readout. No additional Ru or S5 computation follows from this refresh.

[Refreshed cost evidence](../../results/lowtail_dft_2026-09-18/cost_refresh.json) uses 41 accepted SCFs at the record settings (21 atomic, 20 ortho), with same-site force references when available and explicit proxies otherwise. The relaxation survey still contains the same 102 included and 11 excluded raw outputs. Its scorer provenance now records the corrected canonical September 17 parser.

| Set | Refreshed planning core-hours | Refreshed ceiling core-hours | Comparison with preserved limits |
| --- | ---: | ---: | --- |
| Nine atomic primary decks | 5,424.344 | 17,394.004 | Every revised ceiling is below its original supervisor limit |
| Nine conditional ortho controls | 10,622.609 | 31,867.826 | Every revised ceiling is about 0.576–0.577% above its original supervisor limit |

All memory estimates fit the node, and every revised ceiling remains below the input's `max_seconds`. The original primary budget of 5,443.2 planning / 17,925.0 ceiling core-hours therefore remains supported for release, with its original per-leg limits unchanged. The conditional ortho set needs its small timing-limit revision reviewed before release. This cost refresh changes no prepared deck, manifest or supervisor limit and is not a guarantee of convergence.
