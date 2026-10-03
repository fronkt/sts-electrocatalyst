import importlib.util
import pathlib
import tempfile
import unittest
import xml.etree.ElementTree as ET

HERE = pathlib.Path(__file__).resolve().parent

def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE/(name+'.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

class IntakeTests(unittest.TestCase):
    def test_retain_refuses_different_copy(self):
        prep = module('prepare_sources')
        with tempfile.TemporaryDirectory() as temporary:
            path = pathlib.Path(temporary)/'original'
            prep.retain(path,b'first')
            prep.retain(path,b'first')
            with self.assertRaises(ValueError):
                prep.retain(path,b'second')
            self.assertEqual(path.read_bytes(),b'first')

    def test_all_five_exact_local_sources(self):
        self.assertEqual(set(module('prepare_sources').SOURCES), {'S29636','S29420','S29447','S28435','S24094'})

    def test_accepted_view_excludes_deleted_and_moved_from(self):
        import sys
        sys.path.insert(0,str(HERE))
        extras = module('inspect_word_extras')
        node=ET.fromstring('<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:r><w:t>keep</w:t></w:r><w:del><w:r><w:delText>old</w:delText></w:r></w:del><w:moveFrom><w:r><w:t>movedold</w:t></w:r></w:moveFrom><w:ins><w:r><w:t>new</w:t></w:r></w:ins><w:moveTo><w:r><w:t>movednew</w:t></w:r></w:moveTo></w:p>')
        self.assertEqual(extras.accepted_text(node),'keepnewmovednew')

    def test_math_tokens_survive_accepted_view(self):
        import sys
        sys.path.insert(0,str(HERE))
        extras=module('inspect_word_extras')
        node=ET.fromstring('<m:oMath xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"><m:r><m:t>∆G</m:t></m:r></m:oMath>')
        self.assertEqual(extras.accepted_text(node),'∆G')

    def test_both_passes_use_main_not_si_as_main(self):
        import json
        for family in ('pdf','word'):
            one=[json.loads(l) for l in (HERE/(family+'_pass1.in.jsonl')).read_text(encoding='utf-8').splitlines()]
            two=[json.loads(l) for l in (HERE/(family+'_pass2.in.jsonl')).read_text(encoding='utf-8').splitlines()]
            self.assertEqual(one,two)
            for row in one:
                self.assertNotEqual(row['text'],row['si_text'])
                self.assertIn('_main_reading.txt',row['text'])

if __name__=='__main__':
    unittest.main()
