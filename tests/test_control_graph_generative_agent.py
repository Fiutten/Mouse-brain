import unittest

from neurotwin_mvp.control_analysis import evaluate_window_controls, summarize_latency_strata
from neurotwin_mvp.functional_graph import build_functional_graph
from neurotwin_mvp.generative import GenerativeCalibration, simulate_evidence_sessions
from neurotwin_mvp.scientific_agent import audit_current_evidence


class ControlGraphGenerativeAgentTests(unittest.TestCase):
    def test_window_controls_require_candidate_margin(self):
        report = evaluate_window_controls(
            {
                "baseline": {"mean_gain": 0.02, "n_sessions": 10},
                "stimulus": {"mean_gain": 0.05, "n_sessions": 10},
                "pre_response": {"mean_gain": 0.09, "n_sessions": 10},
            },
            target_name="go_response",
            minimum_margin=0.02,
        )
        self.assertEqual(report.decision, "passes_window_controls")
        self.assertTrue(all(item.passes for item in report.window_controls))

    def test_latency_summary_groups_rows(self):
        summary = summarize_latency_strata(
            [
                {"latency_stratum": "fast", "observed_gain": 0.10, "p_value": 0.01},
                {"latency_stratum": "fast", "observed_gain": -0.02, "p_value": 0.50},
                {"latency_stratum": "slow", "observed_gain": 0.05, "p_value": 0.04},
            ]
        )
        self.assertEqual(summary["fast"]["n_sessions"], 2)
        self.assertAlmostEqual(summary["slow"]["positive_gain_fraction"], 1.0)

    def test_functional_graph_keeps_predictive_edges_explicit(self):
        report = build_functional_graph(
            target_name="go_response",
            window_name="pre_response",
            temporal_gain_mean=0.14,
            temporal_gain_ci95=[0.04, 0.24],
            regional_drops={"visual_cortex": 0.06, "hippocampus": -0.01},
            minimum_region_drop=0.02,
        )
        edges = {(edge.source, edge.relation, edge.target) for edge in report.edges}
        self.assertIn(("window:pre_response", "predicts", "target:go_response"), edges)
        self.assertIn(("region:visual_cortex", "contributes_to", "window:pre_response"), edges)
        self.assertNotIn(("region:hippocampus", "contributes_to", "window:pre_response"), edges)

    def test_generative_surrogate_is_reproducible(self):
        calibration = GenerativeCalibration(
            target_name="go_response",
            window_name="pre_response",
            n_sessions=3,
            temporal_gain_mean=0.10,
            temporal_gain_ci95=[0.02, 0.18],
            regional_drops={"visual_cortex": 0.05},
            seed=13,
        )
        first = simulate_evidence_sessions(calibration).to_dict()
        second = simulate_evidence_sessions(calibration).to_dict()
        self.assertEqual(first, second)
        self.assertEqual(len(first["generated_sessions"]), 3)

    def test_scientific_agent_blocks_without_controls(self):
        report = audit_current_evidence(
            temporal_ci95=[0.04, 0.24],
            temporal_positive_fraction=0.7,
            regional_ci95=[0.01, 0.11],
            control_decision="fails_window_controls",
            generative_warnings=[],
        )
        self.assertEqual(report.decision, "hold_strong_claims")
        self.assertTrue(any("control" in finding.claim.lower() for finding in report.findings))


if __name__ == "__main__":
    unittest.main()
