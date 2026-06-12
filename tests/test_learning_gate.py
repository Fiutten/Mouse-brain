import numpy as np

from cognitive_organism.evaluation.learning_gate import evaluate_learning_model
from cognitive_organism.learning.baselines import BaselineKind


class StayModel:
    def predict(self, observation, **kwargs):
        del observation
        return np.array(0), kwargs.get("state")


def test_learning_evaluation_is_reproducible_for_fixed_model():
    model = StayModel()

    first = evaluate_learning_model(
        model,
        algorithm=BaselineKind.PPO,
        train_seed=1,
        train_steps=0,
        trainable_parameters=0,
        episodes=4,
        evaluation_seed=50,
    )
    second = evaluate_learning_model(
        model,
        algorithm=BaselineKind.PPO,
        train_seed=1,
        train_steps=0,
        trainable_parameters=0,
        episodes=4,
        evaluation_seed=50,
    )

    assert first == second
    assert first.mean_pre_switch_return < 0
    assert first.mean_post_switch_return < 0


def test_recurrent_evaluation_passes_episode_state():
    summary = evaluate_learning_model(
        StayModel(),
        algorithm=BaselineKind.RECURRENT_PPO,
        train_seed=2,
        train_steps=0,
        trainable_parameters=0,
        episodes=2,
        evaluation_seed=60,
    )

    assert summary.episodes == 2
