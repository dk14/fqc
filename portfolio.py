

from dataclasses import dataclass
from functools import reduce

from comp import *

@dataclass
class Asset:
    name: str
    price_t: int
    swing_up: int = 10
    swing_down: int = 5
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

def predict(asset: Asset) -> Prediction: 
    return Prediction(asset, asset.price_t + (asset.price_t * asset.swing_up / 100), asset.price_t - (asset.price_t * asset.swing_down / 100))

def profit(prediction: Prediction, buy_sell: int) -> ProfitEstimator:
    return ProfitEstimator(prediction.asset, 
        buy_sell * ((prediction.up_price_t_plus_one - prediction.asset.price_t) + 
        (prediction.down_price_t_plus_one - prediction.asset.price_t)))

def add_formula_chunk(acc: Sum, profit: ProfitEstimator) -> Sum:
    return Sum(acc, Mul(profit.profit_sum, profit.asset.name))

def optimize(computer: Computer, portfolio: list[HoldingPosition], assets_of_interest: list[Asset]) -> list[ActingPosition]:
    holding = list(map(lambda x: x.asset, filter(lambda x: x.asset in assets_of_interest, portfolio)))
    candidates = list(filter(lambda x: not x in holding, assets_of_interest))

    sell_profits = list(map(lambda x: profit(predict(x), 1), holding))
    buy_profits = list(map(lambda x: profit(predict(x), -1), candidates))
    profits = buy_profits + sell_profits
    
    formula = reduce(add_formula_chunk, profits, Zero())
    result = list(map(lambda x: x[0], filter(lambda x: x[1] == 1, computer.maximize(formula).items())))
    
    return list(map(lambda x: ActingPosition(x), filter(lambda x: x.name in result, assets_of_interest)))

    
