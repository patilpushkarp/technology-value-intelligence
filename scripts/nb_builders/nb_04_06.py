"""Builders for Notebooks 04, 05, and 06 with exhaustive analytical depth."""

from scripts.nb_builders.common import make_nb, add_md, add_code, save_nb


# ==============================================================================
# Notebook 04: Application Cost Intelligence & Unit Economics
# ==============================================================================
def build_notebook_04():
    nb = make_nb()

    add_md(nb, """# Notebook 04: Application Cost Intelligence & Unit Economics

**Series:** Technology Value Intelligence (TBM / ITFM / TVR)  
**Notebook Index:** 04 of 12  
**Focus:** Fully-Burdened Application TCO, Unit Economics Modeling, Pareto Spend Concentration, Elasticity Dynamics  

---

## 1. Business Problem

Most enterprise IT organizations track application software licenses, but severely underestimate true **Application Total Cost of Ownership (TCO)**. Software licenses often represent less than 35% of an application's true operational burden:
- **Internal & External Labor:** Dedicated engineering, operations, and support staff.
- **Dedicated & Shared Infrastructure:** Cloud compute instances, storage buckets, database clusters, and physical servers.
- **Third-Party Support & Vendor Contracts:** Ancillary monitoring, tooling, and maintenance.

Furthermore, aggregate cost alone does not tell an executive whether an application is efficient. An application costing ₹15 Crores supporting 10,000 active users is vastly more cost-effective than an application costing ₹5 Crores supporting only 50 users. We must evaluate **Unit Economics**.

---

## 2. Core Concept & Formulation

### 2.1 Fully-Burdened Application TCO
$$\\text{TCO}(\\text{App}) = \\text{Software} + \\text{Internal Labor} + \\text{Cloud} + \\text{Infrastructure} + \\text{Vendor Services}$$

### 2.2 Unit Economics Metrics
To normalize cost by operational delivery, we define:
$$\\text{Annual Cost per Active User} = \\frac{\\text{Annual TCO}}{\\text{Average Monthly Active Users}}$$
$$\\text{Cost per Digital Transaction} = \\frac{\\text{Annual TCO}}{\\text{Annual Transaction Volume}}$$
*Safe Zero Handling:* In cases where an application operates in batch or back-office mode with zero interactive users, the denominator is guarded to prevent division-by-zero errors.

### 2.3 Pareto Concentration (80/20 Rule)
We compute cumulative spend share to identify the critical subset of applications that drive the majority of enterprise technology costs.
""")

    add_code(nb, """import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

workspace_root = Path.cwd().parent
sys.path.insert(0, str(workspace_root / "src"))

from tvi.config import load_config
from tvi.cost_analytics import calculate_application_tco, get_application_profile
from tvi.database import get_database

config = load_config()
db = get_database(config.database.path)

# Compute fully burdened TCO and unit economics
app_tco_df = calculate_application_tco()
print("Application Cost Intelligence Table Compiled:")
display(app_tco_df[["application_id", "application_name", "lifecycle_status", "annual_tco", "avg_monthly_users", "annual_cost_per_user", "cost_per_transaction", "cumulative_spend_pct"]].head(8))
""")

    add_md(nb, """---

## 3. Cost Stack Decomposition Across Categories

We unpack the composition of each application's annual TCO across **all cost categories**: Software, Internal Labor, Cloud, and Infrastructure:
""")

    add_code(nb, """# Top 15 Applications Cost Stack Breakdown
top_15 = app_tco_df.head(15)

plt.figure(figsize=(11, 5.5))
bar_w = 0.65
x = np.arange(len(top_15))

p1 = plt.bar(x, top_15["software_cost"] / 1e7, width=bar_w, label="Software / License", color="#1f77b4")
p2 = plt.bar(x, top_15["people_cost"] / 1e7, bottom=top_15["software_cost"] / 1e7, width=bar_w, label="People / Labor", color="#ff7f0e")
p3 = plt.bar(x, top_15["cloud_cost"] / 1e7, bottom=(top_15["software_cost"] + top_15["people_cost"]) / 1e7, width=bar_w, label="Cloud Services", color="#2ca02c")
p4 = plt.bar(x, top_15["infra_cost"] / 1e7, bottom=(top_15["software_cost"] + top_15["people_cost"] + top_15["cloud_cost"]) / 1e7, width=bar_w, label="Shared Infrastructure", color="#d62728")

plt.xticks(x, top_15["application_id"], rotation=45, ha="right", fontsize=9)
plt.ylabel("Annual Spend (₹ Crores)", fontsize=11)
plt.title("Top 15 Applications: Fully-Burdened Cost Stack Decomposition", fontsize=13)
plt.legend(loc="upper right")
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()
""")

    add_md(nb, """---

## 4. Pareto Spend Concentration & Lorenz Curve

We plot the Lorenz curve of cumulative portfolio spend against cumulative application count to identify portfolio concentration:
""")

    add_code(nb, """# Pareto 80/20 Lorenz Curve Analysis
sorted_spend = app_tco_df["annual_tco"].sort_values(ascending=False).values
cum_spend = np.cumsum(sorted_spend) / np.sum(sorted_spend) * 100.0
app_ranks = np.arange(1, len(sorted_spend) + 1) / len(sorted_spend) * 100.0

plt.figure(figsize=(8, 4.5))
plt.plot(app_ranks, cum_spend, color="#2b5c8f", linewidth=3, label="Cumulative Spend % (Actual)")
plt.plot([0, 100], [0, 100], color="grey", linestyle="--", label="Equal Distribution Baseline")
plt.axhline(80, color="#d62728", linestyle=":", alpha=0.8, label="80% Spend Threshold")

# Find app count reaching 80% spend
idx_80 = np.where(cum_spend >= 80.0)[0][0] + 1
pct_apps_80 = (idx_80 / len(sorted_spend)) * 100.0
plt.axvline(pct_apps_80, color="#d62728", linestyle=":")
plt.scatter([pct_apps_80], [80], color="#d62728", zorder=5)
plt.annotate(f"{idx_80} apps ({pct_apps_80:.1f}%) = 80% Spend", xy=(pct_apps_80, 80),
             xytext=(pct_apps_80 + 5, 70), arrowprops=dict(facecolor="black", shrink=0.05, width=1))

plt.xlabel("% of Application Portfolio", fontsize=11)
plt.ylabel("% of Total Technology Spend", fontsize=11)
plt.title("Application Portfolio: Pareto Spend Concentration Curve", fontsize=13)
plt.legend(loc="lower right")
plt.grid(True, linestyle="--", alpha=0.4)
plt.tight_layout()
plt.show()
""")

    add_md(nb, """---

## 5. Interactive Unit Economics Explorer (Plotly)

We create an interactive Plotly bubble chart showing TCO vs Active Users, sized by Annual Cost per User:
""")

    add_code(nb, """fig = px.scatter(
    app_tco_df,
    x="avg_monthly_users",
    y="annual_tco",
    size="annual_cost_per_user",
    color="lifecycle_status",
    hover_name="application_name",
    hover_data={"application_id": True, "annual_tco": ":,.0f", "avg_monthly_users": ":.0f", "annual_cost_per_user": ":,.2f", "cost_per_transaction": ":.4f"},
    title="Application Unit Economics: Spend vs Scale (Bubble Size = Annual Cost/User)",
    labels={"avg_monthly_users": "Average Monthly Active Users", "annual_tco": "Annual TCO (₹)", "lifecycle_status": "Lifecycle"},
    color_discrete_map={"Strategic": "#2ca02c", "Tolerate": "#ff7f0e", "Migrate": "#1f77b4", "Retire": "#d62728"},
    template="plotly_white"
)
fig.update_layout(yaxis=dict(tickformat="~s"))
fig.show()
""")

    add_md(nb, """---

## 6. Sensitivity Analysis: User Volume Decline Simulation

What happens to unit costs if a corporate divestiture or market shift causes a **30% decline in active user volume** while fixed application costs remain locked?
""")

    add_code(nb, """# Simulate -30% User Volume Shift
sim_df = app_tco_df.copy()
sim_df["simulated_users"] = (sim_df["avg_monthly_users"] * 0.70).round(0)
sim_df["simulated_cost_per_user"] = np.where(
    sim_df["simulated_users"] > 0,
    (sim_df["annual_tco"] / sim_df["simulated_users"]).round(2),
    0.0
)
sim_df["unit_cost_escalation_pct"] = (
    (sim_df["simulated_cost_per_user"] - sim_df["annual_cost_per_user"]) / sim_df["annual_cost_per_user"] * 100.0
).round(1)

print("Sensitivity Simulation: Impact of -30% User Adoption on Unit Cost:")
display(sim_df[["application_id", "application_name", "avg_monthly_users", "simulated_users", "annual_cost_per_user", "simulated_cost_per_user", "unit_cost_escalation_pct"]].head(6))
""")

    add_md(nb, """## 7. Limitations & Analytical Guardrails

1. **Fixed vs Variable Cost Realities:** Unit costs (TCO / users) assume simple proportional allocation. In reality, a large portion of software license and infrastructure cost is fixed. A 50% decrease in active users does not automatically reduce total application spend by 50%.
2. **Non-User Applications:** Middleware, batch ETL systems, and security daemons deliver enterprise value without direct interactive end-users; their unit economics must be evaluated via transaction and API volumes.

## 8. Next Step

In **Notebook 05: Capability Cost Intelligence**, we elevate our financial lens from individual applications to **Business Capabilities**, solving the critical challenge of allocating shared IT services without double-counting.
""")

    return nb


