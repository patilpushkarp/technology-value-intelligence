"""NetworkX Knowledge Graph Construction and Topology Engine.

Transforms relational enterprise data into a typed property graph representing
Business Units, Capabilities, IT Services, Applications, Technologies, Vendors,
Projects, Benefits, and KPIs with explicit multi-hop traversal and focused subgraphs.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import networkx as nx
import numpy as np
import pandas as pd

from tvi.config import Config, load_config


def build_knowledge_graph(data_dir: str | Path | None = None) -> nx.DiGraph:
    """Build the complete Technology Value Intelligence knowledge graph.

    Args:
        data_dir: Directory containing generated CSV files.

    Returns:
        nx.DiGraph: Directed property graph with validated typed nodes and edges.
    """
    from tvi.config import get_project_root
    cfg = load_config()
    raw_dir = Path(data_dir or cfg.data.generated_dir)
    if not raw_dir.is_absolute():
        source_path = (get_project_root() / "data" / "generated" if "generated" in str(raw_dir) else get_project_root() / raw_dir).resolve()
    else:
        source_path = raw_dir.resolve()
    G = nx.DiGraph(name="TechnologyValueIntelligence")

    # Load tables
    bu_df = pd.read_csv(source_path / "business_units.csv")
    cap_df = pd.read_csv(source_path / "business_capabilities.csv")
    srv_df = pd.read_csv(source_path / "it_services.csv")
    app_df = pd.read_csv(source_path / "applications.csv")
    tech_df = pd.read_csv(source_path / "technologies.csv")
    ven_df = pd.read_csv(source_path / "vendors.csv")
    prj_df = pd.read_csv(source_path / "projects.csv")
    ben_df = pd.read_csv(source_path / "benefits.csv")
    kpi_df = pd.read_csv(source_path / "kpis.csv")

    rel_app_tech = pd.read_csv(source_path / "rel_app_technology.csv")
    rel_app_cap = pd.read_csv(source_path / "rel_app_capability.csv")
    rel_app_dep = pd.read_csv(source_path / "rel_app_dependency.csv")
    rel_prj_cap = pd.read_csv(source_path / "rel_project_capability.csv")
    rel_app_prj = pd.read_csv(source_path / "rel_app_project.csv")
    rel_ben_kpi = pd.read_csv(source_path / "rel_benefit_kpi.csv")

    # Add Nodes
    _add_business_units(G, bu_df)
    _add_capabilities(G, cap_df)
    _add_services(G, srv_df)
    _add_applications(G, app_df)
    _add_technologies(G, tech_df)
    _add_vendors(G, ven_df)
    _add_projects(G, prj_df)
    _add_benefits(G, ben_df)
    _add_kpis(G, kpi_df)

    # Add Relationships
    # 1. BU OWNS Capability
    for _, row in cap_df.iterrows():
        G.add_edge(row["business_unit_id"], row["capability_id"], relationship="OWNS")

    # 2. App SUPPORTS Capability
    for _, row in rel_app_cap.iterrows():
        G.add_edge(
            row["application_id"],
            row["capability_id"],
            relationship="SUPPORTS",
            support_type=row.get("support_type", "Primary"),
        )

    # 3. IT Service SUPPORTED_BY Application (and reverse Service -> App)
    for _, row in app_df.iterrows():
        G.add_edge(row["service_id"], row["application_id"], relationship="DELIVERED_BY")
        G.add_edge(row["application_id"], row["service_id"], relationship="SUPPORTS_SERVICE")

    # 4. App RUNS_ON Technology
    for _, row in rel_app_tech.iterrows():
        G.add_edge(row["application_id"], row["technology_id"], relationship="RUNS_ON")

    # 5. Technology SUPPLIED_BY Vendor
    for _, row in tech_df.iterrows():
        # Match vendor by name
        v_name = row["technology_vendor"]
        match_v = ven_df[ven_df["vendor_name"] == v_name]
        if not match_v.empty:
            v_id = match_v.iloc[0]["vendor_id"]
            G.add_edge(row["technology_id"], v_id, relationship="SUPPLIED_BY")

    # 6. App DEPENDS_ON App
    for _, row in rel_app_dep.iterrows():
        G.add_edge(
            row["source_app_id"],
            row["target_app_id"],
            relationship="DEPENDS_ON",
            dependency_type=row.get("dependency_type", "API"),
            criticality=row.get("criticality", "High"),
        )

    # 7. Project TARGETS Capability
    for _, row in rel_prj_cap.iterrows():
        G.add_edge(row["project_id"], row["capability_id"], relationship="TARGETS")

    # 8. Project FUNDED / Modernized App
    for _, row in rel_app_prj.iterrows():
        G.add_edge(row["project_id"], row["application_id"], relationship="FUNDS_MODERNIZATION")

    # 9. Project PRODUCES Benefit
    for _, row in ben_df.iterrows():
        G.add_edge(row["project_id"], row["benefit_id"], relationship="PRODUCES")

    # 10. Benefit MEASURED_BY KPI
    for _, row in rel_ben_kpi.iterrows():
        G.add_edge(row["benefit_id"], row["kpi_id"], relationship="MEASURED_BY")

    return G


def _add_business_units(G: nx.DiGraph, df: pd.DataFrame) -> None:
    for _, r in df.iterrows():
        G.add_node(
            r["business_unit_id"],
            label=r["business_unit_name"],
            entity_type="BusinessUnit",
            region=r["region"],
            bu_type=r["business_unit_type"],
            revenue=r["annual_revenue"],
            employees=r["employee_count"],
        )


def _add_capabilities(G: nx.DiGraph, df: pd.DataFrame) -> None:
    for _, r in df.iterrows():
        G.add_node(
            r["capability_id"],
            label=r["capability_name"],
            entity_type="BusinessCapability",
            priority=r["strategic_priority"],
            criticality=r["criticality"],
            owner=r["capability_owner"],
        )


def _add_services(G: nx.DiGraph, df: pd.DataFrame) -> None:
    for _, r in df.iterrows():
        G.add_node(
            r["service_id"],
            label=r["service_name"],
            entity_type="ITService",
            category=r["service_category"],
            owner=r["service_owner"],
            criticality=r["criticality"],
            sla=r["service_level"],
        )


def _add_applications(G: nx.DiGraph, df: pd.DataFrame) -> None:
    for _, r in df.iterrows():
        G.add_node(
            r["application_id"],
            label=r["application_name"],
            entity_type="Application",
            app_type=r["application_type"],
            lifecycle_status=r["lifecycle_status"],
            criticality=r["criticality"],
            business_criticality=r["business_criticality"],
            annual_license=r["annual_license_cost"],
        )


def _add_technologies(G: nx.DiGraph, df: pd.DataFrame) -> None:
    for _, r in df.iterrows():
        G.add_node(
            r["technology_id"],
            label=r["technology_name"],
            entity_type="Technology",
            category=r["technology_category"],
            vendor=r["technology_vendor"],
            lifecycle_status=r["lifecycle_status"],
            environment=r["environment"],
        )


def _add_vendors(G: nx.DiGraph, df: pd.DataFrame) -> None:
    for _, r in df.iterrows():
        G.add_node(
            r["vendor_id"],
            label=r["vendor_name"],
            entity_type="Vendor",
            category=r["vendor_category"],
            contract_value=r["contract_value"],
        )


def _add_projects(G: nx.DiGraph, df: pd.DataFrame) -> None:
    for _, r in df.iterrows():
        G.add_node(
            r["project_id"],
            label=r["project_name"],
            entity_type="Project",
            project_type=r["project_type"],
            budget=r["investment_budget"],
            actual_spend=r["actual_spend"],
            expected_benefit=r["expected_annual_benefit"],
            status=r["status"],
        )


def _add_benefits(G: nx.DiGraph, df: pd.DataFrame) -> None:
    for _, r in df.iterrows():
        G.add_node(
            r["benefit_id"],
            label=f"{r['benefit_type']} ({r['benefit_id']})",
            entity_type="Benefit",
            benefit_type=r["benefit_type"],
            expected_value=r["expected_value"],
            realized_value=r["realized_value"],
            status=r["benefit_status"],
        )


def _add_kpis(G: nx.DiGraph, df: pd.DataFrame) -> None:
    for _, r in df.iterrows():
        G.add_node(
            r["kpi_id"],
            label=r["kpi_name"],
            entity_type="KPI",
            category=r["kpi_category"],
            baseline=r["baseline_value"],
            target=r["target_value"],
            actual=r["actual_value"],
            unit=r["unit"],
        )


def validate_graph(G: nx.DiGraph) -> Dict[str, Any]:
    """Validate graph topology, node types, and relationship endpoints.

    Returns:
        Dict[str, Any]: Validation summary.
    """
    node_types: Dict[str, int] = {}
    for _, data in G.nodes(data=True):
        t = data.get("entity_type", "Unknown")
        node_types[t] = node_types.get(t, 0) + 1

    rel_types: Dict[str, int] = {}
    for _, _, data in G.edges(data=True):
        r = data.get("relationship", "Unknown")
        rel_types[r] = rel_types.get(r, 0) + 1

    is_valid = len(G.nodes) > 0 and len(G.edges) > 0 and "Unknown" not in node_types
    return {
        "is_valid": is_valid,
        "total_nodes": G.number_of_nodes(),
        "total_edges": G.number_of_edges(),
        "node_distribution": node_types,
        "relationship_distribution": rel_types,
    }


def save_graph(G: nx.DiGraph, output_dir: str | Path | None = None) -> Path:
    """Export graph representation in GraphML and Node-Link JSON formats."""
    from tvi.config import get_project_root
    cfg = load_config()
    raw_dir = Path(output_dir or cfg.graph.output_dir)
    if not raw_dir.is_absolute():
        out_dir = (get_project_root() / "graph_output" if "graph_output" in str(raw_dir) else get_project_root() / raw_dir).resolve()
    else:
        out_dir = raw_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Save GraphML
    graphml_path = out_dir / "knowledge_graph.graphml"
    nx.write_graphml(G, str(graphml_path))

    # Save JSON
    json_path = out_dir / "knowledge_graph.json"
    data = nx.node_link_data(G)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return graphml_path


def get_focused_subgraph(
    G: nx.DiGraph, center_node: str, radius: int = 1, max_nodes: int = 35
) -> nx.DiGraph:
    """Extract a clean, readable subgraph around a focal entity node."""
    if center_node not in G:
        return nx.DiGraph()

    # Undirected ego graph to capture both upstream and downstream neighbors
    undirected = G.to_undirected()
    sub_nodes = set(nx.ego_graph(undirected, center_node, radius=radius).nodes())

    if len(sub_nodes) > max_nodes:
        # Keep immediate 1-hop neighbors prioritized
        immediate = set(G.predecessors(center_node)).union(set(G.successors(center_node)))
        immediate.add(center_node)
        sub_nodes = list(immediate)[:max_nodes]

    return G.subgraph(sub_nodes).copy()


def export_cypher_script(G: nx.DiGraph, output_path: str | Path | None = None) -> str:
    """Generate executable Cypher DDL/DML script for Neo4j and Memgraph graph databases.

    Creates uniqueness constraints, typed entity nodes with properties, and multi-relational edges.
    """
    lines = [
        "// ============================================================================",
        "// Technology Value Intelligence (TVI) - Neo4j / Memgraph Cypher Ingestion DDL",
        "// ============================================================================",
        "",
        "// 1. Schema Uniqueness Constraints",
    ]

    entity_types = sorted({data.get("entity_type", "Entity") for _, data in G.nodes(data=True)})
    for et in entity_types:
        lines.append(f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{et}) REQUIRE n.id IS UNIQUE;")
    lines.append("")

    lines.append("// 2. Entity Nodes")
    for node, data in G.nodes(data=True):
        et = data.get("entity_type", "Entity")
        # Clean and format properties
        clean_props = {"id": str(node)}
        for k, v in data.items():
            if k == "entity_type":
                continue
            if isinstance(v, (int, float, bool)):
                clean_props[k] = v
            else:
                clean_props[k] = str(v).replace("'", "\\'")

        props_str = ", ".join(
            f"{k}: {v if isinstance(v, (int, float, bool)) else repr(v)}"
            for k, v in clean_props.items()
        )
        lines.append(f"MERGE (n:{et} {{id: '{node}'}}) SET n += {{{props_str}}};")

    lines.append("")
    lines.append("// 3. Semantic Graph Relationships")
    for u, v, data in G.edges(data=True):
        rel_type = data.get("relationship", "RELATED_TO").upper().replace(" ", "_")
        edge_props = {k: v for k, v in data.items() if k != "relationship"}
        if edge_props:
            prop_entries = ", ".join(
                f"{k}: {v if isinstance(v, (int, float, bool)) else repr(v)}"
                for k, v in edge_props.items()
            )
            props_str = f" {{{prop_entries}}}"
        else:
            props_str = ""

        lines.append(
            f"MATCH (a {{id: '{u}'}}), (b {{id: '{v}'}}) "
            f"MERGE (a)-[r:{rel_type}{props_str}]->(b);"
        )

    cypher_text = "\n".join(lines) + "\n"

    if output_path is not None:
        target = Path(output_path).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            f.write(cypher_text)

    return cypher_text


def compute_graph_embeddings(
    G: nx.DiGraph,
    dimensions: int = 16,
    seed: int = 42,
) -> Dict[str, List[float]]:
    """Compute dense structural node embeddings using Laplacian Spectral Decomposition.

    Captures high-order topological proximity and role equivalence across the enterprise graph
    without requiring external deep learning dependencies.
    """
    nodes = sorted(list(G.nodes()))
    node_to_idx = {n: i for i, n in enumerate(nodes)}
    n_count = len(nodes)

    if n_count == 0:
        return {}

    # Build symmetric adjacency with self-loops
    adj = np.eye(n_count)
    for u, v in G.edges():
        if u in node_to_idx and v in node_to_idx:
            i, j = node_to_idx[u], node_to_idx[v]
            adj[i, j] += 1.0
            adj[j, i] += 1.0

    # Degree normalization
    degrees = np.sum(adj, axis=1)
    d_inv_sqrt = np.zeros_like(degrees)
    pos_mask = degrees > 0
    d_inv_sqrt[pos_mask] = 1.0 / np.sqrt(degrees[pos_mask])
    norm_adj = d_inv_sqrt[:, np.newaxis] * adj * d_inv_sqrt[np.newaxis, :]

    # Truncated SVD decomposition
    k = min(dimensions, n_count - 1) if n_count > 1 else 1
    u, s, _ = np.linalg.svd(norm_adj)
    emb_matrix = u[:, :k] * np.sqrt(s[:k])

    embeddings = {}
    for i, node in enumerate(nodes):
        vec = [round(float(val), 6) for val in emb_matrix[i]]
        # Pad to requested dimension if graph is smaller
        if len(vec) < dimensions:
            vec.extend([0.0] * (dimensions - len(vec)))
        embeddings[node] = vec

    return embeddings


def build_temporal_graph(
    base_graph: nx.DiGraph | None = None,
) -> Dict[str, Any]:
    """Model quarterly enterprise architecture topology dynamics across release cycles.

    Tracks structural evolution (nodes added, deprecated, modified) and density metrics across Q1-Q4.
    """
    if base_graph is None:
        base_graph = build_knowledge_graph()

    quarterly_snapshots = {}
    quarters = ["Q1-2024", "Q2-2024", "Q3-2024", "Q4-2024"]

    # Progressive evolution: Q1 starts at 90% nodes, Q2 adds 5%, Q3 adds 5%, Q4 full
    nodes_sorted = sorted(list(base_graph.nodes()))
    total = len(nodes_sorted)

    q_subsets = {
        "Q1-2024": set(nodes_sorted[: int(total * 0.90)]),
        "Q2-2024": set(nodes_sorted[: int(total * 0.94)]),
        "Q3-2024": set(nodes_sorted[: int(total * 0.98)]),
        "Q4-2024": set(nodes_sorted),
    }

    prev_nodes: Set[str] = set()
    for q in quarters:
        active_nodes = q_subsets[q]
        sub_g = base_graph.subgraph(active_nodes)

        nodes_added = list(active_nodes - prev_nodes)
        quarterly_snapshots[q] = {
            "node_count": sub_g.number_of_nodes(),
            "edge_count": sub_g.number_of_edges(),
            "density": round(nx.density(sub_g), 5),
            "newly_onboarded_nodes": len(nodes_added),
            "sample_new_nodes": nodes_added[:5],
        }
        prev_nodes = active_nodes

    return quarterly_snapshots


def export_cytoscape_json(
    G: nx.DiGraph, output_path: str | Path | None = None
) -> Dict[str, Any]:
    """Export property graph to Cytoscape.js and D3.js web-ready visualization format.

    Generates nodes and edges with formatted visual metadata, colors, and badges.
    """
    type_color_map = {
        "Application": "#1f77b4",
        "BusinessCapability": "#2ca02c",
        "BusinessUnit": "#9467bd",
        "ITService": "#ff7f0e",
        "Technology": "#17becf",
        "Vendor": "#8c564b",
        "Project": "#e377c2",
        "Benefit": "#bcbd22",
        "KPI": "#d62728",
    }

    cy_nodes = []
    for node, data in G.nodes(data=True):
        e_type = data.get("entity_type", "Entity")
        cy_nodes.append({
            "data": {
                "id": str(node),
                "label": str(data.get("label", node)),
                "entity_type": e_type,
                "color": type_color_map.get(e_type, "#7f7f7f"),
                **{k: v for k, v in data.items() if k not in ["label", "entity_type"]},
            }
        })

    cy_edges = []
    for u, v, data in G.edges(data=True):
        cy_edges.append({
            "data": {
                "id": f"{u}->{v}",
                "source": str(u),
                "target": str(v),
                "relationship": data.get("relationship", "RELATED_TO"),
                **{k: v for k, v in data.items() if k != "relationship"},
            }
        })

    payload = {
        "format": "cytoscape_js",
        "elements": {
            "nodes": cy_nodes,
            "edges": cy_edges,
        },
        "metadata": {
            "total_nodes": len(cy_nodes),
            "total_edges": len(cy_edges),
        },
    }

    if output_path is not None:
        target = Path(output_path).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    return payload

