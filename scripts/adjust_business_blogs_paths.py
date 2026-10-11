"""Script to adjust business blogs with Executive Reading Paths and updated technical companion links."""

import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
BIZ_DIR = BASE_DIR / "blog" / "business"

# The 4 Executive Reading Paths
PATHS = {
    "CFO": {
        "name": "CFO & Corporate Controller Track",
        "icon": "💼",
        "desc": "Focuses on financial mass balance, zero reconciliation, fully-burdened TCO, FinOps unit economics, decommissioning economics, Price-Volume-Mix variance, and boardroom governance.",
        "sequence": ["01b", "02a", "02b", "04a", "04b", "05a", "07b", "09a", "10a", "12b"]
    },
    "CIO": {
        "name": "CIO & Technology Executive Track",
        "icon": "💻",
        "desc": "Focuses on enterprise digital twins, IT spend pathologies, graph intelligence, rationalization (TIME), transitive blast radius, single points of failure, grounded enterprise AI, and the unified value chain.",
        "sequence": ["01a", "01b", "03a", "03b", "07a", "08a", "08b", "11a", "11b", "12a", "12b"]
    },
    "LOB": {
        "name": "Business Unit President & Product Executive Track",
        "icon": "📈",
        "desc": "Focuses on capability costing, workhorse vs zombie systems, unmasking software redundancy, 2x2 utilization matrices, digital transformation case studies (Payments vs CRM), and technology value realization.",
        "sequence": ["01a", "04b", "05a", "05b", "06a", "07a", "09a", "09b", "12a"]
    },
    "FINOPS": {
        "name": "FinOps Director & Cloud Governance Track",
        "icon": "⚡",
        "desc": "Focuses on tech spend pathologies, fully-burdened TCO, consumption quadrants, elasticity & GreenOps, decommissioning playbooks, Price-Volume-Mix variance, algorithmic SLA clawbacks, and on-premise AI.",
        "sequence": ["01b", "04a", "04b", "06a", "06b", "07b", "10a", "10b", "11a"]
    }
}

# Accurate companion technical guides mapping
TECH_MAPPING = {
    "01a": ("01a_tbm_foundations_and_synthetic_enterprise_modeling.md", "TBM Foundations & Synthetic Enterprise Modeling"),
    "01b": ("01b_statistical_distributions_and_heavy_tailed_telemetry.md", "Statistical Distributions & Heavy-Tailed Telemetry"),
    "02a": ("02a_tbm_taxonomy_and_relational_accounting_foundations.md", "TBM Taxonomy & Relational Accounting Foundations"),
    "02b": ("02c_zero_reconciliation_financial_proof_and_parquet_storage.md", "Zero-Reconciliation Financial Proof & Parquet Storage"),
    "03a": ("03a_graph_theory_foundations_for_enterprise_architecture.md", "Graph Theory Foundations for Enterprise Architecture"),
    "03b": ("03c_topological_metrics_centrality_and_multi_hop_traversal.md", "Topological Metrics, Centrality & Multi-Hop Traversal"),
    "04a": ("04a_activity_based_costing_and_the_five_layer_cost_stack.md", "Activity-Based Costing & The Five-Layer Cost Stack"),
    "04b": ("04b_unit_economics_and_marginal_cost_modeling.md", "Unit Economics & Marginal Cost Modeling"),
    "05a": ("05a_business_capability_modeling_and_enterprise_lineage.md", "Business Capability Modeling & Enterprise Lineage"),
    "05b": ("05c_capability_redundancy_quantification_and_sankey_value_flows.md", "Capability Redundancy Quantification & Sankey Value Flows"),
    "06a": ("06b_quadrant_segmentation_and_multivariate_clustering.md", "Quadrant Segmentation & Multivariate Clustering"),
    "06b": ("06c_elasticity_analysis_greenops_and_rightsizing_math.md", "Elasticity Analysis, GreenOps & Rightsizing Math"),
    "07a": ("07a_portfolio_rationalization_and_the_gartner_time_framework.md", "Portfolio Rationalization & The Gartner TIME Framework"),
    "07b": ("07d_decommissioning_runbooks_contract_penalties_and_exit_models.md", "Decommissioning Runbooks, Contract Penalties & Exit Models"),
    "08a": ("08b_transitive_closure_and_blast_radius_computation.md", "Transitive Closure & Blast Radius Computation"),
    "08b": ("08c_single_points_of_failure_and_cascade_failure_simulation.md", "Single Points of Failure & Cascade Failure Simulation"),
    "09a": ("09a_beyond_project_accounting_the_tvr_philosophy.md", "Beyond Project Accounting: The TVR Philosophy"),
    "09b": ("09b_benefit_realization_waterfalls_and_gap_quantification.md", "Benefit Realization Waterfalls & Gap Quantification"),
    "10a": ("10a_price_volume_mix_variance_decomposition.md", "Price-Volume-Mix (PVM) Variance Decomposition"),
    "10b": ("10c_statistical_anomaly_detection_z_scores_and_isolation_forests.md", "Statistical Anomaly Detection: Z-Scores & Isolation Forests"),
    "11a": ("11a_the_dual_mode_ai_architecture_deterministic_vs_probabilistic.md", "The Dual-Mode AI Architecture: Deterministic vs Probabilistic"),
    "11b": ("11d_security_prompt_injection_defense_and_hallucination_benchmarks.md", "Security, Prompt Injection Defense & Hallucination Benchmarks"),
    "12a": ("12a_the_unified_technology_value_chain_architecture.md", "The Unified Technology Value Chain Architecture"),
    "12b": ("12c_the_cio_cfo_executive_decision_matrix.md", "The CIO / CFO Executive Decision Matrix")
}

