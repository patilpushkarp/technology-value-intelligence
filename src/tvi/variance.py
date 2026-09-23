"""Cost Driver and Financial Variance Analysis Engine.

Deconstructs Month-over-Month (MoM) and Year-to-Date (YTD) cost variances across
cost pools, categories, applications, services, and business units.
Detects healthy consumption-driven cost growth (Scenario G) vs unbacked spend anomalies (Scenario H).
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from tvi.database import get_database


def calculate_monthly_cost_variance() -> pd.DataFrame:
    """Calculate total technology cost time series with MoM change and MoM growth rate."""
    db = get_database()
    df = db.query_df("""
        SELECT month, SUM(amount) AS monthly_spend
        FROM cost_records
        GROUP BY month
        ORDER BY month ASC
    """)

    df["prev_month_spend"] = df["monthly_spend"].shift(1)
    df["mom_change_amount"] = (df["monthly_spend"] - df["prev_month_spend"]).round(2)
    df["mom_change_pct"] = (
        (df["mom_change_amount"] / df["prev_month_spend"]) * 100.0
    ).round(2)
    df["ytd_cumulative_spend"] = df["monthly_spend"].cumsum().round(2)

    return df


def calculate_category_variance(month_a: str, month_b: str) -> pd.DataFrame:
    """Compare cost category totals between two target months."""
    db = get_database()
    return db.query_df("""
        WITH ma AS (
            SELECT cost_category, SUM(amount) AS spend_a
            FROM cost_records
            WHERE month = ?
            GROUP BY cost_category
        ),
        mb AS (
            SELECT cost_category, SUM(amount) AS spend_b
            FROM cost_records
            WHERE month = ?
            GROUP BY cost_category
        )
        SELECT
            COALESCE(ma.cost_category, mb.cost_category) AS cost_category,
            COALESCE(ma.spend_a, 0.0) AS spend_baseline,
            COALESCE(mb.spend_b, 0.0) AS spend_comparison,
            ROUND(COALESCE(mb.spend_b, 0.0) - COALESCE(ma.spend_a, 0.0), 2) AS variance_amount,
            ROUND((COALESCE(mb.spend_b, 0.0) - COALESCE(ma.spend_a, 0.0)) / NULLIF(ma.spend_a, 0) * 100.0, 2) AS variance_pct
        FROM ma
        FULL OUTER JOIN mb ON ma.cost_category = mb.cost_category
        ORDER BY variance_amount DESC
    """, [month_a, month_b])


def identify_cost_drivers(
    baseline_month: str = "2024-07",
    comparison_month: str = "2024-08",
    top_n: int = 5,
) -> Dict[str, Any]:
    """Perform root-cause driver decomposition explaining cost shift between two periods.

    Distinguishes:
    - Scenario G: Consumption-driven growth (e.g. transactions surged alongside cloud cost)
    - Scenario H: Cost surge with flat/decreasing consumption (anomaly flag)
    """
    db = get_database()

    # 1. Total Variance
    tot_df = db.query_df("""
        SELECT
            SUM(CASE WHEN month = ? THEN amount ELSE 0 END) as spend_base,
            SUM(CASE WHEN month = ? THEN amount ELSE 0 END) as spend_comp
        FROM cost_records
    """, [baseline_month, comparison_month])
    spend_base = float(tot_df.iloc[0]["spend_base"])
    spend_comp = float(tot_df.iloc[0]["spend_comp"])
    total_delta = spend_comp - spend_base

    # 2. Category Drivers
    cat_df = calculate_category_variance(baseline_month, comparison_month)

    # 3. Application Drivers with Consumption Correlation
    app_df = db.query_df("""
        WITH app_costs AS (
            SELECT
                application_id,
                SUM(CASE WHEN month = ? THEN amount ELSE 0 END) AS cost_base,
                SUM(CASE WHEN month = ? THEN amount ELSE 0 END) AS cost_comp
            FROM cost_records
            WHERE application_id IS NOT NULL
            GROUP BY application_id
        ),
        app_cons AS (
            SELECT
                application_id,
                SUM(CASE WHEN month = ? THEN total_transactions ELSE 0 END) AS txns_base,
                SUM(CASE WHEN month = ? THEN total_transactions ELSE 0 END) AS txns_comp,
                SUM(CASE WHEN month = ? THEN total_active_users ELSE 0 END) AS users_base,
                SUM(CASE WHEN month = ? THEN total_active_users ELSE 0 END) AS users_comp
            FROM v_app_monthly_consumption
            GROUP BY application_id
        )
        SELECT
            c.application_id,
            a.application_name,
            c.cost_base,
            c.cost_comp,
            ROUND(c.cost_comp - c.cost_base, 2) AS cost_delta,
            ROUND((c.cost_comp - c.cost_base) / NULLIF(c.cost_base, 0) * 100.0, 1) AS cost_growth_pct,
            u.txns_base,
            u.txns_comp,
            ROUND((u.txns_comp - u.txns_base) / NULLIF(u.txns_base, 0) * 100.0, 1) AS txn_growth_pct,
            u.users_base,
            u.users_comp
        FROM app_costs c
        JOIN applications a ON c.application_id = a.application_id
        JOIN app_cons u ON c.application_id = u.application_id
        ORDER BY cost_delta DESC
    """, [baseline_month, comparison_month, baseline_month, comparison_month, baseline_month, comparison_month])

    # Classify drivers
    classified_drivers = []
    for _, r in app_df.head(top_n).iterrows():
        c_delta = r["cost_delta"]
        t_growth = r["txn_growth_pct"] or 0.0

        if c_delta > 0:
            if t_growth >= 20.0:
                diagnosis = "Consumption-Driven Growth (Elastic scale responding to business activity)"
                flag = "NORMAL_SCALE"
            else:
                diagnosis = "Cost Increase Without Commensurate Consumption Growth (Potential Rate/Infrastructure Anomaly)"
                flag = "ANOMALY_INVESTIGATE"
        else:
            diagnosis = "Cost Reduction / Optimization"
            flag = "SAVING"

        classified_drivers.append({
            "application_id": r["application_id"],
            "application_name": r["application_name"],
            "cost_delta": c_delta,
            "cost_growth_pct": r["cost_growth_pct"],
            "txn_growth_pct": t_growth,
            "diagnosis": diagnosis,
            "investigation_flag": flag,
        })

    return {
        "baseline_month": baseline_month,
        "comparison_month": comparison_month,
        "spend_baseline": spend_base,
        "spend_comparison": spend_comp,
        "total_cost_delta": round(total_delta, 2),
        "total_cost_delta_pct": round((total_delta / max(1.0, spend_base)) * 100.0, 2),
        "top_category_drivers": cat_df.head(top_n),
        "top_application_drivers": pd.DataFrame(classified_drivers),
    }
