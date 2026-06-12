"""POMDP where memory is useful for selecting between two observable advisers."""

from __future__ import annotations

from typing import Any

import numpy as np
from gymnasium import spaces

from cognitive_organism.envs.social_survival_world import (
    Action,
    SocialSurvivalWorld,
    WorldConfig,
)


class SocialInferenceWorld(SocialSurvivalWorld):
    """Grid world with one helpful and one deceptive adviser.

    Both adviser directions are always observable. Which adviser points to the
    resource is hidden and switches during an episode. The last outcome is
    observable, while identifying which previous adviser produced it requires
    memory of prior observations and actions.
    """

    def __init__(self, config: WorldConfig | None = None):
        super().__init__(config)
        self.observation_space = spaces.Dict(
            {
                "local_objects": spaces.Box(0, self.THREAT, shape=(3, 3), dtype=np.int8),
                "advisor_a_direction": spaces.Discrete(len(Action)),
                "advisor_b_direction": spaces.Discrete(len(Action)),
                "body": spaces.Box(0.0, 1.0, shape=(2,), dtype=np.float32),
                "last_outcome": spaces.Box(-1.0, 1.0, shape=(2,), dtype=np.float32),
            }
        )

    def _observation(self) -> dict[str, np.ndarray]:
        observation = super()._observation()
        helpful_direction = self._direction_toward(self.resource_pos)
        deceptive_direction = self._direction_toward(self.threat_pos)
        observation.pop("social_direction")
        observation["advisor_a_direction"] = np.int64(
            helpful_direction if self.helpful_regime else deceptive_direction
        )
        observation["advisor_b_direction"] = np.int64(
            deceptive_direction if self.helpful_regime else helpful_direction
        )
        return observation

    def _info(
        self,
        *,
        novelty: float,
        rule_switch: bool,
        energy_delta: float = 0.0,
    ) -> dict[str, Any]:
        info = super()._info(
            novelty=novelty,
            rule_switch=rule_switch,
            energy_delta=energy_delta,
        )
        info["hidden_helpful_advisor"] = "a" if self.helpful_regime else "b"
        info["hidden_helpful_direction"] = int(self._direction_toward(self.resource_pos))
        return info
