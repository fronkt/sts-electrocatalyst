"""Exact-path publication only after fresh offline and independent clearance."""
import hashlib,importlib.util,json,os,pathlib,subprocess
PHASE=pathlib.Path(__file__).resolve().parent;ROOT=PHASE.parents[1]
RECEIPT=PHASE/'publication.json'
assert not RECEIPT.exists(),'retain prior publication attempt'
ENV=dict(os.environ,GIT_TERMINAL_PROMPT='0',GCM_INTERACTIVE='never',GCM_GUI_PROMPT='0')
report={'scope':'REVIEWED_ONE_BOUNDARY_PRELAUNCH_PACKAGE','successful':False,'commands':[],
        'new_jobs_submitted':0,'qe_executed':False,'production_accepted':False}

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1048576),b''):h.update(chunk)
    return h.hexdigest()

def git(*args,timeout=45,binary=False):
    command=['git','-c','credential.interactive=never',*args]
    p=subprocess.run(command,cwd=ROOT,env=ENV,capture_output=True,timeout=timeout,creationflags=0x08000000)
    row={'args':command,'returncode':p.returncode}
    if not binary:row.update(stdout=p.stdout.decode('utf-8','replace'),stderr=p.stderr.decode('utf-8','replace'))
    report['commands'].append(row);assert p.returncode==0,row
    return p.stdout if binary else p.stdout.decode('utf-8').strip()

try:
    checked=json.loads((PHASE/'offline_checked.json').read_text());assert checked['successful']
    for rel,pin in checked['code_pins'].items():assert digest(ROOT/rel)==pin,'tested byte drift: '+rel
    review=PHASE/'independent_launch_review_final.md'
    assert 'Decision: GO_ONE_BOUNDARY_TRIAL_PRELAUNCH' in review.read_text()
    assert digest(review)=='0d8c4e0ea2eb4775fe5bf233326f8d5c86c765bb133ce1163cb9c2c49761d587'
    report['final_review_sha256']=digest(review);report['checked_receipt_sha256']=digest(PHASE/'offline_checked.json')
    spec=importlib.util.spec_from_file_location('trial_preservation_publication',PHASE/'verify_trial_offline.py')
    verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier)
    report['before']=verifier.preserve()
    assert git('rev-parse','HEAD')=='20119bb5cedea1ac957920133a6f7ff3396f7924'
    assert git('branch','--show-current')=='r0-catalysis-revival'
    assert not git('diff','--cached','--name-only'),'prior staged user work'
    paths=['tasks/todo.md','docs/research/pa-catalyst-trial-2026-10-03.md',
        'src/dft/pa_qe_adapter.py','src/dft/pa_catalyst_trial.py',
        'tests/test_pa_qe_adapter.py','tests/test_pa_catalyst_trial.py','tests/test_pa_catalyst_watch.py',
        'anvil/89_pa_catalyst_boundary_trial.slurm']
    paths += [p.relative_to(ROOT).as_posix() for p in PHASE.iterdir() if p.is_file()
        and p.name not in {'qe_source_tree_index.json','publication.json','commit_paths.json'}]
    for name in ['scientific_initial','scientific_checked']:
        paths += [p.relative_to(ROOT).as_posix() for p in (PHASE/name).glob('*.json')]
    paths.append('results/pa_catalyst_trial_2026-10-03/commit_paths.json');paths=sorted(set(paths))
    (PHASE/'commit_paths.json').write_text(json.dumps({'paths':paths,'source_cache_payloads_excluded':True,'unrelated_dft_excluded':True},indent=2)+'\n')
    report['paths']=paths;report['local_pins']={p:digest(ROOT/p) for p in paths}
    git('add','-f','--',*paths)
    assert set(git('diff','--cached','--name-only').splitlines())==set(paths),'staged path set differs'
    git('diff','--cached','--check')
    for rel in paths:
        blob=git('show',':'+rel,binary=True);data=(ROOT/rel).read_bytes()
        expected=data if rel.startswith('results/pa_catalyst_trial_2026-10-03/') else data.replace(b'\r\n',b'\n')
        assert blob==expected,'unexpected staged bytes: '+rel
    git('commit','-m','Add source-bound catalyst restart trial with capped resource guards',timeout=90)
    report['commit']=git('rev-parse','HEAD')
    git('push','origin','r0-catalysis-revival',timeout=180)
    remote=git('ls-remote','origin','refs/heads/r0-catalysis-revival',timeout=90).split()[0]
    assert remote==report['commit'];report['remote_commit']=remote
    assert not git('diff','--name-only') and not git('diff','--cached','--name-only')
    report['after']=verifier.preserve()
    for rel,pin in report['local_pins'].items():assert digest(ROOT/rel)==pin,'post-publication byte drift: '+rel
    report['successful']=True
except BaseException as exc:
    report['error']=repr(exc);raise
finally:
    RECEIPT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'successful':True,'commit':report['commit'],'remote_commit':report['remote_commit'],'explicit_paths':len(paths),'preserved':report['after'],'new_jobs_submitted':0},indent=2))
