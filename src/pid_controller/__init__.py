import os
import sys
from pathlib import Path


def main() -> None:
    """Open the tutorial in Jupyter Notebook using the project's Python environment."""
    notebook = (
        Path(__file__).resolve().parents[1] / "notebooks" / "01_dc_motor_dynamics.ipynb"
    )
    if not notebook.is_file():
        sys.exit(
            "Tutorial notebook not found. Run this project from its source checkout with uv run pid-controller."
        )

    os.execv(
        sys.executable,
        [sys.executable, "-m", "notebook", str(notebook), *sys.argv[1:]],
    )
