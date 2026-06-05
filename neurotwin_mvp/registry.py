"""Experiment registry and reproducibility utilities.

Research code becomes hard to trust when runs are not traceable. This module
creates a small, dependency-free registry that stores each workflow execution
with:

- timestamp;
- run identifier;
- configuration path and hash;
- seed;
- dataset summary;
- baseline results;
- lesion results;
- hypothesis/reviewer output.

The registry is intentionally simple JSON. It is not a replacement for MLflow,
Weights & Biases or DataJoint; it is a local, auditable baseline that can be
upgraded later.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import uuid

from .workflow import WorkflowReport


DEFAULT_ARTIFACT_ROOT = Path("artifacts")


@dataclass(frozen=True)
class ExperimentRecord:
    """Metadata for a registered workflow execution."""

    run_id: str
    created_at_utc: str
    config_path: str
    config_sha256: str
    seed: int
    artifact_dir: str


def sha256_file(path: str | Path) -> str:
    """Return SHA-256 hash of a file for reproducibility tracking."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def workflow_report_to_dict(report: WorkflowReport) -> dict:
    """Convert a workflow report into JSON-serializable dictionaries."""
    return {
        "hypotheses": [asdict(item) for item in report.hypotheses],
        "reviewer_findings": list(report.reviewer_findings),
        "dataset_summary": dict(report.dataset_summary),
        "region_rate_summary": dict(report.region_rate_summary),
        "baseline_reports": [asdict(item) for item in report.baseline_reports],
        "lesion_results": [asdict(item) for item in report.lesion_results],
        "knowledge_graph": {
            "nodes": report.knowledge_graph.nodes,
            "edges": report.knowledge_graph.edges,
            "evidence": [asdict(item) for item in report.knowledge_graph.evidence],
        },
    }


class ExperimentRegistry:
    """Local filesystem-backed experiment registry."""

    def __init__(self, artifact_root: str | Path = DEFAULT_ARTIFACT_ROOT) -> None:
        self.artifact_root = Path(artifact_root)
        self.experiment_root = self.artifact_root / "experiments"

    def create_run(
        self,
        report: WorkflowReport,
        config_path: str | Path,
        seed: int,
        run_id: str | None = None,
    ) -> ExperimentRecord:
        """Persist one workflow report and return its registry record."""
        config_path = Path(config_path)
        run_id = run_id or self._new_run_id()
        run_dir = self.experiment_root / run_id
        run_dir.mkdir(parents=True, exist_ok=False)

        record = ExperimentRecord(
            run_id=run_id,
            created_at_utc=datetime.now(timezone.utc).isoformat(),
            config_path=str(config_path),
            config_sha256=sha256_file(config_path),
            seed=seed,
            artifact_dir=str(run_dir),
        )
        self._write_json(run_dir / "manifest.json", asdict(record))
        self._write_json(run_dir / "report.json", workflow_report_to_dict(report))
        (run_dir / "config_snapshot.json").write_text(
            config_path.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        return record

    def list_runs(self) -> list[ExperimentRecord]:
        """Load all registered run manifests."""
        if not self.experiment_root.exists():
            return []
        records = []
        for manifest in sorted(self.experiment_root.glob("*/manifest.json")):
            data = json.loads(manifest.read_text(encoding="utf-8"))
            records.append(ExperimentRecord(**data))
        return records

    @staticmethod
    def _new_run_id() -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        suffix = uuid.uuid4().hex[:8]
        return f"{timestamp}-{suffix}"

    @staticmethod
    def _write_json(path: Path, data: dict) -> None:
        path.write_text(
            json.dumps(data, indent=2, sort_keys=True),
            encoding="utf-8",
        )
