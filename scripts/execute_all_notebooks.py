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

NOTEBOOKS = [
    "01_generate_enterprise_data.ipynb",
    "02_tbm_itfm_data_model.ipynb",
    "03_build_knowledge_graph.ipynb",
    "04_application_cost_intelligence.ipynb",
    "05_capability_cost_intelligence.ipynb",
    "06_consumption_intelligence.ipynb",
    "07_application_rationalization.ipynb",
    "08_dependency_and_impact_analysis.ipynb",
    "09_investment_benefit_realization.ipynb",
    "10_cost_driver_and_variance_analysis.ipynb",
    "11_local_llm_knowledge_graph_analyst.ipynb",
    "12_end_to_end_technology_value_intelligence.ipynb",
]

def execute_single_notebook(nb_path: Path):
    print(f"Executing: {nb_path.name:45s} ...", end=" ", flush=True)
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
