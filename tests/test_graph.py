"""Tests for NetworkX Knowledge Graph and multi-hop traversal queries."""

import pytest
from tvi.config import load_config
from tvi.graph import build_knowledge_graph, get_focused_subgraph, validate_graph
from tvi.graph_queries import (
    find_business_units_by_vendor,
    find_capability_overlapping_apps,
    find_costly_underutilized_overlapping_apps,
    get_full_value_chain_path,
)


def test_knowledge_graph_validity():
    """Verify knowledge graph node types, relationships, and absence of unknown entities."""
    G = build_knowledge_graph()
    val = validate_graph(G)
    assert val["is_valid"] is True
    assert val["total_nodes"] > 100
    assert val["total_edges"] > 150
    assert "Unknown" not in val["node_distribution"]


def test_vendor_multi_hop_query():
    """Verify multi-hop query: Vendor -> Tech -> App -> Capability -> BU."""
    G = build_knowledge_graph()
    results = find_business_units_by_vendor(G, "TechNova")
    assert len(results) > 0
    first = results[0]
    assert "vendor_name" in first
    assert "technology_name" in first
    assert "application_name" in first
    assert "capability_name" in first
    assert "business_unit_name" in first


def test_capability_overlap_and_scenario_c():
    """Verify Scenario C: CAP003 (Order-to-Cash) has overlapping applications."""
    G = build_knowledge_graph()
    overlaps = find_capability_overlapping_apps(G)
    assert not overlaps.empty
    # Verify CAP003 is detected
    cap003 = overlaps[overlaps["capability_id"] == "CAP003"]
    assert not cap003.empty
    assert cap003.iloc[0]["application_count"] >= 2


def test_focused_subgraph_extraction():
    """Verify extracting a bounded focused subgraph around an application."""
    G = build_knowledge_graph()
    sub_g = get_focused_subgraph(G, "APP001", radius=1, max_nodes=20)
    assert sub_g.number_of_nodes() > 1
    assert sub_g.number_of_nodes() <= 20
    assert "APP001" in sub_g
