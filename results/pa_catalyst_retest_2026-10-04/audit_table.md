# Real-output audit: what the adapter and controller require against real QE 7.5 output

Zero SU: every row is computed from files already on this machine by `audit_real_outputs.py`; nothing ran on Anvil.
Corpora: CONTROL = the control call of job 21034683 (72 atoms, Hubbard U, 128 MPI, relax stopped after 3 evaluations);
SCF19 = 19 real `calculation='scf'` Hubbard XML files with deck and log (`runs/a0/pproj6`); FRESH21 / SEG21 = 21 real September
72-atom 128-rank fresh-SCF / one-step from-scratch relax logs; TINY = the four retained one-process H2 restart arms.

## 1. XML elements required by `read_qe_arm` (corrected adapter), per arm path

`found once / lookups` counts every `_one(parent, tag)` call made while the corrected adapter accepted the real files. Clean-stop path = CONTROL (control, candidate, resumed, negative and reseed arms all end as clean stops); fresh path = SCF19 (`calculation='scf'`, `expected_exit='normal_scf'`).

| parent | required child | clean-stop path (1 real XML) | fresh path (19 real XML) | result |
|---|---|---|---|---|
| atomic_structure | atomic_positions | 5 / 5 | 38 / 38 | PASS |
| atomic_structure | cell | 5 / 5 | 38 / 38 | PASS |
| bands | occupations | 1 / 1 | 19 / 19 | PASS |
| bands | smearing | 1 / 1 | 19 / 19 | PASS |
| basis | ecutrho | 1 / 1 | 19 / 19 | PASS |
| basis | ecutwfc | 1 / 1 | 19 / 19 | PASS |
| control_variables | calculation | 1 / 1 | 19 / 19 | PASS |
| control_variables | forc_conv_thr | 1 / 1 | 19 / 19 | PASS |
| control_variables | forces | 1 / 1 | 19 / 19 | PASS |
| control_variables | max_seconds | 1 / 1 | not used | PASS |
| control_variables | prefix | 1 / 1 | 19 / 19 | PASS |
| control_variables | restart_mode | 1 / 1 | 19 / 19 | PASS |
| convergence_info | scf_conv | not used | 19 / 19 | PASS |
| dft | functional | 1 / 1 | 19 / 19 | PASS |
| dftU | U_projection_type | 1 / 1 | 19 / 19 | PASS |
| dftU | lda_plus_u_kind | 1 / 1 | 19 / 19 | PASS |
| electron_control | conv_thr | 1 / 1 | 19 / 19 | PASS |
| electron_control | max_nstep | 1 / 1 | 19 / 19 | PASS |
| electron_control | mixing_beta | 1 / 1 | 19 / 19 | PASS |
| electron_control | mixing_mode | 1 / 1 | 19 / 19 | PASS |
| espresso | exit_status | 1 / 1 | 19 / 19 | PASS |
| espresso | general_info | 1 / 1 | 19 / 19 | PASS |
| espresso | input | 1 / 1 | 19 / 19 | PASS |
| espresso | output | 1 / 1 | 19 / 19 | PASS |
| espresso | parallel_info | 1 / 1 | 19 / 19 | PASS |
| general_info | creator | 1 / 1 | 19 / 19 | PASS |
| input | atomic_species | 2 / 2 | 38 / 38 | PASS |
| input | atomic_structure | 1 / 1 | 19 / 19 | PASS |
| input | bands | 1 / 1 | 19 / 19 | PASS |
| input | basis | 1 / 1 | 19 / 19 | PASS |
| input | control_variables | 1 / 1 | 19 / 19 | PASS |
| input | dft | 2 / 2 | 38 / 38 | PASS |
| input | electron_control | 2 / 2 | 38 / 38 | PASS |
| input | free_positions | 1 / 1 | 19 / 19 | PASS |
| input | ion_control | 1 / 1 | 19 / 19 | PASS |
| input | k_points_IBZ | 1 / 1 | 19 / 19 | PASS |
| input | spin | 2 / 2 | 38 / 38 | PASS |
| input | symmetry_flags | 1 / 1 | 13 / 13 | PASS |
| ion_control | ion_dynamics | 1 / 1 | 19 / 19 | PASS |
| k_points_IBZ | monkhorst_pack | 1 / 1 | 19 / 19 | PASS |
| output | atomic_structure | 1 / 1 | 19 / 19 | PASS |
| output | convergence_info | not used | 19 / 19 | PASS |
| output | forces | not used | 19 / 19 | PASS |
| output | total_energy | not used | 19 / 19 | PASS |
| scf_conv | convergence_achieved | 3 / 3 | 19 / 19 | PASS |
| species | mass | 5 / 5 | 47 / 47 | PASS |
| species | pseudo_file | 5 / 5 | 47 / 47 | PASS |
| species | starting_magnetization | 5 / 5 | 27 / 27 | PASS |
| spin | lsda | 1 / 1 | 19 / 19 | PASS |
| spin | noncolin | 1 / 1 | 19 / 19 | PASS |
| spin | spinorbit | 1 / 1 | 19 / 19 | PASS |
| step | atomic_structure | 3 / 3 | not used | PASS |
| step | forces | 3 / 3 | not used | PASS |
| step | scf_conv | 3 / 3 | not used | PASS |
| step | total_energy | 3 / 3 | not used | PASS |
| symmetry_flags | noinv | 1 / 1 | 13 / 13 | PASS |
| symmetry_flags | nosym | 1 / 1 | 13 / 13 | PASS |
| total_energy | etot | 3 / 3 | 19 / 19 | PASS |

