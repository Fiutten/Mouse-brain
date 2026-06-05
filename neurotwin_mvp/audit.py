"""Audit normalized neural-session artifacts before modeling.

A real-data artifact should be treated as suspect until basic diagnostics pass.
This module summarizes behavior, timing and region-rate features using only the
core `Session` contract, so it can audit synthetic, Allen or future IBL exports
without importing dataset-specific SDKs.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
import math

from .data import Session, Trial


@dataclass(frozen=True)
class NumericSummary:
    """Compact descriptive statistics for one numeric field."""

    count: int
    mean: float
    minimum: float
    maximum: float
    std: float


@dataclass(frozen=True)
class SessionAudit:
    """Quality and descriptive summary of a normalized session artifact."""

    session_id: str
    dataset: str
    animal_id: str
    n_trials: int
    n_regions: int
    region_names: list[str]
    choice_rate: float
    reward_rate: float
    positive_stimulus_rate: float
    zero_stimulus_rate: float
    latency_ms: NumericSummary
    engagement: NumericSummary
    region_rates: dict[str, NumericSummary]
    warnings: list[str]

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation."""
        return asdict(self)


def summarize_values(values: list[float]) -> NumericSummary:
    """Summarize a non-empty list of finite numeric values."""
    if not values:
        raise ValueError("Cannot summarize an empty value list")
    if any(not math.isfinite(value) for value in values):
        raise ValueError("Cannot summarize non-finite values")
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    return NumericSummary(
        count=len(values),
        mean=mean,
        minimum=min(values),
        maximum=max(values),
        std=math.sqrt(variance),
    )


def _binary_rate(trials: list[Trial], attr: str) -> float:
    return sum(int(getattr(trial, attr)) for trial in trials) / len(trials)


def audit_session(session: Session) -> SessionAudit:
    """Compute quality diagnostics and warnings for one normalized session."""
    if not session.trials:
        raise ValueError("Cannot audit a session without trials")
    warnings: list[str] = []
    region_names = list(session.region_names)
    missing_regions = {
        region
        for trial in session.trials
        for region in region_names
        if region not in trial.region_rates
    }
    if missing_regions:
        warnings.append(f"Missing region rates for regions: {sorted(missing_regions)}")

    choice_rate = _binary_rate(session.trials, "choice")
    reward_rate = _binary_rate(session.trials, "reward")
    positive_stimulus_rate = sum(1 for trial in session.trials if trial.stimulus > 0) / len(session.trials)
    zero_stimulus_rate = sum(1 for trial in session.trials if trial.stimulus == 0.0) / len(session.trials)

    if choice_rate in {0.0, 1.0}:
        warnings.append("Choices are degenerate; behavioral prediction is not meaningful")
    elif min(choice_rate, 1.0 - choice_rate) < 0.20:
        warnings.append("Choices are strongly imbalanced; report balanced accuracy")
    if reward_rate in {0.0, 1.0}:
        warnings.append("Rewards are degenerate; reward-based validation is not meaningful")
    elif min(reward_rate, 1.0 - reward_rate) < 0.20:
        warnings.append("Rewards are strongly imbalanced; reward prediction needs stratified analysis")
    if positive_stimulus_rate in {0.0, 1.0}:
        warnings.append("Stimulus sign is degenerate; stimulus-rule baselines are not meaningful")
    if len(session.trials) < 200:
        warnings.append("Fewer than 200 trials; benchmark estimates are preliminary")

    latencies = [trial.latency_ms for trial in session.trials]
    if sum(1 for latency in latencies if latency == 0.0) / len(latencies) > 0.25:
        warnings.append("More than 25% of latencies are zero; response-time extraction needs review")

    region_rates: dict[str, NumericSummary] = {}
    for region in region_names:
        values = [trial.region_rates.get(region, 0.0) for trial in session.trials]
        summary = summarize_values(values)
        region_rates[region] = summary
        if summary.std == 0.0:
            warnings.append(f"Region {region} has zero rate variance")

    return SessionAudit(
        session_id=session.session_id,
        dataset=session.dataset,
        animal_id=session.animal_id,
        n_trials=len(session.trials),
        n_regions=len(region_names),
        region_names=region_names,
        choice_rate=choice_rate,
        reward_rate=reward_rate,
        positive_stimulus_rate=positive_stimulus_rate,
        zero_stimulus_rate=zero_stimulus_rate,
        latency_ms=summarize_values(latencies),
        engagement=summarize_values([trial.engagement for trial in session.trials]),
        region_rates=region_rates,
        warnings=warnings,
    )
