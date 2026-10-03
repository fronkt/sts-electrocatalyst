# Tiny P-A restart probe — prelaunch clearance

GO — tiny probe only. Fresh261-test/7-subtest regression passes and the88 wrapper
pins the exact reviewed runner. No production acceptance, slab submission,
allocation expansion, automatic retry or laboratory selection follows.

Final source SHA-256:
136d5f7ef00c4014a78897951d6cd287d0bb5058b3e12fe317d61ad6c1f47ec4

Final test SHA-256:
8a7beb791613953c9b88dbd9911a0a64a907d06e1b2763a680cfa5c2b1b7eb98

Final wrapper SHA-256:
dd610b46e475a8f3adbbfa0167ae16265f58a0692b40f581b43aa6d3ac8a981b

Independent source review withheld release at the initial failed-arm/UPF gates,
the later-only trust marker, a mandatory checkpoint-local UPF assumption, and
the unused arm-local UPF copies. Each finding is retained in the plan/lessons and
separate test receipts. The final targeted review reports no remaining launch
blocker, contingent on the fresh tests and wrapper pin, both now verified.

The first BFGS count0 triggers EXIT only after the first XML step/post-SCF poll;
saved one-step XML, status255, nonzero proposal and BFGS1/SCF1/GDIIS0 verify the
actual stopping boundary. Negative must delete history/start0 and converge;
resumed must inherit BFGS1/SCF2, show no downgrade/initialization and evaluate the
saved proposal. Launcher0 remains distinct from full real trajectory acceptance.

Every deck points pseudo_dir at a rehashed arm-local UPF, with input manifests.
QE restart may restore the saved XML pseudo_dir: if no saved UPF exists, the
fallback may use the retained candidate-local copy instead of the resumed-local
copy. Both match the pin. Retain raw read-path logs to determine the actual file;
do not claim a consumed path solely from the resumed input. No checkpoint mutation.
[UPF fallback](https://github.com/QEF/q-e/blob/qe-7.5/Modules/read_pseudo.f90)

Fresh preservation audit:426 historical,21 unrelated DFT,6 production and16
original source/Downloads pins match; zero errors. No new paid API call, QE run
or Slurm submission has occurred at this clearance checkpoint.

Launch boundary: local explicit-path commit/push and exact remote SHA; fresh
isolated sparse checkout and byte pins; submit exactly one held shared job with
4 cores/6GB/2h/no-requeue, verify requested billing4, then release. The runner
rechecks actual RUNNING allocation before QE. Total ceiling8SU across all arms.
No automatic retry if timing, checkpoint, convergence or trajectory gates fail.
