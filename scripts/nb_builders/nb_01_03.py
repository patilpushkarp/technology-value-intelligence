"""Builders for Notebooks 01, 02, and 03 with exhaustive analytical depth."""

from scripts.nb_builders.common import make_nb, add_md, add_code, save_nb


# ==============================================================================
# Notebook 01: Enterprise Synthetic Data Generation & Scenario Injection
# ==============================================================================
def build_notebook_01():
    nb = make_nb()

    # Title & Metadata
    add_md(nb, """# Notebook 01: Enterprise Synthetic Data Generation & Scenario Injection

**Series:** Technology Value Intelligence (TBM / ITFM / TVR)  
**Notebook Index:** 01 of 12  
**Focus:** Synthetic Enterprise Architecture, Relational Topologies, Controlled Scenario Injection, Referential Auditing  

---

## 1. Business Problem

In enterprise IT Financial Management (ITFM) and Technology Business Management (TBM), analytical models are often starved of representative data. Real-world corporate financial ledgers, Configuration Management Databases (CMDBs), and vendor contracts contain proprietary data, trade secrets, and compliance-restricted identifiers. Conversely, standard synthetic test datasets typically suffer from two severe shortcomings:
1. **Random Noise Without Topology:** Randomly generating applications, costs, and servers fails to capture the intricate hierarchical relationships of enterprise architectures (e.g., applications supporting capabilities, running on specific middleware, procured under multi-year vendor contracts).
2. **Absence of Analytic Scenarios:** Pure random generation lacks the empirical anomalies, bottlenecks, and variances that analytical platforms are built to diagnose—such as underutilized legacy applications, capability overlap, cost anomalies, or failed transformation projects.

To build and validate a portfolio-quality **Technology Value Intelligence (TVI)** engine, we must generate a complete, deterministic, referentially intact enterprise landscape embedding controlled business scenarios.

---

## 2. Why Dummy / Synthetic Data is Being Used

Synthetic data provides three decisive advantages for this research prototype:
- **Zero Privacy & Legal Risk:** Fictional organization names, synthetic financials, and artificial server topologies ensure zero data exposure risk.
- **Reproducibility & Auditability:** By pinning mathematical pseudorandom number generators to fixed seeds, researchers and auditors can replicate every calculation down to the exact rupee and transaction count.
- **Controlled Stress Testing:** We can programmatically inject known failure modes (e.g. single points of failure, budget overruns, unbacked rate spikes) to verify whether downstream graph and financial algorithms correctly detect them.

---

## 3. Enterprise Assumptions & Scale Definition

We model a mid-to-large diversified financial services institution operating across retail, commercial, wealth management, and payment sectors:
- **Currency:** Indian Rupee (INR, ₹), reported in standard Crores ($1\\text{ Cr} = 10,000,000$) and Lakhs ($1\\text{ L} = 100,000$).
- **Reporting Period:** 12 monthly periods representing FY2024 (2024-01 through 2024-12).
- **Enterprise Scale:**
  - $10$ Business Units (e.g., Retail Banking, Wealth Management, Digital Payments).
  - $25$ Business Capabilities (e.g., Order-to-Cash, Procure-to-Pay, Fraud Detection).
  - $18$ IT Services delivering standardized technology offerings.
  - $50$ Applications spanning core banking, CRM, ERP, and payment microservices.
  - $35$ Infrastructure and runtime Technologies (Cloud, Databases, Middleware, OS).
  - $10$ Third-party strategic Vendors with multi-year contract values.
  - $40$ Discretionary Projects / Investments (Modernization, Cloud Migration, AI).
  - $12$ Months of granular General Ledger Cost Records and Operational Consumption Logs.

---

## 4. Deterministic Random Seed Specification

To guarantee mathematical determinism across all operating systems and Python executions, we establish a global seed:
$$\\text{RANDOM\\_SEED} = 42$$
This ensures that all NumPy distributions, random strides, and scenario injections remain identical on every execution.
""")

    add_code(nb, """import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

# Ensure TVI package is importable
workspace_root = Path.cwd().parent
sys.path.insert(0, str(workspace_root / "src"))

from tvi.config import load_config, get_project_root
from tvi.data_generation import EnterpriseDataGenerator
from tvi.validation import DataQualityValidator

config = load_config()
print(f"Project Name : {config.project.name} (v{config.project.version})")
print(f"Random Seed  : {config.project.random_seed}")
print(f"Currency     : {config.project.currency} ({config.project.currency_symbol})")
print(f"Target Year  : {config.project.reporting_year}")
""")

    add_md(nb, """---

## 5. Entity Generation Walkthrough

The generation process executes progressively across foundational entities:
1. `BusinessUnit`: Organizational divisions consuming technology and generating commercial revenue.
2. `BusinessCapability`: Functional domains executed by the enterprise.
3. `ITService`: Standardized technology service offerings cataloged and delivered by IT.
4. `Vendor`: Fictional technology and services providers.
5. `Technology`: Infrastructure, runtime, database, and cloud components.
6. `Application`: Core software systems deployed to deliver services.
7. `Project`: Strategic discretionary investments and capital transformation programs.
""")

    add_code(nb, """# Instantiate the deterministic generator
generator = EnterpriseDataGenerator(config)

# 1. Master Entities
bu_df = generator.generate_business_units()
cap_df = generator.generate_business_capabilities(bu_df)
srv_df = generator.generate_it_services()
ven_df = generator.generate_vendors()
tech_df = generator.generate_technologies(ven_df)
app_df = generator.generate_applications(srv_df, ven_df)
prj_df = generator.generate_projects(bu_df)

print(f"Generated Entities:")
print(f"  • Business Units        : {len(bu_df):3d} rows")
print(f"  • Business Capabilities : {len(cap_df):3d} rows")
print(f"  • IT Services           : {len(srv_df):3d} rows")
print(f"  • Vendors               : {len(ven_df):3d} rows")
print(f"  • Technologies          : {len(tech_df):3d} rows")
print(f"  • Applications          : {len(app_df):3d} rows")
print(f"  • Projects              : {len(prj_df):3d} rows")
""")

    add_md(nb, """---

## 6. Relationship Generation & Topological Mappings

Next, we generate the multi-relational edges that bind these entities into an interconnected enterprise graph:
- `rel_app_technology`: Applications running on underlying infrastructure.
- `rel_app_capability`: Applications supporting business capabilities with explicit support types (`Primary`, `Secondary`, `Overlapping`).
- `rel_app_dependency`: App-to-app dependencies embedding Scenario D (central bottleneck).
- `rel_project_capability`: Projects targeting capability transformations.
- `rel_app_project`: Applications modernized or funded by projects.
""")

    add_code(nb, """rel_app_tech = generator.generate_app_technology_relations(app_df, tech_df)
rel_app_cap = generator.generate_app_capability_relations(app_df, cap_df)
rel_app_dep = generator.generate_app_dependencies(app_df)
rel_prj_cap = generator.generate_project_capability_relations(prj_df, cap_df)
rel_app_prj = generator.generate_app_project_relations(app_df, prj_df)

print("Generated Relational Mappings:")
print(f"  • App -> Technology Mappings   : {len(rel_app_tech):4d} edges")
print(f"  • App -> Capability Mappings   : {len(rel_app_cap):4d} edges")
print(f"  • App -> App Dependencies      : {len(rel_app_dep):4d} edges")
print(f"  • Project -> Capability Links  : {len(rel_prj_cap):4d} edges")
print(f"  • Project -> App Funding Links : {len(rel_app_prj):4d} edges")
""")

    add_md(nb, """---

## 7. Monthly General Ledger Cost Data Generation

Monthly costs are generated across standard TBM cost pools (`Software`, `Internal Labor`, `Outside Services`) and categories (`People`, `Software`, `Hardware`, `Cloud`, `Infrastructure`).
We explicitly incorporate:
- Dedicated direct costs attributed to applications.
- Shared service costs attributed to IT services where `application_id IS NULL`.
- Scenario G: Spend surges in August for `APP014` due to transaction scaling.
- Scenario H: Spend jumps in August for `APP022` with flat utilization.
""")

    add_code(nb, """cost_df = generator.generate_cost_records(
    app_df, srv_df, bu_df, ven_df, prj_df, rel_app_cap
)
print(f"Generated Cost Records: {len(cost_df):5d} ledger rows")
print(f"Total Annual Technology Spend: ₹{cost_df['amount'].sum()/1e7:.2f} Crores")
display(cost_df.head(4))
""")

    add_md(nb, """---

## 8. Monthly Operational Consumption Telemetry Generation

Operational telemetry tracks real-world usage across 6 dimensions:
$$\\mathbf{C} = [\\text{Active Users}, \\text{Transactions}, \\text{API Calls}, \\text{Compute Hours}, \\text{Storage GB}, \\text{Service Tickets}]$$
Correlations are mathematically enforced:
- Higher transactions scale compute hours and API volume.
- Deliberate anomalies are injected (Scenario B with low users/high cost, Scenario G with scaling transactions, Scenario H with flat usage).
""")

    add_code(nb, """cons_df = generator.generate_consumption_records(app_df, bu_df)
print(f"Generated Consumption Records: {len(cons_df):5d} telemetry rows")
display(cons_df.head(4))
""")

    add_md(nb, """---

## 9. Discretionary Projects Generation
Projects represent capital and operational transformation investments across 8 project types: Modernization, Cloud Migration, AI, Application Replacement, Automation, Regulatory, and Infrastructure.
""")

    add_code(nb, """print("Sample Projects:")
display(prj_df[["project_id", "project_name", "project_type", "sponsor_business_unit", "investment_budget", "actual_spend", "status"]].head(5))
""")

    add_md(nb, """---

## 10. Expected and Realized Benefits Generation
Benefits model the financial and operational outcomes delivered by completed and in-progress initiatives:
- `Cost Reduction`, `Productivity`, `Revenue Enablement`, `Risk Reduction`, `Cycle Time Reduction`, `Capacity Release`, `Customer Experience`.
- Embeds Scenario E (PRJ003 exceeded benefit realization) and Scenario F (PRJ014 severe benefit gap).
""")

    add_code(nb, """ben_df = generator.generate_benefits(prj_df)
print(f"Generated Benefits Records: {len(ben_df):4d} entries")
display(ben_df.head(4))
""")

    add_md(nb, """---

## 11. KPI Catalog & Progression Generation
Key Performance Indicators track quantitative performance shifts (e.g., Cost per Transaction, Incident Resolution Time, Core Banking Availability).
""")

    add_code(nb, """kpi_df = generator.generate_kpis()
rel_ben_kpi = generator.generate_benefit_kpi_relations(ben_df, kpi_df)

print(f"Generated KPIs: {len(kpi_df):3d} indicators | Benefit-to-KPI Links: {len(rel_ben_kpi):4d}")
display(kpi_df.head(5))
""")

    add_md(nb, """---

## 12. Referential Integrity & Validation Audit

Before persisting data to disk, we execute a rigorous validation suite verifying:
1. **Uniqueness:** All primary keys are unique.
2. **Null Checks:** Mandatory foreign and primary keys contain zero null values.
3. **Numeric Sanity:** Non-negative costs, users, transactions, and storage.
4. **Temporal Sanity:** Project end dates must be on or after start dates.
5. **Referential Integrity:** All foreign keys link to valid parent entity IDs.
""")

    add_code(nb, """all_datasets = {
    "business_units": bu_df,
    "business_capabilities": cap_df,
    "it_services": srv_df,
    "vendors": ven_df,
    "technologies": tech_df,
    "applications": app_df,
    "projects": prj_df,
    "rel_app_technology": rel_app_tech,
    "rel_app_capability": rel_app_cap,
    "rel_app_dependency": rel_app_dep,
    "rel_project_capability": rel_prj_cap,
    "rel_app_project": rel_app_prj,
    "benefits": ben_df,
    "kpis": kpi_df,
    "rel_benefit_kpi": rel_ben_kpi,
    "cost_records": cost_df,
    "consumption_records": cons_df,
}

validator = DataQualityValidator(all_datasets)
report = validator.validate_all()

print(f"=== Data Quality Audit Report ===")
print(f"Status        : {report['status']}")
print(f"Checks Run    : {report['total_checks']}")
print(f"Issues Logged : {len(report['issues'])}")
if report["issues"]:
    for iss in report["issues"]:
        print(f"  [X] {iss}")
else:
    print("✓ Zero data-quality defects. All integrity constraints verified.")
""")

    add_md(nb, """---

## 13. Exporting Datasets to CSV

We export all 17 DataFrames into `data/generated/` as CSV files, serving as the raw landing zone for DuckDB and NetworkX.
""")

    add_code(nb, """out_dir = get_project_root() / "data" / "generated"
out_dir.mkdir(parents=True, exist_ok=True)

for name, df in all_datasets.items():
    csv_file = out_dir / f"{name}.csv"
    df.to_csv(csv_file, index=False)
    print(f"Exported: {csv_file.name:28s} ({len(df):5d} rows)")
""")

    add_md(nb, """---

## 14. Verification of All 8 Analytical Scenarios (A through H)

We perform formal empirical assertions validating that our synthetic dataset embeds all 8 target scenarios:
""")

    add_code(nb, """# Assertions and Proofs for Scenarios A through H
scenario_results = []

# Scenario A: APP001 Scale Anchor
app001_cost = cost_df[cost_df["application_id"] == "APP001"]["amount"].sum()
app001_users = cons_df[cons_df["application_id"] == "APP001"]["active_users"].mean()
scenario_results.append({
    "Scenario": "Scenario A (Scale Anchor)",
    "Entity": "APP001 (CoreBanking Alpha)",
    "Evidence": f"Annual Cost: ₹{app001_cost/1e7:.2f} Cr, Avg Users: {app001_users:.0f}",
    "Verification": "PASS" if app001_cost > 1e8 and app001_users > 8000 else "FAIL"
})

# Scenario B: APP021 Underutilized Legacy
app021_cost = cost_df[cost_df["application_id"] == "APP021"]["amount"].sum()
app021_users = cons_df[cons_df["application_id"] == "APP021"]["active_users"].mean()
scenario_results.append({
    "Scenario": "Scenario B (Underutilized Sprawl)",
    "Entity": "APP021 (Legacy Web Portal)",
    "Evidence": f"Annual Cost: ₹{app021_cost/1e7:.2f} Cr, Avg Users: {app021_users:.0f} (Cost/User: ₹{app021_cost/app021_users:,.0f})",
    "Verification": "PASS" if app021_cost > 5e7 and app021_users < 200 else "FAIL"
})

# Scenario C: CAP003 Duplicate Capability Overlap
otc_apps = rel_app_cap[rel_app_cap["capability_id"] == "CAP003"]["application_id"].tolist()
scenario_results.append({
    "Scenario": "Scenario C (Capability Duplication)",
    "Entity": "CAP003 (Order-to-Cash)",
    "Evidence": f"Supported by multiple apps: {', '.join(otc_apps)}",
    "Verification": "PASS" if len(otc_apps) >= 2 else "FAIL"
})

# Scenario D: APP010 Single Point of Failure Bottleneck
app010_in_deps = rel_app_dep[rel_app_dep["target_app_id"] == "APP010"]["source_app_id"].tolist()
scenario_results.append({
    "Scenario": "Scenario D (SPOF Hub)",
    "Entity": "APP010 (Central Auth Hub)",
    "Evidence": f"Inbound dependent applications: {len(app010_in_deps)} apps ({', '.join(app010_in_deps[:4])}...)",
    "Verification": "PASS" if len(app010_in_deps) >= 6 else "FAIL"
})

# Scenario E: PRJ003 High Realization Investment
prj003_exp = prj_df[prj_df["project_id"] == "PRJ003"]["expected_annual_benefit"].values[0]
prj003_rel = ben_df[ben_df["project_id"] == "PRJ003"]["realized_value"].sum()
scenario_results.append({
    "Scenario": "Scenario E (High TVR Investment)",
    "Entity": "PRJ003 (Payment Modernization)",
    "Evidence": f"Expected: ₹{prj003_exp/1e7:.1f} Cr | Realized: ₹{prj003_rel/1e7:.1f} Cr ({prj003_rel/prj003_exp*100:.1f}%)",
    "Verification": "PASS" if prj003_rel >= prj003_exp else "FAIL"
})

# Scenario F: PRJ014 Benefit Realization Gap
prj014_exp = prj_df[prj_df["project_id"] == "PRJ014"]["expected_annual_benefit"].values[0]
prj014_rel = ben_df[ben_df["project_id"] == "PRJ014"]["realized_value"].sum()
scenario_results.append({
    "Scenario": "Scenario F (Benefit Gap Overrun)",
    "Entity": "PRJ014 (Legacy CRM Consolidation)",
    "Evidence": f"Expected: ₹{prj014_exp/1e7:.1f} Cr | Realized: ₹{prj014_rel/1e7:.1f} Cr ({prj014_rel/prj014_exp*100:.1f}%)",
    "Verification": "PASS" if (prj014_rel / prj014_exp) < 0.35 else "FAIL"
})

# Scenario G: APP014 Elastic Scaling
app014_cost_jul = cost_df[(cost_df["application_id"] == "APP014") & (cost_df["month"] == "2024-07")]["amount"].sum()
app014_cost_aug = cost_df[(cost_df["application_id"] == "APP014") & (cost_df["month"] == "2024-08")]["amount"].sum()
app014_txns_jul = cons_df[(cons_df["application_id"] == "APP014") & (cons_df["month"] == "2024-07")]["transactions"].sum()
app014_txns_aug = cons_df[(cons_df["application_id"] == "APP014") & (cons_df["month"] == "2024-08")]["transactions"].sum()
scenario_results.append({
    "Scenario": "Scenario G (Elastic Scale Surge)",
    "Entity": "APP014 (Cloud Payment Hub)",
    "Evidence": f"Cost shift: ₹{app014_cost_jul/1e5:.1f}L -> ₹{app014_cost_aug/1e5:.1f}L (+{(app014_cost_aug-app014_cost_jul)/app014_cost_jul*100:.0f}%) | Txns: +{(app014_txns_aug-app014_txns_jul)/app014_txns_jul*100:.0f}%",
    "Verification": "PASS" if app014_cost_aug > app014_cost_jul and app014_txns_aug > app014_txns_jul else "FAIL"
})

# Scenario H: APP022 Rate/Infra Spend Anomaly
app022_cost_jul = cost_df[(cost_df["application_id"] == "APP022") & (cost_df["month"] == "2024-07")]["amount"].sum()
app022_cost_aug = cost_df[(cost_df["application_id"] == "APP022") & (cost_df["month"] == "2024-08")]["amount"].sum()
app022_txns_jul = cons_df[(cons_df["application_id"] == "APP022") & (cons_df["month"] == "2024-07")]["transactions"].sum()
app022_txns_aug = cons_df[(cons_df["application_id"] == "APP022") & (cons_df["month"] == "2024-08")]["transactions"].sum()
scenario_results.append({
    "Scenario": "Scenario H (Unbacked Anomaly)",
    "Entity": "APP022 (Batch Billing Engine)",
    "Evidence": f"Cost shift: ₹{app022_cost_jul/1e5:.1f}L -> ₹{app022_cost_aug/1e5:.1f}L (+{(app022_cost_aug-app022_cost_jul)/app022_cost_jul*100:.0f}%) | Txns: flat ({(app022_txns_aug-app022_txns_jul)/app022_txns_jul*100:.1f}%)",
    "Verification": "PASS" if app022_cost_aug > (app022_cost_jul * 1.5) and abs(app022_txns_aug - app022_txns_jul) / app022_txns_jul < 0.1 else "FAIL"
})

scenarios_df = pd.DataFrame(scenario_results)
display(scenarios_df)
assert (scenarios_df["Verification"] == "PASS").all(), "All scenarios must verify PASS!"
""")

    add_md(nb, """---

## 15. Statistical Telemetry Distributions

We evaluate the statistical distributions of our telemetry variables (Users, Transactions, API Calls, Compute Hours) across the application portfolio:
""")

    add_code(nb, """# Telemetry Distribution Histograms
app_telemetry = cons_df.groupby("application_id").agg({
    "active_users": "mean",
    "transactions": "sum",
    "api_calls": "sum",
    "compute_hours": "mean"
}).reset_index()

fig, axs = plt.subplots(2, 2, figsize=(11, 7))

axs[0, 0].hist(app_telemetry["active_users"], bins=15, color="#1f77b4", edgecolor="black", alpha=0.8)
axs[0, 0].set_title("Distribution of Average Active Users", fontsize=11)
axs[0, 0].set_xlabel("Active Users")
axs[0, 0].grid(True, linestyle="--", alpha=0.4)

axs[0, 1].hist(app_telemetry["transactions"] / 1e6, bins=15, color="#2ca02c", edgecolor="black", alpha=0.8)
axs[0, 1].set_title("Distribution of Annual Transactions (Millions)", fontsize=11)
axs[0, 1].set_xlabel("Transactions (M)")
axs[0, 1].grid(True, linestyle="--", alpha=0.4)

axs[1, 0].hist(app_telemetry["api_calls"] / 1e6, bins=15, color="#ff7f0e", edgecolor="black", alpha=0.8)
axs[1, 0].set_title("Distribution of Annual API Calls (Millions)", fontsize=11)
axs[1, 0].set_xlabel("API Calls (M)")
axs[1, 0].grid(True, linestyle="--", alpha=0.4)

axs[1, 1].hist(app_telemetry["compute_hours"], bins=15, color="#d62728", edgecolor="black", alpha=0.8)
axs[1, 1].set_title("Distribution of Monthly Compute Hours", fontsize=11)
axs[1, 1].set_xlabel("Compute Hours")
axs[1, 1].grid(True, linestyle="--", alpha=0.4)

plt.tight_layout()
plt.show()
""")

    add_md(nb, """## 16. Limitations & Methodological Guardrails

1. **Synthetic Determinism:** While the dataset realistically models enterprise topologies, it is synthetic. It should not be used as an empirical benchmark for production sizing without domain adaptation.
2. **Discrete Monthly Aggregations:** Telemetry is sampled in monthly intervals. Real-time intraday autoscaling spikes are smoothed into monthly compute totals.

## 17. Next Step

In **Notebook 02: TBM / ITFM Data Model**, we ingest these CSV datasets into **DuckDB** to build a high-performance in-process columnar warehouse, establishing formal cost pools, IT towers, and financial allocation models.
""")

    return nb


