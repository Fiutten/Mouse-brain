"""Experiment routines for baseline trials and virtual lesions.

Virtual lesions are counterfactual probes of the model architecture. They ask
questions such as "does disabling the visual relay reduce stimulus sensitivity
in this model?" They do not establish biological causality unless their
predictions are validated against empirical perturbation evidence.
"""

from __future__ import annotations

from dataclasses import dataclass

from .regional_model import RegionalModel, summarize_trial


@dataclass(frozen=True)
class LesionResult:
    """Summary of one virtual lesion probe."""

    lesion: str
    positive_stimulus_probability: float
    negative_stimulus_probability: float
    sensitivity: float


def evaluate_visual_decision(
    model: RegionalModel,
    lesion: str | None = None,
    repeats: int = 30,
    delay_steps: int = 4,
    decision_steps: int = 4,
) -> LesionResult:
    """Evaluate stimulus sensitivity under an optional virtual lesion.

    The metric is the final action-probability gap between positive and
    negative stimuli. In this synthetic task, visual pathway lesions should
    reduce the gap. This is a model sanity check, not a scientific lesion claim.
    """
    if repeats <= 0:
        raise ValueError("repeats must be positive")
    lesions = {lesion} if lesion else set()
    pos = []
    neg = []
    for _ in range(repeats):
        model.reset()
        pos.append(summarize_trial(model.run_trial(1.0, delay_steps, decision_steps, lesions))["final_action_probability"])
        model.reset()
        neg.append(summarize_trial(model.run_trial(-1.0, delay_steps, decision_steps, lesions))["final_action_probability"])
    pos_mean = sum(pos) / len(pos)
    neg_mean = sum(neg) / len(neg)
    return LesionResult(
        lesion=lesion or "none",
        positive_stimulus_probability=pos_mean,
        negative_stimulus_probability=neg_mean,
        sensitivity=pos_mean - neg_mean,
    )


def lesion_sweep(model: RegionalModel, regions: list[str] | None = None) -> list[LesionResult]:
    """Run intact and per-region virtual lesion probes."""
    selected = regions or model.region_names
    return [evaluate_visual_decision(model, None)] + [
        evaluate_visual_decision(model, region) for region in selected
    ]
