"""Audit external-replication readiness without claiming unavailable evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from neurotwin_mvp.datasets import IBLBrainwideMapLoader


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ibl-root", type=Path, default=ROOT / "data" / "ibl")
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "replication" / "external_replication_readiness.json")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "replication" / "external_replication_readiness.md")
    args = parser.parse_args()

    loader = IBLBrainwideMapLoader(args.ibl_root)
    normalized = sorted(args.ibl_root.glob("normalized/*/session.json"))
    payload = {
        "dataset": "IBL brain-wide map",
        "one_api_available": loader.available(),
        "normalized_external_sessions": len(normalized),
        "adapter_load_implemented": False,
        "status": "blocked_no_normalized_external_sessions",
        "required_before_replication_claim": [
            "Select a task-harmonized IBL behavioral target before inspecting neural effects.",
            "Implement and test ONE-to-Session normalization.",
            "Freeze the response-independent primary analysis and thresholds.",
            "Run the frozen analysis on external sessions.",
            "Report exact and conceptual target differences.",
        ],
        "not_allowed": [
            "Calling the current Allen post-hoc partition a replication.",
            "Calling adapter availability an external validation.",
            "Transferring Allen go_response thresholds after inspecting IBL outcomes.",
        ],
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "# External replication readiness",
        "",
        f"- Status: `{payload['status']}`",
        f"- ONE API available: `{payload['one_api_available']}`",
        f"- Normalized external sessions: {payload['normalized_external_sessions']}",
        f"- Adapter load implemented: `{payload['adapter_load_implemented']}`",
        "",
        "External replication has not been performed. The project currently has an adapter contract only.",
        "",
        "## Required before a replication claim",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["required_before_replication_claim"])
    args.out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"external_replication_readiness={args.out_json}")
    print(f"status={payload['status']}")


if __name__ == "__main__":
    main()
