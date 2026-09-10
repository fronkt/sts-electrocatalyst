# Allocation assessment — do not file an STS supplement — 2026-09-10

Read-only assessment. **No allocation request was submitted.** Prompted by the question of whether
to request more ACCESS allocation for this campaign and for a separate ML project.

## 1. Live balance

`mybalance` on Anvil, 2026-09-10:

```
Allocation     Type    SU Limit    SU Usage   SU Balance
che260157       CPU    100000.0     45559.7     54440.3
che260157-gpu   GPU       150.0         0.0       150.0
```

**54.4 % of the CPU allocation and 100 % of the GPU allocation are unused.** The award runs to
2027-08-12.

## 2. Why a supplement should not be requested

Policy read from `allocations.access-ci.org/allocations-policy` and `/how-to` on 2026-09-10:

- A supplement is a **one-time** increase per award period, capped at half the opportunity's
  ACCESS Credit limit.
- It requires a justification describing *"why more resources are needed to complete the work in
  progress"*, plus an uploaded progress report.

With more than half the CPU allocation and all of the GPU allocation unspent, that justification
does not exist. Filing now would spend a single-use lever to obtain capacity already held, and
would leave nothing available if a genuine overrun appears before 2027-08-12.

The binding constraint on this campaign is the **2026-11-05 report lock**, not compute. That was
already the recorded conclusion when 70,950 SU remained (`reference_access_allocation`); it is
still true at 54,440.

**Worst-case remaining spend, priced against banked per-deck costs** (1x1 nat 20 = 6.6 core-h;
2x1v nat 36 = 18.6 core-h; nat 39 = 13.8 core-h, all np=128): the 22 HEA DFT decks are 2x2,
72–75 atoms, so roughly 4–8x the nat-36 cost, i.e. ~75–150 core-h each, ~1,650–3,300 core-h for
the set. Add S5 BEEF, the Ru second-PP control, and the repair sequence, and allow a full repeat
of the Ru nspin=2 disaster (5,216.7 SU for 0/16 converged) as the tail case. That is of order
10,000 core-h against 54,440 remaining.

## 3. Correction — the FAILED core-hour total is not a wasted-compute total

An earlier reading of `sacct` since 2026-09-06 grouped ~3,845 core-h under Slurm FAILED
(`hea-followup` 14 jobs / 2,784.8; `hea-numerical` 3 / 981.8; `hea-sensitivity` 1 / 78.4) and
treated that as wasted. **That reading is wrong.**

`docs/research/hea-failure-assessment-2026-09-10.md` establishes that the follow-up runner rejected
valid output because it accepted only a nonempty `charge-density.dat` and not `charge-density.hdf5`.
**Twelve valid follow-up SCF/projection results were recovered and hash-verified without rerunning
DFT.** Their historical Slurm FAILED labels are scheduler state, not scientific failure.

Genuinely lost, per that assessment:

| category | core-hours |
|---|---|
| two follow-up attempts that genuinely failed to converge | 940.373 |
| one sensitivity endpoint rejected on `IEEE_INVALID_FLAG` (exit 16) | 78.4356 |
| **total** | **~1,019** |

Not every FAILED `sacct` row has been reconciled to a category here, and the assessment's own
item 4 asks that scheduler failure, recovered valid result, nonconvergence and exception rejection
be kept split. The point stands regardless: there is no systematic compute haemorrhage, and no
allocation-shaped problem to solve.

## 4. The separate ML project

Capacity is not the issue there either — 150 GPU-h are unused against a ~106 GPU-h need. The issue
is **scope**: this allocation was awarded against an electrocatalysis project description and is
recorded as STS-scope only. A separate Explore ACCESS project is the correct instrument, drafted
at `C:/Users/frank/pxrd-flow/docs/access-explore-request-2026-09-10.md`.

Note on who files: **Frank is his own PI** — a Purdue research staff appointment satisfies ACCESS's
"researcher or educator at the graduate-student level or higher", and CHE260157 already exists under
his PI-ship. So a supplement here, or a new project there, is self-service. That makes the
multiple-project rule the live constraint instead: a PI gets one project per merit-reviewed grant
plus **one** unfunded research project, and if CHE260157 is that one, a second unfunded project may
be questioned. Explore review is eligibility-and-suitability rather than a panel, so testing it
costs about two business days.
