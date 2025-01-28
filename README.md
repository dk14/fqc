# fqc

## Linear Quantum Portfolio Optimizer

- [test.py](test.py) contains unit tests and backtesting (against [example](example_portfolio.csv) and yfinance prices). 

    ``python3 test.py``

    Full backtesting report is in [report.csv](report.csv). Configuration is in [backtest_config.json](backtest_config.json).

*Semantics: Action closes existing position in portfolio if there is one or opens a new one if position did not exist. Suggested actions to take are dumped into [actions_backtesting.json](actions_backtesting.json)*

- [portfolio.py](portfolio.py) contains portfolio optimizer. `optimize` runs maximization for small portfolios, `optimize_agg` runs it for arbitrarily large ones (given that portfolio fits classic RAM). 
We split every asset into tradable units (e.g. AMZN#0, AMZN#1) in order to potentially optimize allocations as well.

*Note: aggregation (divide and conquer) is trivial for non-correlated assets*

- [comp.py](comp.py) contains abstract `Computer` and DSL for linear **unconstrained** optimization (max weighted sum). It can run on any quantum/classic engine (e.g. qiskit)

$$\max_q \sum_i profitLossForecast_i * qubit(q, i)$$

*Note: Constrained Hamiltonian problems, akin to Lagrangians, are convertable to unconstrained ones by introducing penalizing terms*

- [clacomp.py](clacomp.py) contains `Computer` implementation for regular computer, capable of solving through permutation.

- [hamicomp.py](hamicomp.py) contains `Computer` implementation for Hamiltonian solvers (classic `Eigensolver` and simulated quantum `SamplingVQE`), running in qiskit simulator.

- [testutil.py](testutil.py) contains portfolio reader and `yfinance`.

----
### Assumptions:
- quantum permutation is faster than selecting maximums (or in simple case just positive weights) on CPU/RAM.
- prices are not correlated, thus problem is linear. 

*Note: Introducing covariance matricies would make problem quadratic and would require divide and conquer segmentation of matrix for large portfolios. This implies that covarience matrix should be as sparse as possible with "islands" (around diagonal) of relations corresponding to segments, e.g. industry sectors.
Introducing realistic up/down price variations (asset going up, asset going down are anticorrelated) would make problem quadratic as well
*

- no budget/liquidity constraints so far
- zero-risk rate is 0%. FV comes purely from selling asset at $t_1$. <del>BTC</del>USD's purchase value doesn't depreciate/fluctuate over time and location (USD assumed to be a fixed-rate asset, no inflation, no such thing much).
- concious action is assumed to be possible between $t_0$ and $t_1$. Food/Oxygen/Energy (finite resources for human) is assumed be available to a trader within that period. Population growth is okay, farming lands are fine, wars and pandemics are tolerable, under assumtions of this model.

