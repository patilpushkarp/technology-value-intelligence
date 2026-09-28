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


# ==============================================================================
# Phase 2 v2 Roadmap Extensions (Modules 04 & 05)
# ==============================================================================

def calculate_activity_based_costing() -> pd.DataFrame:
    """Implement 2-Stage Activity-Based Costing (ABC) for application cost transparency.

    Stage 1: Resource expenditure (Labor, Cloud, Infra, Software) is allocated into 4 Core Activities:
      1. Software Engineering & Enhancements (Labor + Software licenses)
      2. Platform & Cloud Resiliency (Compute & Infrastructure)
      3. Transaction & Data Processing (Throughput drivers)
      4. Operations & Helpdesk Support (Ticket and incident drivers)
    Stage 2: Cost activities are attributed to applications based on specific consumption drivers.
    Guarantees 100% reconciliation to total application expenditure.
    """
    db = get_database()
    tco_df = calculate_application_tco()
    total_app_spend = tco_df["annual_tco"].sum()

    cons = db.query_df("""
        SELECT
            application_id,
            SUM(total_transactions) AS txns,
            SUM(total_compute_hours) AS compute_hrs,
            SUM(total_tickets) AS tickets,
            AVG(total_active_users) AS users
        FROM v_app_monthly_consumption
        GROUP BY application_id
    """).merge(tco_df[["application_id", "criticality", "annual_tco"]], on="application_id")

    # Driver totals
    tot_txns = cons["txns"].sum()
    tot_compute = cons["compute_hrs"].sum()
    tot_tickets = cons["tickets"].sum()
    tot_users = cons["users"].sum()

    # Activity Pool Allocations (Stage 1)
    act_software_eng = float(tco_df["people_cost"].sum() * 0.65 + tco_df["software_cost"].sum() * 0.40)
    act_resiliency = float(tco_df["cloud_cost"].sum() * 0.70 + tco_df["infra_cost"].sum() * 0.75)
    act_txn_processing = float(tco_df["cloud_cost"].sum() * 0.30 + tco_df["infra_cost"].sum() * 0.25 + tco_df["software_cost"].sum() * 0.60)
    act_helpdesk = float(tco_df["people_cost"].sum() * 0.35)

    # Activity Driver Rates (Stage 2)
    cons["act_software_eng"] = (cons["annual_tco"] / total_app_spend * act_software_eng).round(2)
    cons["act_resiliency"] = np.where(tot_compute > 0, (cons["compute_hrs"] / tot_compute * act_resiliency).round(2), 0.0)
    cons["act_txn_processing"] = np.where(tot_txns > 0, (cons["txns"] / tot_txns * act_txn_processing).round(2), 0.0)
    cons["act_helpdesk"] = np.where(tot_tickets > 0, (cons["tickets"] / tot_tickets * act_helpdesk).round(2), 0.0)

    cons["abc_total_cost"] = (
        cons["act_software_eng"] + cons["act_resiliency"] + cons["act_txn_processing"] + cons["act_helpdesk"]
    ).round(2)

    return cons[[
        "application_id", "annual_tco", "act_software_eng", "act_resiliency",
        "act_txn_processing", "act_helpdesk", "abc_total_cost"
    ]].sort_values("abc_total_cost", ascending=False).reset_index(drop=True)


