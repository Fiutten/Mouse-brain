"""Audit manuscript wording against executable claim contracts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from mousebrainbench import __version__
from mousebrainbench.artifacts import code_revision
from mousebrainbench.claimdsl import audit_claim_specs, load_claim_specs


DEFAULT_CLAIMS = Path("configs/claims/mousebrainbench_claims.yaml")
DEFAULT_OUTPUT = Path("results/manuscript_claim_audit/summary.json")
DEFAULT_MARKDOWN = Path("results/manuscript_claim_audit/summary.md")


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _read_texts(paths: tuple[Path, ...]) -> str:
    chunks = []
    for path in paths:
        if path.exists():
            chunks.append(path.read_text(errors="ignore"))
    return "\n".join(chunks)


def run(
    claims: Path = DEFAULT_CLAIMS,
    manuscript: tuple[Path, ...] = (Path("README.md"),),
    output: Path = DEFAULT_OUTPUT,
    markdown: Path = DEFAULT_MARKDOWN,
    root: Path = Path("."),
) -> Path:
    """Audit claim contracts and manuscript wording."""

    specs = load_claim_specs(root / claims)
    audit_results = audit_claim_specs(specs, root=root)
    text = _normalize(_read_texts(tuple(root / path for path in manuscript)))
    rows: list[dict[str, Any]] = []
    blocked_hits: list[dict[str, str]] = []
    for spec, result in zip(specs, audit_results, strict=True):
        permitted_present = _normalize(spec.permitted_wording) in text
        claim_blocked_hits = [
            wording for wording in spec.blocked_wording if _normalize(wording) in text
        ]
        for wording in claim_blocked_hits:
            blocked_hits.append({"claim_id": spec.claim_id, "blocked_wording": wording})
        rows.append(
            {
                "claim_id": spec.claim_id,
                "claim_type": spec.claim_type,
                "scope": spec.scope,
                "artifact_status": result.status,
                "permitted_wording_present": permitted_present,
                "blocked_wording_hits": claim_blocked_hits,
                "missing_artifacts": list(result.missing_artifacts),
                "failed_expectations": list(result.failed_expectations),
            }
        )
    unsupported_present = [
        row["claim_id"]
        for row in rows
        if row["permitted_wording_present"] and row["artifact_status"] != "supported"
    ]
    payload = {
        "version": __version__,
        "git_revision": code_revision(),
        "analysis": "manuscript_claim_audit",
        "claims_file": str(claims),
        "manuscript_inputs": [str(path) for path in manuscript],
        "rows": rows,
        "blocked_wording_hits": blocked_hits,
        "unsupported_present_claims": unsupported_present,
        "decision": (
            "manuscript_claim_audit_passed"
            if not blocked_hits and not unsupported_present
            else "manuscript_claim_audit_blocks_release"
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2))
    write_markdown(payload, markdown)
    return output


def write_markdown(payload: dict[str, Any], markdown: Path) -> None:
    """Write claim-audit report."""

    lines = [
        "# Manuscript Claim Audit",
        "",
        f"- Decision: `{payload['decision']}`",
        f"- Claims audited: `{len(payload['rows'])}`",
        f"- Blocked wording hits: `{len(payload['blocked_wording_hits'])}`",
        "",
        "| Claim | Artifact status | Permitted wording present | Blocked hits |",
        "|---|---|---:|---:|",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| `{row['claim_id']}` | `{row['artifact_status']}` | "
            f"`{row['permitted_wording_present']}` | `{len(row['blocked_wording_hits'])}` |"
        )
    lines.append("")
    markdown.parent.mkdir(parents=True, exist_ok=True)
    markdown.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claims", type=Path, default=DEFAULT_CLAIMS)
    parser.add_argument("--manuscript", type=Path, action="append")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    manuscripts = tuple(args.manuscript) if args.manuscript else (Path("README.md"),)
    print(
        json.dumps(
            {
                "output": str(
                    run(args.claims, manuscripts, args.output, args.markdown, args.root).resolve()
                )
            }
        )
    )


if __name__ == "__main__":
    main()
