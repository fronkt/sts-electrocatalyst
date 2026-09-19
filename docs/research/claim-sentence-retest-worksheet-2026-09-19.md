# Worksheet for the September 20 claim-sentence re-test (prepared 2026-09-19)

The registered rule: the claim sentence of record is re-tested on September 20 against only what has landed, must be scorable from S1 + S2 + S6 alone, and if it does not stand a stage is cut rather than hoped for (`docs/43:1932`, `docs/45` section D, `docs/87`). The sentence is the entrant's (C11). This worksheet prepares the re-test: it fixes the landed inventory as of 2026-09-19, re-runs the constraint checks on the bounded claim recorded in `docs/45` section D on 2026-09-18, and states what the September 20 check has to confirm. Nothing here is report prose, and no sentence here is offered for verbatim use.

## Gate status

- The dated line owed by `docs/43:1932` exists: `docs/45` section D, 2026-09-05, elects the registered ordering, records that the `docs/44` sentence is narrative, and reserves the claim sentence until S1 and S2 land. This is exit (i) of tension T1 in `docs/87`; the ordering was not re-registered.
- The 2026-09-18 entry in `docs/45` section D records a bounded claim from the completed Xu census and fixes the six body rows (P7, P-PROJ, P-PLS, P-FLOOR-U, P-XU, P-BEEF; P-SYMCOV to the appendix). The September 20 check re-reads it against the inventory below.

## Landed inventory as of 2026-09-19

| Stage | Item | State | Where |
|---|---|---|---|
| S1 | silentgate core; controls 9/9 in-house positive, 0/11 QE negative, 0/500 OC20 negative; CI green | LANDED | `docs/research/silentgate-core-2026-09-13.md` |
| S2 | P-XU: headers 70/810 (8.64%) FALSIFIED; force clause 50 known successes / 496 known failures / 80 unknown of 626 (7.99% to 20.77% bound) FALSIFIED; named pairs 10/10 HELD; every LOCKED output is in the four-layer class | LANDED, independently verified | `docs/research/s2-scientific-readout-2026-09-18.md` |
| S2 | P-DIVANIS: 1/38 at every point of the correction interval | FALSIFIED, landed | same |
| S2 | P-BUILDER: eight O/OH family clauses | HELD, landed (rutile non-blind) | same |
| S2 | P-XU-SPAN | INCOMPLETE EVIDENCE (one full ladder above 0.20 eV, four incomplete) | same |
| S2 | P-LIT | NOT LANDED: retrieval deferred to the API budget boundary (2026-09-20 00:00 UTC); inclusion not frozen; no methods coded | `docs/research/continuation-readout-2026-09-19.md` |
| S2 | Xu reference molecules | DEFERRED (pseudopotential bytes not recovered) | s2 readout |
| S6 | P-PLS 5/6 CONFIRMED; P-FLOOR-U 3/6 SCORED, MIDDLE BAND / NOT MET | LANDED | `docs/45` section D, 2026-09-18 |
| S4/S5 | P-PROJ (1x1 0.4869 V; 2x1v 0.1725 V), P-PROJ-6 MIDDLE BAND, P-BEEF CONFIRMED 3/3 | landed, but not part of the S1 + S2 + S6 scoring set for the central claim | `docs/84`, `docs/83`, `docs/research/s5-beef-readout-2026-09-17.md` |

Consequence for the cut rule: the central claim is scorable from S1 and S2's P-XU alone, with S6 supplying the second-ranked floor result. P-LIT, P-XU-SPAN and the Xu molecules are appendix rows; if P-LIT has not landed by October 15 it becomes WITHDRAWN-UNSCORED with its date (`docs/43` A7.7) and cuts nothing from the central claim.

## Re-test of the 2026-09-18 bounded claim

The recorded sentence: a tested output detector identifies symmetry constraints concentrated in the four-layer subset of a complete 810-output adsorption corpus, while full-population counts reject the registered high-exposure prediction.

| Check | Result | Note |
|---|---|---|
| C7 ordering: detector + exposure census lead | passes | the floor movement and coverage-conditionality belong in the following sentences |
| C8 eligibility: nothing unlanded stated as a result | passes | S1 core exists and is controlled; the 810-output census is complete |
| C10 only LOCKED counts on a symmetry-on corpus; "not LOCKED" is never "free" | passes if "identifies" is read as the detected (LOCKED) count | all 70 LOCKED outputs are four-layer; the two-layer classes have zero LOCKED outputs; "concentrated" is a statement about where detections are, not where freedom is |
| Exposure-versus-consequence rule (`docs/43:1942`) | passes | no in-house control precision and no per-metal consequence is multiplied into the sentence |
| C1 no absolute overpotential for Cr/Fe/Co/Ni | passes | no number of that kind appears |
| C2, C3, C5 (cells, 1x1 scope, constants disclosure) | not engaged | the sentence carries no projector number |
| C4 no class claim from P-PROJ-6 | not engaged | |
| C9 no amendment sentence reproduced verbatim | to be checked on September 20 | the phrase "high-exposure prediction" must be compared against the A9 registration text; the report paraphrases either way |
| Two denominators kept distinct (810 headers versus 626 force outputs) | passes as written | the sentence names the 810-output corpus and "full-population counts" without fusing the force denominator into 810; the readout keeps both |
| Graspability (`docs/75:95-96`) | passes | one sentence, one object, one outcome |

The sentence stands on the 2026-09-19 inventory. Its one soft point is the verb "identifies": the entrant's own wording should make explicit that what is identified is a detected lock (a lower bound), so that C10 cannot be misread.

## What the September 20 check must do

1. Re-read the inventory above and mark any change (a P-LIT landing changes an appendix row, not the central claim; a Cr relaxation readout changes nothing here, it is S3/S4 evidence and enters no claim).
2. Confirm the central claim is scorable from S1 + S2 + S6 alone. It is, on this inventory.
3. Apply the cut rule. No stage needs cutting for the central claim; the open items are appendix rows with their own dates.
4. Run the C9 verbatim check against the A9 text and the two syntheses.
5. Record the outcome as a dated line in `docs/45` section D in the entrant's words.

## What this worksheet does not do

It does not write the claim sentence of record, does not alter any registered threshold, denominator or ordering, and does not treat the September 20 date as met. It records the state on 2026-09-19 so the September 20 check is a comparison, not a reconstruction.
