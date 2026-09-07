# HEA-DFT — fixed-geometry DFT on the retained rutile(110) high-entropy oxide slab geometries: the branch panel and the fidelity pilot

**Status: DRAFT — a proposal; nothing here is registered, no deck is licensed, every entrant
slot is blank.** Built 2026-09-06 to the two unnumbered proposals of the same date
(`docs/cr-site-chain-readout-2026-09-06.md:30-40`, `docs/site-evidence-continuation-2026-09-06.md:33-45`).
Every threshold below is INHERITED from a deposited or banked number and carries no new value;
every choice that is not inherited is marked **Proposed** and carries a blank entrant slot of the
form `[HEA-<n> 2026-09-__: ____]`. Until those slots are filled in a dated docs/43 line, both
manifests carry a `NOT LICENSED` notice and `anvil/47_submit_a0.sh` refuses them
(anvil/47_submit_a0.sh:54-61; docs/66:98-104).

**Written after.** This draft is written after the site-evidence arc of 2026-09-06 produced the
geometries it uses (commits 8f16868, fefdde1, 6044a6e; `results/cr_site_chains_2026-09-06/`),
after those geometries and their model energies had been read, and after docs/76:290 closed "any
MLIP re-screen" (docs/76:5: not a registration). It re-opens that item as an explicit new research
choice, which is the entrant's to make by the dated line of §9 — the form docs/43:2567-2568
prescribes for a line written after its premise is known. The registered MLIP prohibitions
(docs/43:1943, :1957) reach fine-tuning and external-corpus scans, not inference on in-house
structures.

## 0. What exists in the tree as of this draft

| object | path | state |
|---|---|---|
| deck writer | `src/dft/hea_deck.py` | clones the banked 2x1v namelists verbatim; asserts exact coordinate round-trip, UPF preflight membership, species counts, no CR bytes; refuses differing overwrites |
| geometry integrity | `src/dft/hea_geometry.py` | minimum-image distances and the anomaly class of every state (§2b), printed into both manifests and by the readout |
| panel builder | `src/dft/build_hea_panel.py` | deterministic; `--check` re-renders and compares without writing; verifies every source sha256 against `results/cr_site_chains_2026-09-06/verification.json` |
| pilot builder | `src/dft/build_hea_pilot.py` | `--census/--formula/--seed/--site [--states] [--reuse]` for any screen-diagnostic-v1 result; `--retained` exercises the two retained chains; refuses an `--out-root` outside `runs/` before writing |
| cost model | `src/dft/hea_cost_model.py` -> `runs/hea/COST_MODEL.md` | calibrated on three banked np = 128 SCFs; iteration count from a survey of every banked nspin = 2 slab output; planning / floor / ceiling per deck, memory, billing |
| panel decks | `runs/hea/branch_panel/<label>__{atomic,ortho}.in`, 10 files, nat 75 | md5 in `runs/hea/m_branch_panel.txt:66-75` |
| pilot decks | `runs/hea/pilot_retained/<formula>__s<seed>_site<i>/<state>__{atomic,ortho}.in`, 12 files, nat 72/74/73 | md5 in `runs/hea/m_pilot_retained.txt:78-89`; the four OOH states are the panel decks (§2c), listed at `:56-59` |
| manifests | `runs/hea/m_branch_panel.txt`, `runs/hea/m_pilot_retained.txt` | `NOT LICENSED FOR SUBMISSION`; `# SUBMIT WITH EXCLUDE=a024,a049,a050,a088,a196,a220,a223,a171,a120,a200`; `# NP=128 NCONC=1`; rows at nk = 8 |
| readout | `src/dft/hea_panel_readout.py` | scores nothing yet: exits 3 while any leg is PENDING; writes `docs/figs/hea_panel_readout.json` once every leg is terminal (§4.0) |
| tests | `tests/test_hea_panel.py` | 27 tests: deck round-trip, k-mesh rule against `qe_slab.kgrid_from_cell`, geometry classes, submitter greps, reuse, cost calibration and survey, readout on synthetic fragments including realistic non-convergence |
| commit | — | **none of the above is committed** (HEAD f315f83 carries no `runs/hea/`, no `src/dft/hea_*.py`, no `tests/test_hea_panel.py`, not this file); §9 step 1 |
| run directories on Anvil | — | **not created.** |
| submitted | — | **nothing.** No sbatch was run. |

## 1. Lineage

- The multifidelity plan of docs/22 named an SQS / small-ordered-approximant tier for the top HEAs
  (`docs/22-multifidelity-dft-calibration.md:89-92`). That tier never executed: every QE run in
  `runs/` is a single-metal endmember (nat 18-40, ntyp <= 4; `runs/*_slab/manifest.json`,
  `runs/*_anchor/manifest.json`), and no deck with more than one distinct metal element exists.
- Held-out DFT points for the HEA screen: **zero** (`docs/40:34`). The validation of docs/36 is
  seven endmember eta values against MACE (`docs/36-screen-validation-and-stability-gate.md:16`:
  rho +0.8571, p 0.0238, eta MAE 0.130 V; the exact `mae_eta` 0.12955764753597102 is in
  `results/ranking_adequacy_2026-09-06/inputs/r4_validate.json`); that comparison is
  MACE-relaxed against DFT-relaxed geometries, not a fixed-geometry one.
- The 2026-09-06 chains retained full coordinates for the first time: an equiatomic Cr site whose
  builder-start OOH record sits 31.10 meV above the selected metal-contacted OOH, and a leader
  Cr site whose selected OOH record is an O2 fragment with H transferred to slab O56, 2.28 eV below
  the builder-start record (`results/cr_site_chains_2026-09-06/dft_branch_panel.json:8-63`;
  `docs/cr-site-chain-readout-2026-09-06.md:32-33`). What those records are geometrically is in
  §2b: three of the five panel states carry no adsorbate-metal contact at all. The panel JSON names
  the four geometries and the optional fifth, lists eight protocol fields as unspecified, and
  records `DFT_executed: false` (`:4`, `:61-71`).
