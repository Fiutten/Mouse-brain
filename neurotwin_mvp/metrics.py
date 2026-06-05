"""Metrics used by the prototype.

Metrics are kept separate from models so that baselines, regional simulations
and future trainable models can be compared using the same definitions.
"""

from __future__ import annotations

from .data import Trial


def choice_accuracy(trials: list[Trial], predictions: list[int]) -> float:
    """Compute categorical choice accuracy."""
    if len(trials) != len(predictions):
        raise ValueError("trials and predictions must have equal length")
    if not trials:
        raise ValueError("Cannot evaluate empty trials")
    return sum(int(trial.choice == prediction) for trial, prediction in zip(trials, predictions)) / len(trials)


def behavioral_summary(trials: list[Trial]) -> dict[str, float]:
    """Return compact behavioral/session-level diagnostics."""
    if not trials:
        raise ValueError("Cannot summarize empty trials")
    return {
        "n_trials": float(len(trials)),
        "choice_rate": sum(trial.choice for trial in trials) / len(trials),
        "reward_rate": sum(trial.reward for trial in trials) / len(trials),
        "mean_latency_ms": sum(trial.latency_ms for trial in trials) / len(trials),
        "mean_engagement": sum(trial.engagement for trial in trials) / len(trials),
    }
