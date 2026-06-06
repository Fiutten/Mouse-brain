from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    path = ROOT / "scripts" / "analyze_allen_direct_state_anatomy.py"
    spec = importlib.util.spec_from_file_location("direct_state_anatomy", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class DirectStateAnatomyTests(unittest.TestCase):
    def test_spearman_identifies_perfect_order(self):
        module = load_module()
        rho, p_value = module.spearman_permutation([1, 2, 3, 4], [2, 4, 6, 8], 100, 1)
        self.assertAlmostEqual(rho, 1.0)
        self.assertLessEqual(p_value, 0.1)

    def test_ranks_average_ties(self):
        module = load_module()
        self.assertEqual(module.ranks([1, 1, 3]), [0.5, 0.5, 2.0])


if __name__ == "__main__":
    unittest.main()
