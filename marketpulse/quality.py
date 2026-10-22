"""Independent quality and reconciliation checks for historical research runs.

These checks are intentionally separate from the metrics implementation so that
published figures are not accepted solely because their generating code ran.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path
import json

import numpy as np
import pandas as pd

from .data import MarketDataError, load_prices
from .universe import BENCHMARK, STOCKS, TICKERS, TRADING_DAYS


def audit_history(prices: pd.DataFrame, start: str, end: str, max_stale_days: int = 10) -> dict:
    """Audit adjusted quotes against the requested [start, end) window.

    Freshness is checked only when the requested end is near today, not when
    reproducing a historical period. These are provider-data sanity checks,
    not evidence of exchange-certified prices.
    """
    first = pd.Timestamp(prices.index.min()).date()
    last = pd.Timestamp(prices.index.max()).date()
    requested_start, requested_end = date.fromisoformat(start), date.fromisoformat(end)
    today = datetime.now(timezone.utc).date()
    if not requested_start < requested_end:
        raise MarketDataError("Requested end must follow start.")
    if first < requested_start or last >= requested_end:
        raise MarketDataError("Quotes fall outside the requested end-exclusive date window.")
    if last > today:
        raise MarketDataError("Future-dated prices cannot be used for historical analysis.")
    if len(prices) < 90 or list(prices.columns) != TICKERS:
        raise MarketDataError("Historical data must include >=90 aligned rows for all 12 symbols.")
    if (prices.pct_change(fill_method=None).iloc[1:].abs() > 0.80).any().any():
        raise MarketDataError("Daily adjusted-price movement over 80%; investigate provider or corporate actions.")
    if requested_end >= today - pd.Timedelta(days=2) and (today - last).days > max_stale_days:
        raise MarketDataError("Latest data are stale for a near-current research run.")
    return {
        "requested_start_inclusive": requested_start.isoformat(),
        "requested_end_exclusive": requested_end.isoformat(),
        "first_observation": first.isoformat(),
        "last_observation": last.isoformat(),
        "observation_count": int(len(prices)),
        "daily_return_count": int(len(prices) - 1),
        "symbols_expected": TICKERS,
        "symbols_received": list(prices.columns),
        "all_quotes_finite_positive": bool(np.isfinite(prices.to_numpy()).all() and (prices.to_numpy() > 0).all()),
        "aligned_complete_sessions": bool(not prices.isna().any().any()),
        "current_as_of_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "last_session_age_calendar_days": (today - last).days,
    }


def reconcile_outputs(prices: pd.DataFrame, metrics: pd.DataFrame, tolerance: float = 1e-7) -> dict:
    """Recalculate benchmark/individual cumulative returns and volatility.

    Runs an independent vectorized calculation against the published metrics,
    plus common financial invariants, to detect broken exports and bad joins.
    """
    expected = [*TICKERS, "EQUAL_WEIGHT"]
    if list(metrics.index) != expected:
        raise MarketDataError("Results have missing, extra or reordered ticker rows.")
    r = prices.pct_change(fill_method=None).iloc[1:]
    if r.isna().any().any() or not np.isfinite(r.to_numpy()).all():
        raise MarketDataError("Daily returns contain missing or nonfinite values.")
    gross = prices.iloc[-1].div(prices.iloc[0]).sub(1.0)
    vol = r.std(ddof=1).mul(np.sqrt(TRADING_DAYS))
    portfolio_daily = r.loc[:, list(STOCKS)].sum(axis=1) / len(STOCKS)
    portfolio_growth = (1.0 + portfolio_daily).prod() - 1.0
    expected_total = pd.concat([gross, pd.Series({"EQUAL_WEIGHT": portfolio_growth})])
    expected_vol = pd.concat([vol, pd.Series({"EQUAL_WEIGHT": portfolio_daily.std(ddof=1) * np.sqrt(TRADING_DAYS)})])
    for column, independently_calculated in [
        ("Cumulative Return", expected_total),
        ("Annualized Volatility", expected_vol),
    ]:
        actual = pd.to_numeric(metrics[column], errors="raise")
        if not np.allclose(actual.to_numpy(), independently_calculated.to_numpy(), rtol=tolerance, atol=tolerance):
            raise MarketDataError(f"Reconciliation failed for {column}.")
    if not np.all(metrics["Max Drawdown"].between(-1.0, 0.0)):
        raise MarketDataError("Max drawdown outside [-100%, 0%].")
    if not np.isclose(float(metrics.loc[BENCHMARK, "Beta vs SPY"]), 1.0, atol=tolerance):
        raise MarketDataError("SPY beta against itself must be 1.")
    if not np.isclose(float(metrics.loc[BENCHMARK, "Correlation vs SPY"]), 1.0, atol=tolerance):
        raise MarketDataError("SPY self-correlation must be 1.")
    return {
        "passed": True,
        "independent_reconciliations": ["cumulative return", "annualized volatility"],
        "portfolio": "Equal weight of eleven NYSE shares rebalanced daily",
        "benchmark_self_consistency": "SPY correlation and beta verified at 1",
        "drawdown_bounds_checked": True,
    }


def verify_saved_run(price_path: str | Path, metrics_path: str | Path, metadata_path: str | Path) -> dict:
    """Verify saved quote coverage, calculation reconciliations and provenance."""
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    if metadata.get("dataset_type") != "HISTORICAL_PRICE_DATA":
        raise MarketDataError("Refusing to certify synthetic data as a historical run.")
    dates = metadata.get("requested_window", {})
    start, end = dates.get("start_inclusive"), dates.get("end_exclusive")
    if not start or not end:
        raise MarketDataError("Missing requested historical period in run metadata.")
    prices = load_prices(price_path)
    metrics = pd.read_csv(metrics_path, index_col="Ticker")
    audit = audit_history(prices, start, end)
    calculations = reconcile_outputs(prices, metrics, tolerance=3e-7)
    return {"run_quality": audit, "financial_reconciliation": calculations}
