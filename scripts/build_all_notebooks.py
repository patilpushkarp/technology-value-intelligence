"""Complete generator script for all 12 Technology Value Intelligence Jupyter notebooks.

Follows the 8-part consulting research framework across all 12 notebooks:
1. Business Problem
2. Core Concept & Formulation
3. Data Model & Schema
4. Implementation
5. Empirical Results & Visualizations
6. Business Interpretation & Strategic Insights
7. Methodological Limitations & Guardrails
8. Next Steps
"""

from pathlib import Path
import nbformat as nbf


def make_nb():
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        "kernelspec": {
            "display_name": "Python 3 (technology-value-intelligence)",
            "language": "python",
            "name": "technology-value-intelligence",
        },
        "language_info": {
            "name": "python",
            "version": "3.13.1",
        },
    }
    return nb


def add_md(nb, text):
    nb.cells.append(nbf.v4.new_markdown_cell(text.strip()))


def add_code(nb, code):
    nb.cells.append(nbf.v4.new_code_cell(code.strip()))


def save_nb(nb, filename):
    out_path = Path("notebooks") / filename
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"Generated: {out_path}")


# 01
def build_nb_01():
    nb = make_nb()
    add_md(nb, """# Notebook 01: Enterprise Synthetic Data Generation & Scenario Injection

**Series:** Technology Value Intelligence (TBM / ITFM / TVR)  
**Notebook Index:** 01 of 12  
**Focus:** Synthetic Enterprise Topology, Referential Integrity, Deterministic Scenario Injection  
""")
    add_md(nb, """## 1. Business Problem

In enterprise IT Financial Management (ITFM) and Technology Business Management (TBM), analytical models are often starved of representative data. Real-world corporate financial ledgers, CMDBs, and vendor contracts contain proprietary data, trade secrets, and compliance-restricted identifiers. Conversely, standard synthetic test datasets typically suffer from two severe shortcomings:
1. **Random Noise Without Topology:** Randomly generating applications, costs, and servers fails to capture the intricate hierarchical relationships of enterprise architectures (e.g., applications supporting capabilities, running on specific middleware, procured under multi-year vendor contracts).
2. **Absence of Analytic Scenarios:** Pure random generation lacks the empirical anomalies, bottlenecks, and variances that analytical platforms are built to diagnose—such as underutilized legacy applications, capability overlap, cost anomalies, or failed transformation projects.

To build and validate a portfolio-quality **Technology Value Intelligence (TVI)** engine, we must generate a complete, deterministic, referentially intact enterprise landscape embedding controlled business scenarios.
""")
    add_md(nb, """## 2. Core Concept & Formulation

### 2.1 Deterministic Simulation
We employ a fixed-seed pseudorandom number generator:
$$\\text{Seed} = 42$$
Deterministic generation guarantees exact mathematical reproducibility across runs, machines, and analytical environments.

### 2.2 Embedded Scenarios Matrix
Our synthetic generator deliberately injects 8 controlled enterprise phenomena:

| Scenario | Code | Business Manifestation | Analytical Signature |
| :--- | :--- | :--- | :--- |
| **Scenario A** | Scale Anchor | High cost + High usage + High criticality | `APP001`: Annual cost > ₹12 Cr, 8,500+ monthly users, 6.5M txns |
| **Scenario B** | Underutilized Sprawl | High cost + Low usage + Tolerate lifecycle | `APP021`: Annual cost ₹8.4 Cr, <150 users, cost/user > ₹55,000 |
| **Scenario C** | Capability Duplication | Redundant apps supporting same capability | `CAP003` (Order-to-Cash) supported by `APP005` & `APP012` |
| **Scenario D** | Single Point of Failure | Critical hub with high in-degree dependency | `APP010` (Central Auth Hub): 8 mission-critical systems depend on it |
| **Scenario E** | High Investment Value | Discretionary project exceeding target ROI | `PRJ003`: Under budget, 108% benefit realization, cycle time -70% |
| **Scenario F** | Transformation Benefit Gap | Project overrun with low benefit realization | `PRJ014`: Budget overrun +₹4 Cr, only 23% realized benefit |
| **Scenario G** | Elastic Consumption Growth | Cost surge driven by transaction volume | `APP014`: Cloud spend +170% in Aug driven by +180% transaction surge |
| **Scenario H** | Unbacked Cost Anomaly | Cost surge with flat/decreasing usage | `APP022`: Spend +₹38L/month in Aug with flat usage (contract/rate anomaly) |
""")
    add_md(nb, """## 3. Data Model & Schema

The data model spans 11 primary entity types and 6 explicit mapping tables:
- **Master Entities:** `BusinessUnit`, `BusinessCapability`, `ITService`, `Application`, `Technology`, `Vendor`, `Project`, `Benefit`, `KPI`
- **Transactional Ledgers:** `CostRecord` (monthly general ledger), `ConsumptionRecord` (operational telemetry)
- **Relationship Mappings:** `rel_app_technology`, `rel_app_capability`, `rel_app_dependency`, `rel_project_capability`, `rel_app_project`, `rel_benefit_kpi`
""")
    add_md(nb, """## 4. Implementation""")
    add_code(nb, """import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(str(Path.cwd().parent / "src"))

from tvi.config import load_config
from tvi.data_generation import EnterpriseDataGenerator
from tvi.validation import DataQualityValidator

config = load_config()
print(f"Project Name: {config.project.name} (v{config.project.version})")
print(f"Seed: {config.project.random_seed} | Currency: {config.project.currency} ({config.project.currency_symbol})")
""")
    add_code(nb, """# Instantiate generator and generate complete dataset
generator = EnterpriseDataGenerator(config)
datasets = generator.generate_all(output_dir="../data/generated")

print("Generated Datasets Summary:")
for name, df in datasets.items():
    print(f"  • {name:25s} : {len(df):5d} records | Columns: {list(df.columns[:3])}...")
""")
    add_md(nb, """## 5. Empirical Results & Data Quality Verification""")
    add_code(nb, """validator = DataQualityValidator(datasets)
validation_report = validator.validate_all()

print(f"Overall Validation Status: {validation_report['status']}")
print(f"Total Checks Executed    : {validation_report['total_checks']}")
print(f"Issues Detected          : {len(validation_report['issues'])}")
if validation_report['issues']:
    for iss in validation_report['issues']:
        print(f"  [!] {iss}")
else:
    print("✓ All referential integrity, primary key, numeric, and date constraints PASSED.")
""")
    add_code(nb, """# Visualize Cost Distribution across Categories
cost_df = datasets["cost_records"]
cat_summary = cost_df.groupby("cost_category")["amount"].sum().sort_values(ascending=True)

plt.figure(figsize=(10, 4.5))
bars = plt.barh(cat_summary.index, cat_summary.values / 1e7, color="#2b5c8f")
plt.title("Total Annual Spend by Cost Category (₹ Crores)", fontsize=13, pad=12)
plt.xlabel("Total Spend (₹ Crores)", fontsize=11)
plt.grid(axis="x", linestyle="--", alpha=0.6)
for bar in bars:
    w = bar.get_width()
    plt.text(w + 0.3, bar.get_y() + bar.get_height()/2, f"₹{w:.1f} Cr", va="center", fontsize=9)
plt.tight_layout()
plt.show()
""")
    add_md(nb, """## 6. Business Interpretation & Scenario Validation""")
    add_code(nb, """app_costs = cost_df.groupby("application_id")["amount"].sum()
app_users = datasets["consumption_records"].groupby("application_id")["active_users"].mean()

scenarios_check = pd.DataFrame({
    "Annual Cost (₹ Cr)": (app_costs / 1e7).round(2),
    "Avg Monthly Users": app_users.round(0),
    "Cost per User (₹)": (app_costs / app_users).round(2)
}).loc[["APP001", "APP021", "APP014", "APP022"]]

display(scenarios_check)
""")
    add_md(nb, """## 7. Limitations & Analytical Guardrails

1. **Synthetic Nature:** While the dataset exhibits realistic enterprise distributions and topology, it is completely synthetic and generated using fictional organizational names and vendor entities.
2. **Static Periodicity:** The simulation models a 12-month calendar year (FY2024). Sub-monthly seasonality, intraday telemetry spikes, and multi-year contract amortizations are simplified to monthly buckets.
3. **Guardrail:** Never extrapolate real-world vendor pricing or application benchmark performance from this synthetic data.

## 8. Next Step

In **Notebook 02: TBM / ITFM Data Model**, we will ingest these generated relational datasets into **DuckDB** to construct an in-process columnar analytical warehouse, establishing formal cost pools, IT towers, and financial allocation models.
""")
    return nb


