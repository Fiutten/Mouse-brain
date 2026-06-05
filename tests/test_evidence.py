import unittest

from neurotwin_mvp.evidence import synthesize_multisession_evidence


def report_bundle(
    session_id: str,
    *,
    n_trials: int = 240,
    choice_rate: float = 0.5,
    reward_rate: float = 0.5,
    multisplit_gain: float = 0.01,
    permutation_gain: float = 0.01,
    p_value: float = 0.5,
):
    return {
        "audit": {
            "session_id": session_id,
            "dataset": "allen_visual_behavior_neuropixels",
            "animal_id": "mouse",
            "n_trials": n_trials,
            "choice_rate": choice_rate,
            "reward_rate": reward_rate,
            "warnings": [],
        },
        "benchmark": {
            "session_id": session_id,
            "results": [
                {
                    "name": "logistic_task_compact_image_history",
                    "accuracy": 0.60,
                    "details": {"balanced_accuracy": 0.60},
                },
                {
                    "name": "logistic_task_compact_image_history_region_rates",
                    "accuracy": 0.62,
                    "details": {"balanced_accuracy": 0.62},
                },
            ],
        },
        "multisplit": {
            "session_id": session_id,
            "dataset": "allen_visual_behavior_neuropixels",
            "mean_gain": multisplit_gain,
            "warnings": [],
        },
        "permutation": {
            "session_id": session_id,
            "dataset": "allen_visual_behavior_neuropixels",
            "observed_gain": permutation_gain,
            "p_value": p_value,
            "warnings": [],
        },
    }


class EvidenceTests(unittest.TestCase):
    def test_inconclusive_negative_trend_when_sessions_are_few_and_gains_negative(self):
        bundles = [
            report_bundle("a", multisplit_gain=0.01, permutation_gain=-0.01, p_value=0.7),
            report_bundle("b", multisplit_gain=-0.02, permutation_gain=0.01, p_value=0.3),
            report_bundle("c", multisplit_gain=-0.04, permutation_gain=-0.08, p_value=1.0),
        ]
        report = synthesize_multisession_evidence(
            bundles,
            min_sessions_for_claim=8,
            bootstrap_iterations=100,
            seed=1,
        )
        self.assertEqual(report.n_sessions, 3)
        self.assertEqual(report.decision.label, "inconclusive_negative_trend")
        self.assertLess(report.mean_multisplit_gain, 0.0)
        self.assertIn("Only 3 sessions", " ".join(report.warnings))

    def test_positive_evidence_requires_stable_positive_gains_and_significance(self):
        bundles = [
            report_bundle(
                str(index),
                multisplit_gain=0.03 + index * 0.001,
                permutation_gain=0.02 + index * 0.001,
                p_value=0.01,
            )
            for index in range(8)
        ]
        report = synthesize_multisession_evidence(
            bundles,
            min_sessions_for_claim=8,
            bootstrap_iterations=100,
            seed=2,
        )
        self.assertEqual(report.decision.label, "positive_evidence")
        self.assertGreater(report.mean_multisplit_gain_ci95[0], 0.0)
        self.assertEqual(report.significant_permutation_fraction, 1.0)


if __name__ == "__main__":
    unittest.main()
