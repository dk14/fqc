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

market1 = read_portfolio(limit = None, point_to_unit = 1)
market2 = read_portfolio(limit = 4, point_to_unit = 1)

class Testing(unittest.TestCase):

    def test_classic(self):
        computer = ClassicComputer()
        portfolio = [HoldingPosition(appl), HoldingPosition(btc)]
        candidates = [appl, btc, math]
        decisions = optimize(computer, portfolio, candidates)
        expected_decisions = [ActingPosition(math)]
        self.assertEqual(decisions, expected_decisions)

    def test_hamiltonian_classic(self):
        computer = HamiltonianComputerClassicEigen()
        portfolio = [HoldingPosition(appl), HoldingPosition(btc)]
        candidates = [appl, btc, math]
        decisions = optimize(computer, portfolio, candidates)
        expected_decisions = [ActingPosition(math)]
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
            expected_decisions = [ActingPosition(math)]
            self.assertEqual(decisions, expected_decisions)

    def test_full_portfolio(self):
        market = market1
        self.assertEqual(len(market.assets_of_interest), 70)
        self.assertEqual(len(market.positions), 42)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning, module=r'.*qiskit.*')
            warnings.filterwarnings("ignore", category=PendingDeprecationWarning, module=r'.*qiskit.*') 
            warnings.filterwarnings("ignore", category=DeprecationWarning, module=r'.*portfolio.*')

            # optimize(HamiltonianComputerQuantum(), market.positions, market.assets_of_interest)
            # Insufficient memory to run circuit nlocal using the statevector simulator. Required memory: 18014398509481984M, max memory: 16384M'

    
    def test_portfolio_chunk_ham_classic(self):
        market = market2
        self.assertEqual(len(market.assets_of_interest), 4)
        self.assertEqual(len(market.positions), 2)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning, module=r'.*qiskit.*')
            warnings.filterwarnings("ignore", category=PendingDeprecationWarning, module=r'.*qiskit.*') 
            warnings.filterwarnings("ignore", category=DeprecationWarning, module=r'.*portfolio.*')
            actions = optimize(HamiltonianComputerClassicEigen(), market.positions, market.assets_of_interest)
            result = [x.asset.name for x in actions] 
            dump('decisions_chunk_ham_classic', result)
            self.assertEqual(result, load('decisions_chunk_ham_classic'))
        

    def test_portfolio_chunk_ham_q(self):
        market = market2
        self.assertEqual(len(market.assets_of_interest), 4)
        self.assertEqual(len(market.positions), 2)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning, module=r'.*qiskit.*')
            warnings.filterwarnings("ignore", category=PendingDeprecationWarning, module=r'.*qiskit.*') 
            warnings.filterwarnings("ignore", category=DeprecationWarning, module=r'.*portfolio.*')
            actions = optimize(HamiltonianComputerQuantum(), market.positions, market.assets_of_interest)
            result = [x.asset.name for x in actions] 
            dump('decisions_chunk_q', result)
            self.assertEqual(result, load('decisions_chunk_q'))
            
    # note: liquidity, is not taken into account (unconstrained optimization), potentially can penilize buys at t0 without sells
    # note: zero-risk interest (and overall inflation of usd) not taking into account. time value for money is out of scope
    # note: USD holdings from immediate sell (at t0) are considered part of future value. USD is both metric and an asset on its own
    def test_backtest_ham_q(self): #todo fix

        t0 = datetime(2021, 5, 1)
        t1 = datetime(2022, 8, 1)
        point_to_unit = 100000
        real_market = read_portfolio(limit = 15, point_to_unit = point_to_unit, t0 = t0, t1 = t1, risk = RiskModel(1, 0))
        market = real_market

        #self.assertEqual(len(market.assets_of_interest), 4)
        #self.assertEqual(len(market.positions), 2)


        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning, module=r'.*qiskit.*')
            warnings.filterwarnings("ignore", category=PendingDeprecationWarning, module=r'.*qiskit.*') 
            warnings.filterwarnings("ignore", category=DeprecationWarning, module=r'.*portfolio.*')

            actions = optimize_agg(3, HamiltonianComputerQuantum(), market.positions, market.assets_of_interest)
            # simulator bug?? limit = 10, qbits = 3, qiskit.exceptions.QiskitError: 'block_size (2) cannot be larger than number of qubits (1)'
            result = [x.asset.name for x in actions]
            dump('actions_backtesting', result)
        
        in_portfolio = [x.asset for x in market.positions]
        to_sell = [x.asset for x in market.positions if x.asset.name in result]
        to_buy = [x for x in market.assets_of_interest if x.name in result and not x in in_portfolio]
        to_hold = [x for x in market.assets_of_interest if not x.name in result] 

        #print(to_sell)
        #print(to_buy)
        #print(to_hold)

        # we take projection in absense of data
        project_price_up: Callable[[Asset], int] = lambda x: x.price_t + x.price_t * x.swing_up / 100
        project_price_down: Callable[[Asset], int]  = lambda x: x.price_t - x.price_t * x.swing_down / 100

        # buy t0, sell t1 (liquidity note: immediate zero-interest loan assumed)
        profit_from_buying_at_t0: Callable[[Asset], int]  = lambda x: get_price(t1, x.ticker, project_price_up(x)) - x.price_t

        # sell t0
        cash_from_selling_at_t0: Callable[[Asset], int]  = lambda x: x.price_t

        # hold t0, sell t1
        cash_from_selling_at_t1: Callable[[Asset], int]  = lambda x: get_price(t1, x.ticker, project_price_down(x))
        
        # backtested portfolio value appreciation without taking any action
        
        no_action_fvs = map(lambda x:  cash_from_selling_at_t1(x.asset), market.positions)
        future_value_without_action = sum(no_action_fvs) * point_to_unit

        # backtested profits from taking action  
        
        action_fv: Callable[[Asset], int] = lambda x:  profit_from_buying_at_t0(x) \
                         if x in to_buy else (cash_from_selling_at_t0(x) \
                                              if x in to_sell else cash_from_selling_at_t1(x))
        action_fvs = map(action_fv, market.assets_of_interest)
        
        future_value_with_action = sum(action_fvs) * point_to_unit
        #print(future_value_with_action)
        #print(future_value_without_action)

        report = [Report(x.name,
                x in in_portfolio,
                x.price_t, 
                get_price(t1, x.ticker, project_price_down(x)), 
                "BUY" if x in to_buy else "SELL" if x in to_sell else "NONE", 
                cash_from_selling_at_t1(x),  
                action_fv(x)) for x in market.assets_of_interest]

        dump_csv_report(report)
        self.assertGreater(future_value_with_action, future_value_without_action)
        
if __name__ == '__main__':
        unittest.main()