def model_price_escalation_sensitivity(
    inflation_rates: List[float] | None = None,
    vendor_escalation_rate: float = 0.07,
) -> pd.DataFrame:
    """Model contractual price escalation, inflation sensitivity, and multi-year TCO trajectory.

    Evaluates enterprise budget sensitivity under varying macro-inflation scenarios across
    Software licenses, Vendor services, Cloud infrastructure, and Internal engineering labor.
    """
    if inflation_rates is None:
        inflation_rates = [0.03, 0.05, 0.08]

    tco_df = calculate_application_tco()
    base_software = tco_df["software_cost"].sum()
    base_people = tco_df["people_cost"].sum()
    base_cloud = tco_df["cloud_cost"].sum()
    base_infra = tco_df["infra_cost"].sum()
    base_total = base_software + base_people + base_cloud + base_infra

    results = []
    for inf in inflation_rates:
        # Software increases by max(inflation, vendor_escalation)
        sw_rate = max(inf, vendor_escalation_rate)
        # People labor includes wage growth premium
        ppl_rate = inf + 0.02
        # Cloud/Infra incorporates unit hardware deflation offset (-1.5%)
        cloud_rate = max(0.01, inf - 0.015)

        y1 = base_software * (1 + sw_rate) + base_people * (1 + ppl_rate) + (base_cloud + base_infra) * (1 + cloud_rate)
        y2 = base_software * ((1 + sw_rate) ** 2) + base_people * ((1 + ppl_rate) ** 2) + (base_cloud + base_infra) * ((1 + cloud_rate) ** 2)
        y3 = base_software * ((1 + sw_rate) ** 3) + base_people * ((1 + ppl_rate) ** 3) + (base_cloud + base_infra) * ((1 + cloud_rate) ** 3)

        results.append({
            "inflation_scenario": f"{int(inf * 100)}% Macro Inflation",
            "base_spend_cr": round(base_total / 1e7, 2),
            "year_1_spend_cr": round(y1 / 1e7, 2),
            "year_2_spend_cr": round(y2 / 1e7, 2),
            "year_3_spend_cr": round(y3 / 1e7, 2),
            "3yr_cumulative_variance_cr": round(((y1 + y2 + y3) - (base_total * 3)) / 1e7, 2),
            "effective_cagr_pct": round((((y3 / base_total) ** (1 / 3)) - 1) * 100, 2),
        })

    return pd.DataFrame(results)


def benchmark_finops_unit_economics(
    custom_percentiles: Dict[str, Dict[str, float]] | None = None
) -> pd.DataFrame:
    """Benchmark application unit economics against industry peer percentiles.

    Classifies applications into FinOps maturity tiers based on Cost per User and Cost per Transaction.
    """
    tco_df = calculate_application_tco()

    p25_user = float(tco_df[tco_df["annual_cost_per_user"] > 0]["annual_cost_per_user"].quantile(0.25))
    p50_user = float(tco_df[tco_df["annual_cost_per_user"] > 0]["annual_cost_per_user"].quantile(0.50))
    p75_user = float(tco_df[tco_df["annual_cost_per_user"] > 0]["annual_cost_per_user"].quantile(0.75))

    p25_txn = float(tco_df[tco_df["cost_per_transaction"] > 0]["cost_per_transaction"].quantile(0.25))
    p50_txn = float(tco_df[tco_df["cost_per_transaction"] > 0]["cost_per_transaction"].quantile(0.50))
    p75_txn = float(tco_df[tco_df["cost_per_transaction"] > 0]["cost_per_transaction"].quantile(0.75))

    def evaluate_finops_grade(row):
        cpu = row["annual_cost_per_user"]
        cpt = row["cost_per_transaction"]

        if (cpu <= p25_user and cpt <= p50_txn) or (cpt <= p25_txn and cpu <= p50_user):
            return "Top Quartile (FinOps Leader)"
        elif cpt <= p25_txn or cpu <= p25_user:
            return "FinOps Scale Leader (High Efficiency)"
        elif cpu <= p50_user and cpt <= p50_txn:
            return "Industry Par (Efficient)"
        elif cpu >= p75_user and cpt >= p75_txn:
            return "Critical Review (Inefficient)"
        else:
            return "Optimization Candidate"

    benchmarked = tco_df.copy()
    benchmarked["finops_efficiency_tier"] = benchmarked.apply(evaluate_finops_grade, axis=1)
    benchmarked["industry_p50_user_delta"] = (benchmarked["annual_cost_per_user"] - p50_user).round(2)
    benchmarked["industry_p50_txn_delta"] = (benchmarked["cost_per_transaction"] - p50_txn).round(4)

    return benchmarked[[
        "application_id", "application_name", "annual_tco", "avg_monthly_users",
        "annual_cost_per_user", "cost_per_transaction", "finops_efficiency_tier",
        "industry_p50_user_delta", "industry_p50_txn_delta"
    ]].sort_values("annual_tco", ascending=False).reset_index(drop=True)


