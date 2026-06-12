"""Scientific validity checks for the minimal environment.

These baselines are not candidate cognitive architectures. They test whether the
environment contains the intended causal structure before expensive training is
allowed.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from cognitive_organism.envs.social_survival_world import Action, SocialSurvivalWorld, WorldConfig

Policy = Callable[[SocialSurvivalWorld, dict[str, np.ndarray], np.random.Generator], int]


@dataclass(frozen=True)
class PolicySummary:
    """Aggregate outcomes for one fixed policy."""

    mean_return: float
    mean_danger: float
    mean_danger_rate: float
    mean_resources: float
    mean_steps: float


def random_policy(
    env: SocialSurvivalWorld, observation: dict[str, np.ndarray], rng: np.random.Generator
) -> int:
    """Select uniformly without using observations."""

    del env, observation
    return int(rng.integers(len(Action)))


def social_follower_policy(
    env: SocialSurvivalWorld, observation: dict[str, np.ndarray], rng: np.random.Generator
) -> int:
    """Follow the social channel without inferring whether it is deceptive."""

    del env, rng
    return int(observation["social_direction"])


def privileged_oracle_policy(
    env: SocialSurvivalWorld, observation: dict[str, np.ndarray], rng: np.random.Generator
) -> int:
    """Use hidden state to establish an upper reference, never as a trainable agent."""

    del observation, rng
    return int(env._direction_toward(env.resource_pos))


def evaluate_policy(
    policy: Policy,
    *,
    episodes: int = 100,
    seed: int = 0,
    helpful_regime: bool | None = None,
) -> PolicySummary:
    """Evaluate a fixed policy on a reproducible sequence of episodes."""

    if episodes < 1:
        raise ValueError("episodes must be positive")

    # Fixed-regime comparisons isolate adviser reliability. The default
    # switching environment is retained for random/oracle solvability checks.
    config = WorldConfig(regime_switch_step=None) if helpful_regime is not None else WorldConfig()
    env = SocialSurvivalWorld(config)
    policy_rng = np.random.default_rng(seed + 1_000_000)
    returns: list[float] = []
    dangers: list[float] = []
    resources: list[float] = []
    steps: list[int] = []

    for episode in range(episodes):
        options = {} if helpful_regime is None else {"helpful_regime": helpful_regime}
        observation, _ = env.reset(seed=seed + episode, options=options)
        episode_return = 0.0
        episode_danger = 0.0
        episode_resources = 0.0
        episode_steps = 0
        while True:
            action = policy(env, observation, policy_rng)
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


def evaluate_environment_gate(*, episodes: int = 100, seed: int = 0) -> dict[str, PolicySummary]:
    """Run the prespecified policies needed to assess Gate 1."""

    return {
        "random": evaluate_policy(random_policy, episodes=episodes, seed=seed),
        "oracle": evaluate_policy(privileged_oracle_policy, episodes=episodes, seed=seed),
        "social_helpful": evaluate_policy(
            social_follower_policy,
            episodes=episodes,
            seed=seed,
            helpful_regime=True,
        ),
        "social_deceptive": evaluate_policy(
            social_follower_policy,
            episodes=episodes,
            seed=seed,
            helpful_regime=False,
        ),
    }
