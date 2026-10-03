"""Read-only Word revisions, equations and embedded-object inventories."""
import hashlib
import io
import json
import pathlib
import subprocess
import zipfile
import xml.etree.ElementTree as ET
from lxml import etree

from prepare_sources import FT, HERE, retain, jsonbytes

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
      'o': 'urn:schemas-microsoft-com:office:office', 'v': 'urn:schemas-microsoft-com:vml'}
XSL = pathlib.Path('C:/Program Files/Microsoft Office/root/Office16/OMML2MML.XSL')
PANDOC = pathlib.Path('C:/Users/frank/AppData/Local/Pandoc/pandoc.exe')

def accepted_text(node):
    if node.tag in ('{'+NS['w']+'}del', '{'+NS['w']+'}moveFrom'):
        return ''
    if node.tag in ('{'+NS['w']+'}t', '{'+NS['m']+'}t'):
        return node.text or ''
    return ''.join(accepted_text(child) for child in node)

def main():
    transform = etree.XSLT(etree.parse(str(XSL)))
    summaries = []
    for sid, name in [('S29447','cs-2025-08494p_si_001.docx'),
                      ('S24094','adma202414579-sup-0001-suppmat.docx')]:
        out = HERE/'files'/sid
        path = out/name
        paragraphs, equations, revisions, objects = [], [], [], []
        with zipfile.ZipFile(path) as archive:
            data = archive.read('word/document.xml')
            retain(out/'document_original.xml', data)
            root = ET.fromstring(data)
            rel_data = archive.read('word/_rels/document.xml.rels')
            retain(out/'document_original.xml.rels', rel_data)
            rels = {n.attrib['Id']: n.attrib['Target'] for n in ET.fromstring(rel_data)}
            for i, paragraph in enumerate(root.findall('.//w:p', NS),1):
                text = accepted_text(paragraph)
                if text:
                    paragraphs.append('['+name+' paragraph '+str(i)+']\n'+text)
                for formula in paragraph.findall('.//m:oMath', NS):
                    source = ET.tostring(formula, encoding='utf-8')
                    result = transform(etree.fromstring(source))
                    mathml = bytes(result)
                    mathml_utf8 = etree.tostring(result, encoding='utf-8', xml_declaration=True)
                    idx = len(equations)+1
                    retain(out/'equations'/('equation_'+str(idx).zfill(3)+'.omml.xml'),source)
                    retain(out/'equations'/('equation_'+str(idx).zfill(3)+'.mathml.xml'),mathml)
                    retain(out/'equations'/('equation_'+str(idx).zfill(3)+'.mathml_utf8.xml'),mathml_utf8)
                    equations.append({'paragraph':i,'index':idx,'omml':source.decode(),'mathml':mathml_utf8.decode()})
                for tag in ('ins','del','moveFrom','moveTo'):
                    for change in paragraph.findall('.//w:'+tag,NS):
                        revisions.append({'paragraph':i,'kind':tag,'attributes':change.attrib,
                            'text':''.join(e.text or '' for e in change.iter() if e.tag in
                            ('{'+NS['w']+'}t','{'+NS['w']+'}delText','{'+NS['m']+'}t')),
                            'xml':ET.tostring(change,encoding='unicode')})
                for obj in paragraph.findall('.//w:object',NS):
                    info = {'paragraph':i,'xml':ET.tostring(obj,encoding='unicode'),'context':text}
                    ole = obj.find('.//o:OLEObject',NS)
                    if ole is not None:
                        info['attributes'] = ole.attrib
                        target = rels.get(ole.attrib.get('{'+NS['r']+'}id',''))
                        info['target'] = target
                        if target:
                            member = str(pathlib.PurePosixPath('word')/target)
                            blob = archive.read(member)
                            retain(out/'embedded_objects'/pathlib.PurePosixPath(target).name,blob)
                            info['bytes'] = len(blob)
                            info['sha256'] = hashlib.sha256(blob).hexdigest()
                            info['magic_hex'] = blob[:16].hex()
                            try:
                                import olefile
                                with olefile.OleFileIO(io.BytesIO(blob)) as compound:
                                    info['streams'] = [{'path':p,'bytes':compound.get_size(p)} for p in compound.listdir()]
                            except ImportError:
                                info['compound_stream_inventory'] = 'olefile unavailable; object not executed'
                    preview = obj.find('.//v:imagedata',NS)
                    if preview is not None:
                        info['preview_target'] = rels.get(preview.attrib.get('{'+NS['r']+'}id',''))
                    objects.append(info)
        receipt = subprocess.run([str(PANDOC), '--from=docx', '--to=markdown', '--track-changes=accept', str(path)],
                                 capture_output=True, creationflags=0x08000000, timeout=60)
        assert receipt.returncode == 0, receipt.stderr.decode('utf-8','replace')
        retain(out/(sid+'_pandoc_accepted.md'),receipt.stdout)
        text = '\n\n'.join(paragraphs)
        text += '\n\n[Structured equation/table reading aid: Pandoc accepted-revision view; not additional author evidence]\n'
        text += receipt.stdout.decode('utf-8')
        retain(out/(sid+'_si_scientific_reading.txt'),text.encode('utf-8'))
        report = {'screen_id':sid,'equations':equations,'revisions':revisions,'embedded_objects':objects,
                  'accepted_text_policy':'Exclude w:del/w:moveFrom; include w:ins/w:moveTo. Original XML and revision inventory retained.',
                  'xsl_sha256':hashlib.sha256(XSL.read_bytes()).hexdigest(),
                  'pandoc_stderr':receipt.stderr.decode('utf-8','replace'),
                  'docx_page_layout_rendered':False,'embedded_object_executed':False}
        retain(out/'word_extras.json',jsonbytes(report))
        summaries.append({'id':sid,'equations':len(equations),'revisions':revisions,'objects':objects,
                          'pandoc_stderr':report['pandoc_stderr']})
    retain(HERE/'word_extras_summary.json',jsonbytes(summaries))
    print(json.dumps(summaries,ensure_ascii=False,indent=2))

if __name__ == '__main__':
    main()