TITLE_LOOKUP = {
    "01a": "Enterprise IT Digital Twins",
    "01b": "The 8 Pathologies of Enterprise Tech Spend",
    "02a": "From GL Invoices to Business Capabilities",
    "02b": "Zero-Reconciliation Financial Truth",
    "03a": "Why Spreadsheets Fail and Graphs Win",
    "03b": "The Enterprise Nervous System",
    "04a": "Demystifying Fully-Burdened Application TCO",
    "04b": "Workhorses vs Zombie Systems",
    "05a": "What Does a Business Capability Actually Cost?",
    "05b": "Unmasking the Redundancy Trap",
    "06a": "The 2x2 Utilization Quadrant Matrix",
    "06b": "Elasticity and Sustainable GreenOps",
    "07a": "Objective Portfolio Pruning (MCDA & TIME)",
    "07b": "The Pragmatic Decommissioning Playbook",
    "08a": "The Domino Effect (Transitive Blast Radius)",
    "08b": "Single Points of Failure and Resilience",
    "09a": "Beyond On-Time and On-Budget (TVR)",
    "09b": "A Tale of Two Transformations: Payments vs CRM",
    "10a": "Why Did Our IT Bill Spike? (PVM Variance)",
    "10b": "Algorithmic Governance, Anomalies & SLA Credits",
    "11a": "Chatting with the Enterprise: Grounded AI",
    "11b": "Zero-Hallucination On-Premise Intelligence",
    "12a": "The Unified Technology Value Chain",
    "12b": "The CIO-CFO Executive Board Playbook"
}

def get_article_filename(code: str) -> str:
    for f in os.listdir(BIZ_DIR):
        if f.startswith(code + "_"):
            return f
    return ""

