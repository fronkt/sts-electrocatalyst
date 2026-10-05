import hashlib,json,os,pathlib,subprocess
root=pathlib.Path('C:/Users/frank/sts-electrocatalyst')
phase=root/'results/pa_catalyst_retest_2026-10-04'
phase_rel='results/pa_catalyst_retest_2026-10-04'
launch=json.loads((phase/'launch_summary.json').read_text())
assert launch['job_id']=='21075231' and launch['new_jobs_submitted']==1 and launch['released_once']
assert launch['max_cpu_su']==2048 and launch['max_wall_seconds']==57600 and not launch['automatic_retry']
review=json.loads((phase/'independent_launch_execution_review.json').read_text())
assert review['job_id']==launch['job_id'] and review['decision']=='PASS_ONE_AUTHORIZED_TRIAL_LAUNCH_ONLY' and not review['blocking_findings']
for name,want in review['immutable_receipt_sha256'].items():
 assert hashlib.sha256((phase/name).read_bytes()).hexdigest()==want,name
for name,want in launch['receipt_sha256'].items():
 assert hashlib.sha256((phase/name).read_bytes()).hexdigest()==want,name
pins=json.loads((phase/'independent_launch_review_final_pins.json').read_text())['code_pins']
for rel,want in pins.items():
 assert hashlib.sha256((root/rel).read_bytes()).hexdigest()==want,rel
names=['submission_approval.json','submission_intent.json','submission.json','held_validation_checked.json','release_intent.json','release.json','launch_first_observation.json','launch_summary.json','independent_launch_execution_review.md','independent_launch_execution_review.json','bank_launch_receipts.py','watch-approved-readonly.job.json']
for prefix in ['submit-approved-once','validate-held-approved','release-approved-once']:
 names.extend(prefix+suffix for suffix in ['.job.json','.log','.status.json'])
paths=['tasks/todo.md']+[phase_rel+'/'+name for name in names]
env=dict(os.environ,GIT_TERMINAL_PROMPT='0',GCM_INTERACTIVE='never',GCM_GUI_PROMPT='0')
def git(*args):
 p=subprocess.run(['C:/Program Files/Git/cmd/git.exe','-c','credential.interactive=never','-C',str(root),*args],capture_output=True,env=env,creationflags=0x08000000,timeout=180,check=True)
 return p.stdout
assert git('branch','--show-current').decode().strip()=='r0-catalysis-revival'
assert git('rev-parse','HEAD').decode().strip()=='b21b5eb7452066df994f2289bef0889e3ad9cd4b'
assert not git('diff','--cached','--name-only').strip()
assert set(git('diff','--name-only').decode().splitlines()) <= {'tasks/todo.md'}
for rel in paths:assert (root/rel).is_file(),rel
git('add','-f','--',*paths)
assert set(git('diff','--cached','--name-only').decode().splitlines())==set(paths)
git('-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--cached','--check')
staged_pins={}
for rel in paths:
 data=(root/rel).read_bytes();blob=git('show',':'+rel)
 assert blob in (data,data.replace(b'\r\n',b'\n')),rel
 staged_pins[rel]=hashlib.sha256(blob).hexdigest()
git('commit','-m','Record approved singleton launch and checked resource limits for trial follow-through')
commit=git('rev-parse','HEAD').decode().strip()
git('push','origin','r0-catalysis-revival')
remote=git('ls-remote','origin','refs/heads/r0-catalysis-revival').decode().split()[0]
assert remote==commit
assert not git('diff','--name-only').strip() and not git('diff','--cached','--name-only').strip()
receipt={'successful':True,'commit':commit,'remote_commit':remote,'implementation_commit':launch['implementation_commit'],'job_id':launch['job_id'],'explicit_paths':paths,'staged_blob_pins':staged_pins,'new_jobs_submitted':1,'same_job_released_once':True,'automatic_retry':False,'scientific_outcome_pending':True,'production_accepted':False}
(phase/'launch_publication.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2),flush=True)
