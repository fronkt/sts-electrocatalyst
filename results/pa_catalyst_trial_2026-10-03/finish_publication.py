"""Publish the known index using native per-path Git bytes, not EOL guesses."""
import hashlib,importlib.util,json,os,pathlib,subprocess
PHASE=pathlib.Path(__file__).resolve().parent;ROOT=PHASE.parents[1]
TARGET=PHASE/'publication_final.json';assert not TARGET.exists()
ENV=dict(os.environ,GIT_TERMINAL_PROMPT='0',GCM_INTERACTIVE='never',GCM_GUI_PROMPT='0')
r={'successful':False,'commands':[],'new_jobs_submitted':0,'qe_executed':False,'production_accepted':False}
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for data in iter(lambda:f.read(1048576),b''):h.update(data)
 return h.hexdigest()
def git(*args,timeout=45,binary=False):
 cmd=['git','-c','credential.interactive=never',*args]
 p=subprocess.run(cmd,cwd=ROOT,env=ENV,capture_output=True,timeout=timeout,creationflags=0x08000000)
 row={'args':cmd,'returncode':p.returncode}
 if not binary:row.update(stdout=p.stdout.decode('utf-8','replace'),stderr=p.stderr.decode('utf-8','replace'))
 r['commands'].append(row);assert p.returncode==0,(cmd,p.returncode,row.get('stderr',''))
 return p.stdout if binary else p.stdout.decode('utf-8').strip()
try:
 failed=json.loads((PHASE/'publication_checked.json').read_text())
 assert not failed['successful'] and not failed.get('commit') and failed['error']=="AssertionError('staged bytes differ: tasks/todo.md')"
 assert git('rev-parse','HEAD')=='20119bb5cedea1ac957920133a6f7ff3396f7924'
 assert git('branch','--show-current')=='r0-catalysis-revival'
 paths=json.loads((PHASE/'commit_paths.json').read_text())['paths']
 assert set(git('diff','--cached','--name-only').splitlines())==set(paths),'unrecognized staged work'
 checked=json.loads((PHASE/'offline_checked.json').read_text());assert checked['successful']
 for rel,pin in checked['code_pins'].items():assert digest(ROOT/rel)==pin,'tested byte drift: '+rel
 assert digest(PHASE/'independent_launch_review_final.md')=='0d8c4e0ea2eb4775fe5bf233326f8d5c86c765bb133ce1163cb9c2c49761d587'
 r['native_attributes']=git('check-attr','text','eol','--','tasks/todo.md','docs/research/pa-catalyst-trial-2026-10-03.md')
 extra=['results/pa_catalyst_trial_2026-10-03/finish_publication.py','results/pa_catalyst_trial_2026-10-03/publication_checked.json']
 paths=sorted(set(paths+extra));r['paths']=paths
 (PHASE/'commit_paths.json').write_text(json.dumps({'paths':paths,'source_cache_payloads_excluded':True,'unrelated_dft_excluded':True,'native_receipt_bytes_preserved':True},indent=2)+'\n')
 git('add','-f','--',*extra,'results/pa_catalyst_trial_2026-10-03/commit_paths.json')
 assert set(git('diff','--cached','--name-only').splitlines())==set(paths)
 git('-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--cached','--check')
 r['local_pins']={rel:digest(ROOT/rel) for rel in paths};r['staged_blob_pins']={}
 for rel in paths:
  blob=git('show',':'+rel,binary=True);data=(ROOT/rel).read_bytes()
  if rel.startswith('results/pa_catalyst_trial_2026-10-03/') or rel in checked['code_pins']:assert blob==data,'scientific/receipt Git byte mismatch: '+rel
  else:assert blob in (data,data.replace(b'\r\n',b'\n')),'unexpected native Git transformation: '+rel
  r['staged_blob_pins'][rel]={'sha256':hashlib.sha256(blob).hexdigest(),'bytes':len(blob)}
 spec=importlib.util.spec_from_file_location('trial_native_publication_preserve',PHASE/'verify_trial_offline.py')
 verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier);r['before']=verifier.preserve()
 git('commit','-m','Add source-bound catalyst restart trial with capped resource guards',timeout=90)
 r['commit']=git('rev-parse','HEAD');git('push','origin','r0-catalysis-revival',timeout=180)
 remote=git('ls-remote','origin','refs/heads/r0-catalysis-revival',timeout=90).split()[0]
 assert remote==r['commit'];r['remote_commit']=remote
 r['additional_blob_pins']={}
 for rel in ['.gitattributes','src/dft/pa_checked_contract.py','runs/hea/lowtail_low_state_restart_2026-09-22/Cu8Cr23Mn35Co34__s20_site2/slab_c5low__relax.in']:
  blob=git('show','HEAD:'+rel,binary=True);r['additional_blob_pins'][rel]={'sha256':hashlib.sha256(blob).hexdigest(),'bytes':len(blob)}
 assert not git('diff','--name-only') and not git('diff','--cached','--name-only')
 r['after']=verifier.preserve()
 for rel,pin in r['local_pins'].items():assert digest(ROOT/rel)==pin,'post-publication drift: '+rel
 r['successful']=True
except BaseException as exc:r['error']=repr(exc);raise
finally:TARGET.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'successful':True,'commit':r['commit'],'remote_commit':r['remote_commit'],'explicit_paths':len(paths),'preserved':r['after'],'new_jobs_submitted':0},indent=2))
