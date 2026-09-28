"""Unit tests for TVI v2 Roadmap Phase 4 (Modules 10, 11, 12).

Tests:
- Module 10: Statistical cost anomalies (Isolation Forest & Z-scores), SLA penalties, budget forecasting, FinOps tickets
- Module 11: Conversational memory/anaphora, new intents, structured output, briefing slides
- Module 12: Executive HTML briefing export, JSON presentation deck, webhook payloads, external peer benchmarking, portfolio rebalancing
"""

import json
import pandas as pd
import pytest

from tvi.llm import KnowledgeGraphAnalyst
from tvi.reporting import (
    benchmark_external_industry_peers,
    export_executive_briefing_html,
    export_presentation_deck_json,
    generate_executive_webhook_payload,
    simulate_portfolio_rebalancing,
)
from tvi.variance import (
    calculate_sla_breach_penalties,
    detect_cost_anomalies,
    forecast_budget_variance,
    generate_finops_anomaly_tickets,
)


# ==============================================================================
# Module 10 Tests: Cost Driver & Financial Variance Analysis
# ==============================================================================


def test_statistical_cost_anomalies_and_isolation_forest():
    """Verify statistical anomaly detection with rolling Z-scores and Isolation Forest."""
    anomalies_df = detect_cost_anomalies(z_threshold=2.0)
    assert not anomalies_df.empty
    assert set([
        "application_id", "month", "monthly_spend", "spend_delta", "z_score",
        "iso_anomaly", "anomaly_severity", "root_cause_diagnosis", "requires_investigation"
    ]).issubset(anomalies_df.columns)

    # APP022 should be detected as requiring investigation (unbacked spike)
    app022_anomalies = anomalies_df[anomalies_df["application_id"] == "APP022"]
    assert not app022_anomalies.empty
    assert app022_anomalies.iloc[0]["requires_investigation"] == True


def test_sla_breach_penalties_calculation():
    """Verify vendor SLA breach penalty calculations for unbacked rate surges."""
    penalties_df = calculate_sla_breach_penalties(rate_anomaly_threshold_pct=25.0, penalty_credit_rate=0.20)
    assert not penalties_df.empty
    assert set([
        "vendor_id", "vendor_name", "application_id", "unbacked_spend_surge",
        "assessed_penalty_credit_inr", "sla_contract_clause"
    ]).issubset(penalties_df.columns)

    # APP022 should incur assessed penalty credit
    app022_penalty = penalties_df[penalties_df["application_id"] == "APP022"]
    assert not app022_penalty.empty
    assert app022_penalty.iloc[0]["assessed_penalty_credit_inr"] > 0


def test_budget_variance_forecasting():
    """Verify multi-period forward-looking budget variance forecasting."""
    fc_df = forecast_budget_variance(forecast_months=4, alpha=0.2)
    assert not fc_df.empty
    assert len(fc_df) == 4
    assert set([
        "forecast_month", "projected_monthly_spend", "lower_bound_90pct",
        "upper_bound_90pct", "monthly_budget_target", "runrate_governance_status"
    ]).issubset(fc_df.columns)
    # Check monotonic forecast months
    assert list(fc_df["forecast_month"]) == ["2025-01", "2025-02", "2025-03", "2025-04"]


def test_finops_anomaly_ticket_payloads():
    """Verify generation of structured FinOps investigation tickets."""
    tickets = generate_finops_anomaly_tickets()
    assert isinstance(tickets, list)
    assert len(tickets) > 0
    t0 = tickets[0]
    assert "ticket_id" in t0
    assert "affected_application_id" in t0
    assert "spend_increase_inr" in t0
    assert "investigation_checklist" in t0


# ==============================================================================
# Module 11 Tests: Local Knowledge Graph AI Analyst
# ==============================================================================