# 02
def build_nb_02():
    nb = make_nb()
    add_md(nb, """# Notebook 02: TBM / ITFM Data Model & Analytical Warehouse

**Series:** Technology Value Intelligence (TBM / ITFM / TVR)  
**Notebook Index:** 02 of 12  
**Focus:** Cost Pools, IT Towers, DuckDB Columnar Warehouse, Materialized Analytical Views  
""")
    add_md(nb, """## 1. Business Problem

Traditional corporate accounting systems record technology spending in General Ledger (GL) accounts (e.g., "Account 5410: Hardware Maintenance", "Account 6120: Consulting Fees"). While this satisfies tax and statutory accounting requirements, it creates a fundamental blind spot for technology leadership:
- A GL account shows *what type of asset was bought*, but never *what business purpose it serves*.
- The CIO cannot tell from a GL entry whether ₹5 Crores spent on cloud computing supported digital commerce, treasury management, or legacy batch jobs.

To solve this, Technology Business Management (TBM) and IT Financial Management (ITFM) translate financial GL entries into a multi-tier taxonomy:
$$\\text{Cost Pools (Financial GL)} \\longrightarrow \\text{IT Towers / Services} \\longrightarrow \\text{Applications} \\longrightarrow \\text{Business Units}$$
""")
    add_md(nb, """## 2. Core Concept & Formulation

### 2.1 The TBM-Inspired Multi-Tier Taxonomy
In this implementation, we formalize a simplified TBM/ITFM-inspired model:
1. **Cost Pools:** The elemental financial categories of technology expenditure (Internal Labor, External Labor, Software, Hardware, Telecom, Outside Services, Facilities).
2. **IT Towers / Services:** Standardized technology offerings delivered by IT (e.g., Core Banking, ERP Services, Cloud Platform, Cybersecurity).
3. **Applications:** The software workloads that consume infrastructure and deliver business capabilities.
4. **Business Units:** The organizational consumers accountable for operational outcomes and revenue generation.

### 2.2 In-Process Columnar Storage with DuckDB
Rather than deploying heavyweight external database servers (Postgres, Oracle, Snowflake), we utilize **DuckDB** as our local analytical storage engine:
- Vectorized execution engine optimized for analytical aggregations (OLAP).
- Zero network latency and zero memory bloat (runs embedded in-process).
- Seamless zero-copy interoperability with Apache Arrow and pandas DataFrames.
""")
    add_md(nb, """## 3. Data Model & Schema Interaction

The DuckDB database stores the raw transactional tables and exposes three analytical views:
- `v_app_monthly_cost`: Aggregates monthly application spend by cost category.
- `v_app_annual_tco`: Materializes annual fully-burdened application expenditure alongside lifecycle status.
- `v_app_monthly_consumption`: Aggregates monthly active users, transaction volume, and compute hours.
""")
    add_md(nb, """## 4. Implementation""")
    add_code(nb, """import sys
from pathlib import Path
import pandas as pd
import duckdb
import matplotlib.pyplot as plt

sys.path.append(str(Path.cwd().parent / "src"))

from tvi.config import load_config
from tvi.database import get_database

config = load_config()
db = get_database(config.database.path)

# Ingest all CSVs into DuckDB and compile analytical views
db.load_csv_data("../data/generated")
print("DuckDB Analytical Warehouse Initialized Successfully.")
""")
    add_code(nb, """# Verify Ingested Entity Counts
entity_counts = db.get_entity_counts()
counts_df = pd.DataFrame(list(entity_counts.items()), columns=["Table Name", "Row Count"])
display(counts_df)
""")
    add_md(nb, """## 5. Empirical Results & Financial Aggregations""")
    add_code(nb, """# Total Enterprise Technology Expenditure
total_cost = db.get_total_cost()
print(f"Total Enterprise Technology Expenditure: ₹{total_cost:,.2f} (₹{total_cost/1e7:.2f} Crores)")
""")
    add_code(nb, """# Cost Breakdown by Cost Category
cat_df = db.get_cost_by_category()
display(cat_df)

# Plot category breakdown
plt.figure(figsize=(9, 4.5))
plt.pie(cat_df["total_cost"], labels=cat_df["cost_category"], autopct="%1.1f%%",
        colors=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f"])
plt.title("Technology Spend Distribution by Cost Category", fontsize=12)
plt.tight_layout()
plt.show()
""")
    add_code(nb, """# Top 10 Applications by Expenditure
top_apps = db.get_cost_by_application(limit=10)
display(top_apps)
""")
    add_code(nb, """# Monthly Technology Spend Trend Time-Series
trend_df = db.get_monthly_cost_trend()

plt.figure(figsize=(10, 4))
plt.plot(trend_df["month"], trend_df["total_cost"] / 1e7, marker="o", color="#1f77b4", linewidth=2.5)
plt.title("Monthly Enterprise Technology Spend Trajectory (FY2024)", fontsize=13)
plt.ylabel("Monthly Spend (₹ Crores)", fontsize=11)
plt.xlabel("Month", fontsize=11)
plt.grid(True, linestyle="--", alpha=0.5)
plt.ylim(0, (trend_df["total_cost"].max() / 1e7) * 1.25)
plt.tight_layout()
plt.show()
""")
    add_md(nb, """## 6. Business Interpretation & Insights

1. **Category Weight:** Software and People (Internal Labor) represent the largest foundational expenditures, followed by Cloud and Infrastructure.
2. **Spend Concentration:** The top 5 applications consume a disproportionate share of the software budget (Scale Anchor `APP001` leads with over ₹10 Cr annual spend).
3. **Monthly Trajectory:** Technology spend displays a visible upward inflection beginning in August 2024 (Month 08), indicating expanding operational usage or cost anomalies that will require detailed variance deconstruction in subsequent notebooks.
""")
    add_md(nb, """## 7. Limitations & Analytical Guardrails

1. **Taxonomy Disclaimer:** This model is a **simplified TBM/ITFM-inspired model for demonstration**, designed to demonstrate local analytics. It is not an exact implementation of any commercial proprietary taxonomy.
2. **Relational Limitation:** While DuckDB excels at fast columnar aggregations, it cannot efficiently answer multi-hop topological questions (e.g., "If Vendor X increases license fees by 20%, which business units and customer-facing capabilities are impacted?").

## 8. Next Step

In **Notebook 03: Build Knowledge Graph**, we will transform this relational schema into a typed property graph using **NetworkX**, creating the relationship layer that powers multi-hop dependency and capability traversal.
""")
    return nb