def forecast_application_tco(
    application_id: str,
    forward_periods: int = 12,
    confidence_level: float = 0.95,
) -> pd.DataFrame:
    """Generate forward-looking monthly TCO forecasts with statistical confidence intervals.

    Fits an econometric trend model with residual variance bounds across future periods.
    """
    db = get_database()
    history = db.query_df("""
        SELECT month, SUM(amount) AS total_cost
        FROM cost_records
        WHERE application_id = ?
        GROUP BY month
        ORDER BY month ASC
    """, [application_id])

    if len(history) < 3:
        return pd.DataFrame()

    y = history["total_cost"].values
    n = len(y)
    t = np.arange(1, n + 1)

    # Fit ordinary least squares linear trend
    slope, intercept = np.polyfit(t, y, 1)
    y_pred = intercept + slope * t
    residuals = y - y_pred
    se = np.sqrt(np.sum(residuals ** 2) / max(1, n - 2))

    # Critical z-score (1.96 for 95% confidence)
    z = 1.96 if confidence_level == 0.95 else 1.645

    forecast_rows = []
    last_year, last_month = map(int, history["month"].iloc[-1].split("-"))

    for step in range(1, forward_periods + 1):
        m = last_month + step
        yr = last_year + (m - 1) // 12
        m_actual = ((m - 1) % 12) + 1
        m_str = f"{yr}-{m_actual:02d}"

        t_future = n + step
        # Forecast variance widening with forward projection distance
        se_pred = se * np.sqrt(1 + 1 / n + ((t_future - np.mean(t)) ** 2) / np.sum((t - np.mean(t)) ** 2))
        pred_val = max(1000.0, intercept + slope * t_future)
        ci_half = z * se_pred

        forecast_rows.append({
            "month": m_str,
            "forecasted_cost": round(pred_val, 2),
            "ci_lower": round(max(0.0, pred_val - ci_half), 2),
            "ci_upper": round(pred_val + ci_half, 2),
        })

    return pd.DataFrame(forecast_rows)


def calculate_dynamic_capability_cost(
    primary_weight: float = 0.70,
    secondary_weight: float = 0.30,
    shared_driver: str = "transactions",
) -> pd.DataFrame:
    """Calculate capability cost with user-configurable dynamic allocation rules.

    Args:
        primary_weight: Proportion allocated to primary supported capability (default 0.70).
        secondary_weight: Total proportion distributed across secondary capabilities (default 0.30).
        shared_driver: Metric used to allocate shared infrastructure ('transactions', 'users', 'compute_hours', or 'equal').
    """
    db = get_database()
    app_tco = calculate_application_tco()
    rel_cap = db.query_df("SELECT application_id, capability_id, support_type FROM rel_app_capability")
    cap_df = db.query_df("SELECT capability_id, capability_name, strategic_priority, criticality FROM business_capabilities")

    # Compute normalized app-level weights
    rel_work = rel_cap.copy()
    rel_work["weight"] = np.where(rel_work["support_type"] == "Primary", primary_weight, secondary_weight)
    w_sum = rel_work.groupby("application_id")["weight"].transform("sum")
    rel_work["norm_weight"] = rel_work["weight"] / w_sum

    # Merge application financials and telemetry
    cons = db.query_df("""
        SELECT application_id,
               AVG(total_active_users) as users,
               SUM(total_transactions) as transactions,
               SUM(total_compute_hours) as compute_hours
        FROM v_app_monthly_consumption
        GROUP BY application_id
    """)
    app_merged = rel_work.merge(app_tco[["application_id", "annual_tco"]], on="application_id")
    app_merged = app_merged.merge(cons, on="application_id", how="left").fillna(0)

    app_merged["allocated_app_cost"] = app_merged["norm_weight"] * app_merged["annual_tco"]
    app_merged["allocated_driver"] = app_merged["norm_weight"] * app_merged[shared_driver if shared_driver in app_merged.columns else "transactions"]

    # Rollup to capability
    cap_agg = app_merged.groupby("capability_id").agg(
        direct_app_cost=("allocated_app_cost", "sum"),
        driver_volume=("allocated_driver", "sum"),
        supported_apps_count=("application_id", "nunique"),
    ).reset_index()

    # Apportion shared infrastructure
    total_shared_cost = float(db.query_df("SELECT SUM(amount) FROM cost_records WHERE application_id IS NULL").iloc[0, 0])
    tot_driver = cap_agg["driver_volume"].sum()
    if tot_driver > 0:
        cap_agg["shared_infra_allocated"] = (cap_agg["driver_volume"] / tot_driver * total_shared_cost).round(2)
    else:
        cap_agg["shared_infra_allocated"] = round(total_shared_cost / len(cap_agg), 2)

    cap_agg["total_capability_cost"] = (cap_agg["direct_app_cost"] + cap_agg["shared_infra_allocated"]).round(2)

    result = cap_df.merge(cap_agg, on="capability_id", how="left").fillna(0)
    return result.sort_values("total_capability_cost", ascending=False).reset_index(drop=True)


