# Independent offline XML repair review

Decision: GO_OFFLINE_XML_REPAIR_ONLY

The frozen repair has no remaining blocking finding within its offline,
source-emitted QE7.5 new-format scope. This decision permits no second job,
automatic retry, continued solver arm, production relaxation, every-step P-A
validation, terminal acceptance, highmem/GPU/S8 or melt release. Job21034683
remains FAILED3:0 and its original trial remains INCONCLUSIVE. Reinterpreting
its control cannot supply the unexecuted candidate/fresh/resume/reseed/negative
arms or establish a complete trial pass.

This review used filesystem reads, pure-JavaScript comparisons/rehashing and
creation of this new memo only. No processes, shell, Git, SSH, network or QE
were run by this reviewer. The reviewer read the receipts; the reviewer did
not execute the reported tests or replays.

## Frozen implementation and review pins

| Artifact | SHA256 |
|---|---|
| src/dft/pa_qe_adapter.py | 5e77b8b30789acadd104d9ac14368dfe28b5a88b2b2b84e7b8c8f2bfad10980a |
| tests/test_pa_qe_adapter.py | aa0944f823c1fdd04a4ce0588f36ffa75908cc897854aad732c5b6c8841e308f |
| tests/test_pa_qe_schema_repair.py | 808d6f1a51d231e053dce8f87b4670de11c334b9379ba57f734b0e8db6ad9559 |
| src/dft/pa_catalyst_trial.py, unchanged | d00656aa0e7e666f75900190ccc703c1fd0fee8293738a311ea9ab5880b368ce |
| replay_control.py | 496f4937a218ebf6a38aace5d797d5321bfc224b9e207d58bcfccf4d71b3d103 |
| verify_repair.py, final checked helper | be553498bc852f1ba0e7df119816930471c90e4e375b0dd9b0674207df31a64e |
| launch_adapter_original.py | 255464215aa898d0c9d34317a1be9b16fb27ba6d35108e0ca78215331a628879 |
| source_schema_review.md | f99bb7cd345da1e1cc09cf39c6cd26d8026d236241a02f54e3a44df388ef35ea |
| baseline.json | d64457792af5f44950fce9436558551272efad780b34d341f4fa355f219418bc |

Unqualified paths in the table are in results/pa_xml_repair_2026-10-04.
The exact repaired adapter/test diff, all47 parameter-expanded new adversaries,
both complete replay/verification helpers, relevant historical tests, source
memo, actual control XML and proposed repair document were reviewed. All five
code pins in verification_checked were independently recomputed and match.

## Bounded correction and unchanged scientific checks

The adapter diff replaces the invented mandatory lda_plus_u child with an
explicit new_format="true" requirement. If a boolean child is encountered, the
existing unique-element/strict-boolean check still requires one true value;
false, malformed or duplicate values fail. Exactly one dftU, explicit kind0,
source atomic projector, exact species/orbital/U map, finite values, unit
conversion and duplicate rejection remain mandatory. Missing registered fields
are not inherited from deck metadata. Hubbard_Um/V/back are now explicitly
refused, including zero-valued unsupported channels; nested background U2 cannot
hide in an unparsed outer element. Existing zero-valued J0/alpha/alpha_back/
beta/J entries remain allowed, while nonzero values remain refused.

The only original fixture change replaces its invented flag/missing-format
shape with source-emitted new_format=true. The47 new cases exercise absent/
duplicate dftU, malformed/absent format, optional flag uniqueness/value, missing/
duplicate/changed kind and projector, complete U species/case/shell/value/units/
drop/extra/duplicate/nonfinite adversaries, no-Hubbard inputs, all three forbidden
channels including nested background values, and zero/nonzero existing couplings.

No geometry, constraints, source settings/U values, SCF threshold, tolerance,
UPF binding, MPI/ELPA shape, saved-state parser, filesystem guard, controller,
deadline, stop observer or launch spec changed. The source review explains
caller emission versus restart inference and retains all27 matching official
source/build pins. It makes no XSD-default or general alternative-format claim.

Physical Hubbard validation still covers XML.input only; actual output bindings
were separately inspected in the source review. Output's three Hubbard_Occ and
44 Hubbard_ns entries are occupation metadata/state, not unregistered interaction
couplings. No new validator-output acceptance gate is claimed by this repair.

## Replay safeguards and observed evidence

replay_control rehashes the existing19-file mirror against its retained remote
inventory before/after, rejects a stale EXIT, verifies process contract/global
cycles and reuses actual input/log/XML/UPFs. The original byte-identical adapter
must reproduce exactly `one XML lda_plus_u required`; any other exception or
unexpected original success fails. The repaired control then must pass all
existing raw bindings, first threshold, evaluated counts and source-bound BFGS
checks. Adapter bytes must remain unchanged during replay. The retained tiny
non-Hubbard candidate checks the unaffected branch. No helper invokes QE,
submits a job or tries to execute any remaining catalyst arm.

