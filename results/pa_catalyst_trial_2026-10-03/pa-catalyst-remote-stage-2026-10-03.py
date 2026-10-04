import hashlib,json,pathlib,subprocess
root=pathlib.Path.cwd();phase=root/'results/pa_catalyst_trial_2026-10-03';target=phase/'remote_stage.json';assert not target.exists()
published=json.loads((phase/'publication_final.json').read_text());assert published['successful'] and published['commit']==published['remote_commit']
paths=published['paths']+['.gitattributes','src/dft/pa_checked_contract.py','runs/hea/lowtail_low_state_restart_2026-09-22/Cu8Cr23Mn35Co34__s20_site2/slab_c5low__relax.in']
pins=dict(published['staged_blob_pins'],**published['additional_blob_pins'])
for rel,pin in published['local_pins'].items():assert hashlib.sha256((root/rel).read_bytes()).hexdigest()==pin
remote='commit='+repr(published['commit'])+'\npins='+repr(pins)+'\n'+r'''import hashlib,json,os,pathlib,subprocess,sys
base=pathlib.Path('/anvil/projects/x-che260157');root=base/'sts_pa_catalyst_2026-10-03'
assert root.parent.resolve()==base.resolve() and root.name=='sts_pa_catalyst_2026-10-03'
assert not root.exists() and not root.is_symlink(),'no existing checkout or output may be overwritten'
r={'successful':False,'commit':commit,'commands':{},'pins':[],'new_jobs_submitted':0,'qe_executed':False,'production_accepted':False}
env=dict(os.environ,GIT_TERMINAL_PROMPT='0',GCM_INTERACTIVE='never')
def run(name,args,timeout=60,input=None):
 p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,env=env,timeout=timeout,input=input)
 r['commands'][name]={'args':args,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr};assert p.returncode==0,(name,p.stderr)
 return p.stdout
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as stream:
  for data in iter(lambda:stream.read(1048576),b''):h.update(data)
 return h.hexdigest()
try:
 run('clone',['git','-c','credential.interactive=never','clone','--filter=blob:none','--no-checkout','--single-branch','--branch','r0-catalysis-revival','https://github.com/fronkt/sts-electrocatalyst.git',str(root)],timeout=140)
 run('sparse',['git','-C',str(root),'sparse-checkout','set','--no-cone','--stdin'],input='\n'.join('/'+p for p in sorted(pins))+'\n')
 run('checkout',['git','-C',str(root),'checkout','--detach',commit],timeout=90)
 assert run('head',['git','-C',str(root),'rev-parse','HEAD']).strip()==commit
 for rel,pin in pins.items():
  path=root/rel;assert path.is_file() and not path.is_symlink() and path.stat().st_nlink==1
  assert path.stat().st_size==pin['bytes'] and digest(path)==pin['sha256'],'staged byte mismatch: '+rel
  r['pins'].append(dict(path=rel,**pin))
 phase=root/'results/pa_catalyst_trial_2026-10-03';spec=phase/'launch_spec.json'
 assert digest(spec)=='4bed5002a88857515940230b20ad59e6adc345e29d8567d5b9c5f5511b0b28a2'
 run('wrapper_syntax',['bash','-n',str(root/'anvil/89_pa_catalyst_boundary_trial.slurm')])
 run('preflight',[sys.executable,str(root/'src/dft/pa_catalyst_trial.py'),'--spec',str(spec),'--spec-sha256',digest(spec),'--preflight'],timeout=70)
 run('balance',['bash','-lc','mybalance'],timeout=20)
 run('queue',['squeue','-h','-u','x-fcai3','-o','%i|%T|%j|%C|%R'])
 run('partition',['scontrol','show','partition','wholenode','-o'])
 run('quota',['bash','-lc','myquota'],timeout=20)
 assert not r['commands']['queue']['stdout'].strip(),'existing job requires scoped queue check before singleton submission'
 assert not (root/'trial_results').exists()
 r['successful']=True
except BaseException as exc:r['error']=repr(exc);raise
finally:
 if root.is_dir():(root/'remote_stage_receipt.json').write_text(json.dumps(r,indent=2)+'\n')
 print(json.dumps(r,indent=2))
'''
print('Stage exact published checkpoint',published['commit'],'without QE/job calls',flush=True)
p=subprocess.run(['C:/Program Files/Git/usr/bin/ssh.exe','-i','C:/Users/frank/.ssh/id_ed25519','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=12','x-fcai3@anvil.rcac.purdue.edu','/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3 -'],input=remote,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=360,creationflags=0x08000000)
r={'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'published_commit':published['commit'],'read_only_historical_sources':True,'new_jobs_submitted':0,'qe_executed':False}
target.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print('Remote stage returncode',p.returncode,flush=True)
if p.returncode:print(p.stderr[-5000:],flush=True)
assert p.returncode==0 and json.loads(p.stdout)['successful']
