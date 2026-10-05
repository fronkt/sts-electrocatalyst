# Catalyst trial: QE 7.5 source boundary review

The proposed first/third evaluated-geometry observer has a source-supported
implementation path. This review does not establish that a catalyst adapter,
its tests, a checkpoint copy, or the actual trial has passed. The real H2 result
remains limited to the retained tiny restart-plumbing experiment.

## Stop event and acceptance boundary

Use the anchored output pattern
`(?m)^[ \t]*number of scf cycles[ \t]*=[ \t]*(\d+)[ \t]*$`.
The initial candidate targets cycle 1; continuous and resumed arms target global
cycle 3. Expected observed sequences are candidate `[1]`, continuous `[1,2,3]`,
and resumed `[2,3]`. Preserve each exact matching line and the EXIT receipt.
The printed BFGS count is additional history evidence, not an evaluation counter.

The source order in `PW/src/run_pwscf.f90` is: `electrons` at 189, stop/failure
poll at 197–214, force evaluation at 231, evaluated XML step at 241, optimizer
move at 252, and post-move configuration checkpoint at 260–264. Inside the
optimizer, `Modules/bfgs_module.f90:326–329` reads the prior checkpoint and
increments `scf_iter`; 408–415 prints the observer counters. It saves optimizer
state at 582 before updating the proposed positions at 586–590.

There is no stop poll between the selected counter and completion of this move.
The next electronic loop flushes stdout at `electrons.f90:554` and 596, then
checks EXIT at 606 before the next diagonalization iteration. `check_stop.f90`
checks cwd first at 126–132, then outdir at 138–144; it removes the recognized
file, broadcasts the stop at 161, and retains `stopped_by_user` at 183.
`run_pwscf.f90:197–213` records status 255 and punches the incomplete config.
Use one owned EXIT path. Writing both cwd and outdir EXIT files can leave a
second, unconsumed file that would poison a copied checkpoint.

The event is an observer request, not proof that external timing succeeded.
After complete process shutdown, require the clean-user-stop marker, JOB DONE,
no failure/timeout, XML status 255, exactly one converged evaluated XML record
for the first candidate, three for continuous, and two new records for resumed.
The resume's first evaluated geometry must match the first stopped proposal.
Retain every record, including a rejected line-search evaluation; do not drop a
record to match lengths. Natural BFGS convergence before the registered boundary
is inconclusive. Convergence is checked before counters at
`bfgs_module.f90:404`, so the target marker need not exist in that case.

Allow at least one spare ionic-loop iteration beyond each arm's local stopping
target. `run_pwscf.f90:177` starts a new per-invocation nstep loop. At exactly
the nstep limit, `move_ions.f90:234–237` invokes terminal handling, and
`run_pwscf.f90:343–354` can finish with status 3 and punch all instead of reaching
the following-SCF user-stop poll. nstep exhaustion is not this experiment's
registered clean interruption. Bind the environment `MAX_XML_STEPS=0` to retain
all evaluations: `add_qexsd_step.f90:59–66` otherwise permits XML step
subsampling. This is an environment control, not a CONTROL input keyword.
`input_parameters.f90:127–129` defaults to zero/all, its CONTROL namelist at
296–304 excludes max_xml_steps, and `read_namelists.f90:112–113` reads the
MAX_XML_STEPS environment override. Do not put an unsupported keyword in decks.

## Evaluated records, proposal and optimizer history

`add_qexsd_step.f90:100–103` passes the pre-move Cartesian positions `alat*tau`,
physical cell vectors, total energy divided by e2, and forces divided by e2.
Read evaluated energy, geometry and force from the same XML step, require
converged SCF status and ordered atom indices/species, and validate the complete
72-atom cell and constraints. XML declares Hartree atomic units: energy and
force become Ry and Ry/bohr by multiplying by two; positions/cell remain bohr.
Final output positions likewise use `alat*tau` in `pw_restart_new.f90:356–357`,
while its total energy is divided by e2 at 731. Final-output force normalization
is explicit in `qexsd_init.f90:1321–1347`.

A clean interrupted XML output structure is the post-move proposal. Its energy
can still be the previous evaluation's value, and the following stopped SCF
sets output convergence false. Do not pair that output energy with the proposal
as an evaluated result. A fresh reference belongs at the evaluated step-one
geometry; a continuity resume belongs at the saved proposal. An isolated fresh
SCF requires normal completed output, not the incomplete proposal output.

