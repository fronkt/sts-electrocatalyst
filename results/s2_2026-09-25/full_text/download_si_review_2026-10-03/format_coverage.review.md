# Format coverage — 2026-10-03 SI intake

Scope: source/format completeness and visual-render coverage for S29636, S29420, S29447, S28435, and S24094 only. No scientific screening or eligibility determination. Source identity/read gates remain pending in `source_inventory.json`; this note does not change them.

## Coverage checked

| ID | SI payload | Pages / media | Visual index inspected | Notes |
|---|---|---:|---|---|
| S29636 | `nre-0228_ESM.pdf` | 10 PDF pages | `files/S29636/contacts/si_01.png`, `si_02.png` | Every page has a rendered page image and nonzero extracted text (min 171 chars/page). |
| S29420 | `8680_ESM.pdf` | 18 PDF pages | `files/S29420/contacts/si_01.png`–`si_03.png` | Every page has a rendered page image and nonzero extracted text (min 42 chars/page). |
| S29447 | `cs-2025-08494p_si_001.docx` | 46 embedded media items | `files/S29447/contacts/word_01.png`–`word_08.png` | All eight media sheets inspected; rendered media previews include WDP-derived PNGs and an EMF preview. Page-layout render is not recorded. |
| S28435 | `8487_ESM.pdf` | 18 PDF pages | `files/S28435/contacts/si_01.png`–`si_03.png` | Every page has a rendered page image and nonzero extracted text (min 49 chars/page). |
| S24094 | `adma202414579-sup-0001-suppmat.docx` | 54 embedded media items | `files/S24094/contacts/word_01.png`–`word_09.png` | All nine media sheets inspected; TIFF preview images accompany retained media. Page-layout render is not recorded. |

All SI PDF contact sheets and all Word-media contact sheets are visually inspected for missing tiles, blank assets, or obvious preview failure. No missing page/media tile was apparent. The main-PDF page PNG sets are present (10/13/15/9/16 pages for the IDs in inventory order), but this SI-focused pass does not certify main-article visual coverage.

## Format-specific preservation / follow-up

- Keep original SI files byte-exact; preview conversion is supplementary. Retain both original and preview assets, including WDP/EMF/TIFF inputs and their previews.
- S29447 carries one embedded legacy OLE object (`oleObject1.bin`, 340,480 bytes; Compound File signature), five VML-image references, and a preview relationship to `media/image1.emf`. The object was not executed; the extras inventory reports no OLE stream parser available. Preserve the object bytes, relationship/XML inventory, and preview; do not treat the preview as proof that the embedded object was fully represented.
- The initial S24094 `docx_specials` figures (52 math / 8 tracked-change hits) were substring counts, not exact XML element counts. `word_tag_counts_checked.json` confirms 22 actual math elements, 15 math paragraph wrappers, 15 math paragraph-property wrappers, and zero actual revision elements; `word_extras.json` contains 22 equation entries and an empty revisions array. Preserve the source DOCX XML and structured math/revision extraction alongside accepted-revision text; do not interpret wrapper counts as additional equations or revision hits as actual tracked changes.
- `docx_page_layout_rendered` is `false` for both Word packages. Media-sheet coverage is not equivalent to page-layout coverage or proof that each object/figure is located in its surrounding text correctly.
- Higher-resolution S24094 preview `image20.tif.png` visibly contains white masks over part of a plot/its labels in the image itself. This is present in the asset preview, not solely a reduced contact-sheet effect; the obscured content cannot be recovered from that preview.
- Some S24094 media use black backgrounds, and labels/axes can be difficult to read in contact sheets. Consult the corresponding full-size preview and the DOCX text/structured math/revision sources for any later source-level decision.

## Intake state boundary

`source_inventory.json` currently says `identity_review: pending`; per-record `identity_verified` and `si_complete_for_read` are false. The entrant confirmation that listed attachments were downloaded is recorded separately and does not replace these review gates. This format pass does not update either state.
