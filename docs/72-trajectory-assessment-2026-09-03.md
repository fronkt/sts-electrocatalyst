# docs/72 — Trajectory assessment: is the project degrading in rigor, novelty, or placement? (2026-09-03)

## 0. Status of this document

**draft assessment, not a registration.** Nothing here licenses a deck, moves a
threshold, scores a prediction, amends a deposited section, or supersedes docs/70. Every
recommendation below is a *proposal for a dated line the entrant writes*. Per docs/43 A7.7
the entrant paraphrases; no sentence of this file is report prose, and per the STS 2027
Research Report Guidelines item 1 the report itself is written without generative AI.

**Question asked (entrant, 2026-09-03):** "Is the STS 2027 electrocatalyst project degrading?
Is it getting worse in prestige / rigor / placement quality? To my knowledge, right now it is
finding errors in how current DFTs are modeled and then fixing them/comparing."

**CORRECTIONS OF RECORD, 2026-09-03 (appended after §1-§10 were written; read before quoting
anything below).** Five claims in this file are wrong. They are corrected in place here and in
full in **docs/75 §7.1-§7.3**; nothing below has been silently edited.

1. **§8's "free rows" premise is REFUTED by docs/73.** Of 14 candidate free rows, **13 are refuted
   and one survives.** "Close the unscored pile" is NOT a cheap win. Two of §8's three named rows —
   **P-SPIN-DELTA and P-FLOOR-U-SPIN — do not exist**, both blocked by a dated line written the
   same day this file was. The honest move for most of the pile is to accept WITHDRAWN-UNSCORED
   **deliberately and say so**, which §4.2 only gestured at.
2. **§8 item 1's P15 is real but its scope limit is FALSE.** `:242`'s "Amendment 1's check 4' bulk
   magnetic arm has no run" is wrong — **it has a run.** P15 is bigger than this file thought.
3. **§7's G8 grep is SELF-REFUTING.** "no doc cites it" was falsified by this document printing the
   number at `:228-229`. A negative existence claim must exclude the document asserting it.
4. **§5's "STS publishes no rubric" is REFUTED.** The 2027 Official Rules publish a SELECTION
   PROCESS with four named evaluation areas — Research Report and Scientific Merit; **Student
   Contribution to the Research**; Academic Aptitude and Achievement; Overall Potential as a Future
   Leader — and state that *"the research project, while important, is not the only factor."* Two
   of the four are not about the project at all. This correction runs against docs/70:827-832 too.
5. **§1's "novelty IS degrading" needs its scope stated.** It was measured on docs/70's *remaining
   task list*, not on the project's central claim. Per docs/75 §3-§4 the projector step-flip is
   genuinely unoccupied in the electrocatalytic form; what is dead is the "first pre-registered
   study" claim and the make-and-measure loop. **See docs/75.**

**Verification rule used.** Every claim carries a `path:line` pointer or a recorded command.
Negative existence claims were established by grep, not by impression (`tasks/lessons.md:931`).
The commands are printed in §7 so each one is re-runnable.

**Concurrency note (recorded, not silently fixed).** This file was first written as `docs/71`
from a directory listing taken at the start of the session. A concurrent session committed
`docs/71-silentgate-core-implementation-brief.md` (`1c50886`, 2026-09-03 12:12) while this
assessment was being drafted, so the number was already taken. Renumbered to **docs/72**;
neither commit clobbered the other (`1c50886` touched only its own file, this one only
docs/72 + `tasks/todo.md`). **A stale directory listing is the same error class as a stale
owed-list** — re-`ls` before claiming a filename, the way §7's greps re-check a claim.
Consequences of that brief for §2 and §9 are folded in below.

---

## 1. The verdict, in three lines

- **Rigor is NOT degrading.** It is the strongest and still-rising axis, and it is above the
  finalist median for the first-round filter.
- **Novelty IS degrading**, and the project scored it that way itself: every recommended spike
  in docs/70 carries **novelty 2 of 5**.
- **Placement has drifted one tier**, from docs/18's *"Finalist-credible — conditional on the
  wet-lab loop landing"* (`docs/18:70-77`) to its other line, *"your Scholar floor with a
  Finalist upside"* (`docs/18:74`) — with the upside condition currently unmet.

