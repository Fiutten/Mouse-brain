import numpy as np

from cognitive_organism.envs.advisor_switch_task import AdvisorSwitchTask


def test_outcome_requires_combining_action_and_hidden_adviser():
    env = AdvisorSwitchTask()
    observation, info = env.reset(seed=1, options={"helpful_adviser": 0})

    assert env.observation_space.contains(observation)
    assert "hidden_helpful_adviser" not in observation
    assert info["hidden_helpful_adviser"] == 0

    observation, reward, _, _, info = env.step(0)
    assert reward == 1.0
    assert info["correct_choice"] is True
    np.testing.assert_array_equal(observation["last_outcome"], np.array((1.0,), dtype=np.float32))


def test_hidden_adviser_switches_before_switch_step_choice_is_scored():
    env = AdvisorSwitchTask(horizon=4, switch_step=2)
    env.reset(seed=1, options={"helpful_adviser": 0})

    _, first_reward, _, _, _ = env.step(0)
    _, switch_reward, _, _, switch_info = env.step(0)

    assert first_reward == 1.0
    assert switch_info["rule_switch"] is True
    assert switch_reward == -1.0