def test_llm_conversational_session_memory_and_anaphora():
    """Verify multi-turn session memory and anaphora pronoun resolution."""
    analyst = KnowledgeGraphAnalyst(mode="rules")
    analyst.reset_session()
    assert len(analyst.history) == 0

    # Turn 1: Explicit application
    r1 = analyst.query("What is the cost of APP001?")
    assert r1["intent"] == "APPLICATION_COST"
    assert analyst.context.get("last_application_id") == "APP001"
    assert len(analyst.history) == 1

    # Turn 2: Pronoun resolution ("Can we deploy it?")
    r2 = analyst.query("Can we deploy it for a major release?")
    assert r2["intent"] == "BLAST_RADIUS_GATING"
    assert r2["params"]["application_id"] == "APP001"
    assert r2["params"]["change_tier"] == "Major"
    assert len(analyst.history) == 2


def test_llm_new_intents_and_structured_output():
    """Verify new analytical intents and markdown presentation formatting."""
    analyst = KnowledgeGraphAnalyst(mode="rules")

    # SLA Penalties intent
    r_sla = analyst.query("What SLA penalties or credits are owed for unbacked spikes?")
    assert r_sla["intent"] == "SLA_PENALTIES"
    assert r_sla["status"] == "SUCCESS"

    # Decommissioning Roadmap intent
    r_decom = analyst.query("Show decommissioning roadmap for APP021", output_format="markdown")
    assert r_decom["intent"] == "DECOMMISSIONING_ROADMAP"
    assert "markdown_presentation" in r_decom

    # Capability Maturity intent
    r_mat = analyst.query("Show capability maturity progression")
    assert r_mat["intent"] == "CAPABILITY_MATURITY"


def test_llm_briefing_slide_generation():
    """Verify automated executive summary briefing slide generation."""
    analyst = KnowledgeGraphAnalyst(mode="rules")
    slide = analyst.generate_briefing_slide("Can we deploy APP010 for a major release?")
    assert isinstance(slide, dict)
    assert set(["slide_id", "slide_title", "executive_headline", "key_takeaways", "governance_disclaimer"]).issubset(slide.keys())
    assert "Central Auth" in slide["executive_headline"] or "APP010" in slide["executive_headline"]


# ==============================================================================
# Module 12 Tests: End-to-End Value Intelligence & Reporting
# ==============================================================================


def test_executive_briefing_html_export(tmp_path):
    """Verify styled HTML executive briefing document generation."""
    out_file = str(tmp_path / "executive_briefing.html")
    html = export_executive_briefing_html(out_file)
    assert "<!DOCTYPE html>" in html
    assert "Technology Value Intelligence" in html
    assert "kpi-card" in html


def test_presentation_deck_json_export(tmp_path):
    """Verify 5-slide JSON presentation deck generation."""
    out_file = str(tmp_path / "presentation_deck.json")
    deck = export_presentation_deck_json(out_file)
    assert "slides" in deck
    assert len(deck["slides"]) == 5
    assert deck["slides"][0]["title"] == "Executive Spend & Portfolio Concentration"


def test_executive_webhook_payload():
    """Verify Slack Block Kit / Teams webhook notification structure."""
    payload = generate_executive_webhook_payload("anomalous_spend_alert")
    assert payload["type"] == "message"
    assert "attachments" in payload
    blocks = payload["attachments"][0]["blocks"]
    assert len(blocks) >= 3
    assert any(b.get("type") == "header" for b in blocks)


def test_external_industry_benchmarking():
    """Verify external industry peer benchmarking metrics."""
    bench_df = benchmark_external_industry_peers()
    assert not bench_df.empty
    assert len(bench_df) == 4
    assert set(["benchmark_dimension", "enterprise_value", "peer_median", "top_quartile_benchmark", "quartile_status"]).issubset(bench_df.columns)


def test_portfolio_rebalancing_simulation():
    """Verify portfolio financial rebalancing simulation."""
    rebal = simulate_portfolio_rebalancing(target_decom_ids=["APP021", "APP012"], strategic_reinvestment_pct=0.50)
    assert set([
        "targeted_applications", "gross_headline_spend_identified", "net_avoidable_runrate_savings",
        "strategic_reinvestment_pool", "retained_cash_savings_bottom_line", "baseline_run_vs_change", "rebalanced_run_vs_change"
    ]).issubset(rebal.keys())
    assert rebal["strategic_reinvestment_pool"] > 0
    assert rebal["retained_cash_savings_bottom_line"] > 0
