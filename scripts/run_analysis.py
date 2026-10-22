"""NYSE Market Pulse command-line analysis and chart generator.

Run from the repository root:
  python scripts/run_analysis.py --demo
  python scripts/run_analysis.py --start 2023-01-01
"""

from __future__ import annotations

import argparse
import json
import sys
import hashlib
from datetime import datetime, timezone
import importlib.metadata as package_metadata
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from marketpulse.analytics import daily_returns, market_breadth, monthly_returns, performance_table  # noqa: E402
from marketpulse.charts import export_charts  # noqa: E402
from marketpulse.data import download_adjusted_prices, load_prices, make_demo_prices, save_prices  # noqa: E402
from marketpulse.report import write_report  # noqa: E402
from marketpulse.quality import audit_history, reconcile_outputs  # noqa: E402
from marketpulse.universe import BENCHMARK, STOCKS, TICKERS  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reproducible NYSE market risk and sector analytics")
    parser.add_argument("--demo", action="store_true", help="Offline SYNTHETIC demonstration (never real market data)")
    parser.add_argument("--start", default="2023-01-01", help="Start (inclusive), YYYY-MM-DD")
    parser.add_argument("--end", default=(date.today() + timedelta(days=1)).isoformat(), help="End (exclusive), YYYY-MM-DD")
    parser.add_argument("--use-cache", action="store_true", help="Use last locally saved live price dataset, without fetching")
    parser.add_argument("--risk-free-rate", type=float, default=0.0, help="Annual risk-free assumption as decimal, default 0")
    args = parser.parse_args(argv)
    if args.demo and args.use_cache:
        parser.error("--demo and --use-cache cannot be combined")
    if not 0 <= args.risk_free_rate < 1:
        parser.error("--risk-free-rate must be in [0, 1)")
    if not args.demo:
        if date.fromisoformat(args.start) >= date.fromisoformat(args.end):
            parser.error("--end (exclusive) must be later than --start")

    fetched_at_utc = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if args.demo:
        prices = make_demo_prices()
        source = "SYNTHETIC DEMO (seed=2026)"
        folder = ROOT / "outputs" / "demo"
        save_prices(prices, ROOT / "data" / "demo" / "synthetic_adjusted_close.csv")
    else:
        folder = ROOT / "outputs" / "market"
        saved = ROOT / "data" / "processed" / "adjusted_close.csv"
        if args.use_cache:
            prices = load_prices(saved)
            source = "Local historical cache (Yahoo Finance origin; may be stale)"
        else:
            print("Fetching adjusted daily prices from Yahoo Finance. Requires internet access...")
            prices = download_adjusted_prices(args.start, args.end)
            save_prices(prices, saved)
            source = "Yahoo Finance via yfinance (adjusted daily close)"

    if args.demo:
        quality = {"dataset_type": "SYNTHETIC_DEMO", "passed": False, "reason": "Synthetic data cannot establish real market coverage."}
    else:
        quality = audit_history(prices, args.start, args.end)

    folder.mkdir(parents=True, exist_ok=True)
    table = performance_table(prices, risk_free_rate=args.risk_free_rate)
    reconciliation = reconcile_outputs(prices, table)
    table.to_csv(folder / "performance_metrics.csv", float_format="%.8f")
    daily_returns(prices).to_csv(folder / "daily_returns.csv", float_format="%.8f")
    monthly_returns(prices).to_csv(folder / "monthly_returns.csv", float_format="%.8f")
    market_breadth(prices).to_csv(folder / "sample_breadth.csv", float_format="%.8f")
    images = export_charts(prices, folder, demo=args.demo)
    write_report(prices, folder / "research_brief.md", demo=args.demo, risk_free_rate=args.risk_free_rate)
    metadata = {
        "fetched_or_loaded_at_utc": fetched_at_utc,
        "requested_window": {"start_inclusive": args.start, "end_exclusive": args.end},
        "provider_library": {"name": "yfinance", "installed_version": package_metadata.version("yfinance") if not args.demo else "not required for demo"},
        "quality_audit": quality,
        "financial_reconciliation": reconciliation,
        "dataset_type": "SYNTHETIC_DEMO" if args.demo else "HISTORICAL_PRICE_DATA",
        "provider": source,
        "exchange_universe": "11 curated NYSE listed company stocks; not full NYSE",
        "benchmark": "SPY ETF (NYSE Arca, tracks S&P 500; not NYSE Composite)",
        "stock_symbols": list(STOCKS),
        "benchmark_symbol": BENCHMARK,
        "dates": {"first": prices.index[0].date().isoformat(), "last": prices.index[-1].date().isoformat()},
        "price_observations": len(prices),
        "risk_free_assumption": args.risk_free_rate,
        "input_price_basis": "auto-adjusted closing prices" if not args.demo else "invented seeded price paths",
        "missing_data_policy": "intersection of dates with complete positive prices; no forward fill",
        "portfolio_rebalancing": "every trading session, zero modeled transaction costs",
        "chart_files": images,
    }
    (folder / "run_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    if not args.demo:
        # Quote files are local caches only: record SHA-256 but never redistribute quotes.
        saved = ROOT / "data" / "processed" / "adjusted_close.csv"
        metadata["local_price_cache_sha256"] = hashlib.sha256(saved.read_bytes()).hexdigest()
        (folder / "run_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"\n{'SYNTHETIC DEMO' if args.demo else 'HISTORICAL MARKET'} RUN COMPLETED")
    print(f"Observations: {len(prices)}, from {metadata['dates']['first']} to {metadata['dates']['last']}")
    print(table[["Annualized Return (CAGR)", "Annualized Volatility", "Max Drawdown"]].round(3).to_string())
    print(f"\nCharts, metrics, metadata, and research brief: {folder}")
    if args.demo:
        print("IMPORTANT: all values above are synthetic and are NOT actual stock-market prices.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
