# Business Capability Cost Intelligence & Shared Attribution

**Purpose:** Solves the central TBM problem: how much does each business capability truly cost? Implements primary (70%) vs secondary (30%) application cost attribution and allocates shared infrastructure/services proportionally across business capabilities using transaction consumption drivers without double counting.  
**Series Index:** Notebook 05 of 12  
**Baseline Reference:** [`./v1_baseline.ipynb`](v1_baseline.ipynb) | **Active Development:** [`./v2_development.ipynb`](v2_development.ipynb)

---

## 1. Executive Business Purpose
Solves the central TBM problem: how much does each business capability truly cost? Implements primary (70%) vs secondary (30%) application cost attribution and allocates shared infrastructure/services proportionally across business capabilities using transaction consumption drivers without double counting.

### Core Methodology
Two-tier capability allocation (70% primary, 30% secondary); transaction-weighted shared infrastructure distribution; exact financial reconciliation.

---

## 2. Key Scenarios & Focus Areas
- Accurate capability costing for Order-to-Cash (CAP003), Payment Processing, and Core Banking.

---

## 3. Data Dependencies & Artifacts

### Primary Inputs
- `DuckDB financial ledger`
- `Knowledge Graph capability relationships`
- `Application TCO metrics`

### Primary Outputs
- `Business Capability Cost Table`
- `Shared vs Direct spend breakdown`
- `Capability cost by Business Unit`
- User-configurable dynamic allocation rules engine (`calculate_dynamic_capability_cost()`)
- Nested 3-tier capability taxonomy rollups: L1 Domain -> L2 Area -> L3 Capability (`get_nested_capability_hierarchy_cost()`)
- Public cloud infrastructure migration what-if simulator (`simulate_cloud_migration_what_if()`)
- Automated mathematical reconciliation audit proving zero double counting (`audit_capability_allocation_reconciliation()`)

---

## 4. File Structure & Versioning

```text
05_capability_cost_intelligence/
├── README.md               # Purpose, documentation, and improvement roadmap (this file)
├── v1_baseline.ipynb       # Untouched baseline reference notebook (self-contained)
└── v2_development.ipynb    # Working copy for iterative improvements and code extensions
```

- **`v1_baseline.ipynb`**: Preserves the verified baseline implementation with dynamic root discovery.
- **`v2_development.ipynb`**: Active development notebook expanded with dynamic allocation weighting, 3-tier hierarchical rollups, infrastructure cloud migration what-if simulations, and mathematical zero double-counting audits.
- **Baseline Preservation:** `v1_baseline.ipynb` preserves the verified baseline implementation, while `v2_development.ipynb` is used for active evolution.

---

## 5. Iteration & Improvement Roadmap
- [x] Enable user-configurable dynamic allocation rules via YAML/UI (`calculate_dynamic_capability_cost()`).
- [x] Support Level 1 / Level 2 / Level 3 nested capability hierarchies (`get_nested_capability_hierarchy_cost()`).
- [x] Simulate what-if cost changes when migrating shared infrastructure to public cloud (`simulate_cloud_migration_what_if()`).
- [x] Provide audit trail reports verifying zero double counting across allocations (`audit_capability_allocation_reconciliation()`).
- [ ] Connect capability run costs to business capability maturity scoring (CMMI levels 1-5).
- [ ] Implement automated cost rebasing upon application decommissioning events.
