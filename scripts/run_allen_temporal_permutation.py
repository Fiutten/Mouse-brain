"""Run temporal-window permutation tests on normalized Allen sessions.

This is the confirmatory gate before interpreting a temporal window as carrying
aligned neural information. The null keeps task/image/history rows fixed and
shuffles the selected temporal neural-window rows across trials.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean, median
from typing import Any

from neurotwin_mvp.artifacts import read_session_artifact
from neurotwin_mvp.behavioral_targets import TargetName, diagnose_target
from neurotwin_mvp.benchmark import run_temporal_window_permutation_test


ROOT = Path(__file__).resolve().parents[1]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write per-session temporal permutation rows."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: list[dict[str, Any]], alpha: float) -> dict[str, Any]:
    """Aggregate session-level temporal permutation results."""
    gains = [float(row["observed_gain"]) for row in rows]
    p_values = [float(row["p_value"]) for row in rows]
    return {
        "n_sessions": len(rows),
        "mean_observed_gain": mean(gains) if gains else None,
        "median_observed_gain": median(gains) if gains else None,
        "positive_gain_fraction": sum(1 for value in gains if value > 0.0) / len(gains) if gains else None,
        "significant_fraction": sum(1 for value in p_values if value < alpha) / len(p_values) if p_values else None,
        "mean_valid_trial_fraction": mean(float(row["valid_trial_fraction"]) for row in rows) if rows else None,
    }


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    """Write a reviewer-readable temporal permutation summary."""
    path.parent.mkdir(parents=True, exist_ok=True)
    s = payload["summary"]
    lines = [
        f"# Allen temporal permutation: {payload['target_name']} / {payload['window_name']}",
        "",
        "## Summary",
        "",
        f"- Sessions considered: {payload['n_sessions_considered']}",
        f"- Sessions analyzed: {s['n_sessions']}",
        f"- Skipped sessions: {payload['n_sessions_skipped']}",
        f"- Permutations per session: {payload['n_permutations']}",
        f"- Mean observed gain: {_fmt(s['mean_observed_gain'])}",
        f"- Median observed gain: {_fmt(s['median_observed_gain'])}",
        f"- Positive gain fraction: {_fmt(s['positive_gain_fraction'])}",
        f"- Significant fraction: {_fmt(s['significant_fraction'])}",
        f"- Mean valid-trial fraction: {_fmt(s['mean_valid_trial_fraction'])}",
        "",
        "## Per-session Results",
        "",
        "| session | gain | p value | significant | valid fraction | warnings |",
        "| --- | ---: | ---: | --- | ---: | --- |",
    ]
    for row in payload["sessions"]:
        lines.append(
            "| {session_id} | {gain} | {p_value} | {significant} | {valid} | {warnings} |".format(
                session_id=row["session_id"],
                gain=_fmt(row["observed_gain"]),
                p_value=_fmt(row["p_value"]),
                significant=str(row["significant"]).lower(),
                valid=_fmt(row["valid_trial_fraction"]),
                warnings=row["warnings"] or "",
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Significant rows reject a shuffled temporal-window alignment null for that session.",
            "- Non-significant rows do not invalidate the cohort, but they limit any stable-claim language.",
            "- This is still predictive evidence; causal interpretation requires perturbation or stronger controls.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _fmt(value: Any) -> str:
    if value is None:
        return ""
    try:
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return str(value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-name", default="go_response")
    parser.add_argument("--window-name", default="pre_response")
    parser.add_argument("--n-permutations", type=int, default=50)
    parser.add_argument("--seed", type=int, default=31)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--require-usable-target", action="store_true")
    parser.add_argument("--datasets-root", type=Path, default=ROOT / "artifacts" / "datasets" / "allen")
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_permutation.json")
    parser.add_argument("--out-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_permutation.csv")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_permutation.md")
    args = parser.parse_args()

    target_name: TargetName = args.target_name
    rows = []
    skipped = []
    session_dirs = sorted(path.parent for path in args.datasets_root.glob("*/session.json"))
    for session_dir in session_dirs:
        session = read_session_artifact(session_dir)
        diagnostic = diagnose_target(session, target_name)
        if args.require_usable_target and not diagnostic.usable:
            skipped.append({"session_id": session.session_id, "reason": "target_not_usable", "warnings": diagnostic.warnings})
            continue
        try:
            report = run_temporal_window_permutation_test(
                session,
                window_name=args.window_name,
                target_name=target_name,
                n_permutations=args.n_permutations,
                seed=args.seed,
            )
        except ValueError as exc:
            skipped.append({"session_id": session.session_id, "reason": "temporal_window_unavailable", "warnings": [str(exc)]})
            continue
        row = report.to_dict()
        row["significant"] = bool(row["p_value"] < args.alpha)
        row["warnings"] = "; ".join(row["warnings"])
        rows.append(row)

    payload = {
        "target_name": target_name,
        "window_name": args.window_name,
        "alpha": args.alpha,
        "n_permutations": args.n_permutations,
        "seed": args.seed,
        "n_sessions_considered": len(session_dirs),
        "n_sessions_skipped": len(skipped),
        "summary": summarize(rows, args.alpha),
        "sessions": rows,
        "skipped_sessions": skipped,
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_csv(args.out_csv, rows)
    write_markdown(args.out_md, payload)
    print(f"temporal_permutation_json={args.out_json}")
    print(f"temporal_permutation_csv={args.out_csv}")
    print(f"temporal_permutation_md={args.out_md}")
    print(f"n_sessions={payload['summary']['n_sessions']}")
    print(f"mean_observed_gain={_fmt(payload['summary']['mean_observed_gain'])}")
    print(f"significant_fraction={_fmt(payload['summary']['significant_fraction'])}")


if __name__ == "__main__":
    main()
