# QE7.5 new-format DFT+U source review

Scope: offline repair of the XML validator after job 21034683 retained
FAILED3:0. This review concerns source-emitted QE7.5 new-format XML, not general
XSD validation or permission to resume/retry the trial. No existing file was
changed; no process, Git, SSH, network, QE or job was run for this review.

Finding: the mandatory `dftU/lda_plus_u` child in the original adapter is not
part of the reviewed QE7.5 initializer. Its absence in the actual control XML
is source-normal. It must not be interpreted as disabled U. Kind, projector,
species/orbital and nonzero U values remain independently binding.

## Rechecked source and original-adapter pins

Every one of the 27 successful source/build files below was read and SHA256
recomputed; all 27 match the frozen offline_checked/source-review pins. Failed
source guesses are not successful source files. The original adapter examined
was src/dft/pa_qe_adapter.py SHA256
255464215aa898d0c9d34317a1be9b16fb27ba6d35108e0ca78215331a628879.
Its original failure is the required child lookup at626; its kind/projector/U
checks at627-643 must not be weakened to make absent data pass.

All source paths below are relative to
results/pa_catalyst_trial_2026-10-03/qe_source and the official qe-7.5 cache.

| Source path | Recomputed SHA256 |
|---|---|
| Modules/bfgs_module.f90 | 80417f1e5cd5f52a84ab81878d50175ea078071ce3b76fcb4a959089ab4d9432 |
| Modules/check_stop.f90 | 9ace8cf292c57c671f7df629643817f4342dd27f521b96b6908ebcf741211b86 |
| Modules/constants.f90 | 56c39e90c6f0592aff13972cd090292024a3d4e9e86d0ce4fdfdb5643f1ac1c0 |
| Modules/input_parameters.f90 | 0a871234d0983b2203c1e3550a1711cdf43cbc2145ce3d4e6f3285f814336f56 |
| Modules/io_files.f90 | 9882ee911e667b836024601be193177a6eb5bc4284ddbf7b217f81bb1f9312fd |
| Modules/Makefile | bffcfc7edf22ad11af1521d935a4f0920ed8c5665e7296bc4a225ab389d931c1 |
| Modules/qes_init_module.f90 | 2e81cdbd15d941d23deb371190d5ea41bd51bf90c82f8aae0aa96b413417637f |
| Modules/qes_libs_module.f90 | 276b2743686dd1b669027ba1e72f477b0fb8e8b807fe5b9c95488e3616c9e4b5 |
| Modules/qexsd.f90 | 4f55aa0660ee30a616ade35e0a04ceec133c3631e5dce5d5750f1303d2193782 |
| Modules/qexsd_copy.f90 | 850f6afe33a0871bd88f3e87069a902f2b1cd152973667b0b4bba1181d5b7a23 |
| Modules/qexsd_init.f90 | aa4d0cab034ec79d39a55afa1ae5f6b78fb08c5864789a05e16eae69dd59231d |
| Modules/qexsd_input.f90 | fd4c91478fb8520e786c90c6a90081ce769f4b168cc39a76f210641a9ec03c25 |
| Modules/read_namelists.f90 | dacf74da652b2a07b22e27b383c828885f58078287a84143feb5a6c224b9f7ea |
| Modules/read_pseudo.f90 | 24e93b4fe7214d978034441dba42cbcc7407e2bff9b11c7c891ccb55f0c94fc4 |
| Modules/wgauss.f90 | 78145ca2423a14f3a761737f9eb54ed6e52755c441bd79997da3a138f5d42a8c |
| PW/src/add_qexsd_step.f90 | 3c9e1a63049e9c52d40b7b48deae1651a9e9c559c3f13440dc22866b56cfbf21 |
| PW/src/electrons.f90 | e62ea5f6c65039481f5fa5b580765dac5e3074e9e2d40c0c7ab9d7acd3be8175 |
| PW/src/forces.f90 | acc46cb14d2f08f2dbedeb0451f69e29d21ae880d3009886041cf71cb1e55efa |
| PW/src/input.f90 | bbfe23ac73ccd363812dfd1fb2d6b1784db7e2d430d7a18df177108d3ea4d85a |
| PW/src/Makefile | 88a18e47a92b82aeed3d55239c4b615b58d2238b277a62c685fe354bcfaefb02 |
| PW/src/move_ions.f90 | 29e7145ca0db1fc675a179baf28639f22138bf068dbea78833ae4c6dc67e0b2f |
| PW/src/punch.f90 | 288fe98445b014f9693eeaca53cf90f1deeb080532fe747bcdc88452e39f6cd8 |
| PW/src/pw_init_qexsd_input.f90 | 6ae9b025936035e551cb2d8ee9d4a60325b9df6f6c53be096377349ffe1fe56a |
| PW/src/pw_restart_new.f90 | 82dfdef8ded7f853b705762036fda7a7694e3a4af6e00e1bfeffa50d35cc46ef |
| PW/src/run_pwscf.f90 | 3783fee67652c4d220f94d6a59a16ae5a0c2f8d34589551e35177419861ce8ae |
| PW/src/set_occupations.f90 | feb6505fd556b89d64f103b7709de83136d4c3277e594480a9790283235ce985 |
| PW/src/utils.f90 | 362438958d6ffd70fe7a454f56e27455811c44d1de3a0bfdaa44aa1ea39f20bd |

