# Approved catalyst P-A boundary trial — 2026-10-03

Status: implementation/prelaunch verification cleared and pushed; singleton
Anvil job21034683 is released and queued for scheduling priority. The read-only
background watcher is active. No allocated-node, QE-runtime or numerical pass
is claimed while pending. Frank approves the dated one-boundary trial proposed
in the eligible-comparison memo.
Approval is one regular whole128-core job with16h/2048CPU SU ceiling,<=200GiB,
at most six sequential QE calls each<=2h, no retry/requeue/array/chaining. It does
not approve production relaxation, a full every-step P-A trajectory, S8 ranking
or melt selection. Scientific and raw-source launch gates still apply.

## Scientific registration

Use the existing Cu8Cr23Mn35Co34 seed20/site2 clean slab at the retained cycle5
geometry and known low electronic state. The72-atom PBE/atomic-projector DFT+U
deck, U values, spin starts, smearing, cutoffs, k-points and constraints remain
unchanged. The four historical density/XML/occupation/PAW files are intentional
initialization, not a full restart. Subsequent interrupted-state continuation
requires the complete recursive checkpoint, including wavefunctions and sibling
optimizer/update files. The historical source and failed A/B records remain intact.

The initial warm evaluation's target is1e-6Ry. For this same-settings first-
boundary diagnostic only, the isolated fresh SCF uses that same target; the raw
first warm target must verify, not be inferred from input defaults. This explicit
choice does not overwrite the earlier every-step P-A plan's8.08e-8Ry fresh target
or license a production protocol. Initialization and calculation/stop/scratch
operations differ as registered; physical settings and common solver controls do
not. A converged fresh result is not an electronic-ground-state guarantee.

Sequence: three-evaluation continuous numerical control; one-evaluation stopped
candidate from the same initial seed; fresh SCF at the candidate's evaluated
geometry, not its post-move proposal; then a fresh decision before any resume.
If the fresh state is not more than10meV/cell lower, the copied candidate resumes
with inherited optimizer state for two further evaluations. If it is strictly
more than10meV lower, do not continue the old optimizer: use intentional density
reseed/history reset at the evaluated geometry and report that branch separately.
Exactly10meV or a higher fresh state does not trigger reseed. A failed/missing
fresh reference holds continuation. An independent copied-history/from-scratch
negative control establishes actual startup deletion/count0. No branch is forced.
The reseed branch is only numerically validated if its actual first evaluated
energy remains within1e-6Ry of the lower fresh reference and strictly>10meV/cell
below the original warm state, with the same geometry/settings. Copying a density
and reaching any converged state does not meet that criterion.

Control and candidate+resume must match all three ordered evaluations within
1e-6Ry energy,1e-5bohr position and1e-5Ry/bohr force tolerances. No interpolation,
endpoint-only comparison, periodic remapping or silent dropped frames. A reseed
branch cannot be spliced into a continuity pass; if no true lower-state trigger
occurs, genuine catalyst reseed remains unvalidated. Full every-step checks and
terminal fresh acceptance remain later gates regardless of this trial's outcome.

## Source and execution gates