- The flagship projector result makes the Hubbard projector a declared confound for any DFT number
  on these slabs: 1x1 Cr U = 7.15 |d-eta| 0.48685617462435893 V (133.5 % constants), and in the
  adopted 2x1v cell +0.17251637919980567 V FIRES with the legs agreeing on the potential-limiting
  step (`docs/figs/pproj_cell_readout.json` for the full-precision values; printed as 0.4869 and
  +0.1725164 at `docs/84-pproj-cell-readout-2026-09-04.md:35-38`, `:23`); across six metals the
  split is MIDDLE BAND, 3 of 5 (`docs/83-pproj6-readout-2026-09-04.md:27-29`). Both projectors
  therefore run on every geometry here, as a paired comparison that preserves every other choice
  (`docs/site-evidence-continuation-2026-09-06.md:43`).

## 2. What runs

Fixed-geometry SCFs only (`calculation = 'scf'`); nothing relaxes; no gas-phase deck is built
(the pilot readout uses the banked `runs/Cr_slab/H2O.out` and `H2.out`, §4.2).

### 2a. Branch panel — `runs/hea/branch_panel/`, A8.8-isolated from every banked run directory, ten decks

| label | pair / role | what the geometry is (§2b) | geometry source (positions_A, full precision) | sha256-banked export | MACE E (eV) |
|---|---|---|---|---|---|
| `equiatomic_pull2.10` | pair 1 state A | selected `*OOH` on Cr16, intact (Cr-O 1.975 A) | `equiatomic_ooh_replay.json /attempts/2/geometry` | `ooh_readout/equiatomic_pull2.10.extxyz` bbdf0443… | -432.4724969265869 |
| `equiatomic_builder` | pair 1 state B | HO2 radical in the cell, nearest metal 3.676 A: desorbed | `equiatomic_ooh_replay.json /attempts/0/geometry` | `ooh_readout/equiatomic_builder.extxyz` a08e3796… | -432.4413992175864 |
| `leader_builder` | pair 2 state A | HO2 radical in the cell, nearest metal 4.557 A: desorbed | `leader_ooh_replay.json /attempts/0/geometry` | `ooh_readout/leader_builder.extxyz` 6167100171… | -454.5660460881911 |
| `leader_pull2.10` | pair 2 state B | O2 in the cell (O-O 1.230 A, nearest metal 3.400 A) + H on slab O56 | `leader_ooh_replay.json /attempts/2/geometry` | `ooh_readout/leader_pull2.10.extxyz` ed8af255… | -456.8478789461918 |
| `leader_pull1.70` | optional control | O2 in the cell (O-O 1.238 A, nearest metal 3.931 A) + H on slab O68 | `leader_ooh_replay.json /attempts/1/geometry` | `ooh_readout/leader_pull1.70.extxyz` b3a2a1c9… | -456.12184613969964 |

each as `<label>__atomic.in` and `<label>__ortho.in`. Pair differences of record, copied from the
panel: equiatomic `MACE_E_B_minus_E_A_eV` = 0.031097709000505347 (states [pull2.10, builder]);
leader = -2.281832858000712 (states [builder, pull2.10]); optional
`MACE_E_O68_minus_E_O56_eV` = 0.726032806492185. **The reference of each pair is fixed here as
state A = the first state the panel lists**, so dE = E(B) − E(A) in both pairs; the panel's own
ordering flips which geometry is the selected endpoint between the pairs, and the readout carries
the state names on every row so no sign is read without them. In the words the labels earn: pair 1
is `*OOH(Cr16)` against HO2(g)-in-cell, pair 2 is HO2(g)-in-cell against O2(g)-in-cell + OH_b, and
the control is O2(g)-in-cell + OH_b on O68 against the same on O56.

All five geometries: 75 atoms (24 cations, 48 O, then proximal O, distal O, H), pbc T T T, 28 fixed
atoms [0-7, 24-39, 44-47] with `if_pos 0 0 0`, cell from `cell_A` (equiatomic 5.9455 x
12.601349947525463 x 25.20269989505093 A; leader 5.855999434240528 x 12.511759014755889 x
25.023518029511784 A).

### 2b. Geometry integrity of every state (minimum image on the retained cell; `src/dft/hea_geometry.py`)

Distances in A; `h` = height above the topmost slab metal; nearest metal by symbol and index.
Thresholds are the exploratory audit thresholds the chains were classified with
(`results/cr_site_chains_2026-09-06/paired_readout/readout.json:269-277`: O-H <= 1.25, H-slab-O
<= 1.25, metal contact <= 3.0 A — the desorption cut of `src/hea_oer/data.py:20`). The anomaly
class uses the vocabulary of the adsorbate-integrity screens of record (desorption, dissociation /
migration, normal); every row is re-derived at build and printed in the manifests
(`m_branch_panel.txt:26-33`, `m_pilot_retained.txt:37-40`, `:47-50`).

