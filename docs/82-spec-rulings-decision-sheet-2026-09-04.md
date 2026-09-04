# 82 — the seven open rulings: decision sheet

**Status: recommendations only. Nothing here is a ruling.** Each row is elected by *your* dated
line in `docs/43`; this sheet assembles the evidence, states a recommendation with its reasoning,
and gives you a line to sign or overwrite. `tests/silentgate/test_open_questions.py:41` exists
specifically to reject a ruling recorded without a dated line behind it, so the signature is the
act, not the table.

**Why this is the critical path, and why two rows have a real deadline.** `silentgate/` does not
exist, so all seven currently SKIP. **The moment the core is committed they become failures** —
writing the core does not unlock the census, answering these does. And two of them
(`adsorbate_quantifier`, `truncated_force_block`) decide *what the detector counts*. They are
genuinely blind today because the census has not run. **After it runs they can never be answered
cleanly again**, which is the move this campaign exists to indict. Answer those two first, even
if the rest wait.

Two rows (`oc20_ci_mechanism`, `ai_use_log_path`) additionally block the control face **today**,
before any core exists.

Every measurement below was re-derived against the tree on 2026-09-04, not copied from the
register.

---

## 1. `adsorbate_quantifier` — ANY adsorbate atom, or ALL? → **recommend `all`**

**Registered at** `docs/43:1858` (any) vs `:1830` (all). **Decides** the registered n/n
two-witness agreement count: **96/96 under ALL, 95/96 under ANY.**

**Re-measured.** The single flip is `runs/probe/Ru/s0_OH__dipole.out`, and it is exactly as the
register describes:

| atom | x | y |
|---|---|---|
| 19 | `0.00074807` | **`-0.00000000`** — exactly zero |
| 20 | `0.00066885` | `-0.00000018` — **not** zero |

**Recommendation: `all`.** Three reasons, in order of weight.

1. `:1830`'s run-level rule already says it literally — LOCKED when "at least one lateral axis is
   exactly zero on every step for **every** adsorbate atom." Choosing `all` is not electing a new
   rule; it is declining to contradict the one that is registered.
2. It preserves the published **96/96**. `any` breaks a deposited agreement count by exactly one
   row, and would need its own correction of record.
3. **The `:1858` wording is not in conflict.** It words the *negative control* as "0 of the 11 has
   ANY adsorbate atom …", which is a **measured fact about the control population** (0 of 11), not
   a definition of the verdict. It is the *stricter* statement for a control — not one atom is
   locked anywhere — and it stays true whichever quantifier the verdict uses. The two clauses are
   conservative in their own directions, which is belt-and-braces, not a contradiction.

**Carry this into the reader regardless of the ruling:** the deciding token is `-0.00000000`. A
string comparison against `"0.00000000"` misses it, and **266 of the 1,044 `.out` files under
`runs/` carry the negative-zero token.** Compare parsed floats, or match both spellings.

> `[ADSORBATE QUANTIFIER 2026-__-__: ALL | ANY]` — the run-level LOCKED verdict requires the
> exactly-zero lateral axis on every printed step for ____ adsorbate atom(s), consistent with
> :1830's run-level rule; :1858's "any" wording continues to describe the negative-control
> population and is unaffected.

---

## 2. `truncated_force_block` — scorable or not? → **recommend `scorable-if-all-adsorbate-atoms-present`**

**Registered at** `docs/43:1864`. **Decides** whether three rows archived LOCKED in
`symops_audit.csv` stay in the census. Eighteen tracked outputs have MPI abort text spliced in
mid-file leaving a NUL byte; in nine the `Forces acting on atoms` header is destroyed and the
block begins partway through the atom list (`runs/probe/Cr/s0_OOH__base.out` runs atoms 12–21 of
21).

**Recommendation: `scorable-if-all-adsorbate-atoms-present`.** The other two options each fail in
one direction:

- **`unscorable`** drops three defensible LOCKED rows — the adsorbate atoms *are* present and
  exactly zero on y in all three — and shrinks the census for a reason that is bookkeeping, not
  physics.
- **`scorable`** unconditionally would score a block in which an adsorbate atom is missing, and a
  verdict computed over an unknown subset of the atoms it is defined on is not a verdict.

The conditional is the only option that is both non-destructive and sound, and — the real point —
it is an **explicit, checkable predicate** rather than "whatever the parser happens to do", which
is the status quo the register objects to. It also forces the reader to *know* which atoms are
adsorbates before it scores, which is the A9.1 identification rule doing its job.

**Carry into the reader:** never shell out to `grep` for content here. On the NUL-bearing file
`grep -c` and `-l` are reliable, but `-n`, `-o` and anything piped downstream silently lose the
lines — which is how this family stayed invisible.