The official qe-7.5 source files and exact URLs/SHA-256 pins are retained in
`results/pa_catalyst_trial_2026-10-03/qe_source*`. The reviewed stop observer targets
the optimizer SCF-cycle counter1/3, not BFGS accepted-step count or an arbitrary
trust-radius message. A spare ionic-loop budget permits EXIT polling after the
proposal; exact saved evaluated XML count/status255, normal user-stop completion,
and distinct proposal/energy correspondence determine the actual boundary.
Early convergence, nstep exhaustion or a missed boundary is inconclusive without
retry. Only one owned EXIT path is permitted and no stale exit file can enter a
restart copy. Pin environment MAX_XML_STEPS=0 to retain all evaluated records;
this is not an allowed CONTROL namelist keyword. XML ndiag reflects bandgroup
size in this build; actual launcher/ELPA shape is independently checked.
[QE restart contract](https://www.quantum-espresso.org/Doc/INPUT_PW.html)

Raw bindings include source deck bytes, executable/MPI/UPF hashes and actual
runtime parallel shape. BFGS prior coordinates are fractional and require the
full physical cell transform. Log forces are printed before constraint masking;
XML/BFGS forces are masked. QE if_pos0=fixed/1=free is explicitly inverted for the
offline contract. XML task-group ntasks1 is distinct from Slurm128MPI tasks.
Original optimizer points and evaluated trial points remain distinct when a
line-search rejection occurs. The source review also corrects the older blanket
claim that new-trust-radius output occurs only in a later rejection branch:
qe-7.5 has both rejection and normal-step writes. Older records remain immutable;
the chosen cycle-marker observer and actual tiny outcome are unaffected.

Every QE call requires actual scheduler accounting, the full registered7200s
allowance plus cleanup within remaining aggregate time, and unchanged immutable
source/snapshot pins. Fresh scratch must not alias restart scratch. Reject
symlinks/special files, fallback/reset on continuation, unverified consumed UPFs,
failed/stalled energies or expanded allocation. SCF iteration127 supervision,
clean-stop request, hard process-group deadline and no retry apply to every call.
The scheduler charge is capped by one128-core16h allocation, not an optimistic
solver runtime forecast. [Anvil accounting](https://docs.rcac.purdue.edu/userguides/anvil/jobs/)

Live read-only intake verifies binarySHA1d66c785..., MPI5.0.10, five UPFs and the
historical four-file initialization pins. Wholenode is UP and the user queue is
empty; CPU balance36878.2SU. These are intake observations, not execution
allocation proof. Presubmit and actual RUNNING allocation gates must recheck.
Project quota is2.2/5.0TB at intake, leaving ample room for complete independent
checkpoint copies. The installed pw.x has a package-manager hardlink; its exact
hash is rechecked as an immutable input, never rewritten. Mutable checkpoint
hardlinks and aliases remain prohibited.
The initial two read-only metadata-parser failures are retained separately; no
QE or scheduler job occurred during those checks. The$50 literature cap and
tracked$1.1105254 estimate remain separate from this approved compute cap.

## Acceptance and handoff

Implementation/process-double tests are not a catalyst runtime pass. Independent
source/implementation review, fresh tests, Linux filesystem guard exercise and
historical/scientific preservation must precede the local commit/push, isolated
remote checkout and singleton submission. Scheduler and scientific outcomes are
retained separately. After the bounded trial, report a source-bound numerical
pass, failure or inconclusive result and actual SU without a hidden rerun.

Initial fresh verification:83 evidence tests and451 compute tests/7 subtests
pass; three Windows filesystem fixtures skip. Both scientific verifiers and
9816 historical/21 unrelated byte pins pass. Independent initial review is HOLD
pending actual reseed-energy/runtime-shape and optimizer/cleanup refinements.
The corrected adapter passes retained actual tiny candidate log/XML/BFGS replay.
Linux alias guard and one Windows-only mock failure require checked receipts;
none is a new QE run or compute attempt.

Checked prelaunch gate:83 evidence and491 compute tests/7 subtests pass. The
three Windows filesystem skips are separately exercised by16 actual Linux
filesystem checks, with wrapper syntax and retained actual tiny log/XML/BFGS
replay also passing. Both scientific verifiers and9816 historical/21 unrelated
byte pins pass before/after verification. Adapter25546421..., supervisord00656aa...,
wrapper0ff3deac..., source review7efb6e27... and exact spec4bed5002... are frozen.
No production or catalyst-runtime success follows from these prelaunch checks.
Independent final preparation decision is GO_ONE_BOUNDARY_TRIAL_PRELAUNCH,
memo0d8c4e0e..., conditional on exact published/staged bytes, refreshed balance,
once-only submission, actual allocation and runtime scientific gates. No blocking
implementation finding remains in the frozen reviewed package.

Production references, matched adsorption/free-energy conventions, uncertainty-
aware ranking, population freeze and melt stock/sample-form constraints still
precede a melt candidate. None of this preparation requires Purdue/Elsevier API.

## Published implementation and once-only launch

Implementation checkpointb9f0208ee6f3cd71d0201d03b964b5c23f53d644 is pushed with
exact remote SHA agreement. Sixty explicit paths are published; all9816 historical
and21 unrelated DFT byte pins remain intact. The isolated Anvil checkout at
`/anvil/projects/x-che260157/sts_pa_catalyst_2026-10-03` verifies63 exact Git blob
pins, wrapper syntax and fresh controller PREFLIGHT_PASS. No historical checkout
or source checkpoint is rewritten. Publication receipts retain two local
whitespace/native-newline inspection failures and the final successful check;
neither involved an additional compute attempt or scientific-file change.

Exactly one `sbatch --hold --parsable --no-requeue` submission returned21034683.
Its original inspection receipt failed only because Slurm displays the pending
one-node bounds as `1-1`, not `1`. That failure remains unchanged. A separate
read-only validation proves both bounds equal1,128 CPUs/tasks,200G memory,16h,
128 billing CPUs, no array/dependency/requeue/restart. The same existing job was
released once after another PREFLIGHT_PASS, singleton-queue check and36878.2SU
balance check. There was no replacement submission or retry.

The first watcher observation at2026-10-04T02:16:37Z reports PENDING/Priority,
elapsed0, allocated CPUs0 and CPUTimeRAW0. This is not final compute accounting.
Actual RUNNING allocation and raw128-MPI/one-thread/eight-pool/ELPA4x4 bindings
remain mandatory before accepting any solver call. The watcher polls read-only
for up to24h, stopping at a terminal state or three collection failures; it
cannot submit, cancel, retry or invoke QE. Mutable watcher output stays local;
an immutable launch snapshot and explicit non-secret receipts accompany the
handoff publication. Trial outcome, raw-artifact mirroring and final charged SU
remain pending. The2048SU ceiling is unchanged and separate from the literature
estimate$1.1105254/$50; no paid literature API/key call occurred in this phase.
