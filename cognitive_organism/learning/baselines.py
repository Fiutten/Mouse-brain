"""Construction of reproducible PPO baselines for Gate 2."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from cognitive_organism.envs.social_inference_world import SocialInferenceWorld


class BaselineKind(StrEnum):
    """Supported learning baselines."""

    PPO = "ppo"
    RECURRENT_PPO = "recurrent_ppo"


@dataclass(frozen=True)
class RecurrentConfig:
    """Explicit RecurrentPPO configuration used for auditable selection."""

    name: str
    learning_rate: float = 3e-4
    n_steps: int = 256
    batch_size: int = 64
    n_epochs: int = 5
    lstm_hidden_size: int = 64
    shared_lstm: bool = True
    enable_critic_lstm: bool = False


RECURRENT_CONFIGS = {
    config.name: config
    for config in (
        RecurrentConfig(name="shared_default"),
        RecurrentConfig(name="shared_low_lr", learning_rate=1e-4),
        RecurrentConfig(
            name="shared_long_rollout",
            n_steps=512,
            batch_size=128,
            n_epochs=10,
        ),
        RecurrentConfig(
            name="separate_actor_critic",
            shared_lstm=False,
            enable_critic_lstm=True,
        ),
    )
}


def build_baseline(
    kind: BaselineKind | str,
    *,
    seed: int,
    env: Any | None = None,
    recurrent_config: RecurrentConfig | None = None,
    verbose: int = 0,
    device: str = "cpu",
) -> Any:
    """Build a baseline with a shared rollout and optimization budget.

    Network parameter counts are intentionally reported later because these
    algorithms are not yet parameter matched. Gate 2 assesses learnability, not
    a causal memory advantage.
    """

    kind = BaselineKind(kind)
    recurrent_config = recurrent_config or RECURRENT_CONFIGS["shared_default"]
    common = {
        "env": env or SocialInferenceWorld(),
        "seed": seed,
        "verbose": verbose,
        "device": device,
        "learning_rate": recurrent_config.learning_rate,
        "n_steps": recurrent_config.n_steps,
        "batch_size": recurrent_config.batch_size,
        "n_epochs": recurrent_config.n_epochs,
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
            "lstm_hidden_size": recurrent_config.lstm_hidden_size,
            "n_lstm_layers": 1,
            "net_arch": {"pi": [64], "vf": [64]},
            "shared_lstm": recurrent_config.shared_lstm,
            "enable_critic_lstm": recurrent_config.enable_critic_lstm,
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
