"""Deployment-facing regressions; mocked Yahoo data never requires internet."""

from datetime import date, timedelta
import sys
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from marketpulse.dashboard_data import DEFAULT_START, demo_snapshot, historical_snapshot
from marketpulse.data import MarketDataError, download_adjusted_prices, make_demo_prices
from marketpulse.universe import STOCKS, TICKERS


def test_historical_snapshot_validated_without_network():
    sample = make_demo_prices(periods=252, seed=42)
    calls = []

    def fake_download(start, end):
        calls.append((start, end))
        return sample

    result = historical_snapshot("2024-01-01", "2026-01-01", downloader=fake_download)
    assert calls == [("2024-01-01", "2026-01-01")]
    assert not result.is_demo
    assert list(result.prices.columns) == TICKERS
    assert result.audit["observation_count"] == len(sample)
    assert "Yahoo Finance" in result.source


def test_failed_live_fetch_never_falls_back_to_synthetic():
    def unavailable(start, end):
        raise ConnectionError("host unavailable")

    with pytest.raises(MarketDataError, match="unavailable"):
        historical_snapshot("2023-01-01", "2026-01-01", downloader=unavailable)


def test_bad_date_windows_do_not_call_download():
    def forbid_calls(start, end):
        raise AssertionError("should not fetch")

    for start, end in [("not-a-date", "2024-01-01"), ("2024-01-01", "2024-01-01"),
                       ("2024-02-01", "2024-01-01"),
                       ((date.today() + timedelta(days=1)).isoformat(), "2035-01-01")]:
        with pytest.raises(MarketDataError):
            historical_snapshot(start, end, downloader=forbid_calls)


def test_historical_rejects_invalid_provider_data():
    invalid = make_demo_prices(periods=252, seed=42).drop(columns=["JPM"])
    with pytest.raises(MarketDataError, match="Ticker"):
        historical_snapshot("2024-01-01", "2026-01-01", downloader=lambda a, b: invalid)


def test_demo_is_visibly_labeled_and_reproducible(tmp_path):
    first = demo_snapshot(tmp_path / "not-present.csv")
    second = demo_snapshot(tmp_path / "not-present.csv")
    assert first.is_demo and second.is_demo
    assert "SYNTHETIC" in first.source and "NOT NYSE quotes" in first.source
    pd.testing.assert_frame_equal(first.prices, second.prices)
    assert not first.audit


def test_download_yfinance_schema_and_adjusted_prices(monkeypatch):
    days = pd.bdate_range("2025-02-03", periods=105)
    columns = pd.MultiIndex.from_product([["Close", "Open"], TICKERS])
    arr = np.tile(np.arange(105, dtype=float).reshape(-1, 1), (1, len(columns))) + 100
    data = pd.DataFrame(arr, index=days, columns=columns)
    kw = {}
    def download(**kwargs):
        kw.update(kwargs)
        return data
    monkeypatch.setitem(sys.modules, "yfinance", SimpleNamespace(download=download))
    result = download_adjusted_prices("2025-02-01", "2025-08-01")
    assert list(result.columns) == TICKERS
    assert len(result) == 105
    assert kw["auto_adjust"] is True and kw["interval"] == "1d"
    assert list(kw["tickers"]) == TICKERS


def test_provider_exception_becomes_data_error(monkeypatch):
    def throw(**kwargs):
        raise RuntimeError("Provider outage")
    monkeypatch.setitem(sys.modules, "yfinance", SimpleNamespace(download=throw))
    with pytest.raises(MarketDataError, match="provider may be unavailable"):
        download_adjusted_prices("2024-01-01", "2025-01-01")


def test_default_start_is_historical():
    assert DEFAULT_START == "2023-01-01"
