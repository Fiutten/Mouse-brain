import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "analyze_allen_fragile_sessions.py"


def load_fragility_module():
    spec = importlib.util.spec_from_file_location("analyze_allen_fragile_sessions", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class AllenFragilityAnalysisTests(unittest.TestCase):
    def test_classifies_global_temporal_null_when_main_and_latency_checks_fail(self):
        module = load_fragility_module()

        mode = module.classify_failure_mode(
            [
                "temporal_gain_positive",
                "temporal_significant",
                "fast_gain_positive",
                "slow_gain_positive",
            ]
        )

        self.assertEqual(mode, "global_temporal_null")

    def test_explain_row_joins_metadata_and_failed_checks(self):
        module = load_fragility_module()

        explained = module.explain_row(
            {
                "session_id": "s1",
                "status": "fragile",
                "stability_score": "0.2",
                "temporal_gain": "0.0",
                "temporal_p_value": "0.5",
                "temporal_significant": "False",
                "visual_cortex_drop": "-0.1",
                "fast_latency_gain": "0.0",
                "fast_latency_significant": "False",
                "slow_latency_gain": "0.2",
                "slow_latency_significant": "False",
            },
            {
                "go_labeled_trials": "100",
                "go_positive_rate": "0.4",
                "go_minority_fraction": "0.4",
                "mean_latency_ms": "500.0",
                "median_latency_ms": "450.0",
                "zero_latency_fraction": "0.1",
                "region_count": "4",
                "regions": "visual_cortex,hippocampus",
            },
        )

        self.assertEqual(explained["session_id"], "s1")
        self.assertEqual(explained["go_labeled_trials"], 100)
        self.assertIn("pre_response gain is not positive", explained["failed_checks"])
        self.assertEqual(explained["failure_mode"], "weak_or_non_significant_temporal_effect")


if __name__ == "__main__":
    unittest.main()
