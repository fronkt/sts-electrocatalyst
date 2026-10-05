# Independent corrected catalyst retest review — final

Decision: GO_ONE_BOUNDARY_RETEST_PRELAUNCH

Scope: exact 2026-10-04 one-boundary diagnostic package, with publication and subsequent live prelaunch gates. This is technical clearance of the reviewed package. It does not establish a catalyst continuity/reseed result, production relaxation, every-step P-A, S8 ranking or melt release. Separate staging/submission authorization and live Anvil gates remain required by the documented sequence. This reviewer performed file/source inspection and byte-hash checks only; the root executed the fresh verification. No Anvil operation, QE invocation, process or test was performed by this reviewer.

## Final evidence and binding

The complete fresh final receipt is offline_release.json, SHA-256 723a52576ca41aef7451dd35fcfe80c0beb4ef8b6d09be5f1cae9500807cc2c4, label release, successful=true. The earlier checked attempt was superseded after a missed text replacement; its interrupted/stale execution and focused failures are preserved under verification_replan.md and stale_verification_stop.json. They are not passing receipts. The final run reran every ordinary assertion:83 evidence tests;491 first-trial regressions plus7 subtests,3 existing platform skips;294 retest regressions,2 existing Windows symlink/FIFO skips;78 historical readout tests. No failed or deselected test, source-line waiver or exception remains. bash -n, both scientific verifiers,42 registered recovery reads,2496 canonical rows,144 checklist rows,27 primary-source pins, the accepted real control/19 SCF pairs and12/12 caught mutations pass.9816 tracked and21 unrelated historical byte pins agree before and after the final run. Platform skips retain their stated limitation; unchanged filesystem guard logic also retains the original launch's Linux evidence.

I rehashed all26 final code/source/test/spec/script/document pins after the final receipt completed: zero mismatches. independent_launch_review_final_pins.json binds this exact receipt and its complete code_pins mapping. The publisher requires that mapping and receipt hash before staging explicit local paths; it checks staged bytes and the remote commit before declaring publication successful.

## Resolved findings

The initial submission race is closed. Both local and remote submission/release intent claims use exclusive file creation, durable flush and fsync before their mutating call. A second invocation fails before SSH/sbatch/release or the owner's remote receipt finalizer. The meaningful eight-contender regression demonstrates one remote claim winner; separate tests demonstrate existing local intent refusal before SSH. Intents remain after failures; the implementation provides no replacement submission or automatic retry. The initial review refusal, original reviewed lifecycle source buffers and corrected initial hash memo remain preserved.

Historical checks now use all13 exact original launch files from commit b9f0208ee6f3cd71d0201d03b964b5c23f53d644 / job21034683, fixed manifest SHA-256 dcb15854775caa79577ee6eb6b623dc135d4de487e3c2b027949f8c5da2ade0b. Default spec/deck, controller, adapter, contract, watcher and criterion sources resolve to that snapshot. A differing spec override is refused; the frozen adapter checks a supplied deck against the original deck pin. The loader temporarily binds the exact contract for the adapter import and restores live module cache state, defeating prior cached repaired modules. The verdict records the complete snapshot manifest. I inspected all13 source hashes and all71 structured quotes: every quote is exact at its recorded original line. The explicit DOC-minus3 coordinate map corrects later-added header lines without altering the source or scientific criteria. The numerical-literal test excludes only source-coordinate positions in known citation tuples; actual resource/scientific constants and permitted thresholds remain checked.

The watcher now counts required inner scheduler collection failures and exits after three consecutive failures. Valid terminal accounting remains usable after both squeue and scontrol purge the job. It remains a bounded read-only observer with no submit/cancel/retry/QE path.

## Scientific and resource assessment

Direct inspection of pinned official QE7.5 writers supports the corrected presence-derived dftU/new_format=true validation, explicit U species/shell/projector/value binding, Hartree/eV normalization and XML string canonicalization. Unregistered Hubbard children fail closed. Each arm binds calculation/restart_mode/prefix/max_seconds to its own actual deck; complete common XML/settings identity continues to bind physical and solver settings. The registered deck/UPFs/runtime, full72-atom geometry/cell/constraints, evaluated-versus-proposal distinction, masked forces and source-bound optimizer state retain their original scientific contract. The real-control preflight replay pins compressed and original bytes, five registered UPFs,3 converged evaluations/globalSCF[1,2,3], optimizer3/3/0 and the exact XML identity before any QE invocation.

The controller retains the reviewed first/third evaluated-boundary observer, single owned EXIT file, post-shutdown acceptance, complete checkpoint isolation, fresh decision before any resumed/reseed branch, strict10meV decision and lower-state reseed evidence gate. Missed boundaries, failed fresh references, carry-over refusals, stalls, time limits and other unusable outcomes remain held/inconclusive with no retry.

The wrapper requests one wholenode node,128CPUs/billing128,200GiB and16h with no requeue. Held validation and release recheck the singleton requested shape; the controller requires actual RUNNING allocation/TRES before each invocation, forbids parallel QE, reserves a full7200-second call plus120-second cleanup, caps solver calls at six and tears down only its owned process group. The exclusive one-attempt submission guard and16h scheduler limit bound the one approved job to2048CPU SU. The275–543SU estimate remains planning arithmetic; it is not a guaranteed charge.

## Limits and subsequent gates

