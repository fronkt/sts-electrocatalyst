"""One explicit output record for every requested input, including read failures."""
from pathlib import Path
import hashlib
import subprocess
from .classify import classify

def census(paths, oc20=False):
    from .readers.oc20 import read_oc20
    from .readers.qe import read_qe
    records=[]
    for name in paths:
        try:
            raw=read_oc20(name) if oc20 else read_qe(name)
            raw['path']=Path(name).as_posix()
            record=classify(raw,force_only=oc20)
        except (OSError,ValueError,KeyError,IndexError) as error:
            record=classify(dict(path=Path(name).as_posix(),unidentified=True,fatal_issues=[str(error)],force_steps=[],adsorbate_indices=[]),force_only=oc20)
        records.append(record)
    try:
        source_root=Path(__file__).resolve().parent.parent
        commit=(subprocess.run(['git','-C',str(source_root),'rev-parse','HEAD'],capture_output=True,text=True,timeout=5).stdout.strip() or None) if (source_root/'.git').exists() else None
    except (OSError,subprocess.TimeoutExpired):
        commit=None
    package=Path(__file__).parent
    sources={str(p.relative_to(package)):hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest() for p in sorted(package.rglob('*.py'))}
    return dict(schema='silentgate-census-v1',repository_head=commit,instrument_sha256_lf=sources,control_status='NOT MEASURED BY THIS INVOCATION',runs=records,n_unscorable=sum(r['unscorable'] for r in records),n_unidentified=sum(r.get('unidentified',False) for r in records))
