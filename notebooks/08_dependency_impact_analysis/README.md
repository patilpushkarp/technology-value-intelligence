# Dependency & Blast Radius Impact Analysis

**Purpose:** Computes direct and transitive reverse-graph traversals across the enterprise topology. Identifies Single Points of Failure (SPOFs) like Central Auth Hub (APP010), measures multi-hop blast radius for planned change events, and scores decommissioning risk.  
**Series Index:** Notebook 08 of 12  
**Baseline Reference:** [`./v1_baseline.ipynb`](v1_baseline.ipynb) | **Active Development:** [`./v2_development.ipynb`](v2_development.ipynb)

---

## 1. Executive Business Purpose
Computes direct and transitive reverse-graph traversals across the enterprise topology. Identifies Single Points of Failure (SPOFs) like Central Auth Hub (APP010), measures multi-hop blast radius for planned change events, and scores decommissioning risk.

### Core Methodology
Reverse BFS/DFS graph traversals; in-degree and PageRank centrality ranking; multi-hop transitive closure computation; composite blast radius scoring; Monte Carlo cascading failure modeling; automated CI/CD release deployment gating; Zero-Trust network containment boundary auditing; Mermaid flowchart generation.

---

## 2. Key Scenarios & Focus Areas
- **Scenario D:** Single Point of Failure - `APP010` (Central Auth & Identity Hub) with 8 direct callers and 3 transitive dependent systems.
- **Cascading Outage Simulation:** Monte Carlo stochastic failure percolation tracking systemic collapse probabilities and vulnerable downstream nodes.
- **CI/CD Deployment Gating:** Evaluating proposed changes against risk thresholds, blocking high-blast radius releases or routing to Change Advisory Board (CAB).
- **Zero-Trust Network Auditing:** Identifying unmediated boundary traversals between DMZ edge components and Tier-0 core vaults.

---

## 3. Data Dependencies & Artifacts

### Primary Inputs
- `graph_output/technology_value_intelligence.graphml`
- `rel_app_dependency` table in DuckDB
- Enterprise Knowledge Graph (`build_knowledge_graph()`)

### Primary Outputs
- `SPOF ranking list`
- `Transitive blast radius dependency trees`
- `Decommissioning risk scores`
- `Monte Carlo cascade simulation profiles` (`simulate_failure_cascade()`)
- `CI/CD release gating verdicts` (`evaluate_deployment_gate()`)
- `Zero-Trust containment audit report` (`audit_zero_trust_segmentation()`)
- `Architecture change approval Mermaid DAGs` (`generate_dependency_flowchart_mermaid()`)

---

## 4. File Structure & Versioning

```text
08_dependency_impact_analysis/
├── README.md               # Purpose, documentation, and improvement roadmap (this file)
├── v1_baseline.ipynb       # Untouched baseline reference notebook (self-contained)
└── v2_development.ipynb    # Working copy for iterative improvements and code extensions
```

- **`v1_baseline.ipynb`**: Preserves the verified baseline implementation with dynamic root discovery.
- **`v2_development.ipynb`**: The active development canvas where new algorithms, visualizations, and modular extensions can be developed without touching the baseline.
- **Baseline Preservation:** `v1_baseline.ipynb` preserves the verified baseline implementation, while `v2_development.ipynb` is used for active evolution.

---

## 5. Iteration & Improvement Roadmap
- [x] Implement Monte Carlo failure cascade simulations across the dependency graph (`simulate_failure_cascade()`).
- [x] Integrate with CI/CD deployment pipelines for automated release blast radius gating (`evaluate_deployment_gate()`).
- [x] Evaluate Zero-Trust network segmentation containment boundaries (`audit_zero_trust_segmentation()`).
- [x] Generate visual dependency path flowcharts for high-risk change approvals (`generate_dependency_flowchart_mermaid()`).
