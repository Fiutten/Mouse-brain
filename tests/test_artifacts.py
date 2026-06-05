from pathlib import Path
import tempfile
import unittest

from neurotwin_mvp.artifacts import ArtifactSessionLoader, read_session_artifact, write_session_artifact
from neurotwin_mvp.data import SyntheticNeuropixelsLoader


class ArtifactTests(unittest.TestCase):
    def test_session_artifact_roundtrip(self):
        session = SyntheticNeuropixelsLoader(n_trials=12, seed=21).load()
        with tempfile.TemporaryDirectory() as tmp:
            path = write_session_artifact(session, tmp)
            self.assertTrue(Path(path).exists())
            loaded = read_session_artifact(tmp)
            self.assertEqual(loaded.session_id, session.session_id)
            self.assertEqual(len(loaded.trials), len(session.trials))
            self.assertEqual(loaded.region_names, session.region_names)

    def test_artifact_session_loader(self):
        session = SyntheticNeuropixelsLoader(n_trials=12, seed=21).load()
        with tempfile.TemporaryDirectory() as tmp:
            write_session_artifact(session, tmp)
            loaded = ArtifactSessionLoader(tmp).load()
            self.assertEqual(loaded.dataset, "synthetic-neuropixels")


if __name__ == "__main__":
    unittest.main()
