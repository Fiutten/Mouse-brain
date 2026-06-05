"""Expand Allen exports until a target-specific evidence cohort is ready.

This script is intentionally operational rather than statistical. It automates
the repetitive loop that otherwise invites mistakes:

1. count currently usable target sessions;
2. export one additional Allen session if the target cohort is still too small;
3. rebuild target-specific reports;
4. repeat until the requested usable-session count is reached;
5. run a stronger final report with more permutations.

The default target is `go_response` because current diagnostics show it is the
first task-native Allen target with a plausible neural signal.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class CohortStatus:
    """Current usable target cohort size and trial count."""

    usable_sessions: int
    labeled_trials: int


def run_command(command: list[str], dry_run: bool = False) -> None:
    """Run a subprocess using explicit argv and print the command for logs."""
    print(" ".join(command), flush=True)
    if dry_run:
        return
    subprocess.run(command, check=True, text=True)


def load_target_status(diagnostics_path: Path, target_name: str) -> CohortStatus:
    """Read target diagnostics and return usable-session status."""
    payload = json.loads(diagnostics_path.read_text(encoding="utf-8"))
    target = payload.get("aggregate", {}).get(target_name)
    if target is None:
        return CohortStatus(usable_sessions=0, labeled_trials=0)
    return CohortStatus(
        usable_sessions=int(target["usable_sessions"]),
        labeled_trials=int(target["labeled_trials"]),
    )


def refresh_target_diagnostics(
    *,
    core_python: Path,
    diagnostics_path: Path,
    dry_run: bool,
) -> None:
    """Refresh global Allen target diagnostics."""
    run_command(
        [
            str(core_python),
            str(ROOT / "scripts" / "run_allen_target_diagnostics.py"),
            "--out",
            str(diagnostics_path),
        ],
        dry_run=dry_run,
    )


def export_one_session(
    *,
    core_python: Path,
    candidate_limit: int,
    screening_permutations: int,
    dry_run: bool,
) -> None:
    """Export one pending Allen session and refresh broad Allen reports."""
    run_command(
        [
            str(core_python),
            str(ROOT / "scripts" / "export_allen_sessions_batch.py"),
            "--max-new",
            "1",
            "--candidate-limit",
            str(candidate_limit),
            "--n-permutations",
            str(screening_permutations),
        ],
        dry_run=dry_run,
    )


def rebuild_target_reports(
    *,
    core_python: Path,
    target_name: str,
    reports_root: Path,
    n_permutations: int,
    min_sessions_for_claim: int,
    require_usable_target: bool,
    dry_run: bool,
) -> None:
    """Rebuild target-specific reports and evidence synthesis."""
    report_command = [
        str(core_python),
        str(ROOT / "scripts" / "run_allen_multisession_reports.py"),
        "--target-name",
        target_name,
        "--reports-root",
        str(reports_root),
        "--n-permutations",
        str(n_permutations),
    ]
    if require_usable_target:
        report_command.append("--require-usable-target")
    run_command(report_command, dry_run=dry_run)
    run_command(
        [
            str(core_python),
            str(ROOT / "scripts" / "run_allen_evidence_report.py"),
            "--reports-root",
            str(reports_root),
            "--out",
            str(reports_root / "evidence_report.json"),
            "--min-sessions-for-claim",
            str(min_sessions_for_claim),
        ],
        dry_run=dry_run,
    )


def write_run_status(path: Path, payload: dict[str, Any], dry_run: bool) -> None:
    """Persist orchestration status for reproducibility."""
    print(f"target_evidence_status={path}", flush=True)
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def default_reports_root(target_name: str) -> Path:
    """Return the strict usable-session report directory for a target."""
    return ROOT / "artifacts" / "reports" / "allen_targets" / f"{target_name}_usable"


def main() -> None:
    """Export sessions until the usable target cohort reaches the requested N."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--target-name",
        default="go_response",
        choices=["choice", "go_response", "catch_response", "rewarded"],
    )
    parser.add_argument("--target-usable-sessions", type=int, default=10)
    parser.add_argument("--max-new-sessions", type=int, default=12)
    parser.add_argument("--candidate-limit", type=int, default=25)
    parser.add_argument("--screening-permutations", type=int, default=50)
    parser.add_argument("--final-permutations", type=int, default=500)
    parser.add_argument("--core-python", type=Path, default=ROOT / ".venv" / "bin" / "python")
    parser.add_argument("--diagnostics-path", type=Path, default=ROOT / "artifacts" / "reports" / "allen" / "target_diagnostics.json")
    parser.add_argument(
        "--reports-root",
        type=Path,
        default=None,
        help="Target-specific report directory. Defaults to allen_targets/<target>_usable.",
    )
    parser.add_argument("--status-out", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "target_evidence_status.json")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.target_usable_sessions <= 0:
        raise ValueError("target_usable_sessions must be positive")
    if args.max_new_sessions < 0:
        raise ValueError("max_new_sessions must be non-negative")
    if args.screening_permutations <= 0 or args.final_permutations <= 0:
        raise ValueError("permutation counts must be positive")
    if args.reports_root is None:
        args.reports_root = default_reports_root(args.target_name)

    refresh_target_diagnostics(
        core_python=args.core_python,
        diagnostics_path=args.diagnostics_path,
        dry_run=args.dry_run,
    )
    status = (
        CohortStatus(usable_sessions=0, labeled_trials=0)
        if args.dry_run
        else load_target_status(args.diagnostics_path, args.target_name)
    )
    history: list[dict[str, Any]] = [
        {"phase": "initial", "status": asdict(status)},
    ]

    exported_attempts = 0
    while status.usable_sessions < args.target_usable_sessions and exported_attempts < args.max_new_sessions:
        export_one_session(
            core_python=args.core_python,
            candidate_limit=args.candidate_limit,
            screening_permutations=args.screening_permutations,
            dry_run=args.dry_run,
        )
        exported_attempts += 1
        refresh_target_diagnostics(
            core_python=args.core_python,
            diagnostics_path=args.diagnostics_path,
            dry_run=args.dry_run,
        )
        if not args.dry_run:
            status = load_target_status(args.diagnostics_path, args.target_name)
        history.append(
            {
                "phase": f"after_export_{exported_attempts}",
                "status": asdict(status),
            }
        )

    reached_target = status.usable_sessions >= args.target_usable_sessions
    # Always rebuild the strict cohort. If the target was not reached this still
    # records the best available evidence and makes the stopping point explicit.
    rebuild_target_reports(
        core_python=args.core_python,
        target_name=args.target_name,
        reports_root=args.reports_root,
        n_permutations=args.final_permutations if reached_target else args.screening_permutations,
        min_sessions_for_claim=args.target_usable_sessions,
        require_usable_target=True,
        dry_run=args.dry_run,
    )
    payload = {
        "created_at": datetime.now(UTC).isoformat(),
        "target_name": args.target_name,
        "target_usable_sessions": args.target_usable_sessions,
        "final_status": asdict(status),
        "exported_attempts": exported_attempts,
        "max_new_sessions": args.max_new_sessions,
        "candidate_limit": args.candidate_limit,
        "screening_permutations": args.screening_permutations,
        "final_permutations": args.final_permutations,
        "reached_target": reached_target,
        "history": history,
    }
    write_run_status(args.status_out, payload, dry_run=args.dry_run)
    print(f"usable_sessions={status.usable_sessions}")
    print(f"labeled_trials={status.labeled_trials}")
    print(f"reached_target={reached_target}")


if __name__ == "__main__":
    main()
