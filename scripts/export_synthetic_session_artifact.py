"""Export a synthetic session as a normalized artifact.

This script demonstrates the contract that a future `.venv-allen` exporter must
follow. It runs in the core environment, but writes the same `session.json`
format that Allen/IBL preprocessors should produce.
"""

from __future__ import annotations

from pathlib import Path

from neurotwin_mvp.artifacts import write_session_artifact
from neurotwin_mvp.data import SyntheticNeuropixelsLoader


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Write a synthetic normalized session artifact."""
    session = SyntheticNeuropixelsLoader(seed=7).load()
    output_dir = ROOT / "artifacts" / "datasets" / "synthetic" / session.session_id
    path = write_session_artifact(session, output_dir)
    print(f"session_artifact={path}")


if __name__ == "__main__":
    main()
