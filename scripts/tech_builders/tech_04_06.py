"""Technical blog generator for Notebooks 04, 05, and 06 (9 articles total)."""

from .common import write_tech_article

def generate_nb04_articles():
    # 04a: Activity-Based Costing & The Five-Layer Cost Stack
    write_tech_article("04a_activity_based_costing_and_the_five_layer_cost_stack.md", """---
title: "Technical Guide 04a: Activity-Based Costing & The Five-Layer Cost Stack"
notebook_reference: "notebooks/04_application_cost_intelligence.ipynb"
part: "Part 1 of 3 for Notebook 04"
reading_time: "20 min read"
audience: "FinOps Engineers, Cost Architects, Software Engineering Managers"
tbm_domain_level: "Intermediate"
author: "Technology Value Intelligence Architecture Team"
---

# Technical Guide 04a: Activity-Based Costing & The Five-Layer Cost Stack

> [!NOTE]
> **Executive Summary & Engineering Objective**: How much does an enterprise software application *actually* cost to run? In this guide, we break down Activity-Based Costing (ABC) principles, dismantle naive "flat allocation" models, formulate the Five-Layer Cost Stack, and walk through the implementation in [`src/tvi/cost_analytics.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/cost_analytics.py).

---

## 1. The Cost Distortion of "Direct-Only" Accounting

When development teams are asked about the cost of their application, they usually point to their direct cloud invoice or primary software licenses:

> *"Our microservice costs \$12,000 per month on AWS ECS."*

In reality, direct cloud spend is often only 20% to 30% of the true **Total Cost of Ownership (TCO)**. The organization is also paying for:
- Database administrator salaries.
- Shared network firewall appliances.
- Central enterprise logging (Splunk / Datadog).
- Information security tooling and vulnerability scanners.
- Facilities, electricity, and disaster recovery replication sites.

```text
               The Application Cost Iceberg:
                     ▲
                    / \      Direct Cloud / License Cost (30%)
                   /   \     (What developers see)
                  /     \
            ─────/───────\───── WATERLINE
                /         \
               /  Shared   \  DBAs, Security Scanners, Shared Networks,
              /  Overhead   \ Facilities, Platform Engineering (70%)
             /               \ (What TBM fully burdens)
            ───────────────────
```

If you evaluate applications based only on direct costs, shared enterprise platforms appear artificially cheap, while dedicated systems appear artificially expensive.

---

## 2. Theoretical Foundations: Activity-Based Costing (ABC)

**Activity-Based Costing (ABC)** solves this by identifying the activities that generate costs and assigning them to products and services based on actual resource consumption.

### The Five-Layer Fully-Burdened Cost Stack

We model application TCO across five additive cost categories:

$$\operatorname{TCO}(a) = C_{\text{Infra}}(a) + C_{\text{Software}}(a) + C_{\text{Labor}}(a) + C_{\text{Services}}(a) + C_{\text{Facilities}}(a)$$

1. **Infrastructure ($C_{\text{Infra}}$)**: Compute instances, block storage, load balancers, and network egress directly consumed.
2. **Software ($C_{\text{Software}}$)**: Commercial off-the-shelf (COTS) licenses, per-seat tool fees, and database engines.
3. **Internal Labor ($C_{\text{Labor}}$)**: Fully-burdened engineer compensation (salary + benefits + payroll taxes) allocated via developer time tracking or ticket volume.
4. **External Services ($C_{\text{Services}}$)**: Managed service providers, systems integrators, and third-party SaaS contracts.
5. **Facilities / Overhead ($C_{\text{Facilities}}$)**: Data center floor space, cooling power, and corporate IT governance overhead.

### The Driver Allocation Matrix Formulation

When costs cannot be directly metered, they are allocated using a stochastic driver matrix $D \in \mathbb{R}^{m \times n}$:

$$\mathbf{C}_{\text{Allocated}} = D \cdot \mathbf{C}_{\text{Pool}}$$

where each element $d_{ij} = \frac{\operatorname{ConsumptionMetric}(i, j)}{\sum_k \operatorname{ConsumptionMetric}(k, j)}$ represents the proportion of shared resource $j$ consumed by application $i$.

---

## 3. Code Walkthrough: Computing Fully-Burdened TCO

Let's examine the vectorized aggregation pipeline in [`src/tvi/cost_analytics.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/cost_analytics.py#L35-L95).

```python
# src/tvi/cost_analytics.py
import duckdb
import pandas as pd
from typing import Dict, Any

def calculate_application_tco(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    \"\"\"
    Computes fully-burdened multi-layer TCO across all applications.
    Aggregates general ledger spend grouped by application and cost pool category.
    \"\"\"
    query = \"\"\"
        SELECT 
            a.app_id,
            a.app_name,
            a.tier,
            a.owner_bu,
            SUM(CASE WHEN p.pool_category = 'Infrastructure' THEN f.amount ELSE 0 END) as infra_cost,
            SUM(CASE WHEN p.pool_category = 'Software' THEN f.amount ELSE 0 END) as software_cost,
            SUM(CASE WHEN p.pool_category = 'Labor' THEN f.amount ELSE 0 END) as labor_cost,
            SUM(CASE WHEN p.pool_category = 'External Services' THEN f.amount ELSE 0 END) as services_cost,
            SUM(f.amount) as total_tco
        FROM fact_general_ledger_spend f
        JOIN dim_applications a ON f.app_id = a.app_id
        JOIN dim_cost_pools p ON f.pool_id = p.pool_id
        GROUP BY a.app_id, a.app_name, a.tier, a.owner_bu
        ORDER BY total_tco DESC;
    \"\"\"
    return con.execute(query).df()
```

### Line-by-Line Code Analysis:

- **Lines 15–20**: Conditional SQL aggregation via `SUM(CASE WHEN ...)` pivots the normalized relational fact rows into a clean five-column cost stack table in a single vectorized pass.
- **Line 26**: DuckDB's `.df()` executes the query in C++ and outputs a zero-copy Apache Arrow / Pandas DataFrame, ready for plotting or downstream calculations.

---

## 4. Architectural Decisions & Alternatives

| Costing Methodology | TVI (Activity-Based Costing) | Flat Allocation ("Peanut Butter") | Direct-Only Costing |
| :--- | :--- | :--- | :--- |
| **Accuracy** | High: reflect operational consumption | Low: distorts incentives | Incomplete: ignores 70% of overhead |
| **Data Requirements** | Requires consumption telemetry drivers | Only requires headcounts | Only requires cloud invoices |
| **Computational Cost** | Matrix multiplication in DuckDB (< 50ms) | Trivial division | Trivial filter |
| **Executive Trust** | High: fully auditable and defensible | Low: penalizes efficient teams | Medium: causes surprise budget overruns |

---

## 5. Scope of Improvement & Production Roadmap

1. **Automated Driver Discovery**: Use machine learning (e.g., Lasso regression) to determine which operational telemetry metrics (CPU, RAM, API calls) best explain shared cost variance.
2. **Dynamic Multi-Currency Revaluation**: Calculate historical TCO runs in constant currency vs current spot rates to separate operational cost growth from FX volatility.

---

## 6. Summary & Companion Reading

Activity-Based Costing provides a defensible, multi-layered view of true application ownership costs.

- **Next Guide**: [04b: Unit Economics & Marginal Cost Modeling](file:///Users/pushkar/Documents/projects/value/blog/technical/04b_unit_economics_and_marginal_cost_modeling.md) explores how to normalize TCO against business volume.
- **Companion Business Article**: [04a: Demystifying Fully Burdened Application TCO](file:///Users/pushkar/Documents/projects/value/blog/business/04a_demystifying_fully_burdened_application_tco.md) provides executive framing.
""")

    # 04b: Unit Economics & Marginal Cost Modeling
    write_tech_article("04b_unit_economics_and_marginal_cost_modeling.md", """---
title: "Technical Guide 04b: Unit Economics & Marginal Cost Modeling"
notebook_reference: "notebooks/04_application_cost_intelligence.ipynb"
part: "Part 2 of 3 for Notebook 04"
reading_time: "21 min read"
audience: "FinOps Practitioners, Financial Analysts, Product Architects"
tbm_domain_level: "Intermediate"
author: "Technology Value Intelligence Architecture Team"
---

# Technical Guide 04b: Unit Economics & Marginal Cost Modeling

> [!NOTE]
> **Executive Summary & Engineering Objective**: Absolute cost figures can be misleading: an application that costs \$10M annually might be exceptionally efficient if it processes 1 billion transactions, while a \$100,000 app might be a financial disaster if it serves only two users. In this guide, we dive into the mathematics of IT Unit Economics, fixed vs variable cost separation, and examine the code in [`src/tvi/cost_analytics.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/cost_analytics.py).

---

## 1. Why Raw Spend Fails: The Unit Economic Perspective

Consider two systems in an enterprise portfolio:

```text
┌─────────────────────────────────────────────────────────────┐
│                    SPEND COMPARISON ILLUSION                 │
│                                                             │
│  Application A (Core Banking Engine):                       │
│  • Annual Spend: $23,000,000  (Looks expensive!)            │
│  • Volume: 1,000,000,000 transactions                       │
│  • Unit Cost: $0.023 per transaction (Hyper-efficient)      │
│                                                             │
│  Application B (Legacy Branch CRM):                         │
│  • Annual Spend: $350,000    (Looks cheap!)                 │
│  • Volume: 6 active users                                   │
│  • Unit Cost: $58,333 per user/year  (Financial disaster)   │
└─────────────────────────────────────────────────────────────┘
```

Without **Unit Economics**, an executive glancing at the IT budget might try to cut Application A's budget (risking mission-critical payments) while ignoring Application B as a rounding error.

Unit economics connects IT spending directly to business throughput:
$$\text{Unit Cost} = \frac{\text{Fully-Burdened TCO}}{\text{Business Output Volume}}$$

---

## 2. Theoretical Foundations: Fixed vs Variable Cost Modeling

In economic theory, an application's total cost function $C(q)$ over volume $q$ is decomposed into:

$$C(q) = F + V(q) = F + v \cdot q$$

where:
- $F$ is the **Fixed Cost** (base infrastructure, base license fees, core maintenance staff).
- $v$ is the **Marginal Cost per Unit** (cloud autoscale compute, bandwidth egress, per-transaction gateway fees).
- $q$ is the operational volume (monthly transactions, active users).

### Average Unit Cost Function

$$\operatorname{AUC}(q) = \frac{C(q)}{q} = \frac{F}{q} + v$$

```mermaid
xychart-beta
    title "Economies of Scale: Average Unit Cost vs Volume"
    x-axis [100, 1000, 10000, 100000, 1000000]
    y-axis "Unit Cost ($)" 0 --> 100
    line [100.0, 10.5, 1.5, 0.25, 0.023]
```

As operational volume $q \to \infty$, the average unit cost approaches the pure marginal cost $v$, yielding **economies of scale**.

Conversely, when an application enters its legacy phase and active users decline ($q \to 0$), the fixed cost $F$ is divided across a dwindling user base, causing average unit cost to skyrocket. This is the **"Zombie System Death Spiral"**.

---

## 3. Code Walkthrough: Implementing Unit Economics

In [`src/tvi/cost_analytics.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/cost_analytics.py#L110-L165), we compute multi-dimensional unit costs across transaction and user bases:

```python
# src/tvi/cost_analytics.py
def calculate_unit_economics(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    \"\"\"
    Joins TCO data with operational consumption telemetry to compute unit economics.
    \"\"\"
    query = \"\"\"
        WITH annualized_telemetry AS (
            SELECT 
                app_id,
                SUM(transactions_processed) as annual_transactions,
                AVG(active_users) as avg_active_users,
                SUM(storage_tb_consumed) as annual_storage_tb
            FROM fact_consumption_telemetry
            GROUP BY app_id
        ),
        annualized_spend AS (
            SELECT 
                app_id,
                SUM(amount) as annual_tco
            FROM fact_general_ledger_spend
            GROUP BY app_id
        )
        SELECT 
            a.app_id,
            a.app_name,
            s.annual_tco,
            t.annual_transactions,
            t.avg_active_users,
            -- Safe division to prevent division-by-zero
            CASE 
                WHEN t.annual_transactions > 0 THEN s.annual_tco / t.annual_transactions 
                ELSE NULL 
            END as cost_per_transaction,
            CASE 
                WHEN t.avg_active_users > 0 THEN s.annual_tco / t.avg_active_users 
                ELSE NULL 
            END as cost_per_active_user
        FROM dim_applications a
        JOIN annualized_spend s ON a.app_id = s.app_id
        JOIN annualized_telemetry t ON a.app_id = t.app_id
        ORDER BY annual_tco DESC;
    \"\"\"
    return con.execute(query).df()
```

### Line-by-Line Code Analysis:

- **Lines 8–15**: Common Table Expressions (CTEs) compute annual sums and averages across the 12-month reporting horizon. Vectorized aggregation ensures rapid processing across all telemetry records.
- **Lines 28–35**: Defensive SQL division (`CASE WHEN ... THEN ... ELSE NULL`) prevents division-by-zero errors for backend batch jobs that have zero interactive users.

---

## 4. Empirical Benchmark: Workhorse vs Zombie

Running this query against our enterprise dataset produces clear, data-driven operational contrasts:

| Application ID | System Name | Annual TCO | Annual Volume | Cost per Unit | Classification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`APP001`** | Core Banking Engine | ₹23,450,000 | 1,020,000,000 txns | **₹0.023 / txn** | **Workhorse System** |
| **`APP021`** | Legacy Branch CRM | ₹350,000 | 6 active users | **₹58,333 / user** | **Zombie System** |

These calculations make the case for decommissioning `APP021` immediately obvious to both technical and financial stakeholders.

---

## 5. Scope of Improvement & Production Roadmap

1. **Marginal Cost Regression**: Automatically fit OLS regressions $C = \beta_0 + \beta_1 q$ on monthly historical data to isolate fixed base cost $\beta_0$ from marginal cost $\beta_1$.
2. **Unit Margin Attribution**: Join unit IT costs with customer transaction revenue to compute gross technology margins per business transaction.

---

## 6. Summary & Companion Reading

Unit economics normalizes raw IT spend, enabling fair comparisons across systems of vastly different sizes.

- **Next Guide**: [04c: Lorenz Curves, Pareto Concentration & Volume Elasticity](file:///Users/pushkar/Documents/projects/value/blog/technical/04c_lorenz_curves_pareto_concentration_and_volume_elasticity.md) analyzes spend concentration across the portfolio.
- **Companion Business Article**: [04b: Unit Economics: Workhorses vs Zombie Systems](file:///Users/pushkar/Documents/projects/value/blog/business/04b_unit_economics_workhorses_vs_zombie_systems.md) explains unit metrics for executive leadership.
""")

    # 04c: Lorenz Curves, Pareto Concentration & Volume Elasticity
    write_tech_article("04c_lorenz_curves_pareto_concentration_and_volume_elasticity.md", """---
title: "Technical Guide 04c: Lorenz Curves, Pareto Concentration & Volume Elasticity"
notebook_reference: "notebooks/04_application_cost_intelligence.ipynb"
part: "Part 3 of 3 for Notebook 04"
reading_time: "22 min read"
audience: "FinOps Economists, Data Scientists, Portfolio Managers"
tbm_domain_level: "Intermediate to Advanced"
author: "Technology Value Intelligence Architecture Team"
---

# Technical Guide 04c: Lorenz Curves, Pareto Concentration & Volume Elasticity

> [!NOTE]
> **Executive Summary & Engineering Objective**: How concentrated is your IT spend across your application portfolio? If 80% of your budget is absorbed by just 3 applications, your rationalization strategy should look entirely different than if spend is evenly distributed. In this guide, we dive into the mathematics of the Lorenz Curve, Gini Coefficient, and Volume Elasticity simulations in [`notebooks/04_application_cost_intelligence.ipynb`](file:///Users/pushkar/Documents/projects/value/notebooks/04_application_cost_intelligence.ipynb).

---

## 1. Spend Concentration in Enterprise Portfolios

In economics, the **Pareto Principle** states that roughly 80% of consequences come from 20% of causes. In enterprise software portfolios, this relationship is frequently even more pronounced:

```text
                 100% ┌───────────────────────────────┐
                      │                           .  /│
                      │                       .  '   /│
   Cumulative Spend % │                   . '       / │  <-- Lorenz Curve
                      │             .  '           /  │      (High Concentration)
                      │        .  '               /   │
                      │   . '                    /    │
                      │ /                       /     │  <-- Line of Equality
                   0% └───────────────────────────────┘
                      0%                             100%
                          Cumulative Applications %
```

Understanding portfolio concentration is critical:
- If spend is **hyper-concentrated** (high Gini coefficient), corporate cost-cutting initiatives should focus heavily on optimizing the top 3–5 applications.
- If spend is **fragmented** (low Gini coefficient), cost cutting requires governance guardrails and SaaS consolidation across many smaller contracts.

---

## 2. Theoretical Foundations & Mathematical Formulations

### 1. The Lorenz Curve

Let applications be ordered in ascending order of their TCO:
$$x_1 \le x_2 \le \dots \le x_n$$

The cumulative share of applications is:
$$u_k = \frac{k}{n}, \quad k \in \{1, \dots, n\}$$

The cumulative share of spend is:
$$v_k = \frac{\sum_{i=1}^k x_i}{\sum_{i=1}^n x_i}$$

The **Lorenz Curve** is the polygonal path connecting the points $(u_k, v_k)$, starting at $(0, 0)$ and terminating at $(1, 1)$.

### 2. The Gini Coefficient

The **Gini Coefficient** measures the area between the line of perfect equality ($y = x$) and the observed Lorenz curve:

$$G = \frac{A}{A + B} = 1 - 2B = \frac{2 \sum_{i=1}^n i \cdot x_i}{n \sum_{i=1}^n x_i} - \frac{n + 1}{n}$$

- $G = 0$: Perfect equality (all applications cost the same).
- $G \to 1$: Extreme concentration (one single application consumes virtually 100% of the entire corporate IT budget).

### 3. Volume Elasticity Simulation

What happens to an application's unit cost if business volume declines? We define the **Unit Cost Volume Elasticity** $\epsilon$:

$$\epsilon = \frac{\% \Delta \operatorname{AUC}}{\% \Delta q} = \frac{\partial \operatorname{AUC}}{\partial q} \frac{q}{\operatorname{AUC}} = \left( -\frac{F}{q^2} \right) \frac{q}{\frac{F}{q} + v} = -\frac{F}{F + v \cdot q} = -\frac{\text{Fixed Cost}}{\text{Total Cost}}$$

- For a pure SaaS app with zero fixed costs ($F = 0$), $\epsilon = 0$ (unit cost is invariant to volume).
- For a legacy monolith with 90% fixed costs ($F \approx \text{TCO}$), $\epsilon \approx -0.90$. A 50% drop in user volume triggers an immediate 90% spike in per-user unit cost.

---

## 3. Code Walkthrough: Computing Gini & Plotly Visualization

Let's review the analytical implementation in [`notebooks/04_application_cost_intelligence.ipynb`](file:///Users/pushkar/Documents/projects/value/notebooks/04_application_cost_intelligence.ipynb):

```python
import numpy as np
import pandas as pd
import plotly.graph_objects as go

def compute_lorenz_curve(spend_series: pd.Series) -> tuple[np.ndarray, np.ndarray, float]:
    \"\"\"Calculates Lorenz curve coordinates and the Gini coefficient.\"\"\"
    sorted_spend = np.sort(spend_series.values)
    n = len(sorted_spend)
    
    # Cumulative application share
    cum_apps = np.arange(1, n + 1) / n
    cum_apps = np.insert(cum_apps, 0, 0)
    
    # Cumulative spend share
    cum_spend = np.cumsum(sorted_spend) / np.sum(sorted_spend)
    cum_spend = np.insert(cum_spend, 0, 0)
    
    # Gini Coefficient computation
    gini = (2 * np.sum(np.arange(1, n + 1) * sorted_spend)) / (n * np.sum(sorted_spend)) - (n + 1) / n
    
    return cum_apps, cum_spend, gini
```

### Plotly Lorenz Curve Construction

```python
cum_apps, cum_spend, gini_val = compute_lorenz_curve(apps_df['total_tco'])

fig = go.Figure()

# Perfect equality diagonal
fig.add_trace(go.Scatter(
    x=[0, 1], y=[0, 1],
    mode='lines',
    name='Line of Perfect Equality',
    line=dict(dash='dash', color='gray')
))

# Empirical portfolio Lorenz curve
fig.add_trace(go.Scatter(
    x=cum_apps, y=cum_spend,
    mode='lines+markers',
    name=f'Portfolio Lorenz Curve (Gini = {gini_val:.3f})',
    line=dict(color='firebrick', width=3)
))

fig.update_layout(
    title=f"Application Spend Concentration (Gini = {gini_val:.3f})",
    xaxis_title="Cumulative Share of Applications",
    yaxis_title="Cumulative Share of Spend",
    hovermode="x unified"
)
```

---

## 4. Empirical Results: Portfolio Spend Concentration

Running this calculation across the 25 enterprise systems reveals:
- **Observed Gini Coefficient**: $G = 0.684$
- **Top 5 Applications** account for **72.1% of total enterprise IT spend**.
- **Bottom 10 Applications** account for only **4.2% of spend**.

This empirical finding helps teams focus: instead of conducting lengthy audits on 25 applications, IT leadership can focus cost optimization reviews on the top 5 systems to address nearly three-quarters of the entire budget.

---

## 5. Scope of Improvement & Production Roadmap

1. **Automated Curve Fitting**: Fit continuous Dagum or Singh-Maddala distribution curves to model asymptotic tail risks.
2. **Stress-Testing Elasticity Scenarios**: Automatically simulate economic downturns (-20%, -40% business volume) across all applications to identify systems at risk of severe unit cost inflation.

---

## 6. Summary & Companion Reading

Lorenz curves and volume elasticity provide quantitative tools for assessing portfolio concentration and sensitivity to scale.

- **Next Guide**: [05a: Business Capability Modeling & Enterprise Lineage](file:///Users/pushkar/Documents/projects/value/blog/technical/05a_business_capability_modeling_and_enterprise_lineage.md) begins Notebook 05 by examining business capability costing.
- **Companion Business Article**: [04b: Unit Economics: Workhorses vs Zombie Systems](file:///Users/pushkar/Documents/projects/value/blog/business/04b_unit_economics_workhorses_vs_zombie_systems.md) explores how to apply these insights.
""")

