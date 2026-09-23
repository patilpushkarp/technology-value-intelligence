"""Tests for DuckDB analytical storage and SQL views."""

import pytest
from tvi.config import load_config
from tvi.database import get_database


def test_database_tables_and_counts():
    """Verify DuckDB loads all tables and has correct row counts."""
    cfg = load_config()
    db = get_database(cfg.database.path)
    counts = db.get_entity_counts()

    assert counts.get("business_units", 0) > 0
    assert counts.get("applications", 0) > 0
    assert counts.get("cost_records", 0) > 0
    assert counts.get("consumption_records", 0) > 0


def test_database_cost_aggregations():
    """Verify core cost aggregation queries execute and return positive sums."""
    cfg = load_config()
    db = get_database(cfg.database.path)

    total_cost = db.get_total_cost()
    assert total_cost > 0.0

    cat_df = db.get_cost_by_category()
    assert not cat_df.empty
    assert cat_df["total_cost"].sum() == pytest.approx(total_cost, rel=1e-3)

    app_df = db.get_cost_by_application()
    assert not app_df.empty

    trend_df = db.get_monthly_cost_trend()
    assert len(trend_df) == 12