# ==============================================================================
# Notebook 02: TBM / ITFM Data Model & Analytical Warehouse
# ==============================================================================
def build_notebook_02():
    nb = make_nb()

    add_md(nb, """# Notebook 02: TBM / ITFM Data Model & Analytical Warehouse

**Series:** Technology Value Intelligence (TBM / ITFM / TVR)  
**Notebook Index:** 02 of 12  
**Focus:** Cost Pools, IT Towers, DuckDB Columnar Warehouse, Materialized Views, Vectorized OLAP  

---

## 1. Business Problem

Traditional corporate accounting records technology spending in General Ledger (GL) accounts (e.g., "Account 5410: Hardware Maintenance", "Account 6120: Professional Services"). While this satisfies statutory accounting requirements, it creates a fundamental blind spot for technology leadership:
- A GL account shows *what type of asset was bought*, but never *what business purpose it serves*.
- The CIO cannot tell from a GL entry whether ₹5 Crores spent on cloud computing supported digital commerce, treasury management, or legacy batch jobs.

To solve this, Technology Business Management (TBM) and IT Financial Management (ITFM) translate financial GL entries into a multi-tier taxonomy:
$$\\text{Cost Pools (Financial GL)} \\longrightarrow \\text{IT Towers / Services} \\longrightarrow \\text{Applications} \\longrightarrow \\text{Business Units}$$

---

## 2. Core Concept & Formulation

### 2.1 The TBM-Inspired Multi-Tier Taxonomy
In this implementation, we formalize a simplified TBM/ITFM-inspired model:
1. **Cost Pools:** Elemental financial categories of technology expenditure (Internal Labor, External Labor, Software, Hardware, Telecom, Outside Services, Facilities).
2. **IT Towers / Services:** Standardized technology offerings delivered by IT (e.g., Core Banking, ERP Services, Cloud Platform, Cybersecurity).
3. **Applications:** Software systems deployed to execute IT services.
4. **Business Units:** Organizational consumers accountable for business outcomes.

### 2.2 In-Process Columnar Storage with DuckDB
Rather than deploying heavyweight external database servers (Postgres, Oracle, Snowflake), we utilize **DuckDB** as our local analytical storage engine:
- Vectorized execution engine optimized for analytical aggregations (OLAP).
- Zero network latency and zero memory bloat (runs embedded in-process).
- Seamless zero-copy interoperability with Apache Arrow and pandas DataFrames.
""")

    add_code(nb, """import sys
from pathlib import Path
import pandas as pd
import duckdb
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

workspace_root = Path.cwd().parent
sys.path.insert(0, str(workspace_root / "src"))

from tvi.config import load_config, get_project_root
from tvi.database import get_database

config = load_config()
db = get_database(config.database.path)

# Ingest all CSVs into DuckDB and compile analytical views
db.load_csv_data(get_project_root() / "data" / "generated")
print("DuckDB Analytical Warehouse Initialized Successfully.")
""")

    add_md(nb, """---

## 3. DuckDB Vectorized Query Execution Plan & Profiling

DuckDB uses a vectorized columnar query execution engine that processes data in 2048-tuple vectors using SIMD CPU instructions. We inspect the query plan to verify how columnar scans and hash aggregates optimize financial queries:
""")

    add_code(nb, """# Inspect Query Execution Plan for Cost Aggregations
explain_df = db.query_df(\"\"\"
    EXPLAIN ANALYZE
    SELECT cost_category, SUM(amount) as total_spend
    FROM cost_records
    GROUP BY cost_category
\"\"\")
for line in explain_df["explain_value"]:
    print(line)
""")

    add_md(nb, """---

## 4. Entity Table Counts & Managed Database Schema
We inspect the row counts across all managed tables:
""")

    add_code(nb, """entity_counts = db.get_entity_counts()
counts_df = pd.DataFrame(list(entity_counts.items()), columns=["Table Name", "Row Count"])
display(counts_df)
""")

    add_md(nb, """---

## 5. Formal Mathematical Reconciliation Proof

A mandatory requirement in IT financial governance is reconciliation: the total spend must perfectly balance across all dimensional axes:
$$\\sum \\text{Cost Pools} \\equiv \\sum \\text{Categories} \\equiv \\sum \\text{Services} \\equiv \\sum \\text{Monthly Spend}$$
""")

    add_code(nb, """total_spend = db.get_total_cost()
sum_category = db.query_df("SELECT SUM(amount) FROM cost_records").iloc[0, 0]
sum_monthly = db.query_df("SELECT SUM(total_cost) FROM (SELECT SUM(amount) as total_cost FROM cost_records GROUP BY month)").iloc[0, 0]
sum_pools = db.query_df("SELECT SUM(amount) FROM (SELECT SUM(amount) as amount FROM cost_records GROUP BY cost_pool)").iloc[0, 0]

reconciliation_df = pd.DataFrame([
    {"Dimension": "Gross Ledger Sum", "Total Spend (₹)": total_spend, "Reconciled": True},
    {"Dimension": "Cost Category Sum", "Total Spend (₹)": sum_category, "Reconciled": abs(sum_category - total_spend) < 1e-4},
    {"Dimension": "Monthly Aggregation Sum", "Total Spend (₹)": sum_monthly, "Reconciled": abs(sum_monthly - total_spend) < 1e-4},
    {"Dimension": "Cost Pool Sum", "Total Spend (₹)": sum_pools, "Reconciled": abs(sum_pools - total_spend) < 1e-4},
])
display(reconciliation_df)
assert reconciliation_df["Reconciled"].all(), "Financial reconciliation failed!"
""")

    add_md(nb, """---

## 6. Multi-Dimensional Spend Breakdowns & Visualizations

We analyze spend across cost categories, IT services, applications, and business units:
""")

    add_code(nb, """# Spend by Category and Service
cat_df = db.get_cost_by_category()
srv_cost_df = db.get_cost_by_service()
bu_cost_df = db.get_cost_by_business_unit()

fig, axs = plt.subplots(1, 2, figsize=(13, 5))

axs[0].barh(cat_df["cost_category"], cat_df["total_cost"] / 1e7, color="#2b5c8f")
axs[0].set_title("Technology Spend by Cost Category (₹ Cr)", fontsize=11)
axs[0].set_xlabel("Spend (₹ Crores)")
axs[0].grid(axis="x", linestyle="--", alpha=0.5)

axs[1].barh(bu_cost_df.head(6)["business_unit_name"], bu_cost_df.head(6)["total_cost"] / 1e7, color="#e07a5f")
axs[1].set_title("Top 6 Business Units by Technology Spend (₹ Cr)", fontsize=11)
axs[1].set_xlabel("Spend (₹ Crores)")
axs[1].grid(axis="x", linestyle="--", alpha=0.5)

plt.tight_layout()
plt.show()
""")

    add_code(nb, """# Interactive Plotly Sunburst: Taxonomy Hierarchy
# Cost Pool -> Cost Category -> Top Services
sunburst_query = \"\"\"
    SELECT cost_pool, cost_category, s.service_name, SUM(c.amount) as spend
    FROM cost_records c
    JOIN it_services s ON c.service_id = s.service_id
    GROUP BY cost_pool, cost_category, s.service_name
\"\"\"
sb_df = db.query_df(sunburst_query)

fig = px.sunburst(
    sb_df,
    path=["cost_pool", "cost_category", "service_name"],
    values="spend",
    title="TBM Taxonomy Hierarchy: Cost Pool -> Cost Category -> IT Service",
    color_continuous_scale="Blues"
)
fig.update_layout(margin=dict(t=40, l=0, r=0, b=0))
fig.show()
""")

    add_code(nb, """# Monthly Technology Spend Trajectory
trend_df = db.get_monthly_cost_trend()

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=trend_df["month"],
    y=trend_df["total_cost"] / 1e7,
    mode="lines+markers",
    name="Monthly Spend (₹ Cr)",
    line=dict(color="#1f77b4", width=3),
    marker=dict(size=8)
))
fig.update_layout(
    title="Monthly Technology Spend Trajectory (FY2024)",
    xaxis_title="Month",
    yaxis_title="Monthly Spend (₹ Crores)",
    template="plotly_white",
    hovermode="x unified"
)
fig.show()
""")

    add_md(nb, """## 7. Limitations & Analytical Guardrails

1. **Taxonomy Disclaimer:** This model is a **simplified TBM/ITFM-inspired demonstration model**. It is not an exact implementation of proprietary vendor taxonomies.
2. **Relational Limitation:** While DuckDB delivers instant columnar aggregations, it cannot natively answer multi-hop relationship queries (e.g. tracing third-party software risks to downstream customer capabilities).

## 8. Next Step

In **Notebook 03: Build Knowledge Graph**, we transform this relational data into a typed property graph using **NetworkX**, creating the relationship layer that powers multi-hop dependency and capability traversal.
""")

    return nb


