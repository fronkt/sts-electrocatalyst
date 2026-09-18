# P-BUILDER operating decision — 2026-09-16

This record fixes, before any blind arm runs, the values docs/43 A9.3.5 (:1900-1902) left open:
- the source structures and the bulk-cell setting;
- terminations, slab parameters and adsorbate geometries;
- the enumerator denominators;
- how "rate X per family" is read;
- X with its falsification branch;
- the outcome of the atomate verification gate.

On perovskite(001), spinel(001) and fcc(111), only the registered enumerator and geometry were run. No symmetry was computed on any of their adsorbate structures; symmetry was computed on clean slabs only. The rutile(110) arm had already been seen, and its in-repo re-run reproduces the disclosed 2026-08-15 counts exactly. The atomate gate passes. Both scope checks pass too, so the dated statement carries its full wording.

Every table below is rendered by `python -m s2.p_builder.prestate tables` (run from `src/`) from `results/s2_2026-09-16/p_builder_prestate/{denominators,decision,rutile_nonblind_rerun,atomate_gate}.json`, and the same text is in `tables.md` there. A test requires every rendered row to appear here verbatim. Input, output and code sha256 values are in `manifest.json` in the same directory. Versions: pymatgen 2026.4.16, spglib 2.7.0, scipy 1.17.1, numpy 2.3.5, Python 3.12.10.

## Registered inputs applied unchanged (docs/43 :1902)

- **Enumerator:** `AdsorbateSiteFinder(slab).generate_adsorption_structures(mol, repeat=[1,1,1], find_args={"distance": 2.0})`, run on an unmodified pymatgen.
- **Slabs:** `SlabGenerator(min_slab_size=9., min_vacuum_size=15., center_slab=True, primitive=True)` for every family. `lll_reduce=False` is the pymatgen default and matches t2.py.
- **Adsorbates:** O; OH with d = 0.98 Å, upright; bent OOH `[[0,0,0],[1.29,0,0.7],[1.29,0.9,1.0]]` from `docs/research/2026-08-15-sampling/t2.py`, taken as is.
- **Census:** `SpacegroupAnalyzer(structure, symprec=1e-3)`. An operation counts as adsorbate-invariant when it maps every adsorbate atom onto itself mod lattice (distance < 1e-3 Å) and has a −1 eigenvalue. docs/43 registers no eigenvalue tolerance, so the 1e-6 used in t2.py applies. A test checks these constants against t2.py's AST and docs/43 line 1902.
- **Scope rows:** HELD and FALSIFIED as worded in :1923. The two numbers are never multiplied (:1902).

## Reading of "rate X per family"

docs/43 :1902 defines the population as family × {*O, *OH, *OOH} and asks for "rate X per family". It does not say whether the three adsorbates are scored separately or pooled.

**Decision: per adsorbate.** X and the verdict apply to *O and to *OH separately, each over the N configurations of that adsorbate. Bent *OOH is a construction check with an expected rate of 0.

**Named alternative: pooled.** This gives one rate per family over all 3N configurations. The per-adsorbate reading is chosen because the bent *OOH geometry retains no operation on any of the four cells by construction (bound below). Pooling would therefore fix one third of the population at zero through the chosen adsorbate geometry, not through site selection. The pooled rate is then 2/3 of the upright rate, and a 1/2 line on it would falsify any family whose upright rate is at or below 3/4.

**What pooling would change.** The pooled rate is computed and reported next to the per-adsorbate rates, with no verdict. The last column of the denominators table gives the pooled value at each predicted minimum. Under a pooled reading with the same 1/2 line, the spinel prediction itself (8/13 upright, pooled 16/39) would fall on the FALSIFIED side.

## Values fixed

### Structures

| family | source | space group | cell (Å) | literature | file |
|---|---|---|---|---|---|
| rutile(110) | hand-built (t2.py), = COD 9007541 | P 42/m n m | a = 4.4919, c = 3.1066, u = 0.3058 | Baur, W. H.; Khan, A. A., *Acta Crystallographica, Section B* 27, 2133-2139 (1971), 10.1107/S0567740871005466 | `structures/rutile_RuO2_handbuilt.cif` |
| perovskite(001) | COD 9006864 | P m -3 m | a = 3.90528 | Mitchell, R. H.; Chakhmouradian, A. R.; Woodward, P. M., *Physics and Chemistry of Minerals* 27, 583-589 (2000), 10.1007/s002690000103 | `structures/cod_9006864_SrTiO3.cif` |
| spinel(001) | COD 9005887 | F d -3 m :2 | a = 8.0821, O x = 0.2627 (origin 2) | Liu, X.; Prewitt, C. T., *Physics and Chemistry of Minerals* 17, 168-172 (1990); 301 K | `structures/cod_9005887_Co3O4.cif` |
| fcc(111) | COD 9008480 | F m -3 m | a = 3.9231 | Wyckoff, R. W. G., *Crystal Structures* 1, 7-83 (1963) | `structures/cod_9008480_Pt.cif` |

