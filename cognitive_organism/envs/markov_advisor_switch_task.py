"""Markov control for AdvisorSwitchTask with previous action made explicit."""

from __future__ import annotations

from typing import Any

import numpy as np
from gymnasium import spaces

from cognitive_organism.envs.advisor_switch_task import AdvisorSwitchTask


class MarkovAdvisorSwitchTask(AdvisorSwitchTask):
    """Expose the minimal state needed for a reactive win-stay/lose-shift rule."""

    NO_PREVIOUS_ACTION = 2

    def __init__(self, *, horizon: int = 40, switch_step: int = 20):
        super().__init__(horizon=horizon, switch_step=switch_step)
        self.observation_space = spaces.Dict(
            {
                "last_outcome": spaces.Box(-1.0, 1.0, shape=(1,), dtype=np.float32),
                "previous_action": spaces.Discrete(3),
            }
        )
        self.previous_action = self.NO_PREVIOUS_ACTION

    def reset(
        self, *, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
        self.previous_action = self.NO_PREVIOUS_ACTION
        return super().reset(seed=seed, options=options)

    def step(
        self, action: int
    ) -> tuple[dict[str, np.ndarray], float, bool, bool, dict[str, Any]]:
        # Set before super().step() because it constructs the next observation.
        self.previous_action = int(action)
        return super().step(action)

    def _observation(self) -> dict[str, np.ndarray]:
        return {
            "last_outcome": np.array((self.last_outcome,), dtype=np.float32),
            "previous_action": np.int64(self.previous_action),
        }
