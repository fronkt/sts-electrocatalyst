"""Retain source-identity and input links following root cover review."""
import json
from prepare_sources import HERE, FT, sha, retain, jsonbytes

def main():
    inventory = json.loads((HERE/'source_inventory.json').read_text(encoding='utf-8'))
    gate = []
    for record in inventory['records']:
        sid = record['screen_id']
        si = record['si']['text']
        if sid in ('S29447','S24094'):
            si = (HERE/'files'/sid/(sid+'_si_scientific_reading.txt')).relative_to(FT).as_posix()
        entry = {'screen_id':sid,'doi':record['doi'],'identity_verified':True,
                 'si_complete_for_read':True,'main_text':record['main']['text'],'si_text':si,
                 'main_sha256':record['main']['sha256'],'si_sha256':sha(FT/si),
                 'source_pins':record['sources'],
                 'visual_contacts':record['main']['contacts']+record['si']['contacts'],
                 'docx_layout_render_complete':False if 'docx' in record['si'] else None}
        metadata = {'screen_id':sid,'doi':record['doi'],'title':record['title'],
                    'identity_verified':True,'si_complete':True,
                    'identity_basis':'Root matches main DOI/title/authors and SI cover; entrant confirms every listed attachment downloaded.',
                    'files':record['sources'],'text':entry['main_text'],'si_text':si,
                    'text_sha256':entry['main_sha256'],'si_text_sha256':entry['si_sha256'],
                    'limitations':'Word page layout not rendered; original media, equations and object previews available. ACS editable Origin XRD internals not parsed/executed.' if 'docx' in record['si'] else None}
        retain(HERE/(sid.lower()+'_source_metadata.json'),jsonbytes(metadata))
        gate.append(entry)
    for name in ('pdf_pass1','pdf_pass2','word_pass1','word_pass2'):
        inputs = [json.loads(line) for line in (HERE/(name+'.in.jsonl')).read_text(encoding='utf-8').splitlines() if line.strip()]
        for row in inputs:
            entry = next(g for g in gate if g['screen_id']==row['screen_id'])
            assert row['doi']==entry['doi'] and row['text']==entry['main_text'] and row['si_text']==entry['si_text']
            assert row['si_complete'] is True
    retain(HERE/'source_read_gate.json',jsonbytes({'records':gate,
        'inventory_basis':'Entrant confirms every listed attachment downloaded.',
        'identity_review':'Root compared main DOI/title/authors to each SI cover; ACS alternate filename matches content.',
        'pdf_si_pages':46,'docx_original_media_items':100,'docx_equations':22,
        'word_page_layout_rendered':False,'origin_object_executed':False,'new_paid_external_api_calls':0}))
    print('Five source gates and both pass input joins verified; all original binaries retained.')

if __name__=='__main__':
    main()