| state | O-O | H-O_p | H-O_d | H-nearest slab O | O_p-M | O_d-M | h(O_p) | class | free species implied |
|---|---|---|---|---|---|---|---|---|---|
| `equiatomic_pull2.10` | 1.372 | 1.856 | 0.993 | 3.644 (O64) | 1.975 Cr16 | 2.781 Cr16 | +1.86 | `*OOH` adsorbed, intact — NORMAL | — |
| `equiatomic_builder` | 1.343 | 1.881 | 1.001 | 3.324 (O64) | 4.706 Cr16 | 3.676 Cr16 | +4.40 | HO2 radical in cell, no metal contact — DESORPTION | HO2(g) doublet, 1 Bohr mag |
| `leader_builder` | 1.339 | 1.881 | 1.002 | 4.870 (O57) | 4.557 Cr16 | 4.862 Ni18 | +3.67 | HO2 radical in cell, no metal contact — DESORPTION | HO2(g) doublet, 1 Bohr mag |
| `leader_pull2.10` | 1.230 | 3.665 | 3.303 | 0.971 (O56) | 3.400 Ni18 | 3.985 Cr16 | +2.61 | O2 in cell + H on slab O — DESORPTION + DISSOCIATION / H TRANSFER | O2(g) triplet, 2 Bohr mag |
| `leader_pull1.70` | 1.238 | 2.827 | 1.982 | 0.981 (O68) | 4.181 Cr16 | 3.931 Ni18 | +3.11 | O2 in cell + H on slab O — DESORPTION + DISSOCIATION / H TRANSFER | O2(g) triplet, 2 Bohr mag |
| pilot `Fe25Co25Ni25Cr25` OH / O | — | 1.001 / — | — | 1.772 (O57) / — | 1.809 Cr16 / 1.589 Cr16 | — | +1.77 / +1.59 | `*OH`, `*O` adsorbed — NORMAL | — |
| pilot `Ni31Cr29Cu5Mn35` OH / O | — | 0.987 / — | — | 1.874 (O56) / — | 2.005 Cr16 / 1.592 Cr16 | — | +1.14 / +1.59 | `*OH`, `*O` adsorbed — NORMAL | — |

Only one of the five panel states is an adsorbed OOH. The census flags the leader OOH as desorbed
(`m_pilot_retained.txt:44`, `desorbed ['OOH']`). Consequences carried below: the DFT single
points of four panel states contain an open-shell gas-phase fragment inside a ferromagnetic
nspin = 2 cell whose O starting magnetisation is 0.0 (named risk 9, §5), the surrogate has no spin
degree of freedom, and the leader chain's third state is not an `*OOH` for CHE purposes (§4.2).

### 2c. Fidelity pilot on the two retained chains — `runs/hea/pilot_retained/`, twelve decks

For `Fe25Co25Ni25Cr25` seed 2 site 0 (candidate e42c3cfa…, `equiatomic_result.json`) and
`Ni31Cr29Cu5Mn35` seed 0 site 0 (candidate 1362d44d…, `leader_result.json`): the relaxed clean
slab (`decoration_records[seed].relaxed_slab`, 72 atoms) and the winning OH (74) and O (73)
states (`per_site_records[seed, site].relaxed_states`), each in both projectors. **The OOH state
of each chain is byte-identical (except the `prefix` line) to a panel deck** — equiatomic OOH =
`equiatomic_pull2.10`, leader OOH = `leader_pull2.10` — and is not built or run twice: the builder
asserts the identity at render, the pilot manifest lists the four panel decks with their md5s
(`m_pilot_retained.txt:56-59`), and the readout reads the panel outputs for those states. MACE
energies, dG and eta of each chain are copied into `m_pilot_retained.txt:31-50`; the leader
chain's OOH winner migrated to Ni (index 18) and its site-evidence status is `failed` — it is kept
visible, not substituted (`docs/site-evidence-continuation-2026-09-06.md:35`).

The three-composition pilot of the same proposal (Fe25Co25Ni25Cr25, Ni34Fe6Cu29Co31,
Cu22Fe30Co32Mn15; two site slots each) is **not built**: no retained coordinates exist for the
second and third compositions (`results/r4_screen_box.json` rows carry no positions; §11), so their
census must run first; `build_hea_pilot.py` builds any such chain from its screen-diagnostic-v1
result without further code.

### 2d. Protocol of record, identical on all 22 decks

Every line inherited; the deck writer asserts that the namelists differ from
`runs/a0/cell/ref__2x1v__u715.in` only in prefix, nat, ntyp, the starting-magnetization block,
`electron_maxstep` and `max_seconds`:

| field | value | inherited from |
|---|---|---|
| functional / pseudopotentials | PBE, SSSP-Efficiency files of record: Cr `cr_pbe_v1.5.uspp.F.UPF`, Mn `mn_pbe_v1.5.uspp.F.UPF`, Fe `Fe.pbe-spn-kjpaw_psl.0.2.1.UPF`, Co `Co_pbe_v1.2.uspp.F.UPF`, Ni `ni_pbe_v1.4.uspp.F.UPF`, Cu `Cu.paw.z_11.ld1.psl.v1.0.0-low.upf`, O `O.pbe-n-kjpaw_psl.0.1.UPF`, H `H.pbe-rrkjus_psl.1.0.0.UPF`; masses 51.996 / 54.938 / 55.845 / 58.933 / 58.693 / 63.546 / 15.999 / 1.008 | `src/dft/qe_slab.py:35-47`; md5 on Anvil `anvil/pseudo_md5_preflight_2026-08-23.md:10-23` (Cu: present, never exercised on Anvil) |
| Hubbard U | `U Cr-3d 3.7000`, `U Mn-3d 3.9000`, `U Fe-3d 5.3000`, `U Co-3d 3.3200`, `U Ni-3d 6.2000`; no line for Cu | the MP-calibrated set of record, `src/dft/qe_slab.py:35-47`; S3 deck census (e.g. `runs/s3/Co/ref__2x1v.in:81-82`) |
| projector | `HUBBARD (atomic)` and `HUBBARD (ortho-atomic)`, every geometry in both | `runs/a0/cell/ref__2x1v__u715.in:81`; `src/dft/build_pproj_cell.py` (the two-line transformation) |
| spin | `nspin = 2`, ferromagnetic starts of record per species: Cr 0.6, Mn 0.5, Fe 0.5, Co 0.4, Ni 0.3, Cu 0.2, O/H 0.0 | `src/dft/qe_slab.py:35-47`; `runs/a0/cell/ref__2x1v__u715.in:22-24` |
| charge | neutral (no `tot_charge`) | every banked deck |
| cutoffs | `ecutwfc = 80.0`, `ecutrho = 640.0` Ry | `runs/a0/cell/ref__2x1v__u715.in:15-16` (locked by docs/23) |
| k-mesh | `4 2 1 0 0 0` from `kgrid_from_cell` on the actual cell (25/5.9455 -> 4, 25/12.6013 -> 2; 25/5.8560 -> 4, 25/12.5118 -> 2); `nosym = .true.`, `noinv = .true.` -> 8 k-points; nk = 8 (the largest divisor of 128 not above 8) | `src/dft/qe_slab.py:77-84`; `runs/a0/cell/ref__2x1v__u715.in:20-21` |
| smearing / SCF | `occupations = 'smearing'`, `smearing = 'mv'`, `degauss = 0.01`, `conv_thr = 1.0d-6`, `mixing_mode = 'local-TF'`, `mixing_beta = 0.3` | `runs/a0/cell/ref__2x1v__u715.in:17-19`, `:27-29` |
| `electron_maxstep` | 300 (banked 200, `runs/a0/cell/ref__2x1v__u715.in:30`) | **the one namelist value raised**; part of the HEA-4 slot (§7) |
| `max_seconds` | 165000 (the S3 value, ~45.8 h inside the 48 h cap) | `runs/s3/Co/ref__2x1v.in:9`; `anvil/42_s3_wave1.slurm` |
| boundary / dipole | none (no `tefield`/`dipfield`/`edir`), matching every banked slab | `src/dft/qe_slab.py:21-22` |
| `tprnfor`, `forc_conv_thr`, `nstep`, `&IONS bfgs` | carried verbatim from the template; inert in an scf | `runs/a0/cell/ref__2x1v__u715.in:6-8`, `:32-34` |
| species order | metals alphabetically, then O, then H (so `starting_magnetization(i)` indices follow that order) | this arm's convention; `src/dft/qe_slab.py:88-89` sorts alphabetically with O last, so there H falls between Cu and Fe for these compositions — the values per species are identical, only the index changes |

