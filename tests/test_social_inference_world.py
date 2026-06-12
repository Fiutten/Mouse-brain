import numpy as np

from cognitive_organism.envs.social_inference_world import SocialInferenceWorld
from cognitive_organism.envs.social_survival_world import Action, WorldConfig


def test_both_advisers_are_observed_without_revealing_helpful_identity():
    env = SocialInferenceWorld()
    observation, info = env.reset(seed=8, options={"helpful_regime": True})

    assert env.observation_space.contains(observation)
    assert "hidden_helpful_advisor" not in observation
    assert info["hidden_helpful_advisor"] == "a"
    assert observation["advisor_a_direction"] == env._direction_toward(env.resource_pos)
    assert observation["advisor_b_direction"] == env._direction_toward(env.threat_pos)


def test_switch_swaps_adviser_roles():
    env = SocialInferenceWorld(WorldConfig(regime_switch_step=1))
    env.reset(seed=9, options={"helpful_regime": True})

    observation, _, _, _, info = env.step(Action.STAY)

    assert info["hidden_helpful_advisor"] == "b"
    assert observation["advisor_b_direction"] == env._direction_toward(env.resource_pos)
    assert observation["advisor_a_direction"] == env._direction_toward(env.threat_pos)


def test_seed_reproduces_two_adviser_observation():
    first = SocialInferenceWorld()
    second = SocialInferenceWorld()

    first_observation, _ = first.reset(seed=17)
    second_observation, _ = second.reset(seed=17)

    for key in first_observation:
        np.testing.assert_array_equal(first_observation[key], second_observation[key])
