from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    path = ROOT / "scripts" / "analyze_allen_state_adjusted_signal.py"
    spec = importlib.util.spec_from_file_location("state_adjusted_signal", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class StateAdjustedSignalTests(unittest.TestCase):
    def test_state_row_tracks_missingness(self):
        module = load_module()
        row = module.state_row({"running_speed_0_250": 2.0, "pupil_area_0_250": None})
        self.assertEqual(row["state:running_speed_0_250"], 2.0)
        self.assertEqual(row["state:pupil_area_0_250:missing"], 1.0)


if __name__ == "__main__":
    unittest.main()
