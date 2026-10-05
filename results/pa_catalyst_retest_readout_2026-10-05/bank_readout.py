"""Bank only the reviewed terminal evidence and its complete local scientific archive."""
import datetime,hashlib,json,os,pathlib,subprocess,tarfile
ROOT=pathlib.Path('C:/Users/frank/sts-electrocatalyst')
OUT=ROOT/'results/pa_catalyst_retest_readout_2026-10-05'
GIT='C:/Program Files/Git/cmd/git.exe'
BASE='e47a3fe454ba2e2320822b538214400895ddb0d4'
BRANCH='r0-catalysis-revival'
ENV=dict(os.environ,GIT_TERMINAL_PROMPT='0',GCM_INTERACTIVE='never',GCM_GUI_PROMPT='0')
def git(args,timeout=120):
 p=subprocess.run([GIT,'-c','credential.interactive=never','-c','core.autocrlf=false','-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol']+args,cwd=ROOT,env=ENV,creationflags=0x08000000,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
 if p.returncode: raise RuntimeError({'args':args,'code':p.returncode,'stderr':p.stderr.decode('utf8','replace')})
 return p.stdout
def text(args,timeout=120): return git(args,timeout).decode('utf8').strip()
def load(path): return json.loads(path.read_bytes())
def sha_bytes(data): return hashlib.sha256(data).hexdigest()
def sha(path): return sha_bytes(path.read_bytes())
assert text(['rev-parse','HEAD'])==BASE
assert text(['branch','--show-current'])==BRANCH
assert text(['remote','get-url','origin'])=='https://github.com/fronkt/sts-electrocatalyst.git'
assert text(['ls-remote','origin','refs/heads/'+BRANCH]).split()[0]==BASE
assert not text(['diff','--cached','--name-only'])
assert set(text(['diff','--name-only']).splitlines())=={'tasks/todo.md'}
review=load(OUT/'independent_readout_review.json')
assert review['decision']=='FAILED_CONTINUITY_READOUT_ONLY',review.get('decision')
assert review['blocking_findings']==[]
assert review['pins']
for pin in review['pins']:
 p=(ROOT/pin['path']).resolve()
 assert p.is_relative_to(ROOT.resolve())
 assert sha(p)==pin['sha256'],pin['path']
summary=load(OUT/'preservation_summary.json')
assert summary['status']=='COMPLETE_ANVIL_ARCHIVE_AND_LOCAL_SCIENTIFIC_BUNDLE'
assert summary['scientific_status']=='INCONCLUSIVE' and not summary['production_accepted']
assert summary['new_jobs']==summary['new_qe_calls']==0
assert not summary['optional_windows_binary_mirror']['complete']
for path,expected in summary['artifact_sha256'].items(): assert sha(OUT/path)==expected,path
manifest=load(OUT/'raw_manifest.json')
raw_files={x['path']:x for x in manifest['files'] if x['kind']=='file'}
assert len(raw_files)==1631
assert sum(x['bytes'] for x in raw_files.values())==76112065809
archive=load(OUT/'anvil_archive_complete.json')
assert sha_bytes((OUT/'raw_manifest.json').read_bytes().replace(b'\r\n',b'\n'))==archive['manifest_bytes_sha256']
assert archive['all_source_and_archive_sha256_verified']
assert archive['logical_file_count']==len(raw_files)
assert archive['logical_bytes']==sum(x['bytes'] for x in raw_files.values())
content={x['sha256']:x for x in archive['content_files']}
assert len(content)==492
assert sum(x['bytes'] for x in content.values())==60874634461
assert set(content)=={x['sha256'] for x in raw_files.values()}
for x in raw_files.values(): assert content[x['sha256']]['bytes']==x['bytes']
small={p:x for p,x in raw_files.items() if x['bytes']<=32*1024*1024}
assert len(small)==1098 and sum(x['bytes'] for x in small.values())==35476741
assert sha(OUT/'raw_small_v2.tar.gz')=='d65ac2995f626df4ae5118514613f6b46c5df7ad76c274a98cb10d19e698fe84'
with tarfile.open(OUT/'raw_small_v2.tar.gz','r:gz') as tar:
 members=tar.getmembers()
 assert len(members)==len(small)
 assert {m.name for m in members}==set(small)
 for m in members:
  assert m.isfile() and not m.name.startswith('/') and '..' not in pathlib.PurePosixPath(m.name).parts
  x=small[m.name]
  assert m.size==x['bytes']
  assert sha_bytes(tar.extractfile(m).read())==x['sha256'],m.name
for p,x in small.items():
 local=OUT/'raw_mirror'/p
 assert local.stat().st_size==x['bytes'] and sha(local)==x['sha256'],p
sources=load(OUT/'launch_snapshot/source_manifest.json')
assert sources['implementation_commit']==manifest['launch_commit']=='c5b33c28bb09324d7decf5c2bb5f6100a877a366'
assert sha(OUT/'launch_snapshot/launch_spec.json')==manifest['launch_spec_sha256']=='4c2384c6375f1c7892d33d8f6c37478243f41af3da9dd0f9ec507bcd8423e435'
for pin in sources['sources']:
 assert sha(ROOT/pin['path'])==sha(ROOT/pin['snapshot'])==pin['sha256'],pin['path']
 assert sha_bytes(git(['cat-file','blob',sources['implementation_commit']+':'+pin['path']]))==pin['sha256'],pin['path']
for name in ['cached_source_pins.json','retrieval.json','retrieval_extra.json','retrieval_setup.json']:
 pins=load(OUT/'qe_source'/name)
 assert pins['version']=='qe-7.5'
 for pin in pins['files']:
  data=(OUT/'qe_source'/pin['path']).read_bytes()
  assert len(data)==pin['bytes'] and sha_bytes(data)==pin['sha256'],pin['path']
  if 'git_blob_sha1' in pin:
   assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==pin['git_blob_sha1']
account=load(OUT/'terminal_accounting.json')
assert account['state']=='FAILED' and account['exit_code']=='3:0'
assert account['allocation_cpu_seconds']==1274112 and account['allocation_cpu_su']==353.92
assert account['scientific_status']=='INCONCLUSIVE'
assert all(x['returncode']==0 for x in account['all_four_qe_process_returncodes'])
assert load(OUT/'independent_analysis_v4.status.json')['exit_code']==0
assert load(OUT/'preserve_anvil_archive.status.json')['exit_code']==0
print('Exact review, archive mapping, all 1,098 local files/tar members, launch and QE source pins verified.',flush=True)
# Preserve every historical task byte; only append this dated section and mark the terminal-follow-through item.
todo_path=ROOT/'tasks/todo.md'
original=git(['cat-file','blob',BASE+':tasks/todo.md'])
heading='# STS 2027 — TODO\n\n'.encode('utf8')
marker='## 2026-10-05 — Current timeline and phase scope through STS submission'.encode('utf8')
assert original.startswith(heading+marker)
old_item=b'- [ ] Retain actual running allocation, terminal accounting/raw evidence and scientific readout for job 21075231; no automatic retry.'
new_item=old_item.replace(b'[ ]',b'[x]',1)
assert original.count(old_item)==1
current=todo_path.read_bytes()
assert current.startswith(heading)
assert current.count(marker)==1
start=current.index(marker)
assert current[start:]==original[len(heading):], 'historical task suffix drift before publication'
new_section=current[len(heading):start].decode('utf8')
new_section=new_section.replace('- [ ] Independently review the evidence','- [x] Independently review the evidence').replace('- [ ] Record the scientific readout','- [x] Record the scientific readout')
new_section+='Review: independent FAILED_CONTINUITY_READOUT_ONLY clearance binds the readout, raw numerical reconstruction, complete Anvil/archive and local scientific preservation. No blockers remain. Exact source, geometry/force pairing and unchanged registered failure are confirmed; the startup-threshold difference is supported, causal attribution remains open. Full Windows binary preservation is partial. No new solver calls, implementation tests or jobs. Explicit-path publication checks the archived scientific members, historical task bytes, staged bytes and remote commit equality.\n\n'
new_todo=heading+new_section.encode('utf8')+original[len(heading):].replace(old_item,new_item,1)
todo_path.write_bytes(new_todo)
assert new_todo[new_todo.index(marker):]==original[len(heading):].replace(old_item,new_item,1)
files=load(OUT/'publication_files.json')['paths']
assert files==sorted(set(files))
assert 'tasks/todo.md' in files and 'docs/research/pa-catalyst-retest-readout-2026-10-05.md' in files
allowed='results/pa_catalyst_retest_readout_2026-10-05/'
assert all(p in ['tasks/todo.md','docs/research/pa-catalyst-retest-readout-2026-10-05.md'] or p.startswith(allowed) for p in files)
assert all('/raw_blobs/' not in p and '/raw_mirror/' not in p and not p.endswith('.job.json') for p in files)
assert all((ROOT/p).is_file() and (ROOT/p).stat().st_size<95*1024*1024 for p in files)
prepins={p:sha(ROOT/p) for p in files}
for offset in range(0,len(files),30): git(['add','-f','--']+files[offset:offset+30])
staged=text(['diff','--cached','--name-only']).splitlines()
assert set(staged)==set(files),(set(staged)-set(files),set(files)-set(staged))
assert set(text(['diff','--cached','--diff-filter=M','--name-only']).splitlines())=={'tasks/todo.md'}
assert not text(['diff','--cached','--diff-filter=DR','--name-only'])
assert not text(['diff','--name-only'])
for p,expected in prepins.items(): assert sha_bytes(git(['cat-file','blob',':'+p]))==expected,p
for pin in review['pins']: assert sha(ROOT/pin['path'])==pin['sha256'],pin['path']
git(['diff','--cached','--check'])
print('Staged exact reviewed bytes on '+str(len(files))+' explicit paths; historical tracked content preserved.',flush=True)
print(text(['commit','-m','Preserve catalyst retest failure and locate restart force divergence'],180),flush=True)
commit=text(['rev-parse','HEAD'])
assert text(['rev-parse','HEAD^'])==BASE
assert set(text(['diff-tree','--no-commit-id','--name-only','-r','HEAD']).splitlines())==set(files)
assert not text(['status','--short','--untracked-files=no'])
for p,expected in prepins.items(): assert sha_bytes(git(['cat-file','blob',commit+':'+p]))==expected,p
print(text(['push','origin','HEAD:refs/heads/'+BRANCH],300),flush=True)
remote=text(['ls-remote','origin','refs/heads/'+BRANCH],180).split()[0]
assert remote==commit
assert not text(['status','--short','--untracked-files=no'])
receipt={'schema':'pa-retest-readout-publication-v1','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'commit':commit,'branch':BRANCH,'remote_commit':remote,'explicit_paths':files,'staged_and_committed_byte_sha256':prepins,'review_sha256':sha(OUT/'independent_readout_review.json'),'all_1098_small_archive_and_local_hashes_verified':True,'all_other_tracked_paths_unchanged':True,'historical_todo_suffix_verified':True,'scientific_status':'INCONCLUSIVE','production_accepted':False,'new_qe_calls':0,'new_jobs':0,'tests_run':False}
(OUT/'publication_complete.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode('utf8'))
print(json.dumps({'publication':'COMPLETE','commit':commit,'remote':remote,'paths':len(files),'scientific_status':'INCONCLUSIVE','new_jobs':0,'new_qe_calls':0},indent=2),flush=True)

