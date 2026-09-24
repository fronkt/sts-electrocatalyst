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
