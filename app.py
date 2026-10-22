"""Interactive NYSE Market Pulse dashboard (run: streamlit run app.py)."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from marketpulse.analytics import PORTFOLIO, drawdowns, market_breadth, performance_table, rolling_volatility, wealth_index
from marketpulse.data import MarketDataError, load_prices
from marketpulse.universe import BENCHMARK, STOCKS, TICKERS

ROOT = Path(__file__).parent
st.set_page_config(page_title="NYSE Market Pulse | Finance Analytics", page_icon="📈", layout="wide")
st.markdown("""<style>
.block-container {padding-top: 2rem;}
h1, h2, h3 {color: #1b3049;}
[data-testid='stMetricValue'] {color: #087f8c;}
</style>""", unsafe_allow_html=True)
st.title("NYSE Market Pulse")
st.caption("Cross-sector NYSE stock analytics | S&P 500 ETF benchmark | Educational research")

choice = st.sidebar.radio("Dataset", ["Historical NYSE stock prices", "Synthetic demo"], index=0)
is_demo = choice == "Synthetic demo"
file = ROOT / ("data/demo/synthetic_adjusted_close.csv" if is_demo else "data/processed/adjusted_close.csv")

@st.cache_data(show_spinner=False)
def read_input(path: str, updated_ns: int) -> pd.DataFrame:
    return load_prices(path)

if not file.exists():
    st.info("No downloaded market data found. Run `python scripts/run_analysis.py --start 2023-01-01` in this repository, then refresh this page. Or choose **Synthetic demo** in the sidebar for a clearly labeled offline preview.")
    st.stop()

try:
    all_prices = read_input(str(file), file.stat().st_mtime_ns)
except MarketDataError as exc:
    st.error(str(exc)); st.stop()

if is_demo:
    st.warning("**SIMULATED DEMO — NOT HISTORICAL MARKET DATA.** Every displayed price and statistic is generated from synthetic inputs.")
else:
    st.success(f"Historical adjusted close prices (Yahoo Finance source). Latest observation: {all_prices.index[-1].date()}. Not real-time quotes.")

min_date = all_prices.index[0].date()
max_date = all_prices.index[-1].date()
start, end = st.sidebar.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
selected = st.sidebar.multiselect("Selected NYSE companies", list(STOCKS), default=["JPM", "XOM", "KO", "CAT"])
if start >= end:
    st.error("Select a date range with at least 90 common trading sessions.")
    st.stop()
prices = all_prices.loc[str(start):str(end)]
if len(prices) < 90:
    st.error("At least 90 observations are needed for the risk metrics. Expand the selected date range.")
    st.stop()

metrics = performance_table(prices)
bench = metrics.loc[BENCHMARK]
port = metrics.loc[PORTFOLIO]
cols = st.columns(4)
cols[0].metric("SPY CAGR", f"{bench['Annualized Return (CAGR)']:.1%}")
cols[1].metric("SPY Volatility", f"{bench['Annualized Volatility']:.1%}")
cols[2].metric("Sample Portfolio CAGR", f"{port['Annualized Return (CAGR)']:.1%}")
cols[3].metric("Portfolio Max Drawdown", f"{port['Max Drawdown']:.1%}")

st.subheader("Growth of $100 — adjusted prices")
wealth = wealth_index(prices)
show = [*selected, BENCHMARK, PORTFOLIO]
fig = px.line(wealth[show], labels={"index": "Trading date", "value": "Wealth ($)", "variable": "Ticker"})
fig.update_layout(hovermode="x unified", legend_title_text="Symbol")
st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("Drawdown comparison")
    dd = drawdowns(wealth)[[BENCHMARK, PORTFOLIO]] * 100
    dfig = px.line(dd, labels={"index": "Date", "value": "Drawdown (%)", "variable": "Asset"})
    st.plotly_chart(dfig, use_container_width=True)
with right:
    st.subheader("Rolling annualized volatility (30 days)")
    v = rolling_volatility(prices, window=30)[[BENCHMARK, PORTFOLIO]] * 100
    vfig = px.line(v, labels={"index": "Date", "value": "Volatility (%)", "variable": "Asset"})
    st.plotly_chart(vfig, use_container_width=True)

st.subheader("NYSE sector-representative comparison")
sector_view = metrics.loc[list(STOCKS), ["Sector", "Annualized Return (CAGR)", "Annualized Volatility", "Max Drawdown", "Beta vs SPY"]].copy()
sector_view["Annualized Return (CAGR)"] *= 100
sector_view["Annualized Volatility"] *= 100
sector_view["Max Drawdown"] *= 100
sector_view = sector_view.sort_values("Annualized Return (CAGR)")
sector_fig = px.bar(sector_view.reset_index(), x="Annualized Return (CAGR)", y="Sector", color="Ticker", orientation="h",
                    hover_data=["Beta vs SPY"], labels={"Annualized Return (CAGR)": "CAGR (%)"})
st.plotly_chart(sector_fig, use_container_width=True)
st.caption("One company stands in for each GICS sector. This is not a sector-index return ranking.")

st.subheader("Co-movement & sample breadth")
a, b = st.columns(2)
with a:
    corr = prices[TICKERS].pct_change(fill_method=None).iloc[1:].corr()
    heatmap = go.Figure(data=go.Heatmap(z=corr.values, x=corr.columns, y=corr.index, zmin=-1, zmax=1, colorscale="RdBu", reversescale=False))
    heatmap.update_layout(height=440, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(heatmap, use_container_width=True)
with b:
    breadth = market_breadth(prices)
    st.line_chart(breadth, y_label="Share of 11 sampled stocks (%)")
    st.caption("Percentage of the eleven stocks with positive 63-session returns; not NYSE-wide breadth.")

with st.expander("Methodology, caveats, and raw summary"):
    st.markdown("Annualization: 252 trading sessions; daily-rebalanced equal-weight sample; zero assumed risk-free rate; missing dates dropped without forward-fill. Prices are adjusted for splits/dividends. Historical data can be revised and does not predict future returns. SPY is an NYSE Arca ETF tracking the S&P 500, not an NYSE-only index. The stock sample is not the entire NYSE and is vulnerable to survivorship and selection biases. Educational use only, not investment advice.")
    st.dataframe(metrics.style.format({"Cumulative Return": "{:.1%}", "Annualized Return (CAGR)": "{:.1%}", "Annualized Volatility": "{:.1%}", "Max Drawdown": "{:.1%}", "Sharpe Ratio": "{:.2f}", "Beta vs SPY": "{:.2f}", "Correlation vs SPY": "{:.2f}"}), use_container_width=True)
    st.download_button("Download results CSV", metrics.to_csv().encode("utf-8"), file_name=("SIMULATED_" if is_demo else "") + "nyse_market_metrics.csv", mime="text/csv")
