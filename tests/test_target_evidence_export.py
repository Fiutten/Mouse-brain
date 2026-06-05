import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "export_until_target_evidence.py"


def load_module():
    spec = importlib.util.spec_from_file_location("export_until_target_evidence", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TargetEvidenceExportTests(unittest.TestCase):
    def test_load_target_status_reads_usable_sessions_and_trials(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "target_diagnostics.json"
            path.write_text(
                json.dumps(
                    {
                        "aggregate": {
                            "go_response": {
                                "sessions": 6,
                                "usable_sessions": 4,
                                "labeled_trials": 1313,
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )

            status = module.load_target_status(path, "go_response")

        self.assertEqual(status.usable_sessions, 4)
        self.assertEqual(status.labeled_trials, 1313)

    def test_rebuild_target_reports_can_require_usable_target(self):
        module = load_module()
        commands = []

        def fake_run_command(command, dry_run=False):
            commands.append((command, dry_run))

        original = module.run_command
        try:
            module.run_command = fake_run_command
            module.rebuild_target_reports(
                core_python=Path("python"),
                target_name="go_response",
                reports_root=Path("reports"),
                n_permutations=500,
                min_sessions_for_claim=10,
                require_usable_target=True,
                dry_run=True,
            )
        finally:
            module.run_command = original

        self.assertEqual(len(commands), 2)
        report_command = commands[0][0]
        evidence_command = commands[1][0]
        self.assertIn("--require-usable-target", report_command)
        self.assertIn("--n-permutations", report_command)
        self.assertIn("500", report_command)
        self.assertIn("--min-sessions-for-claim", evidence_command)
        self.assertIn("10", evidence_command)

    def test_default_reports_root_tracks_target_name(self):
        module = load_module()

        path = module.default_reports_root("rewarded")

        self.assertEqual(path.name, "rewarded_usable")
        self.assertEqual(path.parent.name, "allen_targets")


if __name__ == "__main__":
    unittest.main()
