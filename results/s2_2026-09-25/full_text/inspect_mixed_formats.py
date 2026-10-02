"""Local mixed-format reading copies and inventories; no eligibility inference."""
import csv
import hashlib
import json
import pathlib
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

import fitz
import numpy as np
from ase.io.trajectory import Trajectory

HERE = pathlib.Path(__file__).resolve().parent
SOURCE = HERE / 'public_screening_next_2026-10-01' / 'files'
OUTPUT = HERE / 'mixed_si_review_2026-10-02'
IDS = ('S12208', 'R0003', 'S24821', 'S25024')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def retain(path, data):
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError('Refusing differing reading copy: ' + str(path))
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as f:
            f.write(data)


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def plain(value):
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [plain(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return {'uninterpreted_type': type(value).__name__, 'repr': repr(value)}


def inspect_trajectory(path):
    frames = []
    with Trajectory(str(path), 'r') as trajectory:
        for i, atoms in enumerate(trajectory):
            if not np.isfinite(atoms.positions).all() or not np.isfinite(atoms.cell.array).all():
                raise ValueError('Nonfinite coordinates: ' + path.name)
            frames.append({'frame': i, 'atoms': len(atoms),
                           'formula': atoms.get_chemical_formula(),
                           'cell_angstrom': atoms.cell.array.tolist(),
                           'pbc': atoms.pbc.tolist(), 'info': plain(atoms.info),
                           'arrays': {k: {'shape': list(v.shape), 'dtype': str(v.dtype)} for k, v in atoms.arrays.items()},
                           'calculator_results': plain(atoms.calc.results) if atoms.calc else None})
    if not frames:
        raise ValueError('Empty trajectory: ' + path.name)
    return {'filename': path.name, 'sha256': sha(path), 'frames': frames,
            'coverage': 'All frames parsed and coordinate finiteness checked; no polymorph/facet reconstruction, eta calculation or eligibility inference.'}


def inspect_docx(path, out):
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
          'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math',
          'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
          'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
    segments, media = [], []
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if name.startswith('word/media/') and not name.endswith('/'):
                member = pathlib.PurePosixPath(name)
                if len(member.parts) != 3 or member.name in ('.', '..'):
                    raise ValueError('Unsafe embedded media path')
                data = z.read(name)
                target = out / 'docx_media' / member.name
                retain(target, data)
                media.append({'member': name, 'file': str(target.relative_to(HERE)).replace('\\', '/'),
                              'sha256': sha(target), 'bytes': len(data)})
        parts = [n for n in z.namelist() if n.startswith('word/') and n.endswith('.xml')
                 and (n == 'word/document.xml' or pathlib.PurePosixPath(n).name.startswith(('header','footer','footnotes','endnotes','comments')))]
        for name in parts:
            root = ET.fromstring(z.read(name))
            segments.append('[DOCX part ' + name + ']')
            for i, p in enumerate(root.findall('.//w:p', ns), 1):
                text = ''.join(e.text or '' for e in p.iter() if e.tag in ('{' + ns['w'] + '}t', '{' + ns['m'] + '}t'))
                images = [e.attrib.get('{' + ns['r'] + '}embed', '') for e in p.findall('.//a:blip', ns)]
                if text or images:
                    segments.append('[' + path.name + ' paragraph ' + str(i) + ']\n' + text +
                                    ('\n[embedded image relationship IDs: ' + ', '.join(images) + ']' if images else ''))
            relname = str(pathlib.PurePosixPath(name).parent / '_rels' / (pathlib.PurePosixPath(name).name + '.rels'))
            if relname in z.namelist():
                segments.append('[DOCX relationships ' + relname + ']\n' + z.read(relname).decode('utf-8'))
    return '\n\n'.join(segments), {'source': path.name, 'parts': parts, 'embedded_media': media,
                                  'layout_render_complete': False,
                                  'limitation': 'No bundled LibreOffice/loader available in this Windows session; scientific text/OMML and original embedded figures reviewed directly, not rendered page numbers.'}


def inspect_all():
    OUTPUT.mkdir(exist_ok=True)
    records = []
    for sid in IDS:
        source, out = SOURCE / sid, OUTPUT / 'files' / sid
        receipt = json.loads((source / 'recovery.json').read_text(encoding='utf-8'))
        for name, expected in receipt['file_hashes'].items():
            if sha(source / name) != expected:
                raise ValueError('Recovered source changed: ' + sid + '/' + name)
        record = {'screen_id': sid, 'doi': receipt['doi'], 'attachments': [], 'source_hashes': receipt['file_hashes'],
                  'si_complete_for_read': False, 'review_status': 'AWAITING_HUMAN_FORMAT_REVIEW'}
        source_main = source / (sid + '_main.txt')
        retain(out / (sid + '_main.txt'), source_main.read_bytes())
        si_parts = []
        trajectories = []
        for attachment in receipt['attachments']:
            path = source / attachment['filename']
            if sha(path) != attachment['sha256']:
                raise ValueError('Attachment changed')
            entry = dict(attachment)
            if path.suffix.lower() == '.pdf':
                pdf = fitz.open(path)
                pages = []
                for i, page in enumerate(pdf, 1):
                    text = page.get_text(sort=True)
                    si_parts.append('[' + path.name + ' p. ' + str(i) + ']\n' + text)
                    image = out / 'pdf_pages' / (path.stem + '_p' + str(i).zfill(3) + '.png')
                    retain(image, page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).tobytes('png'))
                    pages.append({'page': i, 'chars': len(text), 'image': str(image.relative_to(HERE)).replace('\\', '/')})
                entry['pages'] = pages
                pdf.close()
            elif path.suffix.lower() == '.traj':
                trajectories.append(inspect_trajectory(path))
            elif path.suffix.lower() == '.docx':
                text, detail = inspect_docx(path, out)
                si_parts.append(text)
                entry['docx'] = detail
            elif path.suffix.lower() == '.mp4':
                p = subprocess.run(['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', str(path)],
                                   capture_output=True, text=True, creationflags=0x08000000, timeout=60)
                if p.returncode:
                    raise ValueError('Video probe failed: ' + path.name)
                entry['probe'] = json.loads(p.stdout)
                entry['visual_review_complete'] = False
            else:
                raise ValueError('Unhandled format: ' + path.name)
            record['attachments'].append(entry)
        if trajectories:
            retain(out / 'trajectory_inventory.json', json_bytes({'records': trajectories}))
            si_parts.append('[Trajectory inventory: all 173 files parsed; machine inspection, not author prose]\n' + json.dumps(trajectories, ensure_ascii=False))
        si_path = out / (sid + '_si.txt')
        retain(si_path, '\n\n'.join(si_parts).encode('utf-8'))
        record['reading_copies'] = {'main': str((out / (sid + '_main.txt')).relative_to(HERE)).replace('\\', '/'),
                                    'si': str(si_path.relative_to(HERE)).replace('\\', '/'),
                                    'main_sha256': sha(out / (sid + '_main.txt')), 'si_sha256': sha(si_path)}
        retain(out / 'format_inventory.json', json_bytes(record))
        records.append(record)
        print(sid, 'attachments', len(record['attachments']), 'si_chars', len(si_path.read_text(encoding='utf-8')), flush=True)
    retain(OUTPUT / 'format_inventory.json', json_bytes({'records': records}))
    print('Local inventories verified; no eligibility decisions.', flush=True)


if __name__ == '__main__':
    inspect_all()
