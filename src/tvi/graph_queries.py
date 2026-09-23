"""Multi-Hop Knowledge Graph Traversal and Analytical Query Algorithms."""

from typing import Any, Dict, List, Optional, Set
import networkx as nx
import pandas as pd

from tvi.database import get_database


def find_business_units_by_vendor(G: nx.DiGraph, vendor_query: str) -> List[Dict[str, Any]]:
    """Traverse: Vendor -> Technology -> Application -> Capability -> Business Unit.

    Answers: "Which business units depend on applications that run on technology supplied by Vendor X?"
    """
    # Find vendor node
    vendor_node = None
    for n, data in G.nodes(data=True):
        if data.get("entity_type") == "Vendor":
            if n.lower() == vendor_query.lower() or data.get("label", "").lower() == vendor_query.lower():
                vendor_node = n
                break

    if not vendor_node:
        return []

    results = []
    # 1. Technologies supplied by Vendor (inbound edges to vendor with relationship SUPPLIED_BY)
    tech_nodes = [u for u, v, d in G.in_edges(vendor_node, data=True) if d.get("relationship") == "SUPPLIED_BY"]

    for tech in tech_nodes:
        tech_label = G.nodes[tech].get("label", tech)
        # 2. Applications running on Technology (inbound to tech with RUNS_ON)
        app_nodes = [u for u, v, d in G.in_edges(tech, data=True) if d.get("relationship") == "RUNS_ON"]
        for app in app_nodes:
            app_label = G.nodes[app].get("label", app)
            # 3. Capabilities supported by Application (outbound from app with SUPPORTS)
            cap_nodes = [v for u, v, d in G.out_edges(app, data=True) if d.get("relationship") == "SUPPORTS"]
            for cap in cap_nodes:
                cap_label = G.nodes[cap].get("label", cap)
                # 4. Business Units owning Capability (inbound to cap with OWNS)
                bu_nodes = [u for u, v, d in G.in_edges(cap, data=True) if d.get("relationship") == "OWNS"]
                for bu in bu_nodes:
                    bu_label = G.nodes[bu].get("label", bu)
                    results.append({
                        "vendor_id": vendor_node,
                        "vendor_name": G.nodes[vendor_node].get("label", vendor_node),
                        "technology_id": tech,
                        "technology_name": tech_label,
                        "application_id": app,
                        "application_name": app_label,
                        "capability_id": cap,
                        "capability_name": cap_label,
                        "business_unit_id": bu,
                        "business_unit_name": bu_label,
                    })

    return results


def find_capability_overlapping_apps(G: nx.DiGraph) -> pd.DataFrame:
    """Find capabilities supported by 2 or more distinct applications (Scenario C)."""
    cap_app_map: Dict[str, List[str]] = {}
    for u, v, d in G.edges(data=True):
        if d.get("relationship") == "SUPPORTS":
            cap_app_map.setdefault(v, []).append(u)

    overlap_records = []
    for cap_id, apps in cap_app_map.items():
        if len(apps) > 1:
            cap_data = G.nodes.get(cap_id, {})
            app_names = [G.nodes[a].get("label", a) for a in apps]
            overlap_records.append({
                "capability_id": cap_id,
                "capability_name": cap_data.get("label", cap_id),
                "criticality": cap_data.get("criticality", "Unknown"),
                "application_count": len(apps),
                "application_ids": ", ".join(apps),
                "application_names": ", ".join(app_names),
            })

    return pd.DataFrame(overlap_records).sort_values("application_count", ascending=False)


