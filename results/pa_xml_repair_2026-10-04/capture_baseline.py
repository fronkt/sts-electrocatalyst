"""Pin repair scope and immutable launch history before local validator edits."""
import hashlib,json,os
from pathlib import Path
import subprocess
PHASE=Path(__file__).resolve().parent;ROOT=PHASE.parents[1]
TARGET=PHASE/'baseline.json';assert not TARGET.exists()
ENV=dict(os.environ,GIT_TERMINAL_PROMPT='0',GCM_INTERACTIVE='never',GCM_GUI_PROMPT='0')
def git(*args):
 p=subprocess.run(['git','-c','credential.interactive=never',*args],cwd=ROOT,env=ENV,capture_output=True,timeout=40,creationflags=0x08000000)
 assert p.returncode==0,p.stderr
 return p.stdout.decode('utf-8').strip()
def pin(rel):
 p=ROOT/rel;h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return {'path':rel,'bytes':p.stat().st_size,'sha256':h.hexdigest()}
r={'head':git('rev-parse','HEAD'),'branch':git('branch','--show-current'),'intentional_edit_paths':['src/dft/pa_qe_adapter.py','tasks/todo.md'],'new_jobs_submitted':0,'qe_executed':False,'production_accepted':False}
assert r['head']=='cbf7c7d81dc42b05bf81ca952d57dda8bafaa2a5'
r['checkpoint_reconciliation']='Four intervening clean commits inspected: existing catalyst mirror/dry-run/readout and unrelated public-SI recovery preserved. No expensive mirror/readout repeat.'
assert r['branch']=='r0-catalysis-revival'
assert not git('diff','--name-only') and not git('diff','--cached','--name-only')
tracked=git('ls-files').splitlines();r['tracked_pins']=[pin(x) for x in tracked]
old=json.loads((ROOT/'results/pa_catalyst_trial_2026-10-03/baseline.json').read_text())
r['unrelated_pins']=[pin(x['path']) for x in old['untracked_pins']]
for row,before in zip(r['unrelated_pins'],old['untracked_pins']):assert row==before
original=PHASE/'launch_adapter_original.py';assert not original.exists()
original.write_bytes((ROOT/'src/dft/pa_qe_adapter.py').read_bytes())
assert hashlib.sha256(original.read_bytes()).hexdigest()=='255464215aa898d0c9d34317a1be9b16fb27ba6d35108e0ca78215331a628879'
for name in ['trial_watch_status.json','trial_observations.jsonl']:
 source=ROOT/'results/pa_catalyst_trial_2026-10-03'/name;dest=PHASE/('terminal_'+name)
 assert not dest.exists();dest.write_bytes(source.read_bytes())
TARGET.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'head':r['head'],'tracked':len(r['tracked_pins']),'unrelated':len(r['unrelated_pins']),'intentional_edits':r['intentional_edit_paths']},indent=2),flush=True)
