"""Provider-backed market snapshots for the Streamlit dashboard.

Keep network access and quality checks separate from Streamlit rendering so the
critical real-vs-synthetic distinction can be tested without an internet call.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd

from .data import MarketDataError, download_adjusted_prices, load_prices, make_demo_prices
from .quality import audit_history


DEFAULT_START = "2023-01-01"


@dataclass
class MarketSnapshot:
    prices: pd.DataFrame
    source: str
    as_of_utc: str
    is_demo: bool
    audit: dict | None = None


def historical_snapshot(start: str, end: str, downloader=None) -> MarketSnapshot:
    """Fetch all constituents and reject incomplete, stale, or invalid prices.

    `end` is exclusive. `downloader` enables strictly offline unit tests.
    Never replace an unsuccessful historical query with synthetic values.
    """
    try:
        start_day, end_day = date.fromisoformat(start), date.fromisoformat(end)
    except (ValueError, TypeError) as exc:
        raise MarketDataError("Historical dates must be valid YYYY-MM-DD values.") from exc
    if end_day <= start_day or start_day > datetime.now(timezone.utc).date():
        raise MarketDataError("Select a historical date range with start before end.")
    get_prices = downloader if downloader is not None else download_adjusted_prices
    try:
        prices = get_prices(start, end)
    except MarketDataError:
        raise
    except Exception as exc:
        raise MarketDataError("Historical pricing provider is unavailable; retry later.") from exc
    from .data import validate_prices

    prices = validate_prices(prices)
    audit = audit_history(prices, start, end)
    return MarketSnapshot(
        prices=prices,
        source="Yahoo Finance (yfinance); dividend/split-adjusted daily closes",
        as_of_utc=datetime.now(timezone.utc).isoformat(timespec="minutes"),
        is_demo=False,
        audit=audit,
    )


def demo_snapshot(path: str | Path) -> MarketSnapshot:
    """Load an explicit local synthetic demo, with a synthetic generator fallback.

    The fallback is allowed only when the user explicitly selected demo mode.
    """
    file = Path(path)
    prices = load_prices(file) if file.is_file() else make_demo_prices()
    return MarketSnapshot(
        prices=prices,
        source="SYNTHETIC DEMO (seeded simulated price paths; NOT NYSE quotes)",
        as_of_utc=datetime.now(timezone.utc).isoformat(timespec="minutes"),
        is_demo=True,
        audit=None,
    )
