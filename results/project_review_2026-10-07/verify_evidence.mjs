// Read-only factual verification of this dated review, not a new science analysis.
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../..');
const inputs = new Map();
const checks = [];
async function bytes(relative) {
  const data = await fs.readFile(path.join(root, relative));
  inputs.set(relative, { bytes: data.length, sha256: crypto.createHash('sha256').update(data).digest('hex') });
  return data;
}
async function json(relative) { return JSON.parse((await bytes(relative)).toString('utf8')); }
function check(name, pass, observed) {
  checks.push({ name, pass: Boolean(pass), observed });
  if (!pass) throw new Error(name + ': ' + JSON.stringify(observed));
}

const xu = await json('results/s2_2026-09-18/xu_census.json');
const locks = xu.rows.filter(r => r.force.silentgate_verdict === 'LOCKED');
check('External corpus and lock population', xu.rows.length === 810 && locks.length === 50 && locks.every(r => r.layers === 4), { outputs: xu.rows.length, locks: locks.length, layers: [...new Set(locks.map(r => r.layers))] });
const f = xu.P_XU.final_force;
check('Separate header and final-force denominators', xu.P_XU.header.successes === 70 && xu.P_XU.header.denominator === 810 && f.successes === 50 && f.known_failures === 496 && f.unknown === 80 && f.denominator === 626 && f.original_denominator - f.excluded_union === 626 && f.successes + f.known_failures + f.unknown === 626, { headers: xu.P_XU.header.successes, header_denominator: xu.P_XU.header.denominator, final_force: {successes:f.successes,known_failures:f.known_failures,unknown:f.unknown,denominator:f.denominator,exclusions:f.excluded_union}, bounds_percent:[100*f.lower_fraction,100*f.upper_fraction] });
check('Combined prediction and named-pair outcome', xu.P_XU.outcome === 'FALSIFIED' && xu.P_XU.named_pair_direction.successes === 10 && xu.P_XU.named_pair_direction.outcome === 'HELD', { combined: xu.P_XU.outcome, pairs: xu.P_XU.named_pair_direction.successes, pair_outcome: xu.P_XU.named_pair_direction.outcome });

const controls = await json('results/silentgate_core_2026-09-13/verification.json');
check('Detector control quantifiers', controls.positive === '9/9 two-witness and ALL force-only' && controls.negative_qe === '0/11 ANY adsorbate' && controls.negative_oc20 === '0/500 ANY adsorbate' && controls.tests_passed === 138, {positive:controls.positive,negative_qe:controls.negative_qe,negative_oc20:controls.negative_oc20,tests:controls.tests_passed});
const a0 = await json('docs/figs/a0main_readout.json');
const proj = await json('docs/figs/pproj_readout.json');
const beef = await json('results/s5_beef_2026-09-17/readout.json');
check('Sensitivity numerical results', a0.a7_2.status === 'CONFIRMED' && a0.a7_2.metals_with_flip.length === 5 && a0.a7_3.exceeds.length === 3 && a0.a7_3.denominator === 6 && Math.abs(proj.abs_d_eta_V - 0.48685617462435893) < 1e-12 && beef.score.verdict === 'CONFIRMED' && beef.score.n_scoreable === 3, {pls_flips:a0.a7_2.metals_with_flip.length,fixed_endpoint_over_floor:a0.a7_3.exceeds.length,denominator:a0.a7_3.denominator,projector_delta_V:proj.abs_d_eta_V,beef:beef.score});

