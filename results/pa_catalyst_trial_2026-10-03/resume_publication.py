"""Resume only the known staged package after a CRLF-only whitespace refusal."""
import hashlib,importlib.util,json,os,pathlib,subprocess
PHASE=pathlib.Path(__file__).resolve().parent;ROOT=PHASE.parents[1]
TARGET=PHASE/'publication_checked.json';assert not TARGET.exists()
ENV=dict(os.environ,GIT_TERMINAL_PROMPT='0',GCM_INTERACTIVE='never',GCM_GUI_PROMPT='0')
report={'successful':False,'commands':[],'new_jobs_submitted':0,'qe_executed':False,'production_accepted':False}
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 return h.hexdigest()
def git(*args,timeout=45,binary=False):
 cmd=['git','-c','credential.interactive=never',*args]
 p=subprocess.run(cmd,cwd=ROOT,env=ENV,capture_output=True,timeout=timeout,creationflags=0x08000000)
 row={'args':cmd,'returncode':p.returncode}
 if not binary:row.update(stdout=p.stdout.decode('utf-8','replace'),stderr=p.stderr.decode('utf-8','replace'))
 report['commands'].append(row);assert p.returncode==0,(cmd,p.returncode,row.get('stderr',''))
 return p.stdout if binary else p.stdout.decode('utf-8').strip()
try:
 initial=json.loads((PHASE/'publication.json').read_text());assert not initial['successful'] and not initial.get('commit')
 failed=initial['commands'][-1];assert failed['args'][-3:]==['diff','--cached','--check'] and failed['returncode']==2
 assert git('rev-parse','HEAD')=='20119bb5cedea1ac957920133a6f7ff3396f7924'
 assert git('branch','--show-current')=='r0-catalysis-revival'
 old_paths=json.loads((PHASE/'commit_paths.json').read_text())['paths']
 assert set(git('diff','--cached','--name-only').splitlines())==set(old_paths),'unknown staged files'
 checked=json.loads((PHASE/'offline_checked.json').read_text());assert checked['successful']
 for rel,pin in checked['code_pins'].items():assert digest(ROOT/rel)==pin,'tested byte drift: '+rel
 assert digest(PHASE/'independent_launch_review_final.md')=='0d8c4e0ea2eb4775fe5bf233326f8d5c86c765bb133ce1163cb9c2c49761d587'
 summary={'successful':False,'category':'PRESERVED_CRLF_WHITESPACE_CHECK_ONLY','original_receipt':'publication.json',
  'original_bytes':(PHASE/'publication.json').stat().st_size,'original_sha256':digest(PHASE/'publication.json'),
  'failed_args':failed['args'],'returncode':failed['returncode'],'diagnostic_lines':len(failed['stdout'].splitlines()),
  'diagnostic_prefix':failed['stdout'][:1200],'new_jobs_submitted':0,'qe_executed':False,'scientific_bytes_unchanged':True}
 (PHASE/'publication_initial_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 new_paths=['results/pa_catalyst_trial_2026-10-03/resume_publication.py','results/pa_catalyst_trial_2026-10-03/publication_initial_summary.json']
 paths=sorted(set(old_paths+new_paths));report['paths']=paths
 (PHASE/'commit_paths.json').write_text(json.dumps({'paths':paths,'source_cache_payloads_excluded':True,'unrelated_dft_excluded':True,'native_receipt_bytes_preserved':True},indent=2)+'\n')
 git('add','-f','--',*new_paths,'results/pa_catalyst_trial_2026-10-03/commit_paths.json')
 assert set(git('diff','--cached','--name-only').splitlines())==set(paths)
 # CR at a line ending is intentional raw data, not trailing spaces. This
 # per-command rule changes no file/config/global newline policy.
 git('-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--cached','--check')
 report['local_pins']={rel:digest(ROOT/rel) for rel in paths}
 for rel in paths:
  data=(ROOT/rel).read_bytes();expected=data if rel.startswith('results/pa_catalyst_trial_2026-10-03/') else data.replace(b'\r\n',b'\n')
  assert git('show',':'+rel,binary=True)==expected,'staged bytes differ: '+rel
 spec=importlib.util.spec_from_file_location('trial_publication_preserve',PHASE/'verify_trial_offline.py')
 verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier);report['before']=verifier.preserve()
 git('commit','-m','Add source-bound catalyst restart trial with capped resource guards',timeout=90)
 report['commit']=git('rev-parse','HEAD');git('push','origin','r0-catalysis-revival',timeout=180)
 remote=git('ls-remote','origin','refs/heads/r0-catalysis-revival',timeout=90).split()[0]
 assert remote==report['commit'];report['remote_commit']=remote
 assert not git('diff','--name-only') and not git('diff','--cached','--name-only')
 report['after']=verifier.preserve()
 for rel,pin in report['local_pins'].items():assert digest(ROOT/rel)==pin,'post-publication drift: '+rel
 report['successful']=True
except BaseException as exc:report['error']=repr(exc);raise
finally:TARGET.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'successful':True,'commit':report['commit'],'remote_commit':report['remote_commit'],'explicit_paths':len(paths),'preserved':report['after'],'new_jobs_submitted':0},indent=2))
