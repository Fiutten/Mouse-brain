"""Build the Allen session x control stability matrix."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from neurotwin_mvp.stability import build_stability_matrix


ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


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
        f"# Allen stability matrix: {payload['target_name']} / {payload['window_name']}",
        "",
        "## Summary",
        "",
    ]
    for key, value in payload["summary"].items():
        lines.append(f"- {key}: {_fmt(value)}")
    lines.extend(
        [
            "",
            "## Session Matrix",
            "",
            "| session | score | status | temporal gain | p value | visual cortex drop | fast gain | slow gain |",
            "| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in payload["rows"]:
        lines.append(
            "| {session_id} | {score} | {status} | {temporal_gain} | {p_value} | {drop} | {fast} | {slow} |".format(
                session_id=row["session_id"],
                score=_fmt(row["stability_score"]),
                status=row["status"],
                temporal_gain=_fmt(row["temporal_gain"]),
                p_value=_fmt(row["temporal_p_value"]),
                drop=_fmt(row["visual_cortex_drop"]),
                fast=_fmt(row["fast_latency_gain"]),
                slow=_fmt(row["slow_latency_gain"]),
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Robust sessions pass most current gates; mixed sessions require targeted inspection.",
            "- The matrix is a promotion gate for claims, not a biological mechanism by itself.",
        ]
    )
    if payload["warnings"]:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in payload["warnings"])
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
    parser.add_argument("--permutation-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_permutation_500.csv")
    parser.add_argument("--regional-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_regional_ablation_all_sessions.csv")
    parser.add_argument("--latency-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_latency_strata.csv")
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_stability_matrix.json")
    parser.add_argument("--out-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_stability_matrix.csv")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_stability_matrix.md")
    args = parser.parse_args()

    report = build_stability_matrix(
        target_name=args.target_name,
        window_name=args.window_name,
        temporal_rows=read_csv(args.permutation_csv),
        regional_rows=read_csv(args.regional_csv),
        latency_rows=read_csv(args.latency_csv),
    )
    payload = report.to_dict()
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_csv(args.out_csv, payload["rows"])
    write_markdown(args.out_md, payload)
    print(f"stability_json={args.out_json}")
    print(f"stability_md={args.out_md}")
    print(f"mean_stability_score={payload['summary']['mean_stability_score']:.3f}")


if __name__ == "__main__":
    main()
