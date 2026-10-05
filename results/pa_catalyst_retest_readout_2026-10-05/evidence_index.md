# Terminal evidence index — catalyst re-test 21075231

Scientific status: **INCONCLUSIVE**. Production acceptance remains false. Parent allocation: **353.92 CPU SU**, 2 h 45 m 54 s. Preservation and investigation add no solver calls or jobs.

## Scientific readout

- [Dated readout](../../docs/research/pa-catalyst-retest-readout-2026-10-05.md): first failed comparison, unchanged registered thresholds, checkpoint consumption, competing electronic explanations and prospective diagnostic scope.
- [Independent numerical reconstruction](independent_analysis.json), with the exact parser in [analyze_terminal_v4.py](analyze_terminal_v4.py).
- [Independent final review](independent_readout_review.json) binds the readout and deciding evidence by SHA256.
- [Terminal accounting](terminal_accounting.json) and [fresh terminal inventory](terminal_inventory.json) retain the parent/step accounting and complete controller receipt.

## Preservation layout

[Preservation summary](preservation_summary.json) is the final selected-layout receipt. Earlier progress and small-mirror receipts retain their observation times.

The complete Anvil archive contains all 1,631 trial/launch/source/scheduler files (76,112,065,809 logical bytes), stored as 492 independent unique content files (60,874,634,461 bytes):

~~~text
/anvil/projects/x-che260157/sts_pa_catalyst_retest_2026-10-04/evidence_archive_21075231_2026-10-05
~~~

The [raw manifest](raw_manifest.json) maps every original path to its byte size, metadata and content hash. [Archive completion](anvil_archive_complete.json) records source and destination hash checks and archive paths. Permissions are 0400 for content and 0500 for directories; owner permissions are read-only, not a write-once storage guarantee. Original trial files were only read.

[raw_small_v2.tar.gz](raw_small_v2.tar.gz) retains all 1,098 local scientific files (35,476,741 bytes) under original relative paths. It includes the complete deciding logs, inputs, XML, receipts, BFGS files and electronic restart metadata. Every member byte hash matches the raw manifest; [small-mirror verification](small_mirror_verified.json) records this check. Extracting it into an empty directory reconstructs the scientific mirror. SHA256 of the archive is d65ac2995f626df4ae5118514613f6b46c5df7ad76c274a98cb10d19e698fe84.

The large wavefunction/charge-density binaries remain completely archived on Anvil. The optional full Windows binary transfer is partial; [storage disposition](storage_decision.json) inventories retained verified and partial content files. Full Windows binary preservation is not claimed.

The remote LF manifest SHA is 910c79bca816c42e4ed20480b499b8d00d607eb0c7fecce26ee0cf0b8db9bfa4. The Windows CRLF manifest SHA is c707caea13fdfb49c72fb745c7b79827879607fad93fd95b84010c3c1e7575d5. Only CRLF-to-LF replacement is needed to reproduce the remote hash; content pins and integer metadata are unchanged.

## Exact launch and primary source

[Launch snapshots](launch_snapshot/source_manifest.json) bind the c5b33c28bb09324d7decf5c2bb5f6100a877a366 implementation and the approved spec to retained source bytes. Existing launch and watcher records remain frozen separately.

Official QE7.5 source paths, URLs and hashes are retained in [cached source pins](qe_source/cached_source_pins.json) and retrieval*.json. The exact restart helper and continuous driver account for the observed initial diagonalization-threshold difference. Its causal contribution to the force discrepancy remains unproven.

[Collection refusals](collection_refusals.json) and [offline-analysis corrections](analysis_refusals.json) retain failed collection/parsing attempts separately. They do not alter the raw trial or registered scientific result.

## Next gate

A fixed-geometry electronic initialization/force-convergence diagnostic can distinguish the leading explanations. Its exact controls, readouts, budget and review must precede a separate compute approval. Longer catalyst work, ranking and melt selection remain unresolved.