def update_business_blogs():
    print("Adjusting all 24 business blogs with Executive Reading Paths and verified companion links...")
    
    for code, (tech_file, tech_title) in TECH_MAPPING.items():
        fname = get_article_filename(code)
        if not fname:
            continue
        filepath = BIZ_DIR / fname
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # 1. Update frontmatter technical_companion
        content = re.sub(
            r'technical_companion:\s*\"[^\"]+\"',
            f'technical_companion: \"../technical/{tech_file}\"',
            content
        )

        # 2. Build the Executive Track Navigation Callout
        tracks_in_article = []
        for pkey, pdata in PATHS.items():
            if code in pdata["sequence"]:
                idx = pdata["sequence"].index(code) + 1
                total = len(pdata["sequence"])
                # previous and next in sequence
                prev_code = pdata["sequence"][idx - 2] if idx > 1 else None
                next_code = pdata["sequence"][idx] if idx < total else None
                tracks_in_article.append({
                    "key": pkey,
                    "name": pdata["name"],
                    "icon": pdata["icon"],
                    "step": idx,
                    "total": total,
                    "prev": prev_code,
                    "next": next_code
                })

        nav_lines = ["> [!IMPORTANT]", "> **Recommended Executive Reading Tracks for this Article:**"]
        for t in tracks_in_article:
            next_link_str = ""
            if t["next"]:
                next_file = get_article_filename(t["next"])
                next_title = TITLE_LOOKUP.get(t["next"], t["next"])
                next_link_str = f" → Next: [{next_title}]({next_file})"
            else:
                next_link_str = " → *Track Completed (Capstone)*"
            nav_lines.append(f"> - {t['icon']} **{t['name']}**: Step {t['step']} of {t['total']}{next_link_str}")

        nav_box = "\n".join(nav_lines)

        # Replace or insert Engineering & Data Architecture Deep Dive block and Path Navigation
        tip_block = f"""> [!TIP]
> **Engineering & Technical Companion Deep Dive:**  
> For source code implementations, mathematical derivations, and execution profiling, consult the companion engineering guide:  
> 🛠️ [**Technical Guide {code.upper()}: {tech_title}**](../technical/{tech_file})"""

        # Replace existing TIP block
        content = re.sub(
            r'> \[!TIP\][\s\S]*?(?=\n---)',
            f"{tip_block}\n\n{nav_box}",
            content,
            count=1
        )

        # 3. Clean up any stale old-style technical links in body or footer
        content = re.sub(
            r'\.\./technical/\d\d_[a-z_]+\.md',
            f"../technical/{tech_file}",
            content
        )

        # 4. Update the footer Related Executive Guides section with explicit track progression
        footer_nav_lines = ["\n### 🧭 Executive Track Navigation & Next Steps\n"]
        for t in tracks_in_article:
            prev_str = f"[← Previous: {TITLE_LOOKUP.get(t['prev'], t['prev'])}]({get_article_filename(t['prev'])})" if t["prev"] else "*Track Beginning*"
            next_str = f"[{TITLE_LOOKUP.get(t['next'], t['next'])} →]({get_article_filename(t['next'])})" if t["next"] else "*Final Capstone*"
            footer_nav_lines.append(f"- {t['icon']} **{t['name']}** (Step {t['step']}/{t['total']}): {prev_str} | **Current: {TITLE_LOOKUP[code]}** | {next_str}")

        footer_nav = "\n".join(footer_nav_lines)

        # Check if footer navigation is already present; if not, insert before Related References
        if "### 🧭 Executive Track Navigation" in content:
            content = re.sub(
                r'### 🧭 Executive Track Navigation[\s\S]*?(?=\n## ❓|\n## 🔗|$)',
                footer_nav.strip(),
                content
            )
        else:
            # Insert before ## 🔗 Related Executive Guides
            if "## 🔗 Related Executive Guides" in content:
                content = content.replace(
                    "## 🔗 Related Executive Guides",
                    f"{footer_nav}\n\n---\n\n## 🔗 Related Executive Guides"
                )

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  [ADJUSTED] {fname}")

