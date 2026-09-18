### Structures

| family | source | space group | cell (Å) | literature | file |
|---|---|---|---|---|---|
| rutile(110) | hand-built (t2.py), = COD 9007541 | P 42/m n m | a = 4.4919, c = 3.1066, u = 0.3058 | Baur, W. H.; Khan, A. A., *Acta Crystallographica, Section B* 27, 2133-2139 (1971), 10.1107/S0567740871005466 | `structures/rutile_RuO2_handbuilt.cif` |
| perovskite(001) | COD 9006864 | P m -3 m | a = 3.90528 | Mitchell, R. H.; Chakhmouradian, A. R.; Woodward, P. M., *Physics and Chemistry of Minerals* 27, 583-589 (2000), 10.1007/s002690000103 | `structures/cod_9006864_SrTiO3.cif` |
| spinel(001) | COD 9005887 | F d -3 m :2 | a = 8.0821, O x = 0.2627 (origin 2) | Liu, X.; Prewitt, C. T., *Physics and Chemistry of Minerals* 17, 168-172 (1990); 301 K | `structures/cod_9005887_Co3O4.cif` |
| fcc(111) | COD 9008480 | F m -3 m | a = 3.9231 | Wyckoff, R. W. G., *Crystal Structures* 1, 7-83 (1963) | `structures/cod_9008480_Pt.cif` |

Bulk-cell setting: source cell as deposited (COD conventional cell; registered hand-built rutile cell); no primitive or standard-cell reduction before SlabGenerator.

### Slabs (registered SlabGenerator arguments)

| family | candidates (top-surface species) | selected | top layer: species depth Å (neighbours ≤ 2.3 Å) | atoms | surface cell (Å, °) | reduced in-plane basis (Å, °) | atom span / vacuum along normal (Å) | adsorbates per top-layer metal atom | clean-slab group (symprec 1e-3) |
|---|---|---|---|---|---|---|---|---|---|
| rutile(110) | [0] O2 Ru2; [1] O1 | [0] | Ru 0.000 (5), Ru 0.000 (4), O 0.000 (3), O 0.000 (3) | 18 (Ru6 O12) | 3.1066 × 6.3525, γ = 90 | 3.1066 × 6.3525, 90 | 8.295 / 17.115 | 1/2 (2 top-layer metal) | Pmm2, 4 ops (4 keep the normal) |
| perovskite(001) | [0] O2 Ti1 | [0] | Ti 0.000 (5), O 0.000 (2), O 0.000 (2) | 15 (Sr3 Ti3 O9) | 3.9053 × 3.9053, γ = 90 | 3.9053 × 3.9053, 90 | 9.763 / 17.574 | 1/1 (1 top-layer metal) | P4mm, 8 ops (8 keep the normal) |
| spinel(001) | [0] Co2 O2; [1] Co2 O4 | [1] | O 0.000 (3), O 0.000 (3), Co 0.103 (5), Co 0.103 (5), O 0.205 (3), O 0.205 (3) | 56 (Co24 O32) | 5.7149 × 8.0821, γ = 135 | 5.7149 × 5.7149, 90 | 15.257 / 17.072 | 1/2 (2 top-layer metal) | Pmm2, 4 ops (4 keep the normal) |
| fcc(111) | [0] Pt4 | [0] | Pt 0.000 (9), Pt 0.000 (9), Pt 0.000 (9), Pt 0.000 (9) | 16 (Pt16) | 5.5481 × 5.5481, γ = 60 | 5.5481 × 5.5481, 60 | 6.795 / 18.120 | 1/4 (4 top-layer metal) | R-3m, 48 ops (24 keep the normal) |

### Enumerator reduction group (clean slabs only)

Read from the installed pymatgen (`analysis/adsorption.py` sha256 `0f60b134f62b`): `find_adsorption_sites` defaults symm_reduce = 0.01, near_reduce = 0.01, no_obtuse_hollow = True; `symm_reduce` takes its operations from `SpacegroupAnalyzer(self.slab, 0.1)` and matches positions in fractional coordinates at atol = threshold: True.

| family | census group (symprec 0.001) | enumerator group (symprec 0.1) | operation sets identical | max translation difference (fractional) | symm_reduce match tolerance along a, b, c (Å) |
|---|---|---|---|---|---|
| rutile(110) | Pmm2, 4 ops | Pmm2, 4 ops | True | 0.0 | 0.031 / 0.064 / 0.359 |
| perovskite(001) | P4mm, 8 ops | P4mm, 8 ops | True | 0.0 | 0.039 / 0.039 / 0.273 |
| spinel(001) | Pmm2, 4 ops | Pmm2, 4 ops | True | 0.0 | 0.057 / 0.081 / 0.323 |
| fcc(111) | R-3m, 48 ops | R-3m, 48 ops | True | 0.0 | 0.055 / 0.055 / 0.432 |

