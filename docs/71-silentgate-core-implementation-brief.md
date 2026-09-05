# 71 — silentgate v0.1 core: implementation brief for the entrant

**Status:** supporting infrastructure per A7.7 — *specification and review only*.
**This document contains no implementation code and none may be added to it.** The five core
paths are reserved to the entrant by `docs/43:1840` and enforced by
`.github/ci/run_controls.py` and `tests/silentgate/`. What follows is the contract those
already-written tests and the registration impose, assembled in one place so the core can be
written against a spec rather than against a search.

Every figure below was verified against the tree on 2026-09-03. Where a source document is
wrong, this brief says so and cites the measurement.

---

## 0. What already exists, so the surface area is clear

The gap is **exactly five files**. Everything around them is built:

| built | where | by |
|---|---|---|
| the test suite (1,172 lines) | `tests/silentgate/` | AI, permitted (`docs/43:1840`) |
| adversarial fixtures + manifest | `tests/silentgate/fixtures/` | AI |
| the control runner, gates, status face | `.github/ci/run_controls.py` (614 lines) | AI |
| the OC20 runner | `.github/ci/run_oc20.py` | AI |
| the disjointness check | `.github/ci/check_disjoint.py` | AI |
| the 20-run positive/negative populations | `.github/ci/populations.txt` | transcribed from `docs/43:1864` |
| **the CLI interface declaration** | `.github/ci/silentgate-invocation.toml` | **deliberately blank — yours** |

`run_controls.py` decides the core exists by looking for **five literal names** under
`silentgate/`: `readers`, `census.py`, `classify.py`, `direction.py`, `cli.py`. An empty
directory is not a core; the face names each missing one individually.

---

## 1. Answer these seven first — they gate scoring, and three are real design decisions

`tests/silentgate/spec_rulings.toml` holds **seven** open questions, every `ruling` and
`dated_line` currently empty. **The moment `silentgate/` exists, all seven must carry a non-empty
ruling and a dated line citing a real file, or the suite fails.** (`README.md:9` says "six" — a
drift worth fixing while you are in there.)

| id | what it decides | why it is not cosmetic |
|---|---|---|
| `adsorbate_quantifier` | is a run LOCKED when **any** adsorbate atom is frozen on an axis, or when **all** are? | moves the headline census count between **96/96 and 95/96** |
| `truncated_force_block` | is a NUL-spliced / truncated output *unscorable*, or scored on what survives? | decides whether `runs/probe/Cr/s0_OOH__base.out` enters any denominator |
| `if_pos_parenthetical` | file a correction of record against `docs/43:1834`? | **the registration's stated rationale is measurably false — see §4** |
| `oc20_ci_mechanism` | published release asset vs self-hosted runner for the 500-file sample | `docs/43:1868`: a commit where the OC20 job did not execute **is not green** |
| `ai_use_log_path` | where the provenance record lives | the suite forbids any core path appearing in it, in any spelling |
| `pyproject_build_system` | packaging backend | pip-installability is the S1 deliverable |
| `ai_x_census_disclosure` | how AI involvement is disclosed on the census face | every figure carries commit + control status (`docs/43:1868`) |

**Write these rulings before the code.** Two of them (`adsorbate_quantifier`,
`truncated_force_block`) change what the detector *counts*, so deciding them afterwards would be
choosing a threshold with the answer visible — the exact move this campaign exists to indict.

---

## 2. The five files, and what each must guarantee

### `silentgate/readers/*`

Parse pw.x output. The traps are in §4; the hard requirements:

- **Header form.** Accept the count-first form of QE 7.5 *and* the older
  `Sym. Ops., with inversion, found N` form; record which form each file used. Four distinct
  count-first shapes appear in the corpus and a fifth would fail the fixture test. `No symmetry
  found` means `n_symops = 1`.
- **Force blocks must be delimited, not scraped.** Eleven corpus files carry one real force
  header plus **six** contribution blocks printed in the identical `atom N type M force =`
  format. A regex sweep of the whole file reads `7 × nat` lines and silently inflates every count.
