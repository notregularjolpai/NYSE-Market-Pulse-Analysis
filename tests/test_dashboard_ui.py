"""Streamlit headless smoke test: keeps the public dashboard renderable."""
from pathlib import Path

import pytest


def test_streamlit_app_renders_explicitly_synthetic_demo(monkeypatch):
    streamlit = pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest

    monkeypatch.setenv("NYSE_DASHBOARD_TEST_MODE", "1")
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=65).run()
    errors = [str(exc.message) for exc in app.exception]
    assert not errors, errors
    assert any("NYSE Market Pulse" in h.value for h in app.title)
    assert len(app.error) >= 1  # explicitly labeled synthetic-mode warning banner
    assert len(app.metric) == 4
