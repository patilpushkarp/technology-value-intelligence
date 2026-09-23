"""Builders for Notebooks 07, 08, and 09 with exhaustive analytical depth."""

from scripts.nb_builders.common import make_nb, add_md, add_code, save_nb


# ==============================================================================
# Notebook 07: Application Rationalization & Multi-Criteria Portfolio Scoring
# ==============================================================================
def build_notebook_07():
    nb = make_nb()

    add_md(nb, """# Notebook 07: Application Rationalization & Multi-Criteria Portfolio Scoring

**Series:** Technology Value Intelligence (TBM / ITFM / TVR)  
**Notebook Index:** 07 of 12  
**Focus:** Multi-Criteria Decision Analysis (MCDA), Gartner TIME Matrix, Rationalization Review Index (RRI), Avoidable Cost Scenarios  

---

## 1. Business Problem

Enterprise application rationalization is often paralyzed by internal organizational politics. IT leaders attempt to retire obsolete or redundant systems, only to be met with resistance from departmental sponsors claiming the application is indispensable.

Common failure modes:
1. **Decisions based solely on cost:** Decommissioning a high-cost application that turns out to be mission-critical.
2. **Decisions based on opaque "black box" scoring:** Stakeholders reject recommendations because the underlying formulas cannot be audited or explained.

To build trust and accelerate portfolio optimization, we require a **transparent, rule-based Multi-Criteria Decision Analysis (MCDA)** scoring framework with clear evidence trails.

---

## 2. Core Concept & Formulation

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

    add_code(nb, """import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx

workspace_root = Path.cwd().parent
sys.path.insert(0, str(workspace_root / "src"))

from tvi.config import load_config
from tvi.rationalization import score_application_portfolio, find_rationalization_candidates
from tvi.graph import build_knowledge_graph

config = load_config()

# Compute complete multi-criteria portfolio scores
scored_portfolio = score_application_portfolio()
print("Multi-Criteria Portfolio Rationalization Scores:")
display(scored_portfolio[["application_id", "application_name", "lifecycle_status", "annual_tco", "cost_score", "utilization_score", "capability_overlap_score", "rationalization_review_index"]].head(8))
""")

    add_md(nb, """---

## 3. Filter Candidates for Rationalization Review (RRI $\\ge$ 60.0)

We filter applications meeting the rationalization threshold and inspect their transparent investigation evidence strings:
""")

    add_code(nb, """candidates_df = find_rationalization_candidates(review_threshold=60.0)
print(f"Applications Requiring Rationalization Review ({len(candidates_df)} systems flagged):")
display(candidates_df[["application_id", "application_name", "lifecycle_status", "criticality", "annual_tco", "avg_monthly_users", "overlapping_caps_count", "rationalization_review_index", "investigation_evidence"]])
""")

    add_md(nb, """---

## 4. Gartner TIME Framework Mapping

We map the portfolio into the industry-standard Gartner TIME matrix:
- **Tolerate:** High technical debt, but low cost/risk. Keep as-is.
- **Invest:** High business value, modern architecture. Allocate growth capital.
- **Migrate:** Business critical, but aging platform. Re-host / modernize.
- **Eliminate:** Redundant capability, low utilization, high cost. High rationalization priority.
""")

    add_code(nb, """# Gartner TIME Matrix Mapping
fig = px.scatter(
    scored_portfolio,
    x="utilization_score",
    y="cost_score",
    color="lifecycle_status",
    size="rationalization_review_index",
    hover_name="application_name",
    hover_data={"application_id": True, "annual_tco": ":,.0f", "rationalization_review_index": True},
    title="Gartner TIME / TBM Rationalization Matrix (Size = Rationalization Review Index)",
    labels={"utilization_score": "Business Fit / Utilization Score (0-100)", "cost_score": "Financial Burden / Cost Score (0-100)"},
    template="plotly_white",
    color_discrete_map={"Strategic": "#2ca02c", "Tolerate": "#ff7f0e", "Migrate": "#1f77b4", "Retire": "#d62728"}
)

fig.add_hline(y=50, line_dash="dash", line_color="grey")
fig.add_vline(x=50, line_dash="dash", line_color="grey")

fig.add_annotation(x=25, y=85, text="ELIMINATE / REVIEW<br>(High Cost / Low Adoption)", showarrow=False, font=dict(color="#d62728", size=11))
fig.add_annotation(x=75, y=85, text="INVEST / OPTIMIZE<br>(High Cost / High Adoption)", showarrow=False, font=dict(color="#1f77b4", size=11))
fig.add_annotation(x=25, y=15, text="TOLERATE<br>(Low Cost / Low Adoption)", showarrow=False, font=dict(color="#7f7f7f", size=11))
fig.add_annotation(x=75, y=15, text="HARVEST / WORKHORSE<br>(Low Cost / High Adoption)", showarrow=False, font=dict(color="#2ca02c", size=11))

fig.show()
""")

    add_md(nb, """---

## 5. MCDA Weight Sensitivity Analysis

How do rationalization priorities shift if executive leadership pivots between **Aggressive Cost-Cutting** (Cost weight = 0.55) versus **Risk-Averse Modernization** (Criticality & Lifecycle weights = 0.65)?
""")

    add_code(nb, """# Weight Sensitivity Simulation
sens_df = scored_portfolio.copy()

# Baseline RRI
sens_df["rri_baseline"] = sens_df["rationalization_review_index"]

# Scenario 1: Aggressive Cost-Cutting
sens_df["rri_cost_cutting"] = (
    0.55 * sens_df["cost_score"]
    + 0.20 * (100.0 - sens_df["utilization_score"])
    + 0.15 * sens_df["capability_overlap_score"]
    + 0.10 * (100.0 - sens_df["criticality_score"])
).round(1)

# Scenario 2: Risk-Averse Modernization
sens_df["rri_risk_averse"] = (
    0.20 * sens_df["cost_score"]
    + 0.15 * (100.0 - sens_df["utilization_score"])
    + 0.15 * sens_df["capability_overlap_score"]
    + 0.25 * sens_df["lifecycle_score"]
    + 0.25 * (100.0 - sens_df["criticality_score"])
).round(1)

sens_compare = sens_df[["application_id", "application_name", "rri_baseline", "rri_cost_cutting", "rri_risk_averse"]].sort_values("rri_baseline", ascending=False).head(6)
print("Sensitivity of Top Candidates to Policy Weights:")
display(sens_compare)
""")

    add_md(nb, """---

## 6. Overlapping Capability Subgraph Visualization

We render a focused Knowledge Subgraph illustrating the functional duplication of `CAP003` (Order-to-Cash) supported simultaneously by `APP005` (Strategic) and `APP012` (Retire):
""")

    add_code(nb, """G = build_knowledge_graph()
otc_sub = G.subgraph(["CAP003", "APP005", "APP012", "BU004"]).copy()

plt.figure(figsize=(7, 4.5))
pos = nx.spring_layout(otc_sub, seed=42)

colors = ["#2ca02c" if n == "CAP003" else "#1f77b4" if n == "APP005" else "#d62728" if n == "APP012" else "#9467bd" for n in otc_sub.nodes()]
nx.draw_networkx_nodes(otc_sub, pos, node_color=colors, node_size=1500, alpha=0.9)
nx.draw_networkx_edges(otc_sub, pos, edge_color="#555", arrows=True, arrowsize=18, width=2)

labels = {
    "CAP003": "CAP003\\n(Order-to-Cash)",
    "APP005": "APP005\\n(OrderFlow Strategic)",
    "APP012": "APP012\\n(QuickOrder Retire)",
    "BU004": "BU004\\n(Digital Payments)"
}
nx.draw_networkx_labels(otc_sub, pos, labels=labels, font_size=8, font_weight="bold")

plt.title("Scenario C: Capability Redundancy Subgraph (Order-to-Cash)", fontsize=12)
plt.axis("off")
plt.tight_layout()
plt.show()
""")

    add_md(nb, """## 7. Limitations & Analytical Guardrails

1. **Avoidable vs Sunk Costs:** Contractual termination penalties, multi-year cloud commitments, and retained shared infrastructure will diminish immediate cash savings.
2. **Governance Auditability:** Every recommendation is supported by transparent evidence strings linking back to source data.

## 8. Next Step

In **Notebook 08: Dependency & Impact Analysis**, before recommending any application for retirement, we interrogate the Knowledge Graph to evaluate its **blast radius and hidden integration dependencies**.
""")

    return nb


# ==============================================================================
# Notebook 08: Dependency & Blast Radius Impact Analysis
# ==============================================================================
def build_notebook_08():
    nb = make_nb()

    add_md(nb, """# Notebook 08: Dependency & Blast Radius Impact Analysis

**Series:** Technology Value Intelligence (TBM / ITFM / TVR)  
**Notebook Index:** 08 of 12  
**Focus:** Transitive Dependency Traversal, Single Point of Failure (SPOF) Detection, Blast Radius Index, Cycle Auditing  

---

## 1. Business Problem

One of the greatest fears of enterprise IT executives is **unintended decommissioning blast radius**:
- An application is identified as an obsolete, low-utilization candidate for rationalization.
- The project team powers down the server.
- Suddenly, five mission-critical digital banking channels, ATM networks, and fraud prevention engines crash.

Why does this happen? In complex architectures, applications rarely exist in isolation. They communicate via synchronous APIs, ETL batch jobs, shared databases, and message buses. 

Before touching any application, leadership must know its **complete direct and indirect dependency blast radius**.

---

## 2. Core Concept & Formulation

### 2.1 Graph Transitive Traversal (BFS / DFS)
Given target application $A$:
- **Direct Dependents (1-hop):** $\\text{Adj}^{-}(A) = \\{ u \\in V \\mid (u, A) \\in E_{\\text{DEPENDS\\_ON}} \\}$
- **Indirect Transitive Dependents ($k$-hop):** All nodes $u$ reachable in the reverse graph $G^T$:
  $$\\text{Transitive}(A) = \\{ u \\in V \\mid \\exists \\text{ path from } u \\text{ to } A \\text{ in } G \\}$$

### 2.2 Blast Radius Metric (BRM)
To quantify operational change risk, we define a composite blast radius metric:
$$\\text{BRM}(A) = 3 \\cdot |\\text{Direct}| + 1.5 \\cdot |\\text{Indirect}| + 4 \\cdot |\\text{Capabilities}| + 2 \\cdot |\\text{Impacted BUs}|$$
""")

    add_code(nb, """import sys
from pathlib import Path
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go

workspace_root = Path.cwd().parent
sys.path.insert(0, str(workspace_root / "src"))

from tvi.config import load_config
from tvi.graph import build_knowledge_graph
from tvi.dependency import get_application_dependencies, get_capability_dependencies, get_business_unit_dependencies

config = load_config()
G = build_knowledge_graph()
print(f"Graph Loaded: {G.number_of_nodes()} Nodes, {G.number_of_edges()} Edges")
""")

    add_md(nb, """---

## 3. Dependency Cycle Detection & Topological Sort Audit

Before analyzing linear blast radius, we audit the application dependency network for cyclic dependencies (deadlocks / tight coupling):
""")

    add_code(nb, """# Extract App-to-App dependency subgraph
app_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get("relationship") == "DEPENDS_ON"]
app_dep_graph = nx.DiGraph(app_edges)

