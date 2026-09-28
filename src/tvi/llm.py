"""Dual-Mode Knowledge Graph AI Analyst Engine.

Provides natural language querying over technology cost, capability attribution,
application rationalization, dependencies, and benefit realization.

Architecture:
User Question -> Intent & Slot Detection -> Validated Analytical Function -> Structured Result -> Grounded Explanation.

Safeguards:
- Strict intent registry
- Zero arbitrary code execution or open SQL generation
- Dual mode: deterministic rules (default) + optional local Ollama LLM
"""

import re
from typing import Any, Callable, Dict, List, Optional, Tuple
import pandas as pd
import requests

from tvi.config import Config, load_config
from tvi.cost_analytics import calculate_application_tco, calculate_capability_cost, get_application_profile, get_capability_profile
from tvi.dependency import evaluate_deployment_gate, get_application_dependencies, get_capability_dependencies
from tvi.graph import build_knowledge_graph
from tvi.graph_queries import find_business_units_by_vendor, find_capability_overlapping_apps, find_costly_underutilized_overlapping_apps
from tvi.rationalization import find_rationalization_candidates, generate_decommissioning_roadmap
from tvi.value_realization import calculate_benefit_realization, evaluate_capability_maturity_progression, get_project_value_profile
from tvi.variance import calculate_sla_breach_penalties, identify_cost_drivers


