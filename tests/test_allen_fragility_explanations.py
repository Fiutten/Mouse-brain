import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "analyze_allen_fragility_explanations.py"


def load_module():
    spec = importlib.util.spec_from_file_location("analyze_allen_fragility_explanations", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class AllenFragilityExplanationTests(unittest.TestCase):
    def test_numeric_comparison_detects_large_group_difference(self):
        module = load_module()
        rows = [
            {"fragile": True, "feature": "0"},
            {"fragile": True, "feature": "1"},
            {"fragile": False, "feature": "10"},
            {"fragile": False, "feature": "11"},
        ]

        result = module.numeric_comparison(
            rows,
            "feature",
            n_permutations=1000,
            seed=3,
        )

        self.assertLess(result["mean_difference"], 0.0)
        self.assertLess(result["standardized_mean_difference"], -5.0)
        self.assertLess(result["permutation_p_value"], 0.5)

    def test_animal_recurrence_distinguishes_consistent_and_mixed_animals(self):
        module = load_module()
        result = module.animal_recurrence(
            [
                {"animal_id": "a", "status": "fragile"},
                {"animal_id": "a", "status": "fragile"},
                {"animal_id": "b", "status": "fragile"},
                {"animal_id": "b", "status": "robust"},
            ]
        )

        self.assertIn("a", result["consistent_fragile_animals"])
        self.assertIn("b", result["mixed_status_animals"])

    def test_join_rows_marks_incomplete_metadata(self):
        module = load_module()
        rows = module.join_rows(
            [{"session_id": "s1", "status": "fragile"}],
            [{"session_id": "s1", "experience_level": "", "probe_count": "6"}],
        )

        self.assertEqual(rows[0]["metadata_complete"], 0)


if __name__ == "__main__":
    unittest.main()
