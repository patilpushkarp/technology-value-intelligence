# Application Rationalization & Multi-Criteria Portfolio Scoring

**Purpose:** Applies Multi-Criteria Decision Analysis (MCDA) across cost, business capability criticality, dependency centrality, and technical debt to compute the Rationalization Review Index (RRI). Generates transparent evidence trails and categorizes systems into standard Gartner TIME quadrants (Tolerate, Invest, Migrate, Eliminate).  
**Series Index:** Notebook 07 of 12  
**Baseline Reference:** [`./v1_baseline.ipynb`](v1_baseline.ipynb) | **Active Development:** [`./v2_development.ipynb`](v2_development.ipynb)

---

## 1. Executive Business Purpose
Applies Multi-Criteria Decision Analysis (MCDA) across cost, business capability criticality, dependency centrality, and technical debt to compute the Rationalization Review Index (RRI). Generates transparent evidence trails and categorizes systems into standard Gartner TIME quadrants (Tolerate, Invest, Migrate, Eliminate).

### Core Methodology
Multi-Criteria Decision Analysis (MCDA); min-max normalization; Rationalization Review Index (RRI) scoring; TIME portfolio mapping; avoidable cost quantification; Pareto optimality frontiers; contractual exit penalty and retained shared overhead modeling.

---

## 2. Key Scenarios & Focus Areas
- **Scenario B:** Decommissioning candidate `APP021` (Legacy Customer Web Portal) with high cost and low utilization.
- **Scenario C:** Consolidation of duplicate systems `APP005` (OrderFlow Strategic) and `APP012` (QuickOrder Retire).
- **MCDA Sensitivity:** Parameterized sensitivity curves testing portfolio ranking stability when cost, utilization, or overlap weights vary.
- **Contractual Exit Modeling:** Quantifying the gap between gross headline TCO and true net cash realization after factoring early vendor termination penalties and retained shared hypervisor/network overhead.

---

## 3. Data Dependencies & Artifacts

### Primary Inputs
- `Application TCO` (`v_app_annual_tco`, `cost_records`)
- `Knowledge Graph centrality metrics` (`rel_app_dependency`)
- `Capability overlap mapping` (`rel_app_capability`)

### Primary Outputs
- `RRI ranking tables`
- `TIME matrix distribution`
- `Quantified avoidable cost scenarios`
- `MCDA weight sensitivity tables` (`analyze_mcda_weight_sensitivity()`)
- `Pareto frontier trade-off dataset` (`evaluate_rationalization_pareto_frontier()`)
- `Decommissioning milestone roadmaps` (`generate_decommissioning_roadmap()`)
- `Contractual exit impact dossiers` (`model_contractual_exit_impact()`)

---

## 4. File Structure & Versioning

```text
07_application_rationalization/
├── README.md               # Purpose, documentation, and improvement roadmap (this file)
├── v1_baseline.ipynb       # Untouched baseline reference notebook (self-contained)
└── v2_development.ipynb    # Working copy for iterative improvements and code extensions
```

- **`v1_baseline.ipynb`**: Preserves the verified baseline implementation with dynamic root discovery.
- **`v2_development.ipynb`**: The active development canvas where new algorithms, visualizations, and modular extensions can be developed without touching the baseline.
- **Baseline Preservation:** `v1_baseline.ipynb` preserves the verified baseline implementation, while `v2_development.ipynb` is used for active evolution.

---

## 5. Iteration & Improvement Roadmap
- [x] Provide interactive weight adjustment for MCDA sensitivity testing (`analyze_mcda_weight_sensitivity()`).
- [x] Construct cloud migration complexity vs savings trade-off Pareto frontiers (`evaluate_rationalization_pareto_frontier()`).
- [x] Generate automated application decommissioning milestone roadmaps (`generate_decommissioning_roadmap()`).
- [x] Model contractual exit penalties and retained shared fixed overhead (`model_contractual_exit_impact()`).
