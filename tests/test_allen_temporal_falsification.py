from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

from neurotwin_mvp.data import Session, Trial


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    path = ROOT / "scripts" / "analyze_allen_temporal_falsification.py"
    spec = importlib.util.spec_from_file_location("temporal_falsification", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class TemporalFalsificationTests(unittest.TestCase):
    def test_landmark_excludes_early_responses_and_keeps_misses(self):
        module = load_module()
        trials = [
            Trial(0, 1.0, 1, 1, 300.0, 0.5, {}, {"response_latency_s": 0.30}),
            Trial(1, 1.0, 1, 1, 800.0, 0.5, {}, {"response_latency_s": 0.80}),
            Trial(2, 1.0, 0, 0, 0.0, 0.5, {}, {}),
        ]
        session = Session("s", "a", "d", trials, [])
        view = module.landmark_view(session, 0.75)
        self.assertEqual([trial.choice for trial in view.trials], [1, 0])
        self.assertEqual([trial.trial_id for trial in view.trials], [0, 1])

    def test_benjamini_hochberg_is_monotone_by_rank(self):
        module = load_module()
        raw = [0.001, 0.02, 0.04, 0.50]
        adjusted = module.benjamini_hochberg(raw)
        ranked = [adjusted[index] for index in sorted(range(len(raw)), key=raw.__getitem__)]
        self.assertEqual(ranked, sorted(ranked))
        self.assertTrue(all(value >= raw[index] for index, value in enumerate(adjusted)))

    def test_dynamic_window_metadata_exposes_duration(self):
        module = load_module()
        trial = Trial(
            0,
            1.0,
            1,
            1,
            300.0,
            0.5,
            {},
            {
                "time_windows_s": {"pre_response": {"start": 0.25, "end": 0.55}},
                "time_window_valid": {"pre_response": True},
            },
        )
        row = module.dynamic_window_metadata(trial)
        self.assertAlmostEqual(row["window_duration_s"], 0.30)
        self.assertEqual(row["window_valid"], 1.0)


if __name__ == "__main__":
    unittest.main()
