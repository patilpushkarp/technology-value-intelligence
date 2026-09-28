"""Unit tests for Phase 1 (Modules 01-03) v2 Roadmap Capabilities."""

import json
from pathlib import Path
import networkx as nx
import numpy as np
import pandas as pd
import pytest

from tvi.config import load_config
from tvi.data_generation import EnterpriseDataGenerator
from tvi.database import TVIDatabase
from tvi.graph import (
    build_knowledge_graph,
    export_cypher_script,
    compute_graph_embeddings,
    build_temporal_graph,
    export_cytoscape_json,
)


# ==============================================================================
# Module 01: Enterprise Synthetic Data Generation v2 Tests
# ==============================================================================
def test_scenario_yaml_parameterization(tmp_path):
    """Verify that scenarios can be dynamically loaded from YAML configuration."""
    cfg = load_config()
    generator = EnterpriseDataGenerator(cfg)

    # Scenarios loaded from config/scenarios.yaml or defaults
    assert "scenario_a" in generator.scenarios
    assert generator.scenarios["scenario_a"]["app_id"] == "APP001"
    assert generator.scenarios["scenario_e"]["project_id"] == "PRJ003"
    assert generator.scenarios["scenario_g"]["app_id"] == "APP014"


def test_cloud_billing_records_generation():
    """Verify generation of AWS CUR / Azure Cost Management line-item records."""
    cfg = load_config()
    generator = EnterpriseDataGenerator(cfg)
    apps_df = generator.generate_applications(
        generator.generate_it_services(), generator.generate_vendors()
    )

    cur_df = generator.generate_cloud_billing_records(apps_df)

    assert not cur_df.empty
    expected_cols = {
        "line_item_id",
        "bill_invoice_id",
        "month",
        "cloud_provider",
        "line_item_product_code",
        "pricing_unit",
        "usage_amount",
        "line_item_unblended_cost",
        "line_item_currency_code",
        "resource_id",
        "application_id",
    }
    assert expected_cols.issubset(set(cur_df.columns))
    assert set(cur_df["cloud_provider"].unique()) == {"AWS", "Azure"}
    assert (cur_df["line_item_unblended_cost"] > 0).all()


def test_organizational_hierarchy_generation():
    """Verify 3-tier organizational hierarchy synthesis."""
    cfg = load_config()
    generator = EnterpriseDataGenerator(cfg)
    bu_df = generator.generate_business_units()

    hierarchy_df = generator.generate_organizational_hierarchy(bu_df)

    assert len(hierarchy_df) == len(bu_df) * 3
    assert "cost_center_id" in hierarchy_df.columns
    assert "division_name" in hierarchy_df.columns
    assert "budget_code" in hierarchy_df.columns
    assert set(hierarchy_df["business_unit_id"]).issubset(set(bu_df["business_unit_id"]))


def test_apply_data_drift():
    """Verify organic trend, seasonality, and jitter drift application."""
    cfg = load_config()
    generator = EnterpriseDataGenerator(cfg)
    data = generator.generate_all()

    cost_orig = data["cost_records"]
    cons_orig = data["consumption_records"]

    c_drift, u_drift = generator.apply_data_drift(
        cost_orig, cons_orig, monthly_trend=0.02, seasonality=True
    )

    assert len(c_drift) == len(cost_orig)
    assert len(u_drift) == len(cons_orig)
    # Drifted year-end costs should be higher than early months due to compound trend + Q4 seasonality
    q1_mean = c_drift[c_drift["month"] == "2024-01"]["amount"].mean()
    q4_mean = c_drift[c_drift["month"] == "2024-12"]["amount"].mean()
    assert q4_mean > q1_mean


# ==============================================================================
# Module 02: Analytical Warehouse & Data Model v2 Tests
# ==============================================================================
def test_parquet_export_and_arrow_query(tmp_path):
    """Verify Parquet file export and Apache Arrow zero-copy query execution."""
    db = TVIDatabase(":memory:")
    cfg = load_config()
    data_dir = cfg.data.generated_dir
    db.load_csv_data(data_dir)

    parquet_files = db.export_to_parquet(tmp_path / "parquet")
    assert len(parquet_files) > 0
    assert all(p.endswith(".parquet") for p in parquet_files)

    arrow_tbl = db.query_arrow("SELECT application_id, application_name FROM applications LIMIT 5")
    assert len(arrow_tbl) == 5
    assert "application_id" in arrow_tbl.column_names


