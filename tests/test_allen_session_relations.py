import argparse
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "analyze_allen_session_relations.py"


def load_module():
    spec = importlib.util.spec_from_file_location("analyze_allen_session_relations", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class AllenSessionRelationsTests(unittest.TestCase):
    def test_pearson_returns_none_for_too_few_or_constant_values(self):
        module = load_module()

        self.assertIsNone(module.pearson([1.0, 2.0], [1.0, 2.0]))
        self.assertIsNone(module.pearson([1.0, 1.0, 1.0], [1.0, 2.0, 3.0]))
        self.assertAlmostEqual(module.pearson([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]), 1.0)

    def test_build_report_separates_target_failures_from_evidence_failures(self):
        module = load_module()
        args = argparse.Namespace(target_name="go_response", alpha=0.05)
        rows = [
            self._row("s1", usable=False, minority=0.10, gain=None, p_value=None),
            self._row("s2", usable=True, minority=0.30, gain=0.12, p_value=0.01),
            self._row("s3", usable=True, minority=0.45, gain=-0.02, p_value=0.90),
        ]

        report = module.build_report(rows, args)

        self.assertEqual(report["n_sessions"], 3)
        self.assertEqual(report["n_usable"], 2)
        self.assertEqual(report["n_not_usable"], 1)
        self.assertEqual(report["n_strict_evidence"], 2)
        self.assertEqual(report["n_permutation_significant"], 1)
        self.assertEqual(report["non_usable_warning_counts"]["minority class below 0.20"], 1)
        self.assertIn("go_response class imbalance", " ".join(report["interpretation"]))

    def test_project_metadata_remains_authoritative_across_batch_snapshots(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            metadata = root / "ecephys_sessions.csv"
            metadata.write_text(
                "ecephys_session_id,session_type,mouse_id,unit_count,probe_count,image_set,experience_level\n"
                "1,type-a,mouse-a,2000,6,H,Novel\n",
                encoding="utf-8",
            )
            status = root / "status.json"
            status.write_text(
                json.dumps({"already_exported": [], "attempted": []}),
                encoding="utf-8",
            )

            result = module.load_metadata_by_session(status, metadata)

            self.assertEqual(result["1"]["probe_count"], "6")
            self.assertEqual(result["1"]["experience_level"], "Novel")

    def _row(self, session_id, usable, minority, gain, p_value):
        # The relation report deliberately carries both target viability and
        # evidence columns so that these two failure modes cannot be conflated.
        warning = "" if usable else "Target `go_response` is imbalanced; minority class below 0.20"
        return {
            "session_id": session_id,
            "experience_level": "Familiar",
            "n_total_trials": 100,
            "go_labeled_trials": 80,
            "go_positive_rate": 1.0 - minority,
            "go_minority_fraction": minority,
            "go_usable": usable,
            "target_warnings": warning,
            "n_catch_trials": 20,
            "zero_latency_fraction": 0.0,
            "in_strict_evidence": gain is not None,
            "permutation_observed_gain": gain,
            "permutation_p_value": p_value,
            "permutation_significant": bool(p_value is not None and p_value <= 0.05),
            "multisplit_mean_gain": gain,
        }


if __name__ == "__main__":
    unittest.main()
