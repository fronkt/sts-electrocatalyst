/** Public-only continuation; never assigns scientific eligibility. */
import * as fs from 'node:fs/promises';
import path from 'node:path';
import {csvRows, digest, MODEL, DOMAINS, makeRequest, reviewedRoutes} from './openai_public_si.mjs';

export const TOTAL_CAP = 50;
export const TRANCHE_CAP = 5;
export const RESERVE = 1;
const jsonRead = async p => JSON.parse(await fs.readFile(p, 'utf8'));
const jsonNew = async (p, v) => fs.writeFile(p, JSON.stringify(v, null, 2)+'\n', {flag:'wx'});

// This is a narrow output-shape interpretation, not proof of tool billing.
// Sources from an unfinished item are never accepted. Historical strict flags
// remain unchanged. Every event/query is still charged pessimistically.
export function controls(response) {
  const events = (response.output ?? []).filter(x => x.type === 'web_search_call');
  const completed = events.filter(x => x.status === 'completed');
  const pending = events.filter(x => x.status !== 'completed');
  const ignoredShape = response.status === 'completed' && response.max_tool_calls === 2 &&
    response.output?.at(-1)?.type === 'message' && response.output.at(-1).status === 'completed' &&
    completed.length === 2 && events.length === 3 &&
    events[0].status === 'completed' && events[1].status === 'completed' &&
    events[2].status === 'searching' && events[2].action?.type === 'search' &&
    !(events[2].action.sources?.length) && !events[2].action.url;
  const violations=[];
  if(completed.length > 2) violations.push('completed_tool_limit_exceeded');
  if(pending.length && !ignoredShape) violations.push('unclassified_nonterminal_tool_event');
  if(events.length > 2 && !ignoredShape) violations.push('unclassified_extra_tool_event');
  return {completed:completed.length, pending:pending.length, events:events.length,
    warnings:ignoredShape ? ['source_free_extra_attempt_retained_not_processed_or_billed_proof'] : [],
    violations};
}

export function conservativeCost(response) {
  const u=response.usage;
  if(!Number.isSafeInteger(u?.input_tokens) || u.input_tokens<0 ||
     !Number.isSafeInteger(u?.output_tokens) || u.output_tokens<0) return null;
  const toolUnits=(response.output??[]).filter(x=>x.type==='web_search_call')
    .reduce((n,x)=>n+Math.max(1, Array.isArray(x.action?.queries)?x.action.queries.length:0),0);
  return u.input_tokens*0.20/1e6 + u.output_tokens*0.75/1e6 + toolUnits*0.01;
}