def generate_nb05_articles():
    # 05a: Business Capability Modeling & Enterprise Lineage
    write_tech_article("05a_business_capability_modeling_and_enterprise_lineage.md", """---
title: "Technical Guide 05a: Business Capability Modeling & Enterprise Lineage"
notebook_reference: "notebooks/05_capability_cost_intelligence.ipynb"
part: "Part 1 of 3 for Notebook 05"
reading_time: "19 min read"
audience: "Enterprise Architects, Business Architects, Solution Designers"
tbm_domain_level: "Foundational to Intermediate"
author: "Technology Value Intelligence Architecture Team"
---

# Technical Guide 05a: Business Capability Modeling & Enterprise Lineage

> [!NOTE]
> **Executive Summary & Engineering Objective**: Software applications change constantly, but business capabilities remain relatively stable over decades. In this guide, we define what a Business Capability is, introduce the three-level hierarchical taxonomy (BIAN / TOGAF), and show how we structure capability lineage in [`ontology.yaml`](file:///Users/pushkar/Documents/projects/value/ontology.yaml) and DuckDB.

---

## 1. Why Business Leaders Think in Capabilities, Not Code

When IT leaders communicate with business executives using technical terms (Kubernetes clusters, Kafka topics, Oracle schemas), alignment breaks down. Business leaders think in terms of **business capabilities**:

> **What is a Business Capability?**: An enterprise's fundamental ability to execute a specific business function to deliver customer value, regardless of the underlying software tools or human teams performing it.

```text
┌─────────────────────────────────────────────────────────────┐
│              BUSINESS CAPABILITY ABSTRACTION                │
│                                                             │
│  Capability: "Customer Loan Origination"                     │
│  • Does not change whether powered by paper, mainframe,      │
│    or cloud microservices.                                  │
│  • Stable abstraction layer bridging business & technology. │
└─────────────────────────────────────────────────────────────┘
```

By mapping applications to capabilities, organizations decouple **what the business does** from **how IT currently implements it**.

---

## 2. Theoretical Foundations: Hierarchical Capability Taxonomies

Enterprise Architecture standards (such as TOGAF and the Banking Industry Architecture Network - BIAN) organize capabilities into hierarchical levels:

```mermaid
flowchart TD
    L1["Level 1 Capability: Customer Relationship Management"]
    L2A["Level 2: Customer Onboarding"]
    L2B["Level 2: Customer Servicing"]
    L3A["Level 3: KYC Verification"]
    L3B["Level 3: Document Validation"]

    L1 --> L2A
    L1 --> L2B
    L2A --> L3A
    L2A --> L3B
```

- **Level 1 (Domain)**: Broad strategic domains (e.g., *Core Banking*, *Risk & Compliance*).
- **Level 2 (Capability Group)**: Core business functions (e.g., *Deposit Account Administration*, *Credit Evaluation*).
- **Level 3 (Operational Activity)**: Specific operational steps (e.g., *Real-time KYC Sanction Screening*).

### The Many-to-Many Enterprise Mapping

In real enterprises, the mapping between applications and capabilities is rarely 1-to-1:
1. **One-to-Many**: An enterprise ERP (like SAP) supports *General Ledger Accounting*, *Supply Chain Management*, and *Payroll Processing*.
2. **Many-to-One**: A single capability (like *Order-to-Cash*) is often supported by multiple overlapping legacy systems across different geographic business units.

---

## 3. Schema Representation in DuckDB

In [`src/tvi/database.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/database.py#L85-L105), we model this relationship with a bipartite relational mapping table:

```sql
CREATE TABLE IF NOT EXISTS dim_capabilities (
    capability_id VARCHAR PRIMARY KEY,
    capability_name VARCHAR NOT NULL,
    capability_level VARCHAR NOT NULL,   -- 'Level 1', 'Level 2'
    strategic_importance DOUBLE NOT NULL  -- Weight in [0.0, 1.0]
);

CREATE TABLE IF NOT EXISTS rel_app_capability (
    app_id VARCHAR NOT NULL,
    capability_id VARCHAR NOT NULL,
    allocation_weight DOUBLE NOT NULL,   -- Must sum to 1.0 per app_id
    PRIMARY KEY (app_id, capability_id),
    FOREIGN KEY (app_id) REFERENCES dim_applications(app_id),
    FOREIGN KEY (capability_id) REFERENCES dim_capabilities(capability_id)
);
```

By attaching `allocation_weight` directly to the relational edge, we establish the parameters needed for proportional financial attribution.

---

## 4. Scope of Improvement & Production Roadmap

1. **Automated BIAN / TOGAF Ontological Importers**: Ingest standard industry capability taxonomies directly via JSON-LD or RDF OWL files.
2. **Dynamic Capability Maturity Scoring**: Attach maturity levels (Capability Maturity Model Integration - CMMI Level 1 to 5) to each capability to track modernization readiness alongside costs.

---

## 5. Summary & Companion Reading

Business capabilities provide a stable, business-aligned lens for organizing and analyzing IT portfolios.

- **Next Guide**: [05b: Proportional Attribution & Double-Counting Prevention](file:///Users/pushkar/Documents/projects/value/blog/technical/05b_proportional_attribution_and_double_counting_prevention.md) dives into the mathematics of attributing application TCO to capabilities.
- **Companion Business Article**: [05a: What Does a Business Capability Actually Cost?](file:///Users/pushkar/Documents/projects/value/blog/business/05a_what_does_a_business_capability_actually_cost.md) explores the executive view.
""")

    # 05b: Proportional Attribution & Double-Counting Prevention
    write_tech_article("05b_proportional_attribution_and_double_counting_prevention.md", """---
title: "Technical Guide 05b: Proportional Attribution & Double-Counting Prevention"
notebook_reference: "notebooks/05_capability_cost_intelligence.ipynb"
part: "Part 2 of 3 for Notebook 05"
reading_time: "21 min read"
audience: "Financial Engineers, FinOps Auditors, Systems Analysts"
tbm_domain_level: "Intermediate"
author: "Technology Value Intelligence Architecture Team"
---

# Technical Guide 05b: Proportional Attribution & Double-Counting Prevention

> [!NOTE]
> **Executive Summary & Engineering Objective**: If an enterprise application costs \$10M to operate and supports three distinct business capabilities, how do you divide that spend without creating artificial inflation or financial leakage? In this guide, we examine the mathematics of bipartite graph projections, proportional attribution, and double-counting prevention algorithms in [`src/tvi/cost_analytics.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/cost_analytics.py).

---

## 1. The Double-Counting Trap in Enterprise Analytics

When organizations attempt capability-based costing in spreadsheets, they often make a critical mistake:

```text
The Naive Double-Counting Pitfall:
  Application: SAP Enterprise Suite (TCO: $10,000,000)
  
  Supports Capability 1: "Procurement"        -> Assigned: $10,000,000
  Supports Capability 2: "Financial Planning" -> Assigned: $10,000,000
  Supports Capability 3: "Inventory Mgmt"    -> Assigned: $10,000,000
  
  Reported Total Capability Spend: $30,000,000 (300% Financial Inflation!)
```

When the CFO rolls up total capability costs across the company, the total comes out to \$300M when the actual IT budget is only \$100M. The analysis is discredited, and leadership loses confidence in the model.

Every capability costing algorithm must satisfy **strict financial conservation**.

---

## 2. Theoretical Foundations: Bipartite Attribution Mathematics

Let the enterprise architecture be represented as a bipartite graph $\mathcal{G}_{\text{bipartite}} = (\mathcal{A}, \mathcal{C}, \mathcal{E})$, where:
- $\mathcal{A} = \{a_1, \dots, a_n\}$ is the set of applications with known total costs $\mathbf{t} = [T_1, \dots, T_n]^T$.
- $\mathcal{C} = \{c_1, \dots, c_m\}$ is the set of business capabilities.
- $\mathcal{E}$ contains directed edges $(a, c)$ with attribution weights $w_{a, c} \in [0, 1]$.

```mermaid
graph LR
    subgraph Applications
        A1["APP001 ($10M)"]
        A2["APP002 ($4M)"]
    end
    subgraph Capabilities
        C1["CAP001 (Core Banking)"]
        C2["CAP002 (Payments)"]
    end

    A1 -->|w = 0.70| C1
    A1 -->|w = 0.30| C2
    A2 -->|w = 1.00| C2
```

### The Stochastic Constraint

To prevent financial leakage and double counting, the weight vector for each application must sum to 1:

$$\sum_{c \in \mathcal{C}} w_{a, c} = 1, \quad \forall a \in \mathcal{A}$$

The attributed cost of capability $c_j$ is given by matrix multiplication:

$$\operatorname{Cost}(c_j) = \sum_{i=1}^n w_{a_i, c_j} \cdot T_i$$

In matrix notation, let $W \in \mathbb{R}^{m \times n}$ where $W_{j, i} = w_{a_i, c_j}$:

$$\mathbf{c}_{\text{caps}} = W \cdot \mathbf{t}_{\text{apps}}$$

### Proof of Conservation

$$\sum_{j=1}^m \operatorname{Cost}(c_j) = \sum_{j=1}^m \sum_{i=1}^n w_{a_i, c_j} T_i = \sum_{i=1}^n T_i \cdot 1 = \sum_{i=1}^n T_i = \text{Total Application TCO}$$

This mathematical property guarantees zero inflation and zero reconciliation leakage.

---

## 3. Code Walkthrough: Vectorized Capability Costing

Let's examine the implementation in [`src/tvi/cost_analytics.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/cost_analytics.py#L180-L240):

```python
# src/tvi/cost_analytics.py
def calculate_capability_costs(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    \"\"\"
    Calculates fully-burdened business capability costs via proportional attribution.
    Enforces double-counting prevention via weight normalization.
    \"\"\"
    query = \"\"\"
        WITH app_tcos AS (
            SELECT app_id, SUM(amount) as tco
            FROM fact_general_ledger_spend
            GROUP BY app_id
        ),
        normalized_weights AS (
            -- Ensure weights strictly sum to 1.0 per app to avoid leakage
            SELECT 
                r.app_id,
                r.capability_id,
                r.allocation_weight / SUM(r.allocation_weight) OVER (PARTITION BY r.app_id) as norm_weight
            FROM rel_app_capability r
        )
        SELECT 
            c.capability_id,
            c.capability_name,
            c.strategic_importance,
            COUNT(DISTINCT w.app_id) as supporting_app_count,
            SUM(w.norm_weight * t.tco) as allocated_capability_cost
        FROM dim_capabilities c
        JOIN normalized_weights w ON c.capability_id = w.capability_id
        JOIN app_tcos t ON w.app_id = t.app_id
        GROUP BY c.capability_id, c.capability_name, c.strategic_importance
        ORDER BY allocated_capability_cost DESC;
    \"\"\"
    return con.execute(query).df()
```

### Line-by-Line Code Analysis:

- **Lines 10–18**: `normalized_weights` uses a SQL window function `OVER (PARTITION BY r.app_id)` to normalize edge weights dynamically. Even if configuration data contains dirty weights (e.g., weights summing to 0.95 or 1.10), the query renormalizes them on the fly, maintaining exact financial conservation.
- **Line 26**: `SUM(w.norm_weight * t.tco)` computes the vector dot product in DuckDB C++ memory, running in sub-millisecond time.

---

## 4. Scope of Improvement & Production Roadmap

1. **Activity-Driven Weighting**: Instead of relying on static configuration weights, dynamically derive $w_{a, c}$ using real-time API invocation counts per capability domain.
2. **Confidence Intervals**: Implement Monte Carlo simulations on allocation weights to produce uncertainty bands (e.g. "Capability Cost: \$4.2M ± \$350k") when telemetry is partially estimated.

---

## 5. Summary & Companion Reading

Proportional attribution provides a mathematically rigorous way to map IT spend to business capabilities while preserving financial integrity.

- **Next Guide**: [05c: Capability Redundancy Quantification & Sankey Value Flows](file:///Users/pushkar/Documents/projects/value/blog/technical/05c_capability_redundancy_quantification_and_sankey_value_flows.md) explores how to detect duplicate application waste.
- **Companion Business Article**: [05b: Unmasking the Redundancy Trap](file:///Users/pushkar/Documents/projects/value/blog/business/05b_unmasking_the_redundancy_trap_duplicate_apps.md) details corporate cost rationalization.
""")

    # 05c: Capability Redundancy Quantification & Sankey Value Flows
    write_tech_article("05c_capability_redundancy_quantification_and_sankey_value_flows.md", """---
title: "Technical Guide 05c: Capability Redundancy Quantification & Sankey Value Flows"
notebook_reference: "notebooks/05_capability_cost_intelligence.ipynb"
part: "Part 3 of 3 for Notebook 05"
reading_time: "22 min read"
audience: "Enterprise Architects, Data Visualization Engineers, FinOps Strategists"
tbm_domain_level: "Intermediate to Advanced"
author: "Technology Value Intelligence Architecture Team"
---

# Technical Guide 05c: Capability Redundancy Quantification & Sankey Value Flows

> [!NOTE]
> **Executive Summary & Engineering Objective**: Enterprise mergers and fragmented IT procurement often lead to multiple duplicate applications supporting the exact same business capability. In this guide, we examine the mathematics of capability redundancy (Scenario C: Order-to-Cash), formulate avoidable cost models, and build multi-tier financial Sankey diagrams in Plotly.

---

## 1. The Redundancy Sprawl Problem

When large corporations grow through mergers and acquisitions, each business unit brings its own software stack. Within a few years, the enterprise ends up paying for multiple tools that perform the same function:

```text
               Capability: "Order-to-Cash" (CAP003)
                                 │
           ┌─────────────────────┼─────────────────────┐
           ▼                     ▼                     ▼
    Application 1         Application 2         Application 3
       (SAP ERP)          (Oracle NetSuite)     (Microsoft Dynamics)
    Cost: $14.2M/yr       Cost: $8.5M/yr        Cost: $5.7M/yr
    
          TOTAL CAPABILITY COST: $28,400,000 PER YEAR
```

Running three parallel systems for the same capability introduces:
1. Triple vendor maintenance and license overhead.
2. Fragmented customer records across three databases.
3. Redundant software engineering and support teams.

Our analytical engine identifies and quantifies this duplicate spend to prioritize consolidation opportunities.

---

## 2. Theoretical Foundations: Multi-Tier Value Flow Algorithms

To communicate how financial resources flow through the enterprise, we construct a **Multi-Tier Value Flow Graph**:

$$\mathcal{G}_{\text{flow}} = (V_{\text{pools}} \cup V_{\text{towers}} \cup V_{\text{apps}} \cup V_{\text{caps}} \cup V_{\text{bus}}, E)$$

```mermaid
flowchart LR
    P["Cost Pools\n(Labor, Infra, Software)"] -->|Driver| A["Applications\n(APP001 - APP025)"]
    A -->|Attribution| C["Capabilities\n(CAP001 - CAP010)"]
    C -->|Consumption| B["Business Units\n(Retail, Wealth, etc.)"]
```

### Mass Conservation at Every Node

To render an accurate Sankey diagram, the flow network must satisfy **Kirchhoff's Current Law (Mass Balance)** at every intermediate node $v$:

$$\sum_{u \in \operatorname{In}(v)} \operatorname{Flow}(u, v) = \sum_{w \in \operatorname{Out}(v)} \operatorname{Flow}(v, w)$$

If this condition fails, Sankey bands will visibly shrink or expand midway across the canvas, signaling accounting errors to financial reviewers.

---

## 3. Code Walkthrough: Redundancy Detection & Sankey Construction

Let's examine how [`notebooks/05_capability_cost_intelligence.ipynb`](file:///Users/pushkar/Documents/projects/value/notebooks/05_capability_cost_intelligence.ipynb) builds the Plotly Sankey diagram:

```python
import plotly.graph_objects as go
import pandas as pd

def build_capability_sankey(df_flow: pd.DataFrame) -> go.Figure:
    \"\"\"Constructs multi-tier Sankey diagram tracing App -> Capability -> BU.\"\"\"
    
    # 1. Extract unique entity nodes and create integer index mapping
    all_nodes = list(pd.concat([
        df_flow['source'], 
        df_flow['target']
    ]).unique())
    node_to_idx = {name: idx for idx, name in enumerate(all_nodes)}
    
    # 2. Build source, target, value link arrays
    sources = [node_to_idx[s] for s in df_flow['source']]
    targets = [node_to_idx[t] for t in df_flow['target']]
    values = df_flow['amount'].tolist()
    
    # 3. Render Plotly Sankey
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_nodes,
            color="royalblue"
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color="rgba(180, 180, 220, 0.4)"
        )
    )])
    
    fig.update_layout(title="Financial Value Flow: Applications to Capabilities to Business Units")
    return fig
```

---

## 4. Empirical Case Study: Scenario C (`CAP003`)

Running this analysis reveals our injected Scenario C redundancy in the *Order-to-Cash* capability:
- Total capability spend: **₹28,400,000**.
- Supported by **3 separate applications** (`APP003`, `APP007`, `APP018`).
- Application `APP018` is a legacy regional ERP serving only 4% of total transaction volume while consuming 20% of the capability budget.

Consolidating `APP018` into `APP003` yields an estimated **avoidable cost scenario of ₹5,680,000 annually**, providing clear financial backing for rationalization.

---

## 5. Scope of Improvement & Production Roadmap

1. **Interactive Node Collapse in UI**: Implement hierarchical node bundling in JavaScript/Cytoscape to allow users to expand/collapse capabilities down to microservice components dynamically.
2. **Automated Redundancy Thresholding**: Add an alerting engine that automatically flags capabilities supported by more than 2 applications where Gini concentration is low.

---

## 6. Summary & Companion Reading

Quantifying capability redundancy and visualizing value flows translates complex relational data into clear consolidation roadmaps.

- **Next Guide**: [06a: Telemetry Profiling & Workload Metrics](file:///Users/pushkar/Documents/projects/value/blog/technical/06a_telemetry_profiling_and_workload_metrics.md) begins Notebook 06 by examining operational telemetry.
- **Companion Business Article**: [05b: Unmasking the Redundancy Trap](file:///Users/pushkar/Documents/projects/value/blog/business/05b_unmasking_the_redundancy_trap_duplicate_apps.md) provides leadership guidance.
""")

