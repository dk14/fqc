

from dataclasses import dataclass
from functools import reduce
from typing import Optional
import itertools

from comp import *

@dataclass
class Asset:
    name: str # ticker and (optionally) number
    price_t: int
    swing_up: int = 10 # walk up
    swing_down: int = 5 # walk down
    ticker: Optional[str] = None

# open position at t
@dataclass
class HoldingPosition:
    asset: Asset


# t+1 price delta (poor-man's random walk)
# can be estimated from volatility (or actual changes in price in case of pure optimizer's backtracking)
@dataclass
class Prediction: 
    asset: Asset 
    up_price_t_plus_one: int
    down_price_t_plus_one: int

# future profit. 
# if you open new position, value of portfolio will increase at t+1 = profit 
# if you close existing position, you'll prevent loss in value at t+1 = profit
@dataclass
class ProfitEstimator: 
    asset: Asset 
    profit_sum: int
    profit_up: int
    profit_down: int
    simple: bool = True

# if asset is in portfolio (at t), action would close the position
# otherwise - will open position
@dataclass
class ActingPosition:
    asset: Asset
    simple: bool = True
    optimistic: bool = False

# building a prediction for upper/lower price bracket (per asset or unit of asset)
def predict(asset: Asset) -> Prediction: 
    return Prediction(asset, asset.price_t + (asset.price_t * asset.swing_up / 100), asset.price_t - (asset.price_t * asset.swing_down / 100))

# calculate average profit from prediction
def profit(prediction: Prediction, buy_sell: int, simple: bool) -> ProfitEstimator:
    return ProfitEstimator(prediction.asset, 
        buy_sell * ((prediction.up_price_t_plus_one - prediction.asset.price_t) + 
        (prediction.down_price_t_plus_one - prediction.asset.price_t)),
        buy_sell * (prediction.up_price_t_plus_one - prediction.asset.price_t),
        buy_sell * (prediction.down_price_t_plus_one - prediction.asset.price_t))

# a term of abstract (computer-agnostic) weighted sum. one term per asset (or unit of asset)
def add_formula_chunk(acc: Sum, profit: ProfitEstimator) -> Sum:
    if profit.simple:
        return Sum(acc, Mul(profit.profit_sum, profit.asset.name))
    else:
        return Sum(Sum(acc, Mul(profit.profit_sum, profit.asset.name + "_up")), Mul(profit.profit_sum, profit.asset.name + "_down"))

def optimize(computer: Computer, portfolio: list[HoldingPosition], assets_of_interest: list[Asset], simple: bool = True) -> list[ActingPosition]:
    holding = [x.asset for x in portfolio if x.asset in assets_of_interest]
    candidates = [x for x in assets_of_interest if  not x in holding]

    sell_profits = [profit(predict(x), -1, simple) for x in holding]
    buy_profits = [profit(predict(x), 1, simple) for x in candidates]
    profits = buy_profits + sell_profits
    
    formula = reduce(add_formula_chunk, profits, Zero())
    result = [x[0] for x in computer.maximize(formula).items() if x[1] == 1]
    
    return ([ActingPosition(x) for x in assets_of_interest if x.name in result] 
            + [ActingPosition(x, False, False) for x in assets_of_interest if x.name + "_down" in result]
            + [ActingPosition(x, False, True) for x in assets_of_interest if x.name + "_up" in result])

# since variables (asset prices) are independent (thus problem is linear), we just split assets in chunks and aggregate all actions
def optimize_agg(qbits: int, computer: Computer, portfolio: list[HoldingPosition], assets_of_interest: list[Asset], simple: bool = True) -> list[ActingPosition]:
   chunks = [assets_of_interest[x:x+qbits] for x in range(0, len(assets_of_interest), qbits)]
   results = [optimize(computer, portfolio, chunk, simple) for chunk in chunks]
   return itertools.chain.from_iterable(results)

    