export async function prepareContinuation(root,outDir,limit=10) {
  if(!Number.isSafeInteger(limit)||limit<1||limit>10) throw new Error('invalid tranche size');
  if(path.resolve(outDir)!==path.resolve(root,'openai_public_si_continuation_2026-10-01'))
    throw new Error('refusing a second budget ledger');
  const priorDir=path.join(root,'openai_public_si_2026-10-01');
  const priorManifest=await jsonRead(path.join(priorDir,'manifest.json'));
  const ledger=(await fs.readFile(path.join(priorDir,'ledger.jsonl'),'utf8')).trim().split(/\r?\n/).map(JSON.parse);
  if(ledger.length!==10 || new Set(ledger.map(x=>x.sid)).size!==10) throw new Error('prior pilot coverage changed');
  const baseline={};
  const baselinePaths=['si_checklist.csv','si_checklist.html','reconcile/current_state.csv',
    'reconcile/current_state.json','reconcile/si_policy_choices_2026-10-01.md',
    'openai_public_si.mjs','openai_public_si_2026-10-01/ledger.jsonl',
    'openai_public_si_2026-10-01/verification.json',
    ...Object.keys((await jsonRead(path.join(root,'public_followup_2026-10-01/baseline.json'))).files)];
  for(const rel of new Set(baselinePaths)) baseline[rel]=digest(await fs.readFile(path.join(root,rel)));
  let carried=0; const priorControls=[];
  for(const row of ledger) {
    const rel='openai_public_si_2026-10-01/'+row.sid+'.response.json';
    const raw=await jsonRead(path.join(root,rel)); baseline[rel]=digest(await fs.readFile(path.join(root,rel)));
    const receipt=await jsonRead(path.join(priorDir,row.sid+'.receipt.json'));
    if(!priorManifest.records.some(x=>x.sid===row.sid) || !Number.isFinite(row.charged_usd) || row.charged_usd<0 ||
       receipt.status!=='completed' || receipt.response_id!==raw.id || receipt.charged_usd!==row.charged_usd ||
       JSON.stringify(reviewedRoutes(raw,priorManifest.records.find(x=>x.sid===row.sid)))!==JSON.stringify(receipt.routes))
      throw new Error('inconsistent prior receipt: '+row.sid);
    const audit=controls(raw); const estimate=conservativeCost(raw);
    if(raw.status!=='completed'||estimate===null||audit.violations.length) throw new Error('prior unresolved control: '+row.sid);
    carried+=Math.max(row.charged_usd??row.reserved_usd,estimate);
    priorControls.push({sid:row.sid,...audit});
  }
  const earlier=await jsonRead(path.join(root,'evidence_recovery_2026-10-01/routes_summary.json'));
  const publicFollow=await jsonRead(path.join(root,'public_followup_2026-10-01/public_routes.json'));
  const excluded=new Set([...priorManifest.records.map(x=>x.sid),...earlier.retrieval_targets,
    ...publicFollow.map(x=>x.sid)]);
  const rows=csvRows(await fs.readFile(path.join(root,'si_checklist.csv'),'utf8'));
  const logs=[];
  for(const name of ['si_public_log.jsonl','retrieval_log.jsonl'])
    for(const line of (await fs.readFile(path.join(root,name),'utf8')).split(/\r?\n/).filter(Boolean))
      logs.push({source_log:name,...JSON.parse(line)});
  const records=rows.filter(r=>r.tier==='1'&&r.v5_final==='NEEDS_SI'&&!excluded.has(r.screen_id))
    .slice(0,limit).map(r=>({sid:r.screen_id,doi:r.doi,title:r.title,tier:1,
      open_criteria:r.open_criteria,missing_evidence:r.si_items||r.file,
      previous_public_attempts:logs.filter(x=>(x.screen_id??x.sid)===r.screen_id)
        .map(x=>({source_log:x.source_log,route:x.route??'',url:x.url??'',status:x.status??x.outcome??''}))}));
  if(records.length!==limit || new Set(records.map(x=>x.doi.toLowerCase())).size!==limit)
    throw new Error('invalid distinct priority queue');
  const manifest={at:new Date().toISOString(),model:MODEL,total_cap_usd:TOTAL_CAP,
    tranche_cap_usd:TRANCHE_CAP,reserve_usd:RESERVE,carried_prior_estimate_usd:carried,
    cost_note:'Pessimistic long-context rates, no cache discount, every event/query charged; not invoice.',
    records,excluded_sids:[...excluded],allowed_domains:DOMAINS,baseline_hashes:baseline,
    prior_controls:priorControls,scope:'Public repository discovery only; no eligibility change',
    key_name:'electro-public-si',project:'electrolyte-supercapacitor-dev',key_expiry:'2026-10-08'};
  await fs.mkdir(outDir,{recursive:true});
  await jsonNew(path.join(outDir,'manifest.json'),manifest);
  await jsonNew(path.join(outDir,'guard_acceptance.json'),{
    at:new Date().toISOString(),official_reference:'https://developers.openai.com/api/reference/cli/resources/responses/methods/create',
    interpretation:'Source-free searching item after two completed calls is an unprocessed-attempt-compatible shape; not proof of processing or billing. Strict historical flags retained.',
    prior_controls:priorControls,prior_cost_reestimated_usd:carried});
  return manifest;
}