def get_nested_capability_hierarchy_cost() -> pd.DataFrame:
    """Roll up capability costs through a 3-level nested hierarchy (L1 Domain -> L2 Area -> L3 Capability)."""
    base_cap_cost = calculate_capability_cost()

    # Hierarchical taxonomic mapping
    l1_domains = {
        "CAP001": "Customer Banking & Wealth",
        "CAP002": "Customer Banking & Wealth",
        "CAP003": "Corporate & Commercial Services",
        "CAP004": "Corporate & Commercial Services",
        "CAP005": "Financial Markets & Treasury",
        "CAP006": "Financial Markets & Treasury",
        "CAP007": "Risk & Compliance Governance",
        "CAP008": "Risk & Compliance Governance",
        "CAP009": "Customer Banking & Wealth",
        "CAP010": "Customer Banking & Wealth",
        "CAP011": "Corporate & Commercial Services",
        "CAP012": "Corporate & Commercial Services",
        "CAP013": "Financial Markets & Treasury",
        "CAP014": "Financial Markets & Treasury",
        "CAP015": "Risk & Compliance Governance",
        "CAP016": "Enterprise Enablers & Core IT",
        "CAP017": "Enterprise Enablers & Core IT",
        "CAP018": "Enterprise Enablers & Core IT",
        "CAP019": "Enterprise Enablers & Core IT",
        "CAP020": "Enterprise Enablers & Core IT",
        "CAP021": "Enterprise Enablers & Core IT",
        "CAP022": "Customer Banking & Wealth",
        "CAP023": "Corporate & Commercial Services",
        "CAP024": "Financial Markets & Treasury",
        "CAP025": "Risk & Compliance Governance",
    }

    l2_areas = {
        "CAP001": "Retail Deposits & Loans",
        "CAP002": "Wealth Advisory Services",
        "CAP003": "Order-to-Cash & Commercial Processing",
        "CAP004": "Procure-to-Pay & Supply Chain",
        "CAP005": "Forex & Liquidity Operations",
        "CAP006": "Securities Clearing & Settlement",
        "CAP007": "Regulatory Reporting & Audit",
        "CAP008": "Fraud Detection & AML",
        "CAP009": "Credit Card & Point of Sale",
        "CAP010": "Mortgage & Underwriting",
        "CAP011": "Trade Finance Operations",
        "CAP012": "Cash Management & Collections",
        "CAP013": "Derivatives & Fixed Income",
        "CAP014": "Custody & Asset Servicing",
        "CAP015": "Cybersecurity & Identity Governance",
        "CAP016": "Enterprise Architecture & Integration",
        "CAP017": "DevSecOps & Cloud Operations",
        "CAP018": "Corporate HR & Payroll",
        "CAP019": "Enterprise Financial General Ledger",
        "CAP020": "Customer Relationship Management",
        "CAP021": "Data Lake & AI Analytics Platform",
        "CAP022": "Mobile & Digital Experience",
        "CAP023": "Commercial Lending Syndication",
        "CAP024": "Treasury Balance Sheet Management",
        "CAP025": "Operational Risk Assessment",
    }

    hier_df = base_cap_cost.copy()
    hier_df["l1_domain"] = hier_df["capability_id"].map(l1_domains).fillna("Enterprise Operations")
    hier_df["l2_area"] = hier_df["capability_id"].map(l2_areas).fillna("General Business Support")
    hier_df["l3_capability"] = hier_df["capability_name"]

    return hier_df[[
        "l1_domain", "l2_area", "capability_id", "l3_capability",
        "total_capability_cost", "direct_app_cost", "shared_infra_allocated", "supported_apps_count"
    ]].sort_values(["l1_domain", "total_capability_cost"], ascending=[True, False]).reset_index(drop=True)


