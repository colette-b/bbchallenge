from induction import *
from tm_utils import TM
from db_utils import get_machine_i
import unittest

b = BasicToken('0')
c = ComboToken('011', 0)
e = ComboToken('011', 1)
e2 = ComboToken('011', -1)
d = BasicToken('1')
t1 = TokenSeq([b, b, c])
t2 = TokenSeq([b, c])
rule = Rule([b], [d, d])
r1 = Rule([c, c], [b, c])
r2 = Rule([e, e], [b, e])
r3 = Rule([e2], [c, b, e])

class Induction_test(unittest.TestCase):
    def test1(self):
        self.assertTrue(t2 in t1)
        self.assertTrue(t1 not in t2)
        self.assertEqual(len(t1), 3)
        self.assertEqual(len(t2), 2)

    def test2(self):
        self.assertEqual(t1[0], b)
        self.assertEqual(t1[1], b)
        self.assertEqual(t1[2], c)
        self.assertEqual(t1[1:3], t2)

    def test3(self):
        self.assertEqual(
            list(t1.rule_yield(rule)),
            [TokenSeq([d, d, b, c]), TokenSeq([b, d, d, c])]
        )

    def test4(self):
        self.assertTrue(
            type(look_for_derivation(t1, TokenSeq([d, d, d, d, c]), [rule])) is Proof
        )
        self.assertTrue(
            look_for_derivation(t2, TokenSeq([d, d, d, d, c]), [rule]) is None
        )

    def test5(self):
        self.assertEqual(
            c,
            e.chg_offset(-1)
        )
        
    def test6(self):
        self.assertEqual(r1.minimal_valid_n(), 0)
        self.assertEqual(r2.minimal_valid_n(), 0)
        self.assertEqual(r3.minimal_valid_n(), 1)

    def test7(self):
        self.assertEqual(c.instantiate(1), '011')
        self.assertEqual(e.instantiate(1), '011011')

    def test8(self):
        tm = TM(get_machine_i(8210683))
        start = TokenSeq([ComboToken('11', 0), BasicToken('<'), BasicToken('C')])
        target = TokenSeq([BasicToken('<'), BasicToken('C'), ComboToken('00', 0)])
        wrong_target = TokenSeq([BasicToken('<'), BasicToken('E'), ComboToken('10', 0)])
        rule = Rule(start, target)
        wrong_rule = Rule(start, wrong_target)
        for i in range(5):
            self.assertTrue(rule.test_for_value(i, tm))
            self.assertFalse(wrong_rule.test_for_value(i, tm))


if __name__ == '__main__':
    unittest.main()