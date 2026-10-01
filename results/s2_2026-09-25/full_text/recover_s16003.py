"""Exact public Europe PMC SI recovery; no screening decisions or keyed access."""
import hashlib
import json
import pathlib
import re
import urllib.request
import xml.etree.ElementTree as ET
import urllib.parse
from datetime import datetime, timezone

import fitz

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / 'openai_public_si_continuation_2026-10-01' / 's16003'
DOI = '10.1002/advs.202201654'
BASE = 'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9376819/'


def new_file(path, data):
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError('Existing evidence differs: ' + path.name)
        return
    with path.open('xb') as handle:
        handle.write(data)


def get(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'sts-public-si/1.0'})
    with urllib.request.urlopen(request, timeout=45) as handle:
        if handle.status != 200:
            raise ValueError('Public route not HTTP 200')
        data = handle.read(50 * 1024 * 1024 + 1)
        if len(data) > 50 * 1024 * 1024:
            raise ValueError('Public package exceeds size bound')
        return data


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    xml_path = OUT / 'S16003.xml'
    xml_data = xml_path.read_bytes() if xml_path.exists() else get(BASE + 'fullTextXML')
    article = ET.fromstring(xml_data)
    if article.findtext('.//article-id[@pub-id-type="doi"]').lower() != DOI:
        raise ValueError('Wrong article DOI')
    if article.findtext('.//article-id[@pub-id-type="pmcid"]') != 'PMC9376819':
        raise ValueError('Wrong PMC identity')
    xml_text = xml_data.decode('utf8')
    supplements = re.findall(r'<supplementary-material\b[\s\S]*?</supplementary-material>', xml_text)
    if len(supplements) != 1:
        raise ValueError('Supplement inventory changed; completeness needs review')
    block = supplements[0]
    filename = re.search(r'xlink:href="([^"]+)"', block).group(1)
    expected_md5 = re.search(r'<\?suppdata-md5 ([a-f0-9]{32})\?>', block).group(1)
    expected_bytes = int(re.search(r'<\?suppdata-size (\d+)\?>', block).group(1))
    if filename != 'ADVS-9-2201654-s001.pdf':
        raise ValueError('Unexpected declared supplementary filename')
    new_file(xml_path, xml_data)
    # The Europe PMC package request timed out on the first attempt; do not
    # retry it. NLM's independently public, documented cloud dataset exposes
    # the exact declared file with the same MD5 and no login requirement.
    cloud = 'https://pmc-oa-opendata.s3.amazonaws.com/'
    metadata_url = cloud + 'PMC9376819.1/PMC9376819.1.json'
    metadata = json.loads(get(metadata_url))
    if metadata['doi'].lower() != DOI:
        raise ValueError('Cloud metadata DOI mismatch')
    si_links = [u for u in metadata['media_urls']
                if pathlib.PurePosixPath(urllib.parse.urlsplit(u).path).name == filename]
    if len(si_links) != 1:
        raise ValueError('Cloud SI missing or duplicated')
    si_url = si_links[0].replace('s3://pmc-oa-opendata/', cloud)
    if urllib.parse.parse_qs(urllib.parse.urlsplit(si_url).query).get('md5') != [expected_md5]:
        raise ValueError('XML/cloud MD5 disagreement')
    pdf = get(si_url)
    if len(pdf) != expected_bytes or hashlib.md5(pdf).hexdigest() != expected_md5 or not pdf.startswith(b'%PDF'):
        raise ValueError('Declared SI content identity mismatch')
    new_file(OUT / filename, pdf)
    new_file(HERE / 'files_si' / 'S16003_SI1.pdf', pdf)
    # Preserve the entire XML text, including captions/tables/references. Image
    # values remain subject to separate visual verification.
    main_text = '\n'.join(s.strip() for s in article.itertext() if s.strip())
    new_file(OUT / 'S16003_main.txt', main_text.encode('utf8'))
    main_url = metadata['pdf_url'].replace('s3://pmc-oa-opendata/', cloud)
    main_pdf = get(main_url)
    main_md5 = urllib.parse.parse_qs(urllib.parse.urlsplit(main_url).query)['md5'][0]
    if hashlib.md5(main_pdf).hexdigest() != main_md5 or not main_pdf.startswith(b'%PDF'):
        raise ValueError('Main PDF identity mismatch')
    new_file(OUT / 'S16003_main.pdf', main_pdf)
    with fitz.open(stream=main_pdf, filetype='pdf') as document:
        main_pdf_text=[]
        for i, page in enumerate(document):
            text = page.get_text()
            main_pdf_text.append('[main PDF p. ' + str(i+1) + ']\n' + text)
            if i == 0 or re.search(r'[Dd]ensity|[Cc]omputational|[Ff]ree.energy|Fig(?:ure)?\.?\s*4', text):
                page.get_pixmap(matrix=fitz.Matrix(1.6,1.6)).save(str(OUT / ('main_page_' + str(i+1) + '.png')))
        main_pages = len(document)
    new_file(OUT / 'S16003_main_pdf.txt', '\n\n'.join(main_pdf_text).encode('utf8'))
    pages=[]
    with fitz.open(stream=pdf, filetype='pdf') as document:
        for i, page in enumerate(document):
            text = page.get_text()
            pages.append('[SI file ' + filename + ' p. ' + str(i+1) + ']\n' + text)
            if i == 0 or re.search(r'Fig(?:ure)?\.?\s*S2[678]|[Dd]ensity [Ff]unctional|[Cc]omputational [Dd]etails|\(110\)', text):
                page.get_pixmap(matrix=fitz.Matrix(1.6, 1.6)).save(str(OUT / ('SI_page_' + str(i+1) + '.png')))
        count = len(document)
    si_text = '\n\n'.join(pages)
    new_file(OUT / 'S16003_si.txt', si_text.encode('utf8'))
    receipt = dict(at=datetime.now(timezone.utc).isoformat(), screen_id='S16003', doi=DOI,
        pmcid='PMC9376819', xml_url=BASE+'fullTextXML', metadata_url=metadata_url, si_url=si_url,
        main_url=main_url, main_md5=main_md5, main_pages=main_pages,
        prior_package_outcome='Europe PMC supplementaryFiles read timeout; not retried',
        filename=filename, declared_supplement_count=1, declared_bytes=expected_bytes,
        declared_md5=expected_md5, verified_md5=hashlib.md5(pdf).hexdigest(),
        sha256=hashlib.sha256(pdf).hexdigest(), xml_sha256=hashlib.sha256(xml_data).hexdigest(),
        license_code=metadata.get('license_code'), is_manuscript=metadata.get('is_manuscript'),
        pdf_pages=count, main_chars=len(main_text), si_chars=len(si_text),
        declared_inventory_complete=True, scientific_decision=None,
        access='Public Europe PMC XML + NLM Cloud Service; no credentials, browser, publisher API or institutional proxy')
    new_file(OUT / 'recovery.json', (json.dumps(receipt, indent=1)+'\n').encode('utf8'))
    print(json.dumps({k:v for k,v in receipt.items() if k!='package_members'}, indent=1))


if __name__ == '__main__':
    main()
