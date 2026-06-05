"""Select candidate Allen sessions from metadata without downloading NWB files."""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from neurotwin_mvp.allen_selection import load_allen_session_candidates


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Print the top candidate Allen sessions as JSON."""
    metadata = ROOT / "data" / "allen" / "project_metadata" / "ecephys_sessions.csv"
    candidates = load_allen_session_candidates(metadata)
    print(json.dumps([asdict(item) for item in candidates[:10]], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
