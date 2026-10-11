/**
 * Expedition Milestones Composable for Vedanam / TVI
 * Models the mountain ascent journey from Valley Basecamp (1,400m) to Apex Summit (8,848m).
 * At each milestone, two clickable notebooks provide:
 * 1. Business Field Guide: Executive ROI, strategic value, cost avoidance, TBM value realization, KPIs.
 * 2. Technical Field Manual: First-principles KaTeX math formulation, SLA, memory budgets, contracts, code snippets.
 */

export interface ExpeditionMilestone {
  number: number
  id: string
  name: string
  altitude: number
  elevationGain: string
  location: string
  subTitle: string
  phaseNumber: number
  terrainType: 'moraine' | 'ridge' | 'crevasse' | 'cirque' | 'col' | 'summit'
  business: {
    title: string
    executiveSummary: string
    businessImpact: string
    costImplications: string
    cfoTakeaway: string
    kpis: { label: string; value: string }[]
  }
  technical: {
    title: string
    formulaName: string
    formulaLatex: string
    formulaHtml?: string
    formulaExplanation: string
    moduleLineage: string
    inputContract: string
    outputContract: string
    latencySla: string
    memoryBudget: string
    codeSnippet: string
  }
}

export const useExpeditionMilestones = () => {
  const milestones: ExpeditionMilestone[] = [
    {
      number: 1,
      id: 'basecamp',
      name: 'Valley Basecamp',
      altitude: 1400,
      elevationGain: '+0m',
      location: 'Glacial Moraine Plateau',
      subTitle: 'Procedural Generation, Non-Gaussian Copulas & DuckDB Ingestion',
      phaseNumber: 1,
      terrainType: 'moraine',
      business: {
        title: 'Enterprise Foundation & Non-Gaussian Financial Reality',
        executiveSummary: 'Establishes a baseline enterprise model eliminating spreadsheet hallucinations. Replaces naive bell curves with authentic heavy-tailed telemetry and multi-tier ITFM mass balance.',
        businessImpact: 'Ensures CFO and CIO make strategic capital allocations against realistic risk profiles rather than normalized averages that conceal enterprise fragility.',
        costImplications: 'Identifies initial $2.1M hidden variance arising from unmodeled peak spikes and non-linear consumption patterns across cloud and on-prem nodes.',
        cfoTakeaway: 'Never budget technology operations based on Gaussian means. Heavy-tailed distributions reveal the actual tail-risk exposure of our digital footprint.',
        kpis: [
          { label: 'Baseline Enterprise Nodes', value: '102 Nodes' },
          { label: 'Data Reconciliation Drift', value: '0.00% Exact' },
          { label: 'Initial Hidden Variance', value: '$2.1M Isolated' },
          { label: 'Determinism Seed', value: 'Seed 42 (Reproducible)' }
        ]
      },
      technical: {
        title: 'Multivariate Copula Synthesis & Vectorized DuckDB Ingestion',
        formulaName: "Sklar's Theorem for Multivariate Copulas",
        formulaLatex: 'F(x_1, \\dots, x_d) = C(F_1(x_1), \\dots, F_d(x_d)) \\quad \\text{with} \\quad C_R(u) = \\Phi_R(\\Phi^{-1}(u_1), \\dots, \\Phi^{-1}(u_d))',
        formulaHtml: '<i>F</i>(<i>x</i><sub>1</sub>, …, <i>x</i><sub><i>d</i></sub>) = <i>C</i>(<i>F</i><sub>1</sub>(<i>x</i><sub>1</sub>), …, <i>F</i><sub><i>d</i></sub>(<i>x</i><sub><i>d</i></sub>)) &emsp;<span class="math-keyword">with</span>&emsp; <i>C</i><sub><i>R</i></sub>(<b>u</b>) = &Phi;<sub><i>R</i></sub>(&Phi;<sup>&minus;1</sup>(<i>u</i><sub>1</sub>), …, &Phi;<sup>&minus;1</sup>(<i>u</i><sub><i>d</i></sub>))',
        formulaExplanation: 'Separates marginal distributions (Beta proportions, Weibull MTBF, Log-Normal compute spikes) from joint dependency matrices via Cholesky decomposition L·L^T.',
        moduleLineage: 'src/tvi/data_generation.py & copulas.py',
        inputContract: 'config.yaml, ontology.yaml, random_seed = 42',
        outputContract: '11 Structured Parquet/CSV Entities (data/generated/)',
        latencySla: '< 1.4 seconds (102 nodes, 196 edges)',
        memoryBudget: '< 180 MB peak heap',
        codeSnippet: `import numpy as np
from scipy import stats
import duckdb

def generate_copula_telemetry(n_samples: int = 1000, seed: int = 42):
    """Generates non-Gaussian heavy-tailed compute consumption."""
    rng = np.random.default_rng(seed)
    # Correlation matrix between Users, vCPU, and Storage
    R = np.array([[1.0, 0.72, 0.55],
                  [0.72, 1.0, 0.68],
                  [0.55, 0.68, 1.0]])
    L = np.linalg.cholesky(R)
    Z = rng.standard_normal((3, n_samples))
    correlated_Z = L @ Z
    U = stats.norm.cdf(correlated_Z)
    
    # Transform margins: Log-Normal CPU, Beta active share, Weibull errors
    vcpu = stats.lognorm.ppf(U[0], s=0.85, scale=48.0)
    users = stats.beta.ppf(U[1], a=2.5, b=5.0) * 10000
    return vcpu, users`
      }
    },
    {
      number: 2,
      id: 'ridge',
      name: 'Ice Ridge Crossing',
      altitude: 2900,
      elevationGain: '+1,500m',
      location: 'Khumbu Ice Ridge & Arête',
      subTitle: 'Semantic Graph Topology & Brandes Centrality Blast Radius',
      phaseNumber: 2,
      terrainType: 'ridge',
      business: {
        title: 'Structural Architecture & Single Points of Failure',
        executiveSummary: 'Reveals the true hidden web of dependencies connecting shared databases, vendor platforms, and mission-critical business capabilities.',
        businessImpact: 'Unmasks critical single-point-of-failure vulnerabilities that would otherwise remain invisible in siloed departmental spreadsheets.',
        costImplications: 'Prevents catastrophic outage cascades estimated at $340,000/hr by isolating shared infrastructure blast radiuses prior to decommissioning.',
        cfoTakeaway: 'You cannot manage technology cost or risk in 2D rows and columns. Relationship topology is the only way to safeguard enterprise continuity.',
        kpis: [
          { label: 'Enterprise Graph Edges', value: '196 Typed Links' },
          { label: 'Max Directed Diameter', value: '6 Hops' },
          { label: 'Vulnerability Blast Index', value: '72% Isolated' },
          { label: 'Transitive Path Resolution', value: '< 8.5ms BFS' }
        ]
      },
      technical: {
        title: 'Typed MultiDiGraph Topology & Brandes Centrality',
        formulaName: 'Directed Brandes Betweenness Centrality',
        formulaLatex: 'C_B(v) = \\sum_{s \\neq v \\neq t \\in V} \\frac{\\sigma_{st}(v)}{\\sigma_{st}} \\quad \\text{subject to} \\quad \\text{edge\\_type} \\in \\mathcal{E}_{ontology}',
        formulaHtml: '<i>C</i><sub><i>B</i></sub>(<i>v</i>) = &sum; <sup>&sigma;<sub><i>st</i></sub>(<i>v</i>)</sup>&frasl;<sub>&sigma;<sub><i>st</i></sub></sub> &emsp;<span class="math-keyword">s.t.</span>&emsp; edge &isin; &Epsilon;<sub><i>ontology</i></sub>',
        formulaExplanation: 'Computes structural transit load through nodes, identifying architectural chokepoints and upstream dependencies across DAG hierarchies.',
        moduleLineage: 'src/tvi/graph.py & dependency.py',
        inputContract: 'DuckDB relational tables + ontology.yaml semantic specifications',
        outputContract: 'In-memory NetworkX MultiDiGraph & exported GraphML',
        latencySla: '< 8.5 ms BFS transitive traversal',
        memoryBudget: '< 250 MB RAM',
        codeSnippet: `import networkx as nx

def calculate_blast_radius(G: nx.MultiDiGraph, target_node: str) -> dict:
    """Computes downstream transitive blast radius of an infrastructure node."""
    if target_node not in G:
        raise ValueError(f"Node {target_node} not in graph")
        
    downstream_apps = set()
    downstream_capabilities = set()
    
    # Reverse directed BFS traversal for dependent consumers
    for predecessor in nx.bfs_tree(G.reverse(), source=target_node):
        node_type = G.nodes[predecessor].get("type")
        if node_type == "Application":
            downstream_apps.add(predecessor)
        elif node_type == "BusinessCapability":
            downstream_capabilities.add(predecessor)
            
    return {
        "impacted_applications": list(downstream_apps),
        "impacted_capabilities": list(downstream_capabilities),
        "severity_score": len(downstream_apps) / max(1, len(G.nodes))
    }`
      }
    },
    {
      number: 3,
      id: 'crevasse',
      name: 'The Crevasse Traverse',
      altitude: 4400,
      elevationGain: '+1,500m',
      location: 'Serac Crevasse Glacial Field',
      subTitle: '5-Layer Activity-Based Costing & Double-Counting Firewall',
      phaseNumber: 3,
      terrainType: 'crevasse',
      business: {
        title: 'Fully Loaded TCO & Proportional Capability Attribution',
        executiveSummary: 'Eliminates blunt cost allocations by routing every dollar from general ledger cost centers through shared infrastructure down to business capabilities.',
        businessImpact: 'Provides line-of-business leaders with incontrovertible total cost of ownership, driving accountable consumption rather than arbitrary corporate overhead tax.',
        costImplications: 'Reallocates $14.2M in misclassified shared overhead, restoring true product margins across Core Banking, Payments, and Wealth Advisory.',
        cfoTakeaway: 'When business units see their true fully loaded run-rate, discretionary compute demand drops organically by 15-20% without top-down mandates.',
        kpis: [
          { label: 'Fully Loaded TCO Allocated', value: '$48.6M Run-Rate' },
          { label: 'Double-Counting Error', value: '0.00% Firewall' },
          { label: 'Reallocated Shared Spend', value: '$14.2M Cleaned' },
          { label: 'Capability Mass Balance', value: '100% Reconciled' }
        ]
      },
      technical: {
        title: '5-Layer Activity-Based Cost Allocation & Mass Balance Firewall',
        formulaName: 'Mass-Balanced Proportional Cost Attribution',
        formulaLatex: 'C(c) = \\sum_{a \\in \\text{Apps}(c)} \\left[ C_{\\text{direct}}(a) + \\sum_{i \\in \\text{Infra}(a)} C(i) \\cdot w_{ia} + \\sum_{v \\in \\text{Vendors}(a)} C(v) \\cdot w_{va} \\right] \\cdot w_{ac}',
        formulaHtml: '<i>C</i>(<i>c</i>) = &sum; [<i>C</i><sub><i>dir</i></sub>(<i>a</i>) + &sum; <i>C</i>(<i>i</i>)&middot;<i>w</i><sub><i>ia</i></sub> + &sum; <i>C</i>(<i>v</i>)&middot;<i>w</i><sub><i>va</i></sub>] &middot; <i>w</i><sub><i>ac</i></sub>',
        formulaExplanation: 'Strictly enforces that the total attributed capability cost matches General Ledger expenses with machine-epsilon accuracy: sum(C_i) == sum(GL_j).',
        moduleLineage: 'src/tvi/cost_analytics.py & database.py',
        inputContract: 'DuckDB cost_items, applications, infra_allocations',
        outputContract: 'Materialized views: v_application_tco, v_capability_costs',
        latencySla: '< 12.0 ms full allocation run',
        memoryBudget: '< 90 MB DuckDB execution memory',
        codeSnippet: `import duckdb

def compute_tco_allocation(con: duckdb.DuckDBPyConnection):
    """Executes 5-layer activity-based costing with zero GL leakage."""
    query = """
    CREATE OR REPLACE VIEW v_application_tco AS
    WITH direct_costs AS (
        SELECT app_id, SUM(amount) as direct_spend
        FROM cost_items WHERE allocation_type = 'DIRECT'
        GROUP BY app_id
    ),
    shared_infra AS (
        SELECT a.app_id, SUM(ci.amount * alloc.weight) as shared_infra_spend
        FROM applications a
        JOIN infra_allocations alloc ON a.app_id = alloc.app_id
        JOIN cost_items ci ON alloc.infra_id = ci.infra_id
        GROUP BY a.app_id
    )
    SELECT 
        a.app_id, a.app_name,
        COALESCE(d.direct_spend, 0) + COALESCE(s.shared_infra_spend, 0) AS total_tco
    FROM applications a
    LEFT JOIN direct_costs d ON a.app_id = d.app_id
    LEFT JOIN shared_infra s ON a.app_id = s.app_id;
    """
    con.execute(query)`
      }
    },
    {
      number: 4,
      id: 'cirque',
      name: 'Glacial Cirque',
      altitude: 5900,
      elevationGain: '+1,500m',
      location: 'Western Cwm High Glacier Cirque',
      subTitle: 'Telemetry Consumption Quadrants & TOPSIS TIME Rationalization',
      phaseNumber: 4,
      terrainType: 'cirque',
      business: {
        title: 'Workhorses vs. Zombies & Portfolio Rationalization',
        executiveSummary: 'Cross-references financial expenditure against telemetry utilization to distinguish high-value workhorses from expensive zombie legacy platforms.',
        businessImpact: 'Drives objective TIME (Tolerate, Invest, Migrate, Eliminate) portfolio actions backed by quantifiable utilization and multi-criteria scoring.',
        costImplications: 'Identifies $3.8M in annual avoidable costs by sun-setting 4 identified zombie systems and decommissioning redundant OMS stacks.',
        cfoTakeaway: 'We do not guess which systems to eliminate. We follow the mathematical intersection of low telemetry and high run-rate.',
        kpis: [
          { label: 'Zombie Systems Identified', value: '4 Legacy Apps' },
          { label: 'Avoidable Cost Scenario', value: '$3.8M/yr Cash' },
          { label: 'Redundant Platform Clusters', value: '2 Overlaps' },
          { label: 'TIME Decision Confidence', value: '94.8% TOPSIS' }
        ]
      },
      technical: {
        title: '2x2 Telemetry Quadrants & TOPSIS Vector Normalization',
        formulaName: 'TOPSIS Multi-Criteria Relative Closeness',
        formulaLatex: 'R_i = \\frac{d_i^-}{d_i^+ + d_i^-} \\quad \\text{where} \\quad d_i^+ = \\sqrt{\\sum_j (v_{ij} - v_j^+)^2}, \\quad d_i^- = \\sqrt{\\sum_j (v_{ij} - v_j^-)^2}',
        formulaHtml: '<i>R</i><sub><i>i</i></sub> = <sup><i>d</i><sub><i>i</i></sub><sup>&minus;</sup></sup>&frasl;<sub>(<i>d</i><sub><i>i</i></sub><sup>+</sup> + <i>d</i><sub><i>i</i></sub><sup>&minus;</sup>)</sub> &emsp;<span class="math-keyword">where</span>&emsp; <i>d</i><sub><i>i</i></sub><sup>&plusmn;</sup> = &radic;&sum;(<i>v</i><sub><i>ij</i></sub> &minus; <i>v</i><sub><i>j</i></sub><sup>&plusmn;</sup>)<sup>2</sup>',
        formulaExplanation: 'Evaluates applications across 5 weighted dimensions (cost, business criticality, technical health, compliance risk, utilization) relative to ideal solutions.',
        moduleLineage: 'src/tvi/consumption_analytics.py & rationalization.py',
        inputContract: 'Telemetry metrics + application TCO + risk survey weights',
        outputContract: 'TIME quadrant assignments and Pareto rationalization ranking',
        latencySla: '< 4.5 ms MCDA calculation',
        memoryBudget: '< 35 MB RAM',
        codeSnippet: `import numpy as np

def topsis_rationalization(decision_matrix: np.ndarray, weights: np.ndarray, is_benefit: list[bool]):
    """Calculates TOPSIS score for multi-criteria rationalization."""
    # 1. Vector normalization
    norm = decision_matrix / np.sqrt((decision_matrix ** 2).sum(axis=0))
    # 2. Weighted normalization
    weighted = norm * weights
    # 3. Ideal solutions
    ideal_best = np.where(is_benefit, weighted.max(axis=0), weighted.min(axis=0))
    ideal_worst = np.where(is_benefit, weighted.min(axis=0), weighted.max(axis=0))
    # 4. Euclidean distance
    d_pos = np.sqrt(((weighted - ideal_best) ** 2).sum(axis=1))
    d_neg = np.sqrt(((weighted - ideal_worst) ** 2).sum(axis=1))
    # 5. Relative closeness
    closeness = d_neg / (d_pos + d_neg)
    return closeness`
      }
    },
    {
      number: 5,
      id: 'col',
      name: 'High Camp Col',
      altitude: 7300,
      elevationGain: '+1,400m',
      location: 'The South Col Windy Ridge',
      subTitle: 'Investment Value Realization & 3-Factor MoM Variance',
      phaseNumber: 5,
      terrainType: 'col',
      business: {
        title: 'Investment Value Realization & Price-Volume-Mix Variance',
        executiveSummary: 'Bridges the chasm between upfront business cases and actual operational realization, decomposing month-over-month expenditure movements into exact economic drivers.',
        businessImpact: 'Enforces post-delivery accountability for technology investments, tracking whether committed cost reductions and revenue expansions actually materialized.',
        costImplications: 'Isolates a $420K monthly cost surge into $310K pure volume expansion (business growth) vs. $110K vendor rate inflation.',
        cfoTakeaway: 'Knowing whether cloud cost increases come from user growth or vendor rate hikes is the difference between rewarding an engineering team or renegotiating a contract.',
        kpis: [
          { label: 'Realized Value Capture', value: '88.4% On-Track' },
          { label: 'Volume-Driven Variance', value: '+$310K Expansion' },
          { label: 'Vendor Rate Inflation', value: '+$110K Unit Rate' },
          { label: 'Net Counterfactual ROI', value: '3.4x Payback' }
        ]
      },
      technical: {
        title: 'Counterfactual KPI Tracking & 3-Factor Variance Decomposition',
        formulaName: '3-Factor Price-Volume-Mix Decomposition',
        formulaLatex: '\\Delta C = \\Delta P \\cdot V_0 + P_0 \\cdot \\Delta V + \\Delta P \\cdot \\Delta V',
        formulaHtml: '&Delta;<i>C</i> = (&Delta;<i>P</i> &middot; <i>V</i><sub>0</sub>) + (<i>P</i><sub>0</sub> &middot; &Delta;<i>V</i>) + (&Delta;<i>P</i> &middot; &Delta;<i>V</i>)',
        formulaExplanation: 'Decomposes cost shifts into pure price effect, pure volume effect, and cross-term interaction effect, ensuring exact additive closure without reconciliation gap.',
        moduleLineage: 'src/tvi/value_realization.py & variance.py',
        inputContract: 'MoM General Ledger records, resource unit rates, consumption metrics',
        outputContract: 'Decomposed variance waterfall & KPI trajectory delta tables',
        latencySla: '< 7.2 ms vector decomposition',
        memoryBudget: '< 45 MB RAM',
        codeSnippet: `import pandas as pd

def decompose_variance_3factor(p0: float, p1: float, v0: float, v1: float) -> dict:
    """Exact 3-factor Price-Volume-Mix additive decomposition."""
    delta_p = p1 - p0
    delta_v = v1 - v0
    
    price_effect = delta_p * v0
    volume_effect = p0 * delta_v
    mix_interaction = delta_p * delta_v
    total_variance = (p1 * v1) - (p0 * v0)
    
    assert abs(total_variance - (price_effect + volume_effect + mix_interaction)) < 1e-6
    return {
        "price_effect": price_effect,
        "volume_effect": volume_effect,
        "interaction_effect": mix_interaction,
        "total_variance": total_variance
    }`
      }
    },
    {
      number: 6,
      id: 'summit',
      name: 'The Apex Summit',
      altitude: 8848,
      elevationGain: '+1,548m',
      location: 'Crystal Pinnacle Summit Overlook',
      subTitle: 'Dual-Mode Knowledge Graph Analyst & Executive Synthesis',
      phaseNumber: 6,
      terrainType: 'summit',
      business: {
        title: 'Autonomous C-Suite Intelligence & Zero-Hallucination Decisions',
        executiveSummary: 'Delivers natural-language board-level intelligence grounded directly in the enterprise knowledge graph and verified financial ledger, completely eliminating LLM hallucinations.',
        businessImpact: 'Enables instant answers to complex C-level queries ("What is the blast radius if we terminate Vendor X?") within milliseconds rather than waiting 3 weeks for an analyst report.',
        costImplications: 'Accelerates portfolio restructuring cycles from quarters to hours, unlocking millions in deferred decision velocity.',
        cfoTakeaway: 'Board-level decision support with mathematical proof lineage. No guessing, no opaque cloud LLM leaks, pure deterministic analytical truth.',
        kpis: [
          { label: 'C-Suite Query Latency', value: '< 1.8ms (Rules)' },
          { label: 'Grounded Query Accuracy', value: '100% Deterministic' },
          { label: 'Hallucination Rate', value: '0.00% Zero-Leak' },
          { label: 'Offline SLM Memory Footprint', value: '5.2GB (Ollama)' }
        ]
      },
      technical: {
        title: 'Deterministic AST Parser & Grounded Local SLM Cypher Translation',
        formulaName: 'Grounded Natural Language Query Formulation',
        formulaLatex: 'Q^*(q) = \\arg\\max_{T \\in \\mathcal{T}_{valid}} P(T \\mid q, \\mathcal{G}_{ontology}) \\quad \\text{s.t.} \\quad \\text{Exec}(T) \\subseteq \\text{Sandbox}(\\mathcal{D})',
        formulaHtml: '<i>Q</i><sup>*</sup>(<i>q</i>) = argmax <i>P</i>(<i>T</i> | <i>q</i>, &Gscr;) &emsp;<span class="math-keyword">s.t.</span>&emsp; Exec(<i>T</i>) &sube; Sandbox(&Dscr;)',
        formulaExplanation: 'Translates natural language intents into parameterized graph traversals and DuckDB SQL with schema constraint guarantees and zero untrusted code execution.',
        moduleLineage: 'src/tvi/llm.py & graph_queries.py',
        inputContract: 'Natural language query string + graph schema AST',
        outputContract: 'Structured response JSON with graph path and analytical proof',
        latencySla: '< 1.8 ms (Deterministic Rules) / < 1.2s (Local Ollama)',
        memoryBudget: '< 50 MB (Rules) / 5.2 GB (Ollama SLM)',
        codeSnippet: `import re
from typing import Optional, Dict, Any

class GroundedGraphAnalyst:
    """Dual-mode grounded query processor ensuring zero LLM hallucination."""
    def __init__(self, duckdb_con, nx_graph):
        self.con = duckdb_con
        self.graph = nx_graph
        
    def query(self, nl_prompt: str) -> Dict[str, Any]:
        # Fast-path deterministic grammar matcher
        match_tco = re.search(r"tco of ([a-zA-Z0-9_-]+)", nl_prompt, re.I)
        if match_tco:
            app_id = match_tco.group(1).upper()
            result = self.con.execute(
                "SELECT total_tco FROM v_application_tco WHERE app_id = ?", [app_id]
            ).fetchone()
            return {"type": "TCO", "app_id": app_id, "amount": result[0] if result else 0}
            
        # Optional local SLM fallback with prompt grounding
        return {"mode": "deterministic_grounded", "status": "executed"}`
      }
    }
  ]

  const getMilestoneByNumber = (num: number) => {
    return milestones.find(m => m.number === num) || milestones[0]
  }

  const getMilestoneById = (id: string) => {
    return milestones.find(m => m.id === id) || milestones[0]
  }

  return {
    milestones,
    getMilestoneByNumber,
    getMilestoneById
  }
}
