"""Public NYSE Market Pulse dashboard; real data is downloaded and cached.

Run: streamlit run app.py
Historical prices are held in Streamlit's ephemeral cache and are not committed,
exported, or redistributed as raw provider quotes.
"""

from __future__ import annotations

from datetime import date, timedelta
import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from marketpulse.analytics import (
    PORTFOLIO, daily_returns, drawdowns, market_breadth,
    performance_table, rolling_volatility, wealth_index,
)
from marketpulse.dashboard_data import DEFAULT_START, demo_snapshot, historical_snapshot
from marketpulse.data import MarketDataError
from marketpulse.universe import BENCHMARK, STOCKS, TICKERS

ROOT = Path(__file__).resolve().parent
DEMO_FILE = ROOT / "data" / "demo" / "synthetic_adjusted_close.csv"
NAVY = "#1a3153"
TEAL = "#087f8c"
LIGHT = "#f6f8fb"

st.set_page_config(page_title="NYSE Market Pulse | Market Analytics", page_icon="📈", layout="wide")
st.markdown("""<style>
.block-container {padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1450px;}
[data-testid="stMetric"] {border:1px solid #e0e8f0; border-radius:12px; padding:16px;
 background:linear-gradient(145deg,#fff,#f7fafc);}
[data-testid="stMetricValue"] {color:#087f8c;}
h1,h2,h3 {letter-spacing:-.015em;}
</style>""", unsafe_allow_html=True)

@st.cache_data(ttl=3600, max_entries=3, show_spinner=False)
def cached_history(start: str, end: str):
    """Hourly TTL limits provider calls across reruns and dashboard visitors."""
    return historical_snapshot(start, end)

@st.cache_data(show_spinner=False)
def cached_demo(path: str):
    return demo_snapshot(path)

st.title("NYSE Market Pulse")
st.caption("Cross-sector equity performance • historical risk analytics • finance & data science portfolio")
st.markdown("**Research question:** How have eleven NYSE-listed stocks from distinct sectors performed against the broader U.S. market, and what are the diversification trade-offs?")

st.sidebar.header("Research controls")
source_options = ["Historical market prices", "Synthetic demonstration"]
default_source = 1 if os.getenv("NYSE_DASHBOARD_TEST_MODE") == "1" else 0
source = st.sidebar.radio("Data source", source_options, index=default_source)
is_demo = source == source_options[1]

if st.sidebar.button("↻ Refresh historical data", disabled=is_demo, help="Clear the historical cache and request updated closing prices."):
    cached_history.clear()
    st.rerun()

with st.spinner("Loading and validating price history…"):
    try:
        if is_demo:
            snapshot = cached_demo(str(DEMO_FILE))
        else:
            # End is exclusive, so tomorrow includes the latest available trading date.
            snapshot = cached_history(DEFAULT_START, (date.today() + timedelta(days=1)).isoformat())
    except (MarketDataError, ValueError) as exc:
        st.error("Historical prices could not be verified. No simulated data was substituted.")
        st.warning(str(exc))
        st.info("You can retry using **Refresh historical data**, or explicitly select **Synthetic demonstration** in the sidebar to explore a labeled offline example.")
        st.stop()
    except Exception:
        st.error("Historical data could not be loaded. Please retry later or select the separate synthetic demonstration.")
        st.stop()

prices_all = snapshot.prices
if snapshot.is_demo:
    st.error("**SYNTHETIC DEMONSTRATION — NOT REAL NYSE MARKET DATA.** All prices and results below are fabricated for visualization and software testing.")
else:
    st.success(f"**Validated historical data** · Yahoo Finance adjusted daily closes · Last trading session: **{prices_all.index[-1]:%B %d, %Y}**")

st.caption(f"Data source: {snapshot.source}  ·  Loaded at {snapshot.as_of_utc} UTC  ·  {len(prices_all):,} aligned trading sessions")
if not is_demo:
    st.caption("Data refreshes at most once per hour unless manually refreshed. **Not real-time quotes.** Provider availability, adjustments, and data rights apply.")

