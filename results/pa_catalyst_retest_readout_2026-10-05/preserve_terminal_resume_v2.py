"""Preserve all terminal bytes using a small raw mirror and deduplicated large blobs.
Read-only on Anvil; no QE, scheduler mutation or automatic transfer retries.
"""
from pathlib import Path
import concurrent.futures, datetime, hashlib, json, os, re, shutil, subprocess, tarfile, threading, time
ROOT=Path.cwd()
OUT=ROOT/'results/pa_catalyst_retest_readout_2026-10-05'
REMOTE='/anvil/projects/x-che260157/sts_pa_catalyst_retest_2026-10-04'
KEY='C:/Users/frank/.ssh/id_ed25519'
HOST='x-fcai3@anvil.rcac.purdue.edu'
OPTIONS=['-i',KEY,'-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=12','-o','Compression=no']
SSH=['C:/Program Files/Git/usr/bin/ssh.exe',*OPTIONS,HOST]
SCP=['C:/Program Files/Git/usr/bin/scp.exe','-q',*OPTIONS]
PYTHON='/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3 -'
SMALL=32*1024*1024

def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def write(name,data):
 (OUT/name).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()

REMOTE_HASH=r'''from pathlib import Path
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
'''
manifest=json.loads((OUT/'raw_manifest.json').read_text(encoding='utf-8'))
assert sha(OUT/'raw_manifest.json')=='c707caea13fdfb49c72fb745c7b79827879607fad93fd95b84010c3c1e7575d5','existing full manifest drifted'
initial=json.loads((OUT/'terminal_inventory.json').read_text(encoding='utf-8'))
initial_map={x['path']:(x['bytes'],x['mtime_ns']) for x in initial['files'] if x['kind']=='file'}
remote_map={x['path']:(x['bytes'],x['mtime_ns']) for x in manifest['files'] if x['kind']=='file' and x['path'].startswith('trial_results/')}
assert initial_map==remote_map,'terminal tree changed after first inventory'
files=[x for x in manifest['files'] if x['kind']=='file']
small=[x for x in files if x['bytes']<=SMALL]
large=[x for x in files if x['bytes']>SMALL]
unique={}
for x in large:
 unique.setdefault(x['sha256'],x)
required=sum(x['bytes'] for x in unique.values())+sum(x['bytes'] for x in small)*2
assert shutil.disk_usage(OUT).free>required+10*1024**3,'insufficient free disk'
write('preservation_progress.json',{'state':'FETCHING_SMALL_RAW','recorded_utc':now(),'full_remote_files':len(files),'logical_bytes':manifest['total_file_bytes'],'unique_large_blobs':len(unique),'unique_large_bytes':sum(x['bytes'] for x in unique.values()),'qe_executed':False})
print(json.dumps({'unique_large_blobs':len(unique),'unique_large_bytes':sum(x['bytes'] for x in unique.values()),'small_files':len(small)},indent=2),flush=True)
script="base="+repr(REMOTE)+"\nentries="+repr(small)+"\n"+r'''import pathlib,sys,tarfile,gzip
root=pathlib.Path(base)
with gzip.GzipFile(fileobj=sys.stdout.buffer,mode='wb',compresslevel=1) as gz:
 with tarfile.open(fileobj=gz,mode='w|') as tar:
  for x in entries:
   p=root/x['path'];s=p.stat();assert (s.st_size,s.st_mtime_ns)==(x['bytes'],x['mtime_ns'])
   tar.add(str(p),arcname=x['path'],recursive=False)
'''
(OUT/'remote_small_archive_v2.py').write_text(script,encoding='utf-8')
with (OUT/'raw_small_v2.tar.gz').open('xb') as stdout,(OUT/'small_archive_v2.stderr.log').open('xb') as stderr:
 r=subprocess.run(SSH+[PYTHON],input=script.encode(),stdout=stdout,stderr=stderr,timeout=600,creationflags=0x08000000)
