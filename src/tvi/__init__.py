"""Technology Value Intelligence (TVI) Package.

A local-first analytical and knowledge graph architecture for
Technology Business Management (TBM), IT Financial Management (ITFM),
and Technology Value Realization (TVR).
"""

from tvi.config import Config, load_config, load_ontology
from tvi.cost_analytics import (
    calculate_application_tco,
    calculate_capability_cost,
    calculate_service_cost,
    get_application_profile,
    get_capability_profile,
    get_service_profile,
)
from tvi.consumption_analytics import (
    analyze_consumption_quadrants,
    analyze_unit_economics_trends,
    find_high_cost_low_utilization,
)
from tvi.database import TVIDatabase, get_database
from tvi.data_generation import EnterpriseDataGenerator
from tvi.dependency import (
    get_application_dependencies,
    get_business_unit_dependencies,
    get_capability_dependencies,
)
from tvi.graph import (
    build_knowledge_graph,
    get_focused_subgraph,
    save_graph,
    validate_graph,
)
from tvi.graph_queries import (
    find_business_units_by_vendor,
    find_capability_overlapping_apps,
    find_costly_underutilized_overlapping_apps,
    get_full_value_chain_path,
)
from tvi.llm import (
    KnowledgeGraphAnalyst,
    answer_application_cost_question,
    answer_benefit_question,
    answer_capability_cost_question,
    answer_dependency_question,
    answer_rationalization_question,
)
from tvi.rationalization import (
    find_rationalization_candidates,
    score_application_portfolio,
)
from tvi.reporting import generate_executive_report
from tvi.validation import DataQualityValidator, run_data_quality_checks
from tvi.value_realization import (
    analyze_benefit_kpi_progression,
    calculate_benefit_realization,
    calculate_project_budget_variance,
    get_project_value_profile,
)
from tvi.variance import (
    calculate_category_variance,
    calculate_monthly_cost_variance,
    identify_cost_drivers,
)

# Convenient aliases matching section 33 naming
find_capability_overlap = find_capability_overlapping_apps
find_application_dependencies = get_application_dependencies
find_capability_dependencies = get_capability_dependencies

__all__ = [
    "Config",
    "load_config",
    "load_ontology",
    "EnterpriseDataGenerator",
    "DataQualityValidator",
    "run_data_quality_checks",
    "TVIDatabase",
    "get_database",
    "build_knowledge_graph",
    "validate_graph",
    "save_graph",
    "get_focused_subgraph",
    "find_business_units_by_vendor",
    "find_capability_overlapping_apps",
    "find_capability_overlap",
    "find_costly_underutilized_overlapping_apps",
    "get_full_value_chain_path",
    "calculate_application_tco",
    "calculate_capability_cost",
    "calculate_service_cost",
    "get_application_profile",
    "get_capability_profile",
    "get_service_profile",
    "analyze_consumption_quadrants",
    "find_high_cost_low_utilization",
    "analyze_unit_economics_trends",
    "score_application_portfolio",
    "find_rationalization_candidates",
    "get_application_dependencies",
    "find_application_dependencies",
    "get_capability_dependencies",
    "find_capability_dependencies",
    "get_business_unit_dependencies",
    "calculate_project_budget_variance",
    "calculate_benefit_realization",
    "analyze_benefit_kpi_progression",
    "get_project_value_profile",
    "calculate_monthly_cost_variance",
    "calculate_category_variance",
    "identify_cost_drivers",
    "KnowledgeGraphAnalyst",
    "answer_application_cost_question",
    "answer_capability_cost_question",
    "answer_dependency_question",
    "answer_rationalization_question",
    "answer_benefit_question",
    "generate_executive_report",
]
