# Generalization row1 - cost and ceiling (2026-09-22)

NOT LICENSED: needs the entrant's dated A11.R3 line after the discriminating SCF test reads out.

12 legs = 4 sites x (slab, O_recon, O_unrecon), HUBBARD (atomic), 128 ranks, concurrency 1. Cost model: src/s2/lowtail_dft/lt_cost.py deck_cost as in results/lowtail_dft_2026-09-18/launch_spec.json (measured HEA per-SCF anchors x banked relaxation-step bands; ceiling = max(3 x planning, p90 formula)).

| site | job | nat | planning core-h | ceiling core-h | planning wall h | ceiling wall h | leg wall ceiling s | spec-basis planning | spec-basis ceiling |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Cu8Cr23Mn35Co34__s16_site2 | slab__atomic | 72 | 589.8 | 1904.0 | 4.61 | 14.87 | 53550 | 585.6 | 1928.4 |
| Cu8Cr23Mn35Co34__s16_site2 | O_recon__atomic | 73 | 595.9 | 1923.4 | 4.66 | 15.03 | 54097 | 591.6 | 1948.0 |
| Cu8Cr23Mn35Co34__s16_site2 | O_unrecon__atomic | 73 | 595.9 | 1923.4 | 4.66 | 15.03 | 54097 | 591.6 | 1948.0 |
| Cu8Cr23Mn35Co34__s26_site1 | slab__atomic | 72 | 589.8 | 1904.0 | 4.61 | 14.87 | 53550 | 585.6 | 1928.4 |
| Cu8Cr23Mn35Co34__s26_site1 | O_recon__atomic | 73 | 595.9 | 1923.4 | 4.66 | 15.03 | 54097 | 591.6 | 1948.0 |
| Cu8Cr23Mn35Co34__s26_site1 | O_unrecon__atomic | 73 | 595.9 | 1923.4 | 4.66 | 15.03 | 54097 | 591.6 | 1948.0 |
| Cu26Ni9Cr31Co33__s1_site0 | slab__atomic | 72 | 590.4 | 1905.6 | 4.61 | 14.89 | 53597 | 586.1 | 1930.0 |
| Cu26Ni9Cr31Co33__s1_site0 | O_recon__atomic | 73 | 595.0 | 1920.5 | 4.65 | 15.00 | 54015 | 590.7 | 1945.1 |
| Cu26Ni9Cr31Co33__s1_site0 | O_unrecon__atomic | 73 | 595.0 | 1920.5 | 4.65 | 15.00 | 54015 | 590.7 | 1945.1 |
| Cu26Ni9Cr31Co33__s17_site1 | slab__atomic | 72 | 590.4 | 1905.6 | 4.61 | 14.89 | 53597 | 586.1 | 1930.0 |
| Cu26Ni9Cr31Co33__s17_site1 | O_recon__atomic | 73 | 595.0 | 1920.5 | 4.65 | 15.00 | 54015 | 590.7 | 1945.1 |
| Cu26Ni9Cr31Co33__s17_site1 | O_unrecon__atomic | 73 | 595.0 | 1920.5 | 4.65 | 15.00 | 54015 | 590.7 | 1945.1 |
| total (12) | | | 7123.7 | 22995.0 | | | | 7072.6 | 23289.3 |

Current anchors: 21 accepted atomic SCFs (first-SCF iterations p50 40, p90 75). Spec basis: the frozen 2026-09-18 anchors, 14 accepted atomic SCFs (p50 37, p90 87).

Launch-spec scheduler conventions (src/dft/prepare_lowtail_launch.py:63-67), current anchors: relaxation ceiling 22995.3 core-h (rounded per-leg walls), projection ceiling 768 core-h (12 x 1800 s), wall 934 min per task, scheduler ceiling 23910 core-h. Spec-basis anchors: relaxation ceiling 23289.5, wall 946 min, scheduler ceiling 24218 core-h.

Reference: the nine-leg 2026-09-18 spec carries 5443.2 planning / 17925.2 relaxation-ceiling / 19296 scheduler-ceiling core-h; the sizing note's bracket-row proxy (4 x the Cu8Cr23Mn35Co34 seed20 site2 legs of the 2026-09-18 spec) is 7075.2 planning / 23297.8 ceiling core-h.

- Planning and ceiling costs are empirical estimates, not guarantees of convergence.
- No DFT force exists at any row-1 site: the Ni31 seed-1 endpoint forces of the 2026-09-16 zero-compute readout set the step bands, as in the 2026-09-18 spec.
- Array 20813525 observed a clean-slab leg fail at the SCF ceiling (538 core-h) and an adsorbate leg reach 1,194 core-h before its kill (docs/research/lowtail-generalization-sizing-2026-09-22.md section 3); the bands do not model that failure mode.
