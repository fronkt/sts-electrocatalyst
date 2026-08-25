# A8.1 non-additivity bins — S3 crossed factorial (2026-08-24)

Input: `runs/s3/readout/s3_readout_2026-08-24.json` (sha256 `6ae13a51aaf0009f...`). Machine-readable twin: `nonadditivity_2026-08-24.json`. No existing file modified.

## Registered rules applied (quoted authorities)

- **quantity_and_bin**: docs/43-prereg-week1-factorial.md:1523-1525 (DEPOSITED, 'THRESHOLD (adopted as proposed, 2026-08-23)'): NON-ADDITIVE where |E(both)-E(cell)-E(sym)+E(neither)| exceeds 0.10 eV; the <=0.10 eV side carries NO deposited label
- **corner_mapping**: docs/54-s3-deck-matrix-2026-08-23.md:37-40 (INFRASTRUCTURE, not registration): N=1x1 mir, S=1x1 off, C=2x1v mir, B=2x1v off; bares (ref) are not corners; 'at fixed basin' gloss docs/54:20-21
- **algebraic_identity**: docs/43:169 — the double difference equals deltaE_sym(2x1v) - deltaE_sym(1x1), block 1A's I
- **parallel_1a_ladder**: docs/43:171-176 (DEPOSITED, prior scheme; inherited verbatim by A6.2, docs/43:1216-1220): <0.05 additive / 0.05-0.30 inconclusive / >=0.30 not separable — supersession vs coexistence with A8.1 is NOT registered, both reported
- **confound**: docs/43:1566-1571 (DEPOSITED): pair members differing >0.05 uB total magnetisation are CONFOUNDED, excluded from contrast statistics, reported separately; applied to same-coverage symmetry edges per docs/54:55-58; whether a CONFOUNDED pair voids the A8.1 row is UNSTATED
- **pending_dual_quote**: docs/55 R1 (binding): Fe s0_OOH__1x1_off and Mn s0_OOH__2x1v_off quote parent AND child, bank neither as final
- **energy_of_record**: docs/52 C9 (GATE-1 AGREE rows quote the CHILD) + docs/54 row->file matrix + docs/55 R3 (Cr *OOH 2x1v mir = escape minimum; mirror value is a SADDLE diagnostic)

## Interaction table

I = E(B) − E(C) − E(S) + E(N), Ry → eV ×13.605693. A8.1 bin: NON-ADDITIVE iff |I| > 0.10 eV (docs/43:1523-1525). 1A ladder shown in parallel (docs/43:171-176) — coexistence unresolved, flagged for entrant.

