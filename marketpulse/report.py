"""A concise automatically generated, data-dated equity risk report."""

from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd

from .analytics import PORTFOLIO, market_breadth, performance_table
from .universe import BENCHMARK, STOCKS


def write_report(prices: pd.DataFrame, destination: str | Path, demo: bool, risk_free_rate: float) -> str:
    p = performance_table(prices, risk_free_rate=risk_free_rate)
    sample = p.loc[list(STOCKS)]
    leader = sample["Annualized Return (CAGR)"].idxmax()
    laggard = sample["Annualized Return (CAGR)"].idxmin()
    market = p.loc[BENCHMARK]
    portfolio = p.loc[PORTFOLIO]
    latest_breadth = market_breadth(prices).dropna().iloc[-1]
    last_date = prices.index[-1].date().isoformat()
    first_date = prices.index[0].date().isoformat()
    heading = "# SYNTHETIC DEMO — NOT REAL MARKET DATA\n\n" if demo else ""
    generated_utc = datetime.now(timezone.utc).isoformat(timespec="seconds")
    headline_table = p.loc[[BENCHMARK, PORTFOLIO], ["Cumulative Return", "Annualized Return (CAGR)", "Annualized Volatility", "Max Drawdown", "Sharpe Ratio", "Beta vs SPY"]]
    table_md = "| Symbol | Cum. return | CAGR | Annual vol. | Max drawdown | Sharpe | Beta |\n|:--|--:|--:|--:|--:|--:|--:|\n"
    for symbol, row in headline_table.iterrows():
        table_md += f"| {symbol} | {row['Cumulative Return']:.1%} | {row['Annualized Return (CAGR)']:.1%} | {row['Annualized Volatility']:.1%} | {row['Max Drawdown']:.1%} | {row['Sharpe Ratio']:.2f} | {row['Beta vs SPY']:.2f} |\n"

    fmt = lambda x: f"{x:.1%}"
    report = f"""{heading}# NYSE Market Pulse — Performance & Risk Research Brief

**Data dates:** {first_date} to {last_date}  \n**Generated (UTC):** {generated_utc}  \n**Aligned price observations:** {len(prices):,} across all 12 symbols  
**Source:** {'Seeded synthetic series (educational demo)' if demo else 'Yahoo Finance via yfinance, adjusted closing prices'}  
**Universe:** 11 selected NYSE-listed equities (one per GICS sector) + SPY on NYSE Arca  
**Risk-free rate assumption:** {risk_free_rate:.1%} annually  
**Portfolio methodology:** Equal weighting, rebalanced *every trading day*, no transaction costs.

## Executive summary

- **Broad U.S. market benchmark (SPY):** {fmt(market['Cumulative Return'])} cumulative return; {fmt(market['Annualized Volatility'])} annualized historical volatility; {fmt(market['Max Drawdown'])} maximum drawdown.
- **Equal-weighted NYSE sample:** {fmt(portfolio['Cumulative Return'])} cumulative return; {fmt(portfolio['Annualized Volatility'])} annualized historical volatility; {fmt(portfolio['Max Drawdown'])} maximum drawdown.
- **Highest sample CAGR:** {leader} ({STOCKS[leader][1]}) at {fmt(sample.loc[leader, 'Annualized Return (CAGR)'])}.
- **Lowest sample CAGR:** {laggard} ({STOCKS[laggard][1]}) at {fmt(sample.loc[laggard, 'Annualized Return (CAGR)'])}.
- **Sample breadth (63-session):** {latest_breadth:.1f}% of the 11 selected stocks had a positive trailing 63-trading-day return at the latest available date.

## Performance summary (historical, not a forecast)

{table_md}

## Interpretation

This project compares individual NYSE-listed stocks with a diversified U.S. market ETF proxy. The difference between the sample portfolio and SPY reflects ticker selection, equal-weighting and rebalancing choices; it **does not** establish a reliable investing strategy or predict future performance. A sector represented by only one company is a **case study**, not a sector-index estimate.

## Metrics definitions

- **Cumulative return:** ending wealth / starting wealth minus 1, using adjusted prices.
- **CAGR:** compounded return annualized using 252 trading sessions.
- **Volatility:** standard deviation of daily simple returns × sqrt(252).
- **Sharpe:** (annualized arithmetic mean daily return − assumed annual risk-free rate) / annualized daily-return volatility.
- **Max drawdown:** minimum percentage difference between running cumulative wealth and preceding peak.
- **Beta:** covariance of daily returns with SPY divided by SPY return variance.
- **Breadth:** count of sampled stocks with positive 63-session return divided by 11.

## Figures

1. `01_growth_of_100.png` — cumulative, adjusted-price performance.
2. `02_risk_return.png` — realized risk and compounded return.
3. `03_drawdowns.png` — path-dependent losses from peaks.
4. `04_correlation_matrix.png` — co-movement of daily returns.
5. `05_sample_breadth.png` — 63-session sample breadth (not exchange-wide breadth).
6. `06_sector_representatives.png` — company-specific returns grouped by sector classification.

## Critical limitations

- **{'Synthetic demonstration only: all input prices and results are fabricated for testing, not historical market observations.' if demo else 'Historical, adjusted Yahoo Finance price data; not an exchange-certified market feed and may be revised or unavailable.'}**
- This is a curated **current-stock sample**, not all NYSE constituents, not sector-index performance, and not a survivorship-bias-free backtest.
- SPY is a **NYSE Arca-listed S&P 500 tracking ETF**, not an NYSE Composite Index or NYSE-only benchmark.
- SPY is subject to ETF fees and tracking variation relative to its reference index.
- Data are aligned to shared trading sessions with missing observations dropped, not forward-filled.
- Prices adjusted for splits/dividends are used; results are retrospective and cannot guarantee returns.
- Returns ignore tax, commissions, slippage, bid/ask spread, shorting constraints, funding costs, and investor-specific risk capacity.
- This educational report is **not investment advice**.

## Reproduction

```bash
python scripts/run_analysis.py {'--demo' if demo else '--start ' + first_date + ' --end ' + (prices.index[-1] + pd.Timedelta(days=1)).date().isoformat()}
```
"""
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")
    return report