Bulk-cell setting: source cell as deposited (COD conventional cell; registered hand-built rutile cell); no primitive or standard-cell reduction before SlabGenerator.

The COD files were downloaded on 2026-09-16 and are committed byte for byte under `structures/`. The Materials Project was not used.

- **rutile(110):** the registered hand-built RuO₂ cell. Its a, c and u equal COD 9007541 (AMCSD data from Boman 1970), and `structures.rutile_matches_cod` checks the match site by site.
- **perovskite(001):** SrTiO₃, the untilted cubic Pm-3m aristotype with one formula unit, so no octahedral-tilt pattern lowers the ideal p4mm surface group. The entry is the x = 0.00 end member.
- **spinel(001):** Co₃O₄, a normal spinel with Co on tetrahedral 8a and octahedral 16d in the CIF, and itself an OER oxide. The entry is the 301 K refinement.
- **fcc(111):** Pt, a pure fcc metal as :1902 requires, and a standard (111) adsorption reference.

### Bulk-cell setting

**Decision.** SlabGenerator receives the source cell as deposited: the COD conventional cell, or the registered hand-built rutile cell. No primitive or standard-cell reduction is applied first.

**Rationale.** The family Miller indices are conventional-cubic-cell indices, and SlabGenerator reads (hkl) in the basis of the cell it receives. The table below reruns the same registered call on each primitive cell (enumerator only; not part of the population).

| family | primitive bulk sites | (hkl) normal, deposited cell | (hkl) normal, primitive cell | same frame | candidates: atoms, top species, reduced basis (Å, °), N (ontop/bridge/hollow), *OOH image contact (Å) |
|---|---|---|---|---|---|
| perovskite(001) | 5 (deposited 5) | (0.0000, 0.0000, 1.0000) | (0.0000, 0.0000, 1.0000) | True | [0] 15, O2 Ti1, 3.9053 × 3.9053 90, N = 5 (2/3/0), 2.707 |
| spinel(001) | 14 (deposited 56) | (0.0000, 0.0000, 1.0000) | (0.5774, -0.5774, -0.5774) | True | [0] 28, Co2, 5.7149 × 5.7149 60, N = 6 (2/4/0), 4.456; [1] 28, Co2, 5.7149 × 5.7149 60, N = 6 (2/4/0), 4.456; [2] 28, Co1 O3, 5.7149 × 5.7149 60, N = 9 (2/5/2), 4.456; [3] 28, Co1 O4, 5.7149 × 5.7149 60, N = 10 (3/4/3), 4.456 |
| fcc(111) | 1 (deposited 4) | (0.5774, 0.5774, 0.5774) | (-0.5774, -0.5774, -0.5774) | True | [0] 4, Pt1, 2.7741 × 2.7741 60, N = 4 (1/1/2), 1.641 |

- **Co₃O₄:** (001) of the rhombohedral primitive cell is a cubic {111} plane with a 60° surface cell, so it is a different surface.
- **SrTiO₃:** the deposited cell is already primitive.
- **Pt:** the primitive cell gives the same (111) plane, but as a 1×1 cell with the same N and site types. The deposited 4-atom cell gives the 2×2 cell used here. **The Pt(111) coverage of 1/4 ML therefore follows from this bulk-cell setting, not from `primitive=True`.** In the 1×1 alternative, the bent OOH comes closer to its own periodic image than in the 2×2 cell, and that contact is only a little longer than the O₁–O₂ distance inside the molecule (contacts table below).

### Slabs (registered SlabGenerator arguments)