| Metal | State | Reading | I (Ry) | I (eV) | A8.1 bin | 1A ladder | Row tag |
|---|---|---|---|---|---|---|---|
| Cr | *O | energy-of-record | +0.00001812 | +0.000247 | <=0.10 eV (no deposited label) | additive (<0.05) | definitive |
| Cr | *OH | energy-of-record | -0.01200190 | -0.163294 | NON-ADDITIVE | inconclusive (0.05-0.30) | definitive |
| Cr | *OOH | energy-of-record | +0.00954877 | +0.129918 | NON-ADDITIVE | inconclusive (0.05-0.30) | definitive |
|  |  | INFORMATIONAL — ALT member: production runs/Cr_slab/s0_OOH.out (member identity OPEN, docs/54:150, :400-405) | +0.02267364 | +0.308491 | NON-ADDITIVE | not separable (>=0.30) | definitive |
| Mn | *O | energy-of-record | +0.00365624 | +0.049746 | <=0.10 eV (no deposited label) | additive (<0.05) | definitive |
| Mn | *OH | energy-of-record | -0.00316559 | -0.043070 | <=0.10 eV (no deposited label) | additive (<0.05) | definitive |
| Mn | *OOH | reading with B = parent (runs/s3/Mn/s0_OOH__2x1v_off.out = -3617.09868891 Ry) — docs/55 R1 dual quote, NOT banked | -0.02580248 | -0.351061 | NON-ADDITIVE | not separable (>=0.30) | PENDING-RERELAX (docs/55 R1: quote parent AND child, bank neither) |
|  |  | reading with B = child (runs/s3/Mn/s0_OOH__2x1v_off__g1.out = -3617.10020414 Ry) — docs/55 R1 dual quote, NOT banked | -0.02731771 | -0.371676 | NON-ADDITIVE | not separable (>=0.30) | PENDING-RERELAX (docs/55 R1: quote parent AND child, bank neither) |
| Fe | *O | energy-of-record | +0.00811511 | +0.110412 | NON-ADDITIVE | inconclusive (0.05-0.30) | definitive |
| Fe | *OH | energy-of-record | -0.01254337 | -0.170661 | NON-ADDITIVE | inconclusive (0.05-0.30) | definitive |
| Fe | *OOH | reading with S = parent (runs/s3/Fe/s0_OOH__1x1_off.out = -2558.13528265 Ry) — docs/55 R1 dual quote, NOT banked | -0.05326708 | -0.724736 | NON-ADDITIVE | not separable (>=0.30) | PENDING-RERELAX (docs/55 R1: quote parent AND child, bank neither) |
|  |  | reading with S = child (runs/s3/Fe/s0_OOH__1x1_off__g1.out = -2558.16352817 Ry) — docs/55 R1 dual quote, NOT banked | -0.02502156 | -0.340436 | NON-ADDITIVE | not separable (>=0.30) | PENDING-RERELAX (docs/55 R1: quote parent AND child, bank neither) |
| Co | *O | — | — | — | — | — | NOT COMPUTABLE (S:UNVERIFIED, C:PENDING-RETRY) |
| Co | *OH | — | — | — | — | — | NOT COMPUTABLE (S:PENDING-RETRY, C:PENDING-RETRY, B:PENDING-RETRY) |
| Co | *OOH | — | — | — | — | — | NOT COMPUTABLE (N:GAP, S:ABSENT (no such cell in readout), C:PENDING-RETRY, B:PENDING-RETRY) |
| Ni | *O | — | — | — | — | — | NOT COMPUTABLE (S:UNCLASSIFIED) |
| Ni | *OH | — | — | — | — | — | NOT COMPUTABLE (B:UNVERIFIED) |
| Ni | *OOH | — | — | — | — | — | NOT COMPUTABLE (N:GAP, S:ABSENT (no such cell in readout), C:PENDING-RETRY, B:PENDING-RETRY) |
| Ru | *O | energy-of-record | -0.00007019 | -0.000955 | <=0.10 eV (no deposited label) | additive (<0.05) | definitive |
| Ru | *OH | energy-of-record | -0.01724111 | -0.234577 | NON-ADDITIVE | inconclusive (0.05-0.30) | definitive |
| Ru | *OOH | energy-of-record | -0.00198969 | -0.027071 | <=0.10 eV (no deposited label) | additive (<0.05) | definitive |
|  |  | INFORMATIONAL — ALT member: oosh conformer, lowest banked (oosh-member question OPEN, docs/54:249, :422-424) | +0.00620467 | +0.084419 | <=0.10 eV (no deposited label) | inconclusive (0.05-0.30) | definitive |
| Ir | *O | energy-of-record | -0.00005789 | -0.000788 | <=0.10 eV (no deposited label) | additive (<0.05) | definitive |
| Ir | *OH | energy-of-record | -0.00315531 | -0.042930 | <=0.10 eV (no deposited label) | additive (<0.05) | definitive |
| Ir | *OOH | energy-of-record | +0.01956116 | +0.266143 | NON-ADDITIVE | inconclusive (0.05-0.30) | definitive |
|  |  | INFORMATIONAL — ALT member: oosh conformer (oosh-member question OPEN, docs/54:264, :422-424) | +0.02147659 | +0.292204 | NON-ADDITIVE | inconclusive (0.05-0.30) | definitive |
| Ti | *O | — | — | — | — | — | NOT COMPUTABLE (N:ABSENT (no such cell in readout), S:ABSENT (no such cell in readout)) |
| Ti | *OH | — | — | — | — | — | NOT COMPUTABLE (N:ABSENT (no such cell in readout), S:ABSENT (no such cell in readout)) |
| Ti | *OOH | — | — | — | — | — | NOT COMPUTABLE (N:ABSENT (no such cell in readout), S:ABSENT (no such cell in readout)) |

## Bin populations (energy-of-record readings on definitive rows only)