### Bulk-cell setting: the primitive-input alternative (enumerator only, not in the population)

| family | primitive bulk sites | (hkl) normal, deposited cell | (hkl) normal, primitive cell | same frame | candidates: atoms, top species, reduced basis (Å, °), N (ontop/bridge/hollow), *OOH image contact (Å) |
|---|---|---|---|---|---|
| perovskite(001) | 5 (deposited 5) | (0.0000, 0.0000, 1.0000) | (0.0000, 0.0000, 1.0000) | True | [0] 15, O2 Ti1, 3.9053 × 3.9053 90, N = 5 (2/3/0), 2.707 |
| spinel(001) | 14 (deposited 56) | (0.0000, 0.0000, 1.0000) | (0.5774, -0.5774, -0.5774) | True | [0] 28, Co2, 5.7149 × 5.7149 60, N = 6 (2/4/0), 4.456; [1] 28, Co2, 5.7149 × 5.7149 60, N = 6 (2/4/0), 4.456; [2] 28, Co1 O3, 5.7149 × 5.7149 60, N = 9 (2/5/2), 4.456; [3] 28, Co1 O4, 5.7149 × 5.7149 60, N = 10 (3/4/3), 4.456 |
| fcc(111) | 1 (deposited 4) | (0.5774, 0.5774, 0.5774) | (-0.5774, -0.5774, -0.5774) | True | [0] 4, Pt1, 2.7741 × 2.7741 60, N = 4 (1/1/2), 1.641 |

### Adsorbate–image contacts (geometry only)

Shortest distance from an adsorbate atom to an adsorbate atom of an in-plane periodic image, minimum over the configurations; for reference the O₁–O₂ distance inside the registered OOH is 1.468 Å.

| family | *O (Å) | *OH (Å) | *OOH (Å, pair) |
|---|---|---|---|
| rutile(110) | 3.107 | 3.107 | 1.947 (O–O) |
| perovskite(001) | 3.905 | 3.905 | 2.707 (O–O) |
| spinel(001) | 5.715 | 5.715 | 4.480 (O–O) |
| fcc(111) | 5.548 | 5.548 | 4.295 (O–H) |

### Files named by path and sha256

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

### Denominators and X

| family | N per adsorbate (O = OH = OOH) | ontop/bridge/hollow | X for *O, *OH | HELD if retained ≥ | FALSIFIED if retained ≤ | gap | *OOH | pooled reading at the predicted minimum (not used) |
|---|---|---|---|---|---|---|---|---|
| rutile(110) | 10 | 3/6/1 | 9/10 = 0.900 | 9 | 5 | 6, 7, 8 | 0 (construction) | 18/30 = 0.600; above 1/2 needs ≥ 8 upright |
| perovskite(001) | 5 | 2/3/0 | 5/5 = 1.000 | 5 | 2 | 3, 4 | 0 (construction) | 10/15 = 0.667; above 1/2 needs ≥ 4 upright |
| spinel(001) | 13 | 3/8/2 | 8/13 = 0.615 | 8 | 6 | 7 | 0 (construction) | 16/39 = 0.410; at or below 1/2; above 1/2 needs ≥ 10 upright |
| fcc(111) | 4 | 1/1/2 | 4/4 = 1.000 | 4 | 2 | 3 | 0 (construction) | 8/12 = 0.667; above 1/2 needs ≥ 4 upright |

*OOH bound: 2|d_lat(O₂)| = 2.58 Å; mirror shift of H = 1.80 Å; shortest in-plane lattice vector = 3.1066 Å (rutile(110)); holds for all families: True.

### rutile(110) in-repo re-run (non-blind)

| adsorbate | retained / N | space group P1 | ontop | bridge | hollow | verdict |
|---|---|---|---|---|---|---|
| *O | 9/10 | 1 | 3/3 | 5/6 | 1/1 | HELD |
| *OH | 9/10 | 1 | 3/3 | 5/6 | 1/1 | HELD |
| *OOH | 0/10 | 10 | 0/3 | 0/6 | 0/1 | construction check: pass |
| pooled *O, *OH, *OOH | 18/30 | – | – | – | – | no verdict (reading) |

Reproduces docs/43 :1902 disclosure: True; slab rebuild max |Δ| = 0.0 Å; enumerator re-run max |Δ| = 0.0 Å.

### Atomate gate

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
