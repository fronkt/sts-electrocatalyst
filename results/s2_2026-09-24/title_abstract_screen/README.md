# Title/abstract pre-screen of the provider-identity union — 2026-09-24

Two independent title/abstract passes over all 31,471 provider identities of the 2026-09-22 handoff, merged by a fixed rule. **A pre-screen routes records; it decides no eligibility.** Method fields stay NOT_CODED. There is no P-LIT proportion or verdict.

## Files

- `build_screen_inputs.py` builds the inputs offline from the handoff and the hashed raw OpenAlex pages: 410 pages hash-verified; 31,471 identities; 28,478 with a DOI; 27,280 with an abstract; 596 abstracts cut at 4,000 characters and flagged. `inputs/chunk_*.jsonl` (32 × 1,000) is regenerable and kept local. Its hashes are in `manifest.json`.
- `screened_identities.csv` holds the full record of every screened identity: DOI, title, date, type, venue, first author, author count, language, query membership, and raw-page locator with hash.
- `screening_instructions.md` gives both passes the same instructions: three labels, and "when in doubt, not CLEARLY_IRRELEVANT".
- `merge_passes.py` applies the fixed rule. A record is **PRESCREEN_EXCLUDED only when both passes independently label it CLEARLY_IRRELEVANT**. Every other record, including one missing from either pass, goes to FULL_TEXT_REVIEW.
- `batch_screen.py` runs the same two passes through the Message Batches API. It uses 20 records per request, with a different seeded grouping and order in each pass, and saves every raw result. It needs Anthropic credentials, and none are present yet.

## Pilot (`pilot/`)

The pilot drew 200 records: 193 at random (seed 20260924) plus 7 sentinels. The sentinels are papers already independently reviewed as eligible, or eligible base papers of the reference pass. They were shuffled in and hidden from both screeners. Each pass read every record itself, with no keyword labelling, and neither pass saw the other's output or the key. Pass B worked through the records in reverse order.

| Result | Value |
|---|---|
| Sentinel recall (routed to full text) | **7 / 7**; both passes labelled all seven LIKELY_RELEVANT |
| Exclusion agreement between passes | 191 / 200 (0.955) |
| Routed PRESCREEN_EXCLUDED / FULL_TEXT_REVIEW | 156 / 44 |
| Random records routed to full text | 37 / 193 (19%) |

The nine disagreements are borderline: photocatalysis, reviews, experimental Ir/Ru nanoparticles, and a RuO2(110) surface-state paper. The rule sends all nine to full text. Extrapolated from the random 19%, about 6,000 identities would reach full-text review. That volume, not the pre-screen, drives cost and access work for the next stage.

## Full run, 2026-09-25 (`passes/`)

The full run used the pilot's procedure unchanged:
- **Screeners:** in-session, the same model as the pilot.
- **Inputs:** one batch file of 200 records per screener, with the shared instructions and `passes/SCREENER_BRIEF.md`.
- **Coverage:** all 31,471 union identities plus the 238 reference-pass DOIs (`reference_inputs/`, built by `build_reference_inputs.py` from OpenAlex; 192 of the 238 have abstracts). Total 31,709 records.
- **Batching:** `session_screen.py` makes 159 batches per pass. Each pass uses a different seeded grouping, and no A batch shares more than 9 records with any B batch.
- **Order:** pass-B screeners read each batch from last record to first.
- **Validation:** every batch output was checked for order, coverage and labels (0 invalid). The `*.in.jsonl` batch files are regenerable from the chunks and are kept local; their hashes are in each pass's `plan.json`.
- **Interruption:** a usage limit cut off 20 in-flight screeners partway through. None had written output, so all 20 were rerun from scratch.

| | Pass A | Pass B |
|---|---:|---:|
| CLEARLY_IRRELEVANT | 27,909 | 27,641 |
| POSSIBLY_RELEVANT | 3,295 | 3,580 |
| LIKELY_RELEVANT | 505 | 488 |

- **Agreement on exclusion:** 30,369 / 31,709 records (0.958).
- **Recall:** all 7 pilot sentinels were labelled LIKELY_RELEVANT by both passes and routed to full text.
- **Fixed rule** (`passes/merge_rule_only/`): 27,105 PRESCREEN_EXCLUDED, 4,604 FULL_TEXT_REVIEW.

**Declared safety net (deviation, added 2026-09-25 during the run).**

- **What was found:** an audit of batch B_077 found screeners splitting on an ambiguity in the instructions. "Any OER work on RuO2, IrO2 …" is listed as POSSIBLY_RELEVANT, but "purely experimental … no computation mentioned" is listed as CLEARLY_IRRELEVANT. Experimental rutile-oxide OER papers that often carry DFT in the SI were therefore sometimes excluded by one screener.
- **The net:** `merge_passes.py --rescue` sends a double-excluded record to full text anyway when its title or abstract names a rutile-family oxide (RuO2, IrO2, rutile, SnO2, MnO2, PbO2, TiO2(110)) within 300 characters of an OER term. These records get their own route, FULL_TEXT_REVIEW_RESCUE, so they stay identifiable. The net only adds records and never excludes one.
- **Result** (`passes/merge/`, the routing of record): 26,123 PRESCREEN_EXCLUDED, 4,604 FULL_TEXT_REVIEW, 982 FULL_TEXT_REVIEW_RESCUE. That is **5,586 records for full-text review**.
- **Pilot check:** on the pilot, the net adds 8 records and leaves recall unchanged.

`passes/merge/merged_routes.csv` carries each record's DOI, title, date, both labels and both reasons, and its route. It is the DOI-level record of what was screened and how.
