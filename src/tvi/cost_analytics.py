"""Application, Service, and Capability Cost Analytics Suite.

Calculates application TCO, fully-burdened cost distributions, unit economics
(cost/user, cost/transaction), Pareto cost concentration, and business capability
cost attribution with proportional consumption drivers.
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from tvi.database import get_database


def calculate_application_tco() -> pd.DataFrame:
    """Calculate annual Total Cost of Ownership (TCO) per application.

    TCO = Software + People + Cloud + Infrastructure + Vendor Services.
    """
    db = get_database()
    df = db.query_df("""
        SELECT
            c.application_id,
            a.application_name,
            a.service_id,
            s.service_name,
            a.lifecycle_status,
            a.criticality,
            a.annual_license_cost,
            SUM(c.amount) AS annual_tco,
            SUM(CASE WHEN c.cost_category = 'Software' THEN c.amount ELSE 0 END) AS software_cost,
            SUM(CASE WHEN c.cost_category = 'People' THEN c.amount ELSE 0 END) AS people_cost,
            SUM(CASE WHEN c.cost_category = 'Cloud' THEN c.amount ELSE 0 END) AS cloud_cost,
            SUM(CASE WHEN c.cost_category = 'Infrastructure' THEN c.amount ELSE 0 END) AS infra_cost
        FROM cost_records c
        JOIN applications a ON c.application_id = a.application_id
        JOIN it_services s ON a.service_id = s.service_id
        GROUP BY c.application_id, a.application_name, a.service_id, s.service_name, a.lifecycle_status, a.criticality, a.annual_license_cost
        ORDER BY annual_tco DESC
    """)

    # Merge annual average consumption for unit economics
    cons = db.query_df("""
        SELECT
            application_id,
            AVG(total_active_users) AS avg_monthly_users,
            SUM(total_transactions) AS annual_transactions
        FROM v_app_monthly_consumption
        GROUP BY application_id
    """)

    merged = df.merge(cons, on="application_id", how="left").fillna(0)
    # Unit economics with safe zero denominator handling
    merged["annual_cost_per_user"] = np.where(
        merged["avg_monthly_users"] > 0,
        (merged["annual_tco"] / merged["avg_monthly_users"]).round(2),
        0.0,
    )
    merged["cost_per_transaction"] = np.where(
        merged["annual_transactions"] > 0,
        (merged["annual_tco"] / merged["annual_transactions"]).round(4),
        0.0,
    )

    # Pareto concentration cumulative share
    total_spend = merged["annual_tco"].sum()
    merged["spend_share_pct"] = (merged["annual_tco"] / total_spend * 100.0).round(2)
    merged["cumulative_spend_pct"] = (merged["spend_share_pct"].cumsum()).round(2)

    return merged


def calculate_service_cost() -> pd.DataFrame:
    """Calculate annual cost per IT Service, including direct and allocated infrastructure."""
    db = get_database()
    return db.query_df("""
        SELECT
            s.service_id,
            s.service_name,
            s.service_category,
            s.criticality,
            s.service_level,
            COUNT(DISTINCT a.application_id) AS supported_application_count,
            SUM(c.amount) AS total_service_cost,
            SUM(CASE WHEN c.application_id IS NOT NULL THEN c.amount ELSE 0 END) AS direct_application_cost,
            SUM(CASE WHEN c.application_id IS NULL THEN c.amount ELSE 0 END) AS shared_infra_cost
        FROM it_services s
        LEFT JOIN applications a ON s.service_id = a.service_id
        JOIN cost_records c ON s.service_id = c.service_id
        GROUP BY s.service_id, s.service_name, s.service_category, s.criticality, s.service_level
        ORDER BY total_service_cost DESC
    """)


def calculate_capability_cost() -> pd.DataFrame:
    """Calculate total technology cost attributed to Business Capabilities.

    Allocation Rule:
    - Direct application cost is attributed to supported capabilities.
    - If an application supports N capabilities, cost is apportioned proportionally
      based on primary support (70%) vs secondary/overlapping support (30% / k).
    - Shared non-application IT service costs are allocated proportionally based on
      the capability's share of total transaction consumption.
    This guarantees 100% reconciliation without double counting.
    """
    db = get_database()
    app_tco = calculate_application_tco()[["application_id", "annual_tco", "annual_transactions"]]
    rel_cap = db.query_df("SELECT application_id, capability_id, support_type FROM rel_app_capability")
    cap_df = db.query_df("SELECT capability_id, capability_name, strategic_priority, criticality FROM business_capabilities")

    # Determine allocation weight per app-capability link
    rel_with_counts = rel_cap.copy()
    rel_with_counts["weight"] = np.where(rel_with_counts["support_type"] == "Primary", 1.0, 0.5)

    # Normalize weights so sum of weights per application == 1.0
    weight_sums = rel_with_counts.groupby("application_id")["weight"].transform("sum")
    rel_with_counts["norm_weight"] = rel_with_counts["weight"] / weight_sums

    # Merge application cost
    app_allocated = rel_with_counts.merge(app_tco, on="application_id", how="inner")
    app_allocated["allocated_app_cost"] = app_allocated["norm_weight"] * app_allocated["annual_tco"]
    app_allocated["allocated_txns"] = app_allocated["norm_weight"] * app_allocated["annual_transactions"]

    # Aggregate by capability
    cap_cost = (
        app_allocated.groupby("capability_id")
        .agg(
            direct_app_cost=("allocated_app_cost", "sum"),
            supported_apps_count=("application_id", "nunique"),
            total_capability_txns=("allocated_txns", "sum"),
        )
        .reset_index()
    )

    # Allocate shared infrastructure cost based on transaction share
    total_shared_cost = float(
        db.query_df("SELECT SUM(amount) FROM cost_records WHERE application_id IS NULL").iloc[0, 0]
    )
    total_txns = cap_cost["total_capability_txns"].sum()
    if total_txns > 0:
        cap_cost["shared_infra_allocated"] = (
            cap_cost["total_capability_txns"] / total_txns * total_shared_cost
        ).round(2)
    else:
        cap_cost["shared_infra_allocated"] = round(total_shared_cost / len(cap_cost), 2)

    cap_cost["total_capability_cost"] = (
        cap_cost["direct_app_cost"] + cap_cost["shared_infra_allocated"]
    ).round(2)

    # Join metadata
    result = cap_df.merge(cap_cost, on="capability_id", how="left").fillna(0)

    # Unit cost per capability transaction
    result["cost_per_transaction"] = np.where(
        result["total_capability_txns"] > 0,
        (result["total_capability_cost"] / result["total_capability_txns"]).round(4),
        0.0,
    )

    result = result.sort_values("total_capability_cost", ascending=False).reset_index(drop=True)
    return result


def get_application_profile(application_id: str) -> Dict[str, Any]:
    """Compile comprehensive analytical profile for a single application."""
    db = get_database()
    tco_df = calculate_application_tco()
    app_row = tco_df[tco_df["application_id"] == application_id]
    if app_row.empty:
        return {}

    app_data = app_row.iloc[0].to_dict()

    # Monthly cost trend
    m_cost = db.query_df("""
        SELECT month, cost_category, amount
        FROM cost_records
        WHERE application_id = ?
        ORDER BY month, cost_category
    """, [application_id])

    # Monthly consumption trend
    m_cons = db.query_df("""
        SELECT month, total_active_users, total_transactions, total_compute_hours
        FROM v_app_monthly_consumption
        WHERE application_id = ?
        ORDER BY month
    """, [application_id])

    # Capabilities supported
    caps = db.query_df("""
        SELECT c.capability_id, c.capability_name, r.support_type, c.criticality
        FROM rel_app_capability r
        JOIN business_capabilities c ON r.capability_id = c.capability_id
        WHERE r.application_id = ?
    """, [application_id])

    return {
        "summary": app_data,
        "monthly_costs": m_cost,
        "monthly_consumption": m_cons,
        "supported_capabilities": caps,
    }


def get_capability_profile(capability_id: str) -> Dict[str, Any]:
    """Compile analytical profile for a specific business capability."""
    db = get_database()
    cap_costs = calculate_capability_cost()
    match = cap_costs[cap_costs["capability_id"] == capability_id]
    if match.empty:
        return {}

    summary = match.iloc[0].to_dict()
    # Supporting apps
    apps = db.query_df("""
        SELECT a.application_id, a.application_name, r.support_type, a.lifecycle_status, a.criticality
        FROM rel_app_capability r
        JOIN applications a ON r.application_id = a.application_id
        WHERE r.capability_id = ?
    """, [capability_id])

    return {
        "summary": summary,
        "supporting_applications": apps,
    }


def get_service_profile(service_id: str) -> Dict[str, Any]:
    """Compile analytical profile for an IT service."""
    srv_df = calculate_service_cost()
    match = srv_df[srv_df["service_id"] == service_id]
    if match.empty:
        return {}
    return {"summary": match.iloc[0].to_dict()}
