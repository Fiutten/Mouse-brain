from pathlib import Path
import unittest

from neurotwin_mvp.baselines import MajorityChoiceBaseline, StimulusRuleBaseline, evaluate_classifier
from neurotwin_mvp.data import REGIONS, SyntheticNeuropixelsLoader, mean_region_rates, train_test_split
from neurotwin_mvp.metrics import behavioral_summary
from neurotwin_mvp.workflow import run_workflow


ROOT = Path(__file__).resolve().parents[1]


class DataPipelineTests(unittest.TestCase):
    def test_synthetic_session_schema(self):
        session = SyntheticNeuropixelsLoader(n_trials=50, seed=3).load()
        self.assertEqual(len(session.trials), 50)
        self.assertEqual(session.region_names, REGIONS)
        self.assertEqual(set(session.trials[0].region_rates), set(REGIONS))

    def test_train_test_split(self):
        session = SyntheticNeuropixelsLoader(n_trials=100, seed=3).load()
        train, test = train_test_split(session, train_fraction=0.75)
        self.assertEqual(len(train), 75)
        self.assertEqual(len(test), 25)

    def test_behavioral_summary(self):
        session = SyntheticNeuropixelsLoader(n_trials=80, seed=4).load()
        summary = behavioral_summary(session.trials)
        self.assertEqual(summary["n_trials"], 80.0)
        self.assertGreaterEqual(summary["reward_rate"], 0.0)
        self.assertLessEqual(summary["reward_rate"], 1.0)

    def test_region_rates(self):
        session = SyntheticNeuropixelsLoader(n_trials=80, seed=4).load()
        rates = mean_region_rates(session.trials)
        self.assertEqual(set(rates), set(REGIONS))
        self.assertGreater(rates["visual_cortex"], 0.0)

    def test_stimulus_baseline_beats_majority_on_fixture(self):
        session = SyntheticNeuropixelsLoader(n_trials=240, seed=5).load()
        train, test = train_test_split(session)
        majority = evaluate_classifier(MajorityChoiceBaseline(), train, test)
        stimulus = evaluate_classifier(StimulusRuleBaseline(), train, test)
        self.assertGreater(stimulus.accuracy, majority.accuracy)

    def test_workflow_includes_data_reports(self):
        report = run_workflow(str(ROOT / "configs" / "mouse_level0.json"))
        self.assertGreater(report.dataset_summary["n_trials"], 0)
        self.assertEqual(len(report.baseline_reports), 2)


if __name__ == "__main__":
    unittest.main()
