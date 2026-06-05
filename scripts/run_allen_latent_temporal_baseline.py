"""Run PCA latent temporal baselines on normalized Allen sessions."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean
from typing import Any

from neurotwin_mvp.artifacts import read_session_artifact
from neurotwin_mvp.behavioral_targets import TargetName, diagnose_target
from neurotwin_mvp.latent import run_latent_temporal_baseline


ROOT = Path(__file__).resolve().parents[1]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Allen latent temporal baseline: {payload['target_name']}",
        "",
        "## Summary",
        "",
    ]
    for key, value in payload["summary"].items():
        lines.append(f"- {key}: {_fmt(value)}")
    lines.extend(
        [
            "",
            "## Sessions",
            "",
            "| session | latent gain | baseline bal acc | latent bal acc | recon MSE | explained variance | warnings |",
            "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in payload["sessions"]:
        lines.append(
            "| {session_id} | {gain} | {baseline} | {latent} | {mse} | {ev} | {warnings} |".format(
                session_id=row["session_id"],
                gain=_fmt(row["latent_gain"]),
                baseline=_fmt(row["baseline_balanced_accuracy"]),
                latent=_fmt(row["latent_balanced_accuracy"]),
                mse=_fmt(row["reconstruction_mse"]),
                ev=_fmt(row["explained_variance_fraction"]),
                warnings="; ".join(row["warnings"]),
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- PCA latents are a transparent baseline for later representation-learning models.",
            "- Positive latent gain means temporal population structure helped beyond compact behavioral rows.",
            "- Failure here argues against adding heavier latent models until failure modes are understood.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    gains = [float(row["latent_gain"]) for row in rows]
    return {
        "n_sessions": len(rows),
        "mean_latent_gain": mean(gains) if gains else None,
        "positive_gain_fraction": sum(1 for gain in gains if gain > 0.0) / len(gains) if gains else None,
        "mean_reconstruction_mse": mean(float(row["reconstruction_mse"]) for row in rows) if rows else None,
        "mean_explained_variance_fraction": mean(float(row["explained_variance_fraction"]) for row in rows) if rows else None,
    }


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
    parser.add_argument("--window-names", nargs="+", default=["baseline", "stimulus", "pre_response"])
    parser.add_argument("--n-components", type=int, default=3)
    parser.add_argument("--require-usable-target", action="store_true")
    parser.add_argument("--datasets-root", type=Path, default=ROOT / "artifacts" / "datasets" / "allen")
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_latent_temporal_baseline.json")
    parser.add_argument("--out-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_latent_temporal_baseline.csv")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_latent_temporal_baseline.md")
    args = parser.parse_args()

    rows = []
    skipped = []
    for session_dir in sorted(path.parent for path in args.datasets_root.glob("*/session.json")):
        session = read_session_artifact(session_dir)
        diagnostic = diagnose_target(session, args.target_name)
        if args.require_usable_target and not diagnostic.usable:
            skipped.append({"session_id": session.session_id, "reason": "target_not_usable", "warnings": diagnostic.warnings})
            continue
        try:
            report = run_latent_temporal_baseline(
                session,
                target_name=args.target_name,
                window_names=args.window_names,
                n_components=args.n_components,
            )
        except ValueError as exc:
            skipped.append({"session_id": session.session_id, "reason": "latent_unavailable", "warnings": [str(exc)]})
            continue
        rows.append(report.to_dict())
    payload = {
        "target_name": args.target_name,
        "window_names": args.window_names,
        "n_components": args.n_components,
        "summary": summarize(rows),
        "sessions": rows,
        "skipped_sessions": skipped,
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_csv(args.out_csv, rows)
    write_markdown(args.out_md, payload)
    print(f"latent_json={args.out_json}")
    print(f"latent_md={args.out_md}")
    print(f"mean_latent_gain={_fmt(payload['summary']['mean_latent_gain'])}")


if __name__ == "__main__":
    main()
