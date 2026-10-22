# Data Dictionary

| Variable | Type | Meaning |
|---|---|---|
| `Date` | YYYY-MM-DD | Trading session date; the dataset index |
| `JPM`, `XOM`, `KO`, `JNJ`, `CAT`, `HD`, `NEE`, `IBM`, `PLD`, `DIS`, `SHW` | Float > 0 | Dividend/split-adjusted daily close in USD per share, as returned by Yahoo Finance; **synthetic USD-like levels in demo** |
| `SPY` | Float > 0 | NYSE Arca ETF tracking the S&P 500, adjusted close; benchmark |
| `Ticker` | Text | A stock ticker, SPY, or `EQUAL_WEIGHT` for daily rebalanced equal-weight sample |
| `Sector` | Text | Curated sector label for chosen company; not sector index |
| `Cumulative Return` | Decimal | End/start growth of $100 minus one |
| `Annualized Return (CAGR)` | Decimal | Compounded cumulative return annualized by 252 / number of daily returns |
| `Annualized Volatility` | Decimal | Standard deviation of daily returns × sqrt(252) |
| `Sharpe Ratio` | Numeric | (mean daily return × 252 − assumed annual risk-free return) / annualized volatility |
| `Max Drawdown` | Decimal ≤ 0 | Lowest wealth / previously seen wealth peak − 1 |
| `Beta vs SPY` | Numeric | Cov(asset daily returns, SPY daily returns) / Var(SPY daily returns) |
| `Correlation vs SPY` | [-1,1] | Pearson correlation between daily returns |
| `Observations` | Integer | Number of daily return observations |
| `Sample Breadth (%)` | 0 to 100 | Percent of **11 sampled** stocks above their price from 63 sessions before |

**No forward-filling:** A missing price on any ticker's date removes that whole date for every ticker, maintaining a matched sample. Invalid, non-positive prices trigger a validation error. Return computation uses adjusted closing prices (`auto_adjust=True`) and `pct_change(fill_method=None)`.

Historical data is downloaded at runtime; the repository ships only clearly synthetic demonstration inputs.