The source passes step SCF-error metadata without division in
`add_qexsd_step.f90:103`; `qexsd.f90:486` copies it directly to the SCF-convergence
object. It therefore retains the internal Ry convention, whereas final-output
error is divided by e2 in `pw_restart_new.f90:313`. This is a source-level
metadata discrepancy despite the root Hartree label (`qexsd.f90:135`). Normalize
these fields separately, and verify the actual log threshold and convergence
receipt for the first-boundary fresh comparison. The evaluated force matrix is
also copied directly at `qexsd.f90:501`, after its explicit add-step division.

For this fixed-cell, non-FCP slab, BFGS dimensions are `n=3*72+10=226`, including
nine cell and one FCP slots even when inactive (`bfgs_module.f90:245–254`).
With standard bfgs_ndim=1 (default in `input_parameters.f90:1232` and
`read_namelists.f90:546`), the complete text state has 51,986 numerical tokens:
two n-vectors, three counters, energy, two n-history vectors, n*n Hessian,
tr_min_hit and nr_step_length (`773–783`, `844–854`). Zero-based counters are
tokens 452–454 and prior Ry energy is token 455. The first stop must have
SCF/BFGS/GDIIS counters 1/1/0, finite complete state, positive step length, and a
nonzero saved proposal.

The stored prior coordinates are fractional, not generally Cartesian/alat.
`move_ions.f90:110–115` forms the physical cell h, converts positions into
fractional coordinates, and transforms the negative Cartesian force into the
cell-scaled gradient. Recover each Cartesian prior position as the cell-vector
combination of its three stored fractional coordinates. Recover the gradient
relation as minus cell-transpose times Cartesian force. The H2 reader's simple
factor 20 was valid for its cubic cell and must not be copied to this anisotropic
slab. Verify these relations against step one and verify inactive slots.

The first stop has no line-search ambiguity: the Wolfe-rejection branch requires
scf_iter>1 (`bfgs_module.f90:419`). At later boundaries that branch restores the
last successful prior position, energy and gradient at 455–457 before saving
state. A third evaluated point can therefore be present in XML while the saved
prior belongs to an earlier accepted point. Bind the third snapshot to its
source-supported last accepted point, rather than demanding unconditional
prior-equals-step-three equality. `reset_bfgs:722–745` resets the inverse Hessian
and GDIIS counter without resetting scf_iter or bfgs_iter. A later in-algorithm
reset is distinguishable from a startup from-scratch reset.

## Constraints, restart shape and checkpoint ownership

QE if_pos uses 0=fixed, 1=free (`input.f90:1974–1978`); contract fixed_flags uses
the inverse convention. In `forces.f90:350–352`, QE prints unconstrained atom
forces, then masks fixed components at 357–358. XML steps and BFGS use the masked
array after forces returns. Log/XML force comparisons must apply if_pos to
printed forces; nonzero printed forces on fixed coordinates do not prove a
constraint violation. Check fixed positions directly across every geometry.

The resumed deck needs explicit startingwfc=file, startingpot=file and saved
ion positions. `input.f90:845–860` warns about other WFC starts without overriding
them and allows ion_positions=from_input to override the saved configuration.
Reject downgrade, incompatible restart warnings, startup fresh initialization,
startup deletion, or first resumed SCF/BFGS counters other than 2/1. An initial
copy of low-state density/occupations/PAW is deliberate initialization and is
not evidence of optimizer restart consumption.

`input.f90:125–133` can disable restart when scratch is missing; from_scratch
calls clean_tempdir, whose `io_files.f90:240–243` deletes update/MD/BFGS/FIRE
history. A copied-history negative control must show deletion and count zero
before its first optimizer counter. Normal BFGS convergence deletes history at
`bfgs_module.f90:1138`; terminal deletion cannot establish startup reset.

Full continuation snapshots must recursively cover outdir and any distinct
wfcdir, including distributed WFC buffers, restart_scf, update, mixing state,
density/Hubbard/PAW state, schema and BFGS history. Preserve immutable manifests
with relative names, sizes and hashes, then compare each complete copied tree
before invocation. `input.f90:118–135` permits a separate WFC directory.
`punch.f90:14–24,74–109,150–169` distinguishes config/config-only from all;
clean-stop config is not a collected portable checkpoint for arbitrary shape.

