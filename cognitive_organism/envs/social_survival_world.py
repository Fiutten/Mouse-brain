"""A minimal POMDP for testing integration under hidden social regime changes.

This environment is intentionally a benchmark instrument, not a model of animal
social cognition. Its hidden variables allow controlled interventions and
out-of-distribution evaluation without leaking privileged state to the agent.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces


class Action(IntEnum):
    """Discrete actions with stable integer identifiers."""

    STAY = 0
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4


MOVE_DELTAS = {
    Action.STAY: np.array((0, 0), dtype=np.int64),
    Action.UP: np.array((-1, 0), dtype=np.int64),
    Action.RIGHT: np.array((0, 1), dtype=np.int64),
    Action.DOWN: np.array((1, 0), dtype=np.int64),
    Action.LEFT: np.array((0, -1), dtype=np.int64),
}


@dataclass(frozen=True)
class WorldConfig:
    """Immutable parameters controlling one environment family."""

    size: int = 7
    max_steps: int = 80
    regime_switch_step: int | None = 40
    initial_energy: float = 1.0
    metabolism: float = 0.015
    resource_energy: float = 0.45
    threat_damage: float = 0.35

    def __post_init__(self) -> None:
        if self.size < 5:
            raise ValueError("size must be at least 5")
        if self.max_steps < 1:
            raise ValueError("max_steps must be positive")
        if self.regime_switch_step is not None and not 0 < self.regime_switch_step < self.max_steps:
            raise ValueError("regime_switch_step must fall inside the episode")


class SocialSurvivalWorld(gym.Env[dict[str, np.ndarray], int]):
    """Partially observable grid world with a hidden adviser reliability regime.

    The local sensor reveals nearby objects. A separate social channel recommends
    a movement direction. In the helpful regime it points toward the resource; in
    the deceptive regime it points toward the threat. The regime is hidden and
    may switch during an episode, forcing inference from outcomes over time.
    """

    metadata = {"render_modes": []}

    EMPTY = 0
    RESOURCE = 1
    THREAT = 2

    def __init__(self, config: WorldConfig | None = None):
        super().__init__()
        self.config = config or WorldConfig()
        self.action_space = spaces.Discrete(len(Action))
        self.observation_space = spaces.Dict(
            {
                "local_objects": spaces.Box(0, self.THREAT, shape=(3, 3), dtype=np.int8),
                "social_direction": spaces.Discrete(len(Action)),
                "body": spaces.Box(0.0, 1.0, shape=(2,), dtype=np.float32),
                "last_outcome": spaces.Box(-1.0, 1.0, shape=(2,), dtype=np.float32),
            }
        )
        self.agent_pos = np.zeros(2, dtype=np.int64)
        self.resource_pos = np.zeros(2, dtype=np.int64)
        self.threat_pos = np.zeros(2, dtype=np.int64)
        self.energy = self.config.initial_energy
        self.stress = 0.0
        self.step_count = 0
        self.helpful_regime = True
        self.last_reward = 0.0
        self.last_danger = 0.0
        self.last_moved = 0.0
        self._visited: set[tuple[int, int]] = set()

    def reset(
        self, *, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
        super().reset(seed=seed)
        options = options or {}
        self.step_count = 0
        self.energy = self.config.initial_energy
        self.stress = 0.0
        self.last_reward = 0.0
        self.last_danger = 0.0
        self.last_moved = 0.0
        self.helpful_regime = bool(
            options.get("helpful_regime", self.np_random.integers(0, 2))
        )

        positions = self.np_random.choice(self.config.size**2, size=3, replace=False)
        self.agent_pos = self._unflatten(int(positions[0]))
        self.resource_pos = self._unflatten(int(positions[1]))
        self.threat_pos = self._unflatten(int(positions[2]))
        self._visited = {tuple(self.agent_pos)}
        return self._observation(), self._info(novelty=1.0, rule_switch=False)

    def step(
        self, action: int
    ) -> tuple[dict[str, np.ndarray], float, bool, bool, dict[str, Any]]:
        if not self.action_space.contains(action):
            raise ValueError(f"invalid action: {action}")

        self.step_count += 1
        rule_switch = self.step_count == self.config.regime_switch_step
        if rule_switch:
            self.helpful_regime = not self.helpful_regime

        previous_energy = self.energy
        previous_position = self.agent_pos.copy()
        self.agent_pos = np.clip(
            self.agent_pos + MOVE_DELTAS[Action(action)], 0, self.config.size - 1
        )
        self.last_moved = float(not np.array_equal(previous_position, self.agent_pos))
        position = tuple(self.agent_pos)
        novelty = float(position not in self._visited)
        self._visited.add(position)

        reward = -0.01
        danger = 0.0
        self.energy -= self.config.metabolism
        if np.array_equal(self.agent_pos, self.resource_pos):
            reward += 1.0
            self.energy = min(1.0, self.energy + self.config.resource_energy)
            self.resource_pos = self._sample_free_position()
        if np.array_equal(self.agent_pos, self.threat_pos):
            reward -= 1.0
            danger = 1.0
            self.energy -= self.config.threat_damage
            self.stress = min(1.0, self.stress + 0.4)
            self.threat_pos = self._sample_free_position()
        else:
            self.stress = max(0.0, self.stress - 0.02)

        self.energy = float(np.clip(self.energy, 0.0, 1.0))
        self.last_reward = float(np.clip(reward, -1.0, 1.0))
        self.last_danger = danger
        terminated = self.energy <= 0.0
        truncated = self.step_count >= self.config.max_steps
        info = self._info(
            novelty=novelty,
            rule_switch=rule_switch,
            energy_delta=self.energy - previous_energy,
        )
        return self._observation(), reward, terminated, truncated, info

    def _observation(self) -> dict[str, np.ndarray]:
        local = np.zeros((3, 3), dtype=np.int8)
        for position, object_id in (
            (self.resource_pos, self.RESOURCE),
            (self.threat_pos, self.THREAT),
        ):
            relative = position - self.agent_pos
            if np.all(np.abs(relative) <= 1):
                local[relative[0] + 1, relative[1] + 1] = object_id

        target = self.resource_pos if self.helpful_regime else self.threat_pos
        return {
            "local_objects": local,
            "social_direction": np.int64(self._direction_toward(target)),
            "body": np.array((self.energy, self.stress), dtype=np.float32),
            "last_outcome": np.array((self.last_reward, self.last_danger), dtype=np.float32),
        }

    def _info(
        self,
        *,
        novelty: float,
        rule_switch: bool,
        energy_delta: float = 0.0,
    ) -> dict[str, Any]:
        # Hidden variables are exposed only for scientific evaluation and oracle baselines.
        return {
            "novelty": novelty,
            "danger": self.last_danger,
            "moved": self.last_moved,
            "energy_delta": energy_delta,
            "rule_switch": rule_switch,
            "hidden_helpful_regime": self.helpful_regime,
            "hidden_resource_position": tuple(int(x) for x in self.resource_pos),
            "hidden_threat_position": tuple(int(x) for x in self.threat_pos),
        }

    def _direction_toward(self, target: np.ndarray) -> Action:
        delta = target - self.agent_pos
        if delta[0] < 0:
            return Action.UP
        if delta[0] > 0:
            return Action.DOWN
        if delta[1] > 0:
            return Action.RIGHT
        if delta[1] < 0:
            return Action.LEFT
        return Action.STAY

    def _sample_free_position(self) -> np.ndarray:
        blocked = {tuple(self.agent_pos), tuple(self.resource_pos), tuple(self.threat_pos)}
        candidates = [
            (row, col)
            for row in range(self.config.size)
            for col in range(self.config.size)
            if (row, col) not in blocked
        ]
        return np.asarray(candidates[int(self.np_random.integers(len(candidates)))], dtype=np.int64)

    def _unflatten(self, index: int) -> np.ndarray:
        return np.array(divmod(index, self.config.size), dtype=np.int64)
