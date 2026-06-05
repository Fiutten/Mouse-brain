"""Run repeated chronological neural-gain validation on a session artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from neurotwin_mvp.artifacts import read_session_artifact
from neurotwin_mvp.benchmark import run_multisplit_neural_gain


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--n-splits", type=int, default=4)
    parser.add_argument("--initial-train-fraction", type=float, default=0.50)
    parser.add_argument("--test-fraction", type=float, default=0.15)
    args = parser.parse_args()

    session = read_session_artifact(args.session_dir)
    report = run_multisplit_neural_gain(
        session,
        n_splits=args.n_splits,
        initial_train_fraction=args.initial_train_fraction,
        test_fraction=args.test_fraction,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    print(f"multisplit_report={args.out}")
    print(f"mean_gain={report.mean_gain:.3f}")
    print(f"warnings={len(report.warnings)}")


if __name__ == "__main__":
    main()
