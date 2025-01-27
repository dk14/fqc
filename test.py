import unittest
import warnings

from clacomp import *
from portfolio import *
from hamicomp import *
from testutil import *
from datetime import datetime
from typing import Callable

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
            
    # note: liquidity, is not taken into account (unconstrained optimization), potentially can penilize buys at t0 without sells
    # note: zero-risk interest (and overall inflation of usd) not taking into account. time value for money is out of scope
    def test_backtrack_ham_q(self): #todo fix
        t0 = datetime(2021, 5, 1)
        t1 = datetime(2022, 8, 1)
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
        to_hold = list(filter(lambda x: not x.name in result, market.assets_of_interest))

        # we take projection in absense of data
        project_price_up: Callable[[Asset], int] = lambda x: x.price_t + x.price_t * x.swing_up / 100
        project_price_down: Callable[[Asset], int]  = lambda x: x.price_t - x.price_t * x.swing_down / 100

        # buy t0, sell t1
        profit_from_buying_at_t0: Callable[[Asset], int]  = lambda x: get_price(t1, x.ticker, project_price_up(x)) - x.price_t

        # sell t0
        cash_from_selling_at_t0: Callable[[Asset], int]  = lambda x: x.price_t

        # hold t0, sell t1
        cash_from_selling_at_t1: Callable[[Asset], int]  = lambda x: get_price(t1, x.ticker, project_price_down(x))
        
        # backtracked portfolio value appreciation without taking any action
        
        no_action_fvs = map(lambda x:  cash_from_selling_at_t1(x.asset), market.positions)
        future_value_without_action = sum(no_action_fvs)

        # backtracked profits from taking action  
        
        action_fvs = map(lambda x:  profit_from_buying_at_t0(x) \
                         if x in to_buy else (cash_from_selling_at_t0(x) \
                                              if x in to_sell else cash_from_selling_at_t1(x)), market.assets_of_interest)
        
        future_value_with_action = sum(action_fvs)
        #print(future_value_with_action)
        #print(future_value_without_action)

        self.assertGreater(future_value_with_action, future_value_without_action)
        



if __name__ == '__main__':
        unittest.main()