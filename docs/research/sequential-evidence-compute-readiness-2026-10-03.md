# Evidence continuation and compute/melt readiness — 2026-10-03

Public evidence recovery and numerical-protocol preparation can proceed without
Purdue's pending Elsevier API. They are separate scientific lanes. Neither
completion of P-LIT nor an Elsevier token is a prerequisite for an independently
licensed numerical test; conversely, an accepted DFT result cannot close missing
literature access or validate a P-LIT proportion.

## 1. Evidence first

Baseline:7aa9de8783b1e46dcfd189c77b1f2b8c105560cf,2496 reconciled records,
176 ELIGIBLE/94 NEEDS_SI/118 UNRESOLVED,149 SI-checklist entries. Checklist and
unresolved categories overlap. All104 third reads and130 verification targets
are complete; the seven policy choices are approved. Do not repeat them.

The bounded next queue has five records. Exact-file manual downloads, with every
listed attachment retained, are a legitimate workaround independent of Purdue:

| Record | Exact missing document | Access route |
|---|---|---|
| S29636 | nre-0228_ESM.pdf | [SciOpen](https://www.sciopen.com/article/10.26599/NRE.2026.9120228) |
| S29420 | 8680_ESM.pdf | [SciOpen](https://www.sciopen.com/article/10.26599/NR.2026.94908680) |
| S29447 | cs5c08494_si_001.docx | [ACS](https://pubs.acs.org/doi/abs/10.1021/acscatal.5c08494) |
| S28435 | 8487_ESM.pdf | [SciOpen](https://www.sciopen.com/article/10.26599/NR.2026.94908487) |
| S24094 | adma202414579-sup-0001-SuppMat.docx | [Wiley](https://advanced.onlinelibrary.wiley.com/doi/10.1002/adma.202414579) |

SciOpen direct HTTP returned403; automated requests stop. ACS and Wiley remain
stopped after their earlier publisher blocks. Two distinct SciOpen pages were
requested in the preassembled root batch, the second after the first403; both
original receipts remain. Further automated batches must enforce the stop by
host/publisher before another request. There was no challenge bypass.

The [manuscript-linked Copenhagen ERDA archive](https://www.erda.dk/archives/c691ae73360009f1ebbefa040643ca7b/published-archive.html)
for S29447 is newly retained:426017216 bytes,2838 ZIP members, advertised size
match, SHA-256582dcbeb8a082516ea7b9d14fd18816e463123fc18ea4ba3bd5d33b692663c99,
all-member ZIP CRC check passes. The repository advertises no usable remote
checksum, so no remote-checksum match is claimed. It includes author TableS3.txt,
README and figure scripts, but no PDF/DOCX SI. No archive code executed, no new
eta calculated, no four method-reporting fields coded, and no complete-SI claim.
S29447 stays NEEDS_SI pending the listed document or genuinely resolving evidence
within the approved source rules. Zero new blind eligibility reads this phase.

The eight targeted holds remain: S24821/S25024 model/facet/reference,
S25856 contradictory phase, S26411 incomplete coordinates, S16323 computational
reference, S26256 contradictory ranking, S27700 explicit model/eta assignment,
S21356 computational CHE reference. Bounded new repository/correction discovery
did not resolve them. Absence of search hits is not absence of evidence. Exact
clarification needs are retained in sequential_2026-10-03/targeted_holds.md; no
author contact sent and no policy reapproval needed.

## 2. Numerical cause, then a small discriminating test

The September25 readout stands: ArmB stalls at step7; ArmA stops at segment21,
with no converged relaxed reference. It does not validate P-A's intended BFGS
continuation. Both failures remain evidence, not accepted slab energies.

The specific restart mechanism is now directly established:

- Checked runner sets from_scratch for every one-step segment and copies the
  previous .bfgs into the next scratch.
- Mirrored segment2/3/20 runtime/output pairs match their original mirror
  manifest. Each later output logs .bfgs deletion at line27, then a new BFGS
  initialization and step counter0. Their trust radii are0.0169666579,
  0.0145300293 and0.0044436439 bohr.
- QE7.5 [input handling](https://github.com/QEF/q-e/blob/qe-7.5/PW/src/input.f90)
  calls clean_tempdir for an existing scratch when not restarting; its
  [I/O module](https://github.com/QEF/q-e/blob/qe-7.5/Modules/io_files.f90)
  removes .bfgs. The
  [BFGS module](https://github.com/QEF/q-e/blob/qe-7.5/Modules/bfgs_module.f90)
  initializes counters when no history exists. This explains the retained logs,
  rather than merely correlating the stall with a small trust radius.

191 existing runner/launcher tests pass. They prove process-double contracts and
guards, not real QE optimizer efficacy. The old copying test checks that bytes
reach scratch; it never tests whether QE consumes them. Pinned production runner,
decks, launch specifications and A/B results remain unchanged.

Direction elected: offline P-A restart repair/test before another production run.
Frank selects that route and permits a suitable Anvil tiny test with a suggested
bounded SU ceiling. The repair is not
simply a flag replacement: QE's [restart contract](https://www.quantum-espresso.org/Doc/INPUT_PW.html)
requires an interrupted, cleanly stopped calculation with the same processors
and parallelization. Four density/Hubbard files alone do not prove a complete
restart checkpoint. The bounded local inventory finds no pw.x on PATH; WSL is
not installed and no checked top-level installation candidate is present. This
does not claim an exhaustive disk scan. Read-only Anvil access/runtime/balance
verification precedes any tiny-test submission; no real QE test has run.

Prospective tiny-system acceptance requirements; production remains unlicensed:

1. Pin the same QE7.5 executable/pseudopotentials, one nontrivial tiny fixed-cell
   system needing multiple ionic steps, identical numerical settings, and an
   isolated scratch per arm. Compare a continuous control, the copied-history
   from_scratch negative control, and a clean-stop/restart candidate.
2. Stop candidate segments cleanly at an ionic boundary, retain the complete
   restart inventory including optimizer/history/wavefunction state, and resume
   with unchanged rank/pool shape. Verify when forces, geometry and checkpoint
   correspond; never compare an evaluated energy with a proposed geometry.
3. Before execution, adopt the exact segment-stop mechanism and tolerances.
   Proposed tiny-test comparison tolerances:1e-6 Ry energy,1e-5 bohr coordinates,
   1e-5 Ry/bohr forces against continuous control at corresponding evaluated
   steps. These are test proposals, not changed production acceptance thresholds.
4. Require negative-control deletion/reset; candidate history retention, advancing
   optimizer state, finite clean SCFs, and trajectory/endpoint agreement. A step
   counter alone or a copied file is insufficient. Retain every failed attempt.
5. Only after real-QE acceptance, implement the additive repaired runner and its
   process-double regressions. Review a fresh A11.R3 count/cost/cap and boundary
   before any slab rerun. No new production slab job, substitute optimizer, threshold
   relaxation, allocation expansion or retry is licensed here. See the separate
   pa-offline-restart-probe-2026-10-03.md for the tiny Anvil8-SU ceiling, remaining
   nstep accounting, exact stop-boundary caveats and offline-checker limitations.

## 3. Toward melt, without conflating the lanes

| Lane | Can advance independently of library access | Remaining scientific/resource gate |
|---|---|---|
| P-LIT | Public/manual evidence; source verification; approved-rule reconciliation | Preserve unresolved entries; explicit inclusion freeze before registered method coding and primary proportion |
| Compute | Elected offline P-A diagnosis/tests and a bounded tiny Anvil probe after readiness verification | Real-QE restart validation; fresh count/cost/cap before production; accepted complete chains and held-out/generalization evidence |
| Laboratory | Confirm melt/instrument availability, stock/sample form and supervised feasibility | Dated ranking statistic/predictions, S8 freeze/deposit, chosen compositions, matched controls/replication, weigh sheet and current risk review before sample preparation |

P-LIT's176 eligible papers are not176 melt candidates. The existing low-tail
ranking is model-specific exploratory evidence, not a demonstrated fixed-current
or iridium-beating prediction. Preserve S8's hold on superior-melt selection.
The generalization alternatives are9 versus12 legs with different populations,
not interchangeable convenient deck counts; their direction and cost must be
reviewed after the protocol measurement. See September22 sizing and September16
research decisions rather than stale historical melt lists.

Frank confirms melt and potentiostat availability, with a target of about one
week (approximately October10), and says exact time/availability is not binding.
This is not a confirmed appointment date. Stock/composition and sample-form
limits remain unspecified. No laboratory message sent and no melt elected.
The next critical path is tiny numerical test -> accepted slab/chain
validation -> dated ranking/freeze -> supervised sample preparation/measurement.

## Verification and cost

Fresh evidence regressions67/67, compute-runner regressions191/191 and additive
offline diagnostic regressions36/36 pass.
Final scientific verifiers, deterministic rebuild and preservation receipts are
in results/s2_2026-09-25/full_text/sequential_2026-10-03: zero errors and zero
canonical changes; all426 baseline pins/2496 records/149 checklist rows and21
unrelated DFT files remain unchanged. Evidence/offline checkpoint8aafa8c is
pushed with exact remote SHA verification. No new paid API request
or key use this phase; conservative tracked literature estimate remains
$1.1105254/$50, not an account invoice. The$50 cap does not authorize compute.
Discovery/gate research uses GPT-6 Luna; completed screening is not repeated.

## Subsequent tiny-compute outcome

Job21024848 ran once under the8SU ceiling; jobsu reports0.1376CPU SU. The
continuous8-step trajectory agrees with the complete1+7 clean-stop/restart
trajectory inside all registered tolerances, with inherited optimizer state,
negative-control startup reset, correct actual UPFs/version/rank shape and66
mirrored-file pins. Independent review confirms tiny restart plumbing only.
SlurmFAILED2:0 remains as the original launcher's normal-terminal-cleanup false
positive; an offline startup-only gate correction and276 tests/7 subtests pass,
with no rerun. Production P-A interleaved fresh-SCF/reseed integration and a
separate count/cost/cap proposal remain next. S8 stays held; no melt candidates
elected. Details: [tiny restart readout](pa-tiny-restart-readout-2026-10-03.md).

Frank agrees to download the five exact next SI attachments. They remain absent
at the latest Downloads check; this is willingness to retrieve, not a completeness
confirmation. No source exclusion, eligibility change or method coding follows.