- **Normalise CRLF/LF before any content comparison.**
- **Never shell out to `grep`.** One corpus file contains a NUL byte. **[REASON CORRECTED
  2026-09-03 — the instruction stands, its stated mechanism was wrong, and wrong in the
  dangerous direction.]** `grep` does **not** skip the file and does **not** return a clean
  zero: on `runs/probe/Cr/s0_OOH__base.out`, `grep -c force` returns **13** and `grep -l` names
  the file. What it does is detect binary, **suppress the matching lines**, and print
  `Binary file ... matches` instead. So `-c` and `-l` are *reliable* here — the original wording
  would teach an auditor to distrust exactly the file-list evidence that still works — while
  `-n`, `-o`, any content read, and **anything piped downstream** lose the lines. A second
  `grep` in a pipe needs its own `-a`; that is where a false negative is actually manufactured.
- **Two S2 readers are core too** (`docs/43:1828`): a per-step total-energy reader over the
  680-file ladder (for `span_U`, A9.3.3) and a per-deck reader returning `tot_magnetization`,
  `nspin`, `U`, `forc_conv_thr` (A9.3.2).

### `silentgate/classify.py`

**Three outcomes, and the third is not optional.** `LOCKED`, `not-LOCKED`, and **unscorable** —
`docs/43:1864` and `fixtures/manifest.toml:185` both make unscorable a distinct outcome. An
aborted or truncated output is **reported**, never silently counted as not-locked. `UNIDENTIFIED`
is a separate reported flag whose count is printed on the figure face and never dropped.

- **Census every ionic step.** No tolerance, no last-step shortcut, no dropped steps.
- The registered class definitions (`docs/43:1828 ff.`, carried from `docs/41 §6g`):
  **LOCKED** — ≥2 operations kept *and* the component symmetrised to exactly 0.0 on every step;
  **ON_PLANE** — no symmetry enforced and `max|F_axis|` below the per-corpus noise floor;
  **EXPLORED** — `max|F_axis|` at or above it.
- **Noise floor is a registered rule, not a number:** `forc_conv_thr / 20`, in that corpus's force
  units, read per deck at parse time.
- **Run-level:** LOCKED when the run has ≥2 operations and at least one lateral axis is exactly
  zero on every step for every adsorbate atom — subject to the `adsorbate_quantifier` ruling.
- **Force-only mode** (a corpus with no symmetry header, e.g. OC20): LOCKED means "exact-zero
  component on every step", with no header witness, and the output must say it ran in that mode.

### `silentgate/direction.py`

`locked_axes` is a **list of axis strings** — `["x","y"]`, `["y"]`, `[]` — not a boolean. **The x
axis must be censused**, not just y.

### `silentgate/census.py`

Assemble per-run records over a supplied path list. See §3 for the quantities.

### `silentgate/cli.py`

- Reads a temp file of newline-delimited, repo-relative POSIX paths via a `{paths_file}`
  placeholder; writes JSON to **stdout**; exits 0.
- A non-zero exit or non-JSON stdout makes all five in-house gates **NOT MEASURED** — never
  "failed". That distinction is load-bearing throughout.
- A second entry point takes `{sample_dir}` for the OC20 negative control, same JSON shape, one
  entry per trajectory, and must supply `per_step_exact_zero_count`.
- Paths are normalised on the runner's side (`\\`→`/`, leading `./` stripped), so either spelling
  matches.

Then fill in `.github/ci/silentgate-invocation.toml`: the `[cli]` commands and the `[schema]`
JSON pointers. **Field names stay yours** — the pointers are how the runner finds your names.

---

## 3. The JSON contract

Top level `{"runs": [ ... ]}`. Ten quantities per run, each named by the registration (the
invocation file cites the line for each):

`path`, `n_symops`, `nosym_in_deck`, `locked_two_witness`, `locked_force_only`, `locked_axes`,
`n_adsorbate`, `unidentified`, `n_if_pos_excluded`, `header_form`.

**Verdicts must be real JSON booleans.** `null` or absent → the gate reports **NOT MEASURED**,
never "not locked". A run missing from the census is NOT MEASURED, never a failure.

### The five in-house gates and the exact strings CI checks

| gate | passes when | detail string |
|---|---|---|
| `positive_9_9` | all 9 nosym-absent runs LOCKED on **both** witnesses | `two-witness 9/9, force-only 9/9` |
| `negative_qe_0_11` | zero of the 11 nosym-present runs LOCKED (force-only witness) | starts `force-only LOCKED 0/11` |
| `partition_20_20` | `nosym_in_deck` False on all 9, True on all 11 | starts `20/20 partition` |
| `tag_agreement_20_20` | `n_adsorbate` matches the filename tag: `s0_OOH`→3, `s0_OH`→2, `s0_O`→1 | starts `20/20 agree` |
| `two_witness_n_n` | `locked_two_witness == locked_force_only` on every CSV row | exactly `96/96 agree` |

