from pathlib import Path
import unittest

from neurotwin_mvp.datasets import AllenVisualBehaviorNeuropixelsLoader, IBLBrainwideMapLoader
from neurotwin_mvp.datasets.errors import DatasetConfigurationError


ROOT = Path(__file__).resolve().parents[1]


class DatasetAdapterTests(unittest.TestCase):
    def test_allen_adapter_has_plan(self):
        loader = AllenVisualBehaviorNeuropixelsLoader(ROOT / "data" / "allen")
        plan = loader.describe_plan()
        self.assertGreaterEqual(len(plan), 5)
        self.assertIn("AllenSDK", plan[0])

    def test_ibl_adapter_has_plan(self):
        loader = IBLBrainwideMapLoader(ROOT / "data" / "ibl")
        plan = loader.describe_plan()
        self.assertGreaterEqual(len(plan), 5)
        self.assertIn("ONE API", plan[0])

    def test_allen_load_is_explicitly_not_implemented(self):
        loader = AllenVisualBehaviorNeuropixelsLoader(ROOT / "data" / "allen")
        with self.assertRaises(DatasetConfigurationError):
            loader.load()

    def test_allen_metadata_smoke_test_contract_with_fake_cache(self):
        class FakeTable:
            columns = ["ecephys_session_id", "project_code"]

            def __len__(self):
                return 2

        class FakeCache:
            @classmethod
            def from_s3_cache(cls, cache_dir):
                return cls()

            def current_manifest(self):
                return "visual-behavior-neuropixels_project_manifest_fake.json"

            def get_ecephys_session_table(self):
                return FakeTable()

        class FakeAllenLoader(AllenVisualBehaviorNeuropixelsLoader):
            def _cache_class(self):
                return FakeCache

        loader = FakeAllenLoader(ROOT / "data" / "allen")
        result = loader.metadata_smoke_test()
        self.assertEqual(result.n_ecephys_sessions, 2)
        self.assertIn("ecephys_session_id", result.columns)
        self.assertEqual(result.source, "allensdk")

    def test_ibl_load_is_explicitly_not_implemented(self):
        loader = IBLBrainwideMapLoader(ROOT / "data" / "ibl")
        with self.assertRaises(DatasetConfigurationError):
            loader.load()


if __name__ == "__main__":
    unittest.main()
