"""Execute every Lesson 04 notebook without modifying the checked-in sources."""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path
from typing import Sequence


DEFAULT_NOTEBOOK_ROOT = Path("/workspace/labs/spark/notebooks")


def parse_args() -> argparse.Namespace:
    """Parse the notebook directory used by the smoke runner."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--notebook-root",
        type=Path,
        default=DEFAULT_NOTEBOOK_ROOT,
        help="Directory containing the checked-in .ipynb demos.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=300,
        help="Maximum execution time for each notebook.",
    )
    return parser.parse_args()


def discover_notebooks(notebook_root: Path) -> Sequence[Path]:
    """Return demos in deterministic teaching order."""

    notebooks = tuple(sorted(notebook_root.glob("[0-9][0-9]_*.ipynb")))
    if not notebooks:
        raise FileNotFoundError(f"No demo notebooks found under {notebook_root}")
    return notebooks


def execute_notebook(source: Path, output_root: Path, timeout_seconds: int) -> None:
    """Run one notebook through nbconvert and keep outputs outside the repo."""

    command = [
        "jupyter",
        "nbconvert",
        "--to",
        "notebook",
        "--execute",
        str(source),
        "--output",
        source.name,
        "--output-dir",
        str(output_root),
        f"--ExecutePreprocessor.timeout={timeout_seconds}",
    ]
    subprocess.run(command, check=True)


def main() -> None:
    """Execute all notebooks and report a compact acceptance marker."""

    args = parse_args()
    notebooks = discover_notebooks(args.notebook_root)
    with tempfile.TemporaryDirectory(prefix="de-mentor-notebooks-") as temp_dir:
        output_root = Path(temp_dir)
        for notebook in notebooks:
            print(f"RUN notebook: {notebook.name}", flush=True)
            execute_notebook(notebook, output_root, args.timeout_seconds)
            print(f"PASS notebook: {notebook.name}", flush=True)
    print(f"PASS notebook_suite: {len(notebooks)} demos", flush=True)


if __name__ == "__main__":
    main()
