# Enterprise Synthetic Data Generation & Scenario Injection

**Purpose:** Generates deterministic synthetic enterprise architecture topologies, relational master data, general ledger cost records, and operational telemetry across 12 monthly periods (FY2024). Injects 8 controlled business scenarios (A–H) to benchmark and stress-test TVI analytics.  
**Series Index:** Notebook 01 of 12  
**Baseline Reference:** [`./v1_baseline.ipynb`](v1_baseline.ipynb) | **Active Development:** [`./v2_development.ipynb`](v2_development.ipynb)

---

## 1. Executive Business Purpose
Generates deterministic synthetic enterprise architecture topologies, relational master data, general ledger cost records, and operational telemetry across 12 monthly periods (FY2024). Injects 8 controlled business scenarios (A–H) to benchmark and stress-test TVI analytics.

### Core Methodology
Mathematical pseudorandom generation with seed=42; multi-entity relational schema synthesis; deterministic scenario embedding; referential integrity auditing.

---

## 2. Key Scenarios & Focus Areas
- **Scenario A (Scale Anchor - APP001):** High TCO (> ₹15 Cr), 8,500+ users, 6.5M txns, ultra-low unit cost ₹0.023/txn.
- **Scenario B (Underutilized Legacy - APP021):** Cost ₹8.4 Cr/yr, < 150 active users, unit cost > ₹58,000/user.
- **Scenario C (Capability Duplication - CAP003):** Order-to-Cash duplicated across APP005 and APP012.
- **Scenario D (Single Point of Failure - APP010):** Central Auth Hub with 8 mission-critical dependents.
- **Scenario E (High-Performing Investment - PRJ003):** Real-Time Payment Modernization, under budget, 108% benefit realization.
- **Scenario F (Transformation Benefit Gap - PRJ014):** CRM Consolidation, over budget, 23.3% benefit realization.
- **Scenario G (Elastic Scale - APP014):** +171% August spend increase backed by +180% transaction surge.
- **Scenario H (Unbacked Cost Anomaly - APP022):** +₹38L August spend spike with completely flat transaction and user metrics.

---

## 3. Data Dependencies & Artifacts

### Primary Inputs
- `ontology.yaml`
- `config.yaml`

### Primary Outputs
- `data/raw/*.csv` (10 core entity tables, 12 months ledger, 12 months consumption)
- `config/scenarios.yaml` (Declarative YAML configuration for Scenarios A–H)
- Synthetic AWS CUR / Azure Cost Management line-item records (`generate_cloud_billing_records`)
- 3-tier organizational hierarchy & cost centers (`generate_organizational_hierarchy`)
- Synthetic multi-period compound drift & seasonal progression engine (`apply_data_drift`)

---

## 4. File Structure & Versioning

```text
01_enterprise_data_generation/
├── README.md               # Purpose, documentation, and improvement roadmap (this file)
├── v1_baseline.ipynb       # Untouched baseline reference notebook (self-contained)
└── v2_development.ipynb    # Working copy for iterative improvements and code extensions
```

- **`v1_baseline.ipynb`**: Preserves the verified baseline implementation with dynamic root discovery.
- **`v2_development.ipynb`**: Active development notebook expanded with declarative YAML scenario inspection, AWS CUR cloud billing generation, 3-tier hierarchy mapping, and data drift simulations.
- **Baseline Preservation:** `v1_baseline.ipynb` preserves the verified baseline implementation, while `v2_development.ipynb` is used for active evolution.

---

## 5. Iteration & Improvement Roadmap
- [x] Parameterize scenario injection rules via YAML configuration files (`config/scenarios.yaml`).
- [x] Add synthetic cloud billing dataset generation (AWS CUR / Azure Cost Management schemas).
- [x] Incorporate multi-level organizational hierarchies and cost-center sub-allocations.
- [x] Implement automated synthetic data drift and trend progression generators.
- [ ] Incorporate multi-currency exchange rate volatility and hedging simulations.
- [ ] Add real-time event-driven Kafka CDC log generator for sub-second telemetry streams.
