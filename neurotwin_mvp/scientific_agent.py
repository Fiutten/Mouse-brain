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


def audit_advanced_evidence(
    *,
    stability_summary: dict,
    graph_registry_summary: dict,
    latent_summary: dict,
    generator_warnings: list[str],
    minimum_mean_stability: float = 0.55,
    minimum_latent_positive_fraction: float = 0.5,
) -> ScientificAgentReport:
    """Audit the advanced evidence stack with explicit blocking rules.

    This is the deterministic contract we later wrap with an LLM/LangGraph
    planner. The deterministic layer remains the authority: an LLM may propose
    experiments, but these rules decide whether claims can advance.
    """
    findings: list[AgentFinding] = []
    mean_stability = float(stability_summary.get("mean_stability_score", 0.0))
    robust_sessions = int(stability_summary.get("robust_sessions", 0))
    controlled_edges = int(graph_registry_summary.get("controlled", 0))
    latent_positive_fraction = float(latent_summary.get("positive_gain_fraction", 0.0))
    if mean_stability < minimum_mean_stability:
        findings.append(
            AgentFinding(
                severity="major",
                claim="Session-level stability is below the promotion threshold.",
                evidence=f"mean_stability_score={mean_stability:.3f}",
                recommendation="Do not strengthen biological claims; inspect fragile sessions and latency strata.",
            )
        )
    if robust_sessions == 0:
        findings.append(
            AgentFinding(
                severity="major",
                claim="No session reaches robust stability status.",
                evidence=f"robust_sessions={robust_sessions}",
                recommendation="Treat the current result as exploratory until robust sessions appear.",
            )
        )
    if controlled_edges == 0:
        findings.append(
            AgentFinding(
                severity="major",
                claim="No functional graph edge is controlled under the evidence registry.",
                evidence=f"controlled_edges={controlled_edges}",
                recommendation="Keep graph edges as hypotheses, not conclusions.",
            )
        )
    if latent_positive_fraction < minimum_latent_positive_fraction:
        findings.append(
            AgentFinding(
                severity="moderate",
                claim="Latent temporal baseline is not consistently useful.",
                evidence=f"positive_gain_fraction={latent_positive_fraction:.3f}",
                recommendation="Do not invest in heavier latent models until baseline failures are understood.",
            )
        )
    for warning in generator_warnings:
        findings.append(
            AgentFinding(
                severity="minor",
                claim="Session generator emitted a caution.",
                evidence=warning,
                recommendation="Use generated sessions for stress tests only.",
            )
        )
    decision = "advance_to_microcircuit_design" if not any(item.severity == "major" for item in findings) else "hold_for_fragility_resolution"
    next_actions = [
        "Prioritize sessions marked robust or mixed for region-window mechanistic follow-up.",
        "Investigate fragile sessions before increasing model biological detail.",
        "Use latent baselines as the entry gate for heavier representation learning models.",
        "Keep generator-v2 outputs separate from empirical evidence in all reports.",
    ]
    return ScientificAgentReport(decision=decision, findings=findings, next_actions=next_actions)
