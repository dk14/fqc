# fqc

## Linear Quantum Portfolio Optimizer

- [test.py](test.py) contains unit tests and backtracking (against [example](example_portfolio.csv) and yfinance prices). 

    ``python3 test.py``

    Suggested actions to take are dumped to [acions_backtracking.json](actions_backtracking.json). 

*Semantics: Action closes existing position in portfolio if there is one or opens new one if position did not exist.*

- [portfolio.py](portfolio.py) contains portfolio optimizer. `optimize` runs maximization for small portfolios, `optimize_agg` runs it for arbitrarily large ones. *Note: aggregation is trivial for non-correlated assets*. We split every asset into tradable units (e.g. AMZN#0, AMZN#1) in order to optimize allocations as well.

- [comp.py](comp.py) contains abstract `Computer` and DSL for linear unconstrained optimization (max weighted sum). It can run on any quantum/classic engine (e.g. qiskit)

$$\max_q \sum_i profitForecast_i * qubit(q, i)$$

*Note: Constrained Hamiltonian problems, akin to Lagrangians, are convertable to constrained ones by introducing penalizing terms*

- [clacomp.py](clacomp.py) contains regular computer solving problem through permutation.

- [hamicomp.py](hamicomp.py) contains Hamiltonian solver (classic Eigensolver and simulated quantum SamplingVQE), running in qiskit simulator.

- [testutil.py](testutil.py) contains portfolio reader and yfinance.

----
### Assumptions:
- prices are not correlated, problem is linear. 

*Note: Introducing covariance matricies would make problem quadratic and would require divide and conquer segmentation of matrix for large portfolios. This implies that covarience matrix should be as sparse as possible with "islands" of relations corresponding to segments, e.g. industry sectors.*

- no budget/liquidity constraints so far
- zero-risk rate is 0%. FV comes purely from selling asset at $t_1$. USD's value doesn't change over time (fixed-rate asset).