Elements used only on one path: `step` records and `output` proposal (clean stop); `output/convergence_info`, `output/total_energy`, `output/forces` (fresh path).

## 2. XML attributes the adapter reads

| element | attribute | present in real QE 7.5 XML |
|---|---|---|
| espresso | Units | yes |
| creator | NAME | yes |
| creator | VERSION | yes |
| atomic_structure | nat | yes |
| atom | name | yes |
| atom | index | yes |
| forces | rank | yes |
| forces | dims | yes |
| free_positions | dims | yes |
| species | name | yes |
| Hubbard_U | specie | yes |
| Hubbard_U | label | yes |
| smearing | degauss | yes |
| dftU | new_format | yes |
| monkhorst_pack | nk1 | yes |
| monkhorst_pack | nk2 | yes |
| monkhorst_pack | nk3 | yes |
| monkhorst_pack | k1 | yes |
| monkhorst_pack | k2 | yes |
| monkhorst_pack | k3 | yes |

Element the frozen synthetic fixture invented and the frozen adapter required: `lda_plus_u`; present in any real QE 7.5 XML: **no** (24 real XML files scanned).

## 3. Deck strings that QE rewrites before they reach the XML (canonicalization map)

Source = cached official QE 7.5 source (retrieval receipts pin every file).

| key | rule | QE 7.5 source | cited text |
|---|---|---|---|
| diagonalization | map {"david": "davidson"} | PW/src/pw_init_qexsd_input.f90:477-481 | `IF (TRIM(ip_diagonalization) == 'david') THEN / diagonalization = 'davidson' / ELSE / diagonalization = ip_diagonalization / END IF` |
| disk_io | map {"default": "low"} | Modules/qexsd_input.f90:85-89 | `IF ( TRIM(disk_io) .EQ. 'default' ) THEN / disk_io_value="low" / ELSE / disk_io_value=TRIM(disk_io) / END IF` |
| verbosity | map {"default": "low"} | Modules/qexsd_input.f90:80-84 | `IF ( TRIM( verbosity ) .EQ. 'default' ) THEN / verbosity_value = "low" / ELSE / verbosity_value=TRIM(verbosity) / END IF` |
| functional | upper | PW/src/pw_init_qexsd_input.f90:203-211 (input_dft upper-cased; absent input_dft gives the pseudopotential functional, PBE here) | `IF ( TRIM(input_dft) .NE. "none" ) THEN / dft_name=TRIM(input_dft) / DO i=1, LEN(dft_name) / dft_name(i:i) = capital(dft_name(i:i)) / END DO / ELSE / dft_shortn` |
| smearing | smearing | PW/src/set_occupations.f90:135-157 schema_smearing | `FUNCTION schema_smearing( smearing ) / !------------------------------------------------------------------------ / ! Converts smearing to the standard value nee` |
| mixing_mode | verbatim | PW/src/input.f90:1163 (case-sensitive SELECT CASE) | `SELECT CASE( trim( mixing_mode ) )` |
| ion_dynamics | verbatim | Modules/input_parameters.f90:1099-1103 allowed list | `CHARACTER(len=80) :: ion_dynamics_allowed(12) / !! allowed options for ion\_dynamics. / DATA ion_dynamics_allowed / 'none', 'sd', 'cg', 'langevin', & / 'damp', ` |
| occupations | verbatim | PW/src/pw_init_qexsd_input.f90:449 ip_occupations | `CALL qexsd_init_bands(obj%bands, nbnd_pt, smearing_loc, degauss/e2, ip_occupations, tot_charge, ip_nspin)` |
| calculation | verbatim | Modules/qexsd_input.f90:92-93 TRIM(calculation) | `CALL qes_init (obj,tagname,title=TRIM(title),calculation=TRIM(calculation),& / restart_mode=TRIM(restart_mode),prefix=TRIM(prefix),        &` |
| restart_mode | verbatim | Modules/qexsd_input.f90:92-93 TRIM(restart_mode) | `CALL qes_init (obj,tagname,title=TRIM(title),calculation=TRIM(calculation),& / restart_mode=TRIM(restart_mode),prefix=TRIM(prefix),        &` |
| prefix | verbatim | Modules/qexsd_input.f90:92-93 TRIM(prefix) | `CALL qes_init (obj,tagname,title=TRIM(title),calculation=TRIM(calculation),& / restart_mode=TRIM(restart_mode),prefix=TRIM(prefix),        &` |
| U_projection_type | verbatim | PW/src/pw_init_qexsd_input.f90:396 ip_hubbard_projectors | `U_PROJECTION_TYPE=ip_hubbard_projectors, U=hubbard_U_, Um = hubbard_Um_, U2=hubbard_U2_,&` |

