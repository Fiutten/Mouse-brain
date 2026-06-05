import unittest

from neurotwin_mvp.control_analysis import evaluate_window_controls, summarize_latency_strata
from neurotwin_mvp.functional_graph import build_functional_graph, build_graph_evidence_registry
from neurotwin_mvp.generative import (
    GenerativeCalibration,
    SessionGeneratorCalibration,
    generate_calibrated_session,
    simulate_evidence_sessions,
)
from neurotwin_mvp.latent import run_latent_temporal_baseline
from neurotwin_mvp.scientific_agent import audit_advanced_evidence, audit_current_evidence
from neurotwin_mvp.stability import build_stability_matrix


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

    def test_stability_matrix_scores_sessions(self):
        report = build_stability_matrix(
            target_name="go_response",
            window_name="pre_response",
            temporal_rows=[{"session_id": "s1", "observed_gain": 0.2, "p_value": 0.01}],
            regional_rows=[{"session_id": "s1", "region": "visual_cortex", "drop_from_full": 0.1}],
            latency_rows=[
                {"session_id": "s1", "latency_stratum": "fast", "observed_gain": 0.1, "p_value": 0.1},
                {"session_id": "s1", "latency_stratum": "slow", "observed_gain": 0.1, "p_value": 0.01},
            ],
        )
        self.assertEqual(report.rows[0].status, "robust")
        self.assertGreater(report.summary["mean_stability_score"], 0.7)

    def test_graph_evidence_registry_promotes_controlled_edges(self):
        graph = build_functional_graph(
            target_name="go_response",
            window_name="pre_response",
            temporal_gain_mean=0.14,
            temporal_gain_ci95=[0.04, 0.24],
            regional_drops={"visual_cortex": 0.06},
        )
        registry = build_graph_evidence_registry(
            graph,
            stability_by_session=[
                {"session_id": "s1", "stability_score": 0.8, "status": "robust"},
                {"session_id": "s2", "stability_score": 0.8, "status": "robust"},
            ],
            temporal_ci95_low=0.04,
            control_decision="passes_window_controls",
        )
        self.assertGreaterEqual(registry.summary["controlled"], 1)

    def test_calibrated_session_generator_outputs_temporal_metadata(self):
        report = generate_calibrated_session(
            SessionGeneratorCalibration(
                target_name="go_response",
                window_names=["baseline", "pre_response"],
                region_names=["visual_cortex", "basal_ganglia"],
                n_trials=120,
                positive_rate=0.5,
                latency_mean_ms=300.0,
                latency_std_ms=30.0,
                region_window_means={
                    "baseline": {"visual_cortex": 1.0, "basal_ganglia": 0.5},
                    "pre_response": {"visual_cortex": 1.2, "basal_ganglia": 0.6},
                },
                seed=17,
            )
        )
        self.assertEqual(len(report.session.trials), 120)
        self.assertIn("region_rates_by_window", report.session.trials[0].metadata)

    def test_latent_temporal_baseline_runs_on_generated_session(self):
        generated = generate_calibrated_session(
            SessionGeneratorCalibration(
                target_name="go_response",
                window_names=["baseline", "stimulus", "pre_response"],
                region_names=["visual_cortex", "basal_ganglia"],
                n_trials=160,
                positive_rate=0.5,
                latency_mean_ms=300.0,
                latency_std_ms=30.0,
                region_window_means={
                    "baseline": {"visual_cortex": 1.0, "basal_ganglia": 0.5},
                    "stimulus": {"visual_cortex": 1.1, "basal_ganglia": 0.5},
                    "pre_response": {"visual_cortex": 1.2, "basal_ganglia": 0.6},
                },
                seed=19,
            )
        )
        report = run_latent_temporal_baseline(generated.session, target_name="go_response", n_components=2)
        self.assertEqual(report.n_components, 2)
        self.assertGreaterEqual(report.explained_variance_fraction, 0.0)

    def test_advanced_agent_blocks_low_stability(self):
        report = audit_advanced_evidence(
            stability_summary={"mean_stability_score": 0.2, "robust_sessions": 0},
            graph_registry_summary={"controlled": 0},
            latent_summary={"positive_gain_fraction": 0.0},
            generator_warnings=[],
        )
        self.assertEqual(report.decision, "hold_for_fragility_resolution")


if __name__ == "__main__":
    unittest.main()
