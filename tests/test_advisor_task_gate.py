import pytest

from cognitive_organism.evaluation.advisor_task_gate import evaluate_reference


def test_one_bit_memory_controller_solves_task():
    summary = evaluate_reference("win_stay_lose_shift", episodes=100, seed=10)

    assert summary.post_switch_accuracy > 0.95
    assert summary.early_post_switch_accuracy == pytest.approx(0.8)


def test_unknown_reference_is_rejected():
    with pytest.raises(ValueError, match="unknown reference"):
        evaluate_reference("invented")
