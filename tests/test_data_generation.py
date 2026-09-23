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