cycles = list(nx.simple_cycles(app_dep_graph))
print(f"=== Dependency Cycle Audit ===")
print(f"Dependency Edges Checked : {len(app_edges)}")
print(f"Cyclic Dependencies Found: {len(cycles)}")
if cycles:
    print(f"Warning: Circular coupling detected: {cycles[:2]}")
else:
    print("✓ Architecture is a Directed Acyclic Graph (DAG) for tested components.")
""")

    add_md(nb, """---

## 4. Single Point of Failure (SPOF) Analysis: Scenario D (`APP010`)

We compute the complete direct and transitive blast radius for `APP010` (Central Auth Hub):
""")

    add_code(nb, """app010_dep = get_application_dependencies("APP010", G)

print("=== Blast Radius Dossier: APP010 (Central Auth & Identity Hub) ===")
print(f"Blast Radius Metric (BRM)      : {app010_dep['blast_radius_metric']}")
print(f"Direct Dependent Applications  : {len(app010_dep['direct_dependent_apps'])}")
print(f"Indirect Transitive Dependents : {len(app010_dep['indirect_dependent_apps'])}")
print(f"Capabilities Supported         : {len(app010_dep['capabilities'])}")
print(f"Business Units Impacted        : {len(app010_dep['business_units'])}")

print("\\nDirect Dependent Applications List:")
for a in app010_dep["direct_dependent_apps"]:
    print(f"  • {a['id']}: {a['name']}")

