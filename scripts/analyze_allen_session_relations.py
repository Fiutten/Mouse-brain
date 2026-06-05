"""Explain why Allen sessions are usable, non-usable or evidentially strong.

The target-export workflow answers "how many usable sessions do we have?" but
publication planning needs a sharper question: why did some downloaded sessions
work and others fail for the chosen behavioral target, and why do only some
usable sessions show neural evidence?

This script joins three already-generated sources:

- `target_diagnostics.json`: target label count and class balance;
- target-specific `evidence_report.json`: per-session neural-gain evidence;
- normalized `session.json` artifacts: animal id, trial metadata and simple
  behavioral summaries.

The output is deliberately descriptive. With 15 sessions we should treat
relationships as hypotheses for selection/redesign, not as confirmatory
statistics.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median
from typing import Any

from neurotwin_mvp.artifacts import read_session_artifact
from neurotwin_mvp.behavioral_targets import derive_binary_target


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict[str, Any]:
    """Read a UTF-8 JSON object from disk."""
    return json.loads(path.read_text(encoding="utf-8"))


def load_metadata_by_session(export_status_path: Path) -> dict[str, dict[str, Any]]:
    """Return Allen export metadata indexed by ecephys session id."""
    if not export_status_path.exists():
        return {}
    payload = load_json(export_status_path)
    rows = payload.get("already_exported", [])
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        session_id = str(row.get("ecephys_session_id", ""))
        if session_id:
            result[session_id] = row
    return result


def load_go_diagnostics(target_diagnostics_path: Path, target_name: str) -> dict[str, dict[str, Any]]:
    """Extract one target diagnostic per session."""
    payload = load_json(target_diagnostics_path)
    result: dict[str, dict[str, Any]] = {}
    for session_entry in payload.get("sessions", []):
        session_id = str(session_entry["session_id"])
        for diagnostic in session_entry.get("diagnostics", []):
            if diagnostic.get("target_name") == target_name:
                result[session_id] = diagnostic
                break
    return result


def load_evidence_by_session(evidence_report_path: Path) -> dict[str, dict[str, Any]]:
    """Return target evidence rows indexed by session id."""
    if not evidence_report_path.exists():
        return {}
    payload = load_json(evidence_report_path)
    return {
        str(item["session_id"]): item
        for item in payload.get("session_evidence", [])
    }


def summarize_session_artifact(session_dir: Path, target_name: str) -> dict[str, Any]:
    """Compute simple behavioral summaries from one normalized session."""
    session = read_session_artifact(session_dir)
    target_labels = [
        label
        for trial in session.trials
        if (label := derive_binary_target(trial, target_name)) is not None
    ]
    latencies = [trial.latency_ms for trial in session.trials]
    go_trials = [trial for trial in session.trials if bool(trial.metadata.get("go", False))]
    catch_trials = [trial for trial in session.trials if bool(trial.metadata.get("catch", False))]
    zero_latency_fraction = (
        sum(1 for latency in latencies if latency == 0.0) / len(latencies)
        if latencies
        else 0.0
    )
    return {
        "animal_id": session.animal_id,
        "n_trials_total": len(session.trials),
        "n_go_trials": len(go_trials),
        "n_catch_trials": len(catch_trials),
        "target_labeled_trials": len(target_labels),
        "target_positive_rate_from_trials": mean(target_labels) if target_labels else None,
        "mean_latency_ms": mean(latencies) if latencies else None,
        "median_latency_ms": median(latencies) if latencies else None,
        "zero_latency_fraction": zero_latency_fraction,
        "region_count": len(session.region_names),
        "regions": ",".join(session.region_names),
    }


def pearson(xs: list[float], ys: list[float]) -> float | None:
    """Compute a small-sample Pearson correlation when possible."""
    if len(xs) < 3 or len(xs) != len(ys):
        return None
    mean_x = mean(xs)
    mean_y = mean(ys)
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if den_x == 0.0 or den_y == 0.0:
        return None
    return num / (den_x * den_y)


def summarize_group(rows: list[dict[str, Any]], group_key: str) -> dict[str, Any]:
    """Summarize numeric columns by a binary/group label."""
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row[group_key])].append(row)

    numeric_columns = [
        "n_total_trials",
        "go_labeled_trials",
        "go_positive_rate",
        "go_minority_fraction",
        "permutation_observed_gain",
        "permutation_p_value",
        "multisplit_mean_gain",
        "zero_latency_fraction",
    ]
    summary: dict[str, Any] = {}
    for name, items in sorted(grouped.items()):
        entry: dict[str, Any] = {"n_sessions": len(items)}
        for column in numeric_columns:
            values = [
                float(item[column])
                for item in items
                if item.get(column) is not None
            ]
            if values:
                entry[f"mean_{column}"] = mean(values)
                entry[f"median_{column}"] = median(values)
        summary[name] = entry
    return summary


def build_rows(args: argparse.Namespace) -> list[dict[str, Any]]:
    """Join diagnostics, evidence, metadata and session-level summaries."""
    diagnostics = load_go_diagnostics(args.target_diagnostics, args.target_name)
    evidence = load_evidence_by_session(args.evidence_report)
    metadata = load_metadata_by_session(args.export_status)
    rows: list[dict[str, Any]] = []

    for session_json in sorted(args.datasets_root.glob("*/session.json")):
        session_dir = session_json.parent
        session_id = session_dir.name
        diagnostic = diagnostics.get(session_id, {})
        evidence_row = evidence.get(session_id, {})
        meta = metadata.get(session_id, {})
        artifact_summary = summarize_session_artifact(session_dir, args.target_name)
        positive_rate = diagnostic.get("positive_rate")
        minority_fraction = (
            min(float(positive_rate), 1.0 - float(positive_rate))
            if positive_rate is not None
            else None
        )
        permutation_p = evidence_row.get("permutation_p_value")
        row = {
            "session_id": session_id,
            "animal_id": artifact_summary["animal_id"],
            "mouse_id": meta.get("mouse_id", artifact_summary["animal_id"]),
            "experience_level": meta.get("experience_level"),
            "image_set": meta.get("image_set"),
            "session_type": meta.get("session_type"),
            "unit_count": meta.get("unit_count"),
            "probe_count": meta.get("probe_count"),
            "covered_model_regions": ",".join(meta.get("covered_model_regions", [])),
            "n_total_trials": diagnostic.get("n_total_trials", artifact_summary["n_trials_total"]),
            "go_labeled_trials": diagnostic.get("n_labeled_trials", artifact_summary["target_labeled_trials"]),
            "go_positive_count": diagnostic.get("positive_count"),
            "go_negative_count": diagnostic.get("negative_count"),
            "go_positive_rate": positive_rate,
            "go_minority_fraction": minority_fraction,
            "go_usable": bool(diagnostic.get("usable", False)),
            "target_warnings": "; ".join(diagnostic.get("warnings", [])),
            "n_go_trials": artifact_summary["n_go_trials"],
            "n_catch_trials": artifact_summary["n_catch_trials"],
            "mean_latency_ms": artifact_summary["mean_latency_ms"],
            "median_latency_ms": artifact_summary["median_latency_ms"],
            "zero_latency_fraction": artifact_summary["zero_latency_fraction"],
            "region_count": artifact_summary["region_count"],
            "regions": artifact_summary["regions"],
            "in_strict_evidence": session_id in evidence,
            "permutation_observed_gain": evidence_row.get("permutation_observed_gain"),
            "permutation_p_value": permutation_p,
            "permutation_significant": (
                bool(permutation_p is not None and float(permutation_p) <= args.alpha)
            ),
            "multisplit_mean_gain": evidence_row.get("multisplit_mean_gain"),
            "quality_flags": "; ".join(evidence_row.get("quality_flags", [])),
        }
        rows.append(row)
    return rows


def build_report(rows: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    """Create machine-readable relationship summaries."""
    usable = [row for row in rows if row["go_usable"]]
    not_usable = [row for row in rows if not row["go_usable"]]
    strict = [row for row in rows if row["in_strict_evidence"]]
    significant = [row for row in strict if row["permutation_significant"]]
    non_significant = [row for row in strict if not row["permutation_significant"]]

    warning_counts = Counter(
        warning
        for row in rows
        for warning in str(row["target_warnings"]).split("; ")
        if warning
    )
    experience_counts = {
        "usable": Counter(str(row.get("experience_level") or "unknown") for row in usable),
        "not_usable": Counter(str(row.get("experience_level") or "unknown") for row in not_usable),
        "significant": Counter(str(row.get("experience_level") or "unknown") for row in significant),
        "non_significant": Counter(str(row.get("experience_level") or "unknown") for row in non_significant),
    }

    correlations: dict[str, float | None] = {}
    for column in [
        "go_labeled_trials",
        "go_positive_rate",
        "go_minority_fraction",
        "zero_latency_fraction",
        "n_catch_trials",
    ]:
        xs: list[float] = []
        ys: list[float] = []
        for row in strict:
            if row.get(column) is None or row.get("permutation_observed_gain") is None:
                continue
            xs.append(float(row[column]))
            ys.append(float(row["permutation_observed_gain"]))
        correlations[f"{column}_vs_permutation_gain"] = pearson(xs, ys)

    return {
        "target_name": args.target_name,
        "alpha": args.alpha,
        "n_sessions": len(rows),
        "n_usable": len(usable),
        "n_not_usable": len(not_usable),
        "n_strict_evidence": len(strict),
        "n_permutation_significant": len(significant),
        "non_usable_warning_counts": dict(warning_counts),
        "experience_counts": {
            key: dict(value)
            for key, value in experience_counts.items()
        },
        "group_summaries": {
            "by_go_usable": summarize_group(rows, "go_usable"),
            "by_permutation_significant": summarize_group(strict, "permutation_significant"),
        },
        "correlations_in_strict_evidence": correlations,
        "interpretation": [
            "Non-usable downloaded sessions are primarily target failures, not model failures.",
            "The dominant target failure mode is go_response class imbalance.",
            "Permutation-significant sessions are a minority of the usable cohort, so evidence remains mixed.",
            "Relationships are descriptive because the cohort is still small.",
        ],
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write per-session rows as CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, Any]], report: dict[str, Any]) -> None:
    """Write a concise human-readable relationship report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Allen go_response session relationship analysis",
        "",
        "## Summary",
        "",
        f"- Sessions analyzed: {report['n_sessions']}",
        f"- Usable `go_response` sessions: {report['n_usable']}",
        f"- Non-usable `go_response` sessions: {report['n_not_usable']}",
        f"- Sessions in strict evidence cohort: {report['n_strict_evidence']}",
        f"- Permutation-significant sessions: {report['n_permutation_significant']}",
        "",
        "## Main explanation",
        "",
        "Downloaded sessions failed for the strict `go_response` cohort mainly because the target labels were not viable, not because the neural benchmark crashed. A session is rejected when it has too few labeled target trials or when the minority class is below the usability threshold.",
        "",
        "## Non-usable warning counts",
        "",
    ]
    for warning, count in sorted(report["non_usable_warning_counts"].items()):
        lines.append(f"- {warning}: {count}")
    lines.extend(
        [
            "",
            "## Per-session table",
            "",
            "| session | usable | go trials | hit rate | minority frac | p gain | p value | significant | warnings |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for row in rows:
        gain = row["permutation_observed_gain"]
        p_value = row["permutation_p_value"]
        lines.append(
            "| {session_id} | {usable} | {trials} | {rate} | {minority} | {gain} | {pvalue} | {sig} | {warnings} |".format(
                session_id=row["session_id"],
                usable=str(row["go_usable"]).lower(),
                trials=row["go_labeled_trials"],
                rate=_fmt(row["go_positive_rate"]),
                minority=_fmt(row["go_minority_fraction"]),
                gain=_fmt(gain),
                pvalue=_fmt(p_value),
                sig=str(row["permutation_significant"]).lower(),
                warnings=row["target_warnings"] or "",
            )
        )
    lines.extend(
        [
            "",
            "## Descriptive correlations inside the strict cohort",
            "",
        ]
    )
    for name, value in report["correlations_in_strict_evidence"].items():
        lines.append(f"- `{name}`: {_fmt(value)}")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The first filter is behavioral viability: enough go-trial labels and acceptable hit/miss balance.",
            "- Sessions with very high hit rate are rejected because they contain too few misses to train/evaluate a balanced target.",
            "- Among usable sessions, neural evidence is still heterogeneous; only a minority is permutation-significant.",
            "- This supports a next step based on stratification and target redesign, not a strong positive claim yet.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value).lower()
    try:
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return str(value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-name", default="go_response")
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--datasets-root", type=Path, default=ROOT / "artifacts" / "datasets" / "allen")
    parser.add_argument("--target-diagnostics", type=Path, default=ROOT / "artifacts" / "reports" / "allen" / "target_diagnostics.json")
    parser.add_argument("--evidence-report", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_usable" / "evidence_report.json")
    parser.add_argument("--export-status", type=Path, default=ROOT / "artifacts" / "reports" / "allen" / "export_batch_status.json")
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_session_relations.json")
    parser.add_argument("--out-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_session_relations.csv")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_session_relations.md")
    args = parser.parse_args()

    rows = build_rows(args)
    report = build_report(rows, args)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(
        json.dumps({"summary": report, "sessions": rows}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_csv(args.out_csv, rows)
    write_markdown(args.out_md, rows, report)
    print(f"relation_report={args.out_json}")
    print(f"relation_table={args.out_csv}")
    print(f"relation_markdown={args.out_md}")
    print(f"n_sessions={report['n_sessions']}")
    print(f"n_usable={report['n_usable']}")
    print(f"n_permutation_significant={report['n_permutation_significant']}")


if __name__ == "__main__":
    main()
