from portfolio import Asset, HoldingPosition
from dataclasses import dataclass
from operator import add
from functools import reduce
import csv
import itertools
import yfinance as yf
from datetime import timedelta
from typing import Optional

@dataclass
class Allocation:
    ticker: str
    allocation: int # assume a unit = (1/persent_to_unit)%
    allocation_usd: int

@dataclass
class Market:
    assets_of_interest: list[Asset]
    positions: list[HoldingPosition]

@dataclass
class RiskModel:
    leverage: float = 1.0
    spread: float = 0.0


def sum_allocations_by_ticker(allocations: list[Allocation]) -> list[Allocation]:
    tickers = set(map(lambda x: x.ticker, allocations))
    grouped = [[y for y in allocations if y.ticker == x] for x in tickers]
    return list(map(lambda g: Allocation(g[0].ticker, reduce(add, map(lambda x: x.allocation, g)), reduce(add, map(lambda x: x.allocation_usd, g))), grouped))


def get_price(date, ticker: str, default = None):
    yticker = yf.Ticker(ticker)
    final_time = date + timedelta(days=40)
    prices = yticker.history(start=date, end=final_time, interval='1d')['Close'].iloc
    print(ticker)
    if len(list(prices)) == 0:
        return default
    else:
        print(prices[0])
        return int(prices[0])

def read_allocations(persent_to_unit, t0) -> list[Allocation]:
    with open('example_portfolio.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        def units(ticker, allocation, allocation_usd):
            if t0 == None:
                return allocation * persent_to_unit
            else:
                price = get_price(t0, ticker, None)
                if price != None:
                    return int(allocation_usd / price) + 1
                else:
                    return allocation * persent_to_unit
            
        allocations = [Allocation(row['ticker'], units(row['ticker'], int(float(row['allocation'])), int(float(row['allocation_usd']))), int(float(row['allocation_usd']))) for row in reader]
        return sum_allocations_by_ticker(allocations)



# todo: approximate price swings from (get_price(t1) - get_price(t0)) / get_price(t0)
def approximate_price_up(ticker: str, t0, t1, risk: RiskModel) -> int:
    if t0 == None:
        return 100
    else: 
       diff = 100 * (get_price(t1, ticker, 200) - get_price(t0, ticker, 100)) / get_price(t0, ticker, 100)
       if diff > 0:
           return risk.leverage * diff + risk.spread
       else:
           return risk.spread
           

def approximate_price_down(ticker: str, t0, t1, risk: RiskModel) -> int:
    if t0 == None:
        return 10
    else: 
       diff = 100 * (get_price(t1, ticker, 100) - get_price(t0, ticker, 110)) / get_price(t0, ticker, 100)
       if diff < 0:
           return risk.leverage * (- diff) + risk.spread
       else:
           return risk.spread

def get_asset_price(a: Allocation, t0) -> int:
    if t0 == None:
        if a.allocation == 0:
            return 1
        else:
            return a.allocation_usd / a.allocation
    else:
        return get_price(t0, a.ticker)

def get_assets(allocations: list[Allocation], t0, t1, risk: RiskModel) -> list[Asset]:
    def split(a: Allocation):
        price = get_asset_price(a, t0)
        price_up = approximate_price_up(a.ticker, t0, t1, risk)
        price_down = approximate_price_down(a.ticker, t0, t1, risk)
        return map(lambda i: Asset(a.ticker + "#" + str(i), price, price_up, price_down, a.ticker), range(0, a.allocation))

    fragmented = map(lambda a: split(a), allocations)
    return list(itertools.chain.from_iterable(fragmented))

def get_positions(assets: list[Asset], open_positions_ratio) -> list[HoldingPosition]:
    n = len(assets)
    k = int(open_positions_ratio * n)
    return list(map(lambda x: HoldingPosition(x), assets[:k]))

def read_portfolio(limit: Optional[int] = None, persent_to_unit = 10, t0 = None, t1 = None, open_positions_ratio = 0.6, risk: RiskModel = RiskModel()) -> Market:
    allocations = read_allocations(persent_to_unit, t0)
    allocations.sort(key = lambda x: x.ticker)
    assets_of_interest = get_assets(allocations, t0, t1, risk)
    assets_of_interest.sort(key = lambda x: x.name)
    assets_of_interest = assets_of_interest[:limit]
    portfolio = get_positions(assets_of_interest, open_positions_ratio)
    portfolio.sort(key = lambda x: x.asset.name)
    return Market(assets_of_interest, portfolio)