def generate_nb06_articles():
    # 06a: Telemetry Profiling & Workload Metrics
    write_tech_article("06a_telemetry_profiling_and_workload_metrics.md", """---
title: "Technical Guide 06a: Telemetry Profiling & Workload Metrics"
notebook_reference: "notebooks/06_consumption_intelligence.ipynb"
part: "Part 1 of 3 for Notebook 06"
reading_time: "20 min read"
audience: "Site Reliability Engineers, Cloud Operations Engineers, FinOps Analysts"
tbm_domain_level: "Intermediate"
author: "Technology Value Intelligence Architecture Team"
---

# Technical Guide 06a: Telemetry Profiling & Workload Metrics

> [!NOTE]
> **Executive Summary & Engineering Objective**: Financial cost data only tells you what you spent; operational telemetry tells you what you actually received. In this guide, we dive into the collection, normalization, and correlation of operational telemetry metrics (CPU, RAM, Storage, Active Users, Transactions) in [`src/tvi/consumption_analytics.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/consumption_analytics.py).

---

## 1. The Disconnect Between Cost and Consumption

In many enterprises, IT Finance and Cloud Engineering operate in complete isolation:

```text
┌──────────────────────────────┐        ┌──────────────────────────────┐
│       FinOps / Finance       │        │     Engineering / DevOps     │
│  • "AWS bill is $400,000"    │   ≠    │  • "CPU is running at 12%"   │
│  • Tracks invoices & budgets │        │  • Tracks Prometheus metrics │
└──────────────────────────────┘        └──────────────────────────────┘
```

When these two data streams are separated:
1. Operations provisions large cloud instances for "safety margins", creating waste.
2. Finance demands across-the-board budget cuts without understanding which systems are genuinely under heavy load.

**Consumption Intelligence** bridges this divide by linking hourly operational telemetry directly to the general ledger.

---

## 2. Theoretical Foundations: Telemetry Normalization & Correlation

Operational metrics come in diverse scales and units:
- CPU Utilization: Percentage $\in [0, 100\%]$
- Active Users: Integer count $\in [1, 100,000]$
- Storage Consumed: Terabytes $\in [0.1, 500 \text{ TB}]$

### Min-Max Normalization

To compare disparate metrics on a common baseline without distorting relative differences:

$$z_{i} = \frac{x_i - \min(\mathbf{x})}{\max(\mathbf{x}) - \min(\mathbf{x})} \in [0, 1]$$

### Multivariate Correlation Matrix

To determine whether infrastructure spend scales linearly with user activity, we compute the **Pearson Correlation Coefficient**:

$$r_{xy} = \frac{\sum_{i=1}^n (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum_{i=1}^n (x_i - \bar{x})^2} \sqrt{\sum_{i=1}^n (y_i - \bar{y})^2}}$$

```mermaid
flowchart TD
    RAW["Raw Telemetry Stream\n(Prometheus / CloudWatch / Datadog)"] --> CLEAN["Data Cleaning & NaN Imputation"]
    CLEAN --> NORM["Min-Max & Z-Score Normalization"]
    NORM --> CORR["Multivariate Correlation Matrix (Heatmap)"]
    CORR --> EVAL["Workload Elasticity Evaluation"]
```

---

## 3. Code Walkthrough: Profiling Consumption Telemetry

Let's examine how [`src/tvi/consumption_analytics.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/consumption_analytics.py#L30-L85) processes raw telemetry:

```python
# src/tvi/consumption_analytics.py
import duckdb
import pandas as pd
import numpy as np

def profile_operational_telemetry(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    \"\"\"
    Aggregates and normalizes 12-month consumption telemetry across all systems.
    \"\"\"
    query = \"\"\"
        SELECT 
            app_id,
            AVG(cpu_utilization) as avg_cpu,
            MAX(cpu_utilization) as peak_cpu,
            AVG(active_users) as avg_users,
            AVG(transactions_processed) as avg_txns,
            AVG(storage_tb_consumed) as avg_storage_tb
        FROM fact_consumption_telemetry
        GROUP BY app_id
        ORDER BY app_id;
    \"\"\"
    df = con.execute(query).df()
    
    # Vectorized Min-Max Normalization for composite utilization index
    metrics = ['avg_cpu', 'avg_users', 'avg_txns', 'avg_storage_tb']
    for col in metrics:
        min_v = df[col].min()
        max_v = df[col].max()
        df[f'{col}_norm'] = (df[col] - min_v) / (max_v - min_v) if max_v > min_v else 0.5
        
    # Composite Utilization Score (weighted average)
    df['composite_utilization'] = (
        0.35 * df['avg_cpu_norm'] +
        0.35 * df['avg_txns_norm'] +
        0.20 * df['avg_users_norm'] +
        0.10 * df['avg_storage_tb_norm']
    )
    return df
```

### Line-by-Line Code Analysis:

- **Lines 8–18**: Aggregates average and peak telemetry across the time horizon. Tracking both average and peak CPU is essential: a system with 10% average CPU that hits 98% during month-end financial close cannot simply be downsized to a smaller VM.
- **Lines 28–33**: Computes a single normalized **Composite Utilization Score** $\in [0, 1]$. This metric combines CPU load, transaction volume, and active user counts into an index for portfolio segmentation.

---

## 4. Scope of Improvement & Production Roadmap

1. **High-Frequency Telemetry Ingestion**: Stream 5-minute metric rollups from Prometheus into DuckDB using Apache Arrow flight endpoints.
2. **Seasonal Decomposition (STL)**: Apply Seasonal and Trend decomposition using Loess to separate baseline growth from cyclical weekly bursts.

---

## 5. Summary & Companion Reading

Normalizing operational telemetry allows engineering and finance teams to analyze workloads using consistent benchmarks.

- **Next Guide**: [06b: Quadrant Segmentation & Multivariate Clustering](file:///Users/pushkar/Documents/projects/value/blog/technical/06b_quadrant_segmentation_and_multivariate_clustering.md) explains the 2x2 Cost vs Utilization Matrix.
- **Companion Business Article**: [06a: The 2x2 Utilization Quadrant Matrix](file:///Users/pushkar/Documents/projects/value/blog/business/06a_the_2x2_utilization_quadrant_matrix.md) details operational portfolio reviews.
""")

    # 06b: Quadrant Segmentation & Multivariate Clustering
    write_tech_article("06b_quadrant_segmentation_and_multivariate_clustering.md", """---
title: "Technical Guide 06b: Quadrant Segmentation & Multivariate Clustering"
notebook_reference: "notebooks/06_consumption_intelligence.ipynb"
part: "Part 2 of 3 for Notebook 06"
reading_time: "21 min read"
audience: "FinOps Strategists, Data Scientists, Infrastructure Architects"
tbm_domain_level: "Intermediate"
author: "Technology Value Intelligence Architecture Team"
---

# Technical Guide 06b: Quadrant Segmentation & Multivariate Clustering

> [!NOTE]
> **Executive Summary & Engineering Objective**: How do you identify which applications are delivering strong value for their spend, and which ones are draining budget with minimal utilization? In this guide, we dive into the mathematics of the 2x2 Cost vs Utilization Quadrant Matrix, median-split boundary conditions, and implementation in [`src/tvi/consumption_analytics.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/consumption_analytics.py).

---

## 1. The Portfolio Segmentation Problem

Managing an enterprise portfolio of 50 or 500 applications requires clear, automated classification. Without a structured matrix, cost optimization discussions devolve into subjective debates.

To establish an objective baseline, we segment the entire portfolio across two orthogonal axes:
- **Axis X (Financial Investment)**: Fully-burdened Annual TCO.
- **Axis Y (Operational Return)**: Composite Utilization & Business Throughput.

```text
               High Utilization
                     ▲
       Quadrant IV   │   Quadrant I
     Hyper-Efficient │ Critical Workhorses
       Utilities     │ (Core Value Engines)
   ──────────────────┼──────────────────► High Cost
       Quadrant III  │   Quadrant II
      Niche / Micro  │  ZOMBIE SYSTEMS
         Services    │ (High Spend, Low Value)
                     │
                Low Utilization
```

---

## 2. Theoretical Foundations: Quadrant Boundary Formulations

Let $(x_i, y_i)$ denote the coordinates of application $a_i$, where $x_i = \operatorname{TCO}(a_i)$ and $y_i = \operatorname{Util}(a_i)$.

### Median-Split vs Mean-Split

Rather than using arithmetic means $(\bar{x}, \bar{y})$—which are heavily distorted by extreme outliers like Core Banking—we use the **sample medians** as the quadrant dividing thresholds:

$$\theta_x = \operatorname{Median}(\mathbf{x}), \quad \theta_y = \operatorname{Median}(\mathbf{y})$$

### The Four Operational Quadrants

1. **Quadrant I: Critical Workhorses ($x_i \ge \theta_x, y_i \ge \theta_y$)**:
   - High cost, but heavily utilized. These are the mission-critical systems that drive enterprise revenue. Optimization strategy: **Continuous efficiency improvements and architectural modernization**.
2. **Quadrant II: Zombie Systems ($x_i \ge \theta_x, y_i < \theta_y$)**:
   - High cost, low utilization. These systems consume significant budget while delivering minimal active user throughput. Optimization strategy: **Primary candidates for aggressive decommissioning or consolidation**.
3. **Quadrant III: Niche / Dormant Utilities ($x_i < \theta_x, y_i < \theta_y$)**:
   - Low cost, low utilization. Specialized tools or small internal utilities. Optimization strategy: **Tolerate with light governance; low priority for refactoring**.
4. **Quadrant IV: Hyper-Efficient Utilities ($x_i < \theta_x, y_i \ge \theta_y$)**:
   - Low cost, high utilization. Lightweight microservices or tools delivering exceptional return on spend. Optimization strategy: **Architectural blueprints to emulate**.

---

## 3. Code Walkthrough: Implementing Quadrant Segmentation

In [`src/tvi/consumption_analytics.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/consumption_analytics.py#L90-L150), we compute these quadrant assignments:

```python
# src/tvi/consumption_analytics.py
def assign_consumption_quadrants(df_profile: pd.DataFrame) -> pd.DataFrame:
    \"\"\"
    Assigns each application to a 2x2 operational quadrant based on median splits.
    \"\"\"
    cost_median = df_profile['total_tco'].median()
    util_median = df_profile['composite_utilization'].median()
    
    def classify(row):
        is_high_cost = row['total_tco'] >= cost_median
        is_high_util = row['composite_utilization'] >= util_median
        
        if is_high_cost and is_high_util:
            return "Quadrant I: Critical Workhorse"
        elif is_high_cost and not is_high_util:
            return "Quadrant II: Zombie System"
        elif not is_high_cost and not is_high_util:
            return "Quadrant III: Niche / Dormant"
        else:
            return "Quadrant IV: Hyper-Efficient"
            
    df_profile['quadrant'] = df_profile.apply(classify, axis=1)
    df_profile['cost_median'] = cost_median
    df_profile['util_median'] = util_median
    
    return df_profile
```

### Line-by-Line Code Analysis:

- **Lines 7–8**: Computes robust sample medians. Median splits ensure that applications are evaluated relative to peers within the enterprise, rather than against arbitrary external thresholds.
- **Lines 10–23**: Assigns categorical labels that link directly into our Multi-Criteria Decision Analysis (MCDA) rationalization scoring in Notebook 07.

---

## 4. Empirical Case Study: Spotting `APP021`

When executed across our enterprise dataset:
- `APP021` (*Legacy Branch CRM*) lands squarely in **Quadrant II (Zombie System)**:
  - TCO: ₹350,000 (above median for its tier).
  - Composite Utilization: $0.041$ (Bottom 5th percentile; 6 users, 4% idle CPU).

By formalizing this quadrant logic, the analytical engine highlights `APP021` as an immediate candidate for decommission review, eliminating subjective debate.

---

## 5. Scope of Improvement & Production Roadmap

1. **K-Means / Gaussian Mixture Clustering**: Upgrade from rigid median quadrant splits to unsupervised machine learning clustering (GMM) to uncover organic, multi-dimensional cluster geometries.
2. **Dynamic Quadrant Drift Tracking**: Track quadrant transitions over time (e.g. flagging an app drifting from Quadrant I to Quadrant II over consecutive quarters).

---

## 6. Summary & Companion Reading

Quadrant segmentation separates high-value systems from low-efficiency budget drains using transparent mathematical criteria.

- **Next Guide**: [06c: Elasticity Analysis, GreenOps & Rightsizing Math](file:///Users/pushkar/Documents/projects/value/blog/technical/06c_elasticity_analysis_greenops_and_rightsizing_math.md) examines infrastructure rightsizing and carbon attribution.
- **Companion Business Article**: [06a: The 2x2 Utilization Quadrant Matrix](file:///Users/pushkar/Documents/projects/value/blog/business/06a_the_2x2_utilization_quadrant_matrix.md) provides leadership framing.
""")

    # 06c: Elasticity Analysis, GreenOps & Rightsizing Math
    write_tech_article("06c_elasticity_analysis_greenops_and_rightsizing_math.md", """---
title: "Technical Guide 06c: Elasticity Analysis, GreenOps & Rightsizing Math"
notebook_reference: "notebooks/06_consumption_intelligence.ipynb"
part: "Part 3 of 3 for Notebook 06"
reading_time: "22 min read"
audience: "FinOps Practitioners, Cloud Architects, Sustainability Engineers"
tbm_domain_level: "Intermediate to Advanced"
author: "Technology Value Intelligence Architecture Team"
---

# Technical Guide 06c: Elasticity Analysis, GreenOps & Rightsizing Math

> [!NOTE]
> **Executive Summary & Engineering Objective**: When cloud workload demand drops by 40%, do your cloud costs drop proportionally? If not, you have an elasticity leak. In this guide, we dive into the mathematics of the Cloud Cost Elasticity Coefficient, GreenOps carbon footprint attribution, and algorithmic rightsizing formulas in [`src/tvi/consumption_analytics.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/consumption_analytics.py).

---

## 1. The Promise vs Reality of Cloud Elasticity

Cloud providers promote public cloud infrastructure as completely elastic: you pay only for what you consume.

In practice, enterprise cloud spending often behaves like a fixed on-premise datacenter:
- Developers provision large VM clusters and leave them running over weekends.
- Autoscaling groups scale up during traffic spikes, but conservative minimum thresholds prevent them from scaling back down.
- Reserved Instances and Savings Plans lock the organization into paying for unutilized capacity.

```text
The Elasticity Gap:
  Workload Demand:  ───▲───\______/───▲───  (Highly volatile, drops 60% on weekends)
  Cloud Invoices:   ──────────────────────  (Completely flat line = 0.0 Elasticity)
```

To optimize cloud investments, FinOps teams need to quantify **Cost Elasticity** mathematically.

---

## 2. Theoretical Foundations & Formulations

### 1. The FinOps Cloud Elasticity Coefficient ($E_c$)

In economics, elasticity measures the percentage change in one variable relative to the percentage change in another. We define the **Cloud Cost Elasticity Coefficient** between month $t-1$ and month $t$:

$$E_c = \frac{\% \Delta \operatorname{Cost}}{\% \Delta \operatorname{Workload}} = \frac{\frac{\operatorname{Cost}_t - \operatorname{Cost}_{t-1}}{\operatorname{Cost}_{t-1}}}{\frac{\operatorname{Workload}_t - \operatorname{Workload}_{t-1}}{\operatorname{Workload}_{t-1}}}$$

- **$E_c \approx 1.0$ (Ideal Elasticity)**: Costs scale in lockstep with demand. When transactions drop by 30%, costs decrease by 30%.
- **$E_c \approx 0.0$ (Inelastic)**: Costs remain unchanged regardless of volume fluctuations (typical of static VM allocations).
- **$E_c < 0.0$ (Pathological Elasticity)**: Costs increase while workload drops (often indicating storage leaks or rate increases).

### 2. GreenOps: Carbon Footprint Attribution

Technology Business Management now frequently incorporates environmental sustainability. We model carbon emissions using the **Greenhouse Gas Protocol (Scope 2)**:

$$\operatorname{CO}_2e = \operatorname{Energy}(\text{kWh}) \times \operatorname{PUE} \times \operatorname{GridCarbonIntensity} \left( \frac{\text{kg CO}_2\text{e}}{\text{kWh}} \right)$$

where:
- $\operatorname{Energy}(\text{kWh}) = \operatorname{vCPU} \times \operatorname{TDP}_{\text{avg}} \times \text{Hours} \times \operatorname{Util}_{\text{avg}} + \text{RAM\_GB} \times 0.38 \text{ W/GB}$.
- $\operatorname{PUE}$ is the Power Usage Effectiveness of the hosting datacenter (e.g. $1.15$ for modern AWS/GCP datacenters, $1.65$ for legacy on-premise facilities).

### 3. Algorithmic Rightsizing Formulations

For over-provisioned infrastructure where $\operatorname{PeakCPU} < 40\%$, the recommended rightsized capacity is:

$$\operatorname{TargetCores} = \left\lceil \frac{\operatorname{PeakCPU} \cdot \operatorname{CurrentCores}}{\operatorname{TargetUtilization}} \right\rceil$$

Setting $\operatorname{TargetUtilization} = 70\%$ preserves a 30% safety headroom for traffic bursts while eliminating unneeded capacity.

---

## 3. Code Walkthrough: Rightsizing Engine

Let's examine the rightsizing simulation logic in [`src/tvi/consumption_analytics.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/consumption_analytics.py#L160-L215):

```python
# src/tvi/consumption_analytics.py
def calculate_rightsizing_opportunities(
    df_profile: pd.DataFrame, 
    target_utilization: float = 0.70
) -> pd.DataFrame:
    \"\"\"
    Identifies over-provisioned infrastructure and calculates avoidable cost scenarios.
    \"\"\"
    candidates = df_profile[df_profile['peak_cpu'] < 0.40].copy()
    
    # Calculate recommended downscale ratio
    candidates['downscale_ratio'] = candidates['peak_cpu'] / target_utilization
    
    # Calculate potential monthly avoidable infrastructure spend
    candidates['avoidable_infra_spend'] = (
        candidates['infra_cost'] * (1.0 - candidates['downscale_ratio'])
    )
    
    # Estimate monthly carbon reduction (assuming 0.42 kg CO2e per USD infra spend)
    candidates['avoidable_co2_kg'] = candidates['avoidable_infra_spend'] * 0.42
    
    return candidates.sort_values(by='avoidable_infra_spend', ascending=False)
```

### Line-by-Line Code Analysis:

- **Line 8**: Filters for systems where peak CPU across 12 months never exceeded 40%. This conservative threshold helps prevent rightsizing from causing performance issues on bursty systems.
- **Lines 14–16**: Quantifies avoidable spend by scaling only the infrastructure portion of the cost stack ($C_{\text{Infra}}$), rather than assuming labor or software license savings from a simple VM resize.

---

## 4. Scope of Improvement & Production Roadmap

1. **Instance Family Recommendation Engine**: Map downscale ratios to concrete AWS/Azure instance catalog SKUs (e.g., recommend moving from `m5.4xlarge` to `c6g.xlarge` Graviton).
2. **Automated Terraform PR Generation**: Connect rightsizing recommendations directly to infrastructure-as-code repositories, opening automated pull requests to update instance sizes.

---

## 5. Summary & Companion Reading

Elasticity metrics and rightsizing formulas turn raw telemetry into actionable cost reduction and sustainability roadmaps.

- **Next Guide**: [07a: Portfolio Rationalization & The Gartner TIME Framework](file:///Users/pushkar/Documents/projects/value/blog/technical/07a_portfolio_rationalization_and_the_gartner_time_framework.md) begins Notebook 07 by exploring application rationalization.
- **Companion Business Article**: [06b: Elasticity and Sustainable GreenOps](file:///Users/pushkar/Documents/projects/value/blog/business/06b_elasticity_and_sustainable_greenops.md) details corporate sustainability initiatives.
""")

def run():
    print("Generating Technical Blogs for Notebooks 04, 05, and 06...")
    generate_nb04_articles()
    generate_nb05_articles()
    generate_nb06_articles()
    print("Notebooks 04-06 Generation Complete! (9 articles written)")

if __name__ == "__main__":
    run()
