"""Deterministic scientific-agent layer.

LLM/LangGraph components will be useful later, but the first production-quality
step is a deterministic agent contract: read artifacts, apply explicit review
rules, and emit auditable next actions. This prevents an LLM from becoming an
unmeasured source of scientific claims.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class AgentFinding:
    """One audit finding produced from current artifacts."""

    severity: str
    claim: str
    evidence: str
    recommendation: str


@dataclass(frozen=True)
class ScientificAgentReport:
    """Auditable scientific-agent output."""

    decision: str
    findings: list[AgentFinding]
    next_actions: list[str]

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation."""
        return {
            "decision": self.decision,
            "findings": [asdict(item) for item in self.findings],
            "next_actions": list(self.next_actions),
        }


def audit_current_evidence(
    *,
    temporal_ci95: list[float],
    temporal_positive_fraction: float,
    regional_ci95: list[float],
    control_decision: str | None,
    generative_warnings: list[str],
) -> ScientificAgentReport:
    """Apply explicit reviewer rules to current evidence layers."""
    findings: list[AgentFinding] = []
    if len(temporal_ci95) != 2 or len(regional_ci95) != 2:
        raise ValueError("CI inputs must contain [low, high]")
    if temporal_ci95[0] <= 0.0:
        findings.append(
            AgentFinding(
                severity="major",
                claim="Temporal gain is not strictly positive under CI95.",
                evidence=f"temporal_ci95={temporal_ci95}",
                recommendation="Do not promote the temporal window until broader data or stronger controls improve stability.",
            )
        )
    if temporal_positive_fraction < 0.7:
        findings.append(
            AgentFinding(
                severity="major",
                claim="Temporal effect is not consistently positive across sessions.",
                evidence=f"positive_fraction={temporal_positive_fraction:.3f}",
                recommendation="Expand sessions or stratify failures before claiming cohort-level robustness.",
            )
        )
    if regional_ci95[0] <= 0.0:
        findings.append(
            AgentFinding(
                severity="moderate",
                claim="Regional contribution is uncertain under CI95.",
                evidence=f"regional_ci95={regional_ci95}",
                recommendation="Treat regional ranking as hypothesis generation.",
            )
        )
    if control_decision != "passes_window_controls":
        findings.append(
            AgentFinding(
                severity="major",
                claim="Temporal control gate has not passed.",
                evidence=f"control_decision={control_decision}",
                recommendation="Run/strengthen control windows and latency stratification before increasing biological claims.",
            )
        )
    for warning in generative_warnings:
        findings.append(
            AgentFinding(
                severity="minor",
                claim="Generative surrogate emitted a caution.",
                evidence=warning,
                recommendation="Keep surrogate outputs separate from empirical evidence in reports.",
            )
        )
    decision = "advance_with_controls" if not any(item.severity == "major" for item in findings) else "hold_strong_claims"
    next_actions = [
        "Keep pre_response as the candidate temporal hypothesis, not a final mechanism.",
        "Prioritize response-aligned controls, latency strata and cohort expansion before manuscript claims.",
        "Use the functional graph and generative surrogate to design experiments, not to replace empirical validation.",
    ]
    return ScientificAgentReport(decision=decision, findings=findings, next_actions=next_actions)
