from __future__ import annotations

import importlib.util
import math
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    path = ROOT / "scripts" / "export_allen_state_anatomy.py"
    spec = importlib.util.spec_from_file_location("state_anatomy_export", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class StateAnatomyExportTests(unittest.TestCase):
    def test_finite_rejects_nan_and_text(self):
        module = load_module()
        self.assertFalse(module.finite(math.nan))
        self.assertFalse(module.finite("missing"))
        self.assertTrue(module.finite(1.2))


if __name__ == "__main__":
    unittest.main()
