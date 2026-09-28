# Investment & Technology Value Realization (TVR)

**Purpose:** Connects capital investments (PRJ001–PRJ040) to application modernizations and tracked business KPIs. Calculates budget variance, audits post-delivery expected vs. realized benefit gaps (highlighting success in PRJ003 and underperformance in PRJ014), and enforces association vs. causality guardrails.  
**Series Index:** Notebook 09 of 12  
**Baseline Reference:** [`./v1_baseline.ipynb`](v1_baseline.ipynb) | **Active Development:** [`./v2_development.ipynb`](v2_development.ipynb)

---

## 1. Executive Business Purpose
Connects capital investments (PRJ001–PRJ040) to application modernizations and tracked business KPIs. Calculates budget variance, audits post-delivery expected vs. realized benefit gaps (highlighting success in PRJ003 and underperformance in PRJ014), and enforces association vs. causality guardrails.

### Core Methodology
Capital project budget variance analysis; expected vs realized benefit gap calculations; monthly KPI progression tracking; strict association vs causality guardrails; discounted cash flow valuation (NPV, IRR, discounted payback); econometric Difference-in-Differences (DiD) evaluation; multi-dimensional portfolio stage-gate health scorecards; capability maturity progression modeling.

---

## 2. Key Scenarios & Focus Areas
- **Scenario E:** High-Performing Project `PRJ003` (Real-Time Payment Modernization - 108% benefit realization, high NPV).
- **Scenario F:** Transformation Gap Project `PRJ014` (Global Legacy CRM Consolidation - ₹23 Cr value gap, sub-hurdle return).
- **Difference-in-Differences Evaluation:** Econometric comparison of `APP007` (modernized by `PRJ003`) against peer application `APP019` measuring observed unit cost divergence.
- **Stage-Gate Health Cards:** Automated governance ratings (Green/Amber/Red) identifying projects requiring steering committee intervention.
- **Capability Maturity Uplift:** Measuring business capability level progression (1.0 to 5.0) and transformation capital efficiency ($\text{₹}/\Delta\text{Maturity}$).

---

## 3. Data Dependencies & Artifacts

### Primary Inputs
- `DuckDB projects, benefits, rel_benefit_kpi, kpis, consumption_records, cost_records`
- `rel_project_capability`, `business_capabilities`

### Primary Outputs
- `Project Budget Variance table`
- `Benefit Realization Ratio (BRR) ranking`
- `KPI progression charts`
- `Discounted cash flow financial metrics` (`calculate_investment_financial_metrics()`)
- `Econometric DiD dossiers` (`estimate_causal_impact_did()`)
- `Stage-gate governance scorecards` (`generate_stage_gate_health_scorecard()`)
- `Capability maturity uplift tracking` (`evaluate_capability_maturity_progression()`)

---

## 4. File Structure & Versioning

```text
09_investment_benefit_realization/
├── README.md               # Purpose, documentation, and improvement roadmap (this file)
├── v1_baseline.ipynb       # Untouched baseline reference notebook (self-contained)
└── v2_development.ipynb    # Working copy for iterative improvements and code extensions
```

- **`v1_baseline.ipynb`**: Preserves the verified baseline implementation with dynamic root discovery.
- **`v2_development.ipynb`**: The active development canvas where new algorithms, visualizations, and modular extensions can be developed without touching the baseline.
- **Baseline Preservation:** `v1_baseline.ipynb` preserves the verified baseline implementation, while `v2_development.ipynb` is used for active evolution.

---

## 5. Iteration & Improvement Roadmap
- [x] Calculate post-implementation Net Present Value (NPV) and Internal Rate of Return (IRR) (`calculate_investment_financial_metrics()`).
- [x] Implement econometric causal inference (Difference-in-Differences / Synthetic Controls) (`estimate_causal_impact_did()`).
- [x] Build automated portfolio stage-gate health cards (`generate_stage_gate_health_scorecard()`).
- [x] Link project deliverables directly to capability maturity score increases (`evaluate_capability_maturity_progression()`).
