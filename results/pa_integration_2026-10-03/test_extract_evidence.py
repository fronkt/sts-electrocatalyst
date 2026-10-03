"""Extraction guards use synthetic fixtures, never alter original sources."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('pa_eligible_extract_under_test', Path(__file__).with_name('extract_evidence.py'))
extract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extract)


class ExtractionGuards(unittest.TestCase):
    def test_fragment_requires_correct_page(self):
        claim = {'id':'x', 'fragment':'maximum free energy', 'marker':'[main: p.1]'}
        with self.assertRaises(ValueError):
            extract.check_claim(claim, '[main: p.1]\nunrelated\n[main: p.2]\nmaximum free energy')

    def test_ligature_and_linebreak_are_not_new_wording(self):
        extract.check_claim({'id':'x','fragment':'first maximum energy','marker':'[main: p.1]'},
                            '[main: p.1]\nﬁrst maximum\nenergy')

    def test_missing_or_duplicate_location_fails(self):
        for text in ('nothing', '[main: p.1]\na\n[main: p.1]\nb'):
            with self.assertRaises(ValueError):
                extract.section(text, '[main: p.1]')

    def test_merged_site_table_is_not_silently_flattened(self):
        headers = ['X'] + ['energy']*6 + ['max deltaG','Cus site element','Surface number']
        cells = ''.join('<w:tc><w:p><w:r><w:t>'+s+'</w:t></w:r></w:p></w:tc>' for s in headers)
        xml = '<w:document xmlns:w="'+extract.NS['w']+'"><w:body><w:tbl><w:tr>'+cells+'</w:tr><w:vMerge/></w:tbl></w:body></w:document>'
        with self.assertRaisesRegex(ValueError, 'merged'):
            extract.table_s3(xml)

    def test_missing_table_is_not_62_sites(self):
        with self.assertRaises(ValueError):
            extract.table_s3('<w:document xmlns:w="'+extract.NS['w']+'"/>')


if __name__ == '__main__':
    unittest.main()