Populations are **asserted, not assumed**: 9 + 11, disjoint, every file must exist, or the runner
exits fatally naming "not the registered N".

**OC20 green** requires `locked_rate_percent == 0.0` **and** `n_relaxations == 500` exactly.

---

## 4. The traps the fixtures were built to catch

These are the failure modes an obvious implementation walks into. Each is measured.

1. **The exact-zero token is `-0.00000000`, not `0.00000000`.** A string comparison against
   `"0.00000000"` misses it. Parse to float, or match both spellings. **[COUNT CORRECTED
   2026-09-03: 196, NOT 263.]** The negative form appears in **196 of the 1,042** `.out` files
   under `runs/` (`grep -arl --include='*.out' -e '-0.00000000' runs`). The 263 first recorded
   here is the count over **all file types**, not `.out` files, so pairing it with 1,042 — which
   *is* the `.out` count — was a category error. It reproduces only under
   `grep -arl -- "-0.00000000" runs --include='*.out'`, where the `--` ends option parsing and
   demotes `--include` to a path operand, so the filter silently applies to nothing. **That
   malformed form is itself a trap worth keeping:** it looks like a filtered count and is not.
2. **`(no inversion)` is not a safe anchor** — anchoring the header read on it misses **32 of the
   173** header-bearing files. **[CORPUS CORRECTED 2026-09-03: the 515 git-tracked outputs, NOT
   "the fixture corpus".]** The 32/173 is docs/45:1898-1913's census over all 515 tracked outputs
   (header forms 128 + 21 + 13 + 11 = 173; the 32 missed are the two `, with inversion, found`
   spellings). `tests/silentgate/fixtures/` holds three files, all generators, and exhibits none
   of this. Over all `.out` under `runs/` the same anchor misses **33 of 360** — a different
   population with a nearly identical ratio, which is exactly how the two get conflated.
3. **Contribution blocks masquerade as force blocks** — 11 files, 6 decoys each, identical format.
4. **One file contains a NUL byte.** Re-verified 2026-09-03 by byte read: `runs/probe/Cr/
   s0_OOH__base.out` is 84,708 bytes with **exactly 1** NUL at offset 81,105, **0**
   `Forces acting on atoms` headers, **10** per-atom force lines (atoms 12–21), `nat = 21`, and
   the surviving block starts at atom 12. Read bytes, not `grep` — but see the corrected reason
   above. **Note the 10 against trap 3:** a naive sweep for `force =` returns **11** lines here,
   because QE's `Total force =` trailer matches the same substring. The eleventh line is not an
   atom row, and a reader that counts it will be off by one on every truncated file.
5. **`docs/43:1834`'s if_pos rationale is FALSE, and the ruling is owed.** It states "pw.x prints
   the if_pos-masked force, so a fixed coordinate reads exactly zero for a reason that is not
   symmetry." Re-measured over **49 frozen atoms across five metals, every ionic step, 704
   frozen-atom force observations: not one prints all three components exactly zero.** QE 7.5
   prints the **raw, unmasked** force (`runs/s3/Mn/ref__2x1v.in` atom 12, flagged `0 0 0`, prints
   z = 0.04355221 Ry/bohr; largest frozen component seen 0.08723744 in `runs/Cr_slab/s0_O.out`).
   **Do not build the reader on the masked premise.** Excluding `if_pos = 0` atoms remains correct
   and conservative — adsorbate atoms are always `1 1 1`, so no production verdict changes — but
   frozen atoms cannot be a source of false LOCKED in QE 7.5, and the report must not say they are.

---

## 5. Order of work

1. **Write the seven rulings** in `spec_rulings.toml`, each with its dated line. Two of them
   change what the detector counts, so they come first, before any number exists.
2. **`readers/`** — header form + delimited force blocks + byte-safe reading. This is where the
   traps live and where most of the work is.
3. **`classify.py`** and **`direction.py`** — the three classes, the noise-floor rule, the axis
   list.
