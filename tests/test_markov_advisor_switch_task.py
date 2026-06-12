import numpy as np

from cognitive_organism.envs.markov_advisor_switch_task import MarkovAdvisorSwitchTask


def test_reset_marks_absence_of_previous_action():
    env = MarkovAdvisorSwitchTask()

    observation, _ = env.reset(seed=3)

    assert env.observation_space.contains(observation)
    assert observation["previous_action"] == env.NO_PREVIOUS_ACTION


def test_next_observation_contains_action_that_produced_outcome():
    env = MarkovAdvisorSwitchTask()
    env.reset(seed=3, options={"helpful_adviser": 1})

    observation, reward, _, _, _ = env.step(1)

    assert reward == 1.0
    assert observation["previous_action"] == 1
    np.testing.assert_array_equal(observation["last_outcome"], np.array((1.0,), dtype=np.float32))
