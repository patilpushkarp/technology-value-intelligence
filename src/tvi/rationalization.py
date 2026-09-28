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


def score_application_portfolio(
    custom_weights: Optional[Dict[str, float]] = None,
) -> pd.DataFrame:
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

    # Weights configuration
    w_cost = 0.30
    w_util = 0.25
    w_cap = 0.20
    w_life = 0.15
    w_crit = 0.10

    if custom_weights:
        w_cost = custom_weights.get("cost_score", w_cost)
        w_util = custom_weights.get("utilization_score", w_util)
        w_cap = custom_weights.get("capability_overlap_score", w_cap)
        w_life = custom_weights.get("lifecycle_score", w_life)
        w_crit = custom_weights.get("criticality_score", w_crit)
        total_w = w_cost + w_util + w_cap + w_life + w_crit
        if total_w > 0:
            w_cost /= total_w
            w_util /= total_w
            w_cap /= total_w
            w_life /= total_w
            w_crit /= total_w

    # Composite Rationalization Review Index (RRI)
    # Higher score = Stronger case for human architectural and financial review
    df["rationalization_review_index"] = (
        w_cost * df["cost_score"]
        + w_util * (100.0 - df["utilization_score"])  # low utilization increases review priority
        + w_cap * df["capability_overlap_score"]
        + w_life * df["lifecycle_score"]
        + w_crit * (100.0 - df["criticality_score"])  # lower criticality increases feasibility
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


def analyze_mcda_weight_sensitivity(
    weight_param: str = "cost_score",
    weight_range: Optional[List[float]] = None,
) -> pd.DataFrame:
    """Analyze rank and score sensitivity when varying one MCDA criterion weight.

    Varies the chosen weight across weight_range and renormalizes the other 4 weights,
    demonstrating the stability and governance rigor of the MCDA model.
    """
    if weight_range is None:
        weight_range = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60]

    base_weights = {
        "cost_score": 0.30,
        "utilization_score": 0.25,
        "capability_overlap_score": 0.20,
        "lifecycle_score": 0.15,
        "criticality_score": 0.10,
    }
    base_df = score_application_portfolio(base_weights)
    base_ranks = base_df.set_index("application_id")["rationalization_review_index"].rank(ascending=False)

    rows = []
    other_params = [k for k in base_weights if k != weight_param]
    sum_other_base = sum(base_weights[k] for k in other_params)

    for w_val in weight_range:
        current_weights = {weight_param: w_val}
        remaining_weight = max(0.0, 1.0 - w_val)
        for k in other_params:
            current_weights[k] = (base_weights[k] / sum_other_base) * remaining_weight if sum_other_base > 0 else 0

        sens_df = score_application_portfolio(current_weights)
        sens_df["sens_rank"] = sens_df["rationalization_review_index"].rank(ascending=False).astype(int)
        for _, row in sens_df.iterrows():
            app_id = row["application_id"]
            b_rank = int(base_ranks[app_id])
            s_rank = int(row["sens_rank"])
            rows.append({
                "application_id": app_id,
                "application_name": row["application_name"],
                "varied_parameter": weight_param,
                "weight_value": round(w_val, 2),
                "rationalization_review_index": row["rationalization_review_index"],
                "base_rank": b_rank,
                "sensitivity_rank": s_rank,
                "rank_shift": b_rank - s_rank,  # positive means moved higher up review queue
            })

    return pd.DataFrame(rows)


