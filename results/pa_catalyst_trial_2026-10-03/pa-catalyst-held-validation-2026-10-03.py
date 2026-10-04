import json,pathlib,subprocess
phase=pathlib.Path.cwd()/'results/pa_catalyst_trial_2026-10-03';target=phase/'held_validation_checked.json';assert not target.exists()
submitted=json.loads((phase/'submission.json').read_text());job=submitted['job_id'];assert job=='21034683'
remote='job='+repr(job)+'\n'+r'''import json,pathlib,re,subprocess
root=pathlib.Path('/anvil/projects/x-che260157/sts_pa_catalyst_2026-10-03');phase=root/'results/pa_catalyst_trial_2026-10-03'
original=json.loads((phase/'submission_remote.json').read_text());assert original['job_id']==job and original['error']=="AssertionError('held requested shape mismatch; leave held, no replacement')"
p=subprocess.run(['scontrol','show','job',job,'-o'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,timeout=20);assert p.returncode==0
f=dict(re.findall(r'(?:^|\s)([^\s=]+)=([^\s]+)',p.stdout))
expected={'JobId':job,'JobState':'PENDING','Reason':'JobHeldUser','Account':'che260157','Partition':'wholenode','JobName':'pa-catalyst-boundary','NumCPUs':'128','NumTasks':'128','CPUs/Task':'1','TimeLimit':'16:00:00','Requeue':'0','Restarts':'0','BatchFlag':'1','Dependency':'(null)','Exclusive':'NODE','OverSubscribe':'NO'}
assert all(f.get(k)==v for k,v in expected.items()) and not any(k.startswith('Array') for k in f)
assert f['NumNodes'] in {'1','1-1'},'pending node bounds must both equal1'
assert dict(piece.split('=',1) for piece in f['ReqTRES'].split(','))=={'cpu':'128','mem':'200G','node':'1','billing':'128'}
assert f['Command']==str(root/'anvil/89_pa_catalyst_boundary_trial.slurm') and f['WorkDir']==str(root)
r={'successful':True,'job_id':job,'held_shape_validated':True,'raw_scontrol':p.stdout,'stderr':p.stderr,'pending_num_nodes_raw':f['NumNodes'],'pending_node_lower_bound':1,'pending_node_upper_bound':1,'max_cpu_su':2048,'new_jobs_submitted':0,'qe_executed':False,'production_accepted':False}
(phase/'held_validation_checked_remote.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
'''
p=subprocess.run(['C:/Program Files/Git/usr/bin/ssh.exe','-i','C:/Users/frank/.ssh/id_ed25519','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=12','x-fcai3@anvil.rcac.purdue.edu','/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3 -'],input=remote,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=40,creationflags=0x08000000)
r={'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'job_id':job,'new_jobs_submitted':0,'qe_executed':False}
target.write_text(json.dumps(r,indent=2)+'\n');print('Held exactsingleton validation returncode',p.returncode,'job',job);assert p.returncode==0 and json.loads(p.stdout)['successful']
