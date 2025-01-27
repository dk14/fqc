import unittest
import warnings

from clacomp import *
from portfolio import *
from hamicomp import *
from testutil import *
import json

appl = Asset("APPL", 100)
btc = Asset("BTC", 200)
math = Asset("MATH", 100)

def dump(name: str, data):

    with open(name + '.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load(name: str):
    with open(name + '.json') as f:
        return json.load(f)

class Testing(unittest.TestCase):

    def test_classic(self):
        computer = ClassicComputer()
        portfolio = [HoldingPosition(appl), HoldingPosition(btc)]
        candidates = [appl, btc, math]
        decisions = optimize(computer, portfolio, candidates)
        expected_decisions = [ActingPosition(appl), ActingPosition(btc)]
        self.assertEqual(decisions, expected_decisions)

    def test_hamiltonian_classic(self):
        computer = HamiltonianComputerClassicEigen()
        portfolio = [HoldingPosition(appl), HoldingPosition(btc)]
        candidates = [appl, btc, math]
        decisions = optimize(computer, portfolio, candidates)
        expected_decisions = [ActingPosition(appl), ActingPosition(btc)]
        self.assertEqual(decisions, expected_decisions)

    def test_hamiltonian_quantum(self):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning, module=r'.*qiskit.*')
            warnings.filterwarnings("ignore", category=PendingDeprecationWarning, module=r'.*qiskit.*') 
            warnings.filterwarnings("ignore", category=DeprecationWarning, module=r'.*portfolio.*')

            computer = HamiltonianComputerQuantum()
            portfolio = [HoldingPosition(appl), HoldingPosition(btc)]
            candidates = [appl, btc, math]
            decisions = optimize(computer, portfolio, candidates)
            expected_decisions = [ActingPosition(appl), ActingPosition(btc)]
            self.assertEqual(decisions, expected_decisions)

    def test_full_portfolio(self):
        market = read_portfolio(limit = None, persent_to_unit = 1)
        self.assertEqual(len(market.assets_of_interest), 70)
        self.assertEqual(len(market.positions), 42)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning, module=r'.*qiskit.*')
            warnings.filterwarnings("ignore", category=PendingDeprecationWarning, module=r'.*qiskit.*') 
            warnings.filterwarnings("ignore", category=DeprecationWarning, module=r'.*portfolio.*')

            # optimize(HamiltonianComputerQuantum(), market.positions, market.assets_of_interest)
            # Insufficient memory to run circuit nlocal using the statevector simulator. Required memory: 18014398509481984M, max memory: 16384M'

    
    def test_portfolio_chunk_ham_classic(self):
        market = read_portfolio(limit = 4, persent_to_unit = 1)
        self.assertEqual(len(market.assets_of_interest), 4)
        self.assertEqual(len(market.positions), 2)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning, module=r'.*qiskit.*')
            warnings.filterwarnings("ignore", category=PendingDeprecationWarning, module=r'.*qiskit.*') 
            warnings.filterwarnings("ignore", category=DeprecationWarning, module=r'.*portfolio.*')

            result = list(map(lambda x: x.asset.name, optimize(HamiltonianComputerClassicEigen(), market.positions, market.assets_of_interest)))
            #dump('decisions_chunk_ham_classic', result)
            self.assertEqual(result, load('decisions_chunk_ham_classic'))
        

    def test_portfolio_chunk_ham_q(self):
        market = read_portfolio(limit = 4, persent_to_unit = 1)
        self.assertEqual(len(market.assets_of_interest), 4)
        self.assertEqual(len(market.positions), 2)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning, module=r'.*qiskit.*')
            warnings.filterwarnings("ignore", category=PendingDeprecationWarning, module=r'.*qiskit.*') 
            warnings.filterwarnings("ignore", category=DeprecationWarning, module=r'.*portfolio.*')

            result = list(map(lambda x: x.asset.name, optimize(HamiltonianComputerQuantum(), market.positions, market.assets_of_interest)))
            #dump('decisions_chunk_q', result)
            self.assertEqual(result, load('decisions_chunk_q'))
            
    def backtest_ham_q(self):
        return
        t0 = 100
        t1 = 1000
        market = read_portfolio(limit = 4, persent_to_unit = 1, t0 = t0, t1 = t1, risk = RiskModel(1.5, 0))
        self.assertEqual(len(market.assets_of_interest), 4)
        self.assertEqual(len(market.positions), 2)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning, module=r'.*qiskit.*')
            warnings.filterwarnings("ignore", category=PendingDeprecationWarning, module=r'.*qiskit.*') 
            warnings.filterwarnings("ignore", category=DeprecationWarning, module=r'.*portfolio.*')

            result = list(map(lambda x: x.asset.name, optimize(HamiltonianComputerQuantum(), market.positions, market.assets_of_interest)))
        
        to_sell = list(map(lambda x: x.asset, filter(lambda x: x.asset.name in result, market.positions)))
        to_buy = list(filter(lambda x: x.name in result and not x.name in to_sell, market.assets_of_interest))

        projected_profits = map(lambda x: x.price_t + x.swing_up if x in to_buy else x.price_t - x.swing_down, market.assets_of_interest)
        real_profits = map(lambda x: get_price(x.ticker, t1) - x.price_t if x in to_buy else x.price_t - get_price(x.ticker, t1), market.assets_of_interest)
        
        projected_revenue = sum(projected_profits)
        real_revenue = sum(real_profits)

        self.assertGreater(real_revenue, projected_revenue)



if __name__ == '__main__':
        unittest.main()