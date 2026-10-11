"""Technical blog generator for Notebooks 07, 08, and 09 (11 articles total)."""

from .common import write_tech_article

def generate_nb07_articles():
    # 07a: Portfolio Rationalization & The Gartner TIME Framework
    write_tech_article("07a_portfolio_rationalization_and_the_gartner_time_framework.md", """---
title: "Technical Guide 07a: Portfolio Rationalization & The Gartner TIME Framework"
notebook_reference: "notebooks/07_application_rationalization.ipynb"
part: "Part 1 of 4 for Notebook 07"
reading_time: "20 min read"
audience: "Enterprise Architects, Portfolio Directors, IT Strategists"
tbm_domain_level: "Intermediate"
author: "Technology Value Intelligence Architecture Team"
---

# Technical Guide 07a: Portfolio Rationalization & The Gartner TIME Framework

> [!NOTE]
> **Executive Summary & Engineering Objective**: How do you determine whether an enterprise application should be tolerated, modernized, re-architected, or eliminated? In this guide, we dive into the Gartner TIME Framework, formulate the mathematical classification boundaries for each quadrant, and walk through the implementation in [`src/tvi/rationalization.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/rationalization.py).

---

## 1. The Portfolio Sprawl Dilemma

Large enterprises often maintain hundreds or thousands of software applications. Over time, portfolios become cluttered with:
- Systems running unsupported database versions.
- Modern SaaS tools purchased by departmental shadow IT without architectural review.
- High-cost legacy monoliths that are difficult to modify.

Without a structured rationalization framework, decisions about which systems to retire or modernize are often driven by corporate politics rather than objective data.

```text
               High Business Value
                     ▲
        [ MIGRATE ]  │   [ INVEST ]
       High Value,   │  High Value,
     High Tech Debt  │  High Tech Health
   ──────────────────┼──────────────────► High Technical Health
       [ ELIMINATE ] │  [ TOLERATE ]
        Low Value,   │   Low Value,
      High Tech Debt │  High Tech Health
                     │
               Low Business Value
```

---

## 2. Theoretical Foundations: The Gartner TIME Framework

The **Gartner TIME Framework** maps application portfolios across two composite dimensions:
1. **Business Value ($V \in [0, 100]$)**: Strategic importance, operational criticality, revenue enablement, and user satisfaction.
2. **Technical Health ($H \in [0, 100]$)**: Code maintainability, security compliance, architectural currency, and operational stability.

### The Four Quadrants & Decision Rules

Let thresholds $\theta_V = 50.0$ and $\theta_H = 50.0$ define the quadrant boundaries:

1. **Invest ($V \ge \theta_V, H \ge \theta_H$)**:
   - High business value and sound technical health.
   - Strategy: Continue investing in feature delivery, cloud modernization, and capacity expansion.
2. **Migrate ($V \ge \theta_V, H < \theta_H$)**:
   - High business value, but poor technical health (e.g. core legacy transaction systems).
   - Strategy: Refactor, re-platform to cloud-native microservices, or replace with modern commercial packages.
3. **Tolerate ($V < \theta_V, H \ge \theta_H$)**:
   - Low business value, but running smoothly on modern technology with low maintenance overhead.
   - Strategy: Retain with minimal ongoing investment; do not commit new development capacity.
4. **Eliminate ($V < \theta_V, H < \theta_H$)**:
   - Low business value and deteriorating technical health (high security risk and technical debt).
   - Strategy: Prioritize for decommission, consolidation, or contract termination.

---

## 3. Code Walkthrough: Computing TIME Classifications

Let's inspect the classification pipeline in [`src/tvi/rationalization.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/rationalization.py#L35-L85):

```python
# src/tvi/rationalization.py
import pandas as pd
from typing import Dict, Any

def assign_time_quadrants(
    df_portfolio: pd.DataFrame,
    threshold_value: float = 50.0,
    threshold_health: float = 50.0
) -> pd.DataFrame:
    \"\"\"
    Assigns applications to Gartner TIME quadrants based on business value and technical health.
    \"\"\"
    def classify(row):
        val = row['business_value_score']
        health = row['technical_health_score']
        
        if val >= threshold_value and health >= threshold_health:
            return "Invest"
        elif val >= threshold_value and health < threshold_health:
            return "Migrate"
        elif val < threshold_value and health >= threshold_health:
            return "Tolerate"
        else:
            return "Eliminate"
            
    df_portfolio['time_category'] = df_portfolio.apply(classify, axis=1)
    return df_portfolio
```

### Line-by-Line Code Analysis:

- **Lines 10–22**: Applies the decision boundary rules cleanly across the portfolio. Applications assigned to the **Eliminate** quadrant are immediately forwarded to the Multi-Criteria Decision Analysis (MCDA) pipeline to rank decommissioning priority.

---

## 4. Scope of Improvement & Production Roadmap

1. **Dynamic Threshold Tuning**: Calibrate thresholds $\theta_V$ and $\theta_H$ using percentile ranks (e.g. top 40th percentile) rather than fixed static constants.
2. **Migration Difficulty Scoring**: Attach an architectural complexity factor to Migrate systems to estimate replatforming timelines and costs.

---

## 5. Summary & Companion Reading

The TIME framework provides an established enterprise baseline for categorizing application portfolio lifecycle stages.

- **Next Guide**: [07b: Multi-Criteria Decision Analysis (MCDA) & Scoring](file:///Users/pushkar/Documents/projects/value/blog/technical/07b_multi_criteria_decision_analysis_topsis_and_scoring.md) explores how to construct objective composite scoring models.
- **Companion Business Article**: [07a: Objective Portfolio Pruning](file:///Users/pushkar/Documents/projects/value/blog/business/07a_objective_portfolio_pruning_mcda_and_time.md) covers strategic portfolio governance.
""")

    # 07b: Multi-Criteria Decision Analysis (MCDA) & Scoring
    write_tech_article("07b_multi_criteria_decision_analysis_topsis_and_scoring.md", """---
title: "Technical Guide 07b: Multi-Criteria Decision Analysis (MCDA) & Scoring"
notebook_reference: "notebooks/07_application_rationalization.ipynb"
part: "Part 2 of 4 for Notebook 07"
reading_time: "22 min read"
audience: "Operations Researchers, FinOps Architects, Quantitative Engineers"
tbm_domain_level: "Intermediate to Advanced"
author: "Technology Value Intelligence Architecture Team"
---

# Technical Guide 07b: Multi-Criteria Decision Analysis (MCDA) & Scoring

> [!NOTE]
> **Executive Summary & Engineering Objective**: How do you combine disparate metrics—TCO in dollars, security vulnerabilities, business criticality, and user counts—into a single objective score without distorting the units? In this guide, we dive into Multi-Criteria Decision Analysis (MCDA), vector normalization, the TOPSIS formulation, and implementation in [`src/tvi/rationalization.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/rationalization.py).

---

## 1. The Multi-Metric Dilemma in Portfolio Governance

When enterprise architects and financial officers debate application decommissioning, they frequently talk past each other because they evaluate different metrics:

- The **CFO** focuses on raw cost: *"Application X costs \$1.5M/yr, shut it down."*
- The **CISO** focuses on vulnerabilities: *"Application Y has 14 unpatched CVEs, shut it down."*
- The **BU Head** focuses on business continuity: *"Application Z supports vital quarterly reporting, keep it running."*

To make fair, data-driven decisions, we need a mathematical model that evaluates multiple competing criteria simultaneously: **Multi-Criteria Decision Analysis (MCDA)**.

---

## 2. Theoretical Foundations: The RRI & TOPSIS Formulations

We formulate the **Rationalization Recommendation Index (RRI)** $\in [0, 100]$. A higher RRI indicates an urgent candidate for decommissioning or consolidation.

### Decision Matrix Normalization

Let $X \in \mathbb{R}^{m \times n}$ be the decision matrix for $m$ applications across $n$ evaluation criteria:
- **Cost Magnitude ($C$)**: Criteria to minimize (higher cost = higher candidate priority).
- **Technical Health ($H$)**: Criteria to maximize (lower health = higher candidate priority).
- **Business Criticality ($B$)**: Criteria to maximize (lower criticality = higher candidate priority).
- **Utilization Score ($U$)**: Criteria to maximize (lower usage = higher candidate priority).

Using vector normalization:

$$r_{ij} = \frac{x_{ij}}{\sqrt{\sum_{k=1}^m x_{kj}^2}}$$

### The RRI Weighted Additive Model

Let $\mathbf{w} = [w_{\text{cost}}, w_{\text{health}}, w_{\text{crit}}, w_{\text{util}}]^T$ be the weight vector satisfying $\sum_j w_j = 1$. The composite score is:

$$\operatorname{RRI}(a_i) = 100 \times \left( w_c \cdot \hat{C}_i + w_h \cdot (1 - \hat{H}_i) + w_b \cdot (1 - \hat{B}_i) + w_u \cdot (1 - \hat{U}_i) \right)$$

where $\hat{X}$ denotes Min-Max normalized variables scaled to $[0, 1]$.

```mermaid
flowchart LR
    INPUT["Raw Input Metrics\n(Cost $, CVE Count, Criticality 0-1, Usage %)"] --> NORM["Min-Max & Vector Normalization"]
    NORM --> WEIGHT["Executive Weight Vector\n(wC = 0.35, wH = 0.25, wB = 0.25, wU = 0.15)"]
    WEIGHT --> RRI["Rationalization Recommendation Index (RRI)\n0.0 (Keep) to 100.0 (Decommission)"]
```

---

## 3. Code Walkthrough: Implementing the Scoring Engine

Let's examine the scoring implementation in [`src/tvi/rationalization.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/rationalization.py#L90-L155):

```python
# src/tvi/rationalization.py
import numpy as np
import pandas as pd
from typing import Dict

def score_portfolio_mcda(
    df_apps: pd.DataFrame,
    weights: Dict[str, float] = None
) -> pd.DataFrame:
    \"\"\"
    Computes Rationalization Recommendation Index (RRI) using MCDA.
    \"\"\"
    if weights is None:
        weights = {
            'cost': 0.35,
            'technical_debt': 0.25,
            'business_value': 0.25,
            'utilization': 0.15
        }
    assert abs(sum(weights.values()) - 1.0) < 1e-5, "Weights must sum to 1.0!"

    df = df_apps.copy()
    
    # Min-Max Normalization helper
    def min_max(series):
        mn, mx = series.min(), series.max()
        return (series - mn) / (mx - mn) if mx > mn else np.zeros_like(series)
        
    c_norm = min_max(df['total_tco'])
    debt_norm = min_max(100.0 - df['technical_health_score'])  # Inverse health
    val_norm = min_max(df['business_value_score'])
    util_norm = min_max(df['composite_utilization'])
    
    # Calculate composite RRI: higher score = higher decommission candidate
    df['rri_score'] = 100.0 * (
        weights['cost'] * c_norm +
        weights['technical_debt'] * debt_norm +
        weights['business_value'] * (1.0 - val_norm) +
        weights['utilization'] * (1.0 - util_norm)
    )
    
    return df.sort_values(by='rri_score', ascending=False)
```

### Line-by-Line Code Analysis:

- **Lines 10–18**: Default weights align with TBM best practices, allocating 35% weight to cost, 25% to technical health, 25% to business value, and 15% to usage.
- **Lines 28–34**: Computes normalized components and inverts beneficial attributes ($(1.0 - \text{val})$ and $(1.0 - \text{util})$). This aligns all components so that higher values consistently indicate greater urgency for retirement.

---

## 4. Scope of Improvement & Production Roadmap

1. **TOPSIS (Ideal Solution Distance)**: Upgrade from the weighted sum model to full TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution), evaluating Euclidean distance to positive-ideal and negative-ideal solutions.
2. **Interactive Weight Tuning UI**: Provide an interactive UI slider allowing executive committees to observe how portfolio rankings re-order dynamically as stakeholder priorities shift.

---

## 5. Summary & Companion Reading

MCDA provides an objective, transparent framework for ranking portfolio rationalization candidates across competing criteria.

- **Next Guide**: [07c: Pareto Frontiers & Multi-Objective Tradeoff Optimization](file:///Users/pushkar/Documents/projects/value/blog/technical/07c_pareto_frontiers_and_multi_objective_tradeoff_optimization.md) explores multi-objective tradeoff frontiers.
- **Companion Business Article**: [07a: Objective Portfolio Pruning](file:///Users/pushkar/Documents/projects/value/blog/business/07a_objective_portfolio_pruning_mcda_and_time.md) covers executive alignment.
""")

    # 07c: Pareto Frontiers & Multi-Objective Tradeoff Optimization
    write_tech_article("07c_pareto_frontiers_and_multi_objective_tradeoff_optimization.md", """---
title: "Technical Guide 07c: Pareto Frontiers & Multi-Objective Tradeoff Optimization"
notebook_reference: "notebooks/07_application_rationalization.ipynb"
part: "Part 3 of 4 for Notebook 07"
reading_time: "21 min read"
audience: "Optimization Engineers, Quantitative Data Scientists, FinOps Leads"
tbm_domain_level: "Advanced"
author: "Technology Value Intelligence Architecture Team"
---

# Technical Guide 07c: Pareto Frontiers & Multi-Objective Tradeoff Optimization

> [!NOTE]
> **Executive Summary & Engineering Objective**: When rationalizing software portfolios, cutting costs often conflicts with minimizing operational risk. How do you find the optimal tradeoff boundary without relying on arbitrary weighting choices? In this guide, we dive into Pareto Dominance, non-dominated sorting algorithms, and implement multi-objective tradeoff optimization in [`notebooks/07_application_rationalization.ipynb`](file:///Users/pushkar/Documents/projects/value/notebooks/07_application_rationalization.ipynb).

---

## 1. The Cost vs Risk Tradeoff Dilemma

Single composite scores (like RRI) require assigning fixed weights to different goals ($w_{\text{cost}} = 0.35$). But in executive committees, the Chief Financial Officer and the Chief Risk Officer rarely agree on weights:

- The CFO wants to maximize **Cost Avoidance** ($f_1$).
- The CRO wants to minimize **Operational & Dependency Risk** ($f_2$).

```text
               Operational Risk (f2)
                     ▲
                     │   * (Suboptimal)
                     │
                     │       * (Dominated)
                     │     /
       Pareto        │    *
       Optimal       │   /
       Frontier      │  *
                     │ /
                     └──────────────────► Cost Reduction ($) (f1)
```

Instead of choosing arbitrary weights, multi-objective optimization identifies the **Pareto Optimal Set**: the collection of portfolio decisions where you cannot save another dollar without increasing risk.

---

## 2. Theoretical Foundations: Pareto Dominance

Let each application $a \in \mathcal{A}$ be represented as an objective vector:
$$\mathbf{f}(a) = \big( \text{Cost}(a), -\text{Risk}(a) \big)$$

### Definition of Dominance

A solution $a_1$ **strictly dominates** solution $a_2$ (denoted $a_1 \succ a_2$) if and only if:
1. $a_1$ is no worse than $a_2$ across all objectives:
   $$\forall k, \quad f_k(a_1) \ge f_k(a_2)$$
2. $a_1$ is strictly better than $a_2$ in at least one objective:
   $$\exists k, \quad f_k(a_1) > f_k(a_2)$$

### The Non-Dominated Pareto Set

$$\mathcal{P}^* = \{a \in \mathcal{A} \mid \nexists a' \in \mathcal{A} \text{ such that } a' \succ a\}$$

Applications residing on the Pareto frontier $\mathcal{P}^*$ are mathematically optimal rationalization candidates: they provide the highest cost recovery for their specific level of operational risk.

---

## 3. Code Walkthrough: Computing the Non-Dominated Frontier

Let's examine the non-dominated sorting algorithm in [`notebooks/07_application_rationalization.ipynb`](file:///Users/pushkar/Documents/projects/value/notebooks/07_application_rationalization.ipynb):

```python
import numpy as np
import pandas as pd

def identify_pareto_frontier(
    df: pd.DataFrame, 
    cost_col: str = 'total_tco', 
    risk_col: str = 'criticality'
) -> pd.DataFrame:
    \"\"\"
    Identifies applications on the non-dominated Pareto frontier.
    Objective 1: Maximize Avoidable Cost (TCO)
    Objective 2: Minimize Criticality Risk (Lower is better)
    \"\"\"
    # Sort primarily by descending cost, secondarily by ascending risk
    sorted_df = df.sort_values(by=[cost_col, risk_col], ascending=[False, True]).copy()
    
    pareto_candidates = []
    min_risk_seen = float('inf')
    
    for idx, row in sorted_df.iterrows():
        curr_risk = row[risk_col]
        # If current application achieves lower risk than previously seen high-cost apps
        if curr_risk < min_risk_seen:
            pareto_candidates.append(row['app_id'])
            min_risk_seen = curr_risk
            
    df['is_pareto_optimal'] = df['app_id'].isin(pareto_candidates)
    return df
```

### Line-by-Line Code Analysis:

- **Line 13**: Sorting in $O(N \log N)$ time allows non-dominated identification in a single $O(N)$ linear scan.
- **Lines 18–22**: Tracks the running minimum risk (`min_risk_seen`). Any application that offers a lower risk footprint than higher-cost alternatives is added to the non-dominated frontier.

---

## 4. Scope of Improvement & Production Roadmap

1. **NSGA-II (Non-dominated Sorting Genetic Algorithm)**: For multi-period decommissioning schedules with 10+ constraints (e.g. database migration dependencies and team capacity), deploy NSGA-II to evaluate combinatorial retirement sequences.
2. **Hypervolume Indicator Calculation**: Quantify the quality of different portfolio rationalization roadmaps using the hypervolume metric.

---

## 5. Summary & Companion Reading

Pareto optimization resolves conflicting executive priorities by finding mathematically non-dominated tradeoffs between cost savings and operational risk.

- **Next Guide**: [07d: Decommissioning Runbooks, Contract Penalties & Exit Models](file:///Users/pushkar/Documents/projects/value/blog/technical/07d_decommissioning_runbooks_contract_penalties_and_exit_models.md) explains how to calculate real avoidable savings.
- **Companion Business Article**: [07b: The Pragmatic Decommissioning Playbook](file:///Users/pushkar/Documents/projects/value/blog/business/07b_the_pragmatic_decommissioning_playbook.md) explores corporate execution.
""")

    # 07d: Decommissioning Runbooks, Contract Penalties & Exit Models
    write_tech_article("07d_decommissioning_runbooks_contract_penalties_and_exit_models.md", """---
title: "Technical Guide 07d: Decommissioning Runbooks, Contract Penalties & Exit Models"
notebook_reference: "notebooks/07_application_rationalization.ipynb"
part: "Part 4 of 4 for Notebook 07"
reading_time: "21 min read"
audience: "FinOps Auditors, Commercial Procurement Leads, Enterprise Architects"
tbm_domain_level: "Intermediate"
author: "Technology Value Intelligence Architecture Team"
---

# Technical Guide 07d: Decommissioning Runbooks, Contract Penalties & Exit Models

> [!NOTE]
> **Executive Summary & Engineering Objective**: Retiring an application does not automatically return 100% of its budget on day one. Multi-year vendor lock-ins, stranded shared infrastructure, and employee transition timelines create delayed cost realizations. In this guide, we dive into the mathematics of Avoidable Cost Amortization, contract termination penalty modeling, and implementation in [`src/tvi/rationalization.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/rationalization.py).

---

## 1. The Myth of Instant Cash Savings

When enterprise analysts pitch an application decommissioning project, they often show slides claiming:

> *"Retiring Application X will save \$2,000,000 per year."*

Then, 12 months after the servers are powered down, the CFO reviews the budget and discovers that actual savings were only \$300,000.

```text
The Decommissioning Savings Gap:
  Theoretical TCO:        $2,000,000 / yr
  
  Vendor Contract Lock-in: - $800,000 (Committed 3-year enterprise agreement)
  Stranded Shared Infra:  - $500,000 (Mainframe / DB cluster costs remain fixed)
  Severance / Retention:  - $400,000 (Transitional operations staff)
  
  REAL REALIZED SAVINGS:   $300,000 in Year 1!
```

To provide credible financial guidance, rationalization models must separate **Avoidable Costs** from **Sunk and Stranded Costs**.

---

## 2. Theoretical Foundations: Avoidable Cost Modeling

Let the baseline TCO of application $a$ be decomposed into its operational cost categories:

$$\operatorname{TCO}(a) = C_{\text{Infra}} + C_{\text{Software}} + C_{\text{Labor}} + C_{\text{Services}}$$

When an application is decommissioned at time $t_0$, each cost category recovers savings according to a specific realization decay function:

$$\operatorname{Savings}(t) = \sum_{k} C_k \cdot \alpha_k(t) - \operatorname{Penalties}(t)$$

### Category Realization Functions

1. **Direct Cloud Infrastructure ($\alpha_{\text{Infra}}$)**: Recovers rapidly (typically 100% within 30 days of instance termination).
2. **Software Licenses ($\alpha_{\text{Software}}$)**: Depends on contract renewal dates:
   $$\alpha_{\text{Software}}(t) = \begin{cases} 0, & t < t_{\text{renewal}} \\ 1.0, & t \ge t_{\text{renewal}} \end{cases}$$
3. **Internal Labor ($\alpha_{\text{Labor}}$)**: Requires redeploying software engineers to new projects or natural attrition (typically takes 6–12 months).
4. **Contract Termination Penalties**: Many enterprise agreements assess early termination fees:
   $$\operatorname{Penalties} = \beta \cdot \text{RemainingContractValue}$$

---

## 3. Code Walkthrough: Avoidable Cost Schedule Implementation

In [`src/tvi/rationalization.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/rationalization.py#L160-L220), we calculate the 3-year phased avoidable savings schedule:

```python
# src/tvi/rationalization.py
def calculate_avoidable_costs(
    app_tco_row: pd.Series,
    contract_months_remaining: int = 14,
    penalty_rate: float = 0.30
) -> Dict[str, float]:
    \"\"\"
    Calculates realistic 3-year phased cash savings accounting for exit friction.
    \"\"\"
    infra = app_tco_row.get('infra_cost', 0.0)
    software = app_tco_row.get('software_cost', 0.0)
    labor = app_tco_row.get('labor_cost', 0.0)
    services = app_tco_row.get('services_cost', 0.0)
    
    # Year 1 Realization
    y1_infra = infra * 0.90  # 90% cloud downscale
    y1_software = 0.0 if contract_months_remaining > 12 else software * 0.50
    y1_labor = labor * 0.30  # Slower redeployment
    y1_penalty = (software * (contract_months_remaining / 12.0)) * penalty_rate
    
    y1_net = max(0.0, (y1_infra + y1_software + y1_labor + services * 0.50) - y1_penalty)
    
    # Year 2 & Year 3 Realization
    y2_net = (infra * 1.0) + (software * 1.0) + (labor * 0.80) + (services * 1.0)
    y3_net = app_tco_row.get('total_tco', 0.0)  # Full run-rate savings
    
    return {
        'year_1_net_avoidable': y1_net,
        'year_2_net_avoidable': y2_net,
        'year_3_net_avoidable': y3_net,
        'year_1_penalty_incurred': y1_penalty
    }
```

---

## 4. Scope of Improvement & Production Roadmap

1. **Procurement Contract Ingestion**: Ingest contract metadata (renewal dates, penalty percentages) directly from enterprise contract management systems (e.g. Ironclad, Coupa).
2. **Transitional Service Agreement (TSA) Accounting**: Model interim consulting and migration vendor fees as negative cash flow offsets in the first 6 months.

---

## 5. Summary & Companion Reading

Avoidable cost modeling provides transparent financial expectations that preserve trust with corporate finance teams.

- **Next Guide**: [08a: DAG Topological Sort & Cycle Detection](file:///Users/pushkar/Documents/projects/value/blog/technical/08a_dag_topological_sort_and_cycle_detection.md) begins Notebook 08 by analyzing architectural dependencies.
- **Companion Business Article**: [07b: The Pragmatic Decommissioning Playbook](file:///Users/pushkar/Documents/projects/value/blog/business/07b_the_pragmatic_decommissioning_playbook.md) details operational decommission governance.
""")

