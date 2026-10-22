"""Transparent finance analytics, with no forward-looking estimation."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .universe import BENCHMARK, STOCKS, TICKERS, TRADING_DAYS

PORTFOLIO = "EQUAL_WEIGHT"


def daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Simple, close-to-close daily returns on aligned adjusted prices."""
    return prices.pct_change(fill_method=None).iloc[1:].dropna(how="any")


def portfolio_returns(prices: pd.DataFrame) -> pd.Series:
    """Equal-weight sample portfolio REBALANCED DAILY (ignores costs)."""
    return daily_returns(prices)[list(STOCKS)].mean(axis=1).rename(PORTFOLIO)


def wealth_index(prices: pd.DataFrame) -> pd.DataFrame:
    """$100 growth series for securities and daily-rebalanced sample portfolio."""
    normalized = prices / prices.iloc[0] * 100.0
    p_returns = portfolio_returns(prices)
    wealth = (1 + p_returns).cumprod() * 100
    portfolio = pd.Series([100.0, *wealth.tolist()], index=prices.index, name=PORTFOLIO)
    return pd.concat([normalized, portfolio], axis=1)


def drawdowns(wealth: pd.DataFrame) -> pd.DataFrame:
    """Drawdown relative to the preceding running peak; a loss is negative."""
    return wealth.div(wealth.cummax()).sub(1.0)


def performance_table(prices: pd.DataFrame, risk_free_rate: float = 0.0) -> pd.DataFrame:
    """CAGR, annualized realized vol, Sharpe, beta, max drawdown, SPY corr.

    Annualization uses 252 trading days. Sharpe uses arithmetic mean excess
    daily return and sample standard deviation; CAGR uses realized compounded
    growth. Risk-free rate is an explicitly supplied annual assumption.
    """
    if not 0 <= risk_free_rate < 1:
        raise ValueError("Annual risk-free rate must be in [0, 1).")
    series = wealth_index(prices)
    original = daily_returns(prices)
    ret = original.copy()
    ret[PORTFOLIO] = portfolio_returns(prices)
    benchmark = ret[BENCHMARK]
    benchmark_var = benchmark.var(ddof=1)
    wealth_dd = drawdowns(series)

    records = []
    for ticker in [*TICKERS, PORTFOLIO]:
        r = ret[ticker]
        vol = float(r.std(ddof=1) * np.sqrt(TRADING_DAYS))
        cagr = float((series[ticker].iloc[-1] / series[ticker].iloc[0]) ** (TRADING_DAYS / len(r)) - 1)
        sharpe = float((r.mean() * TRADING_DAYS - risk_free_rate) / vol) if vol > 0 else np.nan
        beta = float(r.cov(benchmark) / benchmark_var) if benchmark_var > 0 else np.nan
        records.append(
            {
                "Ticker": ticker,
                "Sector": STOCKS[ticker][1] if ticker in STOCKS else ("Broad market benchmark" if ticker == BENCHMARK else "Daily-rebalanced sample"),
                "Cumulative Return": float(series[ticker].iloc[-1] / 100 - 1),
                "Annualized Return (CAGR)": cagr,
                "Annualized Volatility": vol,
                "Sharpe Ratio": sharpe,
                "Max Drawdown": float(wealth_dd[ticker].min()),
                "Beta vs SPY": beta,
                "Correlation vs SPY": float(r.corr(benchmark)),
                "Observations": int(len(r)),
            }
        )
    return pd.DataFrame.from_records(records).set_index("Ticker")


def rolling_volatility(prices: pd.DataFrame, window: int = 30) -> pd.DataFrame:
    ret = daily_returns(prices)
    ret[PORTFOLIO] = portfolio_returns(prices)
    return ret.rolling(window, min_periods=window).std(ddof=1) * np.sqrt(TRADING_DAYS)


def market_breadth(prices: pd.DataFrame, lookback: int = 63) -> pd.Series:
    """Percentage of the 11 sampled NYSE stocks positive over lookback days.

    This is **sample breadth**, not NYSE market-wide advance/decline breadth.
    """
    trailing = prices[list(STOCKS)].pct_change(periods=lookback, fill_method=None)
    result = (trailing.gt(0).sum(axis=1) / len(STOCKS) * 100.0).rename("Sample Breadth (%)")
    result.iloc[:lookback] = np.nan
    return result


def monthly_returns(prices: pd.DataFrame) -> pd.DataFrame:
    wealth = wealth_index(prices)
    # Month-end performance, using the first available month-end as baseline.
    return wealth.resample("ME").last().pct_change(fill_method=None).iloc[1:]
