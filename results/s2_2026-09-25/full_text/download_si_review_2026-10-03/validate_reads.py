"""Validate and pin original independent reads; one-row views are not new reads."""
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
FT = HERE.parent
sys.path.insert(0,str(FT))
from ft_screen import check
from reconcile import verified
from verify_evidence_recovery import row_errors
from prepare_sources import retain, jsonbytes, sha

def main():
    errors, originals, assessments = [], [], []
    for batch in ('pdf_pass1','pdf_pass2','word_pass1','word_pass2'):
        inp, out = HERE/(batch+'.in.jsonl'), HERE/(batch+'.out.jsonl')
        errors.extend([batch,e] for e in check(inp,out))
        inputs = [json.loads(l) for l in inp.read_text(encoding='utf-8').splitlines() if l.strip()]
        raw = [l for l in out.read_text(encoding='utf-8').splitlines() if l.strip()]
        outputs = [json.loads(l) for l in raw]
        assert len(inputs)==len(outputs)
        originals.append({'input':inp.name,'output':out.name,'sha256':sha(out),'records':len(outputs)})
        for source, row, line in zip(inputs,outputs,raw):
            sid = row['screen_id']
            assert source['screen_id']==sid
            text=(FT/source['text']).read_text(encoding='utf-8')+'\n'+(FT/source['si_text']).read_text(encoding='utf-8')
            errors.extend([sid,batch,e] for e in row_errors(row,text,True))
            if not verified(row,text):
                errors.append([sid,batch,'legacy deciding excerpt verification failed'])
            stem=sid.lower()+'_'+batch.split('_')[-1]
            retain(HERE/(stem+'.in.jsonl'),(json.dumps(source,ensure_ascii=False)+'\n').encode('utf-8'))
            retain(HERE/(stem+'.out.jsonl'),(line+'\n').encode('utf-8'))
            assessments.append({'screen_id':sid,'batch':batch,'output':stem+'.out.jsonl',
                                'sha256':sha(HERE/(stem+'.out.jsonl')),
                                'disposition':row['disposition'],'criteria':{c:row[c]['v'] for c in ('E1','E2','E3','E4','E5','E6')}})
    report={'original_source_assessments':len(assessments),'original_batch_outputs':originals,
            'one_row_views_are_additional_reads':False,'assessments':assessments,'errors':errors}
    retain(HERE/'initial_read_validation.json',jsonbytes(report))
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if errors:
        raise SystemExit(1)

if __name__=='__main__':
    main()
