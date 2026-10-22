# Live historical-data validation protocol

## Status definitions

- **SYNTHETIC DEMO:** reproducible *fabricated* price paths for testing. No historical investment claim.
- **HISTORICAL PRICE DATA (downloaded and verified):** historical adjusted daily prices attributed to Yahoo Finance via `yfinance`, with technical quality and financial reconciliations completed. This is not an official NYSE feed.
- **FAILED / UNVERIFIED:** incomplete sources, stale near-current dates, nonpositive quotes, missing symbols, anomalous jumps, or inconsistent calculated outputs. No historical findings may be reported.

## Live execution and audit

On an internet-connected Python 3.11 environment (including a GitHub Actions runner):

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python scripts/run_analysis.py --start 2023-01-01
python scripts/verify_historical.py
```

A success creates `outputs/market/research_brief.md`, six research charts, `performance_metrics.csv`, calculated returns and sample breadth, `run_metadata.json`, and `verification.json`.

1. Confirm **all 12 symbols**: `JPM XOM KO JNJ CAT HD NEE IBM PLD DIS SHW SPY`.
2. Confirm the first and last market dates fall within the requested **start-inclusive/end-exclusive** window and prices are never future dated.
3. Confirm **at least 90 aligned daily closing prices** for every symbol. Reject source datasets with more than 5% incomplete dates; do not forward-fill missing quotes.
4. Investigate any daily change exceeding 80% or a stale latest date on a near-current run; a historical split/dividend correction can cause a legitimate revision.
5. Confirm the SHA-256 recorded for the locally cached adjusted-close CSV, the provider, retrieval timestamp (UTC), yfinance version, requested window and observed window in `run_metadata.json`.
6. Confirm `verification.json` reports successful independent reconciliations for both historical cumulative returns and volatility. Check SPY self-beta and self-correlation are 1, and maximum drawdowns are between -100% and 0%.
7. Inspect the report's **generated timestamp and data-as-of date**, market benchmark, risk-free-rate assumptions and all limitations. Compare reported returns with the derived metrics CSV rather than unverified online snippets.

## GitHub Actions

Open **Actions → Historical Market Research** and select a successful run. Its **Summary** shows the observed date range and a short findings preview. The downloadable **historical-research-verified** artifact contains calculated metrics, charts and the data-dated research brief; **raw Yahoo prices are not uploaded**. GitHub may require sign-in for artifact download and artifacts expire. If Yahoo blocks or rate-limits a hosted runner, the job fails; rerun it from a permitted environment rather than using fabricated market results.

## Interpretation constraints

- The study is **11 hand-selected, present-day NYSE stocks**, not an exchange-wide NYSE index; single-company returns are not sector returns.
- SPY is an NYSE Arca ETF that tracks the broader U.S. S&P 500, which also contains Nasdaq stocks.
- The equally weighted 11-stock series **rebalances daily**, assumes frictionless execution, and is exposed to selection/survivorship bias.
- Returns and Sharpe ratios change with the observation window. The default Sharpe assumption is **0% annual risk-free**, not a historical Treasury rate.
- Adjusted prices are determined by third-party provider methodology and may be revised retroactively. Business-day gaps from stock-market holidays are expected; missing quotes *within a common trading session* are not filled.
- Output is retrospective educational analysis, not real-time quotes, an investment product or advice.

See the [verified historical research snapshot dated October 21, 2026](verified_historical_2026-10-21.md), which records an actual passing live GitHub Actions run and summarizes its calculated metrics.

## Source references

- [yfinance downloads and parameter definitions](https://ranaroussi.github.io/yfinance/reference/api/yfinance.download.html)
- [yfinance terms / Yahoo usage disclaimer](https://ranaroussi.github.io/yfinance/)
- [State Street SPY ETF description](https://www.ssga.com/us/en/individual/etfs/state-street-spdr-sp-500-etf-trust-spy)
