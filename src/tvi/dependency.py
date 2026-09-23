"""Dependency and Blast Radius Impact Analysis Engine.

Performs transitive dependency traversal, distinguishing direct vs indirect dependencies,
identifying critical hubs, single points of failure (SPOF), and evaluating retirement/migration impact.
"""

from typing import Any, Dict, List, Optional, Set
import networkx as nx
import pandas as pd

from tvi.graph import build_knowledge_graph


def get_application_dependencies(
    application_id: str, G: Optional[nx.DiGraph] = None
) -> Dict[str, Any]:
    """Calculate comprehensive direct and indirect dependencies for an application.

    Distinguishes:
    - Direct vs Transitive dependent applications (blast radius)
    - Directly supported services and business capabilities
    - Impacted Business Units
    - Underlying technologies and vendors
    - Associated projects
    """
    if G is None:
        G = build_knowledge_graph()

    if application_id not in G:
        return {"error": f"Application '{application_id}' not found in Knowledge Graph."}

    app_data = G.nodes[application_id]

    # 1. Direct and Transitive Dependent Applications
    # Apps that depend ON this application (inbound edges with relationship DEPENDS_ON)
    direct_dependents = [
        u for u, v, d in G.in_edges(application_id, data=True) if d.get("relationship") == "DEPENDS_ON"
    ]

    # Reverse graph BFS for transitive dependent applications
    transitive_dependents: Set[str] = set()
    queue = list(direct_dependents)
    visited = set(direct_dependents)
    while queue:
        curr = queue.pop(0)
        transitive_dependents.add(curr)
        for u, v, d in G.in_edges(curr, data=True):
            if d.get("relationship") == "DEPENDS_ON" and u not in visited:
                visited.add(u)
                queue.append(u)

    indirect_dependents = list(transitive_dependents - set(direct_dependents))

    # 2. Downstream dependencies that THIS application relies upon
    direct_dependencies = [
        v for u, v, d in G.out_edges(application_id, data=True) if d.get("relationship") == "DEPENDS_ON"
    ]

    # 3. IT Services supported
    services = [
        {"id": v, "name": G.nodes[v].get("label", v), "criticality": G.nodes[v].get("criticality", "")}
        for u, v, d in G.out_edges(application_id, data=True)
        if d.get("relationship") == "SUPPORTS_SERVICE"
    ]

    # 4. Business Capabilities supported
    capabilities = [
        {
            "id": v,
            "name": G.nodes[v].get("label", v),
            "priority": G.nodes[v].get("priority", ""),
            "criticality": G.nodes[v].get("criticality", ""),
            "support_type": d.get("support_type", "Primary"),
        }
        for u, v, d in G.out_edges(application_id, data=True)
        if d.get("relationship") == "SUPPORTS"
    ]

    # 5. Business Units impacted (via supported capabilities)
    impacted_bus = []
    seen_bus = set()
    for cap in capabilities:
        c_id = cap["id"]
        for bu, _, d in G.in_edges(c_id, data=True):
            if d.get("relationship") == "OWNS" and bu not in seen_bus:
                seen_bus.add(bu)
                impacted_bus.append({
                    "id": bu,
                    "name": G.nodes[bu].get("label", bu),
                    "region": G.nodes[bu].get("region", ""),
                })

    # 6. Technologies and Vendors
    techs = [
        {"id": v, "name": G.nodes[v].get("label", v), "category": G.nodes[v].get("category", "")}
        for u, v, d in G.out_edges(application_id, data=True)
        if d.get("relationship") == "RUNS_ON"
    ]
    vendors = []
    seen_v = set()
    for t in techs:
        for _, ven, d in G.out_edges(t["id"], data=True):
            if d.get("relationship") == "SUPPLIED_BY" and ven not in seen_v:
                seen_v.add(ven)
                vendors.append({"id": ven, "name": G.nodes[ven].get("label", ven)})

    # 7. Associated Projects
    projects = [
        {"id": u, "name": G.nodes[u].get("label", u), "type": G.nodes[u].get("project_type", ""), "status": G.nodes[u].get("status", "")}
        for u, v, d in G.in_edges(application_id, data=True)
        if d.get("relationship") == "FUNDS_MODERNIZATION"
    ]

    blast_radius_score = (
        len(direct_dependents) * 3
        + len(indirect_dependents) * 1.5
        + len(capabilities) * 4
        + len(impacted_bus) * 2
    )

    return {
        "application_id": application_id,
        "application_name": app_data.get("label", application_id),
        "criticality": app_data.get("criticality", ""),
        "lifecycle_status": app_data.get("lifecycle_status", ""),
        "direct_dependent_apps": [
            {"id": a, "name": G.nodes[a].get("label", a)} for a in direct_dependents
        ],
        "indirect_dependent_apps": [
            {"id": a, "name": G.nodes[a].get("label", a)} for a in indirect_dependents
        ],
        "dependencies_relied_on": [
            {"id": a, "name": G.nodes[a].get("label", a)} for a in direct_dependencies
        ],
        "services": services,
        "capabilities": capabilities,
        "business_units": impacted_bus,
        "technologies": techs,
        "vendors": vendors,
        "associated_projects": projects,
        "blast_radius_metric": round(blast_radius_score, 1),
    }