- **A8.1 NON-ADDITIVE (>0.10 eV)**: 6 — Cr *OH (-0.1633 eV); Cr *OOH (+0.1299 eV); Fe *O (+0.1104 eV); Fe *OH (-0.1707 eV); Ir *OOH (+0.2661 eV); Ru *OH (-0.2346 eV)
- **A8.1 <=0.10 eV (no deposited label)**: 7 — Cr *O (+0.0002 eV); Ir *O (-0.0008 eV); Ir *OH (-0.0429 eV); Mn *O (+0.0497 eV); Mn *OH (-0.0431 eV); Ru *O (-0.0010 eV); Ru *OOH (-0.0271 eV)
- **1A ladder (parallel)**: additive 7 (Cr *O, Ir *O, Ir *OH, Mn *O, Mn *OH, Ru *O, Ru *OOH); inconclusive 6 (Cr *OH, Cr *OOH, Fe *O, Fe *OH, Ir *OOH, Ru *OH); not separable 0
- **PENDING dual readings (docs/55 R1, neither banked)**: Mn *OOH (both readings: NON-ADDITIVE); Fe *OOH (both readings: NON-ADDITIVE)
- **Not computable**: 9 — Co *O, Co *OH, Co *OOH, Ni *O, Ni *OH, Ni *OOH, Ti *O, Ti *OH, Ti *OOH

## Per-row confound edges and flags

### Cr *O
- edge N-S (1x1 sym pair): ΔM = 0.0 uB — within 0.05 uB
- edge C-B (2x1v sym pair): ΔM = 0.0 uB — within 0.05 uB
- edge cross-coverage edges (N-C, S-B): ΔM = n/a — NOT EVALUATED — members have different atom counts; no registered raw-total-M normalisation exists (spec ambiguity: A8.3 contrast enumeration unstated)
- FLAG: Cr/Mn k-bridge (docs/54:41-43, infrastructure): 1x1<->2x1v corner comparisons carry an unapplied k-bridge correction; whether it cancels inside the double difference is an interpretation, not a registration — value computed uncorrected

### Cr *OH
- edge N-S (1x1 sym pair): ΔM = 0.0 uB — within 0.05 uB
- edge C-B (2x1v sym pair): ΔM = 0.0 uB — within 0.05 uB
- edge cross-coverage edges (N-C, S-B): ΔM = n/a — NOT EVALUATED — members have different atom counts; no registered raw-total-M normalisation exists (spec ambiguity: A8.3 contrast enumeration unstated)
- FLAG: corner S: docs/54 designates its pair CONFOUNDED — docs/54:147 (corner S; 1x1 pair CONFOUNDED per docs/43:1566-1571)
- FLAG: Cr/Mn k-bridge (docs/54:41-43, infrastructure): 1x1<->2x1v corner comparisons carry an unapplied k-bridge correction; whether it cancels inside the double difference is an interpretation, not a registration — value computed uncorrected

### Cr *OOH
- edge N-S (1x1 sym pair): ΔM = 0.0 uB — within 0.05 uB
- edge C-B (2x1v sym pair): ΔM = 0.0 uB — within 0.05 uB
- edge cross-coverage edges (N-C, S-B): ΔM = n/a — NOT EVALUATED — members have different atom counts; no registered raw-total-M normalisation exists (spec ambiguity: A8.3 contrast enumeration unstated)
- FLAG: docs/54:152 designated the 2x1v symmetry pair CONFOUNDED (Delta_sym 1.188 eV) with the MIRROR SADDLE as member; docs/55 R3 (binding) since made the escape minimum the C-corner record, and escape-vs-off DeltaM = 0.0 uB — whether the CONFOUNDED designation carries to the post-R3 pair is an entrant call, NOT resolved here
- FLAG: corner N: member identity OPEN — which file is the 1x1-mir production-seed MEMBER is unresolved (docs/54:400-405); pair CONFOUNDED either way — entrant's call, NOT resolved here
- FLAG: Cr/Mn k-bridge (docs/54:41-43, infrastructure): 1x1<->2x1v corner comparisons carry an unapplied k-bridge correction; whether it cancels inside the double difference is an interpretation, not a registration — value computed uncorrected
- FLAG: corner N member question OPEN — informational alternate computed, never binned; the call is the entrant's

### Mn *O
- edge N-S (1x1 sym pair): ΔM = 0.0 uB — within 0.05 uB
- edge C-B (2x1v sym pair): ΔM = 0.0 uB — within 0.05 uB
- edge cross-coverage edges (N-C, S-B): ΔM = n/a — NOT EVALUATED — members have different atom counts; no registered raw-total-M normalisation exists (spec ambiguity: A8.3 contrast enumeration unstated)
- FLAG: corner N: nosym ON_PLANE — whether this row stands as a mirror member is OPEN (docs/54:406-411, section 6 item 5)
- FLAG: Cr/Mn k-bridge (docs/54:41-43, infrastructure): 1x1<->2x1v corner comparisons carry an unapplied k-bridge correction; whether it cancels inside the double difference is an interpretation, not a registration — value computed uncorrected

