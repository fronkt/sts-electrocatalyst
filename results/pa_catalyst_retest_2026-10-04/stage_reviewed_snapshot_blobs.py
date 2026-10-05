import hashlib,io,json,pathlib,runpy,subprocess,tempfile
root=pathlib.Path("C:/Users/frank/sts-electrocatalyst")
phase=root/'results/pa_catalyst_retest_2026-10-04'
published=json.loads((phase/'publication_final.json').read_text())
assert published['successful'] and published['commit']==published['remote_commit']=='c5b33c28bb09324d7decf5c2bb5f6100a877a366'
assert not (phase/'remote_stage.json').exists()
approved=json.loads((phase/'staging_approval.json').read_text())
assert approved['scope']=='STAGE_EXACT_REVIEWED_COMMIT_AND_ZERO_SU_PREFLIGHT' and approved['approved_commit']==published['commit'] and approved['submission_approved'] is False
pins=dict(published['staged_blob_pins'],**published['additional_blob_pins'])
paths=sorted(pins)
requests='\n'.join(published['commit']+':'+rel for rel in paths)+'\n'
raw=subprocess.run(['C:/Program Files/Git/cmd/git.exe','-C',str(root),'cat-file','--batch'],input=requests.encode('utf8'),capture_output=True,check=True,timeout=120,creationflags=0x08000000).stdout
stream=io.BytesIO(raw)
local=pathlib.Path(tempfile.mkdtemp(prefix='sts-retest-stage-c5b33c2-blobs-'))
for rel in paths:
 components=pathlib.PurePosixPath(rel)
 assert not components.is_absolute() and '..' not in components.parts
 header=stream.readline().split()
 assert len(header)==3 and header[1]==b'blob',rel
 data=stream.read(int(header[2]));assert stream.read(1)==b'\n'
 pin=pins[rel]
 assert len(data)==pin['bytes'] and hashlib.sha256(data).hexdigest()==pin['sha256'],rel
 expected=published['local_pins'].get(rel)
 if expected is not None and hashlib.sha256(data).hexdigest()!=expected:
  candidate=(root/rel).read_bytes()
  assert hashlib.sha256(candidate).hexdigest()==expected and candidate.replace(b'\r\n',b'\n')==data
  data=candidate
 destination=local.joinpath(*components.parts)
 assert local.resolve() in destination.resolve().parents
 destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(data)
assert not stream.read(),'unexpected cat-file output'
for rel,pin in published['local_pins'].items():
 assert hashlib.sha256((local/rel).read_bytes()).hexdigest()==pin,rel
localphase=local/'results/pa_catalyst_retest_2026-10-04'
(localphase/'publication_final.json').write_bytes((phase/'publication_final.json').read_bytes())
record={'successful':True,'commit':published['commit'],'local_materialization':str(local),'published_paths':len(published['local_pins']),'stage_paths':len(pins),'transport':'git-cat-file-batch-exact-blobs','live_worktree_drift':['tasks/todo.md'],'all_publication_local_pins_verified':True,'new_jobs_submitted':0,'qe_executed':False}
(phase/'staging_materialization.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record),flush=True)
try:
 runpy.run_path(str(localphase/'pa-catalyst-retest-remote-stage-2026-10-04.py'),run_name='__main__')
finally:
 receipt=localphase/'remote_stage.json'
 if receipt.exists():
  with (phase/'remote_stage.json').open('xb') as target:target.write(receipt.read_bytes())
