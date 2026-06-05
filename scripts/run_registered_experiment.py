"""Run the default workflow and persist a registered experiment artifact."""

from __future__ import annotations

from pathlib import Path

from neurotwin_mvp.registry import ExperimentRegistry
from neurotwin_mvp.workflow import run_workflow


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Run the MVP workflow and store manifest/report/config snapshot."""
    config_path = ROOT / "configs" / "mouse_level0.json"
    seed = 7
    report = run_workflow(str(config_path), seed=seed)
    registry = ExperimentRegistry(ROOT / "artifacts")
    record = registry.create_run(report, config_path=config_path, seed=seed)
    print(f"registered_run={record.run_id}")
    print(f"artifact_dir={record.artifact_dir}")
    print(f"config_sha256={record.config_sha256}")


if __name__ == "__main__":
    main()
