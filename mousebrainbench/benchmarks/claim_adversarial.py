"""Adversarial claim benchmark for MouseBrainBench evaluators.

This benchmark deliberately constructs cases where prediction, reproducibility,
topology, direction, and structure-function evidence disagree. The target is not
biological realism. The target is to test whether an evaluator authorizes claims
that are unsupported by known truth.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mousebrainbench import __version__
from mousebrainbench.artifacts import code_revision
from mousebrainbench.validation.claim_evaluation import (
    CLAIM_TYPES,
    ClaimEvidence,
    ClaimGateEvaluator,
    CompensatoryScoreEvaluator,
    CorrelationOnlyEvaluator,
    claim_confusion_matrix,
)


DEFAULT_OUTPUT = Path("results/claim_adversarial_benchmark/summary.json")
DEFAULT_MARKDOWN = Path("results/claim_adversarial_benchmark/summary.md")


@dataclass(frozen=True)
class AdversarialCase:
    """One known-truth claim benchmark case."""

    name: str
    evidence: ClaimEvidence
    true_claims: tuple[str, ...]
    failure_mode: str


CASES = (
    AdversarialCase(
        name="directed_mechanistic_truth",
        evidence=ClaimEvidence(
            predictive_score=0.92,
            reproducibility_score=0.95,
            topology_effect=0.12,
            topology_specific=True,
            directed_fraction=0.85,
            independent_validation=True,
        ),
        true_claims=("predictive", "reproducible", "topology_specific", "directed", "mechanistic"),
        failure_mode="positive control with all non-causal mechanistic gates present",
    ),
    AdversarialCase(
        name="common_drive_high_prediction",
        evidence=ClaimEvidence(
            predictive_score=0.91,
            reproducibility_score=0.94,
            topology_effect=0.00,
            topology_specific=False,
            directed_fraction=0.00,
        ),
        true_claims=("predictive", "reproducible"),
        failure_mode="prediction and reproducibility caused by common drive",
    ),
    AdversarialCase(
        name="topology_without_direction",
        evidence=ClaimEvidence(
            predictive_score=0.82,
            reproducibility_score=0.91,
            topology_effect=0.11,
            topology_specific=True,
            directed_fraction=0.00,
        ),
        true_claims=("predictive", "reproducible", "topology_specific"),
        failure_mode="regional specificity exists but no directed signature is present",
    ),
    AdversarialCase(
        name="direction_without_topology",
        evidence=ClaimEvidence(
            predictive_score=0.80,
            reproducibility_score=0.89,
            topology_effect=0.00,
            topology_specific=False,
            directed_fraction=0.88,
        ),
        true_claims=("predictive", "reproducible", "directed"),
        failure_mode="timing exists but does not identify the proposed topology",
    ),
    AdversarialCase(
        name="spatial_confound_structure_function",
        evidence=ClaimEvidence(
            predictive_score=0.72,
            reproducibility_score=0.86,
            structure_function_effect=0.05,
            matched_structure_function_effect=0.00,
            structure_function_fdr_passed=False,
        ),
        true_claims=("predictive", "reproducible"),
        failure_mode="structure-function association disappears under matched controls",
    ),
    AdversarialCase(
        name="local_structure_function_truth",
        evidence=ClaimEvidence(
            predictive_score=0.68,
            reproducibility_score=0.82,
            structure_function_effect=0.04,
            matched_structure_function_effect=0.02,
            structure_function_fdr_passed=True,
        ),
        true_claims=("predictive", "reproducible", "structure_function"),
        failure_mode="positive local observational structure-function control",
    ),
    AdversarialCase(
        name="causal_component_truth",
        evidence=ClaimEvidence(
            predictive_score=0.86,
            reproducibility_score=0.90,
            topology_effect=0.10,
            topology_specific=True,
            directed_fraction=0.80,
            causal_evidence=True,
            independent_validation=True,
        ),
        true_claims=(
            "predictive",
            "reproducible",
            "topology_specific",
            "directed",
            "mechanistic",
            "causal",
        ),
        failure_mode="causal positive control without whole-brain coverage",
    ),
    AdversarialCase(
        name="whole_brain_digital_twin_truth",
        evidence=ClaimEvidence(
            predictive_score=0.91,
            reproducibility_score=0.93,
            topology_effect=0.10,
            topology_specific=True,
            directed_fraction=0.82,
            causal_evidence=True,
            whole_brain_coverage=True,
            independent_validation=True,
            reproducible_compute=True,
        ),
        true_claims=(
            "predictive",
            "reproducible",
            "topology_specific",
            "directed",
            "mechanistic",
            "causal",
            "digital_twin",
        ),
        failure_mode="upper-bound positive control for digital-twin wording",
    ),
)


def _evaluator_payload() -> tuple[
    dict[str, dict[str, set[str]]],
    list[dict[str, Any]],
]:
    evaluators = (
        CorrelationOnlyEvaluator(),
        CompensatoryScoreEvaluator(),
        ClaimGateEvaluator(),
    )
    decisions: dict[str, dict[str, set[str]]] = {}
    case_rows: list[dict[str, Any]] = []
    for evaluator in evaluators:
        evaluator_decisions: dict[str, set[str]] = {}
        for case in CASES:
            decision = evaluator.evaluate(case.evidence)
            evaluator_decisions[case.name] = set(decision.allowed_claims)
            case_rows.append(
                {
                    "case": case.name,
                    "evaluator": evaluator.name,
                    "allowed_claims": list(decision.allowed_claims),
                    "true_claims": list(case.true_claims),
                    "false_positive_claims": sorted(set(decision.allowed_claims) - set(case.true_claims)),
                    "false_negative_claims": sorted(set(case.true_claims) - set(decision.allowed_claims)),
                    "rationale": decision.rationale,
                    "failure_mode": case.failure_mode,
                }
            )
        decisions[evaluator.name] = evaluator_decisions
    return decisions, case_rows


def _aggregate_by_evaluator(confusion: list[dict[str, int | str]]) -> list[dict[str, Any]]:
    rows = []
    for evaluator in sorted({str(row["evaluator"]) for row in confusion}):
        subset = [row for row in confusion if row["evaluator"] == evaluator]
        tp = sum(int(row["tp"]) for row in subset)
        fp = sum(int(row["fp"]) for row in subset)
        tn = sum(int(row["tn"]) for row in subset)
        fn = sum(int(row["fn"]) for row in subset)
        rows.append(
            {
                "evaluator": evaluator,
                "tp": tp,
                "fp": fp,
                "tn": tn,
                "fn": fn,
                "false_positive_rate": fp / (fp + tn) if (fp + tn) else 0.0,
                "false_negative_rate": fn / (fn + tp) if (fn + tp) else 0.0,
            }
        )
    return rows


def run(output: Path = DEFAULT_OUTPUT, markdown: Path = DEFAULT_MARKDOWN) -> Path:
    """Run the adversarial claim benchmark."""

    truth = {case.name: set(case.true_claims) for case in CASES}
    decisions, case_rows = _evaluator_payload()
    confusion = claim_confusion_matrix(truth_by_case=truth, decisions_by_evaluator=decisions)
    aggregate = _aggregate_by_evaluator(confusion)
    gate = next(row for row in aggregate if row["evaluator"] == "claim_gate")
    payload = {
        "version": __version__,
        "git_revision": code_revision(),
        "analysis": "claim_adversarial_benchmark",
        "claim_types": list(CLAIM_TYPES),
        "cases": [
            {
                "case": case.name,
                "true_claims": list(case.true_claims),
                "failure_mode": case.failure_mode,
            }
            for case in CASES
        ],
        "case_evaluator_rows": case_rows,
        "confusion_matrix": confusion,
        "aggregate_by_evaluator": aggregate,
        "decision": (
            "claim_gate_blocks_adversarial_overclaims"
            if gate["fp"] == 0
            else "claim_gate_requires_revision"
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2))
    write_markdown(payload, markdown)
    return output


def write_markdown(payload: dict[str, Any], markdown: Path) -> None:
    """Write a compact Markdown report."""

    lines = [
        "# Claim Adversarial Benchmark",
        "",
        f"- Decision: `{payload['decision']}`",
        f"- Cases: `{len(payload['cases'])}`",
        f"- Claim types: `{len(payload['claim_types'])}`",
        "",
        "## Aggregate Confusion",
        "",
        "| Evaluator | TP | FP | TN | FN | FPR | FNR |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in payload["aggregate_by_evaluator"]:
        lines.append(
            f"| `{row['evaluator']}` | `{row['tp']}` | `{row['fp']}` | `{row['tn']}` | "
            f"`{row['fn']}` | `{row['false_positive_rate']:.3f}` | "
            f"`{row['false_negative_rate']:.3f}` |"
        )

    lines.extend(
        [
            "",
            "## False-Positive Claims By Case",
            "",
            "| Case | Evaluator | False-positive claims |",
            "|---|---|---|",
        ]
    )
    for row in payload["case_evaluator_rows"]:
        if row["false_positive_claims"]:
            claims = ", ".join(f"`{claim}`" for claim in row["false_positive_claims"])
            lines.append(f"| `{row['case']}` | `{row['evaluator']}` | {claims} |")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The benchmark is useful only if simple evaluators over-authorize claims in "
            "designed adversarial cases while the non-compensatory gate blocks them. "
            "That is the methodological gap MouseBrainBench should emphasize.",
            "",
        ]
    )
    markdown.parent.mkdir(parents=True, exist_ok=True)
    markdown.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()
    print(json.dumps({"output": str(run(args.output, args.markdown).resolve())}))


if __name__ == "__main__":
    main()
