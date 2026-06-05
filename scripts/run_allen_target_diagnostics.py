"""Run task-native behavioral target diagnostics for Allen session artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from neurotwin_mvp.artifacts import read_session_artifact
from neurotwin_mvp.behavioral_targets import diagnose_session_targets


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Diagnose target viability across all normalized Allen sessions."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasets-root", type=Path, default=ROOT / "artifacts" / "datasets" / "allen")
    parser.add_argument("--out", type=Path, default=ROOT / "artifacts" / "reports" / "allen" / "target_diagnostics.json")
    args = parser.parse_args()

    session_dirs = sorted(path.parent for path in args.datasets_root.glob("*/session.json"))
    reports = [
        diagnose_session_targets(read_session_artifact(session_dir)).to_dict()
        for session_dir in session_dirs
    ]
    aggregate: dict[str, dict[str, int]] = {}
    for report in reports:
        for diagnostic in report["diagnostics"]:
            target = diagnostic["target_name"]
            stats = aggregate.setdefault(
                target,
                {"sessions": 0, "usable_sessions": 0, "labeled_trials": 0},
            )
            stats["sessions"] += 1
            stats["usable_sessions"] += int(bool(diagnostic["usable"]))
            stats["labeled_trials"] += int(diagnostic["n_labeled_trials"])

    payload = {
        "n_sessions": len(reports),
        "aggregate": aggregate,
        "sessions": reports,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"target_diagnostics={args.out}")
    print(f"n_sessions={len(reports)}")
    for target, stats in sorted(aggregate.items()):
        print(
            f"{target}: usable_sessions={stats['usable_sessions']}/{stats['sessions']} "
            f"labeled_trials={stats['labeled_trials']}"
        )


if __name__ == "__main__":
    main()
