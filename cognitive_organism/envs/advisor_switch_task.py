"""Minimal POMDP that isolates memory-dependent adviser selection."""

from __future__ import annotations

from typing import Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces


class AdvisorSwitchTask(gym.Env[dict[str, np.ndarray], int]):
    """Choose the currently helpful adviser and adapt after a hidden switch.

    The observation contains only the previous outcome. A reactive policy cannot
    know which adviser produced that outcome; a recurrent policy can combine the
    previous action with its consequence. This isolates memory from navigation
    and sparse-reward confounds.
    """

    metadata = {"render_modes": []}

    def __init__(self, *, horizon: int = 40, switch_step: int = 20):
        super().__init__()
        if not 0 < switch_step < horizon:
            raise ValueError("switch_step must fall inside the episode")
        self.horizon = horizon
        self.switch_step = switch_step
        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Dict(
            {"last_outcome": spaces.Box(-1.0, 1.0, shape=(1,), dtype=np.float32)}
        )
        self.step_count = 0
        self.helpful_adviser = 0
        self.last_outcome = 0.0

    def reset(
        self, *, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
        super().reset(seed=seed)
        options = options or {}
        self.step_count = 0
        self.last_outcome = 0.0
        self.helpful_adviser = int(
            options.get("helpful_adviser", self.np_random.integers(0, 2))
        )
        return self._observation(), self._info(rule_switch=False)

    def step(
        self, action: int
    ) -> tuple[dict[str, np.ndarray], float, bool, bool, dict[str, Any]]:
        if not self.action_space.contains(action):
            raise ValueError(f"invalid action: {action}")
        self.step_count += 1
        rule_switch = self.step_count == self.switch_step
        if rule_switch:
            self.helpful_adviser = 1 - self.helpful_adviser
        reward = 1.0 if action == self.helpful_adviser else -1.0
        self.last_outcome = reward
        truncated = self.step_count >= self.horizon
        return self._observation(), reward, False, truncated, self._info(rule_switch=rule_switch)

    def _observation(self) -> dict[str, np.ndarray]:
        return {"last_outcome": np.array((self.last_outcome,), dtype=np.float32)}

    def _info(self, *, rule_switch: bool) -> dict[str, Any]:
        return {
            "rule_switch": rule_switch,
            "hidden_helpful_adviser": self.helpful_adviser,
            "correct_choice": self.last_outcome > 0,
        }
