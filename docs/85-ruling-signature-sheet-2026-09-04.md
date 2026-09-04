# 85 — Signature sheet for the seven open rulings

**This sheet elects nothing.** Every choice below is `docs/82`'s recommendation, reproduced so
the mechanics are in one place. The act that binds is your dated line in
`docs/43-prereg-week1-factorial.md`; this file is a transcription aid and has no authority.

**Why it exists.** `docs/82` drafts each signature as prose — and its prose is not what the
fixture accepts. Three mechanical traps sit between the decision and a green suite, and two of
them fail the suite *today*, before any core exists. They are fixed in the fixture header as of
`21b0b2f`; this sheet is the paired checklist.

---

## The order that matters

1. **Sign rows 1 and 2 first.** `docs/82:11-15`: they decide *what the detector counts*, they are
   genuinely blind today, and **after the census runs they can never be answered cleanly again**.
   The rest can be signed in any order.
2. **Sign before the core exists.** `tests/silentgate/conftest.py:69-70` gates seven tests on
   `os.path.isdir("silentgate")`. The moment that directory exists — even empty — seven green
   SKIPs become seven FAILURES. Rulings first, then the core, and the core in **one atomic
   commit** so the directory never exists in a half-populated state.

---

## Step 1 — append seven dated lines to `docs/43`

Append at the **bottom**, below the 2026-09-04 addenda. Nothing above the deposit line may be
edited in place. Note the line number each one lands on; you need it for Step 2.

> `[ADSORBATE QUANTIFIER 2026-09-__: ALL]` — the run-level LOCKED verdict requires the
> exactly-zero lateral axis on every printed step for **every** adsorbate atom, consistent with
> :1830's run-level rule; :1858's "any" wording continues to describe the negative-control
> population and is unaffected.

> `[TRUNCATED BLOCK 2026-09-__: SCORABLE-IF-ALL-ADSORBATE-ATOMS-PRESENT]` — a force block
> missing leading atoms is scored if and only if every identified adsorbate atom is present in
> it; otherwise the run is reported **unscorable**, a distinct outcome, never counted as
> not-LOCKED.

> `[OC20 CI MECHANISM 2026-09-__: RELEASE-ASSET]` — the 500-file sample is published as a
> sha256-pinned release asset of the public repo and the workflow downloads and hash-checks it
> against `docs/research/oc20-val_id/first500.SHA256SUMS`; a commit on which the OC20 job did not
> execute is not green.

> `[PROVENANCE RECORD PATH 2026-09-__: docs/provenance-record.md, single file, located by
> $S1_AI_USE_LOG in the CI workflow]` — the A9.1 disjointness assertion reads this file and no
> other.

> `[IF_POS RATIONALE 2026-09-__: CORRECTION FILED]` — the parenthetical at :1834 is withdrawn as
> to its **stated mechanism**; QE 7.5 prints the raw force and a frozen atom does not read zero
> for that reason. The **exclusion of `if_pos = 0` atoms stands unchanged** as a conservative
> rule. No verdict moves.

> `[PACKAGING SCOPE 2026-09-__: KEEP-AS-AI-AUTHORED]` — "packaging" is read to include the
> `[build-system]` table and package discovery, one word wider than the 2026-08-23 adoption note,
> on the ground that a build backend is not the detector and touches no scored quantity.
> Disclosed, not absorbed.

> `[X CENSUS DISPOSITION 2026-09-__: DATED LINE AND PROCEED]` — the x-axis lock figures were
> measured by a disclosed sweep on 2026-08-27, before `silentgate` v0.1 existed, and are recorded
> **as a prior prediction, not as v0.1's measurement**: 3 of 9 nosym-absent and 0 of 11
> nosym-present. v0.1 re-derives them independently; **if v0.1 disagrees, the disagreement is
> reported as the finding** and v0.1's number is the one of record.

---

## Step 2 — transcribe into `tests/silentgate/spec_rulings.toml`

**The `ruling` field does not take the prose above.** It is matched *verbatim* against each
question's `options`, which are lowercase and hyphenated
(`test_a_recorded_ruling_is_one_of_the_registered_options`, not gated on the core — it fails
today). This is the mapping:

