

from dataclasses import dataclass
from abc import ABC, abstractmethod
from functools import reduce

@dataclass
class Asset:
    name: str
    price_t: int
    unit_no: int

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

# DSL

@dataclass
class Zero

@dataclass
class Sum:
    a: Sum | Zero
    b: Mul


type Const = int
type VarName = string

@dataclass
class Mul:
    a: Const
    b: VarName

type VarState = Dict[string, int]

class Computer(ABC):
    @abstractmethod
    def minimize(formula: Sum) -> VarState:
        # extract vars
        # bruteforce evaluations
        # find minimum
        pass


def predict(asset: Asset, swing: int) -> Prediction: 
    return Prediction(asset, asset.price_t + swing, asset.price_t, asset.price_t - swing)

def profit(prediction: Prediction, buy_sell: int) -> ProfitEstimator:
    return ProfitEstimator(prediction.asset, 
        buy_sell * ((prediction.up_price_t_plus_one - prediction.asset.price_t) + 
        (prediction.down_price_t_plus_one - prediction.asset.price_t)))

def add_formula_chunk(acc: Sum, profit: ProfitEstimator) -> Sum:
    return Sum(acc, Mul(profit1.profit_sum, profit1.asset.name))

def optimize(computer: Computer, portfolio: list[HoldingPosition], assets_of_interest: list[Asset], swing: int) -> list[ActingPosition]:
    holding = portfolio.filter(x.asset in assets_of_interest)
    candidates = portfolio.filter(not x.asset in assets_of_interest)
    sell_profits = holding.map(x => profit(predict(x.asset, swing), 1))
    buy_profits = candidates.map(x => profit(predict(x.asset, swing), -1))
    profits = [...buy_profits, sell_profits]
    formula = reduce(add_formula_chunk, profits, Zero())
    result = computer.minimize(formula).filter(x => x[1] == 1).map(x[0]) # todo dict as tuples, tuple access
    return profits.filter(x => x.asset.name in result).map(x => ActingPosition(x.asset))

    
