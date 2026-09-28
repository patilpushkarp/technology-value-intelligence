"""In-process notebook execution and output recording engine.

Executes all 12 notebooks sequentially in-process, capturing text and table outputs,
populating cell outputs, and saving executed notebooks for full reproducibility.
"""

import io
import os
import sys
import time
from pathlib import Path

# Ensure paths and environment variables stay inside workspace
workspace_root = Path(__file__).resolve().parent.parent
os.environ["IPYTHONDIR"] = str(workspace_root / ".ipython")
os.environ["MPLCONFIGDIR"] = str(workspace_root / ".matplotlib")
(workspace_root / ".ipython").mkdir(exist_ok=True)
(workspace_root / ".matplotlib").mkdir(exist_ok=True)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import nbformat
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output

BASE_NOTEBOOKS = [
    "01_enterprise_data_generation/v1_baseline.ipynb",
    "02_tbm_itfm_data_model/v1_baseline.ipynb",
    "03_knowledge_graph_construction/v1_baseline.ipynb",
    "04_application_cost_intelligence/v1_baseline.ipynb",
    "05_capability_cost_intelligence/v1_baseline.ipynb",
    "06_consumption_intelligence/v1_baseline.ipynb",
    "07_application_rationalization/v1_baseline.ipynb",
    "08_dependency_impact_analysis/v1_baseline.ipynb",
    "09_investment_benefit_realization/v1_baseline.ipynb",
    "10_cost_driver_variance_analysis/v1_baseline.ipynb",
    "11_local_llm_knowledge_graph_analyst/v1_baseline.ipynb",
    "12_end_to_end_value_intelligence/v1_baseline.ipynb",
]

DEV_NOTEBOOKS = [
    "01_enterprise_data_generation/v2_development.ipynb",
    "02_tbm_itfm_data_model/v2_development.ipynb",
    "03_knowledge_graph_construction/v2_development.ipynb",
    "04_application_cost_intelligence/v2_development.ipynb",
    "05_capability_cost_intelligence/v2_development.ipynb",
    "06_consumption_intelligence/v2_development.ipynb",
    "07_application_rationalization/v2_development.ipynb",
    "08_dependency_impact_analysis/v2_development.ipynb",
    "09_investment_benefit_realization/v2_development.ipynb",
    "10_cost_driver_variance_analysis/v2_development.ipynb",
    "11_local_llm_knowledge_graph_analyst/v2_development.ipynb",
    "12_end_to_end_value_intelligence/v2_development.ipynb",
]

NOTEBOOKS = BASE_NOTEBOOKS + DEV_NOTEBOOKS

def execute_single_notebook(nb_path: Path):
    rel_display = f"{nb_path.parent.name}/{nb_path.name}"
    print(f"Executing: {rel_display:50s} ...", end=" ", flush=True)
    t0 = time.time()

    with open(nb_path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    # Initialize fresh interactive shell for clean state
    shell = InteractiveShell.instance()
    # Ensure sys.path includes src
    src_dir = str(workspace_root / "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    execution_count = 1
    for cell in nb.cells:
        if cell.cell_type == "code":
            cell.outputs = []
            cell.execution_count = execution_count
            execution_count += 1

            with capture_output() as cap:
                res = shell.run_cell(cell.source)

            # Record standard stdout/stderr
            if cap.stdout:
                cell.outputs.append(
                    nbformat.v4.new_output(
                        output_type="stream",
                        name="stdout",
                        text=cap.stdout,
                    )
                )

            # If there was an error
            if not res.success and res.error_in_exec:
                err_text = str(res.error_in_exec)
                cell.outputs.append(
                    nbformat.v4.new_output(
                        output_type="error",
                        ename=type(res.error_in_exec).__name__,
                        evalue=err_text,
                        traceback=[err_text],
                    )
                )
                print(f"FAILED!\nError in cell:\n{cell.source}\nError: {err_text}")
                raise res.error_in_exec

            # If an execution result was returned
            elif res.result is not None:
                # If pandas DataFrame, generate nice text representation
                res_str = repr(res.result)
                cell.outputs.append(
                    nbformat.v4.new_output(
                        output_type="execute_result",
                        execution_count=cell.execution_count,
                        data={"text/plain": res_str},
                    )
                )

    # Save executed notebook with all captured outputs
    with open(nb_path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)

    elapsed = time.time() - t0
    print(f"DONE ({elapsed:.1f}s)")

def main():
    base_dir = workspace_root / "notebooks"
    print("=== Executing 12 TVI Notebooks In-Process ===")
    for nb_name in NOTEBOOKS:
        nb_path = base_dir / nb_name
        if not nb_path.exists():
            print(f"ERROR: {nb_name} does not exist!")
            sys.exit(1)
        execute_single_notebook(nb_path)

    print("\n✓ All 12 notebooks successfully executed with outputs recorded.")

if __name__ == "__main__":
    main()
