"""Publish reviewed offline repair and receipts, without staging or running QE."""
import ast,hashlib,importlib.util,json,os
from pathlib import Path
import subprocess
PHASE=Path(__file__).resolve().parent;ROOT=PHASE.parents[1]
TARGET=PHASE/'publication.json';assert not TARGET.exists()
ENV=dict(os.environ,GIT_TERMINAL_PROMPT='0',GCM_INTERACTIVE='never',GCM_GUI_PROMPT='0')
REPORT={'successful':False,'commands':[],'scope':'OFFLINE_XML_REPAIR_ONLY','new_jobs_submitted':0,'qe_executed':False,'production_accepted':False}
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def git(*args,timeout=50,binary=False):
 command=['git','-c','credential.interactive=never',*args]
 p=subprocess.run(command,cwd=ROOT,env=ENV,capture_output=True,timeout=timeout,creationflags=0x08000000)
 row={'args':command,'returncode':p.returncode}
 if not binary:row.update(stdout=p.stdout.decode('utf-8','replace'),stderr=p.stderr.decode('utf-8','replace'))
 REPORT['commands'].append(row);assert p.returncode==0,(command,row.get('stderr'))
 return p.stdout if binary else p.stdout.decode('utf-8').strip()
try:
 spec=importlib.util.spec_from_file_location('repair_publication_preserve',PHASE/'verify_repair.py');verify=importlib.util.module_from_spec(spec);spec.loader.exec_module(verify)
 REPORT['before']=verify.preserve()
 checked=json.loads((PHASE/'verification_checked.json').read_text());raw=json.loads((PHASE/'raw_replay_checked.json').read_text())
 assert checked['successful'] and raw['successful'] and raw['complete_trial_pass'] is False
 for rel,pin in checked['code_pins'].items():assert sha(ROOT/rel)==pin,'reviewed code drift: '+rel
 review=PHASE/'independent_repair_review.md'
 assert 'Decision: GO_OFFLINE_XML_REPAIR_ONLY' in review.read_text(encoding='utf-8')
 REPORT['review_sha256']=sha(review)
 assert git('rev-parse','HEAD')=='cbf7c7d81dc42b05bf81ca952d57dda8bafaa2a5'
 assert git('branch','--show-current')=='r0-catalysis-revival'
 assert not git('diff','--cached','--name-only'),'unrecognized staged work'
 existing=['src/dft/pa_qe_adapter.py','tests/test_pa_qe_adapter.py','tasks/todo.md']
 assert set(git('diff','--name-only').splitlines())==set(existing),'unexpected existing-path edits'
 background=Path('C:/Users/frank/AppData/Local/Temp/sts-background-2026-09-06')
 retention=['pa-xml-repair-baseline-2026-10-04.log','pa-xml-repair-baseline-2026-10-04.status.json','pa-xml-repair-verification-initial-2026-10-04.log','pa-xml-repair-verification-initial-2026-10-04.status.json','pa-xml-repair-verification-checked-2026-10-04.status.json']
 for name in retention:
  destination=PHASE/name;assert not destination.exists();destination.write_bytes((background/name).read_bytes())
 phase_files=['.gitattributes','baseline.json','capture_baseline.py','git_inspection.json','launch_adapter_original.py','replay_control.py','source_schema_review.md','terminal_trial_observations.jsonl','terminal_trial_watch_status.json','verification_initial.json','verification_checked.json','verify_repair.py','raw_replay_checked.json','independent_repair_review.md','publish_repair.py','scientific_checked/verification.json','scientific_checked/si_round_verification.json',*retention]
 paths=sorted(existing+['tests/test_pa_qe_schema_repair.py','docs/research/pa-xml-repair-2026-10-04.md']+['results/pa_xml_repair_2026-10-04/'+name for name in phase_files])
 REPORT['paths']=paths
 for rel in paths:
  assert (ROOT/rel).is_file(),rel
  if rel.endswith('.py'):ast.parse((ROOT/rel).read_text(encoding='utf-8'),filename=rel)
 git('add','-f','--',*paths)
 assert set(git('diff','--cached','--name-only').splitlines())==set(paths)
 git('-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--cached','--check')
 REPORT['local_pins']={p:sha(ROOT/p) for p in paths};REPORT['blob_pins']={}
 for rel in paths:
  blob=git('show',':'+rel,binary=True);data=(ROOT/rel).read_bytes()
  if rel.startswith('results/pa_xml_repair_2026-10-04/') or rel in checked['code_pins']:assert blob==data,'reviewed/pinned byte transformation: '+rel
  else:assert blob in (data,data.replace(b'\r\n',b'\n')),'unexpected native Git transformation: '+rel
  REPORT['blob_pins'][rel]={'sha256':hashlib.sha256(blob).hexdigest(),'bytes':len(blob)}
 git('commit','-m','Repair QE7.5 Hubbard XML validation and verify retained catalyst control offline',timeout=100)
 REPORT['commit']=git('rev-parse','HEAD');git('push','origin','r0-catalysis-revival',timeout=180)
 REPORT['remote_commit']=git('ls-remote','origin','refs/heads/r0-catalysis-revival',timeout=90).split()[0]
 assert REPORT['remote_commit']==REPORT['commit']
 assert not git('diff','--name-only') and not git('diff','--cached','--name-only')
 REPORT['after']=verify.preserve()
 for rel,pin in REPORT['local_pins'].items():assert sha(ROOT/rel)==pin,'postpublication drift: '+rel
 REPORT['successful']=True
except BaseException as exc:REPORT['error']=repr(exc);raise
finally:TARGET.write_text(json.dumps(REPORT,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:REPORT[k] for k in ['successful','commit','remote_commit','after','new_jobs_submitted','qe_executed']},indent=2),flush=True)