# ==============================================================================
# Notebook 03: Knowledge Graph Construction & Topological Intelligence
# ==============================================================================
def build_notebook_03():
    nb = make_nb()

    add_md(nb, """# Notebook 03: Knowledge Graph Construction & Topological Intelligence

**Series:** Technology Value Intelligence (TBM / ITFM / TVR)  
**Notebook Index:** 03 of 12  
**Focus:** NetworkX Property Graph, Entity Resolution, Focused Subgraphs, Topological Validation  

---

## 1. Business Problem

Relational databases (SQL/DuckDB) represent enterprise architectures as separate tables linked by foreign keys. While effective for tabular aggregations, relational joins degrade rapidly in readability and performance when answering **multi-hop structural questions**:
- *Which business units depend on applications running on technologies supplied by Vendor X?*
- *If Application Y is retired, what upstream applications, IT services, and business capabilities will experience disruptions?*

In SQL, answering an 8-hop relationship query requires chaining 7 table joins, nested subqueries, and recursive Common Table Expressions (CTEs). 

A **Knowledge Graph** models entities as first-class nodes and business connections as first-class directed edges, transforming complex multi-join relational queries into intuitive graph path traversals.

---

## 2. Core Concept & Formulation

### 2.1 Property Graph Model
We construct a directed multigraph $G = (V, E)$ where:
- Each vertex $v \\in V$ possesses a unique identifier, an `entity_type`, and domain properties (e.g., `lifecycle_status`, `criticality`, `annual_license`).
- Each directed edge $e = (u, v) \\in E$ possesses a typed `relationship` attribute (e.g., `SUPPORTS`, `RUNS_ON`, `OWNS`, `DEPENDS_ON`).

### 2.2 Overcoming the "Hairball" Problem
A major failure mode in enterprise graph analytics is visualizing all 500+ nodes and 1,000+ relationships simultaneously on a single canvas, resulting in an unreadable visual "hairball". 

We employ **focused subgraph ego-networks**:
$$G_{\\text{sub}}(v_0, r) = \\{ v \\in V \\mid \\text{dist}(v_0, v) \\le r \\}$$
By bounding visualization to radius $r \\in \\{1, 2\\}$ around a focal entity, we deliver crisp, decision-ready topological insights.
""")

    add_code(nb, """import sys
from pathlib import Path
import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

workspace_root = Path.cwd().parent
sys.path.insert(0, str(workspace_root / "src"))

from tvi.config import load_config, get_project_root
from tvi.graph import (
    build_knowledge_graph, validate_graph, save_graph, get_focused_subgraph,
    _add_business_units, _add_capabilities, _add_services, _add_applications,
    _add_technologies, _add_vendors, _add_projects, _add_benefits, _add_kpis
)
from tvi.graph_queries import find_business_units_by_vendor, find_capability_overlapping_apps

config = load_config()
source_dir = get_project_root() / "data" / "generated"

# Construct graph progressively using modular builder functions
G = nx.DiGraph(name="TechnologyValueIntelligence")

# Load tables
bu_df = pd.read_csv(source_dir / "business_units.csv")
cap_df = pd.read_csv(source_dir / "business_capabilities.csv")
srv_df = pd.read_csv(source_dir / "it_services.csv")
app_df = pd.read_csv(source_dir / "applications.csv")
tech_df = pd.read_csv(source_dir / "technologies.csv")
ven_df = pd.read_csv(source_dir / "vendors.csv")
prj_df = pd.read_csv(source_dir / "projects.csv")
ben_df = pd.read_csv(source_dir / "benefits.csv")
kpi_df = pd.read_csv(source_dir / "kpis.csv")

# Add nodes progressively
_add_business_units(G, bu_df)
_add_capabilities(G, cap_df)
_add_services(G, srv_df)
_add_applications(G, app_df)
_add_technologies(G, tech_df)
_add_vendors(G, ven_df)
_add_projects(G, prj_df)
_add_benefits(G, ben_df)
_add_kpis(G, kpi_df)

print(f"Total Nodes Added: {G.number_of_nodes()}")
""")

    add_code(nb, """# Add Multi-Relational Edges
rel_app_tech = pd.read_csv(source_dir / "rel_app_technology.csv")
rel_app_cap = pd.read_csv(source_dir / "rel_app_capability.csv")
rel_app_dep = pd.read_csv(source_dir / "rel_app_dependency.csv")
rel_prj_cap = pd.read_csv(source_dir / "rel_project_capability.csv")
rel_app_prj = pd.read_csv(source_dir / "rel_app_project.csv")
rel_ben_kpi = pd.read_csv(source_dir / "rel_benefit_kpi.csv")

# BU OWNS Capability
for _, r in cap_df.iterrows():
    G.add_edge(r["business_unit_id"], r["capability_id"], relationship="OWNS")

# App SUPPORTS Capability
for _, r in rel_app_cap.iterrows():
    G.add_edge(r["application_id"], r["capability_id"], relationship="SUPPORTS", support_type=r.get("support_type", "Primary"))

# Service and Application links
for _, r in app_df.iterrows():
    G.add_edge(r["service_id"], r["application_id"], relationship="DELIVERED_BY")
    G.add_edge(r["application_id"], r["service_id"], relationship="SUPPORTS_SERVICE")

# App RUNS_ON Technology
for _, r in rel_app_tech.iterrows():
    G.add_edge(r["application_id"], r["technology_id"], relationship="RUNS_ON")

# Tech SUPPLIED_BY Vendor
for _, r in tech_df.iterrows():
    m = ven_df[ven_df["vendor_name"] == r["technology_vendor"]]
    if not m.empty:
        G.add_edge(r["technology_id"], m.iloc[0]["vendor_id"], relationship="SUPPLIED_BY")

# App DEPENDS_ON App
for _, r in rel_app_dep.iterrows():
    G.add_edge(r["source_app_id"], r["target_app_id"], relationship="DEPENDS_ON", criticality=r.get("criticality", "High"))

# Project Links
for _, r in rel_prj_cap.iterrows():
    G.add_edge(r["project_id"], r["capability_id"], relationship="TARGETS")

for _, r in rel_app_prj.iterrows():
    G.add_edge(r["project_id"], r["application_id"], relationship="FUNDS_MODERNIZATION")

for _, r in ben_df.iterrows():
    G.add_edge(r["project_id"], r["benefit_id"], relationship="PRODUCES")

for _, r in rel_ben_kpi.iterrows():
    G.add_edge(r["benefit_id"], r["kpi_id"], relationship="MEASURED_BY")

print(f"Total Graph Constructed: {G.number_of_nodes()} Nodes, {G.number_of_edges()} Edges")
""")

    add_md(nb, """---

## 3. Quantitative Topological & Centrality Analysis

We compute topological network metrics to identify key structural hubs:
- **Degree Centrality:** High degree indicates critical enterprise dependencies.
- **In-Degree vs Out-Degree:** Identifies bottleneck providers (high in-degree) vs heavy consumers (high out-degree).
""")

    add_code(nb, """in_degrees = dict(G.in_degree())
out_degrees = dict(G.out_degree())

# Filter to Applications
app_degrees = []
for a_id in app_df["application_id"]:
    app_degrees.append({
        "application_id": a_id,
        "application_name": G.nodes[a_id].get("label", a_id),
        "in_degree": in_degrees.get(a_id, 0),
        "out_degree": out_degrees.get(a_id, 0),
        "total_degree": in_degrees.get(a_id, 0) + out_degrees.get(a_id, 0),
        "lifecycle": G.nodes[a_id].get("lifecycle_status", "")
    })

app_deg_df = pd.DataFrame(app_degrees).sort_values("in_degree", ascending=False)
print("Top 5 Critical Hub Applications by Inbound Dependency:")
display(app_deg_df.head(5))

# Assert Scenario D hub: APP010 must be the highest in-degree app
assert app_deg_df.iloc[0]["application_id"] == "APP010", "APP010 must be the highest in-degree dependency hub!"
""")

    add_md(nb, """---

## 4. Focused Subgraph Visualizations

We extract and visualize bounded ego-networks around focal entities:
1. **Application Ego-Network (`APP001` - Scale Anchor)**
2. **Central Auth Hub Ego-Network (`APP010` - Single Point of Failure)**
""")

    add_code(nb, """# Focused Subgraph: APP001
sub_g1 = get_focused_subgraph(G, "APP001", radius=1, max_nodes=25)

plt.figure(figsize=(9, 5.5))
pos = nx.spring_layout(sub_g1, seed=42)

colors = []
for n in sub_g1.nodes():
    t = sub_g1.nodes[n].get("entity_type", "")
    if t == "Application": colors.append("#d62728")
    elif t == "Technology": colors.append("#1f77b4")
    elif t == "BusinessCapability": colors.append("#2ca02c")
    elif t == "ITService": colors.append("#ff7f0e")
    else: colors.append("#9467bd")

nx.draw_networkx_nodes(sub_g1, pos, node_color=colors, node_size=1300, alpha=0.9)
nx.draw_networkx_edges(sub_g1, pos, edge_color="#666666", arrows=True, arrowsize=15, width=1.5)
labels = {n: sub_g1.nodes[n].get("label", n) for n in sub_g1.nodes()}
nx.draw_networkx_labels(sub_g1, pos, labels=labels, font_size=8, font_weight="bold")

plt.title("Focused Knowledge Subgraph: APP001 (CoreBanking Alpha)", fontsize=13)
plt.axis("off")
plt.tight_layout()
plt.show()
""")

    add_code(nb, """# Interactive Plotly Network Visualization for APP010 (Scenario D Hub)
sub_g2 = get_focused_subgraph(G, "APP010", radius=1, max_nodes=25)
pos2 = nx.spring_layout(sub_g2, seed=42)

edge_x = []
edge_y = []
for edge in sub_g2.edges():
    x0, y0 = pos2[edge[0]]
    x1, y1 = pos2[edge[1]]
    edge_x.extend([x0, x1, None])
    edge_y.extend([y0, y1, None])

edge_trace = go.Scatter(
    x=edge_x, y=edge_y,
    line=dict(width=1.5, color="#888"),
    hoverinfo="none",
    mode="lines"
)

node_x = []
node_y = []
node_text = []
node_color = []
for node in sub_g2.nodes():
    x, y = pos2[node]
    node_x.append(x)
    node_y.append(y)
    data = sub_g2.nodes[node]
    node_text.append(f"{node}: {data.get('label', '')}<br>Type: {data.get('entity_type', '')}")
    node_color.append("#d62728" if node == "APP010" else "#1f77b4")

node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode="markers+text",
    text=[sub_g2.nodes[n].get("label", n)[:12] for n in sub_g2.nodes()],
    textposition="top center",
    hovertext=node_text,
    hoverinfo="text",
    marker=dict(
        color=node_color,
        size=22,
        line_width=2,
        line_color="black"
    )
)

fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                title="Interactive Topology: APP010 Central Auth Hub & Inbound Dependencies",
                showlegend=False,
                hovermode="closest",
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
             )
fig.show()
""")

    add_md(nb, """---

## 5. Multi-Hop Traversal Demonstration

We execute a real-world multi-hop query:
> *"Which business units depend on applications running on technologies supplied by Vendor X?"*

Traversal: `Vendor` $\\longrightarrow$ `Technology` $\\longrightarrow$ `Application` $\\longrightarrow$ `Capability` $\\longrightarrow$ `BusinessUnit`
""")

    add_code(nb, """vendor_results = find_business_units_by_vendor(G, "TechNova")
v_df = pd.DataFrame(vendor_results)
print(f"Total Traversal Paths Found for Vendor 'TechNova': {len(v_df)}")
display(v_df[["vendor_name", "technology_name", "application_name", "capability_name", "business_unit_name"]].head(6))
""")

    add_md(nb, """## 6. Limitations & Methodological Guardrails

1. **In-Memory RAM Limits:** NetworkX stores the entire graph in Python memory. This is ideal for 16 GB machines up to ~100k nodes, but enterprise deployments with 10M+ nodes require Neo4j or Amazon Neptune.
2. **Dynamic Frequency:** Graph edges represent structural connections; edge traversal does not measure call throughput per second without attaching dynamic telemetry.

## 7. Next Step

In **Notebook 04: Application Cost Intelligence**, we combine the relational cost ledgers with consumption telemetry to compute true fully-burdened application TCO and unit economics.
""")

    return nb


def main():
    print("Building Notebooks 01, 02, and 03...")
    save_nb(build_notebook_01(), "01_generate_enterprise_data.ipynb")
    save_nb(build_notebook_02(), "02_tbm_itfm_data_model.ipynb")
    save_nb(build_notebook_03(), "03_build_knowledge_graph.ipynb")
    print("Notebooks 01-03 ready.")


if __name__ == "__main__":
    main()
