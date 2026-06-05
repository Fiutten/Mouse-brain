"""Graph-style orchestration for the prototype.

This module is the current equivalent of a small LangGraph workflow, implemented
without external orchestration dependencies. It wires together knowledge,
hypotheses, review, data loading, baselines and lesion experiments.
"""

from __future__ import annotations

from dataclasses import dataclass

from .agents import Hypothesis, HypothesisAgent, ReviewerAgent
from .baselines import BaselineReport, MajorityChoiceBaseline, StimulusRuleBaseline, evaluate_classifier
from .config import load_config
from .data import SessionLoader, SyntheticNeuropixelsLoader, mean_region_rates, train_test_split
from .experiments import LesionResult, lesion_sweep
from .knowledge import KnowledgeGraph, seed_mouse_decision_graph
from .metrics import behavioral_summary
from .regional_model import RegionalModel


@dataclass
class WorkflowReport:
    """Auditable output of one workflow run."""

    hypotheses: list[Hypothesis]
    reviewer_findings: list[str]
    dataset_summary: dict[str, float]
    region_rate_summary: dict[str, float]
    baseline_reports: list[BaselineReport]
    lesion_results: list[LesionResult]
    knowledge_graph: KnowledgeGraph


def run_workflow(
    config_path: str,
    seed: int = 7,
    session_loader: SessionLoader | None = None,
) -> WorkflowReport:
    """Run the complete MVP workflow.

    `session_loader` is injectable so that synthetic sessions, Allen sessions
    and IBL sessions can all pass through the same downstream evaluation path.
    """
    graph = seed_mouse_decision_graph()
    hypotheses = HypothesisAgent().propose(graph)
    reviewer_findings = ReviewerAgent().review(hypotheses)
    session = (session_loader or SyntheticNeuropixelsLoader(seed=seed)).load()
    train, test = train_test_split(session)
    baseline_reports = [
        evaluate_classifier(MajorityChoiceBaseline(), train, test),
        evaluate_classifier(StimulusRuleBaseline(), train, test),
    ]
    model = RegionalModel(load_config(config_path), seed=seed)
    lesion_results = lesion_sweep(model)
    return WorkflowReport(
        hypotheses=hypotheses,
        reviewer_findings=reviewer_findings,
        dataset_summary=behavioral_summary(session.trials),
        region_rate_summary=mean_region_rates(session.trials),
        baseline_reports=baseline_reports,
        lesion_results=lesion_results,
        knowledge_graph=graph,
    )