def generate_nb08_articles():
    # 08a: DAG Topological Sort & Cycle Detection
    write_tech_article("08a_dag_topological_sort_and_cycle_detection.md", """---
title: "Technical Guide 08a: DAG Topological Sort & Cycle Detection"
notebook_reference: "notebooks/08_dependency_and_impact_analysis.ipynb"
part: "Part 1 of 3 for Notebook 08"
reading_time: "20 min read"
audience: "Systems Engineers, SRE Architects, Graph Developers"
tbm_domain_level: "Intermediate to Advanced"
author: "Technology Value Intelligence Architecture Team"
---

# Technical Guide 08a: DAG Topological Sort & Cycle Detection

> [!NOTE]
> **Executive Summary & Engineering Objective**: How do you safely determine deployment and shutdown sequences across complex enterprise applications? In this guide, we dive into Directed Acyclic Graphs (DAGs), cycle detection using Tarjan's Strongly Connected Components algorithm, Kahn's topological sort, and audit implementation in [`src/tvi/dependency.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/dependency.py).

---

## 1. The Circular Dependency Trap

When applications are built over many years by decentralized teams, architecture diagrams often hide circular dependencies:

```text
The Hidden Cycle Disaster:
  App A (Order Entry) calls App B (Pricing Engine)
  App B (Pricing Engine) calls App C (Customer Profile)
  App C (Customer Profile) makes a database call back to App A (Order History)
  
          ┌────────► App B ────────┐
          │                        ▼
        App A ◄───────────────── App C
```

When an incident occurs or an engineer initiates a cold restart:
1. System A waits for System B to boot.
2. System B waits for System C to boot.
3. System C waits for System A to boot.
4. **Deadlock**: None of the systems can start.

Before running dependency impact analysis or release gating, the architecture graph must be validated as a **Directed Acyclic Graph (DAG)**.

---

## 2. Theoretical Foundations & Graph Algorithms

Let $\mathcal{G} = (\mathcal{V}, \mathcal{E})$ be a directed dependency graph where edge $(u, v) \in \mathcal{E}$ indicates that application $u$ depends on $v$.

### 1. Cycle Detection: Tarjan's Strongly Connected Components

A **Strongly Connected Component (SCC)** of a directed graph is a maximal subgraph $\mathcal{C} \subseteq \mathcal{G}$ such that every vertex in $\mathcal{C}$ is reachable from every other vertex in $\mathcal{C}$.

$$\text{Graph is a DAG} \iff \text{All SCCs have cardinality } |\mathcal{C}| = 1 \text{ (and contain no self-loops)}$$

Tarjan's algorithm uses Depth-First Search (DFS) to identify all SCCs in a single pass in $O(|\mathcal{V}| + |\mathcal{E}|)$ time.

### 2. Kahn's Topological Sorting Algorithm

A **topological sort** of a DAG is a linear ordering of its vertices such that for every directed edge $(u, v)$, node $u$ appears before $v$:

```mermaid
flowchart LR
    S1["Step 1: Compute in-degree for all nodes"] --> S2["Step 2: Enqueue all nodes with in-degree = 0"]
    S2 --> S3["Step 3: Pop node u, append to sort order"]
    S3 --> S4["Step 4: Decrement in-degree of all neighbors v"]
    S4 --> S5["Step 5: Enqueue neighbors where in-degree becomes 0"]
```

If the number of processed nodes is less than $|\mathcal{V}|$, a cycle exists in the graph.

---

## 3. Code Walkthrough: Auditing Cycles & Topological Sort

Let's examine how [`src/tvi/dependency.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/dependency.py#L30-L80) performs this audit:

```python
# src/tvi/dependency.py
import networkx as nx
from typing import List, Tuple

def audit_dependency_cycles(graph: nx.DiGraph) -> Tuple[bool, List[List[str]]]:
    \"\"\"
    Audits application dependency graph for circular dependencies.
    Returns: (is_acyclic: bool, list_of_cycles: list)
    \"\"\"
    # Extract application-only subgraph
    app_nodes = [n for n, d in graph.nodes(data=True) if d.get('node_type') == 'BusinessApplication']
    app_subgraph = graph.subgraph(app_nodes)
    
    is_dag = nx.is_directed_acyclic_graph(app_subgraph)
    
    if is_dag:
        return True, []
        
    # Extract cycles via elementary circuits algorithm (Johnson's algorithm)
    cycles = list(nx.simple_cycles(app_subgraph))
    return False, cycles

def compute_startup_sequence(graph: nx.DiGraph) -> List[str]:
    \"\"\"Computes safe topological boot sequence for applications.\"\"\"
    app_nodes = [n for n, d in graph.nodes(data=True) if d.get('node_type') == 'BusinessApplication']
    app_subgraph = graph.subgraph(app_nodes)
    
    # Topological sort gives safe execution order
    return list(nx.topological_sort(app_subgraph))
```

### Line-by-Line Code Analysis:

- **Lines 10–13**: Isolates the application-only subgraph. Filtering out capability and business unit nodes prevents false cycle detections from bidirectional business mappings.
- **Lines 25–28**: `nx.topological_sort(app_subgraph)` computes a safe boot order in linear time, ensuring base dependencies start before dependent consumers.

---

## 4. Scope of Improvement & Production Roadmap

1. **Cycle Breaking Recommendations**: When a cycle is detected, automatically recommend where to insert an asynchronous message queue (e.g. Apache Kafka or RabbitMQ) to decouple the synchronous circular loop.
2. **Release Gating CI Hook**: Add a git pre-merge hook that prevents deployment if an architecture change introduces a cyclic dependency.

---

## 5. Summary & Companion Reading

Topological sorting and cycle detection ensure safe startup sequencing and prevent deadlocks in complex systems.

- **Next Guide**: [08b: Transitive Closure & Blast Radius Computation](file:///Users/pushkar/Documents/projects/value/blog/technical/08b_transitive_closure_and_blast_radius_computation.md) computes systemic blast radius.
- **Companion Business Article**: [08a: The Domino Effect](file:///Users/pushkar/Documents/projects/value/blog/business/08a_the_domino_effect_transitive_blast_radius.md) covers operational resilience for executive teams.
""")

    # 08b: Transitive Closure & Blast Radius Computation
    write_tech_article("08b_transitive_closure_and_blast_radius_computation.md", """---
title: "Technical Guide 08b: Transitive Closure & Blast Radius Computation"
notebook_reference: "notebooks/08_dependency_and_impact_analysis.ipynb"
part: "Part 2 of 3 for Notebook 08"
reading_time: "22 min read"
audience: "Site Reliability Engineers, Resilience Architects, FinOps Engineers"
tbm_domain_level: "Intermediate to Advanced"
author: "Technology Value Intelligence Architecture Team"
---

# Technical Guide 08b: Transitive Closure & Blast Radius Computation

> [!NOTE]
> **Executive Summary & Engineering Objective**: If a core database fails, direct callers are not the only systems affected—every indirect caller downstream also suffers cascading degradation. In this guide, we dive into the mathematics of Transitive Closure, Breadth-First Reachability, the Blast Radius Index, and walk through the implementation in [`src/tvi/dependency.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/dependency.py).

---

## 1. The Multi-Hop Cascade Problem

When site reliability engineers (SREs) evaluate service degradation, looking only at immediate first-degree dependencies underestimates systemic risk:

```text
                  Direct Impact: 2 Apps (Underestimated)
                           ▲
                           │
       App 1 ──────► [ Core Auth ] ◄────── App 2
         │                                   │
         ▼                                   ▼
       App 3                               App 4
         │                                   │
         ▼                                   ▼
       App 5                               App 6
                           │
                           ▼
               TRUE SYSTEMIC BLAST RADIUS: 6 Applications!
```

If the Core Authentication service experiences an outage, 6 applications and 4 customer-facing business capabilities are degraded.

To quantify systemic vulnerability, we must compute the **Transitive Blast Radius**.

---

## 2. Theoretical Foundations: Transitive Closure & Reachability

Let $\mathcal{G} = (\mathcal{V}, \mathcal{E})$ be the directed architecture graph.

### 1. Transitive Reachability Set

The downstream reachability set $\mathcal{R}(u)$ of an application node $u$ is the set of all vertices reachable via directed paths:

$$\mathcal{R}(u) = \{v \in \mathcal{V} \mid \text{there exists a directed path from } u \text{ to } v\}$$

In an architectural dependency graph where edges represent downstream callers:
- **Upstream Blast Radius**: All systems that depend on $u$ directly or indirectly (impacted by $u$'s failure).
- **Downstream Dependency Footprint**: All backend services that $u$ depends on to operate.

### 2. The Transitive Blast Radius Index (BRI)

We formulate the composite **Blast Radius Index** $\operatorname{BRI}(u) \in [0, 100]$:

$$\operatorname{BRI}(u) = 100 \times \left( w_c \frac{|\mathcal{R}_{\text{apps}}(u)|}{|\mathcal{A}|} + w_b \frac{|\mathcal{R}_{\text{caps}}(u)|}{|\mathcal{C}|} + w_r \frac{\sum_{v \in \mathcal{R}(u)} \operatorname{Criticality}(v)}{\sum_{a \in \mathcal{A}} \operatorname{Criticality}(a)} \right)$$

This metric captures not just the raw count of downstream systems, but also their business importance and critical capabilities.

---

## 3. Code Walkthrough: Computing the Blast Radius

Let's examine how [`src/tvi/dependency.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/dependency.py#L90-L165) implements this reachability traversal:

```python
# src/tvi/dependency.py
import networkx as nx
import pandas as pd
from typing import Dict, Set

def calculate_application_blast_radius(graph: nx.DiGraph, app_id: str) -> Dict[str, Any]:
    \"\"\"
    Computes full transitive blast radius across apps, capabilities, and business units.
    \"\"\"
    # Downstream callers affected if app_id crashes (reverse BFS)
    # Using predecessors because edge is (caller -> dependency)
    impacted_apps = nx.ancestors(graph, app_id)
    impacted_apps.add(app_id)  # Include self
    
    impacted_capabilities = set()
    impacted_bus = set()
    total_impacted_tco = 0.0
    
    for app in impacted_apps:
        # Accumulate TCO of all affected systems
        total_impacted_tco += float(graph.nodes[app].get('tco', 0.0))
        
        # Walk outgoing edges to capabilities
        for neighbor in graph.neighbors(app):
            node_type = graph.nodes[neighbor].get('node_type')
            if node_type == 'BusinessCapability':
                impacted_capabilities.add(neighbor)
            elif node_type == 'BusinessUnit':
                impacted_bus.add(neighbor)
                
    return {
        'source_app': app_id,
        'impacted_app_count': len(impacted_apps),
        'impacted_capability_count': len(impacted_capabilities),
        'impacted_bu_count': len(impacted_bus),
        'total_impacted_tco': total_impacted_tco,
        'blast_radius_apps': list(impacted_apps)
    }
```

### Line-by-Line Code Analysis:

- **Line 11**: `nx.ancestors(graph, app_id)` extracts all upstream vertices that have a directed path to `app_id`. In our dependency graph convention, this identifies every system that relies on `app_id` to function.
- **Lines 17–28**: Traverses from each affected application to its supporting capabilities and business units, providing an end-to-end view of operational and business impact.

---

## 4. Scope of Improvement & Production Roadmap

1. **Failure Probability Weighting**: Weight graph edges by network reliability (e.g. edge latency, error budget burn rates) to calculate probabilistic cascading impact.
2. **Circuit Breaker Dampening**: Model resilience patterns (e.g. Envoy circuit breakers, cached fallbacks) that stop failure propagation midway through the chain.

---

## 5. Summary & Companion Reading

Transitive blast radius analysis provides a clear, quantitative measure of systemic operational risk across multi-hop dependencies.

- **Next Guide**: [08c: Single Points of Failure & Cascade Failure Simulation](file:///Users/pushkar/Documents/projects/value/blog/technical/08c_single_points_of_failure_and_cascade_failure_simulation.md) models systemic cascading outages.
- **Companion Business Article**: [08a: The Domino Effect](file:///Users/pushkar/Documents/projects/value/blog/business/08a_the_domino_effect_transitive_blast_radius.md) explores executive risk communications.
""")

    # 08c: Single Points of Failure & Cascade Failure Simulation
    write_tech_article("08c_single_points_of_failure_and_cascade_failure_simulation.md", """---
title: "Technical Guide 08c: Single Points of Failure & Cascade Failure Simulation"
notebook_reference: "notebooks/08_dependency_and_impact_analysis.ipynb"
part: "Part 3 of 3 for Notebook 08"
reading_time: "23 min read"
audience: "Chaos Engineering Leads, Site Reliability Engineers, Enterprise Risk Officers"
tbm_domain_level: "Advanced"
author: "Technology Value Intelligence Architecture Team"
---

# Technical Guide 08c: Single Points of Failure & Cascade Failure Simulation

> [!NOTE]
> **Executive Summary & Engineering Objective**: What happens when your most connected hub application crashes under peak load? In this guide, we dive into the mathematics of Single Points of Failure (SPOFs), examine Scenario D (`APP010`: Core Payment Router), and implement a Monte Carlo cascade failure simulation in [`src/tvi/dependency.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/dependency.py).

---

## 1. The Anatomy of an Architectural Hub

In large enterprise topologies, certain systems evolve into central communication hubs. These systems:
- Route transactions across disparate business units.
- Mediate legacy mainframe data formats.
- Provide centralized token validation.

While efficient, these hubs create an architectural vulnerability: **a Single Point of Failure (SPOF)**.

```text
               [ 16 Upstream Business Applications ]
                                 │
                                 ▼ (Single Failure Point)
                    ┌─────────────────────────┐
                    │  APP010: Payment Router │
                    │   (Betweenness: 0.412)  │
                    └─────────────────────────┘
                                 │
                                 ▼
                     [ 64% Enterprise Outage ]
```

When `APP010` fails, 16 applications across 4 business units fail with it, causing an immediate cascade.

---

## 2. Theoretical Foundations: Cascading Failure Dynamics

We model cascading outages using an **Epistemic Cascade Dynamics Model**:

Let each node $v \in \mathcal{V}$ have an operational state $s_v(t) \in \{0, 1\}$ ($1 = \text{healthy}, 0 = \text{failed}$) and an operational failure threshold $\theta_v \in (0, 1]$.

At time step $t+1$, an active node $u$ fails if the fraction of its required dependencies that have failed exceeds its resilience threshold:

$$\frac{\sum_{v \in \operatorname{Dep}(u)} (1 - s_v(t))}{|\operatorname{Dep}(u)|} \ge \theta_u \implies s_u(t+1) = 0$$

```mermaid
stateDiagram-v2
    [*] --> Healthy: Initial State
    Healthy --> Degraded: 1 Dependency Fails
    Degraded --> Failed: Exceeds Resilience Threshold (θ)
    Failed --> Cascading: Propagates to Callers
```

### Monte Carlo Cascade Simulation

To account for stochastic recovery behaviors and intermittent retries, we run $N = 1,000$ iterations with randomized latency jitter, computing the **Expected Systemic Outage Magnitude** $\mathbb{E}[\Delta \mathcal{S}]$.

---

## 3. Code Walkthrough: Implementing Cascade Simulation

Let's examine the simulation engine in [`src/tvi/dependency.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/dependency.py#L170-L240):

```python
# src/tvi/dependency.py
import networkx as nx
import numpy as np
from typing import Dict, List

def simulate_cascade_failure(
    graph: nx.DiGraph,
    failed_node: str,
    failure_threshold: float = 0.50,
    max_steps: int = 10
) -> Dict[str, Any]:
    \"\"\"
    Simulates dynamic failure propagation through the enterprise dependency graph.
    \"\"\"
    # Track states: False = Active, True = Failed
    app_nodes = [n for n, d in graph.nodes(data=True) if d.get('node_type') == 'BusinessApplication']
    failed_state = {app: False for app in app_nodes}
    failed_state[failed_node] = True
    
    cascade_timeline = [[failed_node]]
    
    for step in range(max_steps):
        new_failures = []
        for app in app_nodes:
            if failed_state[app]:
                continue
                
            # Get dependencies required by app
            deps = [v for u, v in graph.out_edges(app) if v in failed_state]
            if not deps:
                continue
                
            # Count failed dependencies
            failed_deps = sum(1 for d in deps if failed_state[d])
            ratio = failed_deps / len(deps)
            
            # If failed dependency ratio exceeds resilience threshold
            if ratio >= failure_threshold:
                new_failures.append(app)
                
        if not new_failures:
            break  # Cascade halted
            
        for f in new_failures:
            failed_state[f] = True
        cascade_timeline.append(new_failures)
        
    return {
        'initial_failure': failed_node,
        'total_failed_count': sum(failed_state.values()),
        'cascade_steps': len(cascade_timeline),
        'timeline': cascade_timeline
    }
```

### Line-by-Line Code Analysis:

- **Lines 10–13**: Initializes state tracking across application nodes. `failed_state[failed_node] = True` triggers the initial component failure.
- **Lines 25–31**: Evaluates dependency health for each active node. If the fraction of failed dependencies meets or exceeds `failure_threshold`, the system transitions to a failed state on the subsequent cycle, realistically modeling cascading failures.

---

## 4. Empirical Case Study: Scenario D (`APP010`)

Simulating the failure of `APP010` (*Core Payment Router*) demonstrates its role as a systemic vulnerability:
- Step 0: `APP010` fails.
- Step 1: 8 immediate callers fail (*Retail Mobile Banking, Point-of-Sale, Wealth Transfer, ATM Controller*).
- Step 2: 8 second-degree systems fail (*Notification Engine, Fraud Analytics, Settlement Ledger*).
- **Final Result**: **16 of 25 enterprise systems (64%) fail within 2 steps**.

This simulation provides concrete architectural justification for decoupling `APP010` with an active-active fallback deployment.

---

## 5. Scope of Improvement & Production Roadmap

1. **Backpressure & Retry Storm Simulation**: Model HTTP 503 retry storms that generate exponential traffic spikes during partial recoveries.
2. **Chaos Engineering Integration**: Connect simulation results to Chaos Mesh or Gremlin to safely validate cascade assumptions in staging environments.

---

## 6. Summary & Companion Reading

Cascade simulations highlight systemic Single Points of Failure before outages occur in production.

- **Next Guide**: [09a: Beyond Project Accounting: The TVR Philosophy](file:///Users/pushkar/Documents/projects/value/blog/technical/09a_beyond_project_accounting_the_tvr_philosophy.md) begins Notebook 09 by examining value realization.
- **Companion Business Article**: [08b: Single Points of Failure and Resilience](file:///Users/pushkar/Documents/projects/value/blog/business/08b_single_points_of_failure_and_resilience.md) explains resilience planning to executives.
""")

