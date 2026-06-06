"""Explain fragile Allen sessions in the current temporal-evidence layer.

The stability matrix intentionally reduces several controls into one score, but
reviewers and future us need the inverse view: *why* did a session become
fragile or mixed? This script joins stability rows with target/session metadata
and writes an auditable failure-mode table.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


CHECK_LABELS = {
    "temporal_gain_positive": "pre_response gain is positive",
    "temporal_significant": "temporal permutation is significant",
    "visual_drop_positive": "visual-cortex ablation drop is positive",
    "fast_gain_positive": "fast-latency gain is positive",
    "slow_gain_positive": "slow-latency gain is positive",
}

FAILED_CHECK_LABELS = {
    "temporal_gain_positive": "pre_response gain is not positive",
    "temporal_significant": "temporal permutation is not significant",
    "visual_drop_positive": "visual-cortex ablation drop is not positive",
    "fast_gain_positive": "fast-latency gain is not positive",
    "slow_gain_positive": "slow-latency gain is not positive",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read a CSV artifact into dictionaries."""
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write the joined fragility rows."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def metadata_by_session(relation_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    """Index session-relation metadata by session id."""
    return {str(row["session_id"]): row for row in relation_rows}


def explain_row(row: dict[str, str], metadata: dict[str, str] | None) -> dict[str, Any]:
    """Return one reviewer-readable fragility explanation row."""
    checks = {
        "temporal_gain_positive": _float(row["temporal_gain"]) > 0.0,
        "temporal_significant": _bool(row["temporal_significant"]),
        "visual_drop_positive": _float(row["visual_cortex_drop"]) > 0.0,
        "fast_gain_positive": _float(row["fast_latency_gain"]) > 0.0,
        "slow_gain_positive": _float(row["slow_latency_gain"]) > 0.0,
    }
    failed = [key for key, passed in checks.items() if not passed]
    passed = [key for key, passed in checks.items() if passed]
    failure_mode = classify_failure_mode(failed)
    meta = metadata or {}
    return {
        "session_id": row["session_id"],
        "status": row["status"],
        "stability_score": _float(row["stability_score"]),
        "failure_mode": failure_mode,
        "failed_checks": "; ".join(FAILED_CHECK_LABELS[key] for key in failed),
        "passed_checks": "; ".join(CHECK_LABELS[key] for key in passed),
        "temporal_gain": _float(row["temporal_gain"]),
        "temporal_p_value": _float(row["temporal_p_value"]),
        "visual_cortex_drop": _float(row["visual_cortex_drop"]),
        "fast_latency_gain": _float(row["fast_latency_gain"]),
        "slow_latency_gain": _float(row["slow_latency_gain"]),
        "go_labeled_trials": _int(meta.get("go_labeled_trials")),
        "go_positive_rate": _float(meta.get("go_positive_rate")),
        "go_minority_fraction": _float(meta.get("go_minority_fraction")),
        "mean_latency_ms": _float(meta.get("mean_latency_ms")),
        "median_latency_ms": _float(meta.get("median_latency_ms")),
        "zero_latency_fraction": _float(meta.get("zero_latency_fraction")),
        "region_count": _int(meta.get("region_count")),
        "covered_regions": meta.get("regions", ""),
        "experience_level": meta.get("experience_level", ""),
        "image_set": meta.get("image_set", ""),
        "session_type": meta.get("session_type", ""),
    }


def classify_failure_mode(failed_checks: list[str]) -> str:
    """Assign a compact failure mode from failed stability checks."""
    failed = set(failed_checks)
    if {"temporal_gain_positive", "temporal_significant"}.issubset(failed):
        if {"fast_gain_positive", "slow_gain_positive"}.issubset(failed):
            return "global_temporal_null"
        return "weak_or_non_significant_temporal_effect"
    if "visual_drop_positive" in failed and ("fast_gain_positive" in failed or "slow_gain_positive" in failed):
        return "regional_and_latency_fragility"
    if "visual_drop_positive" in failed:
        return "regional_fragility"
    if {"fast_gain_positive", "slow_gain_positive"}.intersection(failed):
        return "latency_fragility"
    return "mixed_minor_fragility"


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize fragility and mixed-session failure modes."""
    status_counts = Counter(str(row["status"]) for row in rows)
    mode_counts = Counter(str(row["failure_mode"]) for row in rows)
    fragile = [row for row in rows if row["status"] == "fragile"]
    fragile_mode_counts = Counter(str(row["failure_mode"]) for row in fragile)
    return {
        "n_sessions": len(rows),
        "status_counts": dict(sorted(status_counts.items())),
        "failure_mode_counts": dict(sorted(mode_counts.items())),
        "fragile_failure_mode_counts": dict(sorted(fragile_mode_counts.items())),
        "fragile_session_ids": [row["session_id"] for row in fragile],
        "n_fragile": len(fragile),
    }


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    """Write a compact report focused on scientific interpretation."""
    path.parent.mkdir(parents=True, exist_ok=True)
    summary = payload["summary"]
    lines = [
        "# Allen fragile-session analysis",
        "",
        "## Summary",
        "",
        f"- Sessions analyzed: {summary['n_sessions']}",
        f"- Fragile sessions: {summary['n_fragile']}",
        f"- Fragile session ids: {', '.join(summary['fragile_session_ids'])}",
        "",
        "## Failure Modes",
        "",
        "| failure mode | count |",
        "| --- | ---: |",
    ]
    for mode, count in summary["failure_mode_counts"].items():
        lines.append(f"| `{mode}` | {count} |")
    lines.extend(
        [
            "",
            "## Fragile Failure Modes",
            "",
            "| failure mode | fragile count |",
            "| --- | ---: |",
        ]
    )
    for mode, count in summary["fragile_failure_mode_counts"].items():
        lines.append(f"| `{mode}` | {count} |")
    lines.extend(
        [
            "",
            "## Fragile Sessions",
            "",
            "| session | score | mode | temporal gain | p value | visual drop | fast gain | slow gain | notes |",
            "| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in payload["rows"]:
        if row["status"] != "fragile":
            continue
        notes = row["failed_checks"]
        lines.append(
            "| {session} | {score:.3f} | `{mode}` | {gain:.3f} | {p:.3f} | {drop:.3f} | {fast:.3f} | {slow:.3f} | {notes} |".format(
                session=row["session_id"],
                score=row["stability_score"],
                mode=row["failure_mode"],
                gain=row["temporal_gain"],
                p=row["temporal_p_value"],
                drop=row["visual_cortex_drop"],
                fast=row["fast_latency_gain"],
                slow=row["slow_latency_gain"],
                notes=notes,
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Fragile sessions are not excluded by default; they define the failure cases the mechanism must explain.",
            "- `global_temporal_null` means the candidate window fails at the main temporal level and in latency strata.",
            "- `regional_and_latency_fragility` means the temporal signal may exist, but the current regional/motor interpretation is unstable.",
            "- This report supports stratification and redesign; it is not a post-hoc filter for inflating positive claims.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _float(value: Any) -> float:
    if value in (None, ""):
        return 0.0
    return float(value)


def _int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    return int(float(value))


def _bool(value: Any) -> bool:
    return str(value).lower() == "true"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stability-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_stability_matrix.csv")
    parser.add_argument("--session-relations-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_session_relations.csv")
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_fragile_sessions.json")
    parser.add_argument("--out-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_fragile_sessions.csv")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_fragile_sessions.md")
    args = parser.parse_args()

    relation_index = metadata_by_session(read_csv(args.session_relations_csv))
    rows = [
        explain_row(row, relation_index.get(str(row["session_id"])))
        for row in read_csv(args.stability_csv)
    ]
    payload = {
        "summary": summarize(rows),
        "rows": rows,
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_csv(args.out_csv, rows)
    write_markdown(args.out_md, payload)
    print(f"fragility_json={args.out_json}")
    print(f"fragility_csv={args.out_csv}")
    print(f"fragility_md={args.out_md}")
    print(f"fragile_sessions={payload['summary']['n_fragile']}")


if __name__ == "__main__":
    main()
