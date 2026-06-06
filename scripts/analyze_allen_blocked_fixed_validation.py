"""Validate response-independent temporal features across chronological splits."""

from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path
from statistics import mean
from typing import Any

from neurotwin_mvp.artifacts import read_session_artifact
from neurotwin_mvp.behavioral_targets import diagnose_target, materialize_target_session
from neurotwin_mvp.benchmark import (
    DictLogisticRegressionClassifier,
    _merge_feature_rows,
    _sequence_feature_rows,
    _temporal_region_feature_rows,
)


ROOT = Path(__file__).resolve().parents[1]


def balanced_accuracy(targets: list[int], predictions: list[int]) -> float:
    """Return balanced accuracy when both classes are present."""
    recalls = []
    for label in (0, 1):
        indices = [index for index, target in enumerate(targets) if target == label]
        if not indices:
            raise ValueError("balanced accuracy requires both target classes")
        recalls.append(sum(predictions[index] == label for index in indices) / len(indices))
    return mean(recalls)


def landmark_view(session, horizon_s: float = 0.750):
    """Restrict a target session to trials still at risk at one horizon."""
    kept = []
    for trial in session.trials:
        latency = trial.metadata.get("response_latency_s")
        if trial.choice == 0 or (latency is not None and float(latency) >= horizon_s):
            kept.append(replace(trial, trial_id=len(kept)))
    return replace(session, session_id=f"{session.session_id}_landmark", trials=kept)


def viable_binary_session(session, min_trials: int = 40, min_fraction: float = 0.15) -> bool:
    """Return whether a filtered view retains enough of both classes."""
    labels = [trial.choice for trial in session.trials]
    if len(labels) < min_trials:
        return False
    positive = sum(labels) / len(labels)
    return min(positive, 1.0 - positive) >= min_fraction


def gain_at_split(session, window_name: str, train_fraction: float) -> float:
    """Return temporal-window gain over the behavioral baseline at one split."""
    split = int(len(session.trials) * train_fraction)
    train = session.trials[:split]
    test = session.trials[split:]
    train_targets = [trial.choice for trial in train]
    test_targets = [trial.choice for trial in test]
    if len(set(train_targets)) < 2 or len(set(test_targets)) < 2:
        raise ValueError("chronological split lacks both target classes")
    baseline = _sequence_feature_rows(
        session.trials,
        session.region_names,
        task=True,
        compact_image=True,
        history=True,
    )
    temporal = _temporal_region_feature_rows(session.trials, session.region_names, [window_name])
    neural = _merge_feature_rows(baseline, temporal)
    baseline_model = DictLogisticRegressionClassifier("blocked_fixed_baseline")
    neural_model = DictLogisticRegressionClassifier("blocked_fixed_neural")
    baseline_model.fit(baseline[:split], train_targets)
    neural_model.fit(neural[:split], train_targets)
    baseline_predictions = [
        int(baseline_model.predict_probability(row) >= 0.5) for row in baseline[split:]
    ]
    neural_predictions = [
        int(neural_model.predict_probability(row) >= 0.5) for row in neural[split:]
    ]
    return balanced_accuracy(test_targets, neural_predictions) - balanced_accuracy(
        test_targets, baseline_predictions
    )


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize gains by analysis and split."""
    output = {}
    for analysis in sorted({str(row["analysis"]) for row in rows}):
        output[analysis] = {}
        for fraction in sorted({float(row["train_fraction"]) for row in rows}):
            items = [
                row
                for row in rows
                if row["analysis"] == analysis and float(row["train_fraction"]) == fraction
            ]
            gains = [float(row["gain"]) for row in items]
            output[analysis][str(fraction)] = {
                "n_sessions": len(items),
                "mean_gain": mean(gains),
                "positive_fraction": sum(value > 0.0 for value in gains) / len(gains),
            }
    return output


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    """Write blocked-validation report."""
    lines = [
        "# Allen blocked fixed-window validation",
        "",
        "| analysis | train fraction | sessions | mean gain | positive fraction |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for analysis, fractions in payload["summary"].items():
        for fraction, stats in fractions.items():
            lines.append(
                f"| {analysis} | {fraction} | {stats['n_sessions']} | "
                f"{stats['mean_gain']:.3f} | {stats['positive_fraction']:.3f} |"
            )
    lines.extend(
        [
            "",
            "These are chronological sensitivity estimates, not independent replications. Splits lacking both target classes are omitted and reported.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-name", default="go_response")
    parser.add_argument("--train-fractions", nargs="+", type=float, default=[0.5, 0.6, 0.7, 0.8])
    parser.add_argument("--datasets-root", type=Path, default=ROOT / "artifacts" / "datasets" / "allen")
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_blocked_fixed_validation.json")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_blocked_fixed_validation.md")
    args = parser.parse_args()

    rows = []
    skipped = []
    for path in sorted(args.datasets_root.glob("*/session.json")):
        source = read_session_artifact(path.parent)
        if not diagnose_target(source, args.target_name).usable:
            continue
        target = materialize_target_session(source, args.target_name)
        analyses = [
            ("fixed_stimulus_0_250", target, "stimulus"),
            ("landmark_stimulus_0_250", landmark_view(target, 0.250), "stimulus"),
            ("landmark_decision_250_750", landmark_view(target), "decision"),
        ]
        for analysis, view, window in analyses:
            if not viable_binary_session(view):
                skipped.append({"session_id": source.session_id, "analysis": analysis, "reason": "nonviable"})
                continue
            for fraction in args.train_fractions:
                try:
                    gain = gain_at_split(view, window, fraction)
                except ValueError as exc:
                    skipped.append(
                        {
                            "session_id": source.session_id,
                            "analysis": analysis,
                            "train_fraction": fraction,
                            "reason": str(exc),
                        }
                    )
                    continue
                rows.append(
                    {
                        "session_id": source.session_id,
                        "animal_id": source.animal_id,
                        "analysis": analysis,
                        "train_fraction": fraction,
                        "gain": gain,
                    }
                )
    payload = {
        "target_name": args.target_name,
        "train_fractions": args.train_fractions,
        "summary": summarize(rows),
        "rows": rows,
        "skipped": skipped,
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown(args.out_md, payload)
    print(f"blocked_fixed_validation_json={args.out_json}")


if __name__ == "__main__":
    main()
