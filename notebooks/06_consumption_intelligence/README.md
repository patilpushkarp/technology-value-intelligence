# Consumption Intelligence & Utilization Quadrants

**Purpose:** Evaluates operational telemetry across compute, storage, user activity, and transaction volumes. Constructs an objective median-split 2x2 matrix (Scale Anchors, Rationalization Review, Workhorses, Utility) to pinpoint applications with high spend and disproportionately low utilization.  
**Series Index:** Notebook 06 of 12  
**Baseline Reference:** [`./v1_baseline.ipynb`](v1_baseline.ipynb) | **Active Development:** [`./v2_development.ipynb`](v2_development.ipynb)

---

## 1. Executive Business Purpose
Evaluates operational telemetry across compute, storage, user activity, and transaction volumes. Constructs an objective median-split 2x2 matrix (Scale Anchors, Rationalization Review, Workhorses, Utility) to pinpoint applications with high spend and disproportionately low utilization.

### Core Methodology
Multi-dimensional telemetry aggregation; median-split quadrant classification; capacity headroom calculation; underutilization risk scoring.

---

## 2. Key Scenarios & Focus Areas
- Scenario A (Scale Anchor - APP001) vs Scenario B (Rationalization Candidate - APP021).

---

## 3. Data Dependencies & Artifacts

### Primary Inputs
- `DuckDB consumption_telemetry`
- `Application TCO figures`

### Primary Outputs
- `2x2 Utilization Quadrant scatter plot`
- `Underutilization alert list`
- `Capacity headroom metrics`
- Time-series trend and seasonal STL decomposition engine (`decompose_telemetry_time_series()`)
- Serverless concurrency, auto-scaling elasticity, and cold-start metrics (`generate_serverless_concurrency_metrics()`)
- GreenOps energy consumption and greenhouse gas carbon footprint model (`calculate_greenops_carbon_footprint()`)
- Automated infrastructure rightsizing opportunities and cost reduction projections (`generate_rightsizing_recommendations()`)

---

## 4. File Structure & Versioning

```text
06_consumption_intelligence/
├── README.md               # Purpose, documentation, and improvement roadmap (this file)
├── v1_baseline.ipynb       # Untouched baseline reference notebook (self-contained)
└── v2_development.ipynb    # Working copy for iterative improvements and code extensions
```

- **`v1_baseline.ipynb`**: Preserves the verified baseline implementation with dynamic root discovery.
- **`v2_development.ipynb`**: Active development notebook expanded with STL telemetry decomposition, serverless auto-scaling concurrency, GreenOps carbon emission footprints, and automated rightsizing recommendations.
- **Baseline Preservation:** `v1_baseline.ipynb` preserves the verified baseline implementation, while `v2_development.ipynb` is used for active evolution.

---

## 5. Iteration & Improvement Roadmap
- [x] Apply time-series STL / seasonal decomposition to telemetry metrics (`decompose_telemetry_time_series()`).
- [x] Integrate serverless concurrency and dynamic auto-scaling telemetry (`generate_serverless_concurrency_metrics()`).
- [x] Calculate GreenOps and estimated carbon footprint (CO2e) per application (`calculate_greenops_carbon_footprint()`).
- [x] Automate rightsizing recommendations with estimated cost reductions (`generate_rightsizing_recommendations()`).
- [ ] Connect cloud billing APIs directly to real-time spot instance interruption telemetry.
- [ ] Add multivariate vector autoregression (VAR) to forecast concurrent telemetry demand shocks.
