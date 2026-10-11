# GEMINI.md - Agent Guidelines & Repository Instructions

Welcome to the **Technology Value Intelligence (TVI)** codebase. This document defines the operational rules, architectural principles, development conventions, and mandatory quality standards for all AI agents and developers working in this repository.

---

## 🚨 CRITICAL RULE: Mandatory README Maintenance on Every Change

> [!IMPORTANT]
> **READMES MUST BE UPDATED EVERY TIME A CHANGE IS MADE IN THE PROJECT.**
> 
> There is a **zero-tolerance policy for documentation drift**. Any modification to code, architecture, schemas, notebooks, dependencies, pipelines, or configurations **must** be accompanied by an update to the corresponding `README.md` file(s) within the exact same pull request or commit.

### 1. Scope of Required Updates

| Type of Change | Required Documentation Action | Target README(s) |
| :--- | :--- | :--- |
| **Global Architecture / Tech Stack** | Update architecture diagrams, component layers, technology dependencies, or design decisions. | Root [`README.md`](file:///Users/pushkar/Documents/projects/value/README.md) |
| **Environment / Dependencies / Setup** | Update installation commands, Python version requirements, prerequisites, or package additions. | Root [`README.md`](file:///Users/pushkar/Documents/projects/value/README.md) |
| **Verification & Testing** | Update test suite instructions, validation check counts, or script execution commands. | Root [`README.md`](file:///Users/pushkar/Documents/projects/value/README.md) |
| **Configuration / Scenarios** | Update scenario matrix (Scenarios A–H), data generation counts, currency, or reporting settings. | Root [`README.md`](file:///Users/pushkar/Documents/projects/value/README.md) |
| **Notebook / Module Changes** | Update executive purpose, data inputs/outputs, key scenarios, file structure, or methodology. | Root [`README.md`](file:///Users/pushkar/Documents/projects/value/README.md) |
| **Roadmap & Improvement Progress** | Check off completed roadmap items `[x]` or append newly identified future roadmap tasks. | Root [`README.md`](file:///Users/pushkar/Documents/projects/value/README.md) |
| **New Notebooks or Subsystems** | Create a brand-new, comprehensive documentation section following the standard template and register it in the root table. | Root [`README.md`](file:///Users/pushkar/Documents/projects/value/README.md) |

### 2. Pre-Completion README Verification Checklist

Before finishing any task or marking work complete, you must explicitly verify:
- [ ] Did I alter any files in `src/tvi/`, `notebooks/`, `database/`, `data/`, `scripts/`, or `tests/`?
- [ ] Did I update the root [`README.md`](file:///Users/pushkar/Documents/projects/value/README.md) if project-wide commands, dependencies, or structures changed?
- [ ] Are all code snippets, file paths, and command instructions in the updated READMEs verified and accurate?

---

## 🏛️ Project Architecture & Overview

**Technology Value Intelligence (TVI)** is a portfolio-grade, local-first analytical engine and Knowledge Graph architecture built for a 16 GB RAM machine. It demonstrates how Knowledge Graphs transform Technology Business Management (TBM) and IT Financial Management (ITFM) into proactive, relationship-aware **Technology Value Realization (TVR)**.

### Strict Three-Layer Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                       AI & INTERFACE                        │
│   • Dual-Mode Knowledge Graph Analyst (src/tvi/llm.py)      │
│   • Deterministic Rules Mode (Default, Zero Hallucination)  │
│   • Optional Local Ollama LLM Mode                          │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      ANALYTICS LAYER                        │
│   • Application TCO & Unit Economics (cost_analytics.py)    │
│   • Proportional Capability Attribution (cost_analytics.py) │
│   • Multi-Criteria Rationalization MCDA (rationalization.py)│
│   • Transitive Blast Radius Engine (dependency.py)          │
│   • Benefit Realization & Gap Engine (value_realization.py) │
│   • Cost Driver Variance Decomposition (variance.py)        │
└──────────────┬───────────────────────────────┬──────────────┘
               │                               │
               ▼                               ▼
┌──────────────────────────────┐┌─────────────────────────────┐
│       ANALYTICAL TRUTH       ││  RELATIONSHIP INTELLIGENCE  │
│          (DuckDB)            ││         (NetworkX)          │
│  • High-performance OLAP     ││  • Typed property graph     │
│  • Materialized views        ││  • Multi-hop traversals     │
│  • Exact financial sums      ││  • Focused subgraphs        │
└──────────────────────────────┘└─────────────────────────────┘
```

1. **Analytical Truth (DuckDB):** In-process OLAP database for columnar aggregations, general ledger sums, and time-series variance analysis.
2. **Relationship Intelligence (NetworkX):** Typed semantic property graph for multi-hop graph traversals, blast-radius dependency tracing, and capability mapping.
3. **Dual-Mode AI & Interface:** Default deterministic rules engine (zero hallucination, offline) with an optional local Ollama LLM bridge.

---

## 📁 Repository Directory Structure

```text
.
├── GEMINI.md                   # This instruction and rules file
├── README.md                   # Main project executive overview and runbook
├── config.yaml                 # Master system and enterprise parameters
├── ontology.yaml               # Enterprise ontology and semantic graph relationships
├── pyproject.toml              # Build specifications and dependencies
├── requirements.txt            # Pinned Python package dependencies
├── src/tvi/                    # Core Python library
│   ├── __init__.py             # Package exports and versioning
│   ├── config.py               # YAML configuration loader
│   ├── consumption_analytics.py # Telemetry profiling & quadrant split
│   ├── cost_analytics.py       # TCO & capability allocation engine
│   ├── data_generation.py      # Deterministic synthetic enterprise generator
│   ├── database.py             # DuckDB schema management & queries
│   ├── dependency.py           # Blast radius & dependency graph traversal
│   ├── graph.py                # NetworkX graph construction & export
│   ├── graph_queries.py        # Domain-specific graph queries
│   ├── llm.py                  # Dual-mode analyst (rules + Ollama)
│   ├── rationalization.py      # Multi-criteria decision analysis (MCDA)
│   ├── reporting.py            # Executive report generator
│   ├── validation.py           # 4-tier automated integrity validator
│   ├── value_realization.py    # TVR investment benefit realization
│   └── variance.py             # MoM variance decomposition
├── notebooks/                  # 12-notebook progressive curriculum
│   ├── 01_generate_enterprise_data.ipynb
│   ├── 02_tbm_itfm_data_model.ipynb
│   ├── 03_build_knowledge_graph.ipynb
│   ├── 04_application_cost_intelligence.ipynb
│   ├── 05_capability_cost_intelligence.ipynb
│   ├── 06_consumption_intelligence.ipynb
│   ├── 07_application_rationalization.ipynb
│   ├── 08_dependency_and_impact_analysis.ipynb
│   ├── 09_investment_benefit_realization.ipynb
│   ├── 10_cost_driver_and_variance_analysis.ipynb
│   ├── 11_local_llm_knowledge_graph_analyst.ipynb
│   └── 12_end_to_end_technology_value_intelligence.ipynb
├── blog/                       # 24 executive business articles + 42 technical engineering guides (gitignored)
├── data/                       # Local data storage (raw, processed, generated)
├── database/                   # Local DuckDB database file
├── graph_output/               # Exported GraphML and visualization outputs
├── scripts/                    # Maintenance & automation scripts
└── tests/                      # Automated unit test suite
```

---

## 🛠️ Development & Coding Standards

### 1. Notebook Architecture & Production Code
- **Notebooks (`notebooks/0X_*.ipynb`):** The 12-notebook progressive curriculum incorporates complete analytical workflows and developments following the 8-part consulting research framework.
- **Production Code (`src/tvi/`):** All reusable logic, transformations, and mathematical models must live in modular, tested Python files within `src/tvi/`, not solely inside notebook cells.

### 2. Determinism and Reproducibility
- Always use `random_seed = 42` (configured in `config.yaml`) for synthetic data generation and sampling.
- No network calls or cloud dependencies are allowed in the core analytics pipeline. The system must remain 100% operational offline.

### 3. Verification & Testing Commands
Always run and ensure these pass before committing any changes:

```bash
# 1. Four-tier integrity validation (Data, Database, Graph, Analytics)
python -m tvi.validation

# 2. Pytest unit test suite
pytest tests/ -v

# 3. Batch notebook execution (when updating notebooks)
python scripts/execute_all_notebooks.py
```

### 4. Analytical Guardrails
1. **Avoidable Cost vs Guaranteed Savings:** When computing rationalization impact, state spend as an *avoidable cost scenario* rather than a guaranteed cash saving, acknowledging vendor contract lock-ins and shared infrastructure overhead.
2. **Association vs Causality:** Document project benefit realization as *associated with* KPI movements, preventing ungrounded claims of direct single-factor causation.
3. **Zero Code Execution Hallucination:** In NL-to-graph interfaces, use grounded intent detection and parameterized queries rather than executing arbitrary untrusted code.
