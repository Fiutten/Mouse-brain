"""Run transparent behavioral benchmarks on one normalized session artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from neurotwin_mvp.artifacts import read_session_artifact
from neurotwin_mvp.benchmark import run_target_benchmark


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--train-fraction", type=float, default=0.7)
    parser.add_argument(
        "--target-name",
        default="choice",
        choices=["choice", "go_response", "catch_response", "rewarded"],
        help="Binary behavioral target to benchmark.",
    )
    args = parser.parse_args()

    session = read_session_artifact(args.session_dir)
    suite = run_target_benchmark(
        session,
        target_name=args.target_name,
        train_fraction=args.train_fraction,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(suite.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    print(f"benchmark_report={args.out}")
    for result in suite.results:
        log_loss = "NA" if result.log_loss is None else f"{result.log_loss:.3f}"
        print(f"{result.name}: accuracy={result.accuracy:.3f} log_loss={log_loss}")
    print(f"warnings={len(suite.warnings)}")


if __name__ == "__main__":
    main()