Coordinates: every `ATOMIC_POSITIONS` and `CELL_PARAMETERS` value is the shortest round-trip
representation of the retained float; re-parsing each deck reproduces `positions_A` and `cell_A`
exactly (asserted at build and in `tests/test_hea_panel.py`), and the sha256-banked extxyz exports
agree with the JSON to their 8-decimal precision. Launch shape: `anvil/47_submit_a0.sh` ->
`anvil/46_a0.slurm`, 128 ranks, `-nk 8`, `-N 1`, 48 h; the runner rewrites `outdir`/`pseudo_dir`
and runs `projwfc.x` inline on a converged point (A6.5(1)), whose Löwdin table §4.0 reads.

## 3. What the arm measures, and what it does not

**Measured.** (i) The DFT electronic energy difference between two retained geometries with
identical atom inventory, cell and constraints, beside the model's difference at the same
coordinates — for the near-degenerate `*OOH` / HO2(g)-in-cell pair on the equiatomic Cr site and for
the HO2(g)-in-cell / O2(g)-in-cell + OH_b pair on the leader Cr site; the acceptor comparison O68 vs
O56 as a control. (ii) A fixed-geometry DFT eta on the model's own relaxed chain, beside the model's
eta at the same coordinates, on the equiatomic chain; on the leader chain the AEM eta is undefined
(§4.2) and what is measured is the two adsorbed steps and the energy of the desorbed third state.

**The composition statistic these sites come from.** The screen's composition eta is
`eta_min` over the sampled sites (`src/hea_oer/adsorption.py:350`; 12 sites over 3 decorations per
composition, `results/r4_screen_box.json`: Fe25Co25Ni25Cr25 eta 0.4530565517906915 = eta_min,
eta_mean 1.046721011508203, eta_std 0.3285840051032546, winning seed 2; Ni31Cr29Cu5Mn35 eta
0.43999606379672596 = eta_min, eta_mean 0.9103271635814684, eta_std 0.3241490799729384, winning
seed 1). The equiatomic chain here IS that model-selected minimum (the census reproduces it,
0.4530565522419163 against 0.4530565517906915; `m_pilot_retained.txt:34-36`). The leader chain is
NOT its composition's winner: seed 0 site 0 (eta 0.9780789066094675) was chosen deliberately
because the historical seed-1 winning site cannot be reconstructed
(`docs/cr-site-chain-readout-2026-09-06.md:5`; §11). Consequence, pre-stated: a DFT point at a
model-selected minimum of twelve is expected to sit above the model's value by selection alone (an
extreme regresses under an independent evaluator), so the signed residual eta_DFT − eta_MACE on
the equiatomic chain is reported with that caveat attached and is not, on its own, a fidelity
verdict; the energy-blind comparison site the proposal asked for (`docs/site-evidence-continuation-2026-09-06.md:35`)
is the HEA-8 slot and its selection rule is undefined (§11).

**Not measured, not claimed.** No DFT minimum, no relaxation correction, no barrier, no
electrode-performance statement (`dft_branch_panel.json:3`); no re-ranking of any composition; no
statement about whether the deprotonated endpoint is physical — a single point on a model geometry
establishes only the DFT energy of that configuration. No banked number moves in any branch:
A7.1/A13/A12 verdicts, the six-metal box and the r4 ranking stay as banked
(`docs/43:1759-1761`: a re-run is a new measurement reported alongside, never a silent overwrite).

## 4. Pre-stated readouts — inherited bars only, nothing elective

`src/dft/hea_panel_readout.py` is to be committed at the boundary commit of §9 step 1, before any
output exists; it parses every bar from its source file at run time and refuses (exit 4) if any
cannot be found.

### 4.0 Leg states, and when the readout writes

