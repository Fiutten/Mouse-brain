import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "analyze_allen_cross_session_uncertainty.py"


def load_module():
    spec = importlib.util.spec_from_file_location("analyze_allen_cross_session_uncertainty", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CrossSessionUncertaintyTests(unittest.TestCase):
    def test_percentile_interpolates(self):
        module = load_module()

        self.assertEqual(module.percentile([0.0, 10.0], 0.5), 5.0)
        self.assertEqual(module.percentile([0.0, 10.0], 0.0), 0.0)
        self.assertEqual(module.percentile([0.0, 10.0], 1.0), 10.0)

    def test_leave_one_out_reports_session_means(self):
        module = load_module()

        rows = module.leave_one_out({"a": 1.0, "b": 3.0, "c": 5.0})

        by_left_out = {row["left_out_session_id"]: row["mean"] for row in rows}
        self.assertEqual(by_left_out["a"], 4.0)
        self.assertEqual(by_left_out["b"], 3.0)
        self.assertEqual(by_left_out["c"], 2.0)


if __name__ == "__main__":
    unittest.main()
