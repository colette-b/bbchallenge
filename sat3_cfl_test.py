import unittest

from sat3_cfl import *
from glucose_wrapper import *
from db_utils import get_machine_i

class Sat3_cfl_test(unittest.TestCase):
    def test_n_equals_4(self):
        solvable = [3369312, 7540862, 72209248, 56564865, 10862042]
        unsolvable = [9848594, 10893168, 3970426, 7612407, 1039909]
        for idx in solvable:
            self.assertEqual(check_if_solved(4, TM(get_machine_i(idx))), True)
        for idx in unsolvable:
            self.assertEqual(check_if_solved(4, TM(get_machine_i(idx))), False)

if __name__ == '__main__':
    unittest.main()
