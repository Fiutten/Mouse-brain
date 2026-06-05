from dataclasses import dataclass
from pathlib import Path
import tempfile
import unittest

from neurotwin_mvp.allen_normalization import (
    AllenSessionNormalizer,
    TimeWindows,
    allen_acronym_to_model_region,
    count_spikes_in_window,
)
from neurotwin_mvp.artifacts import read_session_artifact


@dataclass
class FakeAllenSession:
    units: dict
    trials: list
    spike_times: dict


@dataclass
class FakeBehaviorEcephysSession:
    """Minimal fake for AllenSDK's BehaviorEcephysSession unit-table API."""

    unit_table: dict
    trials: list
    spike_times: dict
    channel_table: dict | None = None

    def get_units(self, filter_by_validity=False, filter_out_of_brain_units=False):
        return self.unit_table

    def get_channels(self, filter_by_validity=True):
        return self.channel_table or {}


class AllenNormalizationTests(unittest.TestCase):
    def test_acronym_mapping(self):
        self.assertEqual(allen_acronym_to_model_region("VISp"), "visual_cortex")
        self.assertEqual(allen_acronym_to_model_region("LGd"), "visual_thalamus")
        self.assertIsNone(allen_acronym_to_model_region("unknown"))

    def test_count_spikes_half_open_window(self):
        self.assertEqual(count_spikes_in_window([0.0, 0.1, 0.2, 0.3], 0.1, 0.3), 2)

    def test_time_window_validation(self):
        with self.assertRaises(ValueError):
            TimeWindows(stimulus_start=0.2, stimulus_end=0.2).validate()

    def test_normalize_fake_allen_session(self):
        fake = FakeAllenSession(
            units={
                1: {"structure_acronym": "VISp"},
                2: {"structure_acronym": "LGd"},
                3: {"structure_acronym": "CA1"},
            },
            spike_times={
                1: [1.01, 1.05, 1.30],
                2: [1.02, 1.10],
                3: [1.40],
            },
            trials=[
                {
                    "start_time": 1.0,
                    "go": True,
                    "aborted": False,
                    "image_name": "im_a",
                    "response": True,
                    "rewarded": True,
                    "response_time": 1.42,
                }
            ],
        )
        session = AllenSessionNormalizer().normalize(
            fake,
            ecephys_session_id=123,
            behavior_session_id=456,
            animal_id="mouse",
        )
        self.assertEqual(session.session_id, "123")
        self.assertEqual(len(session.trials), 1)
        self.assertIn("visual_cortex", session.trials[0].region_rates)
        self.assertIn("visual_thalamus", session.trials[0].region_rates)
        temporal = session.trials[0].metadata["region_rates_by_window"]
        self.assertEqual(set(temporal), {"baseline", "stimulus", "decision", "pre_response"})
        self.assertEqual(session.trials[0].region_rates, temporal["stimulus"])
        self.assertIn("response_time_s", session.trials[0].metadata)
        self.assertTrue(session.trials[0].metadata["time_window_valid"]["pre_response"])

    def test_pre_response_window_is_invalid_for_too_early_response(self):
        fake = FakeAllenSession(
            units={1: {"structure_acronym": "VISp"}},
            spike_times={1: [1.01, 1.05]},
            trials=[
                {
                    "start_time": 1.0,
                    "go": True,
                    "aborted": False,
                    "hit": True,
                    "response_time": 1.20,
                }
            ],
        )

        session = AllenSessionNormalizer().normalize(fake, ecephys_session_id=123)

        self.assertFalse(session.trials[0].metadata["time_window_valid"]["pre_response"])
        self.assertEqual(session.trials[0].metadata["region_rates_by_window"]["pre_response"]["visual_cortex"], 0.0)

    def test_normalize_behavior_ecephys_get_units_contract(self):
        fake = FakeBehaviorEcephysSession(
            unit_table={1: {"ecephys_structure_acronym": "VISp"}},
            spike_times={1: [1.01, 1.05]},
            trials=[{"start_time": 1.0, "go": True, "aborted": False, "image_name": "im_a"}],
        )
        session = AllenSessionNormalizer().normalize(fake, ecephys_session_id=123)
        self.assertEqual(session.region_names, ["visual_cortex"])

    def test_normalize_behavior_ecephys_peak_channel_contract(self):
        fake = FakeBehaviorEcephysSession(
            unit_table={1: {"peak_channel_id": 10}},
            channel_table={10: {"structure_acronym": "DG"}},
            spike_times={1: [1.01, 1.05]},
            trials=[{"start_time": 1.0, "go": True, "aborted": False, "image_name": "im_a"}],
        )
        session = AllenSessionNormalizer().normalize(fake, ecephys_session_id=123)
        self.assertEqual(session.region_names, ["hippocampus"])

    def test_export_fake_allen_session(self):
        fake = FakeAllenSession(
            units={1: {"structure_acronym": "VISp"}},
            spike_times={1: [1.01, 1.05]},
            trials=[{"start_time": 1.0, "go": True, "aborted": False, "image_name": "im_a"}],
        )
        with tempfile.TemporaryDirectory() as tmp:
            AllenSessionNormalizer().export(fake, tmp, ecephys_session_id=123)
            loaded = read_session_artifact(Path(tmp))
            self.assertEqual(loaded.dataset, "allen-visual-behavior-neuropixels")

    def test_filters_aborted_allen_behavior_trials(self):
        fake = FakeBehaviorEcephysSession(
            unit_table={1: {"peak_channel_id": 10}},
            channel_table={10: {"structure_acronym": "VISp"}},
            spike_times={1: [10.01, 20.01]},
            trials=[
                {
                    "start_time": 10.0,
                    "change_time_no_display_delay": 10.0,
                    "go": True,
                    "aborted": True,
                    "hit": True,
                },
                {
                    "start_time": 20.0,
                    "change_time_no_display_delay": 20.0,
                    "go": True,
                    "aborted": False,
                    "hit": True,
                    "initial_image_name": "im_a",
                    "change_image_name": "im_b",
                    "reward_volume": 0.003,
                },
            ],
        )
        session = AllenSessionNormalizer().normalize(fake, ecephys_session_id=123)
        self.assertEqual(len(session.trials), 1)
        self.assertEqual(session.trials[0].choice, 1)
        self.assertEqual(session.trials[0].reward, 1)
        self.assertEqual(session.trials[0].metadata["change_image_name"], "im_b")


if __name__ == "__main__":
    unittest.main()
