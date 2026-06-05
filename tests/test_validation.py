from pathlib import Path
import unittest

from neurotwin_mvp.baselines import StimulusRuleBaseline, evaluate_classifier
from neurotwin_mvp.config import load_config
from neurotwin_mvp.data import SyntheticNeuropixelsLoader, train_test_split
from neurotwin_mvp.experiments import evaluate_visual_decision
from neurotwin_mvp.regional_model import RegionalModel


ROOT = Path(__file__).resolve().parents[1]


class ValidationTests(unittest.TestCase):
    def test_unknown_lesion_fails(self):
        model = RegionalModel(load_config(ROOT / "configs" / "mouse_level0.json"), seed=1)
        with self.assertRaises(ValueError):
            model.run_trial(1.0, delay_steps=1, decision_steps=1, lesions={"not_a_region"})

    def test_unknown_input_fails(self):
        model = RegionalModel(load_config(ROOT / "configs" / "mouse_level0.json"), seed=1)
        with self.assertRaises(ValueError):
            model.step({"not_a_region": 1.0})

    def test_invalid_repeats_fail(self):
        model = RegionalModel(load_config(ROOT / "configs" / "mouse_level0.json"), seed=1)
        with self.assertRaises(ValueError):
            evaluate_visual_decision(model, repeats=0)

    def test_invalid_synthetic_trial_count_fails(self):
        with self.assertRaises(ValueError):
            SyntheticNeuropixelsLoader(n_trials=1)

    def test_empty_baseline_test_fails(self):
        session = SyntheticNeuropixelsLoader(n_trials=10).load()
        train, _ = train_test_split(session)
        with self.assertRaises(ValueError):
            evaluate_classifier(StimulusRuleBaseline(), train, [])


if __name__ == "__main__":
    unittest.main()
