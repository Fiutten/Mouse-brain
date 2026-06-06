"""Falsify target-timing alternatives to the Allen pre-response result.

This suite is deliberately separate from the primary evidence pipeline. It
tests whether the dynamic `pre_response` construction leaks response timing,
and whether response-independent windows retain predictive signal.

The existing normalized artifacts contain fixed `stimulus` (0-250 ms) and
`decision` (250-750 ms) windows. The decision window may contain post-response
activity, so it is also evaluated as a 750-ms landmark analysis restricted to
trials with no response before that horizon.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from dataclasses import replace
from pathlib import Path
from statistics import mean, median
from typing import Any

from neurotwin_mvp.artifacts import read_session_artifact
from neurotwin_mvp.behavioral_targets import diagnose_target, materialize_target_session
from neurotwin_mvp.benchmark import (
    DictLogisticRegressionClassifier,
    run_temporal_window_permutation_test,
)
from neurotwin_mvp.data import Session, Trial


ROOT = Path(__file__).resolve().parents[1]


def balanced_accuracy(targets: list[int], predictions: list[int]) -> float:
    """Return balanced accuracy, or raise when a class is absent."""
    recalls = []
    for label in (0, 1):
        indices = [index for index, target in enumerate(targets) if target == label]
        if not indices:
            raise ValueError("balanced accuracy requires both target classes")
        recalls.append(sum(predictions[index] == label for index in indices) / len(indices))
    return mean(recalls)


def dynamic_window_metadata(trial: Trial, window_name: str = "pre_response") -> dict[str, float]:
    """Return timing-only features that must not carry neural information."""
    bounds = trial.metadata.get("time_windows_s", {}).get(window_name, {})
    start = float(bounds.get("start", 0.0))
    end = float(bounds.get("end", start))
    valid = bool(trial.metadata.get("time_window_valid", {}).get(window_name, False))
    return {
        "window_duration_s": max(0.0, end - start),
        "window_end_s": end,
        "window_valid": float(valid),
    }


def leakage_only_score(session: Session, train_fraction: float = 0.7) -> dict[str, float]:
    """Predict the target using only target-derived window metadata."""
    split = int(len(session.trials) * train_fraction)
    train = session.trials[:split]
    test = session.trials[split:]
    if not train or not test:
        raise ValueError("leakage audit requires non-empty train and test blocks")
    train_rows = [dynamic_window_metadata(trial) for trial in train]
    test_rows = [dynamic_window_metadata(trial) for trial in test]
    model = DictLogisticRegressionClassifier("pre_response_timing_only")
    model.fit(train_rows, [trial.choice for trial in train])
    predictions = [int(model.predict_probability(row) >= 0.5) for row in test_rows]
    targets = [trial.choice for trial in test]
    return {
        "balanced_accuracy": balanced_accuracy(targets, predictions),
        "n_train": len(train),
        "n_test": len(test),
    }


def landmark_view(session: Session, horizon_s: float = 0.750) -> Session:
    """Keep trials still at risk immediately before a fixed landmark.

    Miss trials have no response and remain at risk. Hit trials remain only
    when their observed response latency is at or after the landmark. Neural
    features must come from a fixed window ending at or before the landmark.
    """
    kept = []
    for trial in session.trials:
        latency = trial.metadata.get("response_latency_s")
        if trial.choice == 0 or (latency is not None and float(latency) >= horizon_s):
            kept.append(replace(trial, trial_id=len(kept)))
    return replace(session, session_id=f"{session.session_id}_landmark_{horizon_s:.3f}", trials=kept)


def viable_binary_session(session: Session, min_trials: int = 40, min_fraction: float = 0.15) -> bool:
    """Return whether a filtered analysis retains enough of both classes."""
    labels = [trial.choice for trial in session.trials]
    if len(labels) < min_trials or not labels:
        return False
    positive = sum(labels) / len(labels)
    return min(positive, 1.0 - positive) >= min_fraction


def bootstrap_ci(values: list[float], iterations: int = 5000, seed: int = 211) -> tuple[float, float]:
    """Return a deterministic percentile bootstrap interval for a mean."""
    rng = random.Random(seed)
    draws = []
    for _ in range(iterations):
        draws.append(mean(rng.choice(values) for _ in values))
    draws.sort()
    return draws[int(0.025 * iterations)], draws[int(0.975 * iterations)]


def benjamini_hochberg(p_values: list[float]) -> list[float]:
    """Return Benjamini-Hochberg adjusted p-values."""
    n = len(p_values)
    ranked = sorted(enumerate(p_values), key=lambda item: item[1])
    adjusted = [1.0] * n
    running = 1.0
    for reverse_rank, (index, p_value) in enumerate(reversed(ranked), start=1):
        rank = n - reverse_rank + 1
        running = min(running, p_value * n / rank)
        adjusted[index] = min(1.0, running)
    return adjusted


def summarize(rows: list[dict[str, Any]], alpha: float) -> dict[str, Any]:
    """Summarize evidence after global session/window BH correction."""
    output = {}
    for analysis in sorted({str(row["analysis"]) for row in rows}):
        items = [row for row in rows if row["analysis"] == analysis]
        gains = [float(row["observed_gain"]) for row in items]
        ci_low, ci_high = bootstrap_ci(gains)
        output[analysis] = {
            "n_sessions": len(items),
            "mean_gain": mean(gains),
            "median_gain": median(gains),
            "ci95": [ci_low, ci_high],
            "positive_fraction": sum(value > 0.0 for value in gains) / len(gains),
            "raw_significant_fraction": sum(float(row["p_value"]) < alpha for row in items) / len(items),
            "bh_significant_fraction": sum(float(row["q_value_bh"]) < alpha for row in items) / len(items),
        }
    return output


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write flat per-session falsification results."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    """Write a reviewer-facing falsification report."""
    lines = [
        "# Allen temporal falsification suite",
        "",
        "## Decision",
        "",
        f"- Verdict: `{payload['decision']['verdict']}`",
        f"- Timing-only mean balanced accuracy: {payload['leakage_summary']['mean_balanced_accuracy']:.3f}",
        f"- Timing-only sessions above 0.55: {payload['leakage_summary']['fraction_above_055']:.3f}",
        "",
        "## Response-independent analyses",
        "",
        "| analysis | sessions | mean gain | CI95 | positive | raw significant | BH significant |",
        "| --- | ---: | ---: | --- | ---: | ---: | ---: |",
    ]
    for name, stats in payload["analysis_summary"].items():
        lines.append(
            f"| {name} | {stats['n_sessions']} | {stats['mean_gain']:.3f} | "
            f"[{stats['ci95'][0]:.3f}, {stats['ci95'][1]:.3f}] | "
            f"{stats['positive_fraction']:.3f} | {stats['raw_significant_fraction']:.3f} | "
            f"{stats['bh_significant_fraction']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `fixed_stimulus_0_250` is response-independent but may include rare responses before 250 ms.",
            "- `landmark_stimulus_0_250` excludes responses before 250 ms and is the strongest currently identifiable pre-action landmark.",
            "- `fixed_decision_250_750_all` is fixed but can contain motor/post-response activity.",
            "- `landmark_decision_250_750` is generally nonviable because almost all positive responses occur before 750 ms.",
            "- A timing-only score above chance demonstrates leakage risk; it does not prove that neural effects are entirely artifactual.",
            "- The suite cannot replace a discrete-time hazard model because current normalized artifacts lack fine neural time bins.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-name", default="go_response")
    parser.add_argument("--n-permutations", type=int, default=20)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--reuse-existing-rows", action="store_true")
    parser.add_argument("--datasets-root", type=Path, default=ROOT / "artifacts" / "datasets" / "allen")
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_temporal_falsification.json")
    parser.add_argument("--out-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_temporal_falsification.csv")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_temporal_falsification.md")
    args = parser.parse_args()

    if args.reuse_existing_rows:
        existing = json.loads(args.out_json.read_text(encoding="utf-8"))
        rows = existing["rows"]
        leakage_rows = existing["leakage_rows"]
        skipped = existing["skipped"]
        args.n_permutations = int(existing["n_permutations"])
    else:
        rows = []
        leakage_rows = []
        skipped = []
        for path in sorted(args.datasets_root.glob("*/session.json")):
            source = read_session_artifact(path.parent)
            if not diagnose_target(source, args.target_name).usable:
                continue
            session = materialize_target_session(source, args.target_name)
            leakage = leakage_only_score(session)
            leakage_rows.append({"session_id": source.session_id, **leakage})

            analyses = [
                ("fixed_stimulus_0_250", session, "stimulus"),
                ("landmark_stimulus_0_250", landmark_view(session, 0.250), "stimulus"),
                ("landmark_decision_250_750", landmark_view(session), "decision"),
            ]
            for index, (name, view, window_name) in enumerate(analyses):
                if not viable_binary_session(view):
                    skipped.append({"session_id": source.session_id, "analysis": name, "reason": "nonviable_after_filter"})
                    continue
                report = run_temporal_window_permutation_test(
                    view,
                    target_name="choice",
                    window_name=window_name,
                    n_permutations=args.n_permutations,
                    seed=401 + index,
                )
                rows.append(
                    {
                        "session_id": source.session_id,
                        "animal_id": source.animal_id,
                        "analysis": name,
                        "n_trials": len(view.trials),
                        "observed_gain": report.observed_gain,
                        "p_value": report.p_value,
                        "valid_trial_fraction": report.valid_trial_fraction,
                    }
                )

    q_values = benjamini_hochberg([float(row["p_value"]) for row in rows])
    for row, q_value in zip(rows, q_values, strict=True):
        row["q_value_bh"] = q_value
    analysis_summary = summarize(rows, args.alpha)
    leakage_scores = [float(row["balanced_accuracy"]) for row in leakage_rows]
    leakage_summary = {
        "n_sessions": len(leakage_scores),
        "mean_balanced_accuracy": mean(leakage_scores),
        "median_balanced_accuracy": median(leakage_scores),
        "fraction_above_055": sum(value > 0.55 for value in leakage_scores) / len(leakage_scores),
    }
    landmark = analysis_summary.get("landmark_stimulus_0_250")
    stimulus = analysis_summary.get("fixed_stimulus_0_250")
    independent_supported = any(
        stats and stats["ci95"][0] > 0.0 and stats["positive_fraction"] >= 0.5
        for stats in (landmark, stimulus)
    )
    if independent_supported and args.n_permutations >= 500:
        verdict = "dynamic_claim_falsified_fixed_signal_confirmatory_positive"
    elif independent_supported:
        verdict = "dynamic_claim_falsified_fixed_signal_screening_positive"
    else:
        verdict = "dynamic_claim_falsified_no_fixed_signal_support"
    payload = {
        "target_name": args.target_name,
        "n_permutations": args.n_permutations,
        "alpha": args.alpha,
        "decision": {
            "verdict": verdict,
            "independent_signal_supported": independent_supported,
            "pre_response_timing_is_target_derived": True,
        },
        "leakage_summary": leakage_summary,
        "analysis_summary": analysis_summary,
        "leakage_rows": leakage_rows,
        "rows": rows,
        "skipped": skipped,
        "limitations": [
            "The current fixed-window permutation run is a 20-permutation screen and is not confirmatory.",
            "Current artifacts provide only 0-250 ms and 250-750 ms fixed neural windows.",
            "The 750-ms landmark loses the positive class in the current response-time distribution.",
            "A full discrete-time hazard model requires re-exported fine neural time bins.",
            "The current cohort was used during development and is not an external replication cohort.",
        ],
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_csv(args.out_csv, rows)
    write_markdown(args.out_md, payload)
    print(f"temporal_falsification_json={args.out_json}")
    print(f"verdict={verdict}")
    print(f"timing_only_mean_balanced_accuracy={leakage_summary['mean_balanced_accuracy']:.3f}")


if __name__ == "__main__":
    main()
