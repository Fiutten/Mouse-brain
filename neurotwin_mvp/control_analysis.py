"""Control analyses for temporal neural evidence.

These routines formalize a conservative rule: a candidate temporal signal is
interesting only if it is stronger than plausible negative/control windows and
does not disappear under simple behavioral stratifications. The functions work
with already-produced reports so they can be rerun without touching NWB files.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class WindowControlResult:
    """Comparison between a candidate window and one control window."""

    candidate_window: str
    control_window: str
    candidate_mean_gain: float
    control_mean_gain: float
    margin: float
    passes: bool

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(frozen=True)
class ControlGateReport:
    """Summary of temporal control checks for one target/window hypothesis."""

    target_name: str
    candidate_window: str
    n_sessions: int
    minimum_margin: float
    window_controls: list[WindowControlResult]
    decision: str
    warnings: list[str]

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation."""
        return asdict(self)


def evaluate_window_controls(
    window_summary: dict[str, dict],
    *,
    target_name: str,
    candidate_window: str = "pre_response",
    control_windows: list[str] | None = None,
    minimum_margin: float = 0.02,
) -> ControlGateReport:
    """Evaluate whether a candidate window beats specified control windows.

    `minimum_margin` is intentionally modest. It avoids declaring victory when
    two windows differ only by rounding noise, while keeping the gate usable for
    early session cohorts.
    """
    control_windows = control_windows or ["baseline", "stimulus"]
    if candidate_window not in window_summary:
        raise ValueError(f"Candidate window `{candidate_window}` is absent from summary")
    candidate = window_summary[candidate_window]
    candidate_gain = float(candidate["mean_gain"])
    candidate_sessions = int(candidate["n_sessions"])
    results = []
    warnings = []
    for control_window in control_windows:
        if control_window not in window_summary:
            warnings.append(f"Control window `{control_window}` is absent from summary")
            continue
        control_gain = float(window_summary[control_window]["mean_gain"])
        margin = candidate_gain - control_gain
        results.append(
            WindowControlResult(
                candidate_window=candidate_window,
                control_window=control_window,
                candidate_mean_gain=candidate_gain,
                control_mean_gain=control_gain,
                margin=margin,
                passes=margin >= minimum_margin,
            )
        )
    if not results:
        decision = "blocked_no_controls"
    elif all(result.passes for result in results):
        decision = "passes_window_controls"
    else:
        decision = "fails_window_controls"
        warnings.append("Candidate window does not exceed every control window by the required margin")
    return ControlGateReport(
        target_name=target_name,
        candidate_window=candidate_window,
        n_sessions=candidate_sessions,
        minimum_margin=minimum_margin,
        window_controls=results,
        decision=decision,
        warnings=warnings,
    )


def summarize_latency_strata(rows: list[dict]) -> dict[str, dict]:
    """Aggregate fast/slow latency-control rows by stratum.

    Rows are produced by the Allen response-control script. Keeping the reducer
    here makes the scientific rule testable without requiring real Allen files
    inside unit tests.
    """
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(str(row["latency_stratum"]), []).append(row)
    summary = {}
    for stratum, items in sorted(grouped.items()):
        gains = [float(item["observed_gain"]) for item in items]
        p_values = [float(item["p_value"]) for item in items]
        summary[stratum] = {
            "n_sessions": len(items),
            "mean_gain": sum(gains) / len(gains) if gains else None,
            "positive_gain_fraction": sum(1 for value in gains if value > 0.0) / len(gains) if gains else None,
            "significant_fraction": sum(1 for value in p_values if value < 0.05) / len(p_values) if p_values else None,
        }
    return summary
