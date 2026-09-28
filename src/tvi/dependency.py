"""Dependency and Blast Radius Impact Analysis Engine.

Performs transitive dependency traversal, distinguishing direct vs indirect dependencies,
identifying critical hubs, single points of failure (SPOF), and evaluating retirement/migration impact.
"""

from typing import Any, Dict, List, Optional, Set
import networkx as nx
import numpy as np
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


def simulate_failure_cascade(
    initial_failed_node: str,
    failure_probability: float = 0.8,
    iterations: int = 1000,
    random_seed: int = 42,
    G: Optional[nx.DiGraph] = None,
) -> Dict[str, Any]:
    """Simulate cascading failures across dependent applications using Monte Carlo simulation.

    Models systemic propagation through inbound DEPENDS_ON edges. If node B fails,
    any application A depending on B experiences conditional failure with failure_probability.
    """
    if G is None:
        G = build_knowledge_graph()

    if initial_failed_node not in G:
        return {"error": f"Node '{initial_failed_node}' not found in Knowledge Graph."}

    rng = np.random.default_rng(random_seed)
    cascade_sizes = []
    node_failure_counts: Dict[str, int] = {}

    for _ in range(iterations):
        failed_nodes = {initial_failed_node}
        queue = [initial_failed_node]

        while queue:
            curr = queue.pop(0)
            for u, v, d in G.in_edges(curr, data=True):
                if d.get("relationship") == "DEPENDS_ON" and u not in failed_nodes:
                    if rng.random() < failure_probability:
                        failed_nodes.add(u)
                        queue.append(u)
                        node_failure_counts[u] = node_failure_counts.get(u, 0) + 1

        cascade_sizes.append(len(failed_nodes))

    mean_size = float(np.mean(cascade_sizes))
    max_size = int(np.max(cascade_sizes))
    std_size = float(np.std(cascade_sizes))
    cascade_runs = sum(1 for s in cascade_sizes if s > 1)
    cascade_prob = cascade_runs / iterations

    vulnerability_rates = {
        node: round(cnt / iterations, 3)
        for node, cnt in sorted(node_failure_counts.items(), key=lambda x: x[1], reverse=True)
    }

    risk_tier = "High (Critical Cascade Hub)" if mean_size >= 4.0 or cascade_prob >= 0.7 else (
        "Moderate" if mean_size > 1.5 else "Low (Isolated Failure)"
    )

    return {
        "initial_failed_node": initial_failed_node,
        "initial_failed_label": G.nodes[initial_failed_node].get("label", initial_failed_node),
        "iterations": iterations,
        "base_failure_probability": failure_probability,
        "mean_affected_systems": round(mean_size, 2),
        "max_affected_systems": max_size,
        "std_affected_systems": round(std_size, 2),
        "cascade_occurrence_probability": round(cascade_prob, 3),
        "risk_tier": risk_tier,
        "vulnerable_callers_frequency": vulnerability_rates,
    }