### Mn *OH
- edge N-S (1x1 sym pair): ΔM = 0.01 uB — within 0.05 uB
- edge C-B (2x1v sym pair): ΔM = 0.0 uB — within 0.05 uB
- edge cross-coverage edges (N-C, S-B): ΔM = n/a — NOT EVALUATED — members have different atom counts; no registered raw-total-M normalisation exists (spec ambiguity: A8.3 contrast enumeration unstated)
- FLAG: corner N: nosym EXPLORED — mirror-member standing OPEN (docs/54:406-411, section 6 item 5)
- FLAG: Cr/Mn k-bridge (docs/54:41-43, infrastructure): 1x1<->2x1v corner comparisons carry an unapplied k-bridge correction; whether it cancels inside the double difference is an interpretation, not a registration — value computed uncorrected

### Mn *OOH
- edge N-S (1x1 sym pair): ΔM = 0.0 uB — within 0.05 uB
- edge C-B (2x1v sym pair): ΔM = n/a — NOT EVALUABLE (a member has no M: nspin=1 row or pending cell)
- edge cross-coverage edges (N-C, S-B): ΔM = n/a — NOT EVALUATED — members have different atom counts; no registered raw-total-M normalisation exists (spec ambiguity: A8.3 contrast enumeration unstated)
- FLAG: corner N: nosym EXPLORED — mirror-member standing OPEN (docs/54:406-411, section 6 item 5)
- FLAG: Cr/Mn k-bridge (docs/54:41-43, infrastructure): 1x1<->2x1v corner comparisons carry an unapplied k-bridge correction; whether it cancels inside the double difference is an interpretation, not a registration — value computed uncorrected

### Fe *O
- edge N-S (1x1 sym pair): ΔM = 0.0 uB — within 0.05 uB
- edge C-B (2x1v sym pair): ΔM = 0.0 uB — within 0.05 uB
- edge cross-coverage edges (N-C, S-B): ΔM = n/a — NOT EVALUATED — members have different atom counts; no registered raw-total-M normalisation exists (spec ambiguity: A8.3 contrast enumeration unstated)
- FLAG: corner N: nosym ON_PLANE — mirror-member standing OPEN (docs/54:406-411, section 6 item 5)

### Fe *OH
- edge N-S (1x1 sym pair): ΔM = 0.14 uB — CONFOUNDED (>0.05 uB, docs/43:1566-1571)
- edge C-B (2x1v sym pair): ΔM = 0.02 uB — within 0.05 uB
- edge cross-coverage edges (N-C, S-B): ΔM = n/a — NOT EVALUATED — members have different atom counts; no registered raw-total-M normalisation exists (spec ambiguity: A8.3 contrast enumeration unstated)
- FLAG: corner N: nosym EXPLORED — mirror-member standing OPEN (docs/54:406-411, section 6 item 5)

### Fe *OOH
- edge N-S (1x1 sym pair): ΔM = n/a — NOT EVALUABLE (a member has no M: nspin=1 row or pending cell)
- edge C-B (2x1v sym pair): ΔM = 0.0 uB — within 0.05 uB
- edge cross-coverage edges (N-C, S-B): ΔM = n/a — NOT EVALUATED — members have different atom counts; no registered raw-total-M normalisation exists (spec ambiguity: A8.3 contrast enumeration unstated)
- FLAG: corner N: nosym ON_PLANE — mirror-member standing OPEN (docs/54:406-411, section 6 item 5)

### Co *O
- edge N-S (1x1 sym pair): ΔM = n/a — NOT EVALUABLE (a member has no M: nspin=1 row or pending cell)
- edge C-B (2x1v sym pair): ΔM = n/a — NOT EVALUABLE (a member has no M: nspin=1 row or pending cell)
- edge cross-coverage edges (N-C, S-B): ΔM = n/a — NOT EVALUATED — members have different atom counts; no registered raw-total-M normalisation exists (spec ambiguity: A8.3 contrast enumeration unstated)
- FLAG: corner N: nosym EXPLORED — mirror-member standing OPEN (docs/54:406-411, section 6 item 5)
- FLAG: corner S is UNVERIFIED but a parent value exists (runs/s3/Co/s0_O__1x1_off.out = -2330.66171228 Ry); GATE-1 child pending — no reading computed (docs/55 R2; not a docs/55-R1 dual-quote row)