The checked replay reports three control evaluations, global[1,2,3], XML255,
MPI128/one thread/npool8 and actual ELPA4*4, first conv_thr1e-6Ry, and complete
72-atom BFGS dimension226/counters3,3,0, positive NR length0.0756056991bohr and
zero inactive tails. Actual log/XML energy, masked force, geometry, input
settings and consumed-UPF bindings passed. The tiny non-Hubbard replay has one
evaluation/global[1]. These are retained-data reader checks, not new solver runs
or continuity/reseed acceptance. The reviewer independently rehashed all19
current mirror files; sizes and hashes match the before/after replay records.

The previously committed403-file/15.2GB remote inventory includes129 bulk files
that remain size-only and on Anvil. This offline review does not claim those
files were newly downloaded/hashed or form a fully verified continuity snapshot.
Existing mirror/dryrun/readout evidence was reused, not repeated or modified.

## Verification receipts and frozen-source test handling

| Receipt | SHA256 |
|---|---|
| verification_initial.json, retained failure | d20514ba5f76ce2bb19e99a1493d03c7ca97234e66c3327f99bdc357b167f3ba |
| verification_checked.json | 74e5610244d2a292b2d3e65b6094f57916b99356a2b89d4f9ddc39e5b41d6386 |
| raw_replay_checked.json | c4fcf94f77c42daab8e955043346eacedd1d2d1239d11cbe232148c93ad886c1 |

The initial verification failed a second historical fixed-line assertion before
raw replay. It retained83 evidence passes,610 pytest passes/one failure/three
Windows skips/one deselection/seven subtests; it is not relabeled successful.
The checked round reports83 evidence passes,610 pytest passes/three skips/two
deselections/seven subtests, both scientific verifiers and42 recovery reads.
Before/after10002 unchanged historical files plus21 unchanged unrelated files
(10023 checks) have no errors. The three intentional existing-path exceptions
are adapter, its fixture and TODO; the baseline originally contains10005 tracked
files. Skips are not reported as passes, and no new Linux runtime test is claimed.

Both deselected historical items are checked separately with equivalent full
logic: exact criterion citations against the pinned original launch snapshot,
and registered call-table/prefix/tolerance assertions against the unchanged
controller plus the original adapter's literal at line845. The reviewer compared
the helper to historical test42-46 and79-88; all assertions are retained. Only
those two named items are deselected; the other readout/regression tests run.
No historical test, citation, readout source or line count is edited to disguise
source supersession. Historical launch spec and both launch reviews retain their
original hashes. Phase-only .gitattributes protects exact new receipts without
changing global or historical attributes.

## Proposed next singleton and authority limits

docs/research/pa-xml-repair-2026-10-04.md was read in full. Its next experiment
is a proposal, not a launch specification or approval: same72-atom seed20/site2
cycle5 low-state clean slab and physical settings/sequence, first warm/fresh
threshold1e-6Ry; one regular wholenode128-MPI/one-thread/200GiB job,16h/2048CPU SU
ceiling, at most six sequential7200s calls and no array/chaining/requeue/retry.
The430-540SU full-RESUME estimate is uncertain, not a guarantee or replacement
for the ceiling. The first job supplied no comparative P-A/P-C evidence.

The document was reread after its checked counts, control energies/state and
receipt pins were updated; those statements match the retained checked receipts.
Its reviewed pre-publication SHA256 is
57c5bb97337aec01c54c5d4aedca4fa6b9bcccb8db05c488a9e19cc0e33240bf.
A later clearance/publication-status sentence may supersede that document pin;
the reviewed scientific body, proposal and authority limits must not change.

The prior102.8622SU is the exact accounting-derived370304 CPUTimeRAW/3600;
the preserved jobsu display102.8608 uses rounded walltime0.8036h. Neither is
erased or offset by unused allowance. A literature/API budget is not compute
permission. Updating the proposal/TODO status from these verified receipts does
not change frozen implementation bytes or authorize a solver invocation.

Before any second singleton, explicit new approval remains required, together
with a new isolated output root, new exact reviewed dependency/spec/review pins,
local-first commit/push and fresh resource/balance/queue/deck/UPF/seed/runtime
checks and live allocation/cap gates. The old frozen Anvil checkout/spec must
not be replaced or reused in place. Production/every-step/terminal/S8/melt remain
unapproved. This memo clears only the bounded offline XML repair; all absent
scientific arms and any future compute decision remain separate.
