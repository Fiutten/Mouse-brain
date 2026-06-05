"""Run a permutation test for neural-feature gain on a session artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from neurotwin_mvp.artifacts import read_session_artifact
from neurotwin_mvp.benchmark import run_neural_gain_permutation_test


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--train-fraction", type=float, default=0.7)
    parser.add_argument("--n-permutations", type=int, default=100)
    parser.add_argument("--seed", type=int, default=17)
    args = parser.parse_args()

    session = read_session_artifact(args.session_dir)
    report = run_neural_gain_permutation_test(
        session,
        train_fraction=args.train_fraction,
        n_permutations=args.n_permutations,
        seed=args.seed,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    print(f"permutation_report={args.out}")
    print(f"observed_gain={report.observed_gain:.3f}")
    print(f"null_gain_mean={report.null_gain_mean:.3f}")
    print(f"p_value={report.p_value:.3f}")
    print(f"warnings={len(report.warnings)}")


if __name__ == "__main__":
    main()