# ==============================================================================
# Notebook 05: Business Capability Cost Intelligence & Shared Attribution
# ==============================================================================
def build_notebook_05():
    nb = make_nb()

    add_md(nb, """# Notebook 05: Business Capability Cost Intelligence & Shared Attribution

**Series:** Technology Value Intelligence (TBM / ITFM / TVR)  
**Notebook Index:** 05 of 12  
**Focus:** Business Capability Costing, Shared Infrastructure Allocation, Avoiding Double-Counting, Sankey Flow  

---

## 1. Business Problem

CFOs and Business Unit leaders do not purchase "applications" for their own sake; they fund **Business Capabilities** (e.g., Order-to-Cash, Procure-to-Pay, Fraud Detection, Regulatory Reporting). 

When executive leadership asks:
> *"What does our Order-to-Cash capability actually cost?"*

Conventional IT accounting fails because:
1. Capabilities are supported by multiple applications concurrently.
2. A single enterprise application often supports multiple capabilities simultaneously.
3. Common shared infrastructure (networks, storage arrays, security operations) is shared across capabilities without clear boundaries.

Without a rigorous allocation model, organizations suffer from **double-counting** or unallocated financial "slush funds".

---

## 2. Core Concept & Formulation

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

    add_code(nb, """import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

workspace_root = Path.cwd().parent
sys.path.insert(0, str(workspace_root / "src"))

from tvi.config import load_config
from tvi.cost_analytics import calculate_capability_cost, calculate_application_tco, get_capability_profile
from tvi.database import get_database

config = load_config()
db = get_database(config.database.path)

# Compute complete capability cost attribution
cap_cost_df = calculate_capability_cost()
print("Business Capability Cost Intelligence Compiled:")
display(cap_cost_df[["capability_id", "capability_name", "strategic_priority", "criticality", "supported_apps_count", "direct_app_cost", "shared_infra_allocated", "total_capability_cost", "cost_per_transaction"]].head(8))
""")

    add_md(nb, """---

## 3. Double-Counting Prevention Audit

We mathematically prove that the sum of all capability allocations reconciles to the exact rupee with total enterprise technology spend in DuckDB:
$$\\sum_{c \\in \\text{Capabilities}} \\text{Capability Cost}(c) \\equiv \\text{Total Enterprise Technology Spend}$$
""")

    add_code(nb, """total_cap_spend = cap_cost_df["total_capability_cost"].sum()
total_direct = cap_cost_df["direct_app_cost"].sum()
total_shared = cap_cost_df["shared_infra_allocated"].sum()
gross_spend = db.get_total_cost()

recon_proof = pd.DataFrame([
    {"Component": "Total Direct App Allocations", "Amount (₹)": total_direct},
    {"Component": "Total Shared Infra Allocations", "Amount (₹)": total_shared},
    {"Component": "Sum of Capability Costs", "Amount (₹)": total_cap_spend},
    {"Component": "Gross Ledger Spend in DuckDB", "Amount (₹)": gross_spend},
    {"Component": "Reconciliation Variance", "Amount (₹)": round(total_cap_spend - gross_spend, 2)}
])
display(recon_proof)
assert abs(total_cap_spend - gross_spend) < 1.0, "Capability spend must perfectly reconcile with total enterprise spend!"
print("✓ Audit PASSED: Zero double-counting. 100% of enterprise technology cost reconciled.")
""")

    add_md(nb, """---

## 4. Capability Redundancy Cost Quantification (Scenario C)

We isolate capabilities supported by multiple distinct applications to quantify the **cost of functional duplication**:
""")

    add_code(nb, """# Find capabilities with 2+ supporting applications
redundant_caps = cap_cost_df[cap_cost_df["supported_apps_count"] > 1].copy()
redundant_caps["redundant_cost_share"] = (redundant_caps["total_capability_cost"] / total_cap_spend * 100.0).round(1)

print(f"Capabilities with Duplicate Application Coverage ({len(redundant_caps)} capabilities):")
display(redundant_caps[["capability_id", "capability_name", "supported_apps_count", "direct_app_cost", "total_capability_cost", "redundant_cost_share"]])
""")

    add_md(nb, """---

## 5. Comparative Allocation Models Analysis

We compare our **Proportional Transaction Allocation Model** against an unweighted **Flat Allocation Model** to observe how allocation mechanics shift capability costs:
""")

    add_code(nb, """# Compare Proportional vs Flat Equal Allocation of Shared Infra
total_shared_cost = float(db.query_df("SELECT SUM(amount) FROM cost_records WHERE application_id IS NULL").iloc[0, 0])
flat_shared_per_cap = total_shared_cost / len(cap_cost_df)

comp_df = cap_cost_df[["capability_id", "capability_name", "direct_app_cost", "shared_infra_allocated"]].copy()
comp_df["flat_shared_allocated"] = round(flat_shared_per_cap, 2)
comp_df["proportional_total"] = comp_df["direct_app_cost"] + comp_df["shared_infra_allocated"]
comp_df["flat_total"] = comp_df["direct_app_cost"] + comp_df["flat_shared_allocated"]
comp_df["allocation_delta_pct"] = (
    (comp_df["proportional_total"] - comp_df["flat_total"]) / comp_df["flat_total"] * 100.0
).round(1)

print("Comparative Allocation Analysis (Top 6 Capabilities):")
display(comp_df[["capability_id", "capability_name", "proportional_total", "flat_total", "allocation_delta_pct"]].head(6))
""")

    add_md(nb, """---

## 6. Financial Value Flow: Applications to Capabilities to Business Units (Sankey)

We render an interactive Plotly Sankey diagram tracing the flow of technology funding from Applications $\\longrightarrow$ Capabilities $\\longrightarrow$ Consuming Business Units:
""")

    add_code(nb, """# Compile link data for Sankey
rel_cap = db.query_df(\"\"\"
    SELECT r.application_id, a.application_name, r.capability_id, c.capability_name, c.business_unit_id, b.business_unit_name
    FROM rel_app_capability r
    JOIN applications a ON r.application_id = a.application_id
    JOIN business_capabilities c ON r.capability_id = c.capability_id
    JOIN business_units b ON c.business_unit_id = b.business_unit_id
\"\"\")

# Focus on Top 6 Apps and Top 6 Capabilities to avoid visual clutter
top_app_ids = app_tco_df.head(6)["application_id"].tolist()
rel_top = rel_cap[rel_cap["application_id"].isin(top_app_ids)].copy()

all_nodes = list(rel_top["application_name"].unique()) + list(rel_top["capability_name"].unique()) + list(rel_top["business_unit_name"].unique())
node_map = {name: idx for idx, name in enumerate(all_nodes)}

sources = []
targets = []
values = []

# App -> Cap links
for _, r in rel_top.iterrows():
    sources.append(node_map[r["application_name"]])
    targets.append(node_map[r["capability_name"]])
    values.append(10)

# Cap -> BU links
for _, r in rel_top.drop_duplicates(subset=["capability_name", "business_unit_name"]).iterrows():
    sources.append(node_map[r["capability_name"]])
    targets.append(node_map[r["business_unit_name"]])
    values.append(15)

fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=all_nodes,
        color="#2b5c8f"
    ),
    link=dict(
        source=sources,
        target=targets,
        value=values,
        color="rgba(31, 119, 180, 0.4)"
    )
)])