A leg is **CONVERGED** (a `!` total energy and `JOB DONE`), **NOT CONVERGED** (pw.x printed
`convergence NOT achieved` or `Maximum CPU time exceeded` — pw.x prints no `!` line in either
case: `runs/s3/Co/ref__2x1v.replay.out` has 0 lines matching `^!`, one `JOB DONE`, and
`convergence NOT achieved after 500 iterations` at `:8023`), **KILLED** (a `<job>.KILLED` sidecar
written when the kill rule of §7 cancels the job), or **PENDING** otherwise. NOT CONVERGED and
KILLED are terminal and score NO NUMBER; the readout exits 3 only while a leg is PENDING and writes
`docs/figs/hea_panel_readout.json` once every leg is terminal, NOT CONVERGED / KILLED rows
included. Per leg the total and absolute magnetisation are printed; for the four desorbed panel
states (§2b) the Löwdin moment summed over the three adsorbate atoms (`<job>.lowdin.txt`, the
banked artefact of `src/dft/extract_lowdin.py`, or the `.projwfc.out`) is printed beside the
free-species moment, and the leg is flagged **SPIN-STATE UNRESOLVED** when |moment| differs from
it by 0.5 Bohr mag or more (a moment that rounds to a different integer) or when no table exists.

### 4.1 Branch panel (per pair, per projector)

- dE_DFT = E(B) − E(A) in eV (Ry x 13.605693122), beside dE_MACE of record.
- **Primary: band.** |dE_DFT − dE_MACE| <= **0.250 eV**, the MACE-MPA-0 single-point 15-point dG
  MAE (`docs/33-r3-mlip-evaluation.md:65`, the MACE-MPA-0 row), reported WITHIN / OUTSIDE.
- **Sign, scored only where it can discriminate:** sign(dE_DFT) against sign(dE_MACE) is SCORED
  only when |dE_MACE| > 0.250 eV — pair 2 (|−2.28| eV) and the control (0.726 eV) — and printed
  **UNSCORED** for pair 1, whose |dE_MACE| = 0.031 eV lies inside the band (any dE_DFT in
  (−0.219, +0.281) eV is WITHIN, and half of that interval has the opposite sign; a sign verdict
  there would say nothing about the model).
- **Projector agreement per pair:** sign(dE_atomic) = sign(dE_ortho), with dE_atomic − dE_ortho
  printed; both-WITHIN flagged.
- The optional control is read the same way against 0.726032806492185 eV.
- A pair with a NOT CONVERGED or KILLED leg is NOT CONVERGED (no number) in that projector and is
  never filled from the other projector.

### 4.2 Fidelity pilot (per chain, per projector)

- dG_OH, dG_O, dG_OOH from the DFT energies with `src/hea_oer/referencing.py` (ZPE/TS 0.35 / 0.05 /
  0.40 eV) and the banked gas references `runs/Cr_slab/H2O.out` (-44.04119711 Ry) and
  `runs/Cr_slab/H2.out` (-2.33323818 Ry) — same O/H files, 80/640 Ry, 12 A Martyna-Tuckerman box,
  nspin = 1, as every banked A0 row uses; eta and potential-limiting step from
  `src/hea_oer/descriptors.py` (4.92 eV, 1.23 V).
- **Primary:** |eta_DFT(fixed geometry) − eta_MACE| <= **0.164 V**, the MACE-MPA-0 eta MAE of the
  same `docs/33:65` row as the 0.250 eV band (single points on DFT geometries — the like-for-like
  protocol for a fixed-geometry arm), WITHIN / OUTSIDE per chain and projector; the
  potential-limiting step reported, not scored. The relaxed-pipeline validation MAE
  0.12955764753597102 V (`r4_validate.json` `mae_eta`; docs/36:16; MACE-relaxed against
  DFT-relaxed, n = 7) is printed beside it as a second column. Which of the two is the bar of
  record is the HEA-9 slot (§8); the draft proposes the docs/33 row.
- Per step: |dG_DFT − dG_MACE| against the 0.250 eV band above, WITHIN / OUTSIDE.
- **A chain whose OOH record is desorbed has no `*OOH` state.** For the leader chain (§2b:
  O2(g)-in-cell + H on O56; census `desorbed ['OOH']`) the readout prints its third-state energy as
  dE3 = E(third) − E(slab) − (2 E_H2O − 3/2 E_H2) **with no 0.40 eV `*OOH` correction**, labels it
  `NOT AN *OOH STATE`, declares the AEM eta **UNDEFINED and does not score it against the band**,
  and prints only the bridge-pathway lower bound max(dG1, dG2, dE3 − dG2) − 1.23 V with the fourth
  step (OH_b -> O_b + H+ + e−, O2 release) marked **UNMEASURED** — the `*O2 + H_b` bookkeeping of
  Svane & Rossmeisl 2022 (Angew. Chem. Int. Ed. 61, e202201146), restated at
  `src/hea_oer/site_integrity.py:15` and `:404-409`, requires that step for a limiting potential to
  exist, and here the fragment is not even adsorbed. The census eta of that chain
  (0.9780789066094675 V) stays visible, labelled as AEM bookkeeping on a non-`*OOH` state.
  dG_OH and dG_O of that chain are scored per step as above.
- **Rank order:** the order of eta_DFT across the chains scored beside the order of eta_MACE,
  IDENTICAL / DIFFERS with Kendall tau, only when two or more chains carry a scored eta; on the two
  retained chains that is NOT SCORED by construction (the leader chain is unscored), and on the
  three-composition pilot it is the pre-stated three-composition order.
- Every eta_DFT − eta_MACE residual carries the selection caveat of §3.

## 5. Named risks, pre-stated

1. **First multi-U-species nspin = 2 slab in the project.** ntyp reaches 6; no banked deck carries
   more than one U-bearing species (the ntyp = 4 decks are Ru1/Ru2 AFM splits). SCF convergence on
   a disordered five-3d-metal slab has no precedent here.
