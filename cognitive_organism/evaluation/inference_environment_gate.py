"""Validity gate for the two-adviser social inference environment."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from cognitive_organism.envs.social_inference_world import SocialInferenceWorld
from cognitive_organism.evaluation.environment_gate import PolicySummary

InferencePolicy = Callable[[SocialInferenceWorld, dict[str, np.ndarray], np.random.Generator], int]


def random_action_policy(
    env: SocialInferenceWorld,
    observation: dict[str, np.ndarray],
    rng: np.random.Generator,
) -> int:
    del observation
    return int(rng.integers(env.action_space.n))


def random_adviser_policy(
    env: SocialInferenceWorld,
    observation: dict[str, np.ndarray],
    rng: np.random.Generator,
) -> int:
    del env
    adviser = "advisor_a_direction" if rng.integers(2) == 0 else "advisor_b_direction"
    return int(observation[adviser])


def helpful_oracle_policy(
    env: SocialInferenceWorld,
    observation: dict[str, np.ndarray],
    rng: np.random.Generator,
) -> int:
    del observation, rng
    return int(env._direction_toward(env.resource_pos))


def evaluate_inference_policy(
    policy: InferencePolicy,
    *,
    episodes: int,
    seed: int,
) -> PolicySummary:
    """Evaluate a fixed policy on common switching episodes."""

    env = SocialInferenceWorld()
    rng = np.random.default_rng(seed + 1_000_000)
    returns: list[float] = []
    dangers: list[float] = []
    resources: list[float] = []
    steps: list[int] = []
    for episode in range(episodes):
        observation, _ = env.reset(seed=seed + episode)
        episode_return = 0.0
        episode_danger = 0.0
        episode_resources = 0.0
        episode_steps = 0
        while True:
            action = policy(env, observation, rng)
            observation, reward, terminated, truncated, info = env.step(action)
            episode_return += reward
            episode_danger += info["danger"]
            episode_resources += float(reward > 0.5)
            episode_steps += 1
            if terminated or truncated:
                break
        returns.append(episode_return)
        dangers.append(episode_danger)
        resources.append(episode_resources)
        steps.append(episode_steps)

    return PolicySummary(
        mean_return=float(np.mean(returns)),
        mean_danger=float(np.mean(dangers)),
        mean_danger_rate=float(np.mean(np.asarray(dangers) / np.asarray(steps))),
        mean_resources=float(np.mean(resources)),
        mean_steps=float(np.mean(steps)),
    )


def evaluate_inference_environment_gate(
    *, episodes: int = 100, seed: int = 0
) -> dict[str, PolicySummary]:
    """Compare information-free, memory-free and privileged references."""

    return {
        "random_action": evaluate_inference_policy(random_action_policy, episodes=episodes, seed=seed),
        "random_adviser": evaluate_inference_policy(
            random_adviser_policy, episodes=episodes, seed=seed
        ),
        "helpful_oracle": evaluate_inference_policy(
            helpful_oracle_policy, episodes=episodes, seed=seed
        ),
    }
