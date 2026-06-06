"""Analyze temporal evidence across chronological and engagement session states."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import replace
from pathlib import Path
from statistics import mean, median
from typing import Any

from neurotwin_mvp.artifacts import read_session_artifact
from neurotwin_mvp.behavioral_targets import diagnose_target, materialize_target_session
from neurotwin_mvp.benchmark import run_temporal_window_permutation_test
from neurotwin_mvp.data import Session, Trial


ROOT = Path(__file__).resolve().parents[1]


def chronological_states(trials: list[Trial]) -> dict[str, list[Trial]]:
    """Split trials into stable chronological thirds."""
    n = len(trials)
    first = n // 3
    second = 2 * n // 3
    return {"early": trials[:first], "middle": trials[first:second], "late": trials[second:]}


def engagement_states(trials: list[Trial]) -> dict[str, list[Trial]]:
    """Split trials at the within-session median engagement."""
    cutoff = median(trial.engagement for trial in trials)
    return {
        "low_engagement": [trial for trial in trials if trial.engagement <= cutoff],
        "high_engagement": [trial for trial in trials if trial.engagement > cutoff],
    }


def session_view(session: Session, trials: list[Trial], suffix: str) -> Session:
    """Create one deterministic state-specific session view."""
    retagged = [replace(trial, trial_id=index) for index, trial in enumerate(trials)]
    return replace(session, session_id=f"{session.session_id}_{suffix}", trials=retagged)


def summarize(rows: list[dict[str, Any]], alpha: float) -> dict[str, Any]:
    """Aggregate state-specific temporal evidence."""
    summary = {}
    for state in sorted({str(row["state"]) for row in rows}):
        items = [row for row in rows if row["state"] == state]
        gains = [float(row["observed_gain"]) for row in items]
        summary[state] = {
            "n_sessions": len(items),
            "mean_gain": mean(gains),
            "positive_fraction": sum(value > 0.0 for value in gains) / len(gains),
            "significant_fraction": sum(float(row["p_value"]) < alpha for row in items) / len(items),
        }
    return summary


def state_dependence_by_session(rows: list[dict[str, Any]], alpha: float) -> dict[str, str]:
    """Classify whether session evidence changes across tested states."""
    output = {}
    session_ids = sorted({str(row["session_id"]) for row in rows})
    for session_id in session_ids:
        items = [row for row in rows if row["session_id"] == session_id]
        supported = [
            row["state"]
            for row in items
            if float(row["observed_gain"]) > 0.0 and float(row["p_value"]) < alpha
        ]
        if len(supported) == 0:
            output[session_id] = "no_supported_state"
        elif len(supported) == len(items):
            output[session_id] = "state_invariant_supported"
        else:
            output[session_id] = "state_dependent_supported"
    return output


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    """Write a state/nonstationarity discussion report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    for label in payload["session_classification"].values():
        counts[label] = counts.get(label, 0) + 1
    lines = [
        "# Allen within-session state and nonstationarity analysis",
        "",
        "## Session Classification",
        "",
    ]
    lines.extend(f"- `{label}`: {count}" for label, count in sorted(counts.items()))
    lines.extend(
        [
            "",
            "## State Summary",
            "",
            "| state | sessions | mean gain | positive fraction | significant fraction |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for state, stats in payload["state_summary"].items():
        lines.append(
            f"| {state} | {stats['n_sessions']} | {stats['mean_gain']:.3f} | "
            f"{stats['positive_fraction']:.3f} | {stats['significant_fraction']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- State-dependent support indicates within-session nonstationarity rather than a fixed session trait.",
            "- Engagement splits are descriptive because engagement is a normalized proxy, not a direct arousal measurement.",
            "- Chronological changes may reflect learning, fatigue, drift or recording nonstationarity.",
            "- Results remain observational and require animal-aware confirmation.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-name", default="go_response")
    parser.add_argument("--window-name", default="pre_response")
    parser.add_argument("--n-permutations", type=int, default=20)
    parser.add_argument("--seed", type=int, default=97)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--min-state-trials", type=int, default=40)
    parser.add_argument("--datasets-root", type=Path, default=ROOT / "artifacts" / "datasets" / "allen")
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_within_session_states.json")
    parser.add_argument("--out-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_within_session_states.csv")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_within_session_states.md")
    args = parser.parse_args()

    rows = []
    skipped = []
    for session_dir in sorted(path.parent for path in args.datasets_root.glob("*/session.json")):
        session = read_session_artifact(session_dir)
        diagnostic = diagnose_target(session, args.target_name)
        if not diagnostic.usable:
            continue
        target_session = materialize_target_session(session, args.target_name)
        states = {**chronological_states(target_session.trials), **engagement_states(target_session.trials)}
        for index, (state, trials) in enumerate(states.items()):
            if len(trials) < args.min_state_trials:
                skipped.append({"session_id": session.session_id, "state": state, "reason": "insufficient_trials"})
                continue
            try:
                report = run_temporal_window_permutation_test(
                    session_view(target_session, trials, state),
                    target_name="choice",
                    window_name=args.window_name,
                    n_permutations=args.n_permutations,
                    seed=args.seed + index,
                )
            except ValueError as exc:
                skipped.append({"session_id": session.session_id, "state": state, "reason": str(exc)})
                continue
            row = report.to_dict()
            row["session_id"] = session.session_id
            row["state"] = state
            row["n_trials"] = len(trials)
            row["significant"] = bool(row["p_value"] < args.alpha)
            row["warnings"] = "; ".join(row["warnings"])
            rows.append(row)

    payload = {
        "target_name": args.target_name,
        "window_name": args.window_name,
        "n_permutations": args.n_permutations,
        "alpha": args.alpha,
        "state_summary": summarize(rows, args.alpha),
        "session_classification": state_dependence_by_session(rows, args.alpha),
        "rows": rows,
        "skipped": skipped,
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_csv(args.out_csv, rows)
    write_markdown(args.out_md, payload)
    print(f"within_session_states_json={args.out_json}")
    print(f"within_session_states_md={args.out_md}")
    print(f"sessions={len(payload['session_classification'])}")


if __name__ == "__main__":
    main()