2. **SCF iteration count is the dominant cost uncertainty.** Over every banked nspin = 2 slab
   output (664 files; `runs/hea/COST_MODEL.md` §1b) the first SCF converged in 594 and never
   converged in 72; at this arm's mixing (local-TF, beta 0.3; n = 564) the median is 27
   iterations, the 90th percentile 42, the maximum 174; 76 of 594 banked SCFs exceed the 42
   planning count and 9 exceed the 126 ceiling count. The three calibration SCFs (22, 26, 30) sit
   at or below the median. None of this is a five-species slab.
3. **Ortho-atomic x nspin = 2 x five 3d species never run.** The ortho legs of record are Cr-only
   (2x1v) or single-metal 1x1; the planning ortho/atomic wall ratio 1.2167 is the one 2x1v OOH
   pair (`COST_MODEL.md` §1), and the 1x1 per-state ratios span 0.953 (OOH) to 1.609 (OH).
4. **Cu.** The Cu PAW is staged on Anvil and never exercised there (`anvil/pseudo_md5_preflight_2026-08-23.md:23`);
   its only banked outputs are Vast-era (`runs/Cu_slab/s0_OH.out`, md5 619f40885d92a09a85a8b37550532d0c,
   valence 11). One Cu atom is in every leader deck.
5. **SCF non-convergence precedent.** The Ru nspin = 2 ladder cost 5,216.7 SU for 0 of 16
   converged (`docs/76:214`); `electron_maxstep = 300` bounds one SCF at 7.1x the planning wall.
6. **Magnetic order.** All starts are ferromagnetic per species; antiferromagnetic or ferrimagnetic
   orders on these slabs are a named, unrun risk (the Mn AFM arm measured a null on the endmember,
   `docs/43:2361-2362`; nothing covers a mixed slab).
7. **Memory.** Planning envelope 87 GB total at 128 ranks (core-bound billing); the 3x ceiling
   (262 GB) exceeds the 237 GB node (`runs/hea/COST_MODEL.md` §3).
8. **Cost-miss precedent.** The q333 pair realised 5.8x its planning figure (`docs/43:4453-4456`);
   the ceiling here is 3x and the kill rule (§7) is what bounds a miss.
9. **Open-shell gas species inside a ferromagnetic slab cell.** Four of the five panel states hold
   a free HO2 radical (doublet) or a free O2 molecule (triplet) in the vacuum of an nspin = 2 cell
   started ferromagnetic on the metals with O at 0.0 (§2b). A fixed-geometry SCF may land the
   fragment in the wrong spin state, or delocalise its moment into the slab under the Marzari-
   Vanderbilt smearing; the model, which carries no spin degree of freedom, cannot. A DFT − MACE
   gap on pairs 1 and 2 therefore measures spin as well as surrogate fidelity, and the SPIN-STATE
   UNRESOLVED flag of §4.0 is printed on every such leg beside its number rather than used to
   exclude it.
10. **Gas-reference protocol.** The DFT eta uses nspin = 1 gas molecules against nspin = 2 slabs,
    as every banked row does; the model's own gas references are float64 MACE in a 12 A box.
    dG differences between DFT and MACE therefore carry both a slab and a gas-reference term.

## 6. Cost basis (`src/dft/hea_cost_model.py`; `runs/hea/COST_MODEL.md`)

Anchor: `runs/a0/cell/ref__2x1v__u715.out` — nat 36, 312 electrons, 187 KS states, 16 k-points,
npool 8, 303.54 MB/process, 32.33 GB total, 8m42.67s WALL for 22 iterations (~18.6 core-h);
calibration points `s0_OOH__2x1v_escape__u715` (nat 39, 325 e, 196 states, 6m29.41s / 26 iter) and
the 1x1 `s0_OH__u715_atomic` (nat 20, 163 e, 98 states, 3m5.39s / 30 iter). Extrapolated by cell
volume, KS-state count (pw.x rule `nbnd = NINT(1.2 NINT(nelec/2))`, checked on nine banked
outputs), per-pool k-load and ranks per pool; the envelope model (V x nbnd^2) is the planning
figure, the FFT-scaling model the floor; **42 iterations** (the 90th percentile of the banked
survey, risk 2), ortho x 1.2167 (the 2x1v OOH twin, `runs/a0/pproj_cell/s0_OOH__2x1v_escape__u715_ortho.out:2530`
against `runs/a0/cell/s0_OOH__2x1v_escape__u715.out:2515`), ceiling 3x = 126 iterations.
Node memory 237 GB from `anvil/logs/a0_20419733_{1,2}.out:17`; billing max(cores, ceil(mem_GB/2))
from `anvil/README.md:91`.

| cell | electrons | KS states | atomic planning / floor / ceiling (core-h) | ortho planning / floor / ceiling (core-h) | memory planning / ceiling (GB, 128 ranks) |
|---|---|---|---|---|---|
| equiatomic 75-atom (Cr6 Ni6 Fe6 Co6 O50 H) | 691 | 415 | 180.9 / 81.5 / 542.7 (planning wall 1.41 h) | 220.1 / 99.2 / 660.3 (1.72 h) | 87.2 / 261.5 |
| leader 75-atom (Mn8 Ni8 Cr7 Cu1 O50 H) | 674 | 404 | 166.5 / 77.1 / 499.4 (1.30 h) | 202.5 / 93.7 / 607.6 (1.58 h) | 82.4 / 247.2 |

Arm totals are per-deck sums over each deck's own geometry (`COST_MODEL.md` §4 lists all 22 rows
and the four reused OOH rows), and are the figures the manifests print
(`m_branch_panel.txt:49-53`, `m_pilot_retained.txt:61-65`; asserted equal in `tests/test_hea_panel.py`):

| arm | SCFs | planning (core-h) | floor | ceiling | 48 h cap the submitter prints (SU) |
|---|---|---|---|---|---|
| branch panel | 10 | 1909.0 | 873.8 | 5727.0 | 61,440 |
| pilot, two retained chains (slab, OH, O; OOH read from the panel) | 12 | 2255.7 | 1042.0 | 6767.2 | 73,728 |
| both | 22 | 4164.7 | 1915.8 | 12494.2 | 135,168 |

