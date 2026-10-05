# Independent terminal readout review — job 21075231

Decision: **FAILED_CONTINUITY_READOUT_ONLY**

Blocking findings: none. Clearance covers publication of the retained failed-continuity investigation. Scientific status remains **INCONCLUSIVE**, production acceptance remains false, causal attribution remains open, and no future compute is approved.

## Exact scope

Reviewed the final dated readout, numerical reconstruction, evidence index, archive/storage receipts, raw deciding payloads, exact launch snapshots, retained official QE7.5 source and publication safeguard. The JSON sidecar binds 118 exact repository-relative path/SHA256 pairs. All 26 previously reviewed prelaunch code pins are unchanged; the four launch source copies and current core source bytes match the exact c5b33c28bb09324d7decf5c2bb5f6100a877a366 launch manifest. The spec is 4c2384c6375f1c7892d33d8f6c37478243f41af3da9dd0f9ec507bcd8423e435.

## Independent evidence checks

- Independently read and hashed all 1,098 local raw files, 35,476,741 bytes: every hash/size matches the terminal manifest. Independently decompressed and inspected the 8,319,743-byte scientific Git archive: exactly 1,098 unique regular-file members, all original names and payload hashes match. Archive SHA256 is d65ac2995f626df4ae5118514613f6b46c5df7ad76c274a98cb10d19e698fe84.
- Independently extracted all seven ordered evaluated XML records using JavaScript, without the registered adapter: control 3, candidate 1, fresh 1, resumed 2. Energies, all 216 force components, all 72 atomic positions, species and cells exactly match parsed receipts. Complete stdout energy/force groups agree within 5e-9 rounding. Proposal coordinates pair with the following evaluated frame or unevaluated output proposal within 9.44e-11 bohr. No frame shift, atom remapping, force-mask or unit artifact was found. There are 132 movable and 84 fixed Cartesian coordinates, comprising 44 movable and 28 fixed atoms.
- Raw frame 1 passes. Frame 2 first fails the Co20 z force by 1.1464205365793734e-4 Ry/bohr (11.464 times the unchanged limit), while geometry and energy pass. Frame 3 fails energy 5.044989848101977e-6 Ry, position 6.767888983993942e-5 bohr and force 6.991968840434166e-5 Ry/bohr. All raw differences exactly reproduce the registered refusal.
- Reconstructed both complete 390-file candidate terminal inventories, including directory names, sizes and content hashes, against the saved pre-fresh inventory. Both trees exactly match dc3637bce66f8c9d85bd7d29f77af40810302650b8eed1f02bdf9de83c98a32c. This independently closes the success-only final inventory gap. Saved BFGS has the complete 51,986 values, counters 1/1/0, zero inactive tails and a positive Newton step. Its prior energy, positions and gradient match the evaluated candidate; observed resumed counters are SCF 2/3 and BFGS 1/2 with no startup reset/fallback.
- Fresh is approximately 0.148621 meV/cell higher at the same evaluated geometry; the strict more than 10 meV lower trigger is absent. The RESUME_CANDIDATE branch is correct independently of the subsequent failed continuity gate. Fresh/warm maximum force spread is 8.82133277420e-4 Ry/bohr at Co23 z. All 22 printed initial resumed Hubbard trace records match the candidate final values at displayed precision; that precision does not identify an electronic basin.

## Primary-source interpretation

The retained tagged QE7.5 sources and exact cited line excerpts support the observed startup ethr 1e-5 versus continuous 1e-6 difference. Saved restart_scf iter 0 does not restore dr2/ethr/eigenvalues (restart_in_electrons.f90:33–56); setup.f90:423–437 assigns the default file-potential startup threshold; run_pwscf.f90:320–334 resets the continuous post-move threshold. These observations support a discriminating prospective diagnostic and do not prove threshold causality.

SCF residual XML units were checked field by field: add_qexsd_step.f90:100–104 keeps relaxation-step scf_error in Ry; pw_restart_new.f90:311–319 divides output scf_error by 2. Fresh output therefore converts to 9.80071310431723e-7 Ry. Corrected residuals match printed stdout. Energy/force Hartree conversion is a separate verified operation. All 19 retained/cached primary-source hashes match; the 10 new helper Git blob pins also match.

## Preservation and allocation

The complete Anvil preservation receipt maps all 1,631 logical files/76,112,065,809 bytes to 492 unique contents/60,874,634,461 bytes and records source/destination verification. Its complete hash/size content set agrees with the terminal manifest. This reviewer checked the retained receipt and metadata, without Anvil contact; independent direct payload verification covered the local scientific bundle. 0400/0500 are owner read-only permissions, not write-once storage. Full Windows binary preservation is explicitly partial; all 16 verified-blob and 4 partial paths remain present at recorded sizes.

Only CRLF-to-LF replacement of the original Windows manifest reproduces the remote manifest SHA 910c79bca816c42e4ed20480b499b8d00d607eb0c7fecce26ee0cf0b8db9bfa4. Exact integer metadata and scientific file hashes are preserved. Final preservation_summary supersedes the scope of earlier timed progress observations without editing them.

Frozen parent accounting is FAILED 3:0, 9,954 seconds, 128 CPUs and 1,274,112 CPU seconds = 353.92 allocation CPU SU. It is within the estimate 275–543 and approved 2,048 SU/16h ceiling. Parent accounting is counted once; batch/extern rows are not added. All four QE processes returned 0, and the wrapper refused the scientific comparison. Negative/reset control did not execute, no reseed ran and no automatic retry/requeue occurred.

## Publication and next scope

The final readout and index preserve the registered failure, separate checkpoint consumption from numerical continuity, label the full-local binary limitation, and require a separately priced/reviewed/approved fixed-geometry diagnostic. No catalyst ranking, melt selection, production/every-step acceptance or causality claim is licensed. Local source links resolve; the index reference to this review resolves upon this additive write.

File-only inspection of bank_readout.py confirms fail-closed review pins, exact scientific/archive member and launch-source checks, explicit allowed publication paths, preserved historical task suffix, exact staged/committed bytes and remote commit equality. No reviewer process, shell, test, SSH, job or solver execution occurred. Only these additive review files were written.
