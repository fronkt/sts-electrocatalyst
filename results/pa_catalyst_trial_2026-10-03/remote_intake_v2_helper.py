import json
from pathlib import Path
import subprocess

phase = Path.cwd() / 'results/pa_catalyst_trial_2026-10-03'
remote = r'''import hashlib,json,pathlib,re,subprocess
base=pathlib.Path('/anvil/projects/x-che260157');root=base/'sts'
deck=root/'runs/hea/lowtail_low_state_restart_2026-09-22/Cu8Cr23Mn35Co34__s20_site2/slab_c5low__relax.in'
seed=root/'runs/hea/lowtail_slab_scf_diag_2026-09-19/Cu8Cr23Mn35Co34__s20_site2/tmp_slab_c5__b030/slab_c5__b030.save'
def pin(path):
 h=hashlib.sha256()
 with path.open('rb') as stream:
  for chunk in iter(lambda:stream.read(1048576),b''):h.update(chunk)
 return {'path':str(path),'bytes':path.stat().st_size,'sha256':h.hexdigest()}
r={'read_only':True,'new_jobs_submitted':0,'qe_executed':False,'commands':{},'runtime':{},'seed':{'path':str(seed),'files':[]},'pseudos':[]}
for name,cmd in [('balance',['bash','-lc','mybalance']),('partition',['scontrol','show','partition','wholenode']),('queue',['squeue','-u','x-fcai3','-h','-o','%i|%j|%T|%C|%M|%l|%R']),('nodes',['sinfo','-p','wholenode','-N','-h','-o','%N|%c|%m|%t']),('mpi_version',[str(base/'qe/env/bin/mpirun'),'--version'])]:
 p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,timeout=25)
 r['commands'][name]={'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
for name,path in [('pw',base/'qe/env/bin/pw.x'),('mpirun',base/'qe/env/bin/mpirun')]:r['runtime'][name]=pin(path.resolve())
r['deck']=pin(deck);text=deck.read_text();r['deck']['text']=text
ntyp=int(re.search(r'\bntyp\s*=\s*(\d+)',text,re.I).group(1))
lines=text.splitlines();index=next(i for i,l in enumerate(lines) if l.strip()=='ATOMIC_SPECIES')
rows=[l.split() for l in lines[index+1:index+1+ntyp]]
assert len(rows)==ntyp and all(len(f)==3 and re.fullmatch(r'[A-Za-z][A-Za-z0-9]*',f[0]) and f[2].endswith('.UPF') for f in rows)
for fields in rows:r['pseudos'].append(pin(base/'pseudo'/fields[2]))
for path in sorted(seed.rglob('*')):
 if path.is_symlink():raise RuntimeError('seed symlink refused')
 if path.is_file():r['seed']['files'].append(pin(path))
r['new_trial_root_exists']=(base/'sts_pa_catalyst_2026-10-03').exists()
r['seed_xml']=(seed/'data-file-schema.xml').read_text()
print(json.dumps(r,indent=2))
'''
compile(remote,'<remote-read-only-v2>','exec')
command=['C:/Program Files/Git/usr/bin/ssh.exe','-i','C:/Users/frank/.ssh/id_ed25519',
         '-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=12',
         'x-fcai3@anvil.rcac.purdue.edu',
         '/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3 -']
process=subprocess.run(command,input=remote,capture_output=True,text=True,encoding='utf-8',
                       errors='replace',timeout=150,creationflags=0x08000000)
receipt={'returncode':process.returncode,'stdout':process.stdout,'stderr':process.stderr,
         'read_only':True,'new_jobs_submitted':0,'qe_executed':False,
         'prior_failed_receipt':'remote_intake.json'}
(phase/'remote_intake_v2.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
assert process.returncode==0,process.stderr
parsed=json.loads(process.stdout)
(phase/'remote_inventory.json').write_text(json.dumps(parsed,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in parsed.items() if k not in ['seed_xml','deck','seed']},indent=2))