print("\\nImpacted Business Units:")
for b in app010_dep["business_units"]:
    print(f"  • {b['id']}: {b['name']} ({b['region']})")
""")

    add_md(nb, """---

## 5. Bidirectional Blast Radius Comparison: Leaf Node vs Central Hub

We compare the decommissioning risk profile of `APP021` (Leaf Node candidate) vs `APP010` (SPOF Hub):
""")

    add_code(nb, """app021_dep = get_application_dependencies("APP021", G)

comp_df = pd.DataFrame([
    {
        "Application": "APP010 (Central Auth Hub)",
        "Direct Dependent Apps": len(app010_dep["direct_dependent_apps"]),
        "Indirect Dependent Apps": len(app010_dep["indirect_dependent_apps"]),
        "Capabilities Supported": len(app010_dep["capabilities"]),
        "Impacted BUs": len(app010_dep["business_units"]),
        "Blast Radius Score": app010_dep["blast_radius_metric"],
        "Decommissioning Risk": "Extremely High Risk (SPOF Hub)"
    },
    {
        "Application": "APP021 (Legacy Web Portal)",
        "Direct Dependent Apps": len(app021_dep["direct_dependent_apps"]),
        "Indirect Dependent Apps": len(app021_dep["indirect_dependent_apps"]),
        "Capabilities Supported": len(app021_dep["capabilities"]),
        "Impacted BUs": len(app021_dep["business_units"]),
        "Blast Radius Score": app021_dep["blast_radius_metric"],
        "Decommissioning Risk": "Low Risk (Isolated Leaf Node)"
    }
])
display(comp_df)
""")

    add_md(nb, """---