min_date, max_date = prices_all.index[0].date(), prices_all.index[-1].date()
window = st.sidebar.date_input(
    "Analysis period", value=(min_date, max_date), min_value=min_date, max_value=max_date,
    help="CAGR, drawdowns and Sharpe ratios are recalculated for the selected period.",
)
if not isinstance(window, (list, tuple)) or len(window) != 2:
    st.info("Select both the start and end date to analyze the historical period.")
    st.stop()
start_date, end_date = window
if start_date >= end_date:
    st.warning("The end date must be later than the start date.")
    st.stop()
prices = prices_all.loc[str(start_date):str(end_date)]
if len(prices) < 90:
    st.warning("Select at least 90 aligned trading sessions for meaningful comparisons.")
    st.stop()

chosen = st.sidebar.multiselect(
    "Companies to highlight", options=list(STOCKS),
    default=["JPM", "XOM", "KO", "CAT"], format_func=lambda t: f"{t} · {STOCKS[t][0]}",
)
assumed_rf = st.sidebar.slider("Assumed annual risk-free rate (%)", 0.0, 10.0, 0.0, step=0.5) / 100
st.sidebar.caption("One selected company per sector; **not** the full NYSE or sector indexes. SPY is the NYSE Arca-listed S&P 500 ETF benchmark.")

metrics = performance_table(prices, risk_free_rate=assumed_rf)
spy = metrics.loc[BENCHMARK]
portfolio = metrics.loc[PORTFOLIO]
wealth = wealth_index(prices)
returns = daily_returns(prices)

st.markdown("### Market overview")
a, b, c, d = st.columns(4)
a.metric("SPY annualized return", f"{spy['Annualized Return (CAGR)']:.1%}")
b.metric("11-stock portfolio CAGR", f"{portfolio['Annualized Return (CAGR)']:.1%}",
         delta=f"{(portfolio['Annualized Return (CAGR)']-spy['Annualized Return (CAGR)'])*100:+.1f} pp vs SPY", delta_color="off")
c.metric("Portfolio volatility", f"{portfolio['Annualized Volatility']:.1%}")
d.metric("Portfolio max drawdown", f"{portfolio['Max Drawdown']:.1%}")
st.caption("Daily-rebalanced equal-weight 11-stock research portfolio; zero transaction costs. CAGR, realized volatility and drawdown reflect the selected historical period.")

st.markdown("### Performance over time")
series = [*chosen, BENCHMARK, PORTFOLIO]
plot_frame = wealth[series].rename(columns={BENCHMARK: "SPY · S&P 500", PORTFOLIO: "NYSE sample · equal weight"})
fig = px.line(plot_frame, labels={"index": "Trading session", "value": "Portfolio value ($)", "variable": "Asset"})
fig.update_traces(line=dict(width=2))
fig.update_layout(hovermode="x unified", legend=dict(orientation="h", y=-0.18),
                  margin=dict(l=15, r=15, t=15, b=15), height=435)
st.plotly_chart(fig, use_container_width=True)

