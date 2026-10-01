import assert from 'node:assert/strict';
import * as fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {csvRows, allowedUrl, makeRequest, usageCost, reviewedRoutes,
  runOne, auditControls, SIDS, MODEL, CAP_USD, RESERVE_USD} from './openai_public_si.mjs';

export function runTests() {
  let count=0;
  const test=fn=>{fn();count++;};
  test(()=>assert.deepEqual(csvRows('a,b\r\n"x,y","z""w"\r\n'),[{a:'x,y',b:'z"w'}]));
  test(()=>assert.throws(()=>csvRows('a\n"broken')));
  test(()=>assert.equal(new Set(SIDS).size,10));
  test(()=>assert.equal(allowedUrl('https://www.osti.gov/biblio/1'),true));
  test(()=>assert.equal(allowedUrl('https://osti.gov.evil.example/file'),false));
  test(()=>assert.equal(allowedUrl('https://user:secret@osti.gov/file'),false));
  test(()=>assert.equal(allowedUrl('https://pubs.acs.org/doi/file'),false));
  test(()=>assert.equal(allowedUrl('https://osti.gov.ezproxy.lib.purdue.edu/file'),false));
  test(()=>{const r=makeRequest({sid:'X'});assert.equal(r.model,MODEL);
    assert.equal(r.store,false);assert.equal(r.max_tool_calls,2);
    assert.equal(r.max_output_tokens,4000);assert.equal(r.tools.length,1);});
  test(()=>assert.equal(usageCost({}),null));
  test(()=>assert.equal(usageCost({usage:{input_tokens:1000,output_tokens:1000},
    output:[{type:'web_search_call'}]}),0.01095));
  const record={sid:'X',doi:'10.1/test',previous_public_attempts:[]};
  const candidate={url:'https://osti.gov/item/2',evidence_type:'SI',identity_basis:'DOI',si_basis:'attachment'};
  const response={output:[{type:'web_search_call',status:'completed',action:{sources:[{url:candidate.url}]}},
    {type:'message',content:[{type:'output_text',text:JSON.stringify({sid:'X',doi:'10.1/test',candidates:[candidate]})}]}]};
  test(()=>assert.equal(reviewedRoutes(response,record).candidates.length,1));
  test(()=>assert.equal(reviewedRoutes({...response,output:response.output.slice(1)},record).candidates.length,0));
  test(()=>assert.equal(reviewedRoutes(response,{...record,previous_public_attempts:[{url:candidate.url}]}).candidates.length,0));
  test(()=>assert.equal(reviewedRoutes(response,{...record,sid:'wrong'}).status,'IDENTITY_MISMATCH'));
  test(()=>assert.equal(reviewedRoutes({output:[]},record).status,'UNPARSED'));
  test(()=>assert.equal(reviewedRoutes({output:[{type:'message',content:[{type:'output_text',text:'null'}]}]},record).status,'IDENTITY_MISMATCH'));
  test(()=>assert.equal(reviewedRoutes({output:[{type:'message',content:[{type:'output_text',text:JSON.stringify({...record,candidates:{}})}]}]},record).candidates.length,0));
  test(()=>assert.equal(reviewedRoutes(response,record).scientific_state_change,false));
  test(()=>assert.equal(auditControls(response).violations.length,0));
  test(()=>assert.equal(auditControls({output:[1,2,3].map(()=>({type:'web_search_call',status:'completed'}))}).violations.length,1));
  test(()=>assert.equal(auditControls({output:[{type:'web_search_call',status:'searching'}]}).nonterminal_tool_events,1));
  test(()=>assert.ok(RESERVE_USD>0 && RESERVE_USD<=CAP_USD));
  return {passed:count,failed:0};
}

export async function runStateTests() {
  const root=await fs.mkdtemp(path.join(os.tmpdir(),'electro-public-si-test-'));
  const manifest={model:MODEL,cap_usd:CAP_USD,
    records:['X','Y','Z','W','V'].map(sid=>({sid,doi:'10.1/test'}))};
  let count=0;
  const fresh=async name=>{const p=path.join(root,name);await fs.mkdir(p);return p;};
  const args=outDir=>({apiKey:'test-only-not-a-real-key',projectId:'test',manifest,outDir});
  const failure=async()=>({ok:false,status:400,json:async()=>({error:{code:'test'}})});
  const noLock=async dir=>assert.rejects(fs.access(path.join(dir,'run.lock')),{code:'ENOENT'});
  try {
    const dir=await fresh('concurrency');
    let release,entered;
    const gate=new Promise(resolve=>{release=resolve;});
    const started=new Promise(resolve=>{entered=resolve;});
    const first=runOne({...args(dir),sid:'X',fetchImpl:async()=>{entered();await gate;return failure();}});
    await started;
    await assert.rejects(runOne({...args(dir),sid:'X',fetchImpl:failure}),{code:'EEXIST'});count++;
    release();await first;
    assert.equal((await runOne({...args(dir),sid:'X',fetchImpl:()=>{throw new Error('must not request');}})).status,'ALREADY_ATTEMPTED');
    await noLock(dir);count++;
    for(const sid of ['Y','Z','W']) await runOne({...args(dir),sid,fetchImpl:failure});
    assert.equal((await runOne({...args(dir),sid:'V',fetchImpl:()=>{throw new Error('must not request');}})).status,'BUDGET_STOP');
    await noLock(dir);count++;
    const readFail=await fresh('read-failure');await fs.mkdir(path.join(readFail,'ledger.jsonl'));
    await assert.rejects(runOne({...args(readFail),sid:'X',fetchImpl:failure}));await noLock(readFail);count++;
    const receiptFail=await fresh('receipt-failure');await fs.writeFile(path.join(receiptFail,'X.receipt.json'),'{}');
    await assert.rejects(runOne({...args(receiptFail),sid:'X',fetchImpl:failure}),{code:'EEXIST'});
    await noLock(receiptFail);
    assert.equal((await runOne({...args(receiptFail),sid:'X',fetchImpl:failure})).status,'ALREADY_ATTEMPTED');count++;
    const anomaly=await fresh('control-stop');
    await fs.writeFile(path.join(anomaly,'ledger.jsonl'),JSON.stringify({sid:'X',charged_usd:0.03})+'\n');
    await fs.writeFile(path.join(anomaly,'X.response.json'),JSON.stringify({output:[{type:'web_search_call',status:'searching'}]}));
    assert.equal((await runOne({...args(anomaly),sid:'Y',fetchImpl:()=>{throw new Error('must not request');}})).status,'CONTROL_STOP');
    await noLock(anomaly);count++;
    return {passed:count,failed:0};
  } finally {
    // Only the explicit isolated test directory is removed.
    await fs.rm(root,{recursive:true,force:true});
  }
}
