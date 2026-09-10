# HEA DFT recovery and historical winner audit — September 10, 2026

The next computation addresses the unresolved seed-0 exception and convergence failures while independently testing the actual historical seed-1 winning chain. The existing census continues on the local machine. Original attempts and scientific acceptance rules remain intact.

## Completed sensitivity and atomic diagnostic

All 316 verified SCF/projection, QC, runtime-input, clone and rank-stream files match remote SHA256 hashes: 309 were retrieved and seven already existed locally. Independent raw-data readout accepts five sensitivity endpoints and rejects the smearing pull endpoint for `IEEE_INVALID_FLAG`. The successful atomic reproduction passes independent raw SCF/projection QC, exact original runtime input, clone-receipt and all 128 rank-stream checks for both executables. It establishes a new accepted atomic pair with the existing tight pull endpoint, not a reclassification of the earlier flagged attempt.

| Fixed-geometry pair | F(pull) − F(builder), eV | Change from corresponding tight ortho reference |
|---|---:|---:|
| Ortho reference, 80/640 Ry | −2.129781595 | — |
| Ortho wavefunction cutoff, 100/640 Ry | −2.130125139 | −0.343544 meV |
| Ortho density cutoff, 80/800 Ry | −2.130180242 | −0.398647 meV |
| Ortho smearing width, 0.005 Ry | Unavailable | Pull endpoint rejected |
| Atomic clean reproduction + existing tight pull | −2.050015906 | Different projector; not a cutoff comparison |

The cutoff perturbations preserve total magnetization at the printed precision. The largest atom-projected Löwdin moment changes are 0.0003 and 0.0017 μB for the wavefunction and density controls, respectively. Maximum free-coordinate force-vector differences are 0.00131 and 0.00758 eV/Å. These small changes are consistent with continuity of the sampled electronic solutions; they do not prove a magnetic ground state. Free-coordinate residual forces remain about 1.41–1.45 eV/Å, far above the 0.05 eV/Å stationarity diagnostic. No relaxed energy, catalytic ranking or overpotential follows from these fixed-geometry tests.

The completed diagnostic plus sensitivity batch used 466.1333 allocated core-hours, including 78.4356 on the rejected smearing endpoint. Largest recorded MaxRSS was 165,257,868 K for the 100 Ry wavefunction-cutoff builder. Current 237G/node requests remain above this observed peak, but a denser mesh still needs its own memory assessment.

Evidence: `results/hea_sensitivity_2026-09-09/status_2026-09-10_verified/`, including paired readout, atomic replacement readout, transfer hashes, printed pseudopotential checks, scheduler accounting and executable identities. Optional projected-density-of-states files and full retained wavefunctions stay on Anvil; they are not needed for the paired QC readout.

## Next bounded experiments

| Arm | Calculations | Resource bound | Purpose |
|---|---:|---:|---|
| Smearing exception reproduction | 1 | 128 ranks × 4 h = 512 core-h | Repeat exact failed smearing input from its original accepted tight checkpoint, capturing every SCF/projection rank stderr stream. |
| Convergence probes | 4 | 128 ranks × 1 h each = 512 core-h | Two solver hypotheses for each repeatedly nonconvergent ortho state, each limited to 60 SCF iterations and max_seconds=3300. |
| Historical winner audit | 8 | 128 ranks × 4 h each = 4096 core-h | Clean/OH/O/OOH × atomic/ortho for the actual Ni31Cr29Cu5Mn35 seed-1/site-0 Cr winner, using the eight previously frozen validation inputs. |

Each array has concurrency one and no requeue. The convergence probes follow the smearing diagnostic with an `afterany` dependency; the winner array is independent. Thus at most two new DFT tasks run together. The combined allocation ceiling is 5120 core-hours, not a runtime forecast. The winner's inherited planning estimate is 1452.415 core-hours; earlier successful controls provide only approximate timing comparators for the other arms. Before preparation, the allocation showed 54,440.3 CPU SU and 4.5 TB free space.

The two failed states already plateaued through about 260–280 iterations under local-TF mixing with beta=0.1. Both new probe arms start independently from the same original failed follow-up checkpoint used by their previous recovery attempt. The precision arm sets `diago_thr_init=1e-10` and `diago_full_acc=.true.`; the mixing arm sets `mixing_beta=0.05` and `mixing_ndim=12`. Hamiltonian, geometry, pseudopotentials, 80/640 Ry cutoffs, 4×2×1 mesh, MV smearing 0.01 Ry and conv_thr=1e-6 Ry remain fixed. These are tests of competing numerical causes, not established fixes. A capped history remains a rejected scientific endpoint, even when it is informative about convergence.

Parameter meaning and convergence guidance: [QE input reference](https://www.quantum-espresso.org/Doc/INPUT_PW.html) and [QE convergence troubleshooting](https://www.quantum-espresso.org/Doc/pw_user_guide/node21.html). The actual histories motivate the choices; neither source guarantees success for these magnetic DFT+U states.

The winner audit can proceed before seed-0 numerical closure because it is an explicitly preliminary fixed-geometry comparison. It uses the historical chain, not a newly selected winner, and retains reconstruction/fragment identity and force diagnostics. A complete adsorption-energy or CHE readout also needs consistent gas references and both projector-specific chains; accepted SCF outputs alone do not validate the ranking.

## Continued independent work and dependencies

The local census snapshot at 19:48 UTC had 77 completed, four running and 22 queued tasks. CENSUS-1, the seven-endmember batch and CENSUS-2 were complete; CENSUS-3 remained active. The existing runner is retained. The frozen composition-selected validation plan can be materialized to a new dated snapshot after the current output availability check; no selection changes or duplicate census jobs are needed.

After the smearing result passes the same strict checks, assess the joint tighter setting and then the denser commensurate k mesh, including pool-layout baseline and memory evidence as needed. Constrained DFT relaxation follows numerical/state assessment. The frozen discovery/held-out chains and later pathway/active-phase work remain separate scientific stages. The old rejected attempts remain in every comparison history.

## Verification and launch

All 85 targeted tests passed: 28 smearing diagnostic, 16 convergence guard, nine convergence shell, and 32 winner guard/shell checks. Short temporary paths resolved Windows-only path-length failures without changing the scientific inputs or cluster paths. Verification is recorded in `results/hea_continuation_2026-09-10/`; submission and startup evidence will be appended after the held-job checks and release.

The convergence probes reuse the original failed density/occupation state and retain `startingwfc='atomic+random'`, as in the previous recovery protocol. They are new SCFs, not exact wavefunction restarts. Individual outcomes test solver hypotheses without uniquely identifying a failure cause.
