# Provenance record

**What this file is.** The register that `docs/43-prereg-week1-factorial.md:1840` and A7.7
(`docs/43-prereg-week1-factorial.md:1441-1447`) require: the artefacts in this repository that were
produced as disclosed research infrastructure — sweeps, amendment drafts, critique, scaffolding,
CI, tests and fixtures — and the statement of what was not produced that way. Its path was
elected 2026-09-04 (`docs/43-prereg-week1-factorial.md:4200`): this single file, read by
`.github/ci/check_disjoint.py` through `S1_AI_USE_LOG` in `.github/workflows/s1-controls.yml`.
Initialised 2026-09-05 at the entrant's specific request (Phase-2 plan, step 1).

**What the CI assertion proves, and its ceiling.** `.github/ci/check_disjoint.py` extracts every
path-like token below and fails if any one of them names a core path, if this file is missing, or
if it names no file at all. It therefore proves exactly one sentence: *every file logged here is
outside the core.* It cannot detect undeclared authorship, and no README, face or disclosure may
claim that it can.

**How the initial list was assembled, and what absence means.** Two sources. (1) Statements the
repository already makes about its own files — `AUTHORSHIP` headers, the hand-off list in
`docs/57-s1-ci-handoff-2026-08-27.md` §1, the per-session entries in
`docs/66-entrant-directive-elections-2026-08-31.md` §8, the provenance blocks heading
`docs/49-block-1C-cr-hessian-2026-08-23.md` §6, `docs/56-s3-analysis-2026-08-24.md` §0,
`docs/70-ideation-holes-spikes-2026-09-02.md` §1 and the `docs/research/` surveys, the disclosures
in `docs/45-error-ledger.md`, the adoption records in `docs/43-prereg-week1-factorial.md`, and
commit messages. **177 candidate entries were checked one by one against their cited lines; 126
were confirmed and 51 were not entered** because the cited line describes adoption, use, execution
or governance rather than production. Each entry below carries the citation that establishes it.
Where the establishing sentence was removed by the 2026-09-03 wording commit `8c41800` ("Remove AI
authorship labels from project documentation", 39 files), the citation reads *"at `8c41800^`"* —
the text is in history and the duty to record it is unchanged
(`docs/43-prereg-week1-factorial.md:3308-3309`). (2) First-hand entries for the sessions of
2026-09-04 and 2026-09-05. **Absence from this list is not a statement that an artefact was written
by the entrant.** It means the repository's own text makes no production statement about it; the
entrant classifies it, by a dated line here, when he does. Entries are appended per artefact,
dated, as produced. Nothing is removed; a correction is a new dated line.

**What was not produced this way** (`docs/43-prereg-week1-factorial.md:1446-1447`): the research
report, the essays and application answers, the six "What did you do" boxes, the disclosures, and
the detector's core — the five module paths that `docs/43-prereg-week1-factorial.md:1840` names,
written and committed only by the entrant. None of those paths appears in this file, and the CI
assertion fails the build if one ever does. Every threshold, election, countersignature and
adoption in the register is the entrant's; the drafts below became registered text only by his
adoption at the cited line.

---

## 1. Tests and fixtures — `docs/43-prereg-week1-factorial.md:1840` "tests and fixtures"

| artefact | establishing line |
|---|---|
| `tests/silentgate/conftest.py` | `tests/silentgate/conftest.py:3-4` |
| `tests/silentgate/test_face_end_to_end.py` | `tests/silentgate/test_face_end_to_end.py:17-18` |
| `tests/silentgate/test_fixture_manifest.py` | `tests/silentgate/test_fixture_manifest.py:15-16` |
| `tests/silentgate/test_gate_fails_closed.py` | `docs/57-s1-ci-handoff-2026-08-27.md:33` |
| `tests/silentgate/test_open_questions.py` (three guards added 2026-09-04) | `tests/silentgate/test_open_questions.py:13-15` |
| `tests/silentgate/spec_rulings.toml` — the seven questions transcribed; the seven rulings are the entrant's elections of 2026-09-04 (`docs/43-prereg-week1-factorial.md:4175-4228`), transcribed | `tests/silentgate/spec_rulings.toml:32-34` |
| `tests/silentgate/fixtures/manifest.toml` — the thirteen fixture choices | `tests/silentgate/fixtures/manifest.toml:39`; `docs/research/ai-survey-2026-08-27/README.md:15` |
| `tests/silentgate/fixtures/fake_census.py` | `tests/silentgate/fixtures/fake_census.py:22-23` |
| `tests/silentgate/fixtures/regenerate_manifest.py` | `tests/silentgate/fixtures/regenerate_manifest.py:21-22` |
| `tests/silentgate/README.md` and the fixture files under `tests/silentgate/fixtures/` | `docs/57-s1-ci-handoff-2026-08-27.md:10-35`; `docs/71-silentgate-core-implementation-brief.md:21-22` |
| `tests/test_verify_dois.py` | 2026-09-04, first-hand |
| `tests/test_mirror_audit.py` | 2026-09-05, first-hand |
| `tests/silentgate/test_preflight.py` | 2026-09-05, first-hand |
| `tests/test_che_box_robustness.py` (33 tests, commit `4a5efad`) and `tests/test_pproj6_shared_box.py` | `tasks/todo.md` 2026-09-05 (session 3) section; first-hand |

## 2. CI — `docs/43-prereg-week1-factorial.md:1840` "the CI workflow"

| artefact | establishing line |
|---|---|
| `.github/workflows/s1-controls.yml` (and its 2026-09-05 edit setting `S1_AI_USE_LOG` to this file) | `.github/workflows/s1-controls.yml:21-25` |
| `.github/ci/run_controls.py` | `.github/ci/run_controls.py:30-31` |
| `.github/ci/run_oc20.py` | `.github/ci/run_oc20.py:38-40` |
| `.github/ci/check_disjoint.py` | `.github/ci/check_disjoint.py:44-46` |
| `.github/ci/core_paths.txt` — transcribed from the registered text | `docs/57-s1-ci-handoff-2026-08-27.md:29` |
| `.github/ci/populations.txt` — transcribed from `docs/43-prereg-week1-factorial.md:1864` | `docs/57-s1-ci-handoff-2026-08-27.md:30` |
| `.github/ci/silentgate-invocation.toml` — the mechanism side only; every value is blank and the entrant declares the interface | `.github/ci/silentgate-invocation.toml:10-11`; `docs/57-s1-ci-handoff-2026-08-27.md:31` |
| `.github/ci/README.md` | `docs/57-s1-ci-handoff-2026-08-27.md:32` |
| the two CI defects the end-to-end tests surfaced, and their fixes | `docs/45-error-ledger.md` S1 CI-defect entry (at `8c41800^`) |
| `.github/ci/preflight_core_commit.py` | 2026-09-05, first-hand |
| `requirements.txt` — the `pymatgen` line (a CI fix) | 2026-09-05, first-hand |
| `.gitattributes` — the `*.lowdin.txt text eol=lf` line | 2026-09-04, first-hand |

## 3. Packaging — `docs/43-prereg-week1-factorial.md:1840` adoption note; ruling `docs/43-prereg-week1-factorial.md:4221`

| artefact | establishing line |
|---|---|
| `pyproject.toml` — metadata, version, entry-point, and the `[build-system]` / package-discovery stanzas the 2026-09-04 ruling elected to keep as they are | `pyproject.toml:3-4`; `docs/57-s1-ci-handoff-2026-08-27.md:36`; `docs/82-spec-rulings-decision-sheet-2026-09-04.md:196-204` |

## 4. Sweeps and surveys — A7.7 "sweeps"

| artefact | establishing line |
|---|---|
| `docs/research/2026-07-24-methodology-survey.md` | `docs/research/2026-07-24-methodology-survey.md:3` |
| `docs/research/2026-07-24-mlip-finetuning-survey.md` | `docs/research/2026-07-24-mlip-finetuning-survey.md:3` |
| `docs/research/2026-07-24-rutile-landscape-stability-survey.md` | `docs/research/2026-07-24-rutile-landscape-stability-survey.md:3` |
| `docs/research/2026-07-24-repo-reconstruction.md` | `docs/research/2026-07-24-repo-reconstruction.md:3` |
| `docs/research/2026-08-11-paywalled-sweep-plan-implications.md` | `docs/43-prereg-week1-factorial.md:923-925` |
| `docs/research/2026-08-15-lit-sweep-lens-digest.md`, `docs/research/2026-08-15-lit-sweep-round1-synthesis.md`, `docs/research/2026-08-15-lit-sweep-round2-synthesis.md` | each file's lines 1-10; `docs/43-prereg-week1-factorial.md:1317-1319` |
| `docs/research/2026-08-15-sampling/` — `t.py`, `t2.py`, `xu_tree.json`, `ruo2_ooh.in`, `ruo2_ooh.out`, `divanis_esi.txt`, the ESI PDF, `SHA256SUMS`: the retained artefacts of the 2026-08-15 sampling act; the header/force sampling script itself was **not** retained | `docs/research/2026-08-15-sampling/README.md:4-6, 17, 28`; `docs/43-prereg-week1-factorial.md:1811-1816` |
| the Xu public-mirror fetch and 20-deck keyword parse of `zhongnanxu/rutile-OER` at c4cb892 | `tasks/todo.md:1514` |
| `docs/research/ai-survey-2026-08-27/` (`sweep.py`, `sweep.json`, `README.md`) — the x-axis sweep disclosed before v0.1 existed | `docs/45-error-ledger.md:1997-2003`; `docs/research/ai-survey-2026-08-27/README.md:12, 21`; `docs/43-prereg-week1-factorial.md:4228-4235` |
| `docs/56-s3-analysis-2026-08-24.md` | `docs/45-error-ledger.md:220-221`; `docs/56-s3-analysis-2026-08-24.md:3-5` |
| `docs/70-ideation-holes-spikes-2026-09-02.md` | `docs/70-ideation-holes-spikes-2026-09-02.md:5-8, 27-35`; `tasks/todo.md:1051, 1098` |
| `docs/73-prediction-ledger-census-2026-09-03.md` | `docs/73-prediction-ledger-census-2026-09-03.md:5`; `tasks/todo.md:1439` |
| `docs/75-novelty-and-placement-2026-09-03.md` | `docs/75-novelty-and-placement-2026-09-03.md:1, 7-9`; `tasks/todo.md:1507` |
| the adversarial audit rounds recorded in the ledgers — the 2026-08-09 verify round (`docs/43-prereg-week1-factorial.md:861-880`), the S3 inventory (`docs/45-error-ledger.md:1750-1758`), the harness audit (`docs/45-error-ledger.md:1946-1950`), wave 4 (`docs/45-error-ledger.md:2303-2307`), wave 5 (`docs/45-error-ledger.md:2373-2376`), the 6-agent verification over docs/64 (`tasks/todo.md:877`), the Amendment 11 / docs/66 passes (`tasks/todo.md:935`) — and their findings files `docs/figs/a0_verification_findings_2026-08-28.txt`, `docs/figs/a0_verification_findings_2026-08-29.txt`, `docs/figs/a0_verification_findings_wave5_2026-08-29.txt` | the lines cited; `docs/figs/a0_verification_findings_wave5_2026-08-29.txt:1-2` |
| `docs/research/2026-09-04-f8-doi-resolution.md`, `docs/figs/f8_doi_resolution.json`, `docs/references.bib` — F8 registrar resolution and the bibliography it built | 2026-09-04, first-hand; commit b6a1c19 |
| `docs/research/2026-09-04-a13r8-staleness-sweep.md` | 2026-09-04, first-hand |
| the Xu `.in` parse of 2026-09-03 — twenty raw `pwscf.in` files (CrO2, MnO2, RuO2, IrO2, TiO2 × bare/*O/*OH/*OOH at U = 3.5 eV) fetched from the GitHub mirror `zhongnanxu/rutile-OER` at commit `c4cb892605` together with the recursive tree, and read for `nspin`, `tot_magnetization`, `U_projection_type`, the `&ELECTRONS` namelist, `calculation`, `nosym` and the selective-dynamics flags. Inputs only: no output file was opened, no total energy read, no census number formed. Disclosed under the `docs/43-prereg-week1-factorial.md:1811` precedent as a pre-registration observation, not the entrant's census | `docs/75-novelty-and-placement-2026-09-03.md:26-62`; `docs/78-action-board-2026-09-03.md:55`; `docs/43-prereg-week1-factorial.md` dated disclosure 2026-09-05 |

## 5. Amendment drafts — A7.7 "amendment drafts"

Each was drafted as disclosed research infrastructure under A7.7 and became registered text only
by the entrant's adoption, recorded at the cited line.

| artefact | establishing line |
|---|---|
| AMENDMENT 7 as drafted — "drafted at the entrant's direction (2026-08-16) and is recorded as such in the provenance record" | `docs/43-prereg-week1-factorial.md:1320-1323` |
| `docs/47-amendment-8-DRAFT.md` (A8) | `docs/43-prereg-week1-factorial.md:1469-1471`; `docs/47-amendment-8-DRAFT.md:5` |
| `docs/50-amendment-9-DRAFT.md` (A9), "drafted 2026-08-22-23, three-lens critique applied" | `docs/43-prereg-week1-factorial.md:1778-1780` |
| AMENDMENT 9 as adopted, and the correction of record withdrawing the §6 z-gate | `docs/43-prereg-week1-factorial.md:1791-1792` |
| the adoption-verification edits to `docs/43-prereg-week1-factorial.md` (9 insertions / 6 deletions) | commit 1c09c38 |
| `docs/61-amendment-11-DRAFT.md` (A11), the consolidated A11 text, the P-DISPOSITION addendum, docs/67, the docs/59 licence line | `docs/43-prereg-week1-factorial.md:2016-2020`; `docs/66-entrant-directive-elections-2026-08-31.md:176-181` |
| `docs/74-amendment-10-DRAFT.md` (A10 — a draft; NOT ADOPTED, NOT DEPOSITED) | `docs/74-amendment-10-DRAFT.md:3-10` |
| `docs/77-amendment-12-pproj6-DRAFT.md` (A12 / A12b) | `docs/43-prereg-week1-factorial.md:3333-3336` |
| the scribe-written dated addenda in the register — `[AFM-SCOPE RESOLVED 2026-08-30]`, the P-DISPOSITION date amendment, the 2026-09-03 nine-item directive lines — "the decision his, this text the scribe's" | `docs/43-prereg-week1-factorial.md:1980-1981, 2254-2255, 2598-2601` |
| the dated addenda of 2026-09-04 in `docs/43-prereg-week1-factorial.md:4001-4235` (A12.R11 and A13.R8 entering the register, the A6.5(1) closure, the Ni repair-deck correction, the seven ruling lines) — drafted as transcription; every election and countersignature in them is the entrant's | 2026-09-04, first-hand |
| the dated addendum of 2026-09-05 in `docs/43-prereg-week1-factorial.md` (OC20 asset, mirror audit, this record) | 2026-09-05, first-hand |
| `docs/88-a10-signature-sheet-2026-09-05.md` (A10 signature sheet — every slot is the entrant's) | 2026-09-05, first-hand |
| `docs/89-ru-pseudopotential-control-DRAFT.md` (a draft; NOT ADOPTED, NOT LICENSED) | 2026-09-05, first-hand |

## 6. Critique and decision sheets — A7.7 "critique"

| artefact | establishing line |
|---|---|
| `docs/49-block-1C-cr-hessian-2026-08-23.md` (banking block) | `docs/49-block-1C-cr-hessian-2026-08-23.md:179, 277` (at `8c41800^`) |
| `docs/51-anvil-queue-triage-2026-08-23.md` | `docs/51-anvil-queue-triage-2026-08-23.md:4-7` |
| `docs/52-decision-sheet-2026-08-23.md` | `docs/52-decision-sheet-2026-08-23.md:3` |
| the CONFIRMED_CUS classification in `docs/53-mom2014-a75-sno2-verification-2026-08-23.md` §4.1, disclosed as a tool classification | `docs/52-decision-sheet-2026-08-23.md:411` |
| `docs/54-s3-deck-matrix-2026-08-23.md` | commit 3cbd192 |
| `docs/55-decision-sheet-2026-08-24.md` | `docs/55-decision-sheet-2026-08-24.md:10-12` |
| `docs/57-s1-ci-handoff-2026-08-27.md` | `docs/57-s1-ci-handoff-2026-08-27.md:10-12, 20-21` |
| `docs/65-decision-sheet-2026-08-31.md` and the 2026-08-31 launch-readiness deliverables | `docs/65-decision-sheet-2026-08-31.md:10-11`; `tasks/todo.md:918` |
| `docs/66-entrant-directive-elections-2026-08-31.md` — the directive of record is the entrant's; the document and its §8 entries are drafted | `docs/66-entrant-directive-elections-2026-08-31.md:3` (at `8c41800^`), `:176-181` |
| `docs/70-ideation-holes-spikes-2026-09-02.md` §8, the completeness critique | `docs/70-ideation-holes-spikes-2026-09-02.md:834-840` |
| `docs/71-silentgate-core-implementation-brief.md` — specification and review only; contains no implementation code | `docs/71-silentgate-core-implementation-brief.md:3-8` |
| `docs/80-own-u-arm-killtest-2026-09-04.md` | `docs/80-own-u-arm-killtest-2026-09-04.md:8-10`; `tasks/todo.md:1665-1667` |
| `docs/82-spec-rulings-decision-sheet-2026-09-04.md`, `docs/85-ruling-signature-sheet-2026-09-04.md`, `docs/86-divanis-decision-sheet-2026-09-04.md` — decision sheets; every election on them is the entrant's | `docs/43-prereg-week1-factorial.md:4159-4164`; 2026-09-04, first-hand |
| `docs/87-claim-sentence-constraints-2026-09-05.md` | 2026-09-05, first-hand |

## 7. Scaffolding scripts and built inputs — A7.7 "scaffolding"

| artefact | establishing line |
|---|---|
| the `anvil/` submit and parity shell scripts (`anvil/*.sh`, `anvil/*.slurm`) | `anvil/README.md:124` (at `8c41800^`; now "supporting infrastructure and must be disclosed as such") |
| `src/dft/s3_readout.py`, `src/dft/s3_nonadditivity.py`, `src/dft/s3_confound_check.py`, `src/dft/p_symcov_score.py` | `docs/45-error-ledger.md:220-224`; `src/dft/s3_readout.py:4`; `src/dft/s3_confound_check.py:4`; `src/dft/p_symcov_score.py:231, 442` |
| `src/dft/lit2_readout.py` | `src/dft/lit2_readout.py:41-42` |
| `src/dft/build_a0main_w2c.py` | `src/dft/build_a0main_w2c.py:132-135` |
| the S3 wave-1 deck tree (46 production-seed relax + 9 SCFs) and the wave-2 tree (37 `__g1` children + 19 Cr re-Hessian SCF decks under `runs/s3/`), built via workflows | `tasks/todo.md:522, 553`; commit 6e7be4c |
| the Stage-1/probe/CMF/Family-C/Mn builders and their manifests; the pipeline-guard code; the Zenodo deposit mechanics | `docs/66-entrant-directive-elections-2026-08-31.md:176-181` |
| `src/lit/verify_dois.py` | 2026-09-04, first-hand; commit b6a1c19 |
| `src/dft/gate1_census.py` — the `--asof` argument (the edit only; the file's origin is not stated in the repository) | 2026-09-04, first-hand |
| `src/dft/mirror_audit.py` | 2026-09-05, first-hand |
| `src/dft/build_hp_cro2_q333.py` and the four decks + manifest under `runs/hp_cro2_q333/` | 2026-09-05, first-hand; commit ca5b33e |
| `src/dft/build_eproj_np128.py`, `runs/a0/eproj_np128/` (two byte-identical copies) and `runs/a0/m_eproj_np128.txt` | 2026-09-05, first-hand; commit ca5b33e |
| `src/dft/build_s5.py` and the S5 deck tree under `runs/s5/` (NOT LICENSED) | 2026-09-05, first-hand |
| `src/dft/build_ru_pp.py`, the twelve decks under `runs/a0/ru_pp/` (NOT LICENSED) and `runs/a0/ru_pp/PSEUDO_PROVENANCE.md` | 2026-09-05, first-hand |
| `src/dft/hp_cro2_q333_readout.py`, `src/dft/eproj_np128_readout.py` and `tests/test_small_arms_readouts.py` (scorers committed before their outputs landed) | 2026-09-05, first-hand; commit b502beb |
| `src/dft/build_h_afm_relax.py` — the `--out-dir` argument (the edit only) and the matching test change | 2026-09-05, first-hand; commit f5d2f7d |
| `src/dft/che_box_robustness.py`, `src/dft/che_robustness_case_study.py`, the 2026-09-05 edit of `src/dft/zpe_decomposition.py` (the `main()` envelope and the `--delta` guard only; `docs/figs/zpe_decomposition.json` untouched) and `results/che_box_case_study_2026-09-05/` (audit, verification and zpe_continuous_check JSON, PNG, SVG) | commit `4a5efad`; `docs/84-pproj-cell-readout-2026-09-04.md:206-213`; `docs/81-zpe-decomposition-of-a71-2026-09-04.md` dated addendum 2026-09-05 (session 3) |
| `src/dft/pproj6_shared_box.py` and `docs/figs/pproj6_shared_box.json` | first-hand; `docs/83-pproj6-readout-2026-09-04.md` dated addendum 2026-09-05 (session 3) |
| *(dated correction 2026-09-06 to the two rows of 2026-09-05 above)* the 2026-09-05 edit of `src/dft/zpe_decomposition.py` is the `main()` envelope, a `--delta` guard with its import, the robustness and summary wording, and two JSON keys — not "only" the first two; `src/dft/pproj6_shared_box.py`, `docs/figs/pproj6_shared_box.json`, `tests/test_pproj6_shared_box.py` and the docs/83 session-3 addendum entered at commit `13268da`, and the JSON's recorded hashes were re-taken over CRLF-normalised bytes at `6172d2f` | `git show 4a5efad -- src/dft/zpe_decomposition.py`; `git show --stat 13268da`; first-hand |

## 8. Ledger and prose infrastructure

| artefact | establishing line |
|---|---|
| `docs/45-error-ledger.md` — its agent-audit sections and the 2026-09-03 ledger-maintenance block; the ledger's governance line describes the whole file as the research-infrastructure view the entrant re-authors before deposit | `docs/45-error-ledger.md:61-63, 1750, 1948, 2373, 3117` (at `8c41800^`) |
| `tasks/todo.md` and `tasks/lessons.md` — the entries dated 2026-09-04 and 2026-09-05 | first-hand |
| the release notes of GitHub release `oc20-val_id-first500` | 2026-09-05, first-hand |
| `docs/provenance-record.md` — this file | 2026-09-05, first-hand |
| the dated addendum of 2026-09-05 (session 2) in `docs/43-prereg-week1-factorial.md:4341-4418` — transcription of four elections and three adoptions from the entrant's instruction; the :4334 slot filled in place | 2026-09-05, first-hand; commit a8c3218 |
| the ordering line in `docs/45-error-ledger.md` section D dated 2026-09-05, and the filled Ruling 1 slot in `docs/86-divanis-decision-sheet-2026-09-04.md` — transcriptions | 2026-09-05, first-hand; commit a8c3218 |
| `tasks/todo.md` — the entries dated 2026-09-05 (session 2) | first-hand |
| `docs/84-pproj-cell-readout-2026-09-04.md` — the dated addendum of 2026-09-05 (the U of each number) | 2026-09-05, first-hand |
| `docs/83-pproj6-readout-2026-09-04.md` — the dated addendum of 2026-09-05 (the cell of every deck) | 2026-09-05, first-hand |
| `docs/75-novelty-and-placement-2026-09-03.md` — the dated addendum of 2026-09-05 (lines 85-90 superseded) | 2026-09-05, first-hand |
| `docs/76-projector-generalization-decision-2026-09-03.md` — the dated addendum of 2026-09-05 (section 5 superseded) | 2026-09-05, first-hand |
| `docs/research-assessment-2026-09-05.md` (commit `4a5efad`) and its dated corrections addendum; the dated correction at `docs/84-pproj-cell-readout-2026-09-04.md:162-219` (commit `4a5efad`) and the dated pointer below it; the dated addenda of 2026-09-05 (session 3) in `docs/81-zpe-decomposition-of-a71-2026-09-04.md`, `docs/83-pproj6-readout-2026-09-04.md` and `docs/87-claim-sentence-constraints-2026-09-05.md`, each carrying a blank countersignature slot or none; the `tasks/todo.md` and `tasks/lessons.md` entries of 2026-09-05 15:31 and (session 3) | commit `4a5efad`; first-hand |
| *(dated correction 2026-09-06 to the session-3 row above)* the session-3 addenda entered at `13268da` (docs/83) and `376a3c7` (docs/81, docs/84, docs/87, the assessment's corrections); dated corrections of the same evening exist under the docs/81 and docs/83 addenda and under the assessment's (`b7d5228`), and none under docs/84 or docs/87. **`b7d5228` rewrote the zpe-edit row of section 7 and the session-3 row of this section in place**, against :33-34 of this file ("Nothing is removed; a correction is a new dated line"); the commit that adds this line restores both rows to their `376a3c7` text, and the amended wording lives in these two dated rows instead | `git diff 376a3c7 b7d5228 -- docs/provenance-record.md`; first-hand |

## 9. Owed, not yet written

| entry owed | where the obligation is recorded |
|---|---|
| *(discharged 2026-09-05 — entered in section 4)* the disclosure line for the Xu `.in` parses of the docs/78 review round | `docs/78-action-board-2026-09-03.md:55` |

---

## Not entered, and why

Fifty-one candidates were checked and not entered because the line offered for them describes
adoption, use, execution or governance rather than production — among them the entrant's review
of `docs/52-decision-sheet-2026-08-23.md`, `anvil/rcac_ticket_draft_2026-08-24.md`, the A11.R7
readout script `src/dft/a0lowdin_valence.py`, `docs/76-projector-generalization-decision-2026-09-03.md`,
and the pre-2026-08-23 code under `src/` generally. The entrant may enter any of them with a dated
line. Until he does, this file says nothing about them either way — see "what absence means" above.

| `tasks/todo.md` — the 2026-09-06 "Current-session assessment and next-step review" block | repository, recent session records, raw small-arm outputs, and independent analytical review; first-hand |
