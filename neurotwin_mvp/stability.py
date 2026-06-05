"""Stability matrices for controlled Allen evidence.

The stability matrix is the reviewer-facing table that keeps us honest. It
joins per-session temporal gains, permutation outcomes, regional drops and
latency-stratified controls into one explicit row per session. This makes it
harder to over-interpret a strong aggregate mean when individual sessions are
fragile.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class StabilityRow:
    """One session-level stability row for a target/window hypothesis."""

    session_id: str
    temporal_gain: float | None
    temporal_p_value: float | None
    temporal_significant: bool
    visual_cortex_drop: float | None
    fast_latency_gain: float | None
    fast_latency_significant: bool
    slow_latency_gain: float | None
    slow_latency_significant: bool
    stability_score: float
    status: str

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(frozen=True)
class StabilityMatrixReport:
    """Aggregate stability report across sessions."""

    target_name: str
    window_name: str
    rows: list[StabilityRow]
    summary: dict[str, float | int]
    warnings: list[str]

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation."""
        return {
            "target_name": self.target_name,
            "window_name": self.window_name,
            "rows": [row.to_dict() for row in self.rows],
            "summary": dict(self.summary),
            "warnings": list(self.warnings),
        }


def build_stability_matrix(
    *,
    target_name: str,
    window_name: str,
    temporal_rows: list[dict],
    regional_rows: list[dict],
    latency_rows: list[dict],
    alpha: float = 0.05,
    primary_region: str = "visual_cortex",
) -> StabilityMatrixReport:
    """Join current control/evidence rows into a session stability matrix."""
    temporal_by_session = {str(row["session_id"]): row for row in temporal_rows}
    regional_by_session = {
        str(row["session_id"]): row
        for row in regional_rows
        if str(row.get("region")) == primary_region
    }
    latency_by_session: dict[str, dict[str, dict]] = {}
    for row in latency_rows:
        latency_by_session.setdefault(str(row["session_id"]), {})[str(row["latency_stratum"])] = row

    session_ids = sorted(set(temporal_by_session) | set(regional_by_session) | set(latency_by_session))
    rows = []
    warnings = []
    for session_id in session_ids:
        temporal = temporal_by_session.get(session_id)
        regional = regional_by_session.get(session_id)
        strata = latency_by_session.get(session_id, {})
        fast = strata.get("fast")
        slow = strata.get("slow")
        temporal_gain = _float_or_none(temporal, "observed_gain")
        temporal_p = _float_or_none(temporal, "p_value")
        visual_drop = _float_or_none(regional, "drop_from_full")
        fast_gain = _float_or_none(fast, "observed_gain")
        fast_p = _float_or_none(fast, "p_value")
        slow_gain = _float_or_none(slow, "observed_gain")
        slow_p = _float_or_none(slow, "p_value")
        checks = [
            temporal_gain is not None and temporal_gain > 0.0,
            temporal_p is not None and temporal_p < alpha,
            visual_drop is not None and visual_drop > 0.0,
            fast_gain is not None and fast_gain > 0.0,
            slow_gain is not None and slow_gain > 0.0,
        ]
        score = sum(1 for passed in checks if passed) / len(checks)
        status = _status_from_score(score)
        if fast is None or slow is None:
            warnings.append(f"{session_id}: missing fast/slow latency stratum")
        rows.append(
            StabilityRow(
                session_id=session_id,
                temporal_gain=temporal_gain,
                temporal_p_value=temporal_p,
                temporal_significant=bool(temporal_p is not None and temporal_p < alpha),
                visual_cortex_drop=visual_drop,
                fast_latency_gain=fast_gain,
                fast_latency_significant=bool(fast_p is not None and fast_p < alpha),
                slow_latency_gain=slow_gain,
                slow_latency_significant=bool(slow_p is not None and slow_p < alpha),
                stability_score=score,
                status=status,
            )
        )
    scores = [row.stability_score for row in rows]
    summary = {
        "n_sessions": len(rows),
        "mean_stability_score": sum(scores) / len(scores) if scores else 0.0,
        "robust_sessions": sum(1 for row in rows if row.status == "robust"),
        "mixed_sessions": sum(1 for row in rows if row.status == "mixed"),
        "fragile_sessions": sum(1 for row in rows if row.status == "fragile"),
    }
    return StabilityMatrixReport(
        target_name=target_name,
        window_name=window_name,
        rows=rows,
        summary=summary,
        warnings=warnings,
    )


def _status_from_score(score: float) -> str:
    """Map a stability score to a conservative qualitative status."""
    if score >= 0.8:
        return "robust"
    if score >= 0.4:
        return "mixed"
    return "fragile"


def _float_or_none(row: dict | None, key: str) -> float | None:
    """Read a possibly missing numeric field."""
    if row is None or row.get(key) in (None, ""):
        return None
    return float(row[key])