> `[TRUNCATED BLOCK 2026-__-__: SCORABLE-IF-ALL-ADSORBATE-ATOMS-PRESENT | SCORABLE | UNSCORABLE]`
> — a force block missing leading atoms is scored if and only if every identified adsorbate atom
> is present in it; otherwise the run is reported **unscorable**, a distinct outcome, never
> counted as not-LOCKED.

---

## 3. `oc20_ci_mechanism` — release asset or self-hosted runner? → **recommend `release-asset`**

**Registered at** `docs/43:1868`, explicitly left open. **Blocks CI today:** both mechanisms are
implemented in `.github/ci/run_oc20.py`, neither is defaulted, and until `$S1_OC20_MECHANISM` is
set the job reports NOT MEASURED and the face is not green. A commit on which the OC20 job did
not execute **is not green**.

**Recommendation: `release-asset`.**

- A **self-hosted runner makes CI depend on your machine being powered on.** Under the registered
  rule that a non-executing job is not green, every hour that box is off is a red commit — and
  that red is indistinguishable from a real regression.
- A sha256-pinned release asset is **reproducible by a third party**, which is the entire purpose
  of the control. A judge or reviewer can re-run it; nobody can re-run your living room.
- The manifest already exists and is staged: `docs/research/oc20-val_id/first500.SHA256SUMS`
  (44,993 bytes), with the sample on Anvil at `$PROJECT/corpora/oc20/`.
- **Licence is clear:** OC20 is CC-BY-4.0, stated twice in the source documentation, so
  redistribution with attribution is permitted.
- **Size is not a blocker:** the full `val_id` tar is 6.3 GB for ~24,945 trajectories, so 500
  members is of order **~126 MB** — well inside GitHub's 2 GB per-asset limit.

> `[OC20 CI MECHANISM 2026-__-__: RELEASE-ASSET | SELF-HOSTED]` — the 500-file sample is published
> as a sha256-pinned release asset of the public repo and the workflow downloads and hash-checks
> it against `docs/research/oc20-val_id/first500.SHA256SUMS`; a commit on which the OC20 job did
> not execute is not green.

---

## 4. `ai_use_log_path` — where does the provenance record live? → **recommend an explicit path, set in CI**

**Registered at** `docs/43:1322, :1443, :1445, :1828, :1840` — named five times, never given a
path. **Blocks CI today:** `.github/ci/check_disjoint.py` fails closed on a missing log, because
an absent log leaves the file list **UNDEFINED, not empty**.

**Recommendation: `docs/provenance-record.md`, with `$S1_AI_USE_LOG` set explicitly in the
workflow.**

**The trap worth knowing before you pick a name:** the auto-discovery regex is
`/ai[-_]?use|ai[-_]?log|use[-_]?log/`. **`provenance-record.md` does not match it.** So if you
want the A7.7 terminology — and A7.7 did rename this object from "AI-use log" to "provenance
record" in prose while deliberately leaving the two *identifiers* alone — you must set
`$S1_AI_USE_LOG` rather than rely on discovery. That is the better engineering anyway: explicit
beats implicit for a path a registered assertion depends on.

If you would rather not touch CI env at all, name the file `docs/ai-use-log.md` and it is found
automatically — at the cost of the prose/identifier mismatch A7.7 already flagged as a separate
dated act.

**One file, not many.** The extractor is format-agnostic and no schema needs registering; a single
file makes the disjointness assertion's input unambiguous, which is the whole reason the path
matters.

> `[PROVENANCE RECORD PATH 2026-__-__: docs/provenance-record.md, single file, located by
> $S1_AI_USE_LOG in the CI workflow]` — the A9.1 disjointness assertion reads this file and no
> other.

---

## 5. `if_pos_parenthetical` — file the correction? → **recommend `file-the-correction`**

**Registered at** `docs/43:1834`, which states as its rationale: *"pw.x prints the if_pos-masked
force, so a fixed coordinate reads exactly zero for a reason that is not symmetry."*

**That sentence is false, and I re-measured it independently today** rather than trusting the
register:

| deck | frozen atoms | force blocks | frozen-atom observations | all three components zero | max \|F\| on a frozen atom |
|---|---|---|---|---|---|
| `runs/s3/Mn/ref__2x1v` | 14 | 1 | 14 | **0** | 0.04355221 |
| `runs/Cr_slab/s0_O` | 7 | 12 | 84 | **0** | **0.08723744** |
| `runs/Co_slab/s0_O` | 10 | 15 | 150 | **0** | 0.05916676 |

**248 observations, not one all-zero.** QE 7.5 prints the **raw, unmasked** force. If the mask
were applied, a `0 0 0` atom would read `0.00000000` on all three axes, and none does.

**Recommendation: `file-the-correction`.** It is free and it is asymmetric:

- **Nothing about the action changes.** Excluding `if_pos = 0` atoms stays correct and
  conservative, adsorbate atoms are always `1 1 1`, and **no production verdict moves.**
