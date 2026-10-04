# Catalyst XML validator repair — 2026-10-04

Status: source-backed correction, checked offline verification and independent
GO_OFFLINE_XML_REPAIR_ONLY clearance pass; publication pending. No new Anvil job or paid literature/API
call is part of this phase. Original job21034683 remains FAILED3:0 and its trial
receipt remains INCONCLUSIVE. A corrected post-hoc control receipt cannot turn
the unexecuted candidate/fresh/resume/reseed/negative arms into a trial pass.

## Cause and bounded correction

The original adapter required a dftU/lda_plus_u child that the pinned QE7.5
caller/initializer does not emit. QE's restart reader instead derives the flag
from dftU presence. The synthetic Hubbard fixture contained that invented child
and omitted actual new_format=true; it did not cover the real format.

The repaired validator requires exactly one explicit new-format dftU and keeps
the original explicit kind0, atomic projector and complete species/shell/U map.
An optional boolean, if encountered, must still be unique and true. Missing
registered values are never copied from the deck. Unregistered Hubbard_Um/V/back
interaction channels are refused; existing permitted zero J/alpha/beta values
remain permitted. No SCF target, U value, energy/force tolerance, geometry/mask,
UPF, MPI shape, solver/supervisor deadline, controller or launch-spec change.
The physical Hubbard checks cover XML.input; actual XML.output bindings were
independently inspected, not promoted to a new validator-output acceptance gate.

Primary source/actual XML locations and27 verified source pins are retained in
results/pa_xml_repair_2026-10-04/source_schema_review.md. No general XSD-default
or alternative-format compatibility claim follows from this bounded repair.

## Preserved evidence and verification scope

Current clean starting checkpointcbf7c7d includes the already completed raw
mirror, scratch dry-run, post-run readout and unrelated SI recovery. Those
records are reused, not repeated or changed. The new phase pins10005 tracked
and21 unrelated files; only the adapter, its faulty test fixture and TODO are
intentional existing-path edits. All other tracked history remains byte-exact.
Original adapter25546421... is retained separately to reproduce the rejection.

The existing19-file control mirror is rehashed before/after replay. Its full
403-file remote inventory covers15.2GB, but the129 bulk wavefunction/density
files remain size-only and on Anvil. This repair does not claim a fully hashed
or mirrored continuity checkpoint, nor delete/move any remote file.

Checks: original rejection; repaired three-evaluation control settings/threshold,
global counters[1,2,3], actual runtime/UPF/log/XML/geometry/force bindings;
actual72-atom saved control optimizer3/3/0; retained non-Hubbard tiny plumbing;
47 new parameter-expanded adversarial cases; fresh relevant historical/evidence
regressions and both scientific verifiers. Control-only replay is distinct from
the unexecuted carry-over and warm/fresh decision tests.

The initial round retains83 evidence passes and610 compute/readout passes with
one frozen-line-number failure, three existing Windows filesystem skips and
one historical citation test checked separately. In the checked round both
historical fixed-source test logics run against the byte-identical launch
snapshot, rather than current repaired source line numbers. This avoids changing
historical tests or disguising source supersession by manipulating line counts.
Previously verified Linux filesystem guards remain relevant because no filesystem
or process-supervision code changed in this repair.

Checked round:83 evidence tests and610 automated compute/readout tests pass,
with7 subtests and three existing Windows filesystem skips. Both separately
executed frozen-source test logics pass, as do both scientific verifiers.
All10002 untouched tracked files and21 unrelated files match before/after.
Original rejection reproduces exactly; repaired control validates all three
evaluations with energies-7551.866334708392,-7551.868205125370 and
-7551.869475892178Ry, global counters[1,2,3], target1e-6Ry and actual128MPI /
one thread / eight pools / ELPA4x4. Saved optimizer counters3/3/0, positive
nr_step_length0.0756056991bohr and inactive tails0 validate against the third
evaluated state. The retained non-Hubbard tiny replay also passes. All19 mirror
files remain byte-identical. There is no remaining-arm, full-trial or production
pass, and no new QE call or SU charge.

Checked adapterSHA5e77b8b30789acadd104d9ac14368dfe28b5a88b2b2b84e7b8c8f2bfad10980a;
verificationSHA74e5610244d2a292b2d3e65b6094f57916b99356a2b89d4f9ddc39e5b41d6386;
raw replaySHAc4fcf94f77c42daab8e955043346eacedd1d2d1239d11cbe232148c93ad886c1.

## Next compute decision — proposed, not approved or submitted

Recommended next experiment is one corrected instance of the same one-boundary
P-A numerical trial, after the offline correction is independently cleared.
It tests the hypothesis the first job never reached; the first job supplies no
evidence favouring P-C over repaired P-A.

Proposal: the same72-atom Cu8Cr23Mn35Co34 seed20/site2 cycle5 low-state clean slab,
physical settings and registered sequence, first warm/fresh conv_thr1e-6Ry;
one new regular wholenode job,128 billing/MPI CPUs,200GiB,16h/2048CPU SU ceiling,
at most six sequential7200s calls, no array/chaining/requeue/automatic retry,
highmem/GPU/production/every-step/terminal/S8/melt. Expected full RESUME cost
about430–540SU is an estimate from the measured control, historical fresh-SCF
times and an unmeasured copying allowance, not a cap or guaranteed outcome.
The first job's102.8622SU remains separately charged; unused allowance is not
permission for a second job. The$50 literature budget does not cover compute.

Before any launch: explicit approval for this new singleton, new isolated output
root and exact reviewed dependency/spec/review pins, a local-first commit/push,
fresh resource/balance/queue/deck/UPF/seed/runtime checks, and unchanged scientific
acceptance gates. The existing frozen Anvil checkout/spec must not be updated or
reused in place. No fresh solver or production/melt result is claimed here.
