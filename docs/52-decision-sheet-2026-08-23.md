# 52 — Decision sheet for the entrant, 2026-08-23

This sheet is an AI-drafted INDEX of open decisions, not a source: the cited drafts govern, and where this sheet and a draft disagree, the draft wins. Nothing here adds an option, removes an option, or recommends among options on any verdict-bearing row — where a draft itself proposes a value, that proposal is quoted as drafted and remains a proposal until re-authored. Each row points at the exact text that must be re-authored, confirmed, or rejected in the entrant's own words. Decisions already made and banked (e.g. the migration certification — `PARITY_PASS` created on the entrant's instruction 2026-08-22, docs/46:223 — and the applied RuO2 benchmark FAIL consequence, lit2 readout :235-238) are excluded.

Hard boundary: nothing under `docs/research/2026-08-15-sampling/` was read in compiling this sheet.

Revised 2026-08-23 (same day) after an adversarial verification pass: tasks/todo.md citations refreshed (the file gained a line at :11 after this sheet was compiled); rows 41 (C6), 56 (S2 entrant-only execution) and 59 (SnO₂ nspin) added; the former S3-launch row folded into row 22; the SnO₂ admission row (58) reframed after docs/53; the closing tally made checkable.

---

## Deposit A9 — overdue since Aug 22

**1. Re-author every A9 THRESHOLD and deposit (the overdue act itself, including A8/A9 ordering)**
Where: docs/50-amendment-9-DRAFT.md:5, 7, 156, 172-178; docs/45-error-ledger.md:52, 58; tasks/todo.md:14
Decides: Whether/when A9 is appended to docs/43 and re-deposited to Zenodo — every proposed number becomes a registration only when Frank writes it — and whether A9 goes alone or as one version with A8.
Options as drafted: "Every threshold below is marked THRESHOLD and must be re-authored by Frank in his own words before this text is appended to docs/43 and re-deposited." / "re-deposited to Zenodo as a new version of record 10.5281/zenodo.21963144 — restricted access, DOI and timestamp public, files closed until report submission — before `silentgate` is pointed at any external corpus and before the first S2 table is computed" / "Ordering relative to A8, proposed: A9 is deposited first and alone if A8 is not ready on the same day, because A9's governed act (the parse) precedes A8's (the first S3 deck, Aug 26) and is already overdue; if both are ready together they go as one version with A8 and A9 in numerical order."
Blocks: docs/45 §E rows S1 and S2 are both "blocked on A9" (docs/45:75-76); every post-DOI act — zip fetch/listing comparison, header-format validation, OC20 download, the census (A9.7).
Deadline: overdue since Aug 22.

**2. Noise-floor divisor: /20 as proposed or /10**
Where: docs/50-amendment-9-DRAFT.md:40, 156
Decides: The per-corpus ON_PLANE/EXPLORED boundary rule, registered as a RULE "so that nothing need be read before deposit".
Options as drafted: "floor = `forc_conv_thr` / 20 in that corpus's force units, read per deck at parse time; where a deck sets none, the pw.x default 1e-3 Ry/bohr applies" OR "If the entrant prefers the round-number rule floor = `forc_conv_thr`/10, the in-house floor becomes 2e-4 Ry/au; no production row lies in (1e-4, 2e-4] … so no class changes; that is his call, written once."
Blocks: A9 deposit text; classes every corpus's ON_PLANE/EXPLORED rows.
Deadline: overdue since Aug 22 (pre-deposit).

**3. Whether "packaging" is inside AI's permitted list**
Where: docs/50-amendment-9-DRAFT.md:48, 156
Decides: The AI-authorship boundary for silentgate — whether AI may write pyproject metadata, the version string and the entry-point declaration.
Options as drafted: "'packaging' means `pyproject` metadata, the version string and the console-script entry-point declaration only — flagged: this is one word wider than round-2 :218's 'test scaffolding, CI and review,' and the entrant decides whether even that is allowed."
Blocks: The who-writes-it registration in the deposit text; the CI disjointness assertion between the AI-use log file list and the core path list.
Deadline: overdue since Aug 22 (pre-deposit).

**4. Confirm the "five existing detectors" list and any legacy/ lift** *(operational, non-verdict-bearing — drafted default stands unless changed)*
Where: docs/50-amendment-9-DRAFT.md:36, 156
Decides: Which legacy modules count as the five detectors and whether any is lifted into silentgate/legacy/.
Options as drafted: "the candidates in `src/dft/` are `symops_audit.py`, `orient_starts.py`, `qe_qc.py`, `adsorbate_qc.py`, and `hessian_mirror_noise.py` / `hessian_analyze.py` — the entrant confirms the list"; "any legacy detector he wants in the package goes into a clearly separated `silentgate/legacy/` sub-module, lifted as-is with its existing authorship recorded in the AI-use log, and is not exercised by the controls"
Blocks: v0.1 package composition in S1 (the scope-narrowing paragraph is deposit text).
Deadline: overdue since Aug 22 (pre-deposit).

**5. OC20 split name and artefact line**
Where: docs/50-amendment-9-DRAFT.md:60, 156
Decides: The negative-control corpus artefact (name, URL, md5, licence), fixed from documentation before deposit.
Options as drafted: "the negative corpus is whole-relaxation, per-system trajectories from OC20's relaxation-trajectory release …; S2EF frame subsets are ineligible … The proposed draw is the smallest in-domain validation split that release offers (`val_id`, if the documentation confirms that name); the artefact name, URL, md5 and licence line (CC-BY-4.0 is the expected licence — confirmed from the documentation, not assumed) are copied from `DATASET.md` into this section before deposit"
Blocks: The deposit text; post-DOI act (3): OC20 download, precision recording, the 500-draw and manifest (A9.7).
Deadline: overdue since Aug 22 (pre-deposit).

**6. OC20 sample size and selection rule (N = 500, first-500 lexical)**
Where: docs/50-amendment-9-DRAFT.md:62
Decides: The negative-control draw rule, fixed before download so the control cannot be re-drawn until it passes.
Options as drafted: "N = 500 relaxations, taken as the first 500 trajectory filenames in ascending lexical order inside the named artefact, fixed in this text before download; no re-draw, no substitution, no second sample. Any enlargement is additive and disclosed."
Blocks: OC20 negative control execution; the deposit (THRESHOLD re-author rule, :5).
Deadline: overdue since Aug 22 (pre-deposit).

**7. OC20 negative-control pass condition (exactly 0.00 %)**
Where: docs/50-amendment-9-DRAFT.md:64
Decides: The false-positive gate whose failure voids downstream symmetry numbers.
Options as drafted: "exactly 0.00 % of the 500 relaxations contain any adsorbate atom (`tags == 2`) with a lateral force component that is exactly zero in every ionic step (the LOCKED criterion), with constrained atoms excluded per A9.1 … Any nonzero rate voids every downstream symmetry number until the detector is repaired"
Blocks: The P-CTRL gate; every downstream symmetry number's validity; the deposit.
Deadline: overdue since Aug 22 (pre-deposit).

**8. QE-reader negative control, force-only 0-of-11**
Where: docs/50-amendment-9-DRAFT.md:66
Decides: The in-house QE-reader false-positive gate on the 11 nosym-present production runs.
Options as drafted: "THRESHOLD (proposed), scored in FORCE-ONLY mode with the header witness ignored: 0 of the 11 has any adsorbate atom with a lateral force component exactly 0.0 in every printed step; the two-witness class is reported alongside." ("unmeasured on x until v0.1 reports it. Re-run on every commit.")
Blocks: QE-reader certification for the Xu census; the deposit.
Deadline: overdue since Aug 22 (pre-deposit).

