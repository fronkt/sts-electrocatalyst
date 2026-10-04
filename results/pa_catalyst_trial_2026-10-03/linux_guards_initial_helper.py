import base64,hashlib,json,pathlib,subprocess
root=pathlib.Path.cwd();phase=root/'results/pa_catalyst_trial_2026-10-03'
target=phase/'linux_guards_checked.json';assert not target.exists()
paths=['src/dft/pa_qe_adapter.py','src/dft/pa_catalyst_trial.py','src/dft/pa_checked_contract.py','anvil/89_pa_catalyst_boundary_trial.slurm']
payload={p:{'data':base64.b64encode((root/p).read_bytes()).decode(),'sha256':hashlib.sha256((root/p).read_bytes()).hexdigest()} for p in paths}
remote='payload='+repr(payload)+'\n'+r'''import base64,hashlib,json,os,pathlib,subprocess,sys
root=pathlib.Path('/anvil/projects/x-che260157/sts_pa_catalyst_linux_preflight_2026-10-03')
assert not root.exists() and not root.is_symlink()
root.mkdir(mode=0o700)
for rel,row in payload.items():
 p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);data=base64.b64decode(row['data']);assert hashlib.sha256(data).hexdigest()==row['sha256']
 with p.open('xb') as stream:stream.write(data)
 if p.suffix=='.py':compile(data,str(p),'exec')
sys.path.insert(0,str(root/'src/dft'));import pa_qe_adapter as a;import pa_catalyst_trial as c
results=[]
def reject(name,fn):
 try:fn()
 except (a.AdapterError,c.TrialError,ValueError,OSError) as exc:results.append({'check':name,'rejected':True,'reason':str(exc)})
 else:raise AssertionError('accepted unsafe case: '+name)
plain=root/'fixtures/plain';plain.mkdir(parents=True);(plain/'empty').mkdir();(plain/'wfc1').write_bytes(b'wavefunction');(plain/'slab.bfgs').write_bytes(b'optimizer');(plain/'slab.update').write_bytes(b'proposal')
before=c.inventory(plain);copied=c.copy_checkpoint(plain,root/'fixtures/snapshot',immutable=True)
assert before==c.inventory(plain) and before['sha256']==c.inventory(pathlib.Path(copied['outdir']))['sha256']
assert (pathlib.Path(copied['outdir'])/'empty').is_dir();results.append({'check':'full_recursive_snapshot_with_empty_directory','passed':True})
linkfile=root/'fixtures/linkfile';linkfile.mkdir();(linkfile/'wfc-link').symlink_to(plain/'wfc1')
reject('supervisor_file_symlink',lambda:c.inventory(linkfile));reject('adapter_file_symlink',lambda:a.checkpoint_inventory(linkfile))
parentlink=root/'fixtures/parentlink';parentlink.symlink_to(plain,target_is_directory=True)
reject('supervisor_parent_symlink',lambda:c.inventory(parentlink));reject('adapter_parent_symlink',lambda:a.checkpoint_inventory(parentlink))
fifo=root/'fixtures/fifo';fifo.mkdir();os.mkfifo(str(fifo/'special'))
reject('supervisor_fifo',lambda:c.inventory(fifo));reject('adapter_fifo',lambda:a.checkpoint_inventory(fifo))
hard=root/'fixtures/hard';hard.mkdir();one=hard/'one';one.write_bytes(b'fixture');os.link(str(one),str(hard/'two'))
reject('supervisor_mutable_hardlink',lambda:c.inventory(hard));reject('adapter_mutable_hardlink',lambda:a.checkpoint_inventory(hard))
pin={'path':str(one),'sha256':hashlib.sha256(b'fixture').hexdigest()}
reject('default_dependency_hardlink',lambda:c.verify_pin(pin,'mutable'))
assert c.verify_pin(pin,'immutable external fixture',allow_external_hardlinks=True)['sha256']==pin['sha256'];results.append({'check':'external_binary_style_hardlink_pin','passed':True})
(hard/'two').write_bytes(b'drift');reject('external_hardlink_byte_drift',lambda:c.verify_pin(pin,'external fixture',allow_external_hardlinks=True))
reject('checkpoint_self_alias',lambda:c.copy_checkpoint(plain,plain/'self'))
reject('checkpoint_existing_destination',lambda:c.copy_checkpoint(plain,root/'fixtures/snapshot'))
syntax=subprocess.run(['bash','-n',str(root/'anvil/89_pa_catalyst_boundary_trial.slurm')],stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,timeout=10);assert syntax.returncode==0
raw=pathlib.Path('/anvil/projects/x-che260157/sts_pa_probe_2026-10-03/tiny_results/candidate-stop')
expected=a.parse_deck(raw/'input.in');expected['upf_pins']={'H.pbe-rrkjus_psl.1.0.0.UPF':'27f8a7e87851d59a2698237d6ab4578d62950640f4f175781b015a0ce731f962'}
process=json.loads((raw/'receipt.json').read_text())
parsed=a.read_qe_arm(raw/'input.in',raw/'stdout.log',raw/'stderr.log',raw/'scratch/h2_probe.save/data-file-schema.xml',process,expected_settings=expected,expected_parallel={'nprocs':1,'nthreads':1,'ntasks':1,'nbgrp':1,'npool':1,'ndiag':1},expected_exit='clean_stop',expected_evaluations=1)
history=a.read_bfgs(raw/'scratch/h2_probe.bfgs',nat=2,cell_bohr=parsed['evaluations'][0]['geometry']['cell'],evaluated=parsed['evaluations'][0]);assert (history['scf_count'],history['bfgs_count'],history['gdiis_count'])==(1,1,0)
report={'successful':True,'scope':'LINUX_FILESYSTEM_GUARDS_AND_RETAINED_ACTUAL_TINY_REPLAY_ONLY','python':sys.version,'code_pins':{p:r['sha256'] for p,r in payload.items()},'checks':results,'wrapper_syntax_returncode':syntax.returncode,'raw_tiny_arm':parsed,'raw_tiny_history':history,'qe_executed':False,'new_jobs':0,'production_accepted':False}
(root/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
'''
p=subprocess.run(['C:/Program Files/Git/usr/bin/ssh.exe','-i','C:/Users/frank/.ssh/id_ed25519','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=12','x-fcai3@anvil.rcac.purdue.edu','/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3 -'],input=remote,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=100,creationflags=0x08000000)
r={'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'code_pins':{k:v['sha256'] for k,v in payload.items()},'qe_executed':False,'new_jobs':0}
target.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print('Linux offline guard/replay returncode',p.returncode,flush=True)
if p.returncode:print(p.stderr,flush=True)
assert p.returncode==0
