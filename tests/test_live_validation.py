"""Independent financial reconciliations and fail-closed source validation."""
from datetime import datetime, timedelta, timezone
import json

import numpy as np
import pandas as pd
import pytest

from marketpulse.analytics import performance_table
from marketpulse.data import MarketDataError, make_demo_prices, save_prices, validate_prices
from marketpulse.quality import audit_history, reconcile_outputs, verify_saved_run
from marketpulse.universe import TICKERS


@pytest.fixture
def example():
    return make_demo_prices(periods=252, seed=1128)


def test_real_reconciliation_math_on_fixture(example):
    result = reconcile_outputs(example, performance_table(example))
    assert result['passed'] is True
    assert len(result['independent_reconciliations']) == 2


def test_reject_modified_cumulative_return(example):
    results = performance_table(example)
    results.loc['SPY', 'Cumulative Return'] += 0.01
    with pytest.raises(MarketDataError, match='Cumulative Return'):
        reconcile_outputs(example, results)


def test_reject_modified_volatility(example):
    results = performance_table(example)
    results.loc['JPM', 'Annualized Volatility'] *= 0.5
    with pytest.raises(MarketDataError, match='Volatility'):
        reconcile_outputs(example, results)


def test_reject_invalid_drawdown(example):
    results = performance_table(example)
    results.loc['JPM', 'Max Drawdown'] = 0.05
    with pytest.raises(MarketDataError, match='drawdown'):
        reconcile_outputs(example, results)


def test_reject_high_missing_source_coverage(example):
    broken = example.copy()
    broken.loc[broken.index[:20], 'JPM'] = np.nan
    with pytest.raises(MarketDataError, match='6|7|8|Missing|lack'):
        validate_prices(broken)


def test_audit_valid_requested_window(example):
    start = example.index.min().date().isoformat()
    end = (example.index.max() + pd.Timedelta(days=1)).date().isoformat()
    audit = audit_history(example, start, end)
    assert audit['observation_count'] == len(example)
    assert audit['symbols_received'] == TICKERS
    assert audit['aligned_complete_sessions']


def test_audit_catches_request_boundary(example):
    start = (example.index.min() + pd.Timedelta(days=1)).date().isoformat()
    end = (example.index.max() + pd.Timedelta(days=1)).date().isoformat()
    with pytest.raises(MarketDataError, match='outside'):
        audit_history(example, start, end)


def test_audit_flags_extreme_daily_move(example):
    broken = example.copy()
    broken.loc[broken.index[30], 'KO'] *= 20
    start = broken.index.min().date().isoformat()
    end = (broken.index.max() + pd.Timedelta(days=1)).date().isoformat()
    with pytest.raises(MarketDataError, match='80%'):
        audit_history(broken, start, end)


def test_audit_rejects_near_current_stale_quotes(example):
    start = example.index.min().date().isoformat()
    near_now = (datetime.now(timezone.utc).date() + timedelta(days=1)).isoformat()
    with pytest.raises(MarketDataError, match='stale'):
        audit_history(example, start, near_now)


def test_saved_run_rejects_synthetic_label(example, tmp_path):
    price_path = tmp_path / 'adjusted_close.csv'
    metrics_path = tmp_path / 'performance_metrics.csv'
    metadata_path = tmp_path / 'run_metadata.json'
    save_prices(example, price_path)
    performance_table(example).to_csv(metrics_path)
    metadata_path.write_text(json.dumps({
        'dataset_type': 'SYNTHETIC_DEMO',
        'requested_window': {
            'start_inclusive': example.index.min().date().isoformat(),
            'end_exclusive': (example.index.max() + pd.Timedelta(days=1)).date().isoformat()
        }
    }))
    with pytest.raises(MarketDataError, match='synthetic'):
        verify_saved_run(price_path, metrics_path, metadata_path)