const sites = await json('results/site_census_2026-09-06/readout_full/per_site.json');
const gated = new Set(['Cu8Cr23Mn35Co34','Ni31Cr29Cu5Mn35','Fe25Co25Ni25Cr25','Cu26Ni9Cr31Co33','Cu22Fe30Co32Mn15','Ni34Fe6Cu29Co31']);
const rows = sites.rows.filter(r => r.tag === 'mpa0' && ['CENSUS-1','CENSUS-3'].includes(r.arm) && gated.has(r.formula));
const siteCounts = { total:rows.length,desorbed:rows.filter(r=>r.OOH_category==='DESORPTION').length,adsorbate_intact:rows.filter(r=>r.all_states_adsorbate_intact).length,strict_intact:rows.filter(r=>r.all_states_intact).length,per_alloy:Object.fromEntries([...gated].map(g=>[g,rows.filter(r=>r.formula===g).length])) };
check('Site census coverage and chemical identity', siteCounts.total===720 && siteCounts.desorbed===551 && siteCounts.adsorbate_intact===109 && siteCounts.strict_intact===72 && Object.values(siteCounts.per_alloy).every(n=>n===120), siteCounts);
const arm = await json('results/arm_c_2026-10-07/readout.json');
const rerun = await json('results/arm_c_2026-10-07_rerun/rerun_plan.json');
check('Original arm-C completeness and rerun scope', arm.counts.scf_total===64 && arm.counts.scf_accepted===33 && arm.counts.sites_complete===4 && rerun.selection.length===31 && rerun.controls.length===2, {original:arm.counts,rerun_scfs:rerun.selection.length,controls:rerun.controls.length,alloy_dispositions:Object.fromEntries(Object.entries(arm.alloys).map(([k,v])=>[k,{status:v.status,C_V:v.C_V}]))});
const o1 = await json('results/pa_catalyst_o1_2026-10-07/readout.json');
const probe = await json('results/pa_repro_probe_2026-10-07/readout.json');
check('Scoped restart and incomplete probe verdicts', o1.registered.reading==='CONTINUITY_PASS' && o1.registered.scientific_status==='PASS_ONE_BOUNDARY' && Object.entries(o1.registered.max_abs_deltas).every(([k,v])=>v<o1.registered.tolerances_in_force[k]) && probe.readings.PR1_same_state_reproducibility==='INCOMPLETE' && probe.readings.PR2_path_vs_noise==='INCOMPLETE', {o1:o1.registered.reading,scope:o1.registered.scientific_status,max_deltas:o1.registered.max_abs_deltas,probe_PR1:probe.readings.PR1_same_state_reproducibility,probe_PR2:probe.readings.PR2_path_vs_noise});
const lit = await json('results/s2_2026-09-25/full_text/reconcile/current_state.json');
const benchmark = await json('results/hea_validation_2026-09-07/benchmark_pending_report.json');
check('Unfinished literature and separate benchmark', lit.records===2496 && Object.values(lit.v5_final).reduce((a,b)=>a+b,0)===2496 && lit.v5_final.ELIGIBLE===178 && lit.v5_final.NEEDS_SI===89 && lit.v5_final.UNRESOLVED===121 && benchmark.status==='PENDING' && benchmark.scores.length===45 && Object.values(benchmark.splits).every(s=>s.n_truth===0 && s.n_evaluable===0), {literature:lit.v5_final,benchmark_status:benchmark.status,benchmark_cases:benchmark.scores.length});
const live = await json('results/project_review_2026-10-07/status_snapshot_20261007T230537Z.json');
const jobs = live.remote.commands.squeue.stdout.trim().split('\n').map(s=>s.split('|'));
check('Dated live scheduler observation', live.rc===0 && jobs.length===33 && jobs.every(r=>r[0].startsWith('21176478_')) && jobs.filter(r=>r[2]==='RUNNING').length===16 && jobs.filter(r=>r[2]==='PENDING').length===17, {at:live.at,running:jobs.filter(r=>r[2]==='RUNNING').length,pending:jobs.filter(r=>r[2]==='PENDING').length});

const documents = ['docs/report/project-review-2026-10-07.md','docs/report/report-foundation-2026-10-07.md','docs/report/review-brief-2026-10-07.md'];
let links = 0;
for (const relative of documents) {
  const text = (await bytes(relative)).toString('utf8');
  for (const match of text.matchAll(/\[[^\]]*\]\(([^)]+)\)/g)) {
    const target = match[1];
    if (/^https?:\/\//.test(target)) continue;
    const resolved = path.resolve(root, path.dirname(relative), target.split('#')[0]);
    const rel = path.relative(root, resolved).replaceAll('\\','/');
    if (rel.startsWith('../')) throw new Error('Link escapes project: '+target);
    await bytes(rel);
    links++;
  }
}
check('Relative source links resolve and have byte hashes', links > 50, { links_checked:links, unique_pinned_files:inputs.size });
const result = {schema:'project-review-verification-v1',verified_at:new Date().toISOString(),status:'PASS',scope:'Existing primary artifact facts, dated scheduler count, and relative-link existence/hash checks. Not a solver rerun, new CI run, official bibliography, or scientific reclassification.',checks,source_pins:Object.fromEntries(inputs)};
await fs.writeFile(path.join(here,'verification.json'),JSON.stringify(result,null,2)+'\n','utf8');
export const summary = {status:result.status,checks:checks.length,links_checked:links,pinned_files:inputs.size};