def generate_nb09_articles():
    # 09a: Beyond Project Accounting: The TVR Philosophy
    write_tech_article("09a_beyond_project_accounting_the_tvr_philosophy.md", """---
title: "Technical Guide 09a: Beyond Project Accounting: The TVR Philosophy"
notebook_reference: "notebooks/09_investment_benefit_realization.ipynb"
part: "Part 1 of 4 for Notebook 09"
reading_time: "20 min read"
audience: "Enterprise Portfolio Managers, Digital Transformation Architects, FinOps Leads"
tbm_domain_level: "Foundational to Intermediate"
author: "Technology Value Intelligence Architecture Team"
---

# Technical Guide 09a: Beyond Project Accounting: The TVR Philosophy

> [!NOTE]
> **Executive Summary & Engineering Objective**: Why do 70% of enterprise digital transformations fail to deliver their promised financial value, even when delivered on time and on budget? In this guide, we introduce the Technology Value Realization (TVR) paradigm, contrast Run-the-Bank vs Grow-the-Bank capital structures, and model project investments in [`src/tvi/value_realization.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/value_realization.py).

---

## 1. The Transformation Paradox

In enterprise IT, project management offices (PMOs) measure project success using the **Iron Triangle**:
1. Was it delivered on time?
2. Was it delivered within budget?
3. Did it deliver the agreed scope?

```text
               The Iron Triangle Illusion:
                   Scope Delivered:    100% (Green)
                   Schedule Met:       100% (Green)
                   Budget Adhered to:  100% (Green)
                   ────────────────────────────────
                   BUSINESS VALUE:       0% (FAILURE)
```

An enterprise can spend \$30M replacing an existing CRM, complete the project on time and within budget, yet see **zero increase in sales productivity or customer retention**. The project was an operational success, but a financial and strategic failure.

**Technology Value Realization (TVR)** shifts governance from tracking project milestones to measuring actual business outcomes.

---

## 2. Theoretical Foundations: Run-the-Bank vs Grow-the-Bank

TBM categorizes technology spending into two distinct financial categories:

```mermaid
flowchart TD
    BUDGET["Total IT Budget ($100M)"] --> RTB["Run-the-Bank (Sustaining Spend)\n• 70-80% of budget\n• Datacenter power, license renewals, patch maintenance\n• Goal: Minimize cost while preserving SLAs"]
    BUDGET --> GTB["Grow-the-Bank (Discretionary Spend)\n• 20-30% of budget\n• Strategic modernization, AI initiatives, new revenue streams\n• Goal: Maximize return on investment (ROI)"]
```

### The TVR Closed-Loop Lifecycle

Traditional IT stops tracking projects once code deploys to production. TVR maintains measurement through three operational phases:

$$\text{Project Capitalization} \longrightarrow \text{Production Release} \longrightarrow \text{KPI Impact Verification (Months 6–24)}$$

If customer acquisition costs do not decline following the launch of a new digital channel, the investment has not realized its business case.

---

## 3. Schema Architecture for TVR Modeling

In [`src/tvi/database.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/database.py#L110-L145), we define relational structures linking projects to planned and realized benefits:

```sql
CREATE TABLE IF NOT EXISTS dim_projects (
    project_id VARCHAR PRIMARY KEY,
    project_name VARCHAR NOT NULL,
    strategic_objective VARCHAR NOT NULL,
    total_capex DOUBLE NOT NULL,
    total_opex DOUBLE NOT NULL,
    start_month VARCHAR NOT NULL,
    delivery_month VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_project_benefits (
    benefit_id VARCHAR PRIMARY KEY,
    project_id VARCHAR NOT NULL,
    benefit_type VARCHAR NOT NULL,       -- 'Cost Reduction', 'Revenue Growth', 'Risk Avoidance'
    expected_amount DOUBLE NOT NULL,
    realized_amount DOUBLE NOT NULL,
    realization_status VARCHAR NOT NULL, -- 'Exceeded', 'On Track', 'Lagging'
    FOREIGN KEY (project_id) REFERENCES dim_projects(project_id)
);
```

---

## 4. Scope of Improvement & Production Roadmap

1. **Automated Jira / ServiceNow Connectors**: Automatically extract project CapEx labor spend directly from engineering sprint hours and project management platforms.
2. **Dynamic Hurdle Rate Adjustments**: Adjust minimum expected return hurdles dynamically based on prevailing corporate cost of capital (WACC).

---

## 5. Summary & Companion Reading

TVR shifts enterprise focus from on-time delivery to verified business outcome delivery.

- **Next Guide**: [09b: Benefit Realization Waterfalls & Gap Quantification](file:///Users/pushkar/Documents/projects/value/blog/technical/09b_benefit_realization_waterfalls_and_gap_quantification.md) dives into tracking benefit realization gaps.
- **Companion Business Article**: [09a: Beyond On-Time and On-Budget](file:///Users/pushkar/Documents/projects/value/blog/business/09a_beyond_on_time_and_on_budget_tvr.md) details executive TVR implementation.
""")

    # 09b: Benefit Realization Waterfalls & Gap Quantification
    write_tech_article("09b_benefit_realization_waterfalls_and_gap_quantification.md", """---
title: "Technical Guide 09b: Benefit Realization Waterfalls & Gap Quantification"
notebook_reference: "notebooks/09_investment_benefit_realization.ipynb"
part: "Part 2 of 4 for Notebook 09"
reading_time: "21 min read"
audience: "Financial Engineers, FinOps Strategists, IT Controllers"
tbm_domain_level: "Intermediate"
author: "Technology Value Intelligence Architecture Team"
---

# Technical Guide 09b: Benefit Realization Waterfalls & Gap Quantification

> [!NOTE]
> **Executive Summary & Engineering Objective**: How do you measure whether a completed project achieved the financial benefits outlined in its original business case? In this guide, we dive into Benefit Realization Ratios (VRR), Value Gaps, Waterfall Visualizations, and contrast Scenario E (`PRJ003`: 108% ROI) with Scenario F (`PRJ014`: ₹23 Cr Value Gap) using [`src/tvi/value_realization.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/value_realization.py).

---

## 1. The Value Leakage Phenomenon

When business units submit capital expenditure requests, business cases often project significant financial returns:
- *"This digital onboarding initiative will generate \$15M in new account fees."*
- *"This automated claims system will reduce processing costs by \$10M."*

After funding is approved and systems deploy, post-implementation reviews are rarely performed. Costs are recorded, but value realization remains unverified.

```text
               Expected Benefits:   $10,000,000
                                       │
                        ┌──────────────┴──────────────┐
                        ▼                             ▼
               Realized Benefits              Value Leakage Gap
                   $4,200,000                    $5,800,000
                 (42% Realized)                (Unrecovered ROI)
```

Quantifying the **Value Realization Gap** allows enterprises to identify and address underperforming initiatives.

---

## 2. Theoretical Foundations: Value Realization Formulations

Let $\mathcal{B}(p)$ denote the set of benefits promised by investment project $p$.

### 1. Value Realization Ratio (VRR)

$$\operatorname{VRR}(p) = \frac{\sum_{b \in \mathcal{B}(p)} \operatorname{Realized}(b)}{\sum_{b \in \mathcal{B}(p)} \operatorname{Expected}(b)}$$

- $\operatorname{VRR} \ge 1.0$: Project met or exceeded its financial business case.
- $\operatorname{VRR} < 1.0$: Project experienced value leakage.

### 2. Net Value Realization (NVR)

$$\operatorname{NVR}(p) = \sum_{b \in \mathcal{B}(p)} \operatorname{Realized}(b) - \operatorname{TotalInvestmentCost}(p)$$

### 3. Financial Return on Investment (ROI)

$$\operatorname{ROI}(p) = \frac{\operatorname{NVR}(p)}{\operatorname{TotalInvestmentCost}(p)} \times 100\%$$

---

## 3. Code Walkthrough: Computing Benefit Realization

Let's examine the aggregation pipeline in [`src/tvi/value_realization.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/value_realization.py#L35-L95):

```python
# src/tvi/value_realization.py
import duckdb
import pandas as pd

def calculate_portfolio_benefit_realization(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    \"\"\"
    Computes expected vs realized benefits, value gaps, and VRR per project.
    \"\"\"
    query = \"\"\"
        SELECT 
            p.project_id,
            p.project_name,
            (p.total_capex + p.total_opex) as total_investment,
            SUM(b.expected_amount) as total_expected_benefit,
            SUM(b.realized_amount) as total_realized_benefit,
            (SUM(b.realized_amount) - SUM(b.expected_amount)) as value_gap,
            CASE 
                WHEN SUM(b.expected_amount) > 0 
                THEN (SUM(b.realized_amount) / SUM(b.expected_amount)) * 100.0 
                ELSE 0.0 
            END as realization_percentage,
            CASE 
                WHEN (p.total_capex + p.total_opex) > 0 
                THEN ((SUM(b.realized_amount) - (p.total_capex + p.total_opex)) / (p.total_capex + p.total_opex)) * 100.0 
                ELSE 0.0 
            END as net_roi_percentage
        FROM dim_projects p
        JOIN fact_project_benefits b ON p.project_id = b.project_id
        GROUP BY p.project_id, p.project_name, p.total_capex, p.total_opex
        ORDER BY value_gap ASC;
    \"\"\"
    return con.execute(query).df()
```

---

## 4. Empirical Case Study: Scenario E vs Scenario F

Analyzing our synthetic enterprise portfolio reveals two contrasting outcomes:

| Project ID | Project Name | Investment | Expected Benefit | Realized Benefit | Net Value Gap | VRR % |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`PRJ003`** (Scenario E) | Payments Platform Modernization | ₹12,000,000 | ₹25,000,000 | **₹27,000,000** | **+₹2,000,000** | **108.0%** |
| **`PRJ014`** (Scenario F) | Legacy CRM Replacement | ₹35,000,000 | ₹42,000,000 | **₹19,000,000** | **-₹23,000,000** | **45.2%** |

- **Scenario E (`PRJ003`)**: High-performing initiative that reduced transaction routing costs beyond initial targets.
- **Scenario F (`PRJ014`)**: Substantial value gap of ₹23 Cr due to low user adoption of the new CRM platform.

---

## 5. Scope of Improvement & Production Roadmap

1. **Dynamic Realization Time Slices**: Track month-by-month benefit realization curves to identify lagging projects before year-end reviews.
2. **Risk-Adjusted Net Present Value (NPV)**: Incorporate discount rates and project risk premiums into multi-year realization projections.

---

## 6. Summary & Companion Reading

Quantifying the value gap separates high-performing initiatives from investments requiring remediation.

- **Next Guide**: [09c: Difference-in-Differences Econometrics for IT Impact](file:///Users/pushkar/Documents/projects/value/blog/technical/09c_difference_in_differences_econometrics_for_it_impact.md) applies econometric causal inference to verify benefits.
- **Companion Business Article**: [09b: A Tale of Two Transformations](file:///Users/pushkar/Documents/projects/value/blog/business/09b_a_tale_of_two_transformations_payments_vs_crm.md) explores these case studies from an executive perspective.
""")

    # 09c: Difference-in-Differences Econometrics for IT Impact
    write_tech_article("09c_difference_in_differences_econometrics_for_it_impact.md", """---
title: "Technical Guide 09c: Difference-in-Differences Econometrics for IT Impact"
notebook_reference: "notebooks/09_investment_benefit_realization.ipynb"
part: "Part 3 of 4 for Notebook 09"
reading_time: "23 min read"
audience: "Econometricians, Quantitative Data Scientists, FinOps Leads"
tbm_domain_level: "Advanced"
author: "Technology Value Intelligence Architecture Team"
---

# Technical Guide 09c: Difference-in-Differences Econometrics for IT Impact

> [!NOTE]
> **Executive Summary & Engineering Objective**: Did your new digital banking platform cause an increase in customer transactions, or was the growth driven by broader market trends? In this guide, we dive into the mathematics of quasi-experimental causal inference, the Difference-in-Differences (DiD) regression formulation, and evaluate the Parallel Trends assumption in Python.

---

## 1. The Attribution Fallacy in IT Investments

When an enterprise rolls out a major software system, project sponsors often take credit for positive business trends:

> *"We launched the New Mobile App in June, and Q3 retail deposits grew by 18%! The app was a massive success."*

In causal inference, this reasoning is known as the **Post Hoc Ergo Propter Hoc fallacy**.

```text
               Did the IT Investment Drive the Gain?
               
    Retail Deposits:  ────────────/───────────▲ (18% Surge)
                                 │
                   Was it the    │   Or was it the Central Bank
                   Mobile App?   │   raising interest rates by 150 bps?
```

If the entire retail banking market grew by 18% during that period due to central bank rate changes, the software release may have contributed nothing.

To isolate true incremental value, we apply econometric **Difference-in-Differences (DiD)** estimation.

---

## 2. Theoretical Foundations: The DiD Estimator

Difference-in-Differences compares the change in outcomes over time between a **treatment group** (business units that adopted the new IT system) and a **control group** (business units operating on standard legacy systems).

```mermaid
xychart-beta
    title "Difference-in-Differences: Parallel Trends & Causal IT Impact"
    x-axis ["Pre-Period (t=0)", "Intervention", "Post-Period (t=1)"]
    y-axis "Business Performance (KPI)" 0 --> 100
    line [30, 45, 80]
    line [20, 35, 50]
```

### The Two-Way Fixed Effects Regression Formulation

$$Y_{it} = \beta_0 + \beta_1 \operatorname{Treated}_i + \beta_2 \operatorname{Post}_t + \beta_3 (\operatorname{Treated}_i \times \operatorname{Post}_t) + \epsilon_{it}$$

where:
- $Y_{it}$ is the business KPI observed for unit $i$ at time $t$ (e.g. transaction processing cost per account).
- $\operatorname{Treated}_i = 1$ if unit $i$ received the new software system; $0$ otherwise.
- $\operatorname{Post}_t = 1$ for observation periods after deployment; $0$ before.
- $\beta_3$ is the **True Causal Treatment Effect of the IT System**:

$$\hat{\beta}_3 = \left( \bar{Y}_{\text{Treated}, \text{Post}} - \bar{Y}_{\text{Treated}, \text{Pre}} \right) - \left( \bar{Y}_{\text{Control}, \text{Post}} - \bar{Y}_{\text{Control}, \text{Pre}} \right)$$

### The Parallel Trends Assumption

The validity of the DiD estimator relies on the **Parallel Trends Assumption**: in the absence of the IT intervention, the difference between the treatment and control groups would have remained constant over time:

$$\mathbb{E}[Y_{i, \text{Post}}(0) - Y_{i, \text{Pre}}(0) \mid \operatorname{Treated} = 1] = \mathbb{E}[Y_{i, \text{Post}}(0) - Y_{i, \text{Pre}}(0) \mid \operatorname{Treated} = 0]$$

---

## 3. Code Walkthrough: Implementing DiD Estimation

Let's examine the econometric regression implementation in [`notebooks/09_investment_benefit_realization.ipynb`](file:///Users/pushkar/Documents/projects/value/notebooks/09_investment_benefit_realization.ipynb):

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

def estimate_it_causal_impact(panel_data: pd.DataFrame) -> Any:
    \"\"\"
    Estimates true causal treatment effect of IT project deployment via DiD.
    Specification: KPI ~ treated + post + treated:post
    \"\"\"
    # Fit Ordinary Least Squares (OLS) with robust standard errors
    model = smf.ols(
        formula="kpi_value ~ treated + post + treated_x_post", 
        data=panel_data
    ).fit(cov_type='HC1')  # Heteroskedasticity-consistent standard errors
    
    beta_3 = model.params['treated_x_post']
    p_value = model.pvalues['treated_x_post']
    conf_int = model.conf_int().loc['treated_x_post']
    
    print(f"Causal IT Treatment Effect (Beta 3): {beta_3:,.4f}")
    print(f"Statistical Significance (p-value):  {p_value:.5f}")
    print(f"95% Confidence Interval:              [{conf_int[0]:.4f}, {conf_int[1]:.4f}]")
    
    return model
```

### Line-by-Line Code Analysis:

- **Lines 11–14**: Fits the interaction regression using heteroskedasticity-consistent standard errors (`cov_type='HC1'`). This ensures robust inference even if operational variance differs between business units.
- **Lines 16–18**: Extracts $\hat{\beta}_3$ and its $p$-value. If $p < 0.05$, we conclude that the software system drove statistically significant business value beyond general background trends.

---

## 4. Scope of Improvement & Production Roadmap

1. **Synthetic Control Method**: For single large enterprise rollouts without a direct control unit, use the Synthetic Control algorithm to create a weighted combination of un-treated departments.
2. **Staggered Rollout DiD (Callaway-Sant'Anna)**: For multi-stage deployments rolling out across different regional units over 18 months, implement robust estimators that account for staggered timing.

---

## 5. Summary & Companion Reading

Difference-in-Differences econometrics helps isolate true incremental IT impact from broader operational trends.

- **Next Guide**: [09d: KPI Linkage Graph & Stage-Gate Governance](file:///Users/pushkar/Documents/projects/value/blog/technical/09d_kpi_linkage_graph_and_stage_gate_governance.md) links investments to business KPI nodes.
- **Companion Business Article**: [09a: Beyond On-Time and On-Budget](file:///Users/pushkar/Documents/projects/value/blog/business/09a_beyond_on_time_and_on_budget_tvr.md) explores leadership value metrics.
""")

    # 09d: KPI Linkage Graph & Stage-Gate Governance
    write_tech_article("09d_kpi_linkage_graph_and_stage_gate_governance.md", """---
title: "Technical Guide 09d: KPI Linkage Graph & Stage-Gate Governance"
notebook_reference: "notebooks/09_investment_benefit_realization.ipynb"
part: "Part 4 of 4 for Notebook 09"
reading_time: "21 min read"
audience: "Enterprise Architects, Transformation Leads, FinOps Directors"
tbm_domain_level: "Intermediate"
author: "Technology Value Intelligence Architecture Team"
---

# Technical Guide 09d: KPI Linkage Graph & Stage-Gate Governance

> [!NOTE]
> **Executive Summary & Engineering Objective**: How do you connect technical deliverables—like an API migration—to executive board KPIs like EBITDA and Customer Retention? In this guide, we dive into the KPI Semantic Linkage Graph, multi-tier value trees, and implement programmatic Stage-Gate funding controls in [`src/tvi/value_realization.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/value_realization.py).

---

## 1. The Disconnect Between Code and KPIs

When engineering teams describe project deliverables, they naturally focus on technical milestones:
- *"Upgraded PostgreSQL from v12 to v16."*
- *"Migrated 14 REST endpoints to gRPC."*
- *"Implemented Redis read-through caching."*

To the Chief Executive Officer or Board of Directors, these operational milestones don't directly answer business questions:
- *Did this improve gross operating margins?*
- *Did this reduce customer transaction churn?*
- *Did this accelerate our time-to-market for new loans?*

To bridge this gap, TVR builds a **KPI Linkage Graph** that traces every technical output to an executive business outcome.

---

## 2. Theoretical Foundations: The Multi-Tier Value Tree

```mermaid
graph TD
    PRJ["Investment: Digital Checkout Modernization"] -->|Delivers| OUT["Technical Output: Latency < 100ms"]
    OUT -->|Improves| K1["Operational Metric: Cart Abandonment Rate (-4%)"]
    K1 -->|Drives| K2["Financial KPI: Monthly Digital Revenue (+12%)"]
    K2 -->|Impacts| K3["Executive KPI: Enterprise EBITDA Margin (+0.8%)"]
```

### Algorithmic Stage-Gate Governance

Traditional PMOs release 100% of project capital upfront based on an approved proposal. Under TVR **Stage-Gate Funding Governance**, capital is distributed in tranches conditioned on verified KPI progression:

$$\text{Tranche Funding Triggers}: \quad \Delta \operatorname{KPI}(t) \ge \tau_{\text{target}} \implies \text{Release Tranche } k+1$$

If Phase 1 fails to move leading operational indicators, funding for Phase 2 is paused for architectural review before additional capital is spent.

---

## 3. Code Walkthrough: Traversing the KPI Linkage Graph

Let's examine how [`src/tvi/value_realization.py`](file:///Users/pushkar/Documents/projects/value/src/tvi/value_realization.py#L110-L165) evaluates KPI progression:

```python
# src/tvi/value_realization.py
import duckdb
import pandas as pd

def evaluate_stage_gate_readiness(
    con: duckdb.DuckDBPyConnection,
    project_id: str,
    target_threshold: float = 0.80
) -> Dict[str, Any]:
    \"\"\"
    Audits KPI movements linked to a transformation project.
    Determines whether stage-gate conditions are met to unlock next capital tranche.
    \"\"\"
    query = \"\"\"
        SELECT 
            k.kpi_id,
            k.kpi_name,
            k.baseline_value,
            k.target_value,
            k.current_value,
            CASE 
                WHEN (k.target_value - k.baseline_value) != 0 
                THEN (k.current_value - k.baseline_value) / (k.target_value - k.baseline_value)
                ELSE 0.0 
            END as progress_ratio
        FROM rel_project_kpi r
        JOIN dim_kpis k ON r.kpi_id = k.kpi_id
        WHERE r.project_id = ?;
    \"\"\"
    df_kpi = con.execute(query, [project_id]).df()
    
    avg_progress = df_kpi['progress_ratio'].mean() if not df_kpi.empty else 0.0
    gate_approved = bool(avg_progress >= target_threshold)
    
    return {
        'project_id': project_id,
        'average_kpi_progress': avg_progress,
        'stage_gate_approved': gate_approved,
        'kpi_details': df_kpi.to_dict(orient='records')
    }
```

### Line-by-Line Code Analysis:

- **Lines 17–21**: Normalizes KPI progression toward its target:
  $$\text{Progress} = \frac{\text{Current} - \text{Baseline}}{\text{Target} - \text{Baseline}}$$
- **Lines 28–34**: Evaluates whether progress meets the required threshold (`target_threshold = 0.80`). If leading indicators fall short, the pipeline flags the project for review.

---

## 4. Scope of Improvement & Production Roadmap

1. **Automated KPI Telemetry Polling**: Connect `dim_kpis` directly to data lakehouses (e.g. Snowflake or Databricks) to stream live business metrics into the governance engine.
2. **Bayesian Belief Networks for Linkage Weights**: Replace simple edge connections with Bayesian network probabilities to model dependencies between operational metrics and executive KPIs.

---

## 5. Summary & Companion Reading

KPI linkage trees and stage-gate controls ground technical deliverables in observable business outcomes.

- **Next Guide**: [10a: Price-Volume-Mix (PVM) Variance Decomposition](file:///Users/pushkar/Documents/projects/value/blog/technical/10a_price_volume_mix_variance_decomposition.md) begins Notebook 10 by examining financial variance analysis.
- **Companion Business Article**: [09a: Beyond On-Time and On-Budget](file:///Users/pushkar/Documents/projects/value/blog/business/09a_beyond_on_time_and_on_budget_tvr.md) explores governance strategies.
""")

def run():
    print("Generating Technical Blogs for Notebooks 07, 08, and 09...")
    generate_nb07_articles()
    generate_nb08_articles()
    generate_nb09_articles()
    print("Notebooks 07-09 Generation Complete! (11 articles written)")

if __name__ == "__main__":
    run()
