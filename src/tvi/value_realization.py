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


def calculate_investment_financial_metrics(
    discount_rate: float = 0.08,
    time_horizon_years: int = 5,
) -> pd.DataFrame:
    """Calculate Net Present Value (NPV), Internal Rate of Return (IRR), and Payback Period.

    Evaluates capital investment cash flows: Year 0 outflow (-actual_spend),
    and recurring annual benefit inflows across time_horizon_years.
    """
    db = get_database()
    projects_df = db.query_df("""
        SELECT
            p.project_id,
            p.project_name,
            p.project_type,
            p.status,
            p.investment_budget,
            p.actual_spend,
            COALESCE(SUM(b.realized_value), 0.0) AS total_realized_benefit,
            COALESCE(SUM(b.expected_value), 0.0) AS total_expected_benefit
        FROM projects p
        LEFT JOIN benefits b ON p.project_id = b.project_id
        GROUP BY p.project_id, p.project_name, p.project_type, p.status, p.investment_budget, p.actual_spend
        ORDER BY p.project_id
    """)

    rows = []
    for _, row in projects_df.iterrows():
        spend = float(row["actual_spend"]) if row["actual_spend"] > 0 else float(row["investment_budget"])
        annual_benefit = float(row["total_realized_benefit"]) if row["total_realized_benefit"] > 0 else (
            float(row["total_expected_benefit"]) * 0.75 if row["status"] != "Cancelled" else 0.0
        )

        pv_benefits = sum(annual_benefit / ((1.0 + discount_rate) ** t) for t in range(1, time_horizon_years + 1))
        npv = pv_benefits - spend

        irr_pct = None
        if spend > 0 and annual_benefit > 0:
            def npv_func(r):
                if r <= -0.99:
                    return 1e9
                return sum(annual_benefit / ((1.0 + r) ** t) for t in range(1, time_horizon_years + 1)) - spend

            try:
                from scipy.optimize import brentq
                f_low = npv_func(-0.50)
                f_high = npv_func(3.0)
                if f_low * f_high <= 0:
                    r_sol = brentq(npv_func, -0.50, 3.0)
                    irr_pct = round(r_sol * 100.0, 1)
                elif f_low < 0:
                    irr_pct = -50.0
                else:
                    irr_pct = 300.0
            except Exception:
                irr_pct = None

        cum_cf = -spend
        payback_years = None
        for t in range(1, time_horizon_years + 1):
            disc_flow = annual_benefit / ((1.0 + discount_rate) ** t)
            cum_cf += disc_flow
            if cum_cf >= 0:
                prev_cum = cum_cf - disc_flow
                frac = abs(prev_cum) / disc_flow if disc_flow > 0 else 0
                payback_years = round((t - 1) + frac, 1)
                break

        bcr = round(pv_benefits / spend, 2) if spend > 0 else 0.0

        if npv > 0 and (irr_pct is None or irr_pct >= 15.0):
            verdict = "High Value Creator"
        elif npv >= 0:
            verdict = "Moderate Payback"
        elif annual_benefit > 0:
            verdict = "Value Deficit (Sub-hurdle)"
        else:
            verdict = "Non-Performing Asset"

        rows.append({
            "project_id": row["project_id"],
            "project_name": row["project_name"],
            "project_type": row["project_type"],
            "status": row["status"],
            "actual_spend": spend,
            "annual_benefit_inflow": annual_benefit,
            "npv": round(npv, 2),
            "irr_pct": irr_pct,
            "discounted_payback_years": payback_years,
            "benefit_cost_ratio": bcr,
            "financial_verdict": verdict,
        })

    return pd.DataFrame(rows).sort_values("npv", ascending=False)


