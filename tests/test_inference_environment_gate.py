from cognitive_organism.evaluation.inference_environment_gate import (
    evaluate_inference_environment_gate,
)


def test_inference_environment_has_large_information_value():
    summaries = evaluate_inference_environment_gate(episodes=80, seed=19)

    assert summaries["helpful_oracle"].mean_return > summaries["random_action"].mean_return + 5.0
    assert summaries["helpful_oracle"].mean_return > summaries["random_adviser"].mean_return + 5.0
    assert summaries["helpful_oracle"].mean_danger_rate < summaries["random_adviser"].mean_danger_rate