def get_capability_dependencies(
    capability_id: str, G: Optional[nx.DiGraph] = None
) -> Dict[str, Any]:
    """Find all applications, services, business units, and projects linked to a capability."""
    if G is None:
        G = build_knowledge_graph()

    if capability_id not in G:
        return {"error": f"Capability '{capability_id}' not found."}

    cap_data = G.nodes[capability_id]

    # Owning BU
    owner_bus = [
        {"id": u, "name": G.nodes[u].get("label", u)}
        for u, v, d in G.in_edges(capability_id, data=True)
        if d.get("relationship") == "OWNS"
    ]

    # Supporting Apps
    apps = [
        {"id": u, "name": G.nodes[u].get("label", u), "support_type": d.get("support_type", "Primary")}
        for u, v, d in G.in_edges(capability_id, data=True)
        if d.get("relationship") == "SUPPORTS"
    ]

    # Projects targeting capability
    projects = [
        {"id": u, "name": G.nodes[u].get("label", u), "status": G.nodes[u].get("status", "")}
        for u, v, d in G.in_edges(capability_id, data=True)
        if d.get("relationship") == "TARGETS"
    ]

    return {
        "capability_id": capability_id,
        "capability_name": cap_data.get("label", capability_id),
        "criticality": cap_data.get("criticality", ""),
        "priority": cap_data.get("priority", ""),
        "owning_business_units": owner_bus,
        "supporting_applications": apps,
        "targeting_projects": projects,
    }


def get_business_unit_dependencies(
    business_unit_id: str, G: Optional[nx.DiGraph] = None
) -> Dict[str, Any]:
    """Find capabilities and underlying applications delivering value to a business unit."""
    if G is None:
        G = build_knowledge_graph()

    if business_unit_id not in G:
        return {"error": f"Business Unit '{business_unit_id}' not found."}

    bu_data = G.nodes[business_unit_id]

    # Owned capabilities
    caps = [
        {"id": v, "name": G.nodes[v].get("label", v), "criticality": G.nodes[v].get("criticality", "")}
        for u, v, d in G.out_edges(business_unit_id, data=True)
        if d.get("relationship") == "OWNS"
    ]

    # Applications supporting those capabilities
    apps = []
    seen_apps = set()
    for c in caps:
        for a_id, _, d in G.in_edges(c["id"], data=True):
            if d.get("relationship") == "SUPPORTS" and a_id not in seen_apps:
                seen_apps.add(a_id)
                apps.append({
                    "id": a_id,
                    "name": G.nodes[a_id].get("label", a_id),
                    "lifecycle": G.nodes[a_id].get("lifecycle_status", ""),
                })

    return {
        "business_unit_id": business_unit_id,
        "business_unit_name": bu_data.get("label", business_unit_id),
        "region": bu_data.get("region", ""),
        "owned_capabilities": caps,
        "supporting_applications": apps,
    }