| family | candidates (top-surface species) | selected | top layer: species depth Å (neighbours ≤ 2.3 Å) | atoms | surface cell (Å, °) | reduced in-plane basis (Å, °) | atom span / vacuum along normal (Å) | adsorbates per top-layer metal atom | clean-slab group (symprec 1e-3) |
|---|---|---|---|---|---|---|---|---|---|
| rutile(110) | [0] O2 Ru2; [1] O1 | [0] | Ru 0.000 (5), Ru 0.000 (4), O 0.000 (3), O 0.000 (3) | 18 (Ru6 O12) | 3.1066 × 6.3525, γ = 90 | 3.1066 × 6.3525, 90 | 8.295 / 17.115 | 1/2 (2 top-layer metal) | Pmm2, 4 ops (4 keep the normal) |
| perovskite(001) | [0] O2 Ti1 | [0] | Ti 0.000 (5), O 0.000 (2), O 0.000 (2) | 15 (Sr3 Ti3 O9) | 3.9053 × 3.9053, γ = 90 | 3.9053 × 3.9053, 90 | 9.763 / 17.574 | 1/1 (1 top-layer metal) | P4mm, 8 ops (8 keep the normal) |
| spinel(001) | [0] Co2 O2; [1] Co2 O4 | [1] | O 0.000 (3), O 0.000 (3), Co 0.103 (5), Co 0.103 (5), O 0.205 (3), O 0.205 (3) | 56 (Co24 O32) | 5.7149 × 8.0821, γ = 135 | 5.7149 × 5.7149, 90 | 15.257 / 17.072 | 1/2 (2 top-layer metal) | Pmm2, 4 ops (4 keep the normal) |
| fcc(111) | [0] Pt4 | [0] | Pt 0.000 (9), Pt 0.000 (9), Pt 0.000 (9), Pt 0.000 (9) | 16 (Pt16) | 5.5481 × 5.5481, γ = 60 | 5.5481 × 5.5481, 60 | 6.795 / 18.120 | 1/4 (4 top-layer metal) | R-3m, 48 ops (24 keep the normal) |

**How the table is built.**
- The neighbour column counts O–metal pairs within 2.3 Å for the oxides, and all neighbours within 3.0 Å for Pt.
- Top-surface species are the AdsorbateSiteFinder surface sites (height 0.9 Å). A termination is selected by that species signature, which must match exactly one slab that SlabGenerator returns (`slabs.select_termination`).
- The coverage column counts one adsorbate per cell against the metal atoms among those surface sites.
- The clean-slab group is computed on the slab without any adsorbate.

**Termination per family.**
- **rutile(110):** slab [0] is `get_slabs()[0]` as in t2.py, kept so the disclosed arm is reproduced. Its top is the Ru₂O₂ plane without bridging O. It is not the stoichiometric bridging-O termination, which is slab [1] and which Man et al. 2011 draw for rutile(110) (Fig. panel a; in-repo PDF sha256 `9c61b31e2d4e`, p. 1164). No rate is computed on slab [1].
- **perovskite(001):** SlabGenerator returned one slab. Its top is the TiO₂ (BO₂) layer, which exposes the B cation with Sr in the subsurface, as in Man et al. 2011 Fig. panel c.
- **spinel(001):** slab [1] has the complete octahedral B layer on top (Co₂O₄, with 5-coordinate Co). Slab [0] keeps that layer's Co but only half its O: the plane clustering separates O lying 0.103 Å above and below the Co plane, so slab [0]'s top is not a whole bulk layer.
- **fcc(111):** there is one termination. The 2×2 cell follows from the bulk-cell setting above.

**Thickness and vacuum.** The registered 9 Å and 15 Å minima apply to all families, so the families differ only in structure. The spinel basis reduces to a square cell.

### Enumerator reduction group (clean slabs only)

Read from the installed pymatgen (`analysis/adsorption.py` sha256 `0f60b134f62b`): `find_adsorption_sites` defaults symm_reduce = 0.01, near_reduce = 0.01, no_obtuse_hollow = True; `symm_reduce` takes its operations from `SpacegroupAnalyzer(self.slab, 0.1)` and matches positions in fractional coordinates at atol = threshold: True.

| family | census group (symprec 0.001) | enumerator group (symprec 0.1) | operation sets identical | max translation difference (fractional) | symm_reduce match tolerance along a, b, c (Å) |
|---|---|---|---|---|---|
| rutile(110) | Pmm2, 4 ops | Pmm2, 4 ops | True | 0.0 | 0.031 / 0.064 / 0.359 |
| perovskite(001) | P4mm, 8 ops | P4mm, 8 ops | True | 0.0 | 0.039 / 0.039 / 0.273 |
| spinel(001) | Pmm2, 4 ops | Pmm2, 4 ops | True | 0.0 | 0.057 / 0.081 / 0.323 |
| fcc(111) | R-3m, 48 ops | R-3m, 48 ops | True | 0.0 | 0.055 / 0.055 / 0.432 |

