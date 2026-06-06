from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    path = ROOT / "scripts" / "analyze_allen_hierarchical_heterogeneity.py"
    spec = importlib.util.spec_from_file_location("hierarchical_heterogeneity", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class HierarchicalHeterogeneityTests(unittest.TestCase):
    def test_cluster_bootstrap_preserves_positive_constant(self):
        module = load_module()
        rows = [
            {"animal_id": "a", "gain": 0.1},
            {"animal_id": "a", "gain": 0.2},
            {"animal_id": "b", "gain": 0.3},
        ]
        low, high = module.cluster_bootstrap_ci(rows, iterations=1000)
        self.assertGreater(low, 0.0)
        self.assertGreaterEqual(high, low)

    def test_stable_partition_is_deterministic(self):
        module = load_module()
        self.assertEqual(module.stable_partition("mouse"), module.stable_partition("mouse"))

    def test_binomial_tail(self):
        module = load_module()
        self.assertAlmostEqual(module.binomial_positive_tail(2, 2), 0.25)


if __name__ == "__main__":
    unittest.main()
