import sys, json, time, os, tempfile
from pathlib import Path
os.environ.setdefault('TORCHINDUCTOR_CACHE_DIR',str(Path(tempfile.gettempdir())/'sts-torch-cache'))
sys.path.insert(0,'src')
from scripts.screen_diagnostic import run
folder=Path('results/site_diagnostic_2026-09-06')
import argparse
parser=argparse.ArgumentParser(description='Repeat the bounded feasibility diagnostic without changing the original output.')
parser.add_argument('--model-file',type=Path,required=True)
parser.add_argument('--out',type=Path,required=True)
args=parser.parse_args()
model=args.model_file
m=json.loads((folder/'feasibility_manifest.json').read_text())
start=time.monotonic()
r=run(m,model,args.out,threads=2)
print('elapsed_seconds',time.monotonic()-start)
print('result_status',r['status'])
for x in r['results']:
 print(json.dumps({'status':x['status'],'quality':x.get('site_evidence',{}).get('quality_counts'),'error':x.get('error')}))
raise SystemExit(1 if r['status']=='complete_with_errors' else 0)