The enumerator's `symm_reduce` takes its operations from the clean slab at symprec 0.1. The census analyses adsorbate structures at 1e-3. On all four clean slabs, the operation sets at the two tolerances are identical, so the reduction and the site-type argument below use the same layer group. Position matching inside `symm_reduce` works per fractional coordinate. Its absolute tolerance is therefore largest along c, the vacuum-padded axis, and smallest in-plane (last column).

### Adsorbate–image contacts (geometry only)

Shortest distance from an adsorbate atom to an adsorbate atom of an in-plane periodic image, minimum over the configurations; for reference the O₁–O₂ distance inside the registered OOH is 1.468 Å.

| family | *O (Å) | *OH (Å) | *OOH (Å, pair) |
|---|---|---|---|
| rutile(110) | 3.107 | 3.107 | 1.947 (O–O) |
| perovskite(001) | 3.905 | 3.905 | 2.707 (O–O) |
| spinel(001) | 5.715 | 5.715 | 4.480 (O–O) |
| fcc(111) | 5.548 | 5.548 | 4.295 (O–H) |

The contacts are reported, not used to select cells. Within the population, the registered rutile cell already has the shortest *OOH contact, across its short in-plane vector.

### Files named by path and sha256

A9.3.5 (:1902) asks for the four slab files to be named by path and sha256. The `.json` slab is the pymatgen `Slab` the census loads; the `.cif` is the same slab in portable form. Configuration and structure files are listed with them.

| file | sha256 |
|---|---|
| `results/s2_2026-09-16/p_builder_prestate/structures/cod_9005887_Co3O4.cif` | `67186f0d5a179eff54ad811b3660828980c3ef0197f664573874bbef835387b6` |
| `results/s2_2026-09-16/p_builder_prestate/structures/cod_9006864_SrTiO3.cif` | `2be22c654ab10ea9958c92d97fd1af9107101f5cbbbaa0337e4dec0766253106` |
| `results/s2_2026-09-16/p_builder_prestate/structures/cod_9007541_RuO2.cif` | `5e8ba6c58302d83f8c3379690114b1788553425e483c1c04e85fe5093e0345ec` |
| `results/s2_2026-09-16/p_builder_prestate/structures/cod_9008480_Pt.cif` | `0373322030e51bc9aa4a3c04edcb15a7bd292a2fb9e80040de8c0f5c8442b8d4` |
| `results/s2_2026-09-16/p_builder_prestate/structures/rutile_RuO2_handbuilt.cif` | `712e5faaf4adefa2c4a00da14206f653d1f20676ee60ac1d061ad6b0ff260e72` |
| `results/s2_2026-09-16/p_builder_prestate/slabs/fcc111.cif` | `8b3f935e8b86af2117f9a615f1a31fc1260bef68c0858fad1bfbbbc2fef67ecb` |
| `results/s2_2026-09-16/p_builder_prestate/slabs/fcc111.json` | `eb43b4b3756526efaf8e9382bb8feb271a797715d72145c383944504949c5f04` |
| `results/s2_2026-09-16/p_builder_prestate/slabs/perovskite001.cif` | `f3387033261b63a5115d4c777162170826c7c75763da3b25c6e773d1f45c61ef` |
| `results/s2_2026-09-16/p_builder_prestate/slabs/perovskite001.json` | `087ed17337232eb490c309186df8bb1a883ae1f29a725e43049645d69121d957` |
| `results/s2_2026-09-16/p_builder_prestate/slabs/rutile110.cif` | `2e419f65bfc545659cd86afb56ae1b00710a870928989facbe941177e66cd0f1` |
| `results/s2_2026-09-16/p_builder_prestate/slabs/rutile110.json` | `e13e76e2f97f356dcec2cd22cfd11554becdba77571596c5b3f4760d0c0cb1d0` |
| `results/s2_2026-09-16/p_builder_prestate/slabs/spinel001.cif` | `64977b7bb74c457123abe88707d21876d6bf575c0e558bc887b3d02fabc0df2e` |
| `results/s2_2026-09-16/p_builder_prestate/slabs/spinel001.json` | `1fcbe248854a3dd551eebede7c5ef6445b8a8009c4fd3bee25f90cc57ad2571a` |
| `results/s2_2026-09-16/p_builder_prestate/configs/fcc111__O.json` | `2cb84d85b8e213777b252bf1e803b12ab3dd8c3a04d07b8fddb849586677f59e` |
| `results/s2_2026-09-16/p_builder_prestate/configs/fcc111__OH.json` | `44aaa0423ab6d6158627f5797abec90f4566899960dfe751a11cd234ba1049c1` |
| `results/s2_2026-09-16/p_builder_prestate/configs/fcc111__OOH.json` | `5f0d98e76cf95c083212b7256139fae72613d19848300dc609dee94b5de5f809` |
| `results/s2_2026-09-16/p_builder_prestate/configs/perovskite001__O.json` | `a0a601ccbde4d3aafa106cbc0e4e563c35f59b92c3370f21441fa7b7d84b4a0b` |
| `results/s2_2026-09-16/p_builder_prestate/configs/perovskite001__OH.json` | `243fc9b22a4602ec3a0faf6c2c643657db3250470a2447c3b410375245265449` |
| `results/s2_2026-09-16/p_builder_prestate/configs/perovskite001__OOH.json` | `1104b138f64c0cd86e9e14576e48800caaf3cd7511bc96bdba75f0a07f8bd015` |
| `results/s2_2026-09-16/p_builder_prestate/configs/rutile110__O.json` | `de6ca8d15328775b27b3ba02b0fd405bf212d113e49f468a5d8d05a824c699bc` |
| `results/s2_2026-09-16/p_builder_prestate/configs/rutile110__OH.json` | `eb316b92b36322adfde7c9fd8ae08e0159e72bb4e9cd39acc9c703bdbeef7755` |
| `results/s2_2026-09-16/p_builder_prestate/configs/rutile110__OOH.json` | `dcfc83ead1a36e31e57701da8680fab454ccffef899cdcb7357ebffbbab3d510` |
| `results/s2_2026-09-16/p_builder_prestate/configs/spinel001__O.json` | `d4e9723c41fb6633e9ebd4af7ea4a98ed38ed6aa60337f138355a773ebba9a5f` |
| `results/s2_2026-09-16/p_builder_prestate/configs/spinel001__OH.json` | `7a43fc4ebf220c12f5cb58eacbefa70863f7e34e2baafa4b6d3900affd65444c` |
| `results/s2_2026-09-16/p_builder_prestate/configs/spinel001__OOH.json` | `525d051126e0caf53e47bef782a81c891aef21f21466b58173356e2ccfd9e6ef` |

