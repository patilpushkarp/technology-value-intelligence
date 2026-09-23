"""Tests for Technology Value Realization (TVR) and investment variances."""

import pytest
from tvi.value_realization import (
    analyze_benefit_kpi_progression,
    calculate_benefit_realization,
    calculate_project_budget_variance,
    get_project_value_profile,
)


def test_project_budget_variance():
    """Verify budget variance calculation."""
    df = calculate_project_budget_variance()
    assert not df.empty
    assert "budget_variance" in df.columns
    assert "variance_status" in df.columns


def test_benefit_realization_scenarios_e_and_f():
    """Verify Scenario E (high realization) and Scenario F (benefit gap)."""
    df = calculate_benefit_realization()
    assert not df.empty

    # Scenario E: PRJ003
    prj003 = df[df["project_id"] == "PRJ003"].iloc[0]
    assert prj003["benefit_realization_pct"] >= 100.0

    # Scenario F: PRJ014
    prj014 = df[df["project_id"] == "PRJ014"].iloc[0]
    assert prj014["benefit_realization_pct"] < 35.0
    assert prj014["benefit_gap"] > 150000000.0  # > ₹15 Cr gap


def test_benefit_kpi_progression():
    """Verify benefit to KPI movement joins."""
    df = analyze_benefit_kpi_progression()
    assert not df.empty
    assert "kpi_id" in df.columns
    assert "kpi_target_achievement_pct" in df.columns


def test_project_value_profile():
    """Verify detailed project dossier retrieval."""
    profile = get_project_value_profile("PRJ003")
    assert "project" in profile
    assert profile["project"]["project_name"] == "Real-Time Payment Modernization"
    assert not profile["benefits"].empty
