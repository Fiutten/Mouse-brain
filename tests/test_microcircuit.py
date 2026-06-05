import unittest

from neurotwin_mvp.data import Session, Trial
from neurotwin_mvp.microcircuit import calibrate_microcircuit_from_sessions, run_selected_microcircuit


class MicrocircuitTests(unittest.TestCase):
    def test_calibrates_from_robust_sessions_and_runs_perturbations(self):
        session = Session(
            session_id="robust_a",
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
                    region_rates={"visual_cortex": 1.0, "basal_ganglia": 0.5},
                    metadata={
                        "region_rates_by_window": {
                            "pre_response": {
                                "visual_cortex": 1.0 + i * 0.01,
                                "basal_ganglia": 0.5 + i * 0.01,
                            }
                        }
                    },
                )
                for i in range(20)
            ],
        )
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


if __name__ == "__main__":
    unittest.main()