fig.update_layout(title_text="Technology Value Flow: Applications -> Capabilities -> Business Units", font_size=10)
fig.show()
""")

    add_md(nb, """## 7. Limitations & Analytical Guardrails

1. **Driver Selection:** We utilized digital transaction volume as the proportional driver for shared infrastructure. Other corporate environments might utilize employee headcount, storage volume, or revenue share.
2. **Reconciliation Check:** Summing `total_capability_cost` across all capabilities perfectly reconciles with total enterprise technology spend in DuckDB, ensuring no unallocated variance.

## 8. Next Step

In **Notebook 06: Consumption Intelligence**, we evaluate technology consumption across multiple dimensions, mapping applications into strategic utilization quadrants.
""")

    return nb


# ==============================================================================
# Notebook 06: Consumption Intelligence & Utilization Quadrants
# ==============================================================================
def build_notebook_06():
    nb = make_nb()

    add_md(nb, """# Notebook 06: Consumption Intelligence & Utilization Quadrants

**Series:** Technology Value Intelligence (TBM / ITFM / TVR)  
**Notebook Index:** 06 of 12  
**Focus:** Multidimensional Telemetry, Correlation Matrices, Cost vs Utilization Quadrants, Unit Economics Curves  

---

## 1. Business Problem

A fundamental flaw in legacy IT financial management is evaluating costs in isolation from consumption telemetry. When an application's annual expenditure increases by 25%, finance teams instinctively flag it as a cost overrun. However:
- If transactions grew by 40%, the application's **unit economics actually improved**.
- Conversely, if an application's spend stayed flat while active user volume declined by 70%, its unit cost escalated dramatically.