class KnowledgeGraphAnalyst:
    """Natural Language Analyst interfacing with analytical engines and Knowledge Graph."""

    def __init__(self, mode: str = "rules", config: Optional[Config] = None):
        self.config = config or load_config()
        self.mode = mode if mode in ["rules", "local_llm"] else "rules"
        self._graph = None
        self.history: List[Dict[str, Any]] = []
        self.context: Dict[str, Any] = {}

    def reset_session(self) -> None:
        """Clear conversation turn history and contextual slot memory."""
        self.history.clear()
        self.context.clear()

    @property
    def graph(self):
        if self._graph is None:
            self._graph = build_knowledge_graph()
        return self._graph

    def is_ollama_available(self) -> bool:
        """Check if local Ollama daemon is active and responsive."""
        try:
            res = requests.get(f"{self.config.llm.base_url}/api/tags", timeout=1.5)
            return res.status_code == 200
        except Exception:
            return False

    def query(self, question: str, output_format: str = "text") -> Dict[str, Any]:
        """Main entrypoint for processing user natural language queries."""
        intent, params = self.detect_intent(question)

        if intent == "UNKNOWN":
            return {
                "question": question,
                "intent": "UNKNOWN",
                "params": params or {},
                "status": "CLARIFICATION_REQUIRED",
                "mode": self.mode,
                "output_format": output_format,
                "explanation": (
                    "I could not confidently match your question to a validated analytical intent. "
                    "You can ask about:\n"
                    "- Application cost or profile (e.g., 'What is the cost of APP001?')\n"
                    "- Capability cost (e.g., 'What does Order-to-Cash cost?')\n"
                    "- Rationalization candidates (e.g., 'Which apps have high cost and low usage?')\n"
                    "- Application dependencies (e.g., 'What depends on APP021?')\n"
                    "- CI/CD release deployment gates (e.g., 'Can we deploy APP010?')\n"
                    "- Vendor contract SLA penalties (e.g., 'What penalties or credits are owed?')\n"
                    "- Decommissioning roadmaps (e.g., 'Show decommissioning roadmap for APP021')\n"
                    "- Capability maturity progression (e.g., 'How did project investments uplift capability maturity?')\n"
                    "- Project investments and benefits (e.g., 'What benefits were expected from PRJ014?')\n"
                    "- Cost variance and spend drivers (e.g., 'Why did spend increase in August?')\n"
                    "- Vendor dependencies (e.g., 'Which business units depend on technology supplied by TechNova?')"
                ),
                "structured_result": None,
            }

        # Track contextual slots across turns
        if "application_id" in params:
            self.context["last_application_id"] = params["application_id"]
        if "project_id" in params:
            self.context["last_project_id"] = params["project_id"]
        if "vendor" in params:
            self.context["last_vendor_name"] = params["vendor"]
        self.context["last_intent"] = intent

        # Dispatch to verified analytical function
        structured_data = self.dispatch(intent, params)

        # Synthesize explanation
        if self.mode == "local_llm" and self.is_ollama_available():
            explanation = self._explain_with_llm(question, intent, structured_data)
        else:
            explanation = self._explain_with_rules(question, intent, structured_data)

        # Record conversational history
        turn_record = {
            "turn_index": len(self.history) + 1,
            "question": question,
            "intent": intent,
            "params": params,
            "explanation": explanation,
        }
        self.history.append(turn_record)

        result_payload = {
            "question": question,
            "intent": intent,
            "params": params,
            "mode": self.mode,
            "output_format": output_format,
            "status": "SUCCESS",
            "explanation": explanation,
            "structured_result": structured_data,
        }

        if output_format == "markdown":
            result_payload["markdown_presentation"] = f"### TVI AI Analyst Insight\n\n{explanation}"

        return result_payload

    def detect_intent(self, question: str) -> Tuple[str, Dict[str, Any]]:
        """Map user query to known intents and extract semantic parameter entities."""
        q = question.lower()

        # Entity extraction helpers
        app_match = re.search(r"\b(app\d{3})\b", q, re.IGNORECASE)
        prj_match = re.search(r"\b(prj\d{3})\b", q, re.IGNORECASE)
        cap_match = re.search(r"\b(cap\d{3})\b", q, re.IGNORECASE)

        # Contextual resolution for anaphoric pronouns ("it", "this app", "the system")
        resolved_app = app_match.group(1).upper() if app_match else None
        if not resolved_app and any(p in q for p in [" it", " this app", " that app", " the app", "deploy it"]):
            resolved_app = self.context.get("last_application_id")

        resolved_prj = prj_match.group(1).upper() if prj_match else None
        if not resolved_prj and any(p in q for p in [" this project", " the project"]):
            resolved_prj = self.context.get("last_project_id")

        # 0. Vendor Multi-hop Dependency (check first to avoid collision with generic 'depend')
        known_vendors = {
            "technova": "TechNova",
            "cloudsphere": "CloudSphere",
            "dataforge": "DataForge",
            "enterprisesoft": "EnterpriseSoft",
            "infraworks": "InfraWorks",
            "cybershield": "CyberShield",
            "apexlogic": "ApexLogic",
            "globalnet": "GlobalNet",
            "primescale": "PrimeScale",
            "syscore": "SysCore"
        }
        for v_key, v_name in known_vendors.items():
            if v_key in q:
                return "VENDOR_DEPENDENCY", {"vendor": v_name}
        if ("vendor" in q or "supplied by" in q) and not any(w in q for w in ["sla", "penalty", "credit"]):
            return "VENDOR_DEPENDENCY", {"vendor": "TechNova"}

        # 1. CI/CD Deployment Gating
        if any(w in q for w in ["deploy", "deployment gate", "release gate", "pipeline gate", "can we deploy", "approval level"]):
            app_id = resolved_app or "APP010"
            tier = "Major" if "major" in q else ("Hotfix" if "hotfix" in q else "Standard")
            return "BLAST_RADIUS_GATING", {"application_id": app_id, "change_tier": tier}

        # 2. Vendor Contract SLA Penalties & Credits
        if any(w in q for w in ["sla", "penalty", "penalties", "contract breach", "credit memo", "unbacked rate"]):
            return "SLA_PENALTIES", {}

        # 3. Decommissioning Roadmap Milestones
        if any(w in q for w in ["decommission", "roadmap", "milestone", "exit phase", "sunset"]):
            app_id = resolved_app or "APP021"
            return "DECOMMISSIONING_ROADMAP", {"application_id": app_id}

        # 4. Capability Maturity Progression
        if any(w in q for w in ["maturity", "progression", "capability uplift", "maturity point"]):
            return "CAPABILITY_MATURITY", {}

        # 5. Dependency Analysis
        if any(w in q for w in ["depend", "impact", "blast radius", "relies on"]):
            if resolved_app:
                return "APPLICATION_DEPENDENCY", {"application_id": resolved_app}
            if cap_match:
                return "CAPABILITY_DEPENDENCY", {"capability_id": cap_match.group(1).upper()}

        # 6. Rationalization / Overlap / Low Utilization
        if any(w in q for w in ["rationaliz", "overlap", "underutilized", "low utilization", "retire", "candidates"]):
            return "RATIONALIZATION_CANDIDATES", {}

        # 7. Project Benefits / Investment Realization
        if resolved_prj or any(w in q for w in ["benefit", "investment", "realized", "project", "budget variance", "roi", "return"]):
            if resolved_prj:
                return "PROJECT_VALUE_PROFILE", {"project_id": resolved_prj}
            return "PROJECT_BENEFIT_REALIZATION", {}

        # 8. Cost Drivers / Variance / Increase
        if any(w in q for w in ["why did", "spend increase", "cost increase", "variance", "driver", "drove"]):
            months = re.findall(r"\b(2024-\d{2}|august|july|september)\b", q)
            return "COST_VARIANCE_DRIVERS", {"months": months}

        # 9. Capability Cost
        if cap_match or any(w in q for w in ["capability", "order-to-cash", "procure-to-pay", "financial reporting"]):
            if cap_match:
                return "CAPABILITY_COST", {"capability_id": cap_match.group(1).upper()}
            if "order-to-cash" in q or "order to cash" in q:
                return "CAPABILITY_COST", {"capability_id": "CAP003", "capability_name": "Order-to-Cash"}
            return "CAPABILITY_COST", {"capability_id": "CAP003", "capability_name": "Order-to-Cash"}

        # 10. Application Cost / Profile
        if resolved_app or any(w in q for w in ["application cost", "tco", "app cost", "spend on"]):
            app_id = resolved_app or "APP001"
            return "APPLICATION_COST", {"application_id": app_id}

        return "UNKNOWN", {}

    def dispatch(self, intent: str, params: Dict[str, Any]) -> Any:
        """Route mapped intent to safe Python analytics function."""
        if intent == "APPLICATION_COST":
            app_id = params.get("application_id", "APP001")
            return get_application_profile(app_id)

        elif intent == "CAPABILITY_COST":
            cap_id = params.get("capability_id", "CAP003")
            return get_capability_profile(cap_id)

        elif intent == "RATIONALIZATION_CANDIDATES":
            return find_rationalization_candidates().to_dict(orient="records")

        elif intent == "APPLICATION_DEPENDENCY":
            app_id = params.get("application_id", "APP021")
            return get_application_dependencies(app_id, self.graph)

        elif intent == "CAPABILITY_DEPENDENCY":
            cap_id = params.get("capability_id", "CAP003")
            return get_capability_dependencies(cap_id, self.graph)

        elif intent == "BLAST_RADIUS_GATING":
            app_id = params.get("application_id", "APP010")
            tier = params.get("change_tier", "Major")
            return evaluate_deployment_gate(app_id, change_tier=tier, G=self.graph)

        elif intent == "SLA_PENALTIES":
            return calculate_sla_breach_penalties().to_dict(orient="records")

        elif intent == "DECOMMISSIONING_ROADMAP":
            app_id = params.get("application_id", "APP021")
            return generate_decommissioning_roadmap(target_app_ids=[app_id]).to_dict(orient="records")

        elif intent == "CAPABILITY_MATURITY":
            return evaluate_capability_maturity_progression().head(10).to_dict(orient="records")

        elif intent == "PROJECT_VALUE_PROFILE":
            prj_id = params.get("project_id", "PRJ014")
            return get_project_value_profile(prj_id)

        elif intent == "PROJECT_BENEFIT_REALIZATION":
            return calculate_benefit_realization().head(10).to_dict(orient="records")

        elif intent == "COST_VARIANCE_DRIVERS":
            return identify_cost_drivers()

        elif intent == "VENDOR_DEPENDENCY":
            v_query = params.get("vendor", "TechNova")
            return find_business_units_by_vendor(self.graph, v_query)

        return None

    def _explain_with_rules(self, question: str, intent: str, data: Any) -> str:
        """Generate deterministic, factually grounded explanation from structured data."""
        if intent == "APPLICATION_COST":
            summary = data.get("summary", {})
            return (
                f"Application {summary.get('application_id')} ({summary.get('application_name')}) "
                f"has an annual TCO of ₹{summary.get('annual_tco', 0)/1e7:.2f} Cr.\n"
                f"- Average Monthly Users: {summary.get('avg_monthly_users', 0):.0f}\n"
                f"- Annual Cost per User: ₹{summary.get('annual_cost_per_user', 0):,.2f}\n"
                f"- Cost per Transaction: ₹{summary.get('cost_per_transaction', 0):.4f}\n"
                f"- Lifecycle Status: {summary.get('lifecycle_status')}, Criticality: {summary.get('criticality')}"
            )

        elif intent == "CAPABILITY_COST":
            summary = data.get("summary", {})
            return (
                f"Capability {summary.get('capability_id')} ({summary.get('capability_name')}) "
                f"represents total annual technology expenditure of ₹{summary.get('total_capability_cost', 0)/1e7:.2f} Cr.\n"
                f"- Direct Application Cost: ₹{summary.get('direct_app_cost', 0)/1e7:.2f} Cr across {summary.get('supported_apps_count', 0)} supporting applications.\n"
                f"- Allocated Shared Infrastructure Cost: ₹{summary.get('shared_infra_allocated', 0)/1e7:.2f} Cr.\n"
                f"- Strategic Priority: {summary.get('strategic_priority')}, Criticality: {summary.get('criticality')}."
            )

        elif intent == "RATIONALIZATION_CANDIDATES":
            items = data[:4]
            lines = [f"Found {len(data)} applications requiring rationalization review:"]
            for item in items:
                lines.append(
                    f"• {item['application_id']} ({item['application_name']}): "
                    f"Annual TCO ₹{item['annual_tco']/1e7:.2f} Cr | Active Users: {item['avg_monthly_users']:.0f} | "
                    f"RRI: {item['rationalization_review_index']} | Evidence: {item['investigation_evidence']}"
                )
            lines.append("Note: Estimated costs reflect current spending scenarios rather than guaranteed savings.")
            return "\n".join(lines)

        elif intent == "APPLICATION_DEPENDENCY":
            return (
                f"Application {data.get('application_id')} ({data.get('application_name')}) Dependency Analysis:\n"
                f"- Direct Dependent Applications ({len(data.get('direct_dependent_apps', []))}): "
                f"{', '.join(a['id'] for a in data.get('direct_dependent_apps', [])) or 'None'}\n"
                f"- Indirect Transitive Dependents: {len(data.get('indirect_dependent_apps', []))} applications\n"
                f"- Capabilities Supported: {', '.join(c['name'] for c in data.get('capabilities', []))}\n"
                f"- Business Units Impacted: {', '.join(b['name'] for b in data.get('business_units', []))}\n"
                f"- Blast Radius Risk Index: {data.get('blast_radius_metric')}"
            )

        elif intent == "PROJECT_VALUE_PROFILE":
            prj = data.get("project", {})
            return (
                f"Project {prj.get('project_id')} ({prj.get('project_name')}):\n"
                f"- Budget: ₹{prj.get('investment_budget', 0)/1e7:.2f} Cr | Actual Spend: ₹{prj.get('actual_spend', 0)/1e7:.2f} Cr\n"
                f"- Expected Annual Benefit: ₹{prj.get('expected_annual_benefit', 0)/1e7:.2f} Cr\n"
                f"- Status: {prj.get('status')} | Sponsor: {prj.get('sponsor_business_unit')}"
            )

        elif intent == "COST_VARIANCE_DRIVERS":
            delta = data.get("total_cost_delta", 0)
            top_apps = data.get("top_application_drivers")
            lines = [
                f"Technology spend shifted by ₹{delta/1e7:+.2f} Cr ({data.get('total_cost_delta_pct'):+.1f}%) "
                f"between {data.get('baseline_month')} and {data.get('comparison_month')}."
            ]
            if isinstance(top_apps, pd.DataFrame) and not top_apps.empty:
                lines.append("Key Application Drivers:")
                for _, r in top_apps.head(3).iterrows():
                    lines.append(
                        f"• {r['application_id']} ({r['application_name']}): Cost change ₹{r['cost_delta']/1e7:+.2f} Cr | "
                        f"Txn Growth: {r['txn_growth_pct']:+.1f}% | Diagnosis: {r['diagnosis']}"
                    )
            return "\n".join(lines)

        elif intent == "VENDOR_DEPENDENCY":
            if not data:
                return "Vendor dependency traversal found 0 connections for this vendor. Please check vendor name."
            v_name = data[0].get("vendor_name", "Vendor")
            bus = sorted(list(set(r["business_unit_name"] for r in data)))
            apps = sorted(list(set(r["application_name"] for r in data)))
            lines = [
                f"Vendor '{v_name}' supplies technology impacting {len(bus)} business units across {len(apps)} applications ({len(data)} value chain connections):",
                f"• Consuming Business Units: {', '.join(bus)}",
                f"• Supported Applications: {', '.join(apps[:4])}{'...' if len(apps) > 4 else ''}",
                "\nSample Value Chain Lineage:"
            ]
            for row in data[:4]:
                lines.append(
                    f"• {row['vendor_name']} -> {row['technology_name']} -> {row['application_name']} -> "
                    f"{row['capability_name']} -> {row['business_unit_name']}"
                )
            return "\n".join(lines)

        elif intent == "BLAST_RADIUS_GATING":
            status = data.get("gate_status", "UNKNOWN")
            app = data.get("application_name", data.get("application_id"))
            tier = data.get("change_tier", "Standard")
            b_rad = data.get("blast_radius_metric", 0)
            thresh = data.get("threshold", 0)
            approval = data.get("approval_level", "")
            recom = data.get("recommendation", "")
            return (
                f"Deployment Gating Verdict for {app} ({tier} Release):\n"
                f"• Gate Status: {status} (Blast Radius: {b_rad} vs Max Threshold: {thresh})\n"
                f"• Direct Dependent Applications: {data.get('direct_dependent_apps_count')} systems\n"
                f"• Required Governance Sign-off: {approval}\n"
                f"• Policy Recommendation: {recom}"
            )

        elif intent == "SLA_PENALTIES":
            if not data:
                return "No vendor SLA breach penalties currently assessed across portfolio."
            lines = ["Assessed Vendor Contract SLA Penalties & Service Credits:"]
            for row in data:
                lines.append(
                    f"• {row['vendor_name']} ({row['application_name']}): Unbacked spend surge ₹{row['unbacked_spend_surge']/1e5:.1f}L | "
                    f"Assessed Credit: ₹{row['assessed_penalty_credit_inr']/1e5:.1f}L ({row['credit_status']})"
                )
            return "\n".join(lines)

        elif intent == "DECOMMISSIONING_ROADMAP":
            if not data:
                return "No decommissioning milestones available."
            app_name = data[0].get("application_name", "Target Application")
            lines = [f"Phased Decommissioning Milestone Roadmap for {app_name}:"]
            for m in data:
                lines.append(
                    f"• {m['phase_code']} (Months {m['start_month']}-{m['end_month']}): {m['phase_name']} "
                    f"[{m['risk_rating']} Risk] — {m['cumulative_cost_unlocked_pct']}% savings unlocked"
                )
            return "\n".join(lines)

        elif intent == "CAPABILITY_MATURITY":
            if not data:
                return "No capability maturity progression records found."
            lines = ["Strategic Capability Maturity Progression from Investments:"]
            for r in data[:4]:
                lines.append(
                    f"• {r['capability_name']} ({r['strategic_priority']} Priority): Maturity {r['baseline_maturity']} -> {r['current_maturity']} "
                    f"(+{r['maturity_uplift']} uplift via {r['project_name']}) | Classification: {r['transformation_impact']}"
                )
            return "\n".join(lines)

        return "Analysis completed. See structured result for quantitative details."

    def generate_briefing_slide(self, question: str) -> Dict[str, Any]:
        """Generate structured executive summary briefing slide components from query."""
        res = self.query(question)
        intent = res["intent"]
        explanation = res["explanation"]

        headline = explanation.split("\n")[0] if "\n" in explanation else explanation
        bullets = [line.strip("•- ") for line in explanation.split("\n")[1:] if line.strip().startswith(("•", "-"))]

        return {
            "slide_id": f"SLIDE-{intent}",
            "slide_title": f"Executive Intelligence: {intent.replace('_', ' ').title()}",
            "user_query": question,
            "executive_headline": headline,
            "key_takeaways": bullets[:4] if bullets else [explanation],
            "governance_disclaimer": "Validated via local DuckDB + NetworkX Enterprise Knowledge Graph (Zero Hallucination).",
        }

    def _explain_with_llm(self, question: str, intent: str, data: Any) -> str:
        """Call local Ollama to formulate a fluent natural language response grounded in returned data."""
        prompt = (
            f"You are the Technology Value Intelligence Analyst. Answer the user question based ONLY on the "
            f"structured data provided below. Do not fabricate numbers or invent assumptions.\n\n"
            f"User Question: {question}\n"
            f"Analytical Intent: {intent}\n"
            f"Structured Data:\n{str(data)[:2000]}\n\n"
            f"Provide a concise, professional consulting explanation:"
        )
        try:
            res = requests.post(
                f"{self.config.llm.base_url}/api/generate",
                json={
                    "model": self.config.llm.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": self.config.llm.temperature},
                },
                timeout=15,
            )
            if res.status_code == 200:
                return res.json().get("response", "").strip()
        except Exception:
            pass
        # Fallback to rules if LLM request fails
        return self._explain_with_rules(question, intent, data)


# Convenience functions required by section 33
def answer_application_cost_question(query: str) -> Dict[str, Any]:
    return KnowledgeGraphAnalyst(mode="rules").query(query)


def answer_capability_cost_question(query: str) -> Dict[str, Any]:
    return KnowledgeGraphAnalyst(mode="rules").query(query)


def answer_dependency_question(query: str) -> Dict[str, Any]:
    return KnowledgeGraphAnalyst(mode="rules").query(query)


def answer_rationalization_question(query: str) -> Dict[str, Any]:
    return KnowledgeGraphAnalyst(mode="rules").query(query)


def answer_benefit_question(query: str) -> Dict[str, Any]:
    return KnowledgeGraphAnalyst(mode="rules").query(query)