def evaluate_deployment_gate(
    application_id: str,
    change_tier: str = "Major",
    max_blast_radius_threshold: Optional[float] = None,
    G: Optional[nx.DiGraph] = None,
) -> Dict[str, Any]:
    """Evaluate CI/CD automated release blast-radius gating thresholds.

    Evaluates proposed deployments against topological blast radius,
    dependent mission-critical applications, and business unit impact.
    """
    if G is None:
        G = build_knowledge_graph()

    deps = get_application_dependencies(application_id, G)
    if "error" in deps:
        return deps

    blast_radius = float(deps["blast_radius_metric"])
    direct_apps = deps["direct_dependent_apps"]
    indirect_apps = deps["indirect_dependent_apps"]
    caps = deps["capabilities"]
    bus = deps["business_units"]

    tier_defaults = {
        "Hotfix": 12.0,
        "Standard": 24.0,
        "Major": 36.0,
        "Emergency": 18.0,
    }
    threshold = max_blast_radius_threshold or tier_defaults.get(change_tier, 25.0)

    mission_crit_callers = [
        a["name"] for a in direct_apps
        if G.nodes[a["id"]].get("criticality") == "Mission Critical"
    ]
    mission_crit_caps = [
        c["name"] for c in caps
        if c.get("criticality") == "Mission Critical"
    ]

    if blast_radius > threshold * 1.5 or (len(direct_apps) >= 6 and change_tier == "Major"):
        gate_status = "BLOCKED_HIGH_BLAST_RADIUS"
        approval_level = "Enterprise Architecture Review Board & VP Escalation"
        recommendation = "Decompose release into phased micro-rollouts or implement canary deployment with rollback telemetry."
    elif blast_radius > threshold or len(mission_crit_callers) > 0 or len(mission_crit_caps) > 0:
        gate_status = "REQUIRES_CAB_APPROVAL"
        approval_level = "Change Advisory Board (CAB) & Domain SRE Sign-off"
        recommendation = "Provide automated regression test coverage report and 30-minute rollback runbook."
    else:
        gate_status = "AUTO_APPROVED"
        approval_level = "Automated CI/CD Pipeline Promotion"
        recommendation = "Deployment within blast radius risk tolerances; proceed through standard automated stage gates."

    return {
        "application_id": application_id,
        "application_name": deps["application_name"],
        "change_tier": change_tier,
        "gate_status": gate_status,
        "approval_level": approval_level,
        "blast_radius_metric": blast_radius,
        "threshold": threshold,
        "direct_dependent_apps_count": len(direct_apps),
        "indirect_dependent_apps_count": len(indirect_apps),
        "mission_critical_callers": mission_crit_callers,
        "mission_critical_capabilities": mission_crit_caps,
        "impacted_business_units_count": len(bus),
        "recommendation": recommendation,
    }


def audit_zero_trust_segmentation(G: Optional[nx.DiGraph] = None) -> pd.DataFrame:
    """Audit Zero-Trust network containment boundaries across enterprise topology.

    Categorizes nodes into network security trust tiers:
    - Tier-0: Core Vault & Data Store (Mission critical backends, relational databases)
    - Tier-1: Enterprise Service Mesh (Internal application services & APIs)
    - Tier-2: DMZ / Edge & Ingress (Public portals, web frontends, API gateways)
    - Tier-3: Third-Party / SaaS Vendor

    Flags cross-boundary containment bypasses (e.g. DMZ directly accessing Core Vault without Tier-1 mediation).
    """
    if G is None:
        G = build_knowledge_graph()

    def get_node_tier(node_id: str) -> str:
        data = G.nodes[node_id]
        entity_type = data.get("entity_type", "")
        cat = str(data.get("category", "")).lower()
        crit = str(data.get("criticality", "")).lower()
        app_type = str(data.get("application_type", "")).lower()

        if entity_type == "Technology":
            if any(k in cat for k in ["database", "storage", "data"]):
                return "Tier-0 (Core Vault)"
            return "Tier-1 (Internal Mesh)"
        elif entity_type == "Application":
            if "mission critical" in crit or "core" in app_type or node_id in ["APP001", "APP010"]:
                return "Tier-0 (Core Vault)"
            elif any(k in app_type for k in ["web", "portal", "gateway", "external"]) or "legacy customer" in str(data.get("label", "")).lower():
                return "Tier-2 (DMZ Edge)"
            else:
                return "Tier-1 (Internal Mesh)"
        elif entity_type == "Vendor":
            return "Tier-3 (Third-Party SaaS)"
        return "Tier-1 (Internal Mesh)"

    findings = []
    for u, v, d in G.edges(data=True):
        rel = d.get("relationship", "")
        if rel not in ["DEPENDS_ON", "RUNS_ON", "SUPPLIED_BY"]:
            continue

        u_tier = get_node_tier(u)
        v_tier = get_node_tier(v)

        u_label = G.nodes[u].get("label", u)
        v_label = G.nodes[v].get("label", v)

        # Violation rule 1: Tier-2 (DMZ) directly touching Tier-0 (Core Vault) without Tier-1 intermediary
        if "Tier-2" in u_tier and "Tier-0" in v_tier:
            findings.append({
                "source_node": u,
                "source_name": u_label,
                "source_zone": u_tier,
                "target_node": v,
                "target_name": v_label,
                "target_zone": v_tier,
                "relationship": rel,
                "is_containment_violation": True,
                "risk_rating": "High Risk",
                "security_policy": "Zero-Trust Rule 4.1: Direct Ingress-to-Vault traversal prohibited.",
                "remediation": "Route ingress traffic through Tier-1 API mediation gateway with mTLS authentication.",
            })
        # Violation rule 2: Tier-3 (Third Party) directly accessing Tier-0
        elif "Tier-3" in u_tier and "Tier-0" in v_tier:
            findings.append({
                "source_node": u,
                "source_name": u_label,
                "source_zone": u_tier,
                "target_node": v,
                "target_name": v_label,
                "target_zone": v_tier,
                "relationship": rel,
                "is_containment_violation": True,
                "risk_rating": "Critical Risk",
                "security_policy": "Zero-Trust Rule 2.3: Third-party vendor unmediated database access prohibited.",
                "remediation": "Isolate vendor integration into dedicated DMZ proxy with IP whitelisting and payload sanitization.",
            })
        else:
            findings.append({
                "source_node": u,
                "source_name": u_label,
                "source_zone": u_tier,
                "target_node": v,
                "target_name": v_label,
                "target_zone": v_tier,
                "relationship": rel,
                "is_containment_violation": False,
                "risk_rating": "Compliant",
                "security_policy": "Compliant boundary traversal.",
                "remediation": "No action required.",
            })

    df = pd.DataFrame(findings)
    # Sort violations first
    return df.sort_values(["is_containment_violation", "risk_rating"], ascending=[False, True])


