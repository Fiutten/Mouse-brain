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
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


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


@dataclass(frozen=True)
class TargetAwareCandidate:
    """Candidate ranked by metadata quality and learned target viability.

    The selector is intentionally conservative: it does not claim that metadata
    can fully predict a useful Allen session. It combines the existing
    anatomical/recording-quality score with empirical rates observed in already
    normalized sessions, so expansion can avoid repeatedly downloading sessions
    that resemble known target-balance failures.
    """

    candidate: AllenSessionCandidate
    selector_score: float
    target_viability_score: float
    neural_evidence_score: float
    metadata_quality_score: float
    rationale: list[str]


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


def load_target_relation_rows(path: str | Path) -> list[dict[str, Any]]:
    """Load per-session rows from a target-relation report.

    The current report stores rows under `sessions`; older drafts used `rows`.
    Supporting both keeps the selector stable across already generated
    artifacts and avoids unnecessary regeneration when only the selector changes.
    """
    report_path = Path(path)
    if not report_path.exists():
        return []
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    rows = payload.get("sessions", payload.get("rows", []))
    if not isinstance(rows, list):
        raise ValueError(f"Expected list of session rows in {report_path}")
    return [row for row in rows if isinstance(row, dict)]


def exported_session_ids(datasets_root: str | Path) -> set[int]:
    """Return ecephys session ids that already have normalized artifacts."""
    root = Path(datasets_root)
    result: set[int] = set()
    for session_json in root.glob("*/session.json"):
        try:
            result.add(int(session_json.parent.name))
        except ValueError:
            continue
    return result


def _as_bool(value: Any) -> bool:
    """Convert JSON/CSV-style booleans into Python booleans."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes"}
    return bool(value)


def _smoothed_rate(
    rows: list[dict[str, Any]],
    *,
    field: str,
    value: str,
    target_field: str,
    prior_rate: float,
    prior_strength: float = 4.0,
) -> tuple[float, int]:
    """Estimate a small-sample category rate with a weak empirical prior.

    Allen session metadata is sparse at our current 40-session scale. A raw
    group rate such as "2/2 usable" would overfit badly, so every category is
    shrunk toward the global prior before it affects candidate ranking.
    """
    matching = [row for row in rows if str(row.get(field) or "unknown") == value]
    successes = sum(1 for row in matching if _as_bool(row.get(target_field)))
    total = len(matching)
    rate = (successes + prior_rate * prior_strength) / (total + prior_strength)
    return rate, total


def _weighted_mean(items: list[tuple[float, float]]) -> float:
    """Return a weighted mean with a neutral fallback."""
    total_weight = sum(weight for _, weight in items)
    if total_weight <= 0.0:
        return 0.5
    return sum(value * weight for value, weight in items) / total_weight


def rank_target_aware_candidates(
    candidates: list[AllenSessionCandidate],
    relation_rows: list[dict[str, Any]],
    *,
    datasets_root: str | Path,
    top_n: int = 20,
    exclude_exported: bool = True,
) -> list[TargetAwareCandidate]:
    """Rank pending Allen candidates for a target-aware expansion.

    The score has three explicit components:

    - target viability: does the candidate resemble sessions with usable target
      balance?
    - neural evidence: does it resemble sessions with permutation-significant
      neural gain? This has low weight because the cohort is small.
    - metadata quality: the pre-existing unit/probe/region coverage score.

    This is a prioritization tool, not a confirmatory model. Its output should
    guide the next download order and should be audited after every batch.
    """
    exported = exported_session_ids(datasets_root) if exclude_exported else set()
    pending = [
        candidate
        for candidate in candidates
        if candidate.ecephys_session_id not in exported
    ]
    if not pending:
        return []

    usable_prior = (
        sum(1 for row in relation_rows if _as_bool(row.get("go_usable"))) / len(relation_rows)
        if relation_rows
        else 0.5
    )
    evidence_rows = [row for row in relation_rows if _as_bool(row.get("in_strict_evidence"))]
    evidence_prior = (
        sum(1 for row in evidence_rows if _as_bool(row.get("permutation_significant"))) / len(evidence_rows)
        if evidence_rows
        else 0.2
    )
    max_metadata_score = max(candidate.score for candidate in pending) or 1.0

    ranked: list[TargetAwareCandidate] = []
    for candidate in pending:
        viability_items: list[tuple[float, float]] = []
        evidence_items: list[tuple[float, float]] = []
        rationale: list[str] = []

        feature_values = [
            ("session_type", candidate.session_type, 0.45),
            ("image_set", candidate.image_set, 0.30),
            ("experience_level", candidate.experience_level or "unknown", 0.25),
        ]
        for field, value, weight in feature_values:
            viability_rate, n_viability = _smoothed_rate(
                relation_rows,
                field=field,
                value=str(value),
                target_field="go_usable",
                prior_rate=usable_prior,
            )
            evidence_rate, n_evidence = _smoothed_rate(
                evidence_rows,
                field=field,
                value=str(value),
                target_field="permutation_significant",
                prior_rate=evidence_prior,
            )
            viability_items.append((viability_rate, weight))
            evidence_items.append((evidence_rate, weight))
            rationale.append(
                f"{field}={value}: usable_rate={viability_rate:.3f} n={n_viability}; "
                f"significant_rate={evidence_rate:.3f} n={n_evidence}"
            )

        viability_score = _weighted_mean(viability_items)
        evidence_score = _weighted_mean(evidence_items)
        metadata_quality_score = candidate.score / max_metadata_score
        selector_score = (
            0.55 * viability_score
            + 0.15 * evidence_score
            + 0.30 * metadata_quality_score
        )
        ranked.append(
            TargetAwareCandidate(
                candidate=candidate,
                selector_score=selector_score,
                target_viability_score=viability_score,
                neural_evidence_score=evidence_score,
                metadata_quality_score=metadata_quality_score,
                rationale=rationale,
            )
        )

    return sorted(ranked, key=lambda item: item.selector_score, reverse=True)[:top_n]
