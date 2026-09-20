"""Bounded public DOI validation; no discovery search, OpenAlex, or scientific compute."""
from pathlib import Path
import hashlib, json, time, urllib.request, urllib.error
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
def sha(data): return hashlib.sha256(data).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
requests = json.loads((BASE / 'metadata_requests_supplement.json').read_text(encoding='utf-8-sig'))
cache_dir = ROOT / 'results/s2_2026-09-19/primary_identity_review'
old = json.loads((cache_dir / 'crossref_receipts.json').read_text(encoding='utf-8-sig'))
cache = {r['doi'].lower(): r for r in old}
raw_dir = BASE / 'crossref_supplement'
raw_dir.mkdir(exist_ok=True)
prior_run = json.loads((BASE / 'crossref_receipts_supplement.json').read_text(encoding='utf-8-sig')) if (BASE / 'crossref_receipts_supplement.json').exists() else []
resume_cache = {r['doi'].lower():r for r in prior_run if r['status'] in ('DOI_RESOLVED','CACHE_REUSED')}
receipts = []
deferred = False
for item in requests:
    doi = item['doi'].lower()
    target = raw_dir / (doi.replace('/', '__') + '.json')
    if doi in resume_cache:
        receipt = resume_cache[doi]
        raw = (ROOT / receipt['raw_path']).read_bytes()
        if sha(raw) != receipt['sha256']:
            raise ValueError('Resume receipt hash mismatch: ' + doi)
        if json.loads(raw).get('message',{}).get('DOI','').lower() != doi:
            raise ValueError('Resume DOI mismatch: ' + doi)
    elif doi in cache:
        prior = cache[doi]
        raw = (ROOT / prior['raw_path']).read_bytes()
        if sha(raw) != prior['sha256']:
            raise ValueError('Prior receipt hash mismatch: ' + doi)
        if target.exists() and target.read_bytes() != raw:
            raise ValueError('Existing destination differs: ' + doi)
        if not target.exists(): target.write_bytes(raw)
        receipt = {'doi':doi,'status':'CACHE_REUSED','url':prior['url'],
          'retrieved_utc':prior['retrieved_utc'],'reviewed_utc':now(),
          'prior_receipt_path':str((cache_dir / 'crossref_receipts.json').relative_to(ROOT)).replace('\\','/'),
          'raw_path':str(target.relative_to(ROOT)).replace('\\','/'),'sha256':sha(raw)}
    elif target.exists():
        raise ValueError('Unreceipted existing response; inspect before resume: ' + str(target))
    else:
        attempts=[]
        receipt={'doi':doi,'url':item['endpoint'],'status':'UNRESOLVED','attempts':attempts,'previous_receipts':[r for r in prior_run if r['doi'].lower()==doi]}
        for attempt in range(3):
            stamp=now()
            try:
                req=urllib.request.Request(item['endpoint'],headers={'User-Agent':'RegisteredLiteratureIdentityReview/1.0 (public DOI validation)','Accept':'application/json'})
                with urllib.request.urlopen(req,timeout=45) as response:
                    raw=response.read(); status=response.status
                data=json.loads(raw)
                returned=data.get('message',{}).get('DOI','').lower()
                if returned != doi: raise ValueError('Returned DOI mismatch: ' + returned)
                target.write_bytes(raw)
                attempts.append({'retrieved_utc':stamp,'http_status':status})
                receipt.update(status='DOI_RESOLVED',retrieved_utc=stamp,raw_path=str(target.relative_to(ROOT)).replace('\\','/'),sha256=sha(raw))
                break
            except urllib.error.HTTPError as exc:
                error_raw=exc.read()
                error_path=raw_dir / (doi.replace('/', '__') + '.error-' + stamp.replace(':','-').replace('+','_') + '-' + str(attempt+1) + '.txt')
                error_path.write_bytes(error_raw)
                attempts.append({'retrieved_utc':stamp,'http_status':exc.code,'error_path':str(error_path.relative_to(ROOT)).replace('\\','/'),'sha256':sha(error_raw)})
                receipt['http_status']=exc.code
                retry_after=exc.headers.get('Retry-After')
                if retry_after and exc.code in (429,503):
                    try: delay=max(0.0,float(retry_after))
                    except ValueError:
                        try: delay=max(0.0,(parsedate_to_datetime(retry_after)-datetime.now(timezone.utc)).total_seconds())
                        except Exception:
                            delay=61.0
                    attempts[-1]['retry_after']=retry_after
                    attempts[-1]['retry_after_seconds']=delay
                    if delay>60:
                        receipt['status']='DEFERRED_RETRY_AFTER'
                        deferred=True
                        break
                    time.sleep(delay)
                if exc.code not in (429,500,502,503,504): break
            except Exception as exc:
                attempts.append({'retrieved_utc':stamp,'error':str(exc)})
            if attempt < 2: time.sleep(2*(attempt+1))
        time.sleep(1.05)
    receipts.append(receipt)
    dump(BASE / 'crossref_receipts_supplement.json',receipts)
    print(doi, receipt['status'], flush=True)
    if deferred: break
dump(BASE / 'fetch_summary_supplement.json',{'finished_utc':now(),'request_count':len(requests),'receipt_count':len(receipts),'resolved_or_reused':sum(r['status'] in ('DOI_RESOLVED','CACHE_REUSED') for r in receipts),'deferred':deferred,'unrequested':[r['doi'] for r in requests if r['doi'] not in {x['doi'] for x in receipts}],'unresolved':[r['doi'] for r in receipts if r['status'] not in ('DOI_RESOLVED','CACHE_REUSED')],'script_sha256':sha(Path(__file__).read_bytes())})
