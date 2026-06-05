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