## 6. Demonstrating Capability & Business Unit Dependencies

We demonstrate `get_capability_dependencies()` and `get_business_unit_dependencies()`:
""")

    add_code(nb, """# Capability Dependencies: CAP003 (Order-to-Cash)
cap003_dep = get_capability_dependencies("CAP003", G)
print("=== Capability Dependencies: CAP003 (Order-to-Cash) ===")
print(f"Owning BU: {cap003_dep['owning_business_units']}")
print(f"Supporting Applications: {cap003_dep['supporting_applications']}")
print(f"Targeting Projects: {cap003_dep['targeting_projects']}")

# Business Unit Dependencies: BU001 (Retail Banking)
bu001_dep = get_business_unit_dependencies("BU001", G)
print("\\n=== Business Unit Dependencies: BU001 (Retail Banking) ===")
print(f"Owned Capabilities Count: {len(bu001_dep['owned_capabilities'])}")
print(f"Supporting Applications Count: {len(bu001_dep['supporting_applications'])}")
""")

    add_md(nb, """## 7. Limitations & Analytical Guardrails

1. **Static CMDB vs Dynamic Runtime Logs:** This model reflects documented architectural relationships. In legacy environments, undocumented batch jobs or shared database table dependencies may exist.
2. **Blast Radius Scope:** The metric assesses topological exposure; actual operational risk also depends on data flow volumes and failure tolerance (circuit breakers).

## 8. Next Step

In **Notebook 09: Investment & Benefit Realization**, we connect discretionary technology spending (projects) with business outcomes (benefits and KPIs) in a formal Technology Value Realization (TVR) framework.
""")

    return nb


# ==============================================================================
# Notebook 09: Investment & Technology Value Realization (TVR)
# ==============================================================================
def build_notebook_09():
    nb = make_nb()

    add_md(nb, """# Notebook 09: Investment & Technology Value Realization (TVR)

