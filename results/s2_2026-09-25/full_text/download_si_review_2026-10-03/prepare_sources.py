"""Pinned local SI intake and reading copies; no scientific verdicts or network."""
import csv
import hashlib
import importlib.util
import json
import pathlib
import re
import subprocess
import zipfile
import xml.etree.ElementTree as ET

import fitz
from PIL import Image, ImageDraw, ImageOps

HERE = pathlib.Path(__file__).resolve().parent
FT = HERE.parent
REPO = FT.parents[2]
DOWNLOADS = pathlib.Path('C:/Users/frank/Downloads')
SOURCES = {
    'S29636': ('10.26599/nre.2026.9120228', 'nre-0228_ESM.pdf'),
    'S29420': ('10.26599/nr.2026.94908680', '8680_ESM.pdf'),
    'S29447': ('10.1021/acscatal.5c08494', 'cs-2025-08494p_si_001.docx'),
    'S28435': ('10.26599/nr.2026.94908487', '8487_ESM.pdf'),
    'S24094': ('10.1002/adma.202414579', 'adma202414579-sup-0001-suppmat.docx'),
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def retain(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError('Refusing differing intake copy: ' + str(path))
    else:
        with path.open('xb') as stream:
            stream.write(data)

def jsonbytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')

def rows(path):
    with path.open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream))

