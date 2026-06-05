from pathlib import Path
import unittest

from neurotwin_mvp.allen_selection import (
    AllenSessionCandidate,
    covered_model_regions,
    exported_session_ids,
    load_allen_session_candidates,
    load_target_relation_rows,
    parse_structure_acronyms,
    rank_target_aware_candidates,
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

    def test_load_target_relation_rows_accepts_current_sessions_key(self):
        with self.subTest("sessions key"):
            path = ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_session_relations.json"
            if path.exists():
                rows = load_target_relation_rows(path)
                self.assertGreaterEqual(len(rows), 1)
                self.assertIn("session_id", rows[0])

    def test_exported_session_ids_reads_normalized_artifacts(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "123" / "session.json").parent.mkdir(parents=True)
            (root / "123" / "session.json").write_text("{}", encoding="utf-8")
            (root / "bad-id" / "session.json").parent.mkdir(parents=True)
            (root / "bad-id" / "session.json").write_text("{}", encoding="utf-8")

            self.assertEqual(exported_session_ids(root), {123})

    def test_target_aware_ranking_uses_viability_not_only_metadata(self):
        candidates = [
            self._candidate(1, image_set="A", experience_level="Familiar", score=4000.0),
            self._candidate(2, image_set="B", experience_level="Novel", score=3000.0),
        ]
        relation_rows = [
            {"image_set": "A", "experience_level": "Familiar", "session_type": "type", "go_usable": False, "in_strict_evidence": False},
            {"image_set": "A", "experience_level": "Familiar", "session_type": "type", "go_usable": False, "in_strict_evidence": False},
            {"image_set": "B", "experience_level": "Novel", "session_type": "type", "go_usable": True, "in_strict_evidence": True, "permutation_significant": True},
            {"image_set": "B", "experience_level": "Novel", "session_type": "type", "go_usable": True, "in_strict_evidence": True, "permutation_significant": False},
        ]

        ranked = rank_target_aware_candidates(
            candidates,
            relation_rows,
            datasets_root=ROOT / "does-not-exist",
            top_n=2,
        )

        self.assertEqual(ranked[0].candidate.ecephys_session_id, 2)
        self.assertGreater(ranked[0].target_viability_score, ranked[1].target_viability_score)

    def _candidate(self, session_id: int, *, image_set: str, experience_level: str, score: float) -> AllenSessionCandidate:
        return AllenSessionCandidate(
            ecephys_session_id=session_id,
            behavior_session_id=session_id + 100,
            session_type="type",
            mouse_id=f"mouse-{session_id}",
            image_set=image_set,
            experience_level=experience_level,
            unit_count=2000,
            probe_count=6,
            channel_count=2000,
            structure_acronyms=["VISp", "LGd", "CA1"],
            covered_model_regions=["hippocampus", "visual_cortex", "visual_thalamus"],
            abnormal_histology="",
            abnormal_activity="",
            score=score,
        )


if __name__ == "__main__":
    unittest.main()