Bind actual processor/pool/thread/task-group/band-group/diagonalization layout
and executable across all continuity arms. Historical catalyst output reports
128 MPI processes, one thread, eight pools and a 4*4 ELPA subgroup. XML ntasks
is QE task-group metadata, distinct from Slurm NumTasks; the anticipated XML
shape is nprocs=128,nthreads=1,ntasks=1,nbgrp=1,npool=8,ndiag=16, to be confirmed
from actual saved XML. `pw_restart_new.f90:1260–1262` reads saved parallel
metadata into processor/pool/image/task-group/band-group/orthogonalization
variables. `qexsd.f90:222–223` initializes XML parallel metadata from nproc,
nthreads, ntask_groups, nbgrp, npool and nproc_bgrp. Its last positional value
populates XML ndiag with band-group processor count, which is not independent
proof of the actual orthogonalization subgroup. Bind the launcher diagonalization
choice and retain the printed ELPA subgroup in addition to XML shape. Scheduler
128-task billing and QE grouping need separate receipts.

Saved UPFs are optional at this clean-stop boundary: `punch.f90:111–129` copies
them only for all. `read_pseudo.f90:92–115` tries the saved directory first and
then external pseudo_dir. Rehash all five external files before every arm,
reject any differing saved copy, validate XML filenames/species, and retain
actual file paths and MD5s from each run. `pw_restart_new.f90:1264–1268` can
restore the prior schema's pseudo_dir; pin that fallback too.

## Raw input/XML identity and conversion map

The final caller `PW/src/pw_init_qexsd_input.f90` and initializer
`Modules/qexsd_input.f90` establish the input-side mapping; the initializer
alone passes its values through and cannot establish their original units.
Bind every arm's raw XML to that arm's pinned parsed deck and UPFs. Agreement
between arms' canonical XML identities is an additional check, not a substitute:
all arms could share the same incorrect setting. Do not populate observed raw
settings from expected metadata without checking the corresponding raw fields.

The caller uses input_parameters for settings (19–78), but uses CURRENT
ions_base.tau for geometry (86,184–196). Its input structure is physical
Cartesian bohr and full physical cell: tau=iob_tau*alat, cell=at*alat.
`input.f90:59,81–86` performs structure_iosys and iosys_end before serializing
this object. A continuation's XML.input therefore legitimately contains the
saved proposal, not necessarily the source deck's pre-restart coordinates.
This source order supports the actual tiny raw resumed-input/XML.input proposal
observation and supersedes any inference that XML.input must remain initial H0.
Still require ion_positions=from_file and verify the consumed proposal; do not
use XML.input as proof that file-based restart positions were overridden.

The direct conversion/binding requirements are:

- Caller 165–170 divides etot_conv_thr and forc_conv_thr by e2, but not pressure
  threshold; 473 divides ecutwfc and ecutrho by e2; 482 divides conv_thr by e2.
  These serialized values are Hartree-based, unlike the step SCF error noted
  above. The actual first evaluated target must also bind to the stdout receipt.
- Caller 436 uses schema_smearing to canonicalize the input spelling, and
  440–451 divides degauss by e2. Bind occupations, canonical smearing and width,
  total charge, and any explicit bands, not just an energy cutoff and nspin.
- Caller 477–480 converts david to davidson. Mixing mode/beta/ndim, electron
  maximum steps and solver flags are mapped at 482–486. diago_thr_init at 484 is
  passed WITHOUT the conv_thr division: blanket Hartree conversion is wrong.
  The initializer's qes_init call at qexsd_input248–255 does not include
  diago_david_ndim despite receiving it as an argument; bind non-serialized
  common solver controls from pinned decks, not invented XML fields.
- Caller 423–428 maps nspin=2 to lsda=true and retains noncollinear/spin-orbit
  flags; 174–179 maps starting magnetization per ordered species.
  `input.f90:1482–1483` normalizes absolute starting moments (any absolute value
  >=1) by UPF valence before this serialization. The registered fractional spin
  starts need no such normalization. Check input-side starts by species; do not
  blindly assume every output-side species start is the untouched source deck.
