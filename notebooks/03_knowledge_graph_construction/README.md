# Knowledge Graph Construction & Topological Intelligence

**Purpose:** Constructs a typed, directed semantic property graph using NetworkX. Models enterprise relationships across Business Units, Capabilities, IT Services, Applications, Technologies, Vendors, Projects, and KPIs. Validates structural invariants and exports GraphML artifacts.  
**Series Index:** Notebook 03 of 12  
**Baseline Reference:** [`./v1_baseline.ipynb`](v1_baseline.ipynb) | **Active Development:** [`./v2_development.ipynb`](v2_development.ipynb)

---

## 1. Executive Business Purpose
Constructs a typed, directed semantic property graph using NetworkX. Models enterprise relationships across Business Units, Capabilities, IT Services, Applications, Technologies, Vendors, Projects, and KPIs. Validates structural invariants and exports GraphML artifacts.

### Core Methodology
Typed property graph modeling; multi-hop relationship extraction; NetworkX graph serialization; degree and centrality distribution profiling; ego-network extraction.

---

## 2. Key Scenarios & Focus Areas
- Capability duplication topological paths (Scenario C) and vendor dependency chains.

---

## 3. Data Dependencies & Artifacts

### Primary Inputs
- `DuckDB relational master data and relationship mappings`

### Primary Outputs
- `graph_output/knowledge_graph.graphml`
- `graph_output/knowledge_graph.json`
- `graph_output/enterprise_knowledge_graph.cypher` (Native Cypher DDL/DML script for Neo4j/Memgraph)
- `graph_output/topology_cytoscape.json` (Web-ready Cytoscape.js interactive topology graph)
- Dense structural node embeddings via Laplacian Spectral Decomposition (`compute_graph_embeddings()`)
- Quarterly enterprise topology evolution tracking (`build_temporal_graph()`)

---

## 4. File Structure & Versioning

```text
03_knowledge_graph_construction/
├── README.md               # Purpose, documentation, and improvement roadmap (this file)
├── v1_baseline.ipynb       # Untouched baseline reference notebook (self-contained)
└── v2_development.ipynb    # Working copy for iterative improvements and code extensions
```

- **`v1_baseline.ipynb`**: Preserves the verified baseline implementation with dynamic root discovery.
- **`v2_development.ipynb`**: Active development notebook expanded with native Cypher script generation, Laplacian spectral graph embeddings, quarterly release evolution tracking, and Cytoscape.js web exports.
- **Baseline Preservation:** `v1_baseline.ipynb` preserves the verified baseline implementation, while `v2_development.ipynb` is used for active evolution.

---

## 5. Iteration & Improvement Roadmap
- [x] Add automated Neo4j / Memgraph export scripts with native Cypher query generation (`export_cypher_script()`).
- [x] Compute Graph Neural Network (GNN) / spectral node embeddings for automated capability and risk clustering (`compute_graph_embeddings()`).
- [x] Model temporal graph dynamics (tracking topology changes across quarterly enterprise releases) (`build_temporal_graph()`).
- [x] Implement interactive Cytoscape / D3.js web graph visualization exports (`export_cytoscape_json()`).
- [ ] Implement Graph Convolutional Networks (GCN) for transductive application risk classification.
- [ ] Stream real-time CMDB change event notifications into live graph edge updates.
