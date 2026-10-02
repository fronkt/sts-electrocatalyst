import unittest

from check_s26411_coordinates import inspect_block

BASE = "RuO2\n1\n4 0 0\n0 4 0\n0 0 12\nRu O\n1 2\nCartesian\n0 0 0\n1 1 1\n2 2 2\n"


class CoordinateGateTests(unittest.TestCase):
    def test_complete_counts(self):
        row = inspect_block(BASE)
        self.assertTrue(row["complete"])
        self.assertEqual(row["coordinate_rows"], 3)

    def test_incomplete_no_reconstruction(self):
        row = inspect_block(BASE.rsplit("2 2 2", 1)[0])
        self.assertFalse(row["complete"])
        self.assertEqual(row["missing_coordinate_rows"], 1)
        self.assertEqual(row["identity_check"], "REFUSED_INCOMPLETE_COORDINATES")

    def test_nonfinite_refused(self):
        with self.assertRaises(ValueError):
            inspect_block(BASE.replace("2 2 2", "nan 2 2"))

    def test_bad_header_refused(self):
        with self.assertRaises(ValueError):
            inspect_block(BASE.replace("1 2\nCartesian", "1 2 3\nCartesian"))
        with self.assertRaises(ValueError):
            inspect_block(BASE.replace("0 4 0", "4 0 0"))


if __name__ == "__main__":
    unittest.main()
