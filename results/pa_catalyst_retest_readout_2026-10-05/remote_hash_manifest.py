from pathlib import Path
import datetime,hashlib,json,os,stat,subprocess,sys,time
base=Path('/anvil/projects/x-che260157/sts_pa_catalyst_retest_2026-10-04')
specpath=base/'results/pa_catalyst_retest_2026-10-04/launch_spec.json'
spec=json.loads(specpath.read_text())
extras=[specpath,base/'retest_21075231.log',Path(spec['source_deck']['path']),Path(spec['source_review']['path'])]
extras.extend(Path(x['path']) for x in spec['dependencies'])
paths=sorted(set([p for p in (base/'trial_results').rglob('*')]+extras))
records=[];done=0;total=0
for p in paths:
 before=p.lstat();rel=p.relative_to(base).as_posix()
 assert not stat.S_ISLNK(before.st_mode),'symlink refused: '+rel
 if stat.S_ISDIR(before.st_mode):
  records.append({'path':rel,'kind':'directory','mode':stat.S_IMODE(before.st_mode)});continue
 assert stat.S_ISREG(before.st_mode),'special file refused: '+rel
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
 after=p.stat()
 assert (before.st_size,before.st_mtime_ns,before.st_ino)==(after.st_size,after.st_mtime_ns,after.st_ino),'file drift: '+rel
 records.append({'path':rel,'kind':'file','bytes':before.st_size,'mtime_ns':before.st_mtime_ns,'mode':stat.S_IMODE(before.st_mode),'sha256':h.hexdigest()})
 done+=1;total+=before.st_size
 if done%20==0:print(json.dumps({'hashed_files':done,'hashed_bytes':total,'path':rel}),file=sys.stderr,flush=True)
# Validate complete terminal inventory and launch/runtime/source identity after scan.
expected=[p.relative_to(base).as_posix() for p in (base/'trial_results').rglob('*')]
assert sorted(expected)==sorted(x['path'] for x in records if x['path'].startswith('trial_results/'))
pins=[*spec['dependencies'],spec['source_deck'],spec['source_review'],spec['pw_x'],spec['mpirun'],*spec['upfs']]
verified=[]
for pin in pins:
 p=Path(pin['path']);h=hashlib.sha256(p.read_bytes()).hexdigest();assert h==pin['sha256'],str(p)
 verified.append({'path':str(p),'sha256':h,'bytes':p.stat().st_size})
for pin in spec['initial_seed']['files']:
 p=Path(spec['initial_seed']['root'])/pin['path'];h=hashlib.sha256(p.read_bytes()).hexdigest();assert h==pin['sha256'],str(p)
 verified.append({'path':str(p),'sha256':h,'bytes':p.stat().st_size})
assert hashlib.sha256(specpath.read_bytes()).hexdigest()=='4c2384c6375f1c7892d33d8f6c37478243f41af3da9dd0f9ec507bcd8423e435'
commit=subprocess.check_output(['git','-C',str(base),'rev-parse','HEAD'],universal_newlines=True).strip()
assert commit=='c5b33c28bb09324d7decf5c2bb5f6100a877a366'
print(json.dumps({'schema':'pa-retest-terminal-raw-manifest-v1','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'job_id':'21075231','remote_root':str(base),'launch_commit':commit,'launch_spec_sha256':'4c2384c6375f1c7892d33d8f6c37478243f41af3da9dd0f9ec507bcd8423e435','readonly':True,'qe_executed':False,'files':records,'external_launch_pins_verified':verified,'file_count':done,'total_file_bytes':total}))
