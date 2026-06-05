"""Run available Allen session reports and aggregate them.

This script intentionally operates on already-normalized `session.json`
artifacts. It does not download NWB files. That keeps multi-session reporting
cheap and explicit: adding a new session requires exporting it first through
the Allen environment.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from neurotwin_mvp.artifacts import read_session_artifact
from neurotwin_mvp.audit import audit_session
from neurotwin_mvp.behavioral_targets import diagnose_target, materialize_target_session
from neurotwin_mvp.benchmark import (
    run_target_benchmark,
    run_multisplit_neural_gain,
    run_neural_gain_permutation_test,
)


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasets-root", type=Path, default=ROOT / "artifacts" / "datasets" / "allen")
    parser.add_argument("--reports-root", type=Path, default=ROOT / "artifacts" / "reports" / "allen")
    parser.add_argument("--n-permutations", type=int, default=50)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument(
        "--target-name",
        default="choice",
        choices=[
            "choice",
            "go_response",
            "catch_response",
            "rewarded",
            "response_made",
            "task_success",
        ],
        help="Binary behavioral target used for benchmark, multi-split and permutation reports.",
    )
    parser.add_argument(
        "--require-usable-target",
        action="store_true",
        help="Skip sessions whose target diagnostic fails count or balance checks.",
    )
    args = parser.parse_args()

    session_dirs = sorted(path.parent for path in args.datasets_root.glob("*/session.json"))
    summaries = []
    skipped = []
    for session_dir in session_dirs:
        session = read_session_artifact(session_dir)
        target_diagnostic = diagnose_target(session, args.target_name)
        if args.require_usable_target and not target_diagnostic.usable:
            skipped.append(
                {
                    "session_id": session.session_id,
                    "target_name": args.target_name,
                    "warnings": target_diagnostic.warnings,
                }
            )
            continue
        report_dir = args.reports_root / session.session_id
        report_dir.mkdir(parents=True, exist_ok=True)

        benchmark = run_target_benchmark(session, target_name=args.target_name)
        multisplit = run_multisplit_neural_gain(session, target_name=args.target_name)
        permutation = run_neural_gain_permutation_test(
            session,
            n_permutations=args.n_permutations,
            seed=args.seed,
            target_name=args.target_name,
        )
        # Audit the same materialized target view used by the benchmark. This
        # makes choice_rate in target-specific evidence mean "target positive
        # rate", which is the relevant imbalance diagnostic for that report.
        audit = audit_session(materialize_target_session(session, args.target_name))

        (report_dir / "audit.json").write_text(
            json.dumps(audit.to_dict(), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (report_dir / "benchmark.json").write_text(
            json.dumps(benchmark.to_dict(), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (report_dir / "multisplit.json").write_text(
            json.dumps(multisplit.to_dict(), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (report_dir / "permutation.json").write_text(
            json.dumps(permutation.to_dict(), indent=2, sort_keys=True),
            encoding="utf-8",
        )

        summaries.append(
            {
                "session_id": session.session_id,
                "target_name": args.target_name,
                "n_trials": audit.n_trials,
                "multisplit_mean_gain": multisplit.mean_gain,
                "permutation_observed_gain": permutation.observed_gain,
                "permutation_p_value": permutation.p_value,
                "permutation_warnings": permutation.warnings,
            }
        )

    aggregate = {
        "n_sessions": len(summaries),
        "target_name": args.target_name,
        "sessions": summaries,
        "skipped_sessions": skipped,
        "warnings": [] if len(summaries) > 1 else ["Only one normalized Allen session is currently available"],
    }
    args.reports_root.mkdir(parents=True, exist_ok=True)
    aggregate_path = args.reports_root / "multisession_summary.json"
    aggregate_path.write_text(json.dumps(aggregate, indent=2, sort_keys=True), encoding="utf-8")
    print(f"multisession_summary={aggregate_path}")
    print(f"n_sessions={len(summaries)}")


if __name__ == "__main__":
    main()
