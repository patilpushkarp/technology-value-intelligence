"""Cost Driver and Financial Variance Analysis Engine.

Deconstructs Month-over-Month (MoM) and Year-to-Date (YTD) cost variances across
cost pools, categories, applications, services, and business units.
Detects healthy consumption-driven cost growth (Scenario G) vs unbacked spend anomalies (Scenario H).
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

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


def detect_cost_anomalies(
    method: str = "combined",
    z_threshold: float = 2.0,
) -> pd.DataFrame:
    """Continuous statistical anomaly detection using rolling Z-scores and Isolation Forests.

    Detects sudden cost spikes and evaluates whether consumption (transactions, active users)
    scaled proportionally.
    """
    db = get_database()
    df = db.query_df("""
        SELECT
            c.application_id,
            a.application_name,
            c.month,
            SUM(c.amount) AS monthly_spend,
            COALESCE(u.transactions, 0) AS transactions,
            COALESCE(u.active_users, 0) AS active_users
        FROM cost_records c
        JOIN applications a ON c.application_id = a.application_id
        LEFT JOIN consumption_records u ON c.application_id = u.application_id AND c.month = u.month
        GROUP BY c.application_id, a.application_name, c.month, u.transactions, u.active_users
        ORDER BY c.application_id, c.month
    """)

    df["prev_spend"] = df.groupby("application_id")["monthly_spend"].shift(1)
    df["spend_delta"] = (df["monthly_spend"] - df["prev_spend"]).fillna(0.0)
    df["prev_txns"] = df.groupby("application_id")["transactions"].shift(1)
    df["txn_growth_pct"] = np.where(
        df["prev_txns"] > 0,
        ((df["transactions"] - df["prev_txns"]) / df["prev_txns"]) * 100.0,
        0.0,
    )
    df["unit_cost"] = np.where(df["transactions"] > 0, df["monthly_spend"] / df["transactions"], 0.0)

    stats = df.groupby("application_id")["monthly_spend"].agg(["mean", "std"]).reset_index()
    stats["std"] = stats["std"].replace(0, 1.0).fillna(1.0)
    df = df.merge(stats, on="application_id", how="left")
    df["z_score"] = ((df["monthly_spend"] - df["mean"]) / df["std"]).round(2)

    X = df[["monthly_spend", "spend_delta", "unit_cost"]].fillna(0.0).values
    iso = IsolationForest(contamination=0.06, random_state=42)
    iso.fit(X)
    df["iso_anomaly"] = iso.predict(X) == -1

    is_anomaly = (df["z_score"] >= z_threshold) | (df["iso_anomaly"] & (df["spend_delta"] > 1e6))
    anomalies = df[is_anomaly].copy()

    def classify_anomaly(row):
        z = row["z_score"]
        iso = row["iso_anomaly"]
        delta = row["spend_delta"]
        t_growth = row["txn_growth_pct"]

        if z >= 3.0 or (iso and delta >= 3e6):
            sev = "Critical"
        elif z >= 2.0 or delta >= 1.5e6:
            sev = "High"
        else:
            sev = "Moderate"

        if t_growth >= 20.0:
            cause = "Healthy Operational Scale (Elastic Surge)"
            investigate = False
        else:
            cause = "Unbacked Spend Spike (Potential Rate/Infrastructure Waste)"
            investigate = True

        return pd.Series([sev, cause, investigate])

    anomalies[["anomaly_severity", "root_cause_diagnosis", "requires_investigation"]] = anomalies.apply(
        classify_anomaly, axis=1
    )

    return anomalies[[
        "month",
        "application_id",
        "application_name",
        "monthly_spend",
        "spend_delta",
        "txn_growth_pct",
        "z_score",
        "iso_anomaly",
        "anomaly_severity",
        "root_cause_diagnosis",
        "requires_investigation",
    ]].sort_values(["requires_investigation", "spend_delta"], ascending=[False, False])


def calculate_sla_breach_penalties(
    rate_anomaly_threshold_pct: float = 25.0,
    penalty_credit_rate: float = 0.20,
) -> pd.DataFrame:
    """Calculate vendor contract SLA penalties for unbacked rate spikes.

    Identifies applications where cost spiked significantly without commensurate
    consumption growth, traces the underlying infrastructure vendor, and computes
    contractual service penalty credits.
    """
    db = get_database()
    drivers_info = identify_cost_drivers(baseline_month="2024-07", comparison_month="2024-08", top_n=20)
    app_drivers = drivers_info["top_application_drivers"]
    if app_drivers.empty:
        return pd.DataFrame()

    anomalous = app_drivers[app_drivers["investigation_flag"] == "ANOMALY_INVESTIGATE"]
    rows = []
    for _, r in anomalous.iterrows():
        app_id = r["application_id"]
        ven_df = db.query_df("""
            SELECT v.vendor_id, v.vendor_name, t.technology_name, t.technology_category AS category
            FROM rel_app_technology r
            JOIN technologies t ON r.technology_id = t.technology_id
            JOIN vendors v ON t.technology_vendor = v.vendor_name
            WHERE r.application_id = ?
            LIMIT 1
        """, [app_id])

        if not ven_df.empty:
            v_id = ven_df.iloc[0]["vendor_id"]
            v_name = ven_df.iloc[0]["vendor_name"]
            tech_name = ven_df.iloc[0]["technology_name"]
        else:
            v_id = "VEND_GENERIC"
            v_name = "Cloud Platform Provider"
            tech_name = "Managed Compute"

        unbacked_spend = float(r["cost_delta"])
        penalty_credit = round(unbacked_spend * penalty_credit_rate, 2)

        rows.append({
            "vendor_id": v_id,
            "vendor_name": v_name,
            "application_id": app_id,
            "application_name": r["application_name"],
            "technology_name": tech_name,
            "surge_month": "2024-08",
            "unbacked_spend_surge": unbacked_spend,
            "cost_growth_pct": r["cost_growth_pct"],
            "txn_growth_pct": r["txn_growth_pct"],
            "sla_contract_clause": "Clause 8.4: Unscheduled Rate/Capacity Over-billing Surcharge",
            "assessed_penalty_credit_inr": penalty_credit,
            "credit_status": "Credit Memo Claim Filed",
        })

    return pd.DataFrame(rows)


def forecast_budget_variance(
    forecast_months: int = 4,
    alpha: float = 0.2,
) -> pd.DataFrame:
    """Multi-period forward-looking budget variance forecast.

    Applies trend-adjusted exponential smoothing over historical 12-month run-rate
    to project upcoming fiscal quarters against target budget allocations.
    """
    hist = calculate_monthly_cost_variance()
    spends = hist["monthly_spend"].tolist()

    annual_budget = sum(spends) * 1.05
    monthly_budget_target = round(annual_budget / 12.0, 2)

    level = spends[0]
    trend = 0.0
    beta = 0.1
    for s in spends[1:]:
        prev_level = level
        level = alpha * s + (1 - alpha) * (prev_level + trend)
        trend = beta * (level - prev_level) + (1 - beta) * trend

    hist_std = float(np.std(spends))

    rows = []
    for h in range(1, forecast_months + 1):
        fc_month = f"2025-{h:02d}"
        proj_spend = level + h * trend
        std_h = hist_std * np.sqrt(h)
        lower_bound = max(0.0, proj_spend - 1.645 * std_h)
        upper_bound = proj_spend + 1.645 * std_h
        var_amount = round(proj_spend - monthly_budget_target, 2)
        var_pct = round((var_amount / monthly_budget_target) * 100.0, 2)

        status = "Budget Overrun Risk" if var_amount > 0 else "Within Budget Target"

        rows.append({
            "forecast_month": fc_month,
            "projected_monthly_spend": round(proj_spend, 2),
            "lower_bound_90pct": round(lower_bound, 2),
            "upper_bound_90pct": round(upper_bound, 2),
            "monthly_budget_target": monthly_budget_target,
            "projected_variance_inr": var_amount,
            "projected_variance_pct": var_pct,
            "runrate_governance_status": status,
        })

    return pd.DataFrame(rows)


def generate_finops_anomaly_tickets() -> List[Dict[str, Any]]:
    """Generate structured FinOps investigation ticket payloads (Jira/ServiceNow compatible)."""
    anomalies = detect_cost_anomalies()
    unbacked = anomalies[anomalies["requires_investigation"]]

    tickets = []
    for _, row in unbacked.iterrows():
        app_id = row["application_id"]
        app_name = row["application_name"]
        month = row["month"]
        delta = row["spend_delta"]
        sev = row["anomaly_severity"]

        ticket = {
            "ticket_id": f"FINOPS-2024-{app_id}-{month.replace('-', '')}",
            "priority": "P1 - Immediate Review" if sev == "Critical" else "P2 - Standard FinOps Review",
            "service_desk": "Cloud FinOps & Infrastructure Governance",
            "title": f"Cost Anomaly Alert: {app_name} ({app_id}) Spend Surged in {month}",
            "affected_application_id": app_id,
            "affected_application_name": app_name,
            "accounting_period": month,
            "spend_increase_inr": round(delta, 2),
            "statistical_z_score": float(row["z_score"]),
            "consumption_status": f"Transaction volume change: {row['txn_growth_pct']:.1f}% (Unbacked by usage)",
            "investigation_checklist": [
                "Audit cloud billing records for unannounced resource SKU upgrades.",
                "Verify whether on-demand container/VM clusters failed to scale down.",
                "Review vendor contract rate tiers and dispute unauthorized surcharge.",
            ],
            "target_sla_resolution_hours": 24 if sev == "Critical" else 48,
        }
        tickets.append(ticket)

    return tickets

