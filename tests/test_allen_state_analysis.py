import importlib.util
from pathlib import Path
import unittest

from neurotwin_mvp.data import Trial


ROOT = Path(__file__).resolve().parents[1]
STATE_SCRIPT = ROOT / "scripts" / "analyze_allen_within_session_states.py"
WINDOW_SCRIPT = ROOT / "scripts" / "analyze_allen_fragile_alternative_windows.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class AllenStateAnalysisTests(unittest.TestCase):
    def test_chronological_states_cover_all_trials(self):
        module = load(STATE_SCRIPT, "states")
        trials = [Trial(i, 0.0, 0, 0, 1.0, float(i), {}) for i in range(10)]

        states = module.chronological_states(trials)

        self.assertEqual(sum(len(items) for items in states.values()), 10)
        self.assertEqual([trial.trial_id for trial in states["early"]], [0, 1, 2])

    def test_alternative_window_rescue_prioritizes_stimulus(self):
        module = load(WINDOW_SCRIPT, "windows")
        rows = [
            {"window_name": "decision", "observed_gain": 0.3, "p_value": 0.01},
            {"window_name": "stimulus", "observed_gain": 0.2, "p_value": 0.01},
        ]

        self.assertEqual(module.classify_rescue(rows, 0.05), "stimulus_window_rescue")


if __name__ == "__main__":
    unittest.main()
