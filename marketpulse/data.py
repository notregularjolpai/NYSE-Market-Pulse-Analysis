"""Download, validate, and store daily adjusted closing prices."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .universe import BENCHMARK, STOCKS, TICKERS


class MarketDataError(ValueError):
    """Raised when downloaded market data cannot support a reliable analysis."""


def validate_prices(prices: pd.DataFrame, min_rows: int = 90) -> pd.DataFrame:
    """Ensure every ticker has enough complete, positive, aligned trading observations.

    The analysis deliberately does not forward-fill missing stock prices.
    Missing sessions are removed uniformly from all tickers to avoid
    spurious zero returns and asynchronous-market comparisons.
    """
    if not isinstance(prices, pd.DataFrame) or prices.empty:
        raise MarketDataError("No price records were found.")
    missing = sorted(set(TICKERS) - set(prices.columns))
    if missing:
        raise MarketDataError(f"Ticker(s) not returned by the provider: {missing}")

    clean = prices.loc[:, TICKERS].copy()
    clean.index = pd.to_datetime(clean.index, errors="coerce")
    if clean.index.isna().any() or clean.index.has_duplicates:
        raise MarketDataError("Invalid or duplicate trading dates.")
    for ticker in TICKERS:
        clean[ticker] = pd.to_numeric(clean[ticker], errors="coerce")
    clean = clean.replace([np.inf, -np.inf], np.nan).sort_index()
    clean = clean.dropna(how="any")
    if len(clean) < min_rows:
        raise MarketDataError(
            f"Only {len(clean)} complete trading dates; at least {min_rows} are required. "
            "Check the time range and source availability."
        )
    if (clean <= 0).any().any():
        raise MarketDataError("All adjusted closing prices must be positive.")
    return clean


def download_adjusted_prices(start: str, end: str) -> pd.DataFrame:
    """Get Yahoo Finance adjusted daily close; end date is exclusive."""
    try:
        import yfinance as yf
    except ImportError as exc:
        raise MarketDataError("Install requirements.txt to enable market downloads.") from exc

    raw = yf.download(
        tickers=TICKERS,
        start=start,
        end=end,
        interval="1d",
        auto_adjust=True,
        progress=False,
        threads=True,
        group_by="column",
        multi_level_index=True,
    )
    if raw is None or raw.empty:
        raise MarketDataError("The provider returned no data. Check your internet connection.")
    if isinstance(raw.columns, pd.MultiIndex):
        if "Close" in raw.columns.get_level_values(0):
            prices = raw.xs("Close", axis=1, level=0)
        elif "Close" in raw.columns.get_level_values(1):
            prices = raw.xs("Close", axis=1, level=1)
        else:
            raise MarketDataError("Expected a Close field from yfinance.")
    elif "Close" in raw and len(TICKERS) == 1:
        prices = raw[["Close"]].rename(columns={"Close": TICKERS[0]})
    else:
        raise MarketDataError("Unexpected yfinance column layout.")
    return validate_prices(prices)


def make_demo_prices(periods: int = 756, seed: int = 2026) -> pd.DataFrame:
    """Create reproducible SYNTHETIC prices solely for offline testing/previews.

    These values are fabricated and should never be labeled NYSE prices.
    """
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(end="2025-12-31", periods=periods)
    market_component = rng.normal(0.0003, 0.009, periods)
    results = {}
    for i, ticker in enumerate(STOCKS):
        daily = 0.0001 + (0.75 + i / 20) * market_component + rng.normal(
            0, 0.006 + (i % 3) * 0.0015, periods
        )
        results[ticker] = 100 * np.cumprod(1 + np.clip(daily, -0.90, None))
    results[BENCHMARK] = 100 * np.cumprod(1 + market_component)
    return validate_prices(pd.DataFrame(results, index=dates))


def save_prices(prices: pd.DataFrame, location: str | Path) -> None:
    destination = Path(location)
    destination.parent.mkdir(parents=True, exist_ok=True)
    prices.to_csv(destination, index_label="Date", float_format="%.8f")


def load_prices(location: str | Path) -> pd.DataFrame:
    file = Path(location)
    if not file.is_file():
        raise MarketDataError(f"No cached prices at {file}. Run the analysis first.")
    prices = pd.read_csv(file, index_col="Date", parse_dates=["Date"])
    return validate_prices(prices)
