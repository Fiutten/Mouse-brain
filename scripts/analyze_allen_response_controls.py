"""Run reviewer-facing response-control summaries for Allen temporal evidence.

The script has two control layers:

1. compare the candidate `pre_response` window against negative/control
   windows already produced by the temporal benchmark;
2. optionally rerun a lightweight permutation check in fast/slow latency
   strata, using normalized artifacts only.

These controls do not prove mechanism. They decide whether the current temporal
hypothesis is strong enough to justify more expensive modeling.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import replace
from pathlib import Path
from statistics import median
from typing import Any

from neurotwin_mvp.artifacts import read_session_artifact
from neurotwin_mvp.behavioral_targets import TargetName, diagnose_target, materialize_target_session
from neurotwin_mvp.benchmark import run_temporal_window_permutation_test
from neurotwin_mvp.control_analysis import evaluate_window_controls, summarize_latency_strata
from neurotwin_mvp.data import Session, Trial


ROOT = Path(__file__).resolve().parents[1]


def read_temporal_summary(path: Path) -> dict[str, Any]:
    """Load the temporal-window benchmark JSON."""
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write latency-stratified rows."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    """Write a compact control report for audit and reviewer use."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Allen response controls: {payload['target_name']} / {payload['candidate_window']}",
        "",
        "## Window Controls",
        "",
        f"- Decision: `{payload['window_control']['decision']}`",
        f"- Minimum required margin: {_fmt(payload['window_control']['minimum_margin'])}",
        "",
        "| candidate | control | candidate gain | control gain | margin | passes |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in payload["window_control"]["window_controls"]:
        lines.append(
            "| {candidate_window} | {control_window} | {candidate_mean_gain} | {control_mean_gain} | {margin} | {passes} |".format(
                candidate_window=row["candidate_window"],
                control_window=row["control_window"],
                candidate_mean_gain=_fmt(row["candidate_mean_gain"]),
                control_mean_gain=_fmt(row["control_mean_gain"]),
                margin=_fmt(row["margin"]),
                passes=str(row["passes"]).lower(),
            )
        )
    lines.extend(
        [
            "",
            "## Latency Strata",
            "",
            f"- Permutations per stratum/session: {payload['latency_permutations']}",
            f"- Stratum rows analyzed: {len(payload['latency_rows'])}",
            "",
            "| stratum | sessions | mean gain | positive fraction | significant fraction |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for stratum, stats in payload["latency_summary"].items():
        lines.append(
            "| {stratum} | {n} | {mean_gain} | {positive_fraction} | {significant_fraction} |".format(
                stratum=stratum,
                n=stats["n_sessions"],
                mean_gain=_fmt(stats["mean_gain"]),
                positive_fraction=_fmt(stats["positive_gain_fraction"]),
                significant_fraction=_fmt(stats["significant_fraction"]),
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Passing window controls means the candidate exceeds specified negative windows by the configured margin.",
            "- Latency strata are a fragility screen: failure in one stratum limits mechanistic language.",
            "- These controls remain predictive and observational; they are not perturbation evidence.",
        ]
    )
    if payload["warnings"]:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in payload["warnings"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def latency_stratum_rows(
    *,
    datasets_root: Path,
    target_name: TargetName,
    window_name: str,
    n_permutations: int,
    seed: int,
    require_usable_target: bool,
    min_stratum_trials: int,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Run lightweight temporal checks in fast/slow response-latency strata."""
    rows = []
    warnings = []
    session_dirs = sorted(path.parent for path in datasets_root.glob("*/session.json"))
    for session_dir in session_dirs:
        session = read_session_artifact(session_dir)
        diagnostic = diagnose_target(session, target_name)
        if require_usable_target and not diagnostic.usable:
            continue
        target_session = materialize_target_session(session, target_name)
        latencies = [trial.latency_ms for trial in target_session.trials]
        cutoff = median(latencies)
        for stratum, keep_fast in [("fast", True), ("slow", False)]:
            selected = [
                trial
                for trial in target_session.trials
                if (trial.latency_ms <= cutoff) == keep_fast
            ]
            if len(selected) < min_stratum_trials:
                warnings.append(f"{session.session_id}/{stratum}: fewer than {min_stratum_trials} trials")
                continue
            stratum_session = _session_with_trials(target_session, selected, suffix=f"_{stratum}")
            try:
                report = run_temporal_window_permutation_test(
                    stratum_session,
                    window_name=window_name,
                    target_name="choice",
                    n_permutations=n_permutations,
                    seed=seed,
                )
            except ValueError as exc:
                warnings.append(f"{session.session_id}/{stratum}: {exc}")
                continue
            rows.append(
                {
                    "session_id": session.session_id,
                    "latency_stratum": stratum,
                    "n_trials": len(selected),
                    "latency_cutoff_ms": cutoff,
                    "observed_gain": report.observed_gain,
                    "p_value": report.p_value,
                    "valid_trial_fraction": report.valid_trial_fraction,
                    "warnings": "; ".join(report.warnings),
                }
            )
    return rows, warnings


def _session_with_trials(session: Session, trials: list[Trial], suffix: str) -> Session:
    """Return a session view with stable trial ids inside the selected stratum."""
    retagged = [replace(trial, trial_id=index) for index, trial in enumerate(trials)]
    return replace(session, session_id=f"{session.session_id}{suffix}", trials=retagged)


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
    parser.add_argument("--candidate-window", default="pre_response")
    parser.add_argument("--control-windows", nargs="+", default=["baseline", "stimulus"])
    parser.add_argument("--minimum-margin", type=float, default=0.02)
    parser.add_argument("--latency-permutations", type=int, default=20)
    parser.add_argument("--seed", type=int, default=53)
    parser.add_argument("--min-stratum-trials", type=int, default=40)
    parser.add_argument("--require-usable-target", action="store_true")
    parser.add_argument("--datasets-root", type=Path, default=ROOT / "artifacts" / "datasets" / "allen")
    parser.add_argument("--temporal-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_temporal_windows.json")
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_controls.json")
    parser.add_argument("--out-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_latency_strata.csv")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_controls.md")
    args = parser.parse_args()

    temporal = read_temporal_summary(args.temporal_json)
    window_control = evaluate_window_controls(
        temporal["window_summary"],
        target_name=args.target_name,
        candidate_window=args.candidate_window,
        control_windows=args.control_windows,
        minimum_margin=args.minimum_margin,
    )
    latency_rows, latency_warnings = latency_stratum_rows(
        datasets_root=args.datasets_root,
        target_name=args.target_name,
        window_name=args.candidate_window,
        n_permutations=args.latency_permutations,
        seed=args.seed,
        require_usable_target=args.require_usable_target,
        min_stratum_trials=args.min_stratum_trials,
    )
    payload = {
        "target_name": args.target_name,
        "candidate_window": args.candidate_window,
        "control_windows": args.control_windows,
        "window_control": window_control.to_dict(),
        "latency_permutations": args.latency_permutations,
        "latency_rows": latency_rows,
        "latency_summary": summarize_latency_strata(latency_rows),
        "warnings": window_control.warnings + latency_warnings,
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_csv(args.out_csv, latency_rows)
    write_markdown(args.out_md, payload)
    print(f"controls_json={args.out_json}")
    print(f"controls_csv={args.out_csv}")
    print(f"controls_md={args.out_md}")
    print(f"window_control_decision={window_control.decision}")
    print(f"latency_rows={len(latency_rows)}")


if __name__ == "__main__":
    main()
