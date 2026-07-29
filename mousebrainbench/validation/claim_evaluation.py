"""Claim-level evaluators for comparing standard and non-compensatory validation.

The goal of this module is not to define biological truth. It defines a compact
decision layer for controlled benchmarks where the ground-truth claim labels are
known. This lets MouseBrainBench test whether common evaluation shortcuts would
authorize claims that the evidence does not support.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


CLAIM_TYPES = (
    "predictive",
    "reproducible",
    "topology_specific",
    "directed",
    "structure_function",
    "mechanistic",
    "causal",
    "digital_twin",
)


@dataclass(frozen=True)
class ClaimEvidence:
    """Normalized evidence fields used by the comparative claim evaluators."""

    predictive_score: float
    reproducibility_score: float
    topology_effect: float = 0.0
    topology_specific: bool = False
    directed_fraction: float = 0.0
    structure_function_effect: float = 0.0
    matched_structure_function_effect: float = 0.0
    structure_function_fdr_passed: bool = False
    causal_evidence: bool = False
    whole_brain_coverage: bool = False
    independent_validation: bool = False
    reproducible_compute: bool = True


@dataclass(frozen=True)
class ClaimDecision:
    """Allowed claims produced by one evaluator."""

    evaluator: str
    allowed_claims: tuple[str, ...]
    rationale: str

    def as_dict(self) -> dict[str, object]:
        return {
            "evaluator": self.evaluator,
            "allowed_claims": list(self.allowed_claims),
            "rationale": self.rationale,
        }


class ClaimEvaluator(Protocol):
    """Protocol implemented by all claim evaluators."""

    name: str

    def evaluate(self, evidence: ClaimEvidence) -> ClaimDecision:
        """Return the claim set allowed by this evaluator."""


def _clip01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class CorrelationOnlyEvaluator:
    """Naive evaluator that overuses held-out prediction as claim support.

    This intentionally models a common failure mode: a model that predicts well
    is treated as supporting broad mechanistic language without asking whether
    topology, direction, or causal evidence is present.
    """

    name = "correlation_only"

    def __init__(self, threshold: float = 0.50) -> None:
        self.threshold = threshold

    def evaluate(self, evidence: ClaimEvidence) -> ClaimDecision:
        if evidence.predictive_score < self.threshold:
            return ClaimDecision(self.name, tuple(), "prediction below threshold")
        return ClaimDecision(
            self.name,
            (
                "predictive",
                "reproducible",
                "topology_specific",
                "directed",
                "structure_function",
                "mechanistic",
            ),
            "prediction above threshold is incorrectly treated as broad evidence",
        )


class CompensatoryScoreEvaluator:
    """Weighted-score evaluator where strong evidence can compensate weak blocks."""

    name = "compensatory_score"

    def __init__(self, threshold: float = 0.62) -> None:
        self.threshold = threshold

    def _score(self, evidence: ClaimEvidence) -> float:
        components = (
            _clip01(evidence.predictive_score),
            _clip01(evidence.reproducibility_score),
            _clip01(evidence.topology_effect / 0.08),
            _clip01(evidence.directed_fraction),
            _clip01(evidence.matched_structure_function_effect / 0.03),
        )
        weights = (0.25, 0.25, 0.20, 0.15, 0.15)
        return sum(weight * component for weight, component in zip(weights, components, strict=True))

    def evaluate(self, evidence: ClaimEvidence) -> ClaimDecision:
        claims: list[str] = []
        score = self._score(evidence)
        if evidence.predictive_score >= 0.30:
            claims.append("predictive")
        if evidence.reproducibility_score >= 0.70:
            claims.append("reproducible")
        if score >= self.threshold:
            claims.extend(["topology_specific", "directed", "structure_function", "mechanistic"])
        if score >= 0.85 and evidence.independent_validation:
            claims.append("digital_twin")
        return ClaimDecision(
            self.name,
            tuple(dict.fromkeys(claims)),
            f"weighted score={score:.3f}; high blocks can compensate failed blocks",
        )


class ClaimGateEvaluator:
    """MouseBrainBench non-compensatory claim gate."""

    name = "claim_gate"

    def evaluate(self, evidence: ClaimEvidence) -> ClaimDecision:
        claims: list[str] = []
        predictive = evidence.predictive_score >= 0.30
        reproducible = evidence.reproducibility_score >= 0.70
        topology = evidence.topology_specific and evidence.topology_effect >= 0.05
        directed = evidence.directed_fraction >= 0.50
        structure_function = (
            evidence.structure_function_effect > 0.0
            and evidence.matched_structure_function_effect >= 0.01
            and evidence.structure_function_fdr_passed
        )
        causal = evidence.causal_evidence
        if predictive:
            claims.append("predictive")
        if reproducible:
            claims.append("reproducible")
        if topology:
            claims.append("topology_specific")
        if directed:
            claims.append("directed")
        if structure_function:
            claims.append("structure_function")
        if predictive and reproducible and topology and directed:
            claims.append("mechanistic")
        if causal:
            claims.append("causal")
        if (
            evidence.whole_brain_coverage
            and evidence.independent_validation
            and evidence.reproducible_compute
            and causal
        ):
            claims.append("digital_twin")
        return ClaimDecision(
            self.name,
            tuple(claims),
            "claims require their own evidence gates and cannot compensate each other",
        )


def claim_confusion_matrix(
    *,
    truth_by_case: dict[str, set[str]],
    decisions_by_evaluator: dict[str, dict[str, set[str]]],
) -> list[dict[str, int | str]]:
    """Build a per-evaluator, per-claim confusion matrix."""

    rows: list[dict[str, int | str]] = []
    for evaluator, case_decisions in decisions_by_evaluator.items():
        for claim in CLAIM_TYPES:
            tp = fp = tn = fn = 0
            for case_name, truth in truth_by_case.items():
                predicted = claim in case_decisions.get(case_name, set())
                expected = claim in truth
                if predicted and expected:
                    tp += 1
                elif predicted and not expected:
                    fp += 1
                elif not predicted and expected:
                    fn += 1
                else:
                    tn += 1
            rows.append(
                {
                    "evaluator": evaluator,
                    "claim": claim,
                    "tp": tp,
                    "fp": fp,
                    "tn": tn,
                    "fn": fn,
                }
            )
    return rows

