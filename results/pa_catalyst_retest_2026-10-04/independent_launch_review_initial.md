# Independent corrected catalyst retest review — initial

Decision: BLOCKED_PENDING_ONCE_ONLY_GUARD_AND_FRESH_VERIFICATION

Scope: independent file/source review of the corrected 2026-10-04 singleton prelaunch package. No process, test, Anvil operation, QE execution, staging, or submission was performed by this reviewer. This is an initial refusal preserved before remediation; it is not staging or submission approval.

## Blocking finding

The held submission program checks that submission_intent_remote.json does not exist, then creates it with Path.write_text before the sole sbatch. The check and creation are separate operations. Two concurrent invocations can both pass the initial check and then each execute sbatch. The local submission_intent.json is also unconditionally overwritten and not checked. This defeats the claimed hard one-job attempt ceiling under concurrent invocation. Use atomic exclusive creation (open with mode x / O_EXCL) for local and remote submission intent before sbatch, preserve the intent on any failure, and exercise duplicate/concurrent invocation refusal. The release program also uses a nonexclusive receipt reservation; use an exclusive release intent to enforce the claimed once-only release.

## Provenance and scientific review

The launch spec hashes agree with the reviewed controller, adapter v2, unchanged checked contract, wrapper, source review, and source deck. It isolates the new dated output tree and retains the previous job 21034683 / spec 4bed5002a88857515940230b20ad59e6adc345e29d8567d5b9c5f5511b0b28a2 / INCONCLUSIVE outcome. Historical readout must be bound to the exact original launch snapshot rather than the currently repaired adapter; that separate root-owned repair is pending and must be re-reviewed before final clearance.

All 27 cached official QE7.5 source files match their original retrieval receipt SHA-256. Direct inspection of the XML writers confirms presence-derived dftU, new_format=true, explicit U/species/shell/projector values, eV-to-Hartree conversion, david-to-davidson, default-to-low, functional capitalization, and operational field serialization. Adapter v2 refuses unregistered Hubbard content and binds restart_mode/calculation/prefix/max_seconds to each actual arm deck. The complete XML identity excludes declared operational fields, keeps physical/solver settings, and distinguishes evaluated XML steps from saved proposals.

The real control corpus exercises the 72-atom U parser, masked force/log/XML correspondence, actual 128-rank/8-pool/4x4 ELPA layout, three converged evaluations and saved optimizer counters. The zero-QE preflight replay pins compressed and original fixture bytes, registered five UPFs, complete XML identity and saved BFGS3/3/0. The checked-in tests retain explicit limitations: the real fresh SCF corpus uses ortho-atomic only inside tests, runtime and UPF checks are stubbed for some pproj6 pairs, and there is no real 72-atom restart log or same-deck catalyst relax/fresh XML pair. Actual carry-over, branch, and reseed acceptance therefore remain outcomes of the proposed trial.

The controller observes the registered first/third SCF-cycle event, requests a single owned EXIT file, and validates the post-shutdown saved boundary rather than treating the observer event as acceptance. It rechecks actual RUNNING allocated TRES before each call, reserves a full 7200-second call plus 120-second cleanup, uses one owned process group for teardown, forbids concurrent solver calls, caps calls at six, and retains scientific failure without retry. The wrapper requests one node /128CPUs /200GiB /16h /no-requeue. Pending held shape checks require exact cpu/billing128 and node1,16h,200G, no array/dependency/restarts. These yield the hard 2048CPU SU cap for one job. The 275–543SU estimate is planning arithmetic, not a charge guarantee.

## Nonblocking observation

The read-only watcher resets the consecutive failure count whenever the remote JSON program succeeds, even if its inner sacct/squeue/scontrol commands have nonzero return codes. Repeated accounting failures can consequently appear as ACCOUNTING_PENDING until the 24h watcher deadline. Count required accounting collection failures explicitly so the stated three-failure stop is meaningful; preserve each raw receipt. This affects monitoring, not compute resource enforcement.

## Fresh gate pending

The retained offline_initial.json includes an expected historical line-number failure and does not prove the final repaired package. Final clearance requires a fresh full relevant receipt, exact launch-snapshot historical readout checks, scientific/history preservation, reviewed remediation/concurrency coverage, and final hash equality. No GO decision is issued here.

## Reviewed byte pins

| Path | SHA-256 |
|---|---|
| src/dft/pa_qe_adapter_v2.py | 63655f45531939a84ad2db4c5c5debab159427bae42e7a02abf0312f9a348f11 |
| src/dft/pa_catalyst_retest.py | b1c49d2d06c93fed4438d46491d8a01532f05cd6d8b6adfed90ca9689a65baf1 |
| anvil/90_pa_catalyst_retest.slurm | d30ca93fc02b4153c6aaeb8eefb8bf27eede3fc9bb171307b53cd021c8aeaf13 |
| tests/test_pa_qe_adapter_v2_real.py | 7ec9e1d7b26112246ae100e0b242a8d71b3da9d0dcf846abd2aba8923a2df6da |
| tests/test_pa_catalyst_retest.py | cccc28c1e1ebf2e85dc714c10a5a7476733db92b4cebd72221ad3eed0843590e |
| tests/test_pa_catalyst_retest_scripts.py | 3612bb88ca289c0f1de471c0d9606a0fe62c778c6b70e7e3451564dcbc350878 |
| results/pa_catalyst_retest_2026-10-04/launch_spec.json | 4c2384c6375f1c7892d33d8f6c37478243f41af3da9dd0f9ec507bcd8423e435 |
| results/pa_catalyst_retest_2026-10-04/source_xml_input_review.md | 3c2c9dc101c0d4e1779aff8abee588a6ff18a4a61904b023ac40808b2dac5929 |
| src/dft/pa_checked_contract.py | 67412c8363877f0a6407e382a4d3c33c6c0f6dac7b1f5de3e3968bf77755ae39 |
| results/pa_catalyst_retest_2026-10-04/pa-catalyst-retest-remote-stage-2026-10-04.py | 065b69805c9300ccb9ccfcf473cf5350cf77b1ef51d50197afbb5fd4252a80da |
| results/pa_catalyst_retest_2026-10-04/pa-catalyst-retest-submit-held-2026-10-04.py | f07fb4c7cb5bd88c76e47a9ee11a84794a0393da3495ac7757068b72ddf79096 |
| results/pa_catalyst_retest_2026-10-04/pa-catalyst-retest-held-validation-2026-10-04.py | 7846e9ea1ee11a9dc618892037b0cdee4797db7da1b3283a9cb93f597f830507 |
| results/pa_catalyst_retest_2026-10-04/pa-catalyst-retest-release-2026-10-04.py | 829c8aae7eaab8fb0c833fe493470eb34b4cac5815b986d55f9dd57438420c01 |
| results/pa_catalyst_retest_2026-10-04/watch_retest_readonly.py | 0e1c13467b02e52eb78dbf011bc2063c30cb2386ac0aec6fbe73efdd6e1c90c9 |
| results/pa_catalyst_retest_2026-10-04/verify_retest_offline.py | bf5f726d89244065f2d0d4b80d393f12bc91c8bf7779a28348d9fd392cc5b5cc |
| results/pa_catalyst_retest_2026-10-04/publish_reviewed_package.py | d58ec607075d8a7ea171b8df9566ae18353fe8a7ffae18b924f577d89b8399e8 |
| results/pa_catalyst_trial_2026-10-03/source_boundary_review.md | 7efb6e27d9859eff629df0cc6dfcd90ef9e17b74819e9500ee398b5e432addac |
