"""Multi-session evidence synthesis for real-data validation.

This module deliberately separates *model execution* from *scientific
interpretation*. Benchmark, multi-split and permutation reports can be generated
elsewhere; this layer consumes those reports and asks a narrower question:

Do neural region-rate features provide a stable gain across sessions after
basic quality warnings and shuffled-neural controls are considered?

The answer is encoded as explicit rules, not as optimistic prose. That makes the
project easier to audit and prevents a single attractive split from becoming a
biological claim.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
import random
from typing import Any


@dataclass(frozen=True)
class SessionEvidence:
    """Evidence summary for one normalized real-data session."""

    session_id: str
    n_trials: int
    choice_rate: float
    reward_rate: float
    audit_warnings: list[str]
    multisplit_mean_gain: float
    permutation_observed_gain: float
    permutation_p_value: float
    permutation_warnings: list[str]
    benchmark_neural_gain: float | None
    quality_flags: list[str]


@dataclass(frozen=True)
class EvidenceDecision:
    """Rule-based decision about the current evidence base."""

    label: str
    rationale: list[str]
    required_next_steps: list[str]


@dataclass(frozen=True)
class MultiSessionEvidenceReport:
    """Publication-facing synthesis over multiple session reports."""

    n_sessions: int
    total_valid_trials: int
    session_evidence: list[SessionEvidence]
    mean_multisplit_gain: float
    mean_multisplit_gain_ci95: tuple[float, float]
    mean_permutation_observed_gain: float
    mean_permutation_observed_gain_ci95: tuple[float, float]
    positive_multisplit_fraction: float
    significant_permutation_fraction: float
    decision: EvidenceDecision
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return asdict(self)


def synthesize_multisession_evidence(
    session_reports: list[dict[str, Any]],
    *,
    min_sessions_for_claim: int = 8,
    bootstrap_iterations: int = 2000,
    seed: int = 17,
) -> MultiSessionEvidenceReport:
    """Synthesize session-level reports into an explicit evidence decision.

    `session_reports` entries are dictionaries with `audit`, `benchmark`,
    `multisplit` and `permutation` keys, mirroring the generated JSON files.
    """
    if not session_reports:
        raise ValueError("At least one session report is required")
    if bootstrap_iterations <= 0:
        raise ValueError("bootstrap_iterations must be positive")

    session_evidence = [_session_evidence(report) for report in session_reports]
    multisplit_gains = [item.multisplit_mean_gain for item in session_evidence]
    permutation_gains = [item.permutation_observed_gain for item in session_evidence]
    mean_multisplit = _mean(multisplit_gains)
    mean_permutation = _mean(permutation_gains)
    positive_fraction = sum(1 for value in multisplit_gains if value > 0.0) / len(multisplit_gains)
    significant_fraction = (
        sum(1 for item in session_evidence if item.permutation_p_value < 0.05)
        / len(session_evidence)
    )
    warnings = _global_warnings(session_evidence, min_sessions_for_claim)
    decision = _decision(
        session_evidence=session_evidence,
        mean_multisplit_gain=mean_multisplit,
        mean_multisplit_ci=_bootstrap_mean_ci(multisplit_gains, bootstrap_iterations, seed),
        mean_permutation_gain=mean_permutation,
        mean_permutation_ci=_bootstrap_mean_ci(permutation_gains, bootstrap_iterations, seed + 1),
        positive_multisplit_fraction=positive_fraction,
        significant_permutation_fraction=significant_fraction,
        min_sessions_for_claim=min_sessions_for_claim,
    )
    return MultiSessionEvidenceReport(
        n_sessions=len(session_evidence),
        total_valid_trials=sum(item.n_trials for item in session_evidence),
        session_evidence=session_evidence,
        mean_multisplit_gain=mean_multisplit,
        mean_multisplit_gain_ci95=_bootstrap_mean_ci(multisplit_gains, bootstrap_iterations, seed),
        mean_permutation_observed_gain=mean_permutation,
        mean_permutation_observed_gain_ci95=_bootstrap_mean_ci(
            permutation_gains,
            bootstrap_iterations,
            seed + 1,
        ),
        positive_multisplit_fraction=positive_fraction,
        significant_permutation_fraction=significant_fraction,
        decision=decision,
        warnings=warnings,
    )


def _session_evidence(report: dict[str, Any]) -> SessionEvidence:
    audit = report["audit"]
    benchmark = report["benchmark"]
    multisplit = report["multisplit"]
    permutation = report["permutation"]
    session_id = str(audit["session_id"])
    if session_id != str(multisplit["session_id"]) or session_id != str(permutation["session_id"]):
        raise ValueError(f"Mismatched session ids in report bundle for {session_id}")
    return SessionEvidence(
        session_id=session_id,
        n_trials=int(audit["n_trials"]),
        choice_rate=float(audit["choice_rate"]),
        reward_rate=float(audit["reward_rate"]),
        audit_warnings=[str(item) for item in audit.get("warnings", [])],
        multisplit_mean_gain=float(multisplit["mean_gain"]),
        permutation_observed_gain=float(permutation["observed_gain"]),
        permutation_p_value=float(permutation["p_value"]),
        permutation_warnings=[str(item) for item in permutation.get("warnings", [])],
        benchmark_neural_gain=_benchmark_compact_neural_gain(benchmark),
        quality_flags=_quality_flags(audit, permutation),
    )


def _benchmark_compact_neural_gain(benchmark: dict[str, Any]) -> float | None:
    results = {item["name"]: item for item in benchmark.get("results", [])}
    baseline = results.get("logistic_task_compact_image_history")
    neural = results.get("logistic_task_compact_image_history_region_rates")
    if baseline is None or neural is None:
        return None
    baseline_balanced = baseline.get("details", {}).get("balanced_accuracy")
    neural_balanced = neural.get("details", {}).get("balanced_accuracy")
    if baseline_balanced is not None and neural_balanced is not None:
        return float(neural_balanced) - float(baseline_balanced)
    return float(neural["accuracy"]) - float(baseline["accuracy"])


def _quality_flags(audit: dict[str, Any], permutation: dict[str, Any]) -> list[str]:
    flags: list[str] = []
    n_trials = int(audit["n_trials"])
    choice_rate = float(audit["choice_rate"])
    reward_rate = float(audit["reward_rate"])
    if n_trials < 200:
        flags.append("low_trial_count")
    if min(choice_rate, 1.0 - choice_rate) < 0.20:
        flags.append("choice_imbalance")
    if min(reward_rate, 1.0 - reward_rate) < 0.20:
        flags.append("reward_imbalance")
    if float(permutation["p_value"]) >= 0.05:
        flags.append("permutation_not_significant")
    if float(permutation["observed_gain"]) <= 0.0:
        flags.append("non_positive_permutation_gain")
    return flags


def _global_warnings(
    session_evidence: list[SessionEvidence],
    min_sessions_for_claim: int,
) -> list[str]:
    warnings: list[str] = []
    if len(session_evidence) < min_sessions_for_claim:
        warnings.append(
            f"Only {len(session_evidence)} sessions available; at least "
            f"{min_sessions_for_claim} are required for a positive claim"
        )
    if any("choice_imbalance" in item.quality_flags for item in session_evidence):
        warnings.append("At least one session has strongly imbalanced choices")
    if any("low_trial_count" in item.quality_flags for item in session_evidence):
        warnings.append("At least one session has fewer than 200 valid trials")
    if all(item.permutation_p_value >= 0.05 for item in session_evidence):
        warnings.append("No session rejects the shuffled-neural permutation null")
    return warnings


def _decision(
    *,
    session_evidence: list[SessionEvidence],
    mean_multisplit_gain: float,
    mean_multisplit_ci: tuple[float, float],
    mean_permutation_gain: float,
    mean_permutation_ci: tuple[float, float],
    positive_multisplit_fraction: float,
    significant_permutation_fraction: float,
    min_sessions_for_claim: int,
) -> EvidenceDecision:
    rationale: list[str] = []
    required_next_steps: list[str] = []

    enough_sessions = len(session_evidence) >= min_sessions_for_claim
    stable_positive = (
        mean_multisplit_gain > 0.0
        and mean_multisplit_ci[0] > 0.0
        and mean_permutation_gain > 0.0
        and mean_permutation_ci[0] > 0.0
        and positive_multisplit_fraction >= 0.70
        and significant_permutation_fraction >= 0.50
    )
    stable_negative_or_null = (
        mean_multisplit_gain <= 0.0
        or mean_permutation_gain <= 0.0
        or positive_multisplit_fraction < 0.50
    )

    rationale.append(
        f"mean multi-split gain={mean_multisplit_gain:.3f}, "
        f"CI95=({mean_multisplit_ci[0]:.3f}, {mean_multisplit_ci[1]:.3f})"
    )
    rationale.append(
        f"mean permutation observed gain={mean_permutation_gain:.3f}, "
        f"CI95=({mean_permutation_ci[0]:.3f}, {mean_permutation_ci[1]:.3f})"
    )
    rationale.append(
        f"positive multi-split fraction={positive_multisplit_fraction:.3f}; "
        f"significant permutation fraction={significant_permutation_fraction:.3f}"
    )

    if enough_sessions and stable_positive:
        return EvidenceDecision(
            label="positive_evidence",
            rationale=rationale
            + ["Evidence passes session-count, stability and permutation-control thresholds"],
            required_next_steps=[
                "replicate on held-out sessions not used for model selection",
                "run richer behavioral targets before making mechanistic claims",
            ],
        )

    if stable_negative_or_null:
        required_next_steps.extend(
            [
                "export additional sessions until the planned minimum evidence base is reached",
                "replace binary choice with task-native Allen targets",
                "add temporally resolved neural features before adding biological layers",
            ]
        )
        label = "negative_or_null_trend" if enough_sessions else "inconclusive_negative_trend"
        return EvidenceDecision(
            label=label,
            rationale=rationale
            + ["Current neural-feature gain is not stable enough for a positive claim"],
            required_next_steps=required_next_steps,
        )

    return EvidenceDecision(
        label="inconclusive_mixed_evidence",
        rationale=rationale + ["Effects are mixed and do not meet positive-evidence thresholds"],
        required_next_steps=[
            "increase session count",
            "stratify by trial balance and animal",
            "inspect whether gains are driven by a small subset of sessions",
        ],
    )


def _bootstrap_mean_ci(values: list[float], iterations: int, seed: int) -> tuple[float, float]:
    if not values:
        raise ValueError("Cannot bootstrap an empty value list")
    rng = random.Random(seed)
    means = []
    for _ in range(iterations):
        sample = [values[rng.randrange(len(values))] for _ in values]
        means.append(_mean(sample))
    means.sort()
    lower = means[_quantile_index(len(means), 0.025)]
    upper = means[_quantile_index(len(means), 0.975)]
    return (lower, upper)


def _quantile_index(n: int, quantile: float) -> int:
    return max(0, min(n - 1, int(math.floor((n - 1) * quantile))))


def _mean(values: list[float]) -> float:
    if not values:
        raise ValueError("Cannot compute mean of an empty value list")
    return sum(values) / len(values)