---

## 2. The premise, corrected: whose errors are these?

The entrant's framing was "finding errors in how current DFTs are modeled." The *fixing* is
real. The *whose* is not yet established.

- **27 of 27 numbered traps in `docs/45` are defects in this project's own scripts,
  registrations, readouts, or prose.** None is a field error.
- The two instruments built specifically to show the errors are the field's are **unstarted**:
  `docs/45:77` — "Act 4 (the census) waits on the entrant's silentgate"; docs/70 H-14
  (`:357`) — the silentgate core is "entrant-written, unstarted, and blocks the S2 census."
  Confirmed by grep: **no silentgate module exists under `src/dft/`** (§7 G4).
  **Updated 2026-09-03 (same day):** `docs/71-silentgate-core-implementation-brief.md` now
  exists — a *specification*, explicitly "no implementation code and none may be added to it,"
  the five core paths reserved to the entrant by `docs/43:1840`. So G4 still holds and the
  census is still blocked, but the blocker is now **five files against a written contract**
  rather than against a search. That materially lowers the cost of decision 2 in §9; it does
  not change the verdict in §1.
- The one literature-premise reversal that *is* a field-level result (RuO2 antiferromagnetism,
  `docs/45:2642`) is framed in the ledger as a repo error first: the refuted premise was
  asserted as fact in **deck-generating code**, `src/dft/probe_decks.py:250-253`.

**Consequence.** As it stands the report says *"I audited myself, exhaustively."* The
sentence the campaign wants — *"these errors are the field's"* — is one unstarted deliverable
away, and that deliverable is zero-compute.

---

## 3. What is NOT degrading (record this, it is load-bearing)

- **Three timestamped Zenodo preregistration deposits**: 10.5281/zenodo.21963144 ->
  22072991 -> 22213117. Registered-report methodology at this level is rare;
  `docs/70:461` — "**No pre-registered DFT or computational-catalysis study was found**"
  in three targeted searches.
- **A withdrawn headline, honored on schedule.** P7 fired at 1.122 V against a 0.15 V
  threshold; `tasks/todo.md:24-30` — "§5 says withdraw, not soften."
- **A registered prediction allowed to fail.** A7.3 NOT MET at 3 of 6 (`tasks/todo.md:730`).
- **Fast response to its own audit.** docs/70 was written 2026-09-02; H-1, H-2, H-3 and H-10
  were all CLOSED 2026-09-03 at 0 SU (`docs/45:2642`, `:2851`, `:2986`, `:3059`).
- **The expensive gate is already open.** `tasks/todo.md:207` — "**potentiostat BOOKED**";
  FWM melt access confirmed. `docs/18:89` called the potentiostat "the single gate between you
  and the Finalist-tier half." It is not the blocker any more.
- **Compute is not the constraint.** 59,761.1 SU, empty queue, AMENDMENT 11 fully run
  (`docs/68:322`); `docs/70:653-657` — "Every remaining hole that matters is closed by
  *deciding* or *writing*, not by computing."

---

## 4. What IS degrading, with the measurement for each

### 4.1 Novelty, by the project's own scoring

docs/70 §5.1 scores 18 surviving ideas on **rigor / novelty / STS, each out of 5**
(`:529`). Every recommended spike scores **N=2**: I-19 (`:533`), I-8 (`:537`), I-2 (`:538`),
I-9b (`:539`). The only N=4 (I-6) is parked NOT NOW. 31 ideas generated, 13 killed by their
critics. The remaining program is rigor and presentation, not new science.

### 4.2 The ledger arithmetic — registration is outgrowing scoring

Of the registered predictions **scored**: roughly **3 confirmed** (A7.2 at 5/6 but on exactly
three robust members against a registered >=3 — *zero margin*, `tasks/todo.md:729`;
A7.1/P-PROJ firing at ~5x, 0.487 V vs a 0.10 V threshold; P14/block-1C CONFIRMED at both
delta but campaign-layer PARTIAL PILOT, `docs/49:255-259`), against **6 failed / inverted**
(A7.3 NOT MET; A6.3 INVERTED, `docs/58:93`; P7 triggered; R7-P1 REFUTED; R7-P3 falsification
fires; R8-P1 does not separate) and **2 inconclusive**.

