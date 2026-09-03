# 2026-08-15 pre-registration sampling — the retained artefacts

**Filed 2026-08-23 under the obligation in docs/50 (Amendment 9 draft) §A9.0 item 3.**
These are the files an AI literature-sweep agent produced or fetched on 2026-08-15 (session
`e1d7c42a`, scratchpad) while sampling the Xu/Rossmeisl/Kitchin rutile-OER deposit and the
Divanis ESI *before* Amendment 9 was written. They are filed so that the disclosure of that
sampling in A9.0 does not depend on a temp directory surviving, and so that every count A9
quotes "per the GitHub mirror at c4cb892" can be re-derived. **They are pre-registration
observations, not results.** Nothing here is re-read by anyone before A9's DOI line exists
(docs/50 §A9.6, last two bullets).

| file | bytes | sha256 | what it is | licence / source |
|---|---|---|---|---|
| `xu_tree.json` | 2,663,448 | `d20af9db…c957e8b9` | GitHub API recursive tree of `zhongnanxu/rutile-OER` at commit `c4cb89260586229f6a007072ca9e4eeed545d622` — paths, sizes, blob SHA-1s; **no file content**. 8,247 entries, 6,989 blobs, 815 `pwscf.in` + 815 `pwscf.out` | listing of a CC-BY-4.0 mirror of 10.5281/zenodo.12635 (CC0) |
| `ruo2_ooh.in` | 2,543 | `447b73e3…8a1dc0e8` | the one Xu deck read in full: `RuO2/Eads-4-layers/OOH-relax/pwscf.in` (nat 51, nspin 1, U 0, no `forc_conv_thr`) | Xu et al. 2015, 10.1021/jp511426q; data CC0 (Zenodo) / CC-BY-4.0 (mirror) — attributed either way |
| `ruo2_ooh.out` | 1,328,638 | `2b9bc0dd…4814ad3e6c620` | the one Xu output cached locally: the matching `pwscf.out` (17 force blocks, header `2 Sym. Ops. (no inversion) found`). Whether its force blocks were looked at on 2026-08-15 is not recorded → RuO₂ *OOH is "blind by record, not by availability" (A9.3.2) | same |
| `t.py`, `t2.py` | 1,285 / 2,274 | see SHA256SUMS | the pymatgen `AdsorbateSiteFinder` census scripts run OUTSIDE the repo on a hand-built RuO₂(110) slab (the non-blind rutile arm of P-BUILDER); `t2.py` is the one whose exact arguments A9.3.5 registers | documented, 2026-08-15 |
| `divanis_esi.txt` | 34,094 | `88bfcda9…d9a74b42c0bd8bda` | text extraction of the Divanis et al. 2020 ESI used for the correction-row facts in A9.3.4 | derivative of the ESI below |
| `SC-011-C9SC05897D-s001.pdf` | 3,557,937 | `348462f7…08d5adc02a` | the ESI itself, Divanis et al., *Chem. Sci.* 2020, 10.1039/C9SC05897D | RSC, Chemical Science (open access, CC-BY); filed so "on disk" means a repo path |

Full hashes: `SHA256SUMS` in this directory. Not filed (hashes recorded only): the raw
supplementary zip the ESI came from (`supp.zip`, 4,269,594 bytes, sha256
`1139c838eefd27fba6032a6830c0b46ccab163f961c47afb2c5650392a04721e`) and the Man 2011 text
extraction (`man2011.txt`, 38,084 bytes, sha256
`e9df2ccf561a4aa6ab83a60ac8751a342dadc1e72a3bc7edaf005b1aac8cdc14`; the PDF is already in
`docs/research/papers/`).

**What the 2026-08-15 agent did NOT retain:** the header/force sampling script (40 of 810
headers, 12 of 810 final-step force blocks) and any results file. The only record of those
numbers is prose in `docs/research/2026-08-15-lit-sweep-lens-digest.md` (:253-261,
:297-303, :314), quoted in A9.0.
