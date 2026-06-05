"""Deterministic agent MVP.

These classes mimic the roles we want before introducing external LLM calls.
The point is to make the workflow testable and auditable first.

Important: these are not autonomous scientific agents yet. They are deterministic
stand-ins that define the interface and expected outputs for future LLM/RAG
components.
"""

from __future__ import annotations

from dataclasses import dataclass

from .knowledge import KnowledgeGraph


@dataclass(frozen=True)
class Hypothesis:
    """A testable hypothesis proposed by the workflow."""

    statement: str
    intervention: str
    expected_effect: str
    required_metric: str
    evidence: list[str]


class HypothesisAgent:
    """Generate narrow, executable hypotheses from the evidence graph."""

    def propose(self, graph: KnowledgeGraph) -> list[Hypothesis]:
        """Return initial lesion hypotheses with evidence references."""
        evidence = [item.claim for item in graph.evidence]
        return [
            Hypothesis(
                statement="Visual thalamus lesion should reduce stimulus sensitivity.",
                intervention="lesion:visual_thalamus",
                expected_effect="Lower positive-vs-negative stimulus action-probability gap.",
                required_metric="sensitivity",
                evidence=evidence[:2],
            ),
            Hypothesis(
                statement="Basal ganglia lesion should impair action selection readout.",
                intervention="lesion:basal_ganglia",
                expected_effect="Compressed decision probability near indifference.",
                required_metric="sensitivity",
                evidence=evidence[:2],
            ),
        ]


class ReviewerAgent:
    """Apply basic rejection checks before experiments run."""

    def review(self, hypotheses: list[Hypothesis]) -> list[str]:
        """Reject unsupported, unmeasured or out-of-scope hypotheses."""
        findings: list[str] = []
        for hypothesis in hypotheses:
            if not hypothesis.evidence:
                findings.append(f"Reject '{hypothesis.statement}': no supporting evidence.")
            if "conscious" in hypothesis.statement.lower():
                findings.append(f"Reject '{hypothesis.statement}': consciousness claim is out of scope.")
            if not hypothesis.required_metric:
                findings.append(f"Reject '{hypothesis.statement}': no metric.")
        if not findings:
            findings.append("No blocking issues. Hypotheses are narrow and testable.")
        return findings
