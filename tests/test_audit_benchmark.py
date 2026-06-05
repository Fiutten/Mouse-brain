import unittest

from neurotwin_mvp.audit import audit_session, summarize_values
from neurotwin_mvp.benchmark import (
    LogisticRegressionClassifier,
    run_choice_benchmark,
    run_multisplit_neural_gain,
    run_neural_gain_permutation_test,
    run_regional_ablation,
    run_temporal_regional_ablation,
    run_temporal_window_permutation_test,
    run_temporal_window_benchmark,
)
from neurotwin_mvp.data import Session, SyntheticNeuropixelsLoader, Trial, train_test_split


class AuditBenchmarkTests(unittest.TestCase):
    def test_summarize_values(self):
        summary = summarize_values([1.0, 2.0, 3.0])
        self.assertEqual(summary.count, 3)
        self.assertEqual(summary.mean, 2.0)
        self.assertGreater(summary.std, 0.0)

    def test_audit_session_reports_basic_quality(self):
        session = SyntheticNeuropixelsLoader(n_trials=24, seed=12).load()
        audit = audit_session(session)
        self.assertEqual(audit.n_trials, 24)
        self.assertEqual(audit.n_regions, len(session.region_names))
        self.assertIn("Fewer than 200 trials", " ".join(audit.warnings))

    def test_audit_warns_on_imbalanced_choices(self):
        trials = [
            Trial(
                trial_id=i,
                stimulus=1.0,
                choice=0,
                reward=0,
                latency_ms=1.0,
                engagement=1.0,
                region_rates={"visual_cortex": float(i)},
            )
            for i in range(12)
        ] + [
            Trial(
                trial_id=12,
                stimulus=-1.0,
                choice=1,
                reward=1,
                latency_ms=1.0,
                engagement=1.0,
                region_rates={"visual_cortex": 12.0},
            )
        ]
        session = Session("toy", "mouse", "toy", trials, ["visual_cortex"])
        audit = audit_session(session)
        self.assertIn("strongly imbalanced", " ".join(audit.warnings))

    def test_logistic_classifier_learns_synthetic_stimulus_rule(self):
        session = SyntheticNeuropixelsLoader(n_trials=120, seed=13).load()
        train, test = train_test_split(session)
        model = LogisticRegressionClassifier("logistic_stimulus", ["stimulus"])
        model.fit(train)
        accuracy = sum(model.predict(trial) == trial.choice for trial in test) / len(test)
        self.assertGreaterEqual(accuracy, 0.65)

    def test_choice_benchmark_runs(self):
        session = SyntheticNeuropixelsLoader(n_trials=80, seed=14).load()
        suite = run_choice_benchmark(session)
        names = {result.name for result in suite.results}
        self.assertIn("majority_choice", names)
        self.assertIn("logistic_region_rates", names)
        self.assertIn("logistic_stimulus_region_rates", names)
        self.assertIn("logistic_task_compact_image", names)
        self.assertIn("logistic_behavior_history", names)
        self.assertIn("logistic_task_compact_image_history_region_rates", names)
        for result in suite.results:
            self.assertIn("balanced_accuracy", result.details)

    def test_choice_benchmark_warns_when_neural_features_do_not_help(self):
        trials = [
            Trial(
                trial_id=i,
                stimulus=1.0 if i % 2 else -1.0,
                choice=1 if i % 2 else 0,
                reward=1,
                latency_ms=0.0,
                engagement=1.0,
                region_rates={"visual_cortex": 1.0},
            )
            for i in range(40)
        ]
        session = Session(
            session_id="toy",
            animal_id="mouse",
            dataset="toy",
            trials=trials,
            region_names=["visual_cortex"],
        )
        suite = run_choice_benchmark(session)
        self.assertTrue(any("did not beat" in warning for warning in suite.warnings))

    def test_neural_gain_permutation_test_runs(self):
        session = SyntheticNeuropixelsLoader(n_trials=60, seed=15).load()
        report = run_neural_gain_permutation_test(session, n_permutations=5, seed=3)
        self.assertEqual(report.n_permutations, 5)
        self.assertGreaterEqual(report.p_value, 0.0)
        self.assertLessEqual(report.p_value, 1.0)

    def test_multisplit_neural_gain_runs(self):
        session = SyntheticNeuropixelsLoader(n_trials=80, seed=16).load()
        report = run_multisplit_neural_gain(session, n_splits=3)
        self.assertEqual(len(report.split_results), 3)
        for item in report.split_results:
            self.assertGreater(item.n_train, 0)
            self.assertGreater(item.n_test, 0)

    def test_regional_ablation_reports_one_row_per_region(self):
        session = SyntheticNeuropixelsLoader(n_trials=140, seed=8).load()

        report = run_regional_ablation(session)

        self.assertEqual(report.session_id, session.session_id)
        self.assertEqual({item.region for item in report.region_results}, set(session.region_names))
        self.assertTrue(-1.0 <= report.full_neural_gain <= 1.0)

    def test_temporal_window_benchmark_requires_temporal_metadata(self):
        session = SyntheticNeuropixelsLoader(n_trials=80, seed=21).load()

        with self.assertRaises(ValueError):
            run_temporal_window_benchmark(session)

    def test_temporal_window_benchmark_runs_with_temporal_metadata(self):
        session = self._temporal_session()

        report = run_temporal_window_benchmark(session)

        self.assertEqual(
            [item.window_name for item in report.window_results],
            ["baseline", "stimulus", "decision", "pre_response"],
        )
        self.assertTrue(-1.0 <= report.all_windows_gain <= 1.0)

    def test_temporal_window_permutation_runs_with_temporal_metadata(self):
        session = self._temporal_session()

        report = run_temporal_window_permutation_test(
            session,
            window_name="pre_response",
            n_permutations=5,
            seed=4,
        )

        self.assertEqual(report.window_name, "pre_response")
        self.assertEqual(report.n_permutations, 5)
        self.assertGreaterEqual(report.p_value, 0.0)
        self.assertLessEqual(report.p_value, 1.0)

    def test_temporal_regional_ablation_reports_one_row_per_region(self):
        session = self._temporal_session()

        report = run_temporal_regional_ablation(session, window_name="pre_response")

        self.assertEqual(report.window_name, "pre_response")
        self.assertEqual({item.region for item in report.region_results}, {"visual_cortex"})
        self.assertTrue(-1.0 <= report.full_window_gain <= 1.0)

    def _temporal_session(self):
        trials = []
        for i in range(120):
            stimulus = 1.0 if i % 2 else -1.0
            choice = int(stimulus > 0)
            temporal = {
                "baseline": {"visual_cortex": 0.1},
                "stimulus": {"visual_cortex": 2.0 if choice else -2.0},
                "decision": {"visual_cortex": 1.0 if choice else -1.0},
                "pre_response": {"visual_cortex": 1.0 if choice else -1.0},
            }
            trials.append(
                Trial(
                    trial_id=i,
                    stimulus=stimulus,
                    choice=choice,
                    reward=choice,
                    latency_ms=100.0,
                    engagement=1.0,
                    region_rates=temporal["stimulus"],
                    metadata={"region_rates_by_window": temporal},
                )
            )
        return Session(
            session_id="temporal_toy",
            animal_id="mouse",
            dataset="toy",
            trials=trials,
            region_names=["visual_cortex"],
        )


if __name__ == "__main__":
    unittest.main()
