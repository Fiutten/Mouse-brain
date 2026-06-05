"""Re-export cached Allen sessions with temporal neural-window metadata.

The Allen NWB files are large, so this script assumes sessions were already
downloaded into the local Allen cache. It orchestrates the Allen-specific
environment from the core environment and rewrites normalized `session.json`
artifacts with `region_rates_by_window` metadata.

Use `--require-usable-target` to limit re-export to sessions that are currently
scientifically viable for a target such as `go_response`.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path
from typing import Any

from neurotwin_mvp.artifacts import read_session_artifact
from neurotwin_mvp.behavioral_targets import TargetName, diagnose_target


ROOT = Path(__file__).resolve().parents[1]


def load_exported_metadata(path: Path) -> dict[str, dict[str, Any]]:
    """Load Allen export metadata indexed by ecephys session id."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("already_exported", [])
    return {
        str(row["ecephys_session_id"]): row
        for row in rows
        if row.get("ecephys_session_id") is not None
    }


def load_session_metadata_csv(path: Path) -> dict[str, dict[str, Any]]:
    """Load fallback Allen session metadata from the local project CSV."""
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        return {
            str(row["ecephys_session_id"]): row
            for row in csv.DictReader(handle)
            if row.get("ecephys_session_id")
        }


def has_temporal_metadata(session_dir: Path) -> bool:
    """Return whether the normalized artifact already contains temporal windows."""
    session = read_session_artifact(session_dir)
    if not session.trials:
        return False
    temporal = session.trials[0].metadata.get("region_rates_by_window")
    return isinstance(temporal, dict) and {"baseline", "stimulus", "decision"}.issubset(temporal)


def target_is_usable(session_dir: Path, target_name: TargetName) -> bool:
    """Evaluate target usability on the current normalized artifact."""
    session = read_session_artifact(session_dir)
    return diagnose_target(session, target_name).usable


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-name", default="go_response")
    parser.add_argument("--require-usable-target", action="store_true")
    parser.add_argument("--skip-existing-temporal", action="store_true")
    parser.add_argument("--max-sessions", type=int)
    parser.add_argument("--datasets-root", type=Path, default=ROOT / "artifacts" / "datasets" / "allen")
    parser.add_argument("--export-status", type=Path, default=ROOT / "artifacts" / "reports" / "allen" / "export_batch_status.json")
    parser.add_argument("--metadata-csv", type=Path, default=ROOT / "data" / "allen" / "project_metadata" / "ecephys_sessions.csv")
    parser.add_argument("--allen-python", type=Path, default=ROOT / ".venv-allen" / "bin" / "python")
    parser.add_argument("--out", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "temporal_reexport_status.json")
    args = parser.parse_args()

    target_name: TargetName = args.target_name
    metadata = load_exported_metadata(args.export_status)
    metadata_csv = load_session_metadata_csv(args.metadata_csv)
    exported = []
    skipped = []
    for session_json in sorted(args.datasets_root.glob("*/session.json")):
        session_dir = session_json.parent
        session_id = session_dir.name
        row = metadata.get(session_id) or metadata_csv.get(session_id)
        if row is None:
            skipped.append({"session_id": session_id, "reason": "missing_export_metadata"})
            continue
        if args.require_usable_target and not target_is_usable(session_dir, target_name):
            skipped.append({"session_id": session_id, "reason": "target_not_usable"})
            continue
        if args.skip_existing_temporal and has_temporal_metadata(session_dir):
            skipped.append({"session_id": session_id, "reason": "already_temporal"})
            continue
        if args.max_sessions is not None and len(exported) >= args.max_sessions:
            skipped.append({"session_id": session_id, "reason": "max_sessions_reached"})
            continue

        command = [
            str(args.allen_python),
            str(ROOT / "scripts" / "allen_export_session.py"),
            "--ecephys-session-id",
            str(row["ecephys_session_id"]),
            "--animal-id",
            str(row.get("mouse_id", "unknown")),
            "--out",
            str(session_dir),
        ]
        if row.get("behavior_session_id") is not None:
            command.extend(["--behavior-session-id", str(row["behavior_session_id"])])
        subprocess.run(command, check=True)
        exported.append({"session_id": session_id, "out": str(session_dir / "session.json")})

    payload = {
        "target_name": target_name,
        "require_usable_target": bool(args.require_usable_target),
        "skip_existing_temporal": bool(args.skip_existing_temporal),
        "n_exported": len(exported),
        "n_skipped": len(skipped),
        "exported": exported,
        "skipped": skipped,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"temporal_reexport_status={args.out}")
    print(f"n_exported={len(exported)}")
    print(f"n_skipped={len(skipped)}")


if __name__ == "__main__":
    main()
