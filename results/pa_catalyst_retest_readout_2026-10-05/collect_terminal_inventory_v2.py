"""Read-only terminal inventory for the single approved catalyst re-test."""
from pathlib import Path
import datetime, hashlib, json, os, shutil, subprocess
ROOT=Path.cwd()
OUT=ROOT/'results/pa_catalyst_retest_readout_2026-10-05'
SSH=['C:/Program Files/Git/usr/bin/ssh.exe','-i','C:/Users/frank/.ssh/id_ed25519','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=12','x-fcai3@anvil.rcac.purdue.edu']
REMOTE='/anvil/projects/x-che260157/sts_pa_catalyst_retest_2026-10-04'
SCRIPT=r'''from pathlib import Path
import datetime,hashlib,json,subprocess,os
base=Path('/anvil/projects/x-che260157/sts_pa_catalyst_retest_2026-10-04')
job='21075231'
result={'job_id':job,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'readonly':True,'qe_executed':False,'remote_root':str(base),'commands':{}}
commands={
 'accounting':['sacct','-n','-P','-j',job,'--format=JobIDRaw,State,ExitCode,Start,End,ElapsedRaw,AllocCPUS,ReqMem,AllocTRES,CPUTimeRAW'],
 'queue':['squeue','-h','-j',job,'-o','%i|%T|%M|%C|%R'],
 'job':['scontrol','show','job',job,'-o'],
 'commit':['git','-C',str(base),'rev-parse','HEAD'],
}
for name,args in commands.items():
 p=subprocess.run(args,capture_output=True,universal_newlines=True,timeout=30)
 result['commands'][name]={'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
assert result['commands']['accounting']['returncode']==0
rows=[r.split('|') for r in result['commands']['accounting']['stdout'].splitlines() if r.strip()]
row=next(r for r in rows if r[0]==job)
assert row[1]=='FAILED' and row[2]=='3:0',row
assert not result['commands']['queue']['stdout'].strip(), 'job still appears in queue'
result['queue_after_retention'] = result['commands']['queue']
result['expected_launch_commit']='c5b33c28bb09324d7decf5c2bb5f6100a877a366'
result['commit_query_matches']=result['commands']['commit']['stdout'].strip()==result['expected_launch_commit']
files=[]
for p in sorted((base/'trial_results').rglob('*')):
 if p.is_symlink():
  files.append({'path':p.relative_to(base).as_posix(),'kind':'symlink','target':os.readlink(p)})
 elif p.is_file():
  stat=p.stat();files.append({'path':p.relative_to(base).as_posix(),'kind':'file','bytes':stat.st_size,'mtime_ns':stat.st_mtime_ns})
 elif p.is_dir():
  files.append({'path':p.relative_to(base).as_posix(),'kind':'directory'})
result['files']=files
result['file_count']=sum(x['kind']=='file' for x in files)
result['total_file_bytes']=sum(x.get('bytes',0) for x in files)
result['largest_files']=sorted([x for x in files if x['kind']=='file'],key=lambda x:x['bytes'],reverse=True)[:12]
result['trial_receipt']=json.loads((base/'trial_results/trial_receipt.json').read_text())
spec=base/'results/pa_catalyst_retest_2026-10-04/launch_spec.json'
result['spec_sha256']=hashlib.sha256(spec.read_bytes()).hexdigest()
assert result['spec_sha256']=='4c2384c6375f1c7892d33d8f6c37478243f41af3da9dd0f9ec507bcd8423e435'
settings=json.loads(spec.read_text());result['dependency_sha256']={}
for record in settings['dependencies']:
 p=Path(record['path']);h=hashlib.sha256(p.read_bytes()).hexdigest();assert h==record['sha256'];result['dependency_sha256'][str(p)]=h
print(json.dumps(result))
'''
(OUT/'remote_inventory_script_v2.py').write_text(SCRIPT,encoding='utf-8')
p=subprocess.run(SSH+['/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3 -'],input=SCRIPT,encoding='utf-8',errors='replace',capture_output=True,timeout=180,creationflags=0x08000000)
(OUT/'inventory_transport_v2.json').write_text(json.dumps({'returncode':p.returncode,'stderr':p.stderr},indent=2),encoding='utf-8')
assert p.returncode==0,p.stderr
result=json.loads(p.stdout)
(OUT/'terminal_inventory.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'job_id':result['job_id'],'file_count':result['file_count'],'total_bytes':result['total_file_bytes'],'largest_files':result['largest_files'],'accounting':result['commands']['accounting'],'trial_keys':list(result['trial_receipt']),'disk_free_bytes':shutil.disk_usage(OUT).free},indent=2),flush=True)