## Denominators and X

| family | N per adsorbate (O = OH = OOH) | ontop/bridge/hollow | X for *O, *OH | HELD if retained ≥ | FALSIFIED if retained ≤ | gap | *OOH | pooled reading at the predicted minimum (not used) |
|---|---|---|---|---|---|---|---|---|
| rutile(110) | 10 | 3/6/1 | 9/10 = 0.900 | 9 | 5 | 6, 7, 8 | 0 (construction) | 18/30 = 0.600; above 1/2 needs ≥ 8 upright |
| perovskite(001) | 5 | 2/3/0 | 5/5 = 1.000 | 5 | 2 | 3, 4 | 0 (construction) | 10/15 = 0.667; above 1/2 needs ≥ 4 upright |
| spinel(001) | 13 | 3/8/2 | 8/13 = 0.615 | 8 | 6 | 7 | 0 (construction) | 16/39 = 0.410; at or below 1/2; above 1/2 needs ≥ 10 upright |
| fcc(111) | 4 | 1/1/2 | 4/4 = 1.000 | 4 | 2 | 3 | 0 (construction) | 8/12 = 0.667; above 1/2 needs ≥ 4 upright |

*OOH bound: 2|d_lat(O₂)| = 2.58 Å; mirror shift of H = 1.80 Å; shortest in-plane lattice vector = 3.1066 Å (rutile(110)); holds for all families: True.

**Rule.** A family is HELD for *O (and, separately, for *OH) when the retained count is at least k, with X = k/N. It is FALSIFIED when the rate is at or below 1/2. At that point the enumerator no longer places a majority of upright configurations on a force-zeroing element, which is the :1923 branch "site selection is not a propagation mechanism". A count in the gap is reported as NOT HELD / NOT FALSIFIED. X is the minimum the site-type argument below allows.

**Construction checks, not predictions.** A violation makes that family VOID until it is explained.
- **\*O = \*OH:** H sits 0.98 Å along the normal. An operation that preserves the normal and fixes O mod lattice also fixes H.
- **Bent \*OOH retains nothing on any family:** the enumerator places OOH rigidly, with O₂ displaced 1.29 Å laterally from O₁ and H displaced (1.29, 0.9) Å. For O₂, |Rd − d| ≤ 2|d_lat(O₂)|, which is shorter than the shortest in-plane lattice vector of every cell (bound line above). So R fixes d(O₂), and R is either the identity or the vertical mirror containing the O–O direction. That mirror moves H by a distance that is not a lattice vector, so only the identity remains.

