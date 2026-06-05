"""Rank pending Allen sessions using target-aware expansion evidence.

The first Allen selector used metadata only: units, probes and coarse region
coverage. That was appropriate before downloading real sessions, but the
40-session checkpoint showed a sharper bottleneck: many valid sessions fail the
strict `go_response` cohort because hit/miss labels are too imbalanced.

This script keeps the anatomical/recording-quality score but adds a conservative
empirical layer learned from already normalized sessions. It produces a ranked
download list plus the category-level rationale used for every score.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from neurotwin_mvp.allen_selection import (
    load_allen_session_candidates,
    load_target_relation_rows,
    rank_target_aware_candidates,
)


ROOT = Path(__file__).resolve().parents[1]


def _candidate_record(rank: int, item: Any) -> dict[str, Any]:
    """Flatten one ranked candidate for JSON/CSV/markdown outputs."""
    candidate = item.candidate
    return {
        "rank": rank,
        "ecephys_session_id": candidate.ecephys_session_id,
        "behavior_session_id": candidate.behavior_session_id,
        "mouse_id": candidate.mouse_id,
        "session_type": candidate.session_type,
        "image_set": candidate.image_set,
        "experience_level": candidate.experience_level,
        "unit_count": candidate.unit_count,
        "probe_count": candidate.probe_count,
        "covered_model_regions": ",".join(candidate.covered_model_regions),
        "metadata_score": candidate.score,
        "selector_score": item.selector_score,
        "target_viability_score": item.target_viability_score,
        "neural_evidence_score": item.neural_evidence_score,
        "metadata_quality_score": item.metadata_quality_score,
        "rationale": " | ".join(item.rationale),
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write an indented UTF-8 JSON report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write the selector table in spreadsheet-friendly form."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _fmt(value: Any, digits: int = 3) -> str:
    """Format numbers compactly for markdown."""
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    """Write a reviewer-readable selector report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Allen target-aware session selector",
        "",
        f"- Target: `{payload['target_name']}`",
        f"- Relation report: `{payload['relation_report']}`",
        f"- Metadata candidates considered: {payload['metadata_candidates_considered']}",
        f"- Pending candidates ranked: {payload['pending_candidates_ranked']}",
        "",
        "This selector is a prioritization tool, not confirmatory evidence. It",
        "combines target-balance viability, weak neural-evidence resemblance and",
        "metadata quality so the next downloads are less blind.",
        "",
        "## Top candidates",
        "",
        "| rank | ecephys session | behavior session | image | experience | selector | viability | evidence | metadata | units | probes |",
        "| ---: | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["candidates"]:
        lines.append(
            "| {rank} | {ecephys_session_id} | {behavior_session_id} | {image_set} | "
            "{experience_level} | {selector_score} | {target_viability_score} | "
            "{neural_evidence_score} | {metadata_quality_score} | {unit_count} | {probe_count} |".format(
                **{
                    **row,
                    "selector_score": _fmt(row["selector_score"]),
                    "target_viability_score": _fmt(row["target_viability_score"]),
                    "neural_evidence_score": _fmt(row["neural_evidence_score"]),
                    "metadata_quality_score": _fmt(row["metadata_quality_score"]),
                }
            )
        )
    lines.extend(
        [
            "",
            "## Scoring",
            "",
            "- `target_viability_score`: smoothed rate of usable `go_response` sessions for matching metadata categories.",
            "- `neural_evidence_score`: smoothed rate of permutation-significant sessions for matching metadata categories.",
            "- `metadata_quality_score`: normalized unit/probe/region coverage score.",
            "- `selector_score`: `0.55 * viability + 0.15 * evidence + 0.30 * metadata`.",
            "",
            "## Caution",
            "",
            "The empirical layer is descriptive and small-sample. After each new batch,",
            "rerun target diagnostics and this selector; do not treat the ranking as a",
            "static scientific model.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    """Build target-aware Allen candidate rankings."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-name", default="go_response")
    parser.add_argument("--metadata-csv", type=Path, default=ROOT / "data" / "allen" / "project_metadata" / "ecephys_sessions.csv")
    parser.add_argument("--datasets-root", type=Path, default=ROOT / "artifacts" / "datasets" / "allen")
    parser.add_argument("--relation-report", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_session_relations.json")
    parser.add_argument("--candidate-limit", type=int, default=80)
    parser.add_argument("--top-n", type=int, default=20)
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_target_aware_selector.json")
    parser.add_argument("--out-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_target_aware_selector.csv")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_target_aware_selector.md")
    args = parser.parse_args()

    candidates = load_allen_session_candidates(args.metadata_csv)[: args.candidate_limit]
    relation_rows = load_target_relation_rows(args.relation_report)
    ranked = rank_target_aware_candidates(
        candidates,
        relation_rows,
        datasets_root=args.datasets_root,
        top_n=args.top_n,
        exclude_exported=True,
    )
    rows = [_candidate_record(rank, item) for rank, item in enumerate(ranked, start=1)]
    payload = {
        "created_at": datetime.now(UTC).isoformat(),
        "target_name": args.target_name,
        "relation_report": str(args.relation_report),
        "metadata_csv": str(args.metadata_csv),
        "metadata_candidates_considered": len(candidates),
        "pending_candidates_ranked": len(rows),
        "score_weights": {
            "target_viability_score": 0.55,
            "neural_evidence_score": 0.15,
            "metadata_quality_score": 0.30,
        },
        "candidates": rows,
    }
    write_json(args.out_json, payload)
    write_csv(args.out_csv, rows)
    write_markdown(args.out_md, payload)
    print(f"selector_json={args.out_json}")
    print(f"selector_csv={args.out_csv}")
    print(f"selector_md={args.out_md}")
    print(f"pending_candidates_ranked={len(rows)}")
    if rows:
        print(f"top_ecephys_session_id={rows[0]['ecephys_session_id']}")


if __name__ == "__main__":
    main()
