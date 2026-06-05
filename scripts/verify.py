"""Project verification script.

Runs the checks that must pass before continuing development: unit tests and the
default prototype workflow. It uses the repository root as working directory so
it can be called from any shell location.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str]) -> None:
    """Run one verification command from the repository root."""
    print("+", " ".join(command))
    subprocess.run(command, check=True, cwd=ROOT)


def main() -> None:
    """Run tests and the prototype demo."""
    run([sys.executable, "-m", "unittest", "discover", "-s", "tests"])
    run([sys.executable, "run_prototype.py"])


if __name__ == "__main__":
    main()
