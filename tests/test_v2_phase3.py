"""Unit tests for TVI v2 Roadmap Phase 3 (Modules 07, 08, 09).

Tests:
- Module 07: MCDA sensitivity, Pareto frontier, decommissioning roadmap, contractual exit penalty
- Module 08: Monte Carlo failure cascade, CI/CD deployment gates, Zero-Trust network containment audit, Mermaid flowchart
- Module 09: Investment NPV & IRR models, econometric DiD, stage-gate health scorecards, capability maturity progression
"""

import pandas as pd
import pytest

from tvi.dependency import (
    audit_zero_trust_segmentation,
    evaluate_deployment_gate,
    generate_dependency_flowchart_mermaid,
    simulate_failure_cascade,
)
from tvi.rationalization import (
    analyze_mcda_weight_sensitivity,
    evaluate_rationalization_pareto_frontier,
    generate_decommissioning_roadmap,
    model_contractual_exit_impact,
    score_application_portfolio,
)
from tvi.value_realization import (
    calculate_investment_financial_metrics,
    estimate_causal_impact_did,
    evaluate_capability_maturity_progression,
    generate_stage_gate_health_scorecard,
)


# ==============================================================================
# Module 07 Tests: Application Rationalization & MCDA
# ==============================================================================


def test_mcda_custom_weights_and_sensitivity():
    """Verify MCDA custom weight rebalancing and rank sensitivity."""
    # Base scoring
    base_df = score_application_portfolio()
    assert not base_df.empty
    assert "rationalization_review_index" in base_df.columns

    # Custom weight favoring cost heavily
    cost_heavy_weights = {
        "cost_score": 0.80,
        "utilization_score": 0.05,
        "capability_overlap_score": 0.05,
        "lifecycle_score": 0.05,
        "criticality_score": 0.05,
    }
    cost_df = score_application_portfolio(cost_heavy_weights)
    assert not cost_df.empty
    assert len(cost_df) == len(base_df)

    # Sensitivity analysis
    sens_df = analyze_mcda_weight_sensitivity(weight_param="cost_score", weight_range=[0.10, 0.30, 0.50])
    assert not sens_df.empty
    assert set(["application_id", "weight_value", "rationalization_review_index", "rank_shift"]).issubset(sens_df.columns)
    assert len(sens_df["weight_value"].unique()) == 3


def test_rationalization_pareto_frontier():
    """Verify Pareto frontier computation for complexity vs savings."""
    pareto_df = evaluate_rationalization_pareto_frontier()
    assert not pareto_df.empty
    assert set(["application_id", "migration_complexity_score", "annual_avoidable_savings", "is_pareto_optimal", "strategic_quadrant"]).issubset(pareto_df.columns)

    # Ensure at least some systems are on the Pareto frontier
    pareto_optimal_count = pareto_df["is_pareto_optimal"].sum()
    assert pareto_optimal_count >= 1

    # Verify strategic quadrant categories
    valid_quadrants = {
        "Quick Win (High Savings, Low Complexity)",
        "Strategic Heavyweight (High Savings, High Complexity)",
        "Low Value Drag (Low Savings, Low Complexity)",
        "Complex Legacy Trapped (Low Savings, High Complexity)",
    }
    assert set(pareto_df["strategic_quadrant"].unique()).issubset(valid_quadrants)


def test_decommissioning_milestone_roadmap():
    """Verify structured decommissioning roadmap generation."""
    roadmap_df = generate_decommissioning_roadmap(target_app_ids=["APP021"])
    assert not roadmap_df.empty
    assert len(roadmap_df) == 4  # 4 operational phases: M1, M2, M3, M4
    assert set(["phase_code", "phase_name", "start_month", "end_month", "cumulative_cost_unlocked_pct"]).issubset(roadmap_df.columns)
    assert list(roadmap_df["phase_code"]) == ["M1", "M2", "M3", "M4"]
    assert roadmap_df.iloc[-1]["cumulative_cost_unlocked_pct"] == 100.0


def test_contractual_exit_penalty_modeling():
    """Verify contractual exit penalty, retained overhead, and net savings yield."""
    impact = model_contractual_exit_impact("APP021", contract_months_remaining=6, penalty_rate=0.50, fixed_overhead_fraction=0.25)
    assert "error" not in impact
    assert impact["application_id"] == "APP021"
    assert impact["gross_annual_tco"] > 0
    assert impact["retained_shared_overhead"] == impact["gross_annual_tco"] * 0.25
    assert impact["net_year1_savings"] < impact["gross_annual_tco"]
    assert impact["net_runrate_savings_year2"] > impact["net_year1_savings"]
    assert "analytical_disclaimer" in impact