At planning memory every deck is core-bound (128 SU/h), so core-h = SU; at the equiatomic ceiling
memory billing rises to 131 SU/h and the job no longer fits one node. Balance context: 59,473.5 SU
on 2026-09-05 (`docs/88-a10-signature-sheet-2026-09-05.md:245`, `mybalance`) before the 11.41
core-h of the gate-(e) pair (`docs/90:352-355`) and the 317.4 core-h of the q333 pair
(`docs/43:4453-4456`). The realised figure is reported beside the planning figure in the readout.

> **Proposed:** planning 1909.0 core-h (panel) + 2255.7 (pilot) = 4164.7; ceilings 5727.0 + 6767.2 = 12494.2.
> `[HEA-7 2026-09-__: ____]`

### 6b. Running total of fixed-geometry SCFs (A6.6)

The A6.6 running total stood at ~380 licensed fixed-geometry SCFs after A12
(`docs/43:3468-3472`), plus 1 SCF and 1 hp.x job under A12b (`:3592-3597`), plus the 2026-09-05
small arms: 2 SCFs and 2 hp.x jobs for the CrO2 q333 pair (`:4384-4386`) and 2 SCFs for the
gate-(e) np = 128 pair (`:4400-4405`) — **~385 fixed-geometry SCFs licensed and 3 hp.x jobs**
(the hp.x jobs counted separately, as A12b.R7 does). This arm adds **22** fixed-geometry SCFs
and no relaxation, four fewer than the 26 states it scores because the four pilot OOH states are
the panel decks (§2c): **~407 if licensed**, ceiling 12,494 core-h ≈ 12,500 SU core-bound.

## 7. Per-SCF kill rule — Proposed as a slot

An SCF is cancelled, a `<job>.KILLED` sidecar written beside its `.out` naming the clause that
fired, and the leg scored KILLED (no number, §4.0) with no restart ladder, when either
(a) its wall exceeds 3x its own planning wall of `COST_MODEL.md` §4 (for the panel decks:
equiatomic atomic 4.24 h, ortho 5.16 h; leader atomic 3.90 h, ortho 4.75 h), or (b) it passes
**126** SCF iterations (3x the 42 planning count; 9 of 594 banked first SCFs went further) without
`convergence has been achieved`. The rule is applied by reading the live `.out` on Anvil; the
decks' `max_seconds = 165000` is the hard backstop, not the rule, and `electron_maxstep = 300`
(banked 200) is the deck value that lets a leg reach (b) rather than stop as NOT CONVERGED at
200 — both values are part of this slot.

> `[HEA-4 2026-09-__: ____]`

## 8. Entrant slots, collected

| id | decides | draft proposal |
|---|---|---|
| HEA-1 | Hubbard U set | the MP-calibrated set of record (Cr 3.7, Mn 3.9, Fe 5.3, Co 3.32, Ni 6.2, Cu none) — the set every banked 3d deck carries and the set MPtrj/MACE-MPA-0 were trained on; the alternative is the Wang–Ceder oxidation-fitted set (Cr 3.5, Mn 4.0, Fe 4.0, Co 3.3, Ni 6.4, Cu 4.0), which would be a second, paired arm and is not built |
| HEA-2 | projector | both, on every geometry (the flagship confound) |
| HEA-3 | spin start | ferromagnetic per-species starts of record; AFM/ferrimagnetic orders named unrun (§5.6); the open-shell fragments of §5.9 flagged, not excluded |
| HEA-4 | kill rule, `electron_maxstep` 300 | §7 |
| HEA-5 | which pairs run | pair 1 (`*OOH` vs HO2(g)-in-cell, equiatomic) and pair 2 (HO2(g)-in-cell vs O2(g)-in-cell + OH_b, leader), both projectors: 8 SCFs |
| HEA-6 | whether the proton-acceptor control runs | yes, `leader_pull1.70` in both projectors: +2 SCFs |
| HEA-7 | cost figure | §6 |
| HEA-8 | pilot scope and the comparison-site rule | the two retained chains now (12 SCFs, OOH from the panel); the three-composition pilot after its census retains coordinates; the energy-blind comparison site per chain is a slot whose rule is undefined (§11) |
| HEA-9 | eta bar of record | the docs/33:65 single-point eta MAE 0.164 V (like-for-like with a fixed-geometry arm) rather than the relaxed-pipeline 0.12955764753597102 V of `r4_validate.json`; both are printed either way (§4.2) |

Nothing above is registered until each slot carries a date and a decision.

## 9. Ordering, and the exact path from this draft to a licensed arm

The decks and manifests exist and are md5-manifested **before** any slot above is filled — the
P-PROJ-6 ordering (built at c2e9a18, licensed at 8aba0ae, then submitted; `docs/43:3459-3465`) —
so the objects submitted are provably the objects built. That ordering is checkable only through
commit hashes, and **as of this draft none exists**: HEAD f315f83 carries none of `runs/hea/`,
`src/dft/hea_*.py`, `tests/test_hea_panel.py` or this file. In order:

1. **The boundary commit.** One commit carrying `runs/hea/` (decks, both manifests, `COST_MODEL.md`),
   `src/dft/hea_deck.py`, `hea_geometry.py`, `build_hea_panel.py`, `build_hea_pilot.py`,
   `hea_cost_model.py`, `hea_panel_readout.py`, `tests/test_hea_panel.py` and this file, with
   `python src/dft/build_hea_panel.py --check`, `python src/dft/build_hea_pilot.py --retained --check`
   and `python -m pytest tests/test_hea_panel.py` green at that tree. Its hash is the blind boundary
   and is written into the dated line of step 2; the readout is therefore committed before any
   output exists by construction, not by assertion.