assert r.returncode==0,(OUT/'small_archive_v2.stderr.log').read_text(errors='replace')
mirror=OUT/'raw_mirror';mirror.mkdir()
with tarfile.open(OUT/'raw_small_v2.tar.gz','r:gz') as tar:
 members=tar.getmembers()
 assert {x.name for x in members}=={x['path'] for x in small}
 assert all(x.isfile() and not x.name.startswith('/') and '..' not in Path(x.name).parts for x in members)
 tar.extractall(mirror,filter='data')
for x in small:
 p=mirror/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],x['path']
write('small_mirror_verified.json',{'recorded_utc':now(),'files_verified':len(small),'bytes_verified':sum(x['bytes'] for x in small),'archive_sha256':sha(OUT/'raw_small_v2.tar.gz'),'complete_large_blob_preservation_pending':True})
print('Small raw mirror verified; starting large content blobs',flush=True)
blobdir=OUT/'raw_blobs';blobdir.mkdir()
receipts={};lock=threading.Lock();start=time.monotonic()
def fetch(x):
 digest=x['sha256'];target=blobdir/digest;partial=blobdir/(digest+'.partial');log=OUT/('blob_'+digest[:16]+'.stderr.log')
 assert re.fullmatch('[0-9a-f]{64}',digest)
 assert not target.exists() and not partial.exists()
 began=time.monotonic()
 with log.open('xb') as stderr:
  r=subprocess.run(SCP+[HOST+':'+REMOTE+'/'+x['path'],str(partial)],stdout=subprocess.DEVNULL,stderr=stderr,timeout=3600,creationflags=0x08000000)
 assert r.returncode==0,log.read_text(errors='replace')
 assert partial.stat().st_size==x['bytes'] and sha(partial)==digest,'large blob content mismatch: '+x['path']
 partial.rename(target)
 rec={'sha256':digest,'bytes':x['bytes'],'representative_remote_path':x['path'],'local_blob':str(target.relative_to(ROOT)).replace('\\','/'),'seconds':time.monotonic()-began,'verified_utc':now()}
 with lock:
  receipts[digest]=rec
  write('large_blob_receipts.json',receipts)
  write('preservation_progress.json',{'state':'FETCHING_LARGE_BLOBS','recorded_utc':now(),'completed_blobs':len(receipts),'total_blobs':len(unique),'completed_bytes':sum(y['bytes'] for y in receipts.values()),'total_bytes':sum(y['bytes'] for y in unique.values()),'elapsed_seconds':time.monotonic()-start,'qe_executed':False})
  print(json.dumps({'preserved_blobs':len(receipts),'total_blobs':len(unique),'bytes':sum(y['bytes'] for y in receipts.values())}),flush=True)
 return rec
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 futures=[pool.submit(fetch,x) for x in unique.values()]
 for future in concurrent.futures.as_completed(futures):future.result()
# Every logical file is represented by byte-verified mirror content or a hash blob.
for x in files:
 p=mirror/x['path'] if x['bytes']<=SMALL else blobdir/x['sha256']
 assert p.is_file() and p.stat().st_size==x['bytes']
write('preservation_complete.json',{'schema':'pa-retest-complete-local-preservation-v1','recorded_utc':now(),'job_id':'21075231','launch_commit':manifest['launch_commit'],'launch_spec_sha256':manifest['launch_spec_sha256'],'raw_manifest_sha256':sha(OUT/'raw_manifest.json'),'file_count':len(files),'logical_bytes_preserved':manifest['total_file_bytes'],'small_mirror_files':len(small),'large_logical_files':len(large),'unique_large_blobs':len(unique),'unique_large_bytes':sum(x['bytes'] for x in unique.values()),'all_content_sha256_verified':True,'storage':'small raw mirror plus content-addressed complete large binary blobs; names/metadata in raw_manifest.json','remote_writes':False,'new_qe_calls':0,'new_jobs':0,'automatic_transfer_retries':0})
write('preservation_progress.json',{'state':'COMPLETE','recorded_utc':now(),'completed_blobs':len(receipts),'qe_executed':False})
print('COMPLETE: all logical file contents preserved with matching SHA256',flush=True)
