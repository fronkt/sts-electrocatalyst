import copy
import importlib.util
import pathlib
import unittest

HERE=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('priority_si_scope',HERE/'verify_phase.py')
scope=importlib.util.module_from_spec(spec)
spec.loader.exec_module(scope)

class ScopeTests(unittest.TestCase):
    def baseline(self):
        ids=sorted(scope.IDS)+['fixture'+str(i) for i in range(2491)]
        old=[{'screen_id':sid,'v5_final':'before','v3_final':'old3','v4_final':'old4','lane':'L','version_primary':sid,'v5_final_before_si':'old5'} for sid in ids]
        new=copy.deepcopy(old)
        for row in new[:5]:
            row['v5_final']='reviewed'
        return old,new

    def test_exact_five_row_changes(self):
        old,new=self.baseline()
        changed,errors=scope.changed_scope(old,new)
        self.assertEqual(set(changed),scope.IDS)
        self.assertEqual(errors,[])

    def test_unrelated_row_change_rejected(self):
        old,new=self.baseline()
        new[5]['v5_final']='unreviewed'
        self.assertTrue(scope.changed_scope(old,new)[1])

    def test_historical_field_change_rejected(self):
        old,new=self.baseline()
        new[0]['v4_final']='rewritten'
        self.assertTrue(any('historical field' in e for e in scope.changed_scope(old,new)[1]))

    def test_missing_record_rejected(self):
        old,new=self.baseline()
        self.assertEqual(scope.changed_scope(old,new[:-1])[1],['record population changed'])

    def test_one_of_five_not_changed_rejected(self):
        old,new=self.baseline()
        new[0]=copy.deepcopy(old[0])
        self.assertTrue(scope.changed_scope(old,new)[1])

if __name__=='__main__':
    unittest.main()
