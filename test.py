import unittest

from clacomp import *
from hamicomp import *

class Testing(unittest.TestCase):
    appl = Asset("APPL", 300)
    btc = Asset("BTC", 200)
    math = Asset("MATH", 100)


    def test_classic(self):
        computer = ClassicComputer()
        portfolio = [HoldingPosition(appl), HoldingPosition(btc)]
        candidates = [math]
        decisions = optimize(computer, portfolio, candidates)
        expected_decisions = [ActingPosition(appl), ActingPosition(math)]
        self.assertEqual(decisions, expected_decisions)

if __name__ == '__main__':
    unittest.main()