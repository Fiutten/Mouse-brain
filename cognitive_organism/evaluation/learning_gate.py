"""Evaluation of trained SB3 agents across the hidden regime switch."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from cognitive_organism.envs.social_inference_world import SocialInferenceWorld
from cognitive_organism.learning.baselines import BaselineKind


@dataclass(frozen=True)
class LearningSummary:
    """Aggregate outcomes split around the prespecified switch step."""

    algorithm: str
    train_seed: int
    episodes: int
    train_steps: int
    trainable_parameters: int
    mean_return: float
    mean_pre_switch_return: float
    mean_post_switch_return: float
    mean_steps: float
    survival_rate: float
    mean_resources: float
    mean_danger_rate: float
    mean_move_rate: float
    action_entropy: float
    pre_switch_helpful_follow_rate: float
    post_switch_helpful_follow_rate: float

    def to_dict(self) -> dict[str, int | float | str]:
        """Serialize without coupling analysis code to dataclass internals."""

        return asdict(self)


def evaluate_learning_model(
    model: Any,
    *,
    algorithm: BaselineKind | str,
    train_seed: int,
    train_steps: int,
    trainable_parameters: int,
    episodes: int = 100,
    evaluation_seed: int = 100_000,
) -> LearningSummary:
    """Evaluate a trained model while preserving recurrent state within episodes."""

    algorithm = BaselineKind(algorithm)
    env = SocialInferenceWorld()
    returns: list[float] = []
    pre_returns: list[float] = []
    post_returns: list[float] = []
    steps: list[int] = []
    survived: list[float] = []
    resources: list[float] = []
    danger_rates: list[float] = []
    move_rates: list[float] = []
    action_counts = np.zeros(env.action_space.n, dtype=np.int64)
    pre_follow: list[float] = []
    post_follow: list[float] = []

    for episode in range(episodes):
        observation, _ = env.reset(seed=evaluation_seed + episode)
        state = None
        episode_start = np.ones((1,), dtype=bool)
        episode_rewards: list[float] = []
        episode_dangers = 0.0
        episode_resources = 0.0
        episode_moves = 0.0
        before_follow: list[float] = []
        after_follow: list[float] = []

        while True:
            helpful_direction = int(env._direction_toward(env.resource_pos))
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
            action_value = int(np.asarray(action).item())
            action_counts[action_value] += 1
            observation, reward, terminated, truncated, info = env.step(action_value)
            episode_rewards.append(float(reward))
            episode_dangers += float(info["danger"])
            episode_resources += float(reward > 0.5)
            episode_moves += float(info["moved"])
            target = after_follow if env.step_count >= env.config.regime_switch_step else before_follow
            target.append(float(action_value == helpful_direction))
            if terminated or truncated:
                break

        switch_index = min(env.config.regime_switch_step - 1, len(episode_rewards))
        returns.append(sum(episode_rewards))
        pre_returns.append(sum(episode_rewards[:switch_index]))
        post_returns.append(sum(episode_rewards[switch_index:]))
        steps.append(len(episode_rewards))
        survived.append(float(truncated and not terminated))
        resources.append(episode_resources)
        danger_rates.append(episode_dangers / len(episode_rewards))
        move_rates.append(episode_moves / len(episode_rewards))
        pre_follow.append(float(np.mean(before_follow)) if before_follow else 0.0)
        post_follow.append(float(np.mean(after_follow)) if after_follow else 0.0)

    action_probabilities = action_counts / action_counts.sum()
    nonzero_probabilities = action_probabilities[action_probabilities > 0]
    action_entropy = float(-np.sum(nonzero_probabilities * np.log(nonzero_probabilities)))
    return LearningSummary(
        algorithm=algorithm.value,
        train_seed=train_seed,
        episodes=episodes,
        train_steps=train_steps,
        trainable_parameters=trainable_parameters,
        mean_return=float(np.mean(returns)),
        mean_pre_switch_return=float(np.mean(pre_returns)),
        mean_post_switch_return=float(np.mean(post_returns)),
        mean_steps=float(np.mean(steps)),
        survival_rate=float(np.mean(survived)),
        mean_resources=float(np.mean(resources)),
        mean_danger_rate=float(np.mean(danger_rates)),
        mean_move_rate=float(np.mean(move_rates)),
        action_entropy=action_entropy,
        pre_switch_helpful_follow_rate=float(np.mean(pre_follow)),
        post_switch_helpful_follow_rate=float(np.mean(post_follow)),
    )