Effect on real files (frozen adapter with only the dry-run's one-line `lda_plus_u` patch, versus the corrected adapter), real control XML, deck with one extra explicit assignment:

| deck assignment | expectation | frozen + dry-run patch | corrected adapter |
|---|---|---|---|
| `diagonalization = 'david'` | QE writes davidson | REFUSED: XML source setting differs: diagonalization | ACCEPTED |
| `disk_io = 'default'` | QE writes low | REFUSED: XML source setting differs: disk_io | ACCEPTED |
| `verbosity = 'default'` | QE writes low | ACCEPTED | ACCEPTED |
| `input_dft = 'pbe'` | QE writes PBE | REFUSED: XML functional differs from pinned PBE source | ACCEPTED |
| `diagonalization = 'cg'` | real XML says davidson: must be refused | REFUSED: XML source setting differs: diagonalization | REFUSED: XML source setting differs: diagonalization |
| `mixing_mode = 'plain'` | real XML says local-TF: must be refused | REFUSED: XML source setting differs: mixing_mode | REFUSED: XML source setting differs: mixing_mode |

## 4. Log literals and regular expressions (match counts per file: min-max over the corpus)

| item | role | CONTROL stdout (1) | SEG21 (21) | FRESH21 (21) | SCF19 pproj6 logs (19) | TINY resumed (1) | TINY scratch negative (1) | TINY clean stop (1) |
|---|---|---|---|---|---|---|---|---|
| QE banner | read_qe_arm banner == ['7.5'] (ADP read_qe_arm) | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| clean shutdown | read_qe_arm requires JOB DONE. | 1 | 0-1 | 0-1 | 1 | 1 | 1 | 1 |
| MPI processes | _raw_parallel mpi_processes | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| threads per MPI | _raw_parallel threads_per_mpi | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| processor cores | _raw_parallel processor_cores | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| k-point pools | _raw_parallel kpoint_pools | 1 | 1 | 1 | 1 | 0 | 0 | 0 |
| proc/nbgrp/npool/nimage | _raw_parallel band-group | 1 | 1 | 1 | 1 | 0 | 0 | 0 |
| ELPA sub-group | _raw_parallel elpa_subgroup (128-rank only) | 1 | 1 | 1 | 0 | 0 | 0 | 0 |
| first SCF threshold | read_qe_arm thresholds[0] | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| pseudopotential read | _raw_upf_reads | 5 | 5 | 5 | 2-3 | 1 | 1 | 1 |
| pseudopotential MD5 | _raw_upf_reads | 5 | 5 | 5 | 2-3 | 1 | 1 | 1 |
| converged SCF energy | log/XML energy binding | 3 | 0-1 | 0-1 | 1 | 7 | 5 | 1 |
| force block header | log/XML force binding | 3 | 0-1 | 0-1 | 1 | 7 | 5 | 1 |
| force row | log/XML force binding rows | 216 | 0-72 | 0-72 | 18-21 | 14 | 10 | 2 |
| SCF-cycle counter | controller SCF_CYCLE; adapter scf_counts | 3 | 0-1 | 0 | 0 | 6 | 4 | 1 |
| BFGS-step counter | adapter optimizer_counts | 3 | 0-1 | 0 | 0 | 6 | 4 | 1 |
| proposal geometry | adapter logged proposals | 3 | 0-1 | 0 | 0 | 7 | 5 | 1 |
| user stop | adapter STOP (clean_stop only) | 1 | 0 | 0-1 | 0 | 0 | 0 | 1 |
| optimizer reset at startup | adapter startup_history_deleted / negative control | 0 | 0-1 | 0 | 0 | 1 | 2 | 0 |

Reading: 0 where a literal is not expected (no ionic cycle in a fixed-geometry scf; no `K-points division` / ELPA line in a serial run; no stop line in a normal run) is correct; `0-1` in the stalled-or-converged corpora is the per-file spread.

## 5. Failure regular expressions on real logs (files that hit)

| corpus | files | adapter FAILURE | controller FAILURE | controller TIME_FAILURE | controller HEA4 iteration >= 127 |
|---|---|---|---|---|---|
| CONTROL stdout (relax, clean stop) | 1 | 0 | 0 | 0 | 0 |
| SEG21 (from-scratch relax, one step) | 21 | 0 | 0 | 20 | 0 |
| FRESH21 (scf, 72 atoms) | 21 | 0 | 0 | 0 | 6 |
| SCF19 pproj6 logs (scf) | 19 | 0 | 0 | 0 | 0 |
| TINY resumed (restart_mode='restart') | 1 | 0 | 0 | 0 | 0 |
| TINY scratch negative | 1 | 0 | 0 | 0 | 0 |
| TINY clean stop | 1 | 0 | 0 | 0 | 0 |

TIME_FAILURE hits in SEG21 are the phrase `The maximum number of steps has been reached` that QE prints when `nstep=1` is exhausted; the registered arms use `nstep=30` with an EXIT stop, and the real control never printed it. HEA4 hits in FRESH21 are the 6 of 21 real fresh SCFs that stalled at iteration 127 (they are the HOLD path of the trial).

## 6. Cross-arm XML identity on real files

- TINY arms (clean stop, continuous, resumed with `restart_mode='restart'`, from-scratch negative): XML identity equal across all four: **True**.
- Real relax (catalyst control) versus real scf (Mn slab) `<input>` fields whose values differ: `/control_variables/calculation, /control_variables/max_seconds, /control_variables/nstep, /control_variables/outdir, /control_variables/prefix, /control_variables/pseudo_dir, /dft/dftU/Hubbard_U, /dft/dftU/U_projection_type, /electron_control/max_nstep, /free_positions, /k_points_IBZ/monkhorst_pack`.
  Of these, `calculation`, `max_seconds`, `nstep`, `outdir`, `prefix`, `pseudo_dir` are the declared operational exclusions of the cross-arm identity; the rest (`Hubbard_U`, `U_projection_type`, `max_nstep`, `free_positions`, `monkhorst_pack`) are set by the two different decks. Fields present on one side only: none.
- No real relax/scf pair from the same deck exists locally, so fresh-versus-control identity on the catalyst deck itself is inferred from the above plus the QE source (`read_namelists.f90` fixval changes only ion_dynamics for `relax`, which the deck sets explicitly; `&IONS` is read for `scf` as well), not observed.

## 7. Outcome of the corrected adapter on every real pair

- CONTROL clean-stop path through `read_qe_arm`: **ACCEPTED** (3 evaluations, SCF counters [1, 2, 3], optimizer counters [0, 1, 2], exit status 255, first threshold 1e-06 Ry, runtime 128 MPI / 8 pools / ELPA [4, 4]).
- SCF19 fresh path through `read_qe_arm(expected_exit='normal_scf')`: **19 of 19 accepted** (4 with real UPF reads; the runtime-header check is stubbed because those runs used 128 ranks / 4 pools / serial diagonalization, not the registered layout).
- Frozen adapter (byte-identical copy of the pin `25546421...`) on the same real files: control `_check_xml_input` -> **REFUSED: one XML lda_plus_u required**; scf decks -> 19 of 19 (ortho-atomic projector outside the registered scope).