**Series:** Technology Value Intelligence (TBM / ITFM / TVR)  
**Notebook Index:** 09 of 12  
**Focus:** Project Budget Variance, Expected vs Realized Benefits, Benefit Realization Gap, KPI Outcomes  

---

## 1. Business Problem

Enterprises spend billions annually on digital transformations, cloud migrations, and software modernization projects. Yet, industry studies consistently report that over 65% of enterprise technology projects fail to deliver their anticipated financial or operational returns.

The root cause is a post-delivery accountability vacuum:
1. When a project is delivered, finance records the capital expenditure, but **stops tracking whether the promised benefits actually materialize**.
2. Project teams disband and claim success based purely on delivery date, while business sponsors never verify whether productivity or cost reduction targets were met.

**Technology Value Realization (TVR)** establishes a continuous feedback loop connecting capital investment to tangible outcome realization.

---

## 2. Core Concept & Formulation

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
from tvi.value_realization import (
    calculate_project_budget_variance, calculate_benefit_realization,
    analyze_benefit_kpi_progression, get_project_value_profile
)
from tvi.database import get_database

config = load_config()
db = get_database(config.database.path)

# Calculate budget variances and benefit realization rates
budget_df = calculate_project_budget_variance()
benefit_df = calculate_benefit_realization()

tvr_df = budget_df.merge(benefit_df[["project_id", "total_expected_benefit", "total_realized_benefit", "benefit_realization_pct", "benefit_gap"]], on="project_id")
print("Technology Value Realization Portfolio Summary:")
display(tvr_df[["project_id", "project_name", "project_type", "investment_budget", "actual_spend", "budget_variance", "total_expected_benefit", "total_realized_benefit", "benefit_realization_pct"]].head(8))
""")

    add_md(nb, """---

## 3. Portfolio-Level Benefit Realization Waterfall

We visualize total portfolio expected benefits against the unrealized benefit gap and net realized benefits:
""")

    add_code(nb, """tot_expected = tvr_df["total_expected_benefit"].sum() / 1e7
tot_realized = tvr_df["total_realized_benefit"].sum() / 1e7
tot_gap = tot_expected - tot_realized

fig = go.Figure(go.Waterfall(
    name="Benefit Realization",
    orientation="v",
    measure=["relative", "relative", "total"],
    x=["Total Expected Benefits", "Unrealized Benefit Gap", "Net Realized Benefits"],
    textposition="outside",
    text=[f"₹{tot_expected:.1f} Cr", f"-₹{tot_gap:.1f} Cr", f"₹{tot_realized:.1f} Cr"],
    y=[tot_expected, -tot_gap, tot_realized],
    connector=dict(line=dict(color="rgb(63, 63, 63)")),
    decreasing=dict(marker=dict(color="#d62728")),
    increasing=dict(marker=dict(color="#2ca02c")),
    totals=dict(marker=dict(color="#1f77b4"))
))

fig.update_layout(
    title="Enterprise Technology Portfolio: Benefit Realization Waterfall (₹ Crores)",
    showlegend=False,
    template="plotly_white"
)
fig.show()
""")

    add_md(nb, """---

## 4. Benefit Realization by Benefit Type

Benefits span 7 categories: Cost Reduction, Productivity, Revenue Enablement, Risk Reduction, Cycle Time Reduction, Capacity Release, and Customer Experience:
""")

    add_code(nb, """# Aggregate benefits by type