**The pile that matters is the fourth one: 9+ registered predictions are measured-but-unscored**
— P-SPIN-DELTA, P-FLOOR-U-SPIN, P-SYMCOV (no branch verdict), P15, P18, P-BEEF, and all five
A9 census predictions. Under `docs/43:2247-2270` every one auto-converts to
**WITHDRAWN-UNSCORED with its date** when REPORT LOCK executes.

> **This is the degradation, stated precisely: the registration is growing faster than the
> scoring.** A preregistered report carrying three scored positives and nine dated
> WITHDRAWN-UNSCORED rows reads very differently from the same work with those rows closed —
> and most of them close with a decision or a paragraph, not with compute.

Registered *priors* have also failed alongside the predictions: P13's "not separable"
(`docs/43:187`), A6.2's "additive" (`docs/58:56`), A5.1(d)'s U-robust intercept
(`docs/60:255-257`). Individually unremarkable; collectively a pattern the report should name
deliberately rather than let a reviewer notice it first.

### 4.3 No positive claim, and a self-imposed ban that keeps it that way

There is no positive discovery claim anywhere. docs/70 H-6 (`:212`): "**No physical result,
no re-rank code**"; `results/r4_melt_list.json` unchanged since 2026-08-05 (§7 G6; the file is
gitignored by design, `.gitignore:14`); **no ingot melted**; no re-rank implementation exists
(§7 G3). The nearest chemical fact is bounded weak binding — TiO2 *OOH at 2.041 A, "+0.035 e
of Loewdin charge ... the binding is real but **weak**" (`docs/60:83-88`) — and it is a
recurrence of a solved defect the DFT deck path never inherited (`docs/60:66-75`).

And `docs/43:1396-1400` bans the materials framing outright: "the report may **never** quote an
absolute eta for Cr, Fe, Co or Ni as a materials claim." **Correct call — but it means no
additional DFT can recover a catalyst headline. Only S8 can.**

### 4.4 The narrative has four beats and two are unexecuted

The standing one-sentence story, `docs/44:176-181`: (1) set out to find a cheap alloy to beat
iridium -> (2) the hidden errors turned out 10x larger than the differences being ranked, so
measure and fix them -> (3) **"showed the same errors sit in the field's published data"** ->
(4) **"then re-ranked my candidates, melted them, and measured them against iridium itself."**

**Beats 3 and 4 are both unexecuted.** Beat 3 is the Xu 810-output census (blocked on
silentgate). Beat 4 is S8. The same passage warns: "**rigor-without-a-payoff has no ending.**"

Note also docs/70 H-7 (`:240`): the "10x" ratio in beat 2 is itself flagged as inflated by
construction — every ledger magnitude is a per-class **maximum on one metal** while
0.03-0.08 V is a *typical* separation, and "Max-versus-typical inflates the ratio by
construction and is the first thing an adversarial reader will say."

### 4.5 Diminishing returns are visible in the commit stream

Since 2026-08-20: **204 commits, 52** matching a broad new-computation keyword set (§7 G5 —
crude proxy, not a precise ratio). The last three days produced four consecutive nulls at
0 SU: A11.R6 EXHAUSTED (0 of 16 converged, closest approach 595x the threshold), R7 REFUTED,
R8 "DOES NOT SEPARATE", R9 with not one rung reaching nominal p<0.05.

---

## 5. A reassurance in the repo that must NOT be leaned on

docs/70 H-6 (`:227-234`) argues make-and-measure is not a Finalist precondition, citing three
compute-only DFT Finalists and "four consecutive computational first places."