2. The entrant's dated line in a docs/43 addendum adopting or replacing HEA-1 … HEA-9, stating that
   it is written after the 2026-09-06 site-evidence arc and after docs/76:290, naming the boundary
   hash of step 1, and naming `runs/hea/m_branch_panel.txt` and `runs/hea/m_pilot_retained.txt` as
   LICENSED by that line, with the per-deck md5s unchanged (form of `docs/43:4380-4418`).
3. Deposit: the next Zenodo version of concept record 10.5281/zenodo.21963143 carrying that
   addendum, before the first governed job (`docs/43:1807`, `:3797-3798`).
4. The `NOT LICENSED` paragraph in each manifest replaced by the dated adoption line and the deposit
   DOI; every deck md5 left as printed; that edit committed and its hash recorded in the same line.
5. Stage `runs/hea/` to `$PROJECT/sts/runs/hea/` by tar + scp with md5 checked both ends and the LF
   fix (`anvil/README.md:226-231`), then from `$PROJECT`:

       EXCLUDE=a024,a049,a050,a088,a196,a220,a223,a171,a120,a200 bash anvil/47_submit_a0.sh $PROJECT/sts/runs/hea/m_branch_panel.txt 2
       EXCLUDE=a024,a049,a050,a088,a196,a220,a223,a171,a120,a200 bash anvil/47_submit_a0.sh $PROJECT/sts/runs/hea/m_pilot_retained.txt 2

   The trailing `2` is the array concurrency (`anvil/47_submit_a0.sh:20`, `%CONC` at `:112`): two
   87 GB jobs on separate nodes (`-N 1`, one job per node on `shared`). The manifests' directive
   `# NP=128 NCONC=1` is a different quantity: `47_submit_a0.sh:100` runs the driver's dry preflight
   as `bash $DRIVER $MANIFEST $NP 1`, and `src/dft/queue_r1.sh:96-104` refuses a manifest whose
   declared NCONC differs from that invocation's — so the directive must read NCONC=1 for any
   manifest submitted through 47, whatever concurrency the array runs at. The preflight also
   refuses stale `.out`, CRLF, missing UPF and a wrong-NP invocation.
6. After landing, pull the outputs and the `.lowdin.txt` tables by explicit list with md5 both
   ends, run `src/dft/mirror_audit.py` (a readout may not be countersigned while any
   `.projwfc.out` for its decks is unmirrored, `docs/43:4126-4128`), then the scorer; a
   LANDED/SCORED addendum with the realised cost beside the planning figure and a blank
   countersignature slot.

## 10. What this draft does NOT license

Nothing. No deck, no relaxation, no path calculation, no re-ranking, no change to any banked
verdict or band; not the Wang–Ceder U arm, not an AFM arm, not the three-composition pilot's census,
not a gas-phase re-run, not a re-relaxation of any panel state. A PENDING, NOT CONVERGED, KILLED or
SPIN-STATE UNRESOLVED outcome on any leg is reported as such; a disagreement in sign or an OUTSIDE
band on any pair is a result about the model at that geometry, not a rescue of, or a verdict on, any
registered prediction.

## 11. Where the tree does not match the notes this draft rests on

- **The panel's sign convention flips between pairs.** In pair 1 state A is the selected endpoint
  (pull2.10); in pair 2 state A is the builder. §2a fixes A = the first-listed state and the readout
  prints both state names on every row.
- **The panel's state labels understate what the geometries are.** "builder detached OOH" is a free
  HO2 radical with no metal within 3.6 A; "OO + H on slab O" is a free O2 molecule (O-O 1.230 A)
  with no metal within 3.4 A plus a protonated slab O (§2b). Both proposals treat these as branch
  endpoints; the adsorbate-integrity screens of record class them as desorption (and, for the O2
  states, H transfer), and this draft names them so.
- **The optional fifth geometry carries no extxyz path or sha in the panel JSON** (`:56-63`); the
  builder takes `ooh_readout/leader_pull1.70.extxyz` (sha256_lf b3a2a1c9…, `verification.json`) and
  asserts it against the JSON pointer.
- **No pass/fail criterion exists in the two proposals** for the pilot; the bars in §4 are
  inherited (docs/33:65, `r4_validate.json`), not invented; which eta bar is of record is HEA-9,
  and any different bar is HEA-slot territory, not an extraction.
- **The three-composition pilot cannot be built from retained records:** `results/r4_screen_box.json`
  rows carry no site_index and no coordinates; Cu22Fe30Co32Mn15 seed 0 has two Co-centred cus sites
  (0 and 3) on rebuild, so its nominal winning site is not uniquely recoverable, and the
  "deterministic energy-blind comparison site" rule is undefined (`docs/site-evidence-continuation-2026-09-06.md:35`).
- **The leader chain is not the leader's winning site.** The r4 winner used seed 1 (eta_min
  0.43999606379672596), whose rebuilt decoration has three Cr cus sites and no retained coordinates
  or per-site energies; seed 0 site 0 (eta 0.9780789066094675) is what exists.
- **The general slab writer's ordering differs.** `src/dft/qe_slab.py:88-89` sorts alphabetically
  with O last (H between Cu and Fe for these compositions); these decks use metals, O, H. Values
  per species are identical.
- **`electron_maxstep` is the one namelist value not inherited verbatim** (300 vs the banked 200;
  HEA-4).
- **The Cu preflight row is UNVERIFIABLE against a banked Anvil output** by the record's own
  wording (`anvil/pseudo_md5_preflight_2026-08-23.md:23`); the Vast-era `runs/Cu_slab/s0_OH.out:81`
  prints the same md5 619f40885d92a09a85a8b37550532d0c.
- **Four of the 26 states the readout scores are the same four decks twice** (pilot OOH = panel
  pull2.10, both projectors, both chains); they run once and are read twice (§2c).
