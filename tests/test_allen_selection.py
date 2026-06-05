from pathlib import Path
import unittest

from neurotwin_mvp.allen_selection import (
    covered_model_regions,
    load_allen_session_candidates,
    parse_structure_acronyms,
)


ROOT = Path(__file__).resolve().parents[1]


class AllenSelectionTests(unittest.TestCase):
    def test_parse_structure_acronyms(self):
        structures = parse_structure_acronyms("['VISp', 'LGd', 'CA1']")
        self.assertEqual(structures, ["VISp", "LGd", "CA1"])

    def test_covered_model_regions(self):
        covered = covered_model_regions(["VISp", "LGd", "CA1", "SNr", "MRN"])
        self.assertIn("visual_cortex", covered)
        self.assertIn("visual_thalamus", covered)
        self.assertIn("hippocampus", covered)
        self.assertIn("basal_ganglia", covered)
        self.assertIn("arousal_midbrain", covered)

    def test_load_candidates_from_downloaded_metadata(self):
        metadata = ROOT / "data" / "allen" / "project_metadata" / "ecephys_sessions.csv"
        if not metadata.exists():
            self.skipTest("Allen metadata CSV is not available")
        candidates = load_allen_session_candidates(metadata)
        self.assertGreater(len(candidates), 0)
        self.assertGreaterEqual(candidates[0].unit_count, 1500)
        self.assertIn("visual_cortex", candidates[0].covered_model_regions)
        self.assertIn("visual_thalamus", candidates[0].covered_model_regions)


if __name__ == "__main__":
    unittest.main()