To separate genuine operational scaling from technical waste, we must fuse financial ledgers with **operational consumption telemetry**.

---

## 2. Core Concept & Formulation

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

    add_code(nb, """import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

workspace_root = Path.cwd().parent
sys.path.insert(0, str(workspace_root / "src"))

from tvi.config import load_config
from tvi.consumption_analytics import analyze_consumption_quadrants, find_high_cost_low_utilization, analyze_unit_economics_trends
from tvi.database import get_database

config = load_config()
db = get_database(config.database.path)

# Classify portfolio into objective consumption quadrants
quadrant_df = analyze_consumption_quadrants()
print("Consumption Quadrant Analysis Compiled:")
display(quadrant_df[["application_id", "application_name", "annual_tco", "avg_monthly_users", "consumption_quadrant"]].head(8))
""")

    add_md(nb, """---

## 3. Multivariate Telemetry Correlation Heatmap

We examine correlations between all 6 telemetry vectors across the application portfolio:
""")

    add_code(nb, """# Compute Correlation Matrix across Telemetry Vectors
telemetry_summary = db.query_df(\"\"\"
    SELECT
        application_id,
        AVG(total_active_users) as users,
        SUM(total_transactions) as transactions,
        SUM(total_api_calls) as api_calls,
        SUM(total_compute_hours) as compute_hours,
        AVG(total_storage_gb) as storage_gb,
        SUM(total_tickets) as tickets
    FROM v_app_monthly_consumption
    GROUP BY application_id
\"\"\")

corr = telemetry_summary.drop(columns=["application_id"]).corr()

plt.figure(figsize=(7, 5))
plt.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
plt.colorbar(label="Pearson Correlation")
plt.xticks(range(len(corr)), corr.columns, rotation=45, ha="right")
plt.yticks(range(len(corr)), corr.columns)
plt.title("Correlation Matrix: Operational Telemetry Vectors", fontsize=12)

for i in range(len(corr)):
    for j in range(len(corr)):
        plt.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", color="black" if abs(corr.iloc[i, j]) < 0.6 else "white", fontsize=9)

plt.tight_layout()
plt.show()
""")

    add_md(nb, """---

## 4. Interactive 2D Bubble Quadrant Matrix (Plotly)

We render an interactive Plotly bubble chart showing the 4 quadrants with median threshold lines and hover inspection:
""")

    add_code(nb, """med_cost = quadrant_df["annual_tco"].median()
med_users = quadrant_df["avg_monthly_users"].median()

fig = px.scatter(
    quadrant_df,
    x="avg_monthly_users",
    y="annual_tco",
    color="consumption_quadrant",
    size="annual_cost_per_user",
    hover_name="application_name",
    hover_data={"application_id": True, "annual_tco": ":,.0f", "avg_monthly_users": ":.0f", "consumption_quadrant": True},
    title="Technology Portfolio: Cost vs Utilization Quadrant Matrix",
    labels={"avg_monthly_users": "Active Users", "annual_tco": "Annual TCO (₹)"},
    template="plotly_white",
    color_discrete_map={
        "High Cost / High Utilization (Scale Anchor)": "#1f77b4",
        "High Cost / Low Utilization (Investigate for Rationalization)": "#d62728",
        "Low Cost / High Utilization (High Efficiency Workhorse)": "#2ca02c",
        "Low Cost / Low Utilization (Niche Utility)": "#7f7f7f"
    }
)

fig.add_hline(y=med_cost, line_dash="dash", line_color="grey", annotation_text=f"Median Spend (₹{med_cost/1e7:.1f} Cr)")
fig.add_vline(x=med_users, line_dash="dot", line_color="grey", annotation_text=f"Median Users ({med_users:.0f})")
fig.update_layout(yaxis=dict(tickformat="~s"))
fig.show()
""")

    add_md(nb, """---

## 5. 12-Month Unit Cost Trajectory Time Series

We analyze monthly unit cost trajectories (Cost per Digital Transaction) over the 12 months of FY2024, contrasting:
- `APP001` (Scale Anchor)
- `APP014` (Scenario G: Scaling volume)
- `APP022` (Scenario H: Cost anomaly)
""")

    add_code(nb, """unit_trends = analyze_unit_economics_trends()

sample_apps = ["APP001", "APP014", "APP022"]
plt.figure(figsize=(10, 4.5))

for a_id in sample_apps:
    sub = unit_trends[unit_trends["application_id"] == a_id]
    plt.plot(sub["month"], sub["monthly_cost_per_transaction"], marker="o", label=f"{a_id} ({sub.iloc[0]['application_name']})", linewidth=2)

plt.title("Monthly Cost per Transaction Trajectory (FY2024)", fontsize=13)
plt.ylabel("Cost per Transaction (₹)", fontsize=11)
plt.xlabel("Month", fontsize=11)
plt.legend()
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()
""")

    add_md(nb, """## 6. Limitations & Methodological Guardrails

1. **Labeling Guardrail:** We intentionally avoid labeling quadrants as "good" or "bad". A low-user application might be an executive risk engine used once a quarter to make multi-billion rupee capital allocation decisions.
2. **Investigation Mandate:** The quadrant matrix generates an **indicator for human investigation**, not an automated termination order.

## 7. Next Step

In **Notebook 07: Application Rationalization**, we formalize a multi-criteria decision index (RRI) that combines cost, utilization, capability redundancy, criticality, and lifecycle status to systematically prioritize portfolio rationalization.
""")

    return nb


def main():
    print("Building Notebooks 04, 05, and 06...")
    save_nb(build_notebook_04(), "04_application_cost_intelligence.ipynb")
    save_nb(build_notebook_05(), "05_capability_cost_intelligence.ipynb")
    save_nb(build_notebook_06(), "06_consumption_intelligence.ipynb")
    print("Notebooks 04-06 ready.")


if __name__ == "__main__":
    main()
