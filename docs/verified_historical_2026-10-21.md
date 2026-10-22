# Historical NYSE Market Research — Verified Snapshot

**Observation period:** 2023-01-03 through 2026-10-21 (inclusive)  
**Generated:** 2026-10-22 04:37 UTC (GitHub Actions)  
**Dataset:** Yahoo Finance adjusted daily closing prices downloaded using `yfinance` 1.7.0  
**Data points:** 954 aligned dates × 12 symbols; 953 daily return observations  
**Audit:** 24 automated tests passed; independent return/volatility reconciliation **PASSED**  
**Provenance:** [Historical Market Research — successful GitHub Actions run](https://github.com/notregularjolpai/NYSE-Market-Pulse-Analysis/actions/runs/39723376151)  
**Download:** Open that run and select artifact `historical-research-verified` for dated charts, the generated report, summary metrics and verification files.

> **Historical, not real-time.** This is a fixed snapshot of selected NYSE-listed equities, **not** a NYSE Composite Index study. SPY is a broad-market S&P 500 ETF listed on NYSE Arca, with constituents from more than one stock exchange. These are *real historical price-based calculations*, not the synthetic preview displayed on the repository homepage.

## Executive findings

- **SPY** returned **112.8% cumulatively** over the observation period (22.1% CAGR), versus **79.8% cumulatively** for the equally weighted 11-stock sample (16.8% CAGR). The spread is a feature of this chosen sample and weighting scheme, not a forecast or investment signal.
- The **daily-rebalanced NYSE sample** showed **13.5% annualized volatility** and a **15.3% maximum drawdown**, compared with **14.9%** and **18.8%** for SPY. Lower realized risk does *not* establish superior risk-adjusted performance.
- SPY's estimated historical **Sharpe ratio was 1.42**, against **1.22** for the equal-weight sample, using the explicit **0% annual risk-free assumption**.
- Within these eleven selections, **Caterpillar (CAT)** had the highest CAGR (**36.9%**) and **NextEra Energy (NEE)** the lowest (**1.1%**). **NEE** had the deepest individual maximum drawdown (**41.3%**). These are single-company results, **not sector-index rankings**.
- At the final data date, **5 of 11 names (45.5%)** were positive over the trailing 63 trading sessions. This is **sample breadth**, not an NYSE-wide advance/decline statistic.

## Historical performance table

| Symbol | Company / basket | CAGR | Annual volatility | Maximum drawdown | Sharpe* |
|:--|:--|--:|--:|--:|--:|
| JPM | JPMorgan Chase | 30.3% | 22.9% | -24.4% | 1.27 |
| XOM | Exxon Mobil | 18.3% | 23.8% | -20.1% | 0.83 |
| KO | Coca-Cola | 14.0% | 15.8% | -17.3% | 0.91 |
| JNJ | Johnson & Johnson | 13.4% | 18.1% | -17.4% | 0.79 |
| CAT | Caterpillar | 36.9% | 31.8% | -34.0% | 1.15 |
| HD | Home Depot | 2.5% | 22.8% | -31.7% | 0.22 |
| NEE | NextEra Energy | 1.1% | 26.0% | -41.3% | 0.17 |
| IBM | IBM | 20.5% | 32.3% | -37.5% | 0.74 |
| PLD | Prologis | 6.6% | 25.4% | -31.4% | 0.38 |
| DIS | Walt Disney | 7.1% | 27.3% | -32.9% | 0.39 |
| SHW | Sherwin-Williams | 10.5% | 24.8% | -25.7% | 0.53 |
| SPY | SPY — S&P 500 ETF | 22.1% | 14.9% | -18.8% | 1.42 |
| EQUAL_WEIGHT | 11-stock equal-weight sample | 16.8% | 13.5% | -15.3% | 1.22 |

*Sharpe calculations annualize arithmetic average daily excess return and use **0%** annual risk-free interest for comparability. The 11-stock sample is rebalanced **every trading session**; transaction costs, spreads, taxes and slippage are ignored.*

## Verification and reliability

1. Fetched the 11 selected NYSE tickers **JPM, XOM, KO, JNJ, CAT, HD, NEE, IBM, PLD, DIS, SHW**, plus **SPY** as a broad US market benchmark.
2. Verified all 12 series had 954 aligned observations, within the requested 2023-01-01 inclusive to 2026-10-23 exclusive date window; no future-dated or stale near-current prices.
3. Rejected incomplete source coverage above the configured 5% tolerance; the accepted series contains **no missing quotes** or nonpositive values after alignment, with **no forward filling**.
4. Independently recalculated stock and portfolio cumulative returns plus annualized volatility, confirmed SPY's self-beta and self-correlation equal 1, and validated the drawdown bounds.
5. Saved provider version, requested and observed periods, collection time, risk assumptions and input-cache SHA-256 in the workflow's metadata. Provider quotes are **not committed** to GitHub.
6. All 24 unit/validation tests and both GitHub Actions workflows passed. This confirms numerical pipeline consistency; it is **not** an independent audit of Yahoo's original quote accuracy or corporate-action methodology.

## Interpretation and limitations

- This is **not** the full NYSE, an NYSE-wide sector breakdown, a point-in-time constituent list, or a benchmark-matched backtest. Only one **selected** company represents each GICS sector.
- SPY is an ETF tracking the **S&P 500**, a broad US market benchmark, not the NYSE Composite or an NYSE-only equity index.
- The daily equal-weight portfolio is theoretical and frictionless. Results depend on dates, dividend adjustments, company selection, and daily rebalancing assumptions.
- Corporate actions and corrections may change historic adjusted prices. Third-party data may have access/licensing restrictions; the full raw-price CSV is deliberately **not** distributed.
- These figures are **backward-looking**, not predicted returns, current quotes, or investment recommendations.

## Reproduce the results

```bash
python -m pip install -r requirements.txt
python scripts/run_analysis.py --start 2023-01-01 --end 2026-10-23
python scripts/verify_historical.py
```

The underlying provider may return revised prices later. Confirm your own `run_metadata.json` date range before comparing any new execution to this fixed snapshot. See [Live Data Validation Protocol](live_data_validation.md) and [Methodology](methodology.md) for more detail.

*Educational project, not investment advice.*
