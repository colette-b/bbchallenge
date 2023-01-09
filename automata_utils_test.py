from automata_utils import *
import unittest

class Tm_utils_test(unittest.TestCase):
    def test1(self):
        arr = [0, 3, 1, 2, 3, 3, 1, 0]
        d = dfa_from_array(arr)
        arr2 = dfa_to_array(d)
        assert arr == arr2

    def test2(self):
        arr = [0, 3, 1, 2, 3, 3, 1, 0]
        assert not dfa_has_sink_state(arr)
        arr2 = [0, 1, 1, 1]
        assert dfa_has_sink_state(arr2)

if __name__ == '__main__':
    unittest.main()