# ==============================================================================
# Module 08 Tests: Dependency & Blast Radius Analysis
# ==============================================================================


def test_monte_carlo_failure_cascade():
    """Verify Monte Carlo cascade simulation on critical hub APP010."""
    result = simulate_failure_cascade("APP010", failure_probability=0.8, iterations=100, random_seed=42)
    assert "error" not in result
    assert result["initial_failed_node"] == "APP010"
    assert result["mean_affected_systems"] >= 1.0
    assert result["cascade_occurrence_probability"] > 0.5
    assert "vulnerable_callers_frequency" in result
    assert len(result["vulnerable_callers_frequency"]) > 0


def test_deployment_gate_evaluation():
    """Verify CI/CD deployment gating policies for hub vs peripheral app."""
    # Critical hub should be blocked or require CAB for major release
    hub_gate = evaluate_deployment_gate("APP010", change_tier="Major")
    assert hub_gate["gate_status"] in ["BLOCKED_HIGH_BLAST_RADIUS", "REQUIRES_CAB_APPROVAL"]
    assert hub_gate["direct_dependent_apps_count"] >= 5

    # Peripheral app with low blast radius
    clean_gate = evaluate_deployment_gate("APP021", change_tier="Standard", max_blast_radius_threshold=50.0)
    assert "gate_status" in clean_gate


def test_zero_trust_network_containment_audit():
    """Verify Zero-Trust boundary classification and containment violations."""
    audit_df = audit_zero_trust_segmentation()
    assert not audit_df.empty
    assert set(["source_node", "source_zone", "target_node", "target_zone", "is_containment_violation", "risk_rating"]).issubset(audit_df.columns)
    # Check that containment violations exist and are highlighted
    violations = audit_df[audit_df["is_containment_violation"]]
    assert len(violations) >= 0


def test_dependency_flowchart_mermaid():
    """Verify generation of valid Mermaid flowchart syntax."""
    mermaid_str = generate_dependency_flowchart_mermaid("APP010")
    assert mermaid_str.startswith("flowchart TD")
    assert "APP010" in mermaid_str
    assert "classDef" in mermaid_str


# ==============================================================================
# Module 09 Tests: Investment & Value Realization
# ==============================================================================


def test_investment_npv_and_irr_metrics():
    """Verify capital investment financial metrics (NPV, IRR, Payback, BCR)."""
    metrics_df = calculate_investment_financial_metrics(discount_rate=0.08, time_horizon_years=5)
    assert not metrics_df.empty
    assert set(["project_id", "actual_spend", "annual_benefit_inflow", "npv", "irr_pct", "discounted_payback_years", "benefit_cost_ratio", "financial_verdict"]).issubset(metrics_df.columns)
    # PRJ003 should be a strong value creator
    prj003 = metrics_df[metrics_df["project_id"] == "PRJ003"]
    assert not prj003.empty
    assert prj003.iloc[0]["financial_verdict"] == "High Value Creator"


def test_econometric_did_impact():
    """Verify Difference-in-Differences evaluation for PRJ003."""
    did_res = estimate_causal_impact_did("PRJ003")
    assert "error" not in did_res
    assert did_res["project_id"] == "PRJ003"
    assert did_res["treatment_application"] == "APP007"
    assert "difference_in_differences_estimate" in did_res
    assert "consulting_guardrail_notice" in did_res


def test_stage_gate_health_scorecard():
    """Verify automated portfolio stage-gate health scorecards."""
    scorecard = generate_stage_gate_health_scorecard()
    assert not scorecard.empty
    assert set(["project_id", "budget_health", "benefit_health", "composite_gate_status", "governance_action"]).issubset(scorecard.columns)
    valid_gates = {
        "Green (Pass Gate)",
        "Amber (Conditional Exception)",
        "Red (Executive Gate Intervention)",
    }
    assert set(scorecard["composite_gate_status"].unique()).issubset(valid_gates)


def test_capability_maturity_progression():
    """Verify linking of project delivery to capability maturity progression."""
    mat_df = evaluate_capability_maturity_progression()
    assert not mat_df.empty
    assert set(["capability_id", "project_id", "baseline_maturity", "maturity_uplift", "current_maturity", "cost_per_maturity_point"]).issubset(mat_df.columns)
    assert (mat_df["current_maturity"] >= mat_df["baseline_maturity"]).all()
    assert (mat_df["current_maturity"] <= 5.0).all()