**9. Positive control re-stated against the record (9/9, 0/11, 20-for-20, n/n)**
Where: docs/50-amendment-9-DRAFT.md:70, 72
Decides: The corrected positive-control gate (round-2's "≥95 % of 20 nosym-absent" population does not exist).
Options as drafted: "silentgate returns 9/9 LOCKED on the `nosym`-absent set (scored two-witness AND force-only with the header ignored), 0/11 LOCKED on the `nosym`-present set (A9.2.1), and the 20-for-20 partition by the deck's `nosym` line, with header-vs-force two-witness agreement on every classifiable adsorbate row … n/n printed (96 of 98 rows at 137010b …). Any miss voids the 20-for-20 partition claim (round-2 :481) and halts the census until repaired"
Blocks: The census (halts until repaired on any miss); the 20-for-20 partition claim; the deposit.
Deadline: overdue since Aug 22 (pre-deposit).

**10. Whether the post-Aug-9 probe runs are added to the gating set**
Where: docs/50-amendment-9-DRAFT.md:72
Decides: Whether the ~22 relaxations + 48 SCFs in runs/probe/ gate, or stay supplementary.
Options as drafted: "Supplementary, MEASURED but not gating unless the entrant adds them: the symmetry-ON adsorbate relaxations and fixed-geometry SCFs added to `runs/probe/` after Aug 9 … their count was tallied off-repo as 22 relaxations + 48 SCFs and is UNKNOWN in the repo until `symops_audit.csv` is regenerated at HEAD, which fixes the number"
Blocks: Scope of the positive-control gate (they are reported per axis by v0.1 either way).

**11. OC20 CI mechanism: release asset or self-hosted runner**
Where: docs/50-amendment-9-DRAFT.md:76, 156
Decides: How the OC20 control runs on every commit, given the sample lives off-repo ("THRESHOLD (proposed), entrant's call between two mechanisms, written once").
Options as drafted: "(a) the 500-file sample is published as a sha256-pinned release asset of the public repo (CC-BY-4.0 permits redistribution with attribution; ~0.5–2 GB, UNKNOWN until drawn) and the workflow downloads and hash-checks it; or (b) a self-hosted runner on the STS machine holds the sample." Under either, "a commit on which the OC20 job did not execute is not green."
Blocks: CI green/VOID semantics for every census table, figure and CSV; the deposit.
Deadline: overdue since Aug 22 (pre-deposit).

**12. P-XU clause (iii) per-metal rule: named-pair or all-outputs-agree**
Where: docs/50-amendment-9-DRAFT.md:96, 156
Decides: How *OH/*OOH orthogonality is scored per metal ("one rule is fixed in the text either way").
Options as drafted: "clause (iii) is scored on the named pair `Eads-4-layers/OH-relax` vs `Eads-4-layers/OOH-relax` per metal … each has a single-axis locked set and the two axes differ" OR "(If the entrant prefers the stricter rule — a metal is orthogonal only if every one of its *OH outputs has the same single-axis locked set {a} and every *OOH output {b} ≠ {a}, otherwise MIXED and not orthogonal — he writes it; one rule is fixed in the text either way.)"
Blocks: P-XU clause (iii) scoring ("≥8 of the 10 metals" / "≥4 of the 6 blind metals"); the deposit.
Deadline: overdue since Aug 22 (pre-deposit).

**13. P-XU rates and FALSIFIED lines**
Where: docs/50-amendment-9-DRAFT.md:98
Decides: The headline external-census prediction over the 810/630 denominators.
Options as drafted: "(i) ≥90 % of the 810 report more than one symmetry operation; (ii) ≥90 % of the 630 carry at least one exactly-zero lateral adsorbate force component in the final ionic step; (iii) *OH and *OOH are orthogonal on ≥8 of the 10 metals under the per-metal rule above. FALSIFIED if (i) or (ii) is below 75 %, or if (iii) holds on ≤4 of 10"
Blocks: The S2 lock census (P-XU is proposed to lead the abstract per round-2 Q6); the deposit.
Deadline: overdue since Aug 22 (pre-deposit).

**14. P-XU-SPAN threshold (supersedes round-1's P-XU-U)**
Where: docs/50-amendment-9-DRAFT.md:102
Decides: The gas-reference-free U-span prediction on the 680-file ladder.
Options as drafted: "span_U(c_M) > 0.20 eV on ≥5 of the 10 rutiles; FALSIFIED below 3 of 10; span_U(ΔG₂) reported alongside without a threshold." — "This supersedes round-1's P-XU-U ('η span > 0.15 V on ≥5 of 10; ≥1 metal changes volcano rank by ≥3' — round-1 :185) because η needs the gas references the deposit lacks."
Blocks: Census product 2 scoring; the deposit.
Deadline: overdue since Aug 22 (pre-deposit).

**15. Whether the two gas-reference molecule jobs (H₂, H₂O) run**
Where: docs/50-amendment-9-DRAFT.md:102, 156
Decides: Whether the absolute floor-margin half of census product 2 is measured or DEFERRED (in the "Open decisions this draft leaves to the entrant" list: "whether the two molecule jobs run (A9.3.3)").
Options as drafted: "proposed protocol 12 Å Martyna–Tuckerman box, ecutwfc 40 / ecutrho 500 Ry to match Xu's decks; ~0.2 box-h … GBRV pseudopotentials … must be staged and md5-logged as a precondition under A8.5's machine rules); whether they run is the entrant's call — if not, that half is reported DEFERRED, not fudged; if they do run, only the floor-margin column (η − floor, a difference) is reported, and no η for any Xu metal appears anywhere"
Blocks: The absolute floor-margin half of census product 2 (the only DFT jobs A9 can license).
Deadline: overdue since Aug 22 (pre-deposit list).

**16. P-DIVANIS δ-curve prediction and rates**
Where: docs/50-amendment-9-DRAFT.md:106
Decides: The floor-population prediction and its registered δ-shift.
Options as drafted: "the floor margin is reported as an explicit curve over δ = corr_OOH − 0.35 eV, δ ∈ [0.00, 0.10] eV, with the shift registered now as Δ(floor margin) = +δ/2 (pls = 3), −3δ/2 (pls = 4), −δ/2 (pls ∈ {1, 2}) … prediction: ≥25 % of the rutile-only entries with η < 0.60 V sit within 50 meV of their own exact scaling floor, per-paper rate (n = 24) alongside; FALSIFIED below 10 %; no exact binomial CI at n = 515"
Blocks: Census product 3 scoring; the deposit.
Deadline: overdue since Aug 22 (pre-deposit).

**17. P-DIVANIS denominator count (or accept the 38-row default)**
Where: docs/50-amendment-9-DRAFT.md:106, 156
Decides: The number of rutile-only rows with η < 0.60 V, counted by the entrant from divanis_esi.txt (filed under the sealed sampling directory — entrant-only under the guard), fixed before the parse.
Options as drafted: "the entrant counts it from `divanis_esi.txt` (a count of a published table already read on 2026-08-15 — not a raw-output corpus under A9.6's no-parse rule; no floor is computed) and writes it into this clause before deposit; if it is not counted before deposit, the denominator defaults to all 38 rutile-only rows and the prediction is read as '≥25 % of the 38 have η < 0.60 V and sit within 50 meV.'"
Blocks: P-DIVANIS's denominator; the deposit — with a stated default if missed.
Deadline: overdue since Aug 22 (pre-deposit).

**18. Whether the deposited Divanis |z| ≥ 3 gate is withdrawn as a correction of record (retain-as-reported and the n = 38 sub-fit replacement are the drafted alternatives)**
Where: docs/50-amendment-9-DRAFT.md:106, 156
Decides: An amendment to a DEPOSITED clause (docs/43 §6 :331-337, in the A1–A7 Zenodo record) — "flagged as a change to a deposited registration, not a clarification".
Options as drafted: "PROPOSED: the §6 |z| ≥ 3 gate is withdrawn as a correction of record, with that reason, in the entrant's words appended to docs/43 (no edit of the deposited text); the z column is retained as reported; if a gate is wanted, the Divanis rutile-only n = 38 sub-fit replaces the pooled intercept." (The deposited clause: z = (c_M − 3.18)/0.12 and "a correction that moves η by ≥ 0.10 V while leaving |z| ≥ 3 has not fixed the scaling anomaly")
Blocks: The docs/43 correction rides the A9 re-deposit; the round-2 F8 demotion of ±0.12 eV to qualitative; whether a scaling-anomaly gate exists at all.
Deadline: overdue since Aug 22 (pre-deposit).

**19. P-BUILDER structure sources, parameters, denominators and rate X**
Where: docs/50-amendment-9-DRAFT.md:110, 156
Decides: Every registered value of the pymatgen census arms — "every value the entrant's call"; X is his number.
Options as drafted: "per family, the source structure (MP id or CIF, written here), termination, slab thickness, vacuum, a pure-metal fcc(111) element; … OOH bent with coordinates as in the retained `t2.py` (`[[0,0,0],[1.29,0,0.7],[1.29,0.9,1.0]]`) or the entrant's choice, written here; … Denominators: UNKNOWN today; the entrant runs the enumerator (no symmetry computed) on the four families under exactly these arguments and writes the four configuration counts into this section before deposit. THRESHOLD (proposed): rate X per family — X is UNKNOWN and is the entrant's number; this draft proposes none."
Blocks: The blind arms (perovskite(001), spinel(001), fcc(111)) may not run before registration; the deposit.
Deadline: overdue since Aug 22 (pre-deposit).

**20. P-LIT search string, databases, date, predicted proportion, fourth field**
Where: docs/50-amendment-9-DRAFT.md:114, 156
Decides: The literature-coding audit's inclusion rule, its predicted proportion, and whether the deposit-availability field is carried.
Options as drafted: "found by a search string, databases and date that are UNKNOWN today and the entrant's — written into this section before the first paper is coded"; "Predicted proportion: UNKNOWN — the entrant writes the number; round-1's example ('>80 % report none of the three') is an example, not a proposal"; "Deposit-availability count: proposed as a fourth coded field (raw outputs deposited? yes/no) at zero marginal cost, no threshold — entrant's call whether to carry it"
Blocks: The first paper coded in P-LIT (census product 5; S2); the deposit.
Deadline: overdue since Aug 22 (pre-deposit).

**21. Xu-repair disposition: (a) cut on evidence or (b) minimum-viable re-run**
Where: docs/50-amendment-9-DRAFT.md:146, 156, 162
Decides: Whether any Xu deck is ever re-run — "the entrant's call, both options on the table"; sources conflict (round-2 :570 cuts it, the addendum names it in neither list, round-1 :225's reasons are mixed).
Options as drafted: "(a) Cut on evidence: frozen moment on the only 3d metals in the set, plus the translation risk; then 'never re-run anyone's decks' stands and A9.6 keeps its first bullet." OR "(b) Round-1 :225's minimum-viable version: 3 metals, a gate on the three ΔG rungs (|ΔΔG_i| < 0.10 eV) rather than on η, a widened ±0.12 V η gate, 2–3 human-days budgeted for the deck translation, charged to S2 or S6, not S3. The entrant writes which"
Blocks: A9.6's first bullet ("standing only if the entrant chooses (a) in A9.5 item 1;" under (b) it "narrows to 'nothing beyond it'"); S2/S6 budget under (b); the deposit.
Deadline: overdue since Aug 22 (pre-deposit).

---

## Deposit A8 — due Aug 24

**22. Re-author every A8 THRESHOLD and deposit to Zenodo (umbrella)**
Where: docs/47-amendment-8-DRAFT.md:6-11, 294-299 (A8.9); docs/45-error-ledger.md:51; tasks/todo.md:13; docs/51-anvil-queue-triage-2026-08-23.md:31-33; docs/49-block-1C-cr-hessian-2026-08-23.md:169-172
Decides: Whether the AI-drafted amendment becomes a registration at all — "re-author or reject" each THRESHOLD-tagged proposal (docs/49:171), then deposit.
Options as drafted: "Every threshold below is marked THRESHOLD and must be re-authored by Frank in his own words before this text is appended to docs/43 and re-deposited. A number proposed here is a proposal. It becomes a registration only when he writes it." A8.9: "docs/43 complete (A1–A8) is re-deposited to Zenodo as a new version of record 10.5281/zenodo.21963144 — restricted access, DOI and timestamp public, files closed until report submission — before the first S3 deck launches. The new version DOI is recorded here in a dated line when it exists."
Blocks: "The next compute that can launch without a decision is none — S3, the gate-(h) relaxations and the Co *OOH re-attempt all wait on A8's re-authoring and re-deposit (due Aug 24)" (docs/51:31-33); A8.9 gates the first S3 deck launch on the deposit. S3 itself — tier_v3 (crossed coverage × symmetry × basin, 8 metals), the critical-path compute — is otherwise executable and dated: "decks buildable now, launch Aug 26" (docs/45 §E :77); "S3 decks: build after A8 deposit, launch Aug 26 (docs/45 §E)" (tasks/todo.md:18). This deposit is the only Frank-owned gate in front of the S3 launch.
Deadline: Aug 24, before the first S3 deck launches; S3 launch itself is dated Aug 26.

**23. A8.1 — NON-ADDITIVE interaction bin (0.10 eV)**
Where: docs/47-amendment-8-DRAFT.md:55-57
Decides: The bin at which S3 reports a cell × symmetry interaction as NON-ADDITIVE.
Options as drafted: "THRESHOLD (proposed): a cell × symmetry interaction term is reported NON-ADDITIVE where |E(both) − E(cell) − E(sym) + E(neither)| exceeds 0.10 eV — the same bin block 1A used, so the two are comparable without a conversion." No alternative value is drafted.
Blocks: First S3 deck launch (amendment deposit gate, A8.9).
Deadline: Aug 24.

**24. A8.2 — P-SYMCOV satisfaction threshold**
Where: docs/47-amendment-8-DRAFT.md:71-73 (both-outcomes text added 2026-08-23 at :75-90, answering the docs/50:124 flag that A8 lacked a P-SYMCOV falsification branch)
Decides: When the coverage-indexed symmetry-claim rule counts as satisfied, and what happens to single-coverage metals in symmetry statistics.
Options as drafted: "THRESHOLD (proposed): P-SYMCOV is satisfied when, for every metal in S3, the symmetry effect is reported at both coverages, or the missing cell is reported as a gap. A metal with only one coverage is not averaged into any symmetry statistic." No alternative is drafted.
Blocks: First S3 deck launch (amendment deposit gate, A8.9).
Deadline: Aug 24.

**25. A8.2 — "most" threshold (≥ 5 of 8) and the claim-scope sentence**
Where: docs/47-amendment-8-DRAFT.md:75-90
Decides: The pre-registered cut deciding which of two pre-written claim scopes fires, and authorship of the resulting sentence: "Neither outcome changes what S3 computes; they change one sentence, and the sentence is the entrant's."
Options as drafted: Outcome 1: "Claim scope if the effect is coverage-dependent on most metals (the Ir pattern, |ΔΔE(1×1) − ΔΔE(2×1v)| large): the symmetry trap is reported as a coverage-conditional effect, the range stated per metal, and the 1×1 numbers of the literature census (A9) are read as the high-coverage end of that range." Outcome 2: "Claim scope if the effect is coverage-independent (the two cells agree within the basin CONFOUND tolerance on most metals): the trap is reported as a property of the placement, not the cell; the 1×1 legacy numbers stand as-is; and P-SYMCOV reduces to the reporting rule with no 'range' to state." THRESHOLD (proposed) for "most": "≥ 5 of the 8 metals with both cells measured; a metal with one cell is a gap, as above."
Blocks: First S3 deck launch (amendment deposit gate, A8.9); also fixes how A9 census 1×1 numbers are read.
Deadline: Aug 24.

**26. A8.1-vs-A8.5 AFM scope collision — second seed vs standalone four (gate-(h) RuO₂ AFM family)**
Where: docs/47-amendment-8-DRAFT.md:48, 170-176, 207-209; docs/51-anvil-queue-triage-2026-08-23.md:25 (skeptic addition iii), hold restated at :32-33
Decides: Whether the four RuO₂-anchor AFM relaxations owed by gate (h) live inside A8.1's crossed magnetic-basin factor or stand as four standalone S3-class jobs — the draft assigns AFM work in two places without reconciling them, and "the deck count this amendment fixes" is what the amendment exists to pin.
Options as drafted: "whether the AFM Ru row is the Ru second seed inside tier_v3 (then crossed with 1×1/2×1v and off/mirror, up to 16 relaxations) or the standalone four must be settled in the A8 re-authoring." (docs/51:25) The colliding clauses: A8.1 table row: "magnetic basin | production seed + second seed | error class 2. Restored beyond *OOH-only wherever triage allows." vs A8.5: "Adopting AFM as the anchor's magnetic row therefore owes four 2×1v AFM relaxations, which are S3-class jobs and are priced in A8.6, not in S0's closed budget." (Also open inside the A8.1 row: "wherever triage allows" is an unspecified triage call.) Family size per the deposited GATE-1 rule: "≥ 8 decks (4 relax + 4 `__g1` children, with the ≥ 5 meV re-relax loop and A8.3's draft 1 meV above-parent refusal)"; docs/48's ~237 SU/relax "understates them, likely 2–4×".
Blocks: The gate-(h) AFM relaxations themselves — verdict "HOLD on A8", "0 built", "Nothing to launch: no decks, manifest or committed builder exist"; the S3 deck count the amendment fixes; the RuO₂ AFM re-anchor re-run owed since S0 gate (h).
Deadline: Aug 24.

**27. A8.3 — magnetic CONFOUND threshold (0.05 µB)**
Where: docs/47-amendment-8-DRAFT.md:98-104
Decides: When a contrast pair is excluded from contrast statistics as magnetically CONFOUNDED.
Options as drafted: "THRESHOLD (proposed): a pair whose members differ in converged total magnetisation by more than 0.05 µB is CONFOUNDED — its energy difference mixes the intended contrast with a basin change — and is excluded from the contrast statistics and reported separately, exactly as a geometry confound is." Drafted rationale: 0.05 µB "sits far below the drifts actually observed (11.00 → 14.90 and 11.00 → 14.71 µB) and far above SCF noise in a converged moment." No alternative value is drafted.
Blocks: First S3 deck launch (amendment deposit gate, A8.9).
Deadline: Aug 24.

**28. A8.3 — __g1 child refusal rule (1 meV above parent)**
Where: docs/47-amendment-8-DRAFT.md:121-124; docs/46-anvil-parity-2026-08-22.md:213-219 ("Proposed rule drafted in docs/47 §A8.3 for the entrant to re-author")
Decides: When a GATE-1 child is refused, re-run, or recorded MULTISTABLE — the rule that resolves the LIT-3 children-above-parents pattern (the interpretive call already routed to the entrant).
Options as drafted: "THRESHOLD (proposed): a __g1 child that lands above its parent by more than 1 meV is refused and re-run from the parent's converged density. If the second attempt also lands above, the pair is recorded MULTISTABLE with both numbers, and neither is banked as the state's energy." No alternative is drafted.
Blocks: First S3 deck launch (amendment deposit gate, A8.9); banking of the two LIT-3 BASIN_DRIFT rows.
Deadline: Aug 24.

**29. A8.4 — convergence-failure budget (20 % low-confidence rule)**
Where: docs/47-amendment-8-DRAFT.md:132-137
Decides: How error class 5 (silently dropped non-convergences) is reported and when a metal's state is marked low-confidence in the ranking.
Options as drafted: "THRESHOLD (proposed): S3 records a per-metal, per-state convergence-failure rate as a reported quantity, not a log artifact. The escalation ladder is A6.5's, unchanged: restart from a converged neighbour's density → halve mixing β → record NOT_CONVERGED and plot as a gap. A metal whose failure rate exceeds 20% on any state has that state's contribution to the ranking marked low-confidence in the report rather than dropped." No alternative is drafted.
Blocks: First S3 deck launch (amendment deposit gate, A8.9).
Deadline: Aug 24.

**30. A8.5 — Anvil parity agreement threshold (1e-5 Ry)**
Where: docs/47-amendment-8-DRAFT.md:145-149; docs/46-anvil-parity-2026-08-22.md:120 ("The tolerance for platform parity (1e-5 Ry is a proposal only)")
Decides: The agreement bound under which an Anvil re-run of a banked Vast deck counts as reproducing it. Marked "(proposed, and already applied)" — the entrant is ratifying a threshold the panel was already scored against, which makes the re-authoring reason sensitive. Status note: the certification act itself is banked — `$PROJECT/parity/PARITY_PASS` "was created on the entrant's instruction after reviewing the panel" (docs/46:222-226) — so only the tolerance's ratification in his words remains open here.
Options as drafted: "THRESHOLD (proposed, and already applied): an Anvil re-run of a banked deck agrees when |ΔE| ≤ 1e-5 Ry." Drafted context: "The first attempt failed at −8.28 meV; the diagnosis is A8.3's — the reference chosen was one of the two BASIN_DRIFT rows. Against its own parent, the same Anvil number agrees to 6.7e-7 Ry (0.009 meV)." No alternative value is drafted; A8.8 forbids "loosening the parity threshold to accommodate a measurement" (docs/47:291).
Blocks: The registered parity record every Anvil wave is judged against; part of the A8 deposit.
Deadline: Aug 24.

**31. A8.6 — S3 production run shape and the walltime cap value**
Where: docs/47-amendment-8-DRAFT.md:198-201; docs/48-anvil-sizing-2026-08-22.md:7-9, 74-81, 95-103, 112-115
Decides: The registered S3 relaxation shape plus a literal blank only the entrant can fill (the walltime cap number); docs/48: "No threshold is set here — the schedule consequences are the entrant's to accept or reject."
Options as drafted: "THRESHOLD (proposed): S3 relaxations run at 128 ranks, −nk 16, -N 1, with the walltime cap raised from 48 h to a value the entrant sets — shared reports MaxTime=UNLIMITED, so 48 h was never a limit, and at the measured rate a 60-step relax lands inside 4 h anyway." The two measured shapes (docs/48:80-81): "20 ranks, −nk 4, unbound (today's production shape)" — ~12 h wall, ~237 SU per relax; vs "128 ranks, −nk 16, bound" — ~1.5–2.1 h wall, ~194–269 SU per relax. (docs/48:95-97: "`shared` reports `MaxTime=UNLIMITED`, so the 48 h cap in `40_wave.slurm` is a choice and not a limit."; Cr Hessian decks excluded — "there is no case for widening them", docs/48:112-115.)
Blocks: First S3 relaxation launch at the registered shape; every S3 schedule and SU figure descends from the per-relax estimate; a widened wave requires editing the manifest `# NP=<n> NCONC=<n>` directive (docs/48:98-103).
Deadline: Aug 24.

**32. A8.7 Question 1 — the σ_F instrument: readings (a)/(b)/(c)**
Where: docs/47-amendment-8-DRAFT.md:211-253 (table :238-242, threshold :244-253), consequence :275-279; docs/49-block-1C-cr-hessian-2026-08-23.md:160-175 (§5); docs/45-error-ledger.md:20; tasks/todo.md:7
Decides: What "measured force noise" means in docs/43 §3-A.3's max(50 cm⁻¹, 3σ) floor — and with it the verdict label of block 1C (the Cr 2×1v Hessian). Section preamble: "This section decides nothing… a verdict-bearing instrument choice is his under P-AUTHORSHIP and A7.7… written with the outcome known… whatever is chosen here must be chosen for a stated reason that does not reference which verdict it yields, and the report must carry both labels if the reason is contestable."
Options as drafted: (a) "asymmetry-based, as coded" — σ_F 2.99e-5 / 1.20e-4, floor i265 / i374, label "UNDERPOWERED / VOID; REFUTED and CONFIRMED unreachable at any δ". (b) "force noise from identities the SCF does not enforce (the Q6 mirror identities; `hessian_mirror_noise.py`)" — σ_F 1.75e-7 / 2.08e-7, effective floor "i50 (the declared minimum)", label "scored against i50, with the mode at i243–i245 and f_y = 1.00". (c) "asymmetry-based on the non-cross pairs only" — σ_F 1.74e-6 / 1.37e-5, floor i64 / i126, label "passes at δ 0.01, UNDERPOWERED (> i80) at δ 0.02 — still an anharmonicity meter". THRESHOLD (proposed): reading (b), with drafted reason "a noise estimator must be δ-invariant when the noise is, and (b) is the only one of the three that is (×1.19 vs ×4 and ×7.85)". Escape hatch as drafted: "The entrant may instead keep (a) — in which case block 1C is recorded as UNDERPOWERED/VOID by instrument, not by physics, with the mode reported as a measurement without a verdict label — or choose (c), or something else. Whatever is chosen, the choice and its reason are written in his words."
Blocks: Block 1C's verdict label; every S3 re-Hessian ("an S3 protocol parameter, not a Cr footnote, and must be settled in this amendment before the first S3 Hessian is built"); "`hessian_analyze.py` is NOT changed until it is."
Deadline: Aug 24.

**33. A8.7 Question 2 — am.2 escalation vs Q4: resolution (i) or (ii)**
Where: docs/47-amendment-8-DRAFT.md:255-266; docs/49-block-1C-cr-hessian-2026-08-23.md:105-111, :169 ("needs resolving regardless")
Decides: How to resolve the registered escalation (UNDERPOWERED → rerun at δ = 0.02 Å) firing Q4a/Q4b by construction, since the Q4b floor falls as 1/δ while the asymmetries it is tested against grow as δ or δ². Drafted as "Two coherent resolutions, both proposed, neither chosen here".
Options as drafted: "(i) under reading (b) the floor is δ-independent and am.2's rerun keeps its registered meaning — a harmonic-regime test (passed: 0.8 %) that does not touch the noise floor; Q4 stays a gate on a noise measurement, not on anharmonicity; (ii) alternatively the y rows return to central differences (the ym decks enter H after Q6 passes), which zeroes the cross-block asymmetry by construction — at the cost of the ym decks' status as an independent control, which am.4 §7 fixed for a stated reason. (i) is the smaller change."
Blocks: Coherence of the registered escalation path for block 1C and every S3 re-Hessian; coupled to Question 1 (resolution (i) presumes reading (b)); part of the A8 deposit.
Deadline: Aug 24.

**34. A8.7 Question 3 — Q4b's standing: register or demote**
Where: docs/47-amendment-8-DRAFT.md:268-273; context docs/49-block-1C-cr-hessian-2026-08-23.md:37-39, 110-111
Decides: Whether an unregistered code-level gate may void a state — "The analyzer labels Q4b 'CODE-LEVEL, in no docs/43 clause (N32/N33) — reported, not registered' and nonetheless counts it toward VOID." Q4b is one of only two failures behind the δ = 0.02 VOID.
Options as drafted: "Either register it here (with its formula and the reading of σ_design it uses) or demote it to reported, as Q5 was. THRESHOLD (proposed): demote to reported; the gate it duplicates (Q4a) carries the registered meaning, and a gate that is not registered must not void a state."
Blocks: Block 1C's VOID accounting (δ = 0.02 rests on Q4a + Q4b, "nothing else"); the analyzer's gate set for all S3 Hessians; part of the A8 deposit.
Deadline: Aug 24.

**35. Solvation × coverage non-additivity — confirm A8.2 carries the docs/45 §B row 9 registration**
Where: docs/50-amendment-9-DRAFT.md:156 (A9.5 flag + fallback); docs/47-amendment-8-DRAFT.md:88-90; docs/45-error-ledger.md:33
Decides: Ownership of the row (|Δc_M(O cov) − Δc_M(OH cov)| > 0.10 eV, TRANSFERRED, ΔG_OOH swept [−0.4, +0.2] eV). docs/47 A8.2 now carries it (2026-08-23); the entrant confirms by depositing A8 with A8.2 as drafted, else the A9 fallback fires.
Options as drafted: A8.2: "The solvation × coverage non-additivity row (docs/45 §B row 9) is carried here as an appendix prediction with its TRANSFERRED status and the swept ΔG_OOH band (A9.5 flagged the ownership; A8 takes it — it is a coverage statement, not a census one)." A9.5 fallback: "if A8 does not carry the §B row 9 registration at its deposit, A9 carries it as an appendix prediction with the TRANSFERRED status and the swept ΔG_OOH band, so that the row is owned by someone."
Blocks: Zero-compute registration of error-class 9; the row being owned by someone at A8's deposit.
Deadline: Aug 24 (A8 deposit).

---

## LIT-2 sign-offs (no deadline, before A10)

Source file for all rows: runs/probe/lit2_readout_2026-08-23.txt ("ENTRANT DECISIONS FLAGGED (docs/43 A5.2 is silent or gives two readings; defaults applied and stated, alternatives printed)", :262). The applied RuO2 benchmark FAIL consequence (Cr = vacuum-CHE-only, :235-238) is already applied and is not a row here.

**36. C1 — Cr mixed_OH_O off-arm VOID: comparability confirmation**
Where: runs/probe/lit2_readout_2026-08-23.txt:189-194 (arm-choice block), :263; docs/45-error-ledger.md:83
Decides: Whether the Cr mixed_OH_O mirror/off pair is comparable after the off arm was voided under docs/43 §1 (dE_sym = E_off − E_mir = +68.6 meV > +20 meV). The readout prints the comparability data ("comparability: dM_tot=+0.00, dM_abs=+0.04 mu_B (within 0.1: True); final compositions both nominal: True") but reserves the call for the entrant.
Options as drafted: "ENTRANT TO CONFIRM the pair is comparable -- same spectator arrangement / final composition and magnetisation within 0.1 mu_B (printed in the arm-choice block): if NOT comparable the mirror arm simply stands alone as the rung; if comparable the off-plane search failed and a re-search of the off arm is owed. 'Higher local minimum' is NOT an admissible reading (§1: 'not a physical result')"
Blocks: Whether a re-search of the Cr mixed off arm is owed; final standing of that LIT-2 rung, which feeds the Cr CHE ladder and the Cr decision-rule comparator set.

**37. C1 — arm-of-record rule where A5.2 is silent (mir vs off within the §1 tolerance)**
Where: runs/probe/lit2_readout_2026-08-23.txt:263 (instances at :87-95 Ru, :182-188 Cr O_full)
Decides: Ratify (or replace) the applied default that the rung's energy of record is the lowest-energy scoreable arm when |dE_sym| ≤ 20 meV — A5.2 does not say which arm is the rung. Ru arm picks move the scored energy by 11.5–13.0 meV; the Cr O_full pick is flagged immaterial.
Options as drafted: "C1 arm choice: O_full/mixed rungs have _mir and _off arms; A5.2 silent on which is the rung, docs/43 §1 not silent on the comparison (dE_sym = E_off - E_mir > +20 meV voids the off arm). Applied on the energies of record when both arms score; lowest-energy scoreable arm within the §1 tolerance (default). Ru O_full: chosen=off [C1 default (within the §1 tolerance); dE_sym=-13.0 meV]; Ru mixed_OH_O: chosen=off [C1 default (within the §1 tolerance); dE_sym=-11.5 meV]; Cr O_full: chosen=mir [C1 default (within the §1 tolerance); dE_sym=0.7 meV] !! arms degenerate within 0.7 meV (below the relaxation's resolution); choice immaterial"
Blocks: The energies of record entering the Ru CHE ladder and RuO₂ benchmark transitions, and the Cr ladder.

**38. C2 — reading of "O-covered" in the Cr decision rule**
Where: runs/probe/lit2_readout_2026-08-23.txt:264 (rule at :29; applied at :251-254)
Decides: Which rungs count as "O-covered" comparators in A5.2's Cr rule. Both drafted readings give FLAG=OFF today, but the reading defines the registered comparator set.
Options as drafted: "C2 'O-covered': DEFAULT: the *O-bearing rungs (O_full, mixed) -> CONDITIONAL-ON-TERMINATION FLAG = OFF; INCLUSIVE reading (OH_full counted): FLAG=OFF (best O_full); cov_Ovac = registered rung, context for the rule"
Blocks: Nothing today (both readings agree, FLAG=OFF); fixes the comparator basis recorded for the final readout.

**39. C3 — benchmark conjunct (i) ordering: envelope-with-clean vs clean-ignored**
Where: runs/probe/lit2_readout_2026-08-23.txt:265 (rule at :26; applied at :233-234)
Decides: How A5.2's ordering test "the ordering with falling potential is full-O -> mixed -> full-*OH" is judged. Both readings return True today, but the reading is part of the registered RuO₂ PASS/FAIL rule.
Options as drafted: "C3 ordering (i): judged on the ANALYTIC lower envelope over all U (clean included: mixed is on the envelope iff U(O_full/mixed) > max(U(mixed/OH_full), U(mixed/clean)); OH_full follows iff U(mixed/OH_full) > U(OH_full/clean) -- if clean undercuts mixed first, OH_full never appears); the clean-ignored alternative 'U(O_full/mixed) > U(mixed/OH_full)' is printed beside it; the 2.0 -> 0.8 V scan is a printed table only; transition potentials are analytic line crossings."
Blocks: Nothing today (both readings True; verdict already FAIL on conjunct (ii)); fixes how conjunct (i) is stated in the record.

**40. C5 — ZPE/TS convention for the removed lattice O in cov_Ovac**
Where: runs/probe/lit2_readout_2026-08-23.txt:267 (cov_Ovac scored at :202; at-U* value :248)
Decides: Whether the literal application of n_O*corr_O with n_O = −1 (a −0.05 eV correction for a REMOVED lattice O) stands, given A5.2 registers no separate correction for that case. cov_Ovac is a SCORED registered rung on the Cr envelope (it dominates below 1.065 V).
Options as drafted: "C5 Ovac ZPE: n_O*corr_O applied literally with n_O = -1 (-0.05 eV); A5.2 registers no separate correction for a removed lattice O"
Blocks: The scored dG0 of the cov_Ovac rung (−2.1291 eV/cell) and the clean/cov_Ovac crossing (1.065 V); cov_Ovac is context, not comparator, for the Cr flag.

**41. C6 — η(Cr) of record: sign-off on the frozen tier_v2 value** *(sign-off — non-verdict-bearing: a read of a frozen registered quantity under docs/43 §0; unlike C1–C5/C7–C10 the readout prints no alternative reading for it)*
Where: runs/probe/lit2_readout_2026-08-23.txt:268 (rule potential at :12; U* evaluated at :244)
Decides: Sign-off that the frozen tier of record supplies the η(Cr) the Cr rule is evaluated at — it fixes "U* = 1.23 V + eta(Cr) = 1.5603 V" (:244), the potential behind every Cr-rule number in rows 38, 42 and 43.
Options as drafted: "C6 eta(Cr): from data\tiers\tier_v2.json [tier_v2] (frozen tier of record, docs/43 §0); eta(Cr) = 0.3302830425896852" — no alternative reading is printed.
Blocks: Nothing today (the frozen tier of record governs); U* for the Cr-flag arithmetic is read from it.

**42. C7 — unregistered 1/2 ML *O context rung (ref__2x1o): admit by amendment or not**
Where: runs/probe/lit2_readout_2026-08-23.txt:269 (also :30, :249, :256, :264)
Decides: Whether to write an amendment admitting the half-ML *O rung ref__2x1o into the Cr decision rule. Today it is CONTEXT only ("never scored; C7") but "the most decision-relevant Cr number on disk": admitting it would flip the CONDITIONAL-ON-TERMINATION flag from OFF to ON. Only an amendment (a registered-scope act) can change this.
Options as drafted: "ref__2x1o (1/2 ML *O) printed (dG0 and value at U*), never scored; 1/2 ML *O context rung at U*: -0.2019 eV per site -> if admitted by amendment the flag would read ON (NOT applied; needs its own amendment)"
Blocks: The Cr CONDITIONAL-ON-TERMINATION flag state (currently OFF at −0.0419 eV per site for O_full) — per A5.2 the flag "qualifies; it does not retract" every clean-termination Cr energetics row.

**43. C8 — "per site" unit in the Cr rule: per cus site vs per cell**
Where: runs/probe/lit2_readout_2026-08-23.txt:270 (interpretation declared at :16; rule at :29; alternative applied at :255)
Decides: The unit of the registered "> 0.1 eV per site" threshold — docs/43 does not define "site". Both readings give FLAG=OFF today (−0.0419 eV/site; −0.0837 eV/cell), but the per-cell reading puts the value 0.016 eV from the −0.1 eV threshold (vs 0.058 eV per-site), so the choice can flip the flag at other U*.
Options as drafted: "C8 'per site': per cus site, N_SITES = 2 (docs/43 does not define 'site'); per-cell reading: FLAG=OFF at -0.0837 eV per cell"
Blocks: Nothing today (FLAG=OFF under both); the registered unit for any future application of the rule.

**44. C9 — GATE-1 drift scoring mode: am.4 §2 vs §5-strict**
Where: runs/probe/lit2_readout_2026-08-23.txt:271 (run mode declared at :7; gate provenance at :21)
Decides: Which registered reading scores a BASIN_DRIFT row. Immaterial today: "Rows drifting today: none" — all 8 Cr GATE-1 children AGREE within 5 meV.
Options as drafted: "C9 GATE-1 drift: BASIN_DRIFT rows: am.4 §2 ('the GATE-1 SCF energy is the corrected value ... scored from it') vs §5-strict ('re-relaxed from it and the loop repeats'; the GATE-1 energy may be quoted with a stated 4 meV residual). DEFAULT applied: am4s2; both readings printed per row and per rung (--gate1-drift swaps). AGREE rows quote the child as the energy of record (as the block-1A evaluator does). Rows drifting today: none"
Blocks: Nothing today (no drifting rows); determines the energy of record and re-relax obligations for any future BASIN_DRIFT row.

**45. C10 — does GATE-1 apply to Ru rows (narrow Cr-only reading vs broader reading)**
Where: runs/probe/lit2_readout_2026-08-23.txt:272 (applied per-row at :49-62; Ru rows scored without children)
Decides: Whether the GATE-1 child requirement is Cr-only or broader. All seven Ru rows currently score on the parent relax with no __g1 child; none exist on disk.
Options as drafted: "C10 Ru GATE-1: Ru GATE-1 child not required (manifest gate1_required=false; am.4 §2 + A5.7 name Cr; §5 P16 and A5.2's unqualified 'a __g1 GATE-1 child' sentence read broader; Ru decks run nspin=1 so there is no magnetic basin to drift). Ru __g1.out on disk today: none (reported if one appears; never substituted)"
Blocks: Under the broader reading the scored Ru ladder rows would lack their required GATE-1 children ("No scoreable child -> PENDING_GATE1") — the Ru ladder and RuO₂ benchmark rest on this reading; under the applied narrow reading nothing is owed.

**46. C4 — partial-ladder verdict reporting choice** *(operational, non-verdict-bearing — moot today: ladder complete)*
Where: runs/probe/lit2_readout_2026-08-23.txt:266 (verdict :235-237; "nothing -- the ladder is complete" :260)
Decides: Whether a FAIL is reported the moment a PASS conjunct is falsified on a partial ladder, or the public verdict is held until the ladder completes. Today the ladder is complete and both lines read the same; only sign-off on the reporting stance remains.
Options as drafted: "C4 partial verdict: a falsified conjunct of the PASS rule yields FAIL on a partial ladder (PASS unreachable); holding the public verdict until the ladder completes is a reporting choice -- the outcome cannot change"
Blocks: Nothing — per the source "the outcome cannot change" and the ladder is complete.

---

## Operational (undated)

**47. --bind-to core as the driver default** *(non-verdict-bearing — drafted default: `--bind-to none` stands; "Not proposed, flagged instead"; provably number-neutral)*
Where: docs/47-amendment-8-DRAFT.md:203-205; docs/48-anvil-sizing-2026-08-22.md:50-54, 107-109; tasks/todo.md:20
Decides: Whether the shared pw.x driver's inherited `--bind-to none` is changed to `--bind-to core`.
Options as drafted: docs/47: "Not proposed, flagged instead: whether --bind-to core becomes the driver's default. It is free and provably number-neutral, but queue_r1.sh is shared with every banked run and changing it is a decision rather than a measurement." docs/48: "Whether `--bind-to core` should become the driver's default. It is an 18% gain and provably cannot move a number, but the driver is shared with every banked run and changing it is a decision, not a measurement."
Blocks: Nothing named as gated; every driver run until it is decided forgoes the measured 18 % wall-clock gain (binding "changes placement, not rank count or reduction order, so it cannot change a number; it only changes the clock").

**48. Filing election: drop the cached Xu output from git, or keep the fixture** *(non-verdict-bearing — drafted default: fixture stays committed; the filing obligation itself is DISCHARGED 2026-08-23)*
Where: docs/50-amendment-9-DRAFT.md:19, 156
Decides: Whether ruo2_ooh.out stays committed as the single format-validation fixture or is hashed-out.
Options as drafted: "filed in `docs/research/2026-08-15-sampling/` with `SHA256SUMS` and a README stating provenance and licence (the deck/output pair committed as the single format-validation fixture with attribution — CC0 on Zenodo, CC-BY-4.0 on the mirror); the entrant may still elect to drop the output from git and keep the hash". The :156 open-decisions list words the election wider — "where the four 2026-08-15 artefacts and the Divanis ESI are filed, in git or hashed-out (A9.0, A9.3.4)" — this row deliberately covers only the output-file election because the filing of the four artefacts and the ESI is DISCHARGED as drafted (docs/50:19, :106).
Blocks: Nothing stated — an election that remains open after the discharge.

**49. Disclosure-wording conflict: verbatim rule-sentence vs own words** *(non-verdict-bearing — drafted resolution exists; wording is Frank's)*
Where: docs/50-amendment-9-DRAFT.md:48
Decides: How the authorship-rule sentence appears in the Task 4 disclosure given A7.7's verbatim ban.
Options as drafted: "round-2 :218 says the rule-sentence 'goes verbatim in the 100-word disclosure,' while A7.7 forbids reproducing any amendment sentence verbatim in an application answer (docs/43 :1443-1445). The proposed resolution is that the entrant writes the rule in his own words in the Task 4 disclosure (docs/25 :110-120; docs/44 :125-126) and cites the AI-use log; this draft does not supply disclosure wording."
Blocks: Task 4 disclosure drafting (Frank-authored; the draft supplies no wording).

**50. Verify the atomate ISYM commits before the pairing sentence is cited** *(verification obligation — non-verdict-bearing: both outcomes are drafted, cited-after-verification or narrowed to a stated date)*
Where: docs/50-amendment-9-DRAFT.md:110
Decides: Whether the input-set-audit date claim (a7d5f316 / d2742a3b / the ISYM: 0 comment) may be paired with the pymatgen rate.
Options as drafted: "It is cited only after the entrant verifies both commits and the comment in the atomate git history; failing that, the statement narrows to the version inspected on a stated date."
Blocks: P-BUILDER's pairing sentence and the "dated statement about when the field's canonical framework began disabling symmetry" (A9.3.7's if-and-only-if gate).

**51. Cu revival / held-out-metal pre-registration (a future amendment, or it stays SUPERSEDED)**
Where: docs/51-anvil-queue-triage-2026-08-23.md:24; tasks/todo.md:372-375 (docs/40)
Decides: Whether the unregistered Cu revival thread is ever registered by amendment. Status quo as drafted: the runs/Cu_slab decks are SUPERSEDED ("A7.5 (deposited) puts CuO₂ on the exclusion row; A5.5 firewall — 'the Co *OOH and Cu holes remain holes'"); note A9.6 bars adding "in-house n beyond the cap of 8 (+ conditional SnO₂)", so this needs its own amendment.
Options as drafted: docs/51: "An unregistered revival thread (Cu as the held-out MLIP metal, tasks/todo.md / docs/40) is a registration question for a future amendment, not a launch trigger." tasks/todo.md: "L-followup (cheap, high value): compute ONE held-out metal at DFT and pre-register it before scoring any model on it. Cu is already in `RUTILE_AC` and carries no Hubbard U. Converts 'zero held-out points' into 'one' — a categorical change in what the report may claim."
Blocks: Any Cu launch (unlaunchable regardless without the registration: the Cu PAW pseudo is not among the 12 UPFs staged on Anvil, preflight would refuse; stale outputs would trip the driver's stale-.out refusal); the report's held-out-validation claim class.

**52. Cr multistability — survey scope and banked-number re-runs**
Where: docs/46-anvil-parity-2026-08-22.md:118-124, 213-219
Decides: Open items docs/46 leaves "for the entrant" that A8.3's drafted rule does not close: whether banked numbers from multistable decks are re-run and how the campaign-wide survey is scoped. (The related __g1-above-parent admissibility rule is covered by row 28.)
Options as drafted: "Whether the Cr *OOH multistability warrants its own amendment, and whether any banked Cr number needs re-running with the magnetic state pinned." / "Whether other `nspin = 2` decks in the campaign share this multistability, and how that would be surveyed." / "Whether banked Cr numbers from multistable decks need re-running with the moment pinned, and how many decks campaign-wide are affected."
Blocks: Standing of banked nspin=2 numbers if re-runs are ordered.

**53. S8 melt-set freeze deposit + FWM melt decision**
Where: docs/45-error-ledger.md:54, 82; tasks/todo.md:267-290, 488
Decides: Freezing the melt-set predictions and deciding the melt. docs/45 §D: "S8 freeze | melt-set predictions frozen before first melt | registered as rule (round-2 addendum ccb1806); deposit owed before first ingot | before first melt"; §E: "re-rank gate -> freeze predictions -> melt 2–4 + poor anchor + IrO2 same-bench -> Purdue OER; ONE figure iff complete by freeze" with "re-rank gate first". No calendar date is stated.
Options as drafted: tasks/todo.md: "F. BUILT, awaiting Frank's freeze decision — results/r4_melt_list.json" ("results/r4_melt_list.json is deliberately NOT regenerated; re-run melt_list.py build --out results/r4_melt_list.json at freeze time"; "THEN: weigh sheet (docs/17) + dated Cr(VI) risk assessment BEFORE the first melt") and "Melt decision at FWM — Frank's call".
Blocks: First ingot/melt; the S8 make->measure chain.

**54. S1 silentgate core — Frank writes it himself** *(non-delegable authorship obligation — non-verdict-bearing)*
Where: tasks/todo.md:19; docs/50-amendment-9-DRAFT.md:48, 170; docs/45-error-ledger.md:75
Decides: A Frank-only authorship obligation: the named module set silentgate/readers/*, census.py, classify.py, direction.py, cli.py "written and committed only by the entrant." A9.0 places S1 at Aug 21-27 on the critical path.
Options as drafted: "THE ENTRANT WRITES THE CORE HIMSELF — a few hundred lines of output parsing plus a symmetry-op header read and an exact-zero force census — with AI limited to test scaffolding, CI and review. Rule: AI may not author the object the project is named after." tasks/todo.md: "S1 silentgate core: Frank writes; CI + in-house controls may be built now (A9.6)".
Blocks: S1 and every S2 census number (all flow through the entrant-written core); S1 is otherwise "blocked on A9".

**55. STS report framing — Frank writes** *(non-delegable authorship obligation — non-verdict-bearing)*
Where: tasks/todo.md:489
Decides: Frank-only authorship of the report under the disclosed-AI rules (AI may not write the report/essays core).
Options as drafted: "STS report framing (AI-assistance rules per docs/25) — Frank writes"
Blocks: The report itself (application due Nov 5, 2026).

**56. S2 execution — entrant-only: P-LIT coding and all census parsing** *(non-delegable execution obligation — non-verdict-bearing; same class as rows 54–55)*
Where: docs/50-amendment-9-DRAFT.md:114 (A9.3.6 "Who codes"), 118 (A9.3.7)
Decides: Frank-only execution of S2 — he codes the literature and parses the census raw outputs himself; only he may perform these acts.
Options as drafted: "the entrant codes every included paper's fields from the paper itself and owns the inclusion list; AI may execute the registered search string and pre-screen titles/abstracts for inclusion, logged as such; an AI-suggested code is never the recorded value" (docs/50:114); "all census numbers computed from raw outputs the entrant parsed himself, and all literature codes entered by him" (docs/50:118).
Blocks: Every S2 census number and the coded literature table.
Deadline: none stated (S2 window Aug 27 – Sep 5, docs/50:15).

---

## Later dated obligations

**57. F7 — four papers in hand via Purdue ILL** *(dated obligation — non-verdict-bearing: the fallback, dependent claims narrowed pre-emptively, is drafted)*
Where: docs/50-amendment-9-DRAFT.md:153 (also :110 — "Montoya & Persson's Methods are still unread — pull through Purdue ILL by Aug 29")
Decides: Dated obligation owed by Frank (Purdue ILL): four sources in hand or dependent claims narrowed pre-emptively.
Options as drafted: "F7 — Briquet 2017 (10.1002/cctc.201601662), Chatterjee arXiv:2512.05938, Montoya & Persson Methods, Huang arXiv:2604.12198 all in hand by Aug 29 via Purdue ILL, and anything not in hand has its dependent claim narrowed pre-emptively (round-2 :519-520)"
Blocks: The dependent claims (narrowed pre-emptively if not in hand); the P-BUILDER Methods reading (A9.3.5).
Deadline: Aug 29.

**58. A7.5 — SnO₂ tier admission: Frank's declaration (the Sep 1 cus-site condition is DISCHARGED)**
Where: docs/43-prereg-week1-factorial.md:1413-1415 (the governing registered condition); docs/53-mom2014-a75-sno2-verification-2026-08-23.md:8, 77-80 (§4.1), 106-114 (§5); docs/45-error-ledger.md:74; tasks/todo.md:10-11
Decides: Whether SnO₂ enters the tier as a declared control-stratum member — now Frank's declaration alone. Both preconditions hold: gate (i) capability arm PASSED (job 20094699, 1.188 meV/atom, tasks/todo.md:10) and the Mom 2014 cus-site condition was CONFIRMED 2026-08-23 — "The Sep 1 leg of A7.5 is DISCHARGED — both preconditions now hold" (docs/53:108-110); "SnO₂ admission now awaits only the entrant's declaration" (docs/45:74); "admission = Frank's declaration (no open dependency)" (tasks/todo.md:11). Before declaring, the §4.1 terminology caveat "is the entrant's to read" (docs/53:8): "If A7.5's 'confirmed cus-site' is read as requiring the literal word, the honest classification drops to AMBIGUOUS-leaning-confirmed. The quotes in §3 let the entrant make that call; the AI classification (CONFIRMED_CUS) is disclosed as an AI classification" (docs/53:77-80).
Options as drafted: The governing registered condition (docs/43:1413-1415): "SnO₂ may be admitted as a declared control-stratum member only if Mom 2014's stoichiometric rows are confirmed cus-site by Sep 1 (Man 2011's reduced-surface SnO₂ row is bridge-site, with the cus site reported not to bind)." The remaining act (docs/53:111-114): "It does NOT admit SnO₂. Admission is a separate registered declaration by the entrant ('declared control-stratum member' that 'never enters a headline rate', per the round-2 basis A7.5 encodes), naturally taken inside A8/A10. That decision now has no open dependency."
Blocks: SnO₂'s entry to the tier (the conditional +1 beyond the in-house cap of 8).
Deadline: none stated (the Sep 1 condition is discharged, docs/53:108-110).

**59. SnO₂ deck nspin — a deliberate choice at deck time, if SnO₂ is admitted**
Where: docs/53-mom2014-a75-sno2-verification-2026-08-23.md:90-95 (§4.2)
Decides: The spin-polarisation setting of any future SnO₂ deck — a verdict-bearing protocol parameter (it selects between the weak-binding and binding regimes Mom 2014's restricted vs unrestricted numbers show).
Options as drafted: the deliberate choice vs the inherited default — "an nspin=1 SnO₂ protocol would sit in exactly the weak-binding regime Mom's restricted numbers show. SnO₂ is d¹⁰; this needs a deliberate nspin choice at deck time, not an inherited default."
Blocks: Any SnO₂ deck build (if SnO₂ is admitted under row 58).
Deadline: none stated.

**60. F8 — five citation clears + Crossref bibliography regeneration** *(dated obligation — non-verdict-bearing: the cleared-or-excluded consequence is drafted per item)*
Where: docs/50-amendment-9-DRAFT.md:152-153
Decides: Clearing or excluding five load-bearing citation items before the report leans on them.
Options as drafted: "F8 — the Divanis +0.40 eV correction (ABSENT), the 3.18 ± 0.12 eV intercept (qualitative), the ~0.12 V code floor (dead), the Sun/Reuter/Scheffler citation (item 7), and the PbO₂/OsO₂/SnO₂/GeO₂/PtO₂ structure-type assignments each cleared or excluded by Sep 15, with the bibliography regenerated from Crossref (round-2 :522-523)" — the Sun/Reuter/Scheffler citation is "UNVERIFIED in this repo … and is cleared or excluded in the F8 Crossref regeneration by Sep 15".
Blocks: The prior-art framing sentences; the report bibliography; the five dependent claims.
Deadline: Sep 15.

**61. Resolve δ (corr_OOH) from Nørskov 2004** *(dated obligation — non-verdict-bearing: the δ-curve-only fallback is drafted)*
Where: docs/50-amendment-9-DRAFT.md:106
Decides: Whether a single-δ floor-margin number can be quoted for P-DIVANIS (Table SI-1 has no *OOH row; the "+0.40 eV *OOH correction" is ABSENT from the cited source).
Options as drafted: "If δ is not resolved from Nørskov 2004 by Sep 15, only the δ-curve is reported and no single-δ number is quoted."
Blocks: Single-δ reporting for census product 3 (δ-curve-only otherwise).
Deadline: Sep 15.

**62. A10 — the BEEF amendment**
Where: docs/45-error-ledger.md:32, 53, 79; docs/47-amendment-8-DRAFT.md:26-30
Decides: Drafting, re-authoring and depositing A10, which governs the S5 BEEF-vdW stage and error-class 8 (XC functional, NOT MEASURED). Per A7.7 the amendment is AI-drafted but every threshold is Frank's to re-author, and the deposit is his.
Options as drafted: docs/45 §D row: "A10 | BEEF row | NOT DRAFTED; gated on S0(a) | Sep 18".
Context (not part of the drafted options): the S0(a) gate it waits on is settled — "BEEF is reachable only through `calculation='ensemble'`" (docs/47:26-30). The +U capability probe (PROBE-U, deck (iv) winner + HUBBARD card — "a capability placeholder, not a physics claim", runs/s0/a_beef/README.md:46) has its raw record at runs/s0/a_beef/slab__beefhub.out, which contains the ensemble block ("BEEFens 2000 ensemble energies"); no doc-level verdict line for the probe exists in the repo.
Blocks: S5 "BEEF-vdW sigma, Ru/Ir/Ti; extension to +U metals if clean" — status "gated" (docs/45:79).
Deadline: Sep 18.

**63. Six-row cap: name the displaced prediction or keep P-XU in the appendix**
Where: docs/50-amendment-9-DRAFT.md:138, 156 (P-SYMCOV placement also open: docs/50:138 — "docs/47 does not itself say 'body row,' so its placement is also open")
Decides: Body-figure ledger allocation — the cap is reached before A9 adds anything (P7, P-PROJ, P-PLS, P-FLOOR-U, P-SYMCOV, P-BEEF = six); "THRESHOLD (proposed), entrant's call, decided once in writing before Sep 20".
Options as drafted: "P-CTRL is a gate and takes no ledger row; of A9's five predictions, P-XU is proposed for the body ledger and P-XU-SPAN, P-DIVANIS, P-BUILDER, P-LIT for the appendix ledger with the same HELD/TRIGGERED/WITHDRAWN vocabulary; and the entrant names which already-registered prediction moves to the appendix ledger to make the room, or decides instead that P-XU stays in the appendix and re-tests the headline sentence against that."
Blocks: The body-figure ledger; the abstract lead (round-2 Q6: "the detector plus the exposure census LEADS the abstract, which means P-XU in the body").
Deadline: before Sep 20.

**64. Is the docs/44 sentence the abstract's claim sentence?**
Where: docs/50-amendment-9-DRAFT.md:140, 156
Decides: The entrant's own claim sentence — AI-drafted candidates exist; "what does not exist is the entrant's own claim sentence." ("'Results to date of an unfinished study' is ineligible.")
Options as drafted: "The entrant says whether the docs/44 sentence is the abstract's claim sentence or only the narrative; if the latter, he writes the claim sentence into docs/45 §D as a dated line, and on Sep 20 redrafts it against only what has landed; if it does not stand, a stage is cut rather than hoped for."
Blocks: The Sep 20 re-test; the F3 kill criterion; possible stage cut; the report abstract.
Deadline: Sep 20 (re-test).

**65. Oct 15 hard freeze — P-DISPOSITION on every unscored prediction**
Where: docs/50-amendment-9-DRAFT.md:138; docs/45-error-ledger.md:81
Decides: The registered freeze consequence Frank owes: score or withdraw each prediction by the date; S7 ("freeze, figure pack, pre-submission assertions; arXiv preprint RESTORED as post-freeze option") runs Oct 8–15.
Options as drafted: "P-DISPOSITION and the six-row cap (docs/43 A7.7 :1436-1440): any A9 prediction not scored by Oct 15 is WITHDRAWN-UNSCORED with its date."
Blocks: Everything the report may score; the post-freeze arXiv preprint option.
Deadline: Oct 15 (S7 window Oct 8-15).

**66. STS sponsor of record** *(administrative — non-verdict-bearing)*
Where: tasks/todo.md:492-493
Decides: Resolving the sponsor — a Frank-only administrative decision.
Options as drafted: "STS sponsor of record still unresolved (docs/16 §10) — highest-priority non-technical item; application due Nov 5, 2026, 8pm ET"
Blocks: STS 2027 application submission.
Deadline: Nov 5, 2026, 8pm ET (application due).

---

66 rows total; 52 verdict-bearing. The 14 non-verdict-bearing rows are tagged in place and listed here so the count is checkable: 4, 41, 46, 47, 48, 49, 50, 54, 55, 56, 57, 60, 61, 66 — operational defaults (4, 46, 47, 48, 49), a sign-off on a frozen registered quantity with no drafted alternative (41), a verification obligation and dated obligations whose outcomes are drafted either way (50, 57, 60, 61), non-delegable authorship/execution obligations (54, 55, 56), and one administrative item (66). Per the project boundary, every other row is verdict-bearing and reaches the entrant with no recommendation attached.
