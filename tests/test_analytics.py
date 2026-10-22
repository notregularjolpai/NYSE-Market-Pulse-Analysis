import numpy as np
import pandas as pd
import pytest

from marketpulse.analytics import (
    PORTFOLIO,
    daily_returns,
    drawdowns,
    market_breadth,
    monthly_returns,
    performance_table,
    portfolio_returns,
    wealth_index,
)
from marketpulse.data import MarketDataError, load_prices, make_demo_prices, save_prices, validate_prices
from marketpulse.universe import BENCHMARK, STOCKS, TICKERS


@pytest.fixture(scope="module")
def prices():
    return make_demo_prices(periods=252, seed=123)


def test_synthetic_reproducible():
    pd.testing.assert_frame_equal(make_demo_prices(seed=111), make_demo_prices(seed=111))
    assert not make_demo_prices(seed=111).equals(make_demo_prices(seed=112))


def test_universe_has_all_major_sectors():
    assert len(STOCKS) == 11
    assert len(set(sector for _, sector in STOCKS.values())) == 11
    assert len(TICKERS) == 12
    assert BENCHMARK not in STOCKS


def test_daily_return_formula(prices):
    r = daily_returns(prices)
    assert len(r) == len(prices) - 1
    assert np.isclose(r.loc[prices.index[1], "JPM"], prices["JPM"].iloc[1] / prices["JPM"].iloc[0] - 1)


def test_equal_weight_portfolio_is_daily_rebalanced(prices):
    r = daily_returns(prices)
    ew = portfolio_returns(prices)
    expected = r[list(STOCKS)].mean(axis=1)
    np.testing.assert_allclose(ew.to_numpy(), expected.to_numpy())
    assert ew.name == PORTFOLIO


def test_wealth_starts_at_100_and_compounds(prices):
    w = wealth_index(prices)
    assert np.allclose(w.iloc[0].to_numpy(), 100)
    final_wealth = 100 * np.prod(1 + portfolio_returns(prices).values)
    assert np.isclose(w[PORTFOLIO].iloc[-1], final_wealth)


def test_max_drawdown_never_positive(prices):
    d = drawdowns(wealth_index(prices))
    assert (d <= 1e-12).all().all()
    assert np.allclose(d.iloc[0].to_numpy(), 0)


def test_finance_metrics(prices):
    p = performance_table(prices)
    assert len(p) == 13
    assert np.isclose(p.loc[BENCHMARK, "Beta vs SPY"], 1.0)
    assert np.isclose(p.loc[BENCHMARK, "Correlation vs SPY"], 1.0)
    assert (p["Annualized Volatility"] > 0).all()
    assert (p["Max Drawdown"] <= 0).all()
    assert (p["Observations"] == len(prices) - 1).all()


def test_risk_free_rate_changes_sharpe_only(prices):
    a, b = performance_table(prices, 0), performance_table(prices, 0.05)
    assert (a["Sharpe Ratio"] > b["Sharpe Ratio"]).all()
    pd.testing.assert_series_equal(a["Annualized Return (CAGR)"], b["Annualized Return (CAGR)"])
    with pytest.raises(ValueError):
        performance_table(prices, 1.1)


def test_missing_prices_not_silently_forward_filled(prices):
    broken = prices.copy()
    broken.loc[broken.index[4], "JPM"] = np.nan
    cleaned = validate_prices(broken)
    assert len(cleaned) == len(prices) - 1
    assert broken.index[4] not in cleaned.index


def test_missing_ticker_raises(prices):
    with pytest.raises(MarketDataError, match="Ticker"):
        validate_prices(prices.drop(columns=["JPM"]))


def test_too_few_rows_raises(prices):
    with pytest.raises(MarketDataError, match="at least"):
        validate_prices(prices.iloc[:9])


def test_breadth_warmup_is_missing(prices):
    b = market_breadth(prices, lookback=63)
    assert b.iloc[:63].isna().all()
    assert b.iloc[63:].between(0, 100).all()


def test_monthly_returns_month_end(prices):
    monthly = monthly_returns(prices)
    assert not monthly.empty
    assert set(TICKERS).issubset(monthly.columns)
    assert PORTFOLIO in monthly.columns


def test_price_cache_roundtrip(prices, tmp_path):
    location = tmp_path / "adjusted_close.csv"
    save_prices(prices, location)
    loaded = load_prices(location)
    assert loaded.shape == prices.shape
    np.testing.assert_allclose(loaded.to_numpy(), prices.to_numpy(), atol=1e-7)