def evaluate_rationalization_pareto_frontier() -> pd.DataFrame:
    """Construct migration complexity vs savings Pareto frontier.

    Complexity factors:
    - Downstream dependent apps (in-degree)
    - Upstream service dependencies (out-degree)
    - Underlying technology count
    - Business criticality

    Returns all applications with migration_complexity_score, annual_avoidable_savings,
    and is_pareto_optimal status (non-dominated trade-offs).
    """
    db = get_database()
    app_tco = calculate_application_tco()

    dep_in = db.query_df("""
        SELECT target_app_id AS application_id, COUNT(DISTINCT source_app_id) AS inbound_dependents
        FROM rel_app_dependency
        GROUP BY target_app_id
    """)
    dep_out = db.query_df("""
        SELECT source_app_id AS application_id, COUNT(DISTINCT target_app_id) AS outbound_dependencies
        FROM rel_app_dependency
        GROUP BY source_app_id
    """)
    tech_cnt = db.query_df("""
        SELECT application_id, COUNT(DISTINCT technology_id) AS technology_count
        FROM rel_app_technology
        GROUP BY application_id
    """)

    df = app_tco.merge(dep_in, on="application_id", how="left")
    df = df.merge(dep_out, on="application_id", how="left")
    df = df.merge(tech_cnt, on="application_id", how="left").fillna(0)

    crit_mult = {
        "Mission Critical": 35.0,
        "Business Critical": 25.0,
        "Operational": 15.0,
        "Standard": 5.0,
    }
    crit_score = df["criticality"].map(crit_mult).fillna(15.0)

    # Complexity score (0-100)
    raw_complexity = (
        df["inbound_dependents"] * 15.0
        + df["outbound_dependencies"] * 10.0
        + df["technology_count"] * 10.0
        + crit_score
    )
    max_c = raw_complexity.max() if raw_complexity.max() > 0 else 1.0
    df["migration_complexity_score"] = ((raw_complexity / max_c) * 100.0).round(1)
    df["annual_avoidable_savings"] = df["annual_tco"]

    # Pareto optimality: non-dominated where (complexity <= other.complexity and savings >= other.savings)
    is_pareto = []
    coords = list(zip(df["migration_complexity_score"], df["annual_avoidable_savings"]))
    for i, (c_i, s_i) in enumerate(coords):
        dominated = False
        for j, (c_j, s_j) in enumerate(coords):
            if i != j:
                if (c_j <= c_i and s_j >= s_i) and (c_j < c_i or s_j > s_i):
                    dominated = True
                    break
        is_pareto.append(not dominated)
    df["is_pareto_optimal"] = is_pareto

    # Strategic Quadrant classification
    median_c = df["migration_complexity_score"].median()
    median_s = df["annual_avoidable_savings"].median()

    def classify_quadrant(row):
        c = row["migration_complexity_score"]
        s = row["annual_avoidable_savings"]
        if c <= median_c and s >= median_s:
            return "Quick Win (High Savings, Low Complexity)"
        elif c > median_c and s >= median_s:
            return "Strategic Heavyweight (High Savings, High Complexity)"
        elif c <= median_c and s < median_s:
            return "Low Value Drag (Low Savings, Low Complexity)"
        else:
            return "Complex Legacy Trapped (Low Savings, High Complexity)"

    df["strategic_quadrant"] = df.apply(classify_quadrant, axis=1)

    return df[[
        "application_id",
        "application_name",
        "lifecycle_status",
        "criticality",
        "migration_complexity_score",
        "annual_avoidable_savings",
        "is_pareto_optimal",
        "strategic_quadrant",
        "inbound_dependents",
        "outbound_dependencies",
        "technology_count",
    ]].sort_values(["is_pareto_optimal", "annual_avoidable_savings"], ascending=[False, False])