**That was withdrawn by the same document's own completeness critic.** §8.1 C-6 (`:851`):
H-6 "rebuts a claim docs/18 does not make" — docs/18 already tables three compute-only
Finalists and states the criterion as **stage, not modality**: "even the pure-compute
Finalists (Guan, D'Halleweyn) had a *finished* computational deliverable applied to real
systems." C-2 (`:845`) further found **Iyer 2021 described as first-principles catalysis when
it is a Li-ion cathode paper**, with six of those STS attributions never opened.

C-6 closes with the sentence that matters here: "**docs/18's actual criterion has still not
been tested against the present state (withdrawn headline + one failed registered
prediction), and that test is what Q-5 needs.**"

Related: `docs/70:827-832` — STS publishes no rubric, so *every* placement claim in this
project, docs/18's original included, is inference from precedent.

---

## 6. Two risks nothing in the tree is tracking

### 6.1 The competing-deadline ledger has vanished from the plan

`grep -icE "ICLR|MoML|AI4Mat|Concord|Breakthrough|Coke|college|ED app"` over docs/70 and
`tasks/todo.md` returns **0 and 0** (§7 G1). The 2026-08-15 round-2 synthesis called this
ledger "the only constraint that decides anything." Since it was written, **ICLR 2027 was
added — abstract Sep 18, full paper Sep 25** — landing on top of spikes S-3 (Sep 15-20) and
S-4 (Sep 20-Oct 6).

*This is not a re-run of the "21 effective days / drop two deadlines" ultimatum, which
`docs/44:190-193` voided under the standing rule that budgets are sized to the hard deadline,
not to assumed hours. The point is narrower and factual: the collision list is not on the
board at all, in either planning document.*

Related and already noted by docs/70 itself, `:894-896`: "**The report itself is unpriced** —
S-5 carries no hour estimate, against a hard page limit, no outline in the tree." Calendar:
Oct 6 -> Nov 5 is **30 days** for a 20-page report the entrant writes without generative AI.

### 6.2 The mentor one-pager promises the melt

`docs/outreach/one-pager.md` (committed 2026-08-18, sent in the Wave-2 mentor mailing) states:
"melt access is confirmed at Fort Wayne Metals ... **so the computational rankings will face a
real measurement before the project's mid-October data freeze.**" If Q-5 lands no-go, the
recipients were recruited on a claim that is no longer true and need a line.

### 6.3 (Observation) The generalist reader is absent from the planning

`grep -icE "cross-disciplinary|generalist|so what|significance"` over docs/70's 929 lines
returns **0** (§7 G2). Every hole and spike is about internal correctness. Per `docs/25:175-187`
the Finalist cut is made by a **15-person cross-disciplinary panel**, and `docs/44:20-41`
already flagged this exact risk: "The **risk is legibility, not substance**."

---

## 7. Commands (each claim above is re-runnable)

```
G1  grep -icE "ICLR|MoML|AI4Mat|Concord|Breakthrough|Coke|college|ED app" \
      docs/70-ideation-holes-spikes-2026-09-02.md tasks/todo.md      -> 0, 0
G2  grep -icE "cross-disciplinary|generalist|so what|significance" \
      docs/70-ideation-holes-spikes-2026-09-02.md                    -> 0
G3  grep -rl "rerank\|re-rank" src/                                  -> (no file)
G4  ls src/dft/ | grep -ci silentgate                                -> 0
G5  git log --pretty=format:'%s' --since=2026-08-20 | wc -l          -> 204
    ... | grep -icE 'BANK|LANDED|banked|converged|SCFs'              -> 52
G6  ls -l results/r4_melt_list.json                                  -> Aug 5 18:54 (gitignored)
G7  grep -A3 -i "Hubbard U parameters" \
      runs/hp_tio2/hp__atomic_q222.Hubbard_parameters.dat            -> 4.2245 eV
      runs/hp_tio2/hp__atomic_q333.Hubbard_parameters.dat            -> 4.2251 eV
G8  grep -rn "4.224\|4.225" docs/ tasks/                             -> no doc cites it
```

---

## 8. Cheap conversions — scored rows for the price of writing them down

1. **P15 / hp.x TiO2 has a banked result that appears in no document.**
   `runs/hp_tio2/hp__atomic_q222.Hubbard_parameters.dat` -> **U(Ti,3d) = 4.2245 eV**;
   `..._q333...` -> **4.2251 eV**. Inside the registered [3.0, 7.0] window, q-mesh spread
   **0.0006 eV**. No doc cites either number (§7 G8) and no GO/NO-GO verdict exists. *0 SU.*
   (Scope limit stands: the CrO2 **slab** arm is 4/4 "Convergence has not been reached", and
   Amendment 1's check 4' bulk magnetic arm has no run — so this closes the TiO2 leg only.)
2. **Co formal discharge** — one GATE-1 SCF on the replay's final geometry, ~5-19 SU, not
   launched (`tasks/todo.md:1252-1263`).
3. **P-SPIN-DELTA has its numbers and no verdict line.** Measured D_M: Ti -0.0169, Ir +0.0091,
   Ru -0.0070, Cr/Mn/Fe ~0; the census states verbatim that it "applies NO P-SPIN-DELTA
   verdict." On its face zero metals cross 0.026 eV and it is not in the falsification band,
   i.e. the same MIDDLE BAND as A7.7 — **but nobody has written that line.** *0 SU.*
4. **RCAC ticket** — drafted in Gmail (`r1072822063942699521`), never sent.

---

## 9. Recommended decisions, with dates

**The scarce resource is entrant-hours, and every item below competes with the report.**

| # | Decision | Why now | Cost |
|---|---|---|---|
| 1 | **Q-5, S8 go/no-go — pull forward from S-3 to this week** | Largest remaining fork (`docs/70:794`); everything downstream is shaped by it; a partial chain is worse than none under the eligibility rule; and the potentiostat is already booked, so this is a decision, not a resource problem | 1-2 h |
| 2 | **Q-10, silentgate: write it or withdraw S2 explicitly** | The single cheapest thing that converts self-audit into field-audit (§2, §4.4 beat 3). "An owed-but-unwritten gate at lock is the worst of the three outcomes" (`docs/70:816-818`). **The spec now exists (docs/71) and the gap is exactly five entrant-written files** — so this is no longer a design problem, only a decision plus writing time | decision now |
| 3 | **Write the claim sentence early — do not wait for Sep 20** | `docs/43:1932` — "what does not exist is the entrant's own claim sentence"; 8-9 claimants against a 6-row cap (`tasks/todo.md:760`); the S-2 figure and the displacement both wait on it | 2-4 h |
| 4 | **Close the unscored pile before it auto-converts** | 9+ predictions -> WITHDRAWN-UNSCORED at lock (`docs/43:2247-2270`); §8 items 1 and 3 are free rows | see §8 |
| 5 | **Put the deadline ledger back on the board, ICLR included** | §6.1; not a capacity assumption, an absent list | 15 min |
| 6 | **Price and outline S-5** | `docs/70:894-896`; 30 days for 20 pages, no outline in the tree | 1-2 h |
| 7 | **Decide the one-pager follow-up** | §6.2 — only if Q-5 is no-go | 15 min |

**Divergence on decision 1, recorded rather than reconciled.** A parallel session on 2026-09-03
recommends the opposite *direction* on the same fork: "S8 make-and-measure is **dead for this
cycle** — declare it rather than letting it hold the report open." **No S8 ruling exists in the
tree** — grep over `tasks/todo.md` and docs returns only the open Q-5 line — so that is a
recommendation, not a decision of record. This file recommends only that the call be **made
this week**, not which way it goes; the two agree that leaving it open is the worst option. The
inputs that argue against a go are the eligibility rule on incomplete investigations and the
absent re-rank code; the input that argues for one is that the potentiostat is already booked
and `docs/18` makes the wet-lab loop the whole difference between the two tiers. **Frank's call,
in a dated line, either way.**

---

## 10. Errors made in producing this file, recorded not silently fixed

- On first reporting, this assessment stated the project owns **one** confirmed prediction. It
  owns **three** (A7.2, A7.1/P-PROJ, P14/1C — the last a partial pilot at the campaign layer).
  Corrected in §4.2.
- The §4.5 commit ratio was first computed as 203/48 under a line-anchored pattern and is
  **204/52** under the pattern printed in §7 G5. It is a crude keyword proxy for "banks new
  computation" and should not be quoted as a precise figure.
- `results/r4_melt_list.json` is **gitignored by design** (`.gitignore:14`), so its Aug 5 date
  is a filesystem mtime, not a git fact, and its absence from version control is a project
  convention rather than a defect. Stated correctly in §4.3.

---

## Dated addendum — 2026-09-03: four claims in this file are corrected, and §9 decision 4's premise does not hold

**Status: draft correction of record. Nothing above this line is edited in place.** The
census that produced these corrections is **docs/73**; it was run specifically to test this
file's §8/§9 premise, and it refuted most of it.

**The premise that failed.** §4.2 and §9 decision 4 hold that **9+ predictions are
"measured-but-unscored"** and that §8's items are **free rows** closable "with a decision or a
paragraph, not with compute." Tested with 51 agents over two passes — bottom-up enumeration,
then per-token adversarial refutation. **Of 14 candidate free rows, 13 are refuted and one
survives.** The pile is mostly a *dated entrant line* away, or unreachable. **§9 decision 4
should be rewritten on the corrected premise**; §9's other six decisions are unaffected.

**Four factual corrections, each measured:**

1. **§4.2 / §8 — "measured-but-unscored" is wrong for the A9 five.** Nothing in P-XU,
   P-XU-SPAN, P-DIVANIS, P-BUILDER or P-LIT has been **measured**: the detector does not exist,
   the census has never run, and `.github/ci/run_controls.py` prints **RESULT: NOT GREEN** with
   all six control rows NOT MEASURED. This file already says so at :52 and :142; the §4.2 phrasing
   contradicts its own later sections. The right label is **UNSCORED AND UNMEASURED**. Related:
   **P-BEEF is not a registered prediction at all** — Amendment 10 exists nowhere as registered
   text, so it cannot be "measured-but-unscored" either.
2. **§8 item 1 / :242 — "Amendment 1's check 4′ bulk magnetic arm has no run" is FALSE.** It ran,
   it converged, and it matches docs/43:619-627 term for term:
   `runs/hp_tio2/hp__cro2_q222.Hubbard_parameters.dat` gives **U(Cr-3d) = 6.1635 eV**, the `.out`
   has **zero** "Convergence has not been reached" and one `JOB DONE`, and the parent SCF carries
   `nspin = 2`, `mv`/0.01, `U Cr-3d 1.d-8` with a 4.00 µB/cell moment. **Commit `dc38c23`
   (2026-08-10) records it in its own message.** The claim was contradicted by the repo's own
   history for 24 days. **Consequence: the P15 GO is a BULK GO, not "the TiO₂ leg only"** — check
   4′ is precisely the registered escape from docs/43:620-621's closed-shell scope sentence.
3. **§7 G8 / :230 — "no doc cites it" is self-refuting.** This file prints both U values at
   :228-229 and again at :238-239, and `tasks/todo.md:1414` prints both. The grep was accurate
   about the corpus it ran over and wrong as a claim.
4. **§4.2 / :117-118 — P13's failed prior is mis-pointed.** It cites `docs/43:187`, which is
   inside the Ru-coverage paragraph. The "not separable" prior is at **docs/43:177-179**. The
   verdict is right (I(Ir, *OOH) = +0.2661 eV lands INCONCLUSIVE, not ≥ 0.30 eV); the pointer
   sends a reader to a different, unscored prediction.

**What survived unchanged**, and is worth saying because most of this file did: §1's three-line
verdict, §3's list of what is not degrading, §4.1's novelty scoring, §4.4's beat count, §5's
warning about H-6, §6's two untracked risks, and decisions 1, 2, 3, 5, 6 and 7 of §9. The
strategic reading of this file stands. What failed is one premise about cost, and it failed in
the direction that makes the remaining work **larger**, not smaller.

**Two items this file listed as owed were discharged the same day it was written**, so its own
owed-list is already partly stale — the failure mode it correctly names at §0 and §10:
**P14's §7c commit step** (banked 2026-09-03; the artifact record no longer contradicts docs/49)
and **H-9** (docs/45 §B row 10). Grep for the resolution token before repeating any item here.
