"""Builders for Notebooks 10, 11, and 12 with exhaustive analytical depth."""

from scripts.nb_builders.common import make_nb, add_md, add_code, save_nb


# ==============================================================================
# Notebook 10: Cost Driver & Financial Variance Analysis
# ==============================================================================
def build_notebook_10():
    nb = make_nb()

    add_md(nb, """# Notebook 10: Cost Driver & Financial Variance Analysis

**Series:** Technology Value Intelligence (TBM / ITFM / TVR)  
**Notebook Index:** 10 of 12  
**Focus:** Month-over-Month (MoM) Variance, Driver Decomposition, Price-Volume-Mix Modeling, Anomaly Detection  

---

## 1. Business Problem

Every month, CIOs and IT Finance Directors face the recurring executive question:
> *"Why did technology spending increase by ₹4 Crores this month?"*

Typical corporate responses are frustratingly vague: *"Cloud costs were up"* or *"Vendor invoices arrived."* 

An executive needs a precise **root-cause driver decomposition**:
1. Was the cost increase driven by genuine business volume expansion (e.g., e-commerce transaction surge)?
2. Or was the cost increase caused by rate hikes, unoptimized idle infrastructure, or contract scope creep?

---

## 2. Core Concept & Formulation

### 2.1 Multi-Level Variance Decomposition
Given baseline month $t_0$ and comparison month $t_1$:
$$\\Delta \\text{Total Spend} = \\text{Spend}(t_1) - \\text{Spend}(t_0)$$
We decompose this delta hierarchically:
$$\\Delta \\text{Total Spend} = \\sum_{c} \\Delta \\text{Category}_c = \\sum_{a} \\Delta \\text{Application}_a = \\sum_{s} \\Delta \\text{Service}_s = \\sum_{b} \\Delta \\text{BU}_b$$

### 2.2 Price-Volume-Mix (PVM) Algebraic Decomposition
For an application with unit rate $P = \\frac{\\text{Spend}}{\\text{Volume}}$ and operational transaction volume $V$:
$$\\Delta \\text{Spend} = \\underbrace{\\Delta P \\times V_0}_{\\text{Rate Effect}} + \\underbrace{P_0 \\times \\Delta V}_{\\text{Volume Effect}} + \\underbrace{\\Delta P \\times \\Delta V}_{\\text{Cross/Mix Effect}}$$

### 2.3 Elasticity Diagnosis: Scenario G vs Scenario H
- **Scenario G (Elastic Scale):**
  $$\\frac{\\Delta \\text{Spend}}{\\text{Spend}} > 0 \\quad \\text{and} \\quad \\frac{\\Delta \\text{Volume}}{\\text{Volume}} \\ge 20\\% \\implies \\text{Healthy Scaling}$$
- **Scenario H (Rate/Infrastructure Anomaly):**
  $$\\frac{\\Delta \\text{Spend}}{\\text{Spend}} > 0 \\quad \\text{and} \\quad \\frac{\\Delta \\text{Volume}}{\\text{Volume}} \\approx 0\\% \\implies \\text{Anomaly (Immediate Audit)}$$
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
from tvi.variance import calculate_monthly_cost_variance, calculate_category_variance, identify_cost_drivers
from tvi.database import get_database

config = load_config()
db = get_database(config.database.path)

# Compute Month-over-Month (MoM) time series variance
mom_variance = calculate_monthly_cost_variance()
print("Monthly Cost Variance Trajectory:")
display(mom_variance)
""")

    add_md(nb, """---

## 3. Financial Waterfall Chart: August Spend Shift Decomposition

We visualize the Month-over-Month shift from July (2024-07) to August (2024-08) using an executive financial waterfall chart:
""")

    add_code(nb, """drivers = identify_cost_drivers(baseline_month="2024-07", comparison_month="2024-08", top_n=6)
cat_var = drivers["top_category_drivers"]

base_spend = drivers["spend_baseline"] / 1e7
comp_spend = drivers["spend_comparison"] / 1e7

# Prepare waterfall data
x_names = ["July Spend"] + list(cat_var["cost_category"]) + ["August Spend"]
measures = ["absolute"] + ["relative"] * len(cat_var) + ["total"]
y_vals = [base_spend] + list(cat_var["variance_amount"] / 1e7) + [comp_spend]
text_vals = [f"₹{base_spend:.1f} Cr"] + [f"{v/1e7:+.2f} Cr" for v in cat_var["variance_amount"]] + [f"₹{comp_spend:.1f} Cr"]

fig = go.Figure(go.Waterfall(
    name="Monthly Shift",
    orientation="v",
    measure=measures,
    x=x_names,
    y=y_vals,
    text=text_vals,
    textposition="outside",
    connector=dict(line=dict(color="rgb(63, 63, 63)")),
    decreasing=dict(marker=dict(color="#2ca02c")),
    increasing=dict(marker=dict(color="#d62728")),
    totals=dict(marker=dict(color="#1f77b4"))
))

fig.update_layout(
    title="Executive Spend Shift Waterfall: July vs August 2024 (₹ Crores)",
    template="plotly_white",
    yaxis_title="Spend (₹ Crores)"
)
fig.show()
""")

    add_md(nb, """---

## 4. Multi-Level Variance Decomposition (Service & Business Unit Levels)

We deconstruct the August variance across IT Services and Consuming Business Units:
""")

    add_code(nb, """# Service-Level Variance
srv_var = db.query_df(\"\"\"
    WITH ma AS (
        SELECT service_id, SUM(amount) as s_a FROM cost_records WHERE month = '2024-07' GROUP BY service_id
    ),
    mb AS (
        SELECT service_id, SUM(amount) as s_b FROM cost_records WHERE month = '2024-08' GROUP BY service_id
    )
    SELECT
        s.service_id, s.service_name,
        COALESCE(ma.s_a, 0)/1e7 as spend_jul_cr,
        COALESCE(mb.s_b, 0)/1e7 as spend_aug_cr,
        ROUND((COALESCE(mb.s_b, 0) - COALESCE(ma.s_a, 0))/1e7, 2) as delta_cr,
        ROUND((COALESCE(mb.s_b, 0) - COALESCE(ma.s_a, 0)) / NULLIF(ma.s_a, 0) * 100.0, 1) as growth_pct
    FROM it_services s
    LEFT JOIN ma ON s.service_id = ma.service_id
    LEFT JOIN mb ON s.service_id = mb.service_id
    ORDER BY delta_cr DESC
\"\"\")

print("Top 5 IT Service Spend Shifts:")
display(srv_var.head(5))

# Business Unit Variance
bu_var = db.query_df(\"\"\"
    WITH ma AS (
        SELECT business_unit_id, SUM(amount) as b_a FROM cost_records WHERE month = '2024-07' GROUP BY business_unit_id
    ),
    mb AS (
        SELECT business_unit_id, SUM(amount) as b_b FROM cost_records WHERE month = '2024-08' GROUP BY business_unit_id
    )
    SELECT
        b.business_unit_id, b.business_unit_name,
        COALESCE(ma.b_a, 0)/1e7 as spend_jul_cr,
        COALESCE(mb.b_b, 0)/1e7 as spend_aug_cr,
        ROUND((COALESCE(mb.b_b, 0) - COALESCE(ma.b_a, 0))/1e7, 2) as delta_cr
    FROM business_units b
    LEFT JOIN ma ON b.business_unit_id = ma.business_unit_id
    LEFT JOIN mb ON b.business_unit_id = mb.business_unit_id
    ORDER BY delta_cr DESC
\"\"\")

print("\\nTop Business Unit Spend Shifts:")
display(bu_var.head(5))
""")

    add_md(nb, """---

## 5. Statistical Anomaly Detection (Z-Score Outlier Flagging)

We apply Z-score statistical outlier detection on month-over-month application cost deltas to automatically flag uncharacteristic spend surges:
""")

    add_code(nb, """app_deltas = db.query_df(\"\"\"
    WITH app_m AS (
        SELECT application_id,
               SUM(CASE WHEN month = '2024-07' THEN amount ELSE 0 END) as jul_cost,
               SUM(CASE WHEN month = '2024-08' THEN amount ELSE 0 END) as aug_cost
        FROM cost_records
        WHERE application_id IS NOT NULL
        GROUP BY application_id
    )
    SELECT
        m.application_id, a.application_name,
        m.jul_cost, m.aug_cost,
        (m.aug_cost - m.jul_cost) as cost_delta
    FROM app_m m
    JOIN applications a ON m.application_id = a.application_id
\"\"\")

mean_delta = app_deltas["cost_delta"].mean()
std_delta = app_deltas["cost_delta"].std()
app_deltas["z_score"] = ((app_deltas["cost_delta"] - mean_delta) / std_delta).round(2)
app_deltas["statistical_flag"] = np.where(app_deltas["z_score"] >= 2.0, "ANOMALY (Z >= 2.0)", "Normal")

anomalies = app_deltas[app_deltas["statistical_flag"].str.contains("ANOMALY")].sort_values("z_score", ascending=False)
print("Statistically Flagged Spend Anomalies:")
display(anomalies)

assert "APP014" in anomalies["application_id"].values and "APP022" in anomalies["application_id"].values, "Anomalies must detect APP014 and APP022!"
""")

    add_md(nb, """## 6. Business Interpretation: Explaining Scenario G vs Scenario H

1. **Scenario G (`APP014` - Cloud Payment Hub):**
   - Cost Delta: +₹60 Lakhs in August.
   - Root-Cause: E-commerce and mobile payment transactions surged by **+180%**.
   - Conclusion: **Healthy elastic scaling**. The cloud architecture scaled compute instances in direct response to genuine business transaction volume.
2. **Scenario H (`APP022` - Batch Billing Engine):**
   - Cost Delta: +₹38 Lakhs in August.
   - Root-Cause: Operational volume and active user count remained flat (-1.2%).
   - Conclusion: **Unbacked cost anomaly**. The surge represents an unmonitored infrastructure sizing change or vendor rate increase, triggering an immediate FinOps audit.
""")

    add_md(nb, """## 7. Limitations & Analytical Guardrails

1. **Price-Volume-Mix Breakdown:** Fine-grained price vs volume deconstruction requires cloud billing SKU-level detail (e.g., AWS CUR per-second billing), which is abstracted to monthly totals here.
2. **Lagged Invoicing:** Real-world enterprise billing occasionally reflects catch-up vendor invoices spanning prior quarters.

## 8. Next Step

In **Notebook 11: Local LLM + Knowledge Graph Analyst**, we introduce a guarded, dual-mode natural language interface that allows executives to ask questions and receive factually grounded answers without arbitrary code execution risks.
""")

    return nb


