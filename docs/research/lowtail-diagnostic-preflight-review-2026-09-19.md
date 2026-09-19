# Clean-slab SCF diagnostic: offline preflight review

Date: 2026-09-19. Scope: the five fixed-geometry SCFs in `results/lowtail_slab_scf_diag_2026-09-19/launch_spec.json`, their staging and held-array controls, and complete terminal evidence collection. No launch or remote action belongs to this review.

## Portability and preserved history

The original specification contained Windows separators in its manifest and extracted-coordinate file paths; both shell wrappers also contained Windows separators in executable paths. The builder now serializes these paths with `as_posix()`. The specification and wrapper references follow that serialization, and their embedded specification digest follows the corrected bytes.

Exact original bytes for the specification, both wrappers and the builder remain in `results/lowtail_slab_scf_diag_2026-09-19/pre_portability_fix/`. Its `preservation.json` records their hashes, lengths and original commit `20cf9e9bcac0fce9e76db7d32b938345025140c0`. The corrected specification SHA256 is `72838973c58bac1482c39391d89fc7cfd0c7930545016897032867eed4b22607`.

The path correction does not change any of the five scientific decks, input source hashes, geometries, mixing choices, thresholds, job population or resource budget. Deterministic builder checking and an old/new comparison normalized only for path separators must establish this before the replacement pushed boundary is eligible for staging. The launcher rejects non-POSIX, absolute and traversing paths even after this correction.

## Maintenance window

The [Purdue Anvil maintenance notice](https://rcac.purdue.edu/news/7788) gives Sep 21, 2026 at 20:00 EDT as the end of the outage, equivalent to **Sep 22 at 00:00 UTC**. The previous wait deadline, Sep 21 at 12:00 UTC, expired twelve hours before that advertised recovery. The default wait deadline is now Sep 23 at 12:00 UTC to allow a recovery margin. The observation deadline remains Sep 25 at 12:00 UTC. Deadlines require time zones, polling must be positive, and an expired watcher starts no new remote poll.

## Launch and evidence invariants

- Every staged input and every local execution or parsing source must match the full pushed boundary commit, the local snapshot and its staged receipt. Resume and release repeat these checks; remote staged bytes are hashed again. This includes the launcher, SCF tracer and canonical readout parser, which are not all remote-upload inputs. Checkout/index newline differences therefore fail closed and must be resolved before banking the boundary.
- A durable submission-intent receipt precedes `sbatch`. An ambiguous response blocks a second submission until the actual scheduler outcome is reconciled. A local exclusive lock prevents competing launcher instances; a stale lock requires inspection. Existing queue and receipt guards remain in force.
- Held inspection requires the exact parent array, owner, working directory and command, five tasks at concurrency two, 128 one-CPU ranks on one node, the specified account/partition/memory/time and exact excluded-node set. Any mismatch leaves the array held. A successful release is recorded before the follow-up scheduler query.
- Accounting requires the exact five array task identities. Parent and batch records cannot satisfy that denominator. Unexpected or conflicting task identities are errors. Every terminal leg remains in the readout, including failed or missing-artifact legs.
- Raw output, runtime deck, QC, projection input/output and stop markers are mirrored by named path with hashes and bounded reads. Differing local evidence is never overwritten. Missing artifacts remain explicit. Interrupted terminal transfers retry until the watch deadline and reuse identical bytes; evidence collisions and identity errors remain hard failures.
- Failed rows still require a matching stage, row, job, pinned input and exact permitted runtime rewrite before a residual crossing is attributed. Available hashes are checked. Failure receipts legitimately omit final output/runtime hashes; their absence does not alone invalidate identity, but prevents successful-SCF acceptance when required success hashes are absent. Unverified crossings remain null.
- Accepted diagnostics require clean terminal scheduling at 128 ranks, a COMPLETE QC receipt, matching mandatory hashes, exact runtime and projection inputs, process limits, independent canonical SCF and force checks, a single SCF cycle satisfying the actual deck threshold within the iteration cap, and complete projection evidence. Large forces are allowed for this fixed-geometry numerical diagnostic. A residual below 1e-6 Ry remains a diagnostic observation, not acceptance at the tighter deck target.

## Verification and limits

Focused offline regressions cover POSIX paths, the exact five-task denominator, held resources and identity, duplicate prevention after ambiguous submission, immutable evidence, independent SCF/QC rejection cases, complete failure denominators, source/boundary drift, failed-row identity, watcher locking, deadline behavior and transient collection retries. The successful-SCF fixture uses the real force, canonical-output and SCF-trace parsers; its projection parser is isolated. Existing projection/parser suites remain relevant complementary checks.

The parent execution session must run the tests after source freeze and record the actual outcome. Suggested commands from the repository root:

```text
python -m pytest tests/test_lowtail_slab_scf_diag_launch.py tests/test_qe_relax_trace.py -q
python src/dft/lowtail_slab_scf_diag.py --check
```

The parent session has confirmed the path-only builder check, normalized old/new specification equality and all scientific worktree pins. It found one existing committed-byte mismatch for `results/lowtail_slab_scf_diag_2026-09-19/cu8_cycle5_positions.json` caused by line-ending normalization; a narrow `-text` attribute preserves the exact already-pinned local bytes when staged. No scientific content changes. Full launcher regression results, Git index byte equality and the replacement pushed boundary remain the parent's verification responsibilities. No evidence here establishes that Anvil is reachable, that an array has been submitted, or that any SCF diagnostic has finished. The results will diagnose numerical convergence at frozen geometries; they will not establish relaxed clean-slab references, adsorption energies or a census winner.

## Executed checks — 2026-09-19

The verified isolated desktop ran the launcher, SCF-trace, research-batch, force-audit and canonical-panel suites: **190 tests passed**. The deterministic builder check passed, and independently normalizing the historical specification's path separators gives exactly the corrected specification. Every frozen file hash matches. The verification receipt is `results/lowtail_slab_scf_diag_2026-09-19/offline_verification.json`. These are offline checks; live scheduler acceptance and submission remain untested.
