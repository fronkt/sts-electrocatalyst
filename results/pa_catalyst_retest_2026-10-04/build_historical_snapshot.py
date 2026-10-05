import ast, hashlib, json, pathlib, subprocess
root=pathlib.Path("C:/Users/frank/sts-electrocatalyst")
phase=root/'results/pa_catalyst_retest_2026-10-04'
prep=root/'results/pa_catalyst_trial_readout_prep_2026-10-04'
commit='b9f0208ee6f3cd71d0201d03b964b5c23f53d644'
pub=json.loads((root/'results/pa_catalyst_trial_2026-10-03/publication_final.json').read_text())
assert pub['successful'] and pub['commit']==pub['remote_commit']==commit
tree=ast.parse((prep/'readout_trial.py').read_text())
constants={n.targets[0].id:ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str)}
rels={constants[k] for k in ['DOC','REV','REV1','IMPL','SBR','SPEC','CTRL','ADP','ELIG','WATCH','WRAP']}
rels.add('src/dft/pa_checked_contract.py')
rels.add('runs/hea/lowtail_low_state_restart_2026-09-22/Cu8Cr23Mn35Co34__s20_site2/slab_c5low__relax.in')
base=prep/'launch_snapshot'
base.mkdir(exist_ok=False)
rows={}
for rel in sorted(rels):
 p=subprocess.run(['C:/Program Files/Git/cmd/git.exe','-C',str(root),'show',commit+':'+rel],capture_output=True,check=True,creationflags=0x08000000)
 data=p.stdout; sha=hashlib.sha256(data).hexdigest()
 pin=pub['staged_blob_pins'].get(rel,pub['additional_blob_pins'].get(rel))
 if pin is not None: assert sha==pin['sha256'] and len(data)==pin['bytes'],rel
 destination=base/rel; destination.parent.mkdir(parents=True,exist_ok=True); destination.write_bytes(data)
 rows[rel]={'sha256':sha,'bytes':len(data),'snapshot_path':destination.relative_to(root).as_posix()}
manifest={'schema':'pa-original-launch-snapshot-v1','commit':commit,'job_id':'21034683','publication_receipt_sha256':hashlib.sha256((root/'results/pa_catalyst_trial_2026-10-03/publication_final.json').read_bytes()).hexdigest(),'files':rows}
(prep/'launch_snapshot.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8',newline='\n')
print(json.dumps({'commit':commit,'files':len(rows),'manifest_sha256':hashlib.sha256((prep/'launch_snapshot.json').read_bytes()).hexdigest()}),flush=True)
