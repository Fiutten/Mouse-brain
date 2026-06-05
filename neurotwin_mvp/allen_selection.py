"""Select Allen Visual Behavior Neuropixels sessions for the first real-data layer.

This module works on project metadata only. It does not download NWB session
files. Its purpose is to choose candidate sessions with enough recorded units
and region coverage to support a realistic first regional digital-twin layer.

Important scientific distinction:

- `unit_count` is the number of recorded/sorted electrophysiological units in a
  session, not the biological number of neurons in the mouse brain.
- The Level-1 real-data layer should use recorded units as empirical anchors.
  It should not invent full-brain neuron counts before we have a calibration
  strategy.
"""

from __future__ import annotations

import ast
import csv
from dataclasses import dataclass
from pathlib import Path


COARSE_REGION_MAP = {
    "visual_cortex": {
        "VISp",
        "VISal",
        "VISam",
        "VISl",
        "VISpm",
        "VISrl",
    },
    "visual_thalamus": {
        "LGd",
        "LGd-sh",
        "LP",
        "APN",
        "TH",
    },
    "hippocampus": {
        "CA1",
        "CA3",
        "DG",
        "DG-mo",
        "DG-po",
        "DG-sg",
        "SUB",
        "POST",
        "PRE",
        "ProS",
        "HPF",
    },
    "basal_ganglia": {
        "SNr",
        "CP",
        "GPe",
        "GPi",
        "STR",
    },
    "arousal_midbrain": {
        "MRN",
        "MB",
        "NB",
        "PPT",
        "ZI",
    },
}


@dataclass(frozen=True)
class AllenSessionCandidate:
    """Ranked metadata candidate for real-data normalization."""

    ecephys_session_id: int
    behavior_session_id: int
    session_type: str
    mouse_id: str
    image_set: str
    experience_level: str
    unit_count: int
    probe_count: int
    channel_count: int
    structure_acronyms: list[str]
    covered_model_regions: list[str]
    abnormal_histology: str
    abnormal_activity: str
    score: float


def parse_structure_acronyms(value: str) -> list[str]:
    """Parse Allen metadata structure acronym lists safely."""
    if not value:
        return []
    parsed = ast.literal_eval(value)
    if not isinstance(parsed, list):
        raise ValueError(f"Expected list of structures, got: {value}")
    return [str(item) for item in parsed]


def covered_model_regions(structures: list[str]) -> list[str]:
    """Map Allen acronyms to coarse model regions represented in a session."""
    observed = set(structures)
    covered = [
        region
        for region, acronyms in COARSE_REGION_MAP.items()
        if observed.intersection(acronyms)
    ]
    return sorted(covered)


def session_score(unit_count: int, probe_count: int, covered_regions: list[str]) -> float:
    """Score a session using unit count, probe count and coarse region coverage."""
    return unit_count + 150.0 * probe_count + 400.0 * len(covered_regions)


def load_allen_session_candidates(
    metadata_csv: str | Path,
    min_units: int = 1500,
    min_probes: int = 4,
    require_regions: set[str] | None = None,
    exclude_abnormal: bool = True,
) -> list[AllenSessionCandidate]:
    """Load and rank candidate sessions from Allen metadata.

    The default thresholds are intentionally conservative for the first
    real-data layer: enough sorted units, multiple probes and broad region
    coverage. This selects sessions that are more likely to support a meaningful
    regional model.
    """
    require_regions = require_regions or {"visual_cortex", "visual_thalamus", "hippocampus"}
    candidates: list[AllenSessionCandidate] = []
    with Path(metadata_csv).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            unit_count = int(float(row["unit_count"]))
            probe_count = int(float(row["probe_count"]))
            channel_count = int(float(row["channel_count"]))
            abnormal_histology = row.get("abnormal_histology", "")
            abnormal_activity = row.get("abnormal_activity", "")
            if unit_count < min_units or probe_count < min_probes:
                continue
            if exclude_abnormal and (abnormal_histology.strip() or abnormal_activity.strip()):
                continue
            structures = parse_structure_acronyms(row["structure_acronyms"])
            covered = covered_model_regions(structures)
            if not require_regions.issubset(set(covered)):
                continue
            candidates.append(
                AllenSessionCandidate(
                    ecephys_session_id=int(row["ecephys_session_id"]),
                    behavior_session_id=int(row["behavior_session_id"]),
                    session_type=row["session_type"],
                    mouse_id=row["mouse_id"],
                    image_set=row["image_set"],
                    experience_level=row["experience_level"],
                    unit_count=unit_count,
                    probe_count=probe_count,
                    channel_count=channel_count,
                    structure_acronyms=structures,
                    covered_model_regions=covered,
                    abnormal_histology=abnormal_histology,
                    abnormal_activity=abnormal_activity,
                    score=session_score(unit_count, probe_count, covered),
                )
            )
    return sorted(candidates, key=lambda item: item.score, reverse=True)
