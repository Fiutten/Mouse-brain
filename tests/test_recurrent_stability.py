import pytest

from cognitive_organism.evaluation.recurrent_stability import score_configurations
from cognitive_organism.learning.baselines import RECURRENT_CONFIGS


def test_candidate_registry_matches_preregistered_names():
    assert set(RECURRENT_CONFIGS) == {
        "shared_default",
        "shared_low_lr",
        "shared_long_rollout",
        "separate_actor_critic",
    }


def test_selection_prioritizes_worst_seed_then_mean_then_parameters():
    rows = [
        {"config_name": "robust", "mean_post_switch_accuracy": 0.81, "trainable_parameters": 20},
        {"config_name": "robust", "mean_post_switch_accuracy": 0.82, "trainable_parameters": 20},
        {"config_name": "fragile", "mean_post_switch_accuracy": 0.99, "trainable_parameters": 10},
        {"config_name": "fragile", "mean_post_switch_accuracy": 0.80, "trainable_parameters": 10},
    ]

    scores = score_configurations(rows)

    assert scores[0].config_name == "robust"


def test_selection_rejects_inconsistent_parameter_counts():
    with pytest.raises(ValueError, match="inconsistent parameter counts"):
        score_configurations(
            [
                {"config_name": "x", "mean_post_switch_accuracy": 0.8, "trainable_parameters": 1},
                {"config_name": "x", "mean_post_switch_accuracy": 0.9, "trainable_parameters": 2},
            ]
        )
