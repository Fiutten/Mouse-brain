"""Evaluation for the isolated memory diagnostic task."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from cognitive_organism.envs.advisor_switch_task import AdvisorSwitchTask
from cognitive_organism.learning.baselines import BaselineKind


@dataclass(frozen=True)
class AdvisorMemorySummary:
    algorithm: str
    train_seed: int
    train_steps: int
    trainable_parameters: int
    mean_return: float
    mean_pre_switch_accuracy: float
    mean_post_switch_accuracy: float
    mean_early_post_switch_accuracy: float

    def to_dict(self) -> dict[str, int | float | str]:
        return asdict(self)


def evaluate_advisor_memory_model(
    model: Any,
    *,
    algorithm: BaselineKind | str,
    train_seed: int,
    train_steps: int,
    trainable_parameters: int,
    episodes: int = 100,
    evaluation_seed: int = 200_000,
) -> AdvisorMemorySummary:
    """Evaluate accuracy around the hidden switch using held-out episodes."""

    algorithm = BaselineKind(algorithm)
    env = AdvisorSwitchTask()
    returns: list[float] = []
    pre_accuracy: list[float] = []
    post_accuracy: list[float] = []
    early_post_accuracy: list[float] = []

    for episode in range(episodes):
        observation, _ = env.reset(seed=evaluation_seed + episode)
        state = None
        episode_start = np.ones((1,), dtype=bool)
        correct: list[float] = []
        rewards: list[float] = []
        while True:
            if algorithm is BaselineKind.RECURRENT_PPO:
                action, state = model.predict(
                    observation,
                    state=state,
                    episode_start=episode_start,
                    deterministic=True,
                )
                episode_start[:] = False
            else:
                action, _ = model.predict(observation, deterministic=True)
            observation, reward, _, truncated, info = env.step(int(np.asarray(action).item()))
            rewards.append(float(reward))
            correct.append(float(info["correct_choice"]))
            if truncated:
                break
        split = env.switch_step - 1
        returns.append(sum(rewards))
        pre_accuracy.append(float(np.mean(correct[:split])))
        post_accuracy.append(float(np.mean(correct[split:])))
        early_post_accuracy.append(float(np.mean(correct[split : split + 5])))

    return AdvisorMemorySummary(
        algorithm=algorithm.value,
        train_seed=train_seed,
        train_steps=train_steps,
        trainable_parameters=trainable_parameters,
        mean_return=float(np.mean(returns)),
        mean_pre_switch_accuracy=float(np.mean(pre_accuracy)),
        mean_post_switch_accuracy=float(np.mean(post_accuracy)),
        mean_early_post_switch_accuracy=float(np.mean(early_post_accuracy)),
    )
