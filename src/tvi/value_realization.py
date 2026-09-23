"""Technology Value Realization (TVR) Analytics Engine.

Measures discretionary investment execution, budget variances, expected vs realized
benefits, benefit realization gaps, and tracked KPI outcome shifts.
Enforces analytical guardrails: expresses relations as 'associated with' rather than
unsubstantiated claims of direct causality.
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from tvi.database import get_database


def calculate_project_budget_variance() -> pd.DataFrame:
    """Evaluate capital/operational budget variance for all projects.

    Investment Variance = Actual Spend - Investment Budget
    Variance % = (Actual Spend - Budget) / Budget * 100
    """
    db = get_database()
    df = db.query_df("""
        SELECT
            project_id,
            project_name,
            project_type,
            sponsor_business_unit,
            status,
            investment_budget,
            actual_spend,
            ROUND(actual_spend - investment_budget, 2) AS budget_variance,
            ROUND((actual_spend - investment_budget) / NULLIF(investment_budget, 0) * 100.0, 2) AS budget_variance_pct
        FROM projects
        ORDER BY budget_variance DESC
    """)
    df["variance_status"] = np.where(
        df["budget_variance"] > 0,
        "Over Budget",
        np.where(df["budget_variance"] < 0, "Under Budget", "On Budget"),
    )
    return df


def calculate_benefit_realization() -> pd.DataFrame:
    """Calculate expected vs recorded realized benefit per project and category.

    Benefit Realization % = Realized Benefit / Expected Benefit * 100
    Benefit Gap = Expected Benefit - Realized Benefit
    """
    db = get_database()
    df = db.query_df("""
        SELECT
            p.project_id,
            p.project_name,
            p.project_type,
            p.status AS project_status,
            p.investment_budget,
            p.actual_spend,
            SUM(b.expected_value) AS total_expected_benefit,
            SUM(b.realized_value) AS total_realized_benefit,
            ROUND(SUM(b.expected_value) - SUM(b.realized_value), 2) AS benefit_gap,
            ROUND(SUM(b.realized_value) / NULLIF(SUM(b.expected_value), 0) * 100.0, 2) AS benefit_realization_pct
        FROM projects p
        LEFT JOIN benefits b ON p.project_id = b.project_id
        GROUP BY p.project_id, p.project_name, p.project_type, p.status, p.investment_budget, p.actual_spend
        ORDER BY total_expected_benefit DESC
    """)

    # ROI proxy: recorded realized benefit vs actual spend
    df["recorded_value_multiple"] = np.where(
        df["actual_spend"] > 0,
        (df["total_realized_benefit"] / df["actual_spend"]).round(2),
        0.0,
    )
    return df


def analyze_benefit_kpi_progression() -> pd.DataFrame:
    """Connect project benefits to targeted KPI performance movements."""
    db = get_database()
    return db.query_df("""
        SELECT
            p.project_id,
            p.project_name,
            b.benefit_id,
            b.benefit_type,
            b.expected_value,
            b.realized_value,
            b.benefit_status,
            k.kpi_id,
            k.kpi_name,
            k.kpi_category,
            k.baseline_value,
            k.target_value,
            k.actual_value,
            k.unit,
            ROUND((k.actual_value - k.baseline_value) / NULLIF(k.target_value - k.baseline_value, 0) * 100.0, 1) AS kpi_target_achievement_pct
        FROM projects p
        JOIN benefits b ON p.project_id = b.project_id
        JOIN rel_benefit_kpi r ON b.benefit_id = r.benefit_id
        JOIN kpis k ON r.kpi_id = k.kpi_id
        ORDER BY p.project_id, b.benefit_id
    """)


def get_project_value_profile(project_id: str) -> Dict[str, Any]:
    """Retrieve detailed investment, benefit realization, and KPI outcome dossier."""
    db = get_database()
    p_df = db.query_df("SELECT * FROM projects WHERE project_id = ?", [project_id])
    if p_df.empty:
        return {}

    p_data = p_df.iloc[0].to_dict()

    b_df = db.query_df("SELECT * FROM benefits WHERE project_id = ?", [project_id])
    kpi_df = db.query_df("""
        SELECT k.*
        FROM rel_benefit_kpi r
        JOIN benefits b ON r.benefit_id = b.benefit_id
        JOIN kpis k ON r.kpi_id = k.kpi_id
        WHERE b.project_id = ?
    """, [project_id])

    apps_funded = db.query_df("""
        SELECT a.application_id, a.application_name, a.lifecycle_status
        FROM rel_app_project r
        JOIN applications a ON r.application_id = a.application_id
        WHERE r.project_id = ?
    """, [project_id])

    return {
        "project": p_data,
        "benefits": b_df,
        "kpis": kpi_df,
        "associated_applications": apps_funded,
    }