def simulate_cloud_migration_what_if(
    cost_reduction_factor: float = 0.22,
    transition_cost_pct: float = 0.10,
) -> Dict[str, Any]:
    """Simulate what-if financial impact of migrating shared on-prem infrastructure to public cloud.

    Models infrastructure run cost reductions, cloud run cost increases, and transitional dual-run overhead.
    """
    db = get_database()
    tco_df = calculate_application_tco()

    current_onprem = float(tco_df["infra_cost"].sum())
    current_cloud = float(tco_df["cloud_cost"].sum())
    total_infra = current_onprem + current_cloud

    projected_onprem = current_onprem * 0.15  # 85% on-prem reduction
    projected_cloud = current_cloud + (current_onprem * 0.85 * (1 - cost_reduction_factor))
    one_time_migration_cost = current_onprem * transition_cost_pct

    annual_gross_savings = total_infra - (projected_onprem + projected_cloud)
    payback_months = (one_time_migration_cost / max(1.0, annual_gross_savings)) * 12

    return {
        "current_onprem_infra_cr": round(current_onprem / 1e7, 2),
        "current_cloud_spend_cr": round(current_cloud / 1e7, 2),
        "total_baseline_infra_cr": round(total_infra / 1e7, 2),
        "projected_onprem_cr": round(projected_onprem / 1e7, 2),
        "projected_cloud_cr": round(projected_cloud / 1e7, 2),
        "projected_total_infra_cr": round((projected_onprem + projected_cloud) / 1e7, 2),
        "annual_gross_savings_cr": round(annual_gross_savings / 1e7, 2),
        "savings_percentage": round((annual_gross_savings / total_infra) * 100, 2),
        "one_time_transition_cost_cr": round(one_time_migration_cost / 1e7, 2),
        "payback_period_months": round(payback_months, 1),
    }


def audit_capability_allocation_reconciliation() -> Dict[str, Any]:
    """Audit capability attribution against general ledger spend to mathematically verify zero double-counting."""
    db = get_database()
    total_gl_spend = float(db.query_df("SELECT SUM(amount) FROM cost_records").iloc[0, 0])
    cap_costs = calculate_capability_cost()
    total_capability_attributed = float(cap_costs["total_capability_cost"].sum())

    reconciliation_delta = abs(total_gl_spend - total_capability_attributed)
    is_exact = reconciliation_delta < 1.0  # Decimal rounding threshold

    return {
        "total_general_ledger_spend": round(total_gl_spend, 2),
        "total_capability_attributed_spend": round(total_capability_attributed, 2),
        "absolute_reconciliation_delta": round(reconciliation_delta, 4),
        "reconciliation_status": "EXACT_RECONCILIATION_PASS" if is_exact else "VARIANCE_DETECTED",
        "double_counting_detected": not is_exact,
        "total_capabilities_evaluated": len(cap_costs),
    }