def generate_decommissioning_roadmap(
    target_app_ids: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Generate structured decommissioning milestones and financial run-rate unlock schedule.

    For selected rationalization candidates, computes phased operational gates:
    - Phase 1 (M1-M2): Architecture Decoupling & Read-Only Freeze
    - Phase 2 (M3-M4): Data Extraction, Archive & Legal Compliance Lock
    - Phase 3 (M5-M6): Vendor Notice, Host/VM & Storage Instance Teardown
    - Phase 4 (M7-M8): General Ledger De-allocation & Net Run-Rate Audit
    """
    candidates = find_rationalization_candidates()
    if target_app_ids:
        df = candidates[candidates["application_id"].isin(target_app_ids)]
    else:
        df = candidates.head(5)

    milestones_data = []
    for _, row in df.iterrows():
        app_id = row["application_id"]
        app_name = row["application_name"]
        tco = row["potential_avoidable_cost_scenario"]

        milestones = [
            {
                "application_id": app_id,
                "application_name": app_name,
                "phase_code": "M1",
                "phase_name": "Dependency Decoupling & Read-Only Freeze",
                "start_month": 1,
                "end_month": 2,
                "risk_rating": "Medium",
                "key_deliverables": "Reroute upstream API clients; snapshot master databases; set tenant read-only flag.",
                "cumulative_cost_unlocked_pct": 0.0,
                "monthly_runrate_unlocked": 0.0,
            },
            {
                "application_id": app_id,
                "application_name": app_name,
                "phase_code": "M2",
                "phase_name": "Data Extraction & Vault Archival",
                "start_month": 3,
                "end_month": 4,
                "risk_rating": "Low",
                "key_deliverables": "Extract historical cold audit logs to cold storage / Glacier; compliance signoff.",
                "cumulative_cost_unlocked_pct": 15.0,
                "monthly_runrate_unlocked": round((tco / 12) * 0.15, 2),
            },
            {
                "application_id": app_id,
                "application_name": app_name,
                "phase_code": "M3",
                "phase_name": "Contract Termination & Instance Teardown",
                "start_month": 5,
                "end_month": 6,
                "risk_rating": "High",
                "key_deliverables": "Terminate vendor SaaS seats; terminate hypervisors/EC2 instances; release static IPs.",
                "cumulative_cost_unlocked_pct": 75.0,
                "monthly_runrate_unlocked": round((tco / 12) * 0.75, 2),
            },
            {
                "application_id": app_id,
                "application_name": app_name,
                "phase_code": "M4",
                "phase_name": "GL De-allocation & Post-Audit Realization",
                "start_month": 7,
                "end_month": 8,
                "risk_rating": "Low",
                "key_deliverables": "Zero cost center chargeback in ERP; confirm post-decommissioning stability; TVR audit.",
                "cumulative_cost_unlocked_pct": 100.0,
                "monthly_runrate_unlocked": round(tco / 12, 2),
            },
        ]
        milestones_data.extend(milestones)

    return pd.DataFrame(milestones_data)


def model_contractual_exit_impact(
    application_id: str,
    contract_months_remaining: int = 6,
    penalty_rate: float = 0.50,
    fixed_overhead_fraction: float = 0.25,
) -> Dict[str, Any]:
    """Model net realizable financial impact of application decommissioning.

    Distinguishes:
    - Gross Avoidable TCO (Total headline cost)
    - Retained Shared Overhead (Platform/network/hypervisor overhead that does not evaporate: e.g. 25%)
    - Contract Early Termination Penalty (Remaining commit x penalty rate)
    - True Net Cash Realization Year 1 vs Run-rate Year 2+

    Consulting Guardrail:
    - Financial impacts are modeled as analytical scenarios acknowledging contract lock-in.
    """
    app_tco_df = calculate_application_tco()
    app_row = app_tco_df[app_tco_df["application_id"] == application_id]
    if app_row.empty:
        return {"error": f"Application '{application_id}' not found."}

    row = app_row.iloc[0]
    gross_annual_tco = float(row["annual_tco"])
    monthly_runrate = gross_annual_tco / 12.0

    # Retained overhead that cannot be eliminated
    retained_shared_overhead = gross_annual_tco * fixed_overhead_fraction

    # Variable avoidable portion before exit penalties
    avoidable_variable_spend = gross_annual_tco - retained_shared_overhead

    # Early termination fee on remaining software license / vendor commit
    remaining_vendor_commit = monthly_runrate * contract_months_remaining
    contract_exit_penalty = remaining_vendor_commit * penalty_rate

    # Net Year 1 savings accounts for penalty fee
    net_year1_savings = max(0.0, avoidable_variable_spend - contract_exit_penalty)

    # Net Run-rate Year 2+ savings (no more exit fee)
    net_runrate_savings_year2 = avoidable_variable_spend

    return {
        "application_id": application_id,
        "application_name": row["application_name"],
        "gross_annual_tco": round(gross_annual_tco, 2),
        "monthly_runrate": round(monthly_runrate, 2),
        "contract_months_remaining": contract_months_remaining,
        "early_termination_penalty": round(contract_exit_penalty, 2),
        "retained_shared_overhead": round(retained_shared_overhead, 2),
        "fixed_overhead_fraction": fixed_overhead_fraction,
        "net_year1_savings": round(net_year1_savings, 2),
        "net_runrate_savings_year2": round(net_runrate_savings_year2, 2),
        "year1_net_yield_pct": round((net_year1_savings / gross_annual_tco) * 100.0, 1),
        "analytical_disclaimer": "Scenario model: Shared fixed costs and contract penalties reduce gross headline TCO to true net realizable cash savings.",
    }
