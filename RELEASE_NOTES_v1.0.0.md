# NYSE Market Pulse v1.0.0 — Release Notes

**Release title:** NYSE Market Pulse v1.0.0 — Live Market Analytics Dashboard

## Overview

The first stable milestone of **NYSE Market Pulse**, a Python and Streamlit research application for comparing historical performance and investment risk across **11 selected NYSE-listed companies** (one company from each major GICS sector) against **SPY**, the NYSE Arca-listed S&P 500 ETF benchmark.

**Live dashboard:** https://nyse-market-pulse-analysis-me.streamlit.app/

## Features

- Public **Streamlit dashboard** with interactive company and date filters, financial KPI cards, growth-of-$100 comparisons, drawdowns, rolling volatility, correlations, risk–return charts, and 63-session **sample** breadth.
- **Historical Yahoo Finance adjusted-price** retrieval through `yfinance`, with one-hour Streamlit caching, user-requested refresh, and explicit download-failure handling.
- A transparent **daily-rebalanced, 11-stock equal-weight sample** compared with SPY. Exports include CAGR, volatility, drawdown, beta, correlations, and configurable-risk-free-rate Sharpe ratios.
- Six generated research charts, a Jupyter notebook, a dated historical research brief, a data dictionary, methodological notes, and reproducible scripts.
- Separately labeled **synthetic demonstration** data for offline education and automated tests. The application never silently substitutes demo prices for failed live downloads.

## Verified research snapshot

The October 22, 2026 GitHub Actions research run analyzed **954 aligned trading sessions** from **January 3, 2023 through October 21, 2026**, using adjusted closing prices for 11 equities and SPY.

| Metric | SPY | 11-stock equal-weight sample |
|:--|--:|--:|
| Cumulative historical return | 112.8% | 79.8% |
| Annualized return (CAGR) | 22.1% | 16.8% |
| Annualized realized volatility | 14.9% | 13.5% |
| Maximum drawdown | −18.8% | −15.3% |

These are **retrospective results**, not live quotes, predictions, or investable strategy results. Daily rebalancing assumes zero transaction costs and the sample is subject to selection and survivorship biases.

**Research report:** [Verified historical findings](docs/verified_historical_2026-10-21.md)

## Validation and engineering

- **33 automated tests passed**, including a headless Streamlit rendering smoke test, numerical finance tests, provider-failure tests, and synthetic-versus-historical data separation.
- Independent historical financial reconciliation and data-quality checks passed in GitHub Actions.
- GitHub Actions includes separate offline CI and historical-data verification workflows.
- The public repository excludes raw Yahoo Finance price-history exports.

**Evidence:**
- [Passing dashboard and offline test run](https://github.com/notregularjolpai/NYSE-Market-Pulse-Analysis/actions/runs/39725893331)
- [Passing historical research workflow](https://github.com/notregularjolpai/NYSE-Market-Pulse-Analysis/actions/runs/39725893382)

## Run locally

```bash
git clone https://github.com/notregularjolpai/NYSE-Market-Pulse-Analysis.git
cd NYSE-Market-Pulse-Analysis
python -m pip install -r requirements.txt
streamlit run app.py
```

The dashboard uses the historical market-data source by default; its separate synthetic demonstration is selectable in the sidebar.

## Scope and limitations

This is **not** the entire NYSE, the NYSE Composite Index, a GICS sector-index analysis, or a real-time trading system. SPY represents the broader U.S. S&P 500 market rather than NYSE-only securities. Historical prices and provider availability may change, and third-party data use remains subject to provider terms. **Educational and portfolio research only; not investment advice.**

**Author:** Ashraful Enam · Finance & Data Analytics
