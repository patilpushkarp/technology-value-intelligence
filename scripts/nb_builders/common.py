"""Common utilities for building deep, advanced TVI notebooks."""

from pathlib import Path
import nbformat as nbf


def make_nb():
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        "kernelspec": {
            "display_name": "Python 3 (technology-value-intelligence)",
            "language": "python",
            "name": "technology-value-intelligence",
        },
        "language_info": {
            "name": "python",
            "version": "3.13.1",
        },
    }
    return nb


def add_md(nb, text):
    nb.cells.append(nbf.v4.new_markdown_cell(text.strip()))


def add_code(nb, code):
    nb.cells.append(nbf.v4.new_code_cell(code.strip()))


def save_nb(nb, filename):
    workspace_root = Path(__file__).resolve().parent.parent.parent
    out_path = workspace_root / "notebooks" / filename
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"✓ Saved deep notebook: {out_path.name} ({len(nb.cells)} cells)")
