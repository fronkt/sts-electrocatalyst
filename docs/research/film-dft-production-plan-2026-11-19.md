# Film-model DFT production: job list and SU estimate (proposal, 2026-11-19)

Status: **PROPOSAL for Frank's OK. Not registered.** No production job runs until Frank picks a scope
and a compute source, and the chosen design is committed as a registration with the ranking rule.
That commit comes in its own step, before any deploy.

Context:
- Pilot: `docs/research/film-dft-pilot-2026-11-14.md`. V1 passes at U = 0. The PBE+U check is open,
  a stated limitation. V2 (CoOOH) is not evaluable.
- Role: `tasks/isef-2027-master-plan-2026-11-14.md` section 5, and `tasks/isef-2027-round2-plan.md`
  item C3. Film-model DFT is a third registered predictor, beside CALPHAD and the film Ni+Fe rule. Its
  ranking is registered before the round-2 bench. If it beats the Ni+Fe rule on round 2, it picks
  round 3.

## 1. What the test is

Round 2 has only two films whose activity is not yet known:
- **R3's film** (Ni34Fe29Mn30Co7 -> Ni49Fe41Co10).
- **Cu26's film** (Co49Cu38Ni14). Cu26's new disks come from the leftover ARC00150 rod.

R1 and R2 grow Fe25's film (Fe33Co33Ni33), so the DFT can only predict them equal to Fe25. That tests
the film hypothesis, not the DFT ranking. To place R3 and Cu26 on a scale, the DFT also has to compute
the five measured round-1 films. Those serve as a post hoc calibration and are not a test. So
production covers the seven distinct films.

## 2. Films and sites

Films are the composition left after Cr and Mn leach (round-2 plan P2). This is an assumption: no film
has been measured yet (post-OER SEM-EDS / XPS are planned). Each film is decorated on the pilot slab's 12
metal positions:
- β-NiOOH (01-12), 2x1, 48 atoms; U = 0; the pilot's settings and QC.
- Two top-edge sites per slab.
- Every element with at least 1 of 12 metals is a site type.
- One seeded decoration per slab.

| Film (alloys) | Film composition | 12-metal decoration | Measured eta10 | Ni+Fe | Site types |
|---|---|---|---|---|---|
| F1 (Ni31) | Ni86Cu14 | Ni10 Cu2 | 0.316 | 0.86 | Ni, Cu |
| F2 (Fe25, R1, R2) | Fe33Co33Ni33 | Fe4 Co4 Ni4 | 0.313 (Fe25) | 0.67 | Fe, Co, Ni |
| F3 (R3) | Ni49Fe41Co10 | Ni6 Fe5 Co1 | **blind** | 0.90 | Fe, Ni, Co |
| F4 (Ni34) | Ni34Co31Cu29Fe6 | Ni4 Co4 Cu3 Fe1 | 0.369 | 0.40 | Fe, Ni, Co, Cu |
| F5 (Cu22) | Co38Fe36Cu26 | Co5 Fe4 Cu3 | 0.365 | 0.35 | Fe, Co, Cu |
| F6 (Cu8) | Co81Cu19 | Co10 Cu2 | > 0.393 | 0.00 | Co, Cu |
| F7 (Cu26) | Co49Cu38Ni14 | Co6 Cu4 Ni2 | **blind** | 0.14 | Co, Cu, Ni |

Proposed predictor, to be fixed at registration: a film's predicted eta is the lowest eta over its
evaluable sites (best site). Films are ranked by it.

## 3. What the model is validated for

| Site element | Status | Films with it |
|---|---|---|
| Fe (in a Ni host) | **Validated**: V1, Fe site 0.38-0.39 V vs Ni site 0.96 V, the experimental order | F2, F3, F4, F5 |
| Ni | Validated as V1's reference site | F1, F2, F3, F4, F7 |
| Co | **Not validated.** V2 not evaluable: the CoOOH slab and \*OH were POISONED, \*O incomplete, \*OOH missing, and the clean slab's SCF sloshed at 5e-3 to 1e-2 Ry for 200 iterations | F2, F3, F4, F5, F6, F7 |
| Cu | **Never run** in this model (no Cu pseudopotential staged yet) | F1, F4, F5, F6, F7 |

Other limits, stated with any ranking:
- The Hubbard-U ordering is open (pilot amendments 23-24).
- The film compositions are assumed, not measured.
- With one decoration per slab, the site-environment spread is not sampled.
- The model cannot see electrolyte Fe uptake. That matters for Ni31: its film has no Fe, yet it ties
  Fe25. Gate 2 (iron-free KOH) tests this.
