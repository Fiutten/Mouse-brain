"""Generative surrogate layer calibrated to empirical summaries.

This module deliberately implements a modest generator rather than a claimed
whole-brain simulator. Its job is to create synthetic session-level evidence
with the same coarse effect sizes as the Allen-derived summaries, so downstream
agents, graph analyses and reproducibility tooling can be stress-tested before
we add heavier mechanistic detail.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import random


@dataclass(frozen=True)
class GenerativeCalibration:
    """Minimal parameters estimated from empirical evidence reports."""

    target_name: str
    window_name: str
    n_sessions: int
    temporal_gain_mean: float
    temporal_gain_ci95: list[float]
    regional_drops: dict[str, float]
    seed: int

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(frozen=True)
class SyntheticEvidenceSession:
    """One generated session-level evidence sample."""

    session_index: int
    temporal_gain: float
    regional_drops: dict[str, float]


@dataclass(frozen=True)
class GenerativeValidationReport:
    """Validation summary for the generative surrogate layer."""

    calibration: GenerativeCalibration
    generated_sessions: list[SyntheticEvidenceSession]
    mean_temporal_gain: float
    mean_regional_drops: dict[str, float]
    warnings: list[str]

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation."""
        return {
            "calibration": self.calibration.to_dict(),
            "generated_sessions": [asdict(item) for item in self.generated_sessions],
            "mean_temporal_gain": self.mean_temporal_gain,
            "mean_regional_drops": dict(self.mean_regional_drops),
            "warnings": list(self.warnings),
        }


def simulate_evidence_sessions(
    calibration: GenerativeCalibration,
    *,
    n_generated_sessions: int | None = None,
) -> GenerativeValidationReport:
    """Generate session-level evidence from calibrated coarse summaries.

    The temporal sampling scale is inferred from the empirical CI width. This
    makes the surrogate conservative: wide empirical uncertainty produces more
    variable synthetic sessions.
    """
    n = n_generated_sessions or calibration.n_sessions
    if n <= 0:
        raise ValueError("n_generated_sessions must be positive")
    if len(calibration.temporal_gain_ci95) != 2:
        raise ValueError("temporal_gain_ci95 must contain [low, high]")
    rng = random.Random(calibration.seed)
    ci_low, ci_high = calibration.temporal_gain_ci95
    temporal_sigma = max(1e-6, (float(ci_high) - float(ci_low)) / 3.92)
    sessions = []
    for session_index in range(n):
        temporal_gain = rng.gauss(calibration.temporal_gain_mean, temporal_sigma)
        regional_drops = {
            region: rng.gauss(drop, max(1e-6, abs(drop) * 0.35))
            for region, drop in calibration.regional_drops.items()
        }
        sessions.append(
            SyntheticEvidenceSession(
                session_index=session_index,
                temporal_gain=temporal_gain,
                regional_drops=regional_drops,
            )
        )
    mean_temporal = sum(item.temporal_gain for item in sessions) / len(sessions)
    mean_regions = {
        region: sum(item.regional_drops[region] for item in sessions) / len(sessions)
        for region in calibration.regional_drops
    }
    warnings = []
    if calibration.temporal_gain_ci95[0] <= 0.0:
        warnings.append("Empirical temporal CI includes zero; surrogate should be treated as exploratory")
    if not calibration.regional_drops:
        warnings.append("No regional drops were provided; surrogate cannot validate regional structure")
    return GenerativeValidationReport(
        calibration=calibration,
        generated_sessions=sessions,
        mean_temporal_gain=mean_temporal,
        mean_regional_drops=mean_regions,
        warnings=warnings,
    )
