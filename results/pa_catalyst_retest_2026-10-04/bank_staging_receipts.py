import hashlib,json,os,pathlib,subprocess
root=pathlib.Path("C:/Users/frank/sts-electrocatalyst")
phase=root/'results/pa_catalyst_retest_2026-10-04'
phase_rel='results/pa_catalyst_retest_2026-10-04'
summary=json.loads((phase/'anvil_preflight_summary.json').read_text())
assert summary['state']=='PREFLIGHT_PASS_AWAITING_SUBMISSION_APPROVAL' and summary['new_jobs_submitted']==0 and summary['preflight_cpu_su']==0
assert (phase/'staging_independent_review.md').is_file() and (phase/'staging_independent_review.json').is_file()
names=['staging_approval.json','staging_materialization.json','staging_materialization_refusal.json','staging_transport_note.md','stage_reviewed_snapshot.py','stage_reviewed_snapshot_blobs.py','remote_stage.json','anvil_preflight_summary.json','staging_independent_review.md','staging_independent_review.json','completion_pending_submission.json','bank_staging_receipts.py']
for prefix in ['anvil-stage-approved','anvil-stage-approved-blobs','staging-materialization-diagnosis']:
 names.extend(prefix+suffix for suffix in ['.job.json','.log','.status.json'])
paths=['tasks/todo.md']+[phase_rel+'/'+name for name in names]
env=dict(os.environ,GIT_TERMINAL_PROMPT='0',GCM_INTERACTIVE='never',GCM_GUI_PROMPT='0')
def git(*args):
 p=subprocess.run(['C:/Program Files/Git/cmd/git.exe','-c','credential.interactive=never','-C',str(root),*args],capture_output=True,env=env,creationflags=0x08000000,timeout=180,check=True)
 return p.stdout
assert git('branch','--show-current').decode().strip()=='r0-catalysis-revival'
assert not git('diff','--cached','--name-only').strip()
assert set(git('diff','--name-only').decode().splitlines()) <= {'tasks/todo.md'}
for rel in paths:assert (root/rel).is_file(),rel
git('add','-f','--',*paths)
assert set(git('diff','--cached','--name-only').decode().splitlines())==set(paths)
git('-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--cached','--check')
for rel in paths:
 data=(root/rel).read_bytes();blob=git('show',':'+rel)
 assert blob in (data,data.replace(b'\r\n',b'\n')),rel
git('commit','-m','Bank approved Anvil staging and exact preflight proof before trial submission')
commit=git('rev-parse','HEAD').decode().strip()
git('push','origin','r0-catalysis-revival')
remote=git('ls-remote','origin','refs/heads/r0-catalysis-revival').decode().split()[0]
assert remote==commit
assert not git('diff','--name-only').strip() and not git('diff','--cached','--name-only').strip()
receipt={'successful':True,'commit':commit,'remote_commit':remote,'implementation_commit':summary['implementation_commit'],'explicit_paths':paths,'preflight_cpu_su':0,'new_jobs_submitted':0,'submission_approval_pending':True}
(phase/'staging_publication.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2),flush=True)
