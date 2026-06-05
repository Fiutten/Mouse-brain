"""Simple baselines for behavioral prediction.

Baselines are not an afterthought in this project. They are the guardrail
against building a biologically themed model that performs no better than a
simple rule. The first baselines are intentionally basic; stronger baselines
must be added before any scientific claim.
"""

from __future__ import annotations

from dataclasses import dataclass

from .data import Trial


@dataclass(frozen=True)
class BaselineReport:
    """Evaluation summary for a baseline model."""

    name: str
    accuracy: float
    n_train: int
    n_test: int
    details: dict[str, float]


class StimulusRuleBaseline:
    """Predict choice directly from stimulus sign.

    This is intentionally simple. If our later model cannot beat or explain
    this baseline under richer settings, it has no scientific value.
    """

    name = "stimulus_rule"

    def fit(self, trials: list[Trial]) -> None:
        """Validate training data; the rule itself has no learned parameters."""
        if not trials:
            raise ValueError("Cannot fit baseline on empty trials")

    def predict(self, trial: Trial) -> int:
        """Choose right/positive action for positive stimulus."""
        return 1 if trial.stimulus > 0 else 0


class MajorityChoiceBaseline:
    """Predict the most common training-set choice."""

    name = "majority_choice"

    def __init__(self) -> None:
        self.choice = 1

    def fit(self, trials: list[Trial]) -> None:
        """Estimate the majority choice from training trials."""
        if not trials:
            raise ValueError("Cannot fit baseline on empty trials")
        positives = sum(trial.choice for trial in trials)
        self.choice = 1 if positives >= len(trials) / 2 else 0

    def predict(self, trial: Trial) -> int:
        """Return the fitted majority choice."""
        return self.choice


def evaluate_classifier(model, train: list[Trial], test: list[Trial]) -> BaselineReport:
    """Fit a baseline and evaluate choice accuracy on held-out trials."""
    if not test:
        raise ValueError("Cannot evaluate baseline on empty test trials")
    model.fit(train)
    correct = sum(1 for trial in test if model.predict(trial) == trial.choice)
    accuracy = correct / len(test)
    return BaselineReport(
        name=model.name,
        accuracy=accuracy,
        n_train=len(train),
        n_test=len(test),
        details={"correct": float(correct)},
    )
