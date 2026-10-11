"""Unit tests for Level 4 Parametric Distribution Sampler."""

import numpy as np
import pytest

from tvi.config import load_config
from tvi.distributions import DistributionSampler, DistributionSpec


@pytest.fixture
def sample_config():
    """Sample distribution configuration for testing."""
    return {
        "annual_license_cost": {
            "family": "lognormal",
            "mu": 16.2,
            "sigma": 0.75,
            "min_clip": 3000000.0,
            "max_clip": 40000000.0,
        },
        "monthly_cost_jitter": {
            "family": "normal",
            "mu": 1.0,
            "sigma": 0.03,
            "min_clip": 0.92,
            "max_clip": 1.08,
        },
        "cost_pool_split": {
            "family": "dirichlet",
            "alpha": [9.0, 6.0, 5.0],
        },
        "active_users": {
            "family": "lognormal",
            "mu": 6.5,
            "sigma": 0.9,
            "min_clip": 20.0,
            "max_clip": 10000.0,
        },
        "compute_hours": {
            "family": "gamma",
            "shape": 3.0,
            "scale": 250.0,
            "min_clip": 50.0,
            "max_clip": 5000.0,
        },
        "benefit_realization_completed": {
            "family": "beta",
            "a": 8.0,
            "b": 2.5,
            "scale": 1.15,
        },
        "ticket_rate": {
            "family": "poisson",
            "lambda_per_user": 0.015,
            "min_clip": 1.0,
        },
        "shared_infra_cost": {
            "family": "truncnorm",
            "mu": 2200000.0,
            "sigma": 400000.0,
            "min_clip": 1200000.0,
            "max_clip": 3500000.0,
        },
    }


def test_sampler_deterministic(sample_config):
    """Verify that identical random seeds produce identical samples."""
    s1 = DistributionSampler(rng=np.random.default_rng(42), dist_config=sample_config)
    s2 = DistributionSampler(rng=np.random.default_rng(42), dist_config=sample_config)

    samples1 = s1.sample("active_users", size=100)
    samples2 = s2.sample("active_users", size=100)

    np.testing.assert_array_equal(samples1, samples2)


def test_clipping_bounds_respected(sample_config):
    """Verify min_clip and max_clip bounds are strictly enforced."""
    sampler = DistributionSampler(rng=np.random.default_rng(42), dist_config=sample_config)
    samples = sampler.sample("annual_license_cost", size=5000)

    assert (samples >= 3000000.0).all()
    assert (samples <= 40000000.0).all()


def test_dirichlet_proportions_sum_to_one(sample_config):
    """Verify Dirichlet draws sum to 1.0 across all components."""
    sampler = DistributionSampler(rng=np.random.default_rng(42), dist_config=sample_config)
    splits = sampler.sample_dirichlet("cost_pool_split")

    assert len(splits) == 3
    assert np.isclose(np.sum(splits), 1.0, atol=1e-7)
    assert (splits > 0.0).all()


def test_beta_bounded_range(sample_config):
    """Verify Beta distribution scales properly to target maximum."""
    sampler = DistributionSampler(rng=np.random.default_rng(42), dist_config=sample_config)
    samples = sampler.sample("benefit_realization_completed", size=1000)

    assert (samples >= 0.0).all()
    assert (samples <= 1.15).all()
    # Mean of Beta(8, 2.5) * 1.15 is approximately (8 / 10.5) * 1.15 ≈ 0.876
    assert 0.80 < np.mean(samples) < 0.95


def test_lognormal_skewness(sample_config):
    """Verify Log-Normal distribution produces realistic right-skewed values."""
    sampler = DistributionSampler(rng=np.random.default_rng(42), dist_config=sample_config)
    samples = sampler.sample("active_users", size=10000)

    # Right skew implies mean > median
    assert np.mean(samples) > np.median(samples)
    # Median should be close to exp(mu) = exp(6.5) ≈ 665
    assert 550 < np.median(samples) < 800


def test_gamma_positive_and_range(sample_config):
    """Verify Gamma distribution generates strictly positive values."""
    sampler = DistributionSampler(rng=np.random.default_rng(42), dist_config=sample_config)
    samples = sampler.sample("compute_hours", size=5000)

    assert (samples >= 50.0).all()
    assert (samples <= 5000.0).all()
    # Expected value: shape * scale = 3 * 250 = 750
    assert 650 < np.mean(samples) < 850


def test_sample_one_scalar(sample_config):
    """Verify sample_one returns a native float."""
    sampler = DistributionSampler(rng=np.random.default_rng(42), dist_config=sample_config)
    val = sampler.sample_one("monthly_cost_jitter")

    assert isinstance(val, float)
    assert 0.92 <= val <= 1.08


def test_unknown_distribution_raises(sample_config):
    """Verify querying an unregistered distribution raises KeyError."""
    sampler = DistributionSampler(rng=np.random.default_rng(42), dist_config=sample_config)
    with pytest.raises(KeyError):
        sampler.sample("non_existent_distribution")


def test_sampler_integration_with_loaded_config():
    """Verify sampler operates seamlessly with master config.yaml."""
    cfg = load_config()
    sampler = DistributionSampler(rng=np.random.default_rng(cfg.project.random_seed), dist_config=cfg.data.distributions)

    assert sampler.has_distribution("annual_license_cost")
    assert sampler.has_distribution("cost_pool_split")
    assert sampler.has_distribution("active_users")
    assert sampler.has_distribution("shared_infra_cost")

    val = sampler.sample_one("shared_infra_cost")
    assert 1200000.0 <= val <= 3500000.0
