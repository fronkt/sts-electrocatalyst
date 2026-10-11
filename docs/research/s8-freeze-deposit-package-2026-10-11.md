# S8 freeze deposit package, 2026-10-11

Status: **ready to run once Frank has settled the items below. Nothing has been created on Zenodo.**

Decision of record: Frank, 2026-10-11: "Yes, start on the deposit package", after the arm C extension's last readout ([s8-arm-c-extension-2026-10-08.md](s8-arm-c-extension-2026-10-08.md), "Round 6 readout").

Deadlines (freeze status line and §1): the freeze must be deposited before the first ingot. If the extension's readout is not deposited by Oct 21, OER measurements start anyway and the extension is reported as not tested.

## What it deposits

One new restricted version of concept record 10.5281/zenodo.21963143, drafted off version 22884160 (A10, published 2026-09-21).
- A read-only check on 2026-10-11 found 22884160 the latest of the concept's five published versions, with no draft open (`docs/deposits/2026-10-11-S8-zenodo-precheck.json`).
- The version carries the S8 stage-1 freeze ([s8-stage1-freeze-proposal-2026-10-07.md](s8-stage1-freeze-proposal-2026-10-07.md)) as confirmed, with arm C's final readout and the extension's final readout. It therefore makes both deposits of the freeze's blinding rule (freeze §1, §8).
- A new version replaces the whole fileset, so it also carries every file of the A10 version.
- docs/43 also brings its four dated addenda of 2026-09-22 into a deposit for the first time: three licensed compute additions under A11.R3, and the entrant's election "Protocol research first, freeze later". docs/45 has gained only the A10 DOI line.

## Fileset

21 files, about 1.6 MB. The manifest is written at deposit time from the committed blobs.

| Repo path | Deposited as | Why |
|---|---|---|
| the 12 files of the A10 version | as in A10 (docs/43 as `43-prereg-week1-factorial-A1-A13-plus-A10-plus-S8.md`) | a new version replaces the fileset |
| `docs/research/s8-stage1-freeze-proposal-2026-10-07.md` | `s8-stage1-freeze-as-confirmed-<confirmation date>.md` | the frozen predictions, hypotheses and protocol |
| `docs/95-census-2-3-readout-2026-09-13.md` | same name | arm B's census readout |
| `results/s8_ranking_statistic_2026-09-19/ranking_statistics.md` | `s8-ranking-statistics-2026-09-19.md` | arm B's statistic and quantile convention |
| `docs/research/s8-arm-c-dft-design-2026-10-07.md` | same name | arm C's design and readout record |
| `results/arm_c_2026-10-07_rerun/readout.json` | `s8-arm-c-final-readout-2026-10-07.json` | arm C's final readout |
| `docs/research/s8-arm-c-extension-2026-10-08.md` | same name | the extension's design, each round's rules and every readout |
| `results/arm_c_ext_r6_2026-10-11/readout.json` | `s8-arm-c-extension-final-readout-2026-10-11.json` | the extension's final readout |
| `docs/research/s8-melt-plan-2026-10-07.md` | same name | the processing and electrode format the freeze cites (§5, §6) |
| `docs/research/s8-weigh-sheet-2026-10-08.md` | same name | the six compositions at 200 g (§5) |

Not deposited:
- Arm A's record, `docs/37-hea-screen-result-and-melt-list.md`. Arm A is dated by commit 96b1cb1 and enters as a dated historical prediction. The file has changed since (8f16868, 2026-09-06), and the freeze carries arm A's values (§3).
- The Cr(VI) risk assessment. It is a safety document, not part of the predictions.
- `results/r4_gated.json`, which is not committed; the freeze carries the compositions (§2).

## Metadata

Set in `src/dft/zenodo_deposit.py` (`metadata()`):
- The published title stem, upload type, keywords, creator and restricted access are unchanged. The title ends "…, the Hubbard-projector arms, and the S8 stage-1 melt freeze (confirmed <confirmation date>)".
- Version: `A1-A13-plus-A10-plus-S8`.
- The standing description and the three earlier dated paragraphs are carried byte for byte. One dated paragraph is added. It covers:
  - the three arms;
  - the registered hypotheses;
  - the recorded departures;
  - the first deposit of docs/43's 2026-09-22 addenda;
  - the commit and the manifest.

## What Frank settles first

1. The freeze's [CONFIRM] items:
   - the scope line's wording (§1);
   - the processing values, with Fort Wayne Metals (§5): Mn over-charge +4%, and homogenization at 1,050 °C for 24 h under Ar;
   - the electrode format (§6). The freeze still describes a potted stationary disk ("Stationary electrodes only"). The melt plan has, since 2026-10-09, specified 5.00 × 4.00 mm press-fit rotating-disk inserts at 1600 rpm, pending Tackett's shroud confirmation, with the stationary disk as the fallback. The EC-MS disk in the O2 item follows the same choice;
   - the electrochemistry values (§6), including the rule that a difference counts only above twice the pooled coupon-to-coupon SD;
   - the O2 / Faradaic-efficiency framing (§6).