- Caller 143 defines ev_to_Ha=1/e2/RYTOEV and 341–344 applies it to Hubbard_U;
  393–401 binds species, projector type, U and orbital n/l. The orbital label is
  constructed from n and l at `qexsd_init.f90:527–544`, then each U is serialized
  with species and label at 546–556. The consumed output U follows the same
  physical units via `input.f90:2051` and `pw_restart_new.f90:494,543–549`.
  Check PBE functional (caller 203–211,405 and output pw_restart_new557–559),
  atomic projector, each species/orbital/U value, and absence of unregistered
  additional Hubbard/J/V/hybrid/dispersion terms. A bare unordered U list is
  insufficient. XML omits inactive no-Hubbard species by source design.
- Caller 497–498 sends all nk1/nk2/nk3/k1/k2/k3 automatic-grid integers;
  `qexsd_input.f90:287–295` serializes them as monkhorst_pack. Bind all six
  registered values, rather than infer the mesh solely from reduced k-point count.
- Caller 504–506 binds ion dynamics, BFGS dimension, trust radii and Wolfe w1/w2;
  `qexsd_input.f90:380–393` emits the BFGS controls. Caller 518–520 and initializer
  453–466 retain the complete symmetry flags, including nosym and noinv.
- Caller 627–629 ALWAYS writes free_positions from rd_if_pos. Initializer
  698–709 sets dimensions [3,nat] and order F, i.e. each atom's x/y/z flags in
  sequence. Compare those raw 0=fixed/1=free values to every deck and require
  atom indices/species/order and the complete cell to match the selected slab.

The mapping does not serialize startingwfc/startingpot/ion_positions as a
complete restart-consumption receipt. Bind those controls from actual decks and
runtime startup evidence as well. Different calculation/restart/scratch/stop
controls and geometry are allowed only as explicitly registered for each arm;
unregistered physical or common solver changes remain launch-blocking.

## Final smearing, constants and initial-seed identity addendum

The exact helper is `PW/src/set_occupations.f90:135–157`. Its 149–150 mapping
serializes marzari-vanderbilt/cold/m-v/mv (and listed capitalized variants) as
`mv`, NOT `cold`. Gaussian aliases become gaussian at 145–146, Methfessel-Paxton
aliases become mp at 147–148, and Fermi-Dirac aliases become fd at 151–152.
The physical setup at 48–60 uses the same recognized families and sets ngauss
to 0/1/-1/-99. Preserve this exact equivalence; reject an unrelated or unknown
smearing rather than silently inheriting expected metadata. Both input caller
436 and output writer `pw_restart_new.f90:662` use schema_smearing. The actual
seed input has `<smearing degauss="5.0000000000000001E-003">mv</smearing>`,
consistent with the deck's mv and 0.01 Ry. Generated schema initializer
`qes_init_module.f90:2208,2213` copies the passed width and name without further
conversion. Preliminary retained helper candidates contain no definition;
the successful set_occupations bytes, not a speculative file, prove the aliases.

Use QE's exact constants from `Modules/constants.f90`: e2=2 at 105;
HARTREE_SI=4.3597447222071e-18 and ELECTRONVOLT_SI=1.602176634e-19 at 34,36;
AUTOEV=their ratio and RYTOEV=AUTOEV/2 at 54–55. Its BOHR_RADIUS_ANGS is
0.529177210903 from 38,110–112. A rounded independently chosen Ry/eV or bohr
constant can fail tight direct settings/geometry comparisons. Generated
qes_init_HubbardCommon copies species/label/value at 1406–1419, and
qes_init_integerMatrix_2 flattens the mask with Fortran reshape at 5040–5046.
Generated parallel_info copies ndiag as the final positional field at 272–294,
confirming the separately described bandgroup/launcher distinction.

An independent file-only comparison used the exact local deck
`runs/hea/lowtail_low_state_restart_2026-09-22/Cu8Cr23Mn35Co34__s20_site2/slab_c5low__relax.in`,
SHA256 `dfed65abc93a5eb5ef350c31f963fd6044c5b6e68fd39904063a0292de5f8539`.
Its bytes exactly equal remote_inventory.deck.text. The retained seed_xml
UTF-8 bytes hash to `2360316d4d5d759bfce9e8f6dbb024acd3315df12f1039a71fb28898ae2ae0fd`
(399,395 bytes), matching the seed manifest. XML.input and XML.output each have
all 72 ordered species/indexed atoms. Both complete coordinate sets and full
3x3 cells agree with the deck converted by QE's exact bohr constant to maximum
absolute error 7.105427357601002e-15 bohr. All 216 free_positions values match
the deck flags exactly. The seed parallel shape is directly confirmed as
128/1/1/1/8/16 (nprocs/nthreads/ntasks/nbgrp/npool/ndiag), while actual launcher
ELPA shape remains a separate runtime check. The comparison receipt source is
`remote_inventory.json`, SHA256
`0c654f881304d1315b91d173c9e82842ba8cafdc2b4e91db2619d02dd719ce49`.
This establishes pinned XML/deck geometry and constraint consistency; it does
not independently decode the binary charge/PAW grid or prove future consumption.

