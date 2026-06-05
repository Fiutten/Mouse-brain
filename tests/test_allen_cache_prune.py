import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "prune_allen_nwb_cache.py"


def load_prune_module():
    spec = importlib.util.spec_from_file_location("prune_allen_nwb_cache", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class AllenCachePruneTests(unittest.TestCase):
    def test_plan_requires_nonusable_session_and_normalized_artifact(self):
        prune = load_prune_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cache = root / "cache"
            datasets = root / "datasets"
            raw = (
                cache
                / "visual-behavior-neuropixels-0.5.0"
                / "behavior_ecephys_sessions"
                / "1"
                / "ecephys_session_1.nwb"
            )
            raw.parent.mkdir(parents=True)
            raw.write_bytes(b"raw")
            artifact = datasets / "1" / "session.json"
            artifact.parent.mkdir(parents=True)
            artifact.write_text("{}", encoding="utf-8")

            plan = prune.build_prune_plan(
                relation_rows=[
                    {"session_id": "1", "go_usable": False, "target_warnings": "imbalanced"},
                    {"session_id": "2", "go_usable": True, "target_warnings": ""},
                ],
                cache_dir=cache,
                datasets_root=datasets,
                target_name="go_response",
            )

            self.assertEqual(len(plan), 1)
            self.assertTrue(plan[0]["eligible_for_delete"])
            self.assertEqual(plan[0]["nwb_size_bytes"], 3)

    def test_execute_plan_deletes_only_eligible_files(self):
        prune = load_prune_module()
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp) / "session.nwb"
            raw.write_bytes(b"raw")
            outcomes = prune.execute_plan(
                [
                    {
                        "session_id": "1",
                        "eligible_for_delete": True,
                        "nwb_path": str(raw),
                    },
                    {
                        "session_id": "2",
                        "eligible_for_delete": False,
                        "nwb_path": str(Path(tmp) / "missing.nwb"),
                    },
                ]
            )

            self.assertFalse(raw.exists())
            self.assertEqual(outcomes[0]["delete_status"], "deleted")
            self.assertEqual(outcomes[1]["delete_status"], "skipped_not_eligible")


if __name__ == "__main__":
    unittest.main()
