/** Exact finite empirical bootstrap oracle; no Monte Carlo or population inference. */
import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
const inputUrl = new URL('../readout/rank_resolution.json', import.meta.url);
const outputUrl = new URL('./exact_min_bootstrap_audit.json', import.meta.url);
const expectedSha256 = '409a6d582ef442cbd69d8ebaf3f2881b99c155d90b374ba637bac5bbdf83edaf';
const raw = await readFile(inputUrl);
const sha256 = createHash('sha256').update(raw).digest('hex');
if (sha256 !== expectedSha256) throw new Error('Pinned input bytes changed');
const data = JSON.parse(raw);
if (data.status !== 'complete' || data.settings.admit !== 'all' || data.settings.B !== 10000) throw new Error('Unexpected input scope');
const formulas = data.banked_order;
if (formulas.length !== 6 || data.site_rows.length !== 720) throw new Error('Expected six compositions / 720 sites');
const decorationMinima = {};
for (const formula of formulas) {
  const rows = data.site_rows.filter(r => r.formula === formula);
  if (rows.length !== 120 || rows.some(r => !r.admitted || !Number.isFinite(r.eta))) throw new Error('Invalid site coverage/admission');
  decorationMinima[formula] = Array.from({length: 30}, (_, seed) => {
    const sites = rows.filter(r => r.seed === seed);
    if (sites.length !== 4 || new Set(sites.map(r => r.site_index)).size !== 4 || sites.some(r => ![0,1,2,3].includes(r.site_index))) throw new Error('Invalid decoration coverage');
    return { seed, minimum_V: Math.min(...sites.map(r => r.eta)) };
  });
}
// Strict rank calculation needs no tie correction for this particular pinned input.
for (let i=0; i<formulas.length; i++) for (let j=i+1; j<formulas.length; j++) {
  const a=decorationMinima[formulas[i]].map(r=>r.minimum_V);
  const b=new Set(decorationMinima[formulas[j]].map(r=>r.minimum_V));
  if (a.some(v=>b.has(v))) throw new Error('Cross-composition minimum tie requires explicit tie handling');
}
const values = Object.fromEntries(formulas.map(f=>[f,decorationMinima[f].map(r=>r.minimum_V)]));
const rank1 = {};
for (const f of formulas) {
  let probability=0;
  for (const v of new Set(values[f])) {
    const mass=(values[f].filter(x=>x>=v).length/30)**30-(values[f].filter(x=>x>v).length/30)**30;
    const opponents=formulas.filter(g=>g!==f).reduce((p,g)=>p*(values[g].filter(x=>x>v).length/30)**30,1);
    probability+=mass*opponents;
  }
  rank1[f]=probability;
}
const probabilitySum=Object.values(rank1).reduce((a,b)=>a+b,0);
if (Math.abs(probabilitySum-1)>1e-12) throw new Error('Rank-1 probabilities do not sum to one');
const candidate='Cu8Cr23Mn35Co34';
const threshold=Math.min(...formulas.filter(f=>f!==candidate).flatMap(f=>values[f]));
const lowerSeeds=decorationMinima[candidate].filter(r=>r.minimum_V<threshold).map(r=>r.seed);
const lowerSites=data.site_rows.filter(r=>r.formula===candidate && r.eta<threshold);
const stored=data.rank_probability.min;
const report={
  schema:'exact-empirical-min-bootstrap-audit-v1',
  input:'../readout/rank_resolution.json', input_sha256:sha256,
  method:"Finite discrete summation over each composition's 30 decoration minima; 30 independent draws with replacement within each composition; independent composition resampling; IEEE-754 arithmetic, no simulation.",
  estimand:'Rank-1 probability conditional on the observed all-admitted six-composition MPA-0 empirical decoration distributions, at resample depth 30 decorations / 120 sites.',
  scope:{model:data.model,admit:'all',compositions:6,decorations_per_composition:30,sites_per_decoration:4,seed_range:[0,29],cross_composition_minimum_ties:false},
  formula:'P(M_f=v)=(count(m_f>=v)/30)^30-(count(m_f>v)/30)^30; P(f rank1)=sum_v P(M_f=v)*product_g!=f (count(m_g>v)/30)^30',
  exact_empirical_rank1_probability:rank1,
  probability_sum:probabilitySum,
  stored_monte_carlo:{replicates:stored.n_replicates,rng_seed:data.settings.seed,rank1_frequency:Object.fromEntries(stored.formulas.map((f,i)=>[f,stored.rank_matrix[i][0]]))},
  cu8_lower_tail:{competitor_best_observed_V:threshold,lower_site_count:lowerSites.length,lower_decoration_count:lowerSeeds.length,lower_seeds:lowerSeeds,probability_omit_all_lower_seeds:((30-lowerSeeds.length)/30)**30,expected_omissions_in_10000:10000*((30-lowerSeeds.length)/30)**30,probability_all_10000_replicates_rank1:rank1[candidate]**10000},
  decoration_minima_V:decorationMinima,
  limitations:['Exact refers to summing finite empirical support rather than Monte Carlo; arithmetic remains floating point.','Not a calibrated population-rank probability: unseen lower-tail values cannot occur in empirical resampling, and minimum bootstrap is descriptive.','Conditional on one model, six gated compositions, all admission and the observed sampling protocol; not an electrode or DFT ranking.','This post-hoc oracle audits the fixed 10000-replicate readout; it does not replace or alter it.']
};
const serialized=JSON.stringify(report,null,2)+'\n';
try {
  await writeFile(outputUrl, serialized, {flag:'wx'});
} catch (error) {
  if (error.code !== 'EEXIST') throw error;
  if (await readFile(outputUrl,'utf8') !== serialized) throw new Error('Existing audit output differs; preserved without overwrite');
}
export default report;