## Scientific scope and bounded feasibility

Matching the fresh SCF to the actual first warm target 1e-6 Ry is consistent
with this approved same-settings numerical boundary trial. The first BFGS call
sets step_accepted=false (`bfgs_module.f90:501–505`), so the threshold-update
branch in `move_ions.f90:243–248` does not change the first-boundary target.
Verify the actual log, rather than assume this from the nominal input.
1e-6 Ry is about 0.0136 meV of estimated energy error, well below the 10 meV/cell
comparison criterion; it is not a proof of the global electronic ground state.
Retain the historical separate fresh target 8.08e-8 Ry as historical. This
experiment interposes one fresh check and cannot validate checking every
production step. Starting from the known low state may supply no genuine lower
fresh state; absent an actual >10 meV drop, the real reseed branch stays pending.

Two hours per invocation is feasible on retained evidence, not guaranteed.
The previous matched low-state warm relaxation reaches its first three
evaluations in 3,12,26 iterations with trace cycle ends 480.0,1121.6,2498.7 s.
Its SCF3/BFGS2 marker is output lines 9246–9247. The source log is
`results/lowtail_low_state_restart_2026-09-22/relax2/outputs/Cu8Cr23Mn35Co34__s20_site2/slab_c5low__relax.out`,
SHA256 `6a99fcd94e2b9b5756aa5a9ee905dc16b330deab69c43bff414f50b2aeb24082`.
The old fresh SCF measured 3485 s at a tighter target. Historical memory
estimates are >102.03 GB total, with runtime reports approximately 533.7–637.3
Mb/process. These support the bounded attempt but do not certify peak RSS,
new-node speed or memory availability. A stall/timeout/OOM or missed boundary
must remain inconclusive, without a retry, chain or trajectory splice.

## Retained source correction and pins

The earlier tiny planning/release narrative asserted that the new-trust-radius
line exists only in a later Wolfe branch. The retrieved official qe-7.5 source
has both the Wolfe write at bfgs_module449–451 and the normal/new-step write at
568–570. That blanket exclusivity claim is too strong. Preserve the old
refusal/receipts and record this correction. The selected count-based observer,
actual one-step H2 checkpoint and tiny numerical result are unaffected.

All source files below were read from the retained official qe-7.5 byte cache;
their hashes were computed independently from local bytes. Retrieval receipts
are qe_source_retrieval.json, qe_source_extra_retrieval.json,
qe_source_xml_retrieval.json, qe_source_qexsd_retrieval.json,
qe_source_input_retrieval.json and qe_source_input_caller_retrieval.json. Final
additions are documented by qe_source_schema_retrieval.json,
qe_source_schema_map_retrieval.json, qe_source_smearing_retrieval.json,
qe_source_alias_retrieval.json and qe_source_definition_retrieval.json. Successful
cached source/build files total 27 (25 Fortran files and two Makefiles); failed
speculative retrieval entries are metadata, not executable source pins. The attempted
Modules/qexsd_module.f90 URL was unavailable; the correct retained module source
is Modules/qexsd.f90. These source pins supplement the runtime binary
pin; they do not prove the installed binary's complete build ancestry.