2. The date of that confirmation. It goes into the script as `CONFIRMED`, and into the freeze's deposit name.
3. Whether any button has been melted yet. It goes into the script as `FIRST_INGOT`: "before the first ingot", or, if a button was melted before the deposit, the recorded departure. The freeze requires the deposit before the first ingot (its status line).
4. The fileset above: any file to add or drop.
5. The go to publish. Publishing is irreversible: it mints the DOI.

The script refuses to write a manifest, create a draft, upload or publish while any of these holds (`pending()`, tested in `tests/test_zenodo_deposit.py`):
- `CONFIRMED` or `FIRST_INGOT` is unset;
- `CONFIRMED` is not a YYYY-MM-DD date;
- the committed freeze still carries a [CONFIRM] marker or its "proposed, not frozen" status line.

## Run sequence

Each command is `PYTHONPATH=src python src/dft/zenodo_deposit.py …`. The script refuses while any tracked file is modified, so every step runs from a committed tree. `docs/deposits/.draft_state.json` is tracked, and `--create` rewrites it, so the draft is created and uploaded in one invocation, as for A10 (27ced99, e4b3e65).
1. **Settle and commit.**
   - Fill `CONFIRMED` and `FIRST_INGOT`.
   - Edit the freeze: the settled [CONFIRM] items, and a status line saying it was frozen on the confirmation date. Every "[CONFIRM" must go, including the mentions in the status line and §8, or the script refuses.
   - Append the docs/43 addendum and update docs/45 (texts below). Their DOI and commit stay as `S8-DEPOSIT-PENDING` and `S8-COMMIT-PENDING`, as A10's did.
   - Commit.
2. **Dry run**, with no flag. Check the fileset, and that nothing is left to settle.
3. **`--manifest --create --upload`**, in one invocation at the step-1 commit.
   - It writes `docs/deposits/<step-1 commit date>-S8.manifest.txt` and opens a new-version draft off 22884160.
   - It removes the inherited files and uploads the 21 committed blobs.
   - It sets the metadata and checks every remote checksum against the blobs.
   - The manifest, the draft and the description all name that one commit. Nothing is published.
4. **Commit** the manifest and `docs/deposits/.draft_state.json`.
5. **Publish, on Frank's go:** `--publish`. This mints the DOI.
6. **Fill in and close.**
   - Replace `S8-DEPOSIT-PENDING` and `S8-COMMIT-PENDING` in docs/43, docs/45 and the freeze's status line with the DOI and the step-1 commit.
   - Set `LATEST_PUBLISHED_RECID` to the new record.
   - Commit and push.

## Text for the dated lines

**docs/43**, appended at the end at step 1:

> ## <confirmation date> — S8 stage-1 melt freeze: confirmed by the entrant and deposited
>
> **The entrant's confirmation of <confirmation date>** of `docs/research/s8-stage1-freeze-proposal-2026-10-07.md`, with its [CONFIRM] items settled: <scope line; processing values; electrode format; electrochemistry values; O2 framing>.
>
> **What is frozen.** Three predictions of OER activity for the six batch-1 alloys (freeze §2–§3):
> - (A) the August 5 MLIP screen, a dated historical prediction (commit 96b1cb1);
> - (B) the September census's 10th-percentile statistic, the re-rank of record;
> - (C) arm C's DFT+U values, whose registered readings (K1, K2, the Ni34 nomination) are NOT_EVALUABLE_UNDER_ARM_C and which enter as an exploratory partial order over four alloys. With them come the arm C extension's exploratory values for five alloys (`results/arm_c_ext_r6_2026-10-11/readout.json`, commit f944a91); Cu8Cr23Mn35Co34 has no DFT alloy value.
>
> Of the primary hypotheses, K1 decides between arms A and B and K2 is shared by them (freeze §3). The same-bench comparison with IrO2 is a registered secondary outcome (freeze §6).
>
> **Departures recorded in the freeze.**
> - The re-rank gate departs from the S8 rule of 2026-08-16 in three places (freeze §1a).
> - Every extension round after the first was chosen after the previous readout was known.
> - The last round's selection threshold was set after its screen was run (freeze §4b).
>
> **Timing.** Deposited <before the first ingot | the recorded departure> and before any OER measurement of these alloys. This makes both deposits of the freeze's blinding rule.
>
> **Deposit.** A new restricted version of concept record 21963143: DOI S8-DEPOSIT-PENDING, from commit S8-COMMIT-PENDING (manifest `docs/deposits/<step-1 commit date>-S8.manifest.txt`).

**docs/45**, §D, the S8 freeze row's status, at step 1:

> **CONFIRMED <confirmation date>** by the entrant (docs/43, addendum of <confirmation date>), with arm C's and the extension's final readouts; deposit: DOI S8-DEPOSIT-PENDING

and §E, the S8 row's status:

> freeze confirmed <confirmation date>; deposit DOI S8-DEPOSIT-PENDING; melt next, after the Cr(VI) risk assessment is signed