**Site-type argument for \*O and \*OH.** For an upright adsorbate, retention means the site lies on a vertical mirror or two-fold axis of the clean slab. With V surface atoms per cell, the Delaunay triangulation has E = 3V edges and F = 2V faces per cell. The multiplicities of the bridge classes must sum to E, and a class with multiplicity below the group order sits on a symmetry element.

- **perovskite(001), p4mm:** multiplicities are 1, 2, 4 or 8, and V = 3 gives E = 9. Three bridge classes cannot include a general class of 8, since 8 + 1 + 1 > 9. Ontop Ti is a 4mm site and ontop O a 2mm site. Every TiO₂-net triangle has a right angle, which the enumerator's obtuse test (cos < 1e-5) excludes; this is consistent with the 0 hollows. Prediction: 5 of 5.
- **fcc(111), p3m1 in the 2×2 cell:** multiplicities are 4 (3m), 12 (m) or 24, and V = 4 gives E = 12 and F = 8. The single bridge class of 12 must be m, and two hollow classes summing to 8 must both be 3m (fcc and hcp). Ontop is 3m. Prediction: 4 of 4.
- **spinel(001), p2mm:** multiplicities are 1, 2 or 4, and V = 6 gives E = 18. Eight bridge classes must satisfy 4(8 − r) + m = 18 with r ≤ m ≤ 2r, which gives r ∈ {5, 6, 7} retained bridges. All 3 ontop sites are retained: each top-layer atom (octahedral Co, bulk −3m; O, bulk 3m) has exactly one vertical mirror, since of the three {110} mirrors through its three-fold axis only one contains [001]. Hollows are retained only when a mirror maps the triangle onto itself, or by coincidence, so 0 to 2 of 2 are retained. Prediction: at least 3 + 5 + 0 = 8 of 13.
- **rutile(110), a cross-check only:** the same count gives 3 ontop, 4 to 6 bridges and 0 to 1 hollows, so 7 to 10 of 10.

**What a miss would mean.** A miss would measure the enumerator-and-tolerance pipeline, which is what this census reports. Two premises remain open before the run; a third is now measured.

1. **Symmetric triangulation (open).** When four points are cocircular, Qhull keeps one diagonal. For a mirror-symmetric cyclic quadrilateral that is not a rectangle, the two diagonals have different midpoints, so the kept edge can fall in a general class, which lowers r below the bound.
2. **Same group for reduction and census (measured).** The enumerator's reduction group at symprec 0.1 is identical to the census group at 1e-3 on all four clean slabs (reduction-group table). **Open part:** position matching at 1e-2 per fractional coordinate could merge two symmetry-inequivalent sites only if their images lie within that tolerance in-plane.
3. **Exact positions (open).** spglib must recognise floating-point-exact positions in the vacuum-padded cells. The slanted c vectors of the rutile and Pt slabs already pass on the clean slabs.

**Disclosure.** The rutile(110) arm is non-blind. docs/43 :1902 records:
- clean slab Pmm2, 4 ops;
- *O and *OH retaining in 9 of 10 configurations (1 of 10 P1);
- bent *OOH P1 in 10 of 10.

The in-repo re-run is reported below. For upright adsorbates, the rate is nearly fixed by the clean-slab layer group and the site classes, so the blind arms test that argument and the pipeline rather than an open physical question.

## rutile(110) in-repo re-run (non-blind)

| adsorbate | retained / N | space group P1 | ontop | bridge | hollow | verdict |
|---|---|---|---|---|---|---|
| *O | 9/10 | 1 | 3/3 | 5/6 | 1/1 | HELD |
| *OH | 9/10 | 1 | 3/3 | 5/6 | 1/1 | HELD |
| *OOH | 0/10 | 10 | 0/3 | 0/6 | 0/1 | construction check: pass |
| pooled *O, *OH, *OOH | 18/30 | – | – | – | – | no verdict (reading) |

Reproduces docs/43 :1902 disclosure: True; slab rebuild max |Δ| = 0.0 Å; enumerator re-run max |Δ| = 0.0 Å.

