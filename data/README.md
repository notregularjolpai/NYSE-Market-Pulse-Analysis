# Data provenance and storage

- **Historical (real)**: Running `python scripts/run_analysis.py` fetches *adjusted daily closing prices* from Yahoo Finance via `yfinance`, checks 12 symbols, then writes `data/processed/adjusted_close.csv`. The full source output and date window are noted in `outputs/market/run_metadata.json`.
- **Demo (synthetic only)**: Running `python scripts/run_analysis.py --demo` generates a reproducible, fabricated series in `data/demo/synthetic_adjusted_close.csv`. These are not stock quotes.
- `data/processed/` is intentionally `.gitignore`d: downloaded third-party price records are not shipped with this repository, because usage and redistribution may be restricted.
- All price rows are aligned to the **intersection** of dates with valid positive values for every ticker; missing prices are not filled.
- The ticker sample is current/curated and is **not** a historical NYSE constituent universe.

For columns, definitions, and missing data decisions see [data dictionary](../docs/data_dictionary.md).