async function validateManifest(root, outDir, supplied) {
  const saved=await jsonRead(path.join(outDir,'manifest.json'));
  if(JSON.stringify(saved)!==JSON.stringify(supplied) || saved.model!==MODEL ||
     saved.total_cap_usd!==TOTAL_CAP || saved.tranche_cap_usd!==TRANCHE_CAP ||
     saved.reserve_usd!==RESERVE || !Number.isFinite(saved.carried_prior_estimate_usd) ||
     saved.carried_prior_estimate_usd<0) throw new Error('invalid manifest');
  for(const [rel,sha] of Object.entries(saved.baseline_hashes))
    if(digest(await fs.readFile(path.join(root,rel)))!==sha) throw new Error('baseline_changed:'+rel);
  // Production manifests always include the pinned prior ledger. Validate its
  // receipt chain before every new paid call, not just preparation.
  if(saved.baseline_hashes['openai_public_si_2026-10-01/ledger.jsonl']) {
    const prior=path.join(root,'openai_public_si_2026-10-01');
    const oldManifest=await jsonRead(path.join(prior,'manifest.json'));
    const oldRows=(await fs.readFile(path.join(prior,'ledger.jsonl'),'utf8')).split(/\r?\n/).filter(Boolean).map(JSON.parse);
    if(new Set(oldManifest.records.map(x=>x.sid)).size!==10 || oldManifest.records.length!==10 || oldRows.length!==10 || new Set(oldRows.map(x=>x.sid)).size!==10)
      throw new Error('prior coverage mismatch');
    let carried=0;
    for(const row of oldRows) {
      const record=oldManifest.records.find(x=>x.sid===row.sid);
      const raw=await jsonRead(path.join(prior,row.sid+'.response.json'));
      const receipt=await jsonRead(path.join(prior,row.sid+'.receipt.json'));
      const cost=conservativeCost(raw);
      if(!record || !Number.isFinite(row.charged_usd) || row.charged_usd<0 || cost===null ||
         raw.status!=='completed' || controls(raw).violations.length || receipt.status!=='completed' ||
         receipt.response_id!==raw.id || receipt.charged_usd!==row.charged_usd ||
         JSON.stringify(reviewedRoutes(raw,record))!==JSON.stringify(receipt.routes))
        throw new Error('prior receipt mismatch:'+row.sid);
      carried+=Math.max(row.charged_usd,cost);
    }
    if(carried!==saved.carried_prior_estimate_usd) throw new Error('prior carried cost mismatch');
  }
}

async function ledgerRead(outDir,manifest) {
  let ledger=[];
  try {ledger=(await fs.readFile(path.join(outDir,'ledger.jsonl'),'utf8')).split(/\r?\n/).filter(Boolean).map(JSON.parse);}
  catch(e) {if(e.code!=='ENOENT') throw e;}
  if(new Set(ledger.map(x=>x.sid)).size!==ledger.length) throw new Error('duplicate ledger');
  for(const r of ledger) {
    if(!manifest.records.some(x=>x.sid===r.sid) || r.reserved_usd!==RESERVE ||
       !Number.isFinite(r.charged_usd??RESERVE) || (r.charged_usd??RESERVE)<0)
      throw new Error('invalid ledger row');
  }
  return ledger;
}