| # | `id` | prose signature says | `ruling =` must read |
|---|---|---|---|
| 1 | `adsorbate_quantifier` | ALL | `all` |
| 2 | `truncated_force_block` | SCORABLE-IF-ALL-… | `scorable-if-all-adsorbate-atoms-present` |
| 3 | `oc20_ci_mechanism` | RELEASE-ASSET | `release-asset` |
| 4 | `ai_use_log_path` | a path | `docs/provenance-record.md` — free text, `options` is empty |
| 5 | `if_pos_parenthetical` | **CORRECTION FILED** | **`file-the-correction`** |
| 6 | `pyproject_build_system` | KEEP-AS-AI-AUTHORED | `keep-as-ai-authored` |
| 7 | `ai_x_census_disclosure` | DATED LINE AND PROCEED | `dated-line-and-proceed` |

**Row 5 is the one that bites.** "CORRECTION FILED" is not a case variant of anything — it is not
in that question's option list at all. A straight paste fails, and the failure message used to be
a bare enum rejection; as of `21b0b2f` a guard names it as *"the right decision in the wrong
form."*

**`dated_line` must cite a path that exists.** The test does `cite.split(":")[0]` then
`os.path.exists`. The abbreviation `docs/43` is **not a path on disk** and fails. Write:

```
dated_line = "docs/43-prereg-week1-factorial.md:<line>, 2026-09-__"
```

---

## Step 3 — the two rows that are not just a signature

Five of the seven are complete once Steps 1–2 are done. Two carry real work:

**Row 3, `oc20_ci_mechanism`.** Publish the 500-file sample as a release asset, then set three
repository variables the workflow reads at `.github/workflows/s1-controls.yml:64-66`:
`S1_OC20_MECHANISM`, `S1_OC20_ASSET_URL`, `S1_OC20_ASSET_SHA256`. Repository variables are
owner-only. The manifest is already staged at `docs/research/oc20-val_id/first500.SHA256SUMS`;
OC20 is CC-BY-4.0, so redistribution with attribution is permitted; ~126 MB for 500 members is
well inside GitHub's 2 GB per-asset limit.

**Row 4, `ai_use_log_path`.** The file **does not exist anywhere in the tree** —
`git ls-files | grep -iE 'ai[-_]?use|ai[-_]?log|use[-_]?log|provenance'` returns zero. It has to
be created, and `.github/ci/check_disjoint.py` fails closed on a missing log because an absent log
leaves the file list UNDEFINED, not empty. Note the auto-discovery regex is
`/ai[-_]?use|ai[-_]?log|use[-_]?log/` and **`provenance-record.md` does not match it** — so
`$S1_AI_USE_LOG` must be set explicitly, which is the better engineering anyway for a path a
registered assertion depends on. If you would rather not touch CI env, name it
`docs/ai-use-log.md` and it is found automatically, at the cost of the prose/identifier mismatch
A7.7 already flagged.

---

## Step 4 — the core, and why the directory must not appear early

`docs/43:1840` names the core: `silentgate/readers/*`, `census.py`, `classify.py`,
`direction.py`, `cli.py` — *"written and committed only by the entrant"*, with the rule quoted
verbatim from the program: **"AI may not author the object the project is named after."** A9.6
adds that nothing licenses *"tool authorship of any part of the `silentgate` core."* CI checks it
rather than trusting it: the provenance record's file list and the core path list are asserted
disjoint, and the assertion's status prints next to the controls.

Two consequences worth stating plainly:

- **One atomic commit.** `conftest.py:69-70` keys on the directory existing, and
  `test_face_end_to_end.py:140` (`test_an_empty_package_directory_is_not_a_core`) exists precisely
  to catch a half-populated one. Write all five files locally, then commit them together.
- **Fill `.github/ci/silentgate-invocation.toml` after.** Three commands and twelve schema
  pointers, **all fifteen blank today** — the interface is declared once, by you, after the core
  exists.

**Definition of done** is `docs/71:212-215`: five paths present, five in-house gates green, seven
rulings answered, invocation toml filled, OC20 mechanism decided and running in CI.

---

## What is already done for you

- The fixture's own citation example was wrong and would have broken the suite for anyone who
  followed it; fixed, with a regression test that parses the header example and asserts its path
  resolves.
- Three guards added and each verified to fail when its trap is injected: the header-example
  check, an option-vocabulary check, and a case-variant diagnoser.
- Suite state at `21b0b2f`: **55 passed, 7 skipped**.
- The seven skips are the seven rulings. They turn into seven failures the moment `silentgate/`
  exists, which is the whole reason Step 1 precedes Step 4.
