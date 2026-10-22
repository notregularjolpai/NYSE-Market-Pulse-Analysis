# Methodology and Research Design

## Primary question
How did a sector-diverse selection of NYSE-listed equities perform compared with a broad US stock-market benchmark, and what do historical return, volatility, drawdown, and correlation reveal about portfolio risk?

## Universe and why it matters

The sample is deliberately **one NYSE company from each of the 11 common GICS sectors**. See `marketpulse/universe.py` for all tickers. This is a *case study of sector representatives*, not an exhaustive or capitalization-weighted NYSE sector index. Sector classifications may change, and selection bias is present.

`SPY` tracks the S&P 500 and is **listed on NYSE Arca**. It is a broad-market comparator, *not* an NYSE Composite Index or a stock on the main NYSE-listed equity sample.

## Data source and reproducibility

`yfinance` downloads daily adjusted OHLCV; the pipeline retains **adjusted Close** only. Adjusted series account for corporate actions as the provider calculates them. Data should be considered third-party estimates/records rather than an official NYSE historical tape. Yahoo usage rights may restrict redistribution, so market data caches are gitignored. Research periods must be read from generated metadata; no hard-coded market returns are claimed.

The downloader validates missing symbols, rejects inputs with more than 5% missing or unaligned sessions, strips remaining dates without forward fill, and requires at least 90 aligned closing-price observations. This excludes suspended/invalid days and may create common-sample selection effects. The provider may rate-limit or change its schema; the documented failure behavior is to stop with an error, not silently fabricate observations.

## Return and risk definitions

Let `P_t` be adjusted Close, `r_t = P_t/P_(t-1) - 1`.

- Total return = `P_last/P_first - 1`.
- CAGR = `(P_last/P_first) ** (252/N) - 1` where N = count of daily returns.
- Realized volatility = `sd(r_t) * sqrt(252)` using sample standard deviation.
- Sharpe = `[mean(r_t)*252 - risk_free_rate] / [sd(r_t)*sqrt(252)]`, with risk-free default `0` (explicit configurable assumption). This is a historical realized estimate, not an expected-return forecast.
- Beta vs SPY = `cov(r_stock, r_SPY) / var(r_SPY)`.
- Max drawdown = `min(W_t / max(W_0, ..., W_t) - 1)`.
- Rolling volatility is 30-session historical standard deviation, annualized.
- Sample breadth = percent of the 11 stocks with positive trailing 63-session adjusted-price return. It is **not** the NYSE advance/decline line.

## The portfolio is a comparison, not a strategy backtest

Each of the 11 sample securities has 1/11 weight **re-established daily**. Portfolio return per session is the simple mean of stock returns. This differs from a buy-and-hold equally funded basket, from a cap-weighted market index, and from a transaction-cost-aware portfolio. It assumes fractional shares, immediate daily rebalancing, zero trading costs, and no execution slippage.

## Important caveats

- **Survivorship/selection bias**: choosing well-known active companies now overstates what an historical ex-ante investor could have known; delisted companies are absent.
- **Benchmark mismatch**: the S&P 500 includes both NYSE- and Nasdaq-listed companies and is cap-weighted; the 11-stock sample has one name per sector and is equal weighted. Relative performance cannot be attributed only to exchange listing.
- **Regime dependence**: historical alpha/beta/correlation/Sharpe change with market conditions; estimates are period-specific.
- **Corporate actions/provider issues**: data adjustments vary by source, dates, and corrections.
- **No trading recommendation**: no forecast, market timing, or causal model is claimed, and all educational analyses omit taxes and transaction costs.

## Source documentation

- https://ranaroussi.github.io/yfinance/reference/api/yfinance.download.html
- https://www.ssga.com/us/en/individual/etfs/state-street-spdr-sp-500-etf-trust-spy
- https://stockanalysis.com/list/nyse-stocks/

## Quality audit, verification, and generated evidence

`marketpulse/quality.py` checks the requested inclusive/exclusive window, future or near-current stale observations, all twelve aligned symbols, and daily adjusted-price changes larger than 80% (flagged for manual investigation, not automatically treated as a market event). Any failure stops the historical run; there is no fallback to synthetic data. Data with more than 5% dates missing any requested symbol is rejected before alignment. These conservative checks can exclude periods with provider gaps.

`reconcile_outputs` recalculates individual cumulative returns, the 11-asset daily-rebalanced portfolio's compounded return, and annualized volatility independently from source prices. It also checks SPY self-beta and self-correlation and the maximum-drawdown range. The verifier rejects mismatches rather than publishing unverified metrics.

The run metadata records the provider, collection timestamp, yfinance version, requested data window, observed window, symbols, numerical validation findings, risk-free-rate assumption and local input-cache SHA-256. The actual Yahoo adjusted-price CSV is omitted from GitHub and Actions artifacts to respect third-party usage restrictions. Artifacts report analysis outputs, **not** live quotes; execution does not prove source data are exchange-certified.

See [live validation protocol](live_data_validation.md) for instructions to inspect successful GitHub Actions historical runs and reproduce the research using a local Python environment.
