# Tiny QE restart readout — 2026-10-03

The real QE7.5 restart-plumbing test passes the registered scientific checks.
This is not acceptance of the catalyst P-A protocol, a production slab licence
or a melt recommendation.

One Anvil shared job21024848, from pushed checkpoint9cbcab2, executed four QE
invocations: continuous control, interrupted candidate, copied-history negative
control and resumed candidate. Actual allocation4 cores/6GB/2h, all QE ranks,
threads, pools, tasks, band groups and diagonalization groups1. Runtime124s;
jobsu reports0.1376 CPU SU, no GPU SU. Final CPU balance36878.2SU; queue empty.
No automatic retry or second job. The$50 literature cap is separate; zero new
paid literature/API requests and the conservative tracked estimate stays$1.1105254.

## Scientific comparison

Continuous has8 converged evaluated XML steps. The split sequence has exactly
the candidate's1 evaluated step plus all7 resumed steps: no duplicated boundary,
dropped point, interpolation or endpoint-only acceptance. XML declares Hartree
atomic units; energy and force are multiplied by2 for Ry and Ry/bohr, positions
remain bohr. Original QE files, checksums and timing are retained.

| Complete-trajectory quantity | Largest absolute difference | Registered tolerance |
|---|---:|---:|
| Energy | 1.3175088e-8 Ry | 1e-6 Ry |
| Cartesian position | 1.7068798e-7 bohr | 1e-5 bohr |
| Force component | 4.0852483e-7 Ry/bohr | 1e-5 Ry/bohr |

Every evaluated SCF converges. The final energy difference is4.2188475e-14 Ry,
position1.3065254e-10 bohr, force1.8712758e-10 Ry/bohr. Independent raw-output
review reproduces the full ordering, units and maxima and clears tiny plumbing.

The stopped checkpoint has exactly1 step, XML status255 and a nonzero proposal;
the clean user-stop receipt retains the first-BFGS-count0 line and EXIT timestamp.
Its326-token BFGS file stores SCF1/BFGS1/GDIIS0. Scaled prior coordinates,
gradient and energy correspond to evaluated step1, not the unevaluated proposal.
First resumed evaluation matches that proposal; its first optimizer call is
SCF2/BFGS1 and subsequent counters advance through SCF7/BFGS6, ending with normal
convergence at8 SCFs/7 BFGS steps.

Negative control deletes its copied history before the first optimizer call,
starts BFGS0 and converges in5 evaluations. Its endpoint is close to the control,
but its different trajectory/history demonstrates why endpoint agreement alone
would not prove a restart.

All4 arm-local UPFs match SHA25627f8a7e87851d59a2698237d6ab4578d62950640f4f175781b015a0ce731f962;
raw read paths and MD5f52b6d4d1c606e5624b1dc7b2218f220 agree. Binary SHA256
1d66c7856f5d6b3cd9c66b8578e01512b16bbe907b4360e54234890712ccd6a1 matches before
and after the job, and each actual banner is7.5. All66 mirrored files rehash
against the remote inventory; the complete stopped snapshot remains unchanged.
Raw text, inputs, XML, optimizer state and receipts are in the scientific Git
checkpoint. The complete70,481,462-byte file set, including binary density/WFC
files and UPFs, is retained locally and on Anvil; binary payloads/archive stay
outside Git. Full-inventory replay requires that complete local mirror.

## Launcher outcome and offline correction

Slurm outcome remains FAILED2:0. All QE invocations returned0; continuous,
negative and resumed arms normally converged. The launcher rejected the resumed
log because its whole-output deletion check included normal final .bfgs cleanup.
That cleanup follows the convergence banner and is not a startup optimizer reset.
[QE optimizer lifecycle](https://github.com/QEF/q-e/blob/qe-7.5/Modules/bfgs_module.f90)

The original launch source136d5f7e… and88 wrapper remain in9cbcab2 and the remote
checkout; no historical outcome is relabelled. The offline corrected gate5cec00a1…
checks deletion only before the first optimizer counter, and requires negative
control reset in that same startup interval. Normal-end and adverse-startup
fixtures accompany the fix. Fresh276 tests/7 subtests pass; an offline replay
uses the immutable real outputs, not another QE run.

## Next licensed preparation, not production execution

1. Integrate this verified restart contract in an additive P-A runner; retain the
   historical checked runner and failed A/B evidence. Interleaved fresh-SCF checks
   must not overwrite optimizer history, scratch or proposal/energy correspondence.
2. Test the branch/reseed state machine and checkpoint coverage independently.
   H2 cannot validate DFT+U metastability, the10meV catalyst reseed rule or a
   converged slab reference.
3. Present a distinct production-slab protocol, count, core-hour/SU and wall-time
   cap for review before staging/submission. The unused portion of this8SU ceiling
   is not permission for another job.
4. In parallel, verify the five manual SI attachments when downloaded and resolve
   the eight source/model/reference holds. Only then can the applicable literature
   population/extraction freeze and S8 ranking/melt-selection gates close.

Fort Wayne Metals and potentiostat are available, with approximately one week
as Frank's target rather than a fixed appointment. Availability is not binding;
scientific validation and selection are. No sample preparation or melt executed.

The five files/eight holds are priority work, not the entire P-LIT backlog.
Current176 ELIGIBLE/94 NEEDS_SI/118 UNRESOLVED remains unchanged; no global
literature-completion or inclusion-freeze claim follows from this probe.
