"""Application Rationalization and Multi-Criteria Portfolio Scoring Engine.

Implements transparent, rule-based indicators for application rationalization review
grounded in cost, utilization, capability redundancy, business criticality, and lifecycle status.
Adheres strictly to consulting guardrails: identifies 'Applications requiring rationalization review'
and labels financial impacts as 'analytical scenarios rather than guaranteed savings'.
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from tvi.cost_analytics import calculate_application_tco
from tvi.database import get_database
from tvi.graph_queries import find_capability_overlapping_apps


def score_application_portfolio() -> pd.DataFrame:
    """Calculate transparent multi-criteria rationalization scores for all applications.

    Scores (0.0 to 100.0):
    - cost_score: Higher indicates higher expenditure burden
    - utilization_score: Higher indicates robust user & transaction adoption (inverse of risk)
    - criticality_score: Higher indicates mission-critical dependency
    - capability_overlap_score: Higher indicates duplicate capability coverage in enterprise
    - lifecycle_review_score: Higher indicates obsolete or transitional lifecycle status (Migrate, Tolerate, Retire)
    """
    db = get_database()
    app_tco = calculate_application_tco()

    # Determine overlapping capabilities per application
    overlap_df = db.query_df("""
        WITH cap_app_counts AS (
            SELECT capability_id, COUNT(DISTINCT application_id) as app_cnt
            FROM rel_app_capability
            GROUP BY capability_id
        )
        SELECT
            r.application_id,
            COUNT(DISTINCT r.capability_id) as total_caps_supported,
            SUM(CASE WHEN c.app_cnt > 1 THEN 1 ELSE 0 END) as overlapping_caps_count
        FROM rel_app_capability r
        JOIN cap_app_counts c ON r.capability_id = c.capability_id
        GROUP BY r.application_id
    """)

    df = app_tco.merge(overlap_df, on="application_id", how="left").fillna(0)

    # 1. Cost Score (Percentile ranking 0-100)
    df["cost_score"] = (df["annual_tco"].rank(pct=True) * 100.0).round(1)

    # 2. Utilization Score (Percentile ranking of active users 0-100)
    df["utilization_score"] = (df["avg_monthly_users"].rank(pct=True) * 100.0).round(1)

    # 3. Criticality Score (Explicit business weight)
    crit_weights = {
        "Mission Critical": 100.0,
        "Business Critical": 75.0,
        "Operational": 40.0,
        "Standard": 20.0,
    }
    df["criticality_score"] = df["criticality"].map(crit_weights).fillna(50.0)

    # 4. Capability Overlap Score
    df["capability_overlap_score"] = np.where(
        df["overlapping_caps_count"] > 0,
        np.clip(df["overlapping_caps_count"] * 50.0, 50.0, 100.0),
        0.0,
    )

    # 5. Lifecycle Review Score (Retire / Migrate / Tolerate / Strategic)
    lifecycle_review_weights = {
        "Retire": 100.0,
        "Migrate": 80.0,
        "Tolerate": 65.0,
        "Strategic": 10.0,
    }
    df["lifecycle_score"] = df["lifecycle_status"].map(lifecycle_review_weights).fillna(30.0)

    # Composite Rationalization Review Index (RRI)
    # Higher score = Stronger case for human architectural and financial review
    df["rationalization_review_index"] = (
        0.30 * df["cost_score"]
        + 0.25 * (100.0 - df["utilization_score"])  # low utilization increases review priority
        + 0.20 * df["capability_overlap_score"]
        + 0.15 * df["lifecycle_score"]
        + 0.10 * (100.0 - df["criticality_score"])  # lower criticality increases feasibility
    ).round(1)

    return df


def find_rationalization_candidates(review_threshold: float = 60.0) -> pd.DataFrame:
    """Identify applications requiring rationalization review with transparent evidence.

    Guardrail:
    - Avoids black-box labels.
    - Estimated avoidable cost is clearly labeled as an 'analytical scenario rather than a guaranteed saving'.
    """
    df = score_application_portfolio()

    candidates = df[df["rationalization_review_index"] >= review_threshold].copy()
    candidates = candidates.sort_values("rationalization_review_index", ascending=False)

    # Generate transparent human-readable evidence
    evidence_list = []
    for _, row in candidates.iterrows():
        reasons = []
        if row["cost_score"] >= 65:
            reasons.append(f"High annual cost (₹{row['annual_tco']/1e7:.2f} Cr, top {100-row['cost_score']:.0f}% of portfolio)")
        if row["utilization_score"] <= 40:
            reasons.append(f"Low active user base ({row['avg_monthly_users']:.0f} users, cost/user ₹{row['annual_cost_per_user']/1e5:.2f}L)")
        if row["capability_overlap_score"] > 0:
            reasons.append(f"Capability overlap ({int(row['overlapping_caps_count'])} redundant capability mappings)")
        if row["lifecycle_status"] in ["Tolerate", "Migrate", "Retire"]:
            reasons.append(f"Lifecycle designated as '{row['lifecycle_status']}'")
        if row["criticality"] not in ["Mission Critical"]:
            reasons.append(f"Criticality level is '{row['criticality']}' (manageable operational risk)")

        evidence_list.append(" | ".join(reasons))

    candidates["investigation_evidence"] = evidence_list
    candidates["potential_avoidable_cost_scenario"] = candidates["annual_tco"]

    return candidates[
        [
            "application_id",
            "application_name",
            "lifecycle_status",
            "criticality",
            "annual_tco",
            "avg_monthly_users",
            "annual_cost_per_user",
            "overlapping_caps_count",
            "rationalization_review_index",
            "investigation_evidence",
            "potential_avoidable_cost_scenario",
        ]
    ]
