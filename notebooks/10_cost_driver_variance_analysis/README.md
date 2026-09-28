# Cost Driver & Financial Variance Analysis

**Purpose:** Deconstructs Month-over-Month (MoM) spend shifts into rate variances vs. volume/consumption variances. Mathematically distinguishes healthy operational scale (e.g. APP014 surge matching +180% transaction volume) from unbacked spend anomalies (e.g. APP022 rate spike with flat usage).  
**Series Index:** Notebook 10 of 12  
**Baseline Reference:** [`./v1_baseline.ipynb`](v1_baseline.ipynb) | **Active Development:** [`./v2_development.ipynb`](v2_development.ipynb)

---

## 1. Executive Business Purpose
Deconstructs Month-over-Month (MoM) spend shifts into rate variances vs. volume/consumption variances. Mathematically distinguishes healthy operational scale (e.g. APP014 surge matching +180% transaction volume) from unbacked spend anomalies (e.g. APP022 rate spike with flat usage).

### Core Methodology
Two-factor financial variance decomposition (Rate Variance + Volume Variance); percentage shift attribution; continuous statistical anomaly detection (rolling Z-scores + Isolation Forests); contractual vendor SLA breach penalty calculations; forward-looking trend-adjusted budget variance forecasting; automated FinOps ticket generation.

---

## 2. Key Scenarios & Focus Areas
- **Scenario G:** Elastic Scale (`APP014` - Cloud Payment Microhub) where spend surged +171% in August matching a +180% surge in transaction volume.
- **Scenario H:** Unbacked Cost Anomaly (`APP022` - Batch Billing Engine v2) where spend surged +₹38L (+68%) while transactions and user counts remained flat (-1.2%).
- **Isolation Forest & Statistical Z-Scores:** Multidimensional outlier detection separating usage-backed surges from operational waste.
- **Vendor SLA Penalties:** Assessing contractual service penalty credits against infrastructure vendors for unauthorized or unannounced rate hikes.

---

## 3. Data Dependencies & Artifacts

### Primary Inputs
- `cost_records` and `consumption_records` in DuckDB
- `technologies` and `vendors` tables

### Primary Outputs
- `Variance decomposition tables`
- `Rate vs Volume breakdown charts`
- `FinOps anomaly detection register` (`detect_cost_anomalies()`)
- `Assessed vendor SLA breach credits` (`calculate_sla_breach_penalties()`)
- `Forward-looking budget variance forecast` (`forecast_budget_variance()`)
- `Structured FinOps ticket payloads` (`generate_finops_anomaly_tickets()`)

---

## 4. File Structure & Versioning

```text
10_cost_driver_variance_analysis/
├── README.md               # Purpose, documentation, and improvement roadmap (this file)
├── v1_baseline.ipynb       # Untouched baseline reference notebook (self-contained)
└── v2_development.ipynb    # Working copy for iterative improvements and code extensions
```

- **`v1_baseline.ipynb`**: Preserves the verified baseline implementation with dynamic root discovery.
- **`v2_development.ipynb`**: The active development canvas where new algorithms, visualizations, and modular extensions can be developed without touching the baseline.
- **Baseline Preservation:** `v1_baseline.ipynb` preserves the verified baseline implementation, while `v2_development.ipynb` is used for active evolution.

---

## 5. Iteration & Improvement Roadmap
- [x] Implement continuous statistical anomaly detection using rolling Z-scores and Isolation Forests (`detect_cost_anomalies()`).
- [x] Automate vendor contract SLA penalty calculation for unbacked rate spikes (`calculate_sla_breach_penalties()`).
- [x] Build multi-period forward-looking budget variance forecasting models (`forecast_budget_variance()`).
- [x] Generate automated FinOps investigation ticket payloads (`generate_finops_anomaly_tickets()`).
