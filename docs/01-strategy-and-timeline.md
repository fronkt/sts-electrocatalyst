# 01 — Strategy & Timeline

## STS rules (official, STS 2026 cycle — confirm for 2027)

- **Solo only.** STS is an individual competition; no team entries. Multi-year /
  continuation research by the individual is allowed.
- **Research paper:** maximum **20 pages**, original work, plus essays, project
  questions, recommendations, transcript, optional test scores.
- **Deadline:** entry due in **November of senior year** (STS 2026 was 8:00 pm ET,
  **Nov 5, 2026** — the STS 2027 deadline will be ~the same).
- **Eligibility:** 12th grade / final year; US resident or territories; any
  citizenship; must not have previously entered STS.
- **Funnel:** ~2,500–2,600 entrants → **Top 300 Scholars** (Jan) → **Top 40
  Finalists** (late Jan, compete in DC in March). STS 2026 drew 2,612 entrants
  (largest since 1967), $1.8M in awards.

Sources: <https://www.societyforscience.org/regeneron-sts/application-requirements/> ·
<https://www.societyforscience.org/regeneron-sts/frequently-asked-questions/> ·
Official Rules PDF: <https://sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2026/Application/Official-Rules.pdf>

## Timeline to Nov 5, 2026 (today: 2026-06-25)

| Window | Milestone |
|---|---|
| **Now → mid-Jul** | Lock ONE framing. Confirm instrument + fabrication access. Secure sponsor + sign STS forms. Stand up the ML/compute pipeline (reuse existing stack). |
| **Jul → early Oct** | **Execution.** Generate computational results; fabricate 1–3 candidates; characterize and validate vs. a baseline. Iterate once, not five times. |
| **early Oct** | **Freeze data.** No new experiments after this. |
| **Oct → Nov 4** | Write & polish the ≤20-page paper + essays. Make it legible to a generalist judging panel. |
| **Nov 5** | Submit. |

> **Hard truth:** the effective research runway is **~3.5 months, not 5**. Any
> experimental loop must be **1–3 samples and booked this month**, or drop to a
> mostly-computational framing with a single confirmatory measurement.

## The ceiling analysis (why the original thermal idea needs elevating)

The original instinct — *a high-thermal-conductivity material for heat dissipation
in computing* — already exists in the STS record and shows the ceiling:

> **Anthony Low, STS 2026 — "A Novel 0D/2D Composite Phase Change Material for
> Thermal Management in High-Performance Computing." → Top 300 Scholar (not Finalist).**

Across 2021–2026, **no** classic "high-κ material for heat dissipation" project
cracked the Top 40. Other thermal entries (aerogels, radiative ice-melt) also
stalled at Scholar. Read it both ways:

- **White space** — few competitors, so Scholar is very achievable and the work
  is differentiated.
- **Proven low ceiling** — to exceed Scholar you must do something structurally
  different from "make a conductive material and measure κ."

## Strategic verdict

The structural difference that breaks the ceiling, and which this student is
uniquely positioned to deliver:

> **A hybrid project: ML / simulation designs or screens a candidate → the student
> fabricates it → measures it and beats a baseline.**

This combines the two things STS Top-40 materials projects reward — **method
novelty** (the inverse-design/generative template) and **"you made and measured
something"** credibility — and it leverages two assets almost no entrant has at
once: a real wet lab *and* a mature ML-materials toolkit.

**Lane choice:** if optimizing purely for Top-40 *probability*, batteries /
catalysis / energy storage are statistically safer lanes. Thermal and rare-earth
are **Finalist-stretch, Scholar-safe** — chosen here for white space, unique
access, and (for rare earth) the strongest "so what" in materials right now.
See [`06-project-shortlist.md`](06-project-shortlist.md).