st.markdown("### Return and risk")
col1, col2 = st.columns(2)
with col1:
    view = metrics.loc[[*STOCKS, BENCHMARK, PORTFOLIO]].copy().reset_index()
    view["CAGR (%)"] = view["Annualized Return (CAGR)"] * 100
    view["Volatility (%)"] = view["Annualized Volatility"] * 100
    view["Type"] = view["Ticker"].map(lambda t: "Benchmark" if t == BENCHMARK else ("Equal-weight basket" if t == PORTFOLIO else "Selected NYSE stock"))
    scatter = px.scatter(view, x="Volatility (%)", y="CAGR (%)", text="Ticker", color="Type",
                         hover_data=["Sector", "Sharpe Ratio"],
                         color_discrete_map={"Benchmark": NAVY, "Equal-weight basket": TEAL, "Selected NYSE stock": "#6a9dc9"},
                         title="Risk–return map")
    scatter.update_traces(textposition="top center")
    scatter.update_layout(height=420, margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(scatter, use_container_width=True)
with col2:
    dd = drawdowns(wealth)[[BENCHMARK, PORTFOLIO]] * 100
    dd.columns = ["SPY", "Equal-weight NYSE sample"]
    dfig = px.line(dd, title="Historical drawdown", labels={"index": "Date", "value": "Drawdown (%)", "variable": "Asset"},
                   color_discrete_sequence=[NAVY, TEAL])
    dfig.update_layout(height=420, hovermode="x unified", margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(dfig, use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    rv = rolling_volatility(prices, window=30)[[BENCHMARK, PORTFOLIO]] * 100
    rv.columns = ["SPY", "Equal-weight NYSE sample"]
    rfig = px.line(rv, title="30-session rolling annualized volatility", labels={"index": "Date", "value": "Volatility (%)", "variable": "Asset"},
                   color_discrete_sequence=[NAVY, TEAL])
    rfig.update_layout(height=380, margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(rfig, use_container_width=True)
with col4:
    sample_metrics = metrics.loc[list(STOCKS)].copy().reset_index()
    sample_metrics["CAGR (%)"] = sample_metrics["Annualized Return (CAGR)"] * 100
    sample_metrics = sample_metrics.sort_values("CAGR (%)")
    bfig = px.bar(sample_metrics, x="CAGR (%)", y="Ticker", orientation="h", color="CAGR (%)",
                  color_continuous_scale="Teal", title="Individual NYSE stock returns by ticker",
                  hover_data=["Sector", "Annualized Volatility"])
    bfig.update_layout(height=380, coloraxis_showscale=False, margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(bfig, use_container_width=True)
st.caption("Each stock represents only itself, **not** its entire sector. Sample selection and daily rebalancing influence comparisons.")

st.markdown("### Correlation and breadth")
x, y = st.columns(2)
with x:
    corr = returns[TICKERS].corr()
    heat = go.Figure(go.Heatmap(z=corr.values, x=corr.columns, y=corr.index, zmin=-1, zmax=1,
                                colorscale="RdBu", reversescale=False, zmid=0))
    heat.update_layout(title="Daily return correlations", height=430, margin=dict(l=15, r=15, t=50, b=15))
    st.plotly_chart(heat, use_container_width=True)
with y:
    breadth = market_breadth(prices)
    br = px.line(breadth, title="11-company sample breadth · trailing 63 sessions",
                 labels={"index": "Date", "value": "Share of positive stocks (%)"}, color_discrete_sequence=[TEAL])
    br.update_layout(height=430, showlegend=False, margin=dict(l=15, r=15, t=50, b=15))
    br.update_yaxes(range=[0, 100])
    st.plotly_chart(br, use_container_width=True)

with st.expander("Methodology, data quality and download", expanded=False):
    st.markdown(f"""- **Price basis:** dividend/split-adjusted daily closing prices, not intraday or investment recommendations.
- **Coverage:** {len(prices)} aligned sessions; 11 selected NYSE equities plus SPY, a broad U.S. market ETF.
- **Portfolio:** equal-weight across the eleven companies, rebalanced each trading session; no taxes, slippage or trading costs.
- **Calculation:** annualization uses 252 trading sessions; historical Sharpe uses an explicitly selected {assumed_rf:.1%} annual risk-free assumption.
- **Data quality:** complete shared dates only, no forward filling; provider-date and large-return checks apply before displaying real data.
- **Limitations:** curated sample, survivorship/selection bias, revised provider quotes, correlation instability, not a NYSE-wide breadth statistic.
- **Data privacy/licensing:** the app does not expose downloadable raw Yahoo price records. The CSV below contains **derived summary metrics**, not raw quotes.
""")
    columns = ["Sector", "Cumulative Return", "Annualized Return (CAGR)", "Annualized Volatility", "Sharpe Ratio", "Max Drawdown", "Beta vs SPY", "Correlation vs SPY"]
    st.dataframe(metrics[columns].style.format({
        "Cumulative Return": "{:.1%}", "Annualized Return (CAGR)": "{:.1%}",
        "Annualized Volatility": "{:.1%}", "Max Drawdown": "{:.1%}",
        "Sharpe Ratio": "{:.2f}", "Beta vs SPY": "{:.2f}", "Correlation vs SPY": "{:.2f}",
    }), use_container_width=True)
    st.download_button("Download derived metrics CSV", data=metrics.to_csv().encode("utf-8"),
                       file_name=("SYNTHETIC_DEMO_" if is_demo else "") + "nyse_market_metrics.csv", mime="text/csv")

st.divider()
st.caption("Research by Ashraful Enam · Finance & Data Analytics | Education only, not financial advice. Historic performance cannot predict future results.")
