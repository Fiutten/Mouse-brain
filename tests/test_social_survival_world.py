import numpy as np
import pytest

from cognitive_organism.envs.social_survival_world import Action, SocialSurvivalWorld, WorldConfig


def test_reset_returns_valid_observation_and_hidden_evaluation_info():
    env = SocialSurvivalWorld()

    observation, info = env.reset(seed=7)

    assert env.observation_space.contains(observation)
    assert "hidden_helpful_regime" not in observation
    assert isinstance(info["hidden_helpful_regime"], bool)


def test_seed_reproduces_initial_state_and_observation():
    first = SocialSurvivalWorld()
    second = SocialSurvivalWorld()

    first_observation, first_info = first.reset(seed=13)
    second_observation, second_info = second.reset(seed=13)

    for key in first_observation:
        np.testing.assert_array_equal(first_observation[key], second_observation[key])
    assert first_info == second_info


def test_regime_switch_changes_social_adviser_target():
    env = SocialSurvivalWorld(WorldConfig(regime_switch_step=1))
    env.reset(seed=2, options={"helpful_regime": True})
    resource_direction = env._direction_toward(env.resource_pos)
    threat_direction = env._direction_toward(env.threat_pos)

    observation, _, _, _, info = env.step(Action.STAY)

    assert info["rule_switch"] is True
    assert info["hidden_helpful_regime"] is False
    assert observation["social_direction"] == threat_direction
    if resource_direction != threat_direction:
        assert observation["social_direction"] != resource_direction


def test_resource_and_threat_have_opposing_consequences():
    resource_env = SocialSurvivalWorld()
    resource_env.reset(seed=3)
    resource_env.agent_pos = resource_env.resource_pos.copy()
    resource_env.energy = 0.5
    _, resource_reward, _, _, resource_info = resource_env.step(Action.STAY)

    threat_env = SocialSurvivalWorld()
    threat_env.reset(seed=3)
    threat_env.agent_pos = threat_env.threat_pos.copy()
    threat_env.energy = 0.8
    _, threat_reward, _, _, threat_info = threat_env.step(Action.STAY)

    assert resource_reward > 0
    assert resource_info["energy_delta"] > 0
    assert threat_reward < 0
    assert threat_info["danger"] == 1.0
    assert threat_info["energy_delta"] < 0


def test_episode_truncates_at_fixed_horizon():
    env = SocialSurvivalWorld(WorldConfig(max_steps=3, regime_switch_step=None, metabolism=0.0))
    env.reset(seed=5)

    for _ in range(2):
        _, _, terminated, truncated, _ = env.step(Action.STAY)
        assert not terminated
        assert not truncated

    _, _, terminated, truncated, _ = env.step(Action.STAY)
    assert not terminated
    assert truncated


def test_info_reports_whether_action_changed_position():
    env = SocialSurvivalWorld()
    env.reset(seed=5)
    env.agent_pos = np.array((0, 0), dtype=np.int64)

    _, _, _, _, blocked_info = env.step(Action.UP)
    _, _, _, _, moved_info = env.step(Action.RIGHT)

    assert blocked_info["moved"] == 0.0
    assert moved_info["moved"] == 1.0


def test_invalid_action_is_rejected():
    env = SocialSurvivalWorld()
    env.reset(seed=1)

    with pytest.raises(ValueError, match="invalid action"):
        env.step(99)