- What changes is a **risk assessment**. Frozen atoms were registered as a source of false LOCKED.
  In QE 7.5 they cannot be one. Building the reader on the false premise would make it defend
  against a thing that does not happen while the real mechanism — the symmetry witness genuinely
  zeroing one axis, e.g. `runs/Cr_slab/s0_O.out` atom 1 reading
  `0.00000000 0.00000000 0.08723744` — goes unnamed.
- `leave-as-registered` means the report repeats a mechanism you have measured to be untrue. In a
  project about undisclosed methodological error, that is the one option with a downside.

> `[IF_POS RATIONALE 2026-__-__: CORRECTION FILED]` — the parenthetical at :1834 is withdrawn as
> to its **stated mechanism**; QE 7.5 prints the raw force and a frozen atom does not read zero
> for that reason. The **exclusion of `if_pos = 0` atoms stands unchanged** as a conservative
> rule. No verdict moves.

---

## 6. `pyproject_build_system` — two stanzas beyond the literal permission → **recommend `keep-as-ai-authored`**

**Registered at** `docs/43:1840`'s adoption note: packaging means "pyproject metadata, the version
string and the entry-point declaration, nothing wider." `pyproject.toml` also carries a
`[build-system]` table and a package-discovery entry, flagged inline, because without them the
package does not install and CI cannot invoke the CLI at all.

**Recommendation: `keep-as-ai-authored`, with the widening disclosed in the dated line.** The
permission's purpose is that **AI does not author the detector**; a build backend declaration is
not the detector, has no bearing on any census number, and cannot influence a verdict. The honest
move is to say plainly that the reading is one word wider than the adoption note and why, rather
than to have you retype two stanzas so that a provenance line reads differently for no epistemic
gain.

`entrant-rewrites` is also perfectly defensible and costs about five minutes — if you would rather
have zero AI-authored lines in the packaging path, take it. This is the one row where I think both
answers are genuinely fine and the only real error is leaving it unexamined.

> `[PACKAGING SCOPE 2026-__-__: KEEP-AS-AI-AUTHORED | ENTRANT-REWRITES]` — "packaging" is read to
> include the `[build-system]` table and package discovery, one word wider than the 2026-08-23
> adoption note, on the ground that a build backend is not the detector and touches no scored
> quantity. Disclosed, not absorbed.

---

## 7. `ai_x_census_disclosure` — how is the pre-existing x census disposed of? → **recommend `dated-line-and-proceed`**

**Registered at** `docs/43:1858` ("unmeasured on x until v0.1 reports it") and `:1864` ("x
INFERRED … reported by v0.1"). An AI sweep on 2026-08-27 measured the x half before v0.1 exists:
over the 20 registered P-CTRL runs, **3 of the 9 nosym-absent lock x** — the three `n_symops = 4`
1×1 \*O runs — and **0 of the 11 nosym-present**. The y figures (9/9, 0/11) are *not* new; they
are already the published record.

**Recommendation: `dated-line-and-proceed`, worded so the disclosure buys you something.**

The tension is real: F4 at `:1848` makes P-CTRL a gate **because** "every number flows through
code written by the person who believes the trap is real," and a control whose expected answer is
already published before the detector exists is weaker than one whose answer is not.

But notice what the sweep actually found: the three runs that lock x are **exactly the class
`:1864` predicted**. That is evidence *for* the registered reasoning, not against it. So the
strongest disposition is not to bury it and not to demote it — it is to **name it as a prior
prediction and let v0.1 re-derive it independently**, with the disagreement, if any, being the
finding. That converts a weakened control into a second witness.

Nothing in CI is scored against these numbers and no test asserts them, so this row costs nothing
operationally. The survey is preserved at `docs/research/ai-survey-2026-08-27/`.

> `[X CENSUS DISPOSITION 2026-__-__: DATED LINE AND PROCEED]` — the x-axis lock figures were
> measured by a disclosed AI sweep on 2026-08-27, before `silentgate` v0.1 existed, and are
> recorded here **as a prior prediction, not as v0.1's measurement**: 3 of 9 nosym-absent and 0 of
> 11 nosym-present. v0.1 re-derives them independently; **if v0.1 disagrees, the disagreement is
> reported as the finding** and v0.1's number is the one of record.

---

## What is ready behind these

Not a blocker, recorded so the sequencing is visible: **both corpora are staged on Anvil.** The Xu
deposit is at `$PROJECT/corpora/xu/rutile-OER-v1.0.zip` and the OC20 sample plus its manifest at
`$PROJECT/corpora/oc20/`. Nothing downstream of the core is waiting on data.

The remaining chain to a scored P-XU-SPAN is: **these seven rulings → the five core files
(`docs/71` is the spec) → P-CTRL passes as a gate → the census runs → span_U is scored against the
registered "> 0.20 eV on ≥5 of 10 rutiles, FALSIFIED below 3 of 10."**

Rows 1 and 2 are the ones with a deadline. The rest can be signed in any order.