type_agg = db.query_df(\"\"\"
    SELECT
        benefit_type,
        SUM(expected_value) as expected_val,
        SUM(realized_value) as realized_val,
        ROUND(SUM(realized_value) / NULLIF(SUM(expected_value), 0) * 100.0, 1) as realization_pct
    FROM benefits
    GROUP BY benefit_type
    ORDER BY expected_val DESC
\"\"\")

plt.figure(figsize=(10, 4.5))
x = np.arange(len(type_agg))
w = 0.35

plt.bar(x - w/2, type_agg["expected_val"] / 1e7, width=w, label="Expected Benefit (₹ Cr)", color="#2b5c8f")
plt.bar(x + w/2, type_agg["realized_val"] / 1e7, width=w, label="Realized Benefit (₹ Cr)", color="#2ca02c")

plt.xticks(x, type_agg["benefit_type"], rotation=30, ha="right", fontsize=9)
plt.ylabel("Benefit Value (₹ Crores)", fontsize=11)
plt.title("Benefit Realization Performance across Categories", fontsize=13)
plt.legend()
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()
""")

    add_md(nb, """---

## 5. Contrasting Scenario E (`PRJ003`) vs Scenario F (`PRJ014`)

We inspect the dossiers for the top-performing project vs the project with the largest benefit gap:
""")

    add_code(nb, """prj003_dossier = get_project_value_profile("PRJ003")
prj014_dossier = get_project_value_profile("PRJ014")

comp_projects = pd.DataFrame([
    {
        "Project ID": "PRJ003",
        "Project Name": prj003_dossier["project"]["project_name"],
        "Budget Variance (₹ Cr)": (prj003_dossier["project"]["actual_spend"] - prj003_dossier["project"]["investment_budget"]) / 1e7,
        "Expected Benefit (₹ Cr)": prj003_dossier["project"]["expected_annual_benefit"] / 1e7,
        "Realized Benefit (₹ Cr)": prj003_dossier["benefits"]["realized_value"].sum() / 1e7,
        "Realization %": f"{(prj003_dossier['benefits']['realized_value'].sum() / prj003_dossier['project']['expected_annual_benefit'])*100:.1f}%",
        "Status": "Exceeded Target (Scenario E)"
    },
    {
        "Project ID": "PRJ014",
        "Project Name": prj014_dossier["project"]["project_name"],
        "Budget Variance (₹ Cr)": (prj014_dossier["project"]["actual_spend"] - prj014_dossier["project"]["investment_budget"]) / 1e7,
        "Expected Benefit (₹ Cr)": prj014_dossier["project"]["expected_annual_benefit"] / 1e7,
        "Realized Benefit (₹ Cr)": prj014_dossier["benefits"]["realized_value"].sum() / 1e7,
        "Realization %": f"{(prj014_dossier['benefits']['realized_value'].sum() / prj014_dossier['project']['expected_annual_benefit'])*100:.1f}%",
        "Status": "Severe Benefit Gap (Scenario F)"
    }
])
display(comp_projects)
""")

    add_md(nb, """---

## 6. Grounding Benefits to Measurable KPI Outcomes

We inspect how project benefits connect to empirical KPI movements:
""")

    add_code(nb, """kpi_progression = analyze_benefit_kpi_progression()
print("Associated KPI Progression Table:")
display(kpi_progression[["project_id", "project_name", "benefit_type", "kpi_name", "baseline_value", "target_value", "actual_value", "unit", "kpi_target_achievement_pct"]].head(8))
""")

    add_md(nb, """## 7. Limitations & Analytical Guardrails

1. **Observational Metrics:** Recorded realized benefits represent observed financial shifts in operational accounts. Without controlled econometric isolation, other macro factors (market growth, organizational restructuring) also influence outcomes.
2. **Language Guardrail:** Express outcomes using: *"The project is associated with a recorded realized benefit of..."* rather than declaring unverified direct causality.

## 8. Next Step

In **Notebook 10: Cost Driver & Variance Analysis**, we analyze monthly spending fluctuations, deconstructing spend spikes into healthy transaction scaling versus unbacked rate anomalies.
""")

    return nb


def main():
    print("Building Notebooks 07, 08, and 09...")
    save_nb(build_notebook_07(), "07_application_rationalization.ipynb")
    save_nb(build_notebook_08(), "08_dependency_and_impact_analysis.ipynb")
    save_nb(build_notebook_09(), "09_investment_benefit_realization.ipynb")
    print("Notebooks 07-09 ready.")


if __name__ == "__main__":
    main()
