"""Empirical functional graph utilities.

The graph layer turns session-level predictive evidence into a compact regional
network. It is not an anatomical connectome: edges encode observed predictive
relationships among coarse regions, temporal windows and behavioral targets.
That distinction matters because it keeps the system honest about what the data
currently support.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class FunctionalNode:
    """One node in the empirical functional graph."""

    node_id: str
    kind: str
    label: str
    attributes: dict[str, float | str]


@dataclass(frozen=True)
class FunctionalEdge:
    """Directed empirical relation between graph nodes."""

    source: str
    relation: str
    target: str
    weight: float
    evidence: str


@dataclass(frozen=True)
class FunctionalGraphReport:
    """Serializable report for the empirical graph layer."""

    target_name: str
    window_name: str
    nodes: list[FunctionalNode]
    edges: list[FunctionalEdge]
    interpretation: list[str]

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation."""
        return {
            "target_name": self.target_name,
            "window_name": self.window_name,
            "nodes": [asdict(node) for node in self.nodes],
            "edges": [asdict(edge) for edge in self.edges],
            "interpretation": list(self.interpretation),
        }


@dataclass(frozen=True)
class EvidenceEdgeRecord:
    """Evidence registry record for one functional graph edge."""

    source: str
    relation: str
    target: str
    weight: float
    evidence: str
    strength: float
    fragility: float
    state: str
    rationale: str

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(frozen=True)
class GraphEvidenceRegistry:
    """Accumulated edge evidence with explicit interpretability states."""

    target_name: str
    window_name: str
    records: list[EvidenceEdgeRecord]
    summary: dict[str, int]
    warnings: list[str]

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation."""
        return {
            "target_name": self.target_name,
            "window_name": self.window_name,
            "records": [record.to_dict() for record in self.records],
            "summary": dict(self.summary),
            "warnings": list(self.warnings),
        }


def build_functional_graph(
    *,
    target_name: str,
    window_name: str,
    temporal_gain_mean: float,
    temporal_gain_ci95: list[float],
    regional_drops: dict[str, float],
    minimum_region_drop: float = 0.02,
) -> FunctionalGraphReport:
    """Build an empirical graph from temporal and regional evidence.

    Regions are connected to the candidate temporal window when their
    leave-one-region-out drop is positive enough to be worth following. The
    temporal window is then linked to the behavioral target using the
    cross-session gain estimate.
    """
    if len(temporal_gain_ci95) != 2:
        raise ValueError("temporal_gain_ci95 must contain [low, high]")
    nodes = [
        FunctionalNode(
            node_id=f"target:{target_name}",
            kind="behavioral_target",
            label=target_name,
            attributes={},
        ),
        FunctionalNode(
            node_id=f"window:{window_name}",
            kind="temporal_window",
            label=window_name,
            attributes={
                "mean_gain": temporal_gain_mean,
                "ci95_low": float(temporal_gain_ci95[0]),
                "ci95_high": float(temporal_gain_ci95[1]),
            },
        ),
    ]
    edges = [
        FunctionalEdge(
            source=f"window:{window_name}",
            relation="predicts",
            target=f"target:{target_name}",
            weight=temporal_gain_mean,
            evidence="cross_session_temporal_gain",
        )
    ]
    for region, drop in sorted(regional_drops.items(), key=lambda item: item[1], reverse=True):
        nodes.append(
            FunctionalNode(
                node_id=f"region:{region}",
                kind="coarse_region",
                label=region,
                attributes={"drop_from_full": float(drop)},
            )
        )
        if drop >= minimum_region_drop:
            edges.append(
                FunctionalEdge(
                    source=f"region:{region}",
                    relation="contributes_to",
                    target=f"window:{window_name}",
                    weight=float(drop),
                    evidence="temporal_regional_feature_ablation",
                )
            )
    interpretation = [
        "Edges are predictive empirical relations, not anatomical projections.",
        "Positive region-to-window edges prioritize hypotheses for later controls or perturbation data.",
    ]
    if temporal_gain_ci95[0] <= 0.0:
        interpretation.append("The temporal gain confidence interval crosses zero; treat graph edges as exploratory.")
    return FunctionalGraphReport(
        target_name=target_name,
        window_name=window_name,
        nodes=nodes,
        edges=edges,
        interpretation=interpretation,
    )


def build_graph_evidence_registry(
    graph: FunctionalGraphReport,
    *,
    stability_by_session: list[dict],
    temporal_ci95_low: float,
    control_decision: str,
) -> GraphEvidenceRegistry:
    """Annotate graph edges with strength, fragility and evidence state.

    The registry turns a graph into an auditable scientific object. Each edge
    is tagged as exploratory, controlled or replicated-like based on current
    controls and session stability. We avoid the word `replicated` because this
    is still one dataset; `controlled` is the strongest current admissible state.
    """
    if not stability_by_session:
        raise ValueError("stability_by_session must not be empty")
    mean_stability = sum(float(row["stability_score"]) for row in stability_by_session) / len(stability_by_session)
    robust_fraction = sum(1 for row in stability_by_session if row["status"] == "robust") / len(stability_by_session)
    records = []
    warnings = []
    for edge in graph.edges:
        strength = max(0.0, float(edge.weight))
        fragility = 1.0 - mean_stability
        state, rationale = _edge_state(
            strength=strength,
            robust_fraction=robust_fraction,
            temporal_ci95_low=temporal_ci95_low,
            control_decision=control_decision,
        )
        records.append(
            EvidenceEdgeRecord(
                source=edge.source,
                relation=edge.relation,
                target=edge.target,
                weight=float(edge.weight),
                evidence=edge.evidence,
                strength=strength,
                fragility=fragility,
                state=state,
                rationale=rationale,
            )
        )
    if control_decision != "passes_window_controls":
        warnings.append("Graph edges cannot be promoted because the control gate failed")
    summary = {
        "exploratory": sum(1 for record in records if record.state == "exploratory"),
        "controlled": sum(1 for record in records if record.state == "controlled"),
        "fragile": sum(1 for record in records if record.state == "fragile"),
    }
    return GraphEvidenceRegistry(
        target_name=graph.target_name,
        window_name=graph.window_name,
        records=records,
        summary=summary,
        warnings=warnings,
    )


def _edge_state(
    *,
    strength: float,
    robust_fraction: float,
    temporal_ci95_low: float,
    control_decision: str,
) -> tuple[str, str]:
    """Classify one edge using conservative current-project rules."""
    if strength <= 0.0:
        return "fragile", "Non-positive edge weight."
    if control_decision != "passes_window_controls" or temporal_ci95_low <= 0.0:
        return "exploratory", "Controls or temporal CI do not support promotion."
    if robust_fraction >= 0.4:
        return "controlled", "Positive edge with passed controls and enough robust-session support."
    return "exploratory", "Positive edge but limited robust-session support."
