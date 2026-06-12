from cognitive_organism.evaluation.environment_gate import (
    evaluate_environment_gate,
    evaluate_policy,
    random_policy,
)


def test_environment_gate_contains_intended_causal_structure():
    summaries = evaluate_environment_gate(episodes=80, seed=21)

    assert summaries["oracle"].mean_return > summaries["random"].mean_return + 5.0
    assert summaries["social_helpful"].mean_return > summaries["social_deceptive"].mean_return
    assert (
        summaries["social_deceptive"].mean_danger_rate
        > summaries["social_helpful"].mean_danger_rate
    )


def test_policy_evaluation_is_reproducible():
    first = evaluate_policy(random_policy, episodes=5, seed=4)
    second = evaluate_policy(random_policy, episodes=5, seed=4)

    assert first == second
