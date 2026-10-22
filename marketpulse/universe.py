"""Curated cross-sector NYSE-listed stock sample; not the entire exchange."""

from collections import OrderedDict

# One representative publicly traded NYSE company per GICS sector.
# GICS classification is for analytical categorization only and can change.
STOCKS = OrderedDict(
    [
        ("JPM", ("JPMorgan Chase", "Financials")),
        ("XOM", ("Exxon Mobil", "Energy")),
        ("KO", ("Coca-Cola", "Consumer Staples")),
        ("JNJ", ("Johnson & Johnson", "Health Care")),
        ("CAT", ("Caterpillar", "Industrials")),
        ("HD", ("Home Depot", "Consumer Discretionary")),
        ("NEE", ("NextEra Energy", "Utilities")),
        ("IBM", ("IBM", "Information Technology")),
        ("PLD", ("Prologis", "Real Estate")),
        ("DIS", ("Walt Disney", "Communication Services")),
        ("SHW", ("Sherwin-Williams", "Materials")),
    ]
)
BENCHMARK = "SPY"  # NYSE Arca-listed ETF tracking the S&P 500, not a NYSE-only index.
TICKERS = [*STOCKS.keys(), BENCHMARK]
TRADING_DAYS = 252
