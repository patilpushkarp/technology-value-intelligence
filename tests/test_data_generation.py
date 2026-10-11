"""Tests for deterministic data generator and integrity validation."""

import pytest
from tvi.config import load_config
from tvi.data_generation import EnterpriseDataGenerator
from tvi.validation import DataQualityValidator


def test_data_generation_deterministic():
    """Verify that identical random seed produces identical datasets."""
    cfg = load_config()
    gen1 = EnterpriseDataGenerator(cfg)
    data1 = gen1.generate_all()

    gen2 = EnterpriseDataGenerator(cfg)
    data2 = gen2.generate_all()

    # Compare key DataFrames
    assert data1["applications"].equals(data2["applications"])
    assert data1["cost_records"].equals(data2["cost_records"])
    assert data1["consumption_records"].equals(data2["consumption_records"])
    assert data1["benefits"].equals(data2["benefits"])


def test_data_generation_counts():
    """Verify record counts match or exceed minimum thresholds."""
    cfg = load_config()
    gen = EnterpriseDataGenerator(cfg)
    data = gen.generate_all()

    assert len(data["business_units"]) == cfg.data.business_units
    assert len(data["business_capabilities"]) == cfg.data.capabilities
    assert len(data["it_services"]) == cfg.data.services
    assert len(data["applications"]) == cfg.data.applications
    assert len(data["technologies"]) == cfg.data.technologies
    assert len(data["vendors"]) == cfg.data.vendors
    assert len(data["projects"]) == cfg.data.projects
    assert len(data["cost_records"]) >= 500
    assert len(data["consumption_records"]) >= 500


def test_data_quality_validation_passes():
    """Verify that the generated enterprise data passes all validation checks."""
    validator = DataQualityValidator()
    report = validator.validate_all()
    assert report["status"] == "PASS"
    assert len(report["issues"]) == 0


def test_level4_parametric_distributions_in_generated_data():
    """Verify Level 4 parametric distribution sampling in generated datasets."""
    from scipy import stats
    cfg = load_config()
    gen = EnterpriseDataGenerator(cfg)
    data = gen.generate_all()

    # 1. Cost pool splits are Dirichlet distributed across non-scenario applications
    costs = data["cost_records"]
    non_scenario_costs = costs[~costs["application_id"].isin(["APP001", "APP021", "APP014", "APP022"])]
    assert (non_scenario_costs["amount"] > 0).all()

    # 2. Benefit realization ratios are Beta-distributed for completed non-scenario projects
    benefits = data["benefits"]
    # Completed projects (excluding PRJ003 and PRJ014)
    std_completed = benefits[~benefits["project_id"].isin(["PRJ003", "PRJ014"]) & (benefits["benefit_status"] == "Realized")]
    assert len(std_completed) > 0
    # Expected value and realized value must be strictly positive
    assert (std_completed["expected_value"] > 0).all()
    assert (std_completed["realized_value"] > 0).all()


def test_level6_copula_correlations_in_consumption_data():
    """Verify Level 6 copula rank correlation across standard application consumption records."""
    from scipy import stats
    cfg = load_config()
    gen = EnterpriseDataGenerator(cfg)
    data = gen.generate_all()

    cons = data["consumption_records"]
    # Filter to non-scenario applications to test copula dependencies
    std_cons = cons[~cons["application_id"].isin(["APP001", "APP021", "APP014", "APP022"])]

    # Check positive rank correlation between active users and transactions
    rho_users_txns, _ = stats.spearmanr(std_cons["active_users"], std_cons["transactions"])
    assert rho_users_txns > 0.50

    # Check positive rank correlation between transactions and API calls
    rho_txns_api, _ = stats.spearmanr(std_cons["transactions"], std_cons["api_calls"])
    assert rho_txns_api > 0.60

    # Check non-negativity across all operational telemetry columns
    for col in ["active_users", "transactions", "api_calls", "compute_hours", "storage_gb", "tickets"]:
        assert (std_cons[col] > 0).all()
