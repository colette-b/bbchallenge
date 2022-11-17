from tm_utils import *
import unittest

class Tm_utils_test(unittest.TestCase):
    def test_basics1(self):
        sample_machine_code = '1RB1LC_0LA0LD_1LA---_1LB1RE_0RD0RB'
        tm = TM(sample_machine_code)
        self.assertEqual(tm.code, sample_machine_code)
        self.assertEqual(tm.tm_state_count, 5)
        self.assertEqual(tm.tape_symbol_count, 2)
        self.assertEqual(tm.tm_symbols, 'aAbBcCdDeE')
        self.assertEqual(
            tm.get_transition_info('a'),
            ('1', 'R', 'B')
        )
        self.assertEqual(
            tm.get_transition_info('A'),
            ('1', 'L', 'C')
        )
        self.assertEqual(
            tm.get_transition_info('A1'),
            ('1', 'L', 'C')
        )
        self.assertEqual(
            tm.get_transition_info(('A', '1')),
            ('1', 'L', 'C')
        )
        
    def test_basics2(self):
        sample_machine_code = '1RB1RA_1RC---_1LA---'
        tm = TM(sample_machine_code)
        self.assertEqual(tm.tm_state_count, 3)
        self.assertEqual(tm.tape_symbol_count, 2)
        self.assertEqual(tm.tm_symbols, 'aAbBcC')

    def test_basics3(self):
        sample_machine_code = '1RB0RB2RC_1RC2LA0LB_1RB---2RA'
        tm = TM(sample_machine_code)
        self.assertEqual(tm.tm_state_count, 3)
        self.assertEqual(tm.tape_symbol_count, 3)
        self.assertEqual(
            tm.get_transition_info(('A', '2')),
            ('2', 'R', 'C')
        )

    def test_simulator1(self):
        # a machine from bbchallenge front page
        sample_machine_code = '1RB1LC_0LA0LD_1LA1RZ_1LB1RE_0RD0RB'
        tm = TM(sample_machine_code)
        left, s, right = '', 'a', ''
        iteration = 1
        while not tm.is_final(s):
            left, s, right = tm.simulation_step(left, s, right)
            iteration += 1
        self.assertEqual(iteration, 2133492)

if __name__ == '__main__':
    unittest.main()