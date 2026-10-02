import pathlib
import tempfile
import unittest
import zipfile

import numpy as np
from ase import Atoms
from ase.io.trajectory import Trajectory

import inspect_mixed_formats as mixed


class MixedFormatTests(unittest.TestCase):
    def test_retain_preserves_identical_and_refuses_differing_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / 'copy.txt'
            mixed.retain(path, b'original')
            mixed.retain(path, b'original')
            with self.assertRaises(ValueError):
                mixed.retain(path, b'different')
            self.assertEqual(path.read_bytes(), b'original')

    def test_numpy_inventory_serializable(self):
        self.assertEqual(mixed.plain({'value': np.array([1., 2.]), 'count': np.int64(2)}),
                         {'value': [1., 2.], 'count': 2})

    def test_all_trajectory_frames_inspected_without_phase_inference(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / 'sample.traj'
            with Trajectory(str(path), 'w') as trajectory:
                trajectory.write(Atoms('OH', positions=[[0, 0, 0], [0, 0, 1]], cell=[5, 5, 5]))
                trajectory.write(Atoms('OH', positions=[[0, 0, 0], [0, 0, 1.1]], cell=[5, 5, 5]))
            result = mixed.inspect_trajectory(path)
            self.assertEqual(len(result['frames']), 2)
            self.assertEqual(result['frames'][0]['atoms'], 2)
            self.assertNotIn('phase', result)
            self.assertNotIn('disposition', result)

    def test_empty_trajectory_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / 'empty.traj'
            with Trajectory(str(path), 'w'):
                pass
            with self.assertRaises(ValueError):
                mixed.inspect_trajectory(path)

    def test_docx_includes_body_table_math_and_original_image(self):
        with tempfile.TemporaryDirectory(dir=mixed.HERE) as directory:
            folder = pathlib.Path(directory)
            path, out = folder / 'sample.docx', folder / 'out'
            xml = b'''<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"><w:body><w:p><w:r><w:t>Body</w:t></w:r><m:oMath><m:r><m:t>G</m:t></m:r></m:oMath></w:p><w:tbl><w:tr><w:tc><w:p><w:r><w:t>Table</w:t></w:r></w:p></w:tc></w:tr></w:tbl></w:body></w:document>'''
            with zipfile.ZipFile(path, 'w') as z:
                z.writestr('word/document.xml', xml)
                z.writestr('word/media/image1.png', b'original bytes')
            text, report = mixed.inspect_docx(path, out)
            self.assertIn('BodyG', text)
            self.assertIn('Table', text)
            self.assertEqual((out / 'docx_media/image1.png').read_bytes(), b'original bytes')
            self.assertFalse(report['layout_render_complete'])


if __name__ == '__main__':
    unittest.main()
