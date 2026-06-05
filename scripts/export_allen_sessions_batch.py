"""Export multiple Allen Visual Behavior Neuropixels sessions reproducibly.

The single-session exporter is deliberately small: it opens one local/remote
Allen NWB file and writes one normalized `session.json`. This batch script adds
the operational layer needed for real validation:

- rank candidate sessions from metadata;
- skip sessions already normalized;
- download NWB files with resumable `curl -C -`;
- call the Allen-specific Python environment for normalization;
- refresh core-environment reports after successful exports.
- refresh behavioral-target diagnostics after successful exports.

Large NWB files are several GB each. For that reason this script defaults to a
small number of new sessions and supports `--dry-run` for planning without
network or data writes.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from neurotwin_mvp.allen_selection import AllenSessionCandidate, load_allen_session_candidates


ROOT = Path(__file__).resolve().parents[1]
ALLEN_S3_BASE = "https://visual-behavior-neuropixels-data.s3.us-west-2.amazonaws.com"
ALLEN_PROJECT_PREFIX = "visual-behavior-neuropixels"


def nwb_url(ecephys_session_id: int) -> str:
    """Return the public S3 URL for one Allen Visual Behavior Neuropixels NWB."""
    return (
        f"{ALLEN_S3_BASE}/{ALLEN_PROJECT_PREFIX}/behavior_ecephys_sessions/"
        f"{ecephys_session_id}/ecephys_session_{ecephys_session_id}.nwb"
    )


def local_nwb_path(cache_dir: Path, ecephys_session_id: int) -> Path:
    """Return the local cache path used by AllenSDK for one ecephys session."""
    return (
        cache_dir
        / "visual-behavior-neuropixels-0.5.0"
        / "behavior_ecephys_sessions"
        / str(ecephys_session_id)
        / f"ecephys_session_{ecephys_session_id}.nwb"
    )


def session_artifact_path(datasets_root: Path, ecephys_session_id: int) -> Path:
    """Return the normalized artifact path for one exported session."""
    return datasets_root / str(ecephys_session_id) / "session.json"


def command_text(command: list[str]) -> str:
    """Render a command for logs without invoking a shell."""
    return " ".join(command)


def run_command(command: list[str], dry_run: bool) -> subprocess.CompletedProcess[str] | None:
    """Run a command unless this is a dry run.

    The command is passed as an argument list, not through a shell. That keeps
    quoting predictable and avoids accidental shell expansion in paths.
    """
    print(command_text(command), flush=True)
    if dry_run:
        return None
    return subprocess.run(command, check=True, text=True)


def download_nwb(
    *,
    curl_bin: Path,
    cache_dir: Path,
    ecephys_session_id: int,
    dry_run: bool,
    retry: int,
    retry_delay: int,
    connect_timeout: int,
    speed_time: int,
    speed_limit: int,
    max_time: int,
) -> Path:
    """Download or resume one NWB file with conservative network controls.

    Retries are handled outside `curl`. In practice, `curl --retry` can restart
    the transfer inside the same process and truncate the partially downloaded
    output. Starting a fresh `curl -C -` process per attempt is slower but more
    transparent: each attempt resumes from the current on-disk file size.
    """
    nwb_path = local_nwb_path(cache_dir, ecephys_session_id)
    nwb_path.parent.mkdir(parents=True, exist_ok=True)
    command = _curl_download_command(
        curl_bin=curl_bin,
        nwb_path=nwb_path,
        ecephys_session_id=ecephys_session_id,
        connect_timeout=connect_timeout,
        speed_time=speed_time,
        speed_limit=speed_limit,
        max_time=max_time,
    )
    if dry_run:
        run_command(command, dry_run=True)
        return nwb_path

    last_error: subprocess.CalledProcessError | None = None
    previous_size = nwb_path.stat().st_size if nwb_path.exists() else 0
    for attempt in range(retry + 1):
        try:
            run_command(command, dry_run=False)
            return nwb_path
        except subprocess.CalledProcessError as exc:
            last_error = exc
            current_size = nwb_path.stat().st_size if nwb_path.exists() else 0
            print(
                f"download_attempt_failed={attempt + 1} "
                f"partial_bytes={current_size} previous_bytes={previous_size}",
                flush=True,
            )
            if attempt >= retry:
                break
            previous_size = current_size
            time.sleep(retry_delay)
    if last_error is not None:
        raise last_error
    return nwb_path


def _curl_download_command(
    *,
    curl_bin: Path,
    nwb_path: Path,
    ecephys_session_id: int,
    connect_timeout: int,
    speed_time: int,
    speed_limit: int,
    max_time: int,
) -> list[str]:
    """Build one resumable `curl` invocation without internal retry flags."""
    return [
        str(curl_bin),
        "-L",
        "-C",
        "-",
        "--connect-timeout",
        str(connect_timeout),
        "--speed-time",
        str(speed_time),
        "--speed-limit",
        str(speed_limit),
        "--max-time",
        str(max_time),
        "-o",
        str(nwb_path),
        nwb_url(ecephys_session_id),
    ]


def export_session(
    *,
    allen_python: Path,
    datasets_root: Path,
    candidate: AllenSessionCandidate,
    max_trials: int | None,
    dry_run: bool,
) -> Path:
    """Normalize one downloaded Allen NWB session into `session.json`."""
    out_dir = datasets_root / str(candidate.ecephys_session_id)
    command = [
        str(allen_python),
        str(ROOT / "scripts" / "allen_export_session.py"),
        "--ecephys-session-id",
        str(candidate.ecephys_session_id),
        "--behavior-session-id",
        str(candidate.behavior_session_id),
        "--animal-id",
        str(candidate.mouse_id),
        "--out",
        str(out_dir),
    ]
    if max_trials is not None:
        command.extend(["--max-trials", str(max_trials)])
    run_command(command, dry_run=dry_run)
    return out_dir / "session.json"


def refresh_multisession_reports(
    *,
    core_python: Path,
    n_permutations: int,
    dry_run: bool,
) -> None:
    """Recompute reports over all currently normalized Allen session artifacts."""
    command = [
        str(core_python),
        str(ROOT / "scripts" / "run_allen_multisession_reports.py"),
        "--n-permutations",
        str(n_permutations),
    ]
    run_command(command, dry_run=dry_run)


def refresh_evidence_report(
    *,
    core_python: Path,
    dry_run: bool,
) -> None:
    """Recompute the scientific evidence synthesis over current reports."""
    command = [
        str(core_python),
        str(ROOT / "scripts" / "run_allen_evidence_report.py"),
    ]
    run_command(command, dry_run=dry_run)


def refresh_target_diagnostics(
    *,
    core_python: Path,
    dry_run: bool,
) -> None:
    """Recompute target-viability diagnostics over normalized Allen sessions.

    Target diagnostics are part of the evidence pipeline, not an optional
    notebook-style check. A newly exported session can change whether a task
    label is usable enough to benchmark, especially for rare catch responses.
    """
    command = [
        str(core_python),
        str(ROOT / "scripts" / "run_allen_target_diagnostics.py"),
    ]
    run_command(command, dry_run=dry_run)


def write_status_report(reports_root: Path, payload: dict[str, Any], dry_run: bool) -> Path:
    """Persist a machine-readable batch status report."""
    report_path = reports_root / "export_batch_status.json"
    if not dry_run:
        reports_root.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"batch_status={report_path}", flush=True)
    return report_path


def select_pending_candidates(
    *,
    metadata_csv: Path,
    datasets_root: Path,
    candidate_limit: int,
) -> tuple[list[AllenSessionCandidate], list[AllenSessionCandidate]]:
    """Return ranked candidates split into already-exported and pending groups."""
    candidates = load_allen_session_candidates(metadata_csv)[:candidate_limit]
    exported: list[AllenSessionCandidate] = []
    pending: list[AllenSessionCandidate] = []
    for candidate in candidates:
        artifact = session_artifact_path(datasets_root, candidate.ecephys_session_id)
        if artifact.exists():
            exported.append(candidate)
        else:
            pending.append(candidate)
    return exported, pending


def main() -> None:
    """Run a controlled multi-session Allen export batch."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata-csv", type=Path, default=ROOT / "data" / "allen" / "project_metadata" / "ecephys_sessions.csv")
    parser.add_argument("--cache-dir", type=Path, default=ROOT / "data" / "allen")
    parser.add_argument("--datasets-root", type=Path, default=ROOT / "artifacts" / "datasets" / "allen")
    parser.add_argument("--reports-root", type=Path, default=ROOT / "artifacts" / "reports" / "allen")
    parser.add_argument("--allen-python", type=Path, default=ROOT / ".venv-allen" / "bin" / "python")
    parser.add_argument("--core-python", type=Path, default=ROOT / ".venv" / "bin" / "python")
    parser.add_argument("--curl-bin", type=Path, default=Path("/usr/bin/curl"))
    parser.add_argument("--candidate-limit", type=int, default=10)
    parser.add_argument("--max-new", type=int, default=1)
    parser.add_argument("--max-trials", type=int)
    parser.add_argument("--n-permutations", type=int, default=50)
    parser.add_argument("--retry", type=int, default=10)
    parser.add_argument("--retry-delay", type=int, default=10)
    parser.add_argument("--connect-timeout", type=int, default=30)
    parser.add_argument("--speed-time", type=int, default=90)
    parser.add_argument("--speed-limit", type=int, default=2048)
    parser.add_argument("--max-time", type=int, default=1800)
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    exported, pending = select_pending_candidates(
        metadata_csv=args.metadata_csv,
        datasets_root=args.datasets_root,
        candidate_limit=args.candidate_limit,
    )
    selected = pending[: args.max_new]
    attempted: list[dict[str, Any]] = []
    exported_count = 0
    had_failure = False

    for candidate in selected:
        record: dict[str, Any] = {
            "candidate": asdict(candidate),
            "nwb_path": str(local_nwb_path(args.cache_dir, candidate.ecephys_session_id)),
            "session_artifact": str(session_artifact_path(args.datasets_root, candidate.ecephys_session_id)),
            "status": "pending",
        }
        attempted.append(record)
        try:
            download_nwb(
                curl_bin=args.curl_bin,
                cache_dir=args.cache_dir,
                ecephys_session_id=candidate.ecephys_session_id,
                dry_run=args.dry_run,
                retry=args.retry,
                retry_delay=args.retry_delay,
                connect_timeout=args.connect_timeout,
                speed_time=args.speed_time,
                speed_limit=args.speed_limit,
                max_time=args.max_time,
            )
            export_session(
                allen_python=args.allen_python,
                datasets_root=args.datasets_root,
                candidate=candidate,
                max_trials=args.max_trials,
                dry_run=args.dry_run,
            )
            record["status"] = "exported" if not args.dry_run else "planned"
            exported_count += 1
        except Exception as exc:
            record["status"] = "failed"
            record["error"] = str(exc)
            had_failure = True
            if not args.continue_on_error:
                break

    if exported_count > 0 or (args.dry_run and selected):
        refresh_multisession_reports(
            core_python=args.core_python,
            n_permutations=args.n_permutations,
            dry_run=args.dry_run,
        )
        refresh_evidence_report(
            core_python=args.core_python,
            dry_run=args.dry_run,
        )
        refresh_target_diagnostics(
            core_python=args.core_python,
            dry_run=args.dry_run,
        )

    payload = {
        "created_at": datetime.now(UTC).isoformat(),
        "dry_run": args.dry_run,
        "candidate_limit": args.candidate_limit,
        "max_new": args.max_new,
        "already_exported": [asdict(candidate) for candidate in exported],
        "attempted": attempted,
        "remaining_pending": [asdict(candidate) for candidate in pending[args.max_new :]],
    }
    write_status_report(args.reports_root, payload, dry_run=args.dry_run)
    print(f"already_exported={len(exported)}")
    print(f"attempted={len(attempted)}")
    print(f"remaining_pending={max(0, len(pending) - len(selected))}")
    if had_failure:
        sys.exit(1)


if __name__ == "__main__":
    main()
