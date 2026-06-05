"""Normalized artifact exchange between Python environments.

The project intentionally supports multiple Python environments:

- core environment: simulation, baselines, registry and tests;
- Allen environment: AllenSDK/NWB extraction and normalization;
- optional IBL environment: ONE/OpenAlyx extraction and normalization.

These environments must not import each other at runtime. They communicate by
writing and reading transparent normalized artifacts. This module defines the
core-side artifact contract for `Session` objects.

Current format:

```text
session_dir/
  session.json
```

The JSON format is deliberately simple for early inspection. It can later be
extended to CSV/Parquet for large real sessions while keeping the same logical
contract.
"""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from .data import Session, Trial


SESSION_JSON = "session.json"


def write_session_artifact(session: Session, output_dir: str | Path) -> Path:
    """Write a normalized `Session` artifact.

    This is the format that an Allen-specific environment should produce after
    extracting trials, behavior and region-level spike-rate features. The core
    environment can then consume it without importing AllenSDK.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / SESSION_JSON
    path.write_text(
        json.dumps(asdict(session), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return path


def read_session_artifact(input_dir: str | Path) -> Session:
    """Read a normalized `Session` artifact produced by another environment."""
    path = Path(input_dir) / SESSION_JSON
    data = json.loads(path.read_text(encoding="utf-8"))
    trials = [
        Trial(
            trial_id=int(item["trial_id"]),
            stimulus=float(item["stimulus"]),
            choice=int(item["choice"]),
            reward=int(item["reward"]),
            latency_ms=float(item["latency_ms"]),
            engagement=float(item["engagement"]),
            region_rates={str(k): float(v) for k, v in item["region_rates"].items()},
            metadata={str(k): v for k, v in item.get("metadata", {}).items()},
        )
        for item in data["trials"]
    ]
    return Session(
        session_id=str(data["session_id"]),
        animal_id=str(data["animal_id"]),
        dataset=str(data["dataset"]),
        trials=trials,
        region_names=[str(item) for item in data["region_names"]],
    )


class ArtifactSessionLoader:
    """Session loader that consumes a normalized session artifact directory."""

    def __init__(self, artifact_dir: str | Path) -> None:
        self.artifact_dir = Path(artifact_dir)

    def load(self) -> Session:
        """Load the session artifact using the core environment only."""
        return read_session_artifact(self.artifact_dir)