def contacts(images, directory, stem):
    outputs = []
    for start in range(0, len(images), 6):
        canvas = Image.new('RGB', (1600, 2100), 'white')
        draw = ImageDraw.Draw(canvas)
        for j, path in enumerate(images[start:start+6]):
            with Image.open(path) as source:
                thumb = ImageOps.contain(source.convert('RGB'), (785, 650))
                x, y = (j % 2) * 800, (j // 2) * 700
                canvas.paste(thumb, (x + (800-thumb.width)//2, y+30))
                draw.text((x+10, y+8), path.name, fill='black')
        output = directory / (stem + '_' + str(start//6+1).zfill(2) + '.png')
        import io
        buffer = io.BytesIO()
        canvas.save(buffer, format='PNG')
        retain(output, buffer.getvalue())
        outputs.append(output.relative_to(FT).as_posix())
    return outputs

def pdf_read(path, out, sid, kind):
    texts, pages = [], []
    with fitz.open(path) as doc:
        if doc.is_encrypted or not len(doc):
            raise ValueError('Unreadable/empty PDF')
        embedded = doc.embfile_names()
        for number, page in enumerate(doc, 1):
            text = page.get_text()
            texts.append('[' + kind + ': ' + path.name + ' p. ' + str(number) + ']\n' + text)
            image = out / (kind + '_pages') / (sid + '_' + kind + '_p' + str(number).zfill(3) + '.png')
            retain(image, page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).tobytes('png'))
            pages.append({'page': number, 'chars': len(text), 'image': image.relative_to(FT).as_posix()})
        meta = dict(doc.metadata or {})
    text_path = out / (sid + '_' + kind + '_reading.txt')
    retain(text_path, ('\n\n'.join(texts) + '\n').encode('utf-8'))
    visual = contacts([FT/p['image'] for p in pages], out/'contacts', kind)
    return {'text': text_path.relative_to(FT).as_posix(), 'sha256': sha(text_path),
            'pages': pages, 'embedded_files': embedded, 'metadata': meta, 'contacts': visual}

def main():
    previous = json.loads((FT/'sequential_2026-10-03/baseline.json').read_text(encoding='utf-8'))
    pins = {name: sha(FT/name) for name in previous['files']}
    assert all(pins[name] == expected for name, expected in previous['files'].items())
    unrelated = {name: sha(REPO/name) for name in previous['unrelated_untracked_files']}
    assert unrelated == previous['unrelated_untracked_files']
    git = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=REPO, capture_output=True,
                         creationflags=0x08000000, timeout=15, check=True)
    assert git.stdout.decode().strip() == '3fe7219fee1cdc2604f4455e9589e937980d8431'
    baseline = {'git_head': git.stdout.decode().strip(), 'files': pins,
                'records': rows(FT/'reconcile/current_state.csv'), 'checklist': rows(FT/'si_checklist.csv'),
                'unrelated_untracked_files': unrelated, 'budget': previous['budget']}
    retain(HERE/'baseline.json', jsonbytes(baseline))
    spec = importlib.util.spec_from_file_location('sts_mixed_intake', FT/'inspect_mixed_formats.py')
    mixed = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mixed)
    metadata = {r['screen_id']: r for r in rows(FT/'si_checklist.csv')}
    records = []
    for sid, (doi, filename) in SOURCES.items():
        out = HERE/'files'/sid
        main_path, si_path = out/(sid+'_main.pdf'), out/filename
        retain(main_path, (FT/'files'/(sid+'.pdf')).read_bytes())
        retain(si_path, (DOWNLOADS/filename).read_bytes())
        record = {'screen_id': sid, 'doi': doi, 'title': metadata[sid]['title'],
                  'inventory_confirmed_by_entrant': True,
                  'identity_verified': False, 'si_complete_for_read': False,
                  'sources': [{'kind': 'main', 'file': main_path.relative_to(FT).as_posix(),
                               'sha256': sha(main_path), 'bytes': main_path.stat().st_size},
                              {'kind': 'si', 'file': si_path.relative_to(FT).as_posix(),
                               'download_path': str(DOWNLOADS/filename),
                               'sha256': sha(si_path), 'bytes': si_path.stat().st_size}]}
        record['main'] = pdf_read(main_path, out, sid, 'main')
        if si_path.suffix.lower() == '.pdf':
            record['si'] = pdf_read(si_path, out, sid, 'si')
        else:
            with zipfile.ZipFile(si_path) as archive:
                assert archive.testzip() is None, 'DOCX CRC failure'
                xml = archive.read('word/document.xml')
                record['docx_specials'] = {'omml_math_elements': xml.count(b'<m:oMath'),
                    'legacy_objects': xml.count(b'<w:object'), 'vml_images': xml.count(b'<v:imagedata'),
                    'embeddings': [n for n in archive.namelist() if n.startswith('word/embeddings/')],
                    'tracked_changes': xml.count(b'<w:ins') + xml.count(b'<w:del'),
                    'core_properties': archive.read('docProps/core.xml').decode('utf-8') if 'docProps/core.xml' in archive.namelist() else None}
            text, detail = mixed.inspect_docx(si_path, out)
            text_path = out/(sid+'_si_reading.txt')
            retain(text_path, text.encode('utf-8'))
            images = []
            for entry in detail['embedded_media']:
                original = FT/entry['file']
                decoded = original
                if original.suffix.lower() == '.wdp':
                    decoded = original.with_name(original.name+'.png')
                    if not decoded.exists():
                        command = '& {\n' + (HERE/'decode_wdp.ps1').read_text(encoding='utf-8') + '\n} -SourcePath '
                        command += "'" + str(original).replace("'", "''") + "' -TargetPath '" + str(decoded).replace("'", "''") + "'"
                        receipt = subprocess.run(['C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe',
                            '-NoProfile', '-NonInteractive', '-Command', command],
                            capture_output=True, creationflags=0x08000000, timeout=30)
                        if receipt.returncode:
                            raise ValueError('WDP decoder failed: '+receipt.stderr.decode('utf-8','replace'))
                    entry['conversion'] = 'Windows WIC/PngBitmapEncoder; original WDP retained'
                with Image.open(decoded) as image:
                    entry['image_format'] = image.format
                    entry['frames'] = getattr(image, 'n_frames', 1)
                    assert entry['frames'] == 1, 'Multi-frame media needs separate coverage'
                    if decoded.suffix.lower() not in ('.png', '.jpg', '.jpeg'):
                        import io
                        buffer = io.BytesIO()
                        image.convert('RGB').save(buffer, format='PNG')
                        display = original.with_name(original.name+'.png')
                        retain(display, buffer.getvalue())
                    else:
                        display = decoded
                entry['visual_file'] = display.relative_to(FT).as_posix()
                images.append(display)
            record['si'] = {'text': text_path.relative_to(FT).as_posix(), 'sha256': sha(text_path),
                            'docx': detail, 'contacts': contacts(images, out/'contacts', 'word')}
        retain(out/'source_metadata.json', jsonbytes(record))
        records.append(record)
        print(sid, 'main_pages', len(record['main']['pages']), 'SI', filename, flush=True)
    retain(HERE/'source_inventory.json', jsonbytes({'records': records, 'new_paid_external_api_calls': 0,
                                                   'identity_review': 'pending', 'attachment_coverage': 'entrant confirms every listed attachment downloaded'}))
    print('Pinned all five packages; identity/visual coverage gates remain pending.', flush=True)

if __name__ == '__main__':
    main()
