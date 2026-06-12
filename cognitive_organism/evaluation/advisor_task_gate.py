"""Non-learning references for validating the isolated adviser-switch task."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from cognitive_organism.envs.advisor_switch_task import AdvisorSwitchTask


@dataclass(frozen=True)
class AdvisorReferenceSummary:
    """Accuracy summary for a fixed reference controller."""

    mean_return: float
    pre_switch_accuracy: float
    post_switch_accuracy: float
    early_post_switch_accuracy: float


def evaluate_reference(
    name: str,
    *,
    episodes: int = 200,
    seed: int = 300_000,
) -> AdvisorReferenceSummary:
    """Evaluate random, reactive, or one-bit-memory reference controllers."""

    if name not in {"random", "always_zero", "win_stay_lose_shift"}:
        raise ValueError(f"unknown reference: {name}")

    env = AdvisorSwitchTask()
    rng = np.random.default_rng(seed + 1_000_000)
    returns: list[float] = []
    pre_accuracy: list[float] = []
    post_accuracy: list[float] = []
    early_post_accuracy: list[float] = []

    for episode in range(episodes):
        observation, _ = env.reset(seed=seed + episode)
        previous_action = int(rng.integers(2))
        correct: list[float] = []
        rewards: list[float] = []
        while True:
            if name == "random":
                action = int(rng.integers(2))
            elif name == "always_zero":
                action = 0
            elif float(observation["last_outcome"][0]) < 0:
                action = 1 - previous_action
            else:
                action = previous_action

            previous_action = action
            observation, reward, _, truncated, info = env.step(action)
            rewards.append(float(reward))
            correct.append(float(info["correct_choice"]))
            if truncated:
                break

        split = env.switch_step - 1
        returns.append(sum(rewards))
        pre_accuracy.append(float(np.mean(correct[:split])))
        post_accuracy.append(float(np.mean(correct[split:])))
        early_post_accuracy.append(float(np.mean(correct[split : split + 5])))

    return AdvisorReferenceSummary(
        mean_return=float(np.mean(returns)),
        pre_switch_accuracy=float(np.mean(pre_accuracy)),
        post_switch_accuracy=float(np.mean(post_accuracy)),
        early_post_switch_accuracy=float(np.mean(early_post_accuracy)),
    )
