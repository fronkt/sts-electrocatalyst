# Pseudo md5 preflight — A8.5 byte-identity discharge for the S3 metals, 2026-08-23

A8.5 (deposited, DOI 10.5281/zenodo.22072991) requires the pseudopotentials to be
"byte-identical (md5 verified on both ends)". The Vast box is destroyed, but every banked
`.out` prints per-pseudo `MD5 check sum` lines — the pre-destruction hashes are in the
banked record. Verification = those lines vs `md5sum` on `$PROJECT/pseudo/` (Anvil),
run 2026-08-23. The S3-matrix verifier (wf_fc7261af) flagged Mn/Fe/Co/Ni/Ir as
never-exercised on Anvil; all five are covered below.

| species | UPF on Anvil | banked-output md5 (source) | Anvil md5 | verdict |
|---|---|---|---|---|
| Cr | cr_pbe_v1.5.uspp.F.UPF | 0d52af634a40206e4dee301ad30da4bf (runs/Cr_slab/s0_OOH.out) | 0d52af634a40206e4dee301ad30da4bf | MATCH |
| Mn | mn_pbe_v1.5.uspp.F.UPF | 82ef2b46521d7a7d9e736dc3972e4928 (runs/Mn_slab/s0_OOH.out) | 82ef2b46521d7a7d9e736dc3972e4928 | MATCH |
| Fe | Fe.pbe-spn-kjpaw_psl.0.2.1.UPF | e86618425769142926afa95317d90200 (runs/Fe_slab/s0_OOH.out) | e86618425769142926afa95317d90200 | MATCH |
| Co | Co_pbe_v1.2.uspp.F.UPF | 5f91765df6ddd3222702df6e7b74a16d (runs/Co_slab/s0_OH.out) | 5f91765df6ddd3222702df6e7b74a16d | MATCH |
| Ni | ni_pbe_v1.4.uspp.F.UPF | 1ee80287db30b12d2bc1f57a5b5d6409 (runs/Ni_slab/s0_OH.out) | 1ee80287db30b12d2bc1f57a5b5d6409 | MATCH |
| Ru | Ru_ONCV_PBE-1.0.oncvpsp.upf | be037bb81c227cfb9b1461a9f099f4bd (runs/Ru_anchor/s0_OOH.out) | be037bb81c227cfb9b1461a9f099f4bd | MATCH |
| Ir | Ir_pbe_v1.2.uspp.F.UPF | 8836f839c3459d2b385c504ce6d91f2c (runs/Ir_anchor/s0_O.out) | 8836f839c3459d2b385c504ce6d91f2c | MATCH |
| O | O.pbe-n-kjpaw_psl.0.1.UPF | 0234752ac141de4415c5fc33072bef88 (every banked deck) | 0234752ac141de4415c5fc33072bef88 | MATCH |
| H | H.pbe-rrkjus_psl.1.0.0.UPF | f52b6d4d1c606e5624b1dc7b2218f220 (runs/Mn_slab/s0_OH.out) | f52b6d4d1c606e5624b1dc7b2218f220 | MATCH |
| Ti | ti_pbe_v1.4.uspp.F.UPF | 88a00a6731bd790ddea75d31a80cb452 (anvil/README.md:196, cross-checked at staging; exercised by gate (g)/(i)) | 88a00a6731bd790ddea75d31a80cb452 | MATCH |
| Sn | Sn_pbe_v1.uspp.F.UPF | 4cf58ce39ec5d5d420df3dd08604eb00 (anvil/README.md:200-206; exercised by job 20094699) | 4cf58ce39ec5d5d420df3dd08604eb00 | MATCH |
| Cu | Cu.paw.z_11.ld1.psl.v1.0.0-low.upf | — no banked Cu output exists to compare against | 619f40885d92a09a85a8b37550532d0c | PRESENT, UNVERIFIABLE against banked record, UNUSED (Cu is a GAP column, docs/54 §2.9). Note: docs/51:24 / docs/54:288 say the Cu PAW "is not among the 12 staged UPFs" — as of this check a Cu PAW IS present on Anvil (13 files in $PROJECT/pseudo). The GAP disposition is unchanged (registration, not staging, excludes Cu). |

**Verdict: every UPF an S3 wave-1 deck reads is byte-identical to the pseudo the banked
record was produced with. The A8.5 pseudo precondition is discharged for the S3 build.**
Method: `grep "MD5 check sum"` on banked outputs (pw.x prints the hash of the file it
actually read) vs `md5sum $PROJECT/pseudo/*` — zero new compute.
