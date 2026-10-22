"""Publication-ready figures. Demo exports are visibly labeled synthetic."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .analytics import PORTFOLIO, drawdowns, market_breadth, performance_table, wealth_index
from .universe import BENCHMARK, STOCKS, TICKERS

NAVY = "#13243D"
TEAL = "#087F8C"
BLUE = "#4B83C2"
MUTED = "#718096"
WARM = "#C67743"


def _setup(title: str, demo: bool, figsize: tuple[int, int] = (11, 6)):
    fig, ax = plt.subplots(figsize=figsize, dpi=130)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.set_title(title, loc="left", fontsize=16, fontweight="bold", color=NAVY, pad=17)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(colors=MUTED)
    ax.grid(axis="y", alpha=0.17)
    if demo:
        fig.text(0.5, 0.5, "SIMULATED DEMO  •  NOT MARKET DATA",
                 fontsize=23, fontweight="bold", color="#b44b4b",
                 alpha=0.18, ha="center", va="center", rotation=25)
        fig.text(0.01, 0.01, "SYNTHETIC DATA • FOR CODE DEMONSTRATION ONLY", fontsize=9, color="#9b3b3b")
    else:
        fig.text(0.01, 0.01, "Historical adjusted closing prices; retrospective performance does not predict future results.", fontsize=8, color=MUTED)
    return fig, ax


def _save(fig, folder: Path, name: str) -> None:
    fig.savefig(folder / name, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def export_charts(prices: pd.DataFrame, folder: str | Path, demo: bool = False) -> list[str]:
    out = Path(folder)
    out.mkdir(parents=True, exist_ok=True)
    performance = performance_table(prices)
    wealth = wealth_index(prices)
    dd = drawdowns(wealth)
    names: list[str] = []

    fig, ax = _setup("NYSE Sample vs. S&P 500 Proxy | $100 Growth", demo)
    palette = plt.get_cmap("tab20")
    for i, ticker in enumerate(STOCKS):
        ax.plot(wealth.index, wealth[ticker], label=ticker, alpha=0.65, lw=1.2, color=palette(i / 12))
    ax.plot(wealth.index, wealth[BENCHMARK], label="SPY (S&P 500 proxy)", color=NAVY, lw=2.6)
    ax.plot(wealth.index, wealth[PORTFOLIO], label="Equal weight (daily rebalance)", color=TEAL, lw=2.8)
    ax.set_ylabel("Growth of an initial $100", color=NAVY)
    ax.legend(loc="upper left", bbox_to_anchor=(1, 1), frameon=False)
    _save(fig, out, "01_growth_of_100.png"); names.append("01_growth_of_100.png")

    fig, ax = _setup("Risk–Return Profile | Volatility vs. CAGR", demo)
    for ticker in [*STOCKS, BENCHMARK, PORTFOLIO]:
        row = performance.loc[ticker]
        color = NAVY if ticker == BENCHMARK else (TEAL if ticker == PORTFOLIO else BLUE)
        ax.scatter(row["Annualized Volatility"] * 100, row["Annualized Return (CAGR)"] * 100,
                   color=color, s=115 if ticker in (BENCHMARK, PORTFOLIO) else 65, alpha=0.85)
        ax.annotate(ticker, (row["Annualized Volatility"] * 100, row["Annualized Return (CAGR)"] * 100),
                    xytext=(5, 5), textcoords="offset points", fontsize=8)
    ax.axhline(0, ls="--", lw=1, color=MUTED)
    ax.set_xlabel("Annualized realized volatility (%)", color=NAVY)
    ax.set_ylabel("Annualized compounded return (%)", color=NAVY)
    _save(fig, out, "02_risk_return.png"); names.append("02_risk_return.png")

    fig, ax = _setup("Drawdowns | Broad Market vs. Equal-Weight Sample", demo)
    ax.fill_between(dd.index, dd[BENCHMARK] * 100, 0, color=BLUE, alpha=0.2)
    ax.plot(dd.index, dd[BENCHMARK] * 100, color=NAVY, lw=1.6, label="SPY")
    ax.plot(dd.index, dd[PORTFOLIO] * 100, color=TEAL, lw=1.9, label="Daily-rebalanced sample")
    ax.set_ylabel("Drawdown from prior peak (%)", color=NAVY)
    ax.legend(frameon=False)
    _save(fig, out, "03_drawdowns.png"); names.append("03_drawdowns.png")

    fig, ax = _setup("Daily Return Correlation | NYSE Sample and SPY", demo, (10, 8))
    corr = prices.pct_change(fill_method=None).iloc[1:][TICKERS].corr()
    img = ax.imshow(corr.to_numpy(), cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr))); ax.set_xticklabels(corr.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(corr))); ax.set_yticklabels(corr.index)
    for i in range(len(corr)):
        for j in range(len(corr)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=7,
                    color="white" if abs(corr.iloc[i, j]) > 0.65 else NAVY)
    fig.colorbar(img, ax=ax, fraction=0.046, pad=0.04)
    ax.grid(False)
    _save(fig, out, "04_correlation_matrix.png"); names.append("04_correlation_matrix.png")

    breadth = market_breadth(prices)
    fig, ax = _setup("Sample Market Breadth | Positive 63-Day Return", demo)
    ax.plot(breadth.index, breadth, lw=2, color=TEAL)
    ax.axhline(50, color=MUTED, lw=1.0, ls="--", label="50% of sampled stocks")
    ax.set_ylabel("Share of 11 NYSE stocks (%)", color=NAVY)
    ax.set_ylim(0, 100); ax.legend(frameon=False)
    _save(fig, out, "05_sample_breadth.png"); names.append("05_sample_breadth.png")

    sample = performance.loc[list(STOCKS)].sort_values("Annualized Return (CAGR)")
    fig, ax = _setup("Sector Representative | Compounded Annual Return", demo, (11, 7))
    labels = [f"{STOCKS[t][1]}  ({t})" for t in sample.index]
    v = (sample["Annualized Return (CAGR)"] * 100).to_numpy()
    ax.barh(labels, v, color=[TEAL if x >= 0 else WARM for x in v])
    ax.axvline(0, color=MUTED, lw=1)
    ax.set_xlabel("Annualized compounded return (%)", color=NAVY)
    ax.text(0.99, -0.13, "One selected stock per sector; NOT sector-index returns.", transform=ax.transAxes,
            fontsize=9, color=MUTED, ha="right")
    _save(fig, out, "06_sector_representatives.png"); names.append("06_sector_representatives.png")
    return names
