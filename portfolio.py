

from dataclasses import dataclass
from functools import reduce

from comp import *

@dataclass
class Asset:
    name: str
    price_t: int
    swing: int = 10
    unit_no: int = 0

@dataclass
class HoldingPosition:
    asset: Asset

@dataclass
class Prediction: 
    asset: Asset 
    up_price_t_plus_one: int
    down_price_t_plus_one: int

@dataclass
class ProfitEstimator:
    asset: Asset 
    profit_sum: int

@dataclass
class ActingPosition:
    asset: Asset

def predict(asset: Asset, swing: int) -> Prediction: 
    return Prediction(asset, asset.price_t + asset.price_t * asset.swing / 100, asset.price_t - asset.price_t * asset.swing / 100)

def profit(prediction: Prediction, buy_sell: int) -> ProfitEstimator:
    return ProfitEstimator(prediction.asset, 
        buy_sell * ((prediction.up_price_t_plus_one - prediction.asset.price_t) + 
        (prediction.down_price_t_plus_one - prediction.asset.price_t)))

def add_formula_chunk(acc: Sum, profit: ProfitEstimator) -> Sum:
    return Sum(acc, Mul(profit1.profit_sum, profit1.asset.name))

def optimize(computer: Computer, portfolio: list[HoldingPosition], assets_of_interest: list[Asset]) -> list[ActingPosition]:
    holding = portfolio.filter(lambda x: x.asset in assets_of_interest)
    candidates = portfolio.filter(lambda x: not x.asset in assets_of_interest)

    sell_profits = holding.map(lambda x: profit(predict(x.asset), 1))
    buy_profits = candidates.map(lambda x: profit(predict(x.asset), -1))
    profits = buy_profits + sell_profits

    formula = reduce(add_formula_chunk, profits, Zero())
    result = computer.maximize(formula).items().filter(lambda x: x[1] == 1).map(x[0]) # todo dict as tuples, tuple access
    
    return profits.filter(lambda x: x.asset.name in result).map(x => ActingPosition(x.asset))

    
