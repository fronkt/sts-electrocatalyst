"""Offline transcription of two eligible papers; no screening or eta derivation."""
import csv
import hashlib
import json
from pathlib import Path
import re
import unicodedata
import xml.etree.ElementTree as ET
import zipfile

PHASE = Path(__file__).resolve().parent
REPO = PHASE.parents[1]
FT = REPO / 'results/s2_2026-09-25/full_text'
PRIOR = FT / 'download_si_review_2026-10-03'
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
FIELDS = ['composition_x_author', 'dG_OH_eV', 'dG_OHtwist_eV', 'dG_O_Hb_eV',
          'dG_O_eV', 'dG_OOH_eV', 'dG_O2_Hb_eV', 'max_dGi_author_eV',
          'cus_element_author', 'surface_number_author']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', text).lower() if c.isalnum())


def section(text, marker):
    if text.count(marker) != 1:
        raise ValueError('source locator is absent or duplicated: ' + marker)
    tail = text.split(marker, 1)[1]
    return tail.split('\n[', 1)[0]


def check_claim(claim, text):
    fragment = canonical(claim['fragment'])
    if not fragment or fragment not in canonical(section(text, claim['marker'])):
        raise ValueError('fragment is not in its exact source location: ' + claim['id'])


def table_s3(xml):
    root = ET.fromstring(xml)
    def cell_text(cell):
        return ' '.join(' '.join(''.join(t.text or '' for t in p.findall('.//w:t', NS))
                                for p in cell.findall('w:p', NS)).split())
    candidates = []
    for candidate in root.findall('.//w:tbl', NS):
        first = candidate.find('w:tr', NS)
        if first is not None:
            header = [cell_text(c) for c in first.findall('w:tc', NS)]
            if (len(header) == 10 and header[0] == 'X' and 'max' in header[7]
                    and header[8:] == ['Cus site element', 'Surface number']):
                candidates.append(candidate)
    if len(candidates) != 1:
        raise ValueError('original Table S3 header is absent or nonunique')
    table = candidates[0]
    for tag in ('vMerge', 'gridSpan', 'gridBefore', 'gridAfter'):
        if table.findall('.//w:' + tag, NS):
            raise ValueError('merged/omitted cells need separate reviewed handling: ' + tag)
    rows = []
    for row in table.findall('w:tr', NS):
        cells = row.findall('w:tc', NS)
        if len(cells) != 10:
            raise ValueError('Table S3 row must have ten explicit cells')
        rows.append([cell_text(cell) for cell in cells])
    if len(rows) != 63 or rows[0][0] != 'X' or 'max' not in rows[0][7]:
        raise ValueError('Table S3 header/62-site population differs')
    if rows[0][8:] != ['Cus site element', 'Surface number']:
        raise ValueError('Table S3 column labels differ')
    for index, row in enumerate(rows[1:], 2):
        if any(not re.fullmatch(r'[+-]?\d+\.\d+', value) for value in row[1:8]):
            raise ValueError('nonliteral reported energy in Table S3 row ' + str(index))
        if row[8] not in ('Ru', 'Ir'):
            raise ValueError('unknown reported cus element')
    if rows[1][9] != '' or rows[-1][9] != '':
        raise ValueError('pure endpoint blank surface labels changed')
    return rows


def write_csv(path, fields, rows):
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def main():
    spec = json.loads((PHASE / 'evidence_spec.json').read_text(encoding='utf-8'))
    if set(spec['screen_ids']) != {'S29420', 'S29447'} or any(spec[k] is not False for k in
            ('screening_changes', 'cross_study_ranking_permitted', 'derived_eta', 'melt_candidates_selected')):
        raise ValueError('extraction scope changed')
    sources, texts = {}, {}
    for sid in spec['screen_ids']:
        meta = json.loads((PRIOR / (sid.lower() + '_source_metadata.json')).read_text(encoding='utf-8'))
        for source in meta['files']:
            path = FT / source['file']
            if sha(path) != source['sha256'] or path.stat().st_size != source['bytes']:
                raise ValueError('original binary pin differs: ' + sid)
        for kind, field, hashfield in [('main','text','text_sha256'), ('si','si_text','si_text_sha256')]:
            path = FT / meta[field]
            if sha(path) != meta[hashfield]:
                raise ValueError('source text pin differs: ' + sid)
            texts[sid, kind] = path.read_text(encoding='utf-8')
        sources[sid] = meta
    for claim in spec['claims']:
        check_claim(claim, texts[claim['screen_id'], claim['source']])
    ids = [claim['id'] for claim in spec['claims']]
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate claim identity')
    quantities = spec['reported_quantities']
    if [r['value'] for r in quantities] != ['0.59','0.75','0.56','0.73']:
        raise ValueError('reported conflicting pairs changed')
    for row in quantities:
        claim = next(c for c in spec['claims'] if c['id'] == row['claim_id'])
        if row['value'] not in claim['fragment'] or row['reported_unit'] != 'eV':
            raise ValueError('quantity is not verbatim author unit/value')
    write_csv(PHASE / 's29420_reported_eta.csv', list(quantities[0]), quantities)
    source = FT / sources['S29447']['files'][1]['file']
    with zipfile.ZipFile(source) as archive:
        xml = archive.read('word/document.xml')
    cache = PRIOR / 'files/S29447/document_original.xml'
    if xml != cache.read_bytes():
        raise ValueError('cached XML differs from original Word member')
    raw = table_s3(xml)
    site_rows = []
    for number, row in enumerate(raw[1:], 2):
        data = dict(zip(FIELDS, row))
        data.update(screen_id='S29447', original_table='S3', original_table_row=str(number),
                    potential_reference_author='U=0V vs RHE', quantity_route='author_assigned_limiting_potential',
                    eta_derived='false', source_si_sha256=sources['S29447']['files'][1]['sha256'])
        site_rows.append(data)
    write_csv(PHASE / 's29447_table_s3.csv', list(site_rows[0]), site_rows)
    report = {'schema':spec['schema'], 'source_pins_verified':sources, 'claims_verified':ids,
              'direct_reported_eta_rows':len(quantities), 'site_rows':len(site_rows),
              'table_header_author':raw[0], 'table_source_xml_sha256':sha(cache),
              'pure_endpoint_surface_number_blanks_retained':True,
              'no_recalculation_or_cross_study_ranking':True, 'screening_changes':False,
              'outputs':{name:sha(PHASE/name) for name in
                         ('s29420_reported_eta.csv','s29447_table_s3.csv')}, 'errors':[]}
    (PHASE / 'extraction_verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='source_pins_verified'},indent=2))
    return report


if __name__ == '__main__':
    main()
