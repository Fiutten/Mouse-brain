"""Minimal evidence graph for auditable model decisions.

The knowledge graph records why a region, function or lesion hypothesis exists.
At this MVP stage it is an in-memory structure with seed evidence. Later it
should be replaced or backed by a curated graph extracted from papers and
dataset metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Evidence:
    """One evidence item attached to claims or modeling choices."""

    claim: str
    source: str
    confidence: str


@dataclass
class KnowledgeGraph:
    """Small directed graph with evidence records.

    This intentionally avoids a heavy graph dependency while the project is
    still validating contracts. The API is narrow enough to swap in NetworkX,
    Neo4j or another graph backend later.
    """

    nodes: dict[str, dict[str, str]] = field(default_factory=dict)
    edges: list[dict[str, str]] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)

    def add_node(self, node_id: str, kind: str, label: str) -> None:
        """Add or replace a typed graph node."""
        self.nodes[node_id] = {"kind": kind, "label": label}

    def add_edge(self, source: str, relation: str, target: str, evidence: str = "") -> None:
        """Add a directed relation between existing nodes."""
        if source not in self.nodes:
            raise ValueError(f"Unknown source node: {source}")
        if target not in self.nodes:
            raise ValueError(f"Unknown target node: {target}")
        self.edges.append({"source": source, "relation": relation, "target": target, "evidence": evidence})

    def add_evidence(self, claim: str, source: str, confidence: str = "medium") -> None:
        """Register textual evidence with a coarse confidence label."""
        self.evidence.append(Evidence(claim=claim, source=source, confidence=confidence))

    def neighbors(self, node_id: str, relation: str | None = None) -> list[str]:
        """Return outgoing neighbors, optionally filtered by relation type."""
        out = []
        for edge in self.edges:
            if edge["source"] == node_id and (relation is None or edge["relation"] == relation):
                out.append(edge["target"])
        return out


def seed_mouse_decision_graph() -> KnowledgeGraph:
    """Create the initial hand-seeded graph for mouse visual decision-making."""
    graph = KnowledgeGraph()
    for node_id, kind, label in [
        ("visual_thalamus", "region", "Visual thalamus"),
        ("visual_cortex", "region", "Visual cortex"),
        ("association_cortex", "region", "Association cortex"),
        ("basal_ganglia", "region", "Basal ganglia"),
        ("hippocampus", "region", "Hippocampus"),
        ("arousal", "region", "Arousal system"),
        ("visual_decision", "function", "Visual decision-making"),
        ("engagement", "function", "Behavioral engagement"),
    ]:
        graph.add_node(node_id, kind, label)
    graph.add_edge("visual_thalamus", "projects_to", "visual_cortex", "Allen connectivity prior")
    graph.add_edge("visual_cortex", "supports", "visual_decision", "Visual behavior literature")
    graph.add_edge("basal_ganglia", "supports", "visual_decision", "Action selection literature")
    graph.add_edge("arousal", "supports", "engagement", "Neuropixels engagement analyses")
    graph.add_evidence(
        "Choice, action and engagement variables are distributed across mouse brain regions.",
        "Steinmetz et al., Nature 2019",
        "high",
    )
    graph.add_evidence(
        "Brain-wide Neuropixels datasets support visual decision-making analyses in mouse.",
        "Allen/IBL public datasets",
        "high",
    )
    return graph
