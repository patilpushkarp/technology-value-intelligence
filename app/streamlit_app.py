"""Technology Value Intelligence (TVI) - Interactive Streamlit Application.

Local-first TBM / ITFM / Technology Value Realization prototype demonstrating
how Knowledge Graphs transform technology financial management and portfolio governance.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configure paths
app_dir = Path(__file__).resolve().parent
workspace_root = app_dir.parent
sys.path.insert(0, str(workspace_root / "src"))

from tvi.config import load_config, get_project_root
from tvi.database import get_database
from tvi.graph import build_knowledge_graph, get_focused_subgraph
from tvi.graph_queries import (
    find_business_units_by_vendor,
    find_capability_overlapping_apps,
    get_full_value_chain_path
)
from tvi.cost_analytics import (
    calculate_application_tco,
    calculate_capability_cost,
    calculate_service_cost,
    get_application_profile,
    get_capability_profile
)
from tvi.consumption_analytics import (
    analyze_consumption_quadrants,
    find_high_cost_low_utilization,
    analyze_unit_economics_trends
)
from tvi.rationalization import (
    score_application_portfolio,
    find_rationalization_candidates
)
from tvi.dependency import (
    get_application_dependencies,
    get_capability_dependencies,
    get_business_unit_dependencies
)
from tvi.value_realization import (
    calculate_project_budget_variance,
    calculate_benefit_realization,
    analyze_benefit_kpi_progression,
    get_project_value_profile
)
from tvi.variance import (
    calculate_monthly_cost_variance,
    identify_cost_drivers
)
from tvi.llm import KnowledgeGraphAnalyst
from tvi.reporting import generate_executive_report

# Streamlit Page Config
st.set_page_config(
    page_title="Technology Value Intelligence",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #555555;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        border-left: 4px solid #1f77b4;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #2b5c8f;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #666666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# Cache data loading
@st.cache_resource
def load_tvi_engine():
    cfg = load_config()
    db = get_database(cfg.database.path)
    # Ensure tables are loaded
    gen_dir = get_project_root() / "data" / "generated"
    if (gen_dir / "applications.csv").exists():
        db.load_csv_data(gen_dir)
    G = build_knowledge_graph(gen_dir)
    return cfg, db, G

cfg, db, G = load_tvi_engine()

# Sidebar Navigation
st.sidebar.image("https://img.icons8.com/color/96/network.png", width=64)
st.sidebar.title("TVI Navigation")
st.sidebar.caption("Technology Value Intelligence v1.0")

selected_view = st.sidebar.radio(
    "Select Intelligence Domain:",
    [
        "Executive Spend & Variance",
        "Business Capability Costing",
        "Application TCO & Unit Economics",
        "Consumption Quadrants",
        "Application Rationalization",
        "Graph Dependencies & Blast Radius",
        "Investment & Benefit Realization (TVR)",
        "AI Knowledge Graph Analyst",
        "Board Executive Report"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Target Hardware:** 16 GB RAM Local Machine")
st.sidebar.markdown("**Analytical Engine:** DuckDB (OLAP) + NetworkX (Graph)")
st.sidebar.markdown("**Deterministic Seed:** `42`")

# ==============================================================================
# 1. Executive Spend & Variance
# ==============================================================================
if selected_view == "Executive Spend & Variance":
    st.markdown("<div class='main-header'>Executive Technology Spend & Variance Intelligence</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Holistic enterprise expenditure, multi-tier taxonomy breakdown, and Month-over-Month variance decomposition.</div>", unsafe_allow_html=True)

    total_cost = db.get_total_cost()
    tco_df = calculate_application_tco()
    var_df = calculate_monthly_cost_variance()
    drivers = identify_cost_drivers()

    # KPI Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Total Annual Spend</div>
            <div class='metric-value'>₹{total_cost/1e7:,.2f} Cr</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Active Applications</div>
            <div class='metric-value'>{len(tco_df)}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        aug_shift = drivers['total_cost_delta']
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>August Shift (MoM)</div>
            <div class='metric-value' style='color: {"#d62728" if aug_shift > 0 else "#2ca02c"}'>₹{aug_shift/1e7:+.2f} Cr ({drivers['total_cost_delta_pct']:+.1f}%)</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        top_app = tco_df.iloc[0]
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Largest System Spend</div>
            <div class='metric-value'>{top_app['application_id']} (₹{top_app['annual_tco']/1e7:.1f} Cr)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c_left, c_right = st.columns([6, 5])
    with c_left:
        st.subheader("Monthly Technology Spend Trajectory")
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=var_df["month"],
            y=var_df["monthly_spend"] / 1e7,
            mode="lines+markers",
            name="Monthly Spend (₹ Cr)",
            line=dict(color="#1f77b4", width=3),
            marker=dict(size=8)
        ))
        fig_trend.update_layout(
            yaxis_title="Monthly Spend (₹ Crores)",
            template="plotly_white",
            height=360,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    with c_right:
        st.subheader("Cost Pool & Category Hierarchy")
        sunburst_query = """
            SELECT cost_pool, cost_category, s.service_name, SUM(c.amount) as spend
            FROM cost_records c
            JOIN it_services s ON c.service_id = s.service_id
            GROUP BY cost_pool, cost_category, s.service_name
        """
        sb_df = db.query_df(sunburst_query)
        fig_sb = px.sunburst(
            sb_df,
            path=["cost_pool", "cost_category", "service_name"],
            values="spend",
            color_continuous_scale="Blues"
        )
        fig_sb.update_layout(height=360, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_sb, use_container_width=True)

    st.subheader("August Spend Shift Waterfall (Root-Cause Driver Decomposition)")
    cat_var = drivers["top_category_drivers"]
    base_s = drivers["spend_baseline"] / 1e7
    comp_s = drivers["spend_comparison"] / 1e7

    x_names = ["July Spend"] + list(cat_var["cost_category"]) + ["August Spend"]
    measures = ["absolute"] + ["relative"] * len(cat_var) + ["total"]
    y_vals = [base_s] + list(cat_var["variance_amount"] / 1e7) + [comp_s]
    text_vals = [f"₹{base_s:.1f} Cr"] + [f"{v/1e7:+.2f} Cr" for v in cat_var["variance_amount"]] + [f"₹{comp_s:.1f} Cr"]

    fig_wf = go.Figure(go.Waterfall(
        name="August Variance",
        orientation="v",
        measure=measures,
        x=x_names,
        y=y_vals,
        text=text_vals,
        textposition="outside",
        decreasing=dict(marker=dict(color="#2ca02c")),
        increasing=dict(marker=dict(color="#d62728")),
        totals=dict(marker=dict(color="#1f77b4"))
    ))
    fig_wf.update_layout(template="plotly_white", height=380, margin=dict(l=20, r=20, t=30, b=20), yaxis_title="₹ Crores")
    st.plotly_chart(fig_wf, use_container_width=True)

# ==============================================================================
# 2. Business Capability Costing
# ==============================================================================
elif selected_view == "Business Capability Costing":
    st.markdown("<div class='main-header'>Business Capability Cost Intelligence</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Attributing direct application costs and transaction-proportional shared infrastructure without double-counting.</div>", unsafe_allow_html=True)

    cap_df = calculate_capability_cost()
    overlaps = find_capability_overlapping_apps(G)

    st.subheader("Enterprise Capabilities Ranked by Technology Cost")
    fig_cap = px.bar(
        cap_df.head(12),
        x="total_capability_cost",
        y="capability_name",
        orientation="h",
        color="criticality",
        hover_data={"direct_app_cost": ":,.0f", "shared_infra_allocated": ":,.0f", "supported_apps_count": True},
        title="Top 12 Capabilities by Total Technology Expenditure",
        labels={"total_capability_cost": "Total Cost (₹)", "capability_name": "Business Capability"},
        template="plotly_white",
        color_discrete_map={"Mission Critical": "#d62728", "Business Critical": "#1f77b4", "Operational": "#2ca02c", "Standard": "#7f7f7f"}
    )
    fig_cap.update_layout(yaxis=dict(autorange="reversed"), height=420)
    st.plotly_chart(fig_cap, use_container_width=True)

    col_a, col_b = st.columns([6, 5])
    with col_a:
        st.subheader("Capability Detail Dossier")
        selected_cap_name = st.selectbox("Select Business Capability to Inspect:", cap_df["capability_name"].tolist())
        sel_cap_id = cap_df[cap_df["capability_name"] == selected_cap_name]["capability_id"].values[0]
        profile = get_capability_profile(sel_cap_id)

        st.markdown(f"**Capability ID:** `{sel_cap_id}` | **Priority:** {profile['summary'].get('strategic_priority')} | **Criticality:** {profile['summary'].get('criticality')}")
        st.markdown(f"**Total Cost:** ₹{profile['summary'].get('total_capability_cost')/1e7:.2f} Cr (Direct: ₹{profile['summary'].get('direct_app_cost')/1e7:.2f} Cr | Shared Infra: ₹{profile['summary'].get('shared_infra_allocated')/1e7:.2f} Cr)")
        st.dataframe(profile["supporting_applications"], use_container_width=True)

    with col_b:
        st.subheader("Capability Redundancy Detector (Scenario C)")
        st.caption("Capabilities supported by 2+ distinct applications representing consolidation opportunities:")
        st.dataframe(overlaps[["capability_id", "capability_name", "application_count", "application_names"]], use_container_width=True)

# ==============================================================================
# 3. Application TCO & Unit Economics
# ==============================================================================
elif selected_view == "Application TCO & Unit Economics":
    st.markdown("<div class='main-header'>Application TCO & Unit Economics</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Evaluating fully-burdened cost stacks, cost per active user, and cost per digital transaction.</div>", unsafe_allow_html=True)

    app_tco_df = calculate_application_tco()

    col1, col2 = st.columns([7, 5])
    with col1:
        st.subheader("Spend vs Adoption (Bubble Size = Annual Cost / User)")
        fig_scatter = px.scatter(
            app_tco_df,
            x="avg_monthly_users",
            y="annual_tco",
            size="annual_cost_per_user",
            color="lifecycle_status",
            hover_name="application_name",
            hover_data={"application_id": True, "annual_tco": ":,.0f", "avg_monthly_users": ":.0f", "annual_cost_per_user": ":,.2f", "cost_per_transaction": ":.4f"},
            labels={"avg_monthly_users": "Active Monthly Users", "annual_tco": "Annual TCO (₹)"},
            template="plotly_white",
            color_discrete_map={"Strategic": "#2ca02c", "Tolerate": "#ff7f0e", "Migrate": "#1f77b4", "Retire": "#d62728"}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col2:
        st.subheader("Pareto 80/20 Spend Concentration")
        top_apps = app_tco_df.head(10)
        fig_pareto = go.Figure()
        fig_pareto.add_trace(go.Bar(
            x=top_apps["application_id"],
            y=top_apps["annual_tco"] / 1e7,
            name="Spend (₹ Cr)",
            marker_color="#1f77b4"
        ))
        fig_pareto.add_trace(go.Scatter(
            x=top_apps["application_id"],
            y=top_apps["cumulative_spend_pct"],
            name="Cumulative Spend %",
            yaxis="y2",
            line=dict(color="#d62728", width=2.5),
            marker=dict(size=6)
        ))
        fig_pareto.update_layout(
            template="plotly_white",
            yaxis=dict(title="Annual TCO (₹ Cr)"),
            yaxis2=dict(title="Cumulative %", overlaying="y", side="right", range=[0, 100]),
            height=380,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_pareto, use_container_width=True)

    st.subheader("Full Application Cost Intelligence Dossier")
    st.dataframe(app_tco_df[["application_id", "application_name", "lifecycle_status", "criticality", "annual_tco", "avg_monthly_users", "annual_cost_per_user", "cost_per_transaction", "cumulative_spend_pct"]], use_container_width=True)

# ==============================================================================
# 4. Consumption Quadrants
# ==============================================================================
elif selected_view == "Consumption Quadrants":
    st.markdown("<div class='main-header'>Technology Consumption Quadrants</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Objective median-split quadrant matrix classifying applications by spend burden vs operational adoption.</div>", unsafe_allow_html=True)

    quad_df = analyze_consumption_quadrants()
    med_c = quad_df["annual_tco"].median()
    med_u = quad_df["avg_monthly_users"].median()

    fig_quad = px.scatter(
        quad_df,
        x="avg_monthly_users",
        y="annual_tco",
        color="consumption_quadrant",
        size="annual_cost_per_user",
        hover_name="application_name",
        hover_data={"application_id": True, "annual_tco": ":,.0f", "avg_monthly_users": ":.0f", "consumption_quadrant": True},
        title="Portfolio Consumption Quadrants (Median Splits)",
        labels={"avg_monthly_users": "Active Monthly Users", "annual_tco": "Annual TCO (₹)"},
        template="plotly_white",
        color_discrete_map={
            "High Cost / High Utilization (Scale Anchor)": "#1f77b4",
            "High Cost / Low Utilization (Investigate for Rationalization)": "#d62728",
            "Low Cost / High Utilization (High Efficiency Workhorse)": "#2ca02c",
            "Low Cost / Low Utilization (Niche Utility)": "#7f7f7f"
        }
    )
    fig_quad.add_hline(y=med_c, line_dash="dash", line_color="grey", annotation_text=f"Median Spend (₹{med_c/1e7:.1f} Cr)")
    fig_quad.add_vline(x=med_u, line_dash="dot", line_color="grey", annotation_text=f"Median Users ({med_u:.0f})")
    fig_quad.update_layout(height=480)
    st.plotly_chart(fig_quad, use_container_width=True)

    st.subheader("Applications Flagged in 'High Cost / Low Utilization' Quadrant (Immediate Review)")
    inv_df = find_high_cost_low_utilization(cost_percentile=0.55, utilization_percentile=0.45)
    st.dataframe(inv_df[["application_id", "application_name", "lifecycle_status", "annual_tco", "avg_monthly_users", "annual_cost_per_user", "investigation_flag"]], use_container_width=True)

# ==============================================================================
# 5. Application Rationalization
# ==============================================================================
elif selected_view == "Application Rationalization":
    st.markdown("<div class='main-header'>Application Rationalization & Review Index (RRI)</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Transparent, multi-criteria decision analysis prioritizing systems for decommissioning review without subjective bias.</div>", unsafe_allow_html=True)

    rri_threshold = st.slider("Select Rationalization Review Threshold (RRI):", min_value=30.0, max_value=80.0, value=55.0, step=5.0)
    candidates = find_rationalization_candidates(review_threshold=rri_threshold)

    st.subheader(f"Candidates Flagged for Rationalization Review ({len(candidates)} systems)")
    st.caption("Guardrail Notice: Avoidable costs represent current baseline expenditure scenarios, not guaranteed cash savings.")
    st.dataframe(candidates, use_container_width=True)

    scored_portfolio = score_application_portfolio()
    st.subheader("Gartner TIME Matrix Overlay")
    fig_time = px.scatter(
        scored_portfolio,
        x="utilization_score",
        y="cost_score",
        color="lifecycle_status",
        size="rationalization_review_index",
        hover_name="application_name",
        hover_data={"application_id": True, "annual_tco": ":,.0f", "rationalization_review_index": True},
        title="Gartner TIME / TBM Rationalization Matrix",
        labels={"utilization_score": "Business Fit / Utilization Score (0-100)", "cost_score": "Financial Burden / Cost Score (0-100)"},
        template="plotly_white",
        color_discrete_map={"Strategic": "#2ca02c", "Tolerate": "#ff7f0e", "Migrate": "#1f77b4", "Retire": "#d62728"}
    )
    fig_time.add_hline(y=50, line_dash="dash", line_color="grey")
    fig_time.add_vline(x=50, line_dash="dash", line_color="grey")
    fig_time.update_layout(height=440)
    st.plotly_chart(fig_time, use_container_width=True)

# ==============================================================================
# 6. Graph Dependencies & Blast Radius
# ==============================================================================
elif selected_view == "Graph Dependencies & Blast Radius":
    st.markdown("<div class='main-header'>Knowledge Graph Topology & Blast Radius Intelligence</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Tracing direct vs transitive application dependencies to safeguard against unintended decommissioning blast radius.</div>", unsafe_allow_html=True)

    app_list = sorted([n for n, d in G.nodes(data=True) if d.get("entity_type") == "Application"])
    selected_app = st.selectbox("Select Application to Interrogate:", app_list, index=app_list.index("APP010") if "APP010" in app_list else 0)

    dep_dossier = get_application_dependencies(selected_app, G)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Blast Radius Metric", dep_dossier["blast_radius_metric"])
    with col2:
        st.metric("Direct Inbound Dependents", len(dep_dossier["direct_dependent_apps"]))
    with col3:
        st.metric("Indirect Transitive Dependents", len(dep_dossier["indirect_dependent_apps"]))
    with col4:
        st.metric("Impacted Business Units", len(dep_dossier["business_units"]))

    st.subheader(f"Dependency Lineage for {selected_app} ({dep_dossier['application_name']})")
    c_d1, c_d2 = st.columns(2)
    with c_d1:
        st.markdown("**Direct Dependent Applications (Would be disrupted):**")
        if dep_dossier["direct_dependent_apps"]:
            st.dataframe(pd.DataFrame(dep_dossier["direct_dependent_apps"]), use_container_width=True)
        else:
            st.info("Zero direct inbound dependents (Leaf node).")

        st.markdown("**Capabilities Supported:**")
        st.dataframe(pd.DataFrame(dep_dossier["capabilities"]), use_container_width=True)

    with c_d2:
        st.markdown("**Impacted Consuming Business Units:**")
        st.dataframe(pd.DataFrame(dep_dossier["business_units"]), use_container_width=True)

        st.markdown("**Underlying Technologies:**")
        st.dataframe(pd.DataFrame(dep_dossier["technologies"]), use_container_width=True)

# ==============================================================================
# 7. Investment & Benefit Realization (TVR)
# ==============================================================================
elif selected_view == "Investment & Benefit Realization (TVR)":
    st.markdown("<div class='main-header'>Technology Value Realization (TVR)</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Bridging discretionary transformation investments to realized benefits and measurable KPI progression.</div>", unsafe_allow_html=True)

    budget_df = calculate_project_budget_variance()
    benefit_df = calculate_benefit_realization()
    tvr_merged = budget_df.merge(benefit_df[["project_id", "total_expected_benefit", "total_realized_benefit", "benefit_realization_pct", "benefit_gap"]], on="project_id")

    st.subheader("Transformation Investment Performance Portfolio")
    st.dataframe(tvr_merged[["project_id", "project_name", "project_type", "investment_budget", "actual_spend", "budget_variance", "total_expected_benefit", "total_realized_benefit", "benefit_realization_pct", "benefit_gap"]], use_container_width=True)

    c_wf, c_kpi = st.columns([6, 5])
    with c_wf:
        st.subheader("Portfolio Benefit Realization Waterfall")
        tot_exp = tvr_merged["total_expected_benefit"].sum() / 1e7
        tot_rel = tvr_merged["total_realized_benefit"].sum() / 1e7
        tot_gap = tot_exp - tot_rel

        fig_tvr_wf = go.Figure(go.Waterfall(
            orientation="v",
            measure=["relative", "relative", "total"],
            x=["Expected Annual Benefits", "Unrealized Benefit Gap", "Net Realized Benefits"],
            text=[f"₹{tot_exp:.1f} Cr", f"-₹{tot_gap:.1f} Cr", f"₹{tot_rel:.1f} Cr"],
            y=[tot_exp, -tot_gap, tot_rel],
            textposition="outside",
            decreasing=dict(marker=dict(color="#d62728")),
            increasing=dict(marker=dict(color="#2ca02c")),
            totals=dict(marker=dict(color="#1f77b4"))
        ))
        fig_tvr_wf.update_layout(template="plotly_white", height=380, yaxis_title="₹ Crores")
        st.plotly_chart(fig_tvr_wf, use_container_width=True)

    with c_kpi:
        st.subheader("Targeted KPI Progression")
        kpi_prog = analyze_benefit_kpi_progression()
        st.dataframe(kpi_prog[["project_id", "benefit_type", "kpi_name", "baseline_value", "target_value", "actual_value", "unit", "kpi_target_achievement_pct"]].head(8), use_container_width=True)

# ==============================================================================
# 8. AI Knowledge Graph Analyst
# ==============================================================================
elif selected_view == "AI Knowledge Graph Analyst":
    st.markdown("<div class='main-header'>AI Knowledge Graph Analyst (Natural Language Console)</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Safe natural language queries mapped to validated analytical functions with zero arbitrary code execution.</div>", unsafe_allow_html=True)

    analyst = KnowledgeGraphAnalyst(mode="rules", config=cfg)
    ollama_ok = analyst.is_ollama_available()

    col_m1, col_m2 = st.columns([8, 4])
    with col_m1:
        sample_q = st.selectbox(
            "Select or Type an Executive Question:",
            [
                "What is the cost of the Order-to-Cash capability?",
                "Which applications have high cost and low utilization?",
                "What depends on APP010?",
                "What is the blast radius of APP021?",
                "Why did spend increase in August?",
                "What benefits were expected from PRJ014?",
                "What is the cost of APP001?",
                "Which business units depend on technology supplied by TechNova?"
            ]
        )
    with col_m2:
        st.markdown(f"**Execution Mode:** Rules Mode (Deterministic)")
        st.caption(f"Local Ollama Status: {'🟢 Active' if ollama_ok else '⚪ Offline (Rules Fallback)'}")

    user_query = st.text_input("Enter Custom Query:", value=sample_q)

    if st.button("Analyze with Knowledge Graph", type="primary"):
        with st.spinner("Executing Graph and Analytical Query..."):
            res = analyst.query(user_query)

        # 1. Analyst Grounded Explanation
        st.markdown("### Analyst Grounded Explanation")
        st.info(res["explanation"])

        # 2. Executive Query Metadata & Intent Mapping (User-Friendly Cards)
        st.markdown("### Executive Query & Execution Profile")
        intent = res.get("intent", "UNKNOWN")
        params = res.get("params", {})
        status = res.get("status", "SUCCESS")
        mode = res.get("mode", analyst.mode)

        intent_labels = {
            "COST_VARIANCE_DRIVERS": "Cost Variance & Spend Shift Drivers",
            "VENDOR_DEPENDENCY": "Vendor Multi-Hop Lineage",
            "APPLICATION_COST": "Application TCO Profile",
            "CAPABILITY_COST": "Business Capability Costing",
            "APPLICATION_DEPENDENCY": "Application Blast Radius & Lineage",
            "CAPABILITY_DEPENDENCY": "Capability Dependency Structure",
            "RATIONALIZATION_CANDIDATES": "Application Rationalization Review",
            "PROJECT_VALUE_PROFILE": "Project Value & Investment Profile",
            "PROJECT_BENEFIT_REALIZATION": "Portfolio Benefit Realization",
            "UNKNOWN": "Clarification / Unmapped Query"
        }

        if params:
            param_str = ", ".join(f"{k.replace('_', ' ').title()}: {v}" for k, v in params.items())
        else:
            param_str = "None (Portfolio-wide)"

        meta_c1, meta_c2, meta_c3, meta_c4 = st.columns(4)
        with meta_c1:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Identified Intent</div>
                <div class='metric-value' style='font-size: 1.05rem;'>{intent_labels.get(intent, intent)}</div>
            </div>
            """, unsafe_allow_html=True)
        with meta_c2:
            status_icon = "🟢" if status == "SUCCESS" else "🟡"
            status_text = "Verified Grounding" if status == "SUCCESS" else "Clarification Needed"
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Verification Status</div>
                <div class='metric-value' style='font-size: 1.05rem;'>{status_icon} {status_text}</div>
            </div>
            """, unsafe_allow_html=True)
        with meta_c3:
            mode_label = "Deterministic Rules Engine" if mode == "rules" else "Local Ollama LLM"
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Analytical Engine</div>
                <div class='metric-value' style='font-size: 1.05rem;'>⚙️ {mode_label}</div>
            </div>
            """, unsafe_allow_html=True)
        with meta_c4:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Target Parameters</div>
                <div class='metric-value' style='font-size: 1.05rem;'>{param_str}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 3. Structured Analytical Result (Executive Presentation)
        s_data = res.get("structured_result")
        if s_data is not None:
            st.markdown("### Structured Analytical Dossier")

            if intent == "COST_VARIANCE_DRIVERS" and isinstance(s_data, dict):
                b_month = s_data.get("baseline_month", "2024-07")
                c_month = s_data.get("comparison_month", "2024-08")
                spend_b = s_data.get("spend_baseline", 0) / 1e7
                spend_c = s_data.get("spend_comparison", 0) / 1e7
                delta = s_data.get("total_cost_delta", 0) / 1e7
                delta_pct = s_data.get("total_cost_delta_pct", 0)

                vk1, vk2, vk3, vk4 = st.columns(4)
                with vk1:
                    st.metric(label=f"Baseline Spend ({b_month})", value=f"₹{spend_b:,.2f} Cr")
                with vk2:
                    st.metric(label=f"Comparison Spend ({c_month})", value=f"₹{spend_c:,.2f} Cr")
                with vk3:
                    st.metric(label="Month-over-Month Delta", value=f"₹{delta:+.2f} Cr", delta=f"{delta_pct:+.1f}%", delta_color="inverse")
                with vk4:
                    st.metric(label="Primary Shift Root Cause", value="Software & Cloud Scale")

                st.markdown("<br>", unsafe_allow_html=True)
                tab_cat, tab_app = st.tabs(["📊 Cost Category Drivers", "💻 Application Shift Drivers & Diagnosis"])

                with tab_cat:
                    cat_df = s_data.get("top_category_drivers")
                    if isinstance(cat_df, pd.DataFrame) and not cat_df.empty:
                        disp_cat = cat_df.copy()
                        for c in ["spend_baseline", "spend_comparison", "variance_amount"]:
                            if c in disp_cat.columns:
                                disp_cat[c] = disp_cat[c].apply(lambda x: f"₹{x/1e7:,.2f} Cr" if pd.notnull(x) else "-")
                        if "variance_pct" in disp_cat.columns:
                            disp_cat["variance_pct"] = disp_cat["variance_pct"].apply(lambda x: f"{x:+.1f}%" if pd.notnull(x) else "-")
                        st.dataframe(disp_cat, use_container_width=True)

                with tab_app:
                    app_df = s_data.get("top_application_drivers")
                    if isinstance(app_df, pd.DataFrame) and not app_df.empty:
                        disp_app = app_df.copy()
                        for c in ["spend_baseline", "spend_comparison", "cost_delta"]:
                            if c in disp_app.columns:
                                disp_app[c] = disp_app[c].apply(lambda x: f"₹{x/1e7:,.2f} Cr" if pd.notnull(x) else "-")
                        for c in ["cost_delta_pct", "txn_growth_pct"]:
                            if c in disp_app.columns:
                                disp_app[c] = disp_app[c].apply(lambda x: f"{x:+.1f}%" if pd.notnull(x) else "-")
                        st.dataframe(disp_app, use_container_width=True)

            elif intent == "VENDOR_DEPENDENCY" and isinstance(s_data, list):
                if s_data:
                    df_vendor = pd.DataFrame(s_data)
                    v_name = df_vendor["vendor_name"].iloc[0] if "vendor_name" in df_vendor.columns else "Vendor"
                    n_bu = df_vendor["business_unit_name"].nunique() if "business_unit_name" in df_vendor.columns else len(df_vendor)
                    n_app = df_vendor["application_name"].nunique() if "application_name" in df_vendor.columns else 0

                    vk1, vk2, vk3, vk4 = st.columns(4)
                    with vk1:
                        st.metric("Vendor Evaluated", v_name)
                    with vk2:
                        st.metric("Consuming Business Units", f"{n_bu} Units")
                    with vk3:
                        st.metric("Dependent Applications", f"{n_app} Systems")
                    with vk4:
                        st.metric("Value Chain Connections", f"{len(df_vendor)} Paths")

                    st.markdown("<br>", unsafe_allow_html=True)
                    st.subheader(f"Multi-Hop Value Chain Lineage ({v_name})")
                    cols_order = [c for c in ["vendor_name", "technology_name", "application_name", "capability_name", "business_unit_name"] if c in df_vendor.columns]
                    st.dataframe(df_vendor[cols_order] if cols_order else df_vendor, use_container_width=True)
                else:
                    st.info("No dependency records found for this vendor in the knowledge graph.")

            elif intent == "APPLICATION_COST" and isinstance(s_data, dict):
                summ = s_data.get("summary", {})
                ak1, ak2, ak3, ak4 = st.columns(4)
                with ak1:
                    st.metric("Annual TCO", f"₹{summ.get('annual_tco', 0)/1e7:.2f} Cr")
                with ak2:
                    st.metric("Monthly Active Users", f"{summ.get('avg_monthly_users', 0):,.0f}")
                with ak3:
                    st.metric("Annual Cost / User", f"₹{summ.get('annual_cost_per_user', 0):,.2f}")
                with ak4:
                    st.metric("Cost / Transaction", f"₹{summ.get('cost_per_transaction', 0):.4f}")

                st.markdown("<br>", unsafe_allow_html=True)
                app_tabs = st.tabs(["🗓️ Monthly Cost History", "🏢 Supported Capabilities", "👥 Consuming Business Units"])
                with app_tabs[0]:
                    if isinstance(s_data.get("monthly_cost"), pd.DataFrame):
                        st.dataframe(s_data["monthly_cost"], use_container_width=True)
                with app_tabs[1]:
                    if isinstance(s_data.get("capabilities"), pd.DataFrame):
                        st.dataframe(s_data["capabilities"], use_container_width=True)
                with app_tabs[2]:
                    if isinstance(s_data.get("consuming_business_units"), pd.DataFrame):
                        st.dataframe(s_data["consuming_business_units"], use_container_width=True)

            elif intent == "CAPABILITY_COST" and isinstance(s_data, dict):
                summ = s_data.get("summary", {})
                ck1, ck2, ck3, ck4 = st.columns(4)
                with ck1:
                    st.metric("Total Capability Cost", f"₹{summ.get('total_capability_cost', 0)/1e7:.2f} Cr")
                with ck2:
                    st.metric("Direct Application Cost", f"₹{summ.get('direct_app_cost', 0)/1e7:.2f} Cr")
                with ck3:
                    st.metric("Shared Infra Allocated", f"₹{summ.get('shared_infra_allocated', 0)/1e7:.2f} Cr")
                with ck4:
                    st.metric("Supporting Applications", f"{summ.get('supported_apps_count', 0)} Systems")

                st.markdown("<br>", unsafe_allow_html=True)
                cap_tabs = st.tabs(["💻 Supporting Applications", "🏢 Owning Business Units"])
                with cap_tabs[0]:
                    if isinstance(s_data.get("supporting_applications"), pd.DataFrame):
                        st.dataframe(s_data["supporting_applications"], use_container_width=True)
                with cap_tabs[1]:
                    if isinstance(s_data.get("owning_business_units"), pd.DataFrame):
                        st.dataframe(s_data["owning_business_units"], use_container_width=True)

            elif intent == "APPLICATION_DEPENDENCY" and isinstance(s_data, dict):
                dk1, dk2, dk3, dk4 = st.columns(4)
                with dk1:
                    st.metric("Blast Radius Metric", s_data.get("blast_radius_metric", 0))
                with dk2:
                    st.metric("Direct Dependents", len(s_data.get("direct_dependent_apps", [])))
                with dk3:
                    st.metric("Indirect Transitive Dependents", len(s_data.get("indirect_dependent_apps", [])))
                with dk4:
                    st.metric("Impacted Business Units", len(s_data.get("business_units", [])))

                st.markdown("<br>", unsafe_allow_html=True)
                dep_tabs = st.tabs(["⚠️ Direct Inbound Dependents", "🌐 Transitive Dependents", "🏢 Consuming Business Units"])
                with dep_tabs[0]:
                    if s_data.get("direct_dependent_apps"):
                        st.dataframe(pd.DataFrame(s_data["direct_dependent_apps"]), use_container_width=True)
                    else:
                        st.info("Zero direct inbound dependents (Safe leaf node).")
                with dep_tabs[1]:
                    if s_data.get("indirect_dependent_apps"):
                        st.dataframe(pd.DataFrame(s_data["indirect_dependent_apps"]), use_container_width=True)
                    else:
                        st.info("Zero indirect transitive dependents.")
                with dep_tabs[2]:
                    if s_data.get("business_units"):
                        st.dataframe(pd.DataFrame(s_data["business_units"]), use_container_width=True)

            elif intent == "PROJECT_VALUE_PROFILE" and isinstance(s_data, dict):
                prj = s_data.get("project", {})
                pk1, pk2, pk3, pk4 = st.columns(4)
                with pk1:
                    st.metric("Investment Budget", f"₹{prj.get('investment_budget', 0)/1e7:.2f} Cr")
                with pk2:
                    st.metric("Actual Spend", f"₹{prj.get('actual_spend', 0)/1e7:.2f} Cr")
                with pk3:
                    st.metric("Budget Variance", f"₹{prj.get('budget_variance', 0)/1e7:+.2f} Cr")
                with pk4:
                    st.metric("Expected Annual Benefit", f"₹{prj.get('expected_annual_benefit', 0)/1e7:.2f} Cr")

                st.markdown("<br>", unsafe_allow_html=True)
                prj_tabs = st.tabs(["💰 Targeted Benefits", "📈 Benefit KPI Progression"])
                with prj_tabs[0]:
                    if isinstance(s_data.get("benefits"), pd.DataFrame):
                        st.dataframe(s_data["benefits"], use_container_width=True)
                with prj_tabs[1]:
                    if isinstance(s_data.get("kpis"), pd.DataFrame):
                        st.dataframe(s_data["kpis"], use_container_width=True)

            elif isinstance(s_data, pd.DataFrame):
                st.dataframe(s_data, use_container_width=True)

            elif isinstance(s_data, list):
                if len(s_data) > 0:
                    st.dataframe(pd.DataFrame(s_data), use_container_width=True)
                else:
                    st.info("No matching records found in knowledge graph.")

            elif isinstance(s_data, dict):
                scalar_dict = {k: v for k, v in s_data.items() if not isinstance(v, (pd.DataFrame, list, dict))}
                if scalar_dict:
                    st.dataframe(pd.DataFrame(list(scalar_dict.items()), columns=["Metric / Field", "Value"]), use_container_width=True)
                for k, v in s_data.items():
                    if isinstance(v, pd.DataFrame):
                        st.subheader(k.replace('_', ' ').title())
                        st.dataframe(v, use_container_width=True)
                    elif isinstance(v, list) and v:
                        st.subheader(k.replace('_', ' ').title())
                        st.dataframe(pd.DataFrame(v), use_container_width=True)

            # Collapsible Technical View
            with st.expander("🛠️ Technical / Developer Details (Raw Payload)"):
                st.json({
                    "detected_intent": intent,
                    "parameters": params,
                    "status": status,
                    "mode": mode,
                    "raw_result": {k: (v.to_dict(orient="records") if isinstance(v, pd.DataFrame) else v) for k, v in s_data.items()} if isinstance(s_data, dict) else s_data
                })

# ==============================================================================
# 9. Board Executive Report
# ==============================================================================
elif selected_view == "Board Executive Report":
    st.markdown("<div class='main-header'>Board-Level Executive Report</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Formal 9-section synthesized Technology Value Intelligence dossier for the CIO and CFO.</div>", unsafe_allow_html=True)

    report_md = generate_executive_report()
    st.markdown(report_md)

    st.download_button(
        label="Download Executive Report (Markdown)",
        data=report_md,
        file_name="TVI_Executive_Report_FY2024.md",
        mime="text/markdown"
    )