def update_business_readme():
    print("Updating blog/business/README.md with Role-Tailored Executive Reading Paths...")
    
    readme_path = BIZ_DIR / "README.md"
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Build the 4 Role-Tailored Reading Paths formatted like the user's screenshot
    paths_md = r"""## 🎯 Role-Tailored Executive Reading Paths

The master index organizes these 24 executive articles into four specialized leadership tracks:

### 1. Chief Financial Officer (CFO) & Financial Controller Track
*Focuses on financial mass balance, zero reconciliation, fully-burdened TCO, FinOps unit economics, decommissioning economics, Price-Volume-Mix variance, and boardroom governance:*

- `01b` $\to$ `02a` $\to$ `02b` $\to$ `04a` $\to$ `04b` $\to$ `05a` $\to$ `07b` $\to$ `09a` $\to$ `10a` $\to$ `12b`

1. [`01b: The 8 Pathologies of Enterprise Tech Spend`](01b_the_eight_pathologies_of_enterprise_tech_spend.md)
2. [`02a: From GL Invoices to Business Capabilities`](02a_from_gl_invoices_to_business_capabilities.md)
3. [`02b: Zero-Reconciliation Financial Truth`](02b_zero_reconciliation_financial_truth.md)
4. [`04a: Demystifying Fully-Burdened Application TCO`](04a_demystifying_fully_burdened_application_tco.md)
5. [`04b: FinOps Unit Economics: Workhorses vs Zombie Systems`](04b_unit_economics_workhorses_vs_zombie_systems.md)
6. [`05a: Capability-Based Costing: What Does a Capability Actually Cost?`](05a_what_does_a_business_capability_actually_cost.md)
7. [`07b: The Pragmatic Decommissioning Playbook`](07b_the_pragmatic_decommissioning_playbook.md)
8. [`09a: Beyond On-Time & On-Budget: Technology Value Realization (TVR)`](09a_beyond_on_time_and_on_budget_tvr.md)
9. [`10a: Why Did Our IT Bill Spike? (Price-Volume-Mix Variance)`](10a_why_did_our_it_bill_spike_variance_decomposition.md)
10. [`12b: The CIO & CFO Executive Board Playbook`](12b_the_cio_cfo_executive_board_playbook.md)

---

### 2. Chief Information Officer (CIO) & Technology Executive Track
*Focuses on enterprise digital twins, IT spend pathologies, graph intelligence, rationalization (TIME), transitive blast radius, single points of failure, grounded enterprise AI, and the unified value chain:*

- `01a` $\to$ `01b` $\to$ `03a` $\to$ `03b` $\to$ `07a` $\to$ `08a` $\to$ `08b` $\to$ `11a` $\to$ `11b` $\to$ `12a` $\to$ `12b`

1. [`01a: Enterprise IT Digital Twins for IT Leadership`](01a_digital_twins_for_it_leadership.md)
2. [`01b: The 8 Pathologies of Enterprise Tech Spend`](01b_the_eight_pathologies_of_enterprise_tech_spend.md)
3. [`03a: Why Spreadsheets Fail and Graphs Win`](03a_why_spreadsheets_fail_and_graphs_win.md)
4. [`03b: The Enterprise Nervous System: Lineage & Supply Chain Risk`](03b_the_enterprise_nervous_system_lineage.md)
5. [`07a: Objective Application Pruning (MCDA & TIME Framework)`](07a_objective_portfolio_pruning_mcda_and_time.md)
6. [`08a: The Domino Effect: Transitive Blast Radius in IT`](08a_the_domino_effect_transitive_blast_radius.md)
7. [`08b: Single Points of Failure & Resilience`](08b_single_points_of_failure_and_resilience.md)
8. [`11a: Chatting with the Enterprise: Grounded Enterprise AI`](11a_chatting_with_the_enterprise_grounded_ai.md)
9. [`11b: Zero-Hallucination On-Premise Intelligence`](11b_zero_hallucination_on_premise_intelligence.md)
10. [`12a: The Unified Technology Value Chain`](12a_the_unified_technology_value_chain.md)
11. [`12b: The CIO & CFO Executive Board Playbook`](12b_the_cio_cfo_executive_board_playbook.md)

---

### 3. Business Unit President & Product Executive Track
*Focuses on capability costing, workhorse vs zombie systems, unmasking software redundancy, 2x2 utilization matrices, digital transformation case studies (Payments vs CRM), and technology value realization:*

- `01a` $\to$ `04b` $\to$ `05a` $\to$ `05b` $\to$ `06a` $\to$ `07a` $\to$ `09a` $\to$ `09b` $\to$ `12a`

1. [`01a: Enterprise IT Digital Twins for IT Leadership`](01a_digital_twins_for_it_leadership.md)
2. [`04b: FinOps Unit Economics: Workhorses vs Zombie Systems`](04b_unit_economics_workhorses_vs_zombie_systems.md)
3. [`05a: Capability-Based Costing: What Does a Capability Actually Cost?`](05a_what_does_a_business_capability_actually_cost.md)
4. [`05b: Unmasking the Redundancy Trap: Duplicate Applications`](05b_unmasking_the_redundancy_trap_duplicate_apps.md)
5. [`06a: The 2x2 Utilization Matrix: Spotting Cash Drains`](06a_the_2x2_utilization_quadrant_matrix.md)
6. [`07a: Objective Application Pruning (MCDA & TIME Framework)`](07a_objective_portfolio_pruning_mcda_and_time.md)
7. [`09a: Beyond On-Time & On-Budget: Technology Value Realization (TVR)`](09a_beyond_on_time_and_on_budget_tvr.md)
8. [`09b: Real-Time Payments vs CRM: A Tale of Two Digital Transformations`](09b_a_tale_of_two_transformations_payments_vs_crm.md)
9. [`12a: The Unified Technology Value Chain`](12a_the_unified_technology_value_chain.md)

---

### 4. FinOps Director & Cloud Engineering Leadership Track
*Focuses on tech spend pathologies, fully-burdened TCO, consumption quadrants, elasticity & GreenOps, decommissioning playbooks, Price-Volume-Mix variance, algorithmic SLA clawbacks, and on-premise AI:*

- `01b` $\to$ `04a` $\to$ `04b` $\to$ `06a` $\to$ `06b` $\to$ `07b` $\to$ `10a` $\to$ `10b` $\to$ `11a`

1. [`01b: The 8 Pathologies of Enterprise Tech Spend`](01b_the_eight_pathologies_of_enterprise_tech_spend.md)
2. [`04a: Demystifying Fully-Burdened Application TCO`](04a_demystifying_fully_burdened_application_tco.md)
3. [`04b: FinOps Unit Economics: Workhorses vs Zombie Systems`](04b_unit_economics_workhorses_vs_zombie_systems.md)
4. [`06a: The 2x2 Utilization Matrix: Spotting Cash Drains`](06a_the_2x2_utilization_quadrant_matrix.md)
5. [`06b: Elasticity, Rightsizing & Sustainable GreenOps`](06b_elasticity_and_sustainable_greenops.md)
6. [`07b: The Pragmatic Decommissioning Playbook`](07b_the_pragmatic_decommissioning_playbook.md)
7. [`10a: Why Did Our IT Bill Spike? (Price-Volume-Mix Variance)`](10a_why_did_our_it_bill_spike_variance_decomposition.md)
8. [`10b: Algorithmic FinOps Governance: Anomalies & Vendor SLA Clawbacks`](10b_algorithmic_governance_anomalies_and_sla_credits.md)
9. [`11a: Grounded Enterprise AI: Why Knowledge Graphs Stop LLM Hallucinations`](11a_chatting_with_the_enterprise_grounded_ai.md)
"""

    # Replace section ## 🎯 Executive Persona Reading Guides in README.md
    content = re.sub(
        r'## 🎯 (?:Executive Persona Reading Guides|Role-Tailored Executive Reading Paths)[\s\S]*?(?=\n## 🔬|\n---|\Z)',
        lambda m: paths_md.strip() + "\n\n",
        content
    )

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  [UPDATED] blog/business/README.md")

def main():
    update_business_blogs()
    update_business_readme()
    print("\\nAll business blogs and indexes updated successfully!")

if __name__ == "__main__":
    main()
