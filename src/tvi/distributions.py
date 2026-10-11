"""Parametric distribution sampler for Technology Value Intelligence (TVI).

Provides a configuration-driven wrapper around NumPy/SciPy statistical distributions
for Level 4 synthetic data generation. Ensures deterministic reproducibility, bounded
clipping, and domain-appropriate distribution shapes (Log-Normal, Gamma, Beta, Dirichlet,
Poisson, Truncated Normal) for financial, operational, and architectural metrics.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
import numpy as np
from numpy.random import Generator


@dataclass
class DistributionSpec:
    """Specification defining a statistical distribution and its boundaries."""
    family: str
    params: Dict[str, Any] = field(default_factory=dict)
    min_clip: Optional[float] = None
    max_clip: Optional[float] = None


class DistributionSampler:
    """Seeded parametric distribution sampler for TBM/ITFM synthetic data generation.

    All samples are generated using a dedicated NumPy Generator (`np.random.default_rng`),
    preserving reproducibility across runs while supporting configurable distribution
    families and constraints.
    """

    def __init__(
        self,
        rng: Optional[Generator] = None,
        dist_config: Optional[Dict[str, Any]] = None,
        seed: Optional[int] = 42,
    ):
        """Initialize the sampler.

        Args:
            rng: Optional NumPy random Generator. If not provided, initialized with `seed`.
            dist_config: Dictionary mapping distribution names to their configuration.
            seed: Seed for random number generation if `rng` is None.
        """
        self.rng = rng if rng is not None else np.random.default_rng(seed)
        self.specs: Dict[str, DistributionSpec] = self._parse_config(dist_config or {})

    def _parse_config(self, config: Dict[str, Any]) -> Dict[str, DistributionSpec]:
        """Parse configuration dictionary into structured DistributionSpec instances."""
        specs = {}
        for name, cfg in config.items():
            if isinstance(cfg, dict) and "family" in cfg:
                family = cfg["family"]
                min_clip = cfg.get("min_clip")
                max_clip = cfg.get("max_clip")
                params = {
                    k: v
                    for k, v in cfg.items()
                    if k not in ("family", "min_clip", "max_clip")
                }
                specs[name] = DistributionSpec(
                    family=family,
                    params=params,
                    min_clip=float(min_clip) if min_clip is not None else None,
                    max_clip=float(max_clip) if max_clip is not None else None,
                )
        return specs

    def has_distribution(self, name: str) -> bool:
        """Check if a named distribution is registered."""
        return name in self.specs

    def get_spec(self, name: str) -> Optional[DistributionSpec]:
        """Retrieve the specification for a named distribution."""
        return self.specs.get(name)

    def sample(self, name: str, size: int = 1, **overrides) -> np.ndarray:
        """Draw samples from a registered distribution with optional parameter overrides.

        Args:
            name: Key of the distribution registered in specs.
            size: Number of samples to generate.
            **overrides: Runtime parameter overrides (e.g. mu, sigma, scale, min_clip).

        Returns:
            np.ndarray: Generated sample array of shape (size,) or (size, dim).
        """
        if name not in self.specs:
            raise KeyError(f"Unknown distribution '{name}'. Available: {list(self.specs.keys())}")

        spec = self.specs[name]
        params = {**spec.params, **overrides}
        min_c = overrides.get("min_clip", spec.min_clip)
        max_c = overrides.get("max_clip", spec.max_clip)

        values = self._draw(spec.family, params, size)

        # Apply clipping constraints for scalar/univariate samples
        if values.ndim == 1:
            if min_c is not None:
                values = np.maximum(values, min_c)
            if max_c is not None:
                values = np.minimum(values, max_c)

        return values

    def sample_one(self, name: str, **overrides) -> float:
        """Draw a single scalar value from a registered distribution.

        Args:
            name: Key of the distribution.
            **overrides: Runtime parameter overrides.

        Returns:
            float: Single generated value.
        """
        samples = self.sample(name, size=1, **overrides)
        return float(samples[0])

    def sample_dirichlet(self, name: str = "cost_pool_split", **overrides) -> np.ndarray:
        """Draw a single vector of proportions summing to 1.0 from a Dirichlet distribution."""
        spec = self.specs.get(name)
        if spec is None or spec.family != "dirichlet":
            alpha = overrides.get("alpha", [9.0, 6.0, 5.0])
            draw = self.rng.dirichlet(alpha=alpha, size=1)
            return draw[0]
        params = {**spec.params, **overrides}
        draw = self.rng.dirichlet(alpha=params["alpha"], size=1)
        return draw[0]

    def _draw(self, family: str, params: Dict[str, Any], size: int) -> np.ndarray:
        """Internal dispatch to NumPy distribution methods."""
        fam = family.lower()

        if fam == "lognormal":
            mu = float(params.get("mu", params.get("mean", 0.0)))
            sigma = float(params.get("sigma", 1.0))
            return self.rng.lognormal(mean=mu, sigma=sigma, size=size)

        elif fam in ("normal", "gaussian"):
            mu = float(params.get("mu", params.get("loc", 0.0)))
            sigma = float(params.get("sigma", params.get("scale", 1.0)))
            return self.rng.normal(loc=mu, scale=sigma, size=size)

        elif fam == "gamma":
            shape = float(params.get("shape", params.get("k", 1.0)))
            scale = float(params.get("scale", params.get("theta", 1.0)))
            return self.rng.gamma(shape=shape, scale=scale, size=size)

        elif fam == "beta":
            a = float(params.get("a", params.get("alpha", 1.0)))
            b = float(params.get("b", params.get("beta", 1.0)))
            scale = float(params.get("scale", 1.0))
            raw = self.rng.beta(a=a, b=b, size=size)
            return raw * scale

        elif fam == "poisson":
            lam = float(params.get("lam", params.get("lambda_per_user", params.get("mu", 1.0))))
            return self.rng.poisson(lam=lam, size=size).astype(float)

        elif fam in ("negative_binomial", "nbinom"):
            n = float(params.get("n", 5.0))
            p = float(params.get("p", 0.5))
            return self.rng.negative_binomial(n=n, p=p, size=size).astype(float)

        elif fam == "dirichlet":
            alpha = params.get("alpha", [1.0, 1.0, 1.0])
            return self.rng.dirichlet(alpha=alpha, size=size)

        elif fam in ("truncnorm", "truncated_normal"):
            mu = float(params.get("mu", params.get("loc", 0.0)))
            sigma = float(params.get("sigma", params.get("scale", 1.0)))
            min_c = params.get("min_clip", -np.inf)
            max_c = params.get("max_clip", np.inf)
            raw = self.rng.normal(loc=mu, scale=sigma, size=size)
            return np.clip(raw, min_c, max_c)

        elif fam == "uniform":
            low = float(params.get("low", params.get("min", 0.0)))
            high = float(params.get("high", params.get("max", 1.0)))
            return self.rng.uniform(low=low, high=high, size=size)

        else:
            raise ValueError(f"Unsupported distribution family '{family}'.")
