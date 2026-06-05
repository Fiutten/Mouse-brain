"""Prune raw Allen NWB files for target-non-usable sessions.

Normalized `session.json` artifacts are small and remain valuable for audit,
diagnostics and reviewer-facing reproducibility. Raw NWB files are large and
can be re-downloaded from Allen S3, so this script deletes only the raw NWB
files for sessions that a target-relation report marks as non-usable.

The default mode is a dry run. Use `--execute` only after reviewing the JSON,
CSV or markdown plan that the dry run writes.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def load_relation_rows(path: Path) -> list[dict[str, Any]]:
    """Load per-session rows from the current or legacy relation-report schema."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("sessions", payload.get("rows", []))
    if not isinstance(rows, list):
        raise ValueError(f"Expected list of relation rows in {path}")
    return [row for row in rows if isinstance(row, dict)]


def nwb_path(cache_dir: Path, session_id: str) -> Path:
    """Return the AllenSDK raw NWB cache path for one ecephys session."""
    return (
        cache_dir
        / "visual-behavior-neuropixels-0.5.0"
        / "behavior_ecephys_sessions"
        / session_id
        / f"ecephys_session_{session_id}.nwb"
    )


def artifact_path(datasets_root: Path, session_id: str) -> Path:
    """Return the normalized session artifact path used for audit retention."""
    return datasets_root / session_id / "session.json"


def file_size(path: Path) -> int:
    """Return file size in bytes, or zero when the file is absent."""
    return path.stat().st_size if path.exists() else 0


def build_prune_plan(
    *,
    relation_rows: list[dict[str, Any]],
    cache_dir: Path,
    datasets_root: Path,
    target_name: str,
) -> list[dict[str, Any]]:
    """Build a deletion plan for raw NWB files that are safe to prune.

    A row is eligible only when:

    - the relation report marks it as not usable for the target;
    - the normalized `session.json` artifact exists;
    - the raw NWB file exists.

    Keeping the normalized artifact preserves the scientific reason for
    exclusion while freeing the expensive raw cache file.
    """
    planned: list[dict[str, Any]] = []
    for row in sorted(relation_rows, key=lambda item: str(item.get("session_id", ""))):
        if bool(row.get("go_usable", False)):
            continue
        session_id = str(row.get("session_id", ""))
        if not session_id:
            continue
        raw_nwb = nwb_path(cache_dir, session_id)
        normalized = artifact_path(datasets_root, session_id)
        planned.append(
            {
                "session_id": session_id,
                "target_name": target_name,
                "reason": row.get("target_warnings", "target_not_usable"),
                "go_labeled_trials": row.get("go_labeled_trials"),
                "go_positive_rate": row.get("go_positive_rate"),
                "go_minority_fraction": row.get("go_minority_fraction"),
                "nwb_path": str(raw_nwb),
                "nwb_exists": raw_nwb.exists(),
                "nwb_size_bytes": file_size(raw_nwb),
                "normalized_artifact": str(normalized),
                "normalized_artifact_exists": normalized.exists(),
                "eligible_for_delete": raw_nwb.exists() and normalized.exists(),
            }
        )
    return planned


def execute_plan(plan: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Delete eligible raw NWB files and return per-file outcomes."""
    outcomes: list[dict[str, Any]] = []
    for item in plan:
        outcome = dict(item)
        if not item["eligible_for_delete"]:
            outcome["delete_status"] = "skipped_not_eligible"
        else:
            path = Path(str(item["nwb_path"]))
            path.unlink()
            outcome["delete_status"] = "deleted"
        outcomes.append(outcome)
    return outcomes


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write a reproducible cleanup report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write the cleanup plan/outcome as a CSV table."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    """Write a human-readable cache-pruning report."""
    rows = payload["sessions"]
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Allen raw NWB cache pruning",
        "",
        f"- Mode: `{payload['mode']}`",
        f"- Target: `{payload['target_name']}`",
        f"- Candidate non-usable sessions: {payload['n_candidate_sessions']}",
        f"- Eligible raw NWB files: {payload['n_eligible_files']}",
        f"- Bytes eligible/deleted: {payload['eligible_bytes']}",
        "",
        "Raw NWB files are pruned only when the normalized `session.json` audit",
        "artifact exists. This keeps target-failure evidence available while",
        "freeing local cache space.",
        "",
        "| session | eligible | size GB | minority frac | reason | status |",
        "| ---: | --- | ---: | ---: | --- | --- |",
    ]
    for row in rows:
        size_gb = float(row["nwb_size_bytes"]) / (1024**3)
        minority = row.get("go_minority_fraction")
        minority_text = f"{float(minority):.3f}" if minority is not None else ""
        lines.append(
            "| {session} | {eligible} | {size:.2f} | {minority} | {reason} | {status} |".format(
                session=row["session_id"],
                eligible=str(row["eligible_for_delete"]).lower(),
                size=size_gb,
                minority=minority_text,
                reason=row.get("reason", ""),
                status=row.get("delete_status", "planned"),
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    """Prune raw NWB cache files for target-non-usable Allen sessions."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-name", default="go_response")
    parser.add_argument("--relation-report", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_session_relations.json")
    parser.add_argument("--cache-dir", type=Path, default=ROOT / "data" / "allen")
    parser.add_argument("--datasets-root", type=Path, default=ROOT / "artifacts" / "datasets" / "allen")
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen" / "nwb_cache_prune_nonusable_go_response.json")
    parser.add_argument("--out-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen" / "nwb_cache_prune_nonusable_go_response.csv")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "allen" / "nwb_cache_prune_nonusable_go_response.md")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    rows = load_relation_rows(args.relation_report)
    plan = build_prune_plan(
        relation_rows=rows,
        cache_dir=args.cache_dir,
        datasets_root=args.datasets_root,
        target_name=args.target_name,
    )
    sessions = execute_plan(plan) if args.execute else plan
    eligible_bytes = sum(int(row["nwb_size_bytes"]) for row in plan if row["eligible_for_delete"])
    payload = {
        "created_at": datetime.now(UTC).isoformat(),
        "mode": "execute" if args.execute else "dry_run",
        "target_name": args.target_name,
        "relation_report": str(args.relation_report),
        "cache_dir": str(args.cache_dir),
        "datasets_root": str(args.datasets_root),
        "n_candidate_sessions": len(plan),
        "n_eligible_files": sum(1 for row in plan if row["eligible_for_delete"]),
        "eligible_bytes": eligible_bytes,
        "sessions": sessions,
    }
    write_json(args.out_json, payload)
    write_csv(args.out_csv, sessions)
    write_markdown(args.out_md, payload)
    print(f"mode={payload['mode']}")
    print(f"candidate_sessions={payload['n_candidate_sessions']}")
    print(f"eligible_files={payload['n_eligible_files']}")
    print(f"eligible_gb={eligible_bytes / (1024**3):.2f}")
    print(f"report_json={args.out_json}")


if __name__ == "__main__":
    main()
