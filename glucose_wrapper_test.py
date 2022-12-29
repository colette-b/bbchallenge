import unittest
from pysat.formula import CNF
from glucose_wrapper import *

def unsat_formula():
    F = CNF()
    F.append([1])
    F.append([-1])
    return F

def sat_formula():
    F = CNF()
    F.append([1, 2])
    F.append([-1])
    return F
class Glucose_wrapper_test(unittest.TestCase):
    def test_unsat(self):
        result = run_glucose(1, unsat_formula())
        assert result == None

    def test_sat(self):
        result = run_glucose(1, sat_formula())
        assert result == [-1, 2]

if __name__ == '__main__':
    unittest.main()