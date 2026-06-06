import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "run_allen_temporal_permutation.py"


def load_temporal_permutation_module():
    spec = importlib.util.spec_from_file_location("run_allen_temporal_permutation", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class TemporalPermutationScriptTests(unittest.TestCase):
    def test_cache_path_includes_parameters_that_change_the_null(self):
        module = load_temporal_permutation_module()

        path = module.cache_path_for_session(
            Path("cache"),
            session_id="session-a",
            target_name="go_response",
            window_name="pre_response",
            n_permutations=500,
            seed=31,
        )

        self.assertEqual(
            path,
            Path("cache/go_response/pre_response/permutations_500/seed_31/session-a.json"),
        )

    def test_load_cached_row_rejects_incompatible_permutation_count(self):
        module = load_temporal_permutation_module()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cached.json"
            path.write_text(
                json.dumps(
                    {
                        "session_id": "session-a",
                        "target_name": "go_response",
                        "window_name": "pre_response",
                        "n_permutations": 50,
                        "seed": 31,
                        "p_value": 0.01,
                        "warnings": [],
                    }
                ),
                encoding="utf-8",
            )

            row = module.load_cached_row(
                path,
                target_name="go_response",
                window_name="pre_response",
                n_permutations=500,
                seed=31,
                alpha=0.05,
            )

            self.assertIsNone(row)

    def test_load_cached_row_marks_compatible_hit(self):
        module = load_temporal_permutation_module()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cached.json"
            path.write_text(
                json.dumps(
                    {
                        "session_id": "session-a",
                        "target_name": "go_response",
                        "window_name": "pre_response",
                        "n_permutations": 500,
                        "seed": 31,
                        "p_value": 0.01,
                        "warnings": ["kept for audit"],
                    }
                ),
                encoding="utf-8",
            )

            row = module.load_cached_row(
                path,
                target_name="go_response",
                window_name="pre_response",
                n_permutations=500,
                seed=31,
                alpha=0.05,
            )

            self.assertIsNotNone(row)
            self.assertTrue(row["significant"])
            self.assertEqual(row["cache_status"], "hit")
            self.assertEqual(row["warnings"], "kept for audit")


if __name__ == "__main__":
    unittest.main()
