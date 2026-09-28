"""Master build script that generates all 12 deep, advanced TVI notebooks."""

import sys
from pathlib import Path

# Add project root to sys.path
workspace_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(workspace_root))

from scripts.nb_builders.nb_01_03 import build_notebook_01, build_notebook_02, build_notebook_03
from scripts.nb_builders.nb_04_06 import build_notebook_04, build_notebook_05, build_notebook_06
from scripts.nb_builders.nb_07_09 import build_notebook_07, build_notebook_08, build_notebook_09
from scripts.nb_builders.nb_10_12 import build_notebook_10, build_notebook_11, build_notebook_12
from scripts.nb_builders.common import save_nb

def main():
    print("=" * 60)
    print("Generating Complete Suite of 12 Deep Research Notebooks")
    print("=" * 60)

    notebooks = [
        (build_notebook_01, "01_enterprise_data_generation/v1_baseline.ipynb"),
        (build_notebook_02, "02_tbm_itfm_data_model/v1_baseline.ipynb"),
        (build_notebook_03, "03_knowledge_graph_construction/v1_baseline.ipynb"),
        (build_notebook_04, "04_application_cost_intelligence/v1_baseline.ipynb"),
        (build_notebook_05, "05_capability_cost_intelligence/v1_baseline.ipynb"),
        (build_notebook_06, "06_consumption_intelligence/v1_baseline.ipynb"),
        (build_notebook_07, "07_application_rationalization/v1_baseline.ipynb"),
        (build_notebook_08, "08_dependency_impact_analysis/v1_baseline.ipynb"),
        (build_notebook_09, "09_investment_benefit_realization/v1_baseline.ipynb"),
        (build_notebook_10, "10_cost_driver_variance_analysis/v1_baseline.ipynb"),
        (build_notebook_11, "11_local_llm_knowledge_graph_analyst/v1_baseline.ipynb"),
        (build_notebook_12, "12_end_to_end_value_intelligence/v1_baseline.ipynb"),
    ]

    for builder_fn, filename in notebooks:
        nb = builder_fn()
        save_nb(nb, filename)

    print("=" * 60)
    print("✓ All 12 deep notebooks generated successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