- A ranking that uses only Fe and Ni sites will be shaped mostly by whether a film contains Fe.
  Differences among the Fe-containing films come from the Fe site's environment, which is what
  production measures.

## 4. Cost basis (measured in the pilot, U = 0, 48 Anvil ranks)

- One SCF iteration: 0.43 SU (31-33 s at 48 ranks). The AWS runs came to 0.35-0.45 core-h per iteration.
- Relaxation per state, all restarts included: 787-3,137 SCF iterations, about 640 SU on average (range
  338-1,349). Two of the eight states needed 7 and 11 restarts.
- Configuration single point (rule 3): 35 run, median 88 iterations, about 51 SU each on average.
- Per state as planned: one relaxation plus two configuration single points (the two neighbour flips),
  about 740 SU. Contingency 30%.
- Not included: PBE+U single points. The pilot showed those cost more than the U = 0 states and did not
  settle; the U = 0 model is the validated one.

## 5. Three scopes

| Scope | Films | Sites | Slabs | Relaxations | Single points | Estimate | With 30% |
|---|---|---|---|---|---|---|---|
| **Full**: every site type | F1-F7 | 20 | 12 | 72 | 144 | 53,400 SU | **~69,500 SU** |
| **Lean**: validated sites only (Fe, Ni) | F1-F5, F7 (F6 has no Fe or Ni site, so not evaluable) | 9 | 6 | 33 | 66 | 24,500 SU | **~31,800 SU** |
| **Lean + Co gate**: Lean, then V2 finished (CoOOH vs NiOOH); Co sites join only if V2 passes | as Lean, then Co sites in F2-F7 | 9 (+6 Co) | 6 (+1 V2, +4 Co) | 33 (+4 V2, +22 Co) | 66 (+8 V2, +44 Co) | 24,500 (+3,000 V2, +16,300 Co) | ~31,800, then ~3,900 for V2, then ~21,200 for Co |

The Lean job list: the six slabs (F1 Ni10Cu2; F2, F3 and F4 with the top-edge pair Fe+Ni; F5 with Fe +
Co; F7 with Ni + Co), plus \*OH / \*O / \*OOH at each of the nine sites (F1 Ni; F2 Fe, Ni; F3 Fe, Ni; F4
Fe, Ni; F5 Fe; F7 Ni). The gas references come from the pilot. The Co step adds the Co sites of F5 and F7
on their Lean slabs, and four new slabs with Co at the top edge (F2, F3, F4, F6).

## 6. Compute source

- **Current balance: 1,820.6 SU** (CHE260157 CPU, 2026-11-19). It covers no scope. It is about three
  relaxations, under one site, so it cannot even finish V2 (about 3,000 SU).
- **ACCESS supplement:** the draft (`docs/research/access-supplement-request-2026-11-14.md`) asks for
  70,000 SU and is recorded as **not submitted**. Its scope text is out of date: it says 11 alloys, 6
  tested and 5 being melted, and it budgets PBE+U single points for every state. It needs revising to the
  seven films and the U = 0 design before Frank files it. A supplement is one-time per award period, so
  keeping 70,000 would cover Full, or Lean plus round-3 work.
- **AWS (as in the pilot, Frank's call):** c7a.48xlarge at about $9.8 per instance-hour, so about $0.051
  per core-hour. That puts Lean at about $1,600 and Full at about $3,500.

## 7. Timing

- **Deadline:** register the ranking before the first round-2 disk is measured. The January order
  starts with R3, so that means before about Jan 4, and safer by Dec 18, when the disks go to Josh.
- **Throughput:**
  - The average relaxation is about 1,500 iterations, or about 13 h at 48 ranks.
  - With about 8 jobs at once, Lean needs about 2-3 weeks of calendar time, and Full about 4-5 weeks,
    counting queue waits and restarts.
- **Consequence:** Lean has to start by about Dec 1 to register by Dec 18. Full cannot be finished
  before January, unless it is split so the blind films and their Fe and Ni sites (F2, F3, F7) run
  first.

## 8. Decisions for Frank

1. Scope: Full, Lean, or Lean + Co gate (recommended: Lean + Co gate).
2. Compute source: revise and file the supplement, AWS, or stop production.
3. Then a registration commit (decoration seeds, site list, QC, the best-site predictor, the comparison
   with the Ni+Fe rule on round 2), and the jobs run after it.
