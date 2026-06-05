"""Task-native behavioral target diagnostics.

The first real-data benchmarks used `Trial.choice` because it was the only
target guaranteed by the core session contract. For Allen Visual Behavior
Neuropixels that is too crude: the task already distinguishes go/catch trials,
hits, misses, false alarms and correct rejects.

This module does not replace the benchmark target yet. It audits candidate
targets first, because training on a poorly populated or severely imbalanced
target would create another fragile result. The intended workflow is:

1. derive target labels from trial metadata;
2. check sample count and class balance per session;
3. only promote viable targets into neural-gain benchmarks.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from dataclasses import replace
from typing import Literal

from .data import Session, Trial


TargetName = Literal[
    "choice",
    "go_response",
    "catch_response",
    "rewarded",
    "response_made",
    "task_success",
]


@dataclass(frozen=True)
class TargetDiagnostic:
    """Viability summary for one candidate behavioral target."""

    session_id: str
    target_name: str
    n_total_trials: int
    n_labeled_trials: int
    positive_count: int
    negative_count: int
    positive_rate: float
    usable: bool
    warnings: list[str]

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(frozen=True)
class SessionTargetDiagnostics:
    """All target diagnostics for one session."""

    session_id: str
    dataset: str
    diagnostics: list[TargetDiagnostic]

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation."""
        return asdict(self)


def derive_binary_target(trial: Trial, target_name: TargetName) -> int | None:
    """Return a binary target label for one trial, or `None` if not applicable."""
    if target_name == "choice":
        return int(trial.choice)
    if target_name == "rewarded":
        return int(trial.reward)
    if target_name == "response_made":
        # Allen Visual Behavior separates the animal's action from trial type:
        # hits and false alarms are lick/response trials, while misses and
        # correct rejects are no-response trials. This target is less tied to
        # go-only class imbalance than `go_response`.
        if _metadata_bool(trial, "hit") or _metadata_bool(trial, "false_alarm"):
            return 1
        if _metadata_bool(trial, "miss") or _metadata_bool(trial, "correct_reject"):
            return 0
        return None
    if target_name == "task_success":
        # Correctness uses both go and catch trials: hit/correct-reject are
        # successful outcomes, miss/false-alarm are errors. It is scientifically
        # meaningful as a behavioral-performance target, but it must be reported
        # carefully because reward is partly outcome-derived in this task.
        if _metadata_bool(trial, "hit") or _metadata_bool(trial, "correct_reject"):
            return 1
        if _metadata_bool(trial, "miss") or _metadata_bool(trial, "false_alarm"):
            return 0
        return None
    if target_name == "go_response":
        if not _metadata_bool(trial, "go"):
            return None
        if _metadata_bool(trial, "hit"):
            return 1
        if _metadata_bool(trial, "miss"):
            return 0
        return None
    if target_name == "catch_response":
        if not _metadata_bool(trial, "catch"):
            return None
        if _metadata_bool(trial, "false_alarm"):
            return 1
        if _metadata_bool(trial, "correct_reject"):
            return 0
        return None
    raise ValueError(f"Unsupported target: {target_name}")


def diagnose_target(
    session: Session,
    target_name: TargetName,
    *,
    min_labeled_trials: int = 80,
    min_class_fraction: float = 0.20,
) -> TargetDiagnostic:
    """Assess whether a target has enough labels and class balance."""
    labels = [
        label
        for trial in session.trials
        if (label := derive_binary_target(trial, target_name)) is not None
    ]
    warnings: list[str] = []
    positive = sum(labels)
    negative = len(labels) - positive
    positive_rate = positive / len(labels) if labels else 0.0

    if len(labels) < min_labeled_trials:
        warnings.append(
            f"Fewer than {min_labeled_trials} labeled trials for target `{target_name}`"
        )
    if labels and min(positive_rate, 1.0 - positive_rate) < min_class_fraction:
        warnings.append(
            f"Target `{target_name}` is imbalanced; minority class below {min_class_fraction:.2f}"
        )
    if not labels:
        warnings.append(f"No labels available for target `{target_name}`")

    return TargetDiagnostic(
        session_id=session.session_id,
        target_name=target_name,
        n_total_trials=len(session.trials),
        n_labeled_trials=len(labels),
        positive_count=positive,
        negative_count=negative,
        positive_rate=positive_rate,
        usable=not warnings,
        warnings=warnings,
    )


def diagnose_session_targets(
    session: Session,
    target_names: list[TargetName] | None = None,
) -> SessionTargetDiagnostics:
    """Assess all candidate targets for one session."""
    target_names = target_names or [
        "choice",
        "go_response",
        "catch_response",
        "rewarded",
        "response_made",
        "task_success",
    ]
    return SessionTargetDiagnostics(
        session_id=session.session_id,
        dataset=session.dataset,
        diagnostics=[diagnose_target(session, target) for target in target_names],
    )


def materialize_target_session(session: Session, target_name: TargetName) -> Session:
    """Return a session whose `choice` field stores the requested target.

    The benchmark stack intentionally consumes `Trial.choice` as its binary
    supervised label. Rewriting every model around target callbacks would add a
    lot of surface area. Instead, this adapter creates a transparent filtered
    view: trials without a label are dropped, the derived target is placed in
    `choice`, and the original choice/reward values remain available in
    metadata for audit and history inspection.
    """
    if target_name == "choice":
        return session

    retargeted_trials: list[Trial] = []
    for trial in session.trials:
        label = derive_binary_target(trial, target_name)
        if label is None:
            continue
        metadata = dict(trial.metadata)
        metadata["original_choice"] = trial.choice
        metadata["target_name"] = target_name
        retargeted_trials.append(
            replace(
                trial,
                trial_id=len(retargeted_trials),
                choice=int(label),
                metadata=metadata,
            )
        )
    if not retargeted_trials:
        raise ValueError(f"No labeled trials available for target `{target_name}`")
    return replace(
        session,
        trials=retargeted_trials,
    )


def _metadata_bool(trial: Trial, key: str) -> bool:
    value = trial.metadata.get(key, False)
    if isinstance(value, str):
        return value.lower() == "true"
    return bool(value)
