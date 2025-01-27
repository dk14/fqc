import unittest

from clacomp import *
from portfolio import *
from hamicomp import *

appl = Asset("APPL", 100)
btc = Asset("BTC", 200)
math = Asset("MATH", 100)

class Testing(unittest.TestCase):

    def test_classic(self):
        computer = ClassicComputer()
        portfolio = [HoldingPosition(appl), HoldingPosition(btc)]
        candidates = [appl, btc, math]
        decisions = optimize(computer, portfolio, candidates)
        expected_decisions = [ActingPosition(appl), ActingPosition(btc)]
        self.assertEqual(decisions, expected_decisions)

if __name__ == '__main__':
    unittest.main()