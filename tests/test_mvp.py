from pathlib import Path
import unittest

from neurotwin_mvp.agents import HypothesisAgent, ReviewerAgent
from neurotwin_mvp.config import load_config
from neurotwin_mvp.experiments import evaluate_visual_decision
from neurotwin_mvp.knowledge import seed_mouse_decision_graph
from neurotwin_mvp.regional_model import RegionalModel


ROOT = Path(__file__).resolve().parents[1]


class PrototypeTests(unittest.TestCase):
    def test_config_loads(self):
        config = load_config(ROOT / "configs" / "mouse_level0.json")
        self.assertEqual(len(config.regions), 6)
        self.assertGreater(len(config.connections), 0)

    def test_visual_decision_has_sensitivity(self):
        model = RegionalModel(load_config(ROOT / "configs" / "mouse_level0.json"), seed=1)
        result = evaluate_visual_decision(model, repeats=10)
        self.assertGreater(result.sensitivity, 0.05)

    def test_thalamus_lesion_reduces_sensitivity(self):
        model = RegionalModel(load_config(ROOT / "configs" / "mouse_level0.json"), seed=2)
        intact = evaluate_visual_decision(model, repeats=10)
        lesioned = evaluate_visual_decision(model, lesion="visual_thalamus", repeats=10)
        self.assertLess(lesioned.sensitivity, intact.sensitivity)

    def test_agents_produce_reviewable_hypotheses(self):
        graph = seed_mouse_decision_graph()
        hypotheses = HypothesisAgent().propose(graph)
        findings = ReviewerAgent().review(hypotheses)
        self.assertGreaterEqual(len(hypotheses), 2)
        self.assertIn("No blocking issues", findings[0])


if __name__ == "__main__":
    unittest.main()
