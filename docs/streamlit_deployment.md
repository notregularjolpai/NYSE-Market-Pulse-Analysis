# Streamlit Community Cloud — NYSE Market Pulse

**Code readiness:** `app.py` is a public Streamlit app that retrieves historical Yahoo Finance adjusted closing prices server-side, validates all 12 series, and stores them in an **ephemeral hourly Streamlit cache**. A rate limit, connectivity error, stale dataset or failed quality check produces a visible failure message; it does **not** silently show fabricated prices. An intentionally selected synthetic demo remains available.

**Hosting status:** Deployment requires the repository owner's separate Streamlit Community Cloud sign-in and GitHub authorization. A `streamlit.app` URL must not be claimed until the owner deploys the app successfully.

## Deploy (repository owner)

1. Open https://share.streamlit.io and **Continue with GitHub**. Authorize the GitHub repository when prompted.
2. Select **Create app** → **Yup, I have an app** → **Deploy a public app from GitHub** (wording may vary).
3. Set **Repository:** `notregularjolpai/NYSE-Market-Pulse-Analysis`.
4. Set **Branch:** `main`.
5. Set **Main file path:** `app.py`.
6. In **Advanced settings**, choose **Python 3.11**. Dependencies install automatically from the repository-root `requirements.txt`.
7. Optional: choose an available app URL; **do not add credentials, API keys or secrets**. The current data source uses no user API key.
8. Click **Deploy**. After launch, confirm the **Historical market prices** source is selected, the last observation date is shown, and a chart appears. Check that you can switch to the visibly labeled **Synthetic demonstration**.
9. Copy the *actual* URL from the deployed app into the GitHub repository's **About → Website** field, profile README, and portfolio website. Do not guess a URL before deployment.

## Controls and provider behavior

- First live launch needs internet access to Yahoo Finance from the Streamlit host. The historical fetch includes all 11 stocks plus SPY.
- Streamlit `@st.cache_data(ttl=3600, max_entries=3)` limits provider calls. A user can manually select **Refresh historical data**; rerunning a filter or changing a chart does not re-fetch the provider prices.
- The app downloads prices only in memory. The repo does not contain third-party historical stock-price datasets; raw quotes are **not downloadable from the dashboard**. The app offers a derived-metrics summary CSV instead.
- Yahoo Finance may rate-limit or block some cloud IPs. In that case, the app shows a data-source error with no synthetic substitution. The historical price provider is **not an NYSE-certified exchange feed**, and information is **not intraday / real-time**.
- One representative NYSE stock per GICS sector does not mean NYSE-wide sector performance. SPY is an NYSE Arca-listed fund tracking the broader S&P 500, not the NYSE Composite.
- All returns are backward-looking; the sample assumes **daily portfolio rebalancing and no transaction costs**.

## Troubleshooting

| Symptom | Fix |
|:--|:--|
| App dependencies fail to install | Confirm Python 3.11 and root `requirements.txt` |
| Historical provider inaccessible | Try manual refresh once, check deployment logs, then revisit later; use explicitly labeled demo for a software tour |
| Date range too short | Select at least 90 common sessions |
| Metrics changed from published report | The published snapshot ends October 21, 2026. A live app uses the most recently available data and may include provider revisions |
| App displays old last observation | Use Refresh; cache expires hourly, but exchange closures and provider lags are expected |
| GitHub update not reflected | Use Streamlit app settings / reboot and check latest deployed branch |

## Pre-deployment checks

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python -m compileall -q app.py marketpulse
streamlit run app.py
```

An offline unit test mocks Yahoo Finance; a Streamlit headless test renders the labeled synthetic dashboard. The separate `Historical Market Research` GitHub Actions job exercises the real feed and independent audit. **A passing test suite does not guarantee Yahoo Finance will allow downloads from every Community Cloud host.**

**Official references:** [Streamlit deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy), [file structure](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization), [dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies).
