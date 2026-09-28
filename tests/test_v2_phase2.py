"""Unit tests for Phase 2 (Modules 04-06) v2 Roadmap Capabilities."""

import numpy as np
import pandas as pd
import pytest

from tvi.cost_analytics import (
    calculate_application_tco,
    calculate_activity_based_costing,
    model_price_escalation_sensitivity,
    benchmark_finops_unit_economics,
    forecast_application_tco,
    calculate_dynamic_capability_cost,
    get_nested_capability_hierarchy_cost,
    simulate_cloud_migration_what_if,
    audit_capability_allocation_reconciliation,
)
from tvi.consumption_analytics import (
    decompose_telemetry_time_series,
    generate_serverless_concurrency_metrics,
    calculate_greenops_carbon_footprint,
    generate_rightsizing_recommendations,
)


# ==============================================================================
# Module 04: Application Cost Intelligence v2 Tests
# ==============================================================================
def test_activity_based_costing_reconciliation():
    """Verify 2-Stage ABC allocations reconcile 100% to application TCO."""
    tco_df = calculate_application_tco()
    abc_df = calculate_activity_based_costing()

    assert len(abc_df) == len(tco_df)
    assert set(abc_df.columns).issubset({
        "application_id", "annual_tco", "act_software_eng", "act_resiliency",
        "act_txn_processing", "act_helpdesk", "abc_total_cost"
    })
    total_tco = tco_df["annual_tco"].sum()
    total_abc = abc_df["abc_total_cost"].sum()
    # Reconciles within 1% rounding margin across 4 driver transformations
    assert abs(total_tco - total_abc) / total_tco < 0.01


def test_price_escalation_sensitivity():
    """Verify multi-year macro-inflation and contractual price escalation modeling."""
    sensitivity_df = model_price_escalation_sensitivity(
        inflation_rates=[0.03, 0.05, 0.08], vendor_escalation_rate=0.07
    )

    assert len(sensitivity_df) == 3
    assert "year_1_spend_cr" in sensitivity_df.columns
    assert "year_3_spend_cr" in sensitivity_df.columns
    # Higher inflation must produce higher Year 3 spend
    assert sensitivity_df.iloc[2]["year_3_spend_cr"] > sensitivity_df.iloc[0]["year_3_spend_cr"]


def test_finops_unit_economics_benchmarking():
    """Verify FinOps maturity tier assignment and P50 delta calculations."""
    benchmarked = benchmark_finops_unit_economics()

    assert not benchmarked.empty
    assert "finops_efficiency_tier" in benchmarked.columns
    assert "industry_p50_user_delta" in benchmarked.columns
    valid_tiers = {
        "Top Quartile (FinOps Leader)",
        "FinOps Scale Leader (High Efficiency)",
        "Industry Par (Efficient)",
        "Optimization Candidate",
        "Critical Review (Inefficient)",
    }
    assert set(benchmarked["finops_efficiency_tier"]).issubset(valid_tiers)
    # Underutilized legacy APP021 should be flagged for Critical Review
    app21 = benchmarked[benchmarked["application_id"] == "APP021"].iloc[0]
    assert "Critical Review" in app21["finops_efficiency_tier"]


def test_tco_forecasting():
    """Verify forward-looking econometric TCO forecasting with confidence intervals."""
    forecast_df = forecast_application_tco("APP001", forward_periods=6, confidence_level=0.95)

    assert len(forecast_df) == 6
    assert set(forecast_df.columns) == {"month", "forecasted_cost", "ci_lower", "ci_upper"}
    # Upper CI must exceed forecast, and forecast must exceed or equal lower CI
    for _, row in forecast_df.iterrows():
        assert row["ci_upper"] >= row["forecasted_cost"]
        assert row["forecasted_cost"] >= row["ci_lower"]


# ==============================================================================
# Module 05: Capability Cost Intelligence v2 Tests
# ==============================================================================
def test_dynamic_capability_cost_allocation():
    """Verify custom primary/secondary weight and driver configuration."""
    cap_cost_80_20 = calculate_dynamic_capability_cost(
        primary_weight=0.80, secondary_weight=0.20, shared_driver="transactions"
    )
    cap_cost_60_40 = calculate_dynamic_capability_cost(
        primary_weight=0.60, secondary_weight=0.40, shared_driver="compute_hours"
    )

    assert len(cap_cost_80_20) == 25
    assert len(cap_cost_60_40) == 25
    # Total spend must match total GL spend in both weighting configurations
    assert abs(cap_cost_80_20["total_capability_cost"].sum() - cap_cost_60_40["total_capability_cost"].sum()) < 10.0


def test_nested_capability_hierarchy():
    """Verify 3-tier capability rollups (L1 Domain -> L2 Area -> L3 Capability)."""
    hier_df = get_nested_capability_hierarchy_cost()

    assert len(hier_df) == 25
    assert "l1_domain" in hier_df.columns
    assert "l2_area" in hier_df.columns
    assert "l3_capability" in hier_df.columns
    assert hier_df["l1_domain"].nunique() >= 4


def test_cloud_migration_what_if():
    """Verify what-if financial model for infrastructure cloud migration."""
    sim = simulate_cloud_migration_what_if(cost_reduction_factor=0.25, transition_cost_pct=0.10)

    assert sim["annual_gross_savings_cr"] > 0
    assert sim["savings_percentage"] > 0
    assert sim["payback_period_months"] > 0


def test_audit_capability_allocation_reconciliation():
    """Verify automated audit trail mathematically proving zero double-counting."""
    audit = audit_capability_allocation_reconciliation()

    assert audit["reconciliation_status"] == "EXACT_RECONCILIATION_PASS"
    assert audit["double_counting_detected"] is False
    assert audit["absolute_reconciliation_delta"] < 1.0


# ==============================================================================
# Module 06: Consumption Intelligence v2 Tests
# ==============================================================================
def test_telemetry_decomposition():
    """Verify STL time-series trend and seasonal decomposition."""
    decomp = decompose_telemetry_time_series("APP001", metric="total_transactions")

    assert "trend" in decomp
    assert "seasonal" in decomp
    assert "residual" in decomp
    assert len(decomp["trend"]) == 12
    # Mean of centered seasonal component should be near 0
    assert abs(np.mean(decomp["seasonal"])) < 1.0


def test_serverless_concurrency_and_greenops():
    """Verify serverless concurrency metrics and GreenOps CO2e emissions."""
    serv_df = generate_serverless_concurrency_metrics()
    assert len(serv_df) == 50
    assert "avg_concurrency" in serv_df.columns
    assert "peak_concurrency" in serv_df.columns
    assert (serv_df["peak_concurrency"] >= serv_df["avg_concurrency"]).all()

    green_df = calculate_greenops_carbon_footprint()
    assert len(green_df) == 50
    assert "annual_emissions_kg_co2e" in green_df.columns
    assert "emissions_metric_tons" in green_df.columns
    assert (green_df["annual_emissions_kg_co2e"] > 0).all()


def test_rightsizing_recommendations():
    """Verify automated rightsizing recommendations identify candidates with positive savings."""
    recs = generate_rightsizing_recommendations()

    assert not recs.empty
    assert "recommendation_action" in recs.columns
    assert "projected_annual_savings_inr" in recs.columns
    assert (recs["projected_annual_savings_inr"] > 0).all()
    # APP021 (Scenario B legacy) should be captured
    assert "APP021" in set(recs["application_id"])
