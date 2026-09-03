# AI survey of the in-house corpus, 2026-08-27 — DISCLOSURE

**This directory exists to disclose something, not to be used.** It preserves an
documented script and its output so the entrant can see exactly what was measured, when,
and by what. Nothing in the S1 harness reads it; a test enforces that
(`tests/silentgate/test_gate_fails_closed.py::test_the_ai_survey_is_not_wired_into_the_gate`).

## What it is

`sweep.py` walks every `.out` under `runs/`, parses the pw.x force blocks, and records for
each adsorbate atom whether the F_x and F_y components are **exactly zero on every ionic
step**. `sweep.json` is its output: 480 records, one per output carrying the `Program PWSCF`
banner.

It was written at 16:51 on 2026-08-27, about forty minutes before the first file of the CI
harness, as part of choosing the thirteen fixtures in
`tests/silentgate/fixtures/manifest.toml`.

## Why it needs disclosing

Producing it was permitted and, in fact, anticipated: docs/43 :1445 says the provenance record
"records the relevant outputs (**sweeps**, amendment drafts, critique, scaffolding, CI)". So the
sweep is a logged AI product, not a boundary breach — nothing under `silentgate/` was
written, and this script is not the instrument.

What needs the entrant's attention is narrower and specific. The sweep **measured two
quantities the registered text describes as not yet measured**:

> :1858 — "Force-only, the gate is non-trivial: it passes today on y (CSV
> `max_fy_adsorbate` for the 11 ranges 4e-08 to 0.039, none exactly 0.0) and is
> **unmeasured on x** until v0.1 reports it."

> :1864 — "in-house 1×1 \*O locks y MEASURED and x INFERRED (n_symops = 4 with F_y = 0.0 —
> the 4-operation group of a 1×1 rutile(110) cell with the adsorbate on y = 0 contains both
> lateral mirrors — **F_x was never censused by the current code and is reported by v0.1**)"

Both are now censused, by an AI script, before `silentgate` exists. Over the 20 registered
P-CTRL runs of `.github/ci/populations.txt`:

| population | n | F_x zero on every step | F_y zero on every step |
|---|---|---|---|
| `nosym_absent` | 9 | **3** | 9 |
| `nosym_present` | 11 | **0** | 0 |

The three are the 1×1 \*O runs — `Cr_slab/s0_O.out`, `Ir_anchor/s0_O.out`,
`Ru_anchor/s0_O.out`, all `n_symops = 4` — exactly the class :1864 predicts locks x by
inference. The prediction is confirmed. The 0-of-11 negative control also holds on x.

The y-axis figures (9/9 and 0/11) are **not** new: :1864 and :1858 already register them,
and :1964 states the in-house controls may run because "their thresholds (9/9, 0/11,
20-for-20, n/n two-witness) are already the published record". The x half is what changed
status.

## Why that matters, stated plainly

F4 (:1848) makes P-CTRL a gate *because* "the detector is wrong in the same direction as the
finding; every number flows through code written by the person who believes the trap is
real." A control whose expected answer is already published before the detector is written
is weaker than one whose answer is not — the detector can be tuned toward it, even
unintentionally. That is a reason to disclose, not a reason the numbers are wrong.

**Disposition is the entrant's**, recorded as open question `ai_x_census_disclosure` in
`tests/silentgate/spec_rulings.toml`. The options are his: note it in a dated line and
proceed; treat the x results as AI-measured and report them as such rather than as v0.1's;
or something else. CI does not decide it and nothing here is scored against these numbers.

## What this is NOT

- **It is not `silentgate`, and must not become it.** `sweep.py` is a 60-line throwaway with
  known defects — it splits force blocks on the atom index resetting to 1, so it mis-parses
  the eleven force-decomposition files by 7×; it has no adsorbate rule beyond `index > nat -
  n_tag`; it applies no `if_pos` exclusion; it ignores the NUL-spliced truncated blocks.
  Lifting it, or any part of it, into `silentgate/` would violate :1840. A9.1's ADOPTION
  NOTE is explicit that none of the legacy detectors is lifted into the core.
- **It is not an oracle.** No test asserts against `sweep.json`, and none should. Numeric
  expectations enter the suite as golden files the entrant's core generates and he reviews.
- **It is not a substitute for the control.** The registered controls are scored by
  `silentgate`, from `silentgate`'s output, through `.github/ci/run_controls.py`.

## Files

| file | what |
|---|---|
| `sweep.py` | the documented survey script, verbatim as run |
| `sweep.json` | its output, 480 records |
| `README.md` | this disclosure |