## Caller emission versus restart inference

1. Input caller PW/src/pw_init_qexsd_input.f90:305-405 builds dftU only inside
   ip_lda_plus_u. It determines active species at314-326, allocates nonzero scalar
   U/J/alpha/beta vectors at341-367, and converts input U from eV to Hartree at343.
   The call at393-401 explicitly passes actual kind, projector, species and n/l.
   When U is inactive, dftU lwrite is false at403. There is no boolean XML child.
2. Output caller PW/src/pw_restart_new.f90:493-559 likewise enters only when
   actual lda_plus_u is true, converts scalar U from Ry to Hartree at494, and
   explicitly passes kind/projector at546 and n/l/U at547. Its zero-only scalar
   helper at863-872 leaves vectors unallocated. Inactive dftU lwrite is false at555.
3. Modules/qexsd_init.f90:425-511 makes kind at443 and projector at444 mandatory
   arguments and always supplies new_format=.true. to qes_init at510. Kind2 uses
   Hubbard_V at478-479 rather than the ordinary U path at481. Labels derive from n/l
   and active species at527-543; common entries receive exact specie/label at555,
   while inactive labels suppress entry output at556.
4. Modules/qes_init_module.f90:1228-1390 contains no lda_plus_u argument/member
   assignment. Optional new_format, kind, projector and arrays have explicit
   ispresent flags1258-1387. These flags describe initializer presence, not a
   license to assume schema defaults for missing registered fields.
5. Restart copying uses different logic: Modules/qexsd_copy.f90:403 sets
   lda_plus_u from dftU_ispresent, then defaults absent U/U2/Um/J/alpha/beta/V
   arrays to zero405-413 and reads kind/projector414-415. Thus dftU presence,
   not a nested boolean, activates the correction on this restart path.

The namelist/input-variable defaults in Modules/read_namelists.f90:208-229
(atomic projector, lda_plus_u false, kind-1, zero couplings) and
Modules/input_parameters.f90:431-454 are not defaults for absent XML fields.
No XSD/default-schema claim is made: qes_types/read/write and the XSD itself
are outside this 27-file cache. Further retrieval is not needed for the scoped,
explicitly emitted new-format caller validation described here.

## Actual retained control XML

The existing local mirror was read without another download or QE call:
results/pa_catalyst_trial_readout_2026-10-04/mirror/trial_results/control/outdir/
slab_c5low__pa_boundary.save/data-file-schema.xml. It is 437772 bytes, SHA256
3b556aa74327969f2799e19c0a3ad9153e44ec33dd656e2332043221db0b699d.

| Section | Actual dftU shape |
|---|---|
| input:152-158 | new_format=true; kind0; three Hubbard_U entries; projector atomic; no lda_plus_u |
| output:1068-1611 | new_format=true; kind0; three Hubbard_U entries; three Hubbard_Occ entries; 44 Hubbard_ns matrices; projector atomic; no lda_plus_u |

