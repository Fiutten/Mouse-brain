"""Executable claim specification and auditing.

The DSL is intentionally small. A claim is supported only when every declared
artifact exists and every declared expectation matches. This keeps manuscript
wording tied to repository evidence instead of informal interpretation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ClaimSpec:
    """A machine-readable scientific claim contract."""

    claim_id: str
    claim_type: str
    scope: str
    permitted_wording: str
    blocked_wording: tuple[str, ...]
    required_artifacts: tuple[dict[str, Any], ...]
    uncertainty_policy: str = "deterministic"


@dataclass(frozen=True)
class ClaimAuditResult:
    """Result of auditing one claim contract."""

    claim_id: str
    status: str
    missing_artifacts: tuple[str, ...]
    failed_expectations: tuple[str, ...]
    permitted_wording: str
    blocked_wording: tuple[str, ...]


def _get_dotted(payload: dict[str, Any], dotted_key: str) -> Any:
    current: Any = payload
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _expectation_passes(actual: Any, expectation: dict[str, Any]) -> bool:
    if "equals" in expectation:
        return actual == expectation["equals"]
    if "min" in expectation and (actual is None or float(actual) < float(expectation["min"])):
        return False
    if "max" in expectation and (actual is None or float(actual) > float(expectation["max"])):
        return False
    if "not_equals" in expectation:
        return actual != expectation["not_equals"]
    return True


def load_claim_specs(path: Path) -> tuple[ClaimSpec, ...]:
    """Load claim specs from YAML."""

    raw = yaml.safe_load(path.read_text()) or {}
    claims = raw.get("claims", [])
    return tuple(
        ClaimSpec(
            claim_id=str(item["claim_id"]),
            claim_type=str(item["claim_type"]),
            scope=str(item["scope"]),
            permitted_wording=str(item["permitted_wording"]),
            blocked_wording=tuple(str(text) for text in item.get("blocked_wording", [])),
            required_artifacts=tuple(dict(artifact) for artifact in item.get("required_artifacts", [])),
            uncertainty_policy=str(item.get("uncertainty_policy", "deterministic")),
        )
        for item in claims
    )


def audit_claim_specs(specs: tuple[ClaimSpec, ...], root: Path = Path(".")) -> tuple[ClaimAuditResult, ...]:
    """Audit claim contracts against local artifacts."""

    results: list[ClaimAuditResult] = []
    for spec in specs:
        missing: list[str] = []
        failed: list[str] = []
        for artifact in spec.required_artifacts:
            path = root / str(artifact["path"])
            if not path.exists():
                missing.append(str(artifact["path"]))
                continue
            payload = json.loads(path.read_text()) if path.suffix == ".json" else {}
            for expectation in artifact.get("expectations", []):
                key = str(expectation["key"])
                actual = _get_dotted(payload, key)
                if not _expectation_passes(actual, expectation):
                    failed.append(
                        f"{artifact['path']}::{key} expected {expectation}, observed {actual!r}"
                    )
        status = "supported" if not missing and not failed else "blocked"
        results.append(
            ClaimAuditResult(
                claim_id=spec.claim_id,
                status=status,
                missing_artifacts=tuple(missing),
                failed_expectations=tuple(failed),
                permitted_wording=spec.permitted_wording,
                blocked_wording=spec.blocked_wording,
            )
        )
    return tuple(results)
