"""Tests for TCO calculations, capability allocation, and rationalization logic."""

import pytest
from tvi.cost_analytics import (
    calculate_application_tco,
    calculate_capability_cost,
    calculate_service_cost,
    get_application_profile,
)
from tvi.rationalization import find_rationalization_candidates, score_application_portfolio


def test_application_tco_calculation():
    """Verify application TCO calculation and unit economics."""
    df = calculate_application_tco()
    assert not df.empty
    assert "annual_tco" in df.columns
    assert "annual_cost_per_user" in df.columns
    assert "cost_per_transaction" in df.columns
    assert (df["annual_tco"] > 0).all()
    # Check Scenario A (APP001) has high TCO
    app001 = df[df["application_id"] == "APP001"]
    assert not app001.empty
    assert app001.iloc[0]["annual_tco"] > 100000000.0  # > ₹10 Cr


def test_capability_cost_allocation_reconciliation():
    """Verify capability cost attribution logic."""
    cap_df = calculate_capability_cost()
    assert not cap_df.empty
    assert "total_capability_cost" in cap_df.columns
    assert "direct_app_cost" in cap_df.columns
    assert "shared_infra_allocated" in cap_df.columns
    assert (cap_df["total_capability_cost"] > 0).all()


def test_rationalization_candidates():
    """Verify rationalization scoring identifies Scenario B (APP021)."""
    candidates = find_rationalization_candidates(review_threshold=50.0)
    assert not candidates.empty
    app_ids = candidates["application_id"].tolist()
    assert "APP021" in app_ids
    app021_row = candidates[candidates["application_id"] == "APP021"].iloc[0]
    assert "potential_avoidable_cost_scenario" in app021_row
    assert len(app021_row["investigation_evidence"]) > 0


def test_application_profile():
    """Verify individual application profile retrieval."""
    profile = get_application_profile("APP001")
    assert "summary" in profile
    assert profile["summary"]["application_name"] == "CoreBanking Alpha"
    assert not profile["monthly_costs"].empty