def estimate_causal_impact_did(
    project_id: str = "PRJ003",
    control_app_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Estimate project impact via econometric Difference-in-Differences (DiD).

    Compares monthly unit economics between the project's target application (Treatment)
    and a non-modernized peer application (Control) before and after project rollout.

    Consulting Guardrail:
    - Results represent statistical divergence associated with intervention, not isolated causality.
    """
    db = get_database()

    target_apps = db.query_df("""
        SELECT application_id FROM rel_app_project WHERE project_id = ?
    """, [project_id])

    if target_apps.empty:
        return {"error": f"No target application linked to project '{project_id}'."}

    treatment_app = target_apps.iloc[0]["application_id"]

    if control_app_id is None:
        candidates = db.query_df("""
            SELECT a.application_id
            FROM applications a
            WHERE a.application_id != ?
              AND a.application_id NOT IN (SELECT application_id FROM rel_app_project WHERE project_id = ?)
            ORDER BY a.annual_license_cost DESC
            LIMIT 1
        """, [treatment_app, project_id])
        control_app = candidates.iloc[0]["application_id"] if not candidates.empty else "APP008"
    else:
        control_app = control_app_id

    p_info = db.query_df("SELECT * FROM projects WHERE project_id = ?", [project_id]).iloc[0]
    # Synthetic month cutoff: YYYY-MM derived from end_date
    split_month = str(p_info["end_date"])[:7] if pd.notna(p_info.get("end_date")) else "2024-05"

    sql = """
        SELECT
            c.application_id,
            c.month,
            c.transactions,
            COALESCE(sum(cr.amount), 0.0) AS monthly_spend,
            ROUND(COALESCE(sum(cr.amount), 0.0) / NULLIF(c.transactions, 0), 4) AS cost_per_transaction
        FROM consumption_records c
        LEFT JOIN cost_records cr ON c.application_id = cr.application_id AND c.month = cr.month
        WHERE c.application_id IN (?, ?)
        GROUP BY c.application_id, c.month, c.transactions
        ORDER BY c.application_id, c.month
    """
    df = db.query_df(sql, [treatment_app, control_app])

    treat_df = df[df["application_id"] == treatment_app]
    ctrl_df = df[df["application_id"] == control_app]

    treat_pre = float(treat_df[treat_df["month"] <= split_month]["cost_per_transaction"].mean())
    treat_post = float(treat_df[treat_df["month"] > split_month]["cost_per_transaction"].mean())

    ctrl_pre = float(ctrl_df[ctrl_df["month"] <= split_month]["cost_per_transaction"].mean())
    ctrl_post = float(ctrl_df[ctrl_df["month"] > split_month]["cost_per_transaction"].mean())

    treat_delta = treat_post - treat_pre
    ctrl_delta = ctrl_post - ctrl_pre
    did_estimate = treat_delta - ctrl_delta
    rel_improvement_pct = round((did_estimate / (treat_pre if treat_pre > 0 else 1.0)) * 100.0, 2)

    return {
        "project_id": project_id,
        "project_name": p_info["project_name"],
        "treatment_application": treatment_app,
        "control_application": control_app,
        "intervention_split_month": split_month,
        "treatment_pre_mean_unit_cost": round(treat_pre, 4),
        "treatment_post_mean_unit_cost": round(treat_post, 4),
        "treatment_delta": round(treat_delta, 4),
        "control_pre_mean_unit_cost": round(ctrl_pre, 4),
        "control_post_mean_unit_cost": round(ctrl_post, 4),
        "control_delta": round(ctrl_delta, 4),
        "difference_in_differences_estimate": round(did_estimate, 4),
        "relative_cost_reduction_pct": round(abs(rel_improvement_pct), 2) if did_estimate < 0 else 0.0,
        "econometric_interpretation": (
            f"Project {project_id} is associated with a {abs(did_estimate):.4f} ₹/txn reduction in unit cost "
            f"relative to control {control_app} over the post-intervention period."
        ),
        "consulting_guardrail_notice": (
            "Notice: Observed divergence indicates empirical association under difference-in-differences "
            "framing; does not establish strict counterfactual single-cause attribution without random assignment."
        ),
    }


def generate_stage_gate_health_scorecard() -> pd.DataFrame:
    """Evaluate multi-dimensional portfolio stage-gate health scorecards.

    Assesses projects across:
    - Budget variance % (Financial discipline)
    - Benefit realization % (Value delivery)
    - Schedule status
    - Risk intervention recommendation
    """
    db = get_database()
    bv = calculate_project_budget_variance()
    br = calculate_benefit_realization()

    merged = bv.merge(
        br[["project_id", "total_expected_benefit", "total_realized_benefit", "benefit_realization_pct", "benefit_gap"]],
        on="project_id",
        how="left",
    ).fillna(0)

    rows = []
    for _, row in merged.iterrows():
        b_var_pct = float(row["budget_variance_pct"])
        b_real_pct = float(row["benefit_realization_pct"])
        status = row["status"]

        if b_var_pct <= 5.0:
            budget_health = "Green"
        elif b_var_pct <= 15.0:
            budget_health = "Amber"
        else:
            budget_health = "Red"

        if status == "Completed":
            if b_real_pct >= 90.0:
                benefit_health = "Green"
            elif b_real_pct >= 70.0:
                benefit_health = "Amber"
            else:
                benefit_health = "Red"
        else:
            benefit_health = "Amber" if status == "In Progress" else "Red"

        if budget_health == "Red" or benefit_health == "Red":
            gate_status = "Red (Executive Gate Intervention)"
            action = "Escalate to Steering Committee; audit deliverable slippage and pause further capital drawdowns."
        elif budget_health == "Amber" or benefit_health == "Amber":
            gate_status = "Amber (Conditional Exception)"
            action = "Issue formal PMO variance warning; require corrective milestone remediation plan within 30 days."
        else:
            gate_status = "Green (Pass Gate)"
            action = "Approve capital stage-gate progression and release subsequent funding tranche."

        rows.append({
            "project_id": row["project_id"],
            "project_name": row["project_name"],
            "project_type": row["project_type"],
            "status": status,
            "actual_spend": row["actual_spend"],
            "budget_variance_pct": b_var_pct,
            "budget_health": budget_health,
            "benefit_realization_pct": b_real_pct,
            "benefit_health": benefit_health,
            "composite_gate_status": gate_status,
            "governance_action": action,
        })

    return pd.DataFrame(rows).sort_values("composite_gate_status", ascending=False)


def evaluate_capability_maturity_progression() -> pd.DataFrame:
    """Link capital project deliveries to business capability maturity score progression.

    Measures capability baseline maturity vs target maturity and post-project realized uplift,
    computing the capital efficiency of capability transformation (₹/Maturity Point).
    """
    db = get_database()
    df = db.query_df("""
        SELECT
            c.capability_id,
            c.capability_name,
            c.strategic_priority,
            c.criticality,
            p.project_id,
            p.project_name,
            p.actual_spend,
            p.status AS project_status,
            COALESCE(SUM(b.realized_value), 0.0) AS total_realized_benefit,
            COALESCE(SUM(b.expected_value), 0.0) AS total_expected_benefit
        FROM business_capabilities c
        JOIN rel_project_capability r ON c.capability_id = r.capability_id
        JOIN projects p ON r.project_id = p.project_id
        LEFT JOIN benefits b ON p.project_id = b.project_id
        GROUP BY c.capability_id, c.capability_name, c.strategic_priority, c.criticality,
                 p.project_id, p.project_name, p.actual_spend, p.status
        ORDER BY c.capability_id
    """)

    base_map = {
        "High": 2.5,
        "Medium": 2.0,
        "Low": 1.5,
    }
    df["baseline_maturity"] = df["strategic_priority"].map(base_map).fillna(2.0)

    realization_ratio = np.where(
        df["total_expected_benefit"] > 0,
        np.clip(df["total_realized_benefit"] / df["total_expected_benefit"], 0.0, 1.3),
        0.5,
    )
    df["maturity_uplift"] = np.where(
        df["project_status"] == "Completed",
        (1.5 * realization_ratio).round(2),
        (0.5 * realization_ratio).round(2),
    )
    df["current_maturity"] = np.clip(df["baseline_maturity"] + df["maturity_uplift"], 1.0, 5.0).round(2)
    df["cost_per_maturity_point"] = np.where(
        df["maturity_uplift"] > 0,
        (df["actual_spend"] / df["maturity_uplift"]).round(2),
        df["actual_spend"],
    )

    def classify_alignment(row):
        if row["strategic_priority"] == "High" and row["maturity_uplift"] >= 1.0:
            return "Strategic Core Accelerated"
        elif row["maturity_uplift"] >= 1.0:
            return "Solid Operational Uplift"
        elif row["strategic_priority"] == "High":
            return "Strategic Capability Lagging"
        else:
            return "Marginal Value Realized"

    df["transformation_impact"] = df.apply(classify_alignment, axis=1)

    return df[[
        "capability_id",
        "capability_name",
        "strategic_priority",
        "project_id",
        "project_name",
        "project_status",
        "actual_spend",
        "baseline_maturity",
        "maturity_uplift",
        "current_maturity",
        "cost_per_maturity_point",
        "transformation_impact",
    ]].sort_values("current_maturity", ascending=False)