| Source under qe_source | SHA256 |
|---|---|
| PW/src/run_pwscf.f90 | 3783fee67652c4d220f94d6a59a16ae5a0c2f8d34589551e35177419861ce8ae |
| PW/src/electrons.f90 | e62ea5f6c65039481f5fa5b580765dac5e3074e9e2d40c0c7ab9d7acd3be8175 |
| PW/src/move_ions.f90 | 29e7145ca0db1fc675a179baf28639f22138bf068dbea78833ae4c6dc67e0b2f |
| PW/src/punch.f90 | 288fe98445b014f9693eeaca53cf90f1deeb080532fe747bcdc88452e39f6cd8 |
| PW/src/input.f90 | bbfe23ac73ccd363812dfd1fb2d6b1784db7e2d430d7a18df177108d3ea4d85a |
| Modules/bfgs_module.f90 | 80417f1e5cd5f52a84ab81878d50175ea078071ce3b76fcb4a959089ab4d9432 |
| Modules/check_stop.f90 | 9ace8cf292c57c671f7df629643817f4342dd27f521b96b6908ebcf741211b86 |
| Modules/read_pseudo.f90 | 24e93b4fe7214d978034441dba42cbcc7407e2bff9b11c7c891ccb55f0c94fc4 |
| PW/src/forces.f90 | acc46cb14d2f08f2dbedeb0451f69e29d21ae880d3009886041cf71cb1e55efa |
| PW/src/pw_restart_new.f90 | 82dfdef8ded7f853b705762036fda7a7694e3a4af6e00e1bfeffa50d35cc46ef |
| Modules/io_files.f90 | 9882ee911e667b836024601be193177a6eb5bc4284ddbf7b217f81bb1f9312fd |
| PW/src/add_qexsd_step.f90 | 3c9e1a63049e9c52d40b7b48deae1651a9e9c559c3f13440dc22866b56cfbf21 |
| Modules/qexsd_init.f90 | aa4d0cab034ec79d39a55afa1ae5f6b78fb08c5864789a05e16eae69dd59231d |
| Modules/qexsd.f90 | 4f55aa0660ee30a616ade35e0a04ceec133c3631e5dce5d5750f1303d2193782 |
| Modules/input_parameters.f90 | 0a871234d0983b2203c1e3550a1711cdf43cbc2145ce3d4e6f3285f814336f56 |
| Modules/read_namelists.f90 | dacf74da652b2a07b22e27b383c828885f58078287a84143feb5a6c224b9f7ea |
| Modules/qexsd_input.f90 | fd4c91478fb8520e786c90c6a90081ce769f4b168cc39a76f210641a9ec03c25 |
| PW/src/pw_init_qexsd_input.f90 | 6ae9b025936035e551cb2d8ee9d4a60325b9df6f6c53be096377349ffe1fe56a |
| Modules/constants.f90 | 56c39e90c6f0592aff13972cd090292024a3d4e9e86d0ce4fdfdb5643f1ac1c0 |
| Modules/Makefile | bffcfc7edf22ad11af1521d935a4f0920ed8c5665e7296bc4a225ab389d931c1 |
| Modules/qes_init_module.f90 | 2e81cdbd15d941d23deb371190d5ea41bd51bf90c82f8aae0aa96b413417637f |
| Modules/qes_libs_module.f90 | 276b2743686dd1b669027ba1e72f477b0fb8e8b807fe5b9c95488e3616c9e4b5 |
| Modules/qexsd_copy.f90 | 850f6afe33a0871bd88f3e87069a902f2b1cd152973667b0b4bba1181d5b7a23 |
| Modules/wgauss.f90 | 78145ca2423a14f3a761737f9eb54ed6e52755c441bd79997da3a138f5d42a8c |
| PW/src/Makefile | 88a18e47a92b82aeed3d55239c4b615b58d2238b277a62c685fe354bcfaefb02 |
| PW/src/set_occupations.f90 | feb6505fd556b89d64f103b7709de83136d4c3277e594480a9790283235ce985 |
| PW/src/utils.f90 | 362438958d6ffd70fe7a454f56e27455811c44d1de3a0bfdaa44aa1ea39f20bd |

Reviewed local reference pins: tiny runner
`5cec00a14827111161d90a5b41cf01dff8e06a1b1bc9c21ccfe4529f56e0cf3a`;
tiny raw reader `c43b23e4ec6c449fe65f6011524bf481e52d50c2117420f141ea65dc0dacf585`;
readiness document `c5b560d7d2eab1dc12bbfd8b730a43458c614c34d2585bbf4acd0bb662b29a3c`;
September plan `abc7743a247c4ba646507881d318d94b6535fac9d3eb0ababb017bb8b6ac0ab2`;
historical warm trace `d763bddf3f6ccb0b56bff6fa1916c57f79cc9e1b62bae170064b2af520b881fb`.

Remaining launch review must inspect the actual adapter and raw-reader behavior,
current tests including the real filesystem guard, exact stage/binary/UPF/seed
pins, live allocation and full per-invocation/aggregate supervision. No actual
adapter/test/catalyst-trial pass or production acceptance follows from this
source review alone.
