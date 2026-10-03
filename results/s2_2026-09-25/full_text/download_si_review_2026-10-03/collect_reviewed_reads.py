"""Pin frozen assessment batches and retain exact one-paper views, not new reads."""
import json
import pathlib
import sys

HERE=pathlib.Path(__file__).resolve().parent
FT=HERE.parent
sys.path.insert(0,str(FT))
from prepare_sources import retain,jsonbytes,sha
from ft_screen import check
from verify_evidence_recovery import row_errors
from reconcile import verified

def main():
    registry=json.loads((HERE/'assessment_batches.json').read_text(encoding='utf-8'))
    originals=[]
    total,initial=0,0
    for batch in registry['batches']:
        stem=batch['name']
        inp,out=HERE/(stem+'.in.jsonl'),HERE/(stem+'.out.jsonl')
        sources=list(map(json.loads,inp.read_text(encoding='utf-8').splitlines()))
        raw=out.read_text(encoding='utf-8').splitlines()
        rows=list(map(json.loads,raw))
        assert len(sources)==len(rows)==batch['records']
        assert [r['screen_id'] for r in sources]==[r['screen_id'] for r in rows]
        total+=len(rows)
        if batch['kind']=='initial independent':initial+=len(rows)
        errors=check(inp,out)
        for source,row,line in zip(sources,rows,raw):
            text=(FT/source['text']).read_text(encoding='utf-8')+'\n'+(FT/source['si_text']).read_text(encoding='utf-8')
            errors.extend(row['screen_id']+': '+e for e in row_errors(row,text,True))
            if not verified(row,text):errors.append(row['screen_id']+': deciding excerpt verification failed')
            if batch['kind']!='initial independent':
                target=row['screen_id'].lower()+'_'+batch['view_suffix']
                retain(HERE/(target+'.in.jsonl'),(json.dumps(source,ensure_ascii=False)+'\n').encode('utf-8'))
                retain(HERE/(target+'.out.jsonl'),(line+'\n').encode('utf-8'))
        originals.append({'input':inp.name,'input_sha256':sha(inp),'output':out.name,'sha256':sha(out),'records':len(rows),'kind':batch['kind'],'initial_validation_errors_retained':errors})
    assert initial==10
    report={'initial_source_assessments':initial,'all_source_assessments':total,'original_outputs':originals,'transcription_repairs_and_one_row_views_are_additional_reads':False}
    retain(HERE/'assessment_history.json',jsonbytes(report))
    print('Frozen source assessments:',total,'in',len(originals),'batches')

if __name__=='__main__':
    main()