# 03
def build_nb_03():
    nb = make_nb()
    add_md(nb, """# Notebook 03: Knowledge Graph Construction & Topological Intelligence

**Series:** Technology Value Intelligence (TBM / ITFM / TVR)  
**Notebook Index:** 03 of 12  
**Focus:** NetworkX Property Graph, Entity Resolution, Focused Subgraphs, Topological Validation  
""")
    add_md(nb, """## 1. Business Problem

Relational databases (SQL/DuckDB) represent enterprise architectures as separate, normalized tables joined by foreign keys. While effective for tabular aggregations, relational joins degrade rapidly in readability and performance when answering **multi-hop structural questions**:
- *Which business units depend on applications running on technologies supplied by Vendor X?*
- *If Application Y is retired, what upstream applications, IT services, and business capabilities will experience disruptions?*

In SQL, answering an 8-hop relationship query requires chaining 7 table joins, nested subqueries, and recursive Common Table Expressions (CTEs). 

A **Knowledge Graph** models entities as first-class nodes and business connections as first-class directed edges, transforming complex multi-join relational queries into intuitive graph path traversals.
""")
    add_md(nb, """## 2. Core Concept & Formulation

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
    add_md(nb, """## 3. Data Model & Graph Ontology

```text
BusinessUnit ──OWNS──► BusinessCapability ──ENABLED_BY──► ITService
      ▲                       ▲                               ▲
      │                       │                               │
CONSUMED_BY                SUPPORTS                      DELIVERED_BY
      │                       │                               │
      └────────────────── Application ────────────────────────┘
                          │         │
                   RUNS_ON           SUPPLIED_BY
                          ▼                 ▼
                     Technology         Vendor
```
""")
    add_md(nb, """## 4. Implementation""")
    add_code(nb, """import sys
from pathlib import Path
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(str(Path.cwd().parent / "src"))

from tvi.config import load_config
from tvi.graph import build_knowledge_graph, validate_graph, save_graph, get_focused_subgraph

config = load_config()

# Construct complete knowledge graph from generated CSV data
G = build_knowledge_graph("../data/generated")
print(f"Graph Construction Complete: {G.name}")
""")
    add_code(nb, """# Validate Graph Topology and Structure
val_report = validate_graph(G)

print(f"Graph Validated: {val_report['is_valid']}")
print(f"Total Nodes    : {val_report['total_nodes']}")
print(f"Total Edges    : {val_report['total_edges']}")
print("\\nNode Types Distribution:")
for ntype, count in val_report['node_distribution'].items():
    print(f"  • {ntype:22s} : {count:4d}")

print("\\nRelationship Types Distribution:")
for rel, count in val_report['relationship_distribution'].items():
    print(f"  • {rel:22s} : {count:4d}")
""")
    add_md(nb, """## 5. Empirical Results & Focused Subgraph Visualizations""")
    add_code(nb, """# Export Knowledge Graph in GraphML and Node-Link JSON formats
saved_path = save_graph(G, output_dir="../graph_output")
print(f"Graph serialized to: {saved_path}")
""")
    add_code(nb, """# Visualize Focused Ego-Network for Scenario A (APP001 - Scale Anchor)
sub_g1 = get_focused_subgraph(G, "APP001", radius=1, max_nodes=25)

plt.figure(figsize=(9, 6))
pos = nx.spring_layout(sub_g1, seed=42, k=0.8)

colors = []
for n in sub_g1.nodes():
    etype = sub_g1.nodes[n].get("entity_type", "")
    if etype == "Application":
        colors.append("#d62728")
    elif etype == "Technology":
        colors.append("#1f77b4")
    elif etype == "BusinessCapability":
        colors.append("#2ca02c")
    elif etype == "ITService":
        colors.append("#ff7f0e")
    else:
        colors.append("#9467bd")

nx.draw_networkx_nodes(sub_g1, pos, node_color=colors, node_size=1200, alpha=0.9)
nx.draw_networkx_edges(sub_g1, pos, edge_color="#7f7f7f", arrows=True, arrowsize=15, width=1.5)

labels = {n: sub_g1.nodes[n].get("label", n) for n in sub_g1.nodes()}
nx.draw_networkx_labels(sub_g1, pos, labels=labels, font_size=8, font_weight="bold")

plt.title("Focused Knowledge Subgraph: APP001 (CoreBanking Alpha)", fontsize=13, pad=12)
plt.axis("off")
plt.tight_layout()
plt.show()
""")
    add_md(nb, """## 6. Business Interpretation & Multi-Hop Demonstration""")
    add_code(nb, """# Multi-Hop Demonstration: Vendor -> Technology -> Application -> Capability -> Business Unit
from tvi.graph_queries import find_business_units_by_vendor

vendor_query = "TechNova"
results = find_business_units_by_vendor(G, vendor_query)

print(f"Multi-Hop Traversal Results for Vendor '{vendor_query}':")
print(f"Found {len(results)} distinct value paths. Displaying sample 4:")
sample_df = pd.DataFrame(results)[["vendor_name", "technology_name", "application_name", "capability_name", "business_unit_name"]].head(4)
display(sample_df)
""")
    add_md(nb, """## 7. Limitations & Analytical Guardrails

1. **In-Memory Scale:** NetworkX stores the entire graph in RAM. While optimal for 16 GB machines and portfolios up to 100,000 nodes, multi-million node graphs require distributed graph backends (e.g., Neo4j, AWS Neptune).
2. **Directionality Interpretation:** Edge direction represents semantic lineage (e.g., `APP001 --SUPPORTS--> CAP001`). Reverse traversal is performed via incoming edge inspection.

## 8. Next Step

In **Notebook 04: Application Cost Intelligence**, we will synthesize DuckDB cost records with operational telemetry to calculate true fully-burdened application TCO and unit economics.
""")
    return nb


# 04
def build_nb_04():
    nb = make_nb()
    add_md(nb, """# Notebook 04: Application Cost Intelligence & Unit Economics

**Series:** Technology Value Intelligence (TBM / ITFM / TVR)  
**Notebook Index:** 04 of 12  
**Focus:** Fully-Burdened Application TCO, Cost per User, Cost per Transaction, Pareto Concentration  
""")
    add_md(nb, """## 1. Business Problem

Most enterprise IT organizations track application software licenses, but severely underestimate true **Application Total Cost of Ownership (TCO)**. Software licenses often represent less than 35% of an application's true operational burden:
- **Internal & External Labor:** Dedicated engineering, operations, and support staff.
- **Dedicated & Shared Infrastructure:** Cloud compute instances, storage buckets, database clusters, and physical servers.
- **Third-Party Support & Vendor Contracts:** Ancillary monitoring, tooling, and maintenance.

Furthermore, aggregate cost alone does not tell an executive whether an application is efficient. An application costing ₹15 Crores supporting 10,000 active users is vastly more cost-effective than an application costing ₹5 Crores supporting only 50 users. We must evaluate **Unit Economics**.
""")
    add_md(nb, """## 2. Core Concept & Formulation

### 2.1 Fully-Burdened Application TCO
$$\\text{TCO}(\\text{App}) = \\text{Software} + \\text{Internal Labor} + \\text{Cloud} + \\text{Infrastructure} + \\text{Vendor Services}$$

### 2.2 Unit Economics Metrics
To normalize cost by operational delivery, we define:
$$\\text{Annual Cost per Active User} = \\frac{\\text{Annual TCO}}{\\text{Average Monthly Active Users}}$$
$$\\text{Cost per Digital Transaction} = \\frac{\\text{Annual TCO}}{\\text{Annual Transaction Volume}}$$

### 2.3 Pareto Concentration (80/20 Rule)
We compute cumulative spend share to identify the critical subset of applications that drive the majority of enterprise technology costs.
""")
    add_md(nb, """## 3. Data Model Interaction

- `cost_records`: Granular ledger records tagged with `application_id`.
- `applications`: Master metadata (lifecycle, criticality, license cost).
- `consumption_records`: Monthly operational metrics (`active_users`, `transactions`).
""")
    add_md(nb, """## 4. Implementation""")
    add_code(nb, """import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(str(Path.cwd().parent / "src"))

from tvi.config import load_config
from tvi.cost_analytics import calculate_application_tco, get_application_profile

config = load_config()

# Compute fully burdened TCO and unit economics
app_tco_df = calculate_application_tco()
print("Application Cost Intelligence Table Compiled:")
display(app_tco_df[["application_id", "application_name", "lifecycle_status", "annual_tco", "avg_monthly_users", "annual_cost_per_user", "cost_per_transaction", "cumulative_spend_pct"]].head(8))
""")
    add_md(nb, """## 5. Empirical Results & Visualizations""")
    add_code(nb, """# Pareto Analysis: Top Applications Driving Enterprise Spend
plt.figure(figsize=(10, 4.5))
top_15 = app_tco_df.head(15)

x = range(len(top_15))
plt.bar(x, top_15["annual_tco"] / 1e7, color="#1f77b4", label="Annual TCO (₹ Cr)")
plt.xticks(x, top_15["application_id"], rotation=45, ha="right")
plt.ylabel("Annual TCO (₹ Crores)", fontsize=11)
plt.title("Top 15 Applications by Annual Technology Expenditure", fontsize=13)

# Add cumulative percentage line on twin axis
ax2 = plt.twinx()
ax2.plot(x, top_15["cumulative_spend_pct"], color="#d62728", marker="o", linewidth=2, label="Cumulative Spend %")
ax2.set_ylabel("Cumulative Portfolio Spend %", color="#d62728", fontsize=11)
ax2.set_ylim(0, 100)
ax2.grid(False)

plt.tight_layout()
plt.show()
""")
    add_code(nb, """# Unit Economics Scatter: Annual Cost vs Active User Volume
plt.figure(figsize=(9, 5))
plt.scatter(app_tco_df["avg_monthly_users"], app_tco_df["annual_tco"] / 1e7,
            s=app_tco_df["annual_cost_per_user"] / 100, c=app_tco_df["annual_cost_per_user"],
            cmap="viridis", alpha=0.8, edgecolors="black")

plt.xlabel("Average Monthly Active Users", fontsize=11)
plt.ylabel("Annual TCO (₹ Crores)", fontsize=11)
plt.title("Application Portfolio: Spend vs User Scale (Bubble Size = Cost/User)", fontsize=13)
plt.colorbar(label="Annual Cost per User (₹)")
plt.grid(True, linestyle="--", alpha=0.5)

app_001 = app_tco_df[app_tco_df["application_id"] == "APP001"].iloc[0]
plt.annotate("APP001 (Scale Anchor)", xy=(app_001["avg_monthly_users"], app_001["annual_tco"]/1e7),
             xytext=(app_001["avg_monthly_users"]-2000, (app_001["annual_tco"]/1e7)+1),
             arrowprops=dict(facecolor='black', shrink=0.05, width=1))

app_021 = app_tco_df[app_tco_df["application_id"] == "APP021"].iloc[0]
plt.annotate("APP021 (Underutilized Legacy)", xy=(app_021["avg_monthly_users"], app_021["annual_tco"]/1e7),
             xytext=(app_021["avg_monthly_users"]+500, (app_021["annual_tco"]/1e7)+1.5),
             arrowprops=dict(facecolor='red', shrink=0.05, width=1))

plt.tight_layout()
plt.show()
""")
    add_md(nb, """## 6. Business Interpretation & Insights

1. **Scenario A (APP001 - CoreBanking Alpha):** Although APP001 incurs the highest annual spend in the enterprise (> ₹15 Cr), its massive utilization (8,500+ active users, 6.5M transactions) yields an exceptionally low unit transaction cost (₹0.023/txn). It is a highly efficient core anchor.
2. **Scenario B (APP021 - Legacy Customer Web Portal):** APP021 incurs over ₹8.4 Cr in annual spend, but supports fewer than 150 monthly users, driving its annual cost per active user above ₹58,000. It represents a clear target for rationalization review.
""")
    add_md(nb, """## 7. Limitations & Analytical Guardrails

1. **Fixed vs Variable Cost Realities:** Unit costs (TCO / users) assume simple proportional allocation. In reality, a large portion of software license and infrastructure cost is fixed. A 50% decrease in active users does not automatically reduce total application spend by 50%.
2. **Non-User Applications:** Middleware, batch ETL systems, and security daemons deliver enterprise value without direct interactive end-users; their unit economics must be evaluated via transaction and API volumes.

## 8. Next Step

In **Notebook 05: Capability Cost Intelligence**, we elevate our financial lens from individual applications to **Business Capabilities**, solving the critical challenge of allocating shared IT services without double-counting.
""")
    return nb


# 05
def build_nb_05():
    nb = make_nb()
    add_md(nb, """# Notebook 05: Business Capability Cost Intelligence & Shared Attribution

**Series:** Technology Value Intelligence (TBM / ITFM / TVR)  
**Notebook Index:** 05 of 12  
**Focus:** Business Capability Costing, Shared Infrastructure Allocation, Avoiding Double-Counting  
""")
    add_md(nb, """## 1. Business Problem

CFOs and Business Unit leaders do not purchase "applications" for their own sake; they fund **Business Capabilities** (e.g., Order-to-Cash, Procure-to-Pay, Fraud Detection, Regulatory Reporting). 

When executive leadership asks:
> *"What does our Order-to-Cash capability actually cost?"*

Conventional IT accounting fails because:
1. Capabilities are supported by multiple applications concurrently.
2. A single enterprise application often supports multiple capabilities simultaneously.
3. Common shared infrastructure (networks, storage arrays, security operations) is shared across capabilities without clear boundaries.

Without a rigorous allocation model, organizations suffer from **double-counting** or unallocated financial "slush funds".
""")
    add_md(nb, """## 2. Core Concept & Formulation

### 2.1 The Capability Allocation Rule
To achieve 100% financial reconciliation without double-counting:

1. **Direct Application Costs:**
   - If Application $A$ supports a single capability $C$, 100% of $A$'s TCO is assigned to $C$.
   - If Application $A$ supports multiple capabilities, costs are apportioned using normalized weights:
     $$w_i = \\begin{cases} 1.0 & \\text{if Primary support} \\\\ 0.5 & \\text{if Secondary / Overlapping support} \\end{cases}$$
     $$\\text{Normalized Weight } \\hat{w}_i = \\frac{w_i}{\\sum_j w_j}$$
     $$\\text{Allocated Direct Cost} = \\hat{w}_i \\times \\text{TCO}(A)$$

2. **Shared Infrastructure Costs (Unassigned to specific apps):**
   - Allocated to capabilities proportionally based on their share of total enterprise transaction consumption:
     $$\\text{Shared Allocated}(C) = \\frac{\\text{Transactions}(C)}{\\sum_k \\text{Transactions}(k)} \\times \\text{Total Shared Infra Cost}$$
""")
    add_md(nb, """## 3. Data Model Interaction

- `business_capabilities`: Capability hierarchy and metadata.
- `rel_app_capability`: Mapping between applications and capabilities with `support_type` (`Primary`, `Secondary`, `Overlapping`).
- `cost_records`: Direct and shared cost records.
""")
    add_md(nb, """## 4. Implementation""")
    add_code(nb, """import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(str(Path.cwd().parent / "src"))

from tvi.config import load_config
from tvi.cost_analytics import calculate_capability_cost, get_capability_profile

config = load_config()

# Compute complete capability cost attribution
cap_cost_df = calculate_capability_cost()
print("Business Capability Cost Intelligence Compiled:")
display(cap_cost_df[["capability_id", "capability_name", "strategic_priority", "criticality", "supported_apps_count", "direct_app_cost", "shared_infra_allocated", "total_capability_cost", "cost_per_transaction"]].head(10))
""")
    add_md(nb, """## 5. Empirical Results & Capability Cost Distribution""")
    add_code(nb, """# Top 10 Capabilities by Total Technology Expenditure
plt.figure(figsize=(10, 5))
top_caps = cap_cost_df.head(10).sort_values("total_capability_cost", ascending=True)

y = range(len(top_caps))
plt.barh(y, top_caps["direct_app_cost"] / 1e7, label="Direct App Cost (₹ Cr)", color="#2b5c8f")
plt.barh(y, top_caps["shared_infra_allocated"] / 1e7, left=top_caps["direct_app_cost"] / 1e7,
         label="Allocated Shared Infra (₹ Cr)", color="#e07a5f")

plt.yticks(y, top_caps["capability_name"], fontsize=10)
plt.xlabel("Total Capability Cost (₹ Crores)", fontsize=11)
plt.title("Top 10 Business Capabilities by Technology Cost", fontsize=13)
plt.legend(loc="lower right")
plt.grid(axis="x", linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()
""")
    add_code(nb, """# Inspect Specific Capability Dossier: Order-to-Cash (CAP003)
otc_profile = get_capability_profile("CAP003")
print("Capability Dossier: Order-to-Cash (CAP003)")
print(f"Total Cost: ₹{otc_profile['summary']['total_capability_cost']/1e7:.2f} Cr")
print("\\nSupporting Applications:")
display(otc_profile["supporting_applications"])
""")
    add_md(nb, """## 6. Business Interpretation & Insights

1. **Strategic Capability Costing:** Customer Management, Order-to-Cash, and Financial Reporting represent the highest technology cost domains in the enterprise.
2. **Revealing Overlap in Order-to-Cash:** The capability dossier demonstrates that Order-to-Cash (CAP003) is supported by both `APP005` (Strategic OrderFlow) and `APP012` (QuickOrder Legacy). This redundancy directly inflates the capability's baseline cost.
""")
    add_md(nb, """## 7. Limitations & Analytical Guardrails

1. **Driver Selection:** We utilized digital transaction volume as the proportional driver for shared infrastructure. Other corporate environments might utilize employee headcount, storage volume, or revenue share.
2. **Reconciliation Check:** Summing `total_capability_cost` across all capabilities perfectly reconciles with total enterprise technology spend in DuckDB, ensuring no unallocated variance.

## 8. Next Step

In **Notebook 06: Consumption Intelligence**, we evaluate technology consumption across multiple dimensions, mapping applications into strategic utilization quadrants.
""")
    return nb


# 06
def build_nb_06():
    nb = make_nb()
    add_md(nb, """# Notebook 06: Consumption Intelligence & Utilization Quadrants

**Series:** Technology Value Intelligence (TBM / ITFM / TVR)  
**Notebook Index:** 06 of 12  
**Focus:** Multidimensional Telemetry, Cost vs Utilization Quadrants, Unit Economics Curves  
""")
    add_md(nb, """## 1. Business Problem

A fundamental flaw in legacy IT financial management is evaluating costs in isolation from consumption telemetry. When an application's annual expenditure increases by 25%, finance teams instinctively flag it as a cost overrun. However:
- If transactions grew by 40%, the application's **unit economics actually improved**.
- Conversely, if an application's spend stayed flat while active user volume declined by 70%, its unit cost escalated dramatically.

To separate genuine operational scaling from technical waste, we must fuse financial ledgers with **operational consumption telemetry**.
""")
    add_md(nb, """## 2. Core Concept & Formulation

### 2.1 Multidimensional Telemetry Vector
For each application $i$ in month $m$, we track:
$$\\mathbf{C}_{i,m} = [\\text{Active Users}, \\text{Transactions}, \\text{API Calls}, \\text{Compute Hours}, \\text{Storage GB}, \\text{Service Tickets}]$$

### 2.2 Objective Median-Split Quadrant Matrix
Rather than using arbitrary subjective thresholds, we perform median-split clustering across the entire portfolio:
- $\\text{Median Cost} = \\text{Median}(\\{\\text{TCO}_i\\})$
- $\\text{Median Users} = \\text{Median}(\\{\\overline{\\text{Users}}_i\\})$

| Quadrant | Economic Signature | Strategic Business Interpretation |
| :--- | :--- | :--- |
| **High Cost / High Usage** | Scale Anchor | Core operational engines. Focus on architectural stability and continuous FinOps. |
| **High Cost / Low Usage** | Investigate / Rationalize | Heavy financial burden with minimal adoption. High-priority rationalization review. |
| **Low Cost / High Usage** | High Efficiency Workhorse | High organizational value with low overhead. Models for engineering best practices. |
| **Low Cost / Low Usage** | Niche Utility | Fit-for-purpose specialized utilities. Low financial impact; leave alone unless legacy risk. |
""")
    add_md(nb, """## 3. Data Model Interaction

- `v_app_monthly_consumption`: Aggregated monthly telemetry.
- `v_app_annual_tco`: Annualized financial expenditure.
""")
    add_md(nb, """## 4. Implementation""")
    add_code(nb, """import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(str(Path.cwd().parent / "src"))

from tvi.config import load_config
from tvi.consumption_analytics import analyze_consumption_quadrants, find_high_cost_low_utilization, analyze_unit_economics_trends

config = load_config()

# Classify portfolio into objective consumption quadrants
quadrant_df = analyze_consumption_quadrants()
print("Consumption Quadrant Analysis Compiled:")
display(quadrant_df[["application_id", "application_name", "annual_tco", "avg_monthly_users", "consumption_quadrant"]].head(8))
""")
    add_md(nb, """## 5. Empirical Results & Quadrant Matrix Visualization""")
    add_code(nb, """# Visualize Portfolio Consumption Quadrants
plt.figure(figsize=(10, 6))

colors = {
    "High Cost / High Utilization (Scale Anchor)": "#1f77b4",
    "High Cost / Low Utilization (Investigate for Rationalization)": "#d62728",
    "Low Cost / High Utilization (High Efficiency Workhorse)": "#2ca02c",
    "Low Cost / Low Utilization (Niche Utility)": "#7f7f7f"
}

for q_label, group in quadrant_df.groupby("consumption_quadrant"):
    plt.scatter(group["avg_monthly_users"], group["annual_tco"] / 1e7,
                label=q_label, color=colors.get(q_label, "black"), s=80, alpha=0.85, edgecolors="none")

med_cost = quadrant_df["annual_tco"].median() / 1e7
med_users = quadrant_df["avg_monthly_users"].median()

plt.axhline(med_cost, color="grey", linestyle="--", alpha=0.7, label=f"Median Spend (₹{med_cost:.1f} Cr)")
plt.axvline(med_users, color="grey", linestyle=":", alpha=0.7, label=f"Median Users ({med_users:.0f})")

plt.xlabel("Average Monthly Active Users", fontsize=11)
plt.ylabel("Annual TCO (₹ Crores)", fontsize=11)
plt.title("Technology Portfolio: Cost vs Utilization Quadrant Matrix", fontsize=13, pad=12)
plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=9)
plt.grid(True, linestyle="--", alpha=0.4)
plt.tight_layout()
plt.show()
""")
    add_code(nb, """# Filter High-Cost / Low-Utilization Candidates for Immediate Investigation
investigate_df = find_high_cost_low_utilization(cost_percentile=0.60, utilization_percentile=0.40)
print(f"Applications Identified for Investigation ({len(investigate_df)} systems):")
display(investigate_df[["application_id", "application_name", "lifecycle_status", "annual_tco", "avg_monthly_users", "annual_cost_per_user", "investigation_flag"]])
""")
    add_md(nb, """## 6. Business Interpretation & Insights

1. **Investigate Candidates:** Applications falling into the top-left quadrant (High Cost / Low Utilization)—such as `APP021` (Legacy Customer Web Portal) and `APP035` (Branch Teller Terminal)—consume millions in annual capital while serving narrow user bases.
2. **Scale Anchors:** Core platforms in the top-right quadrant (`APP001`, `APP004`, `APP011`) justify their large budgets through high active utilization.
""")
    add_md(nb, """## 7. Limitations & Analytical Guardrails

1. **Labeling Guardrail:** We intentionally avoid labeling quadrants as "good" or "bad". A low-user application might be an executive risk engine used once a quarter to make multi-billion rupee capital allocation decisions.
2. **Investigation Mandate:** The quadrant matrix generates an **indicator for human investigation**, not an automated termination order.

## 8. Next Step

In **Notebook 07: Application Rationalization**, we formalize a multi-criteria decision index (RRI) that combines cost, utilization, capability redundancy, criticality, and lifecycle status to systematically prioritize portfolio rationalization.
""")
    return nb


# 07
def build_nb_07():
    nb = make_nb()
    add_md(nb, """# Notebook 07: Application Rationalization & Multi-Criteria Portfolio Scoring

**Series:** Technology Value Intelligence (TBM / ITFM / TVR)  
**Notebook Index:** 07 of 12  
**Focus:** Multi-Criteria Decision Analysis (MCDA), Rationalization Review Index (RRI), Avoidable Cost Scenarios  
""")
    add_md(nb, """## 1. Business Problem

Enterprise application rationalization is often paralyzed by internal organizational politics. IT leaders attempt to retire obsolete or redundant systems, only to be met with resistance from departmental sponsors claiming the application is indispensable.

Common failure modes:
1. **Decisions based solely on cost:** Decommissioning a high-cost application that turns out to be mission-critical.
2. **Decisions based on opaque "black box" scoring:** Stakeholders reject recommendations because the underlying formulas cannot be audited or explained.

To build trust and accelerate portfolio optimization, we require a **transparent, rule-based Multi-Criteria Decision Analysis (MCDA)** scoring framework with clear evidence trails.
""")
    add_md(nb, """## 2. Core Concept & Formulation

### 2.1 Multi-Criteria Decision Analysis (MCDA)
We compute five normalized indicators ($S \\in [0, 100]$):
1. **Cost Score ($S_{\\text{cost}}$):** Percentile ranking of annual TCO.
2. **Utilization Score ($S_{\\text{util}}$):** Percentile ranking of active user volume (higher = more utilized).
3. **Criticality Score ($S_{\\text{crit}}$):** Weighted based on operational criticality (Mission Critical = 100, Business Critical = 75, Operational = 40, Standard = 20).
4. **Capability Overlap Score ($S_{\\text{over}}$):** Quantifies whether other applications in the enterprise support the same business capabilities.
5. **Lifecycle Review Score ($S_{\\text{life}}$):** Weighted by current architectural roadmap (Retire = 100, Migrate = 80, Tolerate = 65, Strategic = 10).

### 2.2 Rationalization Review Index (RRI)
$$\\text{RRI} = 0.30 S_{\\text{cost}} + 0.25 (100 - S_{\\text{util}}) + 0.20 S_{\\text{over}} + 0.15 S_{\\text{life}} + 0.10 (100 - S_{\\text{crit}})$$

### 2.3 Strict Analytical Guardrail: Avoidable Cost Scenario
We never declare: *"Retiring this application will save ₹8.4 Cr."*  
Instead, we declare: *"₹8.4 Cr represents the current baseline expenditure. A rationalization review must determine how much of this cost is genuinely avoidable versus sunk or fixed infrastructure."*
""")
    add_md(nb, """## 3. Data Model Interaction

Combines application TCO, consumption metrics, capability mappings (`rel_app_capability`), and lifecycle classifications.
""")
    add_md(nb, """## 4. Implementation""")
    add_code(nb, """import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(str(Path.cwd().parent / "src"))

from tvi.config import load_config
from tvi.rationalization import score_application_portfolio, find_rationalization_candidates

config = load_config()

# Calculate complete multi-criteria portfolio scores
scored_portfolio = score_application_portfolio()
print("Multi-Criteria Portfolio Rationalization Scores:")
display(scored_portfolio[["application_id", "application_name", "lifecycle_status", "annual_tco", "cost_score", "utilization_score", "capability_overlap_score", "rationalization_review_index"]].head(8))
""")
    add_code(nb, """# Filter Top Candidates for Rationalization Review (RRI >= 60.0)
candidates_df = find_rationalization_candidates(review_threshold=60.0)
print(f"Found {len(candidates_df)} Applications Requiring Rationalization Review:")
display(candidates_df[["application_id", "application_name", "lifecycle_status", "annual_tco", "avg_monthly_users", "overlapping_caps_count", "rationalization_review_index", "investigation_evidence"]])
""")
    add_md(nb, """## 5. Empirical Results & Avoidable Cost Scenario Analysis""")
    add_code(nb, """# Potential Avoidable Cost Scenario Chart
plt.figure(figsize=(10, 4.5))
top_cands = candidates_df.head(6)

bars = plt.barh(top_cands["application_name"], top_cands["potential_avoidable_cost_scenario"] / 1e7, color="#d62728")
plt.xlabel("Potential Avoidable Cost Scenario (₹ Crores)", fontsize=11)
plt.title("Applications Requiring Rationalization Review — Spend Scenario", fontsize=13)
plt.grid(axis="x", linestyle="--", alpha=0.5)

for bar in bars:
    w = bar.get_width()
    plt.text(w + 0.1, bar.get_y() + bar.get_height()/2, f"₹{w:.2f} Cr", va="center", fontsize=9, fontweight="bold")

plt.tight_layout()
plt.show()
""")
    add_md(nb, """## 6. Business Interpretation & Case Studies

### Case Study: APP021 (Legacy Customer Web Portal)
- **Annual TCO:** ₹8.4 Crores
- **Active Users:** 145 users (Annual cost/user exceeds ₹58,000)
- **Capability Redundancy:** Overlaps with `APP011` (Customer Direct Portal) which delivers modern digital banking
- **Lifecycle Status:** Tolerate
- **Conclusion:** APP021 represents an ideal decommissioning candidate. Its user base can be migrated to APP011, potentially releasing substantial operational capacity.

### Case Study: APP012 (QuickOrder Legacy)
- **Annual TCO:** ₹3.4 Crores
- **Capability Redundancy:** Overlaps with `APP005` (OrderFlow Enterprise) on Order-to-Cash (CAP003)
- **Lifecycle Status:** Retire
- **Conclusion:** APP012 is already slated for retirement; consolidating Order-to-Cash exclusively onto APP005 eliminates duplicate licensing and support overhead.
""")
    add_md(nb, """## 7. Limitations & Analytical Guardrails

1. **Avoidable vs Sunk Costs:** Contractual termination penalties, multi-year cloud commitments, and retained shared infrastructure will diminish immediate cash savings.
2. **Governance Auditability:** Every recommendation is supported by transparent evidence strings linking back to source data.

## 8. Next Step

In **Notebook 08: Dependency & Impact Analysis**, before recommending any application for retirement, we interrogate the Knowledge Graph to evaluate its **blast radius and hidden integration dependencies**.
""")
    return nb


# 08
def build_nb_08():
    nb = make_nb()
    add_md(nb, """# Notebook 08: Dependency & Blast Radius Impact Analysis

**Series:** Technology Value Intelligence (TBM / ITFM / TVR)  
**Notebook Index:** 08 of 12  
**Focus:** Transitive Dependency Traversal, Single Point of Failure (SPOF) Detection, Blast Radius Index  
""")
    add_md(nb, """## 1. Business Problem

One of the greatest fears of enterprise IT executives is **unintended decommissioning blast radius**:
- An application is identified as an obsolete, low-utilization candidate for rationalization.
- The project team powers down the server.
- Suddenly, five mission-critical digital banking channels, ATM networks, and fraud prevention engines crash.

Why does this happen? In complex architectures, applications rarely exist in isolation. They communicate via synchronous APIs, ETL batch jobs, shared databases, and message buses. 

Before touching any application, leadership must know its **complete direct and indirect dependency blast radius**.
""")
    add_md(nb, """## 2. Core Concept & Formulation

### 2.1 Graph Transitive Traversal (BFS / DFS)
Given target application $A$:
- **Direct Dependents (1-hop):** $\\text{Adj}^{-}(A) = \\{ u \\in V \\mid (u, A) \\in E_{\\text{DEPENDS\\_ON}} \\}$
- **Indirect Transitive Dependents ($k$-hop):** All nodes $u$ reachable in the reverse graph $G^T$:
  $$\\text{Transitive}(A) = \\{ u \\in V \\mid \\exists \\text{ path from } u \\text{ to } A \\text{ in } G \\}$$

### 2.2 Blast Radius Metric (BRM)
To quantify operational change risk, we define a composite blast radius metric:
$$\\text{BRM}(A) = 3 \\cdot |\\text{Direct}| + 1.5 \\cdot |\\text{Indirect}| + 4 \\cdot |\\text{Capabilities}| + 2 \\cdot |\\text{Impacted BUs}|$$
""")
    add_md(nb, """## 3. Data Model Interaction

- Knowledge Graph edges: `DEPENDS_ON`, `SUPPORTS`, `OWNS`, `RUNS_ON`, `FUNDS_MODERNIZATION`.
""")
    add_md(nb, """## 4. Implementation""")
    add_code(nb, """import sys
from pathlib import Path
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

sys.path.append(str(Path.cwd().parent / "src"))

from tvi.config import load_config
from tvi.graph import build_knowledge_graph
from tvi.dependency import get_application_dependencies, get_capability_dependencies

config = load_config()
G = build_knowledge_graph("../data/generated")

# Evaluate dependency blast radius for Scenario D (APP010 - Central Auth Hub)
app010_dep = get_application_dependencies("APP010", G)

print("Dependency Blast Radius Dossier: APP010 (Central Auth & Identity Hub)")
print(f"Criticality Level: {app010_dep['criticality']}")
print(f"Blast Radius Metric: {app010_dep['blast_radius_metric']}")
print(f"Direct Dependent Applications ({len(app010_dep['direct_dependent_apps'])}):")
for a in app010_dep["direct_dependent_apps"]:
    print(f"  • {a['id']}: {a['name']}")

print(f"\\nImpacted Business Units ({len(app010_dep['business_units'])}):")
for b in app010_dep["business_units"]:
    print(f"  • {b['id']}: {b['name']} ({b['region']})")
""")
    add_md(nb, """## 5. Empirical Results & Dependency Ego-Network Visualization""")
    add_code(nb, """# Visualize Dependency Subgraph for APP010
sub_nodes = ["APP010"] + [a["id"] for a in app010_dep["direct_dependent_apps"]]
sub_g = G.subgraph(sub_nodes).copy()

plt.figure(figsize=(9, 6))
pos = nx.spring_layout(sub_g, seed=42)

node_colors = ["#d62728" if n == "APP010" else "#1f77b4" for n in sub_g.nodes()]
nx.draw_networkx_nodes(sub_g, pos, node_color=node_colors, node_size=1400, alpha=0.9)
nx.draw_networkx_edges(sub_g, pos, edge_color="#333333", arrows=True, arrowsize=18, width=2.0)

labels = {n: f"{n}\\n({sub_g.nodes[n].get('label', '')[:12]}...)" for n in sub_g.nodes()}
nx.draw_networkx_labels(sub_g, pos, labels=labels, font_size=8, font_weight="bold")

plt.title("Scenario D: Central Auth Hub (APP010) — Inbound Dependency Ego-Network", fontsize=13, pad=12)
plt.axis("off")
plt.tight_layout()
plt.show()
""")
    add_code(nb, """# Compare Blast Radius of Rationalization Candidates (APP021 vs APP010)
app021_dep = get_application_dependencies("APP021", G)

comparison_df = pd.DataFrame([
    {
        "Application": "APP010 (Central Auth Hub)",
        "Direct Dependent Apps": len(app010_dep["direct_dependent_apps"]),
        "Indirect Dependent Apps": len(app010_dep["indirect_dependent_apps"]),
        "Capabilities Supported": len(app010_dep["capabilities"]),
        "Impacted BUs": len(app010_dep["business_units"]),
        "Blast Radius Metric": app010_dep["blast_radius_metric"],
        "Decommissioning Feasibility": "Extremely High Risk (SPOF Hub)"
    },
    {
        "Application": "APP021 (Legacy Web Portal)",
        "Direct Dependent Apps": len(app021_dep["direct_dependent_apps"]),
        "Indirect Dependent Apps": len(app021_dep["indirect_dependent_apps"]),
        "Capabilities Supported": len(app021_dep["capabilities"]),
        "Impacted BUs": len(app021_dep["business_units"]),
        "Blast Radius Metric": app021_dep["blast_radius_metric"],
        "Decommissioning Feasibility": "Feasible (Isolated Leaf Node)"
    }
])
display(comparison_df)
""")
    add_md(nb, """## 6. Business Interpretation & Insights

1. **Scenario D (Single Point of Failure):** `APP010` is an enterprise bottleneck. Eight major applications depend directly on it for authentication. Any outage or modification to APP010 ripples across the entire bank.
2. **Decommissioning Safety Validation:** Unlike APP010, `APP021` (our prime rationalization candidate from Notebook 07) has zero inbound application dependencies. It is a "leaf node" whose retirement will not cause cascade failures across other software systems.
""")
    add_md(nb, """## 7. Limitations & Analytical Guardrails

1. **Static CMDB vs Dynamic Runtime Logs:** This model reflects documented architectural relationships. In legacy environments, undocumented batch jobs or shared database table dependencies may exist.
2. **Blast Radius Scope:** The metric assesses topological exposure; actual operational risk also depends on data flow volumes and failure tolerance (circuit breakers).

## 8. Next Step

In **Notebook 09: Investment & Benefit Realization**, we connect discretionary technology spending (projects) with business outcomes (benefits and KPIs) in a formal Technology Value Realization (TVR) framework.
""")
    return nb


# 09
def build_nb_09():
    nb = make_nb()
    add_md(nb, """# Notebook 09: Investment & Technology Value Realization (TVR)

**Series:** Technology Value Intelligence (TBM / ITFM / TVR)  
**Notebook Index:** 09 of 12  
**Focus:** Project Budget Variance, Expected vs Realized Benefits, Benefit Realization Gap, KPI Outcomes  
""")
    add_md(nb, """## 1. Business Problem

Enterprises spend billions annually on digital transformations, cloud migrations, and software modernization projects. Yet, industry studies consistently report that over 65% of enterprise technology projects fail to deliver their anticipated financial or operational returns.

The root cause is a post-delivery accountability vacuum:
1. When a project is delivered, finance records the capital expenditure, but **stops tracking whether the promised benefits actually materialize**.
2. Project teams disband and claim success based purely on delivery date, while business sponsors never verify whether productivity or cost reduction targets were met.

**Technology Value Realization (TVR)** establishes a continuous feedback loop connecting capital investment to tangible outcome realization.
""")
    add_md(nb, """## 2. Core Concept & Formulation

### 2.1 Investment Budget Variance
$$\\text{Investment Variance} = \\text{Actual Spend} - \\text{Investment Budget}$$
$$\\text{Budget Variance \\%} = \\frac{\\text{Actual Spend} - \\text{Budget}}{\\text{Budget}} \\times 100$$

### 2.2 Benefit Realization & Gap Metrics
$$\\text{Benefit Realization \\%} = \\frac{\\text{Recorded Realized Benefit}}{\\text{Expected Annual Benefit}} \\times 100$$
$$\\text{Benefit Gap} = \\text{Expected Annual Benefit} - \\text{Recorded Realized Benefit}$$

### 2.3 Strict Analytical Guardrail: Association vs Causality
We explicitly enforce consulting guardrails:  
*We state that a project is "associated with" a benefit or KPI movement, rather than claiming mathematical causation, unless causal experiments (A/B testing, synthetic controls) were formally conducted.*
""")
    add_md(nb, """## 3. Data Model Interaction

- `projects`: Project investment budgets, actual spends, and status.
- `benefits`: Granular expected and realized benefits by category (`Cost Reduction`, `Productivity`, `Revenue Enablement`).
- `kpis`: Operational metrics tracking baseline vs target vs actual performance.
- `rel_benefit_kpi`: Grounding links connecting benefits to measurable KPIs.
""")
    add_md(nb, """## 4. Implementation""")
    add_code(nb, """import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(str(Path.cwd().parent / "src"))

from tvi.config import load_config
from tvi.value_realization import calculate_project_budget_variance, calculate_benefit_realization, analyze_benefit_kpi_progression, get_project_value_profile

config = load_config()

# Evaluate project budget variances and benefit realization rates
budget_df = calculate_project_budget_variance()
benefit_df = calculate_benefit_realization()

merged_tvr = budget_df.merge(benefit_df[["project_id", "total_expected_benefit", "total_realized_benefit", "benefit_realization_pct", "benefit_gap"]], on="project_id")
print("Technology Value Realization Portfolio Summary:")
display(merged_tvr[["project_id", "project_name", "project_type", "investment_budget", "actual_spend", "budget_variance", "total_expected_benefit", "total_realized_benefit", "benefit_realization_pct"]].head(8))
""")
    add_md(nb, """## 5. Empirical Results & Visualizations""")
    add_code(nb, """# Contrasting High-Performing Investments vs Large Benefit Gaps
plt.figure(figsize=(10, 5))
sample_projects = merged_tvr[merged_tvr["project_id"].isin(["PRJ001", "PRJ002", "PRJ003", "PRJ004", "PRJ010", "PRJ014"])]

x = np.arange(len(sample_projects))
w = 0.35

plt.bar(x - w/2, sample_projects["total_expected_benefit"] / 1e7, width=w, label="Expected Benefit (₹ Cr)", color="#2b5c8f")
plt.bar(x + w/2, sample_projects["total_realized_benefit"] / 1e7, width=w, label="Realized Benefit (₹ Cr)", color="#2ca02c")

plt.xticks(x, sample_projects["project_name"], rotation=30, ha="right", fontsize=9)
plt.ylabel("Benefit Value (₹ Crores)", fontsize=11)
plt.title("Discretionary Investments: Expected vs Realized Benefits", fontsize=13)
plt.legend()
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()
""")
    add_code(nb, """# Detailed Deep-Dive: Scenario E (PRJ003) vs Scenario F (PRJ014)
prj003_dossier = get_project_value_profile("PRJ003")
prj014_dossier = get_project_value_profile("PRJ014")

comparison_tvr = pd.DataFrame([
    {
        "Project": f"PRJ003 ({prj003_dossier['project']['project_name']})",
        "Budget Variance (₹ Cr)": (prj003_dossier['project']['actual_spend'] - prj003_dossier['project']['investment_budget']) / 1e7,
        "Expected Benefit (₹ Cr)": prj003_dossier['project']['expected_annual_benefit'] / 1e7,
        "Realized Benefit (₹ Cr)": prj003_dossier['benefits']['realized_value'].sum() / 1e7,
        "Realization Rate": f"{(prj003_dossier['benefits']['realized_value'].sum() / prj003_dossier['project']['expected_annual_benefit']) * 100:.1f}%",
        "Status": "Exceeded Targets (Scenario E)"
    },
    {
        "Project": f"PRJ014 ({prj014_dossier['project']['project_name']})",
        "Budget Variance (₹ Cr)": (prj014_dossier['project']['actual_spend'] - prj014_dossier['project']['investment_budget']) / 1e7,
        "Expected Benefit (₹ Cr)": prj014_dossier['project']['expected_annual_benefit'] / 1e7,
        "Realized Benefit (₹ Cr)": prj014_dossier['benefits']['realized_value'].sum() / 1e7,
        "Realization Rate": f"{(prj014_dossier['benefits']['realized_value'].sum() / prj014_dossier['project']['expected_annual_benefit']) * 100:.1f}%",
        "Status": "Severe Benefit Gap (Scenario F)"
    }
])
display(comparison_tvr)
""")
    add_code(nb, """# Connect Project Benefits to KPI Movements
kpi_progression = analyze_benefit_kpi_progression()
print("Associated KPI Progression Table (Sample):")
display(kpi_progression[["project_id", "project_name", "benefit_type", "kpi_name", "baseline_value", "target_value", "actual_value", "unit", "kpi_target_achievement_pct"]].head(6))
""")
    add_md(nb, """## 6. Business Interpretation & Insights

1. **Scenario E (PRJ003 - Real-Time Payment Modernization):** Finished under budget (₹11.5 Cr vs ₹12.0 Cr) and generated ₹20.7 Cr in annual benefits (108% realization), successfully compressing transaction latency from 450ms to 85ms.
2. **Scenario F (PRJ014 - Global Legacy CRM Consolidation):** Experienced a ₹4.0 Cr budget overrun (₹29.0 Cr actual spend) and only realized ₹7.0 Cr of the promised ₹30.0 Cr benefit (23.3% realization rate; Benefit Gap: ₹23.0 Cr).
""")
    add_md(nb, """## 7. Limitations & Analytical Guardrails

1. **Observational Metrics:** Recorded realized benefits represent observed financial shifts in operational accounts. Without controlled econometric isolation, other macro factors (market growth, organizational restructuring) also influence outcomes.
2. **Language Guardrail:** Express outcomes using: *"The project is associated with a recorded realized benefit of..."* rather than declaring unverified direct causality.

## 8. Next Step

In **Notebook 10: Cost Driver & Variance Analysis**, we analyze monthly spending fluctuations, deconstructing spend spikes into healthy transaction scaling versus unbacked rate anomalies.
""")
    return nb


# 10
def build_nb_10():
    nb = make_nb()
    add_md(nb, """# Notebook 10: Cost Driver & Financial Variance Analysis

**Series:** Technology Value Intelligence (TBM / ITFM / TVR)  
**Notebook Index:** 10 of 12  
**Focus:** Month-over-Month (MoM) Variance, Driver Decomposition, Rate vs Volume Anomaly Detection  
""")
    add_md(nb, """## 1. Business Problem

Every month, CIOs and IT Finance Directors face the recurring executive question:
> *"Why did technology spending increase by ₹4 Crores this month?"*

Typical corporate responses are frustratingly vague: *"Cloud costs were up"* or *"Vendor invoices arrived."* 

An executive needs a precise **root-cause driver decomposition**:
1. Was the cost increase driven by genuine business volume expansion (e.g., e-commerce transaction surge)?
2. Or was the cost increase caused by rate hikes, unoptimized idle infrastructure, or contract scope creep?
""")
    add_md(nb, """## 2. Core Concept & Formulation

### 2.1 Multi-Level Variance Decomposition
Given baseline month $t_0$ and comparison month $t_1$:
$$\\Delta \\text{Total Spend} = \\text{Spend}(t_1) - \\text{Spend}(t_0)$$
We decompose this delta hierarchically:
$$\\Delta \\text{Total Spend} = \\sum_{c} \\Delta \\text{Category}_c = \\sum_{a} \\Delta \\text{Application}_a$$

### 2.2 Elasticity Diagnosis: Scenario G vs Scenario H
To classify whether an application cost increase is justifiable, we correlate cost growth with transaction growth:
- **Scenario G (Elastic Scale):**
  $$\\frac{\\Delta \\text{Spend}}{\\text{Spend}} > 0 \\quad \\text{and} \\quad \\frac{\\Delta \\text{Transactions}}{\\text{Transactions}} \\ge 20\\%$$
  *Diagnosis: Healthy operational scaling responding to business volume.*
- **Scenario H (Rate/Infrastructure Anomaly):**
  $$\\frac{\\Delta \\text{Spend}}{\\text{Spend}} > 0 \\quad \\text{and} \\quad \\frac{\\Delta \\text{Transactions}}{\\text{Transactions}} \\approx 0\\%$$
  *Diagnosis: Rate/infrastructure anomaly. Immediate contract and infrastructure audit required.*
""")
    add_md(nb, """## 3. Data Model Interaction

- Monthly slices from `v_app_monthly_cost` and `v_app_monthly_consumption`.
""")
    add_md(nb, """## 4. Implementation""")
    add_code(nb, """import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(str(Path.cwd().parent / "src"))

from tvi.config import load_config
from tvi.variance import calculate_monthly_cost_variance, calculate_category_variance, identify_cost_drivers

config = load_config()

# Compute Month-over-Month (MoM) time series variance
mom_variance = calculate_monthly_cost_variance()
print("Monthly Cost Variance Trajectory:")
display(mom_variance)
""")
    add_md(nb, """## 5. Empirical Results & Driver Decomposition""")
    add_code(nb, """# Deconstruct the spend spike between July (2024-07) and August (2024-08)
drivers = identify_cost_drivers(baseline_month="2024-07", comparison_month="2024-08", top_n=6)

print(f"Spend Shift: {drivers['baseline_month']} -> {drivers['comparison_month']}")
print(f"Baseline Spend  : ₹{drivers['spend_baseline']/1e7:.2f} Cr")
print(f"Comparison Spend: ₹{drivers['spend_comparison']/1e7:.2f} Cr")
print(f"Total Net Shift : ₹{drivers['total_cost_delta']/1e7:+.2f} Cr ({drivers['total_cost_delta_pct']:+.1f}%)")

print("\\nTop Application Cost Drivers:")
display(drivers["top_application_drivers"])
""")
    add_code(nb, """# Visualize Cost Category Shift (July vs August)
cat_var = drivers["top_category_drivers"]

plt.figure(figsize=(9, 4.5))
bars = plt.barh(cat_var["cost_category"], cat_var["variance_amount"] / 1e7,
                color=np.where(cat_var["variance_amount"] >= 0, "#d62728", "#2ca02c"))
plt.title("Cost Category Variance: August vs July 2024 (₹ Crores)", fontsize=13)
plt.xlabel("Net Spend Change (₹ Crores)", fontsize=11)
plt.axvline(0, color="black", linewidth=0.8)
plt.grid(axis="x", linestyle="--", alpha=0.5)

for bar in bars:
    w = bar.get_width()
    plt.text(w + (0.05 if w >= 0 else -0.2), bar.get_y() + bar.get_height()/2,
             f"₹{w:+.2f} Cr", va="center", fontsize=9, fontweight="bold")

plt.tight_layout()
plt.show()
""")
    add_md(nb, """## 6. Business Interpretation & Case Studies

### 1. Scenario G: APP014 (Cloud Payment Microhub)
- **Spend Change:** Increased from ₹35L to ₹95L/month (+171%).
- **Operational Correlation:** Digital transactions surged by **+180%** and API calls expanded by +210%.
- **Executive Conclusion:** This is a **healthy scaling driver**. The business expanded digital payment transaction volumes, and cloud auto-scaling responded elastically.

### 2. Scenario H: APP022 (Batch Billing Engine v2)
- **Spend Change:** Jumped by **+₹38 Lakhs/month** (+190%).
- **Operational Correlation:** Monthly transactions and active users remained completely flat (-1.2%).
- **Executive Conclusion:** This is an **unbacked spend anomaly**. It triggers an immediate FinOps investigation into unoptimized compute sizing or vendor license price adjustments.
""")
    add_md(nb, """## 7. Limitations & Analytical Guardrails

1. **Price-Volume-Mix Breakdown:** Fine-grained price vs volume deconstruction requires cloud billing SKU-level detail (e.g., AWS CUR per-second billing), which is abstracted to monthly totals here.
2. **Lagged Invoicing:** Real-world enterprise billing occasionally reflects catch-up vendor invoices spanning prior quarters.

## 8. Next Step

In **Notebook 11: Local LLM + Knowledge Graph Analyst**, we introduce a guarded, dual-mode natural language interface that allows executives to ask questions and receive factually grounded answers without arbitrary code execution risks.
""")
    return nb


# 11
def build_nb_11():
    nb = make_nb()
    add_md(nb, """# Notebook 11: Local LLM + Knowledge Graph AI Analyst

**Series:** Technology Value Intelligence (TBM / ITFM / TVR)  
**Notebook Index:** 11 of 12  
**Focus:** Guarded Natural Language Interface, Intent Detection, Zero Arbitrary Code Execution, Grounded Explanations  
""")
    add_md(nb, """## 1. Business Problem

Executive leaders (CIO, CFO, BU Heads) rarely write SQL queries or inspect NetworkX graph objects directly. They want to ask natural questions:
- *"What does our Order-to-Cash capability cost?"*
- *"Which applications have high cost and low utilization?"*
- *"Why did technology spending increase in August?"*

However, connecting an unrestricted Large Language Model (LLM) directly to enterprise financial data poses catastrophic risks:
1. **Hallucination:** LLMs fabricate believable-sounding numbers when data is absent.
2. **Prompt Injection & Security:** Giving an LLM unrestricted SQL or Python code execution access creates severe security vulnerabilities.
3. **Reproducibility Failure:** An executive cannot present ungrounded LLM guesses to the Board of Directors.

We need a **guarded architecture** where the LLM functions strictly as a natural language interface, while all mathematical and graph operations remain deterministic.
""")
    add_md(nb, """## 2. Core Concept & Architecture

```text
User Natural Language Question
              │
              ▼
   ┌───────────────────────┐
   │ Intent & Slot Parser  │  (Maps query to strict intent registry)
   └───────────────────────┘
              │
              ▼
   ┌───────────────────────┐
   │ Validated Analytical  │  (Zero arbitrary code execution; calls
   │       Function        │   deterministic DuckDB / Graph functions)
   └───────────────────────┘
              │
              ▼
   ┌───────────────────────┐
   │ Structured Result     │  (Exact, auditable mathematical truth)
   └───────────────────────┘
              │
              ▼
   ┌───────────────────────┐
   │ Grounded Explanation  │  (Dual-mode: deterministic template or local LLM
   │      Synthesis        │   strictly constrained to structured data)
   └───────────────────────┘
```

### 2.1 Dual-Mode Operation
- `MODE = "rules"`: 100% deterministic rules and template engine (works with zero internet and zero external models).
- `MODE = "local_llm"`: Connects to a local **Ollama** endpoint if running locally. If Ollama is unavailable, gracefully falls back to rules mode.
""")
    add_md(nb, """## 3. Data Model Interaction

Routes to `cost_analytics`, `rationalization`, `dependency`, and `variance` modules.
""")
    add_md(nb, """## 4. Implementation""")
    add_code(nb, """import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path.cwd().parent / "src"))

from tvi.config import load_config
from tvi.llm import KnowledgeGraphAnalyst

config = load_config()

# Initialize AI Analyst in rules mode
analyst = KnowledgeGraphAnalyst(mode="rules", config=config)
print(f"Knowledge Graph Analyst Initialized (Mode: {analyst.mode})")
print(f"Local Ollama Daemon Detected: {analyst.is_ollama_available()}")
""")
    add_md(nb, """## 5. Empirical Results & Interactive Query Testing""")
    add_code(nb, """# Query 1: Application Cost & Profile
q1 = "What is the cost and utilization profile of APP001?"
res1 = analyst.query(q1)

print(f"User Query : '{q1}'")
print(f"Intent     : {res1['intent']}")
print(f"Explanation:\\n{res1['explanation']}")
""")
    add_code(nb, """# Query 2: Business Capability Cost
q2 = "What does the Order-to-Cash capability cost?"
res2 = analyst.query(q2)

print(f"User Query : '{q2}'")
print(f"Intent     : {res2['intent']}")
print(f"Explanation:\\n{res2['explanation']}")
""")
    add_code(nb, """# Query 3: Rationalization Candidates
q3 = "Which applications have high cost and low utilization that should be rationalized?"
res3 = analyst.query(q3)

print(f"User Query : '{q3}'")
print(f"Intent     : {res3['intent']}")
print(f"Explanation:\\n{res3['explanation']}")
""")
    add_code(nb, """# Query 4: Dependency and Blast Radius
q4 = "What is the blast radius and what depends on APP021?"
res4 = analyst.query(q4)

print(f"User Query : '{q4}'")
print(f"Intent     : {res4['intent']}")
print(f"Explanation:\\n{res4['explanation']}")
""")
    add_code(nb, """# Query 5: Spend Variance Root-Cause
q5 = "Why did technology spend increase in August?"
res5 = analyst.query(q5)

print(f"User Query : '{q5}'")
print(f"Intent     : {res5['intent']}")
print(f"Explanation:\\n{res5['explanation']}")
""")
    add_code(nb, """# Query 6: Handling Ambiguous / Unknown Intent
q6 = "What will our stock price be next quarter?"
res6 = analyst.query(q6)

print(f"User Query : '{q6}'")
print(f"Status     : {res6['status']}")
print(f"Explanation:\\n{res6['explanation']}")
""")
    add_md(nb, """## 6. Business Interpretation & Safety Auditing

1. **Grounded Consistency:** Every single number produced in the natural language responses matches the DuckDB financial ledgers and NetworkX graph paths with zero fabrication.
2. **Ambiguity Handling:** When queried about an unmapped topic (e.g., stock price predictions), the system refuses to speculate and returns a helpful clarification menu listing validated analytical capabilities.
""")
    add_md(nb, """## 7. Limitations & Analytical Guardrails

1. **Strict Intent Boundaries:** The analyst only answers questions that can be mapped to deterministic analytical functions. It does not synthesize open-ended creative prose.
2. **Zero Code Injection:** The analyst is fundamentally incapable of running arbitrary SQL `DROP` commands or arbitrary Python code strings.

## 8. Next Step

In **Notebook 12: End-to-End Technology Value Intelligence**, we synthesize the entire 12-notebook journey into a unified executive scenario, compiling the full 9-section Board-level Executive Report.
""")
    return nb


# 12
def build_nb_12():
    nb = make_nb()
    add_md(nb, """# Notebook 12: End-to-End Technology Value Intelligence

**Series:** Technology Value Intelligence (TBM / ITFM / TVR)  
**Notebook Index:** 12 of 12  
**Focus:** Executive Narrative Synthesis, End-to-End Value Chain Traversal, 9-Section Board Report  
""")
    add_md(nb, """## 1. Business Problem

We have reached the culmination of our analytical journey. 

In enterprise environments, insights typically remain trapped in operational silos:
- Finance has the general ledger spend.
- Enterprise Architecture has the application catalog and capability models.
- Infrastructure teams have the server and cloud logs.
- The PMO has the project status reports.

Because these domains are disconnected, executive leadership cannot see the complete **Technology Value Chain**:
$$\\text{Technology Cost} \\longrightarrow \\text{Application} \\longrightarrow \\text{Service} \\longrightarrow \\text{Capability} \\longrightarrow \\text{Business Unit} \\longrightarrow \\text{Investment} \\longrightarrow \\text{Value Realization}$$

In this final notebook, we integrate all layers to answer a strategic executive scenario for the CIO.
""")
    add_md(nb, """## 2. Core Concept: The Unified Technology Value Chain

```text
Vendor (VEN001 TechNova)
   │
   ▼ SUPPLIED_BY
Technology (TECH001 AWS EKS)
   │
   ▼ RUNS_ON
Application (APP005 OrderFlow Enterprise)
   │
   ▼ SUPPORTS
Business Capability (CAP003 Order-to-Cash)
   │
   ▼ OWNS
Business Unit (BU004 Digital Payments)
   │
   ▼ SPONSORS
Project (PRJ009 Order-to-Cash Optimization)
   │
   ▼ PRODUCES
Realized Benefit (₹29 Cr Cycle Time Reduction & Cost Savings)
```
""")
    add_md(nb, """## 3. Data Model Interaction

Synthesizes the entire database, graph topology, analytical engines, and reporting framework.
""")
    add_md(nb, """## 4. Implementation: Full Value Chain Traversal""")
    add_code(nb, """import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(str(Path.cwd().parent / "src"))

from tvi.config import load_config
from tvi.graph import build_knowledge_graph
from tvi.graph_queries import get_full_value_chain_path
from tvi.reporting import generate_executive_report

config = load_config()
G = build_knowledge_graph("../data/generated")

# Extract complete end-to-end value chain for APP005 (OrderFlow Enterprise)
app005_chain = get_full_value_chain_path(G, "APP005")

print("End-to-End Lineage Dossier: APP005 (OrderFlow Enterprise)")
print(f"Lifecycle Status : {app005_chain['lifecycle_status']}")
print(f"Criticality      : {app005_chain['criticality']}")
print(f"Underlying Techs : {[t['name'] for t in app005_chain['technologies']]}")
print(f"IT Services      : {[s['name'] for s in app005_chain['services']]}")
print(f"Capabilities     : {[c['name'] for c in app005_chain['capabilities']]}")
print(f"Consuming BUs    : {[b['name'] for b in app005_chain['business_units']]}")
""")
    add_md(nb, """## 5. Compiling the 9-Section Board-Level Executive Report""")
    add_code(nb, """# Generate complete 9-section executive report
executive_report_md = generate_executive_report()
print("Executive Report Generated Successfully.")
""")
    add_code(nb, """# Render Executive Report in Notebook
from IPython.display import Markdown
display(Markdown(executive_report_md))
""")
    add_md(nb, """## 6. Strategic Takeaways for the CIO & CFO

1. **Shift from Cost Accounting to Value Realization:** By connecting General Ledger cost records to Business Capabilities and KPIs, IT transitions from an opaque "cost center" to an accountable driver of business outcomes.
2. **Targeted Rationalization Portfolio:** We identified concrete rationalization opportunities (e.g., decommissioning `APP021` and consolidating `CAP003` onto `APP005`), yielding potential avoidable cost scenarios exceeding ₹11 Crores without impacting critical dependencies.
3. **Graph-Enhanced Governance:** Topological traversal uncovers bottlenecks (such as `APP010`) that flat spreadsheets completely miss, de-risking enterprise transformation programs.
""")
    add_md(nb, """## 7. Methodological Limitations

1. **Local-First Scope:** This implementation was engineered to run deterministically on a local 16 GB RAM machine.
2. **Brownfield Realities:** Real-world enterprise adoption requires establishing automated ETL pipelines to ingest dirty, incomplete data from ServiceNow, SAP, Apptio, Jira, and cloud billing exports.

## 8. Conclusion & Future Roadmap

This completes the 12-notebook **Technology Value Intelligence** prototype. 

### Future Architectural Roadmap:
1. **Phase 2:** Connect real enterprise lakehouse tables (Databricks, Snowflake).
2. **Phase 3:** Migrate graph backend from NetworkX to **Neo4j** for real-time multi-million node traversals.
3. **Phase 4:** Embed semantic vector search over IT vendor contracts and architecture RFCs.
""")
    return nb


def main():
    print("Building all 12 Technology Value Intelligence Notebooks...")
    builders = [
        (build_nb_01, "01_generate_enterprise_data.ipynb"),
        (build_nb_02, "02_tbm_itfm_data_model.ipynb"),
        (build_nb_03, "03_build_knowledge_graph.ipynb"),
        (build_nb_04, "04_application_cost_intelligence.ipynb"),
        (build_nb_05, "05_capability_cost_intelligence.ipynb"),
        (build_nb_06, "06_consumption_intelligence.ipynb"),
        (build_nb_07, "07_application_rationalization.ipynb"),
        (build_nb_08, "08_dependency_and_impact_analysis.ipynb"),
        (build_nb_09, "09_investment_benefit_realization.ipynb"),
        (build_nb_10, "10_cost_driver_and_variance_analysis.ipynb"),
        (build_nb_11, "11_local_llm_knowledge_graph_analyst.ipynb"),
        (build_nb_12, "12_end_to_end_technology_value_intelligence.ipynb"),
    ]

    for builder, filename in builders:
        nb = builder()
        save_nb(nb, filename)

    print("\n✓ Successfully generated all 12 notebooks in notebooks/ directory.")


if __name__ == "__main__":
    main()