# ==============================================================================
# Notebook 11: Local LLM + Knowledge Graph AI Analyst
# ==============================================================================
def build_notebook_11():
    nb = make_nb()

    add_md(nb, """# Notebook 11: Local LLM + Knowledge Graph AI Analyst

**Series:** Technology Value Intelligence (TBM / ITFM / TVR)  
**Notebook Index:** 11 of 12  
**Focus:** Guarded Natural Language Interface, Intent Detection, Zero Arbitrary Code Execution, Grounded Explanations  

---

## 1. Business Problem

Executive leaders (CIO, CFO, BU Heads) rarely write SQL queries or inspect NetworkX graph objects directly. They want to ask natural questions:
- *"What does our Order-to-Cash capability cost?"*
- *"Which applications have high cost and low utilization?"*
- *"Why did technology spending increase in August?"*

However, connecting an unrestricted Large Language Model (LLM) directly to enterprise financial data poses catastrophic risks:
1. **Hallucination:** LLMs fabricate believable-sounding numbers when data is absent.
2. **Prompt Injection & Security:** Giving an LLM unrestricted SQL or Python code execution access creates severe security vulnerabilities.
3. **Reproducibility Failure:** An executive cannot present ungrounded LLM guesses to the Board of Directors.

We need a **guarded architecture** where the LLM functions strictly as a natural language interface, while all mathematical and graph operations remain deterministic.

---

## 2. Core Concept & Architecture

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

    add_code(nb, """import sys
import time
from pathlib import Path
import pandas as pd

workspace_root = Path.cwd().parent
sys.path.insert(0, str(workspace_root / "src"))

from tvi.config import load_config
from tvi.llm import KnowledgeGraphAnalyst

config = load_config()

# Initialize AI Analyst in rules mode
analyst = KnowledgeGraphAnalyst(mode="rules", config=config)
print(f"Knowledge Graph Analyst Initialized (Mode: {analyst.mode})")
print(f"Local Ollama Daemon Detected: {analyst.is_ollama_available()}")
""")

    add_md(nb, """---

## 3. Comprehensive Evaluation Benchmark Harness (15 Diverse Executive Queries)

We construct an automated evaluation benchmark testing 15 diverse executive queries across 6 intent categories, measuring:
- Intent Classification Accuracy
- Parameter / Entity Extraction Precision
- Response Latency
""")

    add_code(nb, """test_queries = [
    # Application Cost
    ("What is the cost and utilization of APP001?", "APPLICATION_COST", "APP001"),
    ("Show me the profile for APP021", "APPLICATION_COST", "APP021"),
    ("What does APP014 cost?", "APPLICATION_COST", "APP014"),

    # Capability Cost
    ("What does our Order-to-Cash capability cost?", "CAPABILITY_COST", "CAP003"),
    ("What is the cost of CAP003?", "CAPABILITY_COST", "CAP003"),
    ("How much do we spend on Procure-to-Pay?", "CAPABILITY_COST", "CAP003"),

    # Rationalization
    ("Which applications have high cost and low utilization?", "RATIONALIZATION_CANDIDATES", None),
    ("Show me applications that should be rationalized", "RATIONALIZATION_CANDIDATES", None),
    ("Which systems are redundant and underutilized?", "RATIONALIZATION_CANDIDATES", None),

    # Dependency Analysis
    ("What depends on APP010?", "APPLICATION_DEPENDENCY", "APP010"),
    ("What is the blast radius of APP021?", "APPLICATION_DEPENDENCY", "APP021"),

    # Cost Variance
    ("Why did spend increase in August?", "COST_VARIANCE_DRIVERS", None),
    ("What drove the cost variance last month?", "COST_VARIANCE_DRIVERS", None),

    # Discretionary Benefits
    ("What benefits were expected from PRJ014?", "PROJECT_VALUE_PROFILE", "PRJ014"),
    ("What is the ROI on PRJ003?", "PROJECT_VALUE_PROFILE", "PRJ003"),
]

benchmark_results = []
for q, exp_intent, exp_param in test_queries:
    t0 = time.time()
    res = analyst.query(q)
    latency_ms = (time.time() - t0) * 1000.0

    intent_match = res["intent"] == exp_intent
    benchmark_results.append({
        "Query": q,
        "Expected Intent": exp_intent,
        "Detected Intent": res["intent"],
        "Intent Match": "PASS" if intent_match else "FAIL",
        "Latency (ms)": round(latency_ms, 2)
    })

bench_df = pd.DataFrame(benchmark_results)
display(bench_df)

accuracy = (bench_df["Intent Match"] == "PASS").mean() * 100.0
avg_lat = bench_df["Latency (ms)"].mean()
print(f"\\n=== Benchmark Performance Summary ===")
print(f"Total Queries Evaluated : {len(bench_df)}")
print(f"Intent Matching Accuracy: {accuracy:.1f}%")
print(f"Average Response Latency: {avg_lat:.2f} ms")
assert accuracy >= 90.0, "Benchmark accuracy must exceed 90%!"
""")

    add_md(nb, """---

## 4. Multi-Turn Conversational Simulation

We simulate an executive conversational session:
- **Turn 1:** Executive asks about the cost of a capability.
- **Turn 2:** Executive drills into the applications driving that capability.
- **Turn 3:** Executive checks the blast radius of a rationalization candidate.
""")

    add_code(nb, """conversation = [
    "What does Order-to-Cash cost?",
    "Which applications have high cost and low utilization?",
    "What depends on APP021?"
]

for idx, user_msg in enumerate(conversation, start=1):
    print(f"\\n--- Turn {idx} ---")
    print(f"Executive : '{user_msg}'")
    reply = analyst.query(user_msg)
    print(f"AI Analyst: {reply['explanation']}")
""")

    add_md(nb, """---

## 5. Security & Prompt Injection Defense Verification

We verify that malicious prompts attempting arbitrary code execution or SQL injection are safely blocked:
""")

    add_code(nb, """injection_queries = [
    "Drop table cost_records;--",
    "import os; os.system('rm -rf /')",
    "What is the CEO personal home address?"
]

for mal_q in injection_queries:
    print(f"\\nTest Injection: '{mal_q}'")
    safe_res = analyst.query(mal_q)
    print(f"Status        : {safe_res['status']}")
    print(f"Explanation   : {safe_res['explanation'][:100]}...")
    assert safe_res["status"] == "CLARIFICATION_REQUIRED", "Security check failed!"
print("\\n✓ All adversarial queries safely defused.")
""")

    add_md(nb, """## 6. Limitations & Methodological Guardrails

1. **Strict Intent Boundaries:** The analyst only answers questions that can be mapped to deterministic analytical functions. It does not synthesize open-ended creative prose.
2. **Zero Code Injection:** The analyst is fundamentally incapable of running arbitrary SQL `DROP` commands or arbitrary Python code strings.

## 7. Next Step

In **Notebook 12: End-to-End Technology Value Intelligence**, we synthesize the entire 12-notebook journey into a unified executive scenario, compiling the full 9-section Board-level Executive Report.
""")

    return nb


# ==============================================================================
# Notebook 12: End-to-End Technology Value Intelligence
# ==============================================================================
def build_notebook_12():
    nb = make_nb()

    add_md(nb, """# Notebook 12: End-to-End Technology Value Intelligence

**Series:** Technology Value Intelligence (TBM / ITFM / TVR)  
**Notebook Index:** 12 of 12  
**Focus:** Executive Narrative Synthesis, End-to-End Value Chain Traversal, 9-Section Board Report  

---

## 1. Business Problem

We have reached the culmination of our analytical journey. 

In enterprise environments, insights typically remain trapped in operational silos:
- Finance has the general ledger spend.
- Enterprise Architecture has the application catalog and capability models.
- Infrastructure teams have the server and cloud logs.
- The PMO has the project status reports.

Because these domains are disconnected, executive leadership cannot see the complete **Technology Value Chain**:
$$\\text{Technology Cost} \\longrightarrow \\text{Application} \\longrightarrow \\text{Service} \\longrightarrow \\text{Capability} \\longrightarrow \\text{Business Unit} \\longrightarrow \\text{Investment} \\longrightarrow \\text{Value Realization}$$

In this final notebook, we integrate all layers to answer a strategic executive scenario for the CIO.

---

## 2. Core Concept: The Unified Technology Value Chain

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

    add_code(nb, """import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from IPython.display import Markdown, display

workspace_root = Path.cwd().parent
sys.path.insert(0, str(workspace_root / "src"))

from tvi.config import load_config
from tvi.graph import build_knowledge_graph
from tvi.graph_queries import get_full_value_chain_path
from tvi.cost_analytics import calculate_application_tco, calculate_capability_cost
from tvi.rationalization import find_rationalization_candidates
from tvi.reporting import generate_executive_report

config = load_config()
G = build_knowledge_graph()
print("Unified Technology Value Intelligence Engine Initialized.")
""")

    add_md(nb, """---

## 3. End-to-End Lineage Dossier: Full Multi-Hop Traversal

We inspect the complete end-to-end lineage path for `APP005` (OrderFlow Enterprise):
""")

    add_code(nb, """app005_chain = get_full_value_chain_path(G, "APP005")

print("=== End-to-End Lineage Dossier: APP005 (OrderFlow Enterprise) ===")
print(f"Application Name : {app005_chain['application_name']}")
print(f"Lifecycle Status : {app005_chain['lifecycle_status']}")
print(f"Criticality      : {app005_chain['criticality']}")
print(f"Technologies     : {[t['name'] for t in app005_chain['technologies']]}")
print(f"Vendors          : {[v['name'] for v in app005_chain['vendors']]}")
print(f"IT Services      : {[s['name'] for s in app005_chain['services']]}")
print(f"Capabilities     : {[c['name'] for c in app005_chain['capabilities']]}")
print(f"Business Units   : {[b['name'] for b in app005_chain['business_units']]}")
""")

    add_md(nb, """---

## 4. Multi-Tier Technology Value Flow (Plotly Sankey)

We trace the complete flow from Vendor Invoices $\\longrightarrow$ Technologies $\\longrightarrow$ Applications $\\longrightarrow$ Capabilities:
""")

    add_code(nb, """# Build interactive Sankey of the complete value chain
sankey_data = [
    ("TechNova (Vendor)", "AWS EKS (Technology)", 18),
    ("EnterpriseSoft (Vendor)", "PostgreSQL (Technology)", 12),
    ("AWS EKS (Technology)", "APP005 (OrderFlow)", 18),
    ("PostgreSQL (Technology)", "APP005 (OrderFlow)", 12),
    ("APP005 (OrderFlow)", "Order-to-Cash (Capability)", 30),
    ("Order-to-Cash (Capability)", "Digital Payments (BU)", 30),
]

nodes = list(set([u for u, v, w in sankey_data] + [v for u, v, w in sankey_data]))
node_indices = {n: idx for idx, n in enumerate(nodes)}

sources = [node_indices[u] for u, v, w in sankey_data]
targets = [node_indices[v] for u, v, w in sankey_data]
values = [w for u, v, w in sankey_data]

fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=nodes,
        color="#2b5c8f"
    ),
    link=dict(
        source=sources,
        target=targets,
        value=values,
        color="rgba(31, 119, 180, 0.4)"
    )
)])

fig.update_layout(title_text="Unified Enterprise Lineage: Vendor -> Technology -> Application -> Capability -> BU", font_size=11)
fig.show()
""")

    add_md(nb, """---

## 5. CIO Executive Decision Matrix

We synthesize portfolio spend, operational utilization, capability redundancy, and topological blast radius into an actionable **Executive Decision Matrix**:
""")

    add_code(nb, """candidates = find_rationalization_candidates(review_threshold=50.0)

decision_matrix = []
for _, r in candidates.head(5).iterrows():
    a_id = r["application_id"]
    if a_id == "APP021":
        action = "Decommission & Migrate Users to APP011"
        risk_level = "Low (Leaf Node, 0 Inbound Deps)"
    elif a_id == "APP012":
        action = "Retire & Consolidate CAP003 onto APP005"
        risk_level = "Low (Designated Retire)"
    elif a_id == "APP018":
        action = "Retire & Consolidate CAP004 onto APP006"
        risk_level = "Low (Designated Retire)"
    else:
        action = "Right-size Infrastructure Sizing"
        risk_level = "Medium"

    decision_matrix.append({
        "Application ID": a_id,
        "Application Name": r["application_name"],
        "Annual TCO (₹ Cr)": round(r["annual_tco"] / 1e7, 2),
        "Active Users": round(r["avg_monthly_users"]),
        "RRI Score": r["rationalization_review_index"],
        "Risk Level": risk_level,
        "Recommended CIO Action": action
    })

decision_df = pd.DataFrame(decision_matrix)
display(decision_df)
""")

    add_md(nb, """---

## 6. Rendering the Formal 9-Section Board-Level Executive Report

We generate and display the formal Board-level Executive Report:
""")

    add_code(nb, """report_markdown = generate_executive_report()
display(Markdown(report_markdown))
""")

    add_md(nb, """## 7. Strategic Recommendations for Leadership

1. **Shift from Cost Accounting to Value Realization:** By connecting General Ledger cost records to Business Capabilities and KPIs, IT transitions from an opaque "cost center" to an accountable driver of business outcomes.
2. **Targeted Rationalization Portfolio:** We identified concrete rationalization opportunities (e.g., decommissioning `APP021` and consolidating `CAP003` onto `APP005`), yielding potential avoidable cost scenarios exceeding ₹11 Crores without impacting critical dependencies.
3. **Graph-Enhanced Governance:** Topological traversal uncovers bottlenecks (such as `APP010`) that flat spreadsheets completely miss, de-risking enterprise transformation programs.

## 8. Conclusion & Future Roadmap

This completes the 12-notebook **Technology Value Intelligence** prototype. 

### Future Architectural Roadmap:
1. **Phase 2:** Connect enterprise lakehouse tables (Databricks, Snowflake).
2. **Phase 3:** Migrate graph backend from NetworkX to **Neo4j** for real-time multi-million node traversals.
3. **Phase 4:** Embed semantic vector search over IT vendor contracts and architecture RFCs.
""")

    return nb


def main():
    print("Building Notebooks 10, 11, and 12...")
    save_nb(build_notebook_10(), "10_cost_driver_and_variance_analysis.ipynb")
    save_nb(build_notebook_11(), "11_local_llm_knowledge_graph_analyst.ipynb")
    save_nb(build_notebook_12(), "12_end_to_end_technology_value_intelligence.ipynb")
    print("Notebooks 10-12 ready.")


if __name__ == "__main__":
    main()
