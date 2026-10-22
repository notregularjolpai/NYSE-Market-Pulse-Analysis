# GitHub publishing guide

## Repository settings

- **Name:** `NYSE-Market-Pulse-Analysis`
- **Visibility:** Public (if you intend to feature it in your portfolio)
- **Description:** `NYSE stock market analysis across 11 sectors with Python, portfolio risk metrics, interactive dashboards, and S&P 500 benchmarking.`
- **Topics:** `nyse`, `stock-market-analysis`, `financial-analysis`, `portfolio-analytics`, `investment-risk`, `python`, `pandas`, `streamlit`, `data-visualization`, `equity-research`

## Publishing the project

1. On GitHub, select **New repository** and use the name above. Do **not** initialize a README, license or gitignore (these files already exist in this project).
2. Extract the ZIP. In the empty repository choose **uploading an existing file** and upload **the contents of the extracted folder**, retaining the directory structure. Avoid uploading the ZIP itself as a single file.
3. Commit the files to `main`; the workflow will run Python unit tests using a network-free demo. Downloaded historical prices are intentionally not part of the repository.
4. To generate real historical results, clone locally, install `requirements.txt`, and run `python scripts/run_analysis.py --start 2023-01-01` with internet access.
5. Launch `streamlit run app.py` to explore a local interactive dashboard.
6. Pin the repository to the GitHub profile once the code and documentation are published.

If GitHub's web interface doesn't retain nested directories during drag-and-drop, use GitHub Desktop or `git add . && git commit -m "Initial NYSE market analytics project" && git push -u origin main` instead.

**Important:** An MIT license covers the project code only, not market-price data downloaded from third parties. Do not publish the unlicensed price cache.
