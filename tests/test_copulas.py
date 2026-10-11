"""Unit tests for Level 6 Copula-Based Correlated Metric Generation."""

import numpy as np
import pytest
from scipy import stats

from tvi.config import load_config
from tvi.copulas import (
    CorrelatedMetricGenerator,
    nearest_correlation_matrix,
    spearman_to_pearson,
)
from tvi.distributions import DistributionSampler


@pytest.fixture
def copula_test_setup():
    """Setup sampler and correlation config for testing."""
    cfg = load_config()
    rng = np.random.default_rng(42)
    sampler = DistributionSampler(rng=rng, dist_config=cfg.data.distributions)
    corr_gen = CorrelatedMetricGenerator(
        rng=rng,
        correlation_config=cfg.data.correlations,
        sampler=sampler,
    )
    return cfg, sampler, corr_gen


def test_spearman_to_pearson_conversion():
    """Verify Greiner's formula converts Spearman correlations accurately."""
    rho_s = np.array([
        [1.0, 0.5],
        [0.5, 1.0]
    ])
    rho_p = spearman_to_pearson(rho_s)

    # 2 * sin(pi/6 * 0.5) = 2 * sin(pi/12) = 2 * 0.258819 ≈ 0.517638
    expected = 2.0 * np.sin(np.pi / 12.0)
    assert np.isclose(rho_p[0, 1], expected, atol=1e-5)
    assert rho_p[0, 0] == 1.0
    assert rho_p[1, 1] == 1.0


def test_nearest_correlation_matrix_psd():
    """Verify that projection produces a positive semi-definite matrix with unit diagonal."""
    # Construct non-PSD matrix
    non_psd = np.array([
        [1.0, 0.9, 0.9],
        [0.9, 1.0, -0.9],
        [0.9, -0.9, 1.0]
    ])
    # Initial smallest eigenvalue is negative
    assert np.min(np.linalg.eigvalsh(non_psd)) < 0.0

    psd = nearest_correlation_matrix(non_psd)
    eigvals = np.linalg.eigvalsh(psd)

    assert (eigvals >= 0.0).all()
    assert np.allclose(np.diag(psd), 1.0)


def test_copula_sampling_determinism(copula_test_setup):
    """Verify identical random seeds produce identical correlated datasets."""
    cfg, _, _ = copula_test_setup

    rng1 = np.random.default_rng(100)
    sampler1 = DistributionSampler(rng=rng1, dist_config=cfg.data.distributions)
    gen1 = CorrelatedMetricGenerator(rng=rng1, correlation_config=cfg.data.correlations, sampler=sampler1)

    rng2 = np.random.default_rng(100)
    sampler2 = DistributionSampler(rng=rng2, dist_config=cfg.data.distributions)
    gen2 = CorrelatedMetricGenerator(rng=rng2, correlation_config=cfg.data.correlations, sampler=sampler2)

    df1 = gen1.sample_dataframe(200)
    df2 = gen2.sample_dataframe(200)

    pd_testing = pytest.importorskip("pandas.testing")
    pd_testing.assert_frame_equal(df1, df2)


def test_rank_correlation_preservation(copula_test_setup):
    """Verify that sampled metrics preserve expected positive Spearman rank correlations."""
    _, _, corr_gen = copula_test_setup
    df = corr_gen.sample_dataframe(5000)

    # Check that users and transactions have strong positive rank correlation (target ~0.85)
    rho_users_txns, _ = stats.spearmanr(df["active_users"], df["transactions"])
    assert 0.70 < rho_users_txns < 0.95

    # Check that transactions and API calls correlate strongly (target ~0.90)
    rho_txns_api, _ = stats.spearmanr(df["transactions"], df["api_calls"])
    assert 0.75 < rho_txns_api < 0.98

    # Check that compute hours and transactions correlate (target ~0.80)
    rho_comp_txns, _ = stats.spearmanr(df["compute_hours"], df["transactions"])
    assert 0.60 < rho_comp_txns < 0.92

    # Check that tickets and users correlate positively (target ~0.60)
    rho_tix_users, _ = stats.spearmanr(df["tickets"], df["active_users"])
    assert 0.40 < rho_tix_users < 0.80


def test_marginal_distributions_preserved(copula_test_setup):
    """Verify marginal values remain strictly non-negative and respect bounds."""
    _, _, corr_gen = copula_test_setup
    df = corr_gen.sample_dataframe(1000)

    assert (df["active_users"] >= 20).all()
    assert (df["transactions"] >= 1000).all()
    assert (df["api_calls"] >= 2500).all()
    assert (df["compute_hours"] >= 50.0).all()
    assert (df["storage_gb"] >= 50.0).all()
    assert (df["tickets"] >= 1).all()


def test_sample_dataframe_returns_correct_shape(copula_test_setup):
    """Verify sample_dataframe returns the expected row count and column headers."""
    _, _, corr_gen = copula_test_setup
    df = corr_gen.sample_dataframe(150)

    assert len(df) == 150
    assert list(df.columns) == [
        "active_users", "transactions", "api_calls",
        "compute_hours", "storage_gb", "tickets"
    ]
