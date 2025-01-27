from portfolio import Asset, HoldingPosition
from dataclasses import dataclass
from operator import add
from functools import reduce
import csv
import itertools
import yfinance as yf

@dataclass
class Allocation:
    ticker: str
    allocation: int # assume a unit = (1/persent_to_unit)%
    allocation_usd: int

@dataclass
class Market:
    assets_of_interest: list[Asset]
    positions: list[HoldingPosition]

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
    return ticker.history(start=datetime_object, end=final_time, interval='1m')['Close'].iloc[-1]

# todo: approximate price swings from (get_price(t1) - get_price(t0)) / get_price(t0)
def approximate_price_up(ticker: str, t0, t1) -> int:
    return 100

def approximate_price_down(ticker: str, t0, t1) -> int:
    return 10

def get_assets(allocations: list[Allocation], t0, t1) -> list[Asset]:
    fragmented = map(lambda a: map(lambda i: \
        Asset(a.ticker + "#" + str(i), a.allocation_usd / a.allocation,\
         approximate_price_up(a.ticker, t0, t1),\
         approximate_price_down(a.ticker, t0, t1)), range(0, a.allocation)), allocations)
    return list(itertools.chain.from_iterable(fragmented))

def get_positions(assets: list[Asset], open_positions_ratio) -> list[HoldingPosition]:
    n = len(assets)
    k = int(open_positions_ratio * n)
    return list(map(lambda x: HoldingPosition(x), assets[:k]))

def read_portfolio(persent_to_unit = 10, t0 = 0, t1 = 0, open_positions_ratio = 0.6) -> Market:
    allocations = read_allocations(persent_to_unit)
    assets_of_interest = get_assets(allocations, t0, t1)
    portfolio = get_positions(assets_of_interest, open_positions_ratio)
    return Market(assets_of_interest, portfolio)
