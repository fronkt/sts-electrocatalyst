"""Complete additive immutable Anvil archive; originals are only read."""
from pathlib import Path
import datetime,hashlib,json,subprocess
ROOT=Path.cwd();OUT=ROOT/'results/pa_catalyst_retest_readout_2026-10-05'
manifest=json.loads((OUT/'raw_manifest.json').read_text(encoding='utf-8'))
script='manifest='+repr(manifest)+'\n'+r'''from pathlib import Path
import datetime,hashlib,json,os,shutil,stat,sys
base=Path(manifest['remote_root'])
archive=base/'evidence_archive_21075231_2026-10-05'
assert not archive.exists() and not archive.is_symlink(),'archive already exists; no overwrite'
unique={}
for x in manifest['files']:
 if x['kind']=='file':unique.setdefault(x['sha256'],x)
required=sum(x['bytes'] for x in unique.values())
assert shutil.disk_usage(base).free>required+1024**3,'insufficient disk'
archive.mkdir(mode=0o700);blobs=archive/'blobs';blobs.mkdir(mode=0o700)
records=[]
for digest,x in unique.items():
 source=base/x['path'];before=source.stat()
 assert (before.st_size,before.st_mtime_ns)==(x['bytes'],x['mtime_ns']),x['path']+' source drift'
 destination=blobs/digest
 h=hashlib.sha256()
 with source.open('rb') as reader,destination.open('xb') as writer:
  for block in iter(lambda:reader.read(4*1024*1024),b''):
   h.update(block);writer.write(block)
  writer.flush();os.fsync(writer.fileno())
 assert h.hexdigest()==digest,x['path']+' source content drift'
 after=source.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
 hh=hashlib.sha256()
 with destination.open('rb') as reader:
  for block in iter(lambda:reader.read(4*1024*1024),b''):hh.update(block)
 assert hh.hexdigest()==digest and destination.stat().st_size==x['bytes'],x['path']+' copy mismatch'
 destination.chmod(0o400)
 records.append({'sha256':digest,'bytes':x['bytes'],'source_path':x['path'],'archive_path':'blobs/'+digest})
 if len(records)%20==0:print(json.dumps({'archived_unique_files':len(records),'total_unique_files':len(unique),'bytes_archived':sum(y['bytes'] for y in records)}),file=sys.stderr,flush=True)
# Hashes from every logical path are available in this unaliased content archive.
assert {x['sha256'] for x in manifest['files'] if x['kind']=='file'}=={x['sha256'] for x in records}
body=json.dumps(manifest,indent=2)+'\n';(archive/'raw_manifest.json').write_text(body)
receipt={'schema':'pa-retest-complete-anvil-preservation-v1','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'job_id':'21075231','archive_root':str(archive),'launch_commit':manifest['launch_commit'],'launch_spec_sha256':manifest['launch_spec_sha256'],'logical_file_count':sum(x['kind']=='file' for x in manifest['files']),'logical_bytes':manifest['total_file_bytes'],'unique_file_count':len(unique),'unique_bytes':required,'all_source_and_archive_sha256_verified':True,'manifest_bytes_sha256':hashlib.sha256(body.encode()).hexdigest(),'file_permissions':'0400','directory_permissions':'0500','original_trial_writes':False,'new_qe_calls':0,'new_jobs':0,'content_files':records}
(archive/'preservation_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
(archive/'raw_manifest.json').chmod(0o400);(archive/'preservation_receipt.json').chmod(0o400);blobs.chmod(0o500);archive.chmod(0o500)
print(json.dumps(receipt))
'''
(OUT/'remote_archive_script.py').write_text(script,encoding='utf-8')
ssh=['C:/Program Files/Git/usr/bin/ssh.exe','-i','C:/Users/frank/.ssh/id_ed25519','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=12','x-fcai3@anvil.rcac.purdue.edu']
with (OUT/'remote_archive.stdout.json').open('xb') as stdout,(OUT/'remote_archive.stderr.log').open('xb') as stderr:
 p=subprocess.run(ssh+['/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3 -'],input=script.encode(),stdout=stdout,stderr=stderr,creationflags=0x08000000,timeout=3600)
assert p.returncode==0,(OUT/'remote_archive.stderr.log').read_text(errors='replace')[-3000:]
r=json.loads((OUT/'remote_archive.stdout.json').read_text());assert r['logical_file_count']==manifest['file_count'] and r['all_source_and_archive_sha256_verified']
(OUT/'anvil_archive_complete.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in r.items() if k!='content_files'},indent=2),flush=True)
