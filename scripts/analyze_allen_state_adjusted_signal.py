"""Test fixed early neural signal after adjustment for direct running and pupil."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path
from statistics import mean, median
from typing import Any

from neurotwin_mvp.artifacts import read_session_artifact
from neurotwin_mvp.behavioral_targets import derive_binary_target, diagnose_target, materialize_target_session
from neurotwin_mvp.benchmark import (
    DictLogisticRegressionClassifier,
    _merge_feature_rows,
    _sequence_feature_rows,
    _temporal_region_feature_rows,
)


ROOT = Path(__file__).resolve().parents[1]


def balanced_accuracy(targets: list[int], predictions: list[int]) -> float:
    """Return balanced accuracy for a binary target."""
    recalls = []
    for label in (0, 1):
        indices = [index for index, target in enumerate(targets) if target == label]
        if not indices:
            raise ValueError("both target classes are required")
        recalls.append(sum(predictions[index] == label for index in indices) / len(indices))
    return mean(recalls)


def state_row(row: dict[str, Any]) -> dict[str, float]:
    """Return early direct-state features with explicit missingness."""
    output = {}
    for name in ("running_speed_0_250", "pupil_area_0_250"):
        value = row.get(name)
        try:
            finite = math.isfinite(float(value))
        except (TypeError, ValueError):
            finite = False
        output[f"state:{name}"] = float(value) if finite else 0.0
        output[f"state:{name}:missing"] = float(not finite)
    return output


def evaluate_rows(rows: list[dict[str, float]], targets: list[int], split: int, name: str) -> float:
    """Fit one chronological model and return held-out balanced accuracy."""
    model = DictLogisticRegressionClassifier(name)
    model.fit(rows[:split], targets[:split])
    predictions = [int(model.predict_probability(row) >= 0.5) for row in rows[split:]]
    return balanced_accuracy(targets[split:], predictions)


def analyze_session(source, sidecar: dict[str, Any], train_fraction: float) -> dict[str, float]:
    """Compare baseline, state-adjusted and state-plus-neural models."""
    target = materialize_target_session(source, "go_response")
    state_by_original = {int(row["trial_id"]): row for row in sidecar["trial_state"]}
    labeled_state = [
        state_by_original[trial.trial_id]
        for trial in source.trials
        if derive_binary_target(trial, "go_response") is not None
    ]
    keep = [
        index
        for index, trial in enumerate(target.trials)
        if trial.choice == 0
        or (
            trial.metadata.get("response_latency_s") is not None
            and float(trial.metadata["response_latency_s"]) >= 0.250
        )
    ]
    trials = [target.trials[index] for index in keep]
    states = [labeled_state[index] for index in keep]
    if len(trials) < 40:
        raise ValueError("insufficient landmark trials")
    targets = [trial.choice for trial in trials]
    split = int(len(trials) * train_fraction)
    if len(set(targets[:split])) < 2 or len(set(targets[split:])) < 2:
        raise ValueError("chronological split lacks both classes")
    baseline = _sequence_feature_rows(
        trials,
        target.region_names,
        task=True,
        compact_image=True,
        history=True,
    )
    state = _merge_feature_rows(baseline, [state_row(row) for row in states])
    neural = _temporal_region_feature_rows(trials, target.region_names, ["stimulus"])
    state_neural = _merge_feature_rows(state, neural)
    baseline_score = evaluate_rows(baseline, targets, split, "state_adjusted_baseline")
    state_score = evaluate_rows(state, targets, split, "state_adjusted_direct_state")
    state_neural_score = evaluate_rows(state_neural, targets, split, "state_adjusted_neural")
    return {
        "n_trials": len(trials),
        "baseline_balanced_accuracy": baseline_score,
        "state_balanced_accuracy": state_score,
        "state_neural_balanced_accuracy": state_neural_score,
        "state_gain": state_score - baseline_score,
        "state_adjusted_neural_gain": state_neural_score - state_score,
    }


def bootstrap_ci(values: list[float], iterations: int = 5000, seed: int = 907) -> tuple[float, float]:
    """Return a deterministic session bootstrap interval."""
    rng = random.Random(seed)
    draws = sorted(mean(rng.choice(values) for _ in values) for _ in range(iterations))
    return draws[int(0.025 * iterations)], draws[int(0.975 * iterations)]


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    """Write state-adjusted neural-signal report."""
    summary = payload["summary"]
    lines = [
        "# Allen direct-state-adjusted fixed neural signal",
        "",
        f"- Sessions analyzed: {summary['n_sessions']}",
        f"- Mean direct-state gain: {summary['mean_state_gain']:.3f}",
        f"- Mean state-adjusted neural gain: {summary['mean_state_adjusted_neural_gain']:.3f}",
        f"- State-adjusted neural gain CI95: [{summary['state_adjusted_neural_gain_ci95'][0]:.3f}, {summary['state_adjusted_neural_gain_ci95'][1]:.3f}]",
        f"- Positive state-adjusted neural fraction: {summary['positive_state_adjusted_neural_fraction']:.3f}",
        f"- Decision: `{payload['decision']}`",
        "",
        "The analysis uses the fixed 0-250 ms neural window and excludes responses before 250 ms. Running and pupil are measured in the same early interval. A positive adjusted gain means neural population rates add held-out information beyond these direct state measurements and the behavioral baseline.",
        "",
        "This remains observational. State adjustment does not identify a causal neural mechanism and cannot control unmeasured state.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-fraction", type=float, default=0.7)
    parser.add_argument("--datasets-root", type=Path, default=ROOT / "artifacts" / "datasets" / "allen")
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_state_adjusted_signal.json")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_state_adjusted_signal.md")
    args = parser.parse_args()

    rows = []
    skipped = []
    for sidecar_path in sorted(args.datasets_root.glob("*/state_anatomy.json")):
        source = read_session_artifact(sidecar_path.parent)
        if not diagnose_target(source, "go_response").usable:
            continue
        try:
            result = analyze_session(
                source,
                json.loads(sidecar_path.read_text(encoding="utf-8")),
                args.train_fraction,
            )
        except ValueError as exc:
            skipped.append({"session_id": source.session_id, "reason": str(exc)})
            continue
        rows.append({"session_id": source.session_id, "animal_id": source.animal_id, **result})
    adjusted = [float(row["state_adjusted_neural_gain"]) for row in rows]
    state_gains = [float(row["state_gain"]) for row in rows]
    ci = bootstrap_ci(adjusted)
    summary = {
        "n_sessions": len(rows),
        "mean_state_gain": mean(state_gains),
        "median_state_gain": median(state_gains),
        "mean_state_adjusted_neural_gain": mean(adjusted),
        "median_state_adjusted_neural_gain": median(adjusted),
        "state_adjusted_neural_gain_ci95": ci,
        "positive_state_adjusted_neural_fraction": sum(value > 0.0 for value in adjusted) / len(adjusted),
    }
    decision = (
        "fixed_neural_signal_survives_direct_state_adjustment"
        if ci[0] > 0.0
        else "fixed_neural_signal_not_confirmed_after_direct_state_adjustment"
    )
    payload = {
        "target_name": "go_response",
        "window": "stimulus_0_250_landmark",
        "train_fraction": args.train_fraction,
        "summary": summary,
        "decision": decision,
        "rows": rows,
        "skipped": skipped,
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown(args.out_md, payload)
    print(f"state_adjusted_signal_json={args.out_json}")
    print(f"decision={decision}")


if __name__ == "__main__":
    main()
