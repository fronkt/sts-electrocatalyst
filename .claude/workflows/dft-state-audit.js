export const meta = {
  name: 'dft-state-audit',
  description: 'Audit the DFT arm of sts-electrocatalyst: methodology, results, claim integrity, screen output, melt readiness, STS fit',
  phases: [
    { title: 'Audit', detail: 'six parallel readers over distinct dimensions of the DFT record' },
    { title: 'Verify', detail: 'adversarial check on success/significance claims' },
  ],
}

const ROOT = 'C:/Users/frank/sts-electrocatalyst'

const LANES = [
  {
    key: 'method',
    label: 'audit:methodology',
    prompt: `You are auditing the DFT METHODOLOGY of the repo at ${ROOT}.

Read: docs/22-multifidelity-dft-calibration.md, docs/23-dft-compute-log.md, docs/26-endmember-parity-checkpoint.md, docs/30-qc-audit-and-r1-campaign.md, src/dft/qe_slab.py, src/dft/qe_qc.py, src/dft/run_convergence.sh, src/dft/gen_rutile.py, results/cro2_dft_convergence.csv, and any *.in input files you can find under runs/ or results/box/.

Establish, with FILE:LINE evidence for each:
1. What DFT code, functional, pseudopotentials, plane-wave/density cutoffs, k-point mesh, smearing, vacuum thickness, slab layers, whether the bottom layers are fixed, dipole correction on/off, spin polarization, Hubbard U values and scheme.
2. What convergence testing was actually DONE (cutoff, k-points, slab thickness, vacuum) and what the residual error was. Quote the numbers.
3. Force/energy convergence thresholds used for the relaxations.
4. Whether zero-point energy / entropy / solvation / dispersion corrections were applied to the free energies, or omitted.
5. How the CHE free energies are assembled (which reference states, any O2 overbinding correction).
6. Any methodological SHORTCUTS or known deviations from standard practice in this literature (e.g. undersized cells, gamma-only k-points, no ZPE, no dipole correction, low cutoff).

Be specific and quantitative. Do NOT speculate — if something is not in the repo, say "not found in repo".`,
  },
  {
    key: 'results',
    label: 'audit:results',
    prompt: `You are auditing the DFT RESULTS actually obtained in the repo at ${ROOT}.

Read: src/dft/eta_bounded.py (especially reference_tier()), results/r3_dft_reference_repaired.json, docs/26, docs/32-anchor-gate-verdict.md, docs/33-r3-mlip-evaluation.md, docs/35-n7-campaign-result.md, docs/23-dft-compute-log.md, src/dft/adsorbate_qc.py.

Establish, with evidence:
1. Exactly WHICH metals have a complete DFT overpotential, and the numeric eta and potential-limiting step for each. Produce the full table.
2. For each metal and each adsorbate state (*OH, *O, *OOH): did the relaxation converge cleanly, get trapped, desorb, or require a restart/rescue? Which geometries were seeded from an MLIP minimum?
3. Total CPU/GPU hours and dollar cost spent on DFT so far, if logged.
4. How the computed eta compare to PUBLISHED DFT values for the same rutile MO2(110) surfaces (e.g. RuO2, IrO2 from the literature). Does the repo contain any such comparison? Quote the published numbers the repo cites and the deltas.
5. Are there ANY error bars, repeat calculations, or uncertainty estimates on the DFT numbers?
6. What fraction of the DFT states are "clean" vs "repaired/rescued/seeded"?

Do NOT speculate — if something is not in the repo, say "not found in repo".`,
  },
  {
    key: 'claims',
    label: 'audit:claims',
    prompt: `You are auditing the CLAIM INTEGRITY of the repo at ${ROOT}.

Read: docs/33-r3-mlip-evaluation.md, docs/34-prereg-sixth-point.md, docs/35-n7-campaign-result.md, docs/38-matched-protocol-parity.md, docs/39-prereg-omat-head.md, docs/40-predictor-reference-independence.md, docs/29-r0-oc22-reparity.md, tasks/lessons.md.

Establish:
1. What claims does the project currently make that are still STANDING (not falsified, not superseded)? List each with the doc that supports it and the statistical evidence (rho, p, MAE, n).
2. What claims have been FALSIFIED or retracted, and by what? List each.
3. What are the KNOWN, DOCUMENTED weaknesses/limitations that an expert judge would find if they read carefully? Rank by how damaging.
4. Is there any held-out validation anywhere in the project? Any prediction made BEFORE the ground truth was known that was then confirmed?
5. What pre-registrations exist and were they honored?
6. Quote the single strongest defensible sentence the project can currently say about its scientific result, and the single most damaging true sentence a hostile reviewer could say.

Do NOT speculate — cite doc sections.`,
  },
  {
    key: 'screen',
    label: 'audit:screen',
    prompt: `You are auditing the HEA SCREEN and MELT LIST in the repo at ${ROOT}.

Read: docs/36-screen-validation-and-stability-gate.md, docs/37-hea-screen-result-and-melt-list.md, docs/31-r2-stability-gate.md, results/r4_screen.json, results/r4_gated.json, results/r4_melt_list.json, results/r4_validate.json, results/r2_stability.json, results/r2_multi_meltset.json, src/dft/pourbaix_r2.py.

Establish:
1. How many candidate compositions were screened, over what composition space, with what model?
2. What is the final melt list? Give the exact compositions and their predicted eta.
3. What is the PREDICTED SPAN of overpotential across the melt list (best minus worst)? Is that span larger than the model's own error bar (MAE ~0.125-0.17 V)? This is the crux: if the span is smaller than the error, the experiment cannot distinguish the candidates.
4. What stability screening (Pourbaix, e_above_hull, dissolution) was applied and what did it eliminate?
5. Does the screen include the reference materials (RuO2/IrO2) as internal controls?
6. Any documented concern about whether the melt list is actually distinguishable experimentally?

Quantitative, with evidence.`,
  },
  {
    key: 'melt',
    label: 'audit:melt-readiness',
    prompt: `You are auditing EXPERIMENTAL / MELT READINESS in the repo at ${ROOT}.

Read: docs/15-round1-melt-test-plan.md, docs/17-fwm-weigh-sheet.md, docs/25-sts-application-playbook.md, docs/12-catalysis-hea-execution-plan.md, docs/28-electrocatalyst-revival-plan.md, tasks/todo.md, src/scripts/ (any weigh sheet or lab scripts).

Establish:
1. What is the concrete experimental plan: what gets melted, on what equipment, where, with whose supervision?
2. What electrochemical characterization is planned (LSV, CV, Tafel, chronopotentiometry, ECSA normalization)? What equipment is available?
3. What is BLOCKING the first melt right now? List every blocker explicitly, including safety/regulatory (e.g. Cr(VI) risk assessment), materials procurement, equipment access, mentor sign-off.
4. What is the timeline in the repo, and what is the stated data-freeze date?
5. Has ANY experimental work been done yet? Any samples made, any measurement taken?
6. What is the realistic minimum path from today to one measured polarization curve on one sample? Enumerate steps with rough durations.

Be concrete. If a blocker is unresolved, say so plainly.`,
  },
  {
    key: 'sts',
    label: 'audit:sts-fit',
    prompt: `You are auditing how this project maps onto REGENERON SCIENCE TALENT SEARCH judging criteria. Repo: ${ROOT}.

Read: docs/25-sts-application-playbook.md, docs/18-competitive-benchmark.md, docs/01-strategy-and-timeline.md, docs/16-project-overview.md, docs/02-sts-materials-landscape.md.

Establish:
1. What does the repo record about STS judging criteria, rubric, scoring, and what distinguishes Scholar (top 300) from Finalist (top 40)? Quote it.
2. What does the repo record about what competitive materials-science STS entries have historically looked like? Any specific past projects benchmarked?
3. What are the stated deliverables and deadlines (report length, due dates, sponsor requirement, research plan/essays)?
4. What does the repo say about the AI-authorship rules and any disqualification traps?
5. What does the repo identify as this project's competitive strengths and weaknesses vs the benchmark?
6. Is there any statement in the repo about whether a computation-only result is sufficient?

Quote the docs. Do NOT invent STS rules that are not in the repo — flag clearly anything you are unsure about.`,
  },
]

