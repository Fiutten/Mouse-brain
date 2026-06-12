"""Selection utilities for recurrent baseline stabilization."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from statistics import mean
from typing import Iterable


@dataclass(frozen=True)
class ConfigurationScore:
    """Robust development score for one recurrent configuration."""

    config_name: str
    worst_post_switch_accuracy: float
    mean_post_switch_accuracy: float
    trainable_parameters: int


def score_configurations(rows: Iterable[dict[str, int | float | str]]) -> list[ConfigurationScore]:
    """Aggregate development rows using the prespecified robust criterion."""

    grouped: dict[str, list[dict[str, int | float | str]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["config_name"])].append(row)

    scores = []
    for name, group in grouped.items():
        accuracies = [float(row["mean_post_switch_accuracy"]) for row in group]
        parameter_counts = {int(row["trainable_parameters"]) for row in group}
        if len(parameter_counts) != 1:
            raise ValueError(f"inconsistent parameter counts for {name}")
        scores.append(
            ConfigurationScore(
                config_name=name,
                worst_post_switch_accuracy=min(accuracies),
                mean_post_switch_accuracy=mean(accuracies),
                trainable_parameters=parameter_counts.pop(),
            )
        )
    return sorted(
        scores,
        key=lambda score: (
            -score.worst_post_switch_accuracy,
            -score.mean_post_switch_accuracy,
            score.trainable_parameters,
            score.config_name,
        ),
    )
