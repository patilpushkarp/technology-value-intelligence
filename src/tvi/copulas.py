"""Gaussian copula-based correlated metric generator for Technology Value Intelligence (TVI).

Implements Level 6 synthetic data generation using Sklar's theorem:
1. Simulates joint dependency structures via a multivariate Gaussian copula parameterized
   by an expert-specified Spearman rank correlation matrix.
2. Converts Spearman rank correlations to Pearson correlations via Greiner's equality:
   rho_p = 2 * sin(pi / 6 * rho_s).
3. Projects the correlation matrix to the nearest positive semi-definite (PSD) matrix.
4. Performs Probability Integral Transform to uniform space U in [0, 1].
5. Applies inverse CDF (percent-point functions) of arbitrary marginal distributions
   (Log-Normal, Gamma, Poisson) to retain realistic statistical shapes while preserving
   cross-metric dependencies.
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from numpy.random import Generator
from scipy import stats

from tvi.distributions import DistributionSampler, DistributionSpec


def spearman_to_pearson(spearman_rho: np.ndarray) -> np.ndarray:
    """Convert Spearman rank correlation matrix to Pearson correlation for Gaussian copula.

    Based on Pearson-Greiner relation for bivariate normal distributions:
    rho_pearson = 2 * sin(pi / 6 * rho_spearman).

    Args:
        spearman_rho: Symmetric square matrix of Spearman rank correlations.

    Returns:
        np.ndarray: Approximated Pearson correlation matrix.
    """
    rho_p = 2.0 * np.sin((np.pi / 6.0) * spearman_rho)
    np.fill_diagonal(rho_p, 1.0)
    return np.clip(rho_p, -1.0, 1.0)


def nearest_correlation_matrix(matrix: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    """Project a symmetric matrix to the nearest positive semi-definite correlation matrix.

    Clips negative eigenvalues and re-normalizes unit diagonals.

    Args:
        matrix: Symmetric square matrix.
        eps: Minimum allowable eigenvalue.

    Returns:
        np.ndarray: Positive semi-definite correlation matrix with unit diagonal.
    """
    # Symmetrize
    sym = (matrix + matrix.T) / 2.0

    # Eigenvalue decomposition
    eigvals, eigvecs = np.linalg.eigh(sym)

    # Clip eigenvalues to ensure positive definiteness
    clipped_eigvals = np.maximum(eigvals, eps)

    # Reconstruct matrix
    reconstructed = eigvecs @ np.diag(clipped_eigvals) @ eigvecs.T

    # Normalize diagonal to 1.0
    inv_sqrt_diag = 1.0 / np.sqrt(np.diag(reconstructed))
    corr = reconstructed * np.outer(inv_sqrt_diag, inv_sqrt_diag)
    np.fill_diagonal(corr, 1.0)
    return corr


class CorrelatedMetricGenerator:
    """Generates correlated operational and financial metrics using a Gaussian Copula.

    Maintains exact marginal distributions configured in `DistributionSampler` while
    inducing prescribed rank correlations across consumption metrics.
    """

    def __init__(
        self,
        rng: Optional[Generator] = None,
        correlation_config: Optional[Dict[str, Any]] = None,
        sampler: Optional[DistributionSampler] = None,
        seed: Optional[int] = 42,
    ):
        """Initialize the correlated metric generator.

        Args:
            rng: Optional NumPy random Generator.
            correlation_config: Configuration dict containing `consumption_metrics` specs.
            sampler: Initialized DistributionSampler instance providing marginal distributions.
            seed: Fallback random seed if `rng` is None.
        """
        self.rng = rng if rng is not None else np.random.default_rng(seed)
        self.sampler = sampler or DistributionSampler(rng=self.rng)

        corr_cfg = (correlation_config or {}).get("consumption_metrics", {})
        self.variables: List[str] = corr_cfg.get(
            "variables",
            ["active_users", "transactions", "api_calls", "compute_hours", "storage_gb", "tickets"],
        )
        raw_matrix = corr_cfg.get("matrix")

        if raw_matrix is not None and len(raw_matrix) == len(self.variables):
            spearman_mat = np.array(raw_matrix, dtype=float)
            pearson_mat = spearman_to_pearson(spearman_mat)
            self.corr_matrix = nearest_correlation_matrix(pearson_mat)
        else:
            # Default fallback correlation matrix
            n = len(self.variables)
            self.corr_matrix = np.eye(n)

        # Mapping between variable names and distribution specifications
        self.marginal_map: Dict[str, str] = {
            "active_users": "active_users",
            "transactions": "transactions",
            "api_calls": "api_calls",
            "compute_hours": "compute_hours",
            "storage_gb": "storage_gb",
            "tickets": "ticket_rate",
        }

    def sample_correlated(self, n_samples: int) -> Dict[str, np.ndarray]:
        """Generate n_samples of jointly-correlated consumption metrics.

        Args:
            n_samples: Number of joint observations to generate.

        Returns:
            Dict[str, np.ndarray]: Dictionary mapping variable names to their sampled arrays.
        """
        if n_samples <= 0:
            return {var: np.array([]) for var in self.variables}

        k = len(self.variables)
        mean_vector = np.zeros(k)

        # Step 1: Draw standard normal vectors with target correlation
        z = self.rng.multivariate_normal(mean=mean_vector, cov=self.corr_matrix, size=n_samples)

        # Step 2: Probability Integral Transform to uniform space [0, 1]
        u = stats.norm.cdf(z)
        # Numerical guard: avoid exact 0.0 and 1.0 for inverse CDF stability
        u = np.clip(u, 1e-7, 1.0 - 1e-7)

        # Step 3: Inverse transform sampling (PPF) using marginal distribution specs
        results: Dict[str, np.ndarray] = {}

        for idx, var_name in enumerate(self.variables):
            u_var = u[:, idx]
            dist_key = self.marginal_map.get(var_name, var_name)
            spec = self.sampler.get_spec(dist_key)

            if spec is None:
                # Fallback: scale uniform to standard variable range
                results[var_name] = u_var
                continue

            values = self._apply_inverse_marginal(spec, u_var)

            # Apply clipping limits if specified
            if spec.min_clip is not None:
                values = np.maximum(values, spec.min_clip)
            if spec.max_clip is not None:
                values = np.minimum(values, spec.max_clip)

            # Integer casting for discrete count variables
            if var_name in ("active_users", "transactions", "api_calls", "tickets"):
                results[var_name] = np.maximum(1, np.round(values)).astype(int)
            else:
                results[var_name] = np.round(values, 1)

        return results

    def sample_dataframe(self, n_samples: int) -> pd.DataFrame:
        """Convenience method returning sampled correlated metrics as a pandas DataFrame."""
        return pd.DataFrame(self.sample_correlated(n_samples))

    def _apply_inverse_marginal(
        self, spec: DistributionSpec, uniform_samples: np.ndarray
    ) -> np.ndarray:
        """Evaluate the quantile function (PPF) for a given marginal specification."""
        p = spec.params
        fam = spec.family.lower()

        if fam == "lognormal":
            mu = float(p.get("mu", p.get("mean", 0.0)))
            sigma = float(p.get("sigma", 1.0))
            return stats.lognorm.ppf(uniform_samples, s=sigma, scale=np.exp(mu))

        elif fam == "gamma":
            shape = float(p.get("shape", p.get("k", 1.0)))
            scale = float(p.get("scale", p.get("theta", 1.0)))
            return stats.gamma.ppf(uniform_samples, a=shape, scale=scale)

        elif fam == "poisson":
            lam = float(p.get("lam", p.get("lambda_per_user", p.get("mu", 15.0))))
            # For Poisson, multiply by scale if lambda_per_user is small (e.g. rate per user)
            if lam < 1.0:
                lam = 15.0  # typical base support tickets
            return stats.poisson.ppf(uniform_samples, mu=lam).astype(float)

        elif fam in ("normal", "gaussian"):
            mu = float(p.get("mu", p.get("loc", 0.0)))
            sigma = float(p.get("sigma", p.get("scale", 1.0)))
            return stats.norm.ppf(uniform_samples, loc=mu, scale=sigma)

        elif fam == "beta":
            a = float(p.get("a", 1.0))
            b = float(p.get("b", 1.0))
            scale = float(p.get("scale", 1.0))
            return stats.beta.ppf(uniform_samples, a=a, b=b) * scale

        elif fam == "uniform":
            low = float(p.get("low", 0.0))
            high = float(p.get("high", 1.0))
            return low + uniform_samples * (high - low)

        else:
            return uniform_samples
