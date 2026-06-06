import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "export_allen_sessions_batch.py"


def load_batch_module():
    spec = importlib.util.spec_from_file_location("export_allen_sessions_batch", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class AllenBatchExportTests(unittest.TestCase):
    def test_nwb_url_points_to_public_allen_session_file(self):
        batch = load_batch_module()
        url = batch.nwb_url(1090800639)
        self.assertIn("visual-behavior-neuropixels-data.s3.us-west-2.amazonaws.com", url)
        self.assertTrue(url.endswith("/1090800639/ecephys_session_1090800639.nwb"))

    def test_local_nwb_path_matches_allensdk_cache_layout(self):
        batch = load_batch_module()
        path = batch.local_nwb_path(Path("cache"), 1090800639)
        self.assertEqual(
            path,
            Path(
                "cache/visual-behavior-neuropixels-0.5.0/"
                "behavior_ecephys_sessions/1090800639/ecephys_session_1090800639.nwb"
            ),
        )

    def test_curl_download_command_uses_external_retry_policy(self):
        batch = load_batch_module()
        command = batch._curl_download_command(
            curl_bin=Path("curl"),
            nwb_path=Path("cache/session.nwb"),
            ecephys_session_id=1090800639,
            connect_timeout=30,
            speed_time=90,
            speed_limit=2048,
            max_time=1800,
        )

        self.assertIn("-C", command)
        self.assertNotIn("--retry", command)
        self.assertNotIn("--retry-all-errors", command)

    def test_select_pending_candidates_skips_existing_artifacts(self):
        batch = load_batch_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            metadata = tmp_path / "ecephys_sessions.csv"
            datasets = tmp_path / "datasets"
            exported_artifact = datasets / "1" / "session.json"
            exported_artifact.parent.mkdir(parents=True)
            exported_artifact.write_text("{}", encoding="utf-8")
            with metadata.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=[
                        "ecephys_session_id",
                        "behavior_session_id",
                        "date_of_acquisition",
                        "equipment_name",
                        "session_type",
                        "mouse_id",
                        "genotype",
                        "sex",
                        "project_code",
                        "age_in_days",
                        "unit_count",
                        "probe_count",
                        "channel_count",
                        "structure_acronyms",
                        "image_set",
                        "prior_exposures_to_image_set",
                        "session_number",
                        "experience_level",
                        "prior_exposures_to_omissions",
                        "file_id",
                        "abnormal_histology",
                        "abnormal_activity",
                    ],
                )
                writer.writeheader()
                for session_id in [1, 2]:
                    writer.writerow(
                        {
                            "ecephys_session_id": session_id,
                            "behavior_session_id": session_id + 100,
                            "date_of_acquisition": "",
                            "equipment_name": "",
                            "session_type": "OPHYS_6_images_B",
                            "mouse_id": f"mouse-{session_id}",
                            "genotype": "",
                            "sex": "",
                            "project_code": "",
                            "age_in_days": "120",
                            "unit_count": "2500",
                            "probe_count": "6",
                            "channel_count": "2000",
                            "structure_acronyms": "['VISp', 'LGd', 'CA1', 'SNr', 'MRN']",
                            "image_set": "B",
                            "prior_exposures_to_image_set": "0",
                            "session_number": "1",
                            "experience_level": "Familiar",
                            "prior_exposures_to_omissions": "0",
                            "file_id": "",
                            "abnormal_histology": "",
                            "abnormal_activity": "",
                        }
                    )

            exported, pending = batch.select_pending_candidates(
                metadata_csv=metadata,
                datasets_root=datasets,
                candidate_limit=10,
            )
            self.assertEqual([item.ecephys_session_id for item in exported], [1])
            self.assertEqual([item.ecephys_session_id for item in pending], [2])

    def test_select_pending_candidates_can_follow_selector_order(self):
        batch = load_batch_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            metadata = tmp_path / "ecephys_sessions.csv"
            selector = tmp_path / "selector.json"
            with metadata.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=[
                        "ecephys_session_id",
                        "behavior_session_id",
                        "date_of_acquisition",
                        "equipment_name",
                        "session_type",
                        "mouse_id",
                        "genotype",
                        "sex",
                        "project_code",
                        "age_in_days",
                        "unit_count",
                        "probe_count",
                        "channel_count",
                        "structure_acronyms",
                        "image_set",
                        "prior_exposures_to_image_set",
                        "session_number",
                        "experience_level",
                        "prior_exposures_to_omissions",
                        "file_id",
                        "abnormal_histology",
                        "abnormal_activity",
                    ],
                )
                writer.writeheader()
                for session_id, units in [(1, 3500), (2, 2500), (3, 2000)]:
                    writer.writerow(
                        {
                            "ecephys_session_id": session_id,
                            "behavior_session_id": session_id + 100,
                            "date_of_acquisition": "",
                            "equipment_name": "",
                            "session_type": "EPHYS_1_images_H_5uL_reward",
                            "mouse_id": f"mouse-{session_id}",
                            "genotype": "",
                            "sex": "",
                            "project_code": "",
                            "age_in_days": "120",
                            "unit_count": str(units),
                            "probe_count": "6",
                            "channel_count": "2000",
                            "structure_acronyms": "['VISp', 'LGd', 'CA1', 'SNr', 'MRN']",
                            "image_set": "H",
                            "prior_exposures_to_image_set": "0",
                            "session_number": "1",
                            "experience_level": "Novel",
                            "prior_exposures_to_omissions": "0",
                            "file_id": "",
                            "abnormal_histology": "",
                            "abnormal_activity": "",
                        }
                    )
            selector.write_text(
                json.dumps({"candidates": [{"ecephys_session_id": 3}, {"ecephys_session_id": 2}]}),
                encoding="utf-8",
            )

            _, pending = batch.select_pending_candidates(
                metadata_csv=metadata,
                datasets_root=tmp_path / "datasets",
                candidate_limit=10,
                selector_json=selector,
            )

            self.assertEqual([item.ecephys_session_id for item in pending], [3, 2, 1])

    def test_refresh_target_diagnostics_runs_expected_script(self):
        batch = load_batch_module()
        commands = []

        def fake_run_command(command, dry_run):
            commands.append((command, dry_run))

        original = batch.run_command
        try:
            batch.run_command = fake_run_command
            batch.refresh_target_diagnostics(core_python=Path("python"), dry_run=True)
        finally:
            batch.run_command = original

        self.assertEqual(len(commands), 1)
        command, dry_run = commands[0]
        self.assertEqual(command[0], "python")
        self.assertTrue(str(command[1]).endswith("scripts/run_allen_target_diagnostics.py"))
        self.assertTrue(dry_run)


if __name__ == "__main__":
    unittest.main()
