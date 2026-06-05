import unittest

from neurotwin_mvp.data import Session, Trial
from neurotwin_mvp.microcircuit import (
    calibrate_microcircuit_from_sessions,
    run_selected_microcircuit,
    validate_microcircuit_against_stability,
)


class MicrocircuitTests(unittest.TestCase):
    def make_session(self, session_id: str, visual_base: float, basal_base: float) -> Session:
        return Session(
            session_id=session_id,
            animal_id="mouse",
            dataset="test",
            region_names=["visual_cortex", "basal_ganglia"],
            trials=[
                Trial(
                    trial_id=i,
                    stimulus=1.0,
                    choice=i % 2,
                    reward=1,
                    latency_ms=250.0,
                    engagement=0.7,
                    region_rates={"visual_cortex": visual_base, "basal_ganglia": basal_base},
                    metadata={
                        "region_rates_by_window": {
                            "pre_response": {
                                "visual_cortex": visual_base + i * 0.001,
                                "basal_ganglia": basal_base + i * 0.001,
                            }
                        }
                    },
                )
                for i in range(20)
            ],
        )

    def test_calibrates_from_robust_sessions_and_runs_perturbations(self):
        session = self.make_session("robust_a", visual_base=1.0, basal_base=0.5)
        calibration = calibrate_microcircuit_from_sessions(
            [session],
            robust_session_ids=["robust_a"],
            visual_cortex_drop=0.06,
            basal_ganglia_drop=0.03,
            temporal_gain=0.14,
        )
        report = run_selected_microcircuit(calibration, n_trials=50)
        self.assertEqual(len(report.trials), 50)
        self.assertEqual(len(report.perturbations), 3)
        self.assertGreater(report.intact_mean_action_probability, 0.0)

    def test_rejects_missing_robust_sessions(self):
        with self.assertRaises(ValueError):
            calibrate_microcircuit_from_sessions(
                [],
                robust_session_ids=["missing"],
                visual_cortex_drop=0.06,
                basal_ganglia_drop=0.03,
                temporal_gain=0.14,
            )

    def test_validates_microcircuit_against_stability_labels(self):
        robust = self.make_session("robust_a", visual_base=1.0, basal_base=0.5)
        mixed = self.make_session("mixed_a", visual_base=0.95, basal_base=0.45)
        fragile = self.make_session("fragile_a", visual_base=0.85, basal_base=0.35)
        calibration = calibrate_microcircuit_from_sessions(
            [robust],
            robust_session_ids=["robust_a"],
            visual_cortex_drop=0.08,
            basal_ganglia_drop=0.04,
            temporal_gain=0.14,
        )
        report = validate_microcircuit_against_stability(
            calibration,
            [fragile, mixed, robust],
            stability_rows=[
                {"session_id": "robust_a", "status": "robust", "stability_score": 1.0},
                {"session_id": "mixed_a", "status": "mixed", "stability_score": 0.5},
                {"session_id": "fragile_a", "status": "fragile", "stability_score": 0.0},
            ],
        )
        self.assertEqual(len(report.sessions), 3)
        self.assertGreater(report.robust_minus_fragile_probability, 0.0)
        self.assertIn(
            report.decision,
            {
                "supports_stability_gradient",
                "weak_partial_robust_fragile_alignment",
                "partial_robust_fragile_alignment",
            },
        )


if __name__ == "__main__":
    unittest.main()
