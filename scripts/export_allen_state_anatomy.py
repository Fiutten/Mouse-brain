"""Export direct state, unit-quality and fine-anatomy summaries from local NWB.

This script runs in `.venv-allen`. It writes a separate sidecar artifact and
does not modify the normalized `session.json` used by existing analyses.
Keeping enrichment separate prevents retrospective changes to the primary
evidence inputs.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from statistics import mean
from typing import Any

from neurotwin_mvp.allen_normalization import allen_acronym_to_model_region
from neurotwin_mvp.artifacts import read_session_artifact


ROOT = Path(__file__).resolve().parents[1]


def local_nwb_path(cache_dir: Path, ecephys_session_id: int) -> Path:
    """Return the expected local Visual Behavior Neuropixels NWB path."""
    return (
        cache_dir
        / "visual-behavior-neuropixels-0.5.0"
        / "behavior_ecephys_sessions"
        / str(ecephys_session_id)
        / f"ecephys_session_{ecephys_session_id}.nwb"
    )


def load_local_allen_session(cache_dir: Path, ecephys_session_id: int):
    """Open one existing NWB without triggering a network download."""
    from allensdk.brain_observatory.ecephys.behavior_ecephys_session import (
        BehaviorEcephysSession,
    )

    path = local_nwb_path(cache_dir, ecephys_session_id)
    if not path.exists():
        raise FileNotFoundError(f"Local NWB is unavailable: {path}")
    return BehaviorEcephysSession.from_nwb_path(str(path))


def finite(value: Any) -> bool:
    """Return whether a value is a finite real number."""
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def interval_mean(table: Any, value_name: str, start: float, end: float) -> float | None:
    """Return a finite mean from one timestamped Allen table interval."""
    mask = (table["timestamps"] >= start) & (table["timestamps"] < end)
    values = [float(value) for value in table.loc[mask, value_name] if finite(value)]
    return mean(values) if values else None


def summarize_numeric_column(table: Any, column: str) -> dict[str, float | int | None]:
    """Summarize one finite numeric table column."""
    values = [float(value) for value in table[column] if finite(value)] if column in table else []
    return {
        "n_finite": len(values),
        "mean": mean(values) if values else None,
        "min": min(values) if values else None,
        "max": max(values) if values else None,
    }


def export_one(session_id: str, datasets_root: Path, cache_root: Path) -> Path:
    """Export one sidecar artifact from a local NWB file."""
    normalized_dir = datasets_root / session_id
    normalized = read_session_artifact(normalized_dir)
    allen = load_local_allen_session(cache_root, int(session_id))
    running = allen.running_speed
    eye = allen.eye_tracking
    units = allen.get_units(filter_by_validity=False, filter_out_of_brain_units=False)
    channels = allen.get_channels(filter_by_validity=False)

    trial_state = []
    for trial in normalized.trials:
        start = float(trial.metadata["trial_start_time_s"])
        trial_state.append(
            {
                "trial_id": trial.trial_id,
                "running_speed_0_250": interval_mean(running, "speed", start, start + 0.250),
                "pupil_area_0_250": interval_mean(eye, "pupil_area", start, start + 0.250),
                "running_speed_250_750": interval_mean(running, "speed", start + 0.250, start + 0.750),
                "pupil_area_250_750": interval_mean(eye, "pupil_area", start + 0.250, start + 0.750),
            }
        )

    unit_columns = [
        "snr",
        "presence_ratio",
        "isi_violations",
        "amplitude_cutoff",
        "firing_rate",
        "max_drift",
    ]
    quality = {
        "n_units": len(units),
        "good_unit_fraction": (
            sum(str(value).lower() == "good" for value in units["quality"]) / len(units)
            if len(units) and "quality" in units
            else None
        ),
        "numeric": {column: summarize_numeric_column(units, column) for column in unit_columns},
    }

    coordinate_columns = [
        "anterior_posterior_ccf_coordinate",
        "dorsal_ventral_ccf_coordinate",
        "left_right_ccf_coordinate",
    ]
    channel_summary = {
        "n_channels": len(channels),
        "valid_data_fraction": (
            sum(bool(value) for value in channels["valid_data"]) / len(channels)
            if len(channels) and "valid_data" in channels
            else None
        ),
        "coordinates": {
            column: summarize_numeric_column(channels, column)
            for column in coordinate_columns
        },
    }
    coarse_counts: dict[str, int] = {}
    if "structure_acronym" in channels:
        for acronym in channels["structure_acronym"]:
            region = allen_acronym_to_model_region(str(acronym))
            if region:
                coarse_counts[region] = coarse_counts.get(region, 0) + 1
    channel_summary["coarse_region_channel_counts"] = coarse_counts

    payload = {
        "session_id": session_id,
        "animal_id": normalized.animal_id,
        "source_nwb": str(local_nwb_path(cache_root, int(session_id)).relative_to(ROOT)),
        "state_window_definition_s": {
            "stimulus": [0.0, 0.250],
            "decision": [0.250, 0.750],
        },
        "trial_state": trial_state,
        "unit_quality": quality,
        "channel_anatomy": channel_summary,
        "limitations": [
            "Pupil means exclude non-finite samples but do not yet perform advanced blink interpolation.",
            "Channel coordinates describe recording coverage, not cell-body coordinates.",
            "This sidecar is exploratory and does not alter primary normalized sessions.",
        ],
    }
    out = normalized_dir / "state_anatomy.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-id")
    parser.add_argument("--datasets-root", type=Path, default=ROOT / "artifacts" / "datasets" / "allen")
    parser.add_argument("--cache-root", type=Path, default=ROOT / "data" / "allen")
    args = parser.parse_args()

    if args.session_id:
        session_ids = [args.session_id]
    else:
        session_ids = [
            path.parent.name
            for path in sorted(args.datasets_root.glob("*/session.json"))
            if local_nwb_path(args.cache_root, int(path.parent.name)).exists()
        ]
    exported = []
    failed = []
    for session_id in session_ids:
        try:
            exported.append(str(export_one(session_id, args.datasets_root, args.cache_root)))
            print(f"exported_state_anatomy={session_id}")
        except Exception as exc:
            failed.append({"session_id": session_id, "error": str(exc)})
            print(f"failed_state_anatomy={session_id}: {exc}")
    status = {
        "requested": len(session_ids),
        "exported": len(exported),
        "failed": failed,
        "artifacts": exported,
    }
    status_path = ROOT / "artifacts" / "reports" / "allen" / "state_anatomy_export_status.json"
    status_path.write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    print(f"state_anatomy_status={status_path}")


if __name__ == "__main__":
    main()
