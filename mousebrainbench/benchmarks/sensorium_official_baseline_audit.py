"""Audit whether the official Sensorium baseline stack is locally executable.

The audit is deliberately read-only. It does not install packages or download
models because doing so would make the publication state depend on mutable
external services. Its job is to decide whether the current repository can run
an official Sensorium baseline now, or whether the tracked local PyTorch MLP
must remain the strongest reproducible neural-network control.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mousebrainbench import __version__
from mousebrainbench.artifacts import code_revision


DEFAULT_OUTPUT = Path("results/sensorium_official_baseline_audit/summary.json")
DEFAULT_MARKDOWN = Path("results/sensorium_official_baseline_audit/summary.md")


@dataclass(frozen=True)
class RequirementProbe:
    """One import-level dependency probe for the official Sensorium ecosystem."""

    package: str
    purpose: str

    def as_dict(self) -> dict[str, str | bool]:
        return {
            "package": self.package,
            "purpose": self.purpose,
            "available": importlib.util.find_spec(self.package) is not None,
        }


OFFICIAL_STACK = (
    RequirementProbe("sensorium", "official Sensorium data/model helper package"),
    RequirementProbe("neuralpredictors", "standard Ecker/Sinz lab neural predictor models"),
    RequirementProbe("nnfabrik", "model/dataloader factory used by official examples"),
    RequirementProbe("datajoint", "metadata/backend dependency used by the ecosystem"),
    RequirementProbe("torch", "PyTorch runtime required by official Sensorium models"),
    RequirementProbe("torchvision", "implicit neuralpredictors dependency for convolutional cores"),
)


def _repo_probe(path: Path) -> dict[str, str | bool]:
    """Check whether an official starter-kit checkout is present locally."""

    return {
        "path": str(path),
        "exists": path.exists(),
        "has_env_yml": (path / "env.yml").exists(),
        "has_pyproject": (path / "pyproject.toml").exists(),
        "has_sensorium_package": (path / "sensorium").exists(),
    }


def audit(
    *,
    official_repo: Path = Path("external/sensorium_2023"),
    official_smoke: Path = Path(
        "results/sensorium_official_baseline_audit/official_model_smoke.json"
    ),
    official_trained_summary: Path = Path(
        "results/sensorium_official_baseline_audit/official_trained_baseline_summary.json"
    ),
    local_mlp_summary: Path = Path(
        "results/dynamic_sensorium_torch_mlp/summary_dynamic_sensorium2023_torch_mlp.json"
    ),
) -> dict[str, Any]:
    """Return a formal viability decision for official Sensorium baselines."""

    packages = [probe.as_dict() for probe in OFFICIAL_STACK]
    repo = _repo_probe(official_repo)
    missing = [item["package"] for item in packages if not item["available"]]
    repo_usable = bool(repo["exists"] and repo["has_sensorium_package"])
    smoke_payload = json.loads(official_smoke.read_text()) if official_smoke.exists() else None
    official_stack_forward_ok = bool(
        smoke_payload and smoke_payload.get("official_stack_forward_ok")
    )
    official_stack_viable = not missing and repo_usable and official_stack_forward_ok
    official_trained_available = official_trained_summary.exists()
    official_viable = official_stack_viable and official_trained_available
    local_mlp_available = local_mlp_summary.exists()

    if official_viable:
        decision = "official_sensorium_trained_baseline_locally_viable"
        action = (
            "Run the trained official baseline through the MouseBrainBench comparator "
            "and update Q1 claims."
        )
    elif official_stack_viable and local_mlp_available:
        decision = "official_sensorium_stack_integrated_training_pending"
        action = (
            "Treat the official stack as integrated at smoke-test level, but keep "
            "the tracked compact PyTorch MLP as the evaluated NN control until an "
            "official trained baseline summary exists."
        )
    elif local_mlp_available:
        decision = "official_sensorium_baseline_not_locally_viable_use_tracked_torch_mlp"
        action = (
            "Use the tracked compact PyTorch MLP as the local NN control, while "
            "stating explicitly that it is not an official/SOTA Sensorium model."
        )
    else:
        decision = "official_sensorium_baseline_not_viable_and_no_local_nn_control"
        action = "Block Q1 claims until either an official baseline or local NN control exists."

    return {
        "version": __version__,
        "git_revision": code_revision(),
        "official_repo_probe": repo,
        "package_probes": packages,
        "missing_packages": missing,
        "official_smoke": str(official_smoke),
        "official_stack_forward_ok": official_stack_forward_ok,
        "official_stack_viable": official_stack_viable,
        "official_trained_summary": str(official_trained_summary),
        "official_trained_baseline_available": official_trained_available,
        "official_baseline_viable": official_viable,
        "local_mlp_summary": str(local_mlp_summary),
        "local_mlp_available": local_mlp_available,
        "decision": decision,
        "recommended_action": action,
        "interpretation": (
            "Official Sensorium baselines are the preferred external control, but "
            "they only count for Q1 when trained/evaluated predictions are available. "
            "A forward-pass smoke test proves integration, not leaderboard-level "
            "performance."
        ),
    }


def write_outputs(payload: dict[str, Any], output: Path, markdown: Path) -> None:
    """Write JSON and compact Markdown audit artifacts."""

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2))
    lines = [
        "# Sensorium Official Baseline Audit",
        "",
        f"- Decision: `{payload['decision']}`",
        f"- Official stack forward OK: `{payload['official_stack_forward_ok']}`",
        (
            "- Official trained baseline available: "
            f"`{payload['official_trained_baseline_available']}`"
        ),
        f"- Official baseline Q1-viable: `{payload['official_baseline_viable']}`",
        f"- Local MLP available: `{payload['local_mlp_available']}`",
        f"- Recommended action: {payload['recommended_action']}",
        "",
        "## Package probes",
        "",
        "| Package | Available | Purpose |",
        "|---|---:|---|",
    ]
    for item in payload["package_probes"]:
        lines.append(f"| `{item['package']}` | `{item['available']}` | {item['purpose']} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            str(payload["interpretation"]),
            "",
        ]
    )
    markdown.parent.mkdir(parents=True, exist_ok=True)
    markdown.write_text("\n".join(lines))


def run(
    output: Path = DEFAULT_OUTPUT,
    markdown: Path = DEFAULT_MARKDOWN,
    official_repo: Path = Path("external/sensorium_2023"),
) -> Path:
    """Execute the read-only audit and write tracked artifacts."""

    payload = audit(official_repo=official_repo)
    write_outputs(payload, output, markdown)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--official-repo", type=Path, default=Path("external/sensorium_2023"))
    args = parser.parse_args()
    print(json.dumps({"output": str(run(args.output, args.markdown, args.official_repo).resolve())}))


if __name__ == "__main__":
    main()