4. **`census.py`** — assemble the ten quantities.
5. **`cli.py`** + fill in `silentgate-invocation.toml`.
6. **Green the in-house controls** — the 9/11 populations have a known answer, so this is a real
   test of the detector, not a smoke test.
7. **Then S2**: the Xu deposit and the OC20 sample. That is the exposure census, and it is the
   leg the registered story ordering (`docs/43:1932`) says leads.

**Definition of done for v0.1:** all five paths present; the five in-house gates green; the seven
rulings answered; `silentgate-invocation.toml` filled; the OC20 mechanism decided and running in
CI. At that point `docs/43:1932`'s claim sentence becomes scorable for the first time — it
requires S1 + S2, which is why it has been owed since August.

---

## Review addendum — 2026-09-05: what the tests and runners demand that this brief does not say

**Status:** review comments, permitted at `docs/43:1840`; no implementation, no pseudocode. Three
reviewers read this brief against `tests/silentgate/`, the two runners and the invocation file, and
against the seven rulings elected 2026-09-04 and the OC20 artefact facts. Of the contract items they
enumerated, 69 are covered by the brief as written; the rest are below, most severe first. Every
line was checked in the tree on 2026-09-05.

### Stale since the rulings were elected (2026-09-04)

1. **§1 and §5 step 1 are discharged.** All seven `ruling` / `dated_line` fields are filled
   (`tests/silentgate/spec_rulings.toml:59-60, :85-86, :108-109, …`; `docs/43:4175-4228`).
   Do not re-answer them. The two that decide what the detector counts are now fixed:
   - **`adsorbate_quantifier = all`** — LOCKED requires the exactly-zero lateral axis on every
     printed step for **every** adsorbate atom (`docs/43:4175-4181`). §1's row still presents
     "any vs all" as open.
   - **`truncated_force_block = scorable-if-all-adsorbate-atoms-present`** — a three-way option,
     not the binary §1:45 describes: a block missing leading atoms **is scored** when every
     identified adsorbate atom is present, otherwise the run is reported **unscorable**
     (`docs/43:4183-4189`).
2. The `ruling` string must be one of that question's `options` **verbatim, lowercase,
   hyphenated**, and `dated_line` must cite the **full filename** (the test splits the citation
   at the first colon and `os.path.exists`-checks it, `tests/silentgate/test_open_questions.py:56-75`).
   Three of those tests are **not** core-gated and bind today. This brief's own `docs/43:NNNN`
   shorthand is the form that fails.
3. `README.md:9` no longer says "six"; the errata item at :39-40 is spent.
4. The OC20 mechanism is elected (`release-asset`) and executed: asset, pin and the three repository
   variables exist, and CI has verified the sample 500/500 (`docs/43` addendum 2026-09-05).
   The provenance record exists at `docs/provenance-record.md` and the disjointness row passes.
5. The corpus figures stamped "verified 2026-09-03" (:162, :172-173) predate the 2026-09-05 mirror
   pull; the `-0.00000000` count appears as 263, 196 and "117 of 480" across this brief and
   `spec_rulings.toml:54-55` — three figures for one quantity. The manifest's four header-form
   counts are **floors** the fixture test enforces both ways (`test_fixture_manifest.py:157-158`).

### The OC20 reader — absent from §2 entirely (blocks CI green)

6. The OC20 trajectory reader is a **named core reader** (`.github/ci/core_paths.txt:6-9` quoting
   :1840) and §2's readers section lists only pw.x readers.
7. The artefact is **xz-compressed extended-XYZ text**, not ASE `.traj`
   (`docs/research/oc20-val_id/README.md:34-40`): per-frame
   `Properties=species:S:1:pos:R:3:move_mask:L:1:tags:I:1:forces:R:3`; adsorbate = `tags == 2`;
   constrained atoms excluded via `move_mask`; forces are **8-decimal fixed-point text in eV/Å**,
   so "exactly zero at the stored precision" is the literal token `0.00000000` or `-0.00000000`.
   None of "extxyz", "xz", "tags", "move_mask" occurs in this brief.
8. `run_oc20.py` ties the census back to the sample: the set of **basenames** of `path` across the
   returned records must equal the 500 manifest names exactly (`run_oc20.py:280-295`), N must be
   500, every `locked_force_only` must be a bool, and **`per_step_exact_zero_count` must be a
   mapped `[schema]` pointer and an `int` on every record** or the control refuses MEASURED
   (`run_oc20.py:328-346`; pre-flight `NEEDED_POINTERS`).