The proposed trial is still unsubmitted. Job21034683 remains FAILED3:0 / scientificINCONCLUSIVE /102.8622CPU SU; its single completed control does not validate the unexecuted catalyst fresh/resumed/negative/reseed arms. No real same-deck catalyst relax/fresh XML pair or72-atom128-rank restart log exists locally; fresh-control identity and catalyst restart behavior retain their documented inference/runtime limits. The real SCF tests disclose ortho-atomic-only test widening and partial runtime/UPF stubs. Anvil's Python3.9/runtime, current balance, partition/queue/quota and new staged checkout pins must pass the actual preflight before one held submission and release. Every final gate remains confined to one diagnostic job and production_accepted=false.

## Final reviewed pins

| Path | SHA-256 |
|---|---|
| src/dft/pa_qe_adapter_v2.py | 63655f45531939a84ad2db4c5c5debab159427bae42e7a02abf0312f9a348f11 |
| src/dft/pa_catalyst_retest.py | b1c49d2d06c93fed4438d46491d8a01532f05cd6d8b6adfed90ca9689a65baf1 |
| src/dft/pa_checked_contract.py | 67412c8363877f0a6407e382a4d3c33c6c0f6dac7b1f5de3e3968bf77755ae39 |
| anvil/90_pa_catalyst_retest.slurm | d30ca93fc02b4153c6aaeb8eefb8bf27eede3fc9bb171307b53cd021c8aeaf13 |
| tests/test_pa_qe_adapter_v2.py | 1f9ed1be9775cb1d5d2481ac3e29f9c85117c4dbf90e1e9b340c61b5bae9efc2 |
| tests/test_pa_qe_adapter_v2_real.py | 7ec9e1d7b26112246ae100e0b242a8d71b3da9d0dcf846abd2aba8923a2df6da |
| tests/test_pa_catalyst_retest.py | cccc28c1e1ebf2e85dc714c10a5a7476733db92b4cebd72221ad3eed0843590e |
| tests/test_pa_catalyst_retest_scripts.py | 46628d04389bffd24c83e8d0e2bc85663bdf710fc7b448270e583aed9a7b3574 |
| tests/qe75_real_fixtures.py | 5aeddf0fb22da95c54ad00cdbb7ef7099346f39d36b9907f29111b32ad5f73db |
| tests/fixtures/qe75_real/manifest.json | 6054cd6ee9d554b43d9a9a4be41a5daa3b32fdd48c6ac5ef25cef363299ca8d0 |
| results/pa_catalyst_retest_2026-10-04/launch_spec.json | 4c2384c6375f1c7892d33d8f6c37478243f41af3da9dd0f9ec507bcd8423e435 |
| results/pa_catalyst_retest_2026-10-04/source_xml_input_review.md | 3c2c9dc101c0d4e1779aff8abee588a6ff18a4a61904b023ac40808b2dac5929 |
| results/pa_catalyst_retest_2026-10-04/pa-catalyst-retest-remote-stage-2026-10-04.py | 065b69805c9300ccb9ccfcf473cf5350cf77b1ef51d50197afbb5fd4252a80da |
| results/pa_catalyst_retest_2026-10-04/pa-catalyst-retest-submit-held-2026-10-04.py | f07fb4c7cb5bd88c76e47a9ee11a84794a0393da3495ac7757068b72ddf79096 |
| results/pa_catalyst_retest_2026-10-04/pa-catalyst-retest-held-validation-2026-10-04.py | 7846e9ea1ee11a9dc618892037b0cdee4797db7da1b3283a9cb93f597f830507 |
| results/pa_catalyst_retest_2026-10-04/pa-catalyst-retest-release-2026-10-04.py | 829c8aae7eaab8fb0c833fe493470eb34b4cac5815b986d55f9dd57438420c01 |
| results/pa_catalyst_retest_2026-10-04/watch_retest_readonly.py | e002b26c8129094af6c7c8a0ff6860089d06b5caee86452717b36425f37b4d31 |
| results/pa_catalyst_trial_readout_prep_2026-10-04/readout_trial.py | aba5a5b7367000108d012610b631e24f0c243758fc8155dda4373c04849d5f1c |
| results/pa_catalyst_trial_readout_prep_2026-10-04/test_readout_trial.py | dc8a42c8105d13fb11c98da56d8844bd2382686f622ceb64d13606563e4107c1 |
| results/pa_catalyst_trial_readout_prep_2026-10-04/launch_sources.py | 1b93e0847b022798f6f4f03551f76d052757aa163de81d823f09205cfab5d08a |
| results/pa_catalyst_trial_readout_prep_2026-10-04/launch_snapshot.json | dcb15854775caa79577ee6eb6b623dc135d4de487e3c2b027949f8c5da2ade0b |
| results/pa_catalyst_trial_readout_prep_2026-10-04/.gitattributes | 730a35ae3d558080083c3103d9ac8100c3f6561678092abe341701dfa331eb1d |
| docs/research/pa-catalyst-retest-2026-10-04.md | 40d75c8dfc093c07216007da1df861a8104ff3ac239a2da4c49fa68433cdc863 |
| results/pa_catalyst_retest_2026-10-04/provenance.md | 9f1dd26b6a29029ccedd9e9db7143c7008819084d4c54a6b2fea951bb1025e18 |
| results/pa_catalyst_retest_2026-10-04/publish_reviewed_package.py | b5ab42dbe71eba94f6ed589de84e23862721145c68e65db545ce2110e3de463f |
| results/pa_catalyst_retest_2026-10-04/verify_retest_offline.py | 39a7837592230096883b99b62f0340913043c9b47e6e4643b2f989a4f151cf41 |
