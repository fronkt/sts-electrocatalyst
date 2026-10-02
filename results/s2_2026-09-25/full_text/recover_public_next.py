"""Retrieve declared public PMC sources, without assigning eligibility decisions."""
import hashlib
import json
import pathlib
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

import fitz

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / 'public_screening_next_2026-10-01'
CLOUD = 'https://pmc-oa-opendata.s3.amazonaws.com/'
XLINK = '{http://www.w3.org/1999/xlink}href'
BOUND = 60 * 1024 * 1024
RECOVERY_OUTCOMES = {
    'RECOVERED_DECLARED_INVENTORY',
    'RECOVERED_INVENTORY_NONPDF_REVIEW_NEEDED',
    'RECOVERY_UNRESOLVED',
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def local_member(name):
    """Require one plain filename/identifier, never a path or drive segment."""
    if (not isinstance(name, str) or not name or name in ('.', '..') or
            any(char in name for char in ('/', '\\', ':')) or
            pathlib.PurePath(name).is_absolute() or pathlib.PureWindowsPath(name).is_absolute()):
        raise ValueError('Unsafe local filename/member: ' + repr(name))
    return name


def member_path(directory, name):
    name = local_member(name)
    root = pathlib.Path(directory).resolve()
    path = (root / name).resolve()
    if path.parent != root:
        raise ValueError('Local filename resolves outside evidence directory: ' + repr(name))
    return path


def retain(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError('Existing evidence differs: ' + str(path))
        return
    with path.open('xb') as handle:
        handle.write(data)


def fetch(url, receipts):
    row = {'url': url, 'at': datetime.now(timezone.utc).isoformat()}
    receipts.append(row)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'sts-public-si/1.0'}), timeout=20) as response:
            row['status'] = response.status
            data = response.read(BOUND + 1)
            if len(data) > BOUND:
                raise ValueError('Payload exceeds retrieval bound')
            row.update(bytes=len(data), sha256=sha(data))
            return data
    except urllib.error.HTTPError as exc:
        row['status'] = exc.code
        raise
    except Exception as exc:
        row['error_type'] = type(exc).__name__
        raise


def pdf_text(data, filename, tag, dest):
    if not data.startswith(b'%PDF'):
        raise ValueError('Not a PDF: ' + filename)
    with fitz.open(stream=data, filetype='pdf') as document:
        if document.is_encrypted or not len(document):
            raise ValueError('Unreadable PDF')
        text = '\n\n'.join('[' + tag + ' ' + filename + ' p. ' + str(i+1) + ']\n' + p.get_text() for i, p in enumerate(document))
        document[0].get_pixmap(matrix=fitz.Matrix(1.2, 1.2)).save(str(dest / (filename + '.first.png')))
        return text, len(document)


