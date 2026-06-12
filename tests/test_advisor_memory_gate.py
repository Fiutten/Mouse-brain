import numpy as np

from cognitive_organism.envs.markov_advisor_switch_task import MarkovAdvisorSwitchTask
from cognitive_organism.evaluation.advisor_memory_gate import evaluate_advisor_memory_model
from cognitive_organism.learning.baselines import BaselineKind


class AdviserZeroModel:
    def predict(self, observation, **kwargs):
        del observation
        return np.array(0), kwargs.get("state")


def test_advisor_evaluation_is_reproducible():
    kwargs = {
        "algorithm": BaselineKind.PPO,
        "train_seed": 1,
        "train_steps": 0,
        "trainable_parameters": 0,
        "episodes": 4,
        "evaluation_seed": 10,
    }
    first = evaluate_advisor_memory_model(AdviserZeroModel(), **kwargs)
    second = evaluate_advisor_memory_model(AdviserZeroModel(), **kwargs)

    assert first == second


def test_evaluation_accepts_markov_control_environment():
    summary = evaluate_advisor_memory_model(
        AdviserZeroModel(),
        algorithm=BaselineKind.PPO,
        train_seed=1,
        train_steps=0,
        trainable_parameters=0,
        episodes=2,
        env=MarkovAdvisorSwitchTask(),
    )

    assert summary.train_seed == 1