const AUDIT_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['findings', 'hard_numbers', 'gaps'],
  properties: {
    findings: {
      type: 'array',
      description: 'Ordered findings, most important first',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['claim', 'evidence'],
        properties: {
          claim: { type: 'string', description: 'A specific factual statement about the repo' },
          evidence: { type: 'string', description: 'file:line or doc section supporting it' },
          confidence: { type: 'string', enum: ['certain', 'likely', 'uncertain'] },
        },
      },
    },
    hard_numbers: {
      type: 'array',
      description: 'Every quantitative value established, as "label = value (source)"',
      items: { type: 'string' },
    },
    gaps: {
      type: 'array',
      description: 'Things asked about that are NOT in the repo',
      items: { type: 'string' },
    },
  },
}

const VERDICT_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['refuted', 'reasoning'],
  properties: {
    refuted: { type: 'boolean' },
    reasoning: { type: 'string' },
    corrected_statement: { type: 'string' },
  },
}

phase('Audit')
const audits = await parallel(LANES.map(l => () =>
  agent(l.prompt, { label: l.label, phase: 'Audit', schema: AUDIT_SCHEMA })
    .then(r => ({ key: l.key, ...r }))))

const ok = audits.filter(Boolean)
log(`${ok.length}/${LANES.length} audit lanes returned`)

const digest = ok.map(a =>
  `### ${a.key}\nFINDINGS:\n${(a.findings || []).map(f => `- ${f.claim} [${f.evidence}] (${f.confidence || '?'})`).join('\n')}\nNUMBERS:\n${(a.hard_numbers || []).map(n => `- ${n}`).join('\n')}\nGAPS:\n${(a.gaps || []).map(g => `- ${g}`).join('\n')}`
).join('\n\n').slice(0, 60000)

phase('Verify')
const PROPOSITIONS = [
  'The DFT calculations in this repo are methodologically sound enough that a professional computational catalysis reviewer would accept the overpotential values as correct to within the accuracy normally claimed for CHE-level DFT (~0.2-0.3 V).',
  'The project has produced a scientific result that is genuinely NEW — i.e. not merely a reproduction of what is already established in the rutile OER literature.',
  'The predicted overpotential span across the melt list is large enough that a real electrochemical measurement could distinguish the candidates from each other and from the reference materials.',
  'The project as it stands TODAY, with zero experimental work, contains enough validated science to be competitive for STS Scholar (top 300).',
]

const verdicts = await parallel(PROPOSITIONS.map((p, i) => () =>
  agent(`You are a skeptical senior reviewer. Try HARD to REFUTE this proposition about the project at ${ROOT}. Default to refuted=true if the evidence does not clearly support it.

PROPOSITION: ${p}

Here is the audit digest gathered by six independent readers of the repo:

${digest}

You may read files in the repo directly to check anything. Give your verdict with concrete reasons, and if you refute it, give the corrected statement that IS supportable.`,
    { label: `verify:p${i + 1}`, phase: 'Verify', schema: VERDICT_SCHEMA })
    .then(v => ({ proposition: p, ...v }))))

return { audits: ok, verdicts: verdicts.filter(Boolean) }