def recover(record):
    sid, doi = record['sid'], record['doi']
    local_member(sid)
    pmcid = next(r['pmcid'] for r in record['exact_doi_results'] if r.get('pmcid'))
    local_member(pmcid)
    dest = OUT / 'files' / sid
    existing = member_path(dest, 'recovery.json')
    if existing.exists():
        receipt = json.loads(existing.read_text(encoding='utf8'))
        if not isinstance(receipt, dict) or any(receipt.get(key) != value for key, value in (
                ('screen_id', sid), ('doi', doi), ('pmcid', pmcid))):
            raise ValueError('Retained recovery identity mismatch: ' + sid)
        outcome = receipt.get('outcome')
        if outcome not in RECOVERY_OUTCOMES:
            raise ValueError('Invalid retained recovery outcome: ' + sid)
        file_hashes = receipt.get('file_hashes')
        if not isinstance(file_hashes, dict):
            raise ValueError('Invalid retained recovery hashes: ' + sid)
        required_files = {sid + '.xml', 'cloud_metadata.json', sid + '_main.pdf',
                          sid + '_main.txt', sid + '_si.txt'}
        declarations = receipt.get('declared_supplements', [])
        if not isinstance(declarations, list):
            raise ValueError('Invalid retained supplement declarations: ' + sid)
        declared_names = set()
        for supplement in declarations:
            if not isinstance(supplement, dict) or not isinstance(supplement.get('hrefs', []), list):
                raise ValueError('Invalid retained supplement declarations: ' + sid)
            for name in supplement.get('hrefs', []):
                local_member(name)
                declared_names.add(name)
        attachments = receipt.get('attachments', [])
        if not isinstance(attachments, list):
            raise ValueError('Invalid retained attachment manifest: ' + sid)
        attachment_names = set()
        for item in attachments:
            name = local_member(item.get('filename') if isinstance(item, dict) else None)
            required_files.add(name)
            attachment_names.add(name)
        if outcome != 'RECOVERY_UNRESOLVED':
            if not declared_names or attachment_names != declared_names:
                raise ValueError('Incomplete retained attachment inventory: ' + sid)
            required_files.update(declared_names)
            if not required_files.issubset(file_hashes):
                raise ValueError('Incomplete retained recovery hashes: ' + sid)
        for name, digest in file_hashes.items():
            path = member_path(dest, name)
            if not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest):
                raise ValueError('Invalid retained evidence hash: ' + repr(name))
            if not path.is_file() or sha(path.read_bytes()) != digest:
                raise ValueError('Retained evidence hash changed')
        print(sid, 'retained checkpoint', receipt['outcome'], flush=True)
        return receipt
    dest.mkdir(parents=True, exist_ok=True)
    receipt = {'screen_id': sid, 'doi': doi, 'pmcid': pmcid, 'scientific_decision': None, 'requests': [], 'file_hashes': {}, 'access': 'Public Europe PMC XML + independently public NLM cloud dataset; no credentials or publisher access.'}
    try:
        xml_url = 'https://www.ebi.ac.uk/europepmc/webservices/rest/' + pmcid + '/fullTextXML'
        xml_data = fetch(xml_url, receipt['requests'])
        article = ET.fromstring(xml_data)
        if (article.findtext('.//article-id[@pub-id-type="doi"]') or '').lower() != doi.lower():
            raise ValueError('XML DOI mismatch')
        if article.findtext('.//article-id[@pub-id-type="pmcid"]') != pmcid:
            raise ValueError('XML PMC mismatch')
        retain(dest / (sid + '.xml'), xml_data)
        receipt['file_hashes'][sid + '.xml'] = sha(xml_data)
        declaration = []
        for elem in article.findall('.//supplementary-material'):
            names = [el.get(XLINK) for el in elem.iter() if el.get(XLINK)]
            declaration.append({'id': elem.get('id'), 'hrefs': names, 'text': ' '.join(elem.itertext()).strip()})
        receipt['declared_supplements'] = declaration
        names = sorted(set(name for d in declaration for name in d['hrefs']))
        if not names:
            raise ValueError('No usable declared supplement inventory')
        for name in names:
            local_member(name)
        metadata_url = CLOUD + pmcid + '.1/' + pmcid + '.1.json'
        metadata_data = fetch(metadata_url, receipt['requests'])
        metadata = json.loads(metadata_data)
        if metadata.get('doi', '').lower() != doi.lower():
            raise ValueError('Cloud DOI mismatch')
        retain(dest / 'cloud_metadata.json', metadata_data)
        receipt['file_hashes']['cloud_metadata.json'] = sha(metadata_data)
        receipt.update(license_code=metadata.get('license_code'), is_manuscript=metadata.get('is_manuscript'))
        manifest = []
        for filename in names:
            media_urls = metadata.get('media_urls', [])
            if not isinstance(media_urls, list):
                raise ValueError('Invalid cloud media URL inventory')
            for media_url in media_urls:
                local_member(pathlib.PurePosixPath(urllib.parse.urlsplit(media_url).path).name)
            links = [u for u in media_urls if pathlib.PurePosixPath(urllib.parse.urlsplit(u).path).name == filename]
            if len(links) != 1:
                raise ValueError('Missing or duplicate declared file: ' + filename)
            url = links[0].replace('s3://pmc-oa-opendata/', CLOUD)
            parsed = urllib.parse.urlsplit(url)
            if parsed.scheme != 'https' or parsed.netloc != 'pmc-oa-opendata.s3.amazonaws.com':
                raise ValueError('Unexpected file origin')
            md5s = urllib.parse.parse_qs(parsed.query).get('md5', [])
            if len(md5s) != 1:
                raise ValueError('Missing attachment checksum')
            data = fetch(url, receipt['requests'])
            if hashlib.md5(data).hexdigest() != md5s[0]:
                raise ValueError('Cloud checksum mismatch')
            retain(member_path(dest, filename), data)
            receipt['file_hashes'][filename] = sha(data)
            manifest.append({'filename': filename, 'url': url, 'bytes': len(data), 'md5': md5s[0], 'sha256': sha(data)})
        receipt['attachments'] = manifest
        main_url = metadata.get('pdf_url', '').replace('s3://pmc-oa-opendata/', CLOUD)
        parsed = urllib.parse.urlsplit(main_url)
        local_member(pathlib.PurePosixPath(parsed.path).name)
        if parsed.scheme != 'https' or parsed.netloc != 'pmc-oa-opendata.s3.amazonaws.com':
            raise ValueError('Unexpected main PDF origin')
        main_pdf = fetch(main_url, receipt['requests'])
        if hashlib.md5(main_pdf).hexdigest() != urllib.parse.parse_qs(parsed.query).get('md5', [None])[0]:
            raise ValueError('Main PDF checksum mismatch')
        retain(dest / (sid + '_main.pdf'), main_pdf)
        receipt['file_hashes'][sid + '_main.pdf'] = sha(main_pdf)
        main_xml_text = '\n'.join(s.strip() for s in article.itertext() if s.strip())
        main_pdf_text, main_pages = pdf_text(main_pdf, sid + '_main.pdf', 'main PDF', dest)
        main_text = main_xml_text + '\n\n[Full main PDF text]\n' + main_pdf_text
        retain(dest / (sid + '_main.txt'), main_text.encode('utf8'))
        receipt['file_hashes'][sid + '_main.txt'] = sha(main_text.encode('utf8'))
        texts, all_pdf = [], True
        for item in manifest:
            if pathlib.Path(item['filename']).suffix.lower() == '.pdf':
                text, pages = pdf_text((dest / item['filename']).read_bytes(), item['filename'], 'SI file', dest)
                item['pages'] = pages
                texts.append(text)
            else:
                all_pdf = False
        si_text = '\n\n'.join(texts)
        retain(dest / (sid + '_si.txt'), si_text.encode('utf8'))
        receipt['file_hashes'][sid + '_si.txt'] = sha(si_text.encode('utf8'))
        receipt.update(main_pages=main_pages, main_chars=len(main_text), si_chars=len(si_text), declared_inventory_downloaded=True, text_inventory_complete=all_pdf, outcome='RECOVERED_DECLARED_INVENTORY' if all_pdf else 'RECOVERED_INVENTORY_NONPDF_REVIEW_NEEDED')
    except Exception as exc:
        receipt.update(outcome='RECOVERY_UNRESOLVED', error_type=type(exc).__name__, error=str(exc))
    receipt['completed_at'] = datetime.now(timezone.utc).isoformat()
    retain(existing, (json.dumps(receipt, indent=2) + '\n').encode('utf8'))
    print(sid, receipt['outcome'], receipt.get('main_chars'), receipt.get('si_chars'), receipt.get('error'), flush=True)
    return receipt


def main():
    records = json.loads((OUT / 'epmc_metadata_routes.json').read_text(encoding='utf8'))['records']
    receipts = []
    for record in records:
        if not any(r.get('pmcid') for r in record.get('exact_doi_results', [])):
            continue
        receipt = recover(record)
        receipts.append(receipt)
        if any(r.get('status') in (401, 403, 429) for r in receipt['requests']):
            print('Stop repository host after access/rate gate', flush=True)
            break
    retain(OUT / 'recovery_inventory.json', (json.dumps(receipts, indent=2) + '\n').encode('utf8'))


if __name__ == '__main__':
    main()
