import assert from 'node:assert/strict';
import * as fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {controls,conservativeCost,runContinuationOne,verifyContinuation,
  prepareContinuation,TOTAL_CAP,TRANCHE_CAP,RESERVE} from './openai_public_si_continue.mjs';
import {MODEL,digest} from './openai_public_si.mjs';

export async function runContinuationTests() {
  let passed=0;
  const check=fn=>{fn();passed++;};
  const response=()=>({id:'test-response',status:'completed',max_tool_calls:2,
    usage:{input_tokens:1000,output_tokens:1000},output:[
      {type:'web_search_call',status:'completed',action:{type:'search',queries:['a'],sources:[]}},
      {type:'web_search_call',status:'completed',action:{type:'search',queries:['b'],sources:[]}},
      {type:'message',status:'completed',content:[{type:'output_text',text:JSON.stringify({sid:'S00001',doi:'10.1/test',candidates:[]})}]}]});
  check(()=>assert.equal(TOTAL_CAP,50));
  check(()=>assert.equal(TRANCHE_CAP,5));
  await assert.rejects(prepareContinuation(os.tmpdir(),path.join(os.tmpdir(),'second-ledger'),1),/second budget ledger/);passed++;
  check(()=>assert.equal(controls(response()).violations.length,0));
  const extra=response();extra.output.splice(2,0,{type:'web_search_call',status:'searching',action:{type:'search',queries:['c']}});
  check(()=>assert.equal(controls(extra).violations.length,0));
  check(()=>assert.equal(controls(extra).warnings.length,1));
  const noFinal=structuredClone(extra);noFinal.output.pop();
  check(()=>assert.ok(controls(noFinal).violations.length));
  const unfinishedMessage=structuredClone(extra);unfinishedMessage.output.at(-1).status='in_progress';
  check(()=>assert.ok(controls(unfinishedMessage).violations.length));
  check(()=>assert.equal(conservativeCost(extra),0.03095));
  const bad=structuredClone(extra);bad.output[2].action.sources=[{url:'https://osti.gov/1'}];
  check(()=>assert.ok(controls(bad).violations.length));
  const three=structuredClone(extra);three.output[2].status='completed';
  check(()=>assert.ok(controls(three).violations.includes('completed_tool_limit_exceeded')));
  const early=structuredClone(extra);early.output.reverse();
  check(()=>assert.ok(controls(early).violations.length));
  const incomplete=structuredClone(extra);incomplete.status='incomplete';
  check(()=>assert.ok(controls(incomplete).violations.length));
  check(()=>assert.equal(conservativeCost({}),null));
  check(()=>assert.equal(conservativeCost({usage:{input_tokens:-1,output_tokens:0}}),null));
  const queries=response();queries.output[0].action.queries=['a','b','c'];
  check(()=>assert.equal(conservativeCost(queries),0.04095));

  const temp=await fs.mkdtemp(path.join(os.tmpdir(),'electro-public-si-continue-test-'));
  try {
    const scenario=async (name,carried=0.22567585)=>{
      const outDir=path.join(temp,name);await fs.mkdir(outDir);
      const manifest={model:MODEL,total_cap_usd:TOTAL_CAP,tranche_cap_usd:TRANCHE_CAP,
        reserve_usd:RESERVE,carried_prior_estimate_usd:carried,baseline_hashes:{},
        records:['S00001','S00002','S00003'].map(sid=>({sid,doi:'10.1/test'}))};
      await fs.writeFile(path.join(outDir,'manifest.json'),JSON.stringify(manifest));
      return {root:temp,outDir,manifest,apiKey:'fake-only-test-credential'};
    };
    const ok=async()=>({ok:true,json:async()=>response()});
    const stop=()=>{throw new Error('must not request');};
    const a=await scenario('normal');
    check(()=>assert.equal(a.manifest.carried_prior_estimate_usd,0.22567585));
    assert.equal((await runContinuationOne({...a,sid:'S00001',fetchImpl:ok})).status,'completed');passed++;
    assert.equal((await runContinuationOne({...a,sid:'S00001',fetchImpl:stop})).status,'ALREADY_ATTEMPTED');passed++;
    const verified=await verifyContinuation(temp,a.outDir);
    assert.equal(verified.errors.length,0);assert.equal(verified.total_estimate_usd,0.24662585);passed++;
    const boundary=await scenario('boundary',4);
    assert.equal((await runContinuationOne({...boundary,sid:'S00001',fetchImpl:ok})).status,'completed');passed++;
    const over=await scenario('over',4.000001);
    assert.equal((await runContinuationOne({...over,sid:'S00001',fetchImpl:stop})).status,'BUDGET_STOP');passed++;
    const ambiguous=await scenario('ambiguous');
    assert.equal((await runContinuationOne({...ambiguous,sid:'S00001',fetchImpl:async()=>{throw Error('timeout');}})).charged_usd,RESERVE);passed++;
    assert.equal((await runContinuationOne({...ambiguous,sid:'S00002',fetchImpl:stop})).status,'PRIOR_UNCERTAINTY_STOP');passed++;
    assert.equal((await runContinuationOne({...ambiguous,sid:'S00001',fetchImpl:stop})).status,'ALREADY_ATTEMPTED');passed++;
    const apiError=await scenario('api-error');
    assert.equal((await runContinuationOne({...apiError,sid:'S00001',fetchImpl:async()=>({ok:false,status:401,json:async()=>({})})})).charged_usd,RESERVE);passed++;
    assert.equal((await runContinuationOne({...apiError,sid:'S00002',fetchImpl:stop})).status,'PRIOR_UNCERTAINTY_STOP');passed++;
    const unknown=await scenario('unknown'); const missingUsage=response();delete missingUsage.usage;
    assert.equal((await runContinuationOne({...unknown,sid:'S00001',fetchImpl:async()=>({ok:true,json:async()=>missingUsage})})).charged_usd,RESERVE);passed++;
    assert.equal((await runContinuationOne({...unknown,sid:'S00002',fetchImpl:stop})).status,'PRIOR_UNCERTAINTY_STOP');passed++;
    const missing=await scenario('missing');
    await fs.writeFile(path.join(missing.outDir,'ledger.jsonl'),JSON.stringify({sid:'S00001',reserved_usd:RESERVE,charged_usd:.02})+'\n');
    assert.equal((await runContinuationOne({...missing,sid:'S00002',fetchImpl:stop})).status,'PRIOR_UNCERTAINTY_STOP');passed++;
    for(const [name,rows] of [
      ['negative',[{sid:'S00001',reserved_usd:RESERVE,charged_usd:-1}]],
      ['duplicate',[{sid:'S00001',reserved_usd:RESERVE},{sid:'S00001',reserved_usd:RESERVE}]],
      ['outside',[{sid:'S99999',reserved_usd:RESERVE}]],
      ['reservation',[{sid:'S00001',reserved_usd:.001}]],
    ]) {
      const s=await scenario(name);
      await fs.writeFile(path.join(s.outDir,'ledger.jsonl'),rows.map(x=>JSON.stringify(x)).join('\n')+'\n');
      await assert.rejects(runContinuationOne({...s,sid:'S00002',fetchImpl:stop}));passed++;
      await assert.rejects(fs.access(path.join(s.outDir,'run.lock')),{code:'ENOENT'});passed++;
    }
    const baseline=await scenario('baseline');
    baseline.manifest.baseline_hashes['pin.txt']=digest('pinned');
    await fs.writeFile(path.join(temp,'pin.txt'),'modified');
    await fs.writeFile(path.join(baseline.outDir,'manifest.json'),JSON.stringify(baseline.manifest));
    await assert.rejects(runContinuationOne({...baseline,sid:'S00001',fetchImpl:stop}),/baseline_changed/);passed++;
    const concurrency=await scenario('concurrency');let release,entered;
    const gate=new Promise(r=>release=r);const start=new Promise(r=>entered=r);
    const first=runContinuationOne({...concurrency,sid:'S00001',fetchImpl:async()=>{entered();await gate;return ok();}});
    await start;
    await assert.rejects(runContinuationOne({...concurrency,sid:'S00002',fetchImpl:stop}),{code:'EEXIST'});passed++;
    release();await first;
    const excessive=await scenario('excessive');
    const receipt=await runContinuationOne({...excessive,sid:'S00001',fetchImpl:async()=>({ok:true,json:async()=>three})});
    assert.equal(receipt.status,'CONTROL_OR_USAGE_STOP');passed++;
    assert.equal((await runContinuationOne({...excessive,sid:'S00002',fetchImpl:stop})).status,'PRIOR_UNCERTAINTY_STOP');passed++;
    const tampered=await scenario('tampered');
    await assert.rejects(runContinuationOne({...tampered,manifest:{...tampered.manifest,total_cap_usd:500},sid:'S00001',fetchImpl:stop}),/invalid manifest/);passed++;
    return {passed,failed:0};
  } finally {
    // Only this explicit mkdtemp test directory is removed, never a workspace.
    await fs.rm(temp,{recursive:true,force:true});
  }
}
