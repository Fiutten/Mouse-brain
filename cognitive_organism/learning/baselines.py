"""Construction of reproducible PPO baselines for Gate 2."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from cognitive_organism.envs.social_inference_world import SocialInferenceWorld


class BaselineKind(StrEnum):
    """Supported learning baselines."""

    PPO = "ppo"
    RECURRENT_PPO = "recurrent_ppo"


def build_baseline(
    kind: BaselineKind | str,
    *,
    seed: int,
    env: Any | None = None,
    verbose: int = 0,
    device: str = "cpu",
) -> Any:
    """Build a baseline with a shared rollout and optimization budget.

    Network parameter counts are intentionally reported later because these
    algorithms are not yet parameter matched. Gate 2 assesses learnability, not
    a causal memory advantage.
    """

    kind = BaselineKind(kind)
    common = {
        "env": env or SocialInferenceWorld(),
        "seed": seed,
        "verbose": verbose,
        "device": device,
        "learning_rate": 3e-4,
        "n_steps": 256,
        "batch_size": 64,
        "n_epochs": 5,
        "gamma": 0.99,
    }
    if kind is BaselineKind.PPO:
        from stable_baselines3 import PPO

        return PPO(
            "MultiInputPolicy",
            policy_kwargs={"net_arch": {"pi": [64, 64], "vf": [64, 64]}},
            **common,
        )

    from sb3_contrib import RecurrentPPO

    return RecurrentPPO(
        "MultiInputLstmPolicy",
        policy_kwargs={
            "lstm_hidden_size": 64,
            "n_lstm_layers": 1,
            "net_arch": {"pi": [64], "vf": [64]},
            "shared_lstm": True,
            "enable_critic_lstm": False,
        },
        **common,
    )


def count_trainable_parameters(model: Any) -> int:
    """Return the trainable parameter count of an SB3 policy."""

    return sum(parameter.numel() for parameter in model.policy.parameters() if parameter.requires_grad)


def load_baseline(kind: BaselineKind | str, path: str) -> Any:
    """Load a saved baseline without constructing a new training environment."""

    kind = BaselineKind(kind)
    if kind is BaselineKind.PPO:
        from stable_baselines3 import PPO

        return PPO.load(path, device="cpu")

    from sb3_contrib import RecurrentPPO

    return RecurrentPPO.load(path, device="cpu")
