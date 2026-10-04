import json,pathlib,subprocess
phase=pathlib.Path.cwd()/'results/pa_catalyst_trial_2026-10-03';target=phase/'release.json';assert not target.exists()
submission=json.loads((phase/'submission.json').read_text())
validated=json.loads((phase/'held_validation_checked.json').read_text());assert validated['returncode']==0 and json.loads(validated['stdout'])['held_shape_validated']
job=submission['job_id'];assert job.isdigit()
remote='job='+repr(job)+'\n'+r'''import hashlib,json,pathlib,re,subprocess
root=pathlib.Path('/anvil/projects/x-che260157/sts_pa_catalyst_2026-10-03');phase=root/'results/pa_catalyst_trial_2026-10-03'
receipt=phase/'release_remote.json';assert not receipt.exists()
r={'successful':False,'job_id':job,'released':False,'automatic_retry':False,'commands':{},'production_accepted':False}
def run(name,args,timeout=25):
 p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,timeout=timeout)
 r['commands'][name]={'args':args,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr};assert p.returncode==0,(name,p.stderr)
 return p.stdout
try:
 submitted=json.loads((phase/'submission_remote.json').read_text());assert submitted['job_id']==job
 validated=json.loads((phase/'held_validation_checked_remote.json').read_text());assert validated['successful'] and validated['job_id']==job and validated['held_shape_validated']
 spec=phase/'launch_spec.json';digest=hashlib.sha256(spec.read_bytes()).hexdigest();assert digest=='4bed5002a88857515940230b20ad59e6adc345e29d8567d5b9c5f5511b0b28a2'
 run('fresh_preflight',['/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3',str(root/'src/dft/pa_catalyst_trial.py'),'--spec',str(spec),'--spec-sha256',digest,'--preflight'],timeout=70)
 held=run('held_before_release',['scontrol','show','job',job,'-o']);f=dict(re.findall(r'(?:^|\s)([^\s=]+)=([^\s]+)',held))
 expected={'JobId':job,'JobState':'PENDING','Reason':'JobHeldUser','Account':'che260157','Partition':'wholenode','NumCPUs':'128','NumTasks':'128','CPUs/Task':'1','TimeLimit':'16:00:00','Requeue':'0','Restarts':'0','BatchFlag':'1','Dependency':'(null)'}
 assert all(f.get(k)==v for k,v in expected.items()) and not any(k.startswith('Array') for k in f)
 assert f['NumNodes'] in {'1','1-1'},'pending node bounds must both equal1'
 assert dict(x.split('=',1) for x in f['ReqTRES'].split(','))=={'cpu':'128','mem':'200G','node':'1','billing':'128'}
 balance=run('balance',['bash','-lc','mybalance']);rows=[line.split() for line in balance.splitlines()];cpu=[row for row in rows if len(row)==6 and row[:2]==['che260157','CPU']];assert len(cpu)==1 and float(cpu[0][-1])>=2048
 queue=run('queue',['squeue','-h','-u','x-fcai3','-o','%i|%T|%j|%C|%R']);assert [line.split('|')[0] for line in queue.splitlines() if line.strip()]==[job]
 r['release_intent']=True;receipt.write_text(json.dumps(r,indent=2)+'\n')
 run('release',['scontrol','release',job]);r['released']=True
 run('job_after_release',['scontrol','show','job',job,'-o']);r['successful']=True
except BaseException as exc:r['error']=repr(exc);raise
finally:receipt.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
'''
p=subprocess.run(['C:/Program Files/Git/usr/bin/ssh.exe','-i','C:/Users/frank/.ssh/id_ed25519','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=12','x-fcai3@anvil.rcac.purdue.edu','/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3 -'],input=remote,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=135,creationflags=0x08000000)
r={'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'job_id':job,'automatic_retry':False,'production_accepted':False}
target.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print('Release returncode',p.returncode,'job',job,flush=True)
if p.returncode:print(p.stderr[-4000:],flush=True)
assert p.returncode==0 and json.loads(p.stdout)['released']
