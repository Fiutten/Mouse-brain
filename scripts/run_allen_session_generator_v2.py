"""Generate calibrated synthetic sessions from current Allen artifacts."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

from neurotwin_mvp.artifacts import read_session_artifact, write_session_artifact
from neurotwin_mvp.behavioral_targets import TargetName, diagnose_target, materialize_target_session
from neurotwin_mvp.generative import SessionGeneratorCalibration, generate_calibrated_session


ROOT = Path(__file__).resolve().parents[1]


def estimate_calibration(
    *,
    datasets_root: Path,
    target_name: TargetName,
    window_names: list[str],
    require_usable_target: bool,
    n_trials: int,
    seed: int,
) -> SessionGeneratorCalibration:
    """Estimate generator-v2 calibration from normalized Allen sessions."""
    labels = []
    latencies = []
    region_window_values: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    region_names: set[str] = set()
    for session_dir in sorted(path.parent for path in datasets_root.glob("*/session.json")):
        session = read_session_artifact(session_dir)
        diagnostic = diagnose_target(session, target_name)
        if require_usable_target and not diagnostic.usable:
            continue
        target_session = materialize_target_session(session, target_name)
        region_names.update(target_session.region_names)
        for trial in target_session.trials:
            labels.append(trial.choice)
            latencies.append(trial.latency_ms)
            temporal = trial.metadata.get("region_rates_by_window", {})
            if not isinstance(temporal, dict):
                continue
            for window in window_names:
                rates = temporal.get(window, {})
                if not isinstance(rates, dict):
                    continue
                for region, value in rates.items():
                    region_window_values[window][str(region)].append(float(value))
    if not labels:
        raise ValueError("No labeled trials available for generator calibration")
    means = {
        window: {
            region: mean(values)
            for region, values in sorted(region_values.items())
            if values
        }
        for window, region_values in sorted(region_window_values.items())
    }
    return SessionGeneratorCalibration(
        target_name=target_name,
        window_names=window_names,
        region_names=sorted(region_names),
        n_trials=n_trials,
        positive_rate=sum(labels) / len(labels),
        latency_mean_ms=mean(latencies),
        latency_std_ms=pstdev(latencies) if len(latencies) > 1 else 1.0,
        region_window_means=means,
        seed=seed,
    )


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    calibration = payload["calibration"]
    lines = [
        f"# Allen calibrated session generator v2: {calibration['target_name']}",
        "",
        "## Calibration",
        "",
        f"- Generated trials: {calibration['n_trials']}",
        f"- Positive rate: {calibration['positive_rate']:.3f}",
        f"- Latency mean ms: {calibration['latency_mean_ms']:.3f}",
        f"- Latency std ms: {calibration['latency_std_ms']:.3f}",
        f"- Regions: {len(calibration['region_names'])}",
        f"- Windows: {', '.join(calibration['window_names'])}",
        "",
        "## Interpretation",
        "",
        "- Generated sessions are normalized artifacts for stress-testing pipelines.",
        "- They are calibrated from empirical summaries but are not biological evidence.",
    ]
    if payload["warnings"]:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in payload["warnings"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-name", default="go_response")
    parser.add_argument("--window-names", nargs="+", default=["baseline", "stimulus", "pre_response"])
    parser.add_argument("--n-trials", type=int, default=500)
    parser.add_argument("--seed", type=int, default=89)
    parser.add_argument("--require-usable-target", action="store_true")
    parser.add_argument("--datasets-root", type=Path, default=ROOT / "artifacts" / "datasets" / "allen")
    parser.add_argument("--out-session-dir", type=Path, default=ROOT / "artifacts" / "datasets" / "generated" / "allen_calibrated_v2")
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_session_generator_v2.json")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_session_generator_v2.md")
    args = parser.parse_args()

    calibration = estimate_calibration(
        datasets_root=args.datasets_root,
        target_name=args.target_name,
        window_names=args.window_names,
        require_usable_target=args.require_usable_target,
        n_trials=args.n_trials,
        seed=args.seed,
    )
    report = generate_calibrated_session(calibration)
    write_session_artifact(report.session, args.out_session_dir)
    payload = report.to_dict()
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown(args.out_md, payload)
    print(f"generator_v2_json={args.out_json}")
    print(f"generator_v2_md={args.out_md}")
    print(f"generated_session_dir={args.out_session_dir}")


if __name__ == "__main__":
    main()