The in-repo bridges fall inside the counting bound. Command, run from `src/`: `python -m s2.p_builder.run_census --families rutile110 --out ../results/s2_2026-09-16/p_builder_prestate/rutile_nonblind_rerun.json`.

## Atomate gate

**Procedure.** `python -m s2.p_builder.atomate_gate --out …` reads:
- **GitHub REST API, hackingmaterials/atomate:**
  - commits a7d5f316 and d2742a3b;
  - `atomate/vasp/workflows/base/adsorption.py` at a7d5f316, at its parent and at d2742a3b;
  - that file's history before a7d5f316, to find where the comment first appears;
  - `requirements.txt` and `setup.py` at d2742a3b;
  - every version of `adsorption.py` that the commits API lists on the default branch from a7d5f316 to the head, with the compare API confirming that a7d5f316 is an ancestor of the head.
- **pymatgen:** `sets.py` and `MPRelaxSet.yaml` at the pinned tag.
- **PyPI:** pymatgen's release list and the sdist of every release that setup.py's specifier admits and that was first uploaded before a7d5f316. Each sdist's sha256 is checked against PyPI's digest, and `sets.py` plus the YAML configs are read from the archive.
- **VASP wiki:** the ISYM page.

**How the record is checked.**
- Every GitHub file's git blob SHA-1 is recomputed from its bytes and must match the API's.
- The record keeps line numbers, blob SHAs and sha256 values; source files are not redistributed.
- `evaluate()` re-derives every check and the dated statement offline from `atomate_gate.json` (`--reevaluate`), and a test enforces this.
- **Gating checks** (1-5) test the statement at the two named commits.
- **Scope checks** (4b, 7) set the wording of the dated statement, which narrows automatically when either fails; a test covers that path.

| check | result | evidence |
|---|---|---|
| MPSurfaceSet sets ISYM 0 under the comment at a7d5f316 | True | `atomate/vasp/workflows/base/adsorption.py` class l.298 (base MVLSlabSet), comment l.327, `"ISYM": 0` l.329, `incar.update(self.user_incar_settings)` l.331; blob 762ccabf82bb |
| introduced by a7d5f316 on 2018-05-25 | True | a7d5f316ae5e, 2018-05-25T18:02:38Z, message "add isym"; parent b3a03e00645b has 0 ISYM lines |
| comment origin (qualifier) | earlier commit | 4b344da08c29, 2018-05-25T16:27:54Z, "added MPSurfaceInputSet" (class MPSurfaceInputSet(MVLSlabSet):) |
| d2742a3b workflow uses MVLSlabSet, no ISYM | True | d2742a3b0764, 2017-06-07T21:23:41Z; l.51 `vasp_input_set = vasp_input_set or MVLSlabSet(slab)`; ISYM lines 0 |
| MVLSlabSet at the pinned pymatgen sets no ISYM | True | requirements.txt l.4 `pymatgen==4.7.7`; v4.7.7 sets.py l.1034 `class MVLSlabSet(MPRelaxSet):`; ISYM in class 0, in MPRelaxSet.yaml 0, LHFCALC in yaml 0 |
| scope: every pymatgen release setup.py admits, before a7d5f316 | True | setup.py l.23 `pymatgen>=4.7.1`; 43 PyPI releases first uploaded before 2018-05-25T18:02:38Z (4.7.1 to 2018.5.22); sdist sha256 = PyPI 43/43; no ISYM in MVLSlabSet -> MPRelaxSet -> DictSet -> VaspInputSet or in MPRelaxSet.yaml, VASPIncarBase.yaml, vdW_parameters.yaml: 43/43 |
| VASP default ISYM = 2 | True (qualified) | VASP wiki ISYM rev. 26986: "ISYM = 1 if VASP runs with USPPs = 3 if LHFCALC =.TRUE. = 2 else" |
| default branch today | True | 2e541f297165 (2024-03-12T00:23:59Z), `"ISYM": 0` l.413 |
| scope: every default-branch version since a7d5f316 | True | 11 versions (a7d5f316 l.329, 08467fd0 l.337, eaedb3cb l.342, 44fc6b33 l.339, ee5cf5aa l.341, c648d286 l.340, 798b32fc l.339, 6a146733 l.421, 7bf7a856 l.413, dedcadd7 l.413, 2608d7a8 l.413); each has ISYM 0 under the comment and MPSurfaceSet as workflow default: 11/11; a7d5f316 → head ahead by 2443 commits; head blob = newest version: True |

GATE passed: True (checked 2026-09-17T03:11:24Z).

Dated statement, as worded by the checks:

