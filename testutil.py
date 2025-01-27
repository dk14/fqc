from portfolio import Asset, HoldingPosition
from dataclasses import dataclass
from operator import add
from functools import reduce
import csv
import itertools
import yfinance as yf
from datetime import datetime, timedelta
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

def read_allocations(persent_to_unit) -> list[Allocation]:
    with open('example_portfolio.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        allocations = [Allocation(row['ticker'], int(float(row['allocation']) * persent_to_unit), int(float(row['allocation_usd']))) for row in reader]
        return sum_allocations_by_ticker(allocations)

def get_price(date, ticker: str):
    ticker = yf.Ticker(ticker)
    final_time = date + timedelta(days=1)
    return ticker.history(start=date, end=final_time, interval='1m')['Close'].iloc[-1]

# todo: approximate price swings from (get_price(t1) - get_price(t0)) / get_price(t0)
def approximate_price_up(ticker: str, t0, t1, risk: RiskModel) -> int:
    if t0 == 0:
        return 100
    else: 
       diff = (get_price(t1, ticker) - get_price(t0, ticker)) / get_price(t0, ticker)
       if diff > 0:
           return risk.leverage * diff + risk.spread
       else:
           return risk.spread
           

def approximate_price_down(ticker: str, t0, t1, risk: RiskModel) -> int:
    if t0 == 0:
        return 10
    else: 
       diff = (get_price(t1, ticker) - get_price(t0, ticker)) / get_price(t0, ticker)
       if diff < 0:
           return risk.leverage * (- diff) + risk.spread
       else:
           return risk.spread

def get_asset_price(a: Allocation, t0) -> int:
    if t0 == 0:
        return a.allocation_usd / a.allocation
    else:
        return get_price(t0, a.ticker)

def get_assets(allocations: list[Allocation], t0, t1, risk: RiskModel) -> list[Asset]:
    fragmented = map(lambda a: map(lambda i: \
        Asset(a.ticker + "#" + str(i), get_asset_price(a, t0),\
         approximate_price_up(a.ticker, t0, t1, risk),\
         approximate_price_down(a.ticker, t0, t1, risk)), range(0, a.allocation)), allocations)
    return list(itertools.chain.from_iterable(fragmented))

def get_positions(assets: list[Asset], open_positions_ratio) -> list[HoldingPosition]:
    n = len(assets)
    k = int(open_positions_ratio * n)
    return list(map(lambda x: HoldingPosition(x), assets[:k]))

def read_portfolio(limit: Optional[int] = None, persent_to_unit = 10, t0 = 0, t1 = 0, open_positions_ratio = 0.6, risk: RiskModel = RiskModel()) -> Market:
    allocations = read_allocations(persent_to_unit)
    allocations.sort(key = lambda x: x.ticker)
    assets_of_interest = get_assets(allocations, t0, t1, risk)
    assets_of_interest.sort(key = lambda x: x.name)
    assets_of_interest = assets_of_interest[:limit]
    portfolio = get_positions(assets_of_interest, open_positions_ratio)
    portfolio.sort(key = lambda x: x.asset.name)
    return Market(assets_of_interest, portfolio)
