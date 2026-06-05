"""Audit one normalized session artifact and write a transparent report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from neurotwin_mvp.artifacts import read_session_artifact
from neurotwin_mvp.audit import audit_session


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    session = read_session_artifact(args.session_dir)
    audit = audit_session(session)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(audit.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    print(f"audit_report={args.out}")
    print(f"n_trials={audit.n_trials}")
    print(f"regions={','.join(audit.region_names)}")
    print(f"warnings={len(audit.warnings)}")


if __name__ == "__main__":
    main()
