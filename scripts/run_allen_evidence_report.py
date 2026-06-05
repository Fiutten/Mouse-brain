"""Synthesize Allen multi-session reports into a scientific evidence decision."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from neurotwin_mvp.evidence import synthesize_multisession_evidence


ROOT = Path(__file__).resolve().parents[1]


def load_session_report_bundle(report_dir: Path) -> dict[str, Any]:
    """Load the four generated reports required for one session-level decision."""
    required = {
        "audit": report_dir / "audit.json",
        "benchmark": report_dir / "benchmark.json",
        "multisplit": report_dir / "multisplit.json",
        "permutation": report_dir / "permutation.json",
    }
    missing = [str(path) for path in required.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing session reports for {report_dir.name}: {missing}")
    return {
        name: json.loads(path.read_text(encoding="utf-8"))
        for name, path in required.items()
    }


def main() -> None:
    """Read available Allen reports and write `evidence_report.json`."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports-root", type=Path, default=ROOT / "artifacts" / "reports" / "allen")
    parser.add_argument("--out", type=Path, default=ROOT / "artifacts" / "reports" / "allen" / "evidence_report.json")
    parser.add_argument("--min-sessions-for-claim", type=int, default=8)
    parser.add_argument("--bootstrap-iterations", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=17)
    args = parser.parse_args()

    session_dirs = sorted(
        path for path in args.reports_root.iterdir()
        if path.is_dir() and (path / "audit.json").exists()
    )
    bundles = [load_session_report_bundle(path) for path in session_dirs]
    report = synthesize_multisession_evidence(
        bundles,
        min_sessions_for_claim=args.min_sessions_for_claim,
        bootstrap_iterations=args.bootstrap_iterations,
        seed=args.seed,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    print(f"evidence_report={args.out}")
    print(f"n_sessions={report.n_sessions}")
    print(f"total_valid_trials={report.total_valid_trials}")
    print(f"decision={report.decision.label}")
    print(f"mean_multisplit_gain={report.mean_multisplit_gain:.3f}")
    print(f"mean_permutation_observed_gain={report.mean_permutation_observed_gain:.3f}")


if __name__ == "__main__":
    main()
