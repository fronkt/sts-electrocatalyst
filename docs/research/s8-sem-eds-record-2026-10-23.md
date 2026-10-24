# S8 SEM-EDS of the six alloys, 2026-10-23

Status: first readout of Fort Wayne Metals' SEM-EDS session of 2026-10-23 (Frank; done earlier than the planned week of 10-26). **These are spot analyses only. Freeze §5's acceptance (±2 at.% of nominal per element) is a bulk test and needs area analyses, which this session did not record.** Nothing here changes a frozen value.

**Update (2026-10-23, Frank): more EDS is probably not possible before the bench; XRD comes soon.** The spots below and the lever-rule estimates are therefore the final composition evidence for these six alloys. The area-EDS asks in the last section are withdrawn, and each alloy's acceptance has to be read from the estimates and stated with their uncertainty.

- **Instrument:** Thermo Fisher Phenom, 15 kV, BSD Full, standardless quantification (`SDUTW5` detector, 129 eV at Mn Kα).
- **Files (not committed; Frank's folder `D:\STS Electrocatalyst EDS & SEM`):**
  - `EDS/<n> EDS/`: Phenom `.phen` + `.odt` report, and `export/` with the BSE image showing the spot markers plus `quantification.csv`, `spectrum.emsa` and `spectrum.tiff` for each spot.
  - `Images/`: 11 BSE micrographs at 135–500×.
  - 23 spots in total: 149 ×4, 150 ×4, 151 ×3, 152 ×3 + 2 ("152 EDS 2"), 153 ×3, 154 ×3 + 1 (2,000×).
- **Readout:** `python src/scripts/s8_sem_eds_readout.py "D:\STS Electrocatalyst EDS & SEM"` writes `results/s8_sem_eds_2026-10-23/readout.json`.

## Identity of the files

- The folders 149–154 are ARC00149–154 ([melt record](s8-melt-record-2026-10-17.md)): 149 Cu8, 150 Cu26, 151 Fe25, 152 Ni34, 153 Cu22, 154 Ni31.
- The label field burned into the images is stale on three sets: the 149 images read "316-111 2000x", the 153 images read "152", and "152 EDS 2" reads "154". The measured element sets match the folder names (for example, 153 has Mn and Fe and no Cr, which is Cu22), so the folder names are taken as the identity.
- **Not recorded: which piece was imaged.** It could be an electrode disk, a homogenized offcut or an as-cast piece. For Cu8 this decides whether the result counts. The melt record (Notes 2026-10-22) excludes the hot-rolled Cu8 pieces as the acceptance sample, because rolling reheated them to 850 °C, where σ and Cu-rich particles can grow.

## Spot compositions (at.%, metals only; C and O dropped)

| Alloy | Spot (on what) | Cr | Mn | Fe | Co | Ni | Cu |
|---|---|---|---|---|---|---|---|
| 149 Cu8 | 1 (bright Cu-rich between particles) | 1.4 | 28.8 | – | 4.8 | 5.4* | 59.6 |
| | 2 (smooth, cracked grey particle) | 34.1 | 27.1 | – | 36.4 | 0.9* | 1.5 |
| | 3 (mottled darker grain) | 17.1 | 33.2 | – | 42.6 | 1.3* | 5.8 |
| | 4 (mottled darker grain) | 17.5 | 33.3 | – | 42.6 | 1.1* | 5.6 |
| | *nominal* | *22.6* | *35.0* | | *34.5* | | *7.9* |
| 150 Cu26 | 1 (matrix) | 53.5 | – | – | 38.0 | 7.0 | 1.6 |
| | 2 (matrix) | 36.1 | – | – | 46.2 | 12.6 | 5.1 |
| | 3 (Cu-rich pool, ~100 µm) | 1.1 | – | – | 4.0 | 11.5* | 83.5 |
| | 4 (small bright particle, ~5 µm, beside the pool) | 2.1 | – | – | 4.6 | 11.4* | 81.9 |
| | *nominal* | *31.5* | | | *33.4* | *9.4* | *25.8* |
| 151 Fe25 | 1–3 (mean) | 23.6 | – | 24.9 | 26.6 | 25.0 | – |
| | *nominal* | *25* | | *25* | *25* | *25* | |
| 152 Ni34 | 5 spots (mean; range) | – | 0.1 | 6.7 (6.1–7.1) | 32.6 (31.2–33.8) | 34.9 (34.8–35.2) | 25.8 (23.9–27.8) |
| | *nominal* | | | *6.0* | *30.7* | *33.9* | *29.4* |
| 153 Cu22 | 1 (grey rounded grain) | – | 12.6 | 36.6 | 41.3 | – | 9.5 |
| | 2 (bright network) | – | 15.6 | 1.3 | 2.9 | 7.0* | 73.1 |
| | 3 (grey rounded grain) | – | 12.4 | 36.3 | 41.2 | – | 10.1 |
| | *nominal* | | *15.5* | *30.0* | *32.4* | | *22.1* |
| 154 Ni31 | 1 (light matrix) | 5.7 | 44.5 | – | – | 36.6 | 13.2 |
| | 2 (dark particle) | 85.9 | 10.9 | – | – | 2.7 | 0.5 |
| | 3 (dark inclusion; raw O 53.5, Si 6.8, S 1.4 at.%) | 63.1 | 34.9 | – | – | 1.9 | – |
| | Image 2 (inside a large dark region, 2,000×) | 44.1 | 26.0 | – | – | 26.1 | 3.8 |
| | *nominal* | *29.2* | *34.5* | | | *31.1* | *5.2* |

\* Mostly or entirely a quantification artifact; see the next section. The "on what" labels come from the marker positions in each `export/Image 1.png`.

## The Ni reported in Cu-rich spots is mostly not there

- Cu8 and Cu22 contain no Ni, yet the software reports 5.4 and 7.0 at.% Ni in their Cu-rich spots.
- A least-squares fit of the K lines (5.6–9.3 keV; one Gaussian per line on a linear background) finds **no Ni Kα peak** at 7.478 keV in either spectrum: −811 ± 489 and −793 ± 510 net counts, against about 1.0–1.3 × 10⁵ counts of Cu Kα. The 152 spectra, by comparison, carry 7–8 × 10⁴ counts of Ni Kα.
- In both spots the "Ni" equals 8.5% of the reported Cu + Ni. So the software books about 8.5% of the Cu signal as Ni (possibly through the Ni Kβ / Cu Kα overlap). Cu26's Cu-rich pool shows the same excess: it has a real, small Ni Kα peak, but the software reports roughly three times the Ni that the peak ratio implies when scaled to 152.
- **Effect on Ni34.** As reported, Cu is 25.8 at.% (−3.7, outside ±2) and Ni is 34.9 (+1.0). Moving 8.5% of the Cu signal back gives Cu 28.1 (−1.3) and Ni 32.5 (−1.3), with Fe +0.7 and Co +1.85. That is within ±2 on every element. **This is an estimate.** The measurement that settles it is a requantification with the right element list, or a fit against a Cu standard.
- **Fe25 shows the method's own scatter:** Cr −1.4 and Co +1.5 on a nominally equiatomic alloy. Standardless EDS errors of this size are common, so the ±2 at.% tolerance is about the method's own uncertainty.

## Microstructures

- **151 Fe25: single phase.** Large grains (hundreds of µm) with straight boundaries, consistent with FCC plus annealing twins. Spot-to-spot variation is ≤ 0.3 at.%. The only alloy that looks like the model's random solid solution without qualification.
- **152 Ni34: single phase at 500×.** Some pits (pull-outs or pores, about 1% of the area). The 205× image shows faint darker patches; spots on and off a patch differ by about 2 at.% in Cu.
- **153 Cu22: two phases.** Rounded, touching Fe–Co–Mn grains (Fe 36, Co 41, Mn 12.5, Cu 10; 20–100 µm) sit in a continuous bright Cu–Mn network (Cu about 80, Mn 16, Co 3, Fe 1; 16–18% of the area).
- **149 Cu8: three phases, and one of them is cracked.**
  - Smooth grey particles: Cr 34, Co 36, Mn 27 (Cr + Mn ≈ 61). They are crossed by many cracks that stop at their edges, as a brittle phase cracks. Composition and cracking fit σ, but XRD has to show it.
  - Mottled darker grains: Co 43, Mn 33, Cr 17, Cu 6.
  - Bright Cu–Mn phase between them: Cu about 65, Mn 29. About 10% of the area.
  - Everything is rounded.
- **150 Cu26: matrix + Cu.**
  - A fine two-phase matrix: Cr-rich (Cr 54, Co 38) and Co-rich (Co 46, Cr 36, Ni 13).
  - Dispersed Cu-rich droplets of 1–5 µm (spot 4 sits on one).
  - Cu-rich pools up to about 100 µm and Cu films along boundaries (Cu about 90 after the Ni artifact, Ni about 3, Co 4).
- **154 Ni31: two phases plus inclusions.**
  - A light Mn–Ni–Cu matrix (Mn 44, Ni 37, Cu 13, Cr 6; about 71% of the area).
  - Irregular, rounded dark Cr-rich regions (about 29%). They are not uniform: one spot reads Cr 86, and a 2,000× spot inside a large region reads Cr 44 / Mn 26 / Ni 26. Both readings sit among bright specks inside the dark regions.
  - Black particles. One of them is an oxide with Si and S (O 53, Si 7, S 1.4, Cr, Mn), which could be slag from the Cr/Mn charge or colloidal silica caught in a pit.

### Local melting during the 1,050 °C anneal (the check planned in step 6)

The melt record (Notes 2026-10-17) lists what step 6's BSE should look for: rounded features, re-solidified pockets, and Cu-rich films. Cu8 and Cu22 show this pattern. Rounded solid grains sit in a continuous Cu–Mn-rich phase, the way solid particles coarsen when they sit in a liquid. The Cu–Mn binary liquidus falls from 1,085 °C (Cu) to a minimum of about 870 °C near 38 at.% Mn. At the measured 16 and 29 at.% Mn it lies roughly 1,000 °C and 900 °C, below the 1,050 °C anneal. **If these pieces went through the anneal, their Cu–Mn phase was probably liquid for the 24 h.**

That is a working explanation. The competing one is liquid immiscibility during casting: Cu does not mix with Fe or Co even in the liquid, so Fe–Co-rich liquid can form separate droplets before solidification. The two can be told apart by imaging an as-cast keeper rod of Cu8 and Cu22, which never went through the anneal:

- dendrites with Cu between the dendrite arms in the as-cast rod means the rounding came from the anneal;
- rounded grains already in the as-cast rod means they formed during casting.

Cu26's Cu-rich phase (Cu with a few % Ni and Co) is probably solid at 1,050 °C (Cu–Cr eutectic 1,075 °C), so its pools and films most likely date from solidification. This fits the copper-coloured skin on the Cu26 rod (melt record): Cu-rich liquid separated during casting.

## Rough bulk estimates (lever rule; not an acceptance measurement)

The bulk estimate is the BSE area fraction of each phase (multi-Otsu threshold, pores excluded, 2–3 fields per alloy) times that phase's spot composition. The limits are one or two fields per alloy, at most four spots, and grey-level classes that only roughly match the phases.

| Alloy | Estimate vs nominal (at.%) | Reading |
|---|---|---|
| Cu8 | Mn 29.5 (**−5.5**), Cr 24.6 (+2.0), Co 35.4 (+0.9), Cu ≈ 10.5 (+2.6 after the Ni artifact; sensitive to the Cu-rich area fraction) | **Mn probably low.** Robust to how the two grey phases are split: even if every non-Cu pixel were the most Mn-rich phase, Mn ≤ 32.8 (−2.2). This is Mn lost in melting; the charge had +4% Mn. |
| Cu26 | Cu 16.8 (**−9.0**), Cr 37.4 (+6.0), Co 35.7 (+2.3) | Cu low in these fields. Cu26 would need about 26–28% Cu-rich area for nominal and shows 14–20%. Cu that went to the rod skin is a candidate explanation. Field-dependent; with no area scans, how well these fields represent the disk stays unknown. |
| Cu22 | Mn 13.0 (**−2.5**), Co 34.7 (+2.3), Fe 30.5 (+0.5), Cu ≈ 21.8 (−0.3 after the Ni artifact) | Borderline on Mn and Co. |
| Ni31 | Undetermined: Cr between 16.9 and 29.1 depending on which dark-phase reading is used; Cu +4 to +5 either way | The dark phase is heterogeneous, so spots cannot fix a bulk value, and no area scan is coming. Cu above nominal would be unexpected; don't read anything into it. |
| Fe25 | Spot mean = bulk: Cr −1.4, Co +1.5, Fe −0.1, Ni 0.0 | **Within ±2.** |
| Ni34 | Spot mean: Cu −3.7 as reported, −1.3 after the Ni correction | **Probably within ±2.** Settle it with a corrected requantification. |

## What this means for the study

- **Four of the six alloys are not single-phase solid solutions:** Cu8, Cu22, Cu26 and Ni31. Fe25 and Ni34 are.
  - The DFT and MLIP screens scored random single-phase FCC slabs, so for those four alloys the electrode face is a mosaic of phases with very different compositions. Cu8's face, for example, is about half Cr–Co–Mn phase, a third Co–Mn phase and a tenth Cu–Mn phase.
  - The test still measures what the screened compositions give as made by arc melting and the frozen anneal. It no longer measures the modeled solid solution itself.
  - Report Section 3.7 and the discussion have to say this.
  - **This is also a finding about the screen's solid-solution gate.** All six passed the Ω–δ rule of `src/hea_oer/phase_stability.py` (Yang & Zhang 2012: Ω ≥ 1.1, δ ≤ 6.6%), and four came out multiphase. Values at nominal composition:

    | Alloy | VEC | δ (%) | ΔH_mix (kJ/mol) | Ω | VEC tendency | Observed |
    |---|---|---|---|---|---|---|
    | Cu8 | 7.78 | 3.62 | −1.08 | 17.1 | FCC+BCC | 3 phases (σ-like Cr-rich, Co–Mn, Cu–Mn) |
    | Cu26 | 8.67 | 1.00 | +3.84 | 5.0 | FCC | matrix + Cu-rich |
    | Fe25 | 8.25 | 0.30 | −3.75 | 5.8 | FCC | single phase |
    | Ni34 | 9.87 | 1.12 | +4.44 | 3.9 | FCC | single phase |
    | Cu22 | 8.83 | 2.92 | +4.32 | 4.3 | FCC | Fe–Co–Mn + Cu-rich |
    | Ni31 | 7.85 | 3.74 | −3.91 | 4.7 | FCC+BCC | Mn–Ni matrix + Cr-rich |

    - The two alloys with a Cr-rich second phase (Cu8, Ni31) are the two whose VEC falls in Guo's FCC+BCC window. The module computes that tendency, but the gate does not use it.
    - Ω and ΔH_mix do not sort the Cu alloys. Ni34 has the most positive ΔH_mix and stayed single phase, while Cu26 and Cu22 separated. A working explanation is that Ni34 has enough Ni to hold its Cu in solution (Cu–Ni mix completely), whereas Cu26 (9% Ni) and Cu22 (no Ni) do not. The regular-solution average hides the strongly positive Cu–Co, Cu–Cr and Cu–Fe pairs.
- **K1 (Cu8 vs Ni31 and Fe25):** two of its three alloys are multiphase, and Cu8 is probably below the Mn tolerance. **K2:** four of its five alloys are multiphase.
- **Freeze §5:** "A sample out of tolerance is re-melted once. If it is still out, it is kept, flagged, and analysed at its measured composition."
  - With no area EDS coming, the estimates above are the measured compositions. Cu8 is out on Mn under every phase split (Mn ≤ 32.8, at least −2.2). Cu26 is out on Cu in the imaged fields (−9.0), but how well those fields represent the disk is unknown. Cu22 is at the edge on Mn and Co. Ni31 cannot be decided from spots. A re-melt adds melting, anneal, machining and polishing, roughly a week, and pushes past the Nov 3 bench date.
  - A re-melt also would not fix the phase separation, and Mn would boil off again unless the over-charge is raised.
  - Skipping the re-melt would be a dated departure from §5. **Frank's decision.**
- **Electrode surfaces:**
  - Cu8's cracked σ-like phase adds real area and crevices. C_dl normalization covers some of that.
  - Cu- and Mn-rich phases may dissolve or restructure first in 1 M KOH at OER potentials. The registered post-mortem SEM-EDS should therefore record which phase was attacked.
  - Cr(VI) in the spent electrolyte is already registered (freeze §6).

## Still needed from Fort Wayne Metals (step 6)

More EDS is probably not possible before the bench (Frank, 2026-10-23). The first-draft asks for area EDS (≥ 3 full-frame fields per alloy at ≤ 250×, centre and edge for Cu26) and for elemental maps are withdrawn for now. They are not needed for the registered tests: K1, K2 and the IrO2 comparison are judged on mean η (freeze §6), and no extra EDS would change Cu8's Mn result. The registered post-mortem XRD/SEM-EDS (freeze §6, a secondary endpoint) is a maybe for the Nov 5 report, probably not (Frank, 2026-10-23). It depends on how fast the Tackett lab finishes and whether Frank can collect the disks at Purdue that day. Plan the report without it and add it only if it arrives. If it doesn't, the report lists it as not yet done. Whenever it is done, add area scans of an untested spare disk of each alloy, which gives the pre-test bulk composition. Before Nov 5, the surface-change evidence comes from the before/after photos of each disk's face that the bench plan asks the lab for, and from the Cr(VI) electrolyte check. What remains:

1. **XRD (coming soon).** It identifies σ in Cu8, the Cr-rich phase in Ni31 (bcc Cr or σ), and whether Cu26's matrix is two FCC phases or FCC + bcc/σ. Peak-area phase fractions from XRD would also give a second, independent check on the BSE fractions in the lever rule.
2. **Provenance:**
   - which piece each image came from (disk, homogenized offcut or as-cast);
   - for Cu8, confirmation that it is not the hot-rolled material.
3. **Only if it needs no new acquisition:** requantify the saved spectra with Ni deselected for Cu8 and Cu22 (this removes the Ni artifact without the correction used here).
4. **Only if SEM imaging, not EDS, is still possible:** a BSE image of an as-cast keeper rod of Cu8 and Cu22, for the local-melting question.
