import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class AllenAnimalCoverageTests(unittest.TestCase):
    def test_leave_one_animal_out_preserves_positive_means(self):
        module = load(ROOT / "scripts" / "analyze_allen_animal_aware_validation.py", "animal")
        rows = [
            {"animal_id": "a", "observed_gain": 0.1},
            {"animal_id": "b", "observed_gain": 0.2},
            {"animal_id": "c", "observed_gain": 0.3},
        ]

        result = module.leave_one_animal_out(rows)

        self.assertTrue(all(row["mean_gain"] > 0.0 for row in result))

    def test_region_presence_detects_group_difference(self):
        module = load(ROOT / "scripts" / "analyze_allen_recording_coverage.py", "coverage")
        rows = [
            {"session_id": "a", "regions": "visual_cortex"},
            {"session_id": "b", "regions": "visual_cortex"},
            {"session_id": "c", "regions": "hippocampus"},
            {"session_id": "d", "regions": "hippocampus"},
        ]

        result = module.region_presence(rows, {"a", "b"}, 100, 3)
        visual = next(row for row in result if row["region"] == "visual_cortex")

        self.assertEqual(visual["difference"], 1.0)


if __name__ == "__main__":
    unittest.main()
