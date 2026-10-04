# Decisions of 2026-10-04 (SI round)

Both decisions: Frank, in session, 2026-10-04. They are recorded here as stated; nothing in this directory applies a screening or eligibility decision.

## Decision 1 — Elsevier asset-CDN route

> Keep the 11 Elsevier-CDN packages AND extend the same route to the 10 non-tier-1 Elsevier checklist records: S22127, S23544, S31125, S00882, S14386, S21070, S30334, S21253, S22941, S29795.

The 11 packages kept: S23135, S31137, S14704, S00358, S00887, S05043, S11279, S20599, S27476, S31037, S23308 (retrieved in `public_si_recovery_2026-10-04/`, route `elsevier_article_asset_cdn_PII_addressed_mmc`). The extension to the ten further records is carried out in `public_si_recovery_2026-10-04_ext/`.

## Decision 2 — S11392 (preprint-version SI): linkage only

> S11392 (preprint-version SI; journal version S13010 already fully read with its own different SI): **linkage only** — record the possible version pair, no duplicate screening, no automatic collapse. S11392 is NOT sent to the reads.

Consequences recorded for this round:

- S11392 is not in any pass input of this directory.
- The possible version pair S11392 (preprint, Research Square 10.21203/rs.3.rs-118932/v1) and S13010 (journal, 10.1021/jacs.1c01655) is recorded as a possible pair only. Neither record is collapsed into the other, and S11392's preprint SI is not screened a second time.
- The recovered S11392 SI file stays where it was retrieved: `public_si_recovery_2026-10-04/files/S11392_VelascoVelezetal_NatureEnergySI2020.docx` (sha256 and size in `public_si_recovery_2026-10-04/recovered_manifest.json`).

## Linkage evidence pointer

`public_si_recovery_2026-10-04/metadata/S11392_S13010_linkage.json` (sha256 `61b57957d9ce8bbf17d81362ede6ca0429001d9639349d810b7aec7ddbc0b955`, 7,987 bytes). It holds the Crossref and OpenAlex records of both versions, the Europe PMC identifiers (preprint PPR253311; journal article PMC8397309), and the differences found: titles differ ("...Water Splitting" versus "...Water Oxidation"), the author lists share the same surnames (17 versus 18 authors), Crossref `relation` is empty for both, OpenAlex lists no link, and the two SI documents differ (preprint: 25 pages, Fig. S1-S7, Table S1-S2; journal: 17 pages, Fig. S1-S10, Table S1-S2). No authoritative link between the two was found; the pair is a possible version pair, not a confirmed one.
