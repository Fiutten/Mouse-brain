"""Run the modular neurotwin MVP from the repository root."""

from __future__ import annotations

from pathlib import Path

from neurotwin_mvp.workflow import run_workflow


def main() -> None:
    """Run the default workflow and print a compact human-readable report."""
    root = Path(__file__).resolve().parent
    report = run_workflow(str(root / "configs" / "mouse_level0.json"))
    print("Hypotheses")
    for item in report.hypotheses:
        print(f"- {item.statement}")
        print(f"  intervention: {item.intervention}")
        print(f"  metric: {item.required_metric}")
    print("\nReviewer")
    for finding in report.reviewer_findings:
        print(f"- {finding}")
    print("\nSynthetic session")
    for key, value in report.dataset_summary.items():
        print(f"- {key}: {value:.3f}")
    print("\nBehavioral baselines")
    for baseline in report.baseline_reports:
        print(
            f"- {baseline.name:16s} "
            f"accuracy: {baseline.accuracy:.3f} "
            f"train: {baseline.n_train} "
            f"test: {baseline.n_test}"
        )
    print("\nLesion sweep")
    for result in report.lesion_results:
        print(
            f"- {result.lesion:20s} "
            f"p(+): {result.positive_stimulus_probability:.3f} "
            f"p(-): {result.negative_stimulus_probability:.3f} "
            f"sensitivity: {result.sensitivity:.3f}"
        )


if __name__ == "__main__":
    main()
