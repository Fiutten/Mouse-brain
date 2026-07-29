from mousebrainbench.validation.claim_evaluation import (
    ClaimEvidence,
    ClaimGateEvaluator,
    CompensatoryScoreEvaluator,
    CorrelationOnlyEvaluator,
)


def test_claim_gate_blocks_prediction_only_mechanistic_claim() -> None:
    evidence = ClaimEvidence(predictive_score=0.95, reproducibility_score=0.95)

    naive = CorrelationOnlyEvaluator().evaluate(evidence)
    gate = ClaimGateEvaluator().evaluate(evidence)

    assert "mechanistic" in naive.allowed_claims
    assert "mechanistic" not in gate.allowed_claims
    assert set(gate.allowed_claims) == {"predictive", "reproducible"}


def test_compensatory_score_can_overauthorize_when_blocks_are_missing() -> None:
    evidence = ClaimEvidence(
        predictive_score=0.95,
        reproducibility_score=0.95,
        topology_effect=0.20,
        topology_specific=True,
        directed_fraction=0.0,
        matched_structure_function_effect=0.03,
        structure_function_effect=0.04,
        structure_function_fdr_passed=True,
    )

    compensatory = CompensatoryScoreEvaluator(threshold=0.60).evaluate(evidence)
    gate = ClaimGateEvaluator().evaluate(evidence)

    assert "mechanistic" in compensatory.allowed_claims
    assert "mechanistic" not in gate.allowed_claims
    assert "directed" not in gate.allowed_claims
