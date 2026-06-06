from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    path = ROOT / "scripts" / "analyze_allen_blocked_fixed_validation.py"
    spec = importlib.util.spec_from_file_location("blocked_fixed_validation", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class BlockedFixedValidationTests(unittest.TestCase):
    def test_empty_summary(self):
        module = load_module()
        self.assertEqual(module.summarize([]), {})


if __name__ == "__main__":
    unittest.main()