### Ni *O
- edge N-S (1x1 sym pair): ΔM = n/a — NOT EVALUABLE (a member has no M: nspin=1 row or pending cell)
- edge C-B (2x1v sym pair): ΔM = 0.0 uB — within 0.05 uB
- edge cross-coverage edges (N-C, S-B): ΔM = n/a — NOT EVALUATED — members have different atom counts; no registered raw-total-M normalisation exists (spec ambiguity: A8.3 contrast enumeration unstated)
- FLAG: corner N: nosym ON_PLANE — mirror-member standing OPEN (docs/54:406-411, section 6 item 5)

### Ni *OH
- edge N-S (1x1 sym pair): ΔM = 2.71 uB — CONFOUNDED (>0.05 uB, docs/43:1566-1571)
- edge C-B (2x1v sym pair): ΔM = n/a — NOT EVALUABLE (a member has no M: nspin=1 row or pending cell)
- edge cross-coverage edges (N-C, S-B): ΔM = n/a — NOT EVALUATED — members have different atom counts; no registered raw-total-M normalisation exists (spec ambiguity: A8.3 contrast enumeration unstated)
- FLAG: corner N: basin __g1 child runs/s3/Ni/s0_OH__basin_g1.out is +177.10 meV vs parent — refused-candidate per docs/43:1589-1592: a __g1 child > 1 meV above its parent is refused and re-run from the parent's converged density; second failure records the pair MULTISTABLE; energy of record stays the docs/54 basin file pending the owed re-run — FLAGGED
- FLAG: corner B is UNVERIFIED but a parent value exists (runs/s3/Ni/s0_OH__2x1v_off.out = -5157.23065359 Ry); GATE-1 child pending — no reading computed (docs/55 R2; not a docs/55-R1 dual-quote row)

### Ru *OOH
- edge N-S (1x1 sym pair): ΔM = n/a — NOT EVALUABLE (a member has no M: nspin=1 row or pending cell)
- edge C-B (2x1v sym pair): ΔM = n/a — NOT EVALUABLE (a member has no M: nspin=1 row or pending cell)
- edge cross-coverage edges (N-C, S-B): ΔM = n/a — NOT EVALUATED — members have different atom counts; no registered raw-total-M normalisation exists (spec ambiguity: A8.3 contrast enumeration unstated)
- FLAG: corner S: oosh conformer -1715.02124065 is LOWEST banked; whether oosh becomes the member is OPEN (docs/54:422-424, section 6 item 10) — entrant's call, NOT resolved here
- FLAG: corner S member question OPEN — informational alternate computed, never binned; the call is the entrant's

### Ir *OOH
- edge N-S (1x1 sym pair): ΔM = n/a — NOT EVALUABLE (a member has no M: nspin=1 row or pending cell)
- edge C-B (2x1v sym pair): ΔM = n/a — NOT EVALUABLE (a member has no M: nspin=1 row or pending cell)
- edge cross-coverage edges (N-C, S-B): ΔM = n/a — NOT EVALUATED — members have different atom counts; no registered raw-total-M normalisation exists (spec ambiguity: A8.3 contrast enumeration unstated)
- FLAG: corner S: Ir_orient yaw90 -1674.11317317 and oosh -1674.11459651 also banked — oosh-member question OPEN (docs/54:422-424, section 6 item 10) — entrant's call, NOT resolved here
- FLAG: corner S member question OPEN — informational alternate computed, never binned; the call is the entrant's

## Standing ambiguities (NOT resolved here — entrant's calls)

- A8.1 vs the 1A three-bin ladder: supersession or coexistence is not registered; both binnings are printed.
- The <=0.10 eV outcome has no deposited label; the column header above is descriptive, not a registered bin name.
- E's definition (raw total energy vs per-adsorbate normalisation) is not registered; raw finals used as docs/54:18-21 does (infrastructure).
- Whether a CONFOUNDED symmetry edge voids the four-corner interaction row is unstated (A8.3 contrast enumeration).
- Cr/Mn k-bridge (docs/54:41-43): correction registered only as infrastructure; applied nowhere here.
- Which member's M enters the 0.05 uB comparison when parent and child moments differ is unstated; the readout's per-cell M was used as printed.
- Member-identity questions (Cr *OOH 1x1 mir; Ru/Ir *OOH oosh) remain OPEN; informational alternates are computed but never binned.