def generate_dependency_flowchart_mermaid(
    application_id: str,
    max_depth: int = 2,
    G: Optional[nx.DiGraph] = None,
) -> str:
    """Generate GitHub/Markdown compatible Mermaid flowchart for change approvals."""
    if G is None:
        G = build_knowledge_graph()

    if application_id not in G:
        return f"%% Error: Node '{application_id}' not found in Knowledge Graph"

    app_label = G.nodes[application_id].get("label", application_id).replace('"', "'")

    mermaid_lines = [
        "flowchart TD",
        f'    subgraph Target["Target Application Under Review"]',
        f'        {application_id}["{app_label} ({application_id})"]:::targetNode',
        "    end",
    ]

    upstream_callers = set()
    for u, v, d in G.in_edges(application_id, data=True):
        if d.get("relationship") == "DEPENDS_ON":
            upstream_callers.add(u)

    downstream_deps = set()
    for u, v, d in G.out_edges(application_id, data=True):
        if d.get("relationship") in ["DEPENDS_ON", "RUNS_ON", "SUPPORTS"]:
            downstream_deps.add((v, d.get("relationship", "")))

    if upstream_callers:
        mermaid_lines.append('    subgraph Callers["Direct Inbound Callers (Blast Radius)"]')
        for u in sorted(upstream_callers):
            u_label = G.nodes[u].get("label", u).replace('"', "'")
            mermaid_lines.append(f'        {u}["{u_label} ({u})"]:::callerNode')
        mermaid_lines.append("    end")
        for u in sorted(upstream_callers):
            mermaid_lines.append(f"    {u} -->|DEPENDS_ON| {application_id}")

    if downstream_deps:
        mermaid_lines.append('    subgraph Downstream["Outbound Dependencies & Tech Stack"]')
        for v, rel in sorted(downstream_deps):
            v_label = G.nodes[v].get("label", v).replace('"', "'")
            v_type = G.nodes[v].get("entity_type", "Entity")
            mermaid_lines.append(f'        {v}["{v_label} [{v_type} - {v}]"]:::depNode')
        mermaid_lines.append("    end")
        for v, rel in sorted(downstream_deps):
            mermaid_lines.append(f"    {application_id} -->|{rel}| {v}")

    mermaid_lines.append("    classDef targetNode fill:#ef4444,stroke:#991b1b,stroke-width:2px,color:#fff;")
    mermaid_lines.append("    classDef callerNode fill:#f97316,stroke:#c2410c,stroke-width:1.5px,color:#fff;")
    mermaid_lines.append("    classDef depNode fill:#3b82f6,stroke:#1d4ed8,stroke-width:1.5px,color:#fff;")

    return "\n".join(mermaid_lines)