def find_costly_underutilized_overlapping_apps(
    G: nx.DiGraph,
    cost_threshold: float = 30000000.0,  # ₹3 Cr annual cost
    utilization_user_threshold: int = 500,
) -> pd.DataFrame:
    """Multi-hop: App -> Cost -> Consumption -> Capability -> Overlapping Apps.

    Answers: "Which applications have high annual cost, low utilization,
    and overlap with another application supporting the same capability?"
    """
    db = get_database()
    tco_df = db.query_df("SELECT application_id, annual_tco, lifecycle_status, criticality FROM v_app_annual_tco")
    cons_df = db.query_df("""
        SELECT application_id, AVG(total_active_users) as avg_users, AVG(total_transactions) as avg_txns
        FROM v_app_monthly_consumption
        GROUP BY application_id
    """)

    app_metrics = tco_df.merge(cons_df, on="application_id", how="left").fillna(0)

    # Get overlapping capabilities
    overlap_caps = find_capability_overlapping_apps(G)
    overlapping_apps_set: Set[str] = set()
    for apps_str in overlap_caps["application_ids"]:
        for a_id in apps_str.split(", "):
            overlapping_apps_set.add(a_id.strip())

    candidates = []
    for _, row in app_metrics.iterrows():
        a_id = row["application_id"]
        cost = row["annual_tco"]
        users = row["avg_users"]

        if cost >= cost_threshold and users <= utilization_user_threshold and a_id in overlapping_apps_set:
            app_label = G.nodes[a_id].get("label", a_id) if a_id in G else a_id
            # Find which capability overlaps
            supp_caps = [v for u, v, d in G.out_edges(a_id, data=True) if d.get("relationship") == "SUPPORTS"]
            cap_names = [G.nodes[c].get("label", c) for c in supp_caps if c in G]

            candidates.append({
                "application_id": a_id,
                "application_name": app_label,
                "annual_tco": cost,
                "avg_monthly_users": round(users),
                "avg_monthly_txns": round(row["avg_txns"]),
                "cost_per_user": round(cost / max(1, users), 2),
                "lifecycle_status": row["lifecycle_status"],
                "criticality": row["criticality"],
                "overlapping_capabilities": ", ".join(cap_names),
                "recommendation_flag": "Candidate for Rationalization Review",
            })

    return pd.DataFrame(candidates)


def get_full_value_chain_path(G: nx.DiGraph, app_id: str) -> Dict[str, Any]:
    """Extract complete upstream and downstream value chain path for an application.

    Chain:
    Vendor -> Technology -> Application -> Service -> Capability -> Business Unit
    """
    if app_id not in G:
        return {}

    app_node = G.nodes[app_id]

    # Technologies used (out edges from app)
    techs = [
        {"id": v, "name": G.nodes[v].get("label", v), "category": G.nodes[v].get("category", "")}
        for u, v, d in G.out_edges(app_id, data=True)
        if d.get("relationship") == "RUNS_ON"
    ]

    # Vendors providing those technologies
    vendors = []
    for t in techs:
        v_list = [
            {"id": v, "name": G.nodes[v].get("label", v)}
            for u, v, d in G.out_edges(t["id"], data=True)
            if d.get("relationship") == "SUPPLIED_BY"
        ]
        vendors.extend(v_list)

    # IT Services
    services = [
        {"id": v, "name": G.nodes[v].get("label", v), "category": G.nodes[v].get("category", "")}
        for u, v, d in G.out_edges(app_id, data=True)
        if d.get("relationship") == "SUPPORTS_SERVICE"
    ]

    # Capabilities supported
    capabilities = [
        {"id": v, "name": G.nodes[v].get("label", v), "priority": G.nodes[v].get("priority", "")}
        for u, v, d in G.out_edges(app_id, data=True)
        if d.get("relationship") == "SUPPORTS"
    ]

    # Owning Business Units
    bus = []
    for c in capabilities:
        bu_list = [
            {"id": u, "name": G.nodes[u].get("label", u)}
            for u, v, d in G.in_edges(c["id"], data=True)
            if d.get("relationship") == "OWNS"
        ]
        bus.extend(bu_list)

    # App-to-App Dependencies
    downstream_deps = [
        {"id": v, "name": G.nodes[v].get("label", v)}
        for u, v, d in G.out_edges(app_id, data=True)
        if d.get("relationship") == "DEPENDS_ON"
    ]
    upstream_deps = [
        {"id": u, "name": G.nodes[u].get("label", u)}
        for u, v, d in G.in_edges(app_id, data=True)
        if d.get("relationship") == "DEPENDS_ON"
    ]

    return {
        "application_id": app_id,
        "application_name": app_node.get("label", app_id),
        "lifecycle_status": app_node.get("lifecycle_status", ""),
        "criticality": app_node.get("criticality", ""),
        "technologies": techs,
        "vendors": vendors,
        "services": services,
        "capabilities": capabilities,
        "business_units": bus,
        "upstream_dependent_apps": upstream_deps,
        "downstream_dependencies": downstream_deps,
    }