export async function runContinuationOne({root,outDir,manifest,sid,apiKey,fetchImpl=fetch}) {
  if(typeof apiKey!=='string'||!apiKey) throw new Error('credential unavailable');
  const lockFile=path.join(outDir,'run.lock'); const lock=await fs.open(lockFile,'wx');
  try {
    await validateManifest(root,outDir,manifest);
    const record=manifest.records.find(x=>x.sid===sid);
    if(!record||!/^S\d{5}$/.test(sid)) throw new Error('SID outside pinned tranche');
    const ledger=await ledgerRead(outDir,manifest);
    if(ledger.some(x=>x.sid===sid)) return {sid,status:'ALREADY_ATTEMPTED'};
    // Every existing attempt must have a complete, self-consistent receipt.
    // A timeout, crash, API error, incomplete result or unknown usage stops the tranche.
    for(const r of ledger) {
      let receipt,raw;
      try {receipt=await jsonRead(path.join(outDir,r.sid+'.receipt.json'));
        raw=await jsonRead(path.join(outDir,r.sid+'.response.json'));}
      catch {return {sid,status:'PRIOR_UNCERTAINTY_STOP',prior_sid:r.sid};}
      if(receipt.status!=='completed' || raw.status!=='completed' || controls(raw).violations.length ||
         conservativeCost(raw)===null || receipt.charged_usd!==r.charged_usd ||
         receipt.charged_usd!==Math.max(0,conservativeCost(raw)) || receipt.response_sha256!==digest(await fs.readFile(path.join(outDir,r.sid+'.response.json'))))
        return {sid,status:'PRIOR_UNCERTAINTY_STOP',prior_sid:r.sid};
    }
    const spent=manifest.carried_prior_estimate_usd+ledger.reduce((n,r)=>n+(r.charged_usd??RESERVE),0);
    if(spent+RESERVE>Math.min(TOTAL_CAP,manifest.tranche_cap_usd)) return {sid,status:'BUDGET_STOP',spent};
    const request=makeRequest(record);
    if(JSON.stringify(request).length>40000) throw new Error('input size limit');
    await jsonNew(path.join(outDir,sid+'.request.json'),request);
    const reservation={sid,at:new Date().toISOString(),reserved_usd:RESERVE};
    await fs.appendFile(path.join(outDir,'ledger.jsonl'),JSON.stringify(reservation)+'\n');
    let receipt={sid,status:'AMBIGUOUS_REQUEST',charged_usd:RESERVE};
    try {
      // Restricted project key selects its project; no browser/session or
      // account settings access is required. Never persist request headers.
      const result=await fetchImpl('https://api.openai.com/v1/responses',{
        method:'POST',headers:{Authorization:'Bearer '+apiKey,'Content-Type':'application/json'},
        body:JSON.stringify(request),signal:AbortSignal.timeout(55000)});
      const raw=await result.json();
      if(!result.ok) receipt={sid,status:'API_ERROR',http_status:result.status,charged_usd:RESERVE};
      else {
        const serialized=JSON.stringify(raw,null,2)+'\n';
        if(serialized.includes(apiKey)) throw new Error('secret echo rejected');
        await fs.writeFile(path.join(outDir,sid+'.response.json'),serialized,{flag:'wx'});
        const audit=controls(raw); const cost=conservativeCost(raw);
        const safe=raw.status==='completed' && cost!==null && cost<=RESERVE && !audit.violations.length;
        receipt={sid,status:safe?'completed':'CONTROL_OR_USAGE_STOP',response_id:raw.id,
          usage:raw.usage,controls:audit,charged_usd:safe?cost:Math.max(RESERVE,cost??RESERVE),
          cost_kind:safe?'conservative_estimate':'full_reservation_or_larger_estimate',
          response_sha256:digest(serialized),routes:safe?reviewedRoutes(raw,record):
            {sid,status:'UNACCEPTED',candidates:[],scientific_state_change:false}};
      }
    } catch { /* Unknown completion is never retried automatically. */ }
    await jsonNew(path.join(outDir,sid+'.receipt.json'),receipt);
    reservation.charged_usd=receipt.charged_usd; ledger.push(reservation);
    const tmp=path.join(outDir,'ledger.jsonl.tmp');
    await fs.writeFile(tmp,ledger.map(x=>JSON.stringify(x)).join('\n')+'\n',{flag:'wx'});
    await fs.rename(tmp,path.join(outDir,'ledger.jsonl'));
    return receipt;
  } finally {try {await lock.close();} finally {await fs.unlink(lockFile);}}
}

export async function verifyContinuation(root,outDir) {
  const manifest=await jsonRead(path.join(outDir,'manifest.json')); const errors=[];
  try {await validateManifest(root,outDir,manifest);} catch(e) {errors.push(e.message);}
  const ledger=await ledgerRead(outDir,manifest); const receipts=[];
  for(const r of ledger) {
    const receipt=await jsonRead(path.join(outDir,r.sid+'.receipt.json')); receipts.push(receipt);
    if(receipt.charged_usd!==r.charged_usd) errors.push('cost_mismatch:'+r.sid);
    if(receipt.status==='completed') {
      const raw=await jsonRead(path.join(outDir,r.sid+'.response.json'));
      if(controls(raw).violations.length || conservativeCost(raw)!==r.charged_usd ||
        receipt.response_sha256!==digest(await fs.readFile(path.join(outDir,r.sid+'.response.json'))) ||
        JSON.stringify(reviewedRoutes(raw,manifest.records.find(x=>x.sid===r.sid)))!==JSON.stringify(receipt.routes))
        errors.push('response_mismatch:'+r.sid);
    } else errors.push('noncompleted_attempt:'+r.sid);
  }
  const charged=manifest.carried_prior_estimate_usd+ledger.reduce((n,r)=>n+(r.charged_usd??RESERVE),0);
  if(charged>Math.min(TOTAL_CAP,manifest.tranche_cap_usd)) errors.push('budget_exceeded');
  return {at:new Date().toISOString(),records:manifest.records.length,attempted:ledger.length,
    completed:receipts.filter(x=>x.status==='completed').length,total_estimate_usd:charged,
    prior_estimate_usd:manifest.carried_prior_estimate_usd,overall_cap_usd:TOTAL_CAP,
    tranche_cap_usd:manifest.tranche_cap_usd,errors,scientific_state_change:false,
    candidate_routes:receipts.flatMap(x=>(x.routes?.candidates??[]).map(c=>({sid:x.sid,...c}))),
    controls:receipts.map(x=>({sid:x.sid,...x.controls})),
    further_requests_stop:errors.length>0};
}