### Contract items the invocation file and runners impose that §2 omits (blocks CI green)

9. **`unscorable` has no representation in the JSON contract** — ten fields, none expresses the
   third outcome §2:87-89 calls "not optional". Today a non-boolean LOCKED verdict makes the gate
   NOT MEASURED (`run_controls.py:596-598`), which is fail-closed but is not "reported as
   unscorable". The entrant decides the field; the runner side is CI work and can follow.
10. An **UNIDENTIFIED** run (`n_adsorbate` null) currently **fails** `tag_agreement_20_20`
    (`run_controls.py:562-574`) rather than reading NOT MEASURED; §2:90 says the flag is reported,
    never dropped. Same decision as item 9.
11. `runs_array` is a required `[schema]` pointer in its own right; the token does not appear in
    this brief (§2:131 says only the top level is a `runs` array). `version_cmd` is a third
    `[cli]` key no script reads today.
12. The census is invoked **once** with the union of the 20 population paths and every classifiable
    row of `docs/figs/symops_audit.csv` (96 today; predicate `int(n_adsorbate) > 0` and a non-blank
    `max_fy_adsorbate`, `run_controls.py:369-382`), and the `path` field must echo a string that
    `norm_path()` normalises to the supplied path exactly. The `two_witness_n_n` figure is
    `len(csv_rows)` at the commit CI runs against — not the literal `96/96`.
13. The command template is `shlex.split` **first**, then the placeholder is substituted per token
    (`run_controls.py:174-189`): backslashes in the template are eaten, so the template must be
    POSIX-quoted. `pyproject.toml` already declares `silentgate = "silentgate.cli:main"`, so
    `cli.py` exposes a zero-argument `main()` or the entry point is renamed there. Both pointer
    walkers now share one dialect (RFC-6901-lite: list indices, `~0`/`~1`), fixed 2026-09-05.
14. The build is green only when **all eight** gate keys are green
    (`run_controls.py:275-284`; `test_gate_fails_closed.py:156-161`): the five in-house gates
    **plus** `core_present`, `disjointness` and `negative_oc20`. §2:140 says "five".
15. The witness tie-break is unstated: where header and force disagree, **the force evidence
    wins and the disagreement is itself reported** (`docs/43:1826`).
16. The noise-floor rule has three clauses §2:97-98 drops (`docs/43:1832`): the pw.x default
    `1e-3` Ry/bohr where a deck sets none; the deliberate retention of the in-house figure; the
    per-corpus derivation. The second registered header form is **count-last**
    (`Sym. Ops., with inversion, found N symmetry operations`), and the `header_form` string has no
    fixed vocabulary — the fixtures use two incompatible ones (`fixtures/manifest.toml:52, :364`).
17. `silentgate/legacy/` is a **permitted sixth path** for a lifted legacy detector, with its
    authorship recorded in the provenance record (`docs/43:1828`; `test_gate_fails_closed.py:42-57`).
    "Exactly five files" (:17) is true of the core and not of the package.
18. Two parse traps arrived with the 2026-09-05 mirror pull and are absent from §4: an output whose
    SCF iteration counter overflowed to `***` (`runs/s3/Co/ref__2x1v.replay_ms.out`) and one that
    stopped at 500 iterations with no `!` line (`runs/s3/Ni/s0_OOH__2x1v_mir.out`).

### Process

19. The core and the filled invocation file arrive in **one commit** (the provenance record and the
    workflow edit can land before it); `.github/ci/preflight_core_commit.py` refuses an empty or
    partial `silentgate/`, checks C1–C6 and prints the git commands without running them. Run it
    first. Once the core exists, CI installs the package (`pip install .`) before invoking it —
    the step is a no-op until then. The registered dependency of the claim sentence is
    **S1 + S2 + S6** (:1932), not S1 + S2 as :213-215 says.
20. The frozen-atom figure of record is one number, not three: this brief says 49 atoms / five
    metals / 704 observations (:187-188); the elected dated line says **248 frozen-atom
    observations across three decks, maximum component 0.08723744 Ry/bohr** (`docs/43:4211-4219`).
    The dated line governs.
