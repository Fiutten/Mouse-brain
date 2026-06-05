from pathlib import Path
import tempfile
import unittest

from neurotwin_mvp.registry import ExperimentRegistry, sha256_file
from neurotwin_mvp.workflow import run_workflow


ROOT = Path(__file__).resolve().parents[1]


class RegistryTests(unittest.TestCase):
    def test_sha256_file_is_stable(self):
        config = ROOT / "configs" / "mouse_level0.json"
        self.assertEqual(sha256_file(config), sha256_file(config))

    def test_registry_persists_run(self):
        config = ROOT / "configs" / "mouse_level0.json"
        report = run_workflow(str(config), seed=13)
        with tempfile.TemporaryDirectory() as tmp:
            registry = ExperimentRegistry(tmp)
            record = registry.create_run(report, config_path=config, seed=13, run_id="test-run")
            run_dir = Path(record.artifact_dir)
            self.assertTrue((run_dir / "manifest.json").exists())
            self.assertTrue((run_dir / "report.json").exists())
            self.assertTrue((run_dir / "config_snapshot.json").exists())
            self.assertEqual(len(registry.list_runs()), 1)


if __name__ == "__main__":
    unittest.main()