Both sections bind the same Co-3d, Cr-3d and Mn-3d entries: respectively
0.1220077496231744,0.1359724920499233,0.1433223564850543Hartree. Using the
exact QE constants (Modules/constants.f90:34,36,54-55) gives 3.32,3.70,3.90 eV
within floating roundoff. No U entry exists for Cu or O, as expected.

The XML contains three evaluated step records at306/479/652 and exit_status255
at6791. The retained process receipt reports returncode0, cycles[1,2,3],
registered-evaluated-boundary, no timeout/failure/stall and elapsed 2883.939 s.
The trial receipt nevertheless records INCONCLUSIVE and `one XML lda_plus_u
required`, with only the control call. These facts do not establish candidate,
fresh, resumed, reseed or negative-control acceptance and do not authorize retry.

Additional rechecked raw pins:

| Raw control file | SHA256 |
|---|---|
| input.in | 5148e8b20373374ee3588c68a112a8cf36858770f1a416c525e79a962dc42790 |
| stdout.log | 56c02e6db6618dd011d736827fe3646b7ea58de8060f858d0ede5b91a069becc |
| stderr.log | 3d8165bc5d885215be20fc4411c896bb7632fc2bf2c07853c7c33858694cc5b8 |
| process_receipt.json | 6db2620490cb2d5662d594ad6ea9ca8f0821c2a6d35ec3e0804cd786e1a73865 |

## Specific additional tags and repair limits

Interaction/correction parameters must remain distinct from occupation state:

| Source XML tag | Representation and relevant source |
|---|---|
| Hubbard_Um | Orbital/spin-resolved on-site interaction vector, not a density matrix; qexsd_init575-615 emits only nonzero channels and binds specie/label/spin. |
| Hubbard_V | Inter-site/species/channel interaction scalar with site indices and both specie/labels; kind2 branch478-479 and helper646-695. Nonzero values are required to emit an entry660-683. |
| Hubbard_back | Second/background Hubbard channel, containing Hubbard_U2 and n2/l2 plus optional n3/l3; qexsd_init851-905, qes_init1957-2006. It is suppressed for inactive background species898-902. |
| Hubbard_J0, Hubbard_alpha, Hubbard_alpha_back, Hubbard_beta | Additional scalar correction parameters; qexsd_init491-494 uses the common species/label helper546-558. |
| Hubbard_J | Three-component correction vector per species; qexsd_init560-573. Nonzero unregistered values cannot be treated as occupation metadata. |
| Hubbard_Occ | Channel-occupation metadata, passed from Hubbard_occ by the output caller545; distinct from U/J/V interactions. |
| Hubbard_ns, Hubbard_ns_nc | Per-atom occupation matrices/state, passed from rho%ns/rho%ns_nc by output549 and serialized by qexsd_init801-849. Normal output can have nonzero values. |
| starting_ns, Hub_m_order | Initial-occupation state and orbital ordering metadata, respectively; qexsd_init760-799/617-644. Neither is a substitute for a U/species/projector binding. |

The original adapter639-641 checks nonzero J0/alpha/alpha_back/beta/J but silently
ignores Um/V/back. A scoped U-only validator should not gain a path that accepts
unregistered coupling tags during this fix. Hubbard_back is nested: testing
only its outer text cannot detect Hubbard_U2. In contrast, rejecting every
unrecognized/nonzero child would incorrectly reject the real output's normal
occupation metadata/state. Do not compare complete input/output dftU trees.

The original physical DFT+U source checks cover XML.input only
(read_qe_arm807 -> _check_xml_input538 -> _check_xml_common_source617-643).
Actual output bindings were inspected here, not accepted by that original
validator. A repaired replay must state separately which sections it checks.

Recommended bounded contract: exactly one source-matched dftU, new_format=true,
explicit kind0/projectoratomic, unique exact three-entry species/orbital/U map,
and no unregistered interaction channels. Remove the invented mandatory boolean
child; if a contradictory explicit false flag is encountered, do not silently
ignore it. Missing registered U/kind/projector must not be filled from the deck.
Retain source unit conversions and every unrelated geometry, constraint, UPF,
MPI, clean-stop, evaluated-count and ordered raw log/XML check unchanged.

This source review is not a repaired adapter diff review or runtime/replay pass.
Those checks belong to the later independent review of frozen repaired bytes
and the existing immutable mirror/dryrun evidence.