> MPSurfaceSet, the default input set of atomate's adsorption workflow, sets ISYM = 0 in every version of atomate/vasp/workflows/base/adsorption.py on the default branch from a7d5f316 (2018-05-25) through 2608d7a8 (2022-09-20), 11 versions, unless the caller overrides it through user_incar_settings; the default-branch head 2e541f29 carries the last of them (checked 2026-09-17T03:11:24Z).
>
> At d2742a3b (2017-06-07) the workflow default was MVLSlabSet; no class in its chain (MVLSlabSet -> MPRelaxSet -> DictSet -> VaspInputSet) and no config it loads (MPRelaxSet, VASPIncarBase, vdW_parameters) sets ISYM in any of the 43 pymatgen releases admitted by setup.py's 'pymatgen>=4.7.1' and first uploaded to PyPI before 2018-05-25T18:02:38Z (4.7.1 to 2018.5.22; requirements.txt pinned 4.7.7), so under that default VASP's own ISYM default applied unless the caller set ISYM.

**Result: GATE PASSED; both scope checks pass.**

**Qualifiers.**
1. **Comment origin:** the comment "Should give better forces for optimization" was added earlier the same day, with the class then named MPSurfaceInputSet (4b344da0). ISYM was placed under it afterwards, so the comment was not written about ISYM.
2. **VASP default:** ISYM defaults to 2 only for PAW potentials without LHFCALC; it is 1 with USPPs and 3 with LHFCALC.
3. **Pin versus specifier:** at d2742a3b, `requirements.txt` pins pymatgen 4.7.7 while `setup.py` admits `pymatgen>=4.7.1`. Scope check 4b therefore covers every admitted release uploaded before 2018-05-25, not only the pin. Releases uploaded later were not checked for this statement.
4. **What the history does not show:** `user_incar_settings` is applied after the default (l.331), so a caller can override ISYM 0. The code history also does not show which atomate or pymatgen version any published calculation used. Montoya & Persson's Methods remain unread in the repo (:1902), so nothing is said about their calculations.

## Execution after the boundary commit

**Boundary paths.** The boundary commit must contain all of these:
- this document;
- `manifest.json`, `decision.json` and `denominators.json`;
- every file under `structures/`, `slabs/` and `configs/`, plus the prestate `.gitattributes`;
- every `src/s2/p_builder/*.py`.

`results/` is gitignored (`.gitignore:14`), so the prestate directory has to be force-added. Its `.gitattributes` stores those files byte for byte, so the sha256 values above survive a checkout under `core.autocrlf`.

**Refusal.** `run_census` refuses perovskite001, spinel001 and fcc111 unless `--allow-blind` is given and all of the following hold:
1. every boundary path is tracked;
2. the boundary commit, which is the earliest commit at which all of them exist, is unique;
3. no boundary path changed between that commit and HEAD (an edit to X, to the definition, to any code file or to this document blocks the blind run);
4. no boundary path has an uncommitted change.

These rules are tested in throwaway git repositories.

**Run.** Once allowed, it:
1. verifies manifest sha256 values for every census input, every code file (in both directions) and this document. A file that matches only after CRLF → LF normalisation is accepted and listed;
2. rebuilds each slab from its structure file and re-runs the enumerator, requiring agreement within 1e-6 Å;
3. applies the definition to the prestate configurations;
4. reads k and F from `decision.json`, reports the pooled rate with no verdict, and records HEAD and the boundary commit.

Command, from `src/`: `python -m s2.p_builder.run_census --allow-blind --out ../results/s2_2026-09-16/p_builder_census/census.json`.

## Limits

- **Mechanism only:** the rate describes where the enumerator places sites relative to clean-slab symmetry elements. It does not show that any relaxation stays there, and it is not a lock rate in any corpus.
- **Population:** each family has one termination and one adsorbate per cell with `repeat=[1,1,1]`. Coverage per top-layer metal atom therefore differs by family (slab table). The stoichiometric rutile(110) and A-layer spinel(001) terminations are outside the population, and so are the primitive-cell alternatives.
- **Enumerator reductions:** the population is the enumerator's output after its own near- and symmetry-reduction and its obtuse-hollow exclusion. Those removals are part of the registered call and are not counted separately.
- **Structures:** unrelaxed experimental refinements. The SrTiO₃ CIF records no temperature. Magnetism does not enter this geometric census.
- **Pymatgen version:** the version used for the 2026-08-15 run is not recorded. Counts and space groups agree with it under pymatgen 2026.4.16.
