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

from .data import Session, Trial


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


@dataclass(frozen=True)
class SessionGeneratorCalibration:
    """Parameters for generating normalized synthetic session artifacts."""

    target_name: str
    window_names: list[str]
    region_names: list[str]
    n_trials: int
    positive_rate: float
    latency_mean_ms: float
    latency_std_ms: float
    region_window_means: dict[str, dict[str, float]]
    seed: int

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(frozen=True)
class GeneratedSessionReport:
    """Generated normalized session plus calibration metadata."""

    calibration: SessionGeneratorCalibration
    session: Session
    warnings: list[str]

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation without losing structure."""
        return {
            "calibration": self.calibration.to_dict(),
            "session": asdict(self.session),
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


def generate_calibrated_session(calibration: SessionGeneratorCalibration) -> GeneratedSessionReport:
    """Generate a normalized session with temporal region-window metadata.

    The generator samples trials from empirical distribution summaries. It is
    designed for pipeline stress tests and ablation sanity checks. It should
    never be mixed with empirical Allen evidence when making biological claims.
    """
    if calibration.n_trials <= 1:
        raise ValueError("n_trials must be greater than 1")
    rng = random.Random(calibration.seed)
    trials = []
    warnings = []
    for trial_id in range(calibration.n_trials):
        label = 1 if rng.random() < calibration.positive_rate else 0
        stimulus = 1.0 if rng.random() < 0.5 else -1.0
        latency = max(40.0, rng.gauss(calibration.latency_mean_ms, calibration.latency_std_ms))
        engagement = max(0.0, min(1.0, rng.gauss(0.62, 0.12)))
        region_rates_by_window = {}
        for window in calibration.window_names:
            means = calibration.region_window_means.get(window, {})
            window_rates = {}
            for region in calibration.region_names:
                mean_rate = float(means.get(region, 0.0))
                signal = 0.15 * label if window == "pre_response" and region == "visual_cortex" else 0.0
                window_rates[region] = rng.gauss(mean_rate + signal, max(0.05, abs(mean_rate) * 0.10))
            region_rates_by_window[window] = window_rates
        primary_window = "pre_response" if "pre_response" in region_rates_by_window else calibration.window_names[-1]
        trials.append(
            Trial(
                trial_id=trial_id,
                stimulus=stimulus,
                choice=label,
                reward=int(label == 1),
                latency_ms=latency,
                engagement=engagement,
                region_rates=dict(region_rates_by_window[primary_window]),
                metadata={
                    "target_name": calibration.target_name,
                    "synthetic_calibrated": True,
                    "go": True,
                    "hit": bool(label == 1),
                    "miss": bool(label == 0),
                    "region_rates_by_window": region_rates_by_window,
                    "time_window_valid": {window: True for window in calibration.window_names},
                },
            )
        )
    if not calibration.region_window_means:
        warnings.append("No empirical region-window means supplied; generated rates are weakly anchored")
    session = Session(
        session_id="generated_calibrated_session_v2",
        animal_id="synthetic_calibrated_mouse",
        dataset="calibrated-surrogate",
        trials=trials,
        region_names=list(calibration.region_names),
    )
    return GeneratedSessionReport(
        calibration=calibration,
        session=session,
        warnings=warnings,
    )
