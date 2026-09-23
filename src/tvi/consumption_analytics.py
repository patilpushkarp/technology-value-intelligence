"""Consumption and Unit Economics Intelligence Engine.

Profiles multidimensional technology consumption (users, transactions, API calls,
compute hours, storage, tickets) and evaluates cost-utilization quadrants.
"""

from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd

from tvi.cost_analytics import calculate_application_tco
from tvi.database import get_database


def analyze_consumption_quadrants() -> pd.DataFrame:
    """Classify applications into consumption vs cost quadrants using median splits.

    Quadrants:
    - High-Cost / High-Utilization: Scale Anchor Systems
    - High-Cost / Low-Utilization: Candidates for Right-Sizing / Rationalization Investigation
    - Low-Cost / High-Utilization: Highly Efficient Workhorses
    - Low-Cost / Low-Utilization: Utility / Niche Tools
    """
    df = calculate_application_tco()

    median_cost = df["annual_tco"].median()
    median_users = df["avg_monthly_users"].median()

    def assign_quadrant(row):
        high_cost = row["annual_tco"] >= median_cost
        high_util = row["avg_monthly_users"] >= median_users

        if high_cost and high_util:
            return "High Cost / High Utilization (Scale Anchor)"
        elif high_cost and not high_util:
            return "High Cost / Low Utilization (Investigate for Rationalization)"
        elif not high_cost and high_util:
            return "Low Cost / High Utilization (High Efficiency Workhorse)"
        else:
            return "Low Cost / Low Utilization (Niche Utility)"

    df["consumption_quadrant"] = df.apply(assign_quadrant, axis=1)
    df["cost_median_delta"] = (df["annual_tco"] - median_cost).round(2)
    df["utilization_median_delta"] = (df["avg_monthly_users"] - median_users).round(0)

    return df


def find_high_cost_low_utilization(
    cost_percentile: float = 0.60,
    utilization_percentile: float = 0.40,
) -> pd.DataFrame:
    """Identify applications with high cost and low utilization based on percentile thresholds."""
    df = calculate_application_tco()

    cost_threshold = df["annual_tco"].quantile(cost_percentile)
    user_threshold = df["avg_monthly_users"].quantile(utilization_percentile)

    candidates = df[
        (df["annual_tco"] >= cost_threshold) & (df["avg_monthly_users"] <= user_threshold)
    ].copy()

    candidates["investigation_flag"] = "High-Cost / Low-Consumption"
    candidates["potential_avoidable_cost_scenario"] = candidates["annual_tco"]

    return candidates.sort_values("annual_tco", ascending=False)


def analyze_unit_economics_trends() -> pd.DataFrame:
    """Analyze monthly unit cost trajectory (cost per transaction, cost per user)."""
    db = get_database()
    return db.query_df("""
        SELECT
            c.month,
            c.application_id,
            a.application_name,
            c.total_cost,
            u.total_active_users,
            u.total_transactions,
            ROUND(c.total_cost / NULLIF(u.total_active_users, 0), 2) AS monthly_cost_per_user,
            ROUND(c.total_cost / NULLIF(u.total_transactions, 0), 4) AS monthly_cost_per_transaction
        FROM v_app_monthly_cost c
        JOIN applications a ON c.application_id = a.application_id
        JOIN v_app_monthly_consumption u ON c.month = u.month AND c.application_id = u.application_id
        ORDER BY c.application_id, c.month
    """)