def test_streaming_telemetry_batch_ingestion():
    """Verify incremental append ingestion and deduplication."""
    db = TVIDatabase(":memory:")
    cfg = load_config()
    db.load_csv_data(cfg.data.generated_dir)

    initial_count = len(db.query_df("SELECT * FROM consumption_records"))

    # Test duplicate batch - should insert 0 records
    dup_batch = db.query_df("SELECT * FROM consumption_records LIMIT 3")
    inserted_dup = db.ingest_telemetry_batch(dup_batch, deduplicate=True)
    assert inserted_dup == 0

    # Test fresh batch - should insert 1 record
    new_record = [{
        "consumption_id": "CON999999",
        "month": "2024-12",
        "application_id": "APP001",
        "business_unit_id": "BU001",
        "active_users": 1000,
        "transactions": 50000,
        "api_calls": 120000,
        "compute_hours": 300.0,
        "storage_gb": 800.0,
        "tickets": 5,
    }]
    inserted = db.ingest_telemetry_batch(new_record, deduplicate=True)
    assert inserted == 1
    assert len(db.query_df("SELECT * FROM consumption_records")) == initial_count + 1


def test_query_benchmarks_and_schema_migrations():
    """Verify performance benchmarking suite and schema migration tracking."""
    db = TVIDatabase(":memory:")
    cfg = load_config()
    db.load_csv_data(cfg.data.generated_dir)

    bench = db.benchmark_queries(iterations=3)
    assert "q1_annual_tco_aggregation" in bench
    assert bench["q1_annual_tco_aggregation"]["avg_ms"] > 0
    assert bench["q1_annual_tco_aggregation"]["result_rows"] > 0

    applied = db.apply_migrations()
    assert len(applied) >= 3
    # Second run should be idempotent
    re_applied = db.apply_migrations()
    assert len(re_applied) == 0


# ==============================================================================
# Module 03: Knowledge Graph v2 Tests
# ==============================================================================
def test_cypher_export(tmp_path):
    """Verify automated Cypher DDL/DML script generation."""
    G = build_knowledge_graph()
    cypher_path = tmp_path / "test_graph.cypher"
    cypher_text = export_cypher_script(G, cypher_path)

    assert cypher_path.exists()
    assert "CREATE CONSTRAINT IF NOT EXISTS" in cypher_text
    assert "MERGE (n:Application" in cypher_text
    assert ":SUPPORTS" in cypher_text or ":RUNS_ON" in cypher_text


def test_graph_node_embeddings():
    """Verify spectral node embedding extraction across graph topology."""
    G = build_knowledge_graph()
    embeddings = compute_graph_embeddings(G, dimensions=16)

    assert len(embeddings) == G.number_of_nodes()
    app1_vec = embeddings["APP001"]
    assert len(app1_vec) == 16
    assert isinstance(app1_vec[0], float)


def test_temporal_graph_dynamics_and_cytoscape_export(tmp_path):
    """Verify quarterly graph evolution modeling and Cytoscape.js export."""
    G = build_knowledge_graph()

    # Temporal dynamics
    quarterly = build_temporal_graph(G)
    assert "Q1-2024" in quarterly
    assert "Q4-2024" in quarterly
    assert quarterly["Q4-2024"]["node_count"] >= quarterly["Q1-2024"]["node_count"]

    # Cytoscape export
    cy_path = tmp_path / "cytoscape.json"
    payload = export_cytoscape_json(G, cy_path)

    assert cy_path.exists()
    assert payload["format"] == "cytoscape_js"
    assert len(payload["elements"]["nodes"]) == G.number_of_nodes()
    assert len(payload["elements"]["edges"]) == G.number_of_edges()